# RD-MATH.1 Phase 1 — Compass Operationalization Inventory

**Purpose:** Detailed inventory of each variable in the project compass Ψ ≈ f(C, F, I). No theory generation. No survivor promotion. Only inventory.

**Date:** 2026-06-15
**Status:** INVENTORY ONLY

---

## Project Compass

**Symbolic form:** Ψ ≈ f(C, F, I)

**Source:** RD-OPEN_ASSUMPTIONS.md (Assumption C):
> "Experienced reality is jointly shaped by coherence (how well parts fit together) and fertility (how much further experience the structure enables)."

**Status:** No functional form established. All definitions under test.

---

## Variable 1: C — Coherence

### Operational Definition

**From RD-CALIBRATION.1:** "Coherence (how well parts fit together)"

**From RD-METRIC.2 scoring rubric:** "Coherence sensitivity: Does this metric capture how well parts fit together?"

**Conceptual decomposition (from METRIC.1 survey):**
- C does not measure distributional properties (that is Shannon entropy)
- C does not measure randomness (that is Kolmogorov complexity)
- C measures the *fit between parts in an assembly* — how components relate to each other to form a unified structure
- C is distinct from complexity: a random string has high complexity but low coherence; a crystal has low complexity but high coherence

### Existing Metrics (with citations)

| Metric | Score | Source | How it relates to C |
|--------|-------|--------|---------------------|
| Effective Complexity | C=4 | METRIC.2, METRIC.1 §2.4 | Measures information content of regularities in an object. Strongest C-score in survey. |
| Sophistication | C=4 | METRIC.2, METRIC.1 §2.5 | Complexity of minimal model explaining structure. Captures structural regularity. |
| Crutchfield's C_μ | C=4 | METRIC.2, METRIC.1 §3.2 | Information about past needed to predict future. Captures structural information enabling prediction. |
| Mutational Robustness | C=4 | METRIC.2, METRIC.1 §5.1 | Maintains coherent behavior despite perturbation. |
| Mutual Information | C=3 | METRIC.2, METRIC.1 §1.2 | Statistical coupling between parts. |
| Transfer Entropy | C=3 | METRIC.2, METRIC.1 §1.3 | Directional coupling between parts over time. |
| Empowerment | C=3 | METRIC.2, METRIC.1 §7.2 | Coherent relationship between actions and effects. |
| Mutual Info (coverage) | — | METRIC.3 | C_μ+Empowerment pair achieves C=4. |

**Known proxy equation:** C ≈ −MSE (r=−0.89)
- Source: RD-019 (RD-DIAG.1)
- C is 80% reconstructable from MSE

### Observable Proxies

1. **MSE (Mean Squared Error)** — RD-019 found C ≈ −MSE with r=−0.89
2. **Structural regularity** — captured by Effective Complexity and Sophistication
3. **Prediction error** — captured by Crutchfield's C_μ (causal states)
4. **Behavioral consistency under perturbation** — captured by Mutational Robustness

### Measurement Domain

- Algorithmic/information-theoretic domain: best coverage (Effective Complexity, Sophistication, C_μ)
- Evolutionary domain: moderate coverage (Mutational Robustness, Evolvability Index)
- Ecological domain: weak coverage (diversity indices score C≤1)
- No domain scores C=5 (direct measure)

### Known Failures

1. **C ≈ −MSE is domain-specific.** RD-019 found that MSE explains 80% of C variance. But this collapses in other domains. The "density" intervention (RD-019) was misdirected — density (R²=0.055) does not explain C.

2. **C ≈ −MSE may be topology-collapsed.** RD-020 found that removing hubs/force-chain backbone did not degrade C or recovery (p=0.09). Structural importance may be a property of the measurement, not the network.

3. **C ≈ −MSE may be novelty-collapsed.** Multiple novelty metrics collapsed to C or to friction/activity: PS → friction, GN → activity, HI → noise, SP → binary artifact (RD-5,6,7,8).

4. **No metric directly measures C.** METRIC.3 identifies a coverage ceiling: "No metric in the survey scores any dimension at 5. The absence of any 5-score metrics indicates that no existing metric directly measures any dimension of Ψ." The gap from 4→5 represents the conceptual distance between measuring structural regularity (C=4) and measuring coherence-of-parts-in-assembly (C=5).

