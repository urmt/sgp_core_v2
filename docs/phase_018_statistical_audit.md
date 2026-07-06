# Phase 018C — Statistical Transparency Audit

## Date: 2026-07-06

### Canonical α Definition

| Parameter | Value | Source |
|-----------|-------|--------|
| Definition | Polyfit to eigenvalues 2 through N/2 of correlation spectrum | Paper 1 Eq. 2, Paper 2 Methods |
| Estimation method | Least-squares regression on log-transformed values | Paper 1 L48, Paper 2 L120 |
| Exclusion range | Leading eigenvalue (outlier) + tail (finite-size noise) | Paper 1 L48 |
| MEC value | α = 0.039 ± 0.018 | Mean ± SD across 21 sessions |
| Null comparison | Poisson α_null ≈ 0.004–0.035; Shuffled α_null ≈ 0.004–0.035 | Phase 015 results |

### Mahalanobis Distance Definition

| Parameter | Value | Source |
|-----------|-------|--------|
| Formula | D_M = sqrt((x - μ)' Σ_pooled^{-1} (x - μ)) | repository/statistical_comparison.py |
| Covariance | Pooled within-class covariance matrix | repository/statistical_comparison.py |
| Permutation test | n_perm = 5000 | repository/statistical_comparison.py |
| Bootstrap CI | n_boot = 5000, percentile method | repository/statistical_comparison.py |
| Null results | Poisson D_M = 143.7, Shuffle D_M = 131.2, Sparse ER p=0.05 D_M = 4.6 | Phase 016 demo |

### Sample Sizes

| Analysis | N_sessions | N_neurons | N_conditions |
|----------|-----------|-----------|--------------|
| MEC recordings | 21 | 100–600 | 21 |
| Synthetic systems | — | 50–500 | 22 |
| Eigenvector stats | 15 | ≥100 | 15 |
| Scaling analysis | 15 | 20–100 | 75 (5 sizes × 15) |
| Bootstrap | 5000 resamples | — | — |
| Permutation | 5000 iterations | — | — |

### Sparse Ensemble Generation

| Parameter | Value | Source |
|-----------|-------|--------|
| Model | Erdős–Rényi random graph | Paper 2 Methods |
| Density tested | p = 0.01, 0.05, 0.10, 0.20, 0.50 | Phase 015D |
| Best match | p = 0.05 (d = 0.86σ at N ≈ 120) | Paper 2 Table 1 |
| Generation | Symmetric binary adjacency, eigenvalues of normalized Laplacian | repository/phase_015_controls.py |

### GraphLasso λ Selection

| Parameter | Value | Source |
|-----------|-------|--------|
| Regularization | α = 0.1 (L1 penalty) | Paper 2 L128 |
| Cross-validation | When computationally feasible | Paper 2 L128 |
| Sparsity achieved | 60–89% zeros | Paper 2 L91 |
| Precision PR | 98 ± 53 | Paper 2 L91 |

### Preprocessing Pipeline

| Step | Parameter | Source |
|------|-----------|--------|
| Binning | 20 ms | Paper 1 L69, Paper 2 L116 |
| Smoothing | Gaussian, σ = 40 ms | Paper 1 L69, Paper 2 L116 |
| Normalization | z-scoring (zero mean, unit variance) | Paper 1 L34, Paper 2 L116 |
| Covariance | Correlation matrix of z-scored activity | Paper 1 L34 |

### Effective Sample Size Limitations

| Issue | Impact | Source |
|-------|--------|--------|
| Recording reuse across subsampling | Effective N < nominal bootstrap N | Paper 1 L181, Paper 2 L110 |
| Temporal autocorrelation | 20 ms bins may not be independent | Not explicitly corrected |
| Single species/region | Generalization requires validation | Paper 1 L179 |

### Null Model Family

| Null | Description | Phase |
|------|-------------|-------|
| Poisson | Independent spike trains, matched rate | 015A |
| Circular shuffle | Temporal structure destroyed, rate preserved | 015B |
| Kernel sweep | Same data, different σ (0, 40, 80 ms) | 015C |
| Sparse ER | Random graphs at varying density | 015D |
| GOE | Wigner semicircle eigenvalues | Paper 2 |
| Shifted Wigner | A = W - cI with c ≈ 0.35 | Paper 2 |
| Ising critical | Zero-mean Gaussian couplings | Paper 2 |

### Reported Statistics — Complete Registry

| Statistic | Value | CI/Null | Method |
|-----------|-------|---------|--------|
| MEC α | 0.039 ± 0.018 | SD across 21 | Polyfit eigenvalues 2..N/2 |
| MEC PR | 37 ± 20 | SD across 21 | (Σλ)² / Σλ² |
| MEC LC | -3.5 ± 1.2 | SD across 21 | log₁₀ reconstruction error |
| Precision α | 0.33 ± 0.11 | SD across sessions | GraphLasso |
| Precision PR | 98 ± 53 | SD across sessions | GraphLasso |
| Sparsity | 78% zeros | Range 60–89% | GraphLasso |
| Scaling exponent | 2.2 ± 0.1 | Bootstrap CI | log-log linear fit |
| d(N) at N=120 | 0.86σ | vs sparse p=0.05 | Mahalanobis |
| d(MEC, GOE) | >3σ eigenvalues, 3.47σ eigenvectors | Permutation | Mahalanobis |
| d(MEC, Wigner) | 0.51σ eigenvalues, 3.45σ eigenvectors | Permutation | Mahalanobis |
| d(MEC, Ising) | 0.51σ eigenvalues, 4.55σ eigenvectors | Permutation | Mahalanobis |
| D_M (Poisson null) | 143.7 | p < 0.001 | Permutation n=5000 |
| D_M (Shuffle null) | 131.2 | p < 0.001 | Permutation n=5000 |
| D_M (Sparse ER p=0.05) | 2.44 | p < 0.001 | Permutation n=5000 |
| α·PR (MEC) | 1.4 ± 0.5 | SD across 21 | Product |
| PR·exp(LC/2) | 5.8 ± 1.0 | SD across 21 | Product |
