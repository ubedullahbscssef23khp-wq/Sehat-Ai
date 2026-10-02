# Production Knowledge Layer

This directory holds the production-active curated medical knowledge entries.
Only APPROVED entries may be loaded.

## Governance Requirements
- Entries must pass rigorous clinical review.
- Allowed state for production: `approved`
- Each entry must be a Markdown file with YAML frontmatter.
- Requires provenance (source, date_reviewed).
- Requires review metadata.
- Unapproved entries, drafts, and rejected knowledge will be ignored or rejected by the loader.
