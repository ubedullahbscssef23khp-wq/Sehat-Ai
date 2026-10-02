# Sehat AI — Architecture

**Status:** Initial architecture pass (2026-08-30), pre-implementation.
**Context:** AI-assisted healthcare guidance and symptom-triage application for the Alibaba Cloud AI Hackathon Pakistan 2026.

---

## 1. What Sehat AI is — and is not

Sehat AI helps a user describe symptoms in their own language (English, Urdu, Sindhi),
understands the description, asks focused follow-up questions, checks safety-critical
signals, and recommends a **next action** (emergency care, same-day care, routine care,
or monitored self-care) together with evidence-backed general information.

**Sehat AI is NOT:**

- Not a diagnostic tool. It never states "you have disease X."
- Not a replacement for a qualified healthcare professional. Every guidance output
  carries this boundary explicitly.
- Not a treatment/prescription engine. It never recommends medications or dosages.

These boundaries are enforced **architecturally** (deterministic output-policy layer),
not only by prompting.

---

## 2. Technology decisions (with rationale)

| Area | Decision | Why |
|---|---|---|
| Frontend | **React + Vite + TypeScript** (SPA) | Chat-style UI needs no SSR; Vite keeps tooling minimal and fast; TypeScript gives a typed API contract; widely understood by humans and AI agents. |
| Backend | **Python 3.11+ with FastAPI** | Best fit for LLM orchestration, NLP, and testable rule logic; async I/O; auto-generated OpenAPI contract that the frontend can type against. |
| Database | **SQLite via SQLAlchemy 2.x** (PostgreSQL-compatible models) | Zero infrastructure for the first demonstrable version; sessions/case history are small; SQLAlchemy keeps the path to Postgres open with no model rewrite. Deliberately NOT a vector DB (see §9). |
| LLM integration | **Alibaba Cloud Model Studio (DashScope) Qwen models via the OpenAI-compatible HTTP endpoint**, behind our own `LLMProvider` interface | Native fit for the Alibaba Cloud hackathon; OpenAI-compatible mode keeps the provider swappable; no heavyweight SDK/framework dependency. |
| RAG / knowledge | **Curated structured knowledge (YAML/Markdown, version-controlled) + lightweight lexical retrieval** for v1 | A vector database is not justified at v1 scale. Safety-critical knowledge must be deterministic rules, not retrieved prose. Retrieved content must carry its source citation. |
| Validation | **Pydantic v2 models at every boundary**; frontend validates inputs; strict JSON-schema-style validation of all LLM outputs | LLM output is untrusted input. Nothing from the model reaches safety or triage logic without schema validation. |
| Config / env | **pydantic-settings + `.env`**, `.env.example` committed, real secrets never committed | Single typed settings object; fail fast at startup on missing required keys. |
| Testing | **pytest** for backend (safety engine = highest coverage), **Vitest** for frontend later; LLM calls mocked in unit tests | Deterministic components must be 100% unit-testable; LLM-dependent paths tested against a mock provider. |
| Logging / errors | **Structured JSON logging** (stdlib `logging`), request IDs, typed error responses; explicit **degraded mode** when the LLM is unavailable | Traceability of every AI decision (principle 6) and graceful failure (principle 7). |
| Deployment (v1) | **Run locally** (`uvicorn` + `vite dev`) for demo; documented path to Alibaba Cloud (ECS/container) later | Avoid premature infra. Docker/K8s only if a demo environment demands it — not yet. |

### Decisions explicitly rejected for v1 (and why)

| Rejected | Reason |
|---|---|
| Microservices | One backend process with clean internal module boundaries gives the same separation without operational cost (principle 10). |
| Vector database | Knowledge corpus for v1 is small and curated; lexical retrieval is sufficient and fully explainable. Revisit only if retrieval quality is measurably insufficient. |
| LangChain or similar frameworks | Direct HTTP calls to an OpenAI-compatible endpoint are simpler, more debuggable, and keep traceability under our control. |
| Docker / Kubernetes / Redis / queues | No demonstrated need for the first demonstrable version. |
| Authentication | The first demonstrable version is a guided single-user/session flow; sessions are identified by generated session IDs. Auth becomes mandatory the moment real personal health data is stored beyond a demo. |
| Next.js / full-stack framework | Splitting frontend and backend keeps the conversational-AI/safety-engine separation physical and obvious (principle 3), and lets the safety core stay a pure, framework-free Python library. |

---

## 3. System context

