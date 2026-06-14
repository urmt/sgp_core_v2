# Critical Assumptions Register

Master list of propositions that the research program depends on, with current evidence for and against each.

Status definitions:
- **Supported**: Evidence consistently positive, multiple tests
- **Plausible**: Preliminary evidence, no counterexamples
- **Challenged**: Evidence exists both for and against
- **Unknown**: No test performed, or test inconclusive
- **Falsified**: Evidence consistently negative
- **Not Supported**: Evidence consistently negative

---

## Assumption 1: Higher coherence implies higher resilience

| | |
|---|---|
| **Statement** | Systems with higher C recover better from perturbation (smaller dip, faster τ_rec, higher restoration) |
| **Evidence For** | C-only model achieves R²=0.10 for ΔC (p~0.01). High-C runs (Q4) all have restoration > 1.0. |
| **Evidence Against** | C-only model fails for τ_rec (R²=0.05) and restoration (R²=0.04). Low-C runs can have restoration > 1.2 (5/15). Same C produces opposite ΔC sign depending on friction. |
| **Status** | **Challenged** |
| **Type** | Predictive |

---

## Assumption 2: Coherence is causally involved in recovery

| | |
|---|---|
| **Statement** | Changing coherence directly (while holding everything else fixed) would change recovery outcomes |
| **Evidence For** | None — no intervention experiment has been performed |
| **Evidence Against** | C fails to predict recovery direction and speed when conditioned on friction. C is correlated with friction (r≈−0.74). The apparent C→recovery relationship may be entirely mediated by mobility. |
| **Status** | **Unknown** |
| **Type** | Causal |

---

## Assumption 3: Coherence is an informative state variable

| | |
|---|---|
| **Statement** | C tracks the degree of interaction structure in a system, and this information is meaningful for understanding system behavior |
| **Evidence For** | C discriminates structured vs unstructured systems across 8 testbeds. C detects perturbations at SNR=2.14 (outperforming I_pred, C_sigma, MSE). C correlates with friction (r=−0.74) in the expected direction (more friction → less structure). |
| **Evidence Against** | None — no evidence that C is uninformative or misleading about interaction structure |
| **Status** | **Supported** |
| **Type** | Epistemological |

---

## Assumption 4: Interaction structure matters more than raw state information

| | |
|---|---|
| **Statement** | Knowing how components interact (via coherence) reveals more about system properties than knowing their individual states |
| **Evidence For** | IF-3 recovers interaction structure from 90% missing data. C outperforms competitor metrics (I_pred, C_sigma, MSE) on perturbation detection. |
| **Evidence Against** | None |
| **Status** | **Supported** |
| **Type** | Theoretical |

---

## Assumption 5: Coherence can be measured without ontological commitment

| | |
|---|---|
| **Statement** | The coherence metric stands independently of the SFH ontology — it is a mathematical quantity (total correlation ratio) that can be computed on any multivariate time series |
| **Evidence For** | Metric computation uses only information theory (Gaussian KDE, total correlation). No SFH-specific operations. Results are reproducible by any researcher with scipy and numpy. |
| **Evidence Against** | None |
| **Status** | **Supported** |
| **Type** | Meta-scientific |

---

## Assumption 6: Results generalize beyond granular systems

| | |
|---|---|
| **Statement** | Findings about C, mobility, and recovery from the granular DEM apply to other complex systems (ecology, neuroscience, opinion dynamics) |
| **Evidence For** | Forest succession shows C perturbation response consistent with granular. C structure discrimination works across 8 testbeds including neural and opinion models. |
| **Evidence Against** | Mobility manipulation is not possible in non-granular systems. The C×recovery relationship has only been tested on granular (60 runs). The sign reversal may be specific to granular physics. |
| **Status** | **Weakly Supported** |
| **Type** | Generalization |

---

## Assumption 7: Binning preserves interaction structure

| | |
|---|---|
| **Statement** | Spatial or functional binning of components (e.g., grouping grains by x-position) preserves the interaction structure relevant to resilience |
| **Evidence For** | Results robust to ±50% bin count variation (5–20 bins). Quadrant analysis consistent across binning schemes. |
| **Evidence Against** | Binning discards spatial resolution. Some interaction patterns may not survive coarse-graining. |
| **Status** | **Supported** (with caveats) |
| **Type** | Methodological |

