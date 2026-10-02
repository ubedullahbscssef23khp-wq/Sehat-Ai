# SehatAI: Final Demo Recording Script

## 1. Recording Timeline & Screen Actions

**0–8 sec: Problem / Opening**
*   **Exact Screen:** Solid, high-contrast dark blue background. 
*   **Exact UI Action:** Text fades in: "Language barriers cause miscommunication in healthcare." followed by "SehatAI: Assistive Healthcare Navigation."
*   **Narration:** "In Pakistan, language barriers often mean vital medical details are lost in translation. SehatAI bridges this gap."
*   **Duration:** 8s
*   **Transition:** Fade to SehatAI landing page.

**8–18 sec: Open SehatAI**
*   **Exact Screen:** SehatAI browser window, clean state.
*   **Exact UI Action:** Cursor moves smoothly over the primary input field.
*   **Narration:** "SehatAI provides an assistive pre-screening interface, empowering users to clearly articulate their health concerns."
*   **Duration:** 10s
*   **Transition:** Direct cut to language selector.

**18–28 sec: Multilingual Capability**
*   **Exact Screen:** SehatAI UI. Overlay label appears: "Multilingual".
*   **Exact UI Action:** Cursor clicks the language dropdown. Selects 'Urdu', UI switches to RTL. Selects 'Sindhi', UI updates.
*   **Narration:** "It seamlessly supports English, Urdu, and Sindhi, dynamically adapting to Right-to-Left layouts for a native experience."
*   **Duration:** 10s
*   **Transition:** Direct cut to input field in Urdu.

**28–43 sec: User Input (Synthetic Scenario)**
*   **Exact Screen:** SehatAI chat interface (Urdu). Overlay label: "DEMO / SYNTHETIC DATA".
*   **Exact UI Action:** Type synthetic symptom in Urdu: "مجھے شدید سر درد ہے" (I have a severe headache). Click send. 
*   **Narration:** "A user describes their symptoms in their preferred language. The system processes the input..."
*   **Duration:** 15s
*   **Transition:** Continuous.

**43–55 sec: Focused Follow-up**
*   **Exact Screen:** SehatAI chat interface.
*   **Exact UI Action:** The AI generates a contextual follow-up question. Cursor hovers over the response.
*   **Narration:** "...and asks focused follow-up questions to generate a structured case, without ever attempting to diagnose."
*   **Duration:** 12s
*   **Transition:** Fade to Architecture Insert.

**55–65 sec: Architecture / Safety Boundary**
*   **Exact Screen:** Architecture Insert Graphic. Overlay label: "Deterministic Safety".
*   **Exact UI Action:** Highlight the 'LLM' box (Language/Extraction) visually separated from a locked 'Deterministic Safety Engine' box (Triage).
*   **Narration:** "Crucially, the LLM handles language, not medical decisions. A strict deterministic safety engine controls all triage and red-flag evaluation."
*   **Duration:** 10s
*   **Transition:** Fade back to SehatAI chat interface.

**65–76 sec: Guided Response**
*   **Exact Screen:** SehatAI chat interface.
*   **Exact UI Action:** The system displays a guided, non-diagnostic next step.
*   **Narration:** "This ensures the user receives safe, provenance-controlled guidance. SehatAI assists users in navigating toward an appropriate next step."
*   **Duration:** 11s
*   **Transition:** Cut to "View Summary" button.

**76–85 sec: Clinician-Ready Summary**
*   **Exact Screen:** SehatAI Clinician Summary Drawer. Overlay label: "Clinician Handoff".
*   **Exact UI Action:** Cursor clicks 'View Summary', scrolls the structured data, and highlights the 'Copy/Print' buttons. 
*   **Narration:** "The interaction is distilled into a Clinician-Ready Summary. This standardizes the handoff, ensuring doctors receive structured, safe data."
*   **Duration:** 9s
*   **Transition:** Fade to End Card.

**85–90 sec: Responsible-AI Closing**
*   **Exact Screen:** End Card Graphic. Overlay label: "Assist, Don't Diagnose".
*   **Exact UI Action:** Static display of the end card text.
*   **Narration:** "SehatAI: Assistive navigation with human-in-the-loop safety."
*   **Duration:** 5s
*   **Transition:** Fade to black.

---

## 2. Synthetic Demo Scenario
*   **Condition:** The scenario must explicitly display a "DEMO / SYNTHETIC DATA" watermark overlay in the recording software.
*   **Input:** User selects Urdu and inputs: "مجھے شدید سر درد ہے" (I have a severe headache).
*   **Expected Output:** The system asks a clarifying question regarding onset/severity, demonstrating language processing without rendering a diagnosis. 

---

## 3. Architecture Insert Specification
**Visual Structure:**
*   **Top Left (LLM):** Box labeled "Language Processing & Extraction".
*   **Bottom Right (Safety Engine):** Box labeled "Deterministic Safety & Triage" (rendered as a solid lock or shield).
*   **Action:** An arrow points from the LLM to the Safety Engine. A giant "NOT TRIAGE AUTHORITY" red slash is drawn over the LLM box. 
*   **Bottom Text:** "Human Clinical Review Required for Medical Content Activation."

---

## 4. End Card Specification
**Visual Structure:**
*   **Title:** SEHATAI
*   **Subtitle:** Multilingual AI-Assisted Healthcare Navigation
*   **Ethos:** Assist. Don't Diagnose.
*   **Governance Footer:** *Clinical activation is gated by qualified human clinical review.*

---

## 5. Screen Recording Checklist
### Before Recording
- [ ] Clean browser state (incognito/private window).
- [ ] Correct application URL (localhost:3000).
- [ ] No personal information or browser bookmarks visible.
- [ ] No API keys, .env files, or terminal secrets visible on screen.
- [ ] No unrelated browser tabs open.
- [ ] No developer tools or debug output visible.
- [ ] Stable 1080p window size (1920x1080).
- [ ] "DEMO / SYNTHETIC DATA" watermark configured in recording software (OBS, etc.).

### During Recording
- [ ] Use slow, deliberate mouse clicks.
- [ ] Ensure the UI is highly readable.
- [ ] Avoid accidental refreshes or jerky movements.
- [ ] Avoid unnecessary scrolling; keep important UI centered.
- [ ] Strictly follow the 90-second timeline.

### After Recording
- [ ] Verify absolutely no personal data was captured.
- [ ] Verify no API keys or secrets were exposed.
- [ ] Verify the audio is clear, leveled, and free of background noise.
- [ ] Verify no unsupported medical claims (diagnosis, treatment) were made or displayed.
- [ ] Verify the total duration is precisely 90 seconds.
