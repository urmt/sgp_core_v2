# RD-019 Executive Recommendation: Causal Intervention

**Date**: 2026-06-06
**Status**: Ready for approval

## One-Sentence Summary

Run 80 density-sweep simulations at friction = 0.40 to determine whether the coordination number (C) is a causal packing state or merely a statistical thermometer.

## Why Now

After 69 structural variables tested across 6 families (RD-017/018), the observational search for Residual(C)'s identity is **saturated**. Multiple entire hypothesis classes have been ruled out (force heterogeneity, fabric anisotropy, non-affine rearrangement, community structure). The best descriptor achieves R² = 0.176. Further descriptor extraction has diminishing returns.

The project must now pivot from **correlation** to **intervention** to resolve the central question: is Residual(C) a causal state or a predictive signature?

## The Experiment

**80 runs · 1 line of code · 4 minutes runtime**

| Parameter | Value |
|-----------|-------|
| Manipulation | `box_width` (25, 30, 35, 40, 45, 50, 55, 60) |
| Fixed | friction = 0.40, n_grains = 50, removal = 10% |
| Sample | 8 densities × 10 replicates = 80 runs |
| Seeds | 0–79 (orthogonal to existing ensemble) |
| Analysis | Baron & Kenny mediation: density → C → recovery |
| Modification | 1 parameter added to `_granular_run` signature |

## What It Tests

The leading hypothesis (H1: Residual(C) ≈ packing sparseness) predicts that when we vary initial density while holding friction fixed:
1. **C varies with density** (tighter packing → lower C)
2. **Recovery varies with density** (tighter packing → worse recovery)
3. **C mediates the density→recovery relationship** (controlling for C eliminates or reduces density's effect on recovery)

If all three hold → Residual(C) IS a causal packing state. If they don't → it's a thermometer.

## Decision Options

| If the result is... | Then... | Time to next decision |
|---------------------|---------|----------------------|
| Strong mediation (C carries ≥70% of density effect) | H1 confirmed. Residual(C) ≈ packing sparseness. Next: test generalizability across friction. | ~5 min to generalize |
| Partial mediation (30–70%) | Ambiguous. Residual(C) captures part of density but not all. Next: design new experiment. | ~30 min to design |
| No mediation | Thermometer view gains support. C predicts but doesn't cause. Next: accept Residual(C) as recovery signature; close. | Project milestone |

## Priority Score

Ranked #2 among 10 candidates overall. Ranked #1 for minimal experiment (best information-per-second: 0.46 pts/s, 1.8× the next best). Tied for easiest code change (1 line).

The top overall candidate (full friction×density grid) would take 450s for an additional 2-point gain in information. Not justified for the minimal mandate.

## Resource Request

- Compute: 80 cores × 3 seconds = 240 core-seconds (negligible)
- Disk: ~80 MB for trajectories
- Code: 1 parameter added to function signature
- Analysis: ~30 minutes of interactive work

## Risk Summary

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Density doesn't affect C | 10% | Experiment fails | 2.4× density range; effect visible in existing data |
| Ambiguous mediation | 35% | Follow-up needed | Designed sequential analysis (check at n=40) |
| Wall effects at extreme widths | 20% | Exclude outermost conditions | Post-hoc removal of extreme widths if needed |

## Expected Information Gain

- 40% probability of strong conclusion (H1 confirmed)
- 25% probability of strong conclusion (thermometer supported)
- 35% probability of ambiguous result (follow-up required)

Expected entropy reduction: 16% (0.31 bits). Maximum possible: 28%.

## Approval Request

**Approve execution of I10: 80-run density sweep at friction = 0.40.**

Modifications will be made to `coherence-benchmark/t901_analysis.py`. Analysis pipeline is unchanged. Results will be reported as RD-020.
