# RD-019 Intervention Design Audit

**Date**: 2026-06-06
**Question**: Which interventions can separate H1 (Residual(C) as causal packing state) from H0 (Residual(C) as statistical thermometer)?

## Design Principle

Every intervention must satisfy three criteria:
1. **Manipulable** — achievable by changing ≤1 parameter or function in the existing DEM code (`_granular_run` in `coherence-benchmark/t901_analysis.py`, 50 grains, 1000 steps, 10% removal at t=500)
2. **Testable** — produces distinguishable predictions under H1 vs H0
3. **Interpretable** — confounds are identifiable and bounded

## Intervention Catalog

### I1: Initial Packing Density Sweep

Manipulate initial grain density by varying box width.

| Property | Current | Range |
|----------|---------|-------|
| box_width | 40 | 25–60 (6 levels: 25, 30, 35, 40, 45, 50, 55, 60) |
| n_grains | 50 | Fixed |
| Density (grain/area) | 0.042 | 0.014–0.080 |

**Implementation**: Change `box_width = 40.0` to a parameter in `_granular_run`.

| | H1 (Causal State) | H0 (Thermometer) |
|---|---|---|
| **Expected result** | Lower density → higher C (more room for correlated motion) → positive Residual(C) → better recovery (smaller dip, higher restoration) | C may increase but recovery does not improve (or does so for reasons unrelated to C). Density is the true cause; C is along for the ride. |
| **Key test** | Residual(C) mediates density→recovery. Controlling for Residual(C) eliminates density effect. | Density→recovery survives controlling for Residual(C). Residual(C) is a confounded correlate, not a mediator. |
| **Falsification** | C does NOT vary with density; or C varies but recovery doesn't. | Controlling for Residual(C) eliminates density effect (would mean C IS the mediator). |

**Confounds**: Wall effects shrink with wider boxes. Wider boxes have more space for grains, which could change collision rates independently of density. Grain-grain contact statistics shift.

---

### I2: Initial Spatial Clustering Manipulation

Replace uniform random initial positions with controlled clustering.

| Property | Current | Range |
|----------|---------|-------|
| Initialization | Uniform random in [2,38]×[5,30] | Poisson cluster process with cluster radius R_c |
| R_c | N/A | 2, 5, 10, 20 (tight→diffuse) + uniform control = 5 levels |

**Implementation**: Replace `x = rng.uniform(2, box_width - 2, n_grains)` logic with cluster sampling. ~15 lines.

| | H1 (Causal State) | H0 (Thermometer) |
|---|---|---|
| **Expected result** | Tighter clustering → lower coordination number → lower C → negative Residual(C) → worse recovery | Clustering changes C but recovery determined by other factors (friction dominates) |
| **Key test** | Does C mediate cluster→recovery? | Does cluster survive C control? |
| **Falsification** | No C variation across clustering levels | C is the sole predictor regardless of clustering |

**Confounds**: Clusters near walls behave differently. Cluster initialization may create transient force imbalances. Clustering correlates with local density in a non-uniform way.

---

### I3: Grain-Size Distribution Manipulation

Change polydispersity of grain radii.

| Property | Current | Range |
|----------|---------|-------|
| radii | Uniform(0.8, 1.5) | 5 distributions: monodisperse(1.15), narrow(0.95–1.35), current(0.8–1.5), wide(0.5–2.0), bimodal(0.8+1.5) |

**Implementation**: Change `rng.uniform(0.8, 1.5, n_grains)` to parameterized distribution. ~5 lines.

| | H1 (Causal State) | H0 (Thermometer) |
|---|---|---|
| **Expected result** | Monodisperse → more ordered packing → higher C, better recovery. Bimodal → less ordered → lower C, worse recovery. | Size distribution directly changes force transmission. C changes but is epiphenomenal. Recovery changes because force chains change, not because C changed. |
| **Key test** | Does C mediate size_distribution→recovery? If H1, controlling C eliminates distribution effect. | Does size distribution survive C control? |
| **Falsification** | No C variation across size distributions | C is the sole driver |

**Confounds**: Polydispersity directly modifies contact mechanics (Hertzian contact area, overlap distributions). This is NOT a clean separation — it changes both the putative cause and the measurement. High confounding risk.

---

### I4: Friction × Density Grid

Two-factor design: vary friction AND packing density simultaneously.

| Factor | Levels |
|--------|--------|
| Friction | 0.05, 0.20, 0.40, 0.60, 0.80 |
| Box width (proxy for density) | 30, 40, 50 |

5 × 3 = 15 conditions × 10 reps = 150 runs.

