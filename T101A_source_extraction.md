# T101A Source Extraction: SFH Book Mathematical Statements

**Source:** `/tmp/opencode/sfh_book16.txt` (5267 lines)
**Extractor:** Director's protocol, book-first evidence rule
**Status:** Complete — every mathematical statement in the book cataloged

---

## 0. Inventory of All Mathematical Formulas in the Book

The book contains exactly these mathematical formulas (listed in order of appearance):

| # | Formula | Location | Context |
|---|---------|----------|---------|
| 1 | fₜ(a,b) = (1−t)(a+b) + t(ab) | Line 1600, §8.5 | Addition→multiplication transition, t∈[0,1] |
| 2 | gₛ(a,b) = a^{(1−s)+sb} · b^{1−s}, s∈[0,1], a>0 | Line 1626, §8.5 | Multiplication→exponentiation (hierarchical model) |
| 3 | fₜ(a,b) = { (1−t)(a+b)+t(ab) if 0≤t≤1; (2−t)(ab)+(t−1)(a^b) if 1≤t≤2 }, a>0 | Lines 1635–1640, §8.5 | Unified model: addition→multiplication→exponentiation |
| 4 | C = (Σᵢ Kᵢ/K_{mat}) / N | Lines 3673–3675, §19.3.2; also lines 4771–4774, §C.4 | **Primary coherence metric** — used in every experimental protocol |
| 5 | K = Cov(F₁,F₂)/(σ_{F₁}σ_{F₂}) | Lines 3700–3703, §19.4.2 | Neural synchrony index |
| 6 | K = 3×triangles / triads | Lines 3738–3739, §19.5.2 | Social network clustering coefficient |
| 7 | ΔC = C_{focused} − C_{distracted} | Line 3917, §20.5.2 | AI coherence deviation |
| 8 | R = Cov(E,K)/(σ_E σ_K) | Lines 4056–4057, §21.4.2 | Cross-scale correlation coefficient |
| 9 | C = Σ_i (synchrony_i) / Σ_i (synchrony_i)_{mat} | Line 4435, §B.2 | Neural coherence (alternate form) |
| 10 | C = Σ_i S_i / Σ_i (S_i)_{quantum} | Line 4472, §B.3 | Entanglement coherence, (S_i)_{quantum} ≤ 2 |
| 11 | C = Σ_i ΔR_i / Σ_i (ΔR_i)_{GP} | Line 4506, §B.4 | BEC coherence, Gross-Pitaevskii baseline |
| 12 | C = Σ_i ΔH_i / Σ_i (ΔH_i)_{mat} | Line 4540, §B.5 | Forest recovery coherence |
| 13 | C = Σ_i clusters_i / Σ_i (clusters_i)_{mat} | Line 4573, §B.6 | Galaxy clustering coherence |
| 14 | C = Σ_i quenching_i / Σ_i (quenching_i)_{QCD} | Line 4607, §B.7 | Jet quenching coherence |
| 15 | C = Σ_i patterns_i / Σ_i (patterns_i)_{mat} | Line 4679, §B.9 | Dark energy/matter coherence |

**Critical note:** Formulas 4 and 9–15 are structurally identical (ratio of sums). The book never defines a single, consistent formula; it rewrites the same pattern with different variable names per chapter. There is ONE metric (C) with NINE stated versions.

---

## Table 1: Physical Constants

All values are stated qualitatively — the book never derives any constant from first principles.

| Constant | Symbol | Book Value | Source Line(s) | Context in Book |
|----------|--------|------------|----------------|-----------------|
| Fine-structure constant | α | ≈ 1/137 | 962, 1611, 4845 | Electromagnetic interaction strength; SFH tests whether SF tunes it |
| Strong coupling constant | α_s | ≈ 0.118 | 3865, 4122, 4125 | Nuclear stability; SFH claims SF selects this value |
| Gravitational constant | G | ≈ 6.6743×10^{-11} m³ kg⁻¹ s⁻² | 1611 | Planetary orbits; no equation links to SFH |
| Proton mass | m_p | ≈ 1.6726×10^{-27} kg | 1610 | Stable nuclei; no equation links to SFH |
| Electron mass | m_e | ≈ 9.1094×10^{-31} kg | 1612 | Molecular bonds; no equation links to SFH |
| Cosmological constant | Λ | ≈ 10^{-120} (natural units) | 3413 | Dark energy; noted as fine-tuned |
| Muon lifetime | τ | ≈ 2.2×10^{-6} s | 3239, 4873 | Cross-scale coherence test |
| Planck constant | ℏ | Implied (ℏω at line 1993) | — | Used in quantum formulas, never stated numerically |
| Fermi constant | G_F | Not stated numerically | — | Mentioned qualitatively in Ch 13 context |
| Boltzmann constant | k_B | Not stated numerically | — | Never stated |

