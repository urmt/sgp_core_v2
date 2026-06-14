# Residual Information Audit

**Question**: What specifically is C capturing that friction is not?

---

## Method

1. Regress C on friction: C = β₀ + β₁·friction + ε
2. Extract ε = residual(C | friction) — the component of C not explained by friction
3. Test whether ε predicts recovery metrics

If ε predicts recovery, C contains genuine state information beyond friction.

---

## 1. C ~ Friction Regression

**C = −0.89 × friction + ε**
**R² = 0.793**

Interpretation: 79.3% of C's variance is shared with friction. 20.7% is independent.

---

## 2. Does Residual(C) Predict Recovery?

| Target | ε R² | ε coefficient | ε t-stat | ε p-value | Status |
|--------|:----:|:-------------:|:--------:|:---------:|--------|
| ΔC | **0.129** | +0.790 | +2.93 | **0.0048** | Significant |
| Restoration | **0.271** | −1.145 | −4.65 | **< 0.001** | Strongly significant |
| τ_rec | **0.126** | +0.781 | +2.90 | **0.0053** | Significant |

**Result**: Residual(C) predicts all three recovery targets. This is stronger evidence that C contains genuine state information not reducible to friction.

---

## 3. Critical Surprise: Residual(C) Outperforms Raw C

| Target | Raw C R² | Residual(C) R² | Ratio |
|--------|:--------:|:--------------:|:-----:|
| ΔC | 0.105 | 0.129 | **1.2×** |
| Restoration | 0.036 | 0.271 | **7.6×** |
| τ_rec | 0.046 | 0.126 | **2.7×** |

Residual(C) predicts restoration **7.6× better** than raw C.

**Why?**

Raw C = friction-correlated signal + friction-independent signal. For restoration:
- The friction-correlated component of C is essentially **noise** (contributes ~nothing to prediction)
- The friction-independent component is **strongly predictive**

This is consistent with the following interpretation:

> C contains two components. The component shared with friction is not useful for predicting recovery. The component independent of friction — which captures genuine structural information — predicts recovery well.

This favors Model C (C participates in the mechanism) over Model D (C is a friction proxy). If C were purely a friction proxy, the residual after removing friction should be noise. It is not — it is the **most** predictive component.

---

## 4. Conditional Information: Residual(C) Given Friction

| Target | Friction R² | +Residual(C) R² | ΔR² | p-value |
|--------|:----------:|:---------------:|:---:|:-------:|
| ΔC | 0.299 | 0.428 | **+0.129** | 0.005 |
| Restoration | 0.229 | 0.500 | **+0.271** | < 0.001 |
| τ_rec | 0.179 | 0.305 | **+0.126** | 0.005 |

Adding residual(C) to friction meaningfully improves prediction for all targets.

---

## 5. Residual(C) Given Friction + Interaction

| Target | Friction+Int R² | +Residual(C) R² | ΔR² |
|--------|:--------------:|:---------------:|:---:|
| ΔC | 0.405 | 0.523 | **+0.118** |
| Restoration | 0.307 | 0.565 | **+0.258** |
| τ_rec | 0.226 | 0.345 | **+0.119** |

Residual(C) adds predictive power even beyond the friction + interaction model. The interaction term does not absorb C's unique information.

---

## 6. Predictive Power Decomposition

How much of C's predictive power is unique (independent of friction)?

| Target | C Total R² | Unique to C (ε R²) | Shared with Friction |
|--------|:---------:|:------------------:|:--------------------:|
| ΔC | 0.105 | **0.129** | −0.025* |
| Restoration | 0.036 | **0.271** | −0.236* |
| τ_rec | 0.046 | **0.126** | −0.080* |

*Negative shared values mean the friction-correlated component of C is **anti-predictive** — it actively suppresses C's predictive signal. Removing it improves prediction.

**Interpretation**: The friction-C correlation does not explain C's predictive success. It **hinders** it. If C were a friction proxy, removing friction's influence should eliminate C's predictive power. Instead, it enhances it.

---

## Key Finding

The portion of C that is **unique** (not explained by friction) predicts recovery:
- **7.6× better** than raw C for restoration
- **1.2× better** for ΔC
- **2.7× better** for τ_rec

This is the strongest evidence obtained so far that C contains genuine state information rather than merely reflecting friction. The alternative interpretation — that the residual captures some other confound — remains possible but requires specifying what that confound would be, given that mobility proxies cannot explain it (ΔR² ≤ 0.042).
