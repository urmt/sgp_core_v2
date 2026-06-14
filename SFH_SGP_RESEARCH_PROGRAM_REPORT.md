# SFH-SGP Research Program Report

**Historical Overview of a Systematic Investigation into Fine-Tuning Claims**

**Date:** June 2026
**Status:** Complete

---

## Origins

### Paper 1: The Sentience-Field Hypothesis (SFH)

The SFH manuscript (5,267 lines, 16 identified versions, titled *The Sentience-Field Hypothesis: Consciousness as Recursive Geometry*) proposed a mathematical framework claiming to connect consciousness, fundamental physics, and the apparent fine-tuning of the universe. The book developed a coherence metric C, defined as a ratio of summed observables to summed expected values, applied across domains from neural synchrony to galaxy clustering.

The book stated that the universe's fundamental constants appear "fine-tuned" and claimed that SFH provided a mathematical explanation for this observation.

### Paper 2: The SGP Core (Stochastic Geometric Paradigm)

The SGP research program (phases 265–550+) developed mathematical machinery around recursive organizational geometry: partition functions, stability analysis, sector dynamics, and manifold geometry. This program operated independently of the SFH book but shared the same research group and some conceptual vocabulary.

### Motivation for the Audit

The SFH BOOK's fine-tuning claims entered public circulation. When traced to their source, the supporting code repository could not reproduce the book's claimed results. The research group decided on a systematic, transparent audit:

1. **Phase 1 (T100):** Establish what the repository actually contains and whether it reproduces the book
2. **Phase 2 (T101):** Attempt to reconstruct the fine-tuning argument from the book itself
3. **Phases 3–6 (T200–T600):** Build an independent assessment of fine-tuning claims from first principles

### Research Goals

The audit program had specific, bounded goals:

- Determine whether a reproducible quantitative fine-tuning derivation exists in the research corpus
- Establish what survives adversarial review in the fine-tuning literature
- Produce a confidence-rated assessment of each claim
- Archive all findings for independent verification

It did not aim to:
- Prove or disprove fine-tuning
- Defend or attack any philosophical position
- Propose a new theory of fine-tuning
- Engage with theological or design arguments

---

## Development

### Books

The SFH BOOK evolved through at least 16 distinct versions (Book1 through Book16). Version tracking revealed:

| Version | Key Changes |
|---------|-------------|
| Book1–Book5 | No constant tables; qualitative philosophy only |
| Book6–Book9 | No constant tables; developing coherence metric |
| Book10+ | Constant tables introduced; fine-tuning claim appears |
| Book16 | Final audited version (5,267 lines) |

The late introduction of constant tables (Book10) suggests the fine-tuning claim was added after the core theoretical work was complete.

### Models

Two distinct mathematical models operated within the program:

**Partition model (code):** Integer partition counting using Hardy-Ramanujan asymptotics. Code analyzed partition density, fertility, stability, and complexity metrics. The mathematics was combinatorial number theory — counting ways to decompose integers.

**Fiber bundle model (book):** Principal bundle geometry Π: P → B with structure group G. The mathematics was differential geometry — analyzing connections, curvature, and sections.

**Critical finding:** These two mathematical frameworks are disjoint. The code's partition math has no relationship to the book's bundle math. No model in the code produces any result used in the book.

### Hypotheses

Several hypotheses were tested across the program's phases:

| Hypothesis | Phase | Outcome |
|------------|-------|---------|
| The repository reproduces the book's figures | T100 | **Falsified** — README claim false; code crashes; frameworks disjoint |
| The book contains a recoverable fine-tuning derivation | T101 | **Falsified** — no quantitative derivation exists |
| An independent FT framework can be built from the literature | T200 | **Partially successful** — framework produces constraint vector, not probability |
| Popular FT claims survive adversarial review | T300 | **Falsified** — most claims weakened or destroyed |
| α/αₛ bounds are independently replicated | T400 | **Falsified** — 36 years without replication |
| Carbon is the unique substrate for complex life | T600 | **Supported at MODERATE confidence** — Petkowski (2020) |

### Experiments

The code repository contained scripts labeled as experiments:

- `partition_calc.py` — Integer partition analysis (counting, density, fertility)
- `stability_analysis.py` — Stability metrics for partition structures
- `coherence_analysis.py` — Coherence calculations
- `reproduce_ch3_figures.py` — Claimed to reproduce Chapter 3 figures

