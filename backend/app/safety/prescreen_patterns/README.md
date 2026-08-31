# Emergency pre-screen patterns

Curated emergency pre-screen patterns live here as YAML files, loaded with the
same fail-closed discipline as `rules/` (see `app/safety/loader.py`).

**This directory intentionally ships empty.** Pattern content is medical safety
content: it must be curated from authoritative public health guidance with
provenance — it is never invented. Until curation happens, the pre-screen
matches nothing and the pipeline relies on extraction + red-flag rules.

File format (enforced by `EmergencyPattern` validation):

```yaml
patterns:
  - id: EP-001               # stable, explainable ID
    pattern: "<phrase>"      # case-insensitive substring match
    description: "<why this phrase is an emergency signal>"
    source: "<authoritative source name>"
    review_date: 2026-01-01
```

Any file missing `source`/`review_date`, malformed, or with duplicate IDs is
rejected whole — invalid patterns can never partially apply.