---

## Assumption 8: Sliding windows capture dynamics

| | |
|---|---|
| **Statement** | Coherence computed over sliding time windows captures the temporal evolution of system organization |
| **Evidence For** | Results robust to ±25% window size variation (56–94 timepoints). Perturbation boundaries produce clean dip signatures. |
| **Evidence Against** | Window size (75 steps) is a free parameter. Window boundaries near perturbation time may blur the dip onset. |
| **Status** | **Supported** |
| **Type** | Methodological |

---

## Assumption 9: Perturbation response reveals intrinsic resilience

| | |
|---|---|
| **Statement** | Removing components and observing the response reveals the system's intrinsic capacity to recover, not an artifact of the removal procedure |
| **Evidence For** | Systematic variation with friction (6 levels, 10 replicates each). Recovery metrics show smooth transitions across friction levels. Dips are measurable and replicable. |
| **Evidence Against** | Only one perturbation type tested (10% random removal). Different perturbation fractions (5%, 20%) may produce different recovery scaling. |
| **Status** | **Supported** |
| **Type** | Methodological |

---

## Assumption 10: The granular DEM is a valid model system

| | |
|---|---|
| **Statement** | Soft-sphere 2D granular dynamics under gravity is an adequate model for studying interaction structure and recovery |
| **Evidence For** | Clean, repeatable dynamics. Friction parameter provides systematic mobility control. Perturbation response is measurable and structured. |
| **Evidence Against** | 2D granular may not capture 3D or non-granular physics. Small system (50 grains) may have finite-size effects. Overdamped dynamics (gravity + friction) may not generalize to inertial or active systems. |
| **Status** | **Supported** (for current purposes) |
| **Type** | Instrumental |

---

## Assumption 11: Friction is an adequate mobility proxy

| | |
|---|---|
| **Statement** | The DEM friction coefficient controls mobility (capacity to reconfigure) in a monotonic and interpretable way |
| **Evidence For** | MSD varies with friction as expected: low friction → high MSD (rms velocity ≈ 16), high friction → low MSD (rms velocity ≈ 12). Friction predicts recovery with R²=0.18–0.30 across targets. |
| **Evidence Against** | MSD variation within friction levels (sd ≈ 2–4) suggests friction does not fully determine mobility. Friction is not directly measurable in non-DEM systems, limiting generalization. |
| **Status** | **Supported** (for granular system) |
| **Type** | Instrumental |

---

## Assumption 12: Coherence and mobility are independent properties

| | |
|---|---|
| **Statement** | C and mobility capture different aspects of system organization and can be independently measured and manipulated |
| **Evidence For** | Within a fixed friction level, C varies by ±0.02–0.03 (from random seed variation). **(RD-016)** Residual(C) = C − E[C\|friction] is largely uncorrelated with all mobility descriptors (max |r| = 0.26 with packing variance). Residual(C) predicts recovery beyond all four mobility variables combined (ΔR² = +0.10–0.24 across targets). This shows the friction-independent component of C carries unique predictive signal not reducible to mobility. |
| **Evidence Against** | C and friction are correlated at r≈−0.89 (R²=0.793). In the current design, friction controls BOTH C and mobility. No experiment has independently manipulated one while holding the other fixed. The residual(C) effect may also be endpoint-driven (see Assumption 14). |
| **Status** | **Challenged** — partial independence demonstrated (residual variance is predictive and non-redundant), but causal independence requires manipulation |
| **Type** | Causal / Methodological |

---

## Assumption 13: Mobility causes recovery

| | |
|---|---|
| **Statement** | The capacity to reconfigure (mobility) is a direct determinant of recovery speed and quality |
| **Evidence For** | Friction-only model predicts ΔC (R²=0.30) and restoration (R²=0.23). All slow-recovery runs (τ_rec > 100) are at high friction. |
| **Evidence Against** | Friction also determines C. The additive model (C + friction) outperforms friction-only, suggesting C contributes independently of friction. |
| **Status** | **Plausible** (not fully separable from C) |
| **Type** | Causal |

---

## Assumption 14: The C × mobility interaction term is genuine

