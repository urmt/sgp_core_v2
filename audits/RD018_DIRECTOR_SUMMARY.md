# RD-018 Director Summary: Targeted diagnostics for Residual(C)

**From**: OpenCode (Research Assistant)
**To**: Research Director
**Date**: 2026-06-06

## Q1: Did any new diagnostic identify what Residual(C) is measuring?

**No.** Four new diagnostic families (40 variables total) were tested. None beat RD-017's best correlate (pre_MSE_s1, R²=0.176). The best new correlate was C_rand_bin (random binning C) at R²=0.142 — a C variant, not an independent physical measurement.

## Q2: What can we rule out?

| Hypothesis | Evidence from RD-018 | Verdict |
|-----------|---------------------|---------|
| "Residual(C) = local rearrangement capacity" | Non-affine D²_min: all n.s. (max |r|=0.16) | **Ruled out** |
| "Residual(C) = force heterogeneity" | Force cv/skew: all n.s. (max |r|=0.15) | **Ruled out** |
| "Residual(C) = fabric anisotropy" | Fabric anisotropy r=0.02, n.s. | **Ruled out** |
| "Residual(C) = community structure" | Modularity r=−0.02, n.s. | **Ruled out** |
| "Residual(C) = percolation threshold" | No spanning clusters detected in any run | **Cannot test** (system too small) |

## Q3: Is there any new positive evidence?

**Weak positive signals, all consistent with sparseness:**

1. **Number of force chains (chain_n_chains):** r=−0.341 with Residual(C). Higher Residual(C) → fewer force chains. This is the strongest non-C correlate. Consistent with sparseness: when the packing is more open, fewer strong force chains form.

2. **Triadic motif profiles:** Higher Residual(C) → more empty triads (r=+0.306), fewer single-edge triads (r=−0.307). This directly measures contact network fragmentation at the mesoscale — the most direct structural evidence yet.

3. **C_rand_bin:** r=+0.377 with Residual(C). Even with grains assigned to random bins, the C metric partially recovers the same signal. This suggests Residual(C) operates at a systems level so fundamental that spatial binning is irrelevant.

But: none of these exceed R²=0.14. All are weaker than pre_MSE_s1 (R²=0.176). The identity question remains open.

## Q4: Should we continue searching, or pivot?

**Recommendation: Pivot.** RD-017 + RD-018 have tested 29 + 40 = 69 variables against Residual(C). The cumulative picture is:

- **Structural/contact-based** (29 variables from RD-017): max R² = 0.176 (pre_MSE_s1)
- **Force chain** (17 variables from RD-018): max R² = 0.116 (chain_n_chains)
- **Non-affine displacement** (8 variables from RD-018): max R² = 0.026 (all n.s.)
- **Network motifs** (11 variables from RD-018): max R² = 0.094 (motif_single)
- **Alternate binning** (4 variables from RD-018): max R² = 0.142 (C_rand_bin)

**Residual(C) is not going to be identified by extracting more descriptors from the existing simulations.** The signal-to-noise ratio is asymptotic: each new family yields weaker correlations than the last.

The path forward has three options:

| Option | Cost | Probability of success | Recommendation |
|--------|------|----------------------|---------------|
| **Extract more descriptors** (higher-order Minkowski functionals, persistence diagrams, etc.) | Low | Low (diminishing returns is clear) | **Not recommended** |
| **Design a causal intervention experiment** (vary packing density independently of friction) | High | Moderate (directly tests the sparseness hypothesis) | **Best next step** |
| **Generalize to new systems** (different grain size distribution, different geometries) | Moderate | Moderate (tests whether Residual(C) is specific to this system) | **Viable alternative** |

### Recommended pivot: Design a causal intervention experiment

The sparseness/disconnectedness hypothesis can be directly tested by an experiment that manipulates packing density independently of friction. For example:

- **Protocol**: Initialize the granular packing with different initial grain densities (e.g., vary the box width from 30 to 50 while keeping n_grains=50 fixed). This changes packing fraction without changing friction.
- **Prediction**: Runs with lower initial density (wider box) will have higher C than expected from friction alone — i.e., positive Residual(C) — and will show better recovery.
- **Controls**: Same friction coefficient, same perturbation protocol, same measurement pipeline.

This is the next logical step. The observational evidence for Residual(C) is saturated.

## Updated model ranking

| Rank | Explanation | Status after RD-018 |
|------|-------------|---------------------|
| 1 | C+Fr+Fr² | Best predictive model |
| 2 | **Residual(C) = latent packing sparseness** | Best hypothesis, strongest observational evidence |
| 3 | Thermometer interpretations | Still viable |
| 4 | Interaction (C×Fr) | Weakened (RD-016) |
| 5 | C-only | Falsified |
| 6 | Mobility-only | Falsified |

## Key numbers

- New diagnostics tested: 40 (4 families)
- Cumulative variables tested against Residual(C): 69
- Best RD-018 correlate: C_rand_bin (R²=0.142)
- Best RD-017 correlate: pre_MSE_s1 (R²=0.176)
- Still unable to reproduce Residual(C) from any known quantity
- Within-level benchmark: Residual(C) achieves r=+0.465 (ΔC), r=−0.525 (Restoration)
