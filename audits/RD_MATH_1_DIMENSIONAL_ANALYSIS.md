# RD-MATH.1 — Dimensional Analysis

**Date:** 2026-06-15  
**Auditor:** OpenCode  
**Trigger:** Research Director directive — "Treat Ψ ≈ f(C,F,I) as if it were a physics equation."

---

## Assumptions

The following analysis treats the compass equation as a formal object, not as a claim about reality. The question is: **can these quantities be given mathematical properties?**

---

## Variable Properties

### C (Coherence)

| Property | Status | Evidence |
|----------|--------|----------|
| Bounded? | **Possibly** | C ≈ −MSE suggests C ∈ [−1, 0] if MSE ∈ [0, 1] |
| Normalizable? | **Yes** | MSE can be normalized to [0, 1] |
| Additive? | **No** | Coherence is not the sum of parts |
| Multiplicative? | **Possibly** | Coherence of independent subsystems might multiply |
| Order parameter? | **Yes** | C measures degree of organization (high = coherent, low = incoherent) |
| Dimensionless? | **Yes** | C ≈ −MSE is dimensionless |

**Candidate range:** 0 ≤ C ≤ 1 (after normalization)

---

### F (Fertility)

| Property | Status | Evidence |
|----------|--------|----------|
| Bounded? | **Unknown** | Empowerment is unbounded in continuous state spaces |
| Normalizable? | **Possibly** | Can be normalized relative to maximum possible empowerment |
| Additive? | **No** | Fertility of combined systems is not the sum of individual fertilities |
| Multiplicative? | **Possibly** | Fertility might compose multiplicatively across subsystems |
| Order parameter? | **Yes** | F measures capacity for future states (high = fertile, low = sterile) |
| Dimensionless? | **Depends** | Empowerment has units of information (bits) in discrete systems |

**Candidate range:** F ≥ 0 (non-negative, possibly unbounded)

---

### I (Interaction)

| Property | Status | Evidence |
|----------|--------|----------|
| Bounded? | **No** | Transfer Entropy is unbounded |
| Normalizable? | **Possibly** | Can be normalized relative to maximum possible transfer |
| Additive? | **No** | Interaction of multiple agents is not the sum of pairwise interactions |
| Multiplicative? | **No** | Interaction does not compose multiplicatively |
| Order parameter? | **Yes** | I measures degree of coupling (high = coupled, low = independent) |
| Dimensionless? | **Depends** | Transfer Entropy has units of information (bits) |

**Candidate range:** I ≥ 0 (non-negative, possibly unbounded)

---

### Ψ (Experience)

| Property | Status | Evidence |
|----------|--------|----------|
| Bounded? | **Unknown** | No measurement exists |
| Normalizable? | **Unknown** | No measurement exists |
| Additive? | **Unknown** | No measurement exists |
| Multiplicative? | **Unknown** | No measurement exists |
| Order parameter? | **Possibly** | Ψ might measure degree of experience (high = rich, low = minimal) |
| Dimensionless? | **Unknown** | No measurement exists |

**Candidate range:** Ψ undefined (no measurement protocol exists)

---

## Candidate Equations

### Ψ = C × F × I

| Property | Analysis |
|----------|----------|
| Dimensions | C (dimensionless) × F (bits) × I (bits) = bits² |
| Consistency | Dimensions mismatch if C is dimensionless and F, I are in bits |
| If all dimensionless | Possible: Ψ = C × F × I ∈ [0, 1] if all ∈ [0, 1] |
| If F, I unbounded | Ψ unbounded — violates boundedness intuition |

### Ψ = C + F + I

| Property | Analysis |
|----------|----------|
| Dimensions | C (dimensionless) + F (bits) + I (bits) |
| Consistency | Dimensions mismatch unless all dimensionless |
| If all dimensionless | Possible: Ψ ∈ [0, 3] if all ∈ [0, 1] |
| If F, I unbounded | Ψ unbounded |

### Ψ = min(C, F, I)

| Property | Analysis |
|----------|----------|
| Dimensions | min of dimensionless quantities is dimensionless |
| Consistency | Consistent if all dimensionless |
| If all dimensionless | Ψ ∈ [0, 1] — bounded |
| Interpretation | Ψ is limited by the weakest component |

### Ψ = weighted sum

| Property | Analysis |
|----------|----------|
| Dimensions | Weighted sum of dimensionless quantities is dimensionless |
| Consistency | Consistent if all dimensionless and weights dimensionless |
| If all dimensionless | Ψ ∈ [0, 1] if weights sum to 1 |
| Interpretation | Ψ is a weighted average of components |

### Ψ = nonlinear interaction

| Property | Analysis |
|----------|----------|
| Dimensions | Depends on the specific nonlinearity |
| Consistency | Must be checked case by case |
| If all dimensionless | Possible: any function f: [0,1]³ → [0,1] |
| Interpretation | Ψ depends on interactions between components |

---

## Key Insight

**The dimensional analysis reveals a fundamental problem:**

> **F and I have units (bits), while C is dimensionless.**

This means:

1. **Ψ = C × F × I** has dimensions of bits² — inconsistent
2. **Ψ = C + F + I** has mixed dimensions — inconsistent
3. **Ψ = min(C, F, I)** requires all dimensionless — requires normalization
4. **Ψ = weighted sum** requires all dimensionless — requires normalization
5. **Ψ = nonlinear interaction** requires specific form — undefined

**The only consistent option is to normalize all variables to [0, 1] and treat them as dimensionless order parameters.**

---

## Recommendation

Before any equation can be tested, the project must:

1. **Normalize C, F, I to [0, 1]** — define maximum and minimum values
2. **Choose a unit system** — either all dimensionless (normalized) or all in bits
3. **Define Ψ operationally** — without this, no equation can be tested

---

## Artifact

`/home/student/sgp_core_v2/audits/RD_MATH_1_DIMENSIONAL_ANALYSIS.md`
