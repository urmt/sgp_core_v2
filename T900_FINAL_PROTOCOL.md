# T900 — Final Pre-Registered Protocol

**Status:** Complete
**Purpose:** The single document that defines the entire empirical program — frozen before any data is touched.
**Audience:** A research team implementing the benchmark.

---

## Preamble: What Survived the Pipeline

T100–T830 audited the SFH-SGP research program across 9 iterations. The surviving hypothesis is:

> **A single, fixed, information-theoretic coherence measure C (normalized total correlation) functions as a domain-general dynamical order parameter and predicts recovery dynamics across diverse systems — including non-predictive systems — without retuning, outperforming active inference, free-energy minimization, entropy maximization, and domain-specific complexity measures.**

The program no longer makes claims about consciousness, quantum measurement, cosmology, or fine-tuning. It claims one thing: **coherence is a dynamical order parameter, not just a descriptive statistic.**

---

## Section 1 — Metric Definitions

### 1.1 Primary Metric: C (Normalized Total Correlation)

C(S) = T(X₁; ... ; Xₙ) / H(X₁...Xₙ)

T = Σᵢ H(Xᵢ) − H(X₁...Xₙ)   (total correlation, multi-information)

H_joint = H(X₁...Xₙ)   (joint entropy)

**Estimator:** k-nearest neighbor mutual information estimator (Kraskov-Stögbauer-Grassberger, k = 3) with bias correction.

**Discretization:** Continuous data → uniform binning with √n bins (Sturges rule) for histogram baseline; kNN for primary analysis.

**Preprocessing:** All data z-scored before metric computation. No filtering, smoothing, or artifact removal beyond standard domain practice (specified per dataset below).

**Frozen before any testing:** YES — estimator, k, binning rule, and preprocessing are fixed.

### 1.2 Competitor Metrics

| ID | Metric | Formula | Reference | Domain of origin |
|:--:|:-------|:--------|:---------|:----------------:|
| M1 | **Shannon entropy** H | −Σ p log p | Shannon 1948 | Information theory |
| M2 | **LMC complexity** | H × D (disequilibrium) | López-Ruiz et al. 1995 | Complexity science |
| M3 | **Statistical complexity** C_μ | I(past; future) | Crutchfield & Young 1989 | Computational mechanics |
| M4 | **Transfer entropy** T_{X→Y} | I(Y_t; X_{<t} | Y_{<t}) | Schreiber 2000 | Information dynamics |
| M5 | **Multiscale entropy** MSE | H at multiple time scales | Costa et al. 2002 | Physiology |
| M6 | **Network integration** N | Global efficiency | Latora & Marchiori 2001 | Network science |
| M7 | **Active inference surprise** | −log P(observation | model) | Friston et al. 2006 | Neuroscience |
| M8 | **Synergy (from PID)** | I_∩ − I_min (specific) | Williams & Beer 2010; ince | Information theory |

### 1.3 Metric Selection Rationale

C is not claimed to be uniquely derivable from SFH-SGP (per T810 identifiability audit). It is claimed to be the metric that, **if it empirically dominates the above competitors** under the dynamical law specified below, provides evidence for the coherence-principle hypothesis.

The benchmark is agnostic about which metric wins. If statistical complexity (M3) or transfer entropy (M4) outperforms C, the coherence hypothesis weakens but the benchmark still produces useful science.

---

## Section 2 — Dynamical Law

### 2.1 Primary Model (Pre-Registered)

dC/dt = α·γ(S)·C·(1−C) − β·C

| Parameter | Meaning | Status | Prior |
|:----------|:--------|:------|:------|
| α | Universal coherence drive strength | Estimated globally across all domains | α ≥ 0, half-Cauchy(0, 1) |
| β | Universal entropy-driven decay rate | Estimated globally | β ≥ 0, half-Cauchy(0, 1) |
| γ(S) | System connectivity | Measured per system (independent variable) | Calculated from system adjacency matrix |

**γ(S) definition:** For a system with n components and adjacency matrix A:
γ(S) = (1/n²) · Σᵢⱼ Aᵢⱼ   (connection density)

For systems without a natural adjacency matrix: γ(S) = 1 by convention (no structural scaling). This applies to sandpiles, reaction-diffusion, etc.

### 2.2 Predictions

