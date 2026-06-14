# RD-9E: Surprise Persistence Audit — VERDICT

**Status**: COMPLETE  
**Date**: 2026-06-10  
**Question**: Does Surprise Persistence (SP) survive rigorous auditing?

## Verdict: SP IS A DISCRETIZATION ARTIFACT. FALSIFIED.

## Evidence

### Step 1: Continuity — SP IS BINARY
- 72 granular runs (20 grains, 500 steps, 12 friction levels × 6 reps): **SP=1.0 for ALL runs. Zero variation.**
- With finer thresholds (pct=80, 85): SP=1.0 or 2.0 — still binary.
- SP does not vary with friction, C, or any physical parameter.
- **SP is not continuous. It is a discretization artifact of the autocorrelation threshold.**

### Step 2: Estimator Sensitivity — SP COLLAPSES UNDER PARAMETER CHANGES
- k=2: SP varies (1-4), but k=3 and k=5: SP=1.0 always.
- Threshold (pct=80-95): SP=1.0 always.
- Warmup (20-50): SP=1.0 always.
- SP is estimator-dependent AND system-size-dependent.

### Step 3: Coarse Graining — SP IS BIN-COUNT DEPENDENT
- bins=3: SP ∈ {0, 2}
- bins=5: SP ∈ {0, 2, 7, 16}
- bins=10: SP ∈ {0, 1, 2, 4, 5, 7, 8, 14, 16, 21, 23, 24}
- SP varies wildly with bin count. Not robust to coarse graining.

### Step 6: Domain Transfer — SP = 1.0 EVERYWHERE
| System | Unique SP values | Result |
|--------|-----------------|--------|
| Coupled Markov (5 coupling levels × 10 seeds) | [1.0] | **UNIFORM** |
| Modular (4 within levels × 10 seeds) | [1.0] | **UNIFORM** |
| Hierarchical (4 coupling levels × 10 seeds) | [1.0] | **UNIFORM** |
| Forest (24 plots) | [1.0, 2.0] | Nearly uniform |
| Sandpile (5 seeds) | [1.0] | **UNIFORM** |
| Independent noise (10 seeds) | [1.0] | **UNIFORM** |

**SP = 1.0 for 99% of all systems tested. It measures nothing.**

## What Went Wrong

SP computes the autocorrelation of a binary surprise series and finds the lag where ACF < 1/e. For almost all systems, the ACF drops below 1/e at lag 1 (the very first lag). This gives SP=1.0 universally.

The "variation" seen in RD-9 (SP=1.0 or 2.0) was:
1. A finite-size effect (50 grains × 1500 steps vs 20 grains × 500 steps)
2. Rarely, the ACF took 2 lags to decay — giving SP=2.0
3. This is noise, not signal

## Falsification Scorecard

| Criterion | Result |
|-----------|--------|
| Continuous? | **NO** — binary (1.0 or 2.0) |
| Estimator-robust? | **NO** — sensitive to k, threshold, warmup |
| Coarse-graining robust? | **NO** — varies wildly with bin count |
| Cross-domain? | **NO** — SP=1.0 everywhere |
| Corresponds to physical events? | **NO** — no variation to map |
| Independent of friction? | **YES** (trivially — SP has no variation at all) |

**Score: 1/6 (trivially). SP is falsified.**

## What This Means

SP joins the cemetery:
- C-resilience (RD-5/6): falsified
- Motion fertility (RD-8B): collapsed into fluidity
- Predictive surprise (RD-9): collapsed into friction
- Generative novelty v1 (RD-9): collapsed into activity
- **Surprise persistence (RD-9E): discretization artifact**

## The Deeper Lesson

Every metric we've tried to capture "fertility" or "novelty production" has failed:
- Motion-based metrics → fluidity
- Surprise magnitude → friction
- Surprise persistence → autocorrelation artifact
- Volume expansion → activity level

The pattern is clear: **no single time-series metric can capture novelty production.** Novelty production is not a property of the signal — it's a property of the relationship between the signal and the space of possible signals. You can't measure it by looking at one trajectory. You need to measure the trajectory against the space of trajectories the system *could* have produced.

This is why the Constraint Geometry Framework (next) may be more important than any metric. The question isn't "what should we measure?" — it's "what constraints must simultaneously hold for generative organization to exist?"

## Status: SP IS FALSIFIED. Moving to RD-10 (Constraint Geometry).
