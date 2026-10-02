"""Clinical Review Lifecycle & Governance Enforcement (PHASE 30A).

ARCHITECTURE PRINCIPLE:
"Only approved evidence controls medical knowledge. Unreviewed or modified
content must never silently enter production."

This module formalizes the review states:
    DRAFT -> PENDING_DOMAIN_REVIEW -> APPROVED -> PRODUCTION
with:
    REJECTED as terminal/review outcome.

NO CLINICAL CONTENT IS CREATED OR ACTIVATED BY THIS MODULE.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.models.domain import ReviewStatus
from app.knowledge.evidence_models import (
    ClinicalDocument,
    compute_document_hash,
)

__all__ = [
    "GovernanceError",
    "validate_for_approval",
    "validate_production_eligibility",
    "promote_to_approved",
    "reject_document",
    "invalidate_approval_on_edit",
    "validate_multilingual_independence",
]


class GovernanceError(ValueError):
    """Raised when clinical governance invariants or approval boundaries are violated."""


def validate_for_approval(doc: ClinicalDocument) -> None:
    """Verifies all mandatory human clinical governance requirements for APPROVED status.
    AI/LLMs cannot auto-approve clinical content.
    """
    if not doc.reviewed_by or not doc.reviewed_by.strip():
        raise GovernanceError(
            f"Document '{doc.id}': APPROVED status requires non-empty human reviewer identity (reviewed_by)."
        )

    if not doc.reviewed_at:
        raise GovernanceError(
            f"Document '{doc.id}': APPROVED status requires an explicit review timestamp (reviewed_at)."
        )

    ref = doc.approval_metadata.get("clinical_approval_reference")
    if not ref or not str(ref).strip():
        raise GovernanceError(
            f"Document '{doc.id}': APPROVED status requires 'clinical_approval_reference' in approval_metadata."
        )

    if not doc.source.name.strip() or not doc.source.publisher.strip():
        raise GovernanceError(
            f"Document '{doc.id}': Missing authoritative source provenance."
        )

    # Verify content hash matches canonical calculation
    expected_hash = compute_document_hash(
        doc_id=doc.id,
        title=doc.title,
        source=doc.source,
        freshness=doc.freshness,
        metadata=doc.metadata,
        version=doc.version,
        raw_content=doc.raw_content,
    )
    if doc.content_hash != expected_hash:
        raise GovernanceError(
            f"Document '{doc.id}': Content integrity hash mismatch: expected {expected_hash}, got {doc.content_hash}."
        )


def validate_production_eligibility(doc: ClinicalDocument) -> None:
    """Enforces that only fully APPROVED, integrity-verified documents can enter production."""
    if doc.review_status != ReviewStatus.APPROVED:
        raise GovernanceError(
            f"Document '{doc.id}' has status '{doc.review_status.value}'; "
            f"only '{ReviewStatus.APPROVED.value}' documents are production eligible."
        )
    validate_for_approval(doc)


def promote_to_approved(
    doc: ClinicalDocument,
    reviewer_name: str,
    approval_ref: str,
    notes: str | None = None,
    timestamp: datetime | None = None,
) -> ClinicalDocument:
    """Promotes a document to APPROVED following validated human clinical review."""
    if not reviewer_name or not reviewer_name.strip():
        raise GovernanceError("Reviewer name cannot be empty.")
    if not approval_ref or not approval_ref.strip():
        raise GovernanceError("Clinical approval reference cannot be empty.")

    ts = timestamp or datetime.now(timezone.utc)
    new_metadata = dict(doc.approval_metadata)
    new_metadata["clinical_approval_reference"] = approval_ref.strip()

    updated_data = doc.model_dump()
    updated_data["review_status"] = ReviewStatus.APPROVED
    updated_data["reviewed_by"] = reviewer_name.strip()
    updated_data["reviewed_at"] = ts
    updated_data["review_notes"] = notes
    updated_data["approval_metadata"] = new_metadata

    approved_doc = ClinicalDocument.model_validate(updated_data)
    validate_for_approval(approved_doc)
    return approved_doc


def reject_document(
    doc: ClinicalDocument,
    reviewer_name: str,
    reason: str,
    timestamp: datetime | None = None,
) -> ClinicalDocument:
    """Transitions a document to REJECTED."""
    if not reviewer_name or not reviewer_name.strip():
        raise GovernanceError("Reviewer name cannot be empty.")
    if not reason or not reason.strip():
        raise GovernanceError("Rejection reason cannot be empty.")

    ts = timestamp or datetime.now(timezone.utc)
    updated_data = doc.model_dump()
    updated_data["review_status"] = ReviewStatus.REJECTED
    updated_data["reviewed_by"] = reviewer_name.strip()
    updated_data["reviewed_at"] = ts
    updated_data["review_notes"] = reason.strip()

    return ClinicalDocument.model_validate(updated_data)


def invalidate_approval_on_edit(
    existing: ClinicalDocument,
    incoming: ClinicalDocument,
) -> ClinicalDocument:
    """Ensures that any content or metadata modification to an existing APPROVED document
    invalidates the approval and resets the document to PENDING_DOMAIN_REVIEW.
    """
    if existing.content_hash != incoming.content_hash or existing.version != incoming.version:
        # Content or core metadata has changed
        data = incoming.model_dump()
        data["review_status"] = ReviewStatus.PENDING_DOMAIN_REVIEW
        data["reviewed_by"] = None
        data["reviewed_at"] = None
        data["approval_metadata"] = {
            k: v for k, v in incoming.approval_metadata.items()
            if k != "clinical_approval_reference"
        }
        data["review_notes"] = (
            f"Approval invalidated due to content/metadata mutation from version {existing.version}."
        )
        return ClinicalDocument.model_validate(data)

    return incoming


def validate_multilingual_independence(
    source_doc: ClinicalDocument,
    translation_doc: ClinicalDocument,
) -> None:
    """Enforces that an approval in one language (e.g., English) does NOT automatically
    grant clinical approval to localized content (e.g., Urdu or Sindhi).
    Each localized document must undergo qualified clinical and linguistic review
    appropriate to the content and language before activation.
    """
    if translation_doc.metadata.language != source_doc.metadata.language:
        if translation_doc.review_status == ReviewStatus.APPROVED:
            # Must have distinct clinical approval reference or note validating the language content
            src_ref = source_doc.approval_metadata.get("clinical_approval_reference")
            trans_ref = translation_doc.approval_metadata.get("clinical_approval_reference")
            if src_ref == trans_ref and not translation_doc.approval_metadata.get("linguistic_clinical_reviewed"):
                raise GovernanceError(
                    f"Multilingual governance violation: Content '{translation_doc.id}' "
                    f"({translation_doc.metadata.language.value}) cannot inherit approval reference "
                    f"from source ({source_doc.metadata.language.value}) without qualified clinical and linguistic review."
                )