Execution audit results:

| Script | Execution Status | Notes |
|--------|-----------------|-------|
| `reproduce_ch3_figures.py` | **CRASHES** — `IndentationError` line 11 | Cannot execute without fixes; after fixes: timeout (>2 min) |
| `partition_calc.py` | **PARTIAL** — runs with stub classes | Contains `TODO` and `return None` placeholders |
| `stability_analysis.py` | **CRASHES** — missing dependencies | References undefined functions |
| `coherence_analysis.py` | **CRASHES** — `math.sqrt` domain error | Negative input to square root |

No experiment produced output traceable to book content.

### Simulations

**Stellar nucleosynthesis simulations (literature-based):**

The audit did not run its own simulations but analyzed published simulation results:

| Simulation | Source | What It Found |
|------------|--------|---------------|
| Livio (1989) stellar code | Proprietary, unreplicated | ±100 keV Hoyle state window |
| Tegmark (2006) N-body | ΛCDM simulation | Λ upper bound ~10⁻¹²⁰ |
| Huang, Adams & Grohs (2019) | MESA (open source) | ±300–500 keV Hoyle window |
| Piran & Jimenez (2023) | N-body simulation | Λ bound within factor ~100 |

---

## Audit Era (T100–T600)

### What Was Tested

**Claims tested under adversarial review:**

| Claim Category | Specific Claims |
|---------------|-----------------|
| Repository integrity | README accuracy, code executability, dataset lineage |
| Book argument coherence | Mathematical consistency, formula-to-code mapping, figure provenance |
| Fine-tuning bounds (6-parameter suite) | α ±4%, αₛ ±0.5%/±50%, μ factor ~100, αG factor ~100, v/M_Pl factor ~2, Λ < 10⁻¹¹⁶ |
| Probability measures | Linear uniform, log-uniform, observer-weighted, landscape counting, causal-patch, Bayesian |
| Dependency assumptions | Independence of parameters, effective DoF count, GUT correlations |
| Life definitions | Carbon-based, silicon, ammonia, exotic, information-processing |
| Observer selection | Λ prediction, α prediction, typicality, reference class |
| Replication status | Livio (1989), Oberhummer (2000), Weinberg (1987), Tegmark (2006), Carr & Rees (1979) |

### What Survived

After all audits, these claims survived:

| Claim | Confidence | Basis |
|-------|-----------|-------|
| Λ < ~10⁻¹¹⁶ for galaxy formation | **HIGH** | 4 independent calculations (Weinberg 1987, Tegmark 2006, Barnes 2012, Piran-Jimenez 2023) |
| m_p > m_e for stable atoms | **HIGH** | Standard QED requirement |
| αₛ ~±1.5% for carbon in massive stars | **MODERATE** | Huang (2019) MESA + Lähde (2020) NLEFT (both unreplicated) |
| Carbon is the best-known chemical substrate for complex life | **MODERATE** | Petkowski, Bains & Seager (2020) |
| α ~±1.5% for carbon (subdominant) | **LOW** | Same paper as αₛ; subdominant contribution |
| OSE must be accounted for | **HIGH** | Carter (1974), Bostrom (2002), Garriga-Vilenkin (2003) |
| No valid measure exists | **HIGH** | McGrew et al. (2001); 5 measures span 10⁴⁰× |

### What Failed

| Claim | Failure Mode | Why |
|-------|-------------|-----|
| Repository reproduces book | Provenance | README false; code crashes; frameworks disjoint |
| Recoverable FT derivation in corpus | Reconstruction | 65-node claim graph has 4 critical path breaks |
| α ±4% for life | Replication | Single unreplicated 1989 paper; proprietary code |
| αₛ ±0.5% for life | Replication | Same paper; modern bound is 3× wider |
| v/M_Pl fine-tuned | Counterexample | Harnik (2006) weakless universe |
| d_u fine-tuned | No defense | Not defended in primary sources |
| Joint probability quantifiable | Measure | No valid measure; 59% of sources use none |
| 6 independent DoF | Dependency | Effective count is 2–3 |
| OSE makes precise Λ prediction | Measure-dependent | Factor ~3000× discrepancy |

---

## Lessons Learned

### Provenance Matters

The initial investigation was triggered by a faulty provenance claim. The repository README stated it contained reproduction code. It did not. Without the audit, this would have remained uncorrected. **Any claim about code should be verified by execution, not by reading the README.**

