# Threshold vs Interaction Model Test

**Competing hypotheses**:
1. Continuous interaction (C × friction)
2. Friction threshold (binary regime change)
3. Piecewise model (different C slopes per regime)
4. Interaction model (current best)

---

## Method

For each target, perform grid search over friction thresholds (0.10, 0.20, 0.40, 0.60). At each threshold:
- **Simple threshold**: binary dummy (low/high friction), no C
- **Piecewise C**: C + threshold dummy + C×threshold dummy (allows different C slopes above/below threshold)

Compare to additive and interaction models.

---

## 1. Threshold Grid Search

### ΔC (dip depth)

| Threshold | Simple Dummy R² | Piecewise C×Dummy R² | Best model at threshold |
|:---------:|:---------------:|:--------------------:|------------------------|
| 0.10 | — | 0.227 | Piecewise C×dummy |
| 0.20 | 0.321 | 0.411 | Piecewise C×dummy |
| **0.40** | — | **0.413** | Piecewise C×dummy ← best |
| 0.60 | — | 0.269 | Piecewise C×dummy |

### Restoration

| Threshold | Simple Dummy R² | Piecewise C×Dummy R² | Best model at threshold |
|:---------:|:---------------:|:--------------------:|------------------------|
| 0.10 | — | 0.227 | Piecewise C×dummy |
| **0.20** | 0.219 | **0.346** | Piecewise C×dummy ← best |
| 0.40 | — | 0.295 | Piecewise C×dummy |
| 0.60 | — | 0.323 | Piecewise C×dummy |

### τ_rec (recovery time)

| Threshold | Simple Dummy R² | Piecewise C×Dummy R² | Best model at threshold |
|:---------:|:---------------:|:--------------------:|------------------------|
| 0.10 | — | 0.076 | Piecewise C×dummy |
| 0.20 | — | 0.201 | Piecewise C×dummy |
| **0.40** | 0.170 | **0.340** | Piecewise C×dummy ← best |
| 0.60 | — | 0.234 | Piecewise C×dummy |

---

## 2. Model Comparison (Full Sample)

### ΔC

| Model | R² | AIC | BIC | k |
|-------|:---:|:---:|:---:|:-:|
| **Interaction (C+Fr+C×Fr)** | **0.523** | **133.9** | **142.3** | 4 |
| Piecewise C×regime (th=0.40) | 0.428 | 144.7 | 153.1 | 4 |
| Additive (C+Fr) | 0.428 | 142.7 | 149.0 | 3 |
| Threshold=0.40 (piecewise C) | 0.413 | 146.3 | 154.7 | 4 |
| Simple threshold=0.20 (binary) | 0.321 | — | — | 2 |
| Friction (linear) | 0.299 | 153.0 | 157.1 | 2 |
| C (linear) | 0.105 | 167.6 | 171.8 | 2 |
| Null | 0.000 | — | — | 1 |

**Interaction beats best threshold by ΔR² = +0.109**

### Restoration

| Model | R² | AIC | BIC | k |
|-------|:---:|:---:|:---:|:-:|
| **Interaction (C+Fr+C×Fr)** | **0.565** | **128.4** | **136.7** | 4 |
| Piecewise C×regime (th=0.20) | 0.534 | 132.4 | 140.8 | 4 |
| Additive (C+Fr) | 0.500 | 134.6 | 140.9 | 3 |
| Threshold=0.20 (piecewise C) | 0.346 | 152.8 | 161.2 | 4 |
| Friction (linear) | 0.229 | 158.7 | 162.9 | 2 |
| Simple threshold=0.20 (binary) | 0.219 | — | — | 2 |
| C (linear) | 0.036 | 172.1 | 176.3 | 2 |
| Null | 0.000 | — | — | 1 |

**Interaction beats best threshold by ΔR² = +0.219**

### τ_rec

| Model | R² | AIC | BIC | k |
|-------|:---:|:---:|:---:|:-:|
| **Interaction (C+Fr+C×Fr)** | **0.345** | **152.9** | **161.3** | 4 |
| Threshold=0.40 (piecewise C) | 0.340 | 153.3 | 161.7 | 4 |
| Piecewise C×regime (th=0.40) | 0.319 | 155.2 | 163.6 | 4 |
| Additive (C+Fr) | 0.305 | 154.4 | 160.7 | 3 |
| Friction (linear) | 0.179 | 162.4 | 166.6 | 2 |
| Simple threshold=0.40 (binary) | 0.171 | — | — | 2 |
| C (linear) | 0.046 | 171.4 | 175.6 | 2 |
| Null | 0.000 | — | — | 1 |

**Interaction beats best threshold by ΔR² = +0.005 (effectively tied)**

---

## 3. Cross-Validation Comparison (k=5, 100× repeated)

| Model | ΔC mean R² (sd) | Restoration mean R² (sd) |
|-------|:--------------:|:-----------------------:|
| Interaction | **0.322** (0.364) | **0.364** (0.352) |
| Additive | 0.216 (0.389) | 0.308 (0.398) |
| Threshold (optimal) | −0.940 (1.319) | −0.291 (0.390) |

**Threshold models perform poorly in CV** — negative mean R². The threshold dummy variable is too crude a discretization to generalize.

---

## 4. Summary

| Target | Does threshold match interaction? | Verdict |
|--------|:-------------------------------:|---------|
| ΔC | **No** | Interaction ΔR² = +0.109 better. Threshold CV fails. |
| Restoration | **No** | Interaction ΔR² = +0.219 better. Threshold CV fails. |
| τ_rec | **Yes (tied)** | Both perform similarly. Neither performs well. |

**The interaction is not merely approximating a friction threshold.** For ΔC and restoration, the interaction model is substantially better than the best threshold model in full sample and cross-validation. For τ_rec, neither model works well.

The piecewise C×regime model (allowing different C slopes above/below threshold) performs better than the simple threshold but still cannot match the continuous interaction model for ΔC (0.428 vs 0.523) or restoration (0.534 vs 0.565).

**Verdict: The interaction is genuinely continuous, not a threshold artifact.**
