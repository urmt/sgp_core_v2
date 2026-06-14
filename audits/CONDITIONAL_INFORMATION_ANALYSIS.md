# Conditional Information Analysis

**Question**: How much predictive information does C contribute after conditioning on friction? And vice versa?

---

## 1. Model Comparison: R² and AIC

Full-sample comparison (n = 60, all variables standardized):

### Target: ΔC (dip depth)

| Model | R² | ΔR² vs Null | AIC | BIC |
|-------|:---:|:-----------:|:---:|:---:|
| Null (mean only) | 0.0000 | — | 2.0 | 4.1 |
| Friction only | 0.2990 | +0.2990 | 153.0 | 157.1 |
| C only | 0.1046 | +0.1046 | 167.6 | 171.8 |
| C + Friction (additive) | 0.4282 | +0.4282 | 142.7 | 149.0 |
| C + Friction + C×Friction (full core) | **0.5226** | +0.5226 | 133.9 | 142.3 |
| Mobility proxies only (4-predictor) | 0.3334 | +0.3334 | 155.9 | 166.4 |
| Full core + all mobility | 0.5513 | +0.5513 | 138.2 | 154.9 |

### Target: Restoration (C_final/C_pre)

| Model | R² | ΔR² vs Null | AIC | BIC |
|-------|:---:|:-----------:|:---:|:---:|
| Null (mean only) | 0.0000 | — | 2.0 | 4.1 |
| Friction only | 0.2290 | +0.2290 | 158.7 | 162.9 |
| C only | 0.0357 | +0.0357 | 172.1 | 176.3 |
| C + Friction (additive) | 0.5004 | +0.5004 | 134.6 | 140.9 |
| C + Friction + C×Friction (full core) | **0.5647** | +0.5647 | 128.4 | 136.7 |
| Mobility proxies only (4-predictor) | 0.1700 | +0.1700 | 169.1 | 179.6 |
| Full core + all mobility | 0.5915 | +0.5915 | 132.6 | 149.3 |

### Target: τ_rec (recovery time)

| Model | R² | ΔR² vs Null | AIC | BIC |
|-------|:---:|:-----------:|:---:|:---:|
| Null (mean only) | 0.0000 | — | 2.0 | 4.1 |
| Friction only | 0.1790 | +0.1790 | 162.4 | 166.6 |
| C only | 0.0462 | +0.0462 | 171.4 | 175.6 |
| C + Friction (additive) | 0.3053 | +0.3053 | 154.4 | 160.7 |
| C + Friction + C×Friction (full core) | **0.3450** | +0.3450 | 152.9 | 161.3 |
| Mobility proxies only (4-predictor) | 0.1858 | +0.1858 | 167.9 | 178.4 |
| Full core + all mobility | 0.3868 | +0.3868 | 156.9 | 173.7 |

---

## 2. Conditional ΔR²: What Does Each Predictor Add?

### ΔR²: C given friction

| Target | Friction R² | +C (additive) R² | ΔR² (C | friction) | +C×Friction R² | ΔR² (C+Int | friction) |
|--------|:-----------:|:----------------:|:------------------------:|:---------------:|:---------------------------:|
| ΔC | 0.2990 | 0.4282 | **+0.1292** | 0.5226 | **+0.2236** |
| Restoration | 0.2290 | 0.5004 | **+0.2714** | 0.5647 | **+0.3357** |
| τ_rec | 0.1790 | 0.3053 | **+0.1263** | 0.3450 | **+0.1660** |

**Interpretation**: C adds predictive information beyond friction for all three targets. The gain is largest for restoration (+0.271 to +0.336) and smallest for τ_rec (+0.126 to +0.166). This is **not** consistent with C being a pure friction proxy — if it were, adding C should not improve prediction.

### ΔR²: Friction given C

| Target | C R² | +Friction (additive) R² | ΔR² (Friction | C) | +C×Friction R² | ΔR² (Fric+Int | C) |
|--------|:----:|:-----------------------:|:-----------------------------:|:---------------:|:------------------------------:|
| ΔC | 0.1046 | 0.4282 | **+0.3236** | 0.5226 | **+0.4181** |
| Restoration | 0.0357 | 0.5004 | **+0.4647** | 0.5647 | **+0.5290** |
| τ_rec | 0.0462 | 0.3053 | **+0.2591** | 0.3450 | **+0.2987** |

**Interpretation**: Friction contributes more predictive information than C does, for all targets. The asymmetry is 2–3×: friction adds 2–4× more R² than C adds, depending on target. This is consistent with friction being the dominant predictor.

---

