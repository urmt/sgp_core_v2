# RD-7: Variance Decomposition — Results

## Primary Question

**How much of C is genuinely novel information?**

## Answer

**Very little.** C's unique contribution to recovery prediction ranges from 0.1% to 4.6% of total variance. It is substantially redundant with I_pred and MSE. When friction is included as a control, it dominates all metrics combined.

---

## Data Sources

| Dataset | n | Description |
|---------|---|-------------|
| t901 ensemble | 60 | Granular runs across 6 friction levels × 10 reps |
| benchmark_v1 | 8 | Cross-system comparison (synthetic + pilot systems) |

**Metrics:** C, I_pred (predictive information), C_σ (statistical complexity), MSE (multiscale entropy)
**Targets:** ΔC (dip), Restoration, τ_rec

---

## 1. Cross-Metric Correlations

### t901 Ensemble (n=60) — within-system

| | C | I_pred | C_σ | MSE |
|---|---|---|---|---|
| **C** | 1.000 | **0.670*** | **−0.457*** | **−0.892*** |
| **I_pred** | 0.670*** | 1.000 | −0.291* | −0.742*** |
| **C_σ** | −0.457*** | −0.291* | 1.000 | 0.608*** |
| **MSE** | −0.892*** | −0.742*** | 0.608*** | 1.000 |

**Key finding:** C is almost perfectly anti-correlated with MSE (r = −0.892) and strongly correlated with I_pred (r = 0.670). These metrics are measuring overlapping constructs.

### Benchmark Systems (n=8) — cross-system

| | C | I_pred | C_σ | MSE |
|---|---|---|---|---|
| **C** | 1.000 | 0.241 | −0.601 | −0.295 |
| **I_pred** | 0.241 | 1.000 | −0.702 | −0.812 |
| **C_σ** | −0.601 | −0.702 | 1.000 | 0.705 |
| **MSE** | −0.295 | −0.812 | 0.705 | 1.000 |

Cross-system correlations are weaker but show the same pattern: C overlaps with I_pred and opposes MSE/C_σ.

---

## 2. Metric → Recovery Prediction

| Metric | ΔC (dip) | Restoration | τ_rec |
|--------|----------|-------------|-------|
| C | **−0.323*** | 0.189 | −0.215 |
| I_pred | −0.262* | **0.262*** | −0.177 |
| C_σ | 0.045 | 0.205 | 0.004 |
| MSE | 0.248 | −0.128 | 0.235 |

C is the best single predictor of dip (r = −0.323, p < 0.05), but the effect is small.

---

## 3. Variance Decomposition (Partial R²)

### ΔC (dip) — Total R² = 0.127 (12.7%)

| Metric | Unique R² | % of R² |
|--------|-----------|---------|
| **C** | **0.046** | **36.0%** |
| I_pred | 0.009 | 7.2% |
| C_σ | 0.003 | 2.3% |
| MSE | 0.007 | 5.5% |
| Shared | 0.062 | 49.0% |
| Unexplained | 0.873 | — |

**C is the most novel metric for dip prediction**, but explains only 4.6% of total variance.

### Restoration — Total R² = 0.174 (17.4%)

| Metric | Unique R² | % of R² |
|--------|-----------|---------|
| C | 0.010 | 5.5% |
| I_pred | 0.027 | 15.6% |
| **C_σ** | **0.079** | **45.5%** |
| MSE | 0.000 | 0.0% |
| Shared | 0.058 | 33.4% |
| Unexplained | 0.826 | — |

**C_σ dominates restoration prediction.** C contributes almost nothing unique.

### τ_rec — Total R² = 0.090 (9.0%)

| Metric | Unique R² | % of R² |
|--------|-----------|---------|
| C | 0.001 | 1.3% |
| I_pred | 0.003 | 3.3% |
| **C_σ** | **0.036** | **40.5%** |
| **MSE** | **0.032** | **36.0%** |
| Shared | 0.017 | 18.9% |
| Unexplained | 0.910 | — |