5. **Ecology diversity indices are structurally weak on C.** Shannon Diversity (C=1), Simpson's (C=1), Hill Numbers (C=1), Chao1 (C=0). They measure component variety but nothing about how components relate.

### Open Questions

1. Is C ≈ −MSE a universal relationship or a domain-specific artifact of the sandpile/glass model?
2. Does C measure a property of the system or a property of the observer's decomposition?
3. Can C be defined independently of the metrics used to measure it, or is C always C-relative-to-a-metric?
4. The RD-DIAG.1 correction: "Research Program may be the deepest fixed variable." Is C shaped by the same cognitive machinery that produces the measurement?

---

## Variable 2: F — Fertility

### Operational Definition

**From RD-CALIBRATION.1:** "Fertility (how much further experience the structure enables)"

**From RD-METRIC.1 §10 (working definition):**
> "Fertility: The capacity of a structure to enable further coherent experience through interaction."

**Three key components (METRIC.1 §10):**
1. **Capacity** — the structure must be *able* to do something, not just be in a certain state
2. **Enable further** — the structure must be *generative*, not merely descriptive
3. **Coherent experience** — what it enables must be structured, not random

**From RD-OPEN_ASSUMPTIONS (Assumption E):** "Complexity increases when persistent structures enable further coherent experience, which in turn creates new persistent structures."

### Existing Metrics (with citations)

| Metric | Score | Source | How it relates to F |
|--------|-------|--------|---------------------|
| Transfer Entropy | F=4 | METRIC.2, METRIC.1 §1.3 | Measures how much one process enables future states of another. |
| Crutchfield's C_μ | F=4 | METRIC.2, METRIC.1 §3.2 | Process with high C_μ has rich structure generating structured future states. |
| Evolvability Index | F=4 | METRIC.2, METRIC.1 §5.2 | Capacity to generate new forms while maintaining function. Closest biological analogue. |
| Niche Construction Index | F=4 | METRIC.2, METRIC.1 §5.3 | Organisms creating conditions for further evolution. |
| MODES: Novelty Potential | F=4 | METRIC.2, METRIC.1 §6.1.2 | Capacity to produce novel types. |
| MODES: Ecological Potential | F=4 | METRIC.2, METRIC.1 §6.1.4 | Capacity to support ecological interactions = further coherent experience. |
| Ω Metric | F=4 | METRIC.2, METRIC.1 §6.2 | Sustained novelty production. |
| Unbounded Evolution | F=4 | METRIC.2, METRIC.1 §6.3 | Non-repeating patterns = unbounded generativity. |
| Novelty Search | F=4 | METRIC.2, METRIC.1 §7.1 | Designed to maximize new behaviors. |
| Empowerment | F=4 | METRIC.2, METRIC.1 §7.2 | Channel capacity between actions and future sensor states. |
| Granger Causality | F=3 | METRIC.2 | One part influencing future states of another. |
| Logical Depth | F=3 | METRIC.2 | Deep structures serve as scaffolding for further computation. |
| Effective Complexity | F=2 | METRIC.2 | Identifies structured part that could serve as basis for elaboration. |

**Coverage:** F = 79/145 = 54%. Best-covered dimension.

### Observable Proxies

1. **Empowerment** — channel capacity between actions and future sensor states (Klyubin et al., 2005)
2. **Transfer Entropy** — directed information flow enabling future states
3. **Evolvability** — expected change in function per unit sequence divergence
4. **Novelty rate** — |{new types at time t}| / Δt (MODES Toolbox)
5. **Ecological interaction diversity** — number/diversity of interaction types

### Measurement Domain

- Information-theoretic domain: 3 metrics score F=4 (Transfer Entropy, C_μ, Empowerment)
- Evolutionary domain: 3 metrics score F=4 (Evolvability, Niche Construction, MODES metrics)
- Ecological domain: 1 metric scores F=4 (MODES: Ecological Potential)
- Fertility is the *only* dimension where multiple independent domains achieve strong scores

### Known Failures

1. **PS collapses to friction.** Persistence of structure (PS) was claimed to capture latent direction, but collapses to friction. Not independent (RD-5).

2. **GN collapses to activity.** Generative novelty (GN) was claimed to capture latent direction, but collapses to activity level. Not independent (RD-7).

3. **HI is unstable.** Historical irreversibility (HI) was claimed to capture latent direction, but is unreliable (RD-6).

4. **SP collapses to binary artifact.** Surprise persistence (SP) was claimed to capture latent direction, but collapses to a binary artifact. Not genuine (RD-8).

