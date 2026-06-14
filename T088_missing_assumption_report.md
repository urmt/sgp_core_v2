# T088 Report: Missing Assumption Localization Audit

## Objective
Identify what drives the four assumptions that fail the emergence metric under MC2+MC3+MC4 alone: OC2, OC1, CD1, IS2.

## Surprising Result

**The "missing" assumptions are NOT missing from viable systems. They are near-universal properties of the system space.**

At threshold >= 0.2 across ALL 240 systems:
- OC2: 99.2% present
- OC1: 97.9% present
- CD1: 100.0% present
- IS2: 100.0% present

Within the viable set (MC2+MC3+MC4 >= 0.5, n=22): all 4 are present in 100% of systems.

The four assumptions fail the emergence metric because the **none-group also scores high** on them. The delta between high-MC and low-MC groups is < 0.2 — not because the assumptions are hard to generate, but because they are **too easy**.

## Per-Assumption Classification

### OC2 (Distinguishability) — Ceiling Effect
- Mean = 0.908, 96.7% >= 0.5 across ALL systems
- Negatively correlated with connectivity (r=-0.48): fewer connections mean more distinguishable transition sets
- Positively correlated with state expansions (r=0.38) and transition diversity (r=0.34)
- **Classification**: Distinguishability is a basic property of any Markov chain with >1 state. The MC framework cannot create a system that lacks it.

### OC1 (Boundedness) — Tradeoff Effect
- Mean = 0.619, 77.1% >= 0.5 across all systems
- **Anti-correlated with MC2** (r=-0.84): high MC2 reduces boundedness
- Strongly correlated with self_correlation (r=0.71), convergence (r=0.46), boundary_strength (r=0.58)
- **Classification**: OC1 trades off against MC2. High-MC systems have diverse state trajectories, which reduces recurrence-based boundedness. The none-group (low MC) scores HIGH on OC1 because simpler systems revisit states more. The emergence metric sees a negative delta where none should exist.

### CD1 (Causal Relations) — Ceiling Effect
- Mean = 0.488, 100% >= 0.2 across ALL systems
- Strongly determined by determinism (r=0.79)
- Mild anti-correlation with MC2 (r=-0.52)
- **Classification**: Causal relations are near-universal. Any non-random system has deterministic structure. At the 0.2 threshold, ALL 240 systems pass — impossible to form an emergence delta.

### IS2 (Coincidence) — Measurement Artifact
- Mean = 0.573, 100% >= 0.5 across ALL systems
- Returns only 0.5 (85% of systems) or 1.0 (15% of systems)
- 0.5 is the MEASUREMENT FLOOR: any system with >2 unique states in last 10 steps
- 1.0 only when system has converged to <=2 states in last 10 steps
- **Classification**: IS2 cannot contribute to an emergence metric because 0.5 is its default value. 100% of systems score >= 0.5. Either remove IS2 or redesign to produce continuous values.

## Common Cause Analysis

The four missing assumptions do NOT share a common driver:
- OC2: driven by transition diversity, suppressed by connectivity
- OC1: anti-correlated with MC2, driven by boundary strength + convergence
- CD1: driven by determinism (universal)
- IS2: measurement floor artifact

Eigenvalue analysis: 4 distinct dimensions in the missing-assumption covariance, confirming independent causes.

## What This Means

1. **The program has no gap.** MC2+MC3+MC4 alone generates ALL 9 substrate assumptions at standard thresholds within the viable population. The 4 "missing" assumptions are not missing from viable systems — they fail the emergence metric because low-MC systems also have them.

2. **Persistence is irrelevant.** T086 showed persistence adds near-zero marginal value. T088 shows there's nothing to add value to — MC2+MC3+MC4 already generates the full set.

3. **The emergence metric is the problem, not the substrate.** The delta-based emergence test (all_mean - none_mean >= threshold) is misleading when assumptions are near-universal. A genuinely missing assumption would have: mean < 0.3, max < 0.5, < 10% of systems above threshold. None of the 4 "missing" assumptions satisfy these criteria.

## Recommendation

The emergence metric should distinguish between three failure modes:
- **UNREACHABLE**: assumptions that cannot be generated (not present here)
- **WEAKLY GENERATED**: assumptions present in absolute terms but absent in the emergence delta (OC2, OC1, CD1)
- **MEASUREMENT ARTIFACT**: assumptions whose measurement scale prevents emergence detection (IS2)

Only the first category represents a genuine gap in the program. The program is architecturally complete with MC2+MC3+MC4 alone.
