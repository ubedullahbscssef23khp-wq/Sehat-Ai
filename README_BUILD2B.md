# BUILD 2B — RED-FLAG SIGNAL ALLOWLIST GOVERNANCE GATE

Successfully completed REQ-001 by implementing a strict, version-controlled allowlist for `StructuredCase.red_flag_signals`.

## Completed Steps:
1. Created `backend/app/safety/signals.py` to define the version-controlled `_ALLOWED_SIGNALS` allowlist.
2. Implemented `validate_red_flag_signals` function to strictly filter unrecognized signals (fail-closed constraint).
3. Integrated `validate_red_flag_signals` into `ConversationOrchestrator.handle_message` right before safety rule evaluation.
4. Added exhaustive unit tests in `backend/tests/test_signal_validation.py`.
5. Updated existing synthetic test signals in the test suite to ensure they use the explicitly approved `TEST_SIGNAL_ALPHA` test identifier, verifying the strict filtering.
6. Ran the test suites and they passed with 100% success rate:
   - Python static typing (`mypy --strict app`) is clear.
   - Backend tests (`pytest`) are all passing (263 tests).
   - Frontend tests pass.
   - Build completes cleanly.

This closes the REQ-001 constraint on the allowlist gate, without adding actual clinical meanings to the signals. The production list remains empty (except for the 2 approved test identifiers), meeting the governance constraint.
