# RD-METRIC.3: Composite Coverage Audit for Ψ ≈ f(C, F, I, E)

**Purpose:** Determine whether existing metrics can be combined to approximate Ψ without inventing new mathematics. Combinatorial coverage analysis of the top 7 metrics scored in RD-METRIC.2.

**Date:** 2026-06-15

---

## 1. Coverage Vectors for Top 7 Metrics

Each metric is scored [C, F, I, E] on a 0–5 scale per RD-METRIC.2 rubric.

| # | Metric | C | F | I | E | Total | Weakest |
|---|--------|---|---|---|---|-------|---------|
| 1 | **Empowerment** | 3 | 4 | 4 | 4 | **15** | C=3 |
| 2 | **Crutchfield's C_μ** | 4 | 4 | 4 | 3 | **15** | E=3 |
| 3 | **Transfer Entropy** | 3 | 4 | 4 | 3 | **14** | C=3, E=3 |
| 4 | **Evolvability Index** | 3 | 4 | 1 | 1 | **9** | I=1, E=1 |
| 5 | **Effective Complexity** | 4 | 2 | 1 | 1 | **8** | I=1, E=1 |
| 6 | **Sophistication** | 4 | 2 | 0 | 0 | **6** | I=0, E=0 |
| 7 | **Mutational Robustness** | 4 | 2 | 1 | 1 | **8** | I=1, E=1 |

**Observation:** The top 7 split into three structural families:
- **Information-theoretic** (C_μ, Transfer Entropy, Empowerment): Strong on I and E, moderate-to-strong on C and F
- **Algorithmic complexity** (Effective Complexity, Sophistication): Strong on C, weak on F/I/E
- **Evolutionary** (Evolvability Index, Mutational Robustness): Strong on C and F, weak on I and E

---

## 2. Combination Analysis Method

For each combination S of metrics, compute:
- **Combined vector:** For each dimension d ∈ {C, F, I, E}, take max{m(d) : m ∈ S}
- **Total coverage:** Sum of combined vector (max = 20)
- **Minimum dimension:** The weakest dimension in the combined vector
- **Blind spots:** Dimensions where combined score < 3
- **Redundancy check:** Does any proper subset of S achieve the same combined vector?

---

## 3. Single Metric Analysis

| Metric | Combined Vector | Total | Min | Blind Spots (score < 3) |
|--------|----------------|-------|-----|------------------------|
| **Empowerment** | [3, 4, 4, 4] | **15** | 3 | None |
| **C_μ** | [4, 4, 4, 3] | **15** | 3 | None |
| Transfer Entropy | [3, 4, 4, 3] | **14** | 3 | None |
| Evolvability Index | [3, 4, 1, 1] | **9** | 1 | I, E |
| Effective Complexity | [4, 2, 1, 1] | **8** | 1 | F, I, E |
| Mutational Robustness | [4, 2, 1, 1] | **8** | 1 | F, I, E |
| Sophistication | [4, 2, 0, 0] | **6** | 0 | F, I, E |

**Best single metric:** **Empowerment** or **C_μ** (tie at total=15, min=3, no blind spots at <3).

Empowerment edges out on E (4 vs 3). C_μ edges out on C (4 vs 3). Both have no blind spots. Neither captures Ψ fully — both score C=3 or E=3, which is moderate, not strong.

---

## 4. Pair Analysis

All C(7,2) = 21 pairs evaluated. Combined vector = element-wise max.

| Pair | C | F | I | E | Total | Min | Blind Spots |
|------|---|---|---|---|-------|-----|-------------|
| **C_μ + Empowerment** | 4 | 4 | 4 | 4 | **16** | 4 | None |
| **Transfer Entropy + Empowerment** | 3 | 4 | 4 | 4 | **15** | 3 | None |
| C_μ + Transfer Entropy | 4 | 4 | 4 | 3 | **15** | 3 | None |
| C_μ + Evolvability Index | 4 | 4 | 4 | 3 | **15** | 3 | None |
| C_μ + Effective Complexity | 4 | 4 | 4 | 3 | **15** | 3 | None |
| C_μ + Mutational Robustness | 4 | 4 | 4 | 3 | **15** | 3 | None |
| C_μ + Sophistication | 4 | 4 | 4 | 3 | **15** | 3 | None |
| Transfer Entropy + Evolvability Index | 3 | 4 | 4 | 3 | **14** | 3 | None |
| Transfer Entropy + Effective Complexity | 3 | 4 | 4 | 3 | **14** | 3 | None |
| Transfer Entropy + Mutational Robustness | 3 | 4 | 4 | 3 | **14** | 3 | None |
| Transfer Entropy + Sophistication | 3 | 4 | 4 | 3 | **14** | 3 | None |
| Empowerment + Effective Complexity | 4 | 4 | 4 | 4 | **16** | 4 | None |
| Empowerment + Mutational Robustness | 4 | 4 | 4 | 4 | **16** | 4 | None |
| Empowerment + Evolvability Index | 3 | 4 | 4 | 4 | **15** | 3 | None |
| Empowerment + Sophistication | 4 | 4 | 4 | 4 | **16** | 4 | None |
| Evolvability Index + Effective Complexity | 4 | 4 | 1 | 1 | **10** | 1 | I, E |
| Evolvability Index + Mutational Robustness | 4 | 4 | 1 | 1 | **10** | 1 | I, E |
| Evolvability Index + Sophistication | 4 | 4 | 1 | 1 | **10** | 1 | I, E |
| Effective Complexity + Mutational Robustness | 4 | 2 | 1 | 1 | **8** | 1 | F, I, E |
| Effective Complexity + Sophistication | 4 | 2 | 1 | 1 | **8** | 1 | F, I, E |
| Mutational Robustness + Sophistication | 4 | 2 | 1 | 1 | **8** | 1 | F, I, E |

