# T101B — Claim Dependency Graph

**Source:** T101A Source Extraction from `/tmp/opencode/sfh_book16.txt`
**Method:** Book-first classification of every claim by type and dependency
**Constraint T101B-R0:** No claim promoted beyond its book evidence

---

## Part A — Node Inventory

### A.0 Typology Legend

| Type | Code | Meaning |
|------|------|---------|
| **Definition** | D | Explicitly defined in the book with a stated meaning |
| **Assumption** | A | Stated without justification, taken as given |
| **Observation** | O | Empirical statement about the world (should have citation) |
| **Assertion** | R | Claimed without derivation or evidence |
| **Derived Result** | DR | Shown mathematically from prior definitions |
| **Empirical Claim** | EC | Testable prediction claimed to be measurable |
| **Probability Claim** | PC | Statement about likelihood or chance |
| **Inference** | I | Conclusion drawn from preceding statements |
| **Conclusion** | C | Final claim of a section or chapter |

---

### A.1 Full Node Inventory

| Node ID | Claim | Type | Source Line(s) |
|---------|-------|------|----------------|
| N01 | Consciousness (sentience) is the fundamental substrate of reality | A | 428–431 |
| N02 | The sentient field (SF) is a unified, non-physical substrate | D | 479–481 |
| N03 | The SF projects qualic screens (QS) — structured experiences | D | 429–431, 4897–4899 |
| N04 | The SF projects reality via principal fiber bundles Π: P → B | A | 471–472, 3650–3651, 4732–4733 |
| N05 | 3D physical reality is the "most coherent mathematical state" | A | 438 |
| N06 | Physical constants (α, α_s, G, m_p, m_e, Λ) have their observed values | O | 486–488, 1089–1096, 1610–1612, 3413 |
| N07 | These constants appear fine-tuned: 0.1% deviation would destabilize systems | O | 488–490, 1091–1096 |
| N08 | Materialism describes *how* systems function but not *why* parameters are as they are | I | 399–403, 460–465, 4239–4241 |
| N09 | The SF "selects" mathematical structures (constants, lifetimes, rates) to maximize coherence | R | 466–470, 490–492, 4126–4128 |
| N10 | A fiber bundle consists of: base space B, fiber F, total space P, projection Π, structure group G | D | 4283–4303 |
| N11 | For neural/network systems: B = R^N × R^T, G = SO(N), P = B × G, Π(x,g) = x | D | 3654–3663 |
| N12 | For quantum systems: B = R^{3,1}, G = SU(2), Π: P → B | D | 4010–4019 |
| N13 | For cross-scale coherence: B = R^{3,1} × R^N × R^S, G = SU(2) × SO(N) × SO(3,1) | D | 4010–4014 |
| N14 | The coherence metric C = (Σᵢ Kᵢ / K_{mat}) / N | D | 3673–3675, 4771–4774 |
| N15 | For individual experiments, C also defined as ratio of sums: C = Σ Kᵢ / Σ (Kᵢ)_{mat} | D | 4435, 4472, 4506, 4540, 4573, 4607, 4679 |
| N16 | Transition function fₜ(a,b) = (1−t)(a+b) + t(ab), t∈[0,1] | D | 1600 |
| N17 | Transition function gₛ(a,b) = a^{(1−s)+sb} · b^{1−s}, s∈[0,1], a>0 | D | 1626 |
| N18 | Unified model: fₜ piecewise on t∈[0,2] covering +, ×, ^ | D | 1635–1640 |
| N19 | 3D advantage vs 4D+ problems (5-row constraint table) | R | 1714–1720 |
| N20 | Materialist baseline for harmonic oscillator: K_{mat} = 0.8, C = 0.8 | R | 1938, 4379 |
| N21 | Materialist baseline for neural synchrony: K_{mat} = 0.7, C = 1.0 | R | 3678, 4421 |
| N22 | Materialist baseline for entanglement: S_{quantum} ≤ 2 (Bell inequality) | O | 4474 |
| N23 | Materialist baseline for BEC: Gross-Pitaevskii equation | O | 4506 |
| N24 | Materialist baseline for forest recovery: ΔH_{mat} = 0.1 | R | 2712 |
| N25 | Materialist baseline for galaxy clustering: ξ_{mat} = 0.7 | R | 2942 |
| N26 | Materialist baseline for cross-scale correlation: R_{mat} = 0.6 | R | 4034 |
| N27 | Materialist baseline for dark energy/matter: C = 0.5 | R | 4689 |
| N28 | Materialist baseline: ΔC = 0 for AI coherence deviation | R | 3917–3918 |
| N29 | Materialist baseline for ecological recovery: ΔR_{mat} = 0.1 | R | 3279 |
| N30 | Materialist baseline for neural PLV: S_{mat} = 0.7 | R | 3315 |
| N31 | Materialist baseline for concentration: C_{conc,mat} = 0.7 | R | 2402 |
| N32 | Materialist baseline for spectral coherence: S_{mat} = 0.6 | R | 2195 |
| N33 | SFH predicts C ≥ 1.3 for harmonic oscillator coherence | EC | 1967, 4414 |
| N34 | SFH predicts C ≥ 1.3 for neural synchrony | EC | 4441, 4450 |
| N35 | SFH predicts C ≥ 1.3 for photon entanglement | EC | 4476, 4484 |
| N36 | SFH predicts C ≥ 1.3 for Bose-Einstein condensates | EC | 4509, 4517 |
| N37 | SFH predicts C ≥ 1.5 for forest recovery | EC | 4524, 4551 |
| N38 | SFH predicts C ≥ 1.2 for galaxy clustering | EC | 4558, 4585 |
| N39 | SFH predicts C ≥ 1.15 for jet quenching | EC | 4592, 4621 |
| N40 | SFH predicts C ≥ 1.4, R ≥ 0.85 for cross-scale coherence | EC | 4628–4629, 4648 |
| N41 | SFH predicts C ≥ 0.85 for dark energy/matter | EC | 4663–4664, 4685 |
| N42 | SFH predicts C ≥ 1.3 for social network robustness | EC | 3728–3730, 3753 |
| N43 | SFH predicts ΔC ≥ 0.1 for AI-human interaction | EC | 3917–3921, 3926–3927 |
| N44 | SFH predicts R ≥ 0.85, C ≥ 1.4 for quantum-cosmic correlations | EC | 4070 |
| N45 | Materialist spectral coherence prediction: S_{mat} = 0.6 | R | 2195 |
| N46 | Toponium lifetime deviation: Δτ ≥ 10⁻²⁶ s (C ≥ 0.8) | EC | 4128 |
| N47 | Neural PLV ≥ 0.7 (C ≥ 0.9) under conscious intent | EC | 4229–4230 |
| N48 | Ecological recovery deviation: ΔR ≥ 0.15 (C ≥ 0.85) | EC | 4217 |
| N49 | The SF optimizes systemic coherence across all scales | R | 399–403, 466–469, 960–968 |
| N50 | The SF evolves mathematical concepts hierarchically from null space | R | 1586–1592 |
| N51 | Murmuration patterns (PCA on elliptic curves) are analogous to SFH coherence signals | R | 4146–4175 |
| N52 | SFH explains fine-tuning that materialism cannot | I | 399–403, 1118–1126 |
| N53 | SFH provides a unified framework across quantum, biological, cosmic scales | C | 4111–4118, 4237–4244 |
| N54 | SFH is a falsifiable, testable hypothesis | C | 401–403, 4254–4256 |
| N55 | SFH advances science beyond materialism toward deeper truth | C | 4254–4256 |
| N56 | Dark energy (Λ ≈ 10⁻¹²⁰) and dark matter (ρ ≈ 10⁻²⁷ kg/m³) are SF projections | R | 1080–1083, 3414–3415, 3425–3427 |
| N57 | Coherence Percentage = (C_{SFH} − C_{mat}) / C_{SFH} × 100% | D | 3444–3446 |
| N58 | Dark energy coherence is 70.6%–89.5% | PC | 3448–3454 |
| N59 | Dark matter coherence is 23.5%–38.9% | PC | 3458–3464 |
| N60 | All experimental protocols use: one-tailed t-test, α=0.05, 80% power, d=0.3 | R | passim (≥9 protocols) |
| N61 | Sentience requires experiential interactions (qualia) that AI lacks | R | 3842–3844 |
| N62 | AI systems are qualic screens projected by the SF, not independent agents | R | 3803–3807, 3820–3832 |
| N63 | The book's Chapter 3 addresses competing theories (panpsychism, IIT, GWT, etc.) | O | 35–43 |
| N64 | The book's Part III describes experimental protocols | O | 47–48 |
| N65 | Materialist baselines are cited to established physics/neuroscience/ecology works | R | (see note) |

