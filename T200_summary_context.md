## Goal
- Reconstruct a rigorous, defensible fine-tuning analysis from first principles using published literature, based on the SFH BOOK repository and T101/T200 audit findings.

## Constraints & Preferences
- T200.0: Four tiers of life-permitting universe (stable chemistry → long-lived stars → complex chemistry → information processing); results reported per-tier, never aggregated.
- T200.0: Four probability measures evaluated uniformly (linear, log-uniform, observer-weighted, agnostic); never collapsed.
- T200.0: No multiplication of probabilities without explicit dependency justification (Phase 2).
- T200.0: No single headline number — final output is structured comparison, not a probability.
- T200.1: Per-constant table with measured value, dimensionlessness, life-permitting criterion, claimed range, source paper, method used, confidence.
- T200.1: Do not merge ranges from different papers — preserve all distinct bounds.
- T200.1: Source hierarchy: original technical papers > review papers > books > secondary summaries.
- T200.1: Required metadata per bound: what varied, what held fixed, one-at-a-time or multi-parameter, definition of life-permitting, computational model or analytic, independence assumptions.
- T200.1: For each constant, collect both strongest fine-tuning argument AND strongest critique/alternative.
- T200.1: Success criterion: answer "what ranges have been claimed, by whom, under what assumptions, and with what level of disagreement?" — without computing any probabilities.

## Progress
### Done
- T100B: Complete provenance audit of SFH repository — README claim false, 3 orphaned CSVs, 2 critical math.sqrt bugs, 3 missing visualization functions, partition math disconnected from book fiber bundles.
- T100C: Adversarial recheck — all 6 T100B claims survived; execution audit found crashes and placeholders; dataset provenance unrecoverable.
- T101A Source Extraction: 15 formulas, 5 tables, 10 unsupported jumps catalogued.
- T101B Claim Dependency Graph: 65 nodes, 23 unsupported, 4 critical path breaks. Book contains no derived quantitative fine-tuning argument.
- T101C Figure-to-Code Provenance: every book artifact fails provenance — disconnected from code.
- T101D Fine-Tuning Reconstruction: intended argument architecture visible but every link is placeholder or incomplete.
- T101 formally closed — verdict: "No recoverable quantitative fine-tuning derivation exists in the available SFH corpus."
- SFH BOOK deep dive: audit of regression4.py, constants_sweep_real.csv, figure provenance, and all 16 book versions. Regression4.py uses observational uncertainty (CODATA, PDG), not anthropic windows. The "anthropic filter" bounds are non-operative (wider than data). Book versions 6-9 have no constants; Book10 introduces them. No version derives a fine-tuning probability. The 0.1% claim is entirely qualitative.
- **T200.0 Definitions & Measure Audit: complete** — `T200.0_definitions_measure_audit.md`. 4 tiers, 6 constants, 4 measures, 5 rules.
- **T200.1 Constants & Literature Survey: complete** — `T200.1_constants_literature_survey.md`. 6 constant sections + synthesis, 17 references from original papers.
- **T200.2 Dependency Structure: complete** — `T200.2_dependency_structure.md`. 6×6 matrix, directed graph, assumption audit, risk assessment, 5 questions.
- **T200.3 Probability Frameworks: complete** — `T200.3_probability_frameworks.md`. Full probability matrix across Measures × Tiers × Dependency Models. Baseline: Model B / log measure / Tier 3 → P ~ 1.9×10⁻¹². Key finding: linear measure is pathologically prior-dominated.
- **T200.4 Sensitivity Analysis: complete** — `T200.4_sensitivity_analysis.md`. Five sensitivity classes (A–E) tested. Robust results: α and αs carbon bounds survive all disagreements. Fragile results: absolute probability collapses under v/M_Pl (Agrawal vs. Harnik), μ (no bound), and observer-selection uncertainty.
- **T200.5 Output & Reporting: complete** — `T200.5_output_reporting.md`. Final synthesis: executive findings, constants audit, dependency audit, probability comparison, sensitivity ranking (6 levels), myths vs. evidence (8 claims assessed), three-category final assessment (empirical / modeling / philosophical), and 12-row confidence table.

### In Progress
- (none)

### Blocked
- (none)

