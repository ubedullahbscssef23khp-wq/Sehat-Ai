# SehatAI - Final Demo & Presentation Plan

## 90-Second Demo Sequence

*   **0–10 sec:** 
    *   *Action:* Title slide or establishing shot of the problem (language barriers). 
    *   *Visible:* "SehatAI: Bridging the Healthcare Communication Gap." 
    *   *Narrator:* "In Pakistan, language barriers often mean vital medical details are lost in translation between patients and doctors. SehatAI bridges this gap."
*   **10–20 sec:** 
    *   *Action:* Screen recording of the SehatAI landing page.
    *   *Visible:* Clean, accessible UI with a prominent text/voice input field.
    *   *Narrator:* "Our platform provides an assistive, multilingual pre-screening interface."
*   **20–30 sec:** 
    *   *Action:* Click the language selector and switch from English to Urdu, then to Sindhi.
    *   *Visible:* UI instantly adapting to RTL (Right-to-Left) and updating labels.
    *   *Narrator:* "It seamlessly supports English, Urdu, and Sindhi, dynamically adapting the layout."
*   **30–45 sec:** 
    *   *Action:* Type a synthetic symptom (e.g., "I have a severe headache") in Urdu. Press enter. Show the AI asking a targeted follow-up question.
    *   *Visible:* Conversation interface; user message and LLM-generated follow-up.
    *   *Narrator:* "When a user describes their symptoms, our AI processes the language and asks focused follow-ups to gather a complete clinical picture."
*   **45–58 sec:** 
    *   *Action:* Show a visual overlay of the architecture, focusing on the deterministic boundary.
    *   *Visible:* Red-flag engine blocking LLM triage.
    *   *Narrator:* "Behind the scenes, the AI never makes medical decisions. A strict deterministic safety engine controls all triage and identifies emergency red flags."
*   **58–70 sec:** 
    *   *Action:* Return to the conversation view; show a non-diagnostic, guided response.
    *   *Visible:* Safe, assistive response without medical diagnosis.
    *   *Narrator:* "This ensures the system provides safe, provenance-controlled guidance without hallucinating diagnoses."
*   **70–80 sec:** 
    *   *Action:* Click the "View Summary" button to open the Clinician-Ready Summary drawer.
    *   *Visible:* Structured timeline, extracted symptoms, and safety flags.
    *   *Narrator:* "The interaction is distilled into a standardized Clinician-Ready Summary."
*   **80–87 sec:** 
    *   *Action:* Click the "Copy" or "Print" button on the summary.
    *   *Visible:* Clipboard success toast or print dialog.
    *   *Narrator:* "Designed for seamless physical or digital handoff to medical professionals."
*   **87–90 sec:** 
    *   *Action:* Show the disclaimer / Responsible AI footer.
    *   *Visible:* "Assistive tool. Not for medical diagnosis."
    *   *Narrator:* "SehatAI: Empowering patients, strictly protecting the human-in-the-loop safety boundary."

## Narrator Script

"In Pakistan, language barriers often mean vital medical details are lost in translation between patients and doctors. SehatAI bridges this gap. 

Our platform provides an assistive, multilingual pre-screening interface. It seamlessly supports English, Urdu, and Sindhi, dynamically adapting the layout. 

When a user describes their symptoms, our AI processes the language and asks focused follow-ups to gather a complete clinical picture. 

Behind the scenes, the AI never makes medical decisions. A strict deterministic safety engine controls all triage and identifies emergency red flags. This ensures the system provides safe, provenance-controlled guidance without hallucinating diagnoses. 

The interaction is distilled into a standardized Clinician-Ready Summary, designed for seamless physical or digital handoff to medical professionals. 

SehatAI: Empowering patients, strictly protecting the human-in-the-loop safety boundary."

## Presentation Slides (10 Slides)

**Slide 1: SehatAI**
*   Title: Multilingual AI-Assisted Healthcare Navigation
*   Bullets: Bridging communication gaps in Pakistan; Non-diagnostic pre-screening; Seamless clinician handoff.
*   Visual: Hero screenshot of the app interface.
*   Note: Introduce the project and the team.

**Slide 2: The Problem**
*   Title: The Problem
*   Bullets: Linguistic diversity causes details to be lost; Unstructured symptom reporting; Diagnostic delays and safety risks.
*   Visual: Icon representing language barriers in a clinical setting.
*   Note: Emphasize that miscommunication is a systemic issue.

**Slide 3: Our Solution**
*   Title: Our Solution
*   Bullets: Multilingual pre-screening; Supports English, Urdu, Sindhi; Structures symptom reports organically.
*   Visual: UI mockup showing language options.
*   Note: Present SehatAI as an assistive bridge, not a replacement for doctors.

**Slide 4: How SehatAI Works**
*   Title: How SehatAI Works
*   Bullets: Natural language input; LLM-driven targeted follow-ups; Generation of structured case data.
*   Visual: Conversation flow snippet.
*   Note: Explain the user journey from symptoms to structured data.

**Slide 5: AI + Deterministic Safety**
*   Title: AI + Deterministic Safety
*   Bullets: LLM processes language only; Deterministic engine handles triage; Strict red-flag allowlist prevents hallucinations.
*   Visual: Architecture flow diagram focusing on the safety boundary.
*   Note: Crucial slide: explain that AI does NOT diagnose.

