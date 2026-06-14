# RD-10B.0B: Identity Audit — Report

## Status: COMPLETE

---

## Question

> **What observations would justify saying that two descriptions refer to the same underlying process?**

---

## Standing Rule Applied

> **Whenever something looks fundamental, ask what makes it possible.**

Identity across representations now looks fundamental.
So the next question is: **What makes identity possible?**

---

## Design

1. Generate 6 different worlds (no motif vocabulary)
2. For each pair of worlds, apply 5 identity criteria:
   - Predictive identity
   - Intervention identity
   - Counterfactual identity
   - Information-theoretic identity
   - Causal-structure identity
3. Ask: do criteria agree on which pairs are "the same"?

---

## Results

### Mean Score per Criterion

| Criterion | Mean | Std |
|-----------|------|-----|
| information | 0.979 | 0.014 |
| causal | 0.988 | 0.012 |
| intervention | 0.762 | 0.165 |
| predictive | 0.343 | 0.188 |
| counterfactual | 0.258 | 0.179 |

### Criterion Correlations

| Pair | Correlation |
|------|-------------|
| information ↔ causal | -0.252 |
| predictive ↔ causal | 0.012 |
| intervention ↔ information | 0.001 |
| predictive ↔ intervention | -0.352 |
| predictive ↔ counterfactual | -0.413 |

**Mean criterion correlation: -0.043** — criteria are essentially uncorrelated.

### Classification Agreement (threshold=0.5)

| Criterion | Same | Different |
|-----------|------|-----------|
| information | 15 | 0 |
| causal | 15 | 0 |
| intervention | 14 | 1 |
| predictive | 3 | 12 |
| counterfactual | 3 | 12 |

### Cross-Criterion Classification Agreement

| Pair | Agreement |
|------|-----------|
| information ↔ causal | 1.000 |
| intervention ↔ information | 0.933 |
| intervention ↔ causal | 0.933 |
| predictive ↔ counterfactual | 0.600 |
| predictive ↔ intervention | 0.267 |
| predictive ↔ information | 0.200 |
| predictive ↔ causal | 0.200 |
| counterfactual ↔ information | 0.200 |
| counterfactual ↔ causal | 0.200 |
| counterfactual ↔ intervention | 0.267 |

---

## Critical Finding

### The Identity Criteria Disagree

Different criteria classify different world pairs as "the same."

- **Information and causal** classify ALL pairs as "same"
- **Predictive and counterfactual** classify most pairs as "different"
- **Intervention** classifies most pairs as "same"

### What This Means

> **"Same world" is itself representation-dependent.**

Which criterion you use determines which worlds count as "the same."

This is not a failure of the criteria. It is a discovery about the structure of identity:

- Information-theoretic identity says: all worlds are similar
- Predictive identity says: most worlds are different
- Causal identity says: all worlds are similar
- Counterfactual identity says: most worlds are different

There is no unified notion of "same world."

---

## The Deeper Finding

The program has been assuming:

```
world → representation A
world → representation B
```

And asking: "When do A and B represent the same world?"

But the answer depends on what you mean by "same."

And different notions of "same" disagree.

This means:

> **The world-representation mapping is not a fact about the world.**
> **It is a fact about the criterion you use to evaluate it.**

---

## Implications

### For RD-10B

1. **Detector validation requires choosing an identity criterion** — but criteria disagree
2. **Motif independence is identity-dependent** — which motifs are "the same" depends on what "same" means
3. **The emergence-first approach must specify the identity criterion** — "what motifs appear?" is meaningless without "in what sense are these the same world?"

### For the Program

The deepest assumption — that there is a fact of the matter about which representations describe the same world — is now in question.

This is not skepticism. It is a methodological discovery:

> **Identity across representations is not a primitive notion.**
> **It must be specified, not assumed.**

---

## The Standing Rule (Confirmed)

> **What makes two representations representations of the same thing?**

The answer: **it depends on what you mean by "same."**

And different meanings disagree.

---

## Next Steps

1. **Map the identity landscape** — for each criterion, what does "same world" mean?
2. **Search for criterion-invariant properties** — what, if anything, survives all notions of identity?
3. **Test across more worlds** — is the disagreement robust?

---

## Files

- `audits/rd10b0b_identity_audit.py` — experiment code
- `audits/rd10b0b_results.json` — results
- `audits/RD10B0B_IDENTITY_AUDIT.md` — this report
