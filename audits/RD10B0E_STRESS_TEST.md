# RD-10B.0E: Stress-Test Audit — Report

## Status: COMPLETE

---

## Question

> **Under what conditions is a criterion informative, uninformative, misleading, or trivial?**

---

## Standing Rule Applied

> **Whenever a pattern appears, ask whether it belongs to:**
> **the world, the representation, the detector, the question,**
> **the observer, or the evaluation protocol.**

---

## Design

Construct worlds designed to stress-test each criterion:
- **chaotic**: high coupling, high nonlinearity → breaks prediction
- **uniform**: identical agents → breaks intervention
- **deterministic**: low noise → breaks counterfactuals
- **trivial**: constant state → breaks information
- **random**: uncorrelated dynamics → breaks causation
- **normal**: baseline comparison

---

## Results

### Criterion Informativeness

| Criterion | Informativeness | Domain |
|-----------|-----------------|--------|
| predictive | 3/6 (50%) | systems with temporal autocorrelation |
| intervention | 4/6 (67%) | systems with response heterogeneity |
| counterfactual | 3/6 (50%) | systems with multiple possible futures |
| information | 4/6 (67%) | systems with statistical complexity |
| causal | 3/6 (50%) | systems with structured dependencies |

### Disagreement Analysis

| World | Informative | Trivial |
|-------|-------------|---------|
| trivial | predictive | intervention, counterfactual, information, causal |
| random | counterfactual, information | predictive, intervention, causal |
| deterministic | predictive, intervention, causal | counterfactual, information |
| uniform | intervention, information, causal | predictive, counterfactual |
| normal | intervention, counterfactual, information | predictive, causal |

---

## Critical Finding

### No Criterion Is Always Informative

Each criterion has a domain where it is informative and a domain where it is trivial:

- **predictive**: informative when system has temporal structure
- **intervention**: informative when agents respond differently
- **counterfactual**: informative when system has multiple possible futures
- **information**: informative when system has statistical complexity
- **causal**: informative when dependencies are structured

### The Disagreement Is the Discovery

The criteria disagree because they measure different things in different worlds.

This is not a crisis of identity. It is a reflection of the diversity of phenomena.

---

## The Deeper Lesson

The question is not: "Which criterion is correct?"

The question is: **"Under what conditions is each criterion informative?"**

That question has a clearer answer than "when does it fail?"

Because a criterion returning "trivial" in a trivial world is not failing — it is succeeding.

---

## Implications

### For RD-10B

1. **Each criterion has a defined domain of applicability** — use it within that domain
2. **Criterion choice is world-dependent** — different worlds require different criteria
3. **The emergence-first approach must specify the world type** — "what motifs appear?" depends on what kind of world you are studying

### For the Program

The deepest insights come from mapping domain boundaries, not from identifying foundations.

When a criterion becomes trivial, it reveals:
- What the criterion measures
- What the world lacks
- What alternative criterion might be informative

---

## Files

- `audits/rd10b0e_stress_test.py` — experiment code
- `audits/rd10b0e_results.json` — results
- `audits/RD10B0E_STRESS_TEST.md` — this report
