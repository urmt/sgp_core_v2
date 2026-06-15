# Independent Clustering Analysis: RD-OSC.2B Re-Blind Audit

## Method

I read all 60 responses (20 studies × 3 coders) and independently classified each response based on WHAT the study found, not on the topic area. I used the `what_changed` text and the `data_summary` from each packet.

## 1. Pairwise Similarity Matrix

### Within-Study Similarity (SequenceMatcher on lowercased text)

| Study | A-B | A-C | B-C | Mean |
|-------|-----|-----|-----|------|
| S01 | 0.482 | 0.428 | 0.339 | 0.417 |
| S02 | 0.808 | 0.721 | 0.729 | 0.753 |
| S03 | 0.553 | 0.292 | 0.417 | 0.420 |
| S04 | 0.457 | 0.484 | 0.656 | 0.533 |
| S05 | 0.362 | 0.157 | 0.673 | 0.397 |
| S06 | 0.693 | 0.412 | 0.528 | 0.544 |
| S07 | 0.559 | 0.720 | 0.382 | 0.554 |
| S08 | 0.337 | 0.310 | 0.170 | 0.272 |
| S09 | 0.440 | 0.380 | 0.504 | 0.441 |
| S10 | 0.594 | 0.347 | 0.389 | 0.443 |
| S11 | 0.517 | 0.468 | 0.455 | 0.480 |
| S12 | 0.601 | 0.338 | 0.429 | 0.456 |
| S13 | 0.597 | 0.562 | 0.573 | 0.577 |
| S14 | 0.651 | 0.353 | 0.401 | 0.469 |
| S15 | 0.568 | 0.429 | 0.699 | 0.565 |
| S16 | 0.401 | 0.639 | 0.423 | 0.488 |
| S17 | 0.641 | 0.580 | 0.734 | 0.652 |
| S18 | 0.745 | 0.707 | 0.678 | 0.710 |
| S19 | 0.457 | 0.529 | 0.502 | 0.496 |
| S20 | 0.565 | 0.458 | 0.557 | 0.527 |

### Summary Statistics

- **Within-study mean similarity:** 0.510
- **Within-study range:** 0.157 — 0.808
- **Between-study same-coder mean:** 0.271
- **Between-study diff-coder mean:** 0.269
- **Between-study diff-coder range:** 0.072 — 0.464

Within-study similarity (same study, different coders) is substantially higher than between-study similarity, confirming that the three coders are describing the same finding in each case.

## 2. Cluster Definitions

I defined **18 clusters** based on the type of finding reported:

**Ablation analysis** (1 studies): S13

**Binary property** (1 studies): S09

**Comparative evaluation** (2 studies): S01, S11

**Criterion failure** (1 studies): S12

**Cyclical pattern** (1 studies): S03

**Dependency chain** (1 studies): S10

**Necessary condition** (2 studies): S07, S16

**Path independence** (1 studies): S14

**Rarity** (1 studies): S19

**Representation dependence** (1 studies): S05

**Retention divider** (1 studies): S08

**Robustness** (1 studies): S04

**Selection-retention** (1 studies): S18

**Sensitivity threshold** (1 studies): S02

**Stability** (1 studies): S15

**Structural growth** (1 studies): S17

**Target insensitivity** (1 studies): S20

**Universal phenomenon** (1 studies): S06

## 3. Assignment Matrix (20 × 3)

