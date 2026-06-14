# T101C — Figure-to-Code Provenance Audit

**Framing:** Does there exist an auditable, reproducible chain from book claim → figure → code → equation → output?

**Sources:**
- Book: `/tmp/opencode/sfh_book16.txt` (5267 lines)
- Code: `/tmp/opencode/SFH_Python_CODE/` (entire repository)
- Prior: T100B, T100C, T101A, T101B audit results

---

## Part A — Book Artifact Inventory

Every visual, tabular, or quantitative result in the book:

| Artifact ID | Type | Book Location | Description | Page (est.) |
|-------------|------|---------------|-------------|-------------|
| B-F01 | Figure 22.1 | Line 4195 | "Murmuration-like patterns in SFH's coherence metric C" — described as PCA-derived oscillatory behavior separating high-coherence (C≥0.8) from low-coherence (C<0.8) systems, with an ASCII-plot representation (lines 4177–4199) referenced to carbon sink data from Yang et al. 2025 | 145 |
| B-T01 | Table B.1 | Lines 4703–4713 | Summary of SFH Experimental Protocols — 9 experiments (Ch 7–15) with metrics, SFH predictions, and materialist baselines | 159 |
| B-T02 | 3D/4D+ constraint table | Lines 1714–1720 | 5-row text table comparing 3D vs 4D+ for Physics, Neural Processing, Motor Control, Survival, Biology | 62 |
| B-P01 | Coherence percentages | Lines 3454–3464 | Dark energy: 70.6%–89.5%; Dark matter: 23.5%–38.9% | 120 |
| B-T03 | C≥threshold predictions | passim | 9+ coherence threshold claims (C≥1.3, C≥1.5, C≥1.2, C≥1.15, C≥1.4, C≥0.85, etc.) | 71–148 |
| B-P02 | Baseline numerical values | passim | ~15 materialist baseline values (Kmat=0.7, Rmat=0.6, etc.) asserted without derivation | 71–148 |
| B-P03 | Transition functions | Lines 1600–1654 | ft(a,b), gs(a,b), unified piecewise model | 59–60 |
| B-T04 | Fiber bundle components | Lines 3650–3663, 4006–4019, 4732–4749 | Π: P → B with specific B, G, P for each system | 130, 142, 161 |

**Total book artifacts requiring provenance: 9**

---

## Part B — Script Inventory

Every Python script in the repository relevant to figure/table generation:

| Script | Claims (from README) | Lines | Status |
|--------|---------------------|-------|--------|
| `reproduce_ch3_figures.py` | "Reproduces the figures from Chapter 3" | 56 | **BROKEN** — imports 3 functions that do not exist |
| `sfh_master_framework.py` | "Runs partition analysis... generates publication-ready plots" | ~350 | **RUNS** (after 5 fixes per T100C) but produces no book figures |
| `advanced_visualization.py` | "Generates comprehensive, publication-ready visualizations" | 1694 | **OK** as library — but missing 3 functions called by reproduce_ch3 |
| `partition_calc.py` | "Hardy–Ramanujan partitions, Euler checks" | 214 | **OK** — standalone |
| `statistical_analysis.py` | "probability distributions, coherence–fertility balance metrics" | — | **OK** — standalone |
| `setup_config.py` | "Initializes experiment environment" | — | **OK** — standalone |

---

## Part C — Provenance Chain Audit

For each book artifact, tracing: **Book Claim → Figure/Table → Source Script → Functions Called → Equations Implemented → Verifiable Output**

### C.1 B-F01: Figure 22.1 (Murmuration-like patterns)

| Link | Finding |
|------|---------|
| Book description | Lines 4169–4199: "PCA on Euler coefficients reveals oscillatory patterns... SFH applies same technique to coherence metric C across quantum, biological, cognitive datasets" |
| Expected script | `reproduce_ch3_figures.py` or `sfh_master_framework.py` |
| Actual script | **None.** No script in the repo implements PCA on coherence data or murmuration patterns. |
| Functions | Not applicable — no implementation exists. |
| Equations | The book references He et al. 2024 (murmuration conjecture) and PCA, but does not implement or connect these to SFH data. Figure 22.1 is manually constructed ASCII art in the book text, not a generated plot. |
| Output files | **No output file exists** matching "murmuration" or "Fig22_1" anywhere in repo. |
| **Verdict** | **NO CHAIN.** Figure 22.1 is a hand-drawn schematic described in text, not a code-generated figure. No script produces it. |

### C.2 B-T01: Table B.1 (Experimental Protocols Summary)

| Link | Finding |
|------|---------|
| Book description | Lines 4700–4713: 9 experiments listed with Chapter, Metric, SFH Prediction, Baseline |
| Expected script | Any config/parameter file or experiment runner |
| Actual script | **None.** The table values (C≥1.3, C≥1.5, etc.) appear in the book text per-chapter but are never collected into a machine-readable format in the repo. |
| Functions | Not applicable. |
| Output files | **No output file exists** that contains the structured data of Table B.1. |
| **Verdict** | **NO CHAIN.** Table B.1 is manually compiled in the book text. No script generates or validates it. |