| Prediction | Equation | Test |
|:-----------|:---------|:-----|
| Equilibrium C | C_eq = max(0, 1 − β/(αγ)) | Compare to measured baseline C |
| Relaxation timescale | τ = 1 / [α·(2C_eq−1)·γ − β] | Fit to C(t) recovery curve |
| Perturbation recovery | C(t) = C_eq + (C₀ − C_eq)·exp(−t/τ) | Measure C₀ after perturbation, fit τ |
| Phase transition detection | d²C/dγ² inflection point at γ = 2β/α | Identify threshold connectivity for coherence onset |

### 2.3 Model Fitting

**Method:** Hierarchical Bayesian model. Parameters α, β fitted globally (one value across all domains). Residual variance per dataset.

**Software:** Stan (via PyStan or CmdStanPy). 4 chains, 2000 warmup, 2000 sampling.

**Comparison to competitors:** For each dataset, fit the SFH model (above) and each competitor's equivalent dynamical model. Compare via:
- Leave-one-out cross-validation (LOO-CV)
- Watanabe-Akaike Information Criterion (WAIC)
- Bayesian R²

---

## Section 3 — Pre-Registered Datasets

### 3.1 Non-Predictive Systems (Highest Information Value)

**NP1: Sandpile model (SOC)**
| Field | Value |
|:------|:------|
| System | Bak-Tang-Wiesenfeld sandpile on 100×100 grid |
| Observable | Grain height per cell |
| Components | n = 10,000 cells |
| Perturbation | Randomly add/subtract grains from 10% of cells |
| Recovery measure | Re-avalanche to critical state |
| Prediction | C(t) → C_eq(SOC) with universal α,β |
| Source | Simulation — generate on demand |

**NP2: Reaction-diffusion system (Belousov-Zhabotinsky)**
| Field | Value |
|:------|:------|
| System | 2D BZ reaction simulation, FitzHugh-Nagumo kinetics |
| Observable | Local concentration at each grid point |
| Components | n = 2500 grid cells |
| Perturbation | Add random noise to concentration field |
| Recovery measure | Spiral wave re-formation |
| Source | Simulation — generate on demand |

**NP3: Granular material (simulated)**
| Field | Value |
|:------|:------|
| System | 3D granular packing, discrete element method (LAMMPS) |
| Observable | Grain positions/velocities |
| Components | n = 1000 grains |
| Perturbation | Remove 10% of grains |
| Recovery measure | Force chain reorganization |
| Source | Simulation — generate on demand |

**NP4: Ecosystem (real data)**
| Field | Value |
|:------|:------|
| System | Grassland plant community, Cedar Creek LTER |
| Observable | Species abundance per plot |
| Components | n = species (varies, ~20–80) |
| Perturbation | Drought treatment (natural experiment) |
| Recovery measure | Post-drought species reassembly |
| Source | publicly available LTER data |

**NP5: Microbial community (real data)**
| Field | Value |
|:------|:------|
| System | Gut microbiome, 16S rRNA sequencing time series |
| Observable | OTU abundance per taxon |
| Components | n = genera (>100) |
| Perturbation | Antibiotic treatment |
| Recovery measure | Post-antibiotic community recovery |
| Source | publicly available (e.g., Human Microbiome Project, Dethlefsen & Relman 2011) |

### 3.2 Predictive Systems (Active Inference Competitor Test)

**PS1: Neural culture (real data)**
| Field | Value |
|:------|:------|
| System | Rat hippocampal culture, multi-electrode array |
| Observable | Spike trains (n electrodes) |
| Components | n = electrodes (typically 60) |
| Perturbation | Chemical (GABA antagonist, e.g., bicuculline) |
| Recovery measure | Post-perturbation firing pattern recovery |
| Source | publicly available (e.g., NeuroElectro, CRCNS) |

**PS2: Resting-state fMRI (real data)**
| Field | Value |
|:------|:------|
| System | Human resting-state fMRI, Human Connectome Project |
| Observable | BOLD time series (n ROIs) |
| Components | n = 100 ROIs (Schaefer atlas) |
| Perturbation | Sleep vs awake (natural perturbation) |
| Recovery measure | C comparison: awake vs sleep vs recovery |
| Source | HCP S1200 publicly available |

**PS3: Social network recovery (real data)**
| Field | Value |
|:------|:------|
| System | Online social network (e.g., Reddit subreddit interactions) |
| Observable | User-to-user reply count matrix |
| Components | n = active users |
| Perturbation | External shock (e.g., API pricing change, moderation policy) |
| Recovery measure | Interaction pattern recovery |
| Source | Publicly available (Reddit dumps, Pushshift) |

