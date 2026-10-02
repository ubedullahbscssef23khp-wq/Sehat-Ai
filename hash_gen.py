import json
import hashlib
payload = {
    "approval_metadata": {},
    "clinical_scope": "general",
    "content": "Synthetic curated body content.",
    "date_reviewed": "2026-01-15",
    "id": "t-kb-1",
    "language": "en",
    "publication_date": None,
    "reviewer_role": "QUALIFIED_CLINICAL_REVIEWER",
    "source": "synthetic authoritative source",
    "source_url": None,
    "terms": ["synthetic-symptom", "synthetic topic"],
    "title": "Synthetic topic",
    "version": "1.0",
}
canonical = json.dumps(payload, separators=(",", ":"), sort_keys=True)
print("t-kb-1:", hashlib.sha256(canonical.encode("utf-8")).hexdigest())

payload["id"] = "t-kb-2"
canonical = json.dumps(payload, separators=(",", ":"), sort_keys=True)
print("t-kb-2:", hashlib.sha256(canonical.encode("utf-8")).hexdigest())
