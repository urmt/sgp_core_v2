Spectral Constraint Framework — Dimensional Persistence in High-Dimensional Correlation Geometry

Reproduces two key results from the accompanying manuscripts:
1. **Collapse law** (PR vs α): High-dimensional systems obey α·PR ≥ 2, with MEC recordings clustering near α·PR ≈ 2.3, separating persistent broad-spectrum organization from dimensional collapse.
2. **Scaling separation** d(N) ∼ N^2.2: The distance between MEC eigenvector statistics and a sparse null ensemble grows with system size N, ruling out finite-size artifacts and confirming genuine higher-dimensional structure.

No theory, ontology, or speculative claims — pure empirical correlation geometry.

Data
----
MEC recordings from Gardner et al. (2021), "A precise coding of spatial information in the medial entorhinal cortex."
Available at: https://doi.org/10.5061/dryad.9s4mw6mh0

The download script will fetch the 14 MEC FRtensor files (∼2.1 GB).

Usage
-----
```
# Install dependencies
pip install -r requirements.txt

# Download data (requires ∼2.1 GB free space)
python download_data.py

# Reproduce all figures
python reproduce_figures.py

# Output: figures/
#   fig1_collapse_law.pdf     — PR vs α with α·PR ≥ 2 bound
#   fig2_scaling_separation.pdf — d(N) ∼ N^2.2: MEC/sparse separation grows with N
#   fig3_metrics_table.csv    — per-recording metrics (α, PR, LC, IPR)
```

Results
-------
- **Collapse law**: MEC α ≈ 0.067 ± 0.03, PR ≈ 34.2, α·PR ≈ 2.3, at the boundary of the forbidden region.
- **Scaling separation**: d_sparse(N) ∼ N^{2.19±0.09}. Finite-size artifact hypothesis rejected.
- **Precision matrix** (requires sklearn): α ≈ 0.33, PR ≈ 98, 78% sparsity — rich instantaneous correlation structure not captured by temporal operators.

Citation
--------
Gardner, R. J. et al. (2021). A precise coding of spatial information in the medial entorhinal cortex. Dryad. https://doi.org/10.5061/dryad.9s4mw6mh0
SGP Collaboration (2026). Spectral constraint framework for dimensional persistence. [Manuscripts in preparation.]
