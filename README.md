# SehatAI

**Bridging the Healthcare Communication Gap in Pakistan.**

## Problem
In Pakistan, language barriers and a lack of standardized medical intake often prevent patients from clearly communicating their symptoms to healthcare providers. Vital details are lost in translation, leading to diagnostic delays and compromised patient safety.

## Solution
SehatAI is a multilingual healthcare navigation and pre-screening platform designed for the diverse linguistic landscape of Pakistan. It acts as an assistive bridge between patients and clinicians, structuring symptom reports organically without making medical diagnoses.

## Key Features
*   **Multilingual Experience:** Full support for English, Urdu, and Sindhi, with dynamic RTL (Right-to-Left) and mixed-script capability.
*   **Assistive Pre-screening:** Empowers patients to describe symptoms naturally (via text or voice) while structuring the data for clinicians.
*   **Clinician Handoff:** Generates a standardized, clinician-ready summary that can be quickly reviewed, printed, or copied.
*   **Safety-First:** Employs a deterministic safety engine that identifies red flags and guides triage without relying on AI for medical decisions.

## How SehatAI Works
1.  **User Input:** The user describes their symptoms in their preferred language.
2.  **Language Processing:** The LLM processes the input to extract structured case details.
3.  **Focused Follow-ups:** The system asks targeted questions to complete the clinical picture.
4.  **Deterministic Safety & Triage:** A strict deterministic engine evaluates the extracted symptoms against a provenance-controlled allowlist.
5.  **Guided Response & Summary:** The system provides non-diagnostic guidance and generates a clinician-ready summary.

## Architecture

```text
USER
 ↓
TEXT / VOICE
 ↓
LANGUAGE PROCESSING
 ↓
STRUCTURED CASE
 ↓
DETERMINISTIC SAFETY / RED-FLAG ENGINE
 ↓
DETERMINISTIC TRIAGE
 ↓
GUIDED RESPONSE
 ↓
CLINICIAN-READY SUMMARY
```

*   **AI/LLM Role:** The LLM is strictly restricted to language processing, symptom extraction, and phrasing. It does not perform clinical triage.
*   **Deterministic Safety Boundary:** The deterministic engine overrides and controls all safety decisions, ensuring the LLM cannot hallucinate diagnoses or bypass safety protocols.
*   **Knowledge/RAG Governance:** All clinical guidance is provenance-controlled.
*   **Human Clinical Review:** Clinical activation is gated by qualified human clinical review. The production clinical corpus remains empty until explicitly approved.

## Privacy & Responsible AI
*   **Privacy:** Employs local persistence. Raw health text is not unnecessarily logged, and no secrets or API keys are exposed.
*   **Assistive Purpose:** The platform explicitly disclaims diagnostic capability, reinforcing the clinician's role and ensuring a safe human-in-the-loop boundary.

## Testing & Reliability Evidence
Engineered for reliability with a heavily verified test suite:
*   **Backend tests:** 341 passed
*   **Frontend tests:** 73 passed
*   **Mypy type checking:** 47 source files clean
*   **Frontend build:** PASS

## Current Clinical-Review Status
*   **Clinical activation is gated by qualified human clinical review.**
*   All clinical content (e.g., BEFAST stroke recognition) is currently staged (`PENDING_DOMAIN_REVIEW`) and will not be activated in production until a qualified clinician formally approves it. Production EmergencyPattern and KnowledgeEntry counts are strictly `0`.

## Demo Instructions
1.  Open the application in a modern web browser.
2.  Select your preferred language (English, Urdu, or Sindhi).
3.  Enter a sample symptom.
4.  Observe the LLM-driven follow-up questions and deterministic triage.
5.  View the Clinician-Ready Summary and test the print/copy handoff.
*(Note: Any clinical content shown during the demo relies on synthetic data or deterministic fallbacks pending human clinical review.)*

## Technology Stack
*   **Frontend:** React, TypeScript, Vite, Tailwind CSS
*   **Backend:** Python, FastAPI, Uvicorn
*   **Language Processing:** @google/genai SDK (Gemini)

## Future Work
*   Integration with hospital HMIS systems.
*   Expansion to additional regional dialects.
*   Full clinical validation and roll-out of verified medical pathways.
