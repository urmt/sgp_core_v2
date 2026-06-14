# RD-019 Causal Priority Ranking

**Date**: 2026-06-06
**Question**: Which intervention maximizes causal information per unit cost?

## Scoring Criteria

Each intervention scored 0–10 on five dimensions:

| Criterion | Weight | Definition |
|-----------|--------|------------|
| **Information Gain** | 4× | How much the experiment narrows the hypothesis space. Distinguishes H1 from H0? Resolves identity vs thermometer? |
| **Difficulty** | 2× | Inverse of implementation complexity. 0 = rewrite engine, 10 = change one parameter. |
| **Runtime** | 1× | Total simulation time. 10 = <60s, 0 = >1000s. (Each run ≈ 3s) |
| **Confounding Risk** | 3× | Inverse of how many alternative explanations could produce the same result. 10 = clean, 0 = uninterpretable. |
| **Isolation of Res(C)** | 3× | Can we directly observe how Residual(C) moves in response? 10 = direct measurement, 0 = inferred. |

**Total Score** = 4×IG + 2×(10−Diff) + 1×(10−Runtime) + 3×(10−Confound) + 3×Iso

Wait — let me standardize so higher is always better:

**Total Score** = 4×IG + 2×(10−Difficulty_raw) + 1×(10−Runtime_raw/100) + 3×(10−Confound_raw) + 3×Iso

Where raw scores are 0–10 (0 = worst, 10 = best).

## Scoring

### I1: Packing Density Sweep (all friction levels)

| Criterion | Raw Score | Rationale |
|-----------|-----------|-----------|
| Information Gain | 8 | Directly tests leading hypothesis. Distinguishes additive density effect from friction. Does NOT distinguish causal from thermometer (still correlational). |
| Difficulty | 10 | Change one parameter: `box_width`. |
| Runtime | 7 | 60 runs × 3s = 180s. Moderate. |
| Confounding Risk | 7 | Wall effects at extreme densities. Density effects could be nonlinear. Otherwise clean. |
| Isolation of Res(C) | 7 | Can compute C and Residual(C) exactly as before. Direct comparison possible. |

**Total** = 4(8) + 2(10) + 1(7) + 3(7) + 3(7) = 32 + 20 + 7 + 21 + 21 = **101**

---

### I2: Initial Clustering

| Criterion | Raw Score | Rationale |
|-----------|-----------|-----------|
| Information Gain | 5 | Tests spatial organization hypothesis. But clustering is transient — grains may re-arrange during equilibration and "forget" initial clustering. |
| Difficulty | 3 | ~15 lines of new initialization code. Cluster process requires parameter tuning. |
| Runtime | 7 | 50 runs × 3s = 150s. |
| Confounding Risk | 3 | Clusters near walls behave differently. Clustering may be washed out by equilibration. Hard to separate clustering from local density variations. |
| Isolation of Res(C) | 4 | Initial clustering may be erased by t=500. Pre-C may show no variation if equilibration wipes out initial conditions. |

**Total** = 4(5) + 2(3) + 1(7) + 3(3) + 3(4) = 20 + 6 + 7 + 9 + 12 = **54**

---

### I3: Grain-Size Distribution

| Criterion | Raw Score | Rationale |
|-----------|-----------|-----------|
| Information Gain | 6 | Tests whether polydispersity drives the sparseness signal. But size distribution affects force transmission directly — hard to separate from C. |
| Difficulty | 8 | ~5 lines. Replace uniform distribution. |
| Runtime | 7 | 50 runs × 3s = 150s. |
| Confounding Risk | 2 | Size distribution changes contact mechanics, overlap distributions, force chains, packing geometry — ALL at once. Cannot isolate C. |
| Isolation of Res(C) | 5 | Can compute C straightforwardly but interpretation is confounded. |

**Total** = 4(6) + 2(8) + 1(7) + 3(2) + 3(5) = 24 + 16 + 7 + 6 + 15 = **68**

---

### I4: Friction × Density Grid