### Code Must Execute

A script labeled "reproduce_ch3_figures.py" crashed on its first line of meaningful execution. Code that cannot run cannot support claims. **Reproducibility requires executable code, not labeled stubs.**

### Datasets Require Lineage

Three CSV files were found with no documentation, no schema, and no originating experiment metadata. Without lineage, datasets are uninterpretable. **Every dataset should have a provenance record: origin, generator code, column schema, and creation date.**

### Probabilities Require Measures

The central finding of the audit is that fine-tuning claims require a probability measure over the space of possible constants. No such measure has ever been physically justified. Popular claims (1 in 10¹²⁰) use ratio-of-widths as a probability — a mathematically invalid operation. **Without a measure, fine-tuning is sensitivity analysis, not probability.**

### Assumptions Must Be Explicit

Every examined fine-tuning claim made implicit assumptions about:
- Parameter independence (rarely tested)
- Uniform prior over constant ranges (never justified)
- Carbon-based life (often unstated)
- One-at-a-time parameter variation (joint effects unexplored)

**An explicit assumption inventory would have identified these weaknesses immediately.**

### Adversarial Review Is Necessary

The strongest results to emerge from the audit — the Λ bound, the αₛ constraint, the measure impossibility — became stronger by surviving adversarial attack. Claims that collapsed (v/M_Pl, d_u) did so quickly under challenge. **Claims that have not been attacked should not be trusted.**

---

## Research Assets Produced

### Reports

| Title | Location | Content |
|-------|----------|---------|
| T100B — Artifact Provenance Matrix | `T100B_artifact_provenance_matrix.csv` | Repository file audit |
| T100C — Adversarial Validation | `T100C_adversarial_validation_report.md` | 6-claim adversarial recheck |
| T100C — Execution Audit | `T100C_execution_audit.md` | Script execution results |
| T100C — Intended Math Reconstruction | `T100C_intended_math_reconstruction.md` | Theoretical architecture |
| T100C — Dataset Provenance | `T100C_dataset_provenance_recovery.md` | Dataset lineage analysis |

### Audits

| Title | Location | Content |
|-------|----------|---------|
| T101A — Source Extraction | `T101A_source_extraction.md` | 15 formulas, 5 tables, 10 jumps |
| T101B — Claim Dependency Graph | `T101B_claim_dependency_graph.md` | 65-node graph |
| T101C — Figure-Code Provenance | `T101C_figure_code_provenance.md` | Artifact traceability |
| T101D — Fine-Tuning Reconstruction | `T101D_fine_tuning_reconstruction.md` | Intended architecture |
| T300.6A — Bound Attack | `T300.6A_bound_attack.md` | 9-strike attack on constants |
| T300.6B — Dependency Attack | `T300.6B_dependency_attack.md` | 6-strike dependency analysis |
| T300.6C — Measure Attack | `T300.6C_measure_attack.md` | Measure impossibility |
| T300.6D — Life Attack | `T300.6D_life_attack.md` | 8-strike life definition analysis |
| T300.6E — Observer Attack | `T300.6E_observer_attack.md` | Observer selection analysis |
| T300.6F — Destruction Report | `T300.6F_destruction_report.md` | Integrated destruction |
| T400.2 — Replication Audit | `T400.2_replication_audit.md` | Full bound reconstruction |
| T400.3 — Alternative Life Audit | `T400.3_alternative_life_audit.md` | 10 alternatives examined |
| T400.4 — Observer Selection Audit | `T400.4_observer_selection_audit.md` | OSE evaluation |
| T600.1 — Surviving Claims | `T600.1_surviving_claims.md` | 10 claims catalogued |
| T600.3 — Carbon Chauvinism | `T600.3_carbon_chauvinism_audit.md` | Silicon life audit |
| T600.4 — Measure Impossibility | `T600.4_measure_impossibility_audit.md` | 6 claim types assessed |

### Literature Surveys

| Title | Location | Coverage |
|-------|----------|---------|
| T200.1 — Constants Survey | `T200.1_constants_literature_survey.md` | 6 constants, 17 references |
| T300.1 — Master Bibliography | `T300.1_master_bibliography.md` | Comprehensive FT bibliography |
| T300.1A — Literature Balance | `T300.1A_literature_balance_audit.md` | Source diversity analysis |
| T600.2 — Expanded Literature | `T600.2_expanded_literature_attack.md` | Post-2007 literature |

