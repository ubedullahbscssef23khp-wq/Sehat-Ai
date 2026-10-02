#!/usr/bin/env python3
"""
CLI script to validate the clinical corpus before production activation.
Validates all knowledge entries and emergency patterns.
Run from backend/ directory:
    python -m scripts.validate_corpus
"""
import sys
from pathlib import Path

from app.knowledge.loader import load_entries_dir, KnowledgeLoadError
from app.knowledge.paths import CONTENT_DIR
from app.safety.loader import load_patterns_dir, RuleLoadError
from app.safety.paths import PRESCREEN_DIR


def main() -> int:
    print("Validating clinical corpus...")
    
    has_errors = False

    try:
        entries = load_entries_dir(CONTENT_DIR)
        print(f"✅ Knowledge corpus valid. Found {len(entries)} APPROVED entries.")
    except KnowledgeLoadError as e:
        print(f"❌ Knowledge validation failed: {e}")
        has_errors = True
    except Exception as e:
        print(f"❌ Unexpected error validating knowledge: {e}")
        has_errors = True

    try:
        patterns = load_patterns_dir(PRESCREEN_DIR)
        print(f"✅ Emergency patterns valid. Found {len(patterns)} APPROVED patterns.")
    except RuleLoadError as e:
        print(f"❌ Emergency patterns validation failed: {e}")
        has_errors = True
    except Exception as e:
        print(f"❌ Unexpected error validating patterns: {e}")
        has_errors = True

    if has_errors:
        print("\nValidation FAILED.")
        return 1

    print("\nValidation PASSED.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
