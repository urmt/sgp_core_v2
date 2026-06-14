# T100B Book–Code Divergence Report

**Audit Date:** 2026-06-01
**Repository:** [SFH_Python_CODE](https://github.com/urmt/SFH_Python_CODE)
**Book Source:** `sfh_book16.pdf` (5267 lines extracted)
**Scope:** Two-directional provenance tracing between book text and codebase.

---

## A. Book → Code Mapping

### A.1 What the Book Actually Contains

The book (`sfh_book16.txt`) uses a **fiber bundle framework**:

> "We can structure the qualic field as a fiber bundle Π : P → B with structure group G acting on the typical fiber F." (line 4394)

- The base space B is spacetime (or configuration space).
- The group G = (G₀, SO(3)) includes scale invariance + rotational symmetry.
- Section 22.2 (line 4122) mentions α_s ≈ 0.118 as "fine-tuned" but provides **no formula** computing any physical constant from SFH first principles.
- Section 3.3 (lines 590–1039) discusses panpsychism, idealism, integrated information theory, materialism — no equations for constants or probabilities.
- Lines 1090–1104 describe fine-tuning **qualitatively** (e.g., "a universe in which the fine-structure constant is changed by only 4%").

### A.2 Book Mathematical Framework

| Concept | Book Framework | Code Framework | Match? |
|---|---|---|---|
| Base structure | Fiber bundle Π: P → B | Integer partitions p(n) | NO |
| Symmetry group | G = (G₀, SO(3)) | Not present | NO |
| Fine-tuning | Qualitative discussion (lines 1090–1104) | "calculate_universe_probability" | NO |
| Physical constants | Discussed qualitatively (α_s line 4122) | calculate_physical_constants placeholder | NO |
| Figures | Chapter 3 has **zero figures** | reproduce_ch3_figures claims 3 figures | NO |
| Coherence | Not defined mathematically | Placeholder C = num_parts/Q_total | NO |
| Fertility | Not defined mathematically | Placeholder F = (max-min)/Q_total | NO |

**Conclusion:** The book and the code operate in **entirely separate mathematical frameworks** with **zero cross-reference**.

---

## B. Code → Book Mapping

### B.1 All Code Artifacts and Their Book Traceability

| Code Artifact | Book Correspondence | Evidence |
|---|---|---|
| `partition_calc.py` | NONE | Book uses fiber bundles, not integer partitions. Code's claimed "Eq. 2" has no book reference. |
| `fitness_functions.py` | NONE | Book provides no fitness function equations. 20-constant placeholder has no book basis. |
| `sfh_master_framework.py` | NONE | Orchestrates pipeline with no book counterpart. |
| `statistical_analysis.py` | NONE | Generic statistical toolkit. No SFH-specific content. |
| `advanced_visualization.py` | NONE | Generic plotting library. No SFH-specific content. |
| `reproduce_ch3_figures.py` | NONE | Claims to reproduce "Chapter 3 figures" — Chapter 3 has no figures. |
| `Cosmo_Tuning/model.py` | NONE | Random matrix surrogate. No book forward model. |
| `samples_v6.csv` | NONE | No generating equation in code or book. |
| `pareto_v6.csv` | NONE | No Pareto computation in code or book. |
| `weight_sweep_v6.csv` | NONE | No weight sweep in code or book. |

### B.2 Claimed vs. Actual Book References

The code comments reference:
- "Eq. 2" (`partition_calc.py` line 22) — **not defined in the book PDF.**
- "Protocol 3" (`Cosmo_Tuning/model.py` line 7) — **not defined in the book PDF.**
- "Section 2.4" (`partition_calc.py` line 89) — **book Section 2.4 does not contain these formulas.**
- "SFH Journal Article" (multiple comments) — **the only text in repo is the book PDF, not a separate journal article.**

---

## C. Divergence Table

### C.1 Mathematical Framework Divergence

| Property | Book | Code | Divergence Classification |
|---|---|---|---|
| Primary structure | Fiber bundle Π: P → B with group G | Integer partitions p(n) of integer n | **Replacement** — different mathematical object |
| Fine-tuning | Qualitative: "4% change in α breaks things" | Quantitative: 1/p with mention of "missing exp term" | **Gap** — book has no probability; code has broken probability |
| Physical constants | α_s mentioned once (line 4122), no computation | Placeholder formulas with math.sqrt bug | **Gap** — book qualitative, code broken |
| Figures | Chapter 3: 0 figures | Script claims to generate 3 figures | **Fabrication** — figures have no book basis |
| Coherence | Not defined | Placeholder: C = num_parts/Q_total | **Invention** — no book definition exists |
| Fertility | Not defined | Placeholder: F = (max-min)/Q_total | **Invention** — no book definition exists |
| Partition numbers | Never mentioned in 5267 lines | Central computational object | **Absence** — partitions have zero book basis |

### C.2 Code Functionality Divergence

| Code Function | Book Claim | Actual Status | Verification |
|---|---|---|---|
| `hardy_ramanujan_asymptotic` | Implements "Eq. 2" | math.sqrt missing argument; crashes | **BROKEN** |
| `calculate_universe_probability` | Implements P formula | Returns 1/p; exp term "missing from article" | **INCOMPLETE** |
| `calculate_physical_constants` | Implements "Section 2.4" | 2nd math.sqrt bug; 2/4 constants are strings "FORMULA_NEEDED" | **BROKEN + INCOMPLETE** |
| `calculate_coherence_fertility` | Replaced with actual SFH definitions | Uses placeholder definitions | **PLACEHOLDER ONLY** |
| `plot_coherence_fertility_histograms` | Generates Figure 3.1 | Function does not exist in advanced_visualization.py | **MISSING** |
| `plot_pareto_frontier` | Generates Figure 3.2 | Function does not exist in advanced_visualization.py | **MISSING** |
| `plot_weight_sweep` | Generates Figure 3.3 | Function does not exist in advanced_visualization.py | **MISSING** |
| `Cosmo_Tuning.forward_model` | Cosmological forward model | Random matrix A = rng.normal() seeded 42 | **NOT PHYSICS** |

### C.3 Data Provenance Divergence

| Dataset | Book Claim | Generation Evidence | Status |
|---|---|---|---|
| `samples_v6.csv` | Ch3 sample universes | No generating script in entire repo | **ORPHANED** |
| `pareto_v6.csv` | Ch3 Pareto frontier | No generating script in entire repo | **ORPHANED** |
| `weight_sweep_v6.csv` | Ch3 weight sweep | No generating script in entire repo | **ORPHANED** |

---

## D. Top-Level Assessment

### D.1 Does the README claim hold?

> *"This repository contains the Python source code used to reproduce the figures and results presented in the book 'The Sentience-Field Hypothesis'."* (README.md lines 5-6)

**Verdict: FALSE.** No figure or result from the book can be reproduced by this code because:
1. The book contains **no figures** in Chapter 3 (the claimed target).
2. The code uses **integer partitions** — a mathematical object entirely absent from the book's fiber bundle framework.
3. The visualization functions called by `reproduce_ch3_figures.py` **do not exist** in `advanced_visualization.py`.
4. The primary computational function `hardy_ramanujan_asymptotic` **crashes** due to `math.sqrt` missing its argument.
5. The three CSV datasets have **no generating script**.

### D.2 Does a quantitative chain (constants → coherence → probability) exist?

**Verdict: NO.** The chain required:
1. A forward model mapping physical constants to a partition value.
2. A coherence/fertility calculation from partition properties.
3. A probability calculation from coherence/fertility.

**What actually exists:**
1. `Cosmo_Tuning/model.py`: Random matrix (not a physics forward model).
2. `calculate_coherence_fertility`: Placeholder definitions marked "These need to be replaced."
3. `calculate_universe_probability`: Returns 1/p with "exp term is missing from the article."

**No quantitative chain exists in either the book or the code.**

### D.3 Mathematical Verification Summary

| Function | Line | Issue | Severity |
|---|---|---|---|
| `hardy_ramanujan_asymptotic` | 27 | `math.sqrt` missing argument (should be `math.sqrt(3)`) | **CRITICAL** — crashes on call |
| `calculate_physical_constants` | 99 | `math.sqrt` missing argument (should be `math.sqrt(3)`) | **CRITICAL** — crashes on call |
| `calculate_universe_probability` | 61 | Returns 1/p; exp term missing | **CRITICAL** — incorrect result |
| `calculate_coherence_fertility` | 72,78 | Placeholder only; "need to be replaced" | **CRITICAL** — not SFH definitions |
| `run_partition_analysis` | 144 | `results[key].append` missing argument | **MODERATE** — unreachable branch |
| 3 × visualization functions | N/A | Do not exist in module | **CRITICAL** — script non-functional |

### D.4 Categorical Classification of All Artifacts

| Category | Count | Artifacts |
|---|---|---|
| **BROKEN** (non-executable) | 2 | `partition_calc.py`, `reproduce_ch3_figures.py` |
| **UNUSED** (no caller) | 1 | `fitness_functions.py` |
| **ORPHANED** (no generator) | 3 | `samples_v6.csv`, `pareto_v6.csv`, `weight_sweep_v6.csv` |
| **NOT PHYSICS** (random matrix) | 1 | `Cosmo_Tuning/model.py` |
| **GENERIC TOOLKIT** (no SFH content) | 2 | `statistical_analysis.py`, `advanced_visualization.py` |
| **DISCONNECTED** (no book basis) | 1 | `sfh_master_framework.py` |
| **BOOK TEXT** (source document) | 1 | `sfh_book16.pdf` |

---

**Prepared by T100B audit. All claims backed by source file line numbers. No assumptions made beyond quoted evidence.**