| | |
|---|---|
| **Statement** | The statistically significant interaction term in Model D reflects a true C×mobility interaction, not a collinearity artifact or nonlinearity in the C→recovery function |
| **Evidence For** | Interaction model significantly outperforms additive (ΔR² ≈ +0.10 for ΔC, +0.06 for restoration) in full data. Bootstrapped confidence intervals exclude zero. Survives 5-fold CV and train/test split. |
| **Evidence Against** | **(RD-016)** Fr² curvature model matches or beats interaction for ΔC and restoration (ΔR² = +0.007–0.009). Interaction adds only ΔR² ≤ 0.007 beyond Fr². The interaction coefficient drops 30–65% and becomes non-significant (p > 0.25) when extreme friction levels (0.05, 0.80) are removed. Removing only friction=0.80 collapses the interaction for restoration (p = 0.20) and ΔC (p = 0.14). The interaction is entirely endpoint-driven — the model cannot distinguish interaction from noise without the two extreme friction levels. Partial F-test not significant for interaction beyond Fr². |
| **Status** | **Challenged** — interaction does not survive Fr² inclusion or endpoint removal. The apparent interaction was a nonlinear (quadratic) friction effect. |
| **Type** | Causal / Statistical |

---

## Assumption 15: Residual(C) corresponds to an identifiable latent state variable

| | |
|---|---|
| **Statement** | The friction-independent component of coherence (residual(C) = C − E[C\|friction]) is not merely predictive — it corresponds to a specific, identifiable physical property of the granular system (e.g., contact topology, force-chain heterogeneity, coordination-number structure, or spatial mobility organization) |
| **Evidence For** | **(RD-016)** Residual(C) predicts all three recovery targets: ΔC alone R²=0.13, restoration alone R²=0.27, τ_rec alone R²=0.13. Predictive power survives controlling for all four measured mobility descriptors (ΔR²=+0.10–0.24). Residual(C) is largely orthogonal to MSD, RMS velocity, neighbor turnover, and packing variance (max \|r\|=0.26). Only ~7% of residual(C) variance is shared with any measured descriptor. The signal is reproducible across 60 runs and 6 friction levels. Existence is well-supported; identification is the open problem. **(RD-017)** 22 structural descriptors extracted; max single R²=0.176 (pre_MSE_s1); PLS fails in CV (R²<0). **(RD-018)** 40 additional targeted diagnostics across 4 families (force chain, non-affine displacement, network motifs, alternate binning); none exceed R²=0.142; all force chain, fabric anisotropy, modularity, and non-affine displacement hypotheses are ruled out (all n.s. or very weak). |
| **Evidence Against** | Correlation with packing variance (r=+0.26, p=0.04) is the only link to a known physical variable so far. Residual(C) may proxy an unmeasured variable (grain shape, size distribution, preparation history, or a higher-order mobility statistic not captured by MSD or RMS velocity). Identification requires targeted measurement or simulation diagnostics. **(RD-018)** After testing 69 total variables across all available diagnostic families, Residual(C) remains irreducible to any known granular observable. |
| **Status** | **Existence: Supported. Identity: CHARACTERIZED (RD-8A).** The latent state is **3D** (BIC-optimal): F1=Fluidity (40.7%), F2=Perturbation Response (16.9%), F3=Recovery (13.3%). C is a projection of F1+F2. **RD-9E falsified SP**: binary artifact (SP=1.0 for 99% of systems across 5 domains). All novelty metrics now falsified. The novelty measurement program is complete: no single time-series metric captures fertility. Search target is constraint configuration, not metric. |
| **Type** | Epistemological / Mechanistic |

---

## Assumption 16: Coherence outperforms competitor metrics

| | |
|---|---|
| **Statement** | C provides information about system structure and perturbation response that standard metrics (predictive information, statistical complexity, MSE) do not |
| **Evidence For** | SNR(C) = 2.14 vs SNR(I_pred) = 0.18 vs SNR(C_sigma) = 0.0 vs SNR(MSE) = −0.80. C uniquely detects the perturbation boundary. |
| **Evidence Against** | Only tested on granular system. Competitor metrics may perform differently on other systems or with different parameter choices (e.g., different tau for predictive information). |
| **Status** | **Supported** |
| **Type** | Comparative |

---

## Assumption 17: Reconstruction from partial observations is possible at high C