**Implementation**: Same code as I1, just run across friction levels.

| | H1 (Causal State) | H0 (Thermometer) |
|---|---|---|
| **Expected result** | Friction and density have independent additive effects on C. Residual(C) = f(density) within each friction level. Recovery follows C. | Friction dominates. Density adds noise but no systematic C→recovery mediation. |
| **Key test** | Does the C+Residual(C) model outperform friction+density model for recovery? If H1, yes — C captures the mechanistic state. If H0, no — density adds direct explanatory power beyond C. | |
| **Falsification** | Density affects C but not recovery; or density×friction interaction dominates C completely. | C and recovery are fully explained by friction and density as independent additive predictors — no "C magic." |

**Confounds**: None beyond I1. This is the most comprehensive test.

---

### I5: Removal Fraction Sweep

Vary perturbation severity.

| Property | Current | Range |
|----------|---------|-------|
| removal_fraction | 0.10 | 0.05, 0.10, 0.15, 0.20, 0.30 |

**Implementation**: Change one parameter. ~1 line.

| | H1 (Causal State) | H0 (Thermometer) |
|---|---|---|
| **Expected result** | Larger removal → larger dip → longer recovery. Relationship between C and recovery parameters is stable across removal fractions. | Same, but C is just reporting system damage. No independent causal role. |
| **Key test** | Does Residual(C) predict recovery fraction at EVERY removal fraction? If H1, yes — because Residual(C) measures latent state independent of perturbation size. | |
| **Falsification** | C→recovery relationship changes slope with removal fraction | Relationship is stable but C adds nothing beyond removal fraction |

**Confounds**: Larger removal fraction changes system size post-perturbation, which directly affects C computation (fewer grains → fewer bins → different C range). This is a measurement artifact, not a mechanistic test. **Major confound.**

---

### I6: Selective Removal

Instead of random removal, target specific grains.

| Strategy | Description |
|----------|-------------|
| Random (control) | Current: rng.choice |
| Largest | Remove the n_remove largest grains by radius |
| Smallest | Remove the n_remove smallest grains |
| Most connected | Remove grains with highest coordination number at t=499 |
| Least connected | Remove grains with lowest coordination number |
| Central | Remove grains closest to centroid |
| Peripheral | Remove grains farthest from centroid |

7 strategies × 10 reps = 70 runs. Fix friction at 0.40.

**Implementation**: Replace `rng.choice` with deterministic selection. ~15 lines.

| | H1 (Causal State) | H0 (Thermometer) |
|---|---|---|
| **Expected result** | Removal of most-connected grains causes larger dip/worse recovery than removal of least-connected grains. The structural importance of removed grains directly affects outcome. C captures this because it measures the interaction structure C of the remaining system. | Recovery depends only on how many grains were removed and the friction. Which grains doesn't matter. |
| **Key test** | Does C (post-removal measurement) still predict recovery after controlling for which type was removed? | |
| **Falsification** | No difference between removal strategies | C fully mediates strategy→recovery |

**Confounds**: Largest grains have more mass, different dynamics. Hard to separate "structural importance" from "size effect."

---

### I7: Contact Network Softening (Parameter Perturbation)

Temporarily modify contact stiffness for a subset of grains instead of removing them.

| Property | Current | Range |
|----------|---------|-------|
| stiffness | 500 | Reduce to 100 or 50 for selected grains |
| damping | 2.0 | Keep fixed |

3 levels: remove 10% (control), soften 30% of contacts, soften 60% of contacts. 3 × 10 = 30 runs.

**Implementation**: Instead of setting `removed[remove_idx] = True`, reduce `stiffness` for contacts involving those grains. ~20 lines — moderate complexity.

| | H1 (Causal State) | H0 (Thermometer) |
|---|---|---|
| **Expected result** | Softening contacts is equivalent to removing interaction structure. C drops, recovery is impaired. The C→recovery relationship mirrors the removal experiment. | Softening changes dynamics but C may not capture it because grains are still present (just interacting weakly). H0 predicts C is less sensitive to softening than removal. |
| **Key test** | Does softening produce the same Residual(C)→recovery relationship as removal? If yes → C is genuinely about interaction structure, not just absence of grains. | |
| **Falsification** | No C change from softening | C changes exactly as with removal |

**Confounds**: The physics of soft contacts vs. absent grains is different. Softening changes time scales (softer → slower dynamics). Recovery times may not be comparable. **Moderate confounding risk.**

---

### I8: Gravity Sweep (Confining Pressure)

Change gravitational acceleration to vary confining pressure and thus packing density.

