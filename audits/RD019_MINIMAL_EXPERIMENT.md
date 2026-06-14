# RD-019 Minimal Experiment: Density Sweep at Fixed Friction

**Date**: 2026-06-06
**Recommendation**: I10 — Initial packing density sweep at friction = 0.40.

## Why This Experiment

After 69 variables tested across RD-017 and RD-018, the leading hypothesis for Residual(C)'s identity is **packing sparseness / contact-network fragmentation**. The minimal experiment to test this is: systematically vary initial packing density while holding friction fixed, and measure whether Residual(C) and recovery move together.

Friction = 0.40 is chosen because RD-017-D4 showed Residual(C) has strong within-level signal at this friction (r=+0.67 for ΔC, r=−0.73 for restoration) — we know the effect exists here.

## Precise Protocol

### Parameter Changes

In `coherence-benchmark/t901_analysis.py`, modify `_granular_run`:
- Add `box_width` parameter (default 40.0)
- Replace hardcoded `box_width = 40.0` with parameter

### Conditions

| Condition | box_width | n_grains | friction | Effective density (grains/area) |
|-----------|-----------|----------|----------|-------------------------------|
| 1 | 25 | 50 | 0.40 | 0.050 |
| 2 | 30 | 50 | 0.40 | 0.042 |
| 3 | 35 | 50 | 0.40 | 0.036 |
| 4 | 40 (control) | 50 | 0.40 | 0.031 |
| 5 | 45 | 50 | 0.40 | 0.028 |
| 6 | 50 | 50 | 0.40 | 0.025 |
| 7 | 55 | 50 | 0.40 | 0.023 |
| 8 | 60 | 50 | 0.40 | 0.021 |

Density range: 0.021–0.050 grains/unit² (2.4× variation). The existing ensemble at μ=0.40, box=40 provides Condition 4.

### Sample Size

**80 runs**: 8 levels × 10 replicates = 80. This matches the RD-017/018 standard (10 reps per condition). Seeds 0–9 for each condition (total seed range 0–79, carefully avoiding overlap with existing runs which used seeds 200–209 for μ=0.40).

**Runtime**: 80 × 3s ≈ 240s (4 minutes).

### What to Measure

For each run, compute the standard recovery pipeline:
- `_granular_run(n_grains=50, n_steps=1000, removal_step=500, removal_fraction=0.1, friction=0.40, box_width=W, seed=S)`
- `_bin_data(y, x, n_bins=10)` → binned trajectories
- `_sliding_C(binned, window=75, step=25)` → C(t)
- `measure_recovery(times, cvals, pert_start=500)` → pre_C, dip, restoration, tau_rec
- `compute_mobility_proxies(x, y, vx, vy, radii, removed, T_pre=500)` → MSD, rms_vel, turnover, packing_var

### Code Modification

```python
# In _granular_run:
# Change:
box_width = 40.0
# To:
# box_width is now a parameter with default 40.0

# Function signature:
def _granular_run(n_grains=50, n_steps=1000, removal_step=500,
                  removal_fraction=0.1, friction=0.3, seed=42,
                  box_width=40.0):  # ADD THIS
```

That is the only code change needed. All downstream analysis code (`_bin_data`, `_sliding_C`, etc.) adapts automatically because they only depend on y-positions, bin ordering by x, and n_bins — not on box dimensions.

## Analysis Plan

### A. Confirm density manipulation worked

For each condition, compute:
- Mean coordination number (should increase with density)
- Mean nearest-neighbor distance (should decrease with density)
- Contact count (should increase with density)

### B. Primary test: Does C vary with density?

Regression: `C ~ density` where density = n_grains / (box_width × 30).
- Prediction: C increases with density (negative slope: wider box → lower density → higher C)
- Effect size expected: ΔC ≈ 0.03–0.05 across the density range (based on within-friction variation in existing data)
- If R²(C~density) > 0.30 and slope is significant at p < 0.01 → manipulation successful

### C. Secondary test: Does recovery vary with density?