| Criterion | Raw Score | Rationale |
|-----------|-----------|-----------|
| Information Gain | 10 | The most comprehensive test. Separates friction from density. Tests additivity vs interaction. Can distinguish whether density has effects beyond friction. |
| Difficulty | 10 | Same as I1 — one parameter. Just more combinations. |
| Runtime | 4 | 150 runs × 3s = 450s. Long but manageable. |
| Confounding Risk | 7 | Same wall effects as I1. The two-factor design actually helps disentangle confounds. |
| Isolation of Res(C) | 9 | Full factorial design allows direct measurement of how Residual(C) changes with both factors. Can test whether Residual(C) is f(density) independent of friction. |

**Total** = 4(10) + 2(10) + 1(4) + 3(7) + 3(9) = 40 + 20 + 4 + 21 + 27 = **112**

---

### I5: Removal Fraction Sweep

| Criterion | Raw Score | Rationale |
|-----------|-----------|-----------|
| Information Gain | 4 | Tests perturbation dependence but NOT Residual(C) identity. Doesn't distinguish H1 from H0 because both predict similar results. |
| Difficulty | 10 | One parameter change. |
| Runtime | 7 | 50 runs × 3s = 150s. |
| Confounding Risk | 5 | Major confound: fewer grains post-removal = fewer bins = different C range. Measurement artifact. |
| Isolation of Res(C) | 3 | C measurement changes systematically with system size. Hard to compare across conditions. |

**Total** = 4(4) + 2(10) + 1(7) + 3(5) + 3(3) = 16 + 20 + 7 + 15 + 9 = **67**

---

### I6: Selective Removal

| Criterion | Raw Score | Rationale |
|-----------|-----------|-----------|
| Information Gain | 8 | Directly tests whether "structural importance" of removed grains matters. If yes → C measures real structure. If no → C is aggregate statistics. Distinguishes H1 from "removal fraction only" H0. |
| Difficulty | 5 | ~15 lines for selection logic. Need to compute coordination at t=499. |
| Runtime | 6 | 70 runs × 3s = 210s. |
| Confounding Risk | 5 | Largest grains ≠ most connected grains. Selection strategies are correlated with grain size, mass, position. Hard to isolate "structural importance" from "size effect." |
| Isolation of Res(C) | 8 | Can compare Residual(C) across removal strategies. The key test is whether strategy predicts recovery beyond C. |

**Total** = 4(8) + 2(5) + 1(6) + 3(5) + 3(8) = 32 + 10 + 6 + 15 + 24 = **87**

---

### I7: Contact Softening

| Criterion | Raw Score | Rationale |
|-----------|-----------|-----------|
| Information Gain | 7 | Could distinguish between "C measures absence of grains" vs "C measures interaction structure." If softening reproduces removal results → C is about interactions, not just presence. Novel information. |
| Difficulty | 2 | ~20 lines. Need to modify contact-force computation. Risk of breaking physics. |
| Runtime | 8 | 30 runs × 3s = 90s. Fastest experiment. |
| Confounding Risk | 3 | Softening changes time scales. Recovery times not comparable. The physics of soft contacts is fundamentally different from absent grains. |
| Isolation of Res(C) | 6 | Can compute C straightforwardly. But the softening parameter choice is arbitrary. |

**Total** = 4(7) + 2(2) + 1(8) + 3(3) + 3(6) = 28 + 4 + 8 + 9 + 18 = **67**

---

### I8: Gravity Sweep

| Criterion | Raw Score | Rationale |
|-----------|-----------|-----------|
| Information Gain | 6 | Tests confining pressure hypothesis. But too many things change: settling dynamics, velocity scales, perturbation magnitude. |
| Difficulty | 10 | One parameter change. |
| Runtime | 7 | 50 runs × 3s = 150s. |
| Confounding Risk | 2 | Gravity changes EVERYTHING: settling rate, contact forces, effective perturbation weight. Cannot isolate C from force changes. |
| Isolation of Res(C) | 4 | C is measurable but confounded with direct force effects. |

**Total** = 4(6) + 2(10) + 1(7) + 3(2) + 3(4) = 24 + 20 + 7 + 6 + 12 = **69**

