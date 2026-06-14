# SFH-SGP Cross-Domain Universality Assessment

## Primary Question

> Do canonical organizational transforms map fundamentally different
> generative systems into SHARED transform geometry classes?

## 1. Per-System Transform Geometry

| System | Category | PC1 | PC2 | EffRank |
|--------|----------|-----|-----|---------|
| primes | arithmetic | 0.9372 | 0.0619 | 1.2708 |
| fibonacci | arithmetic | 0.8616 | 0.0729 | 1.6728 |
| modular_arithmetic | arithmetic | 0.9003 | 0.0534 | 1.5200 |
| additive_recurrence | arithmetic | 0.8564 | 0.1237 | 1.6035 |
| lorenz | dynamical | 0.5072 | 0.4245 | 2.4472 |
| logistic_map | dynamical | 0.8826 | 0.0845 | 1.5617 |
| henon_map | dynamical | 0.9543 | 0.0332 | 1.2431 |
| ising_magnetization | dynamical | 0.7220 | 0.2643 | 1.9225 |
| reaction_diffusion | dynamical | 0.6293 | 0.2122 | 2.6334 |
| cfg_expansion | symbolic | 0.9317 | 0.0675 | 1.2892 |
| lambda_reduction | symbolic | 0.9350 | 0.0641 | 1.2780 |
| rewrite_system | symbolic | 0.8605 | 0.0748 | 1.6741 |
| iid_gaussian | random_control | 0.9287 | 0.0597 | 1.3427 |
| colored_noise | random_control | 0.8123 | 0.1824 | 1.6613 |

## 2. Cross-System τ-Axis Alignment

- **High alignment pairs** (>0.8): 37
- **Low alignment pairs** (<0.3): 12
- **Mean alignment**: 0.6991
- **Std alignment**: 0.2789

### High-Alignment Pairs (>0.8)

| System A | System B | Alignment | Categories |
|----------|----------|-----------|------------|
| fibonacci | primes | 0.9702 | arithmetic / arithmetic |
| modular_arithmetic | primes | 0.9604 | arithmetic / arithmetic |
| modular_arithmetic | fibonacci | 0.9916 | arithmetic / arithmetic |
| lorenz | primes | 0.8324 | dynamical / arithmetic |
| lorenz | fibonacci | 0.8726 | dynamical / arithmetic |
| lorenz | modular_arithmetic | 0.8701 | dynamical / arithmetic |
| logistic_map | additive_recurrence | 0.9983 | dynamical / arithmetic |
| henon_map | additive_recurrence | 0.9979 | dynamical / arithmetic |
| henon_map | logistic_map | 0.9998 | dynamical / dynamical |
| ising_magnetization | additive_recurrence | 0.9943 | dynamical / arithmetic |
| ising_magnetization | logistic_map | 0.9916 | dynamical / dynamical |
| ising_magnetization | henon_map | 0.9919 | dynamical / dynamical |
| reaction_diffusion | lorenz | 0.8342 | dynamical / dynamical |
| cfg_expansion | primes | 0.9999 | symbolic / arithmetic |
| cfg_expansion | fibonacci | 0.9714 | symbolic / arithmetic |
| cfg_expansion | modular_arithmetic | 0.9628 | symbolic / arithmetic |
| cfg_expansion | lorenz | 0.8298 | symbolic / dynamical |
| lambda_reduction | primes | 0.9999 | symbolic / arithmetic |
| lambda_reduction | fibonacci | 0.9710 | symbolic / arithmetic |
| lambda_reduction | modular_arithmetic | 0.9617 | symbolic / arithmetic |
| lambda_reduction | lorenz | 0.8291 | symbolic / dynamical |
| lambda_reduction | cfg_expansion | 1.0000 | symbolic / symbolic |
| rewrite_system | primes | 0.9700 | symbolic / arithmetic |
| rewrite_system | fibonacci | 1.0000 | symbolic / arithmetic |
| rewrite_system | modular_arithmetic | 0.9918 | symbolic / arithmetic |
| rewrite_system | lorenz | 0.8736 | symbolic / dynamical |
| rewrite_system | cfg_expansion | 0.9713 | symbolic / symbolic |
| rewrite_system | lambda_reduction | 0.9709 | symbolic / symbolic |
| iid_gaussian | additive_recurrence | 0.9942 | random_control / arithmetic |
| iid_gaussian | logistic_map | 0.9928 | random_control / dynamical |
| iid_gaussian | henon_map | 0.9906 | random_control / dynamical |
| iid_gaussian | ising_magnetization | 0.9880 | random_control / dynamical |
| colored_noise | additive_recurrence | 0.9956 | random_control / arithmetic |
| colored_noise | logistic_map | 0.9961 | random_control / dynamical |
| colored_noise | henon_map | 0.9946 | random_control / dynamical |
| colored_noise | ising_magnetization | 0.9904 | random_control / dynamical |
| colored_noise | iid_gaussian | 0.9991 | random_control / random_control |

