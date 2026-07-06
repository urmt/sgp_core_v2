# Phase 018A — Cross-Reference Audit

## Date: 2026-07-06

## Paper 1: Empirical Spectral Geometry of MEC Covariance Structure

### Figure References

| Label | File | Ref calls | Status |
|-------|------|-----------|--------|
| fig:collapse | fig1_collapse_law.pdf | Fig.~\ref{fig:collapse} (×2) | ✅ |
| fig:void | fig2_convex_void.pdf | Figure~\ref{fig:void} (×1) | ✅ |
| fig:conservation | fig3_conservation.pdf | Fig.~\ref{fig:conservation} (×1) | ✅ |
| fig:phase | fig4_phase_diagram.pdf | Figure~\ref{fig:phase} (×1) | ✅ |
| fig:operators | fig5_operators.pdf | Figure~\ref{fig:operators} (×1) | ✅ |

### Table References

| Label | Ref calls | Status |
|-------|-----------|--------|
| tab:conditions | Table~\ref{tab:conditions} (×1) | ✅ |

### Equation References

| Label | Ref calls | Status |
|-------|-----------|--------|
| eq:reference | Eq.~\ref{eq:reference} (×3) | ✅ |
| eq:lc_bound | (defined, not ref'd in text) | ⚠️ Orphan label |

### Citations (26 unique)

All 26 citations in Paper 1 resolve to bibliography.bib entries. ✅

### Orphaned Figure Files

| File | Referenced | Status |
|------|------------|--------|
| p1_fig3_ensemble_comparison.pdf | No | ⚠️ Orphan |
| p1_fig4_precision_spectrum.pdf | No | ⚠️ Orphan |
| p1_fig5_constraint_summary.pdf | No | ⚠️ Orphan |

---

## Paper 2: Finite-Size Sensitivity of Spectral Comparison

### Figure References

| Label | File | Ref calls | Status |
|-------|------|-----------|--------|
| fig:spectra | fig1_mec_spectra.pdf | Fig.~\ref{fig:spectra} (×1) | ✅ |
| fig:eigenvectors | fig2_eigenvector_comparison.pdf | Fig.~\ref{fig:eigenvectors} (×1) | ✅ |
| fig:scaling | fig3_finite_size_scaling.pdf | Fig.~\ref{fig:scaling} (×2) | ✅ |

### Table References

| Label | Ref calls | Status |
|-------|-----------|--------|
| tab:ensembles | Table~\ref{tab:ensembles} (×1) | ✅ |

### Equation References

None (equations defined inline). ✅

### Citations (18 unique)

All 18 citations in Paper 2 resolve to bibliography.bib entries. ✅

### Orphaned Figure Files

| File | Referenced | Status |
|------|------------|--------|
| p2_fig3_rg_schematic.pdf | No | ⚠️ Orphan |
| p2_fig4_operator_comparison.pdf | No | ⚠️ Orphan |
| p2_fig5_universality_positioning.pdf | No | ⚠️ Orphan |

---

## Bibliography Audit

### Uncited Entries (18)

These entries exist in bibliography.bib but are not cited in either manuscript:

1. porter1956
2. anderson1958
3. edwards1972
4. haake2010
5. holmes2012
6. mazzucato2015
7. humblenat2020
8. jazayeri2021
9. pourahmadi2013
10. trefethen1997
11. golub2013
12. hohenberg1977
13. beggs2003
14. sethna2001
15. mora2011
16. tkacik2015
17. newman2003
18. wilson1975

**Recommendation:** Remove uncited entries to reduce bibliography noise. Keep only cited entries.

### Duplicate/Overlapping Entries

None detected. ✅

---

## Summary

| Check | Paper 1 | Paper 2 | Status |
|-------|---------|---------|--------|
| Figure refs resolve | 5/5 | 3/3 | ✅ |
| Table refs resolve | 1/1 | 1/1 | ✅ |
| Eq refs resolve | 2/2 | 0/0 | ✅ |
| Citations resolve | 26/26 | 18/18 | ✅ |
| Orphan figures | 3 | 3 | ⚠️ Clean up |
| Uncited bib entries | — | — | 18 to remove |
| Forbidden terminology | 0 | 0 | ✅ |
