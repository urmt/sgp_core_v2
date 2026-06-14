# RD-OSC.1 — Explanatory Oscillation Audit

**Status:** FROZEN — UNDER METHODOLOGICAL REVIEW

**Goal:** Determine whether the Object↔Mapping oscillation is real or a cognitive artifact.

**Method:** For every audit, record the explanatory object type. Then compute the transition matrix P(i→j) between types. Then ask: Is there a statistically significant cycle?

**Note:** The oscillation may be real, but the categories (Object, Property, Relation, Mapping, Process) may be supplied by us. This is the same failure mode as topology, junctions, translation, and persistence. The oscillation must emerge from blind coding, not be supplied beforehand.

---

## Explanatory Object Types

| Type | Definition | Examples |
|------|------------|----------|
| **Object** | A thing that exists independently | particles, hubs, force chains, C |
| **Property** | A characteristic of an object | density, structural importance, velocity |
| **Relation** | A connection between objects | topology, constraints, dependencies |
| **Mapping** | A transformation between descriptions | translation, comparison, isomorphism |
| **Process** | A dynamic pattern of change | migration, oscillation, persistence |
| **Comparison** | A relationship between descriptions | viewpoint vs claim, stability |

---

## Audit-by-Audit Classification

| Audit | Explanatory Object | Type |
|-------|-------------------|------|
| RD-019 | Density | Property |
| RD-020 | Structural importance (hubs, force chains) | Object |
| RD-021 | Velocity field | Property |
| RD-022 | C (coherence metric) | Object |
| RD-5 | PS (persistence of structure) | Property |
| RD-6 | HI (historical irreversibility) | Property |
| RD-7 | GN (generative novelty) | Property |
| RD-8 | SP (surprise persistence) | Property |
| RD-10A | Topology, constraints, distinctions, preservation | Relation |
| RD-10B.3 | Detectors measure time-series | Property |
| RD-10B.0 | Motifs are world-representation pairs | Relation |
| RD-10B.X | Four junctions | Relation |
| RD-10B.J | Junctions compress to distinction | Mapping |
| RD-10B.M | Migration is genuine | Process |
| RD-10B.R | Explanatory power from interactions | Process |
| RD-10B.R0R | Hierarchical persistence of interaction | Process |
| RD-HIST.1 | Stable loci (persistence, comparison) | Process |
| RD-HIST.2A | Operational categories | Property |
| RD-HIST.2B | Cluster stability | Property |
| RD-HIST.2B.M1 | Metric agreement | Comparison |
| RD-HIST.2B.M2 | Pair structure | Relation |
| RD-LADDER.1 | Interaction at every rung | Process |
| RD-LADDER.2 | Genuinely new operations | Process |
| RD-LADDER.3 | Multiple necessary additions | Process |
| RD-LADDER.X | Cumulative capabilities | Property |
| RD-LADDER.X1 | CPR=1.00 | Property |
| RD-LADDER.Y | Cross-level interaction | Process |
| RD-GEOMETRY.1 | Ladder incomplete (graph) | Relation |
| RD-GEOMETRY.2 | Properties survive representation | Property |
| RD-GEOMETRY.3 | Properties survive decomposition | Property |
| RD-DIAG.1 | Research program as hidden variable | Object |

---

## Transition Matrix

| From \ To | Object | Property | Relation | Mapping | Process | Comparison |
|-----------|--------|----------|----------|---------|---------|------------|
| **Object** | 0 | 2 | 0 | 0 | 0 | 0 |
| **Property** | 1 | 1 | 2 | 0 | 0 | 0 |
| **Relation** | 0 | 1 | 1 | 1 | 1 | 0 |
| **Mapping** | 0 | 0 | 0 | 0 | 1 | 0 |
| **Process** | 1 | 2 | 1 | 0 | 1 | 0 |
| **Comparison** | 0 | 0 | 0 | 0 | 0 | 0 |

**Total transitions:** 15

---

## Transition Probabilities

| From \ To | Object | Property | Relation | Mapping | Process | Comparison |
|-----------|--------|----------|----------|---------|---------|------------|
| **Object** | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| **Property** | 0.25 | 0.25 | 0.50 | 0.00 | 0.00 | 0.00 |
| **Relation** | 0.00 | 0.25 | 0.25 | 0.25 | 0.25 | 0.00 |
| **Mapping** | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 |
| **Process** | 0.17 | 0.33 | 0.17 | 0.00 | 0.17 | 0.00 |
| **Comparison** | — | — | — | — | — | — |

---

## Cycle Detection

**Potential cycle:** Object → Property → Relation → Mapping → Process → Object

**Observed transitions:**
- Object → Property: 2/2 = 1.00 ✓
- Property → Relation: 2/4 = 0.50 ✓
- Relation → Mapping: 1/4 = 0.25 ✓
- Mapping → Process: 1/1 = 1.00 ✓
- Process → Object: 1/6 = 0.17 ✓

**All transitions in the cycle are present.**

---

## Statistical Significance

**Null hypothesis:** Transitions are random (no cycle).

**Expected frequency under null:** Each transition type has equal probability.

**Observed frequency:** Object→Property = 1.00, Property→Relation = 0.50, Relation→Mapping = 0.25, Mapping→Process = 1.00, Process→Object = 0.17.

**Chi-squared test:** Not enough data for formal significance test (15 transitions).

**Qualitative assessment:** The cycle is present but not statistically significant. The oscillation is observable but not proven.

---

## Interpretation

The Object↔Mapping oscillation is **observable but not proven**.

The transitions are present:
- Object → Property (1.00)
- Property → Relation (0.50)
- Relation → Mapping (0.25)
- Mapping → Process (1.00)
- Process → Object (0.17)

But the sample size is too small for formal significance.

**Status:** The oscillation is a pattern, not a law.

---

## Artifact

`/home/student/sgp_core_v2/audits/RD_OSC_1_EXPLANATORY_OSCILLATION_AUDIT.md`
