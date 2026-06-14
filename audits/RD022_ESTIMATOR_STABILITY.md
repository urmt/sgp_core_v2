# RD-022: Estimator Stability

**Date:** 2026-06-06
**Companion to:** RD-022 master table (`audits/RD022_master_table.json`)

Per-variant C and Residual(C) statistics across 60 runs (6 friction × 10 reps).
Reference is E0 (baseline: n_bins=10, window=75, step=25).

---

## Per-variant statistics

| Variant | Label | mean(C) | sd(C) | r(C, E0_C) | ρ(C, E0_C) | r(R, E0_R) | ρ(R, E0_R) |
|---------|-------|---------|-------|------------|------------|------------|------------|
| E0 | Baseline (n_bins=10, window=75) | 0.4660 | 0.0559 | +1.000 | +1.000 | +1.000 | +1.000 |
| E1 | Half window (37) | 0.5113 | 0.0594 | +0.980 | +0.982 | +0.890 | +0.874 |
| E2 | Double window (150) | 0.4701 | 0.0458 | +0.983 | +0.986 | +0.933 | +0.926 |
| E3 | Half bins (5) | 0.3735 | 0.0674 | +0.930 | +0.929 | +0.684 | +0.651 |
| E4 | Double bins (20) | 0.5854 | 0.0494 | +0.951 | +0.952 | +0.784 | +0.772 |
| E5 | Shifted bin edges | 0.4627 | 0.0627 | +0.945 | +0.950 | +0.698 | +0.644 |
| E6 | Bootstrap C (50 resamples) | 0.4728 | 0.0547 | +1.000 | +1.000 | +1.000 | +1.000 |
| E7 | Leave-one-bin-out | 0.4472 | 0.0575 | +0.999 | +0.999 | +0.997 | +0.997 |

**Notes:**
- E0 and E6 are *expected* to have r=1.000: E6 (bootstrap with n_boot=50 → ∞) asymptotes to E0. E7 (LOO) is averaging over leave-one-out variants and is also expected to be very close to E0 (r=0.999).
- The strongest perturbations to level come from E3 (5 bins, low C) and E4 (20 bins, high C). Both still correlate ≥0.93 with E0.
- The Residual(C) correlation is generally lower than the raw C correlation, because Residual(C) subtracts the friction-level mean which is the dominant variance component.

---

## Stability ranking (most stable first, by |r(C, E0) − 1|)

1. **E0** — Baseline (n_bins=10, window=75): r=+1.000, ρ=+1.000, mean(C)=0.4660, sd(C)=0.0559
2. **E6** — Bootstrap C (50 resamples): r=+1.000, ρ=+1.000, mean(C)=0.4728, sd(C)=0.0547
3. **E7** — Leave-one-bin-out: r=+0.999, ρ=+0.999, mean(C)=0.4472, sd(C)=0.0575
4. **E2** — Double window (150): r=+0.983, ρ=+0.986, mean(C)=0.4701, sd(C)=0.0458
5. **E1** — Half window (37): r=+0.980, ρ=+0.982, mean(C)=0.5113, sd(C)=0.0594
6. **E4** — Double bins (20): r=+0.951, ρ=+0.952, mean(C)=0.5854, sd(C)=0.0494
7. **E5** — Shifted bin edges: r=+0.945, ρ=+0.950, mean(C)=0.4627, sd(C)=0.0627
8. **E3** — Half bins (5): r=+0.930, ρ=+0.929, mean(C)=0.3735, sd(C)=0.0674

**Stability interpretation:** Even the *least* stable variant (E3) has r=0.93 with E0. All 8 variants are highly stable on rank ordering. Differences in mean C are real but they are monotonic transformations, not measurement dissociations.

---

## Spread of mean(C) across variants

- min mean(C): **0.3735** (variant E3, half bins)
- max mean(C): **0.5854** (variant E4, double bins)
- range: **0.2119**
- relative range: **44.7% of grand mean (0.4735)**

If the range of mean(C) is large, C is **estimator-sensitive on level**. If small, C is **estimator-robust on level**.

The 44.7% relative range is large. C is **highly estimator-sensitive on level** but **highly robust on rank ordering**. This is the central tension of the audit, and the variance decomposition (deliverable 3) and PCA quantify it.

---

## Cross-references

- `audits/RD022_PREDICTIVE_ROBUSTNESS.md` — do these stability differences affect the predictive signal?
- `audits/RD022_VARIANCE_DECOMPOSITION.md` — is estimator variance a large share of total C variance?
- `audits/RD022_DIRECTOR_SUMMARY.md` — final classification (M-A/M-B/M-C/M-D)
