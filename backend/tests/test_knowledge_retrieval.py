"""Lexical knowledge retrieval tests (Phase 4).

Fixtures are synthetic; retrieval must be deterministic and explainable.
"""

from __future__ import annotations

from app.knowledge.retrieval import LexicalKnowledgeRetriever, case_terms, tokenize
from app.models import StructuredCase, SymptomReport

from conversation_support import make_knowledge_entry


def make_case(**overrides) -> StructuredCase:
    base: dict = {
        "chief_complaint": "synthetic complaint about topic alpha",
        "symptoms": [SymptomReport(name="alpha pain")],
    }
    base.update(overrides)
    return StructuredCase(**base)


def test_tokenize_casefolds_and_drops_stopwords() -> None:
    tokens = tokenize("I have a very BAD Headache and fever")
    assert tokens == {"bad", "headache", "fever"}


def test_case_terms_include_symptoms_signals_and_systems() -> None:
    case = StructuredCase(
        chief_complaint="alpha",
        symptoms=[SymptomReport(name="beta pain", body_system="respiratory")],
        red_flag_signals=["gamma_signal"],
        associated_factors=["delta happened"],
    )
    terms = case_terms(case)
    assert {"alpha", "beta", "pain", "respiratory", "gamma", "signal", "delta"} <= terms


def test_retrieval_matches_on_term_overlap() -> None:
    matching = make_knowledge_entry("T-KB-MATCH", terms=("alpha",))
    unrelated = make_knowledge_entry("T-KB-OTHER", terms=("zebra",))
    retriever = LexicalKnowledgeRetriever([unrelated, matching])
    results = retriever.retrieve(make_case())
    assert [entry.id for entry in results] == ["T-KB-MATCH"]


def test_retrieval_ranks_by_overlap_count() -> None:
    weak = make_knowledge_entry("T-KB-WEAK", terms=("alpha",))
    strong = make_knowledge_entry("T-KB-STRONG", terms=("alpha", "pain", "topic"))
    retriever = LexicalKnowledgeRetriever([weak, strong])
    results = retriever.retrieve(make_case())
    assert [entry.id for entry in results] == ["T-KB-STRONG", "T-KB-WEAK"]


def test_retrieval_ties_break_by_entry_id_for_determinism() -> None:
    b = make_knowledge_entry("T-KB-B", terms=("alpha",))
    a = make_knowledge_entry("T-KB-A", terms=("alpha",))
    for ordering in ([a, b], [b, a]):
        retriever = LexicalKnowledgeRetriever(ordering)
        assert [entry.id for entry in retriever.retrieve(make_case())] == ["T-KB-A", "T-KB-B"]


def test_retrieval_respects_max_results() -> None:
    entries = [make_knowledge_entry(f"T-KB-{i}", terms=("alpha",)) for i in range(5)]
    retriever = LexicalKnowledgeRetriever(entries)
    assert len(retriever.retrieve(make_case(), max_results=2)) == 2


def test_retrieval_empty_corpus_returns_empty() -> None:
    assert LexicalKnowledgeRetriever([]).retrieve(make_case()) == []


def test_retrieval_no_overlap_returns_empty() -> None:
    retriever = LexicalKnowledgeRetriever([make_knowledge_entry("T-KB-X", terms=("zebra",))])
    assert retriever.retrieve(make_case()) == []


def test_retrieval_is_repeatable() -> None:
    entries = [
        make_knowledge_entry("T-KB-1", terms=("alpha",)),
        make_knowledge_entry("T-KB-2", terms=("complaint",)),
    ]
    retriever = LexicalKnowledgeRetriever(entries)
    first = [entry.id for entry in retriever.retrieve(make_case())]
    second = [entry.id for entry in retriever.retrieve(make_case())]
    assert first == second


def test_citation_carries_provenance_and_snippet() -> None:
    entry = make_knowledge_entry("T-KB-C")
    citation = entry.citation()
    assert citation.source == entry.source
    assert citation.date_reviewed == entry.date_reviewed
    assert citation.snippet == entry.content