```
                ┌──────────────────────────────────────────────────────┐
                │                     Browser (SPA)                    │
                │  React + Vite + TS  ·  en / ur / sd  ·  RTL-aware    │
                └───────────────────────────┬──────────────────────────┘
                                            │ HTTPS (typed JSON API)
                                            ▼
┌────────────────────────────────────────────────────────────────────────────┐
                          FastAPI backend (single process)                   │
│                                                                            │
│  api (thin HTTP) ──► conversation (orchestrator)                           │
│                          │                                                 │
│        ┌─────────────────┼─────────────────────┐                           │
│        ▼                 ▼                     ▼                           │
│   language          extraction              safety   ◄── rules/*.yaml      │
│   (detection)       (LLM → schema)          (pure, deterministic)          │
│        │                 │                     │                           │
│        │                 ▼                     ▼                           │
│        │            knowledge (RAG-lite)    triage  (pure, deterministic)  │
│        │                 │                     │                           │
│        └────────► llm (provider abstraction) ◄─┘                           │
│                          │                                                 │
│                   persistence (SQLite) · core (config/logging/errors)      │
└──────────────────────────┬─────────────────────────────────────────────────┘
                           │ HTTPS (OpenAI-compatible)
                           ▼
              Alibaba Cloud Model Studio (DashScope) — Qwen models
              (swappable behind LLMProvider; MockProvider for tests/offline)
```

---

## 4. Backend modules and responsibilities

```
backend/
  app/
    main.py                 # app factory, middleware (request id, errors), router mount
    core/                   # settings, structured logging, error types, result wrappers
    models/                 # pydantic domain models (single source of truth, see §7)
    api/                    # thin FastAPI routers; no business logic
    conversation/           # orchestrator: state machine over a session/case
    language/               # language/script detection incl. Roman Urdu; RTL metadata
    extraction/             # free text → StructuredCase via LLM + strict schema validation
    safety/                 # deterministic red-flag engine; NO LLM; pure functions
      rules/                # version-controlled YAML red-flag rule definitions
    triage/                 # deterministic urgency + next-action engine; NO LLM
    knowledge/              # curated content loading, citation handling, retrieval
      content/              # curated Markdown/YAML with source attribution
    llm/                    # LLMProvider interface; DashScopeProvider; MockProvider;
                            # prompt templates; structured-output validation/retry
    persistence/            # SQLAlchemy models + repositories (sessions, cases, traces)
  tests/
  pyproject.toml
```

Module contracts (important invariants):

- **`safety` and `triage` are pure Python, zero LLM, zero I/O.** They take validated
  structured input and return a decision plus the rule IDs that fired. This makes them
  fully unit-testable and auditable (principles 2, 6, 12).
- **`extraction` never decides.** It only converts text into a validated structure.
  If confidence is low or fields are missing, it records gaps — the orchestrator turns
  gaps into follow-up questions.
- **`conversation` owns the state machine**, never medical logic. States:
  `COLLECTING → ASSESSING → GUIDED → ESCALATED → CLOSED`.
- **`llm` is the only module that talks to a model.** Every call records: model, prompt
  template ID, latency, token usage, validation outcome — into a decision trace.
- **`knowledge` content must carry provenance** (source name + date reviewed). Content
  without provenance is rejected at load time. Nothing is auto-generated into it.

## 5. Frontend structure

```
frontend/
  src/
    components/       # ChatThread, MessageBubble, LanguagePicker, TriageCard,
                      # FollowUpForm, ClinicianSummary, DisclaimerBar
    api/              # typed client generated/hand-aligned with backend OpenAPI
    state/            # session state (single lightweight store)
    i18n/             # en / ur / sd strings; RTL layout support
    styles/           # plain CSS (no framework for v1)
  index.html
  package.json
  vite.config.ts
```

v1 frontend is deliberately thin: render the API's structured responses. All medical
logic and all safety text live server-side; the client never computes triage.

---

## 6. Main application flow (user input → final guidance)

```
User message (en/ur/sd, possibly Roman Urdu)
   │
 1. language.detect()                      deterministic script/heuristic detection
   │
 2. safety.prescreen(text)                 deterministic emergency-pattern pre-screen
   │                                        (runs BEFORE expensive LLM work; bilingual
   │                                        keyword/pattern list, version-controlled)
   │──► if emergency pattern matches: immediate EMERGENCY response path (step 8)
   ▼
 3. extraction.extract(text, history)      LLM call #1, constrained to a strict JSON
   │                                        schema → StructuredCase (+ confidence, gaps)
   │                                        schema-invalid output ⇒ retry once ⇒
   │                                        fallback: ask user to rephrase
   ▼
 4. safety.evaluate(StructuredCase)        deterministic red-flag rule engine
   │                                        → fired rule IDs + safety level
   ▼
 5. completeness check                     deterministic: required fields missing?
   │──► yes: follow-up questions (LLM call #2 phrasing ONLY; the *fields to ask*
   │         are computed deterministically; max 2 rounds, then best-effort triage)
   ▼
 6. triage.decide(StructuredCase, flags)   deterministic → TriageLevel + next actions
   │
 7. knowledge.retrieve(case)               curated content matching symptoms/level
   │                                        → cited snippets (evidence backing)
   ▼
 8. response.compose(...)                  LLM call #3: empathetic user-facing message
   │                                        in the user's language, constrained to:
   │                                        triage output + retrieved content + mandatory
   │                                        disclaimers. Output-policy filter rejects
   │                                        diagnostic/prescriptive claims.
   ▼
 9. Persist: message, StructuredCase, fired rules, triage decision, decision trace
    Return: user guidance + (when URGENT/EMERGENCY) clinician-ready case summary
```