### C.3 B-T02: 3D/4D+ Constraint Table

| Link | Finding |
|------|---------|
| Book description | Lines 1714–1720: 5-row table of physical/biological constraints |
| Expected script | None (philosophical/qualitative argument) |
| Actual script | **None.** This is a qualitative argument, not a computed result. |
| Functions | Not applicable. |
| Output files | Not applicable. |
| **Verdict** | **N/A** — this is qualitative reasoning, not a code-generated table. But note: the book has 0 figures in Chapter 3 despite `reproduce_ch3_figures.py` claiming to produce them. |

### C.4 B-P01: Coherence Percentages (Dark Energy/Matter)

| Link | Finding |
|------|---------|
| Book description | Lines 3444–3464: Formula `(C_SFH − C_mat)/C_SFH × 100%` with inputs C_SFH=0.85–0.95, C_mat=0.25–0.35 (dark energy) and C_SFH=0.85–0.90, C_mat=0.65–0.70 (dark matter) |
| Expected script | Any simulation or analysis script in Ch 15 / 18 |
| Actual script | **None.** The book says "simulations (Section 18.3) suggest C_SFH=0.85–0.95" but Section 18.3 (lines 3472–3520) proposes a test using cosmological simulations — it does not report results. |
| Functions | Not applicable — no simulation output exists. |
| Equations | The percentage formula (N57 in T101B) is algebraically correct but depends on arbitrary C inputs. The claimed C_SFH values are asserted, not computed. |
| Output files | **No output file** contains these specific calculations. The CSV files (`samples_v6.csv`, `weight_sweep_v6.csv`, `pareto_v6.csv`) contain partition data, not dark energy coherence. |
| **Verdict** | **NO CHAIN.** The coherence percentages are asserted values, not computed from running code. |

### C.5 B-T03 & B-P02: Coherence Thresholds and Materialist Baselines

| Link | Finding |
|------|---------|
| Book description | 9+ thresholds and ~15 baselines embedded in experimental protocols (Ch 7–15, 19–22, Appendix B) |
| Expected script | Parameter config, experiment runner, or calibration script |
| Actual script | **None.** The thresholds and baselines are stated in the book text and copied into Appendix B. No script derives, calibrates, or validates any of them. |
| Functions | Not applicable. |
| Equations | The generic C formula is defined but the specific thresholds (1.3, 1.5, 1.2, etc.) and baselines (0.7, 0.6, 0.5, 0.8) are free parameters. |
| Output files | **No config file** in the repo contains these values. `setup_config.py` generates parameter JSONs for partition analysis, not coherence baselines. |
| **Verdict** | **NO CHAIN.** Every threshold and baseline is an asserted number in the text with no code backing. |

### C.6 B-P03 & B-T04: Transition Functions and Fiber Bundle Components

| Link | Finding |
|------|---------|
| Book description | Lines 1600–1654 (transition functions), Lines 3650–4749 (fiber bundles) |
| Expected script | Mathematical implementation or visualization |
| Actual script | **None.** The fiber bundle framework Π: P → B is never implemented in code. The transition functions fₜ, gₛ are never implemented or plotted. |
| Functions | Not applicable. |
| Equations | The functions are defined mathematically in the book but never translated to code. |
| Output files | **No output file** contains a fiber bundle computation or transition function evaluation. |
| **Verdict** | **NO CHAIN.** The book's most explicit mathematics has zero code footprint. |

---

## Part D — What the Code Does vs. What the Book Claims

### D.1 Code-Only Artifacts (present in repo, absent from book)

| Code Artifact | Description | In Book? |
|---------------|-------------|----------|
| Integer partition enumeration | `partition_calc.py` generates all partitions of n | **NO** — book does not mention partitions |
| Hardy-Ramanujan formula | `partition_calc.py` computes p(n) via Hardy-Ramanujan (line ~85) | **NO** — book never mentions it |
| Fertility metric | `statistical_analysis.py` computes coherence/fertility balance | **NO** — "fertility" does not appear in book |
| Euler's pentagonal theorem | `partition_calc.py` verifies Euler identity | **NO** — book never mentions it |
| Pareto frontier | `statistical_analysis.py` computes Pareto-optimal partition configurations | **NO** — book never mentions Pareto |
| Monte Carlo universe sampling | `sfh_master_framework.py` samples 10,000+ "universes" from partition space | **NO** — book never describes this method |
| Distribution fitting | `advanced_visualization.py` fits statistical distributions to partition data | **NO** — book never mentions distribution fitting |
| Weight sweep analysis | Data file `weight_sweep_v6.csv` | **NO** — no weight sweep in book |