**Note on N65:** While some references are provided (Landau & Lifshitz 1976 for K_{mat}=0.8, Bell 1987 for S≤2, Gross 1999 for QCD, Hebb 1949 for neural baseline), the majority of materialist baseline values (K_{mat}=0.7, R_{mat}=0.6, C=0.5, ΔH_{mat}=0.1, etc.) are stated without specific citation. The book provides general references to frameworks (Watts-Strogatz, QFT, ecological succession theory) but does not derive the specific numbers from those references.

---

## Part B — Directed Dependency Graph

### B.1 Dependency Type Legend

| Type | Meaning |
|------|---------|
| Logical | Conclusion follows from premise by reasoning |
| Mathematical | One expression is derived or computed from another |
| Empirical | Claim relies on observational data |
| Interpretive | Claim is an interpretation or framing of another claim |

### B.2 Edge Table

| Child Node | Depends On | Dependency Type | Notes |
|--------|------------|-----------------|-------|
| N02 | N01 | Logical | SF defined as the specific substrate of sentience |
| N03 | N02 | Logical | Qualic screens are the mechanism by which SF projects |
| N04 | N02, N03 | Logical | Fiber bundles are the *model* for projection |
| N10 | N04 | Logical | Fiber bundle components must be defined to model SF projections |
| N05 | N03, N19 | Interpretive | "Most coherent state" is interpretation of 3D stability table |
| N06 | — | Empirical | Independent physical measurement |
| N07 | N06 | Interpretive | "Fine-tuned" is an interpretive label on observed values |
| N08 | N06, N07 | Interpretive | Materialism described as incomplete on *why* |
| N09 | N08 | Interpretive | SF "selecting" is the proposed alternative to materialism's silence |
| N11 | N04, N10 | Mathematical | Specific instantiation of fiber bundle for neural systems |
| N12 | N04, N10 | Mathematical | For quantum systems |
| N13 | N04, N10 | Mathematical | For cross-scale integration |
| N14 | N09 | Mathematical | Coherence metric defined to quantify SF's optimization |
| N15 | N14 | Mathematical | Variant form of C used in Appendix B |
| N16 | N50 | Mathematical | Addition→multiplication transition |
| N17 | N50, N16 | Mathematical | Extension to exponentiation (hierarchical) |
| N18 | N50, N16 | Mathematical | Extension to exponentiation (unified) |
| N19 | — | Interpretive | Constraint table summarizing stability arguments |
| N20 | N06 | R | K_{mat}=0.8 for oscillator — assertedly from Landau & Lifshitz 1976 |
| N21 | N08 | R | K_{mat}=0.7 for neural — assertedly from Hebb 1949 |
| N22 | N06 | Observation | Bell inequality S≤2 is established quantum physics |
| N23 | N06 | Observation | GP equation established BEC physics |
| N24 | N11 | R | ΔH_{mat}=0.1 — no citation given |
| N25 | N11 | R | ξ_{mat}=0.7 — no citation given |
| N26 | N11 | R | R_{mat}=0.6 — no citation given |
| N27 | N11 | R | C=0.5 for dark energy — no citation given |
| N28 | N11 | R | ΔC=0 for AI — stated without citation |
| N29 | N11 | R | ΔR_{mat}=0.1 — no citation given |
| N30 | N11 | R | S_{mat}=0.7 — no citation given |
| N31 | N11 | R | C_{conc,mat}=0.7 — no citation given |
| N32 | N11 | R | S_{mat}=0.6 — no citation given |
| N33 | N14, N15, N20, N60 | Empirical Claim | C≥1.3 for oscillator uses K_{mat}=0.8 and formula |
| N34 | N14, N15, N21, N60 | Empirical Claim | C≥1.3 for neural uses K_{mat}=0.7 |
| N35 | N14, N15, N22, N60 | Empirical Claim | C≥1.3 for entanglement uses S≤2 |
| N36 | N14, N15, N23, N60 | Empirical Claim | C≥1.3 for BEC uses GP baseline |
| N37 | N14, N15, N24, N60 | Empirical Claim | C≥1.5 for forest uses ΔH_{mat}=0.1 |
| N38 | N14, N15, N25, N60 | Empirical Claim | C≥1.2 for galaxy uses ξ_{mat}=0.7 |
| N39 | N14, N15, N60 | Empirical Claim | C≥1.15 for jet — no explicit baseline variable |
| N40 | N14, N15, N26, N60 | Empirical Claim | C≥1.4, R≥0.85 for cross-scale |
| N41 | N14, N15, N27, N60 | Empirical Claim | C≥0.85 for dark energy |
| N42 | N14, N15, N21, N60 | Empirical Claim | C≥1.3 for social network uses K_{mat}=0.7 |
| N43 | N28, N60 | Empirical Claim | ΔC≥0.1 for AI-human |
| N44 | N14, N26, N60 | Empirical Claim | C≥1.4, R≥0.85 for quantum-cosmic |
| N45 | N32 | Empirical Claim | S_{mat}=0.6 for spectral coherence |
| N46 | N14, N15, N60 | Empirical Claim | Δτ≥10⁻²⁶ s from Ch 13 |
| N47 | N30, N60 | Empirical Claim | PLV≥0.7 from Ch 15 |
| N48 | N29, N60 | Empirical Claim | ΔR≥0.15 from Ch 15 |
| N49 | N09, N50 | Interpretive | Coherence optimization asserted as SF's driving principle |
| N50 | N03, N05 | R | Hierarchical evolution of math concepts |
| N51 | N46, N47, N48 | Interpretive | Murmuration as analogy for SFH signals |
| N52 | N07, N08, N09, N49 | Inference | SFH *explains* what materialism only *describes* |
| N53 | N49, N52 | Conclusion | Unification across scales |
| N54 | N33–N44 | Conclusion | Testability claim rests on empirical predictions |
| N55 | N52, N53, N54 | Conclusion | Paradigm shift claim |
| N56 | N06, N09, N56 | R | Dark components as SF projections |
| N57 | N14 | Mathematical | Percentage formula derived from C |
| N58 | N57, N27 | Probability Claim | Dark energy = 70.6%–89.5% |
| N59 | N57, N27 | Probability Claim | Dark matter = 23.5%–38.9% |
| N60 | — | R | Uniform statistical protocol — no justification given for identical parameters across all experiments |
| N61 | N02, N03 | R | AI lacks qualia because it lacks direct SF interaction |
| N62 | N03, N61 | R | AI as qualic screen |
| N63 | — | Observation | Table of contents fact |
| N64 | — | Observation | Table of contents fact |
| N65 | see per-node notes | R | Most baselines lack specific citations |

