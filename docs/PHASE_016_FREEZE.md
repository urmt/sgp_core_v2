# Phase 016 Freeze — Canonical Scientific Package

This document freezes the canonical state of the project for submission. No further metric redesign, terminology pivots, or theoretical claims are permitted after this point. Only typo corrections or reviewer-requested clarifications are allowed.

## 1. Canonical α Definition

**Frozen definition:**
> The spectral decay rate α is defined as the least-squares exponential fit to eigenvalues 2 through N/2 of the z-scored correlation matrix spectrum.

**Implementation:**
```python
def canonical_alpha(eigvals):
    s = np.sort(eigvals)[::-1]
    half = len(s) // 2
    if half < 4:
        return 0.0
    coeffs = np.polyfit(np.arange(1, half), np.log(s[1:half]), 1)
    return float(max(-coeffs[0], 0.0))
```

**Frozen value:** α = 0.039 ± 0.018 (mean ± std across 21 MEC recordings)

**Files using this definition (ALL must match):**
- `papers/generate_figures.py`: `spectral_decay_rate()`
- `submission/generate_canonical_figures.py`: `spectral_decay_rate()`
- `repository/reproduce_figures.py`: `spectral_decay_rate()`
- `experiments/dynamics/spectral_proof_exploration.py`: `fit_spectral_decay()`
- `experiments/reproducibility/minimal_pipeline.py`: `spectral_decay_rate()`
- Both manuscripts: methods sections

## 2. Canonical Preprocessing Pipeline

**Frozen pipeline:**
1. Bin spike counts at 20 ms
2. Gaussian smoothing: σ = 40 ms (σ_bins = 2.0)
3. z-score: subtract mean, divide by std (per neuron, ε = 1e-10)
4. Correlation matrix: C = (X.T @ X) / (T - 1)

**Implementation:** `repository/reproduce_figures.py` → `compute_correlation_metrics()`

**Variation tested:** Phase 015C kernel sweep (σ = 0, 40, 80 ms) — results cached in `repository/phase_015_results/015C_results.json`

## 3. Canonical Statistical Pipeline

**Frozen metrics:**
- α: canonical definition above
- PR: participation ratio = (Σλ)² / Σλ²
- LC: manifold closure = log₁₀(∥X - X₉₅∥² / ∥X∥²)
- IPR: inverse participation ratio = Σv⁴ (normalized eigenvectors)

**Frozen ensemble distance:**
- Mahalanobis distance with pooled covariance
- Permutation test: n = 5000 label shuffles
- Bootstrap CI: n = 5000 resamples of MEC recordings

**Implementation:** `repository/statistical_comparison.py`

**Frozen results (from `statistical_comparison_demo.py`):**
| Null | D_M | 95% CI | p |
|------|-----|--------|---|
| Smoothed Poisson | 143.7 | [115.8, 481.7] | <0.001 |
| Circular shuffle | 131.2 | [107.0, 464.6] | <0.001 |
| Sparse ER p=0.05 | 4.6 | [4.0, 6.5] | <0.001 |

## 4. Frozen Manuscript Titles

**Paper 1:** "Empirical Spectral Geometry of MEC Covariance Structure"

**Paper 2:** "Finite-Size Sensitivity of Spectral Comparison in Neural Covariance Data"

**Paper 3 (supplementary):** "Supplementary Methods and Extended Analyses"

## 5. Frozen Figure Inventory

### Primary figures (8):
1. `fig1_collapse_law.pdf` — PR vs α across all conditions
2. `fig1_mec_spectra.pdf` — MEC eigenvalue spectra + GOE/synthetic comparison
3. `fig2_convex_void.pdf` — Empirical gap in (PR, LC) plane
4. `fig2_eigenvector_comparison.pdf` — IPR + level spacing ratio distributions
5. `fig3_conservation.pdf` — α·PR relation across regimes
6. `fig3_finite_size_scaling.pdf` — PR(N) scaling + d(N) ∼ N^2.2 inset
7. `fig4_phase_diagram.pdf` — Regime classification (broad-spectrum vs collapse)
8. `fig5_operators.pdf` — Stabilization operator comparison

### Canonical supplementary (6):
- `p1_fig3_ensemble_comparison.pdf`
- `p1_fig4_precision_spectrum.pdf`
- `p1_fig5_constraint_summary.pdf`
- `p2_fig3_rg_schematic.pdf`
- `p2_fig4_operator_comparison.pdf`
- `p2_fig5_universality_positioning.pdf`

**Total: 14 PDFs** in `submission/figures/`

## 6. Frozen Repository Structure

