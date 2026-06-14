# RD-9: Novelty Measurement Shootout

**Status**: COMPLETE  
**Date**: 2026-06-10  
**Question**: Can any formal novelty metric capture "fertility" — surprise that generates new future possibilities — independent of the existing 3-factor latent structure?

## Design

- 72 runs: 12 friction levels × 6 reps, 2000 steps each
- 4 novelty metrics: Predictive Surprise (PS), Surprise Persistence (SP), Historical Irreversibility (HI), Generative Novelty (GN)
- Tests: correlation audit, regression against F1/F2/F3, PCA+FA with each metric, 5-fold cross-validation

## Results

### Verdict Table

| Metric | Collapses? | r(friction) | r(C) | CV Stable? | Dimension |
|--------|-----------|-------------|------|------------|-----------|
| PS (Predictive Surprise) | **YES** | 0.891 | -0.808 | Yes | 3D (same as baseline) |
| SP (Surprise Persistence) | **NO** | -0.171 | 0.178 | Yes | **4D** (new PC3) |
| HI (Historical Irreversibility) | **YES** | -0.630 | 0.440 | No (3-4D) | Unstable |
| GN (Generative Novelty) | **YES** | -0.760 | 0.731 | No (3-4D) | Unstable |

### Detailed Findings

**PS (Predictive Surprise)** — COLLAPSES
- Heavily correlated with friction (r=0.89) and C (r=-0.81)
- FA loading: F1=-0.84, F2=0.50 — projects onto existing factors
- Interpretation: PS measures how "surprising" the motion is. High friction → erratic dynamics → higher surprise. It's measuring fluidity, not novelty.

**SP (Surprise Persistence)** — SURVIVES
- Weak correlation with friction (r=-0.17) and C (r=0.18) — **independent**
- PCA: creates new PC3 with loading=0.92 (other metrics load <0.30 on this component)
- CV: 4-dimensional structure stable across all 5 folds; loading std=0.024 (consistent)
- FA: still prefers 3 factors (BIC=1068) — SP adds a variance dimension without reshaping factor structure
- Interpretation: SP measures temporal clustering of surprise events. When surprises cluster, the system is in a regime of persistent unpredictability. This is NOT fluidity — a fluid system can be predictable, a frozen system can have isolated surprises.

**HI (Historical Irreversibility)** — COLLAPSES
- Moderate correlations: r=-0.63 with friction, r=0.67 with msd
- Dimension unstable across CV folds (3D or 4D)
- FA loading: F1=0.68 — projects onto fluidity
- Interpretation: HI measures irreversibility of trajectories, but irreversibility correlates with activity level (msd). More active → more irreversible.

**GN (Generative Novelty)** — COLLAPSES
- Strong correlations: r=-0.76 with friction, r=0.73 with C, r=0.76 with msd
- Dimension unstable across CV folds (3D or 4D)
- FA loading: F1=0.81 — projects onto fluidity
- Interpretation: GN (volume expansion after surprise) tracks activity level. More active systems have more volume expansion.

## Assessment

**One metric survived: Surprise Persistence.**

SP measures temporal clustering of surprise events — how long the system stays in a "surprising" regime before returning to predictable behavior. This is distinct from:
- Fluidity (how fast the system moves)
- Perturbation response (how the system reacts to shocks)
- Recovery dynamics (how the system returns to equilibrium)

SP is the first measurement that captures **regime persistence** — the system's tendency to stay in unusual states. This aligns with the Initiative's fertility concept: a fertile system doesn't just produce surprises, it sustains them and builds on them.

## Limitations

1. SP is a single metric — one dimension is thin evidence for a new latent direction
2. FA still prefers 3 factors — SP doesn't reshape the fundamental factor structure
3. SP uses a fixed threshold (90th percentile) — sensitivity to threshold choice is unknown
4. The simulation is still granular DEM — whether SP captures the same thing in other systems is unknown

## Falsification Scorecard

| Criterion | Result |
|-----------|--------|
| Explains new variance? | **PARTIAL** — adds PC3 but FA prefers 3 factors |
| Survives cross-validation? | **YES** — 4D stable across all folds |
| Appears across regimes? | **YES** — computed across 12 friction levels |
| Not reducible to motion? | **YES** — r=0.14 with rms_velocity |
| Not reducible to randomness? | **YES** — structured (autocorrelation decay, not white noise) |
| Corresponds to structural events? | **UNKNOWN** — requires mapping SP to specific events |

**Overall: SP passes 4/6 criteria. Partially survives.**

## Next Steps

1. **RD-10 (Constraint Geometry)**: Map the organizational phase diagram — bounded region where generative organization exists
2. **Characterize the SP dimension**: What physical events correspond to high vs low SP? Map SP to specific simulation dynamics.
3. **Test SP in other systems**: Does SP capture regime persistence in non-granular systems?