### 3.3 Boundary Cases

**BC1: Ideal gas (simulation)**
| Field | Value |
|:------|:------|
| System | n non-interacting particles in box |
| Observable | Particle positions |
| Components | n = 1000 |
| Perturbation | Initial non-uniform distribution |
| Prediction | C → 0 (no recovery). Failure condition if C > 0 persists. |

**BC2: Perfect crystal (simulation)**
| Field | Value |
|:------|:------|
| System | n particles on lattice, no thermal motion |
| Observable | Lattice site occupancy |
| Components | n = 1000 |
| Perturbation | Displace 5% of particles |
| Prediction | C → 1 (perfect recovery). Failure condition if C < 1. |

---

## Section 4 — Hypotheses and Success Criteria

### 4.1 Three Hypotheses

| Hypothesis | Claim | Requires | Minimal evidence |
|:-----------|:------|:---------|:-----------------|
| **H0** | C is a descriptive statistic | Not tested directly | Acknowledged as null if H1/H2 fail |
| **H1** | C is a domain-general dynamical variable | C predicts recovery across ≥3 domains with same α,β | LOO-CV favors SFH model over null in ≥3 of 8 datasets |
| **H2** | C is a domain-general dynamical variable BETTER than competitors | C outperforms active inference (M7) in non-predictive systems AND outperforms best domain-specific metric in ≥3 domains | (a) C beats M7 on NP1-NP5 AND (b) C beats M1-M6 on ≥3 datasets |

### 4.2 Quantitative Success Criteria

| Criterion | Threshold | Measures |
|:----------|:---------|:---------|
| Model fit | Bayesian R² > 0.3 (at least moderate fit) | Posterior predictive check |
| Cross-domain | Same α,β credible intervals overlap across ≥3 domains | Posterior overlap |
| C > competitor | C has lower WAIC than each comparator on ≥3 datasets | WAIC comparison |
| Slow variable | C autocorrelation time ≥ 5× component autocorrelation time | Timescale ratio |
| Non-predictive | C beats M7 on ≥3 of NP1-NP5 | WAIC, LOO-CV |
| Recovery trajectory | Predicted C(t) within 95% CI of observed C(t) | Posterior predictive check |

### 4.3 Failure Conditions (from T830)

| # | Condition | Verdict |
|:-:|:----------|:--------|
| F1 | C definition requires domain-specific retuning | A6 falsified |
| F2 | C not a slow variable (autocorrelation < 5×) | A3 weakened |
| F3 | C-restoration only in predictive systems | SFH redundant with active inference |
| F4 | C does not beat active inference (M7) on non-predictive systems | Active inference is better explanation |
| F5 | C does not beat domain metrics (M1-M6) | H0 confirmed |
| F6 | No cross-scale coupling after controlling for known pathways | A6 weakened |
| F7 | All tests underpowered or unfalsifiable | Program unfalsifiable |

---

## Section 5 — Statistical and Reproducibility Requirements

### 5.1 Power Analysis

| Test | Expected effect size | n required | Power |
|:-----|:-------------------:|:----------:|:-----:|
| C(t) relaxation fit | Cohen's f² = 0.2 | 50 time points | 0.90 |
| Cross-domain α overlap | ICC = 0.6 | 3 domains × 3 datasets | 0.80 |
| C vs competitor WAIC | ΔWAIC > 5 | 1000 posterior samples | 0.90 |
| Autocorrelation ratio | Ratio ≥ 5 | 500 time steps | 0.85 |

### 5.2 Pre-Registration Requirements

| Requirement | Status |
|:------------|:-------|
| Protocol frozen before any data analysis | Enforced by this document |
| All datasets listed with sources | Done (Section 3) |
| All metrics specified with references | Done (Section 1.2) |
| Estimator and parameters frozen | Done (Section 1.1) |
| Dynamical law specified | Done (Section 2.1) |
| Success/failure criteria specified | Done (Section 4.2-4.3) |
| Multiple comparison correction | Bonferroni per domain family |
| Pre-registration repository | OSF or AsPredicted |
| Analysis code repository | GitHub (public upon publication) |

### 5.3 Reproducibility Requirements