| | |
|---|---|
| **Statement** | When coherence is high, interaction structure can be recovered from heavily subsampled data |
| **Evidence For** | IF-3 recovers structure at 90% missing interactions and 10× noise injection. |
| **Evidence Against** | Only tested on synthetic systems with known ground truth. Real-world applicability unconfirmed. |
| **Status** | **Supported** (synthetic systems) |
| **Type** | Methodological |

---

## Assumption 18: SFH ontology is necessary for the metric

| | |
|---|---|
| **Statement** | The coherence metric requires acceptance of the Sentient First Hypothesis to be valid or interpretable |
| **Evidence For** | None — the metric is purely mathematical (information theory, no ontology) |
| **Evidence Against** | Metric computation, validation, and interpretation use only standard statistical concepts. Any researcher can apply it without accepting SFH. |
| **Status** | **Not Supported** — metric is ontology-independent |
| **Type** | Meta-scientific |

---

## Assumption 19: Metric validity implies ontology validity

| | |
|---|---|
| **Statement** | If the coherence metric succeeds empirically, this supports the SFH ontology |
| **Evidence For** | None — success of a metric does not confirm the philosophical framework that inspired it |
| **Evidence Against** | Many useful metrics (e.g., Fourier transform, mutual information) were developed under object-first paradigms and work regardless of philosophical commitments. Metrics and ontology are logically independent. |
| **Status** | **Not Supported** — metrics and ontology are separate |
| **Type** | Meta-scientific |

---

## Assumption 20: Recovery metrics capture meaningful system properties

| | |
|---|---|
| **Statement** | ΔC, τ_rec, and restoration are valid measures of system resilience — they capture how well a system maintains interaction structure after perturbation |
| **Evidence For** | Metrics vary systematically with friction (6 levels, consistent ordering). Metrics show expected relationships (larger dip → longer τ_rec). Replicable across 10 replicates per condition. |
| **Evidence Against** | τ_rec is measured at 25-step resolution (sliding window step). Restoration uses the last 10 recovery-time windows, which may miss late-stage dynamics. |
| **Status** | **Supported** |
| **Type** | Methodological |

---

## Assumption 21: Surprise Persistence captures a latent direction independent of fluidity

| | |
|---|---|
| **Statement** | SP (temporal clustering of surprise events) measures a property of granular systems not captured by fluidity, perturbation response, or recovery dynamics |
| **Evidence For** | **(RD-9)** SP: r=0.17 with friction (weak), r=0.18 with C (weak). PCA: SP loads PC3 at 0.92 (other metrics <0.30 on PC3). 5-fold CV: 4D structure stable across all folds, loading std=0.024. SP measures regime persistence — how long the system stays in a surprising state. |
| **Evidence Against** | FA still prefers 3 factors (BIC=1068) — SP doesn't reshape the fundamental factor structure. SP is a single metric (thin evidence for a new direction). SP uses a fixed threshold (90th percentile) — sensitivity unknown. **(RD-9E) SP is a discretization artifact**: SP=1.0 for 100% of granular runs (72 runs, 12 friction levels). SP=1.0 for 99% of systems across 5 domains (coupled Markov, modular, hierarchical, forest, sandpile). SP is binary (1.0 or 2.0), not continuous. SP varies with bin count (coarse-graining dependent). SP is estimator-dependent (sensitive to k, threshold, warmup). |
| **Status** | **FALSIFIED (RD-9E)** — binary artifact, not a measurement |
| **Type** | Measurement / Latent structure |

---

## Summary

