# RD-MATH.1 — Falsifiability Audit

**Date:** 2026-06-15  
**Auditor:** OpenCode  
**Trigger:** Research Director directive — "What observation would falsify it?"

---

## Assumptions

The following audit records falsification conditions for candidate equations. No fitting, no optimization, no parameter estimation. Only: **what observation would falsify this equation?**

---

## Candidate Equations

### Ψ = C × F × I

**Assumption:** All variables normalized to [0, 1].

**Falsification conditions:**

1. **If Ψ decreases while C, F, I all increase** → falsified
2. **If Ψ increases while any of C, F, I decreases to zero** → falsified
3. **If Ψ > min(C, F, I)** → falsified (product cannot exceed minimum factor)
4. **If Ψ < max(0, C + F + I - 2)** → falsified (product has lower bound)
5. **If any variable is zero and Ψ is non-zero** → falsified

**Observational test:** Measure C, F, I for a system. Compute Ψ_predicted = C × F × I. Compare to Ψ_observed (if measurable). If Ψ_observed deviates significantly from Ψ_predicted, the equation is falsified.

**Problem:** Ψ is not independently measurable. This makes direct falsification impossible without an independent Ψ measurement.

---

### Ψ = C + F + I

**Assumption:** All variables normalized to [0, 1].

**Falsification conditions:**

1. **If Ψ > 3** → falsified (sum cannot exceed 3)
2. **If Ψ < 0** → falsified (sum cannot be negative)
3. **If Ψ decreases while C, F, I all increase** → falsified
4. **If Ψ increases while C, F, I all decrease** → falsified
5. **If any variable change produces opposite Ψ change** → falsified

**Observational test:** Measure C, F, I. Compute Ψ_predicted = C + F + I. Compare to Ψ_observed.

**Problem:** Same as above — Ψ not independently measurable.

---

### Ψ = min(C, F, I)

**Assumption:** All variables normalized to [0, 1].

**Falsification conditions:**

1. **If Ψ > min(C, F, I)** → falsified
2. **If Ψ < min(C, F, I)** → falsified
3. **If Ψ is not determined by the minimum component** → falsified
4. **If increasing a non-minimum component changes Ψ** → falsified

**Observational test:** Measure C, F, I. Compute Ψ_predicted = min(C, F, I). Compare to Ψ_observed.

**Problem:** Same as above — Ψ not independently measurable.

---

### Ψ = w₁C + w₂F + w₃I (weighted sum)

**Assumption:** All variables normalized to [0, 1]; w₁ + w₂ + w₃ = 1; wᵢ ≥ 0.

**Falsification conditions:**

1. **If Ψ > 1** → falsified
2. **If Ψ < 0** → falsified
3. **If the optimal weights are not constant across systems** → falsified (weights are not universal)
4. **If the best-fit weights are negative** → falsified (violates wᵢ ≥ 0)
5. **If the best-fit weights sum to != 1** → falsified (violates normalization)

**Observational test:** For multiple systems, measure C, F, I, and Ψ (if possible). Fit weights. Check if weights are constant, non-negative, and sum to 1.

**Problem:** Requires Ψ measurement and multiple systems.

---

### Ψ = C^α × F^β × I^γ (power law)

**Assumption:** All variables normalized to [0, 1]; α, β, γ are free parameters.

**Falsification conditions:**

1. **If the best-fit exponents are not constant across systems** → falsified
2. **If any exponent is negative** → falsified (violates monotonicity)
3. **If the power law does not fit better than simpler models** → falsified (parsimony)
4. **If the residuals show systematic structure** → falsified (model misspecification)

**Observational test:** For multiple systems, measure C, F, I, and Ψ. Fit exponents. Check constancy, sign, and residual structure.

**Problem:** Requires Ψ measurement, multiple systems, and parameter estimation.

---

### Ψ = nonlinear interaction (general)

**Assumption:** Ψ = f(C, F, I) for some unknown function f.

**Falsification conditions:**

1. **If f is not a function of C, F, I** → falsified (other variables matter more)
2. **If f is not deterministic** → falsified (stochastic component dominates)
3. **If f changes form across systems** → falsified (no universal equation)

**Observational test:** For many systems, measure C, F, I, and Ψ. Attempt to learn f. Check if f is consistent across systems.

**Problem:** Requires Ψ measurement, many systems, and nonparametric regression.

---

## Key Insight

**All candidate equations face the same fundamental problem:**

> **No measurement protocol for Ψ has yet been established within the project.**

Without a Ψ measurement protocol, no equation can be falsified. The equations are:

1. **Untestable** in their current form
2. **Requires** an operational definition of Ψ
3. **Requires** a measurement protocol for Ψ

**This is the real bottleneck.** The problem is not which equation is correct. The problem is:

> **No measurement protocol for Ψ has yet been established.**

---

## Recommendation

Before any equation can be tested, the project must:

1. **Define Ψ operationally** — what would a measurement of Ψ look like?
2. **Develop a Ψ measurement protocol** — how would you measure Ψ in practice?
3. **Validate the protocol** — does it produce consistent results?

Without this, the falsifiability audit is a catalog of untestable hypotheses.

---

## Artifact

`/home/student/sgp_core_v2/audits/RD_MATH_1_FALSIFIABILITY_AUDIT.md`
