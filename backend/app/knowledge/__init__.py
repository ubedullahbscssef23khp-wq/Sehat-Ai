"""Clinical Knowledge & Evidence Layer (PHASE 30A).

ARCHITECTURE PRINCIPLE:
"AI understands. Evidence grounds. Code controls."
"""

from app.knowledge.evidence_models import (
    AbstentionReason,
    ClinicalChunk,
    ClinicalDocument,
    ClinicalDomain,
    EvidenceCategory,
    EvidenceCitation,
    EvidenceItem,
    EvidenceMetadata,
    EvidencePack,
    EvidenceSource,
    EvidenceSufficiency,
    FreshnessMetadata,
    FreshnessPolicy,
    FreshnessStatus,
    IngestionMethod,
    RetrievalContext,
    SourceManifest,
    compute_chunk_hash,
    compute_document_hash,
)
from app.knowledge.governance import (
    GovernanceError,
    invalidate_approval_on_edit,
    promote_to_approved,
    reject_document,
    validate_for_approval,
    validate_multilingual_independence,
    validate_production_eligibility,
)
from app.knowledge.ingestion import (
    IngestionError,
    extract_clinical_chunks,
    generate_review_package_markdown,
    ingest_authoritative_source,
)
from app.knowledge.loader import (
    KnowledgeLoadError,
    load_entries_dir,
    load_entry_file,
    parse_entry,
)
from app.knowledge.paths import CONTENT_DIR, KNOWLEDGE_DIR
from app.knowledge.pipeline import ClinicalOnboardingPipeline, OnboardingError
from app.knowledge.retrieval import (
    KnowledgeRetriever,
    LexicalKnowledgeRetriever,
    case_terms,
    tokenize,
)
from app.knowledge.retriever import (
    ClinicalRetriever,
    LexicalClinicalRetriever,
    MockClinicalRetriever,
)

__all__ = [
    # Models & Types
    "AbstentionReason",
    "ClinicalChunk",
    "ClinicalDocument",
    "ClinicalDomain",
    "EvidenceCategory",
    "EvidenceCitation",
    "EvidenceItem",
    "EvidenceMetadata",
    "EvidencePack",
    "EvidenceSource",
    "EvidenceSufficiency",
    "FreshnessMetadata",
    "FreshnessPolicy",
    "FreshnessStatus",
    "IngestionMethod",
    "RetrievalContext",
    "SourceManifest",
    "compute_chunk_hash",
    "compute_document_hash",
    # Ingestion & Manifests
    "IngestionError",
    "extract_clinical_chunks",
    "generate_review_package_markdown",
    "ingest_authoritative_source",
    # Governance
    "GovernanceError",
    "invalidate_approval_on_edit",
    "promote_to_approved",
    "reject_document",
    "validate_for_approval",
    "validate_multilingual_independence",
    "validate_production_eligibility",
    # Loaders & Paths
    "CONTENT_DIR",
    "KNOWLEDGE_DIR",
    "KnowledgeLoadError",
    "load_entries_dir",
    "load_entry_file",
    "parse_entry",
    "ClinicalOnboardingPipeline",
    "OnboardingError",
    # Legacy & Enterprise Retrievers
    "KnowledgeRetriever",
    "LexicalKnowledgeRetriever",
    "ClinicalRetriever",
    "LexicalClinicalRetriever",
    "MockClinicalRetriever",
    "case_terms",
    "tokenize",
]
