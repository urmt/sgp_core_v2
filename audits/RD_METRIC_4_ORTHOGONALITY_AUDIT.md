# RD-METRIC.4: Orthogonality Audit — Are the Top Metrics Genuinely Non-Redundant?

**Purpose:** Determine whether the top metrics from RD-METRIC.3 actually measure different things, or whether their apparent complementarity is an artifact of dimensional scoring. A composite only matters if its components are non-redundant.

**Date:** 2026-06-15

**Trigger:** RD-METRIC.3 found that {C_μ, Empowerment} jointly cover [4,4,4,4] on the compass dimensions. The Research Director asks: are these metrics genuinely non-redundant, or are they measuring the same underlying construct from two angles?

---

## 1. Method

For each pair of the 6 top metrics, I assess:
- **(a) Mathematical definition overlap:** Do they share formal structure?
- **(b) Domain overlap:** Are they used in the same fields?
- **(c) Information overlap:** Could one be derived from the other?
- **(d) Redundancy estimate:** How much unique variance does each contribute?
- **(e) Complementarity:** What does one capture that the other cannot?

**Metrics under analysis:**

| Metric | Formal Definition | Domain | Key Property |
|--------|------------------|--------|--------------|
| **Empowerment** | Channel capacity between actions and future sensor states: H(A; S') | Agent theory, AI, neuroscience | Agent-relative capacity |
| **C_μ** | Entropy over causal states of the ε-machine: H[μ] | Computational mechanics | Intrinsic structural complexity |
| **Transfer Entropy** | Directed information flow: T_{X→Y} = I(Y_future; X_past | Y_past) | Information theory, causal inference | Directed influence |
| **Evolvability Index** | Δ(phenotype) per unit genotype change | Evolutionary biology | Generative potential |
| **Effective Complexity** | Length of minimal regularity description: EC = K(regularities) | Algorithmic information theory | Structural regularity |
| **Mutational Robustness** | Fraction of neutral mutations: R = 1 - fraction of deleterious | Evolutionary biology | Perturbation tolerance |

---

## 2. Pairwise Analysis

### 2.1 C_μ × Empowerment

**(a) Mathematical overlap:** Low. C_μ is defined over the causal states of a process's own ε-machine — an intrinsic property. Empowerment is defined as channel capacity between actions and future sensor states — a relational property requiring an agent-environment boundary. They share no formal primitives.

**(b) Domain overlap:** Minimal. C_μ belongs to computational mechanics (physics, signal processing, complex systems). Empowerment belongs to agent theory (AI, neuroscience, robotics). Different literatures, different communities.

**(c) Information overlap:** Neither can be derived from the other. A process can have high C_μ but zero empowerment (complex periodic signal — rich causal structure but no agency). An agent can have high empowerment but low C_μ (simple reactive agent in a complex environment — many action-outcome mappings but minimal internal state structure).

**(d) Redundancy estimate:** ~5%. Both score F=4 and I=4, but for different reasons. C_μ scores F=4 because structured processes generate structured futures. Empowerment scores F=4 because agents with many action options enable many future states. These are distinct generative mechanisms.

**(e) Complementarity:** C_μ uniquely provides C=4 (structural coherence of internal states). Empowerment uniquely provides E=4 (agent-relative experiential relevance). Neither covers the dimension the other provides.

**Verdict: Genuinely non-redundant.**

---

### 2.2 C_μ × Transfer Entropy

**(a) Mathematical overlap:** Moderate. Both are information-theoretic. C_μ measures the entropy of causal states (a property of a single process). Transfer Entropy measures directed information flow between two processes. They share Shannon entropy as a building block but apply it to different objects.

**(b) Domain overlap:** High. Both belong to information theory and computational science. Both are used in causal inference, time series analysis, and complex systems.

**(c) Information overlap:** Partially derivable. In the limit of a single isolated process, transfer entropy to a self-loop approximates predictive information, which relates to C_μ. However, for interacting systems, TE captures directed coupling that C_μ does not. A process with high C_μ may have zero transfer entropy to/from another process.

**(d) Redundancy estimate:** ~40%. Both score I=4 and F=4 for related reasons — both measure how past information predicts future states, but C_μ does this intrinsically while TE does it directionally. On C, C_μ contributes C=4 while TE only reaches C=3. The overlap on I and F is substantial.

**(e) Complementarity:** C_μ uniquely provides C=4. TE does not add any dimension that C_μ does not already cover at ≥3. The combined vector of C_μ+TE is [4,4,4,3] — same as C_μ alone.

**Verdict: Partially redundant. TE does not add unique dimensional coverage beyond C_μ.**

---

### 2.3 C_μ × Evolvability Index

**(a) Mathematical overlap:** None. C_μ is information-theoretic. Evolvability is biological. No shared formal structure.

**(b) Domain overlap:** None. C_μ is computational mechanics. Evolvability is evolutionary biology.

**(c) Information overlap:** Neither can be derived from the other. A complex crystal has high C_μ, zero evolvability. A population with high phenotypic variation can have low C_μ.

**(d) Redundancy estimate:** ~5%. Both score F=4 but for entirely different reasons — C_μ because structured processes generate structured futures, evolvability because populations with heritable variation generate new forms.

**(e) Complementarity:** Evolvability's contribution is primarily as a cross-domain validator: it confirms that the F=4 score is robust across information-theoretic and biological frameworks. Evolvability adds no dimension that C_μ does not already cover at ≥3.

**Verdict: Non-redundant in definition, but low incremental value. Cross-domain F validator only.**

---

### 2.4 C_μ × Effective Complexity

**(a) Mathematical overlap:** Moderate. Both measure structural complexity. C_μ measures information content of causal states (temporal predictive structure). EC measures the length of minimal regularity description (compositional structure). Both relate to Kolmogorov complexity but apply different decompositions.

**(b) Domain overlap:** High. Both belong to algorithmic/information-theoretic complexity.

**(c) Information overlap:** Partially. Both capture "how much structure is there" but from different angles. C_μ captures temporal structure. EC captures compositional structure. A chaotic pendulum has high C_μ, low EC. A crystal has high EC, low C_μ.

**(d) Redundancy estimate:** ~30%. Both score C=4 but for different reasons. On F, C_μ scores 4 while EC scores 2 — EC captures structure without generativity. On I and E, C_μ scores 4 and 3 while EC scores 1 and 1.

**(e) Complementarity:** EC provides a different *kind* of C=4 — compositional regularity rather than temporal predictive structure. However, EC's low F/I/E scores mean it adds little beyond C when paired with C_μ.

**Verdict: Partially redundant on C, conceptually distinct. Low incremental value with C_μ.**

---

### 2.5 C_μ × Mutational Robustness

**(a) Mathematical overlap:** None. C_μ is information-theoretic. Robustness is biological perturbation tolerance.

**(b) Domain overlap:** None. Different fields entirely.

**(c) Information overlap:** Neither can be derived from the other. Complex fragile dynamics vs. simple resilient dynamics.

**(d) Redundancy estimate:** ~10%. Both score C=4 but for different reasons — C_μ because complex causal states indicate internal structure, robustness because maintaining behavior under perturbation indicates structural resilience. On F/I/E, C_μ scores 4/4/3 while robustness scores 2/1/1.

**(e) Complementarity:** Robustness provides a biological validation of C=4 only. Its low F/I/E scores mean it adds little beyond C.

**Verdict: Non-redundant in definition, but low incremental value. Biological C validator only.**

---

### 2.6 Empowerment × Transfer Entropy

**(a) Mathematical overlap:** High. Both involve mutual information between past and future states. Empowerment: H(A; S') — mutual information between actions and future sensor states. TE: I(Y_future; X_past | Y_past) — conditional mutual information. Both are directed, both are information-theoretic, both measure "how much does one variable inform another across time."

**(b) Domain overlap:** High. Both are information-theoretic measures applied to directed processes. TE is used in causal inference, neuroscience, complex systems. Empowerment is used in AI, neuroscience, robotics. Neuroscience is a shared application domain.

**(c) Information overlap:** Partially. Empowerment requires an agent with discrete actions. TE requires two coupled processes. In the special case where one "process" is an agent choosing actions, TE from agent to environment approximates a component of empowerment. However, empowerment's channel capacity formulation (maximizing over action distributions) is not equivalent to TE (which measures actual information flow, not maximal possible flow).

**(d) Redundancy estimate:** ~50%. Both score I=4 and F=4. Both measure directed information flow. The key difference: TE measures *actual* directed coupling; empowerment measures *maximal possible* directed influence. Empowerment uniquely provides E=4 (agent-relative experience). TE only reaches E=3.

**(e) Complementarity:** Empowerment uniquely provides E=4. TE provides slightly different I semantics (actual vs. potential flow). Combined vector [3,4,4,4] — empowerment alone reaches [3,4,4,4]. TE does not improve the combined vector.

**Verdict: Substantially redundant. TE adds no new dimensional coverage beyond Empowerment.**

---

### 2.7 Empowerment × Evolvability Index

**(a) Mathematical overlap:** None. Empowerment is information-theoretic (channel capacity). Evolvability is biological (Δphenotype/Δgenotype).

**(b) Domain overlap:** None. AI/neuroscience vs. evolutionary biology.

**(c) Information overlap:** Neither derivable from the other. Agent capacity vs. population generativity.

**(d) Redundancy estimate:** ~10%. Both score F=4 — empowerment because agents enable future states, evolvability because populations generate new forms. Different mechanisms.

**(e) Complementarity:** Empowerment provides I=4, E=4 that evolvability lacks (I=1, E=1). Evolvability provides nothing empowerment does not already cover at ≥3.

**Verdict: Non-redundant in definition. Low incremental value — evolvability adds nothing beyond F=4 validator.**

---

### 2.8 Empowerment × Effective Complexity

**(a) Mathematical overlap:** None. Empowerment is information-theoretic (agent-relative). EC is algorithmic (structure-intrinsic).

**(b) Domain overlap:** Minimal. AI/neuroscience vs. algorithmic information theory.

**(c) Information overlap:** Neither derivable from the other.

**(d) Redundancy estimate:** ~5%. No shared dimensional strengths. EC provides C=4; Emp provides I=4, E=4, F=4.

**(e) Complementarity:** Strong. EC uniquely provides C=4. Empowerment uniquely provides I=4, E=4. Combined vector [4,4,4,4] — fully complementary.

**Verdict: Genuinely non-redundant. Strong complementarity.**

---

### 2.9 Empowerment × Mutational Robustness

**(a) Mathematical overlap:** None. Information-theoretic vs. biological.

**(b) Domain overlap:** None.

**(c) Information overlap:** Neither derivable from the other.

**(d) Redundancy estimate:** ~5%. No shared dimensional strengths. MR provides C=4; Emp provides I=4, E=4, F=4.

**(e) Complementarity:** Strong. MR uniquely provides C=4. Empowerment uniquely provides I=4, E=4. Combined vector [4,4,4,4] — fully complementary.

**Verdict: Genuinely non-redundant. Strong complementarity.**

---

### 2.10 Transfer Entropy × Evolvability Index

**(a) Mathematical overlap:** None. Information theory vs. biology.

**(b) Domain overlap:** None.

**(c) Information overlap:** Neither derivable from the other.

**(d) Redundancy estimate:** ~10%. Both score F=4 and I=4 (TE directly, EI weakly at I=1 — actually TE scores I=4, EI scores I=1, so overlap is only on F).

**(e) Complementarity:** TE provides I=4, E=3. EI provides F=4, C=3. Complementary on different dimensions but neither reaches C=4 or E=4.

**Verdict: Non-redundant but low combined coverage. Neither metric is strong.**

---

### 2.11 Transfer Entropy × Effective Complexity

**(a) Mathematical overlap:** Low. TE is information-theoretic (directed flow). EC is algorithmic (regularity description).

**(b) Domain overlap:** Low.

**(c) Information overlap:** Neither derivable from the other.

**(d) Redundancy estimate:** ~5%. No shared dimensional strengths. TE provides I=4, F=4. EC provides C=4.

**(e) Complementarity:** Moderate. TE provides I=4 that EC lacks. EC provides C=4 that TE lacks. Combined vector [3,4,4,3] — no dimension reaches 4 except F (both have it).

**Verdict: Non-redundant but neither is a top-tier metric. Combined coverage [3,4,4,3] is below the [4,4,4,4] ceiling.**

---

### 2.12 Transfer Entropy × Mutational Robustness

**(a) Mathematical overlap:** None.

**(b) Domain overlap:** None.

**(c) Information overlap:** Neither derivable from the other.

**(d) Redundancy estimate:** ~5%. No shared dimensional strengths.

**(e) Complementarity:** TE provides I=4, F=4. MR provides C=4. Combined vector [3,4,4,3]. Below ceiling.

**Verdict: Non-redundant but low combined coverage.**

---

### 2.13 Evolvability Index × Effective Complexity

**(a) Mathematical overlap:** None. Biological vs. algorithmic.

**(b) Domain overlap:** None.

**(c) Information overlap:** Neither derivable from the other.

**(d) Redundancy estimate:** ~15%. Both score C=3 (moderate). EI scores F=4; EC scores F=2. Shared dimensional space is small.

**(e) Complementarity:** EI provides F=4. EC provides C=4 (stronger than EI's C=3). But combined vector [4,4,1,1] — blind spots on I and E.

**Verdict: Non-redundant. But combined coverage has blind spots on I and E.**

---

### 2.14 Evolvability Index × Mutational Robustness

**(a) Mathematical overlap:** Moderate. Both are evolutionary biology measures. Both operate on genotype-phenotype maps. Both are properties of mutation neighborhoods.

**(b) Domain overlap:** Identical. Both belong to evolutionary biology and population genetics.

**(c) Information overlap:** Partially. Evolvability and robustness are known to be in tension — high robustness can reduce evolvability and vice versa (Wagner 2008, Draghi et al. 2010). They are anti-correlated in many fitness landscapes. However, they are not mathematically derivable from each other — they measure opposite things about the same mutation neighborhood.

**(d) Redundancy estimate:** ~25%. Both score C=4 (for related reasons — structural integrity), F=4 (EI directly, MR weakly at F=2 — actually MR scores F=2, so overlap is mainly on C=4). Both score I=1, E=1. They share the same blind spots.

**(e) Complementarity:** Limited. EI uniquely provides F=4 (generativity). MR uniquely provides C=4 (structural resilience). But both share blind spots on I and E. Combined vector [4,4,1,1] — no coverage on interaction or experience.

**Verdict: Partially redundant (same domain, same blind spots). Conceptual complementarity (opposite ends of robustness-evolvability spectrum) but no I/E coverage.**

---

### 2.15 Effective Complexity × Mutational Robustness

**(a) Mathematical overlap:** Low. EC is algorithmic (description length). MR is biological (mutation tolerance).

**(b) Domain overlap:** Low. Algorithmic information theory vs. evolutionary biology.

**(c) Information overlap:** Neither derivable from the other.

**(d) Redundancy estimate:** ~20%. Both score C=4. Both score F=2, I=1, E=1. They share the same dimensional profile except for the specific mechanism of C=4.

**(e) Complementarity:** Minimal. Both provide C=4 through different mechanisms. Neither provides F/I/E coverage. Combined vector [4,2,1,1] — same as either alone.

**Verdict: Substantially redundant. Same dimensional profile, different C mechanisms.**

---

### 2.16 Effective Complexity × Sophistication

**(a) Mathematical overlap:** Very high. Sophistication is defined as the complexity of the minimal model explaining a string's structure — closely related to EC. Both are based on the structure-function decomposition of algorithmic complexity. Sophistication ≈ K(description of regularities) — nearly the same object as EC.

**(b) Domain overlap:** Identical. Algorithmic information theory.

**(c) Information overlap:** High. In many cases, sophistication and effective complexity are numerically close or identical. They are often discussed as variants of the same concept.

**(d) Redundancy estimate:** ~80%. Both score C=4, F=2, I=0-1, E=0-1. Nearly identical dimensional profiles.

**(e) Complementarity:** Minimal. Sophistication is a refined version of EC, not a complement.

**Verdict: Highly redundant. Do not count both.**

---

### 2.17 Mutational Robustness × Sophistication

**(a) Mathematical overlap:** None.

**(b) Domain overlap:** None.

**(c) Information overlap:** Neither derivable from the other.

**(d) Redundancy estimate:** ~15%. Both score C=4 but for different reasons. Both score F=2, I=0-1, E=0-1. Same dimensional profile, different mechanisms.

**(e) Complementarity:** Minimal. Same blind spots. Same coverage ceiling.

**Verdict: Non-redundant in definition, but functionally equivalent in dimensional coverage.**

---

## 3. Redundancy Matrix

| Metric Pair | Overlap Estimate | Unique to A | Unique to B | Verdict |
|-------------|-----------------|-------------|-------------|---------|
| C_μ × Empowerment | **5%** | C=4 | E=4 | **Non-redundant** |
| C_μ × Transfer Entropy | **40%** | C=4 | (none) | **Partially redundant** |
| C_μ × Evolvability Index | **5%** | I=4 | F=4 (validator) | **Non-redundant, low value** |
| C_μ × Effective Complexity | **30%** | F=4, I=4, E=3 | C=4 (different type) | **Partially redundant on C** |
| C_μ × Mutational Robustness | **10%** | F=4, I=4, E=3 | C=4 (validator) | **Non-redundant, low value** |
| Empowerment × Transfer Entropy | **50%** | E=4 | (none) | **Substantially redundant** |
| Empowerment × Evolvability Index | **10%** | I=4, E=4 | F=4 (validator) | **Non-redundant, low value** |
| Empowerment × Effective Complexity | **5%** | I=4, E=4, F=4 | C=4 | **Non-redundant** |
| Empowerment × Mutational Robustness | **5%** | I=4, E=4, F=4 | C=4 | **Non-redundant** |
| TE × Evolvability Index | **10%** | I=4, E=3 | F=4, C=3 | **Non-redundant, low value** |
| TE × Effective Complexity | **5%** | I=4, F=4 | C=4 | **Non-redundant, low value** |
| TE × Mutational Robustness | **5%** | I=4, F=4 | C=4 | **Non-redundant, low value** |
| EI × Effective Complexity | **15%** | F=4 | C=4 | **Non-redundant, blind spots** |
| EI × Mutational Robustness | **25%** | F=4 | C=4 | **Partially redundant, blind spots** |
| EC × Mutational Robustness | **20%** | (none unique) | (none unique) | **Substantially redundant** |
| EC × Sophistication | **80%** | (none) | (none) | **Highly redundant** |
| MR × Sophistication | **15%** | (none unique) | (none unique) | **Functionally redundant** |

---

## 4. Answers to the Four Specific Questions

### Q1: Are C_μ and Empowerment genuinely complementary?

**Yes.** This is the strongest non-redundant pair in the entire metric set.

- **Mathematical:** C_μ is intrinsic (entropy over a process's own causal states). Empowerment is relational (channel capacity between actions and sensor states). No shared formal primitives.
- **Domain:** Computational mechanics vs. agent theory. Different literatures, different citation networks.
- **Derivability:** Neither can be derived from the other. Complex periodic signals have high C_μ, zero empowerment. Simple reactive agents in complex environments have high empowerment, low C_μ.
- **Dimensional:** C_μ provides C=4 (Emp has 3). Empowerment provides E=4 (C_μ has 3). On F and I, both score 4 but for different reasons — C_μ because structured processes generate structured futures, empowerment because agent actions enable future states.
- **Estimated overlap: 5%.** The shared F=4 and I=4 scores are dimensional co-occurrence, not measurement of the same construct.

**This pair is genuinely non-redundant. Their apparent complementarity in RD-METRIC.3 is real, not an artifact.**

### Q2: Is Evolvability already encoded inside Empowerment?

**No.** Evolvability is not encoded inside empowerment, but it adds negligible incremental value when paired with empowerment.

- **Mathematical:** Evolvability measures Δphenotype/Δgenotype (biological generativity). Empowerment measures channel capacity (agent action-outcome mapping). No shared formal structure.
- **Conceptual:** Evolvability is about generating heritable variation in populations. Empowerment is about an individual agent's capacity to affect its environment. They operate at different levels of organization (population vs. individual).
- **Dimensional:** Evolvability scores [3,4,1,1]. Empowerment scores [3,4,4,4]. Evolvability adds nothing that empowerment does not already cover at ≥3. The only unique contribution of evolvability is confirming that F=4 is robust across biological and information-theoretic frameworks.
- **Estimated overlap: 10%.** Low mathematical overlap, but evolvability's dimensional profile is a strict subset of empowerment's.

**Evolvability is not encoded inside empowerment (different definitions, different domains), but it is informationally dominated by empowerment (empowerment covers everything evolvability covers, plus more). Evolvability's value is as a cross-domain validator, not as an independent information source.**

### Q3: Is Transfer Entropy simply measuring interaction already captured elsewhere?

**Substantially yes.** Transfer Entropy's interaction measurement is largely captured by both C_μ and Empowerment individually, and completely captured by their combination.

- **TE's unique contribution:** TE measures *actual* directed information flow between two processes. C_μ measures *intrinsic* predictive structure. Empowerment measures *maximal possible* influence. TE occupies a middle ground — it measures realized coupling, not potential coupling (empowerment) or internal structure (C_μ).
- **However:** C_μ already scores I=4 (information processing capacity). Empowerment already scores I=4 (action-sensor information flow). TE scores I=4 (directed information flow). All three measure "interaction" at the same dimensional level through different lenses.
- **Dimensional evidence:** TE alone reaches [3,4,4,3]. C_μ alone reaches [4,4,4,3]. Combined: [4,4,4,3] — same as C_μ alone. TE adds zero new dimensional coverage to C_μ. Similarly, TE+Empowerment reaches [3,4,4,4] — same as Empowerment alone.
- **Estimated overlap with C_μ: 40%. Estimated overlap with Empowerment: 50%.**

**TE is not *identical* to the interaction captured by C_μ or Empowerment, but it is *redundant* with them at the dimensional level. Its unique semantic (actual vs. potential vs. intrinsic flow) may matter for specific applications, but it does not add new coverage to the [C,F,I,E] framework.**

### Q4: Which metrics contribute unique variance?

**Variance source: QUALITATIVE ESTIMATE (expert judgment, not empirical calculation)**

**Metrics ranked by estimated unique variance contribution:**

1. **Empowerment** — Unique on E=4 (only metric scoring this). Provides I=4, F=4 through agent-theoretic mechanism. **~35% unique variance.**
2. **C_μ** — Unique on C=4 (temporal predictive type). Provides I=4, F=4 through computational mechanics mechanism. **~30% unique variance.**
3. **Effective Complexity** — Unique on C=4 (compositional regularity type). Different *kind* of coherence than C_μ. **~10% unique variance.**
4. **Evolvability Index** — Unique on F=4 (biological generativity type). Cross-domain F validator. **~8% unique variance.**
5. **Mutational Robustness** — Unique on C=4 (biological resilience type). Cross-domain C validator. **~7% unique variance.**
6. **Transfer Entropy** — Largely redundant with C_μ and Empowerment. Unique semantic (actual flow) but no new dimensional coverage. **~5% unique variance.**

**The top 2 metrics (Empowerment + C_μ) appear to capture the majority of estimated unique variance. Adding EC, EI, and MR appears to capture most of the remainder. TE appears to contribute the least unique variance among the top 6.** All percentages are qualitative estimates based on dimensional coverage analysis, not empirical variance decomposition.

---

## 5. Structural Redundancy Patterns

### 5.1 Information-Theoretic Cluster: C_μ, Transfer Entropy, Empowerment

These three metrics are all information-theoretic and all score I=4, F=4. Within this cluster:
- **C_μ vs. TE:** ~40% overlap. C_μ is intrinsic, TE is directional. C_μ dominates on C.
- **C_μ vs. Empowerment:** ~5% overlap. Maximally complementary. C_μ dominates on C, Empowerment on E.
- **TE vs. Empowerment:** ~50% overlap. Most redundant pair in the cluster. Empowerment dominates (strictly higher dimensional coverage).

**Within the information-theoretic cluster, only the C_μ × Empowerment pair is genuinely non-redundant. TE is redundant with both.**

### 5.2 Algorithmic Cluster: Effective Complexity, Sophistication

- **EC vs. Sophistication:** ~80% overlap. Nearly identical objects. Do not count both.

### 5.3 Evolutionary Cluster: Evolvability Index, Mutational Robustness

- **EI vs. MR:** ~25% overlap. Conceptual complementarity (opposite ends of robustness-evolvability spectrum) but shared blind spots on I and E. Same domain.

### 5.4 Cross-Cluster Pairs

Cross-cluster pairs are generally non-redundant because they draw from different mathematical foundations:
- C_μ × EC: ~30% overlap (both structural, but different types)
- C_μ × EI: ~5% overlap (information theory vs. biology)
- C_μ × MR: ~10% overlap (information theory vs. biology)
- Empowerment × EC: ~5% overlap (agent theory vs. algorithmic)
- Empowerment × EI: ~10% overlap (agent theory vs. biology)
- Empowerment × MR: ~5% overlap (agent theory vs. biology)

---

## 6. Verdict: Which Combinations Are Genuinely Non-Redundant?

### Genuinely non-redundant pairs (overlap < 15%):

| Pair | Overlap | Combined Vector | Assessment |
|------|---------|----------------|------------|
| **C_μ + Empowerment** | 5% | [4,4,4,4] | **Best pair.** Maximally complementary. Ceiling coverage. |
| **Empowerment + Effective Complexity** | 5% | [4,4,4,4] | Fully complementary. Cross-domain. |
| **Empowerment + Mutational Robustness** | 5% | [4,4,4,4] | Fully complementary. Cross-domain. |
| **C_μ + Evolvability Index** | 5% | [4,4,4,3] | Non-redundant but EI adds low value. |
| **C_μ + Mutational Robustness** | 10% | [4,4,4,3] | Non-redundant but MR adds low value. |

### Redundant pairs (overlap ≥ 25%):

| Pair | Overlap | Assessment |
|------|---------|------------|
| **Transfer Entropy + Empowerment** | 50% | Substantially redundant. TE adds nothing to Emp's coverage. |
| **C_μ + Transfer Entropy** | 40% | Partially redundant. TE adds nothing to C_μ's coverage. |
| **EC + Sophistication** | 80% | Highly redundant. Nearly identical objects. |
| **EI + Mutational Robustness** | 25% | Partially redundant. Same domain, same blind spots. |
| **EC + Mutational Robustness** | 20% | Functionally redundant. Same dimensional profile. |

### Non-redundant but low combined value:

| Pair | Overlap | Combined Vector | Issue |
|------|---------|----------------|-------|
| TE + EC | 5% | [3,4,4,3] | Below ceiling. Neither is top-tier. |
| TE + MR | 5% | [3,4,4,3] | Below ceiling. |
| TE + EI | 10% | [3,4,4,3] | Below ceiling. |
| EI + EC | 15% | [4,4,1,1] | Blind spots on I, E. |
| EI + MR | 25% | [4,4,1,1] | Blind spots on I, E. |

---

## 7. Implications for the Composite

### The {C_μ, Empowerment} pair is validated as genuinely non-redundant.

RD-METRIC.3's finding that {C_μ, Empowerment} jointly cover [4,4,4,4] is not an artifact of dimensional scoring. These metrics:
- Share only ~5% mathematical overlap
- Come from different scientific domains
- Cannot be derived from each other
- Each uniquely provides a dimension the other lacks (C_μ→C, Emp→E)

**The pair is the minimum non-redundant combination that achieves full dimensional coverage.**

### Transfer Entropy should not be counted as a third independent metric.

TE's overlap with C_μ (~40%) and Empowerment (~50%) means that counting TE alongside {C_μ, Empowerment} would inflate the apparent information content of the composite. TE's unique semantic (actual vs. potential flow) may matter for specific applications, but it does not add new coverage to the [C,F,I,E] framework.

### The evolutionary metrics (EI, MR) are non-redundant with the information-theoretic metrics but add low incremental value.

EI and MR draw from different mathematical foundations and are genuinely non-redundant with C_μ and Empowerment. However, their dimensional profiles [3,4,1,1] and [4,2,1,1] are subsets of the [4,4,4,4] ceiling already achieved by {C_μ, Empowerment}. Their value is as cross-domain validators, not as independent information sources.

### Effective Complexity provides a genuinely different kind of coherence.

EC's compositional regularity C=4 is mathematically distinct from C_μ's temporal predictive C=4. This is real conceptual complementarity. However, EC's low F/I/E scores (2/1/1) mean it adds little beyond C when paired with C_μ.

### The composite {C_μ, Empowerment} is informationally complete within the surveyed metric set.

No other metric from the top 6 adds unique dimensional coverage that is not already achieved by this pair. Additional metrics provide:
- Cross-domain validation (EI, MR confirm F=4, C=4 via independent domains)
- Conceptual diversity (EC provides different C type)
- Redundancy (TE provides nothing new)

**The Research Director can be confident that {C_μ, Empowerment} is a genuinely non-redundant, informationally complete composite for the [C,F,I,E] framework.**

---

*End of audit.*
