# Metric Ablation & Artifact Diagnostic

## Design

For each system, compute transform PC1 using:
- Full 4-metric vector
- 3-metric subsets (remove one metric at a time)
- Single-metric versions (each metric alone)

If PC1 stays high (>0.8) after removing a metric, that metric is 
*redundant* for the geometry. If PC1 drops sharply, that metric 
is the *driver* of the low-dimensional structure.

Key artifact question: does IID Gaussian noise lose its high PC1
when m2_half_corr is removed?

## PC1 by Ablation Set

ablation              full  m1_only  m2_only  m3_only  m4_only  no_m1  no_m2  no_m3  no_m4
system                                                                                    
cfg_expansion       0.9343   1.0000   1.0000   1.0000   1.0000 0.9047 0.9285 0.9767 0.9329
constant            0.9786   1.0000   1.0000   1.0000   1.0000 0.9769 0.9846 0.8675 0.9878
henon_map           0.9569   1.0000   1.0000   1.0000   1.0000 0.9684 0.7650 0.9609 0.9881
iid_gaussian        0.9304   1.0000   1.0000   1.0000   1.0000 0.9241 0.6787 0.9550 0.9547
ising_magnetization 0.6374   1.0000   1.0000   1.0000   1.0000 0.6095 0.9566 0.9542 0.6035
linear_ramp         0.7752   1.0000   1.0000   1.0000   1.0000 0.6506 0.9629 0.7572 0.7697
logistic_map        0.8835   1.0000   1.0000   1.0000   1.0000 0.9069 0.6967 0.8863 0.9627
lorenz              0.5066   1.0000   1.0000   1.0000   1.0000 0.8068 0.8844 0.5423 0.4932
primes              0.9400   1.0000   1.0000   1.0000   1.0000 0.9114 0.9284 0.9773 0.9343

## Artifact Driver Analysis

IID Gaussian full PC1: 0.9304
IID Gaussian no_m2 PC1: 0.6787
Drop when removing m2: 0.2516
**Conclusion: artifact is distributed across metrics.**
No single metric drives the noise artifact.

## Per-System Dominant Metric

(The single metric that, when removed, drops PC1 the most)

| System | Full PC1 | Dominant Metric | PC1 w/o it | Drop |
|--------|----------|-----------------|------------|------|
| constant             | 0.9786 | no_m3 (m3_compress)            | 0.8675 | 0.1111 |
| linear_ramp          | 0.7752 | no_m1 (m1_flow)                | 0.6506 | 0.1246 |
| iid_gaussian         | 0.9304 | no_m2 (m2_half_corr)           | 0.6787 | 0.2516 |
| primes               | 0.9400 | no_m1 (m1_flow)                | 0.9114 | 0.0286 |
| lorenz               | 0.5066 | no_m4 (m4_transition)          | 0.4932 | 0.0134 |
| logistic_map         | 0.8835 | no_m2 (m2_half_corr)           | 0.6967 | 0.1868 |
| henon_map            | 0.9569 | no_m2 (m2_half_corr)           | 0.7650 | 0.1919 |
| ising_magnetization  | 0.6374 | no_m4 (m4_transition)          | 0.6035 | 0.0339 |
| cfg_expansion        | 0.9343 | no_m1 (m1_flow)                | 0.9047 | 0.0297 |

## Single-Metric PC1 (each metric alone)

| System | m1_flow | m2_half_corr | m3_compress | m4_transition |
|--------|---------|-------------|-------------|---------------|
| constant             | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| linear_ramp          | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| iid_gaussian         | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| primes               | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| lorenz               | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| logistic_map         | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| henon_map            | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ising_magnetization  | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| cfg_expansion        | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

## Interpretation

- If single-metric PC1 is ~1.0 for ALL systems including noise,
  that metric is a *trivial* organizational metric (all transforms
  affect it the same way).
- If single-metric PC1 varies by system, the metric carries
  system-specific information.
- If removing m2 drops PC1 for noise but NOT for structured systems,
  then structured systems have geometry BEYOND the metric artifact.