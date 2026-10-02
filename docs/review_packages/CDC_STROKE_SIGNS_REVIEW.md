# Clinical Evidence Human Review Package: Signs and Symptoms of Stroke

> **STATUS: PENDING_DOMAIN_REVIEW**  
> *DO NOT ACTIVATE WITHOUT VERIFIED QUALIFIED CLINICAL REVIEW.*

## 1. Source Provenance & Metadata

### A. Authoritative Source Metadata
- **Publisher:** Centers for Disease Control and Prevention
- **Title:** Signs and Symptoms of Stroke
- **Canonical URL:** https://www.cdc.gov/stroke/signs-symptoms/index.html
- **Official Publication Date:** 2024-05-15 (First published on CDC portal)
- **Official Update Date:** 2026-05-19 (Last reviewed & updated on CDC portal)
- **Official Source Version:** Unavailable / Not versioned by publisher
- **Language:** `en`
- **Clinical Domain:** `neurology`
- **Jurisdiction:** US / Global Public Health
- **Clinical Scope:** stroke_warning_signs

### B. Ingestion Pipeline Metadata (SehatAI)
- **Ingestion ID:** `src-cdc-stroke-signs-v1`
- **Document ID:** `cdc-stroke-signs-2024`
- **Internal Ingestion Version:** `1.0`
- **Ingestion Method:** `curated_snapshot`
- **Ingestion Timestamp (UTC):** 2026-10-02T11:00:00+00:00
- **Provenance Type:** `authoritative_public_source`
- **Verification Status:** authoritative_retrieval_verified_differences_reported
- **Raw Snapshot SHA-256:** `51e4c4caf89f99de509da279d7fe3435ed50f1d475ab45d09df9153b14a8b265`
- **Document Canonical SHA-256:** `698a1bf2d971f43b67fa5e918dfb42f1bebafa8abb3cd12b1d6cbd86313f253e`
- **Total Granular Chunks:** 7

## 2. Ingested Clinical Chunks for Evaluation

### Chunk `cdc-stroke-signs-2024-chk-00` (Index 1/7)
- **Character Offsets:** start=0, end=229
- **Chunk Hash:** `90ec5784f7fb052ddfdbe2349224154e928f3a6176c18a12c82f19983b7286a1`
- **Indexed Terms:** action, brain, by, can, cause, counts, damage, during, every, fast, knowing, lessen, life, minute, perhaps, quick, save, signs, stroke, symptoms, take, treatment

**Verbatim Source Excerpt:**
> Signs and symptoms of stroke: During a stroke, every minute counts! Fast treatment can lessen the brain damage that stroke can cause. By knowing the signs and symptoms of stroke, you can take quick action and perhaps save a life.

---

### Chunk `cdc-stroke-signs-2024-chk-01` (Index 2/7)
- **Character Offsets:** start=231, end=362
- **Chunk Hash:** `4007cd41f51962b9b33ec856d46c444d8b660c203945605ca0df83ab868ec963`
- **Indexed Terms:** arm, body, especially, face, include, leg, men, numbness, one, side, signs, stroke, sudden, weakness, women

**Verbatim Source Excerpt:**
> Signs of stroke in men and women include: Sudden numbness or weakness in the face, arm, or leg, especially on one side of the body.

---

### Chunk `cdc-stroke-signs-2024-chk-02` (Index 3/7)
- **Character Offsets:** start=364, end=435
- **Chunk Hash:** `055201c0ae9b87437a11c70bd12506805c4ac54f10cae43084451c50edd1cbba`
- **Indexed Terms:** confusion, difficulty, speaking, speech, sudden, trouble, understanding

**Verbatim Source Excerpt:**
> Sudden confusion, trouble speaking, or difficulty understanding speech.

---

### Chunk `cdc-stroke-signs-2024-chk-03` (Index 4/7)
- **Character Offsets:** start=437, end=479
- **Chunk Hash:** `ba195a9f77cc3177fe8cedef78480c2e6161aed80028c1af8356f4b6494ac6df`
- **Indexed Terms:** both, eyes, one, seeing, sudden, trouble

**Verbatim Source Excerpt:**
> Sudden trouble seeing in one or both eyes.

---

### Chunk `cdc-stroke-signs-2024-chk-04` (Index 5/7)
- **Character Offsets:** start=481, end=557
- **Chunk Hash:** `344c6f77fedcdc91fd797286365bc28f383fd53bef34a7d4789f33f6f478e23c`
- **Indexed Terms:** balance, coordination, dizziness, lack, loss, sudden, trouble, walking

**Verbatim Source Excerpt:**
> Sudden trouble walking, dizziness, loss of balance, or lack of coordination.

---

### Chunk `cdc-stroke-signs-2024-chk-05` (Index 6/7)
- **Character Offsets:** start=559, end=602
- **Chunk Hash:** `6cace0b5a1accb7c01cc7144a1aa371db868d2037eff6264b3fa79d66bd8e24a`
- **Indexed Terms:** cause, headache, known, severe, sudden

**Verbatim Source Excerpt:**
> Sudden severe headache with no known cause.

---

### Chunk `cdc-stroke-signs-2024-chk-06` (Index 7/7)
- **Character Offsets:** start=604, end=891
- **Chunk Hash:** `3784531f4df8f01eba7557299c9d7a9a54b2395203c9740981073b19156c06ad`
- **Indexed Terms:** act, any, arm, arms, ask, away, both, call, difficulty, drooping, else, face, identify, if, person, phrase, raise, repeat, right, signs, simple, smile, someone, speech, stroke, symptoms, these, time, weakness

**Verbatim Source Excerpt:**
> Call 9-1-1 right away if you or someone else has any of these symptoms. Act F.A.S.T. to identify stroke signs: Face drooping (ask the person to smile), Arm weakness (ask the person to raise both arms), Speech difficulty (ask the person to repeat a simple phrase), and Time to call 9-1-1.

---

## 3. Human Clinical Review Decision Record

| Field | Required Value / Format | Reviewer Entry |
|---|---|---|
| **Reviewer Full Name** | Non-empty string | `[ ENTER FULL NAME ]` |
| **Reviewer Professional Role** | e.g. Neurologist, Emergency Physician, Clinical Governance Lead | `[ ENTER ROLE & CREDENTIALS ]` |
| **Review Timestamp (UTC)** | ISO-8601 (YYYY-MM-DDTHH:MM:SSZ) | `[ ENTER TIMESTAMP ]` |
| **Clinical Decision** | `APPROVED` or `REJECTED` | `[ PENDING_DOMAIN_REVIEW ]` |
| **Clinical Approval Reference** | Institutional / Guideline Reference ID | `[ ENTER REFERENCE IF APPROVED ]` |
| **Reviewer Clinical Notes** | Specific feedback, reservations, or approval basis | `[ ENTER NOTES ]` |

## 4. Human Clinical Review Checklist

- [ ] **Source Authenticity:** Verified against official CDC public portal.
- [ ] **Factual Veracity:** Stored excerpts are preserved from the ingested source snapshot; provenance and integrity are cryptographically tracked.
- [ ] **Scope Limitation:** Limited strictly to stroke warning signs recognition (BEFAST).
- [ ] **Safety Appropriateness:** Directs urgent emergency action without delaying professional care.
- [ ] **Language Precision:** English terminology is unambiguous and clinically standard.
- [ ] **Multilingual Isolation:** Verified that English approval does NOT grant automatic Urdu/Sindhi approval.
- [ ] **Production Eligibility:** Authorized by qualified clinician for future production activation.