Deterministic steps (1, 2, 4, 5-field-selection, 6) never depend on an LLM.
LLM steps (3, 5-phrasing, 8) are validated, traced, and filterable.

---

## 7. Key data models / interfaces (pydantic, backend is source of truth)

```
Session            id, created_at, preferred_language, status
Message            id, session_id, role(user|assistant|system), text, lang, created_at

StructuredCase
  chief_complaint: str
  symptoms: list[SymptomReport]      # name(normalized), onset, duration, severity(0-10|unknown),
                                     # progression(worse|same|better|unknown), body_system
  demographics: AgeGroup | None, pregnant: bool | None        # coarse buckets only
  associated_factors: list[str]      # as reported, uninterpreted
  red_flag_signals: list[str]        # user-reported phrases mapped to signal IDs
  missing_fields: list[FieldPath]    # drives follow-up questions
  confidence: float
  raw_excerpt: str                   # short quoted source text for traceability

RedFlagRule        id, description, when: ConditionExpr, level: SafetyLevel,
                   source, review_date
SafetyLevel        NONE | MONITOR | URGENT | EMERGENCY
TriageLevel        EMERGENCY | URGENT_SAME_DAY | ROUTINE | SELF_CARE | NEEDS_MORE_INFO
TriageDecision     level, fired_rule_ids: list[str], next_actions: list[LocalizedText],
                   self_care_limits: list[LocalizedText], recheck_advice: LocalizedText

GuidanceResponse   session_id, user_message: LocalizedText, triage: TriageDecision,
                   follow_up_questions: list[LocalizedText],
                   evidence: list[Citation],              # source + date, always shown
                   disclaimers: list[LocalizedText],      # never removable by client
                   clinician_summary: ClinicianSummary | None

ClinicianSummary   structured_case, fired_rules, triage_decision, timeline,
                   generated_at, model_attribution

DecisionTrace      step, input_hash, outputs, rule_ids, llm_calls(model, template_id,
                   latency_ms, valid), timestamps        # auditability (principle 6)

LocalizedText      en: str, ur: str | None, sd: str | None
```

Note: v1 deliberately stores **no names, phone numbers, or identifiers** — sessions are
anonymous and ephemeral. This is both a safety posture and a scope control.

---

## 8. Deterministic safety boundary (must never be LLM-only)

| Component | Implementation | Why deterministic |
|---|---|---|
| Emergency pre-screen (step 2) | Bilingual pattern list in code + YAML | Must catch emergencies even if the LLM is down or hallucinating |
| Red-flag rule engine | YAML rules → pure evaluator | Clinically reviewable, version-controlled, 100% unit-tested, explainable by rule ID |
| Triage level computation | Pure function of StructuredCase + flags | Same input must always produce same triage; testable acceptance criteria |
| Follow-up *field* selection | Derived from `missing_fields` | LLM only phrases questions; it cannot choose to skip a required field |
| Output policy filter | Pattern/classifier guard on final text | Blocks diagnostic claims, medication advice, and removal of disclaimers |
| Disclaimer injection | Server-side, per response | Client cannot strip; missing disclaimer ⇒ response rejected |

Rule content itself (which symptoms/combos map to which level) must be curated from
authoritative public health guidance during implementation — it is **not** invented
now, and every rule carries `source` and `review_date`.

## 9. Knowledge / RAG approach

- **Rules ≠ knowledge.** Safety rules are structured YAML (deterministic). Background
  medical information is curated Markdown with mandatory provenance metadata.
- Retrieval for v1: lexical scoring (term overlap/BM25-style) over the curated corpus —
  small, explainable, no vector DB. The corpus is expected to be small (dozens of
  topics for the hackathon), curated manually from authoritative public sources.
- Every retrieved snippet returned to the user carries `source` + `date_reviewed`.
- If retrieval finds nothing, the response says so — never fill with model memory.

### 9.1 Clinical Content Governance Workflow
To safely introduce authoritative clinical content (Knowledge and Emergency Patterns):
1. Developers may create `DRAFT` content.
2. Content moves to `PENDING_DOMAIN_REVIEW` when ready for evaluation.
3. Qualified human clinical review is required before `APPROVED`.
4. `APPROVED` is the only production-active state (unapproved content is strictly inactive).
5. `REJECTED` content is inactive.
6. `ReviewStatus` is workflow metadata, not proof of authorization by itself.
7. Production medical content must come from authoritative sources.
8. Clinical content must never be invented by the LLM.
9. Emergency patterns require the same qualified clinical review boundary.
10. Clinical source/version/date must remain traceable.
11. Production activation should occur through controlled versioned repository changes.