**Assessment:** The book mentions constants qualitatively to motivate SFH. It contains NO equations that compute any constant from the sentient field or any other first principle. All values are taken from known physics without modification.

---

## Table 2: Probability Claims

Every claim concerns deviations from assumed materialist baselines. The book gives no derivation or citation for any baseline value.

| Claim | Stated Baseline | SFH Prediction | Source Line(s) | Chapter |
|-------|----------------|----------------|----------------|---------|
| Harmonic oscillator coherence | C = 0.8 (K_{mat} = 0.8) | C ≥ 1.3 | 1957, 4379 | 7, B.1 |
| Energy level spacing | ΔE_{mat} = ℏω | — | 1993 | 7 |
| Neural synchrony | C = 1.0 (synchrony_{mat}) | C ≥ 1.3 | 2157, 4421 | 8, B.2 |
| Spectral coherence | S_{mat} = 0.6 | — | 2195 | 8 |
| Concentration coherence | C_{conc,mat} = 0.7 | — | 2402 | 8 |
| Photon entanglement (CHSH) | S_{quantum} ≤ 2 | C ≥ 1.3 | 4472, 4474 | 9, B.3 |
| Bose-Einstein condensate | C = 1.0 (GP baseline) | C ≥ 1.3 | 2561, 4491 | 10, B.4 |
| Forest recovery (ΔH) | ΔH_{mat} = 0.1, C = 1.0 | C ≥ 1.5 | 2712, 4540 | 11, B.5 |
| Forest recovery (alternate) | ΔH_{mat} = 0.1 | C ≥ 1.5 | 2905 | 11 |
| Galaxy clustering | ξ_{mat} = 0.7, C = 1.0 | C ≥ 1.2 | 2942, 4576 | 12, B.6 |
| Toponium decay (BR) | BR_{mat} = 0.998 | — | 3136 | 13 |
| Muon lifetime | decay constant λ = 1/(2.2×10⁻⁶) | — | 3239 | 14 |
| Ecosystem recovery (ΔR) | ΔR_{mat} = 0.1 | — | 3279 | 15 |
| Neural synchrony (PLV) | S_{mat} = 0.7 | — | 3315 | 15 |
| Neural synchrony (learning) | K_{mat} = 0.7 | K ≥ 0.9, C ≥ 1.3 | 3678, 3717 | 19 |
| Social network clustering | K_{mat} = 0.7 | K ≥ 0.9, C ≥ 1.3 | 3743, 3753 | 19 |
| AI coherence deviation | ΔC = 0 | ΔC ≥ 0.1 | 3917, 3927 | 20 |
| Cross-scale correlation | R_{mat} = 0.6 | R ≥ 0.85, C ≥ 1.4 | 4034, 4070 | 21 |
| Dark energy/matter patterns | C = 0.5 | C ≥ 0.85 | 4689, 4713 | 15, B.9 |

**Statistical parameters** (repeated identically in every protocol):
- Test: one-tailed t-test
- α = 0.05
- Power = 80%
- Effect size d = 0.3 (exceptions: d = 0.2 in Ch 8 neural, d = 0.1 in Ch 14 muon)

**Assessment:** Every materialist baseline is asserted without derivation or citation. No protocol justifies why a specific numerical threshold (0.7, 0.6, 0.5, etc.) is the "materialist" prediction. The same statistical setup (one-tailed t-test, α=0.05, 80% power, d=0.3) is copy-pasted across all 9+ protocols without adjustment for different measurement scales.