**Summary:** The repo contains sophisticated partition mathematics (Hardy-Ramanujan, Euler, Pareto, fertility) that the book does not reference. These are not "figures from the book" — they are exploratory analyses conducted independently of the book's argument.

### D.2 Phantom Functions (claimed in code, absent from codebase)

`reproduce_ch3_figures.py` imports and calls:

```python
fig1 = av.plot_coherence_fertility_histograms(results, num_samples=20000)  # DOES NOT EXIST
fig2 = av.plot_pareto_frontier(results)                                     # DOES NOT EXIST
fig3 = av.plot_weight_sweep(results)                                        # DOES NOT EXIST
```

These functions are **not defined anywhere** in `advanced_visualization.py` (1694 lines). The script will raise `ImportError` on execution.

### D.3 README Claims vs. Reality

| README Claim | Reality |
|-------------|---------|
| "contains... visualization tools that reproduce the figures and results presented in the book" | **False.** No script reproduces any book figure. |
| "reproduce_ch3_figures.py [is] hardcoded to reproduce the figures in a specific book chapter" | **False.** Chapter 3 has 0 figures. The script would also crash if run. |
| "Saves outputs into `plots/chX/` with filenames like `Fig3_1_partition_growth.png`" | **False.** No `plots/` directory exists. No figure output from this script exists. |
| "All results in the SFH book can be reproduced with this framework" | **False.** Zero results are reproducible from this framework. |

---

## Part E — What the Book Actually Has (Visual Inventory)

| Location | Claimed Artifact | Actual Form | Reproducible? |
|----------|-----------------|-------------|---------------|
| Ch 3 (entire) | Several figures (per README) | **0 figures, 0 tables, 0 equations** | N/A |
| Ch 8 §8.7 | Constraint table | Text-based table (5 rows, 2 columns) | Qualitative — not code-generated |
| Ch 15 §18.2.3 | Coherence percentages | Formula + typed numbers | Numbers are asserted, not computed |
| Ch 22 §22.2 | Figure 22.1 (murmuration) | ASCII art + text description | No code produces it |
| Appendix B | Table B.1 (protocols summary) | Text-based table | Manually compiled |
| Appendices A, C | Fiber bundle mathematics | Text definitions only | Never implemented in code |

**Summary of existing generated files:**
- `partition_analysis_output/summary_dashboard_partition_function.png` — partition analysis, not book content
- `partition_analysis_output/distribution_fitting_partition_function.png` — partition analysis, not book content
- `partition_analysis_output/distribution_analysis_partition_function.png` — partition analysis, not book content
- `Generated_CODE_Data/samples_v6.csv` — partition samples, not book content
- `Generated_CODE_Data/weight_sweep_v6.csv` — partition weights, not book content
- `Generated_CODE_Data/pareto_v6.csv` — Pareto data, not book content

**None of these correspond to any figure, table, or claim in the book.**

---

## Part F — Overall Verdict

### Does an auditable, reproducible chain exist connecting book claims to code?

| Book Artifact | Chain Status | Notes |
|---------------|-------------|-------|
| Figure 22.1 (murmuration) | **NO CHAIN** | Hand-drawn ASCII art; no implementation exists |
| Table B.1 (protocols summary) | **NO CHAIN** | Manually compiled in book text |
| 3D/4D+ constraint table | **N/A** | Qualitative reasoning |
| Coherence percentages (dark E/M) | **NO CHAIN** | Asserted numbers; no simulation output |
| All coherence thresholds | **NO CHAIN** | All asserted without code derivation |
| All materialist baselines | **NO CHAIN** | All asserted without code calibration |
| Transition functions | **NO CHAIN** | Defined in text, never implemented |
| Fiber bundle framework | **NO CHAIN** | Described qualitatively, never implemented |

**Result:** The chain is broken at every link. No book artifact has a code provenance path.

### Why the Repo Exists

The repo is **not** a figure-generation pipeline for the book. It is an independent exploratory codebase that:

1. Implements integer partition mathematics (Hardy-Ramanujan, Euler, Pareto)
2. Defines a "fertility" metric never mentioned in the book
3. Generates partition-distribution plots (histograms, growth curves)
4. Samples "universes" from partition space using Monte Carlo
5. Produces CSV files with partition statistics

The `reproduce_ch3_figures.py` script is **aspirational code**: it *claims* to generate book figures, but (a) the target chapter has no figures, (b) the called functions don't exist, and (c) it cannot execute.

### T101C Conclusion

The combined book + code corpus does **not** contain the mathematical derivation. Neither the book alone (established in T101A/T101B) nor the book + code together (established here) provides an auditable, reproducible chain from any book claim to any computational output.

The mathematics in the repo (partitions, Hardy-Ramanujan, fertility, Pareto) is about an entirely different mathematical object — integer partitions — that the book never invokes. The mathematics in the book (coherence metric, fiber bundles, transition functions) is never implemented in code.

**They are two disconnected bodies of work sharing only a title.**
