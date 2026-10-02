"""
Clinical Content Onboarding Pipeline (PHASE 15B)
(ARCHITECTURE.md §9).
"""
from __future__ import annotations
from pathlib import Path
from typing import Any
import yaml
import json
import hashlib

from app.models import KnowledgeEntry, ReviewStatus
from app.knowledge.loader import load_entry_file, KnowledgeLoadError, _FRONTMATTER_DELIMITER

__all__ = ["OnboardingError", "ClinicalOnboardingPipeline"]

class OnboardingError(Exception):
    """Raised when onboarding validation fails."""

def _parse_version(v: str) -> tuple[int, ...]:
    try:
        return tuple(int(x) for x in v.split("."))
    except ValueError:
        raise OnboardingError(f"Invalid version format {v!r}, must be numeric dot-separated.")

class ClinicalOnboardingPipeline:
    def __init__(self, target_dir: Path):
        self.target_dir = target_dir

    def _find_existing(self, entry_id: str) -> Path | None:
        if not self.target_dir.is_dir():
            return None
        for p in self.target_dir.glob("*.md"):
            if p.stem.casefold() == "readme":
                continue
            try:
                # We can just read the frontmatter manually to be faster, but for safety:
                entry = load_entry_file(p)
                if entry.id == entry_id:
                    return p
            except KnowledgeLoadError:
                # If there's a broken file, we don't crash the whole pipeline, but ideally
                # it shouldn't be there. We'll skip it for now.
                pass
        return None

    def ingest(self, entry: KnowledgeEntry) -> Path:
        """
        Ingest a KnowledgeEntry into the production corpus.
        Enforces governance rules, version transitions, and approval boundaries.
        """
        if not self.target_dir.exists():
            self.target_dir.mkdir(parents=True, exist_ok=True)
            
        # 1. Validation of REQUIRED boundary fields for APPROVED content.
        if entry.review_status == ReviewStatus.APPROVED:
            # Structurally require explicit human approval evidence
            if not entry.reviewed_by or not entry.reviewed_at:
                raise OnboardingError(
                    "APPROVED state requires explicit human clinical review metadata "
                    "(reviewed_by, reviewed_at). AI/LLMs cannot auto-approve."
                )
            if not entry.approval_metadata.get("clinical_approval_reference"):
                raise OnboardingError(
                    "APPROVED state requires explicit clinical_approval_reference in approval_metadata."
                )
                
        # 2. Check for conflicts and version transitions
        existing_path = self._find_existing(entry.id)
        if existing_path:
            existing = load_entry_file(existing_path)
            
            # Prevent duplicate versions and enforce strictly greater versions
            old_ver = _parse_version(existing.version)
            new_ver = _parse_version(entry.version)
            if new_ver <= old_ver:
                raise OnboardingError(
                    f"Version conflict: incoming version {entry.version} must be strictly "
                    f"greater than existing version {existing.version}."
                )
                
            # Language should match for the same stable ID
            if existing.language != entry.language:
                raise OnboardingError(
                    f"Language mismatch: existing entry is {existing.language}, incoming is {entry.language}."
                )

        # 3. Write out the verified Markdown file
        filename = f"{entry.id}.md"
        out_path = self.target_dir / filename
        
        payload: dict[str, Any] = {
            "id": entry.id,
            "title": entry.title,
            "terms": entry.terms,
            "source": entry.source,
            "date_reviewed": entry.date_reviewed.isoformat(),
            "review_status": entry.review_status.value,
            "content_hash": entry.content_hash,
            "language": entry.language.value,
            "reviewer_role": entry.reviewer_role,
            "version": entry.version,
            "clinical_scope": entry.clinical_scope,
        }
        if entry.source_url:
            payload["source_url"] = entry.source_url
        if entry.publication_date:
            payload["publication_date"] = entry.publication_date.isoformat()
        if entry.approval_metadata:
            payload["approval_metadata"] = entry.approval_metadata
        if entry.reviewed_by:
            payload["reviewed_by"] = entry.reviewed_by
        if entry.reviewed_at:
            payload["reviewed_at"] = entry.reviewed_at.isoformat().replace("+00:00", "Z")
        if entry.review_notes:
            payload["review_notes"] = entry.review_notes

        frontmatter = yaml.dump(payload, sort_keys=False, default_flow_style=False)
        content = f"{_FRONTMATTER_DELIMITER}\n{frontmatter}{_FRONTMATTER_DELIMITER}\n{entry.content}"
        
        out_path.write_text(content, encoding="utf-8")
        
        if existing_path and existing_path.name != filename:
            existing_path.unlink()
            
        return out_path
