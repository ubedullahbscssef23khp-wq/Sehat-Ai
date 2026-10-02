"""Clinical Knowledge Retrieval & EvidencePack Assembly (PHASE 30A).

ARCHITECTURE PRINCIPLE:
"AI understands. Evidence grounds. Code controls.
The system must be able to abstain when evidence is insufficient."

This module defines the swappable clinical retrieval interface, deterministic
evidence packaging, citation linking, and abstention policies.

NO CLINICAL CONTENT IS CREATED OR ACTIVATED BY THIS MODULE.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timezone
import re
from typing import Any, Protocol

from app.models.domain import Language, ReviewStatus, StructuredCase
from app.knowledge.evidence_models import (
    AbstentionReason,
    ClinicalChunk,
    ClinicalDocument,
    EvidenceCategory,
    EvidenceCitation,
    EvidenceItem,
    EvidencePack,
    EvidenceSufficiency,
    FreshnessPolicy,
    FreshnessStatus,
    RetrievalContext,
)

__all__ = [
    "ClinicalRetriever",
    "LexicalClinicalRetriever",
    "MockClinicalRetriever",
]

_TOKEN_RE = re.compile(r"\w+", re.UNICODE)
_STOPWORDS = frozenset(
    {
        "i", "a", "an", "the", "my", "me", "is", "are", "was", "were",
        "have", "has", "had", "having", "of", "and", "or", "for", "to",
        "in", "on", "at", "with", "since", "from", "it", "its", "this",
        "that", "am", "be", "been", "very", "some", "we", "you", "they",
        "he", "she", "not", "no", "so", "do", "does", "did",
        "mujhe", "mera", "meri", "hai", "hain", "ka", "ki", "ke", "aur",
        "ko", "se", "par", "tha", "thi",
    }
)


def _tokenize(text: str) -> set[str]:
    return {
        token
        for token in (m.casefold() for m in _TOKEN_RE.findall(text))
        if len(token) > 1 and token not in _STOPWORDS
    }


def _extract_query_terms(query: str | StructuredCase) -> set[str]:
    if isinstance(query, str):
        return _tokenize(query)

    terms = _tokenize(query.chief_complaint)
    for symptom in query.symptoms:
        terms |= _tokenize(symptom.name)
        if symptom.body_system.value != "unknown":
            terms.add(symptom.body_system.value)
    for signal in query.red_flag_signals:
        terms |= _tokenize(signal.replace("_", " "))
    for factor in query.associated_factors:
        terms |= _tokenize(factor)
    return terms


class ClinicalRetriever(Protocol):
    """Swappable clinical evidence retriever interface."""

    def retrieve(
        self,
        query: str | StructuredCase,
        context: RetrievalContext | None = None,
        max_results: int = 3,
    ) -> EvidencePack:
        """Retrieve approved evidence, evaluate sufficiency, and assemble an EvidencePack."""
        ...


class LexicalClinicalRetriever:
    """Deterministic lexical retriever over governed ClinicalDocument entries."""

    def __init__(self, documents: Sequence[ClinicalDocument] = ()) -> None:
        self._documents = list(documents)

    def retrieve(
        self,
        query: str | StructuredCase,
        context: RetrievalContext | None = None,
        max_results: int = 3,
    ) -> EvidencePack:
        ctx = context or RetrievalContext()
        terms = _extract_query_terms(query)
        eval_time = datetime.now(timezone.utc)
        query_text = query if isinstance(query, str) else query.chief_complaint

        if not self._documents:
            return EvidencePack(
                query=query_text,
                items=[],
                citations=[],
                sufficiency=EvidenceSufficiency.INSUFFICIENT,
                should_abstain=True,
                abstention_reason=AbstentionReason.NO_APPROVED_EVIDENCE,
                retrieval_metadata={"total_corpus_docs": 0, "matched_chunks": 0},
                limitations=["No approved clinical evidence available in production corpus."],
                evaluated_at=eval_time,
            )

        if not terms:
            return EvidencePack(
                query=query_text,
                items=[],
                citations=[],
                sufficiency=EvidenceSufficiency.INSUFFICIENT,
                should_abstain=True,
                abstention_reason=AbstentionReason.MISSING_CONTEXT,
                retrieval_metadata={"reason": "Empty search terms"},
                limitations=["Insufficient query terms to perform clinical evidence matching."],
                evaluated_at=eval_time,
            )

        # 1. Filter documents by approval status, language, and clinical domain
        eligible_chunks: list[tuple[ClinicalDocument, ClinicalChunk, FreshnessStatus]] = []
        for doc in self._documents:
            # Governance enforcement: only APPROVED documents are production eligible
            if not ctx.allow_unreviewed and doc.review_status != ReviewStatus.APPROVED:
                continue

            # Language filtering
            if ctx.language and doc.metadata.language != ctx.language:
                continue

            # Clinical domain filtering (if specified and not GENERAL)
            if ctx.domain and doc.metadata.domain != ctx.domain:
                continue

            # Freshness evaluation
            freshness_status = ctx.freshness_policy.evaluate(
                doc.freshness,
                domain=doc.metadata.domain,
                jurisdiction=doc.metadata.jurisdiction,
                eval_date=ctx.evaluation_date,
            )

            # Document chunks (fallback to raw_content as 1 chunk if chunks list is empty)
            chunks = doc.chunks
            if not chunks:
                chunks = [
                    ClinicalChunk(
                        id=f"{doc.id}-c0",
                        document_id=doc.id,
                        chunk_index=0,
                        total_chunks=1,
                        content=doc.raw_content,
                        terms=list(_tokenize(doc.title + " " + doc.raw_content)),
                        content_hash=doc.content_hash,
                        metadata=doc.metadata,
                    )
                ]

            for chunk in chunks:
                eligible_chunks.append((doc, chunk, freshness_status))

        # 2. Score chunks by lexical term overlap
        scored: list[tuple[int, float, ClinicalDocument, ClinicalChunk, FreshnessStatus]] = []
        for doc, chunk, f_status in eligible_chunks:
            chunk_terms = set(chunk.terms) if chunk.terms else _tokenize(chunk.content)
            overlap = terms & chunk_terms
            if overlap:
                overlap_count = len(overlap)
                score = min(1.0, overlap_count / max(1, len(terms)))
                scored.append((overlap_count, score, doc, chunk, f_status))

        # Sort highest overlap first; break ties by document ID for determinism
        scored.sort(key=lambda x: (-x[0], x[2].id, x[3].id))
        top_matches = scored[:max_results]

        if not top_matches:
            return EvidencePack(
                query=query_text,
                items=[],
                citations=[],
                sufficiency=EvidenceSufficiency.INSUFFICIENT,
                should_abstain=True,
                abstention_reason=AbstentionReason.INSUFFICIENT_EVIDENCE,
                retrieval_metadata={"matched_chunks": 0, "eligible_chunks": len(eligible_chunks)},
                limitations=["No matching clinical evidence found for the specified symptoms."],
                evaluated_at=eval_time,
            )

        # 3. Check for stale evidence
        has_stale = any(f_status == FreshnessStatus.STALE for _, _, _, _, f_status in top_matches)
        all_stale = all(f_status == FreshnessStatus.STALE for _, _, _, _, f_status in top_matches)

        items: list[EvidenceItem] = []
        citations: list[EvidenceCitation] = []

        for _, score, doc, chunk, f_status in top_matches:
            citation = EvidenceCitation(
                source=doc.source.name,
                publisher=doc.source.publisher,
                document_id=doc.id,
                chunk_id=chunk.id,
                version=doc.version,
                publication_date=doc.freshness.publication_date,
                date_reviewed=doc.freshness.last_reviewed,
                excerpt=chunk.content[:280],
                url=doc.source.url,
                language=doc.metadata.language,
                provenance=f"{doc.source.publisher} ({doc.version})",
            )
            citations.append(citation)
            items.append(
                EvidenceItem(
                    document_id=doc.id,
                    chunk=chunk,
                    source=doc.source,
                    relevance_score=score,
                    freshness_status=f_status,
                    citation=citation,
                )
            )

        # 4. Determine Sufficiency & Abstention
        if all_stale:
            sufficiency = EvidenceSufficiency.INSUFFICIENT
            should_abstain = True
            abstention_reason = AbstentionReason.STALE_EVIDENCE
            limitations = ["All retrieved evidence exceeds configured freshness intervals."]
        else:
            match_count = len(items)
            if match_count >= 3:
                sufficiency = EvidenceSufficiency.HIGH
            elif match_count == 2:
                sufficiency = EvidenceSufficiency.MEDIUM
            else:
                sufficiency = EvidenceSufficiency.LOW

            # Evaluate against requested minimum sufficiency
            _tier_order = {
                EvidenceSufficiency.INSUFFICIENT: 0,
                EvidenceSufficiency.LOW: 1,
                EvidenceSufficiency.MEDIUM: 2,
                EvidenceSufficiency.HIGH: 3,
            }
            if _tier_order[sufficiency] < _tier_order[ctx.min_sufficiency]:
                should_abstain = True
                abstention_reason = AbstentionReason.INSUFFICIENT_EVIDENCE
                limitations = [
                    f"Evidence sufficiency '{sufficiency.value}' is below requested threshold '{ctx.min_sufficiency.value}'."
                ]
            else:
                should_abstain = False
                abstention_reason = AbstentionReason.NONE
                limitations = []

        if has_stale and not all_stale:
            limitations.append("One or more retrieved sources are due for review or stale.")

        return EvidencePack(
            query=query_text,
            items=items,
            citations=citations,
            sufficiency=sufficiency,
            should_abstain=should_abstain,
            abstention_reason=abstention_reason,
            retrieval_metadata={
                "matched_chunks": len(items),
                "top_score": top_matches[0][1] if top_matches else 0.0,
                "language": ctx.language.value,
                "domain": ctx.domain.value if ctx.domain else None,
            },
            limitations=limitations,
            evaluated_at=eval_time,
        )


class MockClinicalRetriever:
    """Mock retriever for unit testing deterministic synthesis and abstention behaviors."""

    def __init__(self, packs: Sequence[EvidencePack] = ()) -> None:
        self._packs = list(packs)
        self.queries_received: list[str | StructuredCase] = []

    def retrieve(
        self,
        query: str | StructuredCase,
        context: RetrievalContext | None = None,
        max_results: int = 3,
    ) -> EvidencePack:
        self.queries_received.append(query)
        if not self._packs:
            query_str = query if isinstance(query, str) else query.chief_complaint
            return EvidencePack(
                query=query_str,
                items=[],
                citations=[],
                sufficiency=EvidenceSufficiency.INSUFFICIENT,
                should_abstain=True,
                abstention_reason=AbstentionReason.INSUFFICIENT_EVIDENCE,
                retrieval_metadata={"mock": True},
                limitations=["Mock retriever has no preconfigured packs."],
                evaluated_at=datetime.now(timezone.utc),
            )
        return self._packs.pop(0)
