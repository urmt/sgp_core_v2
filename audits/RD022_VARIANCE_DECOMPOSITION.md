# RD-022: Variance Decomposition

**Date:** 2026-06-06

Decompose variance in C into contributions from friction, estimator choice, and residual.

---

## Two-way ANOVA: C ~ friction + variant

Type II sum of squares, 60 runs × 8 variants = 480 obs, crossed design (6 friction × 8 variant, 10 obs per cell).

| Source | SS | df | MS | F | p | η² |
|--------|----|----|----|---|---|----|
| Friction (signal) | 1.2172 | 5 | 0.2434 | 361.3 | 5.96e-158 | 0.4029 |
| **Variant (estimator)** | **1.4892** | **7** | **0.2127** | **315.8** | **1.32e-172** | **0.4929** |
| Residual (within-cell) | 0.3146 | 467 | 0.000674 | — | — | 0.1042 |
| **Total** | 3.0211 | 479 | — | — | — | 1.0000 |

**Question 1: Is estimator a larger source of variation than friction?** **YES** (η²_var=0.493 vs η²_fric=0.403). The way you compute C explains more total variance in C than the physical parameter (friction) does.

**Question 2: Is the friction effect still strong?** **YES** (F=361, p<10⁻¹⁵⁸). Friction is highly significant; the dominant source of *physical* variance in C is friction.

**Question 3: How much of C is left unexplained by both?** **η²_res=0.10**. Only 10% of C variance is *within-cell* (within same friction × same estimator). This is the floor of intrinsic stochasticity.

---

## E0 baseline variance partition (within vs. between friction)

| Source | Variance | Fraction |
|--------|----------|----------|
| Between-friction (signal) | 0.002582 | 82.5% |
| Within-friction (residual) | 0.000547 | **17.5%** |
| **Total** | 0.003129 | 100.0% |

The fraction of E0 baseline variance that is *within-friction* — i.e., that **is** Residual(C) — is **17.5%**.

---

## Key question: Is estimator choice a larger source of variation than Residual(C)?

| Source of variance | Share |
|--------------------|-------|
| Estimator choice (η² from ANOVA) | **49.3%** |
| Residual(C) (within-friction share of E0) | **17.5%** |
| Friction (η² from ANOVA) | 40.3% |

**YES** — estimator choice explains 2.8× more variance than Residual(C).

---

## Interpretation

The variance decomposition reveals a non-obvious structure:

1. **Friction is the dominant *physical* source of C variance** (40% of total, F=361). Without friction control, C would not be a useful signal.

2. **Estimator choice is a *larger* source of C variance than friction** (49% vs 40%). This is striking: the measurement pipeline is doing as much work as the underlying physics.

3. **Residual(C) — the within-friction signal — is 17.5% of E0's total variance.** This is the smallest of the three components. It is precisely the component that carries predictive power for recovery (per RD-016, RD-019, RD-020, RD-021, and now RD-022).

4. **The 17.5% residual is *not* the bulk of C's variance, but it is the *robust* component.** The estimator variance is largely along a single common axis (PC1 = 95.5%, see director's summary). Within that axis, the rank-ordering of runs is preserved. The 17.5% residual is the part that varies *orthogonally* to estimator choice, and that is what predicts recovery.

This is the cleanest statistical signature of a "real" underlying construct: it is small in magnitude but it is **estimator-invariant**, and that is what makes it predictive.

---

## The trade-off

| Property | Estimator variance (49%) | Friction variance (40%) | Residual(C) (17.5% of E0) |
|----------|--------------------------|--------------------------|-----------------------------|
| Magnitude | Largest | Large | Small |
| Predicts recovery? | No | No (correlated) | **Yes** |
| Varies with physics? | No | Yes | Yes |
| Varies with pipeline? | Yes | No | No |

**The fact that Residual(C) is small but robust is the reason it survived three intervention null results.** It is the unique component of C that is not absorbed by friction or by the measurement choice.

---

## Cross-references

- `audits/RD022_ESTIMATOR_STABILITY.md` — per-variant C statistics
- `audits/RD022_PREDICTIVE_ROBUSTNESS.md` — predictive regressions
- `audits/RD022_DIRECTOR_SUMMARY.md` — final classification
