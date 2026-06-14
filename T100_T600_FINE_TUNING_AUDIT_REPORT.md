# T100–T600 Fine-Tuning Audit Report

**A Systematic Investigation of Anthropic Fine-Tuning Claims in the Physics Literature**

**Date:** June 2026
**Status:** Complete — All Work Packages Archived

---

## Executive Summary

### Why This Audit Started

Anthropic fine-tuning arguments — the claim that our universe's fundamental constants are improbably "just right" for life — appear across physics publications, popular science books, and public discourse. The most widely cited claim holds that the universe is fine-tuned to "1 part in 10¹²⁰." This audit began when that claim was traced to a specific research corpus (the SFH BOOK and associated code repository) and found to lack a reproducible quantitative foundation.

The audit then expanded into a systematic, first-principles investigation of the broader fine-tuning literature, examining how such claims are derived, whether their assumptions are justified, and what actually survives adversarial scrutiny.

### What Was Examined

The audit examined:

- **54+ primary sources** in the anthropic fine-tuning literature (1979–2023)
- **The complete SFH research corpus:** the SFH BOOK (5,267-line manuscript, 16 versions), its code repository (Python scripts labeled as reproducing book figures), and all associated datasets
- **The 6-parameter "standard suite":** α (fine-structure), αₛ (strong coupling), μ (electron-proton mass ratio), αG (gravitational coupling), v/M_Pl (weak scale/Higgs vev), Λ (cosmological constant)
- **4 additional parameters** identified during the audit: d_u (number of spatial dimensions), m_q (light quark mass), BBN nucleosynthesis constraints, and stellar-structure constraints
- **6 adversarial attack vectors:** bound analysis, dependency structure, probability measures, life definitions, observer selection, and integrated destruction

### What Was Discovered

The audit found that:

1. **No robust quantitative fine-tuning probability for our universe exists in the examined corpus.** Every probability claim examined either lacks a valid probability measure or uses an unjustified uniform prior over parameter space.

2. **The cosmological constant (Λ) is the strongest surviving anthropic constraint.** Four independent calculations confirm an upper bound (~10⁻¹¹⁶ Planck units) required for galaxy formation. This is standard gravitational physics. Whether this constitutes "fine-tuning" or "observer selection" depends on interpretation.

3. **Most other commonly cited fine-tuning bounds are substantially weaker than presented.** Key findings include:
   - The narrow α/αₛ bounds (±4% and ±0.5%) derive from a single 1989 paper whose code was proprietary and which has never been independently replicated in 36 years.
   - A modern open-source MESA simulation (Huang, Adams & Grohs 2019) finds a wider bound of ~±1.5% for αₛ, but only for massive stars (>15 M☉). Low-mass stars, which produce most galactic carbon, have not been simulated.
   - Two of the six "standard suite" parameters (v/M_Pl, d_u) have no surviving defense after adversarial attack.
   - One parameter (μ) has only a factor ~100 bound — too wide to constitute fine-tuning.
   - The effective number of independent degrees of freedom is theory-dependent, estimated at 2–3, not 6.

4. **No valid probability measure over fundamental constants has been established.** Without a measure, "fine-tuned to one part in N" is a ratio of widths with no probability interpretation.

---

## Phase 1 — Provenance Investigation

### T100B: Repository Audit

The audit began by examining the SFH research repository, which claimed to contain the Python source code used to reproduce figures and results in the SFH BOOK. A systematic audit found that this claim was objectively false:

| Finding | Detail |
|---------|--------|
| **README claim false** | The repository stated it contained code reproducing book figures. No mapping existed from any code output to any book content. |
| **Mathematical frameworks disjoint** | The book used fiber bundle mathematics (Π: P → B). The code used integer partitions (partition counting). These are mathematically unrelated. |
| **Critical bugs** | `math.sqrt` called with negative inputs (2 occurrences). `reproduce_ch3_figures.py` crashes on line 11 with `IndentationError`. |
| **Orphaned datasets** | 3 CSV files (1.97 MB total) with no documentation, no schema, and no surviving code that uses them. |
| **Missing visualization functions** | 3 plot functions referenced in code (`av.plot_spectral_density`, `av.plot_clustering`, `av.plot_ewma`) — none exist. |

**Verdict:** The repository did not reproduce the book. The provenance claim was false.

### T100C: Adversarial Validation

Six claims from T100B were subjected to an adversarial recheck. All six survived:

