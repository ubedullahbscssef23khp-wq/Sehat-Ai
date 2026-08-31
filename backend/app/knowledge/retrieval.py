"""Lexical retrieval over the curated knowledge corpus (ARCHITECTURE.md §9).

v1 retrieval is deterministic term-overlap scoring — explainable and fully
testable, no vector DB. Matches are computed only from the curated `terms`
field (titles are display metadata, not retrieval signal), so every match is
traceable to an explicit curation choice; an empty result must be reported
honestly by the caller, never filled with model memory.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Protocol

from app.models import KnowledgeEntry, StructuredCase

__all__ = ["KnowledgeRetriever", "LexicalKnowledgeRetriever", "tokenize", "case_terms"]

_TOKEN = re.compile(r"\w+", re.UNICODE)

# Function words that carry no retrieval signal in any of the supported
# languages' Roman transliterations. Content words are never filtered.
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


def tokenize(text: str) -> set[str]:
    """Lowercase word tokens, minus stopwords and single characters."""
    return {
        token
        for token in (match.casefold() for match in _TOKEN.findall(text))
        if len(token) > 1 and token not in _STOPWORDS
    }


def case_terms(case: StructuredCase) -> set[str]:
    """Deterministic query terms for a case: complaint, symptom names,
    reported red-flag signals, associated factors, and body systems."""
    terms = tokenize(case.chief_complaint)
    for symptom in case.symptoms:
        terms |= tokenize(symptom.name)
        if symptom.body_system.value != "unknown":
            terms.add(symptom.body_system.value)
    for signal in case.red_flag_signals:
        terms |= tokenize(signal.replace("_", " "))
    for factor in case.associated_factors:
        terms |= tokenize(factor)
    return terms


class KnowledgeRetriever(Protocol):
    """Swappable retrieval interface (ARCHITECTURE.md §11); a vector-backed
    implementation can replace the lexical one behind this contract."""

    def retrieve(self, case: StructuredCase, max_results: int = 3) -> list[KnowledgeEntry]: ...


class LexicalKnowledgeRetriever:
    def __init__(self, entries: Sequence[KnowledgeEntry]) -> None:
        indexed: list[tuple[KnowledgeEntry, set[str]]] = []
        for entry in entries:
            terms: set[str] = set()
            for curated_term in entry.terms:
                terms |= tokenize(curated_term)
            indexed.append((entry, terms))
        self._indexed = indexed

    def retrieve(self, case: StructuredCase, max_results: int = 3) -> list[KnowledgeEntry]:
        query = case_terms(case)
        if not query:
            return []
        scored = [
            (len(query & entry_terms), entry.id, entry)
            for entry, entry_terms in self._indexed
            if query & entry_terms
        ]
        # Highest overlap first; ties broken by entry ID for determinism.
        scored.sort(key=lambda item: (-item[0], item[1]))
        return [entry for _, _, entry in scored[:max_results]]