**Slide 6: Multilingual Experience**
*   Title: Multilingual Experience
*   Bullets: Dynamic RTL layout; Culturally aware language models; Mixed-script text capability.
*   Visual: Side-by-side screenshots of English and Urdu UI.
*   Note: Highlight the technical implementation of localization.

**Slide 7: Clinician Handoff**
*   Title: Clinician Handoff
*   Bullets: Standardized medical summaries; Copy and print functionality; Preserves details for the doctor.
*   Visual: Screenshot of the Clinician-Ready Summary card.
*   Note: Show how it benefits the healthcare provider.

**Slide 8: Privacy + Responsible AI**
*   Title: Privacy + Responsible AI
*   Bullets: Local persistence; No unnecessary health data logging; Clinical activation gated by human review.
*   Visual: Privacy lock icon and disclaimer text.
*   Note: Reiterate the strict clinical governance and privacy stance.

**Slide 9: Engineering & Reliability**
*   Title: Engineering & Reliability
*   Bullets: 341 backend tests passed; 73 frontend tests passed; 47 mypy source files clean; Robust CI/CD build process.
*   Visual: Screenshot of green test terminal output.
*   Note: Prove the application's stability and engineering rigor.

**Slide 10: Impact + Future Direction**
*   Title: Impact + Future Direction
*   Bullets: Empowering patients today; Future HMIS integration; Expanding voice and dialect support.
*   Visual: Forward-looking graphic or team photo.
*   Note: Conclude with the vision for SehatAI.

## Architecture Visual

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


LLM Role:
→ language understanding
→ structured extraction
→ follow-up phrasing
→ response phrasing

RAG / KNOWLEDGE:
→ provenance-controlled guidance

HUMAN CLINICAL REVIEW:
→ required before clinical activation
```
*(Make the diagram visually clear that the LLM is NOT the triage authority.)*

## Engineering Evidence
*   Backend tests: 341 passed
*   Frontend tests: 73 passed
*   Mypy: 47 source files clean
*   Frontend build: PASS

## Responsible AI Section
SehatAI is an assistive, not diagnostic, tool. It strictly maintains a deterministic safety boundary where an LLM is used solely for language processing, never for medical triage. Medical knowledge is provenance-controlled, and clinical activation is explicitly gated by qualified human clinical review. The platform prioritizes privacy through local persistence and trace protection, ensuring human clinical responsibility remains paramount.

## Synthetic Demo Data
**[DEMO / SYNTHETIC DATA]**
*   Symptom Input (Urdu): "مجھے شدید سر درد ہے" (I have a severe headache)
*   Follow-up (English translation): "When did this headache start, and is it accompanied by any visual changes?"
*(Note: Do not use staged BEFAST clinical content as if it were clinically approved.)*

## Video Shot List
*   **Shot 1 (0:00-0:10):** Slide/Graphic. Narration: Problem introduction. Transition: Fade to UI.
*   **Shot 2 (0:10-0:20):** Screen recording of SehatAI landing page. Narration: Solution introduction. Transition: Cut to language menu.
*   **Shot 3 (0:20-0:30):** Screen recording of language switching (English -> Urdu -> Sindhi). Narration: Multilingual support. Transition: Cut to chat interface.
*   **Shot 4 (0:30-0:45):** Screen recording of typing synthetic symptom and receiving a follow-up. Narration: Language processing & follow-ups. Transition: Fade to Architecture diagram.
*   **Shot 5 (0:45-0:58):** Architecture graphic highlighting deterministic safety. Narration: Safety boundary. Transition: Cut back to chat.
*   **Shot 6 (0:58-0:70):** Screen recording of a guided, non-diagnostic response. Narration: Safe guidance. Transition: Cut to Clinician Summary.
*   **Shot 7 (0:70-0:80):** Screen recording opening the Clinician Summary. Narration: Handoff. Transition: Highlight copy/print buttons.
*   **Shot 8 (0:80-0:87):** Screen recording of clicking 'Print'. Narration: Seamless integration. Transition: Fade to disclaimer.
*   **Shot 9 (0:87-0:90):** Close-up on the medical disclaimer. Narration: Responsible AI closing. Transition: Fade to black.

## Submission Description
SehatAI is a multilingual healthcare navigation and pre-screening platform designed for the diverse linguistic landscape of Pakistan. It bridges the communication gap between patients and healthcare providers by offering an assistive interface in English, Urdu, and Sindhi. Users can describe their symptoms naturally, and an LLM—acting strictly as a language processor—asks focused follow-ups to generate a structured case. Crucially, SehatAI employs a deterministic safety engine that handles all triage and emergency red-flag identification, ensuring the AI never makes autonomous medical decisions. The interaction results in a Clinician-Ready Summary that can be printed or copied for seamless physical handoff. Built with over 400 automated tests and a strict "safety-first" architecture, SehatAI explicitly gates clinical content activation behind qualified human review. It empowers patients to articulate their health concerns accurately while strictly preserving the human-in-the-loop diagnostic boundary.
