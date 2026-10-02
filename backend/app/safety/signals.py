"""Version-controlled red-flag signal allowlist (ARCHITECTURE.md §8).

StructuredCase.red_flag_signals MUST be validated against this explicit
allowlist before any RedFlagRule can depend on those signals.

This prevents the LLM from hallucinating actionable red-flag signals.
"""

from __future__ import annotations

# The explicit version-controlled allowlist.
# Must remain empty in production unless explicitly approved non-clinical
# identifiers exist. 
_ALLOWED_SIGNALS: set[str] = set()

def validate_red_flag_signals(signals: list[str]) -> list[str]:
    """Return only the signals that are present in the allowlist.
    
    Unknown/unrecognized signals fail closed and are discarded.
    """
    return [signal for signal in signals if signal in _ALLOWED_SIGNALS]
