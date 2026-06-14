# RD-8B: Fertility Recon

**Date:** 2026-06-10
**Status:** COMPLETE
**Directive:** Measure possibility-generation metrics. Re-run geometry. Does a new factor appear?

---

## Executive Summary

Computed 6 fertility candidates from 160 raw trajectories (16 friction levels × 10 reps). Three were trivial (constant). Three were informative. Re-ran PCA with all 15 metrics (12 existing + 3 fertility).

**Result: No new factor.** All three fertility metrics load on PC1 (fluidity axis), alongside C, MSE, friction, rms_velocity. They correlate r=0.61-0.75 with C. Factor analysis still optimal at 3 factors (BIC unchanged).

**The reason is precise:** The fertility metrics I computed measure **motion through state space** (trajectory divergence, velocity entropy, expansion rate). These are projections of the same fluidity dimension as C, MSE, and rms_velocity. A system that moves more explores more — this is tautological, not structural.

**What was not measured:** Genuinely novel state creation — states that couldn't be predicted from the system's history. This requires measuring **surprise** or **information gain**, not just **motion**.

---

## 1. Metrics Computed

| Metric | What it measures | Result |
|--------|-----------------|--------|
| trajectory_divergence | Lyapunov-like separation of grain paths | r=0.70 with C — NOT independent |
| velocity_entropy | Shannon entropy of velocity distribution | r=0.61 with C — NOT independent |
| expansion_velocity | Rate of y-volume growth | r=0.75 with C — NOT independent |
| novel_state_rate | Fraction of coarse-grained states never seen | Trivially 1.0 — too stochastic |
| state_coverage | Fraction of possible states visited | Constant across friction — no signal |
| config_diversity | Number of distinct configuration clusters | Trivially 1.0 — always uses all clusters |

---

## 2. PCA with Fertility Metrics

15 metrics × 60 runs. PC1 now explains **45.0%** (up from 40.7% without fertility).

**PC1 (45.0%) — Fluidity/Activity:**
- friction: +0.36
- expansion_velocity: -0.32 ← FERTILITY
- traj_divergence: -0.31 ← FERTILITY
- velocity_entropy: -0.30 ← FERTILITY
- C: -0.34
- MSE: +0.32
- rms_velocity: -0.27

**All three fertility metrics load on the same axis as the existing metrics.** They add variance to PC1 (45.0% vs 40.7%) but do not create a new dimension.

---

## 3. Why No New Factor

The fertility metrics I computed measure **how much the system moves**. But:

- A system that moves a lot → high trajectory divergence, high velocity entropy, high expansion velocity
- A system that moves a lot → also high C (at low friction), high rms_velocity
- Therefore: fertility metrics correlate with C

This is circular. The metrics I chose to operationalize "possibility generation" are themselves projections of the same fluidity dimension they were supposed to be independent of.

**The fundamental confusion:** Motion ≠ Possibility generation. A gas at high temperature has maximum motion but minimum structural novelty. A crystal at low temperature has minimum motion but maximum structural regularity. Neither generates new possibilities.

---

## 4. What Would Be Independent

For fertility to be a genuinely new factor, it must measure something that:
1. Is NOT correlated with fluidity (C, rms_velocity, friction)
2. Captures **structural novelty** — states that are qualitatively different, not just in different positions

Candidates not yet measured:

| Candidate | What it measures | Why it might be independent |
|-----------|-----------------|---------------------------|
| Predictive surprise | How much the next state differs from prediction | A system can be fluid but predictable (low surprise) |
| State novelty rate | How often the system visits states unlike any previous state | A system can be fluid but repetitive |
| Configuration entropy | Shannon entropy of coarse-grained state distribution | A system can be fluid but confined to few states |
| Branching factor | Number of distinct futures accessible from current state | A system can be fluid but deterministic |

---

## 5. Implications

### The current metric family is missing an entire category

RD-8A found 3 factors: Fluidity, Perturbation Response, Recovery Dynamics.

RD-8B confirms: the fertility metrics we computed are **projections of Fluidity**.

The real question — **does the system generate genuinely new possibilities?** — remains unanswered because we haven't measured the right thing.

### What the Initiative should do next

1. **Define "novelty" precisely**: Not motion, not exploration, but **structural surprise** — states that couldn't be predicted from the system's history
2. **Compute predictive surprise**: Fit a model to the system's trajectory, measure how often the system violates its own predictions
3. **Re-run geometry**: If predictive surprise is orthogonal to F1-F3, we've found the 4th dimension

---

## 6. Files

- `audits/rd8b_fertility_v2.py` — sweep + geometry
- `audits/rd8b_fertility_v2.json` — raw data (160 runs)