### Key pair findings:

**Maximum total = 16** achieved by 5 pairs:
1. C_μ + Empowerment
2. Empowerment + Effective Complexity
3. Empowerment + Mutational Robustness
4. Empowerment + Sophistication
5. (C_μ + Empowerment is the canonical pair from RD-METRIC.2)

**Best pair (highest total, highest min):** **C_μ + Empowerment** — total=16, min=4, no blind spots.

This is the only pair where *every* dimension reaches level 4. All other total=16 pairs achieve the same via element-wise max, but C_μ+Empowerment is the most balanced: C_μ contributes C=4, Empowerment contributes E=4, and both share F=4, I=4.

**Redundancy:** C_μ and Empowerment are complementary, not redundant. Their vectors differ on C (4 vs 3) and E (3 vs 4). Neither dominates the other.

---

## 5. Triple Analysis

All C(7,3) = 35 triples evaluated. The critical question: does any *subset* of the triple already achieve the same combined vector?

### Triples achieving total=16 with no blind spots:

| Triple | C | F | I | E | Total | Min | Redundant? |
|--------|---|---|---|---|-------|-----|------------|
| **C_μ + Empowerment + Transfer Entropy** | 4 | 4 | 4 | 4 | **16** | 4 | **Yes** — {C_μ, Empowerment} already = [4,4,4,4] |
| **C_μ + Empowerment + Effective Complexity** | 4 | 4 | 4 | 4 | **16** | 4 | **Yes** — {C_μ, Empowerment} already = [4,4,4,4] |
| **C_μ + Empowerment + Mutational Robustness** | 4 | 4 | 4 | 4 | **16** | 4 | **Yes** — {C_μ, Empowerment} already = [4,4,4,4] |
| **C_μ + Empowerment + Evolvability Index** | 4 | 4 | 4 | 4 | **16** | 4 | **Yes** — {C_μ, Empowerment} already = [4,4,4,4] |
| **C_μ + Empowerment + Sophistication** | 4 | 4 | 4 | 4 | **16** | 4 | **Yes** — {C_μ, Empowerment} already = [4,4,4,4] |
| **Transfer Entropy + Empowerment + Effective Complexity** | 4 | 4 | 4 | 4 | **16** | 4 | **No** — no pair achieves [4,4,4,4]; TE lacks C=4, EC lacks I/E |
| **Transfer Entropy + Empowerment + Mutational Robustness** | 4 | 4 | 4 | 4 | **16** | 4 | **No** — same logic |
| **Transfer Entropy + Empowerment + Sophistication** | 4 | 4 | 4 | 4 | **16** | 4 | **No** — same logic |
| **Transfer Entropy + Empowerment + Evolvability Index** | 3 | 4 | 4 | 4 | **15** | 3 | — |
| **Mutational Robustness + Evolvability Index + Empowerment** | 4 | 4 | 4 | 4 | **16** | 4 | **No** — MR lacks I/E, EI lacks I/E, Emp lacks C=4; no pair reaches [4,4,4,4] |
| **Sophistication + Evolvability Index + Empowerment** | 4 | 4 | 4 | 4 | **16** | 4 | **No** — Soph lacks F/I/E, EI lacks I/E, Emp lacks C=4; no pair reaches [4,4,4,4] |
| **Sophistication + C_μ + Information Gain** | 4 | 4 | 4 | 4 | **16** | 4 | **No** — (outside top 7 but noted for completeness) |

### Non-redundant triples (total=16, no subset achieves same):