## 3. Permutation Importance

For the full core model (C + friction + C×friction), 1000 permutations of each predictor:

| Target | Baseline R² | Permute C | Permute Friction | Permute Interaction |
|--------|:-----------:|:----------:|:----------------:|:-------------------:|
| ΔC | 0.5226 | R² = 0.4153 | R² = 0.1799 | R² = 0.4380 |
| | | **Frac. Loss = 0.205** | **Frac. Loss = 0.656** | **Frac. Loss = 0.162** |
| Restoration | 0.5647 | R² = 0.3185 | R² = 0.0850 | R² = 0.5092 |
| | | **Frac. Loss = 0.436** | **Frac. Loss = 0.849** | **Frac. Loss = 0.098** |
| τ_rec | 0.3450 | R² = 0.2392 | R² = 0.0834 | R² = 0.3178 |
| | | **Frac. Loss = 0.307** | **Frac. Loss = 0.758** | **Frac. Loss = 0.079** |

**Interpretation**:
- **Friction is the most important predictor**: permuting it destroys 66–85% of model R².
- **C contributes meaningful unique information**: permuting it loses 21–44% of R². This is not redundant with friction.
- **The interaction term contributes least**: permuting it loses 8–16% of R². The interaction is a real but modest contributor.

---

## 4. Leave-One-Covariate-Out (LOCO)

R² drop when removing each term from the full core model:

| Term Removed | ΔC (full R² = 0.5226) | Restoration (full R² = 0.5647) | τ_rec (full R² = 0.3450) |
|-------------|:---------------------:|:-----------------------------:|:------------------------:|
| Leave out C (keep Fr + Int) | R² = 0.4047, **drop = −0.1179** | R² = 0.3071, **drop = −0.2576** | R² = 0.2260, **drop = −0.1190** |
| Leave out Friction (keep C + Int) | R² = 0.1649, **drop = −0.3578** | R² = 0.0681, **drop = −0.4966** | R² = 0.0670, **drop = −0.2779** |
| Leave out Interaction (keep C + Fr, i.e. additive) | R² = 0.4282, **drop = −0.0945** | R² = 0.5004, **drop = −0.0643** | R² = 0.3053, **drop = −0.0397** |

**Interpretation**: Every term contributes unique predictive information. No term is fully redundant. The interaction drop (0.04–0.09) is smaller than the friction drop (0.28–0.50) but consistently positive.

---

## 5. Mobility LOCO: Does Mobility Add Beyond the Full Core Model?

Full core (C + Fr + C×Fr) + all 4 mobility proxies vs removing each proxy:

| Target | Full Core R² | +All Mobility R² | Mobility ΔR² | Drop MSD | Drop RMS_Vel | Drop Turnover | Drop Packing |
|--------|:-----------:|:----------------:|:------------:|:--------:|:-----------:|:------------:|:-----------:|
| ΔC | 0.5226 | 0.5513 | +0.0287 | −0.0033 | −0.0051 | −0.0033 | −0.0097 |
| Restoration | 0.5647 | 0.5915 | +0.0268 | −0.0001 | −0.0071 | −0.0151 | −0.0002 |
| τ_rec | 0.3450 | 0.3868 | +0.0418 | −0.0198 | −0.0282 | −0.0232 | −0.0235 |

**Interpretation**: Mobility proxies add at most 0.042 R² beyond the full core model. Individual proxies add almost nothing (ΔR² ≤ 0.03). This is the quantitative evidence that mobility proxies do **not** predict recovery beyond what C and friction already capture.

---

## 6. Key Findings

1. **C contains unique information beyond friction.** ΔR²(C | friction) = +0.13 to +0.27 across targets. Not redundant.

2. **Friction contains more information than C.** ΔR²(friction | C) = +0.26 to +0.46. Friction is the dominant predictor by ~2–4×.

3. **The interaction term is real but modest.** It adds ΔR² = 0.04–0.09 over the additive model. Permutation loss: 8–16%.

4. **Mobility proxies add minimal unique information.** ΔR² ≤ 0.042 beyond the full core model. No single mobility proxy contributes meaningfully (ΔR² ≤ 0.03).

5. **The asymmetry in conditional information** (friction contributes more than C) is consistent with C being partly but not entirely a friction proxy. C carries signal that friction + mobility do not.

6. **Answer to the primary question**: Yes, C contains information that friction and mobility do not. The amount is moderate (ΔR² ~0.13–0.27 for C given friction) compared to friction's contribution (ΔR² ~0.26–0.46 for friction given C), but it is not zero and not explained by available mobility measures.
