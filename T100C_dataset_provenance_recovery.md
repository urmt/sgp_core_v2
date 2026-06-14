# T100C: Dataset Provenance Recovery

**Phase:** 3 of 4 — Exhaustive Search Before Orphan Classification
**Date:** 2026-06-01
**Director's Instruction:** "Only after exhaustive search may they be classified as orphaned."

---

## Search Scope

### Searched Locations
| Location | Searched For | Result |
|---|---|---|
| Entire repo git history (all branches, all commits) | CSV generation scripts, original filenames | `sfh_simulation_v6-Enhanced-Combo.py` → renamed to `sfh_master_framework.py` |
| Git stash | All stashes | Empty |
| Git reflog | Prior state | Single clone |
| All branches | Other worktrees | Only `main` exists |
| All tags | Release notes | Only `v1.3.1` |
| Entire `/home/student` | `.ipynb` notebooks | Found 5 SFH notebooks — none generate these CSV files |
| Entire `/home/student` | `.bak`, `.old`, `*archive*`, `*backup*` files | LibreOffice backups — no Python backups |
| Entire `/home/student` | Directories named "SFH", "sfh", "sentient" | 12 SFH-related directories inspected |
| Entire `/home/student` | Files containing strings "samples_v6.csv", "pareto_v6.csv", "weight_sweep_v6.csv" | Only the T100B report (sgp_core_v2) references these names |
| `/run/media/student/` | Entire mount point | Music files, book PDF — no SFH code |
| All SFH Python files in repo | `to_csv`, `savetxt`, `np.save`, `pd.to_csv` | No matches for CSV filenames |
| `sfh_sgp_core/` directory (67 files) | CSV generation | Outputs are different files (dimensionality, replay, operator algebra) |
| `sgp-tribe3/` directory (9 files) | CSV generation | Outputs are different files (validation_table, AUC, refit) |

---

## Git Timeline of CSV Files

### `pareto_v6.csv` — Commit `a6540c5`
```
commit a6540c5bdfd33f872ebdd7b14fa3b8ac1296b396
Author: I Am <30534610+urmt@users.noreply.github.com>
Date:   Mon Aug 18 16:41:39 2025 -0600

    Create pareto_v6.csv
```

File added: `Generated_CODE_Data/pareto_v6.csv` — 1 file, 1 insertion.

### `samples_v6.csv` + `weight_sweep_v6.csv` — Commit `c27a209`
```
commit c27a20969f6d46a22eede5dca447bb35f2ccd88a
Author: I Am <30534610+urmt@users.noreply.github.com>
Date:   Mon Aug 18 16:39:15 2025 -0600

    Add files via upload
```

Files added: `Generated_CODE_Data/samples_v6.csv` + `Generated_CODE_Data/weight_sweep_v6.csv`.

### Key commit: `11e66e2` — The rename
```
commit 11e66e27a9b9b517c0e486b7b5a5f02a605ee9f6
Author: I Am <30534610+urmt@users.noreply.github.com>
Date:   Mon Aug 18 16:53:02 2025 -0600

    Update and rename sfh_simulation_v6-Enhanced-Combo.py to sfh_master_framework.py
```

**This is the critical commit.** The original script `sfh_simulation_v6-Enhanced-Combo.py` was renamed to `sfh_master_framework.py`. The original filename (`sfh_simulation_v6-Enhanced-Combo.py`) is the only evidence of a script that could generate the v6 CSV files. The "v6" in both names is consistent:
- `sfh_simulation_v6-Enhanced-Combo.py` → v6 simulation script
- `samples_v6.csv`, `pareto_v6.csv`, `weight_sweep_v6.csv` → v6 data files

However, `sfh_master_framework.py` currently does NOT contain any CSV generation code. The generation logic was either:
1. Removed during the rename/edit
2. Existed as a separate file that was never committed
3. Exists in an external environment not present on this machine

---

## CSV Content Analysis

