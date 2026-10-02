# SehatAI Clinical Knowledge & Evidence Architecture (Phase 30A)

> **CORE ARCHITECTURAL PRINCIPLE**  
> *"AI understands. Evidence grounds. Code controls."*

---

## 1. Overview & System Purpose
SehatAI separates natural language comprehension from clinical evidence retrieval, safety guarantees, and deterministic decision-making.

```text
User Query
    ↓
Language / LLM Understanding & Structured Extraction
    ↓
Structured Case (Chief complaint, symptoms, body systems, red flags, demographics)
    ├── Deterministic Safety Engine (Regex emergency prescreen, red-flag rule evaluation)
    └── Clinical Retrieval (Lexical / Vector / Swappable ClinicalRetriever)
             ↓
       Approved Evidence (Governed, integrity-verified, unexpired clinical chunks)
             ↓
      Evidence Synthesizer (Bounded phrasing, confidence attribution)
             ↓
   Answer + Evidence + Uncertainty
             ↓
      Safety / Policy Gate
        ├── ANSWER (Grounded in approved citations with disclaimers)
        └── ABSTAIN (Deterministic fallback on insufficient or stale evidence)
```

> *"SehatAI does not promise universal medical correctness. It is designed to provide evidence-grounded answers for supported, reviewed domains and to abstain when verified evidence or sufficient context is unavailable."*

---

## 2. Evidence Lifecycle & Review Governance

Every unit of clinical evidence follows a strict, non-bypassable four-state lifecycle:

```text
  [ DRAFT ]
      ↓
  [ PENDING_DOMAIN_REVIEW ]
      ↓
  [ APPROVED ] (Mandatory human reviewer identity, timestamp, & clinical reference)
      ↓
  [ PRODUCTION ] (Corpus eligible for retrieval)

  * Terminal / Failure State: [ REJECTED ]
```

### Non-Negotiable Governance Rules:
1. **Human-Only Sign-Off**: Approval requires explicit `reviewed_by`, `reviewed_at`, and `clinical_approval_reference`. AI/LLMs cannot auto-approve clinical content.
2. **Deterministic Content Integrity**: Every document and chunk calculates a canonical SHA-256 hash across content, provenance, and metadata. Any discrepancy causes load/instantiation rejection.
3. **Automatic Approval Invalidation**: If an approved document's content or metadata is edited, its status resets to `PENDING_DOMAIN_REVIEW`, stripping approval references.
4. **Zero Production Contamination**: Unreviewed, draft, or pending materials cannot be loaded by the production orchestrator. The production knowledge and emergency rule counts remain strictly 0 until clinical panel sign-off.

---

## 3. Retrieval Abstraction & Swappability
The `ClinicalRetriever` protocol abstracts retrieval mechanics from storage backends:
```python
class ClinicalRetriever(Protocol):
    def retrieve(
        self,
        query: str | StructuredCase,
        context: RetrievalContext | None = None,
        max_results: int = 3,
    ) -> EvidencePack:
        ...
```
- **Lexical Baseline**: `LexicalClinicalRetriever` performs deterministic term overlap matching against chunk indices with stopwords filtered.
- **Future RAG Swappability**: Vector, BM25, or hybrid search engines can be introduced behind `ClinicalRetriever` without altering conversation orchestrator interfaces or safety gates.

---

## 4. EvidencePack & Sufficiency Model
Retrieval output is packaged into a typed, structured container:
- `items`: Scored `EvidenceItem` records with chunk content and publisher provenance.
- `citations`: Traceable `EvidenceCitation` records linking assertions back to source URLs, publishers, and review dates.
- `sufficiency`: Categorical evidence coverage states:
  - `HIGH`: Multi-source robust coverage (>= 3 verified approved chunks).
  - `MEDIUM`: Moderate verified coverage (2 approved chunks).
  - `LOW`: Single-source verified coverage (1 approved chunk).
  - `INSUFFICIENT`: Inadequate evidence; triggers mandatory abstention.
- `should_abstain`: Boolean flag indicating whether the system must withhold guidance.
- `abstention_reason`: Typed enum indicating the failure condition.

---

## 5. Explicit Abstention Architecture
When evidence is lacking, the system fails closed rather than hallucinating answers. Abstention triggers deterministically upon:
- `NO_APPROVED_EVIDENCE`: Production corpus has no matching approved entries.
- `INSUFFICIENT_EVIDENCE`: Retrieved coverage falls below the requested sufficiency threshold.
- `STALE_EVIDENCE`: All matching sources exceed configured freshness policies.
- `MISSING_PROVENANCE`: Missing publisher or source identity.
- `UNSUPPORTED_DOMAIN`: Query targets an unreviewed or out-of-scope clinical taxonomy domain.
- `LANGUAGE_MISMATCH`: Target language translation lacks independent clinical approval.
- `MISSING_CONTEXT`: Case lacks necessary parameters for meaningful clinical retrieval.

