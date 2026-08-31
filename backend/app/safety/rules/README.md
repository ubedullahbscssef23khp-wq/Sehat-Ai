# Red-flag rules

Version-controlled YAML red-flag rules live here (schema enforced by
`app/safety/loader.py`). Every rule must carry `source` and `review_date`;
files missing them are rejected at load time.

This directory intentionally ships **without rule content**: clinical rule
content must be curated from authoritative public health sources with
citations (DEVELOPMENT_PLAN.md, Phase 1). Engine behavior is verified with
synthetic structural fixtures in `backend/tests/` — those fixtures are test
data, not medical content.
