# RD-10B.0C: Identity Purpose Audit — Report

## Status: COMPLETE

---

## Question

> **What role is identity serving?**
> **Why do we need a notion of "same" in the first place?**

---

## Standing Rule Applied

> **Whenever something appears fundamental, first determine what work it is doing.**

---

## Design

For each identity criterion:
1. What task was it invented to support?
2. What failures does it prevent?
3. What transformations does it preserve?
4. When does it outperform the others?

---

## Results

### Structure by Purpose

| Criterion | Purpose | Structure (mean) | Structure (std) |
|-----------|---------|------------------|-----------------|
| information | compression | 0.991 | 0.004 |
| causal | causal_reasoning | 0.918 | 0.030 |
| intervention | intervention | 0.487 | 0.179 |
| counterfactual | explanation | 0.331 | 0.126 |
| predictive | prediction | 0.140 | 0.232 |

### Transformation Analysis

| Pair | Correlation |
|------|-------------|
| predictive ↔ causal | 0.910 |
| intervention ↔ information | 0.817 |
| predictive ↔ information | 0.610 |
| information ↔ causal | 0.623 |
| counterfactual ↔ causal | 0.548 |
| intervention ↔ counterfactual | 0.527 |
| predictive ↔ intervention | 0.446 |
| counterfactual ↔ information | 0.393 |
| predictive ↔ counterfactual | 0.273 |

---

## Critical Finding

### The Criteria Are Not Competing Definitions

They are tools designed for different tasks:

| Criterion | Purpose | What It Preserves |
|-----------|---------|-------------------|
| predictive | prediction | temporal structure for forecasting |
| intervention | manipulation | response structure for control |
| counterfactual | explanation | structure for reasoning about alternatives |
| information | compression | statistical structure for storage |
| causal | causal reasoning | dependency structure for inference |

### Their Disagreement Reflects Purpose, Not Failure

The question is not: "Which criterion is correct?"
The question is: "What task are you trying to accomplish?"

### Closely Related Tasks

- **prediction ↔ causal reasoning** (r=0.910) — these tasks require similar structure
- **intervention ↔ compression** (r=0.817) — these tasks require similar structure

---

## The Deeper Lesson

The program has repeatedly learned:

> **Whenever something appears fundamental, first determine what work it is doing.**

Identity criteria are not competing definitions of "same world."
They are tools designed for different purposes.

Their disagreement is not a crisis of identity.
It is a reflection of the diversity of purposes.

---

## Implications

### For RD-10B

1. **Identity is purpose-dependent** — different tasks require different notions of "same"
2. **Criterion choice is task choice** — choosing a criterion means choosing a task
3. **The emergence-first approach must specify the task** — "what motifs appear?" is meaningless without "what are you trying to accomplish?"

### For the Program

The deepest assumption — that there is a fact of the matter about which representations describe the same world — is now qualified:

> **"Same world" is relative to a purpose.**
> **Different purposes require different identities.**
> **This is not skepticism. It is a methodological discovery.**

---

## The Standing Rule (Confirmed)

> **Whenever something appears fundamental, first determine what work it is doing.**

Identity criteria are doing different work.
Their disagreement reflects the diversity of purposes.

---

## Next Steps

1. **Map the purpose landscape** — for each task, which criterion is appropriate?
2. **Search for purpose-invariant properties** — what, if anything, survives all purposes?
3. **Test across more tasks** — is the purpose-structure relationship robust?

---

## Files

- `audits/rd10b0c_identity_purpose.py` — experiment code
- `audits/rd10b0c_results.json` — results
- `audits/RD10B0C_IDENTITY_PURPOSE.md` — this report
