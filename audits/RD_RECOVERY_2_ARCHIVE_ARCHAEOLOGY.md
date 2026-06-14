# RD-RECOVERY.2 — Archive Archaeology

**Goal:** For every missing artifact, determine why it is missing. The missingness itself may become data.

**Method:** For every missing artifact, record:

1. Expected purpose
2. First reference
3. Last reference
4. Dependencies
5. Reconstruction confidence (0–100)
6. Missingness type
7. Theoretical Impact (would recovery potentially change any standing rule?)
8. Counterfactual Impact (if recovered and contradictory, what standing rules could fall?)

---

## Missingness Types

| Type | Definition |
|------|------------|
| **never-created** | The artifact was never generated |
| **deleted** | The artifact existed but was removed |
| **renamed** | The artifact exists under a different name |
| **abandoned** | The artifact was started but never completed |

---

## Missing Artifact 1: `RD_HIST_2B_C2_BLIND.json`

**Expected purpose:** C2 (blind LLM) clustering assignments data.

**First reference:** Unknown.

**Last reference:** `audits/RD_HIST_2B_STABILITY_REPORT.md` (line 126).

**Dependencies:** None.

**Reconstruction confidence:** 100

**Missingness type:** renamed

**Theoretical Impact:** Low — naming mismatch only.

**Counterfactual Impact:** None — file exists.

**Note:** The file exists as `RD_HIST_2B_C2_LLM.json`. The reports call it "BLIND" while the data file uses "LLM".

---

## Missing Artifact 2: `RD_HIST_2B_C3_RANDOMIZED.json`

**Expected purpose:** C3 (randomized blind clustering) assignments data.

**First reference:** Unknown.

**Last reference:** `audits/RD_HIST_2B_STABILITY_REPORT.md` (line 127).

**Dependencies:** None.

**Reconstruction confidence:** 100

**Missingness type:** renamed

**Theoretical Impact:** Low — naming mismatch only.

**Counterfactual Impact:** None — file exists.

**Note:** The file exists as `RD_HIST_2B_C3_RANDOM.json`. The reports call it "RANDOMIZED" while the data file uses "RANDOM".

---

## Missing Artifact 3: `rd9e_audit.json`

**Expected purpose:** Output results from the Surprise Persistence (SP) audit.

**First reference:** Unknown.

**Last reference:** `audits/rd9e_sp_audit.py` (line 673, 677).

**Dependencies:** `rd9e_sp_audit.py` (script that generates this file).

**Reconstruction confidence:** 90

**Missingness type:** deleted

**Theoretical Impact:** High — SP was a candidate for persistence. Recovery could change SR-26.

**Counterfactual Impact:** Could alter SR-23 or SR-26.

**Note:** The script was run (findings are in `RD9E_SP_AUDIT.md`) but the output JSON was either never saved or was subsequently deleted.

---

## Missing Artifact 4: `audits/interaction_first/` (directory)

**Expected purpose:** Abandoned interaction-first experiments.

**First reference:** `audits/RD10BR2_FAILED_INTERACTIONS.md` (line 27).

**Last reference:** `audits/RD_HIST_RECONSTRUCTION_REPORT.md` (line 20).

**Dependencies:** None.

**Reconstruction confidence:** 60

**Missingness type:** never-created

**Theoretical Impact:** Medium — failed interactions could inform SR-24 (actual vs possible interaction).

**Counterfactual Impact:** Could weaken interaction claims.

**Note:** The actual experiments exist at `coherence-benchmark/interaction_first/` with 4 experiment files + `run_all.py`. However, the reports claim 6 studies, suggesting 2 studies were never coded or were deleted.

---

## Missing Artifact 5: `interaction_models/` (empty directory)

**Expected purpose:** Placeholder directory for interaction models, never populated.

**First reference:** `audits/RD10BR2_FAILED_INTERACTIONS.md` (line 29).

**Last reference:** `audits/RD10BR2_FAILED_INTERACTIONS.md` (line 98).

**Dependencies:** None.

**Reconstruction confidence:** 0

**Missingness type:** never-created

**Theoretical Impact:** Low — placeholder only.

**Counterfactual Impact:** None.

**Note:** The directory was never populated. There is nothing to reconstruct.

---

## Missing Artifact 6: `docs/publication_notes/` (empty directory)

**Expected purpose:** Publication documentation, never populated.

**First reference:** Unknown.

**Last reference:** Unknown.

**Dependencies:** None.

**Reconstruction confidence:** 0

**Missingness type:** never-created

**Theoretical Impact:** Low — placeholder only.

**Counterfactual Impact:** None.

**Note:** The directory was never populated. There is nothing to reconstruct.

---

## Missing Artifact 7: `docs/methodology/` (empty directory)

**Expected purpose:** Methodology documentation, never populated.

**First reference:** Unknown.

**Last reference:** Unknown.

**Dependencies:** None.

**Reconstruction confidence:** 0

**Missingness type:** never-created

**Theoretical Impact:** Low — placeholder only.

**Counterfactual Impact:** None.

**Note:** The directory was never populated. There is nothing to reconstruct.

---

## Missing Artifact 8: `docs/glossary/` (empty directory)

**Expected purpose:** Glossary documentation, never populated.

**First reference:** Unknown.

**Last reference:** Unknown.

**Dependencies:** None.

**Reconstruction confidence:** 0

**Missingness type:** never-created

**Theoretical Impact:** Low — placeholder only.

**Counterfactual Impact:** None.

**Note:** The directory was never populated. There is nothing to reconstruct.

---

## Summary

| # | Missing Artifact | Missingness Type | Reconstruction Confidence | Theoretical Impact | Counterfactual Impact |
|---|------------------|------------------|---------------------------|-------------------|----------------------|
| 1 | `RD_HIST_2B_C2_BLIND.json` | renamed | 100 | Low | None |
| 2 | `RD_HIST_2B_C3_RANDOMIZED.json` | renamed | 100 | Low | None |
| 3 | `rd9e_audit.json` | deleted | 90 | High | Could alter SR-23 or SR-26 |
| 4 | `audits/interaction_first/` | never-created | 60 | Medium | Could weaken interaction claims |
| 5 | `interaction_models/` | never-created | 0 | Low | None |
| 6 | `docs/publication_notes/` | never-created | 0 | Low | None |
| 7 | `docs/methodology/` | never-created | 0 | Low | None |
| 8 | `docs/glossary/` | never-created | 0 | Low | None |

---

## Observation

The missingness types are:
- **renamed:** 2 (naming mismatches)
- **deleted:** 1 (output file)
- **never-created:** 5 (empty directories, abandoned experiments)

The most informative missingness is **never-created** — artifacts that were planned but never generated. These may represent abandoned hypotheses, failed decompositions, or contradictory evidence.

---

## Recovery Priority

Missing evidence is asymmetrical. A single contradictory file can outweigh many confirmations.

| Priority | Artifact | Reason |
|----------|----------|--------|
| 1 | `rd9e_audit.json` | Could alter SR-23 or SR-26 |
| 2 | `interaction_first/` | Could weaken interaction claims |
| 3 | Abandoned experiments | Could reveal failed hypotheses |
| 4 | Everything else | Low theoretical impact |

---

## Artifact

`/home/student/sgp_core_v2/audits/RD_RECOVERY_2_ARCHIVE_ARCHAEOLOGY.md`