| Triple | Contribution Map |
|--------|-----------------|
| **{Mutational Robustness, Evolvability Index, Empowerment}** | MR→C=4, EI→F=4, Emp→I=4,E=4. Each dimension sourced from a different metric. |
| **{Sophistication, Evolvability Index, Empowerment}** | Soph→C=4, EI→F=4, Emp→I=4,E=4. Same structure, different C-source. |
| **{Transfer Entropy, Empowerment, Effective Complexity}** | TE→I=4, Emp→E=4,F=4, EC→C=4. Cross-domain bridge triple. |
| **{Transfer Entropy, Empowerment, Mutational Robustness}** | TE→I=4, Emp→E=4,F=4, MR→C=4. Biological + information-theoretic bridge. |
| **{Transfer Entropy, Empowerment, Sophistication}** | TE→I=4, Emp→E=4,F=4, Soph→C=4. Algorithmic + information-theoretic bridge. |

---

## 6. The Full Set of All 7 Top Metrics

| | C | F | I | E | Total | Min |
|---|---|---|---|---|-------|-----|
| All 7 combined | 4 | 4 | 4 | 4 | **16** | 4 |

**Redundant.** The pair {C_μ, Empowerment} already achieves [4,4,4,4]. Adding the remaining 5 metrics adds zero new dimensional coverage.

---

## 7. Blind Spot Analysis

### Definition: A blind spot exists when a dimension scores < 3 in the combined vector.

| Combination | Blind Spots | Dimensions below 3 |
|-------------|-------------|-------------------|
| Best single: Empowerment | **None** | — (C=3 is moderate, not blind) |
| Best single: C_μ | **None** | — (E=3 is moderate, not blind) |
| Best single: Transfer Entropy | **None** | — (C=3, E=3 moderate) |
| Best single: Evolvability Index | **I, E** | I=1, E=1 |
| Best single: Effective Complexity | **F, I, E** | F=2, I=1, E=1 |
| Best single: Mutational Robustness | **F, I, E** | F=2, I=1, E=1 |
| Best single: Sophistication | **F, I, E** | F=2, I=0, E=0 |
| Best pair: C_μ + Empowerment | **None** | — |
| Best pair: TE + Empowerment | **None** | — |
| Best pair: Empowerment + EC | **None** | — |
| Best triple: {MR, EI, Emp} | **None** | — |
| Best triple: {TE, Emp, EC} | **None** | — |
| Full set (all 7) | **None** | — |

**Key insight:** No combination of the top 7 metrics produces a blind spot at <3 that isn't already present in the individual metrics. The information-theoretic metrics (C_μ, TE, Empowerment) already cover all four dimensions at ≥3 individually. The algorithmic and evolutionary metrics only add value by *raising* already-covered dimensions from 3 to 4.

---

## 8. Additive vs. Redundant Classification

### Pair additivity:

| Pair | Additive? | Reasoning |
|------|-----------|-----------|
| C_μ + Empowerment | **Complementary** | C_μ provides C=4 (Emp has 3); Emp provides E=4 (C_μ has 3). Different dimensions strengthened. |
| TE + Empowerment | **Complementary** | TE provides C=3 (same as Emp), but combined vector reaches [3,4,4,4]. Emp adds E=4 that TE lacks. |
| C_μ + TE | **Partially redundant** | Both score I=4, F=4. C_μ adds C=4, TE adds nothing C_μ doesn't have at C=3. Net gain: C from 3→4. |
| EC + Empowerment | **Complementary** | EC provides C=4 (Emp has 3). Emp provides I=4, E=4 (EC has 1,1). Strong complementarity. |
| MR + Empowerment | **Complementary** | Same structure as EC + Empowerment. |
| EI + Empowerment | **Partially redundant on F** | Both score F=4. Emp adds I=4, E=4 that EI lacks. EI adds nothing Emp doesn't have. |

### Triple additivity:

| Triple | Additive? | Reasoning |
|--------|-----------|-----------|
| {MR, EI, Emp} | **Fully complementary** | MR→C=4, EI→F=4, Emp→I=4,E=4. Each metric is the sole source of one dimension. No redundancy. |
| {Soph, EI, Emp} | **Fully complementary** | Same structure. Soph→C=4 replaces MR. |
| {TE, Emp, EC} | **Mostly complementary** | TE and Emp share I=4, F=4 (partial overlap). EC uniquely provides C=4. Emp uniquely provides E=4. |
| {C_μ, Emp, anything} | **Redundant** | {C_μ, Emp} already = [4,4,4,4]. Third metric adds nothing. |

---

## 9. Summary of Best Combinations

### Best single metric: **Empowerment** or **C_μ**

| | C | F | I | E | Total | Min | Blind Spots |
|---|---|---|---|---|-------|-----|-------------|
| Empowerment | 3 | 4 | 4 | 4 | 15 | 3 | None |
| C_μ | 4 | 4 | 4 | 3 | 15 | 3 | None |