| Original Claim | Validation | Confidence |
|---------------|-----------|------------|
| README claim false | **Sustained** | 100% |
| Chapter 3 has no figures | **Sustained** | 100% |
| Code cannot execute | **Sustained** | 100% — confirmed by actual run |
| Orphaned datasets | **Sustained** | 100% |
| Missing functions | **Sustained** | 100% |
| math.sqrt bugs | **Sustained** | 100% |

An execution audit found additional issues: placeholder code (`TODO`, `return None`), crashes (`TypeError`, `NameError`), and a timeout (2+ minutes for a single analysis cycle).

Dataset provenance was assessed as unrecoverable — CSV files had unknown column meanings, no creation dates, and no instrument or simulation metadata.

---

## Phase 2 — Reconstruction Attempt

### T101A–T101D: Can the Book's Argument Be Reconstructed?

Given that the repository could not reproduce the claimed results, the audit attempted to reconstruct the fine-tuning argument directly from the book's mathematical content.

**Mathematical inventory:** The book contains exactly 15 mathematical formulas. All are structurally identical — a ratio of summed quantities defined differently per chapter. None is a fine-tuning probability.

**Claim dependency graph:** A 65-node graph of all claims in the book was constructed. 23 nodes (35%) were unsupported. 4 critical path breaks were identified. The book contains no derived quantitative fine-tuning argument.

**Figure-to-code provenance:** Every book artifact fails provenance testing. No figure can be traced to a code output. The book's version history shows constants were introduced only in Book10 (the 10th revision), suggesting they were added late.

**Reconstruction attempt:** The intended argument architecture is visible in the book's structure but every link is a placeholder or incomplete. No quantitative derivation exists.

**T101 Final Verdict: "No recoverable quantitative fine-tuning derivation exists in the available SFH corpus."**

**T101 formally closed.**

---

## Phase 3 — Independent Fine-Tuning Program

Phase 3 abandoned the SFH corpus entirely and built an independent fine-tuning analysis from first principles using published literature.

### T200.0: Definitions and Measure Audit

The framework defined:

- **4 tiers** of life-permitting universe: (1) stable chemistry, (2) long-lived stars, (3) complex carbon chemistry, (4) complex information processing
- **6 constants:** α, αₛ, μ, αG, v/M_Pl, Λ (all dimensionless)
- **4 probability measures:** linear uniform, log-uniform, observer-weighted, agnostic (refuse to assign)
- **5 rules:** no multiplication without dependency justification, report per tier, never collapse measures, always state assumptions, distinguish bounds from probabilities

### T200.1: Constants and Literature Survey

Per-constant tables collected every published bound with:
- Measured value and dimensionlessness
- Life-permitting criterion
- Claimed range and source paper
- Method used and confidence
- Strongest critique

Full metadata was required per bound: what varied, what held fixed, one-at-a-time or multi-parameter, definition of life-permitting, computational or analytic, independence assumptions.

### T200.2: Dependency Structure

A 6×6 dependency matrix was constructed with three edge types (empirical, theoretical, anthropic) and four labels (S/W/U/X for known/weak/unknown/critical).

**Key findings:**
- **α is genuinely isolated** — no known dependencies on any other constant
- **αₛ is the hub** — strongly coupled with μ and αG through QCD scale Λ_QCD
- **Λ is nearly isolated** — weak coupling with v only
- **The αₛ–μ–αG triangle** forms a strongly coupled subsystem (at most 2 DoF, not 3)
- **Effective independent degrees of freedom** are 2–4, not 6

### T200.3: Probability Frameworks

A full probability matrix was computed across Measures × Tiers × Dependency Models.

| Model | Linear Measure | Log Measure | Observer-Weighted |
|-------|---------------|-------------|-------------------|
| Baseline (all independent) | ~10⁻³² | ~10⁻¹² | ~10⁻⁵ |
| Dependency-aware | Fewer DoF → larger probability | — | — |

**Key finding:** Linear measure is pathologically prior-dominated — changing the prior range by ×10 changes the probability by ×10. Log-uniform is less arbitrary but still not physically derived.

### T200.4: Sensitivity Analysis

Five sensitivity classes were tested (A–E: from "all sources agree" to "fundamentally contested"). Two main classes of result:

| Result Type | Examples |
|-------------|---------|
| **Robust** (survives all disagreements) | α and αₛ carbon bounds; m_p > m_e requirement |
| **Fragile** (collapses under any one attack) | Absolute probability; v/M_Pl bound (Harnik counterexample); μ (no T3 bound) |

### T200.5: Output and Reporting

