# Sehat AI — Development Plan

**Project:** Sehat AI — AI-assisted healthcare guidance & symptom triage
**Context:** Alibaba Cloud AI Hackathon Pakistan 2026
**Companion doc:** `ARCHITECTURE.md` (full architecture, data models, flows)

---

## 1. Goal of the first demonstrable version

A reviewer can hold a short conversation with Sehat AI in English, Urdu, or Sindhi:
describe symptoms → receive focused follow-up questions → get a triage-level
recommendation with a clear next action, evidence citations, and an unmissable
"not a diagnosis / see a professional" boundary — and, for urgent cases, see a
clinician-ready case summary. The safety-critical logic behind that recommendation
is deterministic, version-controlled, and unit-tested.

## 2. Architecture overview (summary)

React + Vite + TypeScript SPA → FastAPI backend (single process) → SQLite.
Backend modules: `api`, `conversation`, `language`, `extraction`, `safety`,
`triage`, `knowledge`, `llm`, `persistence`, `core`.

Hard invariant: **LLM is used for language understanding and phrasing only.
Safety screening, red-flag evaluation, and triage decisions are pure deterministic
Python driven by curated, version-controlled rules.** See `ARCHITECTURE.md` §8.

## 3. Modules (responsibility one-liners)

| Module | Responsibility | LLM? |
|---|---|---|
| `api` | Thin HTTP endpoints, request validation, error mapping | No |
| `conversation` | Session state machine: COLLECTING → ASSESSING → GUIDED → ESCALATED → CLOSED | No |
| `language` | Detect en/ur/sd incl. Roman Urdu; script/RTL metadata | No |
| `extraction` | Free text → validated `StructuredCase`; report gaps/confidence | Yes |
| `safety` | Emergency pre-screen + red-flag rule engine (YAML rules) | **No — deterministic** |
| `triage` | Compute `TriageDecision` from structured data + fired rules | **No — deterministic** |
| `knowledge` | Curated content with provenance; lexical retrieval; citations | No |
| `llm` | Provider abstraction (DashScope/Mock), prompt templates, structured-output validation, decision-trace recording | Provider only |
| `persistence` | Sessions, messages, cases, traces in SQLite via SQLAlchemy | No |
| `core` | Typed settings, structured JSON logging, error types, request IDs | No |

## 4. Dependencies — selected and why

Kept deliberately minimal (principle: no dependency installed "just in case").

**Backend (Python 3.11+)**

| Package | Why |
|---|---|
| `fastapi` | HTTP API, validation integration, OpenAPI contract for the frontend |
| `uvicorn` | ASGI server (dev/demo) |
| `pydantic` + `pydantic-settings` | Data validation everywhere; typed env config |
| `httpx` | Async calls to the LLM endpoint (OpenAI-compatible HTTP) |
| `sqlalchemy` (2.x) | SQLite now, Postgres later without model rewrite |
| `pyyaml` | Red-flag rules and knowledge metadata files |
| `pytest` (+ `pytest-asyncio`) | Backend test suite |

**Frontend (Node LTS)**

| Package | Why |
|---|---|
| `react`, `react-dom` | UI |
| `typescript` | Typed API client and state |
| `vite` + `@vitejs/plugin-react` | Minimal fast toolchain |

**Rejected for v1:** LangChain (unnecessary abstraction layer), vector DBs
(corpus too small; lexical retrieval is explainable), Redis/queues/Docker
(no demonstrated need), UI frameworks (plain CSS is enough for v1),
auth libraries (anonymous sessions for the demo — see §7).

## 5. Implementation phases

Every phase ends in a testable, demoable state. Nothing from a later phase is
pre-built earlier.

### Phase 0 — Repository foundation
Backend skeleton (`core` settings/logging, health endpoint), frontend skeleton
(Vite app hitting the health endpoint), `.env.example` wired, test harnesses green.

**Acceptance criteria**
- [ ] `pytest` runs with a passing smoke test; `vite build` succeeds.
- [ ] App fails fast at startup if a required env var is missing.
- [ ] Structured JSON log lines include a request ID for API calls.

### Phase 1 — Domain models + deterministic safety core (the heart)
`models/`, `safety/` rule engine + rule YAML schema, `triage/` engine.
Pure Python, zero I/O, zero LLM.

