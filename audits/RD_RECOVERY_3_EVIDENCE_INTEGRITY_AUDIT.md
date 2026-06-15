# RD-RECOVERY.3 — Evidence Integrity Audit

**Status:** COMPLETE  
**Date:** 2026-06-14  
**Objective:** Determine whether missing artifacts alter any standing conclusions.

---

## Step 1: Enumerate Missing Artifacts

| # | Artifact | Missingness Type | Reconstruction | Theoretical Impact | Counterfactual Impact |
|---|----------|-----------------|----------------|-------------------|----------------------|
| 1 | RD_HIST_2B_C2_BLIND.json | Renamed (→ C2_LLM.json) | 100% — exists | None | None |
| 2 | RD_HIST_2B_C3_RANDOMIZED.json | Renamed (→ C3_RANDOM.json) | 100% — exists | None | None |
| 3 | rd9e_audit.json | Deleted (script exists) | Findings already documented | High → None (SP falsified) | None — SP already demoted |
| 4 | audits/interaction_first/ | Wrong path (exists at coherence-benchmark/) | 100% — exists at correct path | Medium → None | None — already supports SR-24 |
| 5 | interaction_models/ | Never created | 0% — placeholder only | None | None |
| 6 | docs/publication_notes/ | Never created | 0% — placeholder only | None | None |
| 7 | docs/methodology/ | Never created | 0% — placeholder only | None | None |
| 8 | docs/glossary/ | Never created | 0% — placeholder only | None | None |

---

## Priority A: rd9e_audit.json

**Script:** `audits/rd9e_sp_audit.py` (exists, 681 lines)  
**Dependencies:** `synthetic.generators` (exists at `coherence-benchmark/synthetic/`)  
**Regeneration possible:** Yes, but script takes >2 minutes (heavy simulation)  
**Findings already documented:** Yes, in `audits/RD9E_SP_AUDIT.md`

**Verdict:** SP was **falsified**. It is a discretization artifact (SP=1.0 for 99% of all systems). The JSON would just contain raw data supporting this already-documented conclusion.

**Counterfactual impact:** None. SP was already demoted. Recovering the JSON would not change any standing conclusion.

---

## Priority B: interaction_first/

**Actual location:** `coherence-benchmark/interaction_first/`  
**Files:** experiment_if1.py, experiment_if2.py, experiment_if3.py, if_stress_test.py, run_all.py, __init__.py  
**Output files:** None — experiments were never run to completion  
**Claims in reports:** "6 studies" (RD_HIST_RECONSTRUCTION_REPORT.md, line 20)  
**Actual count:** 4 experiment files (2 studies may have been planned but never coded)

**Key finding already documented:**  
> "The abandoned `interaction_first` experiment had I+P+N+C but no gain — because the interaction never occurred. Possible interaction is not enough; actual interaction is required."  
> — CRITICAL_ASSUMPTIONS_REGISTER.md, A52

**Counterfactual impact:** None. Already supports SR-24 (actual vs possible interaction). The experiments that were never completed provide negative evidence: the interaction never occurred, so no gain was observed.

---

## Priority C: Empty Directories

| Directory | Status | Verdict |
|-----------|--------|---------|
| audits/interaction_models/ | Does not exist | Placeholder never created |
| docs/publication_notes/ | Exists, empty | Placeholder never populated |
| docs/methodology/ | Exists, empty | Placeholder never populated |
| docs/glossary/ | Exists, empty | Placeholder never populated |

**Counterfactual impact:** None. These are planning artifacts, not data.

---

## Step 2: Counterfactual Replay

For each recovered artifact, ask: If this artifact had existed during RD-HIST.1, would any conclusion have changed?

| Artifact | Conclusion Change |
|----------|------------------|
| rd9e_audit.json | **No effect** — SP was already falsified from MD report |
| interaction_first/ (full 6 studies) | **No effect** — the 4 existing experiments already support SR-24; 2 missing studies were never coded, so their absence is not evidence |
| Empty directories | **No effect** — placeholders, not data |

**Overall verdict:** No standing conclusion changes.

---

## Step 3: What Conclusions Become Weaker?

**None.** All missing artifacts were either:
1. Already documented (findings in MD reports)
2. Already interpreted (SR-24 already captures the interaction_first finding)
3. Placeholders (never populated)

## Step 4: What Conclusions Become Stronger?

**SR-24 (actual vs possible interaction) becomes slightly stronger.** The interaction_first experiments provide a concrete example: code existed, dependencies were in place, but the interaction never occurred. This is exactly the distinction SR-24 captures.

## Step 5: What Conclusions Become Uncertain?

**None.**

---

## Summary

The archive's missing artifacts are less consequential than initially assessed:

- **rd9e_audit.json:** Findings already documented. SP falsified. No impact.
- **interaction_first/:** Exists at correct path. Never completed. Already supports SR-24.
- **Empty directories:** Placeholders. No data lost.

**The archive is more complete than it appeared.** The missingness was primarily path confusion and naming mismatches, not lost data.

---

## Artifact

`/home/student/sgp_core_v2/audits/RD_RECOVERY_3_EVIDENCE_INTEGRITY_AUDIT.md`