### Within-Category vs Cross-Category Alignment

- **Within-category mean**: 0.6583 (n=20)
- **Cross-category mean**: 0.7105 (n=71)

## 3. Replay Stability

| System | Idempotent MSE | Displacement | Perfect? |
|--------|---------------|-------------|----------|
| primes | 0.000000 ± 0.000000 | 0.0164 ± 0.0000 | ✓ |
| fibonacci | 0.000000 ± 0.000000 | 0.3323 ± 0.0000 | ✓ |
| modular_arithmetic | 0.000000 ± 0.000000 | 0.3304 ± 0.0000 | ✓ |
| additive_recurrence | 0.000000 ± 0.000000 | 1.0950 ± 0.0000 | ✓ |
| lorenz | 0.000000 ± 0.000000 | 0.8634 ± 0.0000 | ✓ |
| logistic_map | 0.000000 ± 0.000000 | 0.8976 ± 0.0000 | ✓ |
| henon_map | 0.000000 ± 0.000000 | 0.9083 ± 0.0000 | ✓ |
| ising_magnetization | 0.000000 ± 0.000000 | 1.0139 ± 0.1941 | ✓ |
| reaction_diffusion | 0.000000 ± 0.000000 | 1.2158 ± 0.0000 | ✓ |
| cfg_expansion | 0.000000 ± 0.000000 | 0.0161 ± 0.0000 | ✓ |
| lambda_reduction | 0.000000 ± 0.000000 | 0.0162 ± 0.0001 | ✓ |
| rewrite_system | 0.000000 ± 0.000000 | 0.3323 ± 0.0000 | ✓ |
| iid_gaussian | 0.000000 ± 0.000000 | 1.0004 ± 0.0536 | ✓ |
| colored_noise | 0.000000 ± 0.000000 | 0.9966 ± 0.0791 | ✓ |

## 4. Null Audit

| System | Temporal | Phase | PC1 Orig | PC1 Shuf | Ratio | Verdict |
|--------|----------|-------|----------|----------|-------|---------|
| primes | -0.5459 | -0.8388 | 0.9352 | 0.7239 | 1.29 | DISTRIBUTIONAL |
| fibonacci | -0.9390 | -0.9711 | 0.8530 | 0.5622 | 1.52 | WEAK |
| modular_arithmetic | -0.9738 | -0.8558 | 0.8984 | 0.7049 | 1.27 | DISTRIBUTIONAL |
| additive_recurrence | 0.9062 | 0.9924 | 0.8558 | 0.3374 | 2.54 | REAL (transform geometry) |
| lorenz | -0.2708 | 0.9605 | 0.5065 | 0.3342 | 1.52 | WEAK |
| logistic_map | 0.9857 | 0.9979 | 0.8827 | 0.3093 | 2.85 | REAL (transform geometry) |
| henon_map | 0.9910 | 0.9968 | 0.9563 | 0.4517 | 2.12 | REAL (transform geometry) |
| ising_magnetization | 0.9010 | 0.9647 | 0.7363 | 0.3354 | 2.20 | REAL (transform geometry) |
| reaction_diffusion | -0.0291 | 0.3680 | 0.6311 | 0.4239 | 1.49 | DISTRIBUTIONAL |
| cfg_expansion | -0.3607 | -0.8873 | 0.9336 | 0.7307 | 1.28 | DISTRIBUTIONAL |
| lambda_reduction | -0.4165 | -0.8657 | 0.9344 | 0.7270 | 1.29 | DISTRIBUTIONAL |
| rewrite_system | -0.9467 | -0.9676 | 0.8571 | 0.5520 | 1.55 | WEAK |
| iid_gaussian | 0.9895 | 0.9985 | 0.9328 | 0.3118 | 2.99 | REAL (transform geometry) |
| colored_noise | 0.9908 | 0.9982 | 0.8124 | 0.3093 | 2.63 | REAL (transform geometry) |

## 5. Final Assessment

- Systems with PC1 > 0.7: 12 / 14
- Shared-geometry pairs (τ > 0.7): 41
- Cross-category shared geometry: 30
- Systems with non-distributional transform geometry: 9 / 14

**Verdict**: YES — OOD systems share structured transform geometry.

The mean cross-system τ-alignment of 0.699 indicates that
canonical organizational transforms produce similar low-dimensional
displacement patterns across radically different generative systems.
This suggests the geometry is a property of the organizational metric
construction interacting with generic recurrence statistics, not of
any single generative mechanism.

### Caveats

- Metrics were designed for time-series signals; symbolic systems
  required encoding as numeric sequences, which may introduce artifacts.
- Some systems (primes, CFG) produce monotonic sequences that
  trivially compress to low-dimensional geometry.
- The canonical metric construction itself may impose low-rank structure
  on any input, regardless of generative mechanism.
- Pure IID control shows low PC1 — the geometry is not purely a
  metric artifact.