**Acceptance criteria**
- [ ] Rules load from YAML; every rule requires `source` and `review_date`
      (loader rejects files missing them).
- [ ] Engine maps cases to all five outcomes: EMERGENCY / URGENT_SAME_DAY /
      ROUTINE / SELF_CARE / NEEDS_MORE_INFO.
- [ ] Every fired decision returns the exact rule IDs that caused it.
- [ ] Unit tests cover each level, rule combinations, and conflict handling
      (highest rule wins); safety tests must never be skipped/disabled.
- [ ] Rule/knowledge content is curated only from authoritative public health
      sources — no invented clinical claims. Content added incrementally with citations.

### Phase 2 — LLM abstraction + structured extraction
`llm/` (DashScope provider + MockProvider), prompt template registry,
`extraction/` with strict schema validation and one retry.

**Acceptance criteria**
- [ ] `MockProvider` lets the whole pipeline run offline and in tests.
- [ ] Extraction produces a valid `StructuredCase` from sample English and Urdu
      texts (tested against MockProvider).
- [ ] Malformed model output → retry once → graceful "please rephrase" path; test-covered.
- [ ] Every LLM call writes a `DecisionTrace` entry (template ID, model, latency, validity).
- [ ] API key comes only from environment; no key in code, prompts, or tests.

### Phase 3 — Conversation orchestration + persistence
`conversation/` state machine, follow-up question generation (fields chosen
deterministically, phrasing by LLM), SQLite persistence of sessions/messages/traces.

**Acceptance criteria**
- [ ] Multi-turn API conversation reaches a triage decision end-to-end using MockProvider.
- [ ] Follow-ups ask only about computed `missing_fields`; max 2 rounds, then
      best-effort triage marked as limited-confidence.
- [ ] Session state survives server restart (SQLite).
- [ ] Emergency pre-screen shortcuts the loop: emergency-pattern input gets the
      emergency path even if extraction hasn't completed.

### Phase 4 — Knowledge base + guided response composition
`knowledge/` loader with provenance enforcement, lexical retrieval,
response composition with output-policy filter and mandatory disclaimer injection.

**Acceptance criteria**
- [ ] Knowledge files without `source` + `date_reviewed` fail to load (test).
- [ ] Guidance responses include ≥1 citation when relevant content exists, and an
      explicit "no reliable information available" note when none exists.
- [ ] Output-policy filter tests prove diagnostic claims ("you have X") and
      medication advice are blocked from final user-facing text.
- [ ] Every response includes server-injected disclaimers; a response lacking
      them fails validation server-side.

### Phase 5 — Frontend chat UI (English first)
Chat thread, language picker, triage result card, evidence list, disclaimer bar,
graceful error/degraded banners. Typed API client aligned with backend OpenAPI.

**Acceptance criteria**
- [ ] Golden path works in the browser: symptom input → follow-ups → guidance card.
- [ ] Emergency result renders distinctly (visual escalation) with emergency services notice.
- [ ] Backend errors/degraded mode show an honest banner, never a silent failure.
- [ ] No triage logic exists in frontend code (review checklist item).

### Phase 6 — Urdu & Sindhi support
RTL layout, `language/` detection incl. Roman Urdu, localized response templates,
localized emergency/disclaimer strings.

**Acceptance criteria**
- [ ] A conversation can be completed in Urdu script and in Roman Urdu.
- [ ] Sindhi supported at the same interface level (content coverage may be
      partial — UI states that honestly).
- [ ] RTL rendering verified for ur/sd; mixed-direction text does not break layout.
- [ ] Emergency and disclaimer strings exist in all three languages (curated, not
      machine-only).

### Phase 7 — Clinician summary + degraded mode
`ClinicianSummary` generation/rendering; templated non-LLM emergency guidance;
full degraded-mode behavior when the LLM is unavailable.

**Acceptance criteria**
- [ ] URGENT/EMERGENCY cases produce a clinician-ready summary (structured case,
      fired rules, timeline, model attribution).
- [ ] With the LLM provider disabled, the app still: pre-screens emergencies,
      triages already-structured data, and returns templated guidance with a
      clear "limited mode" notice (test-covered).