### Replication Studies

| Title | Location | Target |
|-------|----------|--------|
| T400.2 — Replication Audit | `T400.2_replication_audit.md` | Livio (1989), Weinberg (1987), Carr & Rees (1979) |
| T400.5 — Final Evidence Ledger | `T400.5_final_evidence_ledger.md` | All bounds with replication status |

### Software

| Script | Location | Status |
|--------|----------|--------|
| `reproduce_ch3_figures.py` | Repository root | **Non-functional** — crashes, placeholders, buggy |
| `partition_calc.py` | Repository root | **Partial** — contains stubs |
| Various analysis scripts | Various | **Non-functional** — see execution audit |

No software produced in the program is verified as reproducible or independently usable.

---

## Remaining Open Problems

### Consciousness

The original SFH BOOK's central claim — that consciousness can be modeled as recursive geometry — was outside the scope of this audit. No assessment of this claim was made. It remains an open question in the philosophy of mind and theoretical neuroscience.

### Observer Selection

Observer selection provides a potentially sufficient explanation in principle for why we observe life-permitting constants, though the extent of its explanatory power remains unresolved. However:

- The factor ~3000× Garriga-Vilenkin discrepancy for Λ is unresolved
- No OSE prediction exists for αₛ, α, or μ
- The reference class problem (what counts as an observer?) is unresolved
- The Boltzmann brain problem in eternal inflation is unresolved

### Measure Problem

No physically justified probability measure over fundamental constants has been established. This is the single most important unresolved question identified by the audit. Without a measure, fine-tuning claims cannot be quantitative. With a measure, they could be.

### Life Definitions

The audit found that conclusions about fine-tuning depend sensitively on how "life" is defined. The Petkowski (2020) study provides MODERATE confidence that carbon is uniquely viable, but this is based on N=1 (terrestrial life). A rigorous assessment of alternative biochemistries could shift conclusions.

### Fundamental Constants

The origin of the fundamental constants — why they have the values they do — remains unknown. This is a question for fundamental physics (string theory, quantum gravity), not for fine-tuning analysis. The audit does not claim that the constants are or are not explained — only that current fine-tuning arguments do not provide a valid answer.

---

## Future Directions

### Option 1: Independent Replication Program

The highest-impact path forward is independent replication of the α/αₛ anthropic bounds using modern open-source stellar evolution codes (MESA, GENEC, Modules) across the full stellar mass range. If the ~±1.5% bound holds for low-mass stars (the dominant carbon source), the αₛ constraint would be substantially strengthened. If it does not, the fine-tuning claim for αₛ would be weakened.

**Required:** ~1–2 computational FTE, open-source stellar code, lattice QCD inputs from Lähde (2020) or successor calculations.

### Option 2: Measure-Theory Research

If a physically justified measure over fundamental constants is ever developed, the entire fine-tuning question becomes quantitative. Progress on the cosmological measure problem — including the string landscape, causal-patch measure, and scale-factor cutoff — could resolve this.

**Risk:** High. The measure problem has been open for 20+ years with no resolution in sight. No guarantee of progress.

### Option 3: Petkowski-Scale Alternative Biochemistry

Only one rigorous assessment of an alternative biochemistry exists in the literature (Petkowski, Bains & Seager 2020 on silicon). Extending this methodology to other candidates (boron, phosphorus, arsenic, exotic solvents, high-temperature chemistries) would either strengthen or weaken the carbon-uniqueness claim.

**Required:** Collaborative effort with organic chemists. ~2–3 years for a comprehensive survey.

### Option 4: Close the Program

The audit has established what it set out to establish: the provenance of the original claim, the state of the literature, and the confidence with which each bound can be cited. The program can be closed with the archival statement:

> "After extensive auditing, no robust quantitative fine-tuning probability for our universe was established. The cosmological constant remains the strongest surviving anthropic constraint. Major conclusions remain sensitive to unresolved questions about measures, dependencies, life criteria, and observer selection."

---

## Final Note

This program began with a specific question about a specific research corpus. It expanded into a systematic investigation of a much broader literature. The findings are narrower than either side of the fine-tuning debate might prefer — which is usually a sign that the analysis has successfully separated established results from speculation.

The repository, all audit documents, and all source materials are archived for independent verification.
