# Residual(C) Structure Search: Which known quantities does Residual(C) correspond to?

**Audit ID**: RD-017-D1
**Date**: 2026-06-05
**Question**: For every structural variable computable from the existing granular DEM data, what is its correlation with Residual(C)?

## Method

22 structural descriptors were extracted from raw grain trajectories (50 grains, 1000 timesteps) by re-running all 60 DEM simulations with the same seeds as `t901_ensemble.json`. Descriptors span five categories:

- **Contact-based**: mean coordination number, contact count (per snapshot), contact density
- **Overlap/force**: mean overlap, overlap standard deviation, overlap CV (force heterogeneity proxy)
- **Graph/network**: clustering coefficient, number of connected components, largest component fraction
- **Structural/spatial**: mean nearest neighbor distance, NN distance std/skew, Delaunay (Voronoi) area mean/std/CV, radial distribution function g(r) peak height/position/second peak
- **Temporal**: contact network Jaccard similarity (mean, std) — how much the contact graph changes between timesteps

Plus 7 pre-existing variables (4 mobility proxies + 3 competitor metrics) for comparison, totaling 29 candidates.

Residual(C) was computed as `C − E[C | friction]` via linear regression (R² = 0.793, i.e., C ~ friction explains 79.3% of C variance).

## Results

### Top 10 correlates of Residual(C)

| Rank | Variable | Pearson r | p-value | R² | Category | Direction |
|------|----------|-----------|---------|-----|----------|-----------|
| 1 | **pre_MSE_s1** (multiscale entropy) | **−0.420** | 0.0008 | 0.176 | Competitor metric | Higher residual(C) → lower MSE |
| 2 | **mean_nn_dist** (mean nearest neighbor dist) | **+0.347** | 0.0066 | 0.120 | Spatial | Higher residual(C) → more sparse |
| 3 | **pre_C_sigma** (statistical complexity) | **−0.339** | 0.0081 | 0.115 | Competitor metric | Higher residual(C) → less complex |
| 4 | **pre_I_pred** (predictive information) | **+0.310** | 0.0160 | 0.096 | Competitor metric | Higher residual(C) → more predictable |
| 5 | **mean_n_components** | **+0.296** | 0.0217 | 0.088 | Network | More fragmented |
| 6 | **mean_delaunay_area** | **+0.295** | 0.0222 | 0.087 | Spatial | Larger Voronoi cells |
| 7 | **mean_largest_comp** | **−0.293** | 0.0232 | 0.086 | Network | Smaller largest cluster |
| 8 | **mean_contact_count** | **−0.291** | 0.0239 | 0.085 | Contact | Fewer contacts |
| 9 | **contact_density** | **−0.291** | 0.0239 | 0.085 | Contact | Lower contact density |
| 10 | **mean_coordination** | **−0.291** | 0.0239 | 0.085 | Contact | Lower coordination |

### Full ranked table (all 29 variables)

