# T100C: Intended Mathematical Reconstruction

**Phase:** 4 of 4 — Reconstructing the Intended Pipeline
**Date:** 2026-06-01
**Director's Instruction:** "Do not invent mathematics. Produce Known, Plausible, Unsupported sections separately."

---

## K: Known Elements

These are directly observed in the codebase with line-number evidence.

### K1: Hardy-Ramanujan Asymptotic for Integer Partitions

**Location:** `partition_calc.py:19–29`
**Intended formula** (inferred from code + known mathematics):

```
p(n) ~ 1/(4n√3) · exp(π · √(2n/3))
```

**Code implementation** (partition_calc.py:27 — broken):
```python
term1 = 1.0 / (4 * Q * math.sqrt)    # missing (3) — should be math.sqrt(3)
term2 = math.exp(math.pi * math.sqrt(2 * Q / 3))
```

**Fact:** This is the standard Hardy-Ramanujan asymptotic formula for the integer partition function p(n). It is correctly identified in the code but the implementation has a typo (`math.sqrt` vs `math.sqrt(3)`).

### K2: Fine-Structure Constant Inverse Formula

**Location:** `partition_calc.py:97–99`
**Intended formula** (inferred from code):

```
α⁻¹ = (2π² / √3) · √Q_α + ln(p) / (2π)
```

**Code implementation** (partition_calc.py:99 — broken):
```python
alpha_inv = (2 * math.pi**2 / math.sqrt) * math.sqrt(Q_alpha) + (math.log(p_val) / (2 * math.pi))
```

**Fact:** Same `math.sqrt` bug — missing argument. Should be `math.sqrt(3)`. The term `2π²/√3` appears identically in the Hardy-Ramanujan asymptotic prefactor, suggesting Q_α is derived from partition properties.

### K3: Placeholder Coherence Definition

**Location:** `partition_calc.py:80`
**Code:**
```python
C = num_parts / Q_total if Q_total > 0 else 0.0
```

**Fact:** This is marked as a placeholder ("These need to be replaced with actual definitions from the SFH model" — line 72). It uses partition properties (number of parts, total Q) but is not the book's coherence definition.

### K4: Placeholder Fertility Definition

**Location:** `partition_calc.py:81`
**Code:**
```python
F = (max(partition) - min(partition)) / Q_total if Q_total > 0 else 0.0
```

**Fact:** Also a placeholder. Uses partition range normalized by total Q.

### K5: Universe Probability — Incomplete

**Location:** `partition_calc.py:39–61`
**Code:**
```python
return 1.0 / p_val  # Comment: "the exp term is missing from the article for P"
```

**Fact:** The intended formula appears to be `P = (1/p) · exp(...)` where the exponential term involves `π · √(2Q/3)` — i.e., the same exponential from the Hardy-Ramanujan formula. The function signature takes `p_val` but does not receive `Q`, suggesting the full formula could not be implemented without Q as a parameter.

### K6: Cosmological Forward Model — Random Matrix Surrogate

**Location:** `Cosmo_Tuning/model.py:20–24`
**Code:**
```python
rng = np.random.default_rng(42)
A = rng.normal(size=(n_obs, len(theta)))
scaled_theta = theta * np.exp(-np.sum(theta**2) / n_params)
return A @ scaled_theta
```

**Fact:** This is explicitly a "linear surrogate" (comment line 6). It replaces a true cosmological forward model with a random matrix. The use of `seed(42)` makes it deterministic but not physically meaningful.

### K7: Book's Coherence Metric (different from code)

**Location:** book line 1920, 2120, 2327, 2527, 2677, 2868, 3061
**Formula:**
```
C = (sum_i Ki/Kmat) / N
```
Where K_i are measured values and K_mat is the materialist baseline expectation.

**Fact:** This is the book's actual coherence metric. The code does NOT implement this formula. The code uses `C = num_parts/Q_total` as a placeholder.

---

## P: Plausible Reconstruction

These are inferences supported by variable names, formula structure, and dataset columns — but not directly observed in code.

### P1: Intended End-to-End Pipeline

The variable names and function calls suggest the following intended pipeline:

```
Input: Partition data (from a cosmological simulation or MCMC)
  │
  ▼
Step 1: Compute p(n) via enumeration or Hardy-Ramanujan asymptotic
        → p_exact, p_asymptotic
  │
  ▼
Step 2: Extract partition properties
        → Q_alpha (some partition-derived quantity)
        → Q_total (total number being partitioned)
        → num_parts, max_part, min_part
  │
  ▼
Step 3: Compute physical constants from Q_alpha and p
        → α⁻¹ = (2π²/√3)·√Q_α + ln(p)/(2π)
        → G_F = ? (FORMULA_NEEDED_FROM_ARTICLE in code)
        → α_s = ? (FORMULA_NEEDED_FROM_ARTICLE in code)
        → G   = ? (FORMULA_NEEDED_FROM_ARTICLE in code)
        → μ   = ? (not in current code at all)
  │
  ▼
Step 4: Compute coherence C and fertility F from partition
        → C = num_parts / Q_total (placeholder)
        → F = (max-min) / Q_total (placeholder)
        → J = α·C + β·F (linear combination)
  │
  ▼
Step 5: Compute universe probability from p(n)
        → P = (1/p) · exp(-π·√(2Q/3))  (inferred from line 41 comment)
  │
  ▼
Step 6: Pareto optimization: select universes maximizing C and F simultaneously
        → Pareto frontier (pareto_v6.csv columns: coherence, fertility, rank)
  │
  ▼
Step 7: Weight sweep: vary α weight in J = α·C + β·F
        → mean coherence and fertility at each weight
        → (weight_sweep_v6.csv columns: w_coh, mean_combined, ci_low, ci_high)
```