| # | Assumption | Type | Status |
|---|------------|------|--------|
| 1 | Higher C → higher resilience | Predictive | **Challenged** |
| 2 | C is causally involved in recovery | Causal | **Unknown** |
| 3 | C is an informative state variable | Epistemological | **Supported** |
| 4 | Interaction structure matters more | Theoretical | **Supported** |
| 5 | Metric is ontology-independent | Meta-scientific | **Supported** |
| 6 | Results generalize beyond granular | Generalization | **Weakly Supported** |
| 7 | Binning preserves structure | Methodological | **Supported** |
| 8 | Sliding windows capture dynamics | Methodological | **Supported** |
| 9 | Perturbation reveals resilience | Methodological | **Supported** |
| 10 | Granular DEM is a valid model | Instrumental | **Supported** |
| 11 | Friction is an adequate mobility proxy | Instrumental | **Supported** |
| 12 | C and mobility are independent | Causal | **Challenged** |
| 13 | Mobility causes recovery | Causal | **Plausible** |
| 14 | C×mobility interaction is genuine | Causal | **Challenged** |
| 15 | Residual(C) → identifiable latent variable | Epistemological / Mechanistic | **Exists: Supported; Identity: CHARACTERIZED (RD-8A). 3D core (Fluidity, Perturbation Response, Recovery). All novelty metrics falsified (RD-9/9E).** |
| 16 | C outperforms competitor metrics | Comparative | **Supported** |
| 17 | Reconstruction at high C | Methodological | **Supported** |
| 18 | SFH ontology necessary for metric | Meta-scientific | **Not Supported** |
| 19 | Metric validity → ontology validity | Meta-scientific | **Not Supported** |
| 20 | Recovery metrics are meaningful | Methodological | **Supported** |
| 21 | SP captures independent latent direction | Measurement / Latent structure | **FALSIFIED (RD-9E)** — binary artifact |
| 22 | Constraints are the fundamental quantity | Ontological | **SUPERSEDED (RD-10A.8)** — topology is more fundamental than constraint set |
| 23 | Topology is the fundamental quantity | Ontological | **SUPERSEDED (RD-10A.9)** — protected distinctions are more fundamental than topology |
| 24 | Protected distinctions are the fundamental quantity | Ontological | **SUPERSEDED (RD-10A.10)** — distinction preservation is more fundamental than the distinctions themselves |
| 25 | Preservation is the fundamental mechanism | Ontological | **CHALLENGED (RD-10A.11)** — construction of new distinction spaces may dominate at higher levels |
| 26 | Distinctions are intrinsic to reality | Ontological | **SUPERSEDED (RD-10A.12)** — distinctions are realized through lenses, not intrinsic |
| 27 | Post-hoc motif detectors measure architectural features | Methodological | **FALSIFIED (RD-10B.3)** — detectors measure time-series properties, not architecture |
| 28 | Motifs are properties of the world | Ontological | **FALSIFIED (RD-10B.0)** — motifs are properties of the world-representation pair |
| 29 | Representations of the same world correspond consistently | Methodological | **CHALLENGED (RD-10B.0A)** — correspondence varies widely across representation pairs |
| 30 | "Same world" has a unified meaning | Ontological | **QUALIFIED (RD-10B.0C)** — "same world" is relative to a purpose; different tasks require different identities |
| 31 | Causal identity is universally applicable | Methodological | **QUALIFIED (RD-10B.0E)** — causal identity is informative only for systems with structured dependencies; trivial for random systems |
| 32 | Criteria are competing definitions of "same world" | Ontological | **FALSIFIED (RD-10B.0E)** — criteria have different domains of applicability; they are tools, not definitions |
| 33 | Stress worlds are neutral observers | Methodological | **FALSIFIED (RD-10B.0F)** — worlds have hidden assumptions that advantage some criteria |
| 34 | Recursion is a genuine junction candidate | Ontological | **SUPPORTED (RD-10B.X)** — the same transformation (fixed_point of self-referential operator) appears independently from both chains and resists further reduction |
| 35 | Constraint is a genuine junction candidate | Ontological | **SUPPORTED (RD-10B.Y)** — the same transformation (reachable states under a bounding rule) appears independently from both chains and resists further reduction |
| 36 | Preservation is a genuine junction candidate | Ontological | **SUPPORTED (RD-10B.Z)** — the same transformation (invariance under operation) appears independently from both chains and resists further reduction |
| 37 | Distinction is a genuine junction candidate | Ontological | **SUPPORTED (RD-10B.W)** — the same transformation (identity from differentiation) appears independently from both chains and resists further reduction |
| 38 | The four junctions are path-independent | Methodological | **SUPPORTED (RD-10B.J2)** — all four junctions appear in all 11 ladders tested. However, path independence is necessary but not sufficient. Vocabulary convergence and compression convergence remain risks. |
| 39 | The four junctions are vocabulary-independent | Methodological | **SUPPORTED (RD-10B.J3)** — all four junctions appear in all 5 vocabularies tested. The forms differ across vocabularies, which is evidence against vocabulary convergence. However, vocabulary independence is also not sufficient. The question of whether the four junctions are independent or projections of a deeper transformation remains open. |
| 40 | The four junctions are independent | Ontological | **FALSIFIED (RD-10B.J4)** — the four junctions form a dependency chain: distinction → constraint → preservation → recursion. They are four phases of a single process, not independent junctions. The true junction is the chain itself. |
| 41 | The four junctions form a linear dependency chain | Ontological | **SUPPORTED (RD-10B.J5)** — the dependency topology is a linear chain with distinction at the root and recursion at the leaf. No cycles. No symmetry. This is a compression: four junctions → one dependency structure. |
| 42 | The four junctions are independent projections | Ontological | **SUPPORTED (RD-10B.J6)** — all four junctions can be generated from a single transformation: distinction (D: X × X → {0,1}). The other three are derived operators. However, the composition rules were chosen by us. The same hidden-source problem applies. |
| 43 | The generator is decomposition-independent | Methodological | **FALSIFIED (RD-10B.J7)** — the specific generator (distinction) was an artifact of the decomposition choice. Different decompositions yield different generators. However, all generators are isomorphic. The genuine structure is the isomorphism class, not any specific realization. |
| 44 | Translation invariants are properties of the structure | Methodological | **PARTIALLY SUPPORTED (RD-10B.J8)** — the convergence structure has genuine invariants (partition, restriction, invariance, fixed point, binary output, subset containment, transformation dependence, self-reference). These survive translation between decompositions. However, they may be properties of the translation itself, not of the underlying structure. |
| 45 | Explanatory migration is a genuine regularity | Methodological | **CHALLENGED (RD-10B.M1)** — migration rate is 100% across 20 audits, but the null model shows migration appears only when methodology changes. Migration may be a methodological artifact, not a genuine regularity. |
| 46 | The progression is hierarchical | Ontological | **FALSIFIED (RD-10B.M2)** — the progression is not Object → Property → Relation → Transformation → Decomposition → Translation. It is Object → Mapping → Object → Mapping. This is an oscillation, not a hierarchy. |
| 47 | Explanation scales with translation | Methodological | **SUPPORTED (RD-10B.M3)** — explanation scales with translation (87.5% vs 72.7%). However, translation never appears without prior comparison. Translation is a downstream effect, not the source. |
| 48 | Explanation scales with comparison | Methodological | **SUPPORTED (RD-10B.M3)** — explanation scales with comparison (82.4% vs 50.0%). Comparison is necessary but not sufficient. |
| 49 | Tension-preservation is the distinguishing factor | Methodological | **SUPPORTED (RD-10B.M5)** — with tension: 82.35% high gain; without tension: 50.00% high gain. Collapse reduces explanatory power from 90% to 67%. |
| 50 | Viewpoint comparison preserves tension; claim comparison causes collapse | Methodological | **SUPPORTED (RD-10B.M6b)** — viewpoint comparison: 0% collapse; claim comparison: 100% collapse. The distinction is perfectly predictive. |
| 51 | Explanatory power arises from interactions, not objects | Ontological | **QUALIFIED (RD-10B.R1, R2)** — in every recorded audit, explanatory gain appeared after interaction. However, the archive is biased toward productive interactions. The abandoned `interaction_first` experiments and empty `interaction_models` directory suggest non-productive interactions existed but were never recorded. The 0.097 correlation between interaction diversity and gain suggests more interactions do not guarantee more explanation. |
| 52 | Persistent novelty requires I+P+N+C (interaction + persistence + novelty + coherence) | Ontological | **SUPPORTED (RD-10B.R3)** — all 14 persistent novelty audits have I+P+N+C. Falsifications (I+C) produce gain but not persistent novelty. The abandoned `interaction_first` experiment had I+P+N+C but no gain — because the interaction never occurred. Possible interaction is not enough; actual interaction is required. |
| 53 | Objects are frozen experience; interactions are flowing experience | Ontological | **PARTIALLY SUPPORTED (RD-10B.R4)** — Model B (interaction-centric) scores highest on raw fit (78 vs 70 for Model C). But Model C (experience-centric) explains persistence and self-emergence better. The archive suggests both are needed: Model B for mechanics, Model C for meaning. |
| 54 | Hierarchical persistence of interaction is the strongest survivor | Ontological | **SUPPORTED (RD-10B.R0R)** — the archive divides cleanly: 5 failures (Level 0-1, nothing persisted) vs 20 successes (Level 3, higher-order structure preserves lower-order structure). The dividing line is persistence vs non-persistence. A structure persists when its interactions generate conditions that preserve its continued existence. |
| 55 | The program was repeatedly discovering the same structures under different names | Historical | **SUPPORTED (RD-HIST.1)** — Historical Reconstruction showed: Persistence (14 studies) and Comparison (7 studies) are the two most common actual loci. The claimed objects kept changing; the loci did not. The migration graph is a linear chain with no cycles. The final compression is: hierarchical persistence of interaction. |
| 56 | The RD-HIST.2A ontology (5 categories) is stable | Methodological | **FALSIFIED (RD-HIST.2B)** — Assignment stability is 0.03-0.04 (very low). All 20 studies are assigned to different categories across three independent clusterings. The categories are interpretation artifacts, not properties of the archive. |
| 57 | Hierarchical persistence of interaction is the strongest survivor | Ontological | **UNDERMINED (RD-HIST.2A, 2B)** — Persistence does not survive blind coding (only 1/10 exact matches). The RD-HIST.2A ontology is an interpretation artifact. The strongest survivor was an interpretation, not an operational description. |
| 58 | The research program may itself function as a hidden fixed variable | Methodological | **PLAUSIBLE / UNDER TEST (RD-DIAG.1)** — RD-DIAG.1 itself holds the research program fixed. Every audit shares the same research culture, intuitions, decomposition habits, mathematical preferences, and notion of explanation. The observer may itself be a hidden fixed variable. Not yet confirmed; deeper fixed variables may exist (human cognition, language, mathematics, embodiment, evolution, consciousness, logic, or something not yet imagined). |