| Property | Current | Range |
|----------|---------|-------|
| gy | −1.0 | −0.25, −0.5, −1.0, −2.0, −4.0 |

5 levels × 10 reps = 50 runs.

**Implementation**: Change one parameter. ~1 line.

| | H1 (Causal State) | H0 (Thermometer) |
|---|---|---|
| **Expected result** | Stronger gravity → more compact packing → higher coordination → lower C → negative Residual(C) → worse recovery. Weaker gravity → looser packing → higher C → better recovery. | Gravity directly changes forces and dynamics. C is a passive reporter. Recovery changes because forces changed, not because C changed. |
| **Key test** | After controlling for C, does gravity still predict recovery? | |
| **Falsification** | No C variation with gravity | Gravity→recovery fully mediated by C |

**Confounds**: Gravity changes settling dynamics, velocity scales, and the effective "weight" of removed grains (perturbation magnitude). The wall-bottom boundary condition interacts with gravity. **Moderate confounding risk** — too many things change at once.

---

### I9: Packing Preparation History

Change the equilibration period before perturbation.

| Property | Current | Range |
|----------|---------|-------|
| Equilibration (pre-removal steps) | 500 | 200, 500, 1000, 2000 |

4 levels × 10 reps = 40 runs.

**Implementation**: Change `removal_step` parameter. ~1 line.

| | H1 (Causal State) | H0 (Thermometer) |
|---|---|---|
| **Expected result** | Longer equilibration → more settled packing (if friction allows) → different C. The effect depends on friction: at low friction, grains settle quickly; at high friction, they don't fully settle in 500 steps. Longer equilibration → higher C at high friction. | No effect — the system has already reached steady state by t=500 for all friction levels (as the existing data shows stable pre-C). |
| **Key test** | Does longer equilibration change C and recovery at high friction specifically? | |
| **Falsification** | No variation in C across equilibration times | C is the sole driver of recovery variation |

**Confounds**: The granular system may already be equilibrated by t=500 at all friction levels (we can check this from existing data — is pre-C stable?). If so, this is a null manipulation. **Low information gain.**

---

### I10: Friction Fixed, Density Sweep (The Minimal Candidate)

**This is I1 applied at a single friction level.** Keep friction fixed at 0.40. Vary box_width = 25, 30, 35, 40, 45, 50, 55, 60 (8 levels × 10 reps = 80 runs).

This is a subset of I4 but provides the cleanest test of the sparseness hypothesis because:
- Friction is completely controlled (cannot be a confound)
- Density is the only variable manipulated
- The code change is minimal (box_width parameter)
- The prediction is directional and quantitative

| | H1 (Causal State) | H0 (Thermometer) |
|---|---|---|
| **Expected result** | ρ ↓ → C ↑ → Residual(C) > 0 → recovery improves. The within-density-level Residual(C) should also predict recovery (just like within-friction-level). | ρ ↓ → C may or may not change. Residual(C) is just noise from random seed variation. Recovery may improve because of density but NOT because of C. |
| **Key test** | At fixed friction, does Residual(C) mediate ρ → recovery? ∆R² test: C model vs ρ + C model. | |
| **Falsification** | ρ → C but C does NOT predict recovery. Or C → recovery but ρ does not change C. | ρ → recovery but C adds nothing. |

**Confounds**: Wall effects. Box_width also changes the x-boundary distance, which affects grain-wall collisions. At narrow widths (25), boundary effects dominate.

---

## Summary Table

| # | Intervention | Manipulates | Fixes | Code Changes | Runtime (runs × 3s) |
|---|---|---|---|---|---|
| I1 | Density sweep | box_width | friction, n_grains | 1 line | 180s (60 runs) |
| I2 | Clustering | init positions | friction, density | ~15 lines | 150s (50 runs) |
| I3 | Size distribution | radii dist. | friction, density | ~5 lines | 150s (50 runs) |
| I4 | Friction×Density | both | n_grains | 1 line | 450s (150 runs) |
| I5 | Removal fraction | removal % | friction | 1 line | 150s (50 runs) |
| I6 | Selective removal | which grains | friction, removal% | ~15 lines | 210s (70 runs) |
| I7 | Contact softening | stiffness | friction, removal% | ~20 lines | 90s (30 runs) |
| I8 | Gravity sweep | gy | friction, n_grains | 1 line | 150s (50 runs) |
| I9 | Equilibration time | removal_step | friction | 1 line | 120s (40 runs) |
| I10 | Density sweep (fixed μ) | box_width | friction=0.40 | 1 line | 240s (80 runs) |

## Next

See `RD019_CAUSAL_PRIORITY_RANKING.md` for quantitative scoring of each intervention.