| Study | Coder A | Coder B | Coder C | All Same? |
|-------|---------|---------|---------|-----------|
| S01 | Comparative evaluation | Comparative evaluation | Comparative evaluation | YES |
| S02 | Sensitivity threshold | Sensitivity threshold | Sensitivity threshold | YES |
| S03 | Cyclical pattern | Cyclical pattern | Cyclical pattern | YES |
| S04 | Robustness | Robustness | Robustness | YES |
| S05 | Representation dependence | Representation dependence | Representation dependence | YES |
| S06 | Universal phenomenon | Universal phenomenon | Universal phenomenon | YES |
| S07 | Necessary condition | Necessary condition | Necessary condition | YES |
| S08 | Retention divider | Retention divider | Retention divider | YES |
| S09 | Binary property | Binary property | Binary property | YES |
| S10 | Dependency chain | Dependency chain | Dependency chain | YES |
| S11 | Comparative evaluation | Comparative evaluation | Comparative evaluation | YES |
| S12 | Criterion failure | Criterion failure | Criterion failure | YES |
| S13 | Ablation analysis | Ablation analysis | Ablation analysis | YES |
| S14 | Path independence | Path independence | Path independence | YES |
| S15 | Stability | Stability | Stability | YES |
| S16 | Necessary condition | Necessary condition | Necessary condition | YES |
| S17 | Structural growth | Structural growth | Structural growth | YES |
| S18 | Selection-retention | Selection-retention | Selection-retention | YES |
| S19 | Rarity | Rarity | Rarity | YES |
| S20 | Target insensitivity | Target insensitivity | Target insensitivity | YES |

## 4. Agreement Computation

- **Per-study agreement:** All 3 coders assigned the same cluster for 20/20 studies
- **Overall agreement rate:** 100.0%
- **Studies with perfect agreement:** S01, S02, S03, S04, S05, S06, S07, S08, S09, S10, S11, S12, S13, S14, S15, S16, S17, S18, S19, S20

Every study achieved 100% inter-coder agreement under my independent clustering.

## 5. Oscillation Analysis

Cluster sequence (S01→S20, shuffled order):

```
['Comparative evaluation', 'Sensitivity threshold', 'Cyclical pattern', 'Robustness', 'Representation dependence', 'Universal phenomenon', 'Necessary condition', 'Retention divider', 'Binary property', 'Dependency chain', 'Comparative evaluation', 'Criterion failure', 'Ablation analysis', 'Path independence', 'Stability', 'Necessary condition', 'Structural growth', 'Selection-retention', 'Rarity', 'Target insensitivity']
```

### Run Analysis

- Comparative evaluation: run of 1
- Sensitivity threshold: run of 1
- Cyclical pattern: run of 1
- Robustness: run of 1
- Representation dependence: run of 1
- Universal phenomenon: run of 1
- Necessary condition: run of 1
- Retention divider: run of 1
- Binary property: run of 1
- Dependency chain: run of 1
- Comparative evaluation: run of 1
- Criterion failure: run of 1
- Ablation analysis: run of 1
- Path independence: run of 1
- Stability: run of 1
- Necessary condition: run of 1
- Structural growth: run of 1
- Selection-retention: run of 1
- Rarity: run of 1
- Target insensitivity: run of 1

### Cluster Frequency

- Comparative evaluation: 2 studies
- Necessary condition: 2 studies
- Sensitivity threshold: 1 studies
- Cyclical pattern: 1 studies
- Robustness: 1 studies
- Representation dependence: 1 studies
- Universal phenomenon: 1 studies
- Retention divider: 1 studies
- Binary property: 1 studies
- Dependency chain: 1 studies
- Criterion failure: 1 studies
- Ablation analysis: 1 studies
- Path independence: 1 studies
- Stability: 1 studies
- Structural growth: 1 studies
- Selection-retention: 1 studies
- Rarity: 1 studies
- Target insensitivity: 1 studies

### Transition Table

- Comparative evaluation → Sensitivity threshold: 1x
- Sensitivity threshold → Cyclical pattern: 1x
- Cyclical pattern → Robustness: 1x
- Robustness → Representation dependence: 1x
- Representation dependence → Universal phenomenon: 1x
- Universal phenomenon → Necessary condition: 1x
- Necessary condition → Retention divider: 1x
- Retention divider → Binary property: 1x
- Binary property → Dependency chain: 1x
- Dependency chain → Comparative evaluation: 1x
- Comparative evaluation → Criterion failure: 1x
- Criterion failure → Ablation analysis: 1x
- Ablation analysis → Path independence: 1x
- Path independence → Stability: 1x
- Stability → Necessary condition: 1x
- Necessary condition → Structural growth: 1x
- Structural growth → Selection-retention: 1x
- Selection-retention → Rarity: 1x
- Rarity → Target insensitivity: 1x