5. **Fertility metrics narrow-focus problem.** METRIC.2 identifies: "8 of the 10 highest-scoring metrics score F=4 but score I≤1 and E≤1. These metrics capture generativity in a narrow, process-internal sense. They do not capture the *relational* or *experiential* dimensions of fertility."

6. **No metric captures all three components of F.** METRIC.1 §10: "No existing metric simultaneously captures all three components of fertility: Capacity (empowerment does this best), Generativity (novelty search / OEE metrics do this best), Coherence (effective complexity / statistical complexity do this best)."

### Open Questions

1. Is F an intrinsic property of a structure, or always relative to an observer/agent? (METRIC.1 identifies that "empowerment is defined relative to an agent, not as an intrinsic property of a structure.")
2. Can F be measured without specifying an interaction context?
3. What is the relationship between F and the "fertility" of the research program itself (generating new questions)?
4. Is the F = 74% coverage artifact of the metric vocabulary being built for generativity research?

---

## Variable 3: I — Interaction

### Operational Definition

**From RD-CALIBRATION.1:**
- "Observer: Anything capable of interaction is an observer at the instant of interaction."
- "Observation: The sensing that drives interaction."
- "Interaction: Observation and interaction are two descriptions of the same event."

**From RD-OPEN_ASSUMPTIONS (Assumption B):**
> "Interaction, observation, and primitive experience are three descriptions of the same event."

**From RD-METRIC.2 scoring rubric:** "Interaction sensitivity: Does this metric capture interaction, observation, or the relational event?"

**From RD-DIAG.1:** "Explanatory power arises from interactions, not objects. Objects are frozen experience; interactions are flowing experience."

**Conceptual status:** I is the *relational event* — the actual happening where a structure and an observer/environment meet. It is not a property of the structure alone, nor of the observer alone, but of the event.

### Existing Metrics (with citations)

| Metric | Score | Source | How it relates to I |
|--------|-------|--------|---------------------|
| Transfer Entropy | I=4 | METRIC.2, METRIC.1 §1.3 | Directed information flow between processes — the relational event of influence. |
| Crutchfield's C_μ | I=4 | METRIC.2, METRIC.1 §3.2 | Information processing capacity of a process. |
| Empowerment | I=4 | METRIC.2, METRIC.1 §7.2 | Agent's capacity through action — the action-perception loop. |
| Information Gain | I=4 | METRIC.2, METRIC.1 §7.3 | Reducing uncertainty through observation — the experiential event. |
| Mutual Information | I=3 | METRIC.2, METRIC.1 §1.2 | Statistical coupling between paired observations. |
| Granger Causality | I=3 | METRIC.2, METRIC.1 §1.4 | Predictive influence between paired processes. |
| MODES: Ecological Potential | I=3 | METRIC.2, METRIC.1 §6.1.4 | Ecological interactions between components. |

**Coverage:** I = 39/145 = 27%. Severely under-measured.

### Observable Proxies

1. **Transfer Entropy** — directed information flow between paired processes
2. **Mutual Information** — statistical coupling between paired variables
3. **Empowerment** — channel capacity in the action-perception loop
4. **Information Gain** — reduction in uncertainty through observation
5. **Ecological interaction count** — number of interaction types observed (MODES)

### Measurement Domain

- Information-theoretic domain: 4 metrics score I=4 (Transfer Entropy, C_μ, Empowerment, Information Gain)
- Ecological domain: 1 metric scores I=3 (MODES: Ecological Potential)
- Evolutionary domain: 0 metrics score I>1
- Algorithmic domain: 0 metrics score I>1
- **I is almost exclusively measured by information-theoretic metrics applied to paired processes**

### Known Failures

1. **19 of 29 metrics score I≤1 (66%).** METRIC.2: "All ecology diversity indices, all algorithmic complexity measures, all evolutionary metrics, all novelty production metrics, both fitness measures score I≤1."

2. **Ecology and evolutionary metrics fail to capture interaction.** METRIC.2: "The ecology and evolutionary metrics — which conceptually should capture interaction — fail to do so because they measure properties of *components* (species, genotypes) rather than properties of *relational events*."

3. **I=5 (direct measure) does not exist.** No metric in the survey scores I at the direct-measure level. The best metrics score I=4 (strong relation) but not I=5 (direct measure of the relational event).