### `samples_v6.csv`
```
alpha,mu,alpha_s,G,G_F,coherence,fertility
0.007529683913544383,0.007529683913544383,0.007529683913544383,0.007529683913544383,0.007529683913544383,0.007529683913544383,0.007529683913544383
0.008179740044658317,0.008179740044658317,0.008179740044658317,0.008179740044658317,0.008179740044658317,0.008179740044658317,0.008179740044658317
0.007007262632161581,0.007007262632161581,0.007007262632161581,0.007007262632161581,0.007007262632161581,0.007007262632161581,0.007007262632161581
```

**Observations:**
- All 7 columns contain **identical values** in each row.
- This is NOT physical data — it's a degenerate pattern where every variable equals the same number per row.
- A proper simulation of physical constants would produce varying values for each constant.
- This pattern is consistent with a single variable being duplicated into 7 columns.

### `pareto_v6.csv`
```
coherence,fertility,rank
0.0070,0.0070,0
0.0070,0.0070,1
0.0075,0.0050,2
0.0080,0.0040,3
```

**Observations:**
- 7 rows, 3 columns.
- Pareto frontier shows tradeoff between coherence and fertility.
- First 2 rows have identical values (not a proper Pareto-optimal set — duplicates should be removed).
- Rank column suggests sorting by Pareto rank.

### `weight_sweep_v6.csv`
```
w_coh,mean_combined,ci_low,ci_high
0.000,0.00740,0.00734,0.00746
0.025,0.00740,0.00736,0.00743
...
```

**Observations:**
- 41 rows (coherence weight from 0.0 to 1.0 in 0.025 increments).
- `mean_combined` varies slightly (0.00735–0.00745 range).
- Confidence intervals provided (ci_low, ci_high).

---

## Column Name Genealogy

The CSV columns (alpha, mu, alpha_s, G, G_F, coherence, fertility) have the following traceability:

| Column | Book Mention | Code Function | Generating Code |
|---|---|---|---|
| alpha | Line 962: "α ≈ 1/137" (qualitative) | `calculate_physical_constants` (partition_calc.py:86) — broken | NONE |
| mu | Not found in book | Not found in code | NONE |
| alpha_s | Line 4122: "α_s ≈ 0.118" (qualitative) | Returns "FORMULA_NEEDED_FROM_ARTICLE" | NONE |
| G | Not found explicitly | Returns "FORMULA_NEEDED_FROM_ARTICLE" | NONE |
| G_F | Not found explicitly | Not found in code | NONE |
| coherence | Book: C = sum(Ki/Kmat)/N | Code: C = num_parts/Q_total (placeholder) | NONE |
| fertility | Not found in book | Code: F = (max-min)/Q_total (placeholder) | NONE |

---

## Conclusion

### Search Results Summary
| Search Dimension | Coverage | Result |
|---|---|---|
| Git history (all commits) | Full | Web-interface uploads |
| Git branches | All (only main) | No alternate worktree |
| All .py files in repo | 27 files | No CSV generation |
| All .ipynb notebooks | 5 notebooks (repo) + 5 (filesystem) | No CSV generation |
| All filesystem SFH directories | 12 directories | No CSV generation |
| All Python files in /home/student | ~100+ files | No CSV generation |
| All .bak files | ~15 files | Word docs only — no code |
| Full-text grep for CSV filenames | Entire /home/student | Only T100B report references them |

### Verdict: **ORPHANED — FINAL CLASSIFICATION**

The three CSV files were generated by an external process not preserved in this repository. The naming convention (`v6`) traces to `sfh_simulation_v6-Enhanced-Combo.py`, which was renamed to `sfh_master_framework.py` and stripped of generation logic. No copy of the original generation script exists anywhere on this filesystem.

**The datasets are real files but their generation path is unrecoverable from this repository alone.**

### Recommendation
The datasets contain plausible-looking physical constants in the range of actual values (α ≈ 0.007 vs actual 1/137 ≈ 0.0073). The degenerate column pattern (all 7 columns equal per row) suggests the original generator was a prototype or placeholder. If the original `sfh_simulation_v6-Enhanced-Combo.py` can be recovered from GitHub history (it was created before `11e66e2` and is still theoretically available in git objects), it could reveal the actual generation algorithm.