---

## 6. Freshness & Temporal Validity
Clinical knowledge validity is governed by `FreshnessPolicy` without arbitrary universal expiration assumptions:
- **No universal clinical expiry**: The architecture does NOT assume documents universally expire after a fixed number of days (e.g., `max_age_days=365`). Clinical validity is determined through explicit source review metadata or configured domain/jurisdiction policies.
- **Source/Document Review Metadata**:
  - `last_reviewed`: When a qualified clinical reviewer validated the entry for SehatAI.
  - `next_review`: Explicit milestone date for re-evaluation where specified by authoritative guidelines.
  - `review_interval_days`: Source-specified review interval.
- **Configurable Domain & Jurisdiction Policies**: Allows jurisdictional and clinical domain authorities to define review requirements without inventing arbitrary medical intervals.
- **Four Explicit Freshness States**:
  - `CURRENT`: Document is within active validity window.
  - `DUE_FOR_REVIEW`: Document has passed its scheduled review date but is within configured grace period.
  - `STALE`: Document has exceeded review window and grace period; excluded from active retrieval.
  - `UNAVAILABLE`: Document review status or metadata is unrecorded/missing.

---

## 7. Multilingual Governance Independence
SehatAI supports English (`en`), Urdu (`ur`), and Sindhi (`sd`), but strictly separates localized content from clinical approval:
- English approval does **not** grant automatic clinical approval to Urdu or Sindhi content.
- Each localized document carries its own independent `language` tag, its own canonical `content_hash`, and requires qualified clinical and linguistic review appropriate to the content and language before activation.

---

## 8. Clinical Domain Routing Taxonomy
The architecture establishes standardized structural domain labels:
- `CARDIOLOGY`, `NEUROLOGY`, `RESPIRATORY`, `GASTROINTESTINAL`, `DERMATOLOGY`, `PEDIATRICS`, `WOMENS_HEALTH`, `INFECTIOUS_DISEASE`, `MEDICATIONS`, `DIAGNOSTICS_LABORATORY`, `FIRST_AID`, `PREVENTIVE_CARE`, `NUTRITION`, `PUBLIC_HEALTH`, `GENERAL`.
- These labels route queries and enforce boundaries; no unreviewed clinical content or rules are attached.

---

## 9. Why the LLM is Never the Source of Truth
LLMs generate fluent probabilistic language, but:
1. They hallucinate non-existent clinical facts, medication dosages, and guideline references.
2. They cannot guarantee reproducible, auditable decision trees required by healthcare regulations (e.g., SaMD, CE mark, FDA Class II).
3. In SehatAI, the LLM is restricted to language comprehension and empathetic rephrasing. Clinical facts must originate from an `EvidencePack` composed of human-reviewed public health documents.

---

## 10. Why Deterministic Safety Remains Separate
Patient triage is safety-critical. A separate, deterministic engine evaluates:
- Emergency keywords via substring and regex prescreening.
- Red-flag rules with boolean combinators (`all_of`, `any_of`, severity thresholds, progression, demographic bounds).
- Invariant safety gates that override any generative or retrieval output.
- Bounded follow-up counters to prevent endless clarification loops.

---

## 11. Authoritative Evidence Ingestion Lineage & Immutability (Phase 30B, 30B-H, 30C)
Clinical knowledge snapshots are immutable, version-controlled artifacts:
- **Phase 30B Baseline:** Initial staged snapshot `cdc-stroke-signs-2024` captured core warning signs and the F.A.S.T. mnemonic.
- **Phase 30B-H Audit:** Executed live retrieval from `https://www.cdc.gov/stroke/signs-symptoms/index.html`. Verified official source publication (May 15, 2024) and review/update dates (May 19, 2026). Identified source evolution to B.E. F.A.S.T., 3-hour acute treatment window, TIA guidance, and ambulance dispatch instructions. Prohibited in-place mutation of the staged historical snapshot.
- **Phase 30C Current Snapshot:** Staged the current verified CDC source as `cdc-stroke-signs-2026` (`internal_version="2.0"`).
- **Lineage Preservation:**
  ```text
  Historical Snapshot (Immutable)
      ↓
  cdc-stroke-signs-2024 (hash: 698a1bf2..., status: PENDING_DOMAIN_REVIEW)
      ↓ supersedes
  Current Verified Snapshot (Immutable)
      ↓
  cdc-stroke-signs-2026 (hash: 8c24edf1..., status: PENDING_DOMAIN_REVIEW)
  ```
- **Audit Invariant:** The system maintains full point-in-time reproducibility. Historical snapshots are never overwritten or deleted.
- **Zero Production Activation:** Both snapshots remain locked at `PENDING_DOMAIN_REVIEW` outside production retrieval until qualified human physician sign-off.