| Rank | Variable | r | p | R² | Category |
|------|----------|-----|------|------|----------|
| 1 | pre_MSE_s1 | −0.420 | 8.4e-4 | 0.176 | Competitor metric |
| 2 | mean_nn_dist | +0.347 | 6.6e-3 | 0.120 | Spatial |
| 3 | pre_C_sigma | −0.339 | 8.1e-3 | 0.115 | Competitor metric |
| 4 | pre_I_pred | +0.310 | 0.016 | 0.096 | Competitor metric |
| 5 | mean_n_components | +0.296 | 0.022 | 0.088 | Network |
| 6 | mean_delaunay_area | +0.295 | 0.022 | 0.087 | Spatial |
| 7 | mean_largest_comp | −0.293 | 0.023 | 0.086 | Network |
| 8 | mean_contact_count | −0.291 | 0.024 | 0.085 | Contact |
| 9 | contact_density | −0.291 | 0.024 | 0.085 | Contact |
| 10 | mean_coordination | −0.291 | 0.024 | 0.085 | Contact |
| 11 | mean_clustering | −0.271 | 0.037 | 0.073 | Network |
| 12 | delaunay_area_std | +0.265 | 0.040 | 0.070 | Spatial |
| 13 | nn_dist_std | +0.265 | 0.041 | 0.070 | Spatial |
| 14 | packing_var | +0.264 | 0.041 | 0.070 | Spatial |
| 15 | overlap_cv | +0.261 | 0.044 | 0.068 | Force |
| 16 | mean_overlap | −0.212 | 0.104 | 0.045 | Force |
| 17 | delaunay_area_cv | +0.206 | 0.115 | 0.042 | Spatial |
| 18 | contact_jaccard_mean | −0.174 | 0.183 | 0.030 | Temporal |
| 19 | nn_dist_skew | +0.160 | 0.222 | 0.026 | Spatial |
| 20 | g_r_second_peak | −0.156 | 0.233 | 0.025 | Structural |
| 21 | msd | −0.153 | 0.245 | 0.023 | Mobility |
| 22 | rms_velocity | −0.141 | 0.283 | 0.020 | Mobility |
| 23 | contact_jaccard_std | +0.110 | 0.403 | 0.012 | Temporal |
| 24 | overlap_std | −0.108 | 0.412 | 0.012 | Force |
| 25 | clustering_std | +0.107 | 0.418 | 0.011 | Network |
| 26 | coord_std | +0.106 | 0.419 | 0.011 | Contact |
| 27 | g_r_peak_height | −0.078 | 0.554 | 0.006 | Structural |
| 28 | neighbor_turnover | −0.010 | 0.942 | 0.000 | Mobility |
| 29 | g_r_peak_pos | NaN | NaN | — | (constant) |

## Interpretation

### A coherent structural picture emerges

All significant correlations point in the same physical direction. Higher Residual(C) (i.e., more coherence than expected for a given friction level) corresponds to:

| Property | Direction | Interpretation |
|----------|-----------|---------------|
| Nearest neighbor distance | **Larger** (r=+0.35) | Grains are more spread out |
| Delaunay cell areas | **Larger** (r=+0.30) | Voronoi-like cells are bigger |
| Contact count / coordination | **Lower** (r=−0.29) | Fewer grain-grain contacts |
| Contact network components | **More** (r=+0.30) | More fragmented, less connected |
| Largest component | **Smaller** (r=−0.29) | Less percolation |
| Clustering coefficient | **Lower** (r=−0.27) | Less local triangle formation |
| Multiscale entropy | **Lower** (r=−0.42) | Less dynamical complexity |
| Predictive information | **Higher** (r=+0.31) | More predictable dynamics |

**High Residual(C) describes a sparse, less-connected, more predictable packing.**

This is physically sensible: given a fixed friction level (which constrains mobility and average C), the runs that happen to have more open structure (larger grain-grain distances, fewer contacts) have higher coherence. The interaction structure is more prominent when grains are not jammed against each other, because there is more "room" for correlation between grain motions.

### But Residual(C) is NOT reducible to any single descriptor

The strongest single correlate is pre_MSE_s1 (multiscale entropy) at R² = 0.176. All other descriptors explain ≤ 12%. The gradient from #1 (R²=0.176) to #5 (R²=0.088) is continuous rather than gappy — no single descriptor dominates.

This suggests Residual(C) corresponds to a **latent structural mode** that is distributed across multiple observables, not concentrated in any single known quantity.

### Mobility proxies are irrelevant

MSD (r=−0.15), RMS velocity (r=−0.14), and neighbor turnover (r=−0.01) are among the weakest correlates. This confirms the RD-016 finding that Residual(C) is not a mobility proxy.

## Conclusion

Residual(C) corresponds to a **sparseness/disconnectedness dimension** of the granular packing:
- Higher residual(C) → looser, less connected, more predictable packing
- Lower residual(C) → denser, more connected, more dynamically complex packing

But the signal is weak for any single descriptor (max R² = 0.176). No existing structural variable fully explains Residual(C). This points toward either:
1. A **composite latent variable** requiring multiple structural descriptors to capture (see D2), or
2. A **novel structural quantity** not captured by any standard granular descriptor we computed.

## Supporting data

All structural descriptors saved to `audits/rd017_structural_descriptors.json` for independent verification.