---

## Table 3: Coherence

The book's central mathematical quantity is the coherence metric C.

| Definition | Formula | Location | Notes |
|-----------|---------|----------|-------|
| Generic coherence | C = (Σᵢ Kᵢ/K_{mat}) / N | Lines 3673–3675, 4771–4774 | Primary form; Kᵢ is any system-specific observable |
| Cross-scale correlation | R = Cov(E,K)/(σ_E σ_K) | Lines 4056–4057 | Pearsons correlation between quantum+c cosmic observables |
| Synchrony index | K = Cov(F₁,F₂)/(σ_{F₁}σ_{F₂}) | Lines 3700–3703 | Covariance of firing rates normalized by std dev |
| Clustering coefficient | K = 3×triangles/triads | Lines 3738–3739 | Standard network clustering coefficient |
| Coherence deviation | ΔC = C_{focused} − C_{distracted} | Line 3917 | Used in AI experiment |
| Coherence percentage | (C − 1) × 100% | Lines 3445–3464 | Only used in Ch 15 dark energy/matter discussion |
| Forest coherence % | Example: (0.85/0.5) × 100% ≈ 70.6% to 89.5% | Lines 3454–3464 | Dark energy; dark matter gives 23.5%–38.9% |

**C metric inconsistencies across the book:**
- In main text (§19.3.2, §C.4): C = (Σᵢ Kᵢ/K_{mat}) / N — ratio of means
- In Appendix B: C = Σᵢ Kᵢ / Σᵢ (Kᵢ)_{mat} — ratio of sums
- These are NOT mathematically equivalent unless N cancels (which it does not, because the denominator is a sum over i, not N × K_{mat})
- SFH thresholds vary: C ≥ 1.3 (Ch 7–10), C ≥ 1.5 (Ch 11), C ≥ 1.2 (Ch 12), C ≥ 1.15 (Ch 13), C ≥ 1.4 (Ch 14, 21), C ≥ 0.85 (Ch 15)

**Fiber bundle framework:**
- Π: P → B, principal fiber bundle (line 3650, 4006, 4732)
- Base space B varies: R^N × R^T (neural/network), R^{3,1} (spacetime), R^S × R^T (ecological), R^{3,1} × R^N × R^S (cross-scale)
- Structure group G varies: SO(N) (neural), U(1) (BEC/phase), SU(2) (quantum), SU(2)×SO(N)×SO(3,1) (cross-scale)
- The book never writes an explicit expression for the projection map Π beyond Π(x,g) = x
- The book never writes an expression for how the sentient field "selects" parameters

**Assessment:** The coherence metric is the ONLY quantitative prediction mechanism in the book. However, its definition shifts between chapters, its materialist baselines are unsubstantiated, and the fiber bundle framework is used qualitatively (as analogy, not computation).

---

## Table 4: Fertility

| Finding | Source |
|---------|--------|
| The word "fertility" does not appear anywhere in the book | grep returns 0 matches across all 5267 lines |
| There is NO definition, equation, or metric called "fertility" | Confirmed by full-text search |
| There is NO fertility function, fertility landscape, or fertility-adjacent concept | Confirmed by full-text search |
| There is NO connection between fertility and coherence | Concept absent |
| There is NO relationship between fertility and fine-tuning | Concept absent |

**Assessment:** The fertility concept is entirely a Python repository invention with zero basis in the book. Every claim about fertility in the SFH Python repo (including integer partitions, Hardy-Ramanujan asymptotics, exponential/combinatorial fertility definitions) is unsupported by the book text and must be marked as a post-hoc addition in T101C.

---

## Table 5: Fine-Tuning Argument Chain

The book's argument has the following logical structure, extracted verbatim:

### Premises (stated in book)

1. **Physical constants are fine-tuned** (lines 399, 960–962, 1099, 3413): "SFH addresses why reality exhibits fine-tuned stability — why physical constants... have values that allow life."
2. **Materialism describes how but not why** (lines 4111–4118, 4239–4244): Materialist models "fail to explain why coupling constants... are fine-tuned to enable stable nuclear processes."
3. **SF projects reality as qualic screens** (passim): The sentient field structures experience via fiber bundle projections.
4. **SF optimizes for coherence** (lines 1609–1614, 4126–4128, 4241–4243): "The SF selects these parameters to maximize coherence."