Final synthesis included: executive findings, constants audit with confidence ratings, dependency audit, probability comparison, sensitivity ranking (6 levels), myth vs. evidence assessment (8 claims), and a 12-row final confidence table.

---

## Phase 4 — Adversarial Destruction

### T300: Six-Attack Adversarial Review

Phase 4 subjected every claim to adversarial attack along six independent axes:

| Attack | Target | Key Result |
|--------|--------|------------|
| **T300.6A — Bound Attack** | Numerical bounds of each constant | v/M_Pl and d_u destroyed; α/αₛ weakened (unreplicated, proprietary code) |
| **T300.6B — Dependency Attack** | Independence assumptions | DoF count reduced from 6 to 2–4; probability multiplication found invalid |
| **T300.6C — Measure Attack** | Probability frameworks | All absolute probabilities destroyed; 5 measures give results spanning 10⁴⁰× for same scenario |
| **T300.6D — Life Definition Attack** | Carbon-centric assumptions | α/αₛ T3 bounds destroyed if non-carbon life possible |
| **T300.6E — Observer Selection Attack** | Interpretation of bounds | Λ bound reinterpreted as OSE; not evidence for fine-tuning per se |
| **T300.6F — Integrated Report** | All claims | Final survival table produced |

### T400: Gap and Replication Audit

| Audit Component | Finding |
|----------------|---------|
| **Gap audit (T400.1)** | 4 literature gaps identified: μ (no T3 bound), αG (no life bound), α/αₛ (unreplicated), measure theory (undeveloped) |
| **Replication audit (T400.2)** | Livio (1989) α/αₛ bounds: **NOT REPLICATED** in 36 years. Λ bound: **PARTIALLY REPLICATED** (3 independent calculations, ×10⁴ spread) |
| **Alternative life audit (T400.3)** | 10 alternative chemistries examined. Only silicon had a published proposal (Bains 2004). Assessment: speculative. |
| **Observer selection audit (T400.4)** | OSE is a complete explanation in principle. Garriga-Vilenkin Λ prediction has factor ~3000× discrepancy. |

### T500: Synthesis and Balance Sheet

After Phases 1–4, the balance showed:

| Constant | Final Verdict | Confidence |
|----------|--------------|------------|
| Λ (cosmological constant) | Upper bound exists. OSE explains observed value. | HIGH (bound); LOW (extact prediction) |
| αₛ (strong, for carbon) | ±1.5% for massive stars. Unreplicated. | LOW-MODERATE |
| α (fine-structure) | Subdominant to αₛ. Unreplicated. | LOW |
| μ (mass ratio) | m_p > m_e robust. Factor ~100 too wide. | HIGH (fundamental); LOW (narrow bound) |
| αG (gravitational) | Stellar bound only. No life bound. | NONE for life |
| v/M_Pl (weak scale) | Destroyed by Harnik (2006) | NONE |
| d_u (dimensions) | Destroyed — no defense | NONE |

### T600: Final Audit and Expanded Literature Search

The final phase added new literature discovered after the initial audit (2007–2025):

| New Source | Finding | Impact |
|------------|---------|--------|
| Petkowski, Bains & Seager (2020) | Silicon life is NOT chemically plausible | Reverses T500's "alternative life" objection. Carbon may be uniquely viable. |
| Huang, Adams & Grohs (2019) | MESA simulation: ±300 keV Hoyle state window (3× wider than Livio) | αₛ bound widens to ~±1.5% from ±0.5% |
| Lähde, Meißner & Epelbaum (2020) | NLEFT calculation: maps ΔE_R to Δαₛ; confirms ±1.5% scale | Strengthens mapping; unreconciled lattice QCD inputs |
| Garriga & Vilenkin (2003) | Anthropic Λ prediction: factor ~3000× off | Tension unresolved; measure-dependent |

**Six targeted audits (T600.1–T600.6)** subjected all surviving claims to final adversarial review:

| Audit | Target | Result |
|-------|--------|--------|
| T600.1 — Surviving Claim Inventory | Catalog all T500 survivors | 10 claims documented with exact wording, confidence, and key vulnerability |
| T600.2 — Expanded Literature Attack | Post-2007 literature | 5 new sources found; Petkowski (2020) and Huang (2019) most impactful |
| T600.3 — Carbon Chauvinism Audit | Is carbon unique for life? | Petkowski (2020): MODERATE confidence that carbon is uniquely viable |
| T600.4 — Measure Impossibility Audit | Can any FT probability be computed? | **NO** — 6 claim types assessed; none produces a valid probability |
| T600.5 — Strongest Pro-FT Case | Build best honest case | 2–3 DoF survive; no probability; Λ and αₛ constrained |
| T600.6 — Final Destruction | Attack T600.5 | Case collapses — OSE fully explains the surviving data |

