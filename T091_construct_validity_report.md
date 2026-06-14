# T091: Construct Validity Audit — Report

## Objective
For each of the 9 substrate assumptions, determine whether the operational metric actually measures the theoretical construct it is supposed to represent.

## Method
Document analysis: trace each assumption from its original SFH-SGP theoretical definition (T061) through its refined definition (T080) to its operational measurement (T082). Identify specific threats to construct validity, classify validity level, and cross-reference against T090 substrate-independence findings.

## Validity Summary

| Assumption | Theoretical Construct | Operational Metric | Validity | Primary Issue |
|-----------|---------------------|-------------------|----------|--------------|
| **OC2** | Observer-phenomenon distinction | Distinct transition-pattern ratio | LOW-MOD | Narrow — measures state distinguishability, not observer-phenomenon distinction |
| **OC1** | Stable structure / persistence | 1 - recurrence in last 20 steps | **LOW** | **Inversion error**: structure ≠ repetitiveness |
| **CD1** | Causal relations exist | 40% param + 60% consistency | MODERATE | Parametric leakage; empirical component is reasonable |
| **IC1** | Extractable information | Amplified branching factor ×1.5 | **LOW** | **Inversion error**: branching ≠ information |
| **IS1** | Phase structure / stages | Block-change rate (size=5) | MODERATE | Arbitrary timescale; set comparison loses order |
| **IS2** | Determinate outputs | Floored inverse diversity (min=0.5) | **VERY LOW** | **Floor artifact**: uninformative for most systems |
| **CD2** | Self-affecting procedures | Weighted param sum (70% config) | **LOW** | **Parametric contamination**: measures model, not phenomenon |
| **EC1** | Self-knowledge | Weighted param sum (80% config) | **LOW** | **Parametric contamination**: same as CD2 |
| **SR1** | Self-examination of outputs | Bifurcated param sum | **VERY LOW** | **Critical failure**: bifurcation pre-judges phenomenon |

## The Five Threats to Construct Validity

### 1. Inversion Errors (OC1, IC1)
The operational metric for OC1 and IC1 *inverts* the theoretical construct:
- **OC1** (stable structure) measures *repetitiveness* (few distinct states → high score). A system with complex structured dynamics (e.g., deterministic chaos) gets OC1≈0 despite having maximal structure. A trivial 2-state oscillator gets OC1≈0.9.
- **IC1** (extractable information) measures *branching diversity* (many successors → high score). A deterministic system where the next state is perfectly predictable has zero extractable information by this metric, when in fact information is maximally extractable.

**Remediation**: Replace with permutation entropy (OC1) and mutual information between consecutive states (IC1).

### 2. Parametric Contamination (CD2, EC1, SR1)
70-80% of the score for CD2, EC1, and SR1 comes from simulator configuration parameters (`self_model_level`, `self_model_influence`) — direct inputs to T082's simulator, not observed properties of the system. These assumptions measure **how the simulator was configured**, not what the system does.

CD2's formula: 40% from capped sm_level + 30% from sm_influence = 70% parametric.
EC1's formula: 50% from sm_level/3 + 30% from sm_influence = 80% parametric.
SR1's formula: bifurcated by sm_level; both branches driven by sm parameters.

**Remediation**: Replace with behavioral/observational measures. CD2 should detect feedback loops in transition dynamics. EC1 should detect state-dependent modulation of behavior. SR1 should detect output reincorporation into subsequent behavior.

### 3. Measurement Floor Artifacts (IS2)
IS2's formula has a built-in floor: `min(0.5, 5.0/unique)` ensures no system with >2 states in the last 10 steps scores below 0.5. Most systems get exactly 0.5, making the metric nearly uninformative.

**Remediation**: Redesign from scratch. "Determinate outputs" should measure test-retest reliability or output variance under repeated conditions.

### 4. Parameter Leakage (CD1)
40% of CD1's score is the `determinism` parameter — a simulator input, not an observation. In non-Markov substrates this parameter is unavailable, making CD1's measurement inconsistent.

**Remediation**: Remove the parametric component; use only empirical transition consistency.

### 5. Label Overclaiming (OC2, all)
OC2's metric (state distinguishability) is narrower than its theoretical label (observer-phenomenon distinction). More generally, all 9 assumptions use theoretical-philosophical labels for empirical-technical metrics. This creates an **unacknowledged levels gap** between the conceptual framework and its measurement.

**Remediation**: Distinguish between theoretical constructs (philosophical) and operational metrics (empirical) in all documentation.

## Cross-Reference with T090

| T091 Finding | T090 Classification | Relationship |
|-------------|-------------------|--------------|
| IC1: inversion error (branching ≠ information) | Markov artifact | Explains why IC1 fails cross-substrate — deterministic substrates have no branching |
| CD2/EC1/SR1: parametric contamination | Markov artifact | Explains why these fail — they measure simulator parameters absent in other substrates |
| OC1: inversion error (repetitiveness ≠ structure) | Implementation-dependent | Explains variance — repetitiveness varies by substrate |
| CD1: parametric leakage | Implementation-dependent | Explains partial variance — consistency component is substrate-independent, param is not |
| IS1: moderate validity (block-change) | Implementation-dependent | Valid proxy but depends on substrate dynamics |
| OC2: narrow but valid (state distinguishability) | Primitive | Explains universality — any discrete system has distinguishable states |
| IS2: floor artifact | Primitive (floor) | Explains universality — floor ensures 100% prevalence |

The construct validity analysis **explains** the T090 substrate-independence findings. The Markov artifacts are artifacts of parametric contamination; the primitives reflect valid-but-narrow or measurement-floored metrics.

## Revised Architecture Status

The 9 assumptions are **neither discovered universal properties nor random artifacts**. They are:

| Type | Count | What they actually are |
|------|-------|----------------------|
| Valid narrow metrics | 1 (OC2) | State distinguishability — a universal but limited property |
| Moderately valid proxies | 2 (CD1 consistency component, IS1) | Reasonable empirical proxies with acknowledged limitations |
| Inverted constructs | 2 (OC1, IC1) | Metrics that measure the opposite of their label |
| Config artifacts | 3 (CD2, EC1, SR1) | Measurements of simulator parameters, not phenomena |
| Floor artifacts | 1 (IS2) | A measurement floor, not a substantive property |

The SFH-SGP can legitimately claim **one** substrate property (state distinguishability) as a universal primitive. The remaining 8 require either metric redesign or acknowledgment that they are simulator-specific design commitments.

## Recommendation for the Program

1. **Accept the levels gap**: Theoretical constructs and operational metrics operate at different levels. Acknowledge this explicitly.
2. **Redesign 5 metrics**: OC1, IC1, IS2, CD2, EC1, SR1 need new behavioral/observational measures before any cross-substrate claim can be made.
3. **Protect 2 metrics**: CD1 (empirical component only) and IS1 are reasonable proxies with known limitations.
4. **Retain OC2**: As a narrow but valid measure of state distinguishability.
5. **Hold the architecture**: The 9-assumption substrate should be treated as a **simulator design specification**, not as discovered theory.