## 10. LLM integration

```python
class LLMProvider(Protocol):
    async def complete(self, request: LLMRequest) -> LLMResponse: ...

# Implementations:
#   DashScopeProvider  — Alibaba Cloud Model Studio, OpenAI-compatible endpoint,
#                        API key from environment only
#   MockProvider       — scripted responses for tests and offline development
```

- All prompts are versioned **templates** with IDs (traceability).
- Structured outputs are requested as JSON and re-validated; one retry, then fallback.
- Temperature/policy per step: extraction = low temp, phrasing = moderate, never
  free-form medical generation without downstream filtering.
- Provider selection via settings → swapping models/providers is a config change.

## 11. External services and abstraction points (all swappable)

| Service | v1 choice | Abstraction | Replace cost |
|---|---|---|---|
| LLM | DashScope (Qwen) | `LLMProvider` interface | New class + config |
| Retrieval | In-process lexical | `KnowledgeRetriever` interface | Vector DB behind same interface later |
| Persistence | SQLite | SQLAlchemy repositories | Postgres via connection string |
| Translation/localization | LLM-assisted at compose time + curated static strings | `Localizer` interface | Dedicated MT API later |
| Speech (future) | None in v1 | `Transcriber`/`Synthesizer` interfaces reserved | Add class, no core change |

## 12. Failure and degradation

| Failure | Behavior |
|---|---|
| LLM unreachable / timeout | Pre-screen + already-collected structured data still work. If enough structured data exists → deterministic triage + templated (non-LLM) guidance with explicit "limited mode" notice. Otherwise → honest message: service degraded, try again, and for emergencies call emergency services. Never silently degrade safety. |
| LLM returns invalid structure | Retry once with correction hint; then ask the user to rephrase. |
| Knowledge store unreadable | Triage still returned; evidence section shows "information unavailable". |
| DB write failure | Response still delivered; error logged with request ID. |
| Config/secret missing | Fail fast at startup, never at runtime. |

Emergency-path messages are **templated strings in all three languages**, so the worst
case (everything down) still yields correct emergency guidance.

## 13. Deployment view (v1)

- Development/demo: `uvicorn app.main:app` + `vite dev` with a proxy; single `.env`.
- Documented future path (not built now): containerize backend + static frontend build
  to Alibaba Cloud (ECS or equivalent). No Kubernetes, no queues, no Redis.

## 14. Security posture (v1)

- Secrets only via environment (`.env`, never committed; `.env.example` committed).
- No user identifiers collected; sessions anonymous; configurable data retention.
- All user text length-limited and treated as untrusted; no shell/eval of content.
- CORS locked to the frontend origin; OpenAPI docs disabled in production mode.
- Dependency surface kept minimal to keep the attack/audit surface small.

## §13. CLINICAL CONTENT ACTIVATION WORKFLOW

To guarantee medical safety and strictly separate engineering validation from clinical governance, the following workflow governs all medical knowledge and emergency patterns:

1. **Source validation is not clinical approval.** A developer ensuring the URL or markdown format is correct does not constitute medical verification.
2. **Structural corpus validation is not clinical approval.** The `validate_corpus.py` script ensures schema correctness and hashes are valid; it does *not* endorse the medical safety of the content.
3. **DRAFT means not ready.** Content is actively being authored or formatted and is ignored by production loaders.
4. **PENDING_DOMAIN_REVIEW means awaiting qualified human review.** The content is structurally complete but must remain inactive in production until a qualified medical professional reviews it.
5. **APPROVED means eligible for controlled production activation.** Only this status permits the content to be loaded into the production retrieval engine or safety prescreen engine.
6. **REJECTED means inactive.** The content was reviewed and failed clinical safety standards.
7. **Emergency rules require the same clinical review gate.** Red-flag signals and Emergency Patterns must pass the exact same governance workflow as medical knowledge.
8. **Test-only approved fixtures are never production clinical content.** Synthetically approved models used in automated tests (such as pytest) prove the engineering pathways; they must never be deployed to the production content directories.
9. **No LLM may approve clinical content.** The language model is completely excluded from the clinical approval workflow and cannot modify the `ReviewStatus` or bypass the loader.
10. **No developer should self-certify medical safety merely because tests pass.** A passing test suite proves the software works, not that the medical advice is sound.
11. **Production approval must be traceable to a qualified human clinical review process.** If supported by the repository configuration, `reviewed_by`, `reviewed_at`, and `review_notes` must record the actual human who authorized the content.