### Claimed Evidence (stated in book)

| Observable | Predicted Deviation | SFH Claims | Materialist Limit | Chapter |
|-----------|-------------------|------------|-------------------|---------|
| Toponium lifetime | Δτ ≥ 10⁻²⁶ s | C ≥ 0.8 | QFT prediction | 13, 22 |
| Neural phase-locking | PLV ≥ 0.7 | C ≥ 0.9 | PLV ≤ 0.5 | 15, 22 |
| Ecological recovery | ΔR ≥ 0.15 | C ≥ 0.85 | Random models | 15, 22 |
| Forest recovery rate | ΔH deviation | C ≥ 1.5 | ΔH_{mat} = 0.1 | 11 |

### Logical Gaps (identified by audit)

| Gap | Description | Severity |
|-----|-------------|----------|
| G1 | No equation links the fiber bundle structure group G to any specific constant value | Critical |
| G2 | No mechanism explains HOW the SF "selects" or "tunes" parameters | Critical |
| G3 | Materialist baselines (0.7, 0.6, 0.5, 0.8) are asserted without citation or derivation | Critical |
| G4 | Coherence metric C has inconsistent definitions across chapters (ratio-of-means vs ratio-of-sums) | High |
| G5 | The SFH coherence thresholds (1.3, 1.5, 1.2, 1.15, 1.4, 0.85, 0.8, 0.9) vary without explanation | High |
| G6 | Statistical power analysis is identical (α=0.05, 80%, d=0.3) for all experiments despite different scales | Medium |
| G7 | The transition functions (§8.5, addition→multiplication→exponentiation) are never connected to the fine-tuning argument | High |
| G8 | The murmuration/AI pattern-recognition discussion (§22.2) is a methodological analogy, not evidence | Medium |

### The Argument in Minimal Form

```
1. Constants have specific values (α≈1/137, α_s≈0.118, etc.).   [observation, accepted physics]
2. Materialism describes how these arise but not why they are as they are.   [book's claim]
3. SFH posits a sentient field that projects reality via fiber bundles.   [book's ontology]
4. Coherence metric C measures deviation from materialist baselines.   [book's metric]
5. Predicted C > 1 indicates sentient optimization.   [book's interpretation]
6. Therefore: SFH explains the fine-tuning that materialism cannot.   [book's conclusion]
```

**Critical gap:** Step 3 does not connect to Step 4 mathematically. The fiber bundle framework Π: P → B is never used to compute C, never constrains K_{mat}, and never generates thresholds.

---

## Special Audit: Unsupported Mathematical Jumps

Every mathematical statement in the book that is asserted without derivation, citation, or logical link.

### JUMP-1: Materialist Baselines (K_{mat}, R_{mat}, C baselines)

The book states at least 7 distinct materialist baseline values (0.5, 0.6, 0.7, 0.8, 1.0, ℏω, 0.1) without any derivation or peer-reviewed citation for the specific numerical value. For example:
- "K_{mat} = 0.7" for neural synchrony (line 3678): No reference to any neuroscience paper establishing 0.7 as the materialist expectation.
- "R_{mat} = 0.6" for cross-scale correlation (line 4034): No reference or derivation.
- "C = 0.5" baseline for dark energy (line 4689): No reference.

### JUMP-2: Fiber Bundle → Coherence Connection

The book defines Π: P → B (fiber bundle) and C = (Σ Kᵢ/K_{mat})/N (coherence metric) but never writes an equation linking them. The fiber bundle is never used to compute, constrain, or predict C. The two concepts are presented in separate sections and never connected mathematically.

### JUMP-3: Structure Group → Physical Constant Connection

The book states G = SO(N), U(1), SU(2) etc. for different systems but never writes an equation showing how these groups determine or constrain physical constants (α, α_s, G, etc.). The structure groups are purely descriptive analogies.

### JUMP-4: Transition Functions Never Used

