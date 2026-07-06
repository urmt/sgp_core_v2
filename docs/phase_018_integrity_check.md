# Phase 018G — Freeze Integrity Verification

## Date: 2026-07-06

### Repository State

| Item | Value |
|------|-------|
| Latest commit | `d036bcc` |
| Commit message | "Add Zenodo DOI 10.5281/zenodo.21223156 to both manuscripts" |
| Tag | `PHASE_016_FREEZE` (on commit `6b5eb03`) |
| Remote | `urmt/sgp_core_v2` |
| Branch | `master` |

### Zenodo DOI

| Item | Value |
|------|-------|
| DOI | `10.5281/zenodo.21223156` |
| URL | https://doi.org/10.5281/zenodo.21223156 |
| In Paper 1 | ✅ Data Availability section |
| In Paper 2 | ✅ Data Availability section |

### Manuscript PDFs

| File | Size | MD5 | Compiled |
|------|------|-----|----------|
| paper1.pdf | 264 KB | `daf27826982f373999448d9d047b336b` | 2026-07-06 14:04 |
| paper2.pdf | 249 KB | `90239b667ab1caf00588fae8cf9aa4df` | 2026-07-06 14:04 |

### Figure Outputs

| File | Present | Referenced |
|------|---------|------------|
| fig1_collapse_law.pdf | ✅ | ✅ (Paper 1) |
| fig2_convex_void.pdf | ✅ | ✅ (Paper 1) |
| fig3_conservation.pdf | ✅ | ✅ (Paper 1) |
| fig4_phase_diagram.pdf | ✅ | ✅ (Paper 1) |
| fig5_operators.pdf | ✅ | ✅ (Paper 1) |
| fig1_mec_spectra.pdf | ✅ | ✅ (Paper 2) |
| fig2_eigenvector_comparison.pdf | ✅ | ✅ (Paper 2) |
| fig3_finite_size_scaling.pdf | ✅ | ✅ (Paper 2) |

Orphaned figures: **0** (6 removed in 018A)

### Bibliography

| Item | Value |
|------|-------|
| Total entries | 32 |
| Cited in Paper 1 | 26 |
| Cited in Paper 2 | 18 |
| Total unique cited | 32 |
| Uncited removed | 18 |

### Frozen Numerical Values

| Value | Paper 1 | Paper 2 | Status |
|-------|---------|---------|--------|
| α (canonical) | 0.039 ± 0.018 | 0.039 ± 0.018 | ✅ Consistent |
| PR (MEC) | 37 ± 20 | 37 ± 20 | ✅ Consistent |
| LC (MEC) | -3.5 ± 1.2 | -3.5 ± 1.2 | ✅ Consistent |
| N sessions | 21 | 21 | ✅ Consistent |
| Precision α | 0.33 ± 0.11 | 0.33 ± 0.11 | ✅ Consistent |
| Precision PR | 98 ± 53 | 98 ± 53 | ✅ Consistent |
| Scaling exponent | 2.2 ± 0.1 | 2.2 ± 0.1 | ✅ Consistent |
| α·PR | 1.4 ± 0.5 | 1.4 ± 0.5 | ✅ Consistent |
| PR·exp(LC/2) | 5.8 ± 1.0 | 5.8 ± 1.0 | ✅ Consistent |

### Consistency Check

| Check | Status |
|-------|--------|
| Same Zenodo DOI in both papers | ✅ |
| Same α definition in both papers | ✅ |
| Same preprocessing in both papers | ✅ |
| Same N in both papers | ✅ |
| Figures match labels | ✅ |
| Citations match bibliography | ✅ |
| No forbidden terminology | ✅ |
| No overstated language | ✅ |
| Language register consistent | ✅ |

### Integrity Statement

All artifacts correspond to the same frozen state:
- Repository commit: `d036bcc`
- Zenodo tag: `PHASE_016_FREEZE` (commit `6b5eb03`)
- Manuscript PDFs: compiled from updated .tex files with DOI and language edits
- 8 figures: generated from `generate_canonical_figures.py`
- 32 bibliography entries: all cited

The submission package is internally consistent and frozen.
