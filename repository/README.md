Empirical Spectral Geometry of MEC Covariance Structure
========================================================

Reproducible analysis scripts for the accompanying manuscripts:

1. **Paper 1**: Empirical spectral geometry of MEC covariance structure
2. **Paper 2**: Finite-size sensitivity of spectral comparison in neural covariance data

Reproduces:
- α/PR/LC metrics for all MEC recordings
- Comparison against synthetic stabilized systems
- Preprocessing-matched null controls (Phase 015)
- Finite-size scaling analysis d(N) ∼ N^2.2
- Covariance-aware ensemble distances with permutation testing

Data
----
MEC recordings from Gardner et al. (2021), "A precise coding of spatial
information in the medial entorhinal cortex."
Available at: https://doi.org/10.5061/dryad.9s4mw6mh0

The download script will fetch the MEC FRtensor files (∼2.1 GB).

Usage
-----
```
# Install dependencies
pip install -r requirements.txt

# Download data (requires ∼2.1 GB free space)
python download_data.py

# Reproduce all manuscript figures
python reproduce_figures.py

# Run ensemble distance comparison (Mahalanobis + permutation)
python statistical_comparison_demo.py

# Run Phase 015 preprocessing-matched null controls
python phase_015_controls.py --quick
```

Output: `figures/`
  - `fig1_collapse_law.pdf`        — PR vs α: MEC vs synthetic
  - `fig1_mec_spectra.pdf`         — MEC eigenvalue spectra
  - `fig2_convex_void.pdf`         — Empirical gap in (PR, LC) plane
  - `fig2_eigenvector_comparison.pdf` — IPR + level spacing
  - `fig3_conservation.pdf`        — α·PR relation
  - `fig3_finite_size_scaling.pdf` — PR(N) scaling + d(N) inset
  - `fig4_phase_diagram.pdf`       — Regime classification
  - `fig5_operators.pdf`           — Stabilization operator comparison
  - `fig3_metrics_table.csv`       — Per-recording metrics (α, PR, LC)

Results
-------
- **Canonical α**: 0.039 ± 0.018 (least-squares fit to eigenvalues 2..N/2)
- **MEC PR**: 37 ± 20 (effective dimensionality)
- **Preprocessing-matched nulls**: Poisson, shuffled, sparse — all fail to
  reproduce MEC covariance geometry (D_M > 3σ, p < 0.001 for all)
- **Scaling separation**: d(N) ∼ N^{2.2} — MEC/sparse ensemble separation
  grows with system size, ruling out finite-size coincidence

Files
-----
- `reproduce_figures.py`           — Main figure generator
- `statistical_comparison.py`      — Mahalanobis + permutation + bootstrap
- `statistical_comparison_demo.py`  — Run ensemble comparisons
- `phase_015_controls.py`          — Preprocessing-matched null experiments
- `phase_015_results/`             — Cached null control outputs
- `download_data.py`               — Data download from Dryad
- `requirements.txt`               — Python dependencies
- `data_manifest.md`               — Complete file listing and parameters

Citation
--------
Gardner, R. J. et al. (2021). A precise coding of spatial information in the
medial entorhinal cortex. Dryad. https://doi.org/10.5061/dryad.9s4mw6mh0

SGP Collaboration (2026). Empirical spectral geometry of MEC covariance
structure. [Manuscripts in preparation.]