### P2: Intended Q_α Meaning

The parameter `Q_alpha` in `calculate_physical_constants(self, Q_alpha, p_val)` is used to compute α⁻¹. Given the formula `α⁻¹ = (2π²/√3)·√Q_α + ln(p)/(2π)`:

- The term `2π²/√3` is the Hardy-Ramanujan asymptotic prefactor.
- This suggests Q_α is analogous to `n` in the partition function — i.e., the integer being partitioned.
- In `run_partition_analysis`, Q_alpha is set to `float(n)` (line 157), confirming this interpretation.

**Plausible physical interpretation:** Q_α represents the "qualic charge" or "sentient field energy level" corresponding to the fine-structure constant — a higher Q_α produces a larger α⁻¹ (weaker electromagnetic coupling).

### P3: Intended Fertility Meaning

The placeholder definition `F = (max-min)/Q_total` measures the **range** of part sizes in a partition — i.e., how spread out the partition is. This maps intuitively to "fertility" as diversity in qualic states.

### P4: Universe Probability Formula

The comment at line 41 says "the exp term is missing from the article for P." The Hardy-Ramanujan formula is:
```
p(n) ~ (1/(4n√3)) · exp(π·√(2n/3))
```

The inverse of this is:
```
1/p(n) ~ (4n√3) · exp(-π·√(2n/3))
```

The intended P = (1/p) · exp(...) is plausibly:
```
P = (1/p) · exp(-π·√(2p/3))
```
(with p substituted for Q, based on the line 41 comment mentioning `exp(-pi*sqrt(2*p/3))`)

This is an inverse exponential weighting — larger partitions (more complex qualic structures) produce lower probabilities. This is consistent with fine-tuning reasoning: our universe with specific constants is one among many possible qualic states.

---

## U: Unsupported / Speculative

These have NO direct evidence in code or book.

### U1: Connection Between Integer Partitions and Physical Constants

**Status: NO EVIDENCE**

The fundamental claim that integer partitions p(n) determine physical constants (α, G, G_F, α_s, μ) is:
- Not in the book (which uses fiber bundles, not partitions)
- Not mathematically derived in the code
- Not referenced to any external paper

The connection `calculate_physical_constants(Q_alpha=float(n), p_val=p_exact)` is a direct assignment — n is the integer being partitioned, and it plugs directly into the α⁻¹ formula. No physical mechanism is proposed.

### U2: The Missing Formulas (G, G_F, α_s, μ)

**Status: NO EVIDENCE**

The code returns "FORMULA_NEEDED_FROM_ARTICLE" for gravitational coupling and strong coupling. The book does not provide these formulas. No external paper is referenced.

### U3: The MCMC Connection

**Status: NO EVIDENCE**

The repo contains an `MCMC_qualic/` directory with a demo notebook suggesting MCMC sampling of the qualic field. No MCMC code is connected to the partition analysis or physical constants pipeline.

### U4: The Book-to-Code Mapping

**Status: NO EVIDENCE**

No mapping exists between the book's fiber bundle mathematics and the code's integer partition framework. The reconstruction above (P1–P4) describes what the code plausibly intended to do — independent of the book.

---

## Summary: What Existed vs. What Is Documented

### Definitely Known (from code)
| Element | Status |
|---|---|
| Integer partition enumeration | ✓ Working (generate_all_partitions) |
| Hardy-Ramanujan asymptotic | ✗ Broken (math.sqrt bug) |
| Fine-structure constant formula | ✗ Broken (math.sqrt bug) |
| Coherence/fertility placeholders | ✗ Placeholders only |
| Universe probability | ✗ Returns 1/p only |
| Gravitational/strong coupling | ✗ Not implemented |
| Muon constant | ✗ Not implemented |
| Random matrix surrogate | ✓ Working but meaningless |
| Pareto analysis | ✗ Missing from advanced_visualization.py |

### Plausibly Intended (from code structure)
| Element | Evidence |
|---|---|
| Pipeline: partition → constants → coherence → probability | Function call graph and return values |
| Pareto frontier optimization | CSV files exist, function name referenced |
| Weight sweep of coherence/fertility tradeoff | CSV exists, function name referenced |
| 20,000 universe Monte Carlo sample | Hardcoded in reproduce_ch3_figures.py |

### Purely Speculative (no evidence)
| Element | Status |
|---|---|
| Physical meaning of Q_alpha | Unknown |
| Formula for G, G_F, α_s, μ | Unknown |
| Connection to book's fiber bundles | Unknown |
| Source of CSV column values | Unknown |
| Any empirical validation of results | Unknown |

---

## Conclusion

**The intended quantitative pipeline is reconstructable from code artifacts:**
1. Enumerate integer partitions → compute p(n)
2. Derive physical constants from partition properties (Q_α, p_val)
3. Compute coherence and fertility from partition structure
4. Weighted combination J = α·C + β·F
5. Universe probability P inversely related to p(n)
6. Pareto frontier optimization
7. Weight sweep sensitivity analysis

**But this pipeline was never completed and is disconnected from the book's mathematics.** The code sits at the "scaffolding" stage — function signatures defined, formulas partially written, placeholders in critical positions, bugs preventing execution.

**The original SFH fine-tuning argument, if it existed, cannot be recovered from this repository alone.** The `sfh_simulation_v6-Enhanced-Combo.py` script (lost to rename-and-edit) may have contained the working pipeline, but it is not preserved in current code.
