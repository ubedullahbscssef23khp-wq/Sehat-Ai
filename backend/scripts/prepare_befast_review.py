import json
import hashlib
import yaml
from pathlib import Path
from datetime import date

knowledge_staging_dir = Path("/app/applet/backend/app/knowledge/staging_review")
safety_staging_dir = Path("/app/applet/backend/app/safety/staging_review")
docs_dir = Path("/app/applet/docs/review_packages")
knowledge_staging_dir.mkdir(parents=True, exist_ok=True)
safety_staging_dir.mkdir(parents=True, exist_ok=True)
docs_dir.mkdir(parents=True, exist_ok=True)

concepts = [
    {
        "id": "BEFAST-B-001",
        "title": "BEFAST - Balance Loss",
        "content": "Sudden loss of balance or coordination is a warning sign of stroke.",
        "terms": ["balance", "dizziness", "coordination"],
        "source": "CDC - Signs and Symptoms of Stroke",
        "source_url": "https://www.cdc.gov/stroke/signs-symptoms/index.html",
        "publication_date": "2026-05-01",
        "pattern": "loss of balance",
        "pattern_desc": "Sudden loss of balance or coordination"
    },
    {
        "id": "BEFAST-E-001",
        "title": "BEFAST - Eyes (Vision Change)",
        "content": "Sudden vision loss or vision changes in one or both eyes can be a sign of stroke.",
        "terms": ["eyes", "vision loss", "trouble seeing"],
        "source": "WHO - Stroke fact sheet",
        "source_url": "https://www.who.int/news-room/fact-sheets/detail/stroke",
        "publication_date": "2025-12-19",
        "pattern": "vision loss",
        "pattern_desc": "Sudden vision change or loss"
    },
    {
        "id": "BEFAST-F-001",
        "title": "BEFAST - Facial Droop",
        "content": "Sudden facial droop or numbness on one side of the face is a stroke symptom.",
        "terms": ["face", "facial droop", "numbness"],
        "source": "AHA/ASA B.E. F.A.S.T.",
        "source_url": "https://newsroom.heart.org/news/knowing-stroke-signs-can-save-a-life-when-every-minute-counts",
        "publication_date": "2026-05-01",
        "pattern": "facial droop",
        "pattern_desc": "Sudden facial weakness or drooping"
    },
    {
        "id": "BEFAST-A-001",
        "title": "BEFAST - Arm Weakness",
        "content": "Sudden weakness or numbness in one or both arms is a stroke warning sign.",
        "terms": ["arm", "weakness", "numbness"],
        "source": "CDC - Signs and Symptoms of Stroke",
        "source_url": "https://www.cdc.gov/stroke/signs-symptoms/index.html",
        "publication_date": "2026-05-01",
        "pattern": "arm weakness",
        "pattern_desc": "Weakness in one or both arms"
    },
    {
        "id": "BEFAST-S-001",
        "title": "BEFAST - Speech Difficulty",
        "content": "Slurred or strange speech, or sudden trouble speaking, is a sign of stroke.",
        "terms": ["speech", "slurred", "trouble speaking"],
        "source": "WHO - Stroke fact sheet",
        "source_url": "https://www.who.int/news-room/fact-sheets/detail/stroke",
        "publication_date": "2025-12-19",
        "pattern": "slurred speech",
        "pattern_desc": "Slurred or strange speech"
    }
]

today = date.today().isoformat()

review_doc = ["# BEFAST Stroke Recognition - Clinical Review Package", ""]
review_doc.append("## STATUS: NOT APPROVED FOR PRODUCTION")
review_doc.append("This package is PENDING_DOMAIN_REVIEW. Do not activate without qualified clinical approval.\n")

patterns = []

for c in concepts:
    # Knowledge Entry Payload
    payload = {
        "approval_metadata": {},
        "clinical_scope": "stroke",
        "content": c["content"],
        "date_reviewed": today,
        "id": c["id"],
        "language": "en",
        "publication_date": c["publication_date"],
        "reviewer_role": "QUALIFIED_CLINICAL_REVIEWER",
        "source": c["source"],
        "source_url": c["source_url"],
        "terms": c["terms"],
        "title": c["title"],
        "version": "1.0",
    }
    
    canonical = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    h = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    
    fm = payload.copy()
    fm["review_status"] = "pending_domain_review"
    fm["content_hash"] = h
    fm_content = fm.pop("content")
    
    fm_yaml = yaml.dump(fm, sort_keys=False)
    
    entry_text = f"---\n{fm_yaml}---\n{fm_content}"
    
    (knowledge_staging_dir / f"{c['id']}.md").write_text(entry_text, encoding="utf-8")
    
    patterns.append({
        "id": c["id"],
        "pattern": c["pattern"],
        "description": c["pattern_desc"],
        "source": c["source"],
        "review_date": today,
        "review_status": "pending_domain_review",
        "review_notes": f"Source URL: {c['source_url']}"
    })
    
    review_doc.append(f"### {c['id']}")
    review_doc.append(f"- **Proposed Wording:** {c['content']}")
    review_doc.append(f"- **Source:** {c['source']}")
    review_doc.append(f"- **Source URL:** {c['source_url']}")
    review_doc.append(f"- **Publication Date:** {c['publication_date']}")
    review_doc.append(f"- **Version:** 1.0")
    review_doc.append(f"- **Language:** en")
    review_doc.append(f"- **Clinical Scope:** stroke")
    review_doc.append(f"- **Content Hash:** `{h}`")
    review_doc.append(f"- **Review Status:** PENDING_DOMAIN_REVIEW")
    review_doc.append(f"- **Required reviewer qualification:** QUALIFIED_CLINICAL_REVIEWER")
    review_doc.append(f"- **Clinical decision field:** ")
    review_doc.append(f"- **Reviewer identity field:** ")
    review_doc.append(f"- **Review timestamp field:** ")
    review_doc.append(f"- **Clinical approval reference field:** ")
    review_doc.append(f"- **Reviewer comments field:** \n")

(safety_staging_dir / "befast_patterns.yaml").write_text(yaml.dump({"patterns": patterns}, sort_keys=False))

review_doc.append("## REVIEWER CHECKLIST")
review_doc.append("[ ] Source identity verified")
review_doc.append("[ ] Proposed wording accurately represents the source")
review_doc.append("[ ] No unsupported clinical claim introduced")
review_doc.append("[ ] Scope is limited to BEFAST recognition")
review_doc.append("[ ] Emergency semantics are appropriate")
review_doc.append("[ ] English wording is clinically acceptable")
review_doc.append("[ ] Production activation is authorized\n")

(docs_dir / "BEFAST_STROKE_REVIEW.md").write_text("\n".join(review_doc))
print("Prepared review package.")
