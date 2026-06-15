# RD-METRIC.2: Metric Coverage Audit for Ψ ≈ f(C, F, I, E)

**Purpose:** Score each of the 29 metrics from RD-METRIC.1 on four dimensions of the working space Ψ ≈ f(C, F, I, E), assess coverage completeness, identify gaps, and find complementary metric pairs/triples.

**Date:** 2026-06-14

---

## 1. Scoring Rubric

| Score | Meaning |
|-------|---------|
| 0 | No relation to this dimension |
| 1 | Weak/indirect relation |
| 2 | Partial relation |
| 3 | Moderate relation |
| 4 | Strong relation |
| 5 | Direct measure of this dimension |

**Dimensions:**
- **C** (Coherence sensitivity): Does this metric capture how well parts fit together?
- **F** (Fertility sensitivity): Does this metric capture the capacity to enable further coherent experience?
- **I** (Interaction sensitivity): Does this metric capture interaction, observation, or the relational event?
- **E** (Experience relevance): Does this metric relate to experience, sentience, or first-person reality?

---

## 2. Coverage Matrix

| # | Metric | C | F | I | E | Total |
|---|--------|---|---|---|---|-------|
| 1 | Shannon Entropy | 1 | 2 | 1 | 1 | 5 |
| 2 | Mutual Information | 3 | 2 | 3 | 2 | 10 |
| 3 | Transfer Entropy | 3 | 4 | 4 | 3 | 14 |
| 4 | Granger Causality | 1 | 3 | 3 | 2 | 9 |
| 5 | Kolmogorov Complexity | 1 | 0 | 0 | 0 | 1 |
| 6 | Logical Depth | 3 | 3 | 1 | 1 | 8 |
| 7 | Thermodynamic Depth | 3 | 3 | 1 | 1 | 8 |
| 8 | Effective Complexity | 4 | 2 | 1 | 1 | 8 |
| 9 | Sophistication | 4 | 2 | 0 | 0 | 6 |
| 10 | LMC Complexity | 2 | 1 | 0 | 0 | 3 |
| 11 | Crutchfield's C_μ | 4 | 4 | 4 | 3 | 15 |
| 12 | Shannon Diversity (H') | 1 | 2 | 0 | 0 | 3 |
| 13 | Simpson's Diversity (D) | 1 | 1 | 0 | 0 | 2 |
| 14 | Hill Numbers | 1 | 2 | 0 | 0 | 3 |
| 15 | Chao1 Estimator | 0 | 1 | 0 | 0 | 1 |
| 16 | Mutational Robustness | 4 | 2 | 1 | 1 | 8 |
| 17 | Evolvability Index | 3 | 4 | 1 | 1 | 9 |
| 18 | Niche Construction Index | 3 | 4 | 1 | 1 | 9 |
| 19 | MODES: Change Potential | 1 | 2 | 1 | 1 | 5 |
| 20 | MODES: Novelty Potential | 1 | 4 | 1 | 1 | 7 |
| 21 | MODES: Complexity Potential | 3 | 3 | 1 | 1 | 8 |
| 22 | MODES: Ecological Potential | 3 | 4 | 3 | 3 | 13 |
| 23 | Ω Metric | 3 | 4 | 1 | 1 | 9 |
| 24 | Unbounded Evolution | 1 | 4 | 1 | 1 | 7 |
| 25 | Novelty Search | 1 | 4 | 1 | 1 | 7 |
| 26 | Empowerment | 3 | 4 | 4 | 4 | 15 |
| 27 | Information Gain | 1 | 3 | 4 | 4 | 12 |
| 28 | Darwinian Fitness | 1 | 2 | 1 | 1 | 5 |
| 29 | Inclusive Fitness | 3 | 3 | 1 | 1 | 8 |

**Dimension totals (sum across all 29 metrics):** C = 63, F = 79, I = 39, E = 35

---

## 3. Per-Dimension Analysis

### 3.1 Coherence (C) — Total: 63 / (29×5) = 63/145 = 43%

**Strongest scores (C=4):**
- Effective Complexity — explicitly measures regularities/structure
- Sophistication — complexity of minimal model explaining structure
- Crutchfield's C_μ — structural information enabling prediction
- Mutational Robustness — maintains coherent behavior despite perturbation

**Moderate scores (C=3):**
- Mutual Information, Transfer Entropy, Logical Depth, Thermodynamic Depth, Evolvability Index, Niche Construction Index, MODES: Complexity Potential, MODES: Ecological Potential, Ω Metric, Empowerment, Inclusive Fitness

**Weak/absent (C≤1):**
- Kolmogorov Complexity (1), Shannon Entropy (1), Granger Causality (1), LMC Complexity (2), all ecology diversity indices (0-1), all novelty production metrics (1), Darwinian Fitness (1)

**Gap:** No metric scores C=5. Coherence is never *directly* measured. The best approximations (Effective Complexity, Sophistication, C_μ) capture structural regularity but not the fit between parts in an assembly. Ecological and evolutionary metrics that should capture coherence (niche construction, mutational robustness) do so only indirectly. The ecology diversity indices are particularly weak here — they measure component variety but nothing about how components relate.

### 3.2 Fertility (F) — Total: 79 / (29×5) = 79/145 = 54%

**Strongest scores (F=4):**
- Transfer Entropy — enables future states of another process
- Crutchfield's C_μ — generates structured future states
- Evolvability Index — capacity to generate new forms
- Niche Construction Index — creates conditions for further evolution
- MODES: Novelty Potential — novelty production core to fertility
- MODES: Ecological Potential — ecological interactions = further coherent experience
- Ω Metric — sustained novelty production
- Unbounded Evolution — unbounded novelty production
- Novelty Search — designed to maximize new behaviors
- Empowerment — capacity to affect future states

**Moderate scores (F=3):**
- Granger Causality, Logical Depth, Thermodynamic Depth, MODES: Complexity Potential, Information Gain, Inclusive Fitness

**Weak/absent (F≤1):**
- Kolmogorov Complexity (0), LMC Complexity (1), Simpson's Diversity (1), Chao1 (1)

**Gap:** Fertility is the best-covered dimension, but with a significant pattern: 8 of the 10 highest-scoring metrics score F=4 but score I≤1 and E≤1. These metrics capture generativity in a narrow, process-internal sense. They do not capture the *relational* or *experiential* dimensions of fertility. Only Transfer Entropy, Crutchfield's C_μ, MODES: Ecological Potential, and Empowerment score both F=4 and I≥3 or E≥3.

### 3.3 Interaction (I) — Total: 39 / (29×5) = 39/145 = 27%

**Strongest scores (I=4):**
- Transfer Entropy — information flow between processes
- Crutchfield's C_μ — information processing capacity
- Empowerment — agent's capacity through action
- Information Gain — reducing uncertainty through experience

**Moderate scores (I=3):**
- Mutual Information, Granger Causality, MODES: Ecological Potential

**Weak/absent (I≤1):**
- 19 of 29 metrics score I≤1. All ecology diversity indices, all algorithmic complexity measures, all evolutionary metrics, all novelty production metrics, both fitness measures.

**Gap:** Interaction is severely under-measured. No metric scores I=5. Only 4 metrics score I=4, and these are all information-theoretic measures applied to paired processes. The ecology and evolutionary metrics — which conceptually should capture interaction — fail to do so because they measure properties of *components* (species, genotypes) rather than properties of *relational events*. MODES: Ecological Potential (I=3) comes closest but still falls short.

### 3.4 Experience (E) — Total: 35 / (29×5) = 35/145 = 24%

**Strongest scores (E=4):**
- Empowerment — generating sensor states through action
- Information Gain — learning through observation

**Moderate scores (E=3):**
- Transfer Entropy, Crutchfield's C_μ, MODES: Ecological Potential

**Weak/absent (E≤1):**
- 23 of 29 metrics score E≤1 or 0. All ecology diversity indices (0), all algorithmic complexity measures (0-1), all evolutionary metrics (1), all novelty production metrics (1).

**Gap:** Experience is the most under-measured dimension. No metric scores E=5. Only 2 metrics score E=4 (Empowerment, Information Gain), and both are agent-relative — they require an observer/agent to be defined. No metric captures experience as an intrinsic property of a structure. The 12 metrics scoring E=0 have no connection to experience whatsoever.

---

## 4. Does Any Single Metric Dominate All Four Dimensions?

**No.** No metric scores ≥3 on all four dimensions. The closest candidates:

| Metric | C | F | I | E | Weakest |
|--------|---|---|---|---|---------|
| Crutchfield's C_μ | 4 | 4 | 4 | 3 | E=3 (moderate) |
| Empowerment | 3 | 4 | 4 | 4 | C=3 (moderate) |
| Transfer Entropy | 3 | 4 | 4 | 3 | C=3, E=3 (moderate) |
| MODES: Ecological Potential | 3 | 4 | 3 | 3 | C=3 (moderate) |

Crutchfield's C_μ is the closest to four-dimensional coverage, with all scores ≥3. However, its E=3 reflects *processing capacity* rather than *phenomenal experience*. Empowerment has all scores ≥3 but is agent-relative rather than structure-intrinsic.

**Verdict:** No single metric captures Ψ ≈ f(C, F, I, E). The space requires at minimum a combination of metrics.

---

## 5. Do Combinations of Metrics Cover the Space?

**Yes, but with important caveats.**

### Best complementary pairs:

| Pair | C | F | I | E | Gap |
|------|---|---|---|---|-----|
| Crutchfield's C_μ + Empowerment | 4 | 4 | 4 | 4 | None at max, but both C and E only reach 3 from one metric |
| Crutchfield's C_μ + Information Gain | 4 | 4 | 4 | 4 | Same as above |
| Effective Complexity + Empowerment | 4 | 4 | 4 | 4 | I and E only from Empowerment |

### Best complementary triples:

| Triple | C | F | I | E | Assessment |
|--------|---|---|---|---|------------|
| Effective Complexity + Transfer Entropy + Empowerment | 4 | 4 | 4 | 4 | Covers all dimensions at ≥3 |
| Mutational Robustness + Evolvability Index + Empowerment | 4 | 4 | 4 | 4 | Biological + AI coverage |
| Sophistication + Crutchfield's C_μ + Information Gain | 4 | 4 | 4 | 4 | All algorithmic/information-theoretic |

### Why triples are necessary:

- **C+F without I+E:** Effective Complexity + Evolvability Index. Strong on structure and generativity, but silent on interaction and experience.
- **F+I without C+E:** Transfer Entropy + Information Gain. Strong on generativity and interaction, but weak on structural coherence and experience.
- **I+E without C+F:** Empowerment + Information Gain. Strong on interaction and experience, but moderate on coherence and fertility.

The four dimensions are partially independent — no single metric or pair saturates all four. Triples or the special case of C_μ+Empowerment are needed for reasonable coverage.

---

## 6. Which Dimensions Remain Unmeasured or Under-Measured?

### Unmeasured (E=0 for 12 metrics):
- Kolmogorov Complexity, Sophistication, LMC Complexity, Shannon Diversity, Simpson's Diversity, Hill Numbers, Chao1 — have zero connection to experience.

### Severely under-measured:

| Dimension | Metrics scoring ≤1 | % of metrics |
|-----------|-------------------|--------------|
| C (Coherence) | 10 of 29 | 34% |
| F (Fertility) | 3 of 29 | 10% |
| I (Interaction) | 19 of 29 | 66% |
| E (Experience) | 23 of 29 | 79% |

**Ranking of under-measurement:** E > I > C > F

Fertility is the best-covered dimension (only 3 metrics score ≤1). Experience is the worst (23 metrics score ≤1, including 12 at exactly 0). Interaction is second-worst (19 metrics score ≤1, including 9 at exactly 0).

### Structural gap:

The metrics divide into two clusters:
1. **Information-theoretic cluster** (metrics 1-4, 11, 26-27): Covers I and E moderately, but C weakly
2. **Ecological/evolutionary cluster** (metrics 12-18, 28-29): Covers C and F moderately, but I and E very weakly

No metric bridges these clusters in a balanced way. The "bridge" metrics — Transfer Entropy, Crutchfield's C_μ, Empowerment — are all information-theoretic and only partially reach into the ecological/evolutionary domain.

---

## 7. Which Metrics Are Most Complementary?

### Strongest complementary pairs (maximize dimension coverage):

| Pair | Logic |
|------|-------|
| **Crutchfield's C_μ + Empowerment** | C_μ provides C, F, I; Empowerment provides F, I, E. Together: C=4, F=4, I=4, E=4. Closest to full coverage. |
| **Effective Complexity + Information Gain** | EC provides C; IG provides I, E. Transfer Entropy bridges F. |
| **Mutational Robustness + Evolvability Index + Empowerment** | Biological pair (C+F) + AI pair (I+E). Cross-domain coverage. |

### Most complementary single metric to any other:

**Empowerment** is the single most complementary metric. It is the only metric scoring E=4, and it is the only metric that brings the I and E dimensions to their highest observed values. Pairing Empowerment with any strong-C metric (Effective Complexity, Sophistication, or Mutational Robustness) yields the widest coverage with the fewest metrics.

---

## 8. Summary

### Coverage scores by dimension:

| Dimension | Total (max 145) | Coverage % | Status |
|-----------|----------------|------------|--------|
| C (Coherence) | 63 | 43% | Under-measured |
| F (Fertility) | 79 | 54% | Best covered, but concentrated in narrow generativity |
| I (Interaction) | 39 | 27% | Severely under-measured |
| E (Experience) | 35 | 24% | Most under-measured |

### Key findings:

1. **No single metric captures Ψ.** The closest are Crutchfield's C_μ and Empowerment, but each has blind spots.
2. **Fertility dominates the metric landscape.** 10 of 29 metrics score F=4. This reflects the historical focus of complexity science on generativity and open-ended evolution.
3. **Within the surveyed literature, I and E appear comparatively underrepresented relative to C and F.** 66% of metrics score I≤1; 79% score E≤1. The existing metric vocabulary appears built for observer-independent description, not for relational or experiential phenomena.
4. **Coherence is moderately covered but never directly measured.** The best C metrics (Effective Complexity, Sophistication) capture structural regularity, not the fit-between-parts in an assembly.
5. **The ecology/evolutionary and information-theoretic clusters are poorly bridged.** Metrics from one cluster rarely score well on the dimensions emphasized by the other.
6. **Complementary triples are necessary.** No pair of metrics achieves full four-dimensional coverage at the 4-level. Triples like {Effective Complexity, Transfer Entropy, Empowerment} or {Mutational Robustness, Evolvability Index, Empowerment} are needed.

### Implications:

The working space Ψ ≈ f(C, F, I, E) is not captured by any existing metric or small combination. Within the surveyed literature, the I-E interaction-experience axis appears comparatively underrepresented: the existing metric landscape seems built for describing structures and their generative capacity, not for describing relational events or experiential phenomena. Any future metric development targeting Ψ would need to address this axis directly.

---

*End of audit.*