The addition→multiplication→exponentiation functions (§8.5, lines 1600–1654) are the most explicit mathematical construction in the book. They are never referenced again after §8.5. They are never connected to:
- Physical constants
- Coherence metric C
- Fine-tuning argument
- Any experimental protocol

### JUMP-5: C Metric Definition Inconsistency

The main text defines C = (Σ Kᵢ/K_{mat})/N (mean of ratios). Appendix B defines C = Σ Kᵢ / Σ (Kᵢ)_{mat} (ratio of sums). These give different numerical results unless all K_{mat} are equal and N=1. The book uses them interchangeably without acknowledgment.

### JUMP-6: Baseline Values Differ Without Explanation

Different chapters use different materialist baselines for C:
- Chapters 7–10, 12: baseline C = 1.0
- Chapter 7 (B.1): baseline C = 0.8
- Chapter 11: baseline C = 1.0 but threshold C ≥ 1.5 (higher than others)
- Chapter 15: baseline C = 0.5
- No chapter explains WHY its baseline differs from others.

### JUMP-7: Chapter 3 Has Zero Mathematical Content

Chapter 3 (§§3.1–3.3, "Beyond Materialism") claims SFH has a mathematical basis but contains:
- 0 equations
- 0 figures
- 0 data tables
- 0 citations to mathematical literature
This is the chapter the SFH Python repo README falsely claims contains "several figures" — but the book chapter has no figures at all.

### JUMP-8: No Universe Probability Calculation

The book never computes a probability for the universe having its observed constants. There is no:
- P(universe | chance) calculation
- Anthropic probability
- Likelihood ratio between SFH and materialism
- Bayes factor
The Python repo's "1 in 10^84" claim (from T100B audit) has no basis in the book.

### JUMP-9: No Correlation Between Different Experiments

Though the book claims cross-scale coherence (Ch 14, 21), it does not compute correlations between:
- The 9 separate experimental protocols
- Different physical constants
- Different coherence thresholds
Each experiment is treated independently.

### JUMP-10: Coherence Percentage (§15) Uses Different Formula

Chapter 15 (lines 3445–3464) abruptly uses "Coherence Percentage = (C − 1) × 100%" whereas every other chapter uses C directly. The dark energy/matter percentage calculation (70.6%–89.5%, 23.5%–38.9%) uses numeric values that do not match the stated thresholds.

---

## Summary: What the Book Actually Contains vs. What the Python Repo Claims

| Mathematical Object | In Book? | In Python Repo? | Match? |
|-------------------|----------|-----------------|--------|
| Coherence metric C | Yes (9+ forms) | Yes | Partial (repo uses one version) |
| Fiber bundle Π: P → B | Yes (qualitative) | Yes (partial) | Partial |
| Structure groups G | Yes (U(1), SU(2), SO(N)) | No | N/A |
| Transition functions fₜ, gₛ | Yes (never reused) | No | N/A |
| 3D/4D+ constraint table | Yes (descriptive) | No | N/A |
| Physical constant values | Yes (quoted, never derived) | Yes | N/A (both quote standard values) |
| Fine-tuning argument | Yes (qualitative) | Yes | Partial |
| Integer partitions | No | Yes | **FALSE CLAIM** |
| Hardy-Ramanujan formula | No | Yes | **FALSE CLAIM** |
| Fertility concept | No | Yes | **FALSE CLAIM** |
| Pareto distributions | No | Yes | **FALSE CLAIM** |
| Universe probability | No | Yes | **FALSE CLAIM** |
| Fertility landscape | No | Yes | **FALSE CLAIM** |
| Multiverse sampling | No | Yes | **FALSE CLAIM** |
| Chapter 3 figures | No (0 figures) | Claims "several figures" | **FALSE CLAIM** |

**Verdict:** The book contains ≈15 explicit mathematical statements (all listed in §0). The Python repository adds ≈6 major mathematical concepts (partitions, Hardy-Ramanujan, fertility, Pareto, probability, multiverse) that have zero basis in the book text. The book is a qualitative philosophical treatise with a single quantitative metric (C) and a decorative fiber bundle analogy — it is NOT a computational fine-tuning argument.
