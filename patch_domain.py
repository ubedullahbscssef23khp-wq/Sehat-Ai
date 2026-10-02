import sys
import re
path = 'backend/app/models/domain.py'
content = open(path).read()

new_fields = """    content_hash: str = Field(min_length=1)
    
    # Phase 15A Knowledge Governance Fields
    language: Language = Field(default=Language.EN)
    source_url: str | None = None
    publication_date: date | None = None
    reviewer_role: str = Field(default="QUALIFIED_CLINICAL_REVIEWER", min_length=1)
    version: str = Field(default="1.0", min_length=1)
    clinical_scope: str = Field(default="general", min_length=1)
    approval_metadata: dict[str, Any] = Field(default_factory=dict)"""

content = content.replace("    content_hash: str = Field(min_length=1)", new_fields, 1)

old_hash = """    @model_validator(mode="after")
    def _verify_content_hash(self) -> "KnowledgeEntry":
        payload = {
            "content": self.content,
            "date_reviewed": self.date_reviewed.isoformat(),
            "id": self.id,
            "source": self.source,
            "terms": self.terms,
            "title": self.title,
        }
        canonical = json.dumps(payload, separators=(",", ":"), sort_keys=True)
        computed = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        if self.content_hash != computed:
            raise ValueError(f"content hash mismatch: expected {self.content_hash}, got {computed}")
        return self"""

new_hash = """    @model_validator(mode="after")
    def _verify_content_hash(self) -> "KnowledgeEntry":
        payload = {
            "approval_metadata": self.approval_metadata,
            "clinical_scope": self.clinical_scope,
            "content": self.content,
            "date_reviewed": self.date_reviewed.isoformat(),
            "id": self.id,
            "language": self.language.value,
            "publication_date": self.publication_date.isoformat() if self.publication_date else None,
            "reviewer_role": self.reviewer_role,
            "source": self.source,
            "source_url": self.source_url,
            "terms": self.terms,
            "title": self.title,
            "version": self.version,
        }
        canonical = json.dumps(payload, separators=(",", ":"), sort_keys=True)
        computed = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        if self.content_hash != computed:
            raise ValueError(f"content hash mismatch: expected {self.content_hash}, got {computed}")
        return self"""

content = content.replace(old_hash, new_hash)
open(path, 'w').write(content)
