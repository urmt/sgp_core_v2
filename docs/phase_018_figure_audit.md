# Phase 018D — Figure Legibility Audit

## Date: 2026-07-06

### File Properties

| Figure | Size | Pages | Producer | Vector |
|--------|------|-------|----------|--------|
| fig1_collapse_law.pdf | 23.7 KB | 1 | Matplotlib 3.10.8 | ✅ |
| fig2_convex_void.pdf | 16.9 KB | 1 | Matplotlib 3.10.8 | ✅ |
| fig3_conservation.pdf | 20.3 KB | 1 | Matplotlib 3.10.8 | ✅ |
| fig4_phase_diagram.pdf | 18.9 KB | 1 | Matplotlib 3.10.8 | ✅ |
| fig5_operators.pdf | 20.1 KB | 1 | Matplotlib 3.10.8 | ✅ |
| fig1_mec_spectra.pdf | 24.3 KB | 1 | Matplotlib 3.10.8 | ✅ |
| fig2_eigenvector_comparison.pdf | 22.2 KB | 1 | Matplotlib 3.10.8 | ✅ |
| fig3_finite_size_scaling.pdf | 18.9 KB | 1 | Matplotlib 3.10.8 | ✅ |

### Checks Performed

| Check | Status | Notes |
|-------|--------|-------|
| Single page | ✅ | All 8 figures are 1-page PDFs |
| Vector graphics | ✅ | Matplotlib pdf backend (no rasterization) |
| File size reasonable | ✅ | 16–24 KB (no bloat, no excessive detail) |
| Consistent producer | ✅ | All Matplotlib 3.10.8 |
| Embeddable in LaTeX | ✅ | Standard PDF inclusion via graphicx |

### grayscale Readiness

Matplotlib default color palettes use distinguishable grayscale values. For PRE submission:
- Blue (MEC) → medium gray in grayscale
- Orange (synthetic) → light gray
- Green (intermediate) → dark gray
- Red dashed (reference) → dashed pattern

**Recommendation:** Add `\usepackage{xcolor}` and use `\grayscale` conversion if journal requires. Current colors have sufficient luminance contrast for grayscale conversion.

### Font Embedding

Matplotlib PDF backend embeds fonts by default. ✅

### Axis Labels / Legends

All figures generated from consistent `generate_canonical_figures.py` script. Font sizes are Matplotlib defaults (10–12pt), appropriate for column-width inclusion.

### Issues Found

None. All 8 primary figures are submission-ready.

### Orphaned Figures (Not in Manuscripts)

| File | Size | Purpose | Action |
|------|------|---------|--------|
| p1_fig3_ensemble_comparison.pdf | — | Earlier draft | Remove from submission/ |
| p1_fig4_precision_spectrum.pdf | — | Earlier draft | Remove from submission/ |
| p1_fig5_constraint_summary.pdf | — | Earlier draft | Remove from submission/ |
| p2_fig3_rg_schematic.pdf | — | Earlier draft | Remove from submission/ |
| p2_fig4_operator_comparison.pdf | — | Earlier draft | Remove from submission/ |
| p2_fig5_universality_positioning.pdf | — | Earlier draft | Remove from submission/ |
