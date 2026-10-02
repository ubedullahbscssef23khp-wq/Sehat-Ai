import json
import hashlib
from pathlib import Path

def get_hash(payload):
    canonical = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

entries = [
    {
        "id": "HEADACHE-001",
        "title": "General headache information",
        "terms": ["headache", "head pain", "headache disorder"],
        "source": "WHO — Migraine and other headache disorders",
        "date_reviewed": "2025-10-24",
        "content": "Headache disorders, characterized by recurrent headache, are among the most common disorders of the nervous system. Headache itself is a painful and disabling feature of primary headache disorders, namely migraine, tension-type headache, and cluster headache. It can also be caused by or occur secondarily to a long list of other conditions."
    },
    {
        "id": "HEADACHE-002",
        "title": "Migraine characteristics",
        "terms": ["migraine", "migraine headache", "photophobia", "phonophobia", "nausea"],
        "source": "WHO — Migraine and other headache disorders",
        "date_reviewed": "2025-10-24",
        "content": "WHO describes migraine as a primary headache disorder. It often begins at puberty and most affects those aged between 35 and 45 years. It is characterized by recurrent attacks, often lifelong. Attacks may include headache of moderate or severe intensity, one-sided, pulsating in quality, aggravated by routine physical activity, and accompanied by nausea, photophobia (sensitivity to light), or phonophobia (sensitivity to sound)."
    },
    {
        "id": "HEADACHE-003",
        "title": "Tension-type headache characteristics",
        "terms": ["tension headache", "tension-type headache", "pressure", "tightness"],
        "source": "WHO — Migraine and other headache disorders",
        "date_reviewed": "2025-10-24",
        "content": "Tension-type headache is the most common primary headache disorder. Episodic attacks usually last a few hours, but can persist for several days. Chronic tension-type headache can be unremitting. The pain is often described as pressure or tightness, like a band around the head, sometimes spreading into or from the neck."
    },
    {
        "id": "HEADACHE-004",
        "title": "Medication-overuse headache",
        "terms": ["medication-overuse headache", "overuse headache", "headache medication"],
        "source": "WHO — Migraine and other headache disorders",
        "date_reviewed": "2025-10-24",
        "content": "Medication-overuse headache is caused by chronic and excessive use of medication to treat headache. It is the most common secondary headache disorder. It may affect people who have an underlying primary headache disorder (such as migraine or tension-type headache) who use pain medication too frequently, often resulting in headaches occurring on more days than not."
    },
    {
        "id": "HEADACHE-005",
        "title": "General headache self-care information",
        "terms": ["headache self care", "headache lifestyle", "headache triggers", "sleep", "hydration", "exercise"],
        "source": "WHO — Migraine and other headache disorders",
        "date_reviewed": "2025-10-24",
        "content": "Conservative lifestyle factors are often discussed in the context of general headache management. The available curated guidance states that identifying and avoiding specific triggers, maintaining regular sleep patterns, ensuring adequate hydration, and participating in regular physical exercise may support overall well-being. These general lifestyle approaches do not replace medical evaluation."
    }
]

out_dir = Path("app/knowledge/content")
out_dir.mkdir(parents=True, exist_ok=True)

for entry in entries:
    c_hash = get_hash(entry)
    terms_str = "[" + ", ".join(entry['terms']) + "]"
    
    file_content = f"""---
id: {entry['id']}
title: {entry['title']}
terms: {terms_str}
source: {entry['source']}
date_reviewed: {entry['date_reviewed']}
review_status: pending_domain_review
content_hash: '{c_hash}'
---
{entry['content']}"""

    (out_dir / f"{entry['id']}.md").write_text(file_content, encoding="utf-8")
    print(f"Wrote {entry['id']}.md")