**Coverage:** 75% of maximum (15/20). No blind spots, but C=3 or E=3 is moderate, not strong. Each metric is missing the dimension the other provides.

### Best pair: **C_μ + Empowerment**

| | C | F | I | E | Total | Min | Blind Spots |
|---|---|---|---|---|-------|-----|-------------|
| Combined | 4 | 4 | 4 | 4 | **16** | **4** | None |

**Coverage:** 80% of maximum (16/20). Every dimension at level 4. Complementary — neither metric dominates. This is the minimum combination that achieves full coverage at the 4-level within the top 7.

**Second-best pair:** Transfer Entropy + Empowerment (total=15, min=3). Fails to raise C to 4.

### Best triple: **{Mutational Robustness, Evolvability Index, Empowerment}**

| | C | F | I | E | Total | Min | Blind Spots |
|---|---|---|---|---|-------|-----|-------------|
| Combined | 4 | 4 | 4 | 4 | **16** | **4** | None |

**Coverage:** 80% of maximum. Fully complementary — each metric is the sole source of one dimension (MR→C, EI→F, Emp→I,E). No pair within the triple achieves [4,4,4,4]. This is the only non-redundant triple within the top 7 that achieves full coverage.

**Alternative non-redundant triples:**
- {Sophistication, Evolvability Index, Empowerment} — same structure, algorithmic C-source
- {Transfer Entropy, Empowerment, Effective Complexity} — information-theoretic + algorithmic bridge

---

## 10. Coverage Ceiling Analysis

### Why total=16, not 20?

No metric in the RD-METRIC.2 survey scores any dimension at 5. The maximum per-dimension score is 4. Therefore:
- **Theoretical maximum for any combination:** 4 × 4 = 16
- **Achieved by best pair:** 16/16 = 100% of achievable ceiling
- **Achieved by best single:** 15/16 = 93.75% of achievable ceiling

### What the ceiling means:

The absence of any 5-score metrics indicates that **no existing metric directly measures any dimension of Ψ**. All scores of 4 are strong *relations* but not *direct measures*. The gap from 4→5 represents the conceptual distance between:
- Measuring structural regularity (C=4) vs. measuring coherence-of-parts-in-assembly (C=5)
- Measuring generative capacity (F=4) vs. measuring the capacity to enable further coherent experience (F=5)
- Measuring information flow (I=4) vs. measuring the relational event of observation (I=5)
- Measuring agent-relative sensor states (E=4) vs. measuring experience as intrinsic property (E=5)

**This ceiling is not a limitation of combination — it is a limitation of the metric vocabulary itself.**

---

## 11. Principal Findings

1. **The pair {C_μ, Empowerment} achieves the achievable ceiling.** Total=16, min=4, no blind spots. Within the surveyed metrics, this is the minimal combination that covers all four dimensions at the highest observed level.

2. **No triple is needed.** The pair already saturates the ceiling. Triples add redundancy, not coverage — unless the goal is cross-domain validation (biological + information-theoretic + algorithmic).

3. **The non-redundant triple {MR, EI, Empowerment} is the most elegant three-metric combination.** Each metric uniquely provides one dimension. It is the only triple where no subset of two achieves the same coverage.

4. **The ceiling of 16/20 (not 20/20) reveals the fundamental gap.** No existing metric scores 5 on any dimension. The combination analysis shows that *coverage* can be achieved, but *depth* cannot — no metric reaches the direct-measure level on any dimension of Ψ.

5. **The additivity pattern is clear:** Information-theoretic metrics (C_μ, TE, Emp) are complementary to algorithmic (EC, Soph) and evolutionary (MR, EI) metrics. Within the information-theoretic cluster, metrics are partially redundant. The most informative combinations cross cluster boundaries.

6. **Within the surveyed metric set, Empowerment appears in every highest-coverage combination.** It is the only metric scoring E=4, and it appears in every combination that achieves total ≥ 15. Without Empowerment, no combination reaches E=4.

---

## 12. Implications for Ψ

The working space Ψ ≈ f(C, F, I, E) can be *approximated* by the pair {C_μ, Empowerment}, which together cover all four dimensions at level 4. However:

- This approximation is **surface-level**: it captures the *presence* of each dimension but not its *depth* or *mutual entanglement*.
- The function f in Ψ ≈ f(C, F, I, E) remains uncharacterized — the combination tells us *what* to measure but not *how the dimensions interact*.
- The ceiling of 16/20 means that 20% of the conceptual space (the gap between relation and direct measure) is unoccupied by any existing metric.

**The combination {C_μ, Empowerment} is the best available approximation of Ψ within existing mathematics. It is necessary but not sufficient.**

---

*End of audit.*