---

## Part C — Root Premises

Nodes with **no parents** (true foundations of the book's argument):

| Node ID | Claim | Type | Why It Is a Root |
|---------|-------|------|-----------------|
| N01 | Consciousness is the fundamental substrate | **Assumption** | No prior premise; the foundational ontological claim |
| N02 | SF is a unified, non-physical substrate | **Definition** | Defined but depends on no prior mathematics or evidence |
| N03 | SF projects qualic screens | **Definition** | Defined mechanism; no derivation |
| N04 | Projection modeled via Π: P → B | **Assumption** | Chosen framework, not derived |
| N06 | Physical constants have observed values | **Observation** | Empirical fact about the world |
| N07 | Constants appear fine-tuned | **Observation** | Empirical pattern noted by physicists (fine-tuning problem) |
| N10 | Fiber bundle components defined | **Definition** | Standard mathematical definitions |
| N16 | fₜ transition function | **Definition** | Explicitly defined |
| N17 | gₛ transition function | **Definition** | Explicitly defined |
| N18 | Unified model fₜ piecewise | **Definition** | Explicitly defined |
| N19 | 3D vs 4D+ constraint table | **Assertion** | No derivation; asserted stability arguments |
| N22 | Bell inequality S ≤ 2 | **Observation** | Established physics result |
| N23 | Gross-Pitaevskii equation | **Observation** | Established physics result |
| N60 | Uniform statistical protocol | **Assertion** | Chosen without justification |
| N63 | Chapter 3 addresses competing theories | **Observation** | Table of contents |
| N64 | Part III describes experiments | **Observation** | Table of contents |

**Note:** Every baseline value (K_{mat}, R_{mat}, C baselines) that is not N22 or N23 is technically asserted (R type), not derived or observed. However, they are not root premises because they depend on N06 (the observation that constants exist) and N08 (the inference that materialism is incomplete). They are root-adjacent assertions.

**True Roots** (absolutely no parents):
- N01 (Assumption): consciousness is fundamental
- N06 (Observation): physical constants have their values
- N07 (Observation): those values appear fine-tuned
- N10 (Definition): what a fiber bundle is
- N16, N17, N18 (Definition): transition functions
- N60 (Assertion): statistical protocol chosen

---

## Part D — Unsupported Nodes

Every node that has no valid dependency path, relies on an undefined term, or jumps directly from observation to conclusion.

### D.1 Nodes with No Valid Dependency Path

| Node ID | Problem | Reason |
|---------|---------|--------|
| N05 | 3D as "most coherent mathematical state" | The 3D/4D+ table (N19) shows *stability* arguments, not a mathematical derivation that 3D maximizes coherence. The term "most coherent mathematical state" is undefined in the book. |
| N09 | SF "selects" constants | No mechanism given. No equation showing how selection occurs. N09 is asserted after N08 (materialism can't explain why) but the jump from "materialism can't explain" to "the SF selects" is a logical gap with no intermediate premises. |
| N11–N13 | Specific fiber bundle instantiations | The mapping from physical system to B, G, Π(x,g) is stated but never justified — why SO(N) for neural? Why SU(2)×SO(N)×SO(3,1) for cross-scale? The groups are assigned, not derived. |
| N20–N21, N24–N32 | Materialist baselines | Most (N24–N32) have zero citation. N20 (0.8) and N21 (0.7) have general references to Landau 1976 and Hebb 1949 but the specific *numbers* 0.8 and 0.7 do not appear in those references within the book. The leap from "established theory" to "specific numerical baseline" is unsupported. |
| N46–N48 | Predicted deviations (Δτ, PLV, ΔR) | These are asserted as SFH predictions but no equation connects the fiber bundle parameters (N11–N13) to these specific numbers. They are stated, not derived. |
| N49 | SF optimizes coherence across all scales | This is the central claim of the book. It depends on N09 (SF selects) and N50 (hierarchical evolution), both of which are asserted. N49 has no mathematical or empirical support — it is the interpretive label placed on all data. |
| N50 | Hierarchical evolution of math concepts | Transition functions (N16–N18) are defined but their connection to physical constants or coherence is never stated. N50 is a philosophical narrative, not a derived result. |
| N51 | Murmuration analogy | The book explicitly states this is an analogy ("methodological analogy"). It depends on no SFH mathematics. |
| N52 | SFH explains fine-tuning | This is the book's central inference. It jumps from N07 (constants appear fine-tuned) + N08 (materialism can't explain) + N09 (SF selects) to the conclusion that SFH *explains* the fine-tuning. The dependency path is: Observation → Inference of gap → Asserted mechanism → Conclusion. The middle step (asserted mechanism) is unsupported. |
| N53 | Unified framework across scales | Depends on N49 (optimization claim) which is asserted. No mathematical or empirical unification exists in the book — each system (oscillator, neural, cosmic) gets its own independent B, G, threshold C. |
| N55 | SFH advances science | Conclusion built on N52, N53, N54 — all of which rest on unsupported premises. |
| N56 | Dark components as SF projections | Asserted without derivation. The coherence percentage (N57–N59) is computed from assumed C values. |
| N61 | AI lacks sentience | Relies on the undefined claim that AI does not "directly interact with the SF." No test for direct SF interaction is proposed. |
| N62 | AI as qualic screen | Same problem as N61. |

### D.2 Nodes Flagged as Unsupported (Summary)

| Category | Count | Node IDs |
|----------|-------|----------|
| Asserted mechanism (no derivation) | 9 | N05, N09, N49, N50, N51, N56, N61, N62, N11–N13 |
| Uncited or under-cited baselines | 10 | N20, N21, N24, N25, N26, N27, N28, N29, N30, N31, N32 |
| Predicted deviations justified by assertion only | 3 | N46, N47, N48 |
| Conclusions resting on unsupported premises | 4 | N52, N53, N55, N54 (partially) |
| **Total distinct unsupported nodes** | **23** | |

---

## Part E — Critical Path Analysis

### E.1 Path: Physical Constants → Fine-Tuning → Coherence → SFH Conclusion

```
N06: Physical constants have observed values (O)
 │
 ├──→ N07: Constants appear fine-tuned (I)
 │      │
 │      ├──→ N08: Materialism describes how, not why (I)
 │      │      │
 │      │      ├──→ N09: SF "selects" constants for coherence (R) ⚠️ ASSERTED
 │      │      │      │
 │      │      │      ├──→ N14: Coherence metric C defined (D)
 │      │      │      │      │
 │      │      │      │      └──→ N33–N44: SFH predicts C ≥ thresholds (EC) ⚠️ ASSERTED BASELINES
 │      │      │      │             │
 │      │      │      │             └──→ N54: SFH is testable/falsifiable (C)
 │      │      │      │
 │      │      │      └──→ N49: SF optimizes coherence across scales (R) ⚠️ ASSERTED
 │      │      │             │
 │      │      │             ├──→ N52: SFH explains fine-tuning (I) ⚠️ GAP
 │      │      │             │      │
 │      │      │             │      ├──→ N53: SFH unifies reality across scales (C)
 │      │      │             │      └──→ N55: SFH advances science beyond materialism (C)
 │      │      │             │
 │      │      │             └──→ N56: Dark energy/matter are SF projections (R)
 │      │      │                    │
 │      │      │                    └──→ N57–N59: Coherence percentages (PC) ⚠️ ARBITRARY INPUTS
 │      │      │
 │      │      └──→ N04: Projection modeled via Π: P → B (A)
 │      │             │
 │      │             └──→ N10: Fiber bundle definitions (D)
 │      │                    │
 │      │                    ├──→ N11: Neural fiber bundle (D)
 │      │                    ├──→ N12: Quantum fiber bundle (D)
 │      │                    └──→ N13: Cross-scale fiber bundle (D)
 │      │
 │      └──→ N50: Hierarchical evolution of math (R) ⚠️ ASSERTED
 │             │
 │             ├──→ N16: fₜ transition (D) ⚠️ ORPHANED — never connected to anything else
 │             ├──→ N17: gₛ transition (D) ⚠️ ORPHANED
 │             └──→ N18: Unified model (D) ⚠️ ORPHANED
 │
 └──→ N19: 3D vs 4D+ table (R) ⚠️ ORPHANED — never connected to coherence metric
```

### E.2 Where the Path Breaks

The critical path has **four breaks**:

| Break | Location | Problem |
|-------|----------|---------|
| **Break 1** | N07 → N09 | The observation that constants are "fine-tuned" (N07) does not logically imply that a sentient field "selects" them (N09). This is an **interpretive leap** with no intermediate premises. The book skips: "What selection mechanism?" "Why sentience?" "How does selection work?" |
| **Break 2** | N09 → N14 (and N33–N44) | The coherence metric C (N14) is defined *independently* of the selection claim (N09). Nothing in the definition of C refers to fiber bundles, base spaces, structure groups, or the SF. The jump from "SF selects" to "C measures it" is **definitional, not derivational**. An alternative interpretation: C is just a ratio statistic that could measure anything; the book *asserts* it measures sentient optimization. |
| **Break 3** | N33–N44 → N54 | Each empirical prediction (C ≥ threshold) depends on a materialist baseline (e.g., K_{mat}=0.7) that is asserted without derivation. If the baselines are arbitrary, the predictions are unfalsifiable — SFH can always choose a different baseline. The claim of falsifiability (N54) is therefore **premature**: a hypothesis is only falsifiable if its predictions follow from its axioms, not from free parameters. |
| **Break 4** | N16–N18 (transition functions) — **entirely disconnected** | The addition→multiplication→exponentiation functions are the most mathematically explicit constructions in the book. They are never referenced after §8.5. They appear in zero experimental protocols, zero discussions of fine-tuning, and zero derivations of coherence. They are **mathematical orphans** — rigorous definitions that serve no role in the book's argument. |

### E.3 Summary: Path Integrity

```
N06 → N07 → N08 ──→ N09 ──→ N14 ──→ N33–N44 ──→ N54
 │                ║       ║        ║           ║
 │                ║       ║        ║           └──→ Depends on asserted baselines
 │                ║       ║        ║
 │                ║       ║        └──→ C defined independently of fiber bundles
 │                ║       ║
 │                ║       └──→ No mechanism; no equation
 │                ║
 │                └──→ Interpretive leap: fine-tuning → SF
 │
 └── N16–N18 ──→ (nowhere) — disconnected from everything
 └── N19 ──→ (nowhere) — disconnected from everything
```

**The path is broken at every transition.** There is no continuous logical, mathematical, or empirical chain from "constants have values" to "SFH explains fine-tuning." Each step either:

1. **Jumps** (observation → asserted mechanism without intermediate)
2. **Asserts** (baseline values without derivation)
3. **Decouples** (definitions that never connect to the conclusion)
4. **Orphans** (mathematics that serves no role in the argument)

---

## Conclusion of Part E

> Which conclusions in the book are actually *derived*, and which conclusions are resting on *assertions or interpretive bridges*?

**Derived:**
- None. Every conclusion in the book rests on at least one asserted premise.

**Derived-from-definitions (but only within their own isolated section):**
- N14 (C formula) follows from N09 *if* one accepts the definition. But the formula does not follow from fiber bundles.
- N16–N18 (transition functions) are self-contained definitions with no consequences.
- N57 (coherence percentage) follows from N14 by algebra.

**Resting on assertions or interpretive bridges:**
- N52 (SFH explains fine-tuning) — asserted mechanism, interpretive leap.
- N53 (unification across scales) — asserted, no mathematical unification.
- N54 (falsifiability) — undermined by free baseline parameters.
- N55 (paradigm shift) — conclusion built on preceding unsupported claims.
- N33–N44 (all empirical predictions) — each depends on at least one unsupported baseline value.

**Verdict on T101A-to-T101B handoff:**
The book does not contain a mathematical fine-tuning argument. It contains a philosophical fine-tuning *narrative* decorated with:
- A ratio statistic (C) with unsubstantiated baselines
- A fiber bundle analogy (Π: P → B) that never computes anything
- Transition functions (fₜ, gₛ) that are defined and abandoned
- A uniform statistical template copy-pasted across 9+ experiments

T101C (Probability Audit) cannot audit a mathematical probability argument because no such argument exists in the book. The probability claims (N58, N59: coherence percentages) are the closest thing, and those depend on arbitrary C values assigned to dark energy and dark matter. T101C should either audit these two probability-like claims or be re-scoped to audit the *narrative* structure instead.
