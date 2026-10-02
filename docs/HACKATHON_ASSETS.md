# SehatAI - Hackathon Submission Assets

## Hackathon Project Summary

SehatAI is a multilingual healthcare navigation and pre-screening platform designed for the diverse linguistic landscape of Pakistan, supporting English, Urdu, and Sindhi. It bridges the communication gap between patients and healthcare systems by providing an assistive, non-diagnostic interface where users can describe symptoms via text or voice. An LLM acts solely as a language processor to extract structured data and ask focused follow-up questions, while a strict deterministic safety engine handles triage and identifies emergency red flags. This ensures the AI never makes autonomous medical decisions. SehatAI generates a clinician-ready summary designed for seamless handoff to medical professionals. Built with a 'safety-first' architecture, the system employs strict clinical governance where all medical knowledge and emergency patterns require qualified human clinical review before activation. Local persistence ensures privacy, and empty/failed LLM paths have guaranteed deterministic fallbacks. SehatAI empowers patients to articulate their health concerns accurately while strictly preserving the human-in-the-loop diagnostic boundary.

## Hackathon Demo Script (90-120 seconds)

**[0:00 - 0:15] Problem Introduction**
"Welcome to SehatAI. In Pakistan, language barriers often prevent patients from clearly communicating their symptoms to healthcare providers. Vital details are lost, delaying care. SehatAI solves this."

**[0:15 - 0:30] Interface & Language Switching**
"Our platform supports English, Urdu, and Sindhi. Let's switch to Urdu. The interface seamlessly adapts with full RTL support, ready for mixed-script text or voice input."

**[0:30 - 0:45] User Input & Follow-up**
"A user describes their symptoms—like a severe headache. The LLM processes the language and asks focused follow-up questions to gather a complete structured clinical picture, without ever attempting to diagnose."

**[0:45 - 1:00] Safety Boundary & Guided Response**
"Behind the scenes, our deterministic safety engine takes over. It checks the extracted symptoms against a strict red-flag allowlist. The LLM never decides triage—the deterministic engine does, ensuring safe, guided responses."

**[1:00 - 1:10] Clinician Summary & Handoff**
"The result is this Clinician-Ready Summary. It structures the timeline, symptoms, and flags for quick review by a doctor. Users can print or copy this summary for physical handoff at a clinic."

**[1:10 - 1:20] Responsible AI Closing**
"Clinical activation is gated by qualified human clinical review. With over 400 automated tests, SehatAI is built for reliability. SehatAI: Empowering patients, protecting safety."

## Presentation Outline (10 Slides)

**Slide 1 — SehatAI**
* Title: Bridging the Healthcare Communication Gap in Pakistan
* Multilingual pre-screening and clinical handoff
* Non-diagnostic, assistive AI
* Visual/Demo Element: Hero screen of SehatAI

**Slide 2 — Problem**
* Title: The Communication Barrier
* Linguistic diversity causes details to be lost in translation
* Lack of structured symptom reporting
* Diagnostic delays and compromised safety
* Visual/Demo Element: Statistics or icon representing miscommunication

**Slide 3 — Solution**
* Title: Multilingual Healthcare Navigation
* Supports English, Urdu, and Sindhi
* Structures symptom reports organically
* Designed for seamless clinician handoff
* Visual/Demo Element: UI showing language switching

**Slide 4 — How It Works**
* Title: From Natural Language to Structured Case
* User inputs text/voice symptoms
* AI processes language and asks focused follow-ups
* Generates structured data for the clinician
* Visual/Demo Element: The conversation interface

**Slide 5 — AI + Deterministic Safety**
* Title: Safety-First Architecture
* LLM extracts symptoms, but deterministic engine decides triage
* Strict red-flag allowlist prevents AI hallucinations
* AI is never the final triage authority
* Visual/Demo Element: Architecture flow diagram

**Slide 6 — Multilingual Experience**
* Title: Built for Pakistan
* Dynamic RTL (Right-to-Left) layout
* Mixed-script text and voice input handling
* Culturally aware language models
* Visual/Demo Element: Demo scenario in Urdu/Sindhi

**Slide 7 — Clinician Handoff**
* Title: The Clinician-Ready Summary
* Standardized medical summaries for quick review
* Copy-to-clipboard and print functionality
* Prevents details from getting lost at the clinic
* Visual/Demo Element: The generated clinician summary card

**Slide 8 — Privacy + Responsible AI**
* Title: Protecting Patients
* Local persistence and no unnecessary health data logging
* Closed-session protection and empty/failed LLM fallbacks
* Clinical activation is gated by qualified human clinical review
* Visual/Demo Element: The disclaimer and privacy boundary icons

**Slide 9 — Engineering / Testing**
* Title: Proven Reliability
* Backend tests: 341 passed
* Frontend tests: 73 passed
* Mypy: 47 source files clean
* Visual/Demo Element: Screenshot of green test suites

**Slide 10 — Impact + Future Direction**
* Title: Next Steps
* HMIS integration
* Full clinical validation and review of staged content
* Expanding voice dialect support
* Visual/Demo Element: Closing slide with team/contact info
