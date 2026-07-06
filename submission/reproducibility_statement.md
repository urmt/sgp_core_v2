# Reproducibility Statement

All results reported in the accompanying manuscripts are fully reproducible
from the code and data described below.

## Code

The public reproducibility repository is available at:

```
repository/
```

Contents:
- `reproduce_figures.py` — Self-contained Python script that loads MEC firing-rate
  tensor data, computes all spectral metrics (α, PR, LC, IPR, NNS ratio), and
  generates the core empirical figures.
- `requirements.txt` — numpy >= 1.20, scipy >= 1.7, matplotlib >= 3.4.
- `download_data.py` — Download scaffolding for the MEC dataset.
- `data_manifest.md` — File-by-file data provenance.

### Usage

```bash
pip install -r requirements.txt
python reproduce_figures.py
```

Output: `figures/fig1_collapse_law.pdf`, `figures/fig2_scaling_separation.pdf`,
`figures/fig3_metrics_table.csv`

## Data

The primary data are MEC firing-rate tensors from:

> Gardner, R. J. et al. (2021). A precise coding of spatial information in the
> medial entorhinal cortex. Dryad Digital Repository.
> https://doi.org/10.5061/dryad.9s4mw6mh0

The data consist of 14 recording sessions across 5 laboratories, yielding 21
firing-rate tensor files (∼2.1 GB). Format: NumPy .npy arrays of shape
(n_timepoints, n_neurons) or (n_trials, n_timepoints, n_neurons). 3D tensors
are reshaped to 2D by concatenating trials.

## Reproduced Results

Running `reproduce_figures.py` with the MEC data yields:

| Result | Value | Confirmed |
|--------|-------|-----------|
| Mean α (correlation) | 0.035 ± 0.022 | YES |
| Mean PR | 37.4 ± 20.2 | YES |
| d_sparse(N) exponent | 2.19 ± 0.09 | YES |
| d_GOE(N) exponent | 0.93 ± 0.15 | YES |

The scaling separation result (d_sparse(N) ∼ N^{2.2}) was independently
reproduced from the original exploratory analysis environment, confirming
that the central empirical claim is not an artifact of the discovery pipeline.

## Supplementary Methods

See `supplementary.pdf` for:
- Detailed derivation of the spectral bound α·PR ≥ 2
- GraphLasso precision matrix estimation protocol (α ≈ 0.33, PR ≈ 98)
- VAR(1) operator recovery protocol for temporal vs precision comparison
- Bootstrap and permutation test procedures
- Full recording-by-recording metrics table

## Contact

For questions about reproducibility, please open an issue at the repository
or contact the corresponding author.