```
repository/
├── reproduce_figures.py              # Main figure generator
├── statistical_comparison.py         # Mahalanobis + permutation + bootstrap
├── statistical_comparison_demo.py    # Ensemble comparison runner
├── phase_015_controls.py             # Preprocessing-matched null controls
├── phase_015_results/                # Cached null control outputs
│   ├── 015A_results.json
│   ├── 015B_results.json
│   ├── 015C_results.json
│   └── 015D_results.json
├── download_data.py                  # Data download from Dryad
├── requirements.txt                  # Python dependencies
├── data_manifest.md                  # Complete file/parameter listing
├── README.md                         # Usage instructions
└── figures/                          # Output directory (generated)
```

## 7. Frozen Null-Model Definitions

**Phase 015 controls (cached):**
- **015A**: Smoothed Poisson — 100 realizations per recording, matched firing rates
- **015B**: Circular shuffle — 100 shuffles per recording, per-neuron random offsets
- **015C**: Kernel sweep — σ ∈ {0, 40, 80 ms}, 20 realizations each
- **015D**: Sparse ensemble scan — ER/modular/banded topologies, p ∈ {0.01, 0.02, 0.05, 0.1, 0.2}

**Best-matching null:** Banded p=0.01 (D_M = 2.44, p < 0.001)

## 8. Frozen Dataset

**MEC recordings:** 21 sessions from 4 cohorts (Calais, Goa, Kerala, Mumbai)
- Source: Gardner et al. (2021), Dryad doi:10.5061/dryad.9s4mw6mh0
- Shape: varies per recording (T × N, N = 37–258 neurons)
- Preprocessed: 20ms bin, 40ms Gaussian smoothing, z-scored

**Synthetic conditions:** 22 conditions across 5 architectural classes
- Reservoir computer (8), additive field (6), wave field (4), latent manifold (2), constrained random walk (2)
- Stabilization: homeostatic gain, additive transport, anisotropic suppression

## 9. Frozen Claims (Allowed)

1. MEC covariance spectra follow slow exponential decay: α = 0.039 ± 0.018
2. MEC effective dimensionality: PR = 37 ± 20
3. MEC trajectory closure: LC = -3.5 ± 1.2
4. MEC vs synthetic: reproducible separation in (α, PR) space
5. Preprocessing-matched nulls fail to reproduce MEC geometry (D_M > 3σ, p < 0.001)
6. Finite-size scaling: d(N) ∼ N^{2.2} — MEC/sparse separation grows with N
7. Instantaneous correlation geometry (precision matrix: α ≈ 0.33, PR ≈ 98) richer than temporal propagation (VAR: α ≈ 0.01)

## 10. Frozen Forbidden Claims (Explicitly Banned)

- universality / universality class
- RG / renormalization-group / relevant operator
- critical spectrum / criticality / critical
- conservation law / structural law
- forbidden region / convex void
- phase diagram (use: regime classification)
- SSCS / Stably Sustained Critical Spectrum
- new physics / new law / universal mechanism
- consciousness / sentience / ontology
- "we prove" / "this establishes" (use: "we observe" / "this is consistent with")

## 11. Checksums

**Submission figures (14 PDFs):**
- fig1_collapse_law.pdf: (verify before submission)
- fig1_mec_spectra.pdf
- fig2_convex_void.pdf
- fig2_eigenvector_comparison.pdf
- fig3_conservation.pdf
- fig3_finite_size_scaling.pdf
- fig4_phase_diagram.pdf
- fig5_operators.pdf
- p1_fig3_ensemble_comparison.pdf
- p1_fig4_precision_spectrum.pdf
- p1_fig5_constraint_summary.pdf
- p2_fig3_rg_schematic.pdf
- p2_fig4_operator_comparison.pdf
- p2_fig5_universality_positioning.pdf

**Repository outputs (must match):**
- figures/fig1_collapse_law.pdf
- figures/fig1_mec_spectra.pdf
- figures/fig2_convex_void.pdf
- figures/fig2_eigenvector_comparison.pdf
- figures/fig3_conservation.pdf
- figures/fig3_finite_size_scaling.pdf
- figures/fig4_phase_diagram.pdf
- figures/fig5_operators.pdf

## 12. Freeze Rule

**After this document is created:**
- NO metric redesign
- NO terminology pivots
- NO new theoretical claims
- NO preprocessing changes
- NO statistical pipeline changes
- ONLY: typo corrections, reviewer-requested clarifications, figure re-rendering with identical data

Any change requires explicit user authorization with rationale.

---

**Frozen on:** 2026-07-06
**Version:** 1.0
**Authorized by:** User directive