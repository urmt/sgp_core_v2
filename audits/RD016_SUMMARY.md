# RD-016: Nested Model Hierarchy, Residual-C Audit, Level Leverage

**Director's summary of findings**

## Priority 1: Nested Model Hierarchy — interaction does NOT survive Fr²

**Question**: After friction curvature (Fr²) is included, does C×friction interaction still add unique explanatory power?

**Answer: No.** For ΔC and restoration, the `C + Fr + Fr²` model matches or beats `C + Fr + C×Fr`. Adding interaction beyond Fr² yields only ΔR² = +0.004–0.007 — negligible.

| Comparison | ΔC ΔR² | Restoration ΔR² |
|------------|--------|-----------------|
| Fr² vs Interaction | **+0.009** (Fr² wins) | **+0.007** (Fr² wins) |
| Fr² vs Full (Fr²+Interaction) | +0.007 | +0.004 |

The director's earlier concern (RD-015) was correct: the interaction and Fr² models were nearly tied. RD-016 resolves the tie in favor of Fr².

## Priority 2: Residual(C) Mechanism — not mobility in disguise

Residual(C) (C with friction regressed out) is largely orthogonal to all measured mobility descriptors:

| Descriptor | r with residual(C) | Interpretation |
|-----------|-------------------|----------------|
| MSD | −0.15 | Weak, n.s. |
| RMS velocity | −0.14 | Weak, n.s. |
| Neighbor turnover | −0.01 | None |
| Packing variance | +0.26* | Weak, nominally significant |

Residual(C) predicts recovery **beyond all four mobility variables combined**:
- Restoration: ΔR²(res\|mob) = **+0.24**
- τ_rec: ΔR²(res\|mob) = **+0.15**
- ΔC: ΔR²(res\|mob) = **+0.10**

**Conclusion**: The friction-independent component of C captures genuine structural information that standard mobility statistics miss. The RD-015 finding (residual predicts 1.2–7.6× better than raw C) is not because residual proxies some other measured quantity.

## Priority 3: Level Leverage — interaction is endpoint-driven

**CRITICAL FINDING**: The interaction collapses when extreme friction levels are removed.

| Condition | ΔC p(Int) | Restoration p(Int) |
|-----------|-----------|-------------------|
| Full data (n=60) | **0.002** | **0.006** |
| Remove friction=0.80 only | **0.143** | **0.203** |
| Remove both extremes (0.05, 0.80) | **0.253** | **0.652** |

Without the two extreme friction levels, the interaction coefficient drops 30–65% and becomes non-significant for ALL targets. The model cannot distinguish interaction from noise without these anchors.

## Updated model ranking

| Model | Verdict | Rationale |
|-------|---------|-----------|
| **C+Fr+Fr²** (curvature) | **New leader** | Best R², AIC, CV for ΔC and restoration |
| **D: Thermometer / nonlinear** | **Strengthened** | Fr² curvature is consistent with friction dominance |
| **C: Interaction** | **Weakened** | Not robust to Fr² inclusion or endpoint removal |
| **B: Mobility-only** | Unchanged | Adequate but incomplete (missing C's unique contribution) |
| **A: C-only** | Unchanged | Falsified as standalone predictor |

## Assumptions register update

| # | Assumption | Old Status | New Status | Reason |
|---|-----------|-----------|-----------|--------|
| 14 | Interaction is genuine | Unknown | **Challenged** | Doesn't survive Fr² or endpoint removal |

## Next steps

1. **Decision for director**: The interaction model is no longer tenable as the leading explanation. The Fr² curvature model (C adding linearly within a nonlinear friction effect) is the best current description of the data.

2. **Causal claims still not upgraded**: Residual(C) predicts, but we still cannot say C causes recovery. The "C contains unique information" claim remains at Supported, Moderate — strengthened by the residual audit, but the endpoint dependence of interaction weakens the overall story.

3. **Causal experiment (P1 intervention)**: The priority for the next round remains: manipulate C independently of friction. The residual(C) finding shows this is possible in principle (C varies within friction levels), but the mechanism connecting C to recovery is not settled.

4. **Limitation acknowledged**: n=60 with endpoint-driven effects means all findings are tentative. The interaction model's fragility is a clear signal that conclusions depend on the range of friction tested.