---

### I9: Equilibration Time

| Criterion | Raw Score | Rationale |
|-----------|-----------|-----------|
| Information Gain | 3 | The system may already be equilibrated at t=500 at all friction levels (checkable from existing data). Low ceiling on information. |
| Difficulty | 10 | One parameter change. |
| Runtime | 8 | 40 runs × 3s = 120s. |
| Confounding Risk | 8 | If system IS at equilibrium, there's no confound — just no signal. Low risk. |
| Isolation of Res(C) | 3 | If pre-C is already stable, there's nothing to measure. |

**Total** = 4(3) + 2(10) + 1(8) + 3(8) + 3(3) = 12 + 20 + 8 + 24 + 9 = **73**

---

### I10: Density Sweep (Fixed μ = 0.40)

| Criterion | Raw Score | Rationale |
|-----------|-----------|-----------|
| Information Gain | 9 | The cleanest test of the sparseness hypothesis. Friction is completely controlled. If density→C→recovery holds at fixed friction, this strongly favors H1. Does NOT fully distinguish causal from thermometer (still at single friction level). |
| Difficulty | 10 | One parameter: `box_width`. |
| Runtime | 6 | 80 runs × 3s = 240s. |
| Confounding Risk | 7 | Wall effects at extreme widths. But friction is perfectly controlled — cannot be a confound. |
| Isolation of Res(C) | 9 | Direct measurement of Residual(C) = C − E[C\|friction] where friction is constant, so Residual(C) = C − mean(C). Pure density signal. |

**Total** = 4(9) + 2(10) + 1(6) + 3(7) + 3(9) = 36 + 20 + 6 + 21 + 27 = **110**

## Rankings

| Rank | Intervention | Score | IG | Cost (Diff+Runtime+Confound) |
|------|------------|-------|----|------|
| **1** | **I4: Friction×Density Grid** | **112** | 10 | 10+4+7=21 |
| **2** | **I10: Density Sweep (μ=0.40)** | **110** | 9 | 10+6+7=23 |
| 3 | I1: Density Sweep (all μ) | 101 | 8 | 10+7+7=24 |
| 4 | I6: Selective Removal | 87 | 8 | 5+6+5=16 |
| 5 | I9: Equilibration Time | 73 | 3 | 10+8+8=26 |
| 6 | I8: Gravity Sweep | 69 | 6 | 10+7+2=19 |
| 7 | I3: Size Distribution | 68 | 6 | 8+7+2=17 |
| 8 | I5: Removal Fraction | 67 | 4 | 10+7+5=22 |
| 9 | I7: Contact Softening | 67 | 7 | 2+8+3=13 |
| 10 | I2: Initial Clustering | 54 | 5 | 3+7+3=13 |

The top two are separated by 2 points. I4 edges out I10 on information gain (10 vs 9) but costs nearly 2× the runtime (450s vs 240s).

## Decision Matrix

For the director's constraint of "minimal experiment" (fewest changes, largest update):

| | I4 (Friction×Density) | I10 (Density at μ=0.40) |
|---|---|---|
| Code changes | 1 line | 1 line |
| Runtime | 150 runs, 450s | 80 runs, 240s |
| Friction levels | 5 (all) | 1 (0.40) |
| Can test additivity? | Yes | Limited |
| Can test interaction? | Yes | No |
| Can generalize across μ? | Yes | No |
| Confounds controlled? | Wall effects | Wall effects |
| Risk-corrected info | 112/450s = 0.25 pts/s | 110/240s = 0.46 pts/s |

**I10 has 1.8× higher information per second of runtime.** For the "minimal" mandate, I10 wins.

## Recommendation

**I10 (Density sweep at fixed friction=0.40)** is the top candidate for minimal experiment.

**I4 (Full friction×density grid)** is the top candidate if comprehensive information is prioritized over speed.

The deciding factor: the director asked for the experiment that provides the largest causal update with the fewest code modifications. I10 and I4 are equal on modifications (1 line each). I10 provides 80% of the information at 53% of the runtime. I10 wins.
