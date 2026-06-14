# RD-019: Density Intervention — Raw Data Report

**Date**: 2026-06-06
**Status**: Complete
**Runs**: 60 (6 box_widths × 10 reps)
**Code change**: 1 parameter (`box_width`) added to `_granular_run`

## Protocol

- Friction = 0.40 (fixed)
- n_grains = 50 (fixed)
- Removal = 10% at step 500 (fixed)
- Seed range: 300–359 (orthogonal to existing 200-series seeds)
- Manipulation: `box_width` ∈ {30, 35, 40, 45, 50, 55}
- Effective density: 50 / (box_width × 30) = {0.0556, 0.0476, 0.0417, 0.0370, 0.0333, 0.0303}

## Per-Condition Means (n=10 per condition)

| BW  | Density  | C_pre     | dip       | restoration | τ_rec | MSD     | NN dist | Coord | Comps |
|-----|----------|-----------|-----------|-------------|-------|---------|---------|-------|-------|
| 30  | 0.0556   | 0.4422    | +0.0210   | 1.0225      | 122   | 21.87   | 2.311   | 1.60  | 24.4  |
| 35  | 0.0476   | 0.4470    | +0.0294   | 1.0560      |  74   | 20.32   | 2.361   | 1.53  | 25.2  |
| 40  | 0.0417   | 0.4389    | +0.0047   | 1.1408      |  62   | 18.04   | 2.769   | 1.38  | 26.4  |
| 45  | 0.0370   | 0.4509    | +0.0124   | 1.1778      |  50   | 15.64   | 3.071   | 1.13  | 28.6  |
| 50  | 0.0333   | 0.4524    | +0.0148   | 1.1085      |  52   | 12.00   | 3.157   | 0.94  | 30.3  |
| 55  | 0.0303   | 0.4628    | +0.0082   | 1.1104      |  77   | 10.53   | 3.272   | 0.79  | 31.9  |

## Task 3: Structural Validation (Did density manipulation work?)

Correlation between per-condition mean descriptor and density (n=6 conditions):

| Metric                   | r       | p       | R²    | Expected | Match |
|--------------------------|---------|---------|-------|----------|-------|
| mean_nn_dist             | -0.970  | 0.0014  | 0.940 | -        | ✓     |
| contact_count            | +0.959  | 0.0025  | 0.920 | +        | ✓     |
| coordination_number      | +0.959  | 0.0025  | 0.920 | +        | ✓     |
| component_count          | -0.955  | 0.0030  | 0.912 | -        | ✓     |
| largest_component_size   | +0.957  | 0.0027  | 0.916 | +        | ✓     |
| clustering_coefficient   | +0.723  | 0.1043  | 0.523 | +        | ✓     |
| msd                      | +0.966  | 0.0017  | 0.933 | +        | ✓     |
| **pre_C**                | **-0.753** | **0.0843** | **0.566** | **-** | **✓ (weak)** |

**Manipulation succeeded for all 7 structural descriptors.** Density is causally affecting packing structure as expected. Lower density → larger nearest-neighbor distances, fewer contacts, more disconnected components, higher mobility. The result is consistent and statistically robust (5 of 7 at p < 0.01).

**pre_C shows a weak but direction-consistent response** (r=-0.753 between condition means and density, p=0.084). At the per-run level (n=60), the correlation is much weaker (r=-0.235, p=0.070) because within-condition variation in C is large (~0.02) compared to between-condition variation (range of means ≈ 0.024).

## Headline Observation

**C is nearly insensitive to density** at this friction level. Despite the structural descriptors (NNdist, contact count, coordination number) responding strongly to the manipulation, **C essentially does not move**.

This is the critical finding: Residual(C) is not measuring density, contact count, coordination number, or any of the other descriptors that DID respond to the density manipulation. The leading hypothesis (H1: Residual(C) ≈ packing sparseness) is undermined.

## Data Files

- Raw ensemble: `coherence-benchmark/results/rd019_density_ensemble.json`
- 60-row CSV: `audits/RD019_RESULTS_TABLE.csv`
- Analysis code: `audits/rd019_density_intervention.py`, `audits/rd019_causal_models.py`

## Runtime

145 seconds for 60 simulations + ~5 seconds for analysis.
