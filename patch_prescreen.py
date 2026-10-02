import sys
path = 'backend/app/safety/prescreen.py'
content = open(path).read()
new_content = content.replace(
'''from __future__ import annotations

from app.models import EmergencyPattern


def evaluate_prescreen(patterns: list[EmergencyPattern], text: str) -> list[EmergencyPattern]:
    """Return the patterns whose phrase occurs in the text (case-insensitive).
    Matches keep pattern order for stable, explainable results.
    """
    folded = text.casefold()
    return [pattern for pattern in patterns if pattern.pattern.casefold() in folded]''',
'''from __future__ import annotations
import unicodedata

from app.models import EmergencyPattern


def _normalize(text: str) -> str:
    return unicodedata.normalize("NFC", text).casefold()


def evaluate_prescreen(patterns: list[EmergencyPattern], text: str) -> list[EmergencyPattern]:
    """Return the patterns whose phrase occurs in the text (case-insensitive).
    Matches keep pattern order for stable, explainable results.
    """
    folded = _normalize(text)
    return [pattern for pattern in patterns if _normalize(pattern.pattern) in folded]'''
)
open(path, 'w').write(new_content)
print("patched")
