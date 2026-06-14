# Causal Hypotheses Comparison

Four competing models for the relationship between coherence, mobility, and recovery.

---

## Model A: Causal Coherence

```
Coherence ───────► Recovery
```

### Claim

Coherence is a causal driver of recovery. Systems with high coherence recover better BECAUSE their interaction structure buffers perturbation. Lowering coherence directly impairs recovery capacity.

### Mathematical Form

ΔC ~ C + ε
τ_rec ~ C + ε
Restoration ~ C + ε

### Evidence

| Target | R² | p (approx) | Support |
|--------|-----|-----------|---------|
| ΔC (dip) | 0.10 | ~0.01 | Weak |
| τ_rec | 0.05 | ~0.08 | None |
| Restoration | 0.04 | ~0.12 | None |

### Falsifications

1. **Sign ambiguity**: C=0.43–0.44 predicts both ΔC<0 (C increases at friction=0.40) and ΔC>0 (C decreases at friction=0.60–0.80). If C were causal, same C would produce same ΔC sign.
2. **Speed ambiguity**: 10 C-matched pairs show τ_rec ratios of 3–4×. Causal C would predict similar recovery times.
3. **Within-friction reversal**: At friction ≥ 0.40, higher C predicts SLOWER recovery. Causal C predicts faster recovery at higher C.

### Status

**Weakened.** Does not survive adversarial testing. R² values near zero for τ_rec and restoration.

---

## Model B: Mobility-Only

```
Mobility ───────► Recovery
```

### Claim

Recovery is determined solely by the system's capacity to reconfigure its interaction structure (mobility). Coherence is an epiphenomenon — it correlates with mobility but has no independent causal role.

### Mathematical Form

ΔC ~ friction + ε
τ_rec ~ friction + ε
Restoration ~ friction + ε

### Evidence

| Target | R² | p (approx) | Support |
|--------|-----|-----------|---------|
| ΔC | 0.30 | <0.001 | Moderate |
| τ_rec | 0.18 | <0.001 | Moderate |
| Restoration | 0.23 | <0.001 | Moderate |

### Falsifications

1. **Friction-only underperforms additive model**: Model B (R²=0.30 for ΔC) is substantially worse than Model C (R²=0.52). Mobility alone captures less than half the explainable variance.
2. **Within-friction C variation**: At fixed friction, C still varies and predicts ΔC (within-friction correlation of C with ΔC reaches |r| ≈ 0.3–0.6). If only mobility mattered, C would be irrelevant within a friction level.
3. **Different C, same friction, different recovery**: Multiple runs at identical friction (same nominal mobility) show different recovery outcomes that correlate with C.

### Status

**Plausible but incomplete.** Mobility explains more variance than C alone, but the additive and interaction models consistently outperform mobility-only. The within-friction C correlations suggest C contributes independently.

---

## Model C: Coherence × Mobility Interaction

```
Mobility ───────► Recovery
    │
    ▼
Coherence ───────► Recovery
         │
         ▼
Coherence × Mobility ──► Recovery
```

### Claim

Recovery depends on BOTH coherence and mobility, and their effect is interactive (not additive). The same coherence value produces different recovery in different mobility regimes. The same mobility value produces different recovery at different coherence levels.

### Mathematical Form

ΔC ~ C + friction + C×friction + ε
τ_rec ~ C + friction + C×friction + ε
Restoration ~ C + friction + C×friction + ε

### Evidence

| Target | R² | Δ from Model B | Support |
|--------|-----|----------------|---------|
| ΔC | 0.52 | +0.22 | Strong |
| τ_rec | 0.35 | +0.17 | Moderate |
| Restoration | 0.56 | +0.33 | Strong |

### Falsifications

1. **Collinearity**: C and friction are correlated (r≈−0.74). The interaction term may capture nonlinearity in C→recovery rather than genuine C×mobility interaction. This is NOT a falsification of Model C — it is a limitation of the current data.
2. **Within-friction C range small**: Within a friction level, C varies by only ±0.02–0.03. The interaction may be driven by cross-friction comparisons rather than true within-condition effects.

### Status

**Best supported by current data.** R² substantially higher than Models A or B for all three targets. The interaction term is positive for ΔC and τ_rec, negative for restoration — meaning at high friction (low mobility), C's effect on recovery is damped or reversed. This exactly matches the qualitative sign reversal.

---

