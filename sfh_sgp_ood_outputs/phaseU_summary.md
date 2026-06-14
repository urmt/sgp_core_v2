# Phase U: Organizational Geometry Classification — Summary

## Test 1: Geometry Clustering

**Silhouette score**: 0.3517

| System | Cluster | Category |
|--------|---------|----------|
| primes | 1 | arithmetic |
| fibonacci | 1 | arithmetic |
| modular_arithmetic | 1 | arithmetic |
| additive_recurrence | 3 | arithmetic |
| lorenz | 2 | dynamical |
| logistic_map | 3 | dynamical |
| henon_map | 3 | dynamical |
| ising_magnetization | 2 | dynamical |
| reaction_diffusion | 2 | dynamical |
| cfg_expansion | 1 | symbolic |
| lambda_reduction | 1 | symbolic |
| rewrite_system | 1 | symbolic |
| iid_gaussian | 3 | random_control |
| colored_noise | 3 | random_control |

## Test 2: Class Stability

- remove_spectral: agreement=0.0714
- remove_tau_axis: agreement=0.2857
- remove_null_audit: agreement=0.1429
- remove_replay: agreement=0.5714
- remove_ablation: agreement=0.0714
- gaussian_noise_0.3 (n=50): agreement=0.4171

## Test 3: Cross-Metric Transfer

- view1→view2: cv=0.933 transfer=0.786
- view2→view1: cv=0.783 transfer=0.929

## Test 4: Minimal Class Basis

- [3 feat] effective_rank+phase_corr+abl_no_m2_pc1: agreement=1.0000
- [3 feat] pc1+pc1_ratio+abl_no_m2_pc1: agreement=1.0000
- [3 feat] effective_rank+replay_displacement+abl_no_m2_pc1: agreement=1.0000
- [3 feat] temporal_corr+phase_corr+replay_displacement: agreement=0.9286
- [3 feat] tau_m2+phase_corr+replay_displacement: agreement=0.9286

## Test 5: Empirical Class Semantics

**Adjusted Rand Index (cluster vs. category)**: 0.2716

- Cluster 1: arithmetic=50%, symbolic=50%
- Cluster 2: dynamical=100%
- Cluster 3: arithmetic=20%, dynamical=40%, random_control=40%

## Test 6: Adversarial Artifact

- Real silhouette: 0.3517
- Synthetic silhouette: 0.2795
- Ratio: 1.26
- Verdict: MODERATE ARTIFACT RISK: synthetic clusters but less cleanly

## Test 7: Transition Geometry

- Intra-category distance: 5.483
- Inter-category distance: 5.765
- Intra/inter ratio: 0.951
- Transition type: smooth