**C is irrelevant for τ_rec** (unique R² = 0.1%). C_σ and MSE dominate.

---

## 4. C Alone vs C + Competitors

| Target | C alone | C + I_pred | C + C_σ | C + MSE | All 4 |
|--------|---------|-----------|---------|---------|-------|
| ΔC | 0.105 | 0.108 (+0.004) | 0.118 (+0.013) | 0.113 (+0.008) | 0.127 |
| Restoration | 0.036 | 0.069 (+0.033) | 0.144 (+0.108) | 0.044 (+0.008) | 0.174 |
| τ_rec | 0.046 | 0.048 (+0.002) | 0.058 (+0.011) | 0.055 (+0.009) | 0.090 |

Adding competitors to C always improves prediction. C alone is never sufficient.

---

## 5. Synergy Analysis

| Pair | ΔR² | Synergistic? |
|------|-----|-------------|
| C + I_pred | +0.004 | No |
| C + C_σ | +0.013 | **Yes** |
| C + MSE | +0.008 | **Yes** |
| I_pred + C_σ | +0.001 | No |
| I_pred + MSE | +0.006 | **Yes** |
| C_σ + MSE | +0.018 | **Yes** |

C + C_σ and C_σ + MSE show the strongest synergy. C + I_pred adds almost nothing (they're too correlated).

---

## 6. Friction Dominance

| Target | Metrics only | + Friction | Friction ΔR² |
|--------|-------------|-----------|-------------|
| ΔC | 0.127 | **0.447** | +0.320 (71.5%) |
| Restoration | 0.174 | **0.584** | +0.410 (70.2%) |
| τ_rec | 0.090 | **0.327** | +0.238 (72.6%) |

**Friction explains 70–73% of total explained variance.** All four information-theoretic metrics combined explain less than friction alone.

### C unique after controlling for friction:

| Target | C unique (no friction) | C unique (with friction) |
|--------|----------------------|------------------------|
| ΔC | 0.046 | **0.076** |
| Restoration | 0.010 | **0.227** |
| τ_rec | 0.001 | **0.149** |

When friction is held constant, C's unique contribution increases — but this is because friction was masking a within-friction relationship that RD-019/020 already showed was weak.

---

## 7. C Novelty Score

| Target | C unique R² | % of explained variance | Verdict |
|--------|-----------|----------------------|---------|
| ΔC (dip) | 0.046 | 36.0% | C is the best metric here |
| Restoration | 0.010 | 5.5% | C is irrelevant |
| τ_rec | 0.001 | 1.3% | C is irrelevant |

**C is genuinely novel only for dip prediction**, where it uniquely explains 36% of the (small) explained variance. For restoration and τ_rec, C_σ and MSE are far more informative.

---

## Bottom Line

| Question | Answer |
|----------|--------|
| How much variance does C uniquely explain? | **1–5%** across targets |
| Is C redundant with other metrics? | **Yes** — r = −0.89 with MSE, r = 0.67 with I_pred |
| Is C the best metric for anything? | **Yes, but only for dip** (36% of R²) |
| What dominates recovery prediction? | **Friction** (70%+ of R²) |
| What is C's genuine novelty? | **Marginal.** It adds ~1–5% unique information beyond competitors |

---

## Deliverables

- `audits/RD07_VARIANCE_DECOMPOSITION.md` — this report
- `audits/rd07_variance_decomposition.json` — statistical results
- `audits/rd07_fig1_correlations.png` — correlation heatmaps
- `audits/rd07_fig2_variance_partition.png` — variance partition stacked bars
- `audits/rd07_fig3_partial_r2.png` — partial R² grouped bars
- `audits/rd07_fig4_novelty_gauge.png` — C novelty gauge
- `audits/rd07_fig5_friction_dominance.png` — friction dominance chart
