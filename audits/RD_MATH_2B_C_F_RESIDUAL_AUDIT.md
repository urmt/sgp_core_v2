# RD-MATH.2B — C/F Residual Audit

**Date:** 2026-06-15  
**Auditor:** OpenCode  
**Trigger:** Research Director directive  
**Status:** COMPLETE

---

## Method

- 30 granular simulations (6 friction × 5 replicates)
- F proxies: Transfer Entropy (TE), Empowerment (E), Novelty Rate (NR = C)
- Regression: F = αC + β
- Residual_F = F - E[F|C]
- Test: does Residual_F predict novelty, stability, adaptation, persistence?

---

## Result 1: F_clean = (TE + E + NR) / 3

```
α = 0.3333, β = 2.4945
R² = 1.0000 (perfect linear)
Residual_F: mean = 0.0000, std = 0.0000
```

**F is perfectly linearly dependent on C.** Residual has zero variance.

### Why?

F_NR = max(0, C) = C (since C > 0 always).

F_clean = (TE + E + C) / 3

If TE and E are also functions of C, then F_clean is a linear function of C by construction.

---

## Result 2: F_minimal = (TE + E) / 2 (no entropy proxy)

```
α = 0.0000, β = 3.7417
R² = 0.0000 (no correlation)
Residual_minimal: std = 0.000000 (constant!)
```

**TE and E are constant across all friction levels.** They don't vary with system dynamics.

### Interpretation

TE and E are measuring something about the binning scheme or metric implementation, not the system dynamics.

---

## Result 3: Residual prediction

| Outcome | Residual_R² | C_R² | F_clean_R² |
|---------|-------------|-------|------------|
| novelty | 0.0003 | 0.4103 | 0.4103 |
| stability | 0.0018 | 0.4790 | 0.4790 |
| adaptation | 0.0018 | 0.2836 | 0.2836 |
| persistence | 0.0277 | 0.1698 | 0.1698 |

**Residual_F has no predictive power.** C and F_clean predict identically (because F_clean IS a linear function of C).

---

## Interpretation

### What this means

**With current F proxies, F is not distinguishable from C.**

- F_NR = C by construction
- F_TE and F_E are constant (don't vary with friction)
- F_clean = (TE + E + C) / 3 is perfectly linear in C

**The compass equation Ψ ≈ f(C, F, I) collapses to Ψ ≈ f(C, I).**

### What this does NOT mean

**This does NOT mean F is reducible to C in general.**

It means:

1. The current F proxies are bad (they measure the wrong thing)
2. OR the granular system doesn't exhibit fertility variation
3. OR fertility genuinely tracks coherence in this domain

### The proper conclusion

**The F proxies need replacement.** The current proxies either:
- Reference C directly (NR)
- Are constant across friction levels (TE, E)
- Do not capture the intended construct

### Open question

Can F be measured independently of C using better proxies?

The Research Director's question stands: **Can the compass variables be operationally separated?**

With current metrics: **No.**

---

## Recommended Next Steps

1. **Find F proxies that actually vary with friction** (TE and E don't)
2. **Remove all C references from F** (NR is out)
3. **Test whether ANY proxy captures fertility independent of coherence**
4. **If no independent F proxy exists, the compass reduces to Ψ ≈ f(C, I)**

---

## Artifact

- Results: `audits/RD_MATH_2B/cf_residual_results.json`
- Script: `audits/RD_MATH_2B/run_cf_residual.py`
