# SFH-SGP: Scalar-Field Hierarchies with Stochastic-Geometric Properties

## ABSTRACT
Candidate theory derived from empirical analysis of canonical V2_079 embeddings.
Framework posits that time-series classification performance is determined by
the interaction between scalar metric geometry and classifier architecture.

## CORE POSTULATES

### P1: Intrinsic Dimensionality
The canonical embedding manifold is effectively 1-dimensional (PC1=99.3%).
Transform variants occupy distinct loci in this low-dimensional space,
but share identical topological properties (mean distance ~9.0).

### P2: Metric Orthogonality
The four canonical metrics (ordinal flow, half-correlation, compression,
amplitude transition) capture geometrically distinct signal properties:
- m1: temporal ordering (invariant to amplitude)
- m2: autocorrelation structure (half-window)
- m3: informational redundancy (Kolmogorov complexity proxy)
- m4: amplitude state transitions (Markov chain structure)

### P3: Gate-Induced Information Destruction
Scalar gates (L2 threshold + correlation filter) discard discriminative
information for stochastic signals. LDA recovers this information because
it operates in the full metric space, not a projected scalar.

### P4: Transform Invariance Hierarchy
Transform variants exhibit graded invariance:
- REPLAY: quasi-invariant (m1=0.999, m4=0.999) due to duplication symmetry
- REVERSE: invariant in ordinal structure (m1) but not autocorrelation (m2)
- SWAP: disruptive to half-window properties, preserves compression
- STITCH: breaks temporal continuity entirely

### P5: Stochastic vs Deterministic Separation
Deterministic signals (chirp, chaotic_logistic, coupled_osc) have infinite
separation ratios — perfectly distinguishable.
Stochastic signals (rw_trend, regime_switch) have finite separation (2.1-2.6).
regime_switch suffers gate-induced confusion (gate=30% vs LDA=90%).

## MATHEMATICAL FORMULATION

Given signal s(t), canonical embedding e(s) ∈ ℝ⁴:
```
e = [m1(s), m2(s), m3(s), m4(s)]
```

Classification performance:
```
P(correct|deterministic) → 1.0 (always)
P(correct|stochastic, gate) → ~0.3-0.5 (information loss)
P(correct|stochastic, LDA) → ~0.9 (full space utilization)
```

## PREDICTIONS

1. Adding metrics beyond m1-m4 provides diminishing returns (eff_rank=99.3%)
2. Non-linear classifiers (LDA, SVM-RBF) outperform linear gates on stochastic data
3. Replay variant will always achieve 100% on canonical architecture
4. rw_trend has irreducible confusion due to true geometric overlap

## EVIDENCE SUMMARY

- T001: manifold dim95=1, purity=0.80, geo_corr=0.999 (linear)
- T002: curvature=0.059 (flat), connected locally
- T003: replay invariance m1/m4≈1.0, consistent displacement
- T004: all variants geometrically equivalent (spread≈9.0)
- A04: replay=100%, regime_switch (LDA)=90% vs gate=30%
- V2_082: LDA gate replacement confirms separable embeddings

## STATUS: CANDIDATE THEORY
Requires: formal proof of P1, mathematical characterization of P4 invariants
