T079: Meta-Constraint Inference — Report
========================================

## Method

32 findings from T072–T078 were scored against 5 candidate meta-constraints.

Scoring: +1 = supports (finding predicted or consistent)
         0  = neutral (no clear relationship)
         -1 = contradicts (finding would not be expected)

No substrate assumptions. No OC2. No mechanism reasoning.

---

## Constraint Ranking

| Rank | Constraint | Score | Supports | Against | Robustness | Coverage |
|------|-----------|-------|----------|---------|------------|----------|
| 1 | MC3: Constraint Balance | +22 | 22 | 0 | 1.00 | 0.69 |
| 2 | MC2: Productive Transformation | +19 | 19 | 0 | 1.00 | 0.59 |
| 3 | MC5: Recoverable Perturbation | +13 | 13 | 0 | 1.00 | 0.41 |
| 4 | MC4: Recursive Accessibility | +5 | 5 | 0 | 1.00 | 0.16 |
| 5 | MC1: Information Preservation | -5 | 6 | 11 | 0.35 | 0.19 |


---

## Minimal Constraint Set

No single minimal set covers all findings.

## Substrate Independence Test

Findings removed: F05 (viability above substrate), F06 (three-layer architecture),
F24 (recursive exceptional), F32 (RD/S on PC3).

Survivors (positive net without substrate): 4
- ✓ **MC2: Productive Transformation** (net=+19)
- ✓ **MC3: Constraint Balance** (net=+22)
- ✓ **MC4: Recursive Accessibility** (net=+3)
- ✓ **MC5: Recoverable Perturbation** (net=+12)

Eliminated: 1
- ✗ MC1: Information Preservation (net=-3)


---

## What Survives Without the Substrate

If the substrate disappeared — no OC2, no 9 assumptions, no mechanism classes —
the constraints that would remain are those whose explanatory power does not
depend on substrate-specific findings.

Those surviving constraints are the strongest candidates yet for the deepest
layer of the entire program.

Best pairwise synergy: MC2+MC3 covers 26/32 findings.


## Interpretations

### MC3 (Constraint Balance) — Top Ranked

The idea that fertility requires a balance between too much freedom (collapse)
and too much rigidity (fortress) is the single hypothesis most consistent with
the entire T072–T078 dataset. It predicts the boundary regime, the finite
corridor width, the negative stability-fertility correlation, the three-zone
landscape, and the dominance of collapse-ward drift.

### MC2 (Productive Transformation) — Strong Support

The idea that systems must generate novel structure predicts the dominance of
fertility axes in PC1, the existence of the fertile corridor, its connectedness
across domains, and its survival under dimensional compression.

### MC1 (Information Preservation) — Mixed

Information preservation predicts viability correctly (coherence, recoverability)
but contradicts many fertility findings (lower coherence in fertile systems,
boundary regime, negative correlation). It is necessary but not sufficient.

### MC4 (Recursive Accessibility) — Narrow but Deep

Recursive accessibility has the narrowest coverage (many neutrals) but its
specific predictions (S gap, recursive exceptional, RD/S on PC3) are strongly
confirmed. It is the most specialized constraint.

### MC5 (Recoverable Perturbation) — Solid but Secondary

Recoverable perturbation predicts the saddle-like dynamics and the corridor's
persistence, but does not directly predict the geometric structure of the
meta-space. It may be a consequence of other constraints rather than a
fundamental one.