Regression: `dip ~ density` and `restoration ~ density`.
- H1 prediction: Lower density → smaller dip, higher restoration (better recovery)
- H0 prediction: No relationship (friction dominates recovery; density irrelevant)
- If both are significant → density affects recovery

### D. Key causal test: Does C mediate density→recovery?

Three-regression mediation analysis (Baron & Kenny):
1. density → C: significant (test B above)
2. C → recovery: significant (control for density)
3. density → recovery: must be significant WITHOUT controlling for C
4. density → recovery: must be REDUCED when controlling for C

If steps 1–4 hold → C is a partial mediator of density→recovery.
If step 4 reduces to zero → C is a full mediator (strong evidence for H1).
If step 3 is not significant → density does not affect recovery (falsifies both H1 and H0 for this manipulation).

### E. Thermometer test

After controlling for C, does density still predict recovery?
- If no (C fully mediates) → H1 strongly supported. C IS the latent state through which density affects recovery.
- If yes (density still predicts after C) → H0 supported. C is an incomplete measure; density has causal effects beyond what C captures.

### F. Within-density-level test

Within each density level (n=10), compute r(Residual(C), recovery).
- If within-density r ≈ within-friction r from RD-017 (≈+0.50 for ΔC) → Residual(C) operates at a finer scale than density.
- If within-density r ≈ 0 → Residual(C) was just capturing density variation all along.

## Success Criteria

| Criterion | Threshold | Interpretation |
|-----------|-----------|---------------|
| **Manipulation check** | R²(C~density) > 0.30, p < 0.01 | Density manipulation successfully changes C |
| **Primary mediation** | C mediates ≥70% of density→ΔC effect | H1 (causal state) supported |
| **Within-density signal** | Mean within-density r(Res(C),ΔC) > +0.30 | Residual(C) is not just density proxy |

If all three met → **Strong evidence that Residual(C) IS a packing-density-related causal state.**

## Failure Criteria

| Criterion | Interpretation |
|-----------|---------------|
| C does NOT vary with density (R² < 0.05) | Sparseness hypothesis falsified. Density manipulation was too weak or C is unrelated to packing. |
| C varies but recovery does NOT | Residual(C) may be structural but NOT causal. Thermometer view supported. |
| C varies, recovery varies, but C does NOT mediate | Density has causal effects through channels other than C. H0 supported — C is not the causal pathway. |
| Within-density r(Res(C), recovery) ≈ 0 | Residual(C)'s signal was entirely between-density, not within. Rules out fine-grained structural state. |

## Expected Information Gain

| Outcome | Probability (estimated) | Update |
|---------|------------------------|--------|
| Strong mediation (C mediates ≥70%) | 40% | Residual(C) ≈ packing density. Causal role for C supported. Next: generalize to other frictions. |
| Partial mediation (30–70%) | 35% | Density matters; C captures part of it but not all. Residual(C) = density + something else. Next: identify the "something else." |
| No mediation (C varies but doesn't mediate) | 15% | Thermometer view gains support. C predicts but doesn't cause. Next: search for true causal variable. |
| Null (no C variation) | 10% | Sparseness hypothesis falsified. Residual(C) is unrelated to packing density. Next: consider alternative theories. |

Expected reduction in hypothesis entropy: ~1.2 bits (substantial).

## Comparison to Next-Best Candidate

The next-best experiment (I4: Full friction×density grid) would add:
- More runtime (450s vs 240s)
- Ability to test friction×density interaction
- Generalizability across friction levels
- But: same causal logic as I10, just replicated

**The minimal experiment doesn't sacrifice causal inference.** I10 provides the same mediation test as I4, just at a single friction level. If the mediation holds at μ=0.40, we generalize to other frictions in a follow-up. If it fails, we've learned more at lower cost.

## Bottom Line

**80 runs, 1 line of code changed, 4 minutes of runtime.** If the sparseness hypothesis is correct, this experiment will show C mediating density→recovery at a known-signal friction level. If not, we falsify the leading hypothesis and force a theory revision.

No cheaper experiment can provide a larger causal update.
