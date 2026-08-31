# Knowledge content — curation required

This directory holds the curated knowledge corpus served as cited evidence
(ARCHITECTURE.md §9). It **ships empty on purpose**: no entry may be
invented, paraphrased from memory, or model-generated.

## Format

One Markdown file per entry, with mandatory YAML frontmatter:

```markdown
---
id: stable-kebab-case-id
title: Human-readable topic title
terms: [keyword, keyword, keyword]
source: Authoritative public health source (name + page/document if possible)
date_reviewed: YYYY-MM-DD
---
Curated body text. This exact text is shown to users as a cited snippet, so
keep it short, factual, and free of diagnostic or medication advice.
```

## Loader rules (enforced by `app/knowledge/loader.py`)

- `source` and `date_reviewed` are mandatory — entries without provenance
  fail to load and the whole file is rejected.
- `id` must be unique across the corpus.
- The body must be non-empty.
- Files are loaded in sorted filename order; any invalid file stops startup.

## Curation rules

- Content must come from authoritative public health guidance only.
- Record the review date; re-review and update `date_reviewed` when the
  source changes.
- Entries must not diagnose, name treatments or medications, or state
  emergency thresholds — those live exclusively in the deterministic safety
  layer (`app/safety/rules/`).