- [ ] No code path silently swallows an external-service failure.

### Phase 8 — Demo hardening
Scripted end-to-end demo scenarios (one per triage level, one per language),
latency sanity pass, runbook for running the demo locally.

**Acceptance criteria**
- [ ] Each scripted scenario passes end-to-end against the real LLM provider.
- [ ] Full conversation round-trips comfortably within demo time budget (~<15s/turn).
- [ ] One-command local startup documented and verified on a clean checkout.

## 6. Testing strategy

| Layer | Approach |
|---|---|
| `safety` + `triage` | Exhaustive pytest unit tests; golden-case table tests; these suites gate every change |
| `extraction` / prompts | Tests against `MockProvider` + recorded fixture responses |
| API | Integration tests with FastAPI TestClient, MockProvider, temp SQLite |
| Degraded modes | Explicit tests with provider disabled/unreachable |
| Frontend | Manual browser verification per phase (Phase 5+); Vitest added only when components justify it |
| LLM live checks | Never in CI; manual only, since outputs are non-deterministic |

Rule of the project: **a change to any safety rule or triage path must add or update
tests in the same change.**

## 7. Security considerations

- Secrets via environment only; `.env` git-ignored; `.env.example` has placeholders only.
- No names/IDs/contacts collected; sessions anonymous; retention configurable.
- All user input length-limited and untrusted; never interpolated into shell/eval/code.
- Prompt injection posture: user text is data, never instructions; extraction schema
  constrains what can flow forward; safety decisions don't come from model prose.
- CORS restricted to the frontend origin; OpenAPI docs off in production mode.
- Dependency list stays minimal and reviewed; no abandoned/heavy frameworks.

## 8. Safety considerations (product level)

- The app never claims to diagnose; language policy (filter + templates) enforces
  "guidance/triage" framing in all three languages.
- Deterministic safety components (§Phase 1) cannot be bypassed by any code path,
  including LLM shortcuts.
- Emergency patterns are checked before and independently of the LLM.
- All medical rule/knowledge content must cite an authoritative public source with a
  review date; un-cited content is rejected by the loaders. (Content curation happens
  during Phases 1/4 from real public health guidance — nothing is invented.)
- Local emergency contact details (e.g., Pakistan's emergency/rescue number) must be
  verified against an official source during implementation before being templated.
- Every AI-mediated decision is reconstructable from `DecisionTrace` records.

## 9. Intentionally NOT built in v1

Voice input/output, real authentication/user accounts, medical imaging, medication
advice, appointment booking, vector-database RAG, Docker/K8s, multiple backend
services, background queues, analytics pipelines. All are documented extension
points (see `ARCHITECTURE.md` §11), none are pre-built.

## 10. Decision log (irreversible-ish choices, with reasoning)

| # | Decision | Reasoning / reversibility |
|---|---|---|
| D1 | Separate SPA + API (not full-stack framework) | Physical separation of conversational AI from the safety engine; safety core stays a pure library. Reversible, but costly — revisit only if ops simplicity ever outweighs it. |
| D2 | SQLite → SQLAlchemy | Zero-infra demo; models portable to Postgres. Easily reversible. |
| D3 | No LangChain; direct OpenAI-compatible HTTP to DashScope | Fewer moving parts, full prompt/trace control, provider-swappable. Reversible. |
| D4 | YAML rule engine (not code-only, not a rules DSL) | Human/clinician-reviewable, version-controlled diffs; a custom DSL would be premature. Rule *schema* may evolve — versioning field is planned. |
| D5 | Lexical retrieval over curated corpus for v1 | Corpus is small and must be curated anyway; explainability beats recall here. Vector search can slot behind `KnowledgeRetriever` later. |
| D6 | Anonymous sessions, no auth, no personal data | Shrinks safety/legal surface for a demo. Auth becomes mandatory before any real persistent personal health data. |

## 11. Definition of done (hackathon demo)

A live local demo where a reviewer's symptom story in any of the three languages
ends in a correct-level triage card with cited guidance, mandatory disclaimers,
a clinician summary for urgent cases, and a demonstrable deterministic safety
core (rule IDs + tests) behind every decision.