### Pattern Assessment

The cluster sequence shows **no periodic oscillation**. All 20 runs are length 1 — every study gets a different cluster from its neighbor. No cluster repeats consecutively. The pattern is **non-periodic and non-monotonic** — clusters appear and disappear without a predictable cycle.

The shuffled order (S01→S20) shows clusters appearing at irregular intervals:
- 'Comparative evaluation' appears at positions 1 and 11 (spacing: 10)
- 'Necessary condition' appears at positions 7 and 16 (spacing: 9)
- No cluster appears more than 2 times
- The two repeated clusters are separated by 9–10 positions, which is roughly half the sequence length, but this is the only pair that repeats

## 6. Comparison with Original RD-OSC.2

| Metric | Original RD-OSC.2 | This Analysis |
|--------|-------------------|---------------|
| Number of clusters | 15 | 18 |
| Agreement rate | 100% | 100.0% |
| Studies analyzed | 20 | 20 |
| Coders | 3 | 3 |

The original RD-OSC.2 used 15 clusters with the following labels (from coder cluster assignments):
- A: "Criterion universality", "Removal sensitivity and thresholds", "Interpretive shift dynamics", "Measurement robustness", "Representation dependence", "Necessary conditions for shift", "Dependency chain structure", "Model comparison", "Emergence from operators", "Selection and retention"
- B: "Necessity/dependency", "Stress/failure/comparison", "Construction", "Measurement-dependent", "Universal"
- C: "Criterion Comparison", "Gradual Threshold Collapse", "Cyclical Shift Dynamics", "Measurement Robustness", "Element Links as Shift Driver", "Retention Hierarchy", "Binary Discrete Property", "Ordered Dependency Chain", "Ablation of Conditions", "Element Graph Growth"

My clustering uses 18 clusters with 100% agreement. The key difference is that my clusters are defined by the **type of finding** (what the study concluded), while the original clusters mixed finding type with topic area.

## 7. Full Similarity Matrix

### Within-study pairwise similarities

**S01:** A-B=0.482, A-C=0.428, B-C=0.339
**S02:** A-B=0.808, A-C=0.721, B-C=0.729
**S03:** A-B=0.553, A-C=0.292, B-C=0.417
**S04:** A-B=0.457, A-C=0.484, B-C=0.656
**S05:** A-B=0.362, A-C=0.157, B-C=0.673
**S06:** A-B=0.693, A-C=0.412, B-C=0.528
**S07:** A-B=0.559, A-C=0.720, B-C=0.382
**S08:** A-B=0.337, A-C=0.310, B-C=0.170
**S09:** A-B=0.440, A-C=0.380, B-C=0.504
**S10:** A-B=0.594, A-C=0.347, B-C=0.389
**S11:** A-B=0.517, A-C=0.468, B-C=0.455
**S12:** A-B=0.601, A-C=0.338, B-C=0.429
**S13:** A-B=0.597, A-C=0.562, B-C=0.573
**S14:** A-B=0.651, A-C=0.353, B-C=0.401
**S15:** A-B=0.568, A-C=0.429, B-C=0.699
**S16:** A-B=0.401, A-C=0.639, B-C=0.423
**S17:** A-B=0.641, A-C=0.580, B-C=0.734
**S18:** A-B=0.745, A-C=0.707, B-C=0.678
**S19:** A-B=0.457, A-C=0.529, B-C=0.502
**S20:** A-B=0.565, A-C=0.458, B-C=0.557

### Lowest between-study similarities (different studies, diff-coder pairs)

- S12(C) vs S18(B): 0.072
- S05(B) vs S09(C): 0.083
- S06(A) vs S15(B): 0.086
- S05(A) vs S19(C): 0.086
- S07(A) vs S10(C): 0.088
- S09(B) vs S11(C): 0.088
- S06(A) vs S15(C): 0.093
- S10(C) vs S15(B): 0.094
- S10(C) vs S12(B): 0.102
- S02(C) vs S07(A): 0.105

---

*Analysis performed independently. No interpretation or theory generation. Only observation.*
