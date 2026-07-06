# Phase 015 — Preprocessing-Matched Null Controls

## Motivation

All three external reviewers independently identified the same critical concern: the preprocessing pipeline applied to real MEC data (binning, Gaussian smoothing, z-scoring) is not replicated in the null models. This creates an asymmetric comparison where:

- **Real data**: smoothed, binned, temporally correlated
- **Nulls**: iid, unsmoothed, no temporal structure

If smoothing alone manufactures broad spectra, the entire empirical separation collapses. Phase 015 tests this by matching preprocessing exactly between data and nulls.

## Success Criteria

- **Strong survival**: MEC α and PR remain distinct from all preprocessing-matched nulls (d > 2σ for all controls)
- **Partial survival**: Distinguishable from some nulls but not others → bounds the regime
- **Failure**: No survival under any matched null → project terminates

## Experiments

### 015A — Smoothed Poisson Null

Generate synthetic spike trains matched to the empirical statistics of each MEC recording:

- For each recording, compute per-neuron firing rates from the observed spike counts
- Generate iid Poisson spike trains at these rates
- Apply identical binning (20 ms) and Gaussian smoothing (σ = 40 ms)
- Compute covariance matrix, α, PR
- Compare against real MEC distribution

Output: α_null, PR_null distributions across 100 realizations per recording.

**Required**: 21 recordings × 100 realizations × ~30s each ≈ 63 min.

### 015B — Circular Shuffle Control

For each real MEC recording:

- For each neuron, circularly shift its spike train by a random offset (preserving firing statistics, destroying cross-neuron coordination)
- Apply identical preprocessing pipeline
- Compute α, PR, IPR, LC

Output: shuffled distribution across 100 shuffles per recording.

**Required**: 21 recordings × 100 shuffles × ~30s each ≈ 63 min.

### 015C — Kernel Width Sensitivity

Sweep the Gaussian smoothing kernel width σ over:

- 0 ms (no smoothing)
- 10 ms
- 20 ms
- 40 ms (current)
- 80 ms

For each width, recompute α and PR on real MEC data and on 015A Poisson nulls.

Output: α(σ), PR(σ) curves for both real and null.

**Required**: 21 recordings × 5 widths × ~30s ≈ 53 min.

### 015D — Sparse Ensemble Scan

Current sparse null uses a fixed density p = 0.05. Scan:

- p ∈ {0.01, 0.02, 0.05, 0.10, 0.20}
- Alternative topologies: modular (stochastic block model), hierarchical, banded
- Diagonal loading variation

Compare MEC eigenvector statistics against each variant to find the best-matching null at fixed N ≈ 120.

**Required**: ~15 ensemble variants × 100 realizations × ~10s ≈ 25 min.

## Implementation Plan

### File structure

```
experiments/phase_015/
├── __init__.py
├── 015A_smoothed_poisson.py
├── 015B_circular_shuffle.py
├── 015C_kernel_sweep.py
├── 015D_sparse_scan.py
├── utils.py           # Shared preprocessing and metrics
└── run_all.py         # Orchestrator (optional sequential execution)
```

### Shared utilities (utils.py)

- `canonical_alpha(eigvals)` — canonical α definition (polyfit, eigenvalues 2..N/2)
- `mec_preprocessing(spike_trains, bin_ms=20, sigma_ms=40)` — standard pipeline
- `compute_metrics(X)` — α, PR, LC, IPR triplet from a data matrix

### Dependencies

- Standard: numpy, scipy, numpy.linalg
- MEC data from: `experiments/dynamics/tier2_data/*MEC_FRtensor*.npy`
- Output: JSON results per sub-experiment in `experiments/phase_015/results/`

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| 015A destroys effect | High (project termination) | Already budgeted — honest answer is the goal |
| 015C shows smoothing dependence | Medium | Quantify and report as systematic control |
| 015D finds perfect null match | Medium | Will require re-analysis of regime boundaries |
| Computational time too long | Medium | Start with 015A (highest impact), parallelize |