4. **Interaction is conflated with observation in existing metrics.** The existing metrics conflate "interaction" with "information flow" — but the project defines interaction as the relational event, which is broader than information transfer.

5. **Archive is success-biased.** RD-DIAG.1: "Archive is success-biased. Non-productive interactions were never recorded." This means existing metrics are calibrated on successful interactions only.

### Open Questions

1. Is I a property of the event, or is it always relative to the observer's decomposition?
2. Can I be measured independently of C and F, or is I always entangled with them?
3. The project defines Interaction ≈ Observation ≈ Primitive Experience (Assumption B). If this is true, then I and Ψ may be the same variable viewed from different angles. Is this defensible?
4. Why do existing metrics almost exclusively measure I through information-theoretic lenses? Is this a vocabulary limitation or a fundamental asymmetry?
5. RD-DIAG.1: "Research Program may be the deepest fixed variable." Is the weakness of I-measurement an artifact of the research program's preference for observer-independent description?

---

## Variable 4: Ψ — Experience

### Operational Definition

**From RD-CALIBRATION.1:**
- "Experience exists. Experience is self-evident first-person reality."
- "Primitive Experience: The intrinsic side of interaction."
- "Consciousness: Sentience being sentient."
- "Reflection: Experience modeling experience."

**From RD-OPEN_ASSUMPTIONS (Assumption A):**
> "Experience is present from the beginning. It does not emerge at some threshold of complexity."

**From RD-OPEN_ASSUMPTIONS (Assumption C):**
> "Possible symbolic compass: Ψ ≈ f(C, F, I) where Ψ = experienced value"

**From RD-METRIC.2 scoring rubric:** "Experience relevance: Does this metric relate to experience, sentience, or first-person reality?"

**Conceptual status:** Ψ is defined as "experienced value" — the intrinsic quality of experience as it is lived, not as measured from outside. The project takes experience as axiomatic (not derived) and investigates what structures *maximize* Ψ.

**Critical distinction:** Ψ in the compass equation is a *function* of C, F, and I. E (experience relevance) in the METRIC.2 scoring is a *property* of a metric. These are not the same thing. E measures whether a metric is *about* experience; Ψ measures the *experiential quality itself*.

### Existing Metrics (with citations)

| Metric | Score | Source | How it relates to Ψ |
|--------|-------|--------|---------------------|
| Empowerment | E=4 | METRIC.2, METRIC.1 §7.2 | Generating sensor states through action — experience-adjacent. |
| Information Gain | E=4 | METRIC.2, METRIC.1 §7.3 | Learning through observation — directly about reducing uncertainty through experience. |
| Transfer Entropy | E=3 | METRIC.2 | How one process informs/predicts another — experience-adjacent. |
| Crutchfield's C_μ | E=3 | METRIC.2 | Information processing capacity — experience-adjacent. |
| MODES: Ecological Potential | E=3 | METRIC.2 | Ecological interactions are a form of experiential coupling. |
| 23 of 29 metrics | E≤1 | METRIC.2 | No connection to experience. |

**Coverage:** E = 35/145 = 24%. Most under-measured dimension.

**Existing metrics with E=0 (zero connection to experience):** Kolmogorov Complexity, Sophistication, LMC Complexity, Shannon Diversity, Simpson's Diversity, Hill Numbers, Chao1 — 12 metrics total.

### Observable Proxies

1. **Empowerment** — agent-centric: the agent's capacity to generate new sensor states through action
2. **Information Gain** — agent-centric: reduction in uncertainty through observation
3. **No structure-intrinsic proxy exists.** Every metric scoring E≥3 requires an observer/agent to be defined. No metric captures experience as an intrinsic property of a structure.

### Measurement Domain

- Information-theoretic domain: 2 metrics score E=4 (Empowerment, Information Gain)
- All other domains: E≤1
- **Experience is almost unmeasured by existing science.** The metric vocabulary is built for observer-independent description, not for experiential phenomena.

### Known Failures

1. **No metric scores E=5 (direct measure).** METRIC.3: "No metric in the survey scores any dimension at 5. The absence of any 5-score metrics indicates that no existing metric directly measures any dimension of Ψ."

2. **All E≥4 metrics are agent-relative.** METRIC.3: "Empowerment is the only metric scoring E=4, and it is agent-relative — it requires an observer/agent to be defined. No metric captures experience as an intrinsic property of a structure."

