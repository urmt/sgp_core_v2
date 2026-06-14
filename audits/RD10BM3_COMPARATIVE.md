# RD-10B.M3: Comparative Structure Audit — Report

## Status: COMPLETE

---

## Question

> Does explanatory power scale with comparison or with translation?

---

## Hypotheses Tested

| Hypothesis | Statement |
|------------|-----------|
| H1 | Explanation scales with translation |
| H2 | Explanation scales with comparison |
| H3 | Translation only becomes possible after explanatory gains from comparison |

---

## Results

| Hypothesis | Result |
|------------|--------|
| H1 | SUPPORTED (87.5% vs 72.7%) |
| H2 | SUPPORTED (82.4% vs 50.0%) |
| H3 | SUPPORTED (8 vs 0) |

---

## Key Finding: H3

Translation never appears without prior comparison gains.

Every audit where translation is present (8 audits) had earlier audits where comparison was present but translation was absent.

**Translation arrives late. Comparison appears first.**

---

## Interpretation

### What This Shows

1. Both comparison and translation are associated with explanatory gains
2. Translation has a slightly higher association (87.5% vs 82.4%)
3. But translation never appears without prior comparison

### The Order

```
Descriptions → Comparison → Explanation → Translation
```

NOT:
```
Descriptions → Comparison → Translation → Explanation
```

Translation is a downstream effect of comparison, not the source of explanation.

### The Strongest Conclusion

> Explanatory power emerges from structured comparison between descriptions.

Translation may emerge later, but it is not the source. Comparison is.

---

## Implications

### For the Program

The fundamental operation is not distinction, recursion, or translation. It is comparison — maintaining multiple descriptions simultaneously and observing where they differ.

### The Strongest Survivor

> Whenever the program becomes trapped inside a single description, progress stalls. Whenever a second description is introduced, hidden structure becomes visible.

This has survived nearly every collapse in RD-10B.

---

## Files

- `audits/rd10bm3_comparative.py` — experiment code
- `audits/rd10bm3_results.json` — results
- `audits/RD10BM3_COMPARATIVE.md` — this report
