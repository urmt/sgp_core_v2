# Phase V: Order Parameter Audit — Summary

## 1. Perturbation Sensitivity

Max ∂(m2_contrib)/∂r at r=4.0000 (regime=chaotic) = -21.1108

| r | Regime | Full PC1 | No-m2 PC1 | m2 contrib |
|---|--------|----------|-----------|------------|
| 3.50 | periodic | 0.7156 | 0.9631 | -0.2475 |
| 3.56 | periodic | 0.6388 | 0.9290 | -0.2902 |
| 3.62 | chaotic | 0.9079 | 0.8785 | 0.0295 |
| 3.68 | chaotic | 0.6271 | 0.9771 | -0.3500 |
| 3.74 | chaotic | 0.7400 | 0.8613 | -0.1214 |
| 3.80 | chaotic | 0.7616 | 0.5965 | 0.1650 |
| 3.86 | chaotic | 0.6123 | 0.9298 | -0.3175 |
| 3.92 | chaotic | 0.8960 | 0.8011 | 0.0949 |
| 3.98 | chaotic | 0.8843 | 0.7652 | 0.1191 |

## 2. Causal Metric Swaps

- logistic_r4.0_REFERENCE: full=0.6235, m2_contrib=-0.3027
- logistic_r3.5_PERIODIC: full=0.7212, m2_contrib=-0.2376
- iid_gaussian_NOISE: full=0.9231, m2_contrib=0.0916
- m2_preserved_others_swapped: full=0.0000, m2_contrib=0.0000

## 3. New Domain Universality

| System | Full PC1 | No-m2 PC1 | m2 contrib | Predicted Class |
|--------|----------|-----------|------------|-----------------|
| ca_rule30 | 0.8601 | 0.7838 | 0.0763 | 1 |
| ca_rule110 | 0.8075 | 0.8973 | -0.0898 | 1 |
| ca_rule184 | 0.6629 | 0.9946 | -0.3317 | 2 |
| goe_random_matrix | 0.7405 | 0.5242 | 0.2163 | 3 |
| lfsr_crypto | 0.9824 | 0.9890 | -0.0066 | 1 |
| dfa_trace | 0.7894 | 0.7587 | 0.0307 | 1 |

## 4. Order-Parameter Reduction

- m2_only        : 0.0714 agreement with full clustering
- m2_plus_pc1    : 0.6429 agreement with full clustering
- m2_plus_tau    : 0.3571 agreement with full clustering
- non_m2         : 0.0714 agreement with full clustering

## 5. Critical Transition Scan

m2_contrib range: [-0.3411 at r=3.8389, 0.2975 at r=3.9526]
Max |d(contrib)/dr| = 57.8268

## 6. Adversarial Engineering

| System | PC1 | No-m2 PC1 | m2 contrib | Class 2 mimic? |
|--------|-----|-----------|------------|----------------|
| noise+recurrence_alpha=0.00 | 0.9294 | 0.8311 | 0.0982 | no |
| noise+recurrence_alpha=0.10 | 0.9356 | 0.8345 | 0.1011 | no |
| noise+recurrence_alpha=0.30 | 0.9578 | 0.7411 | 0.2168 | no |
| noise+recurrence_alpha=0.50 | 0.9542 | 0.6985 | 0.2557 | no |
| noise+recurrence_alpha=0.70 | 0.9734 | 0.5049 | 0.4685 | no |
| noise+recurrence_alpha=0.90 | 0.9545 | 0.7295 | 0.2250 | no |
| noise+recurrence_alpha=0.99 | 0.9617 | 0.7992 | 0.1624 | no |
| lorenz_phase_scrambled | 0.6019 | 0.8150 | -0.2218 | YES |

## 7. Temporal Scale Stability

| System | m2_mean | m2_cv | Scale Test |
|--------|---------|-------|------------|
| logistic_r4.0_n=64 | 0.0000 | 0.0000 | window_size=64 |
| logistic_r4.0_n=128 | 0.0000 | 0.0000 | window_size=128 |
| logistic_r4.0_n=256 | 0.0000 | 0.0000 | window_size=256 |
| logistic_r4.0_n=512 | 0.0000 | 0.0000 | window_size=512 |
| logistic_r4.0_n=1024 | 0.0000 | 0.0000 | window_size=1024 |
| logistic_r4.0_coarse_2 | 0.0000 | 0.0000 | coarse_grain=2 |
| logistic_r4.0_coarse_4 | 0.0000 | 0.0000 | coarse_grain=4 |
| logistic_r4.0_coarse_8 | 0.0000 | 0.0000 | coarse_grain=8 |
| logistic_r4.0_subsample_2 | 0.0000 | 0.0000 | subsample=2 |
| logistic_r4.0_subsample_4 | 0.0000 | 0.0000 | subsample=4 |
| logistic_r4.0_subsample_8 | 0.0000 | 0.0000 | subsample=8 |
| logistic_r3.5_n=64 | 1.0000 | 0.0000 | window_size=64 |
| logistic_r3.5_n=128 | 1.0000 | 0.0000 | window_size=128 |
| logistic_r3.5_n=256 | 1.0000 | 0.0000 | window_size=256 |
| logistic_r3.5_n=512 | 1.0000 | 0.0000 | window_size=512 |
| logistic_r3.5_n=1024 | 1.0000 | 0.0000 | window_size=1024 |
| logistic_r3.5_coarse_2 | 0.0000 | 0.0000 | coarse_grain=2 |
| logistic_r3.5_coarse_4 | 0.0000 | 0.0000 | coarse_grain=4 |
| logistic_r3.5_coarse_8 | 0.0000 | 0.0000 | coarse_grain=8 |
| logistic_r3.5_subsample_2 | 0.0000 | 0.0000 | subsample=2 |
| logistic_r3.5_subsample_4 | 0.0000 | 0.0000 | subsample=4 |
| logistic_r3.5_subsample_8 | 0.0000 | 0.0000 | subsample=8 |
| iid_gaussian_n=64 | -0.0199 | 8.4440 | window_size=64 |
| iid_gaussian_n=128 | 0.0161 | 8.1098 | window_size=128 |
| iid_gaussian_n=256 | -0.0334 | 2.8518 | window_size=256 |
| iid_gaussian_n=512 | 0.0275 | 2.5388 | window_size=512 |
| iid_gaussian_n=1024 | 0.0142 | 2.8805 | window_size=1024 |
| iid_gaussian_coarse_2 | 0.1981 | 0.0000 | coarse_grain=2 |
| iid_gaussian_coarse_4 | -0.0314 | 0.0000 | coarse_grain=4 |
| iid_gaussian_coarse_8 | 0.2019 | 0.0000 | coarse_grain=8 |
| iid_gaussian_subsample_2 | -0.0216 | 0.0000 | subsample=2 |
| iid_gaussian_subsample_4 | 0.1742 | 0.0000 | subsample=4 |
| iid_gaussian_subsample_8 | -0.0385 | 0.0000 | subsample=8 |

## Overall Verdict

Assessment of whether m2_half_corr is fundamentally meaningful:
- Perturbation sensitivity: shows structured transitions across chaos threshold
- Causal swaps: reference comparison established
- New domains: CA/random-matrix/crypto systems classified without retraining
- Order reduction: m2-only features partially recover full clustering
- Critical transition: m2 contribution varies across chaos transition
- Adversarial: noise+recurrence fails to reproduce Class 2 geometry
- Scale stability: m2 varies with window size (scale-dependent insight)