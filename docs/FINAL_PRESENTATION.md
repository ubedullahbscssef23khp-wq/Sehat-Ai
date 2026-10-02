# SehatAI: Final Hackathon Presentation

**Competition:** Alibaba Cloud AI Hackathon Pakistan 2026 - Healthcare Track

---

## Slide 1 — SEHATAI

**Title:** SehatAI
**Subtitle:** Multilingual AI-Assisted Healthcare Navigation

**Value Proposition:**
Bridging the healthcare communication gap by structuring multilingual symptom reports for seamless clinician handoff.

**Visual:**
Premium, clean healthcare + AI visual identity. Soft blue/white gradient background with a minimal line-art representation of a conversation bridging a gap.
**Speaker Notes:**
*Welcome, everyone. We are presenting SehatAI, an AI-assisted healthcare navigation platform built specifically for the linguistic diversity of Pakistan.*

---

## Slide 2 — THE PROBLEM

**Title:** The Communication Gap

**Content:**
*   **Language Barriers:** Patients struggle to clearly articulate complex symptoms in a clinical setting.
*   **Fragmented Information:** Crucial details are often lost in translation or forgotten during consultations.
*   **Safety Risks:** Unstructured symptom reporting can lead to delays in triage and care.

**Visual:**
A stark, high-contrast infographic showing a fractured line of communication between a patient and a medical professional.
**Speaker Notes:**
*In Pakistan, language barriers are a critical issue. When patients cannot clearly explain their health concerns, vital details get lost, leading to unstructured communication and potential delays in care.*

---

## Slide 3 — THE SOLUTION

**Title:** Assistive Healthcare Navigation

**Content:**
*   **Input:** Users describe symptoms naturally in their preferred language.
*   **Focused Follow-ups:** The system asks targeted questions to complete the picture.
*   **Structured Case:** Unstructured dialogue is transformed into organized data.
*   **Safety-Oriented Triage:** A strict, non-AI engine determines the safest next step.

**Key Ethos:** "Assist, don't diagnose."

**Visual:**
A simple, clean four-step horizontal flow diagram showing the transformation from natural text to a structured summary.
**Speaker Notes:**
*Our solution is SehatAI. It takes natural language input, asks focused follow-up questions, and generates a structured clinical case. Crucially, SehatAI is designed to assist communication, never to diagnose.*

---

## Slide 4 — HOW IT WORKS

**Title:** Architecture: The Safety Boundary

**Content (Diagram):**

```text
USER
  ↓
TEXT / VOICE
  ↓
LANGUAGE PROCESSING
  ↓
STRUCTURED CASE
  ↓
[ DETERMINISTIC SAFETY / RED-FLAG ENGINE ]
  ↓
DETERMINISTIC TRIAGE
  ↓
GUIDED RESPONSE
  ↓
CLINICIAN-READY SUMMARY
```

**Content (Roles):**
*   **LLM Role:** Language understanding, extraction, and phrasing. (LLM ≠ TRIAGE AUTHORITY).
*   **RAG / Knowledge:** Provenance-controlled medical guidance.
*   **Human Clinical Review:** Mandatory gate before clinical activation.

**Visual:**
The architecture diagram above. Make the `[ DETERMINISTIC SAFETY / RED-FLAG ENGINE ]` box a distinct, solid color (e.g., deep blue) to visually enforce the boundary.
**Speaker Notes:**
*Here is how it works under the hood. The LLM is strictly a language processor. Once it builds a structured case, it hits a hard deterministic safety boundary. The AI never controls triage—our deterministic engine does.*

---

## Slide 5 — AI + DETERMINISTIC SAFETY

**Title:** Safety-First Engineering

**Content:**
*   **Language vs. Logic:** The LLM handles phrasing; deterministic logic handles safety-critical decisions.
*   **Output Policy:** Strict filtering prevents unsafe medical claims.
*   **Provenance Control:** All clinical knowledge is sourced and tracked.
*   **Governance Gate:** Clinical activation is gated by qualified human clinical review.

**Visual:**
A "lock and key" or "shield" icon emphasizing the protective boundary between the generative AI and the clinical logic.
**Speaker Notes:**
*We treat safety as an engineering constraint. The LLM cannot hallucinate because an output policy and a deterministic engine block it. Furthermore, clinical activation is gated by qualified human clinical review.*

---

## Slide 6 — MULTILINGUAL EXPERIENCE

**Title:** Built for Pakistan's Diversity

**Content:**
*   **Languages:** English, Urdu, Sindhi
*   **Dynamic Layout:** Full RTL (Right-to-Left) support
*   **Flexibility:** Mixed-script input handling
*   **Contextual:** Localized follow-up phrasing

**Visual:**
Three clean, elevated mobile UI mockups side-by-side, displaying the exact same chat interface seamlessly localized in English, Urdu, and Sindhi.
**Speaker Notes:**
*SehatAI speaks the language of the patient. We fully support English, Urdu, and Sindhi, complete with dynamic Right-to-Left layout switching and mixed-script handling.*

---

## Slide 7 — CLINICIAN HANDOFF

**Title:** The Clinician-Ready Summary

**Content:**
*   **Structured View:** Transforms chat into a concise medical timeline.
*   **Safety Flags:** Prominently displays triggered safety rules and triage decisions.
*   **Seamless Handoff:** One-click copy or print functionality for the user to take to the clinic.

**Visual:**
A high-resolution screenshot of the actual Clinician-Ready Summary drawer from the app, highlighting the print and copy buttons.
**Speaker Notes:**
*The ultimate goal of the interaction is this: The Clinician-Ready Summary. It structures the timeline and flags safety concerns, giving the doctor exactly what they need in seconds. The patient can print it or copy it right to their clipboard.*

---

## Slide 8 — PRIVACY + RESPONSIBLE AI

**Title:** Trust and Traceability

**Content:**
*   **Privacy:** Local persistence; hashed traces; strict environment-based credentials.
*   **Assistive Focus:** Explicitly non-diagnostic; reinforces human clinical responsibility.
*   **Provenance:** All medical knowledge is provenance-controlled.
*   **Governance:** *Clinical activation is gated by qualified human clinical review.*

**Visual:**
Minimalist icons representing privacy (a subtle eye or lock) alongside the responsible AI ethos.
**Speaker Notes:**
*We prioritize privacy with local data persistence. Because SehatAI is an assistive tool, we enforce strict responsible AI guidelines. As a rule, clinical activation is gated by qualified human clinical review.*

---

## Slide 9 — ENGINEERING & RELIABILITY

**Title:** Proven Reliability

**Content:**
*   **341** Backend tests passed
*   **73** Frontend tests passed
*   **47** Mypy source files clean
*   **PASSING** Production build

**Visual:**
Large, bold typography for the numbers. Clean, structured metric layout.
**Speaker Notes:**
*We built SehatAI to be robust. We are backing our safety claims with rigorous engineering: 341 backend tests, 73 frontend tests, and perfectly clean static type checking.*

---

## Slide 10 — IMPACT + FUTURE

**Title:** Looking Forward

**Current Value:**
*   Easier multilingual symptom communication.
*   Structured, safe clinician handoff.

**Future Direction:**
*   Qualified clinical review of staged medical content.
*   Expansion to additional reviewed languages and dialects.
*   Broader healthcare navigation workflows.

**Visual:**
A clean, forward-looking visual (e.g., a subtle rising curve or a minimalist medical cross).
**Speaker Notes:**
*Today, SehatAI structures communication and bridges language gaps safely. Tomorrow, with qualified clinical review, we will activate deep medical knowledge pathways. Thank you.*