## Model D: Coherence as State Descriptor (Thermometer)

```
Underlying Interaction Dynamics
        │
        ├──► Mobility ──► Recovery
        │
        └──► Coherence (informative, not causal)
```

### Claim

Coherence is a useful state variable — it tracks the system's interaction structure — but it is NOT a causal driver of recovery. The underlying interaction dynamics independently produce both:
- the coherence value we measure (as a readout), and
- the mobility that actually determines recovery.

Coherence is like a thermometer: it tells you whether the system is "hot" (organized) or "cold" (disorganized), but reading the thermometer does not change the temperature.

### Mathematical Form

No simple regression formula. The claim is about causal structure, not predictive fit.

Under Model D, C can have any predictive R² value — high or low — without being causal. What matters is whether intervening on C (without changing the underlying dynamics) changes recovery.

### Testable Predictions

1. **Intervention prediction**: If we could artificially set C to a different value WITHOUT changing the system's mobility (e.g., by rescaling the data), recovery would NOT change. This distinguishes Model D from Models A and C.
2. **C-manipulation test**: If we engineer two systems with identical underlying dynamics but different measured C (via different measurement resolution or binning), they should show identical recovery. This would support D over A/C.
3. **C variance source**: Under D, C's predictive power comes entirely from its correlation with mobility/underlying dynamics. If we control for the true underlying dynamics, C adds nothing.

### Relationship to Other Models

Model D is compatible with all current evidence:
- C's weak predictive power (R² ≤ 0.10 alone) — consistent with C being a noisy readout, not a driver
- C's failure to predict sign or speed — consistent with C being epiphenomenal
- Interaction model's superior fit — could be explained by C acting as a nonlinear proxy for the underlying dynamics

However, Model D is also the hardest to falsify with observational data. It requires an intervention experiment.

### Status

**Untestable with current passive-observation data.** Model D is the most philosophically conservative interpretation — it does not require C to be causal — but it cannot be distinguished from Models A or C without a C-intervention experiment.

---

## Cross-Model Comparison

| Property | Model A (C-causal) | Model B (Mobility) | Model C (Interaction) | Model D (Thermometer) |
|----------|-------------------|-------------------|---------------------|---------------------|
| **C is causal** | Yes | No | Yes (interactively) | No |
| **Mobility is causal** | No | Yes | Yes (interactively) | Yes (or underlying dynamics) |
| **R² for ΔC** | 0.10 | 0.30 | 0.52 | N/A (not predictive claim) |
| **R² for τ_rec** | 0.05 | 0.18 | 0.35 | N/A |
| **R² for restoration** | 0.04 | 0.23 | 0.56 | N/A |
| **Interaction required** | No | No | Yes | No |
| **Collinearity concern** | Irrelevant | Low | High | Low |
| **Falsified by current data?** | Yes | Partially | No | Not testable |
| **Testable with intervention?** | Yes | Yes | Yes | Requires C-manipulation |

---

## Experiment Design Implications

Each model makes different predictions for the P1 decoupling experiment:

| Model | Prediction for P1 |
|-------|------------------|
| A (C-causal) | At fixed friction, higher C → better recovery. Effect of C is similar across friction levels. |
| B (Mobility) | At fixed friction, C variation does NOT predict recovery. Only friction matters. |
| C (Interaction) | At fixed friction, C effect DEPENDS on friction level. At low friction: C has weak/positive effect. At high friction: C has negative effect. |
| D (Thermometer) | At fixed friction, C correlates with recovery (if underlying dynamics differ) but does NOT cause it. Within truly identical dynamics, C variation is noise. |

The critical test: **within-friction C variation**. If at friction=0.05, wide-polydisperse runs have lower C than narrow-polydisperse and also show DIFFERENT recovery, then C plays some role (supporting A or C). If they show IDENTICAL recovery despite C differences, then C is purely a readout (supporting B or D).

---

## Recommendation

The interaction model (C) is statistically best-supported but the thermometer model (D) has not been ruled out. No new simulation campaign should begin until:

1. The distinction between C as Causal (A/C) vs C as Readout (B/D) is clarified
2. A testable intervention design exists that discriminates these cases
3. The experiment design (P1) specifies which of these four models it can and cannot rule out

The highest-value intellectual work right now is specifying the intervention test that would distinguish Model D from Models A/C — because those tests are fundamentally different from anything in the current research program.
