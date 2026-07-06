# Phase 016 — Statistical Hardening and Repository Synchronization

## Objective
Convert from vulnerable exploratory framework into statistically defensible empirical spectral-analysis package suitable for PRE-level review.

## Acceptance Gate (016-0)
Project is submission-ready only when:
1. Every figure reproduces from clean repository
2. All major reviewer objections addressed directly
3. All statistics are covariance-aware
4. Preprocessing-matched controls included in repository
5. No unsupported theoretical language remains (already enforced)

## Task 016A — Replace Composite Euclidean σ Metric

### Current problem
Ensemble distances use: `d = sqrt(d_IPR² + d_r² + d_α²)`, each normalized by ensemble std. This is:
- Not covariance-aware (treats metrics as independent)
- No MEC-side uncertainty propagation
- No significance test
- No confidence intervals

### Required implementation
- **Mahalanobis distance**: `D_M = sqrt((μ_mec - μ_null)^T Σ^{-1} (μ_mec - μ_null))` where Σ is the pooled covariance of [IPR, r, α] across both MEC and null realizations
- **Permutation testing**: Shuffle labels between MEC and null, recompute distance, get p-value from 10000 permutations
- **Bootstrap CI**: Resample MEC recordings with replacement (10000 iterations), report 95% CI on all metrics
- **Propagate MEC uncertainty**: MEC-side variance inflates the distance denominator naturally via pooled covariance

### Acceptance
- All ensemble comparisons in both papers use Mahalanobis distance
- p-values reported alongside distances
- 95% bootstrap CIs on all central values (α, PR, LC)

## Task 016B — Repository Synchronization

### Required additions to `repository/`
- `generate_figures.py` — standalone script producing all 14 manuscript figures
- `phase_015_controls.py` — all four Phase 015 null experiments as runnable scripts
- `data_manifest.md` — complete file listing, origins, preprocessing parameters
- `statistical_comparison.py` — Mahalanobis distance + permutation test functions

### Required additions to `repository/phase_015_results/`
- `015A_results.json` — smoothed Poisson null (already in experiments/phase_015/results/)
- `015B_results.json` — circular shuffle controls
- `015C_results.json` — kernel width sweep
- `015D_results.json` — sparse ensemble scan

### Acceptance
- `python reproduce_figures.py` produces all figures from scratch
- `python phase_015_controls.py` reproduces all control results
- `python statistical_comparison.py --all` prints ensemble distances with p-values

## Task 016C — Null-Model Hardening

### Sparse ensemble scan expansion
Current (015D): density scan p ∈ {0.01, 0.02, 0.05, 0.10, 0.20}, topologies {ER, modular, banded}
Missing: diagonal loading, degree heterogeneity, scale-free topologies

### Additional nulls for repository
- Scale-free (Barabási-Albert) sparse covariance: varying degree exponent
- Diagonal-loaded identity: `C = I + ε*W` for ε ∈ {0.01, 0.05, 0.1, 0.5}
- Hierarchical block model with nested community structure
- Smoothed independent noise (already in 015A, include in repository)

### Acceptance
- Null-model catalog covers: density, topology, diagonal loading, degree heterogeneity
- Best-match null identified across full parameter space
- All controls runnable from repository

## Task 016D — Manuscript Language Gate

Already enforced. Verification:
- `grep -ri "universality\|RG.*operator\|critical spectrum\|conservation law\|forbidden region\|phase diagram\|structural law\|SSCS" submission/` returns 0

## Task 016E — Repository Clean-Figure Verification

### Protocol
1. Fresh `pip install -r repository/requirements.txt`
2. `python repository/reproduce_figures.py`
3. Compare generated figures against `submission/figures/` (visual inspection or hash)
4. Document any deviations in reproducibility_statement.md

### Acceptance
- All 14 manuscript figures match repository output
- No manual steps required between install and output

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| Mahalanobis requires invertible cov | Medium | Use pseudoinverse + regularization if singular |
| Data files too large for repository | Low | Keep tier2_data/ reference; repository downloads automatically |
| Number of permutations too expensive | Low | 1000 permutations sufficient for p < 0.001 resolution |
| Phase 015 results take hours to regenerate | Medium | Store cached results in repository; regeneration is opt-in |

## File Inventory

### To create
- `repository/statistical_comparison.py` — Mahalanobis, permutation, bootstrap, CI functions
- `repository/phase_015_controls.py` — runnable Phase 015 experiments
- `repository/phase_015_results/` — cached output files

### To update
- `repository/README.md` — describe statistical methods and null controls
- `repository/reproduce_figures.py` — ensure standalone; add Mahalanobis output
- `repository/data_manifest.md` — complete file listing

### To verify
- Both manuscripts: zero forbidden terminology
- `submission/figures/`: all 14 PDFs reproducible
