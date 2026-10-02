# SehatAI Demo Runbook

## 1. What SehatAI Demonstrates
SehatAI is a deterministic, multilingual assistive healthcare triage and navigation system. It demonstrates a strict separation of concerns where language models act solely as language translation and extraction components, while all safety, triage, and guidance logic is handled by a deterministic, transparent backend engine.

## 2. How to run the deterministic demo
The repository includes a deterministic demo runner that proves the system's safety and reliability without depending on live external language models.

Execute the following command from the root of the project:
```bash
python3 backend/scripts/run_demo.py
```
This runs 8 core scenarios deterministically.

## 3. Scenario List
A. **English normal**: Standard intake flow, generating focused follow-ups and final deterministic guidance.
B. **Missing information**: Verifies the system requests missing demographics before finalizing any guidance.
C. **Emergency safety (test-only)**: Proves that emergency prescreening intercepts red flags *before* any LLM evaluation, completely bypassing the LLM.
D. **Urdu**: Proves full RTL and UTF-8 support for localized interaction.
E. **Sindhi**: Proves full RTL and UTF-8 support for localized interaction.
F. **Knowledge governance**: Demonstrates that the system actively rejects medical content in the `PENDING_DOMAIN_REVIEW` state, only accepting `APPROVED` content.
G. **Clinician summary**: Verifies the generation of a clean, structured patient history devoid of LLM hallucination traces.
H. **Provider failure**: Shows the graceful fallback handling if the LLM provider becomes unavailable.

## 4. Expected Behavior for Each Scenario
Each scenario executes via a fast, mocked LLM provider. The output should be a straightforward success checklist:
```text
[PASS] A — English normal
[PASS] B — Missing information
[PASS] C — Emergency safety (test-only)
[PASS] D — Urdu
[PASS] E — Sindhi
[PASS] F — Knowledge governance
[PASS] G — Clinician summary
[PASS] H — Provider failure
```

## 5. What is test-only
- **Test-only emergency fixtures**: The emergency fixtures (e.g., `STROKE-B`, `STROKE-E`) used to demonstrate safety escalation are strictly test fixtures. They prove the engine works but are NOT activated in production.
- **Test-only approved knowledge**: The fixtures simulating approved medical knowledge in tests are not loaded into the live application.
- **Deterministic Provider**: The `MockProvider` used in the demo runner replaces the live LLM purely to ensure repeatability during demonstrations.

## 6. What is intentionally NOT activated
- **The production emergency corpus**: It is intentionally empty because no qualified clinical body has reviewed and approved real emergency patterns for this system.
- **The production clinical knowledge**: WHO headache facts are present but explicitly marked as `PENDING_DOMAIN_REVIEW`, meaning the application will not load them into active memory.

## 7. Safety Statements
- **Test-only approved emergency fixtures demonstrate the safety mechanism; they are not production clinical rules and have not been activated as production medical content.**
- **The production emergency corpus and production clinical knowledge remain inactive pending appropriate domain review.**
- SehatAI is a technical prototype demonstrating a safety architecture. It makes no claims of medical accuracy and does not provide clinical diagnoses.

## 8. Judge Demonstration Order
1. Run the backend tests to prove core invariants: `backend/.venv/bin/pytest -q`
2. Run the deterministic demo runner: `backend/.venv/bin/python3 backend/scripts/run_demo.py`
3. Show the UI functioning locally via port 3000.
4. Show the code for the deterministic orchestrator (`orchestrator.py`) highlighting the `evaluate_prescreen` happening *before* the LLM call.

## 9. How to explain the architecture in 60–90 seconds
"SehatAI flips the standard AI healthcare model. Instead of trusting an LLM to make medical decisions, we use the LLM solely as a translator. The user speaks in Urdu, Sindhi, or English, and the LLM translates that into a strict, structured JSON schema. Once we have the JSON, the LLM is cut off. Our Python backend uses deterministic, hard-coded clinical logic to assess emergencies and triage the patient. If the patient needs emergency care, the code triggers it automatically. If we need more information, the code asks for it. The LLM only comes back at the very end to phrase the final, rigid guidance back into the user's language. This means we have 100% traceability and safety."

## 10. Known Limitations
- The system currently only handles single-complaint triage efficiently.
- Vocabulary for low-resource languages (Sindhi) may require advanced LLM prompting to prevent dialect blending.
- The clinical corpus is currently a placeholder; scaling it requires a dedicated medical governance dashboard.