### Risk Heat Map

| Status | Count | Interpretation |
|--------|-------|---------------|
| **Supported** | 11 | Stable foundations |
| **Weakly Supported** | 1 | Needs more evidence |
| **Plausible** | 1 | Preliminary, no counterexamples |
| **PLAUSIBLE / UNDER TEST** | 1 | Research program may be a hidden fixed variable (RD-DIAG.1) |
| **Exists: Supported; Identity: Characterized** | 1 | RD-8A complete; 3D core identified. SP (4th dimension) FALSIFIED by RD-9E. |
| **Sparseness FALSIFIED** | 1 | RD-019 ruled out the leading mechanistic hypothesis |
| **Structural importance FALSIFIED (strong form)** | 1 | RD-020: removing hubs/force-chain backbone did not degrade C or recovery |
| **Challenged** | 3 | Active dispute — highest research value |
| **Unknown** | 1 | No test performed |
| **Not Supported** | 2 | Ontological claims, not empirical |
| **FALSIFIED** | 1 | RD-HIST.2B: assignment stability is very low (0.03-0.04) |
| **UNDERMINED** | 1 | RD-HIST.2A/2B: persistence does not survive blind coding |

### Highest-Value Targets

1. **RD-HIST.2B Audit Complete (METHODOLOGICAL CRISIS)**: The cluster stability audit found that assignment stability is 0.03-0.04 (very low). All 20 studies are assigned to different categories across three independent clusterings. The RD-HIST.2A ontology is an interpretation artifact, not a structure found in the archive. The strongest survivor (hierarchical persistence of interaction) was an interpretation, not an operational description. **Next**: The program is in a methodological crisis. The audit phase is complete. The structure is partially stable at the aggregate level (category count, OCR, variance) but unstable at the individual level (assignment stability). The program needs to determine whether to: (a) return to concrete systems and test aggregate structure, (b) develop methods for recovering structure without imposing categories, or (c) abandon the archive and start fresh.

2. **Assumption 2 (C is causal)**: Unknown. This remains the most consequential open question. The distinction between "C predicts" and "C causes" persists. The residual(C) finding strengthens predictive evidence but does not close the causal gap.

3. **Assumption 14 (Interaction is genuine)**: Challenged (was Unknown). RD-016: interaction does not survive Fr² inclusion (ΔR² ≤ 0.007) or endpoint removal (p > 0.25 without extremes). The interaction hypothesis is substantially weakened. Highest research value has shifted away from this question.

4. **Assumption 1 (Higher C → higher resilience)**: Challenged. The evidence is mixed: C predicts weakly alone but contributes in the nonlinear friction model.