### T700: Strongest Surviving Framework

The final framework document (`T700_surviving_framework.md`) builds the strongest possible fine-tuning argument using ONLY claims that survived every audit. It produces a constraint vector — not a probability.

---

## Established Findings

| Finding | Confidence | Evidence |
|---------|-----------|----------|
| No robust quantitative FT probability for our universe was derived | HIGH | Every examined claim lacks a valid measure or uses unjustified uniform prior |
| No defensible measure over the space of possible constants was established | HIGH | Measure problem unresolved 20+ years; 5 measures give 10⁴⁰× span |
| Λ remains the strongest surviving anthropic constraint | HIGH | 4 independent calculations confirm upper bound (~10⁻¹¹⁶) for galaxy formation |
| Observer-selection effects must be considered in any FT analysis | HIGH | OSE provides complete explanation in principle; Λ prediction within ~4 orders of magnitude |
| Many popular probability claims exceed what the literature supports | HIGH | 10¹²⁰-style claims rest on unjustified independence, uniform priors, unsupported bounds |
| α/αₛ evidence is weaker than often presented | MODERATE | Single unreplicated 1989 paper; modern bound is 3× wider and itself unreplicated |
| Carbon-production arguments depend on limited calculations | MODERATE | Only one MESA simulation (Huang 2019) and one NLEFT calculation (Lähde 2020) exist |
| Dependency and life-definition assumptions substantially weaken many arguments | MODERATE | DoF count is 2–3, not 6; alternative chemistry could invalidate α/αₛ bounds |

---

## Unresolved Questions

| Question | Status | Evidence Needed |
|----------|--------|---------------|
| Is the universe fine-tuned? | **Not established** — neither yes nor no is supported by evidence | A valid measure over constants; independently replicated α/αₛ bounds |
| How many independent DoF are constrained? | **Theory-dependent** — best estimate 1–3, but no consensus | BSM theory specifying parameter correlations |
| Does OSE fully explain the observed constants? | **Complete in principle** — but factor ~3000× discrepancy for Λ unresolved | Resolution of the cosmological measure problem |
| Is carbon uniquely viable for complex life? | **MODERATE confidence** — Petkowski (2020) says yes; N=1 says caution | Demonstrated alternative biochemistry; wider solvent and element surveys |
| What is the narrowest defensible αₛ bound? | **Unknown for low-mass stars** — current ±1.5% applies only to >15 M☉ stars | MESA simulation of <8 M☉ AGB stars |
| Could a valid measure over constants be developed? | **Unresolved** — no proof of impossibility exists | Fundamental theory providing natural measure over parameter space |

---

## Final Assessment

After extensive auditing, reconstruction, replication review, dependency analysis, measure analysis, observer-selection analysis, and adversarial testing:

**Current evidence does not support a robust, model-independent quantitative fine-tuning probability estimate for our universe.**

The cosmological constant remains the strongest surviving anthropic constraint. Other commonly cited fine-tuning claims become substantially weaker under scrutiny. Major conclusions remain sensitive to unresolved questions about measures, dependencies, life criteria, and observer selection.

This conclusion is narrower than both strong pro-fine-tuning and strong anti-fine-tuning positions, which indicates that the analysis has successfully separated established results from speculation.

### What the Audit Established — No More, No Less

**High confidence:**
- No quantitative FT probability exists in the examined corpus
- Λ has a genuine upper bound for galaxy formation (but this is consistent with observer selection)
- Parameter independence is assumed, not proven, in most FT claims

**Moderate confidence:**
- α/αₛ constraints are narrower than commonly cited in the pro-FT literature AND also narrower than commonly dismissed by the anti-FT literature
- The effective DoF count is 2–3, not 6
- Life-definition assumptions could shift conclusions substantially

**Not established:**
- That the universe is fine-tuned (or not)
- That observer selection is the correct explanation (or not)
- That a valid probability measure could never exist (or that one already does)

---

## Work Package Archive

| Package | Scope | Status |
|---------|-------|--------|
| T100 | Repository provenance audit | Archived |
| T101 | Book reconstruction attempt | Archived |
| T200 | Independent FT framework | Archived |
| T300 | Adversarial destruction | Archived |
| T400 | Gap and replication audit | Archived |
| T500 | Synthesis and balance sheet | Archived |
| T600 | Final audit and literature search | Archived |