| Requirement | Method |
|:------------|:-------|
| All simulated data | Seed-fixed random generators, code provided |
| All real data | Publicly available (URLs listed) |
| All analysis code | Python/SciPy/Stan, DOI on Zenodo |
| All metric implementations | Reference implementations listed; custom code validated against known distributions |
| All model fits | Stan posterior samples provided (`.csv`) |

---

## Section 6 — Execution Plan

### Phase 1: Implementation (Months 1–4)

| Week | Task | Deliverable |
|:----:|:-----|:------------|
| 1–2 | Implement C estimator (kNN, histogram) | Validated on known distributions (independent, perfect correlation) |
| 3–4 | Implement all competitor metrics (M1–M7) | Reference implementations, validated |
| 5–6 | Generate all simulated datasets (NP1–NP3, BC1–BC2) | Seed-fixed data files |
| 7–8 | Download all real datasets (NP4–NP5, PS1–PS3) | Local copies, preprocessing scripts |
| 9–12 | Implement hierarchical Bayesian model (Stan) | Fitting code, validation on synthetic data |
| 13–14 | Run all metric computations | C(t) for all datasets |
| 15–16 | Run all model fits | Posterior samples for all datasets × models |

### Phase 2: Analysis (Months 5–6)

| Week | Task | Deliverable |
|:----:|:-----|:------------|
| 17–18 | Compute WAIC, LOO-CV for all models | Comparison table |
| 19–20 | Test H1 (cross-domain α,β overlap) | Posterior overlap analysis |
| 21–22 | Test H2 (C vs competitors, non-predictive systems) | WAIC comparison, Bayesian R² |
| 23–24 | Sensitivity analysis (estimator choice, binning effects) | Robustness check |

### Phase 3: Reporting (Month 7)

| Week | Task | Deliverable |
|:----:|:-----|:------------|
| 25 | Write results | Manuscript |
| 26 | Prepare all figures, tables | Publication-ready |
| 27 | Code and data release | Zenodo + GitHub |
| 28 | Submit | Target: e.g., Physical Review X, Entropy, or PLoS Computational Biology |

### Decision Gates

| Gate | Condition | Action |
|:----:|:----------|:-------|
| After Phase 1 | Are C and all competitor metrics computable on all ≥8 datasets? | No: report negative result. Yes: continue. |
| After Phase 2 | Does any hypothesis (H1, H2) meet success criteria? | No: accept H0. Publish negative result. Yes: report strongest result. |
| After Phase 3 | Publication submitted | Program complete. |

---

## Summary

| Element | Content |
|:--------|:--------|
| **Primary question** | Is C a domain-general dynamical order parameter? |
| **Primary metric** | Normalized total correlation (C) |
| **Competitors** | 7 metrics (M1–M7) |
| **Datasets** | 5 non-predictive (NP1–NP5) + 3 predictive (PS1–PS3) + 2 boundary (BC1–BC2) |
| **Dynamical law** | dC/dt = α·γ·C·(1−C) − β·C |
| **Model fitting** | Hierarchical Bayesian (global α,β) |
| **Hypotheses** | H0 (descriptive), H1 (dynamical, domain-general), H2 (dynamical, beats competitors) |
| **Failure conditions** | F1–F7 from T830 |
| **Effort** | 7 months (28 weeks) |
| **Prerequisites** | Python, Stan, computational cluster (for Bayesian sampling) |

---

## Afterword

This protocol is the endpoint of a process that began with fine-tuning arguments about consciousness and quantum mechanics. Those arguments were audited and largely eliminated. What remains is a narrow, testable, falsifiable claim about coherence as a dynamical order parameter.

The research team executing this protocol will produce useful science regardless of the outcome:

| Outcome | Contribution |
|:--------|:------------|
| **H2 confirmed** | Novel domain-general dynamical variable. Strongly supports coherence principle. |
| **H1 confirmed, H2 not** | C is domain-general but not uniquely powerful. Useful but not SFH-supportive. |
| **H0 (none confirmed)** | Negative result for coherence principle. Still provides comparative benchmark of 7 metrics across 10 systems — valuable reference database. |
| **F1–F7 triggered** | Each failure provides specific information about where coherence thinking breaks down. |

The program, as originally conceived, was a metaphysical investigation into consciousness and fine-tuning. It has been transformed into an empirical information-theoretic benchmark. That transformation — from "what should consciousness predict?" to "what can coherence measure?" — is the output of the entire T100–T900 pipeline.