3. **79% of metrics score E≤1.** METRIC.2: "23 of 29 metrics score E≤1 or 0. The existing metric landscape appears built for observer-independent description, not for relational or experiential phenomena."

4. **E=4 metrics measure processing capacity, not phenomenal experience.** METRIC.3: "Empowerment's E=3 (for C_μ) reflects *processing capacity* rather than *phenomenal experience*."

5. **The compass equation Ψ ≈ f(C, F, I) is untested.** RD-OPEN_ASSUMPTIONS: "No functional form established." The relationship between Ψ and its components is assumed, not measured.

6. **Experience is axiomatic, not derived.** The project assumes experience exists (RD-CALIBRATION.1) but does not derive it from other quantities. This means Ψ cannot be reduced to C, F, or I — it can only be *related* to them.

### Open Questions

1. **The core measurement problem:** Can Ψ be measured from outside, or only experienced from inside? If Ψ is defined as "first-person reality," then no third-person metric can capture it. Is this a fundamental limitation or a current technical gap?

2. **Is Ψ the same as E, or different?** The compass equation Ψ ≈ f(C, F, I) treats Ψ as a function of three variables. E in METRIC.2 measures "experience relevance" of a metric. Are these the same concept? If not, what is the relationship between Ψ (experiential quality) and E (metric's connection to experience)?

3. **Assumption B problem:** If Interaction ≈ Observation ≈ Primitive Experience, then I ≈ Ψ (primitive experience). Does this collapse the compass to Ψ ≈ f(C, F, Ψ)? Is this circular?

4. **Assumption A problem:** If experience is present from the beginning, then Ψ is always > 0. The research question becomes *maximizing* Ψ, not *enabling* Ψ. Does this change what metrics should measure?

5. **Standing Rule 30 (RD-DIAG.1):** "Any survivor discovered entirely within one research program must be treated as potentially program-dependent until tested by an independent decomposition or independent research culture." All existing E-metrics were developed within cognitive science / AI / neuroscience. Are they program-dependent?

---

## Cross-Variable Inventory Summary

### Coverage Comparison

| Variable | Coverage (max 145) | Coverage % | Status | Best single metric | Best pair |
|----------|-------------------|------------|--------|-------------------|-----------|
| C (Coherence) | 63 | 43% | Under-measured | Effective Complexity (4) | C_μ + Empowerment (4) |
| F (Fertility) | 79 | 54% | Best covered | Empowerment (4) | C_μ + Empowerment (4) |
| I (Interaction) | 39 | 27% | Severely under-measured | Transfer Entropy (4) | C_μ + Empowerment (4) |
| Ψ (Experience) | 35 | 24% | Most under-measured | Empowerment (4) | C_μ + Empowerment (4) |

### Coverage Ceiling

From METRIC.3: "No metric in the survey scores any dimension at 5. The theoretical maximum for any combination is 4 × 4 = 16, not 5 × 4 = 20."

**This ceiling is not a limitation of combination — it is a limitation of the metric vocabulary itself.**

### Structural Gap

From METRIC.2: "The metrics divide into two clusters:
1. Information-theoretic cluster (metrics 1-4, 11, 26-27): Covers I and E moderately, but C weakly
2. Ecological/evolutionary cluster (metrics 12-18, 28-29): Covers C and F moderately, but I and E very weakly"

**No metric bridges these clusters in a balanced way.** The "bridge" metrics — Transfer Entropy, Crutchfield's C_μ, Empowerment — are all information-theoretic and only partially reach into the ecological/evolutionary domain.

### Best Approximation of Ψ Within Existing Mathematics

From METRIC.3: "The pair {C_μ, Empowerment} achieves the achievable ceiling. Total=16, min=4, no blind spots."

**But:** "This approximation is surface-level: it captures the *presence* of each dimension but not its *depth* or *mutual entanglement*. The function f in Ψ ≈ f(C, F, I, E) remains uncharacterized."

### Fixed Variable Risk

From RD-DIAG.1 Standing Rule 30: "Any survivor discovered entirely within one research program must be treated as potentially program-dependent until tested by an independent decomposition or independent research culture."

**Applied to this inventory:** Every metric in this inventory was developed within the same research culture (Western science, information theory, evolutionary biology, ecology). The entire metric vocabulary may be a fixed variable of the research program.

---

## Artifact

`/home/student/sgp_core_v2/audits/RD_MATH_1_COMPASS_OPERATIONALIZATION.md`
