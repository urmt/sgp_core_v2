# RD-RECOVERY.1 — Lost Archive Reconstruction

**Goal:** Identify every missing file, its expected purpose, references from other documents, scripts that import it, timestamps, neighboring files, and whether reconstruction is possible.

**Method:** For every missing file, list:
1. Filename
2. Expected purpose
3. References from other documents
4. Scripts that import it
5. Timestamps
6. Neighboring files
7. Whether reconstruction is possible

---

## Missing File 1: `RD_HIST_2B_C2_BLIND.json`

**Expected purpose:** C2 (blind LLM) clustering assignments data.

**References from other documents:**
- `audits/RD_HIST_2B_STABILITY_REPORT.md` (line 126)
- `audits/RD_HIST_2B_REPORT.md` (line 126)

**Scripts that import it:** None.

**Timestamps:** Unknown.

**Neighboring files:**
- `RD_HIST_2B_C1_HUMAN.json` (exists)
- `RD_HIST_2B_C2_LLM.json` (exists — same content, different name)
- `RD_HIST_2B_C3_RANDOM.json` (exists)

**Reconstruction possible:** Yes. The file exists as `RD_HIST_2B_C2_LLM.json`. The reports call it "BLIND" while the data file uses "LLM". This is a naming mismatch, not a missing file.

---

## Missing File 2: `RD_HIST_2B_C3_RANDOMIZED.json`

**Expected purpose:** C3 (randomized blind clustering) assignments data.

**References from other documents:**
- `audits/RD_HIST_2B_STABILITY_REPORT.md` (line 127)
- `audits/RD_HIST_2B_REPORT.md` (line 127)

**Scripts that import it:** None.

**Timestamps:** Unknown.

**Neighboring files:**
- `RD_HIST_2B_C1_HUMAN.json` (exists)
- `RD_HIST_2B_C2_LLM.json` (exists)
- `RD_HIST_2B_C3_RANDOM.json` (exists — same content, different name)

**Reconstruction possible:** Yes. The file exists as `RD_HIST_2B_C3_RANDOM.json`. The reports call it "RANDOMIZED" while the data file uses "RANDOM". This is a naming mismatch, not a missing file.

---

## Missing File 3: `rd9e_audit.json`

**Expected purpose:** Output results from the Surprise Persistence (SP) audit.

**References from other documents:**
- `audits/rd9e_sp_audit.py` (line 673, 677) — output file written by the script

**Scripts that import it:** None (output file, not input).

**Timestamps:** Unknown. The script was run (findings are in `RD9E_SP_AUDIT.md`) but the output JSON was either never saved or was subsequently deleted.

**Neighboring files:**
- `rd9e_sp_audit.py` (exists — the script that generates this file)
- `RD9E_SP_AUDIT.md` (exists — the report presenting findings)
- `rd9e_quick.py` (exists)
- `rd9e_steps123.py` (exists)

**Reconstruction possible:** Yes. Re-running `rd9e_sp_audit.py` should regenerate the file. The script is self-contained and uses data from the granular simulations.

---

## Missing File 4: `audits/interaction_first/` (directory)

**Expected purpose:** Abandoned interaction-first experiments.

**References from other documents:**
- `audits/RD10BR2_FAILED_INTERACTIONS.md` (line 27)
- `audits/RD10BR3_FERTILE_INTERACTIONS.md` (line 80)
- `audits/RD_HIST_RECONSTRUCTION_REPORT.md` (line 20) — lists 6 studies in this series

**Scripts that import it:** None.

**Timestamps:** Unknown.

**Neighboring files:**
- `coherence-benchmark/interaction_first/` (exists — actual location)
- `interaction_models/` (exists — empty directory)

**Reconstruction possible:** Partial. The actual experiments exist at `coherence-benchmark/interaction_first/` with 4 experiment files + `run_all.py`. However, the reports claim 6 studies, suggesting 2 studies were never coded or were deleted.

---

## Missing File 5: `interaction_models/` (empty directory)

**Expected purpose:** Placeholder directory for interaction models, never populated.

**References from other documents:**
- `audits/RD10BR2_FAILED_INTERACTIONS.md` (line 29, 98) — "Created but never populated"

**Scripts that import it:** None.

**Timestamps:** Unknown.

**Neighboring files:**
- `coherence-benchmark/interaction_first/` (exists)

**Reconstruction possible:** No. The directory was never populated. There is nothing to reconstruct.

---

## Missing File 6: `docs/publication_notes/` (empty directory)

**Expected purpose:** Publication documentation, never populated.

**References from other documents:** None.

**Scripts that import it:** None.

**Timestamps:** Unknown.

**Neighboring files:**
- `docs/theory/` (exists)
- `docs/methodology/` (exists — empty)

**Reconstruction possible:** No. The directory was never populated. There is nothing to reconstruct.

---

## Missing File 7: `docs/methodology/` (empty directory)

**Expected purpose:** Methodology documentation, never populated.

**References from other documents:** None.

**Scripts that import it:** None.

**Timestamps:** Unknown.

**Neighboring files:**
- `docs/theory/` (exists)
- `docs/glossary/` (exists — empty)

**Reconstruction possible:** No. The directory was never populated. There is nothing to reconstruct.

---

## Missing File 8: `docs/glossary/` (empty directory)

**Expected purpose:** Glossary documentation, never populated.

**References from other documents:** None.

**Scripts that import it:** None.

**Timestamps:** Unknown.

**Neighboring files:**
- `docs/methodology/` (exists — empty)
- `docs/publication_notes/` (exists — empty)

**Reconstruction possible:** No. The directory was never populated. There is nothing to reconstruct.

---

## Summary

| # | Missing File | Type | Reconstruction Possible |
|---|--------------|------|------------------------|
| 1 | `RD_HIST_2B_C2_BLIND.json` | Naming mismatch | Yes — exists as `RD_HIST_2B_C2_LLM.json` |
| 2 | `RD_HIST_2B_C3_RANDOMIZED.json` | Naming mismatch | Yes — exists as `RD_HIST_2B_C3_RANDOM.json` |
| 3 | `rd9e_audit.json` | Missing output | Yes — re-run `rd9e_sp_audit.py` |
| 4 | `audits/interaction_first/` | Wrong path | Partial — exists at `coherence-benchmark/interaction_first/` |
| 5 | `interaction_models/` | Empty directory | No — never populated |
| 6 | `docs/publication_notes/` | Empty directory | No — never populated |
| 7 | `docs/methodology/` | Empty directory | No — never populated |
| 8 | `docs/glossary/` | Empty directory | No — never populated |

---

## Actionable Items

1. **Fix naming mismatches:** Update reports to reference `RD_HIST_2B_C2_LLM.json` and `RD_HIST_2B_C3_RANDOM.json` instead of `RD_HIST_2B_C2_BLIND.json` and `RD_HIST_2B_C3_RANDOMIZED.json`.

2. **Regenerate missing output:** Re-run `rd9e_sp_audit.py` to regenerate `rd9e_audit.json`.

3. **Update path references:** Update reports to reference `coherence-benchmark/interaction_first/` instead of `audits/interaction_first/`.

---

## Artifact

`/home/student/sgp_core_v2/audits/RD_RECOVERY_1_LOST_ARCHIVE_RECONSTRUCTION.md`