## Key Decisions
- T101 closed: audit program reached definitive conclusion that no valid quantitative fine-tuning argument exists in the combined book+code corpus.
- T200 opened: new program focused on independent reconstruction from first principles, not further provenance auditing.
- T200.0: Terms and measures defined before any data collection to prevent hidden assumptions from contaminating results.
- T200.1: Ranges from different papers are never merged — all distinct bounds preserved with citations. Each constant includes both strongest fine-tuning argument AND strongest critique (adversarial balance built into evidence gathering).
- T200.2: Dependency classification uses three edge types (empirical, theoretical, anthropic) with four labels (S/W/U/X).
- T200.2: Dependency matrix provides dual analysis — SM-level independence vs. GUT-level linking.
- **T200.2 key finding: The αₛ–μ–α_G triangle forms a strongly coupled subsystem.** αₛ determines Λ_QCD → m_p, m_p determines μ (inverse) and α_G (square). These are at most 2 degrees of freedom, not 3. Multiplying probabilities across this triangle is formally invalid.
- **T200.2 key finding: α is genuinely isolated** — no known dependencies on any other constant. Low risk.
- **T200.2 key finding: The dependency structure reduces the effective independent degrees of freedom from 6 to as few as 4** (2 isolated + 2 strongly coupled + 2 weakly coupled), depending on GUT assumptions.
- **T200.2 key finding: The strongest result is a negative one** — some probability products commonly quoted in fine-tuning literature cannot be justified because the dependency structure is too poorly understood.

## Next Steps
1. ~~**T200.3 Probability Frameworks**~~ — complete.
2. ~~**T200.4 Sensitivity Analysis**~~ — complete.
3. ~~**T200.5 Output & Reporting**~~ — complete.

**T200 program concluded.** All five phases complete. See `T200.5_output_reporting.md` §8 (Final Confidence Table) for the primary deliverable — 12 conclusions with confidence ratings.

## Critical Context
- The SFH corpus (book + code) is **disconnected** — the book's fiber bundle math and the code's partition math are completely unrelated. No valid argument exists in either.
- T200 starts from scratch with external literature only. The 6 constants under analysis: α, αs, μ = me/mp, α_G = G m_p²/(ħc), weak scale v/MP, cosmological constant Λ (all dimensionless).
- Four tiers of life-permitting universe: (1) any stable chemistry, (2) long-lived stars, (3) complex chemistry (carbon production), (4) complex information processing.
- Four probability measures: A (uniform linear), B (uniform log), C (observer-weighted), D (agnostic — refuse to assign probability).
- **Narrowest anthropic bounds per constant (from T200.1):** α ~4% (Livio 1989), αs ~0.5% (Livio 1989) but contested up to 50%, μ — unknown (no bound exists), α_G ~factor 10 (Adams 2019), v/M_Pl ~factor 2 (Agrawal 1998) but contested (Harnik 2006 says no bound), Λ ~10⁻¹¹⁸ (Weinberg 1987) vs. observed 10⁻¹²².
- **Dependency structure (from T200.2):** α is isolated. αₛ is the hub (S with μ, α_G; W with v/M_Pl). Λ nearly isolated (W with v only). The αₛ–μ–α_G triangle is strongly coupled — at most 2 independent degrees of freedom, not 3.
- **The μ gap** (no quantitative anthropic bound in literature) means one of the 6 constants cannot be included in any probability calculation.

## Relevant Files
- `/home/student/sgp_core_v2/T101A_source_extraction.md`: Complete formula catalog from book.
- `/home/student/sgp_core_v2/T101B_claim_dependency_graph.md`: 65-node claim graph.
- `/home/student/sgp_core_v2/T101C_figure_code_provenance.md`: Provenance audit results.
- `/home/student/sgp_core_v2/T101D_fine_tuning_reconstruction.md`: Reconstruction analysis — intended architecture never completed.
- `/home/student/sgp_core_v2/T200.0_definitions_measure_audit.md`: Foundational definitions (4 tiers, 6 constants, 4 measures, 5 rules).
- `/home/student/sgp_core_v2/T200.1_constants_literature_survey.md`: Literature survey — 6 constants, 17 references.
- `/home/student/sgp_core_v2/T200.2_dependency_structure.md`: Dependency analysis — 6×6 matrix, directed graph, risk assessment.
- `/home/student/sgp_core_v2/T200.3_probability_frameworks.md`: Probability matrix — all Measures × Tiers × Dependency Models.
- `/home/student/sgp_core_v2/T200.4_sensitivity_analysis.md`: Sensitivity analysis — 5 classes (A–E), combined budget.
- `/home/student/sgp_core_v2/T200.5_output_reporting.md`: Final synthesis — executive findings, constants audit, dependency audit, probability comparison, sensitivity ranking, myth vs evidence, final assessment, 12-row confidence table.
