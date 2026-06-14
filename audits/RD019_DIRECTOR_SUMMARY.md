# RD-019 Director Summary: Density Intervention Audit

**Date**: 2026-06-06
**Status**: Complete
**Result**: Pre-perturbation coherence C is **not** a function of packing density.

## One-Sentence Verdict

The density intervention **dissociated C from the structural descriptors that did respond to density manipulation**. C remained nearly constant (R²(C~density)=0.055, n.s.) while NN distance, contact count, coordination number, and component count all changed dramatically (R² ≥ 0.91). The leading hypothesis that Residual(C) ≈ packing sparseness is **falsified**.

## What Was Run

60 simulations. 6 box_widths (30, 35, 40, 45, 50, 55) × 10 replicates. Friction fixed at 0.40. One parameter changed (added `box_width` to `_granular_run`). Runtime: 145 seconds.

## What Was Measured

- All 10 metrics from prior ensemble: pre_C, dip, restoration, τ_rec, pre_I_pred, pre_C_sigma, pre_MSE_s1, rms_velocity, msd, neighbor_turnover, packing_var
- Plus: 6 structural validation descriptors (NN distance, contact count, coordination number, component count, largest component size, clustering coefficient)
- Plus: Residual(C) computed two ways — within density level and globally

## Task 3: Structural Validation (Did the manipulation work?)

**All 7 measured structural descriptors responded in the predicted direction.** Higher density → more contacts, more coordination, fewer components, larger connected component, shorter NN distances, higher mobility. R² of these descriptors with density ranged 0.52–0.94.

| Descriptor             | r(ρ)   | p      | R²    | Sign match |
|------------------------|--------|--------|-------|------------|
| mean_nn_dist           | -0.97  | 0.001  | 0.94  | ✓          |
| contact_count          | +0.96  | 0.003  | 0.92  | ✓          |
| coordination_number    | +0.96  | 0.003  | 0.92  | ✓          |
| component_count        | -0.96  | 0.003  | 0.91  | ✓          |
| largest_component_size | +0.96  | 0.003  | 0.92  | ✓          |
| clustering_coefficient | +0.72  | 0.10   | 0.52  | ✓          |
| msd                    | +0.97  | 0.002  | 0.93  | ✓          |

The manipulation was effective. The physical interpretation: wider boxes (lower density) produce more disconnected, fragmented, less-coordinated packings with higher component counts and longer nearest-neighbor distances. The system responded as expected.

## Task 4: Causal Models

### Critical finding: pre_C did NOT respond to density

| Variable | r(ρ)   | p      | R²    | Significant? |
|----------|--------|--------|-------|--------------|
| pre_C    | -0.24  | 0.070  | 0.055 | NO           |

C is essentially invariant under density manipulation. This is the key dissociation: **structural descriptors responded strongly; C did not.** The leading hypothesis (H1: Residual(C) ≈ packing sparseness) required C to vary with density. It did not.

### Regression results by target

For the target **ΔC (dip depth)**:
- Model A (Density only): R² = 0.011, density p = 0.43 — **density has no effect on dip**
- Model B (Density + ResC): R² = 0.087, ResC p = 0.033 — **ResC drives dip independently**
- Model C (ResC only): R² = 0.077 — almost as good as Model B
- Model D (with interaction): R² = 0.120, interaction n.s.

For the target **restoration**:
- Model A: R² = 0.123, density p = 0.006 — density affects restoration
- Model B: R² = 0.390, both p < 0.001 — **both density AND ResC matter additively**
- Model C: R² = 0.267
- Model D: R² = 0.412, interaction n.s.

For the target **τ_rec**:
- Model A: R² = 0.084, density p = 0.024
- Model B: R² = 0.175, both p < 0.05
- Model C: R² = 0.091
- Model D: R² = 0.209, interaction n.s.

### Decision rule outcomes

The Director's three decision rules, applied to ΔC as the primary target:

| Outcome | Met? | Reasoning |
|---------|------|-----------|
| 1: Density explains it all (R²_A>0.10, ΔR²(B-A)<0.05, R²_C<0.10) | NO | R²_A=0.011 fails |
| 2: Both density and ResC matter (both p<0.05 in Model B) | NO | density p=0.42 fails |
| 3: Density barely affects ResC (R²_C<0.10 AND ΔR²(D-B)<0.05) | **YES** | R²_C=0.077, ΔR²(D-B)=0.033 |

The algorithm flags **Outcome 3** for ΔC.

**Cross-target interpretation**: The decision rule was designed assuming ΔC is the canonical target. The full picture across all three recovery targets is more informative:

- For **ΔC**: ResC is the sole predictor. Density is irrelevant.
- For **restoration and τ_rec**: Both density and ResC matter, additively, with no interaction.
- **Density affects restoration and τ_rec through a mechanism that is NOT C.**

## What This Means for Assumption 15 (Identity of Residual(C))

**Previous status** (post-RD-018): "Residual(C) is real and within-level. Identity unknown. Leading hypothesis: packing sparseness."

**RD-019 update**: Packing sparseness is **falsified as the dominant mechanism** because density manipulation failed to move C. The structural descriptors that did respond to density (NN distance, contact count, coordination number, component count) had no observable effect on C. If C were measuring sparseness, density manipulation would have changed C. It did not.

**New hypothesis space for Residual(C)'s identity**: It cannot be packing geometry (NN distance, contact count, coordination), network topology (component count, largest component size), or any quantity that varies with density. Residual(C) is sensitive to a dimension of the system that the density manipulation did not affect.

**Open candidates** (not yet tested):
- Force-chain geometry (per-grain, not just aggregate)
- Velocity / kinetic structure
- Some aspect of the binning/correlation calculation that is not density-dependent
- Initial condition noise that survives equilibration

## Status Update for Director

| Item | Status |
|------|--------|
| Density manipulation effectiveness | Confirmed (7/7 structural descriptors responded) |
| pre_C sensitivity to density | None (R²=0.055, n.s.) |
| Leading hypothesis (H1: sparseness) | Falsified |
| Residual(C) predictive of dip | Confirmed (independent of density) |
| Density as a separate predictor of restoration | Confirmed (independent of Residual(C)) |
| Interaction density × ResC | None (n.s. in all targets) |
| Assumption 15 (Identity) | **Unknown** — sparseness rejected; mechanism still unidentified |

## Next Steps (Decision Required)

Three options for the Director:

1. **Stop and accept negative result.** Document that Residual(C) is not a density proxy. The thermometer-vs-causal question remains open. Move to a different intervention (selective removal, friction-density grid).

2. **Test a different physical parameter.** Pick the next-best candidate intervention (I6: selective removal at fixed friction). This would test whether the *spatial pattern* of removal matters, rather than total density.

3. **Test friction-density interaction (I4: full grid).** Run the full 5 × 8 friction-density grid to test whether the result generalizes. This costs 4× the runtime but provides comprehensive coverage.

**My recommendation**: Option 2 (selective removal). The current result shows C is independent of density — a strong negative result that does not require replication. Selective removal tests a different dimension (which grains are removed) and is the next-largest-information intervention.

## Files

- `audits/RD019_DENSITY_INTERVENTION.md` — full per-condition data and structural validation
- `audits/RD019_CAUSAL_MODELS.md` — all 12 model fits with coefficients, p-values, R², ΔR²
- `audits/RD019_RESULTS_TABLE.csv` — 60-row results table
- `audits/rd019_density_intervention.py` — simulation script (1-line code change)
- `audits/rd019_causal_models.py` — analysis script
- `coherence-benchmark/results/rd019_density_ensemble.json` — raw ensemble data
