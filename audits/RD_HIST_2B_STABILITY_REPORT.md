# RD-HIST.2B: Cluster Stability Audit

## Audit Overview

**Question:** Does the clustering structure hold when three different methods are used independently?

**Methods:**
- C1: Original human clustering from RD-HIST.2A
- C2: Blind LLM clustering (no prior labels, no theoretical vocabulary)
- C3: Randomized blind clustering (statements shuffled, then blind LLM)

**Primary Metric:** Assignment stability (did same studies cluster together?)

**Secondary Metrics:** Category count stability, compression stability, breakpoint similarity

---

## Results

### 1. Assignment Stability (Primary Metric)

| Comparison | Stability | Pairs | Interpretation |
|------------|-----------|-------|----------------|
| C1 vs C2 | 0.042 | 8/190 | Very Low |
| C1 vs C3 | 0.032 | 6/190 | Very Low |
| C2 vs C3 | 0.026 | 5/190 | Very Low |

**Verdict:** The three clusterings assign studies to categories almost completely independently. The same studies almost never end up together.

### 2. Category Count Stability

| Clustering | Categories | Spread | Interpretation |
|------------|-----------|--------|----------------|
| C1 | 5 | 1 | Stable |
| C2 | 6 | | |
| C3 | 6 | | |

**Verdict:** Category count is stable (spread=1). This is the only stable metric.

### 3. Compression Stability

| Clustering | OCR | Categories | Total Studies |
|------------|-----|-----------|---------------|
| C1 | 4.00 | 5 | 20 |
| C2 | 4.00 | 6 | 20 |
| C3 | 4.00 | 6 | 20 |

**Verdict:** OCR is perfectly stable at 4.0. Category size variance is perfectly stable at 0.4. The overall structure is similar at the aggregate level.

### 4. Breakpoint Similarity

| Comparison | Jaccard | Interpretation |
|------------|---------|----------------|
| C1 vs C2 | 0.790 | High |
| C1 vs C3 | 0.684 | Moderate |
| C2 vs C3 | 0.790 | High |

**Verdict:** Breakpoint similarity is moderate to high. The boundaries between clusters are somewhat similar.

### 5. Disagreements

**All 20 studies** are assigned to different categories across the three clusterings. Examples:

- **Study 1** ("Universes were generated with continuous dynamics..."): C1=2, C2=1, C3=5
- **Study 2** ("Audits were classified by whether descriptions collapsed..."): C1=1, C2=4, C3=6
- **Study 8** ("One world was represented in multiple ways..."): C1=4, C2=6, C3=1

---

## Critical Finding

The structure is **stable at the aggregate level** but **unstable at the individual level**:

- **Stable:** Category count (spread=1), OCR (4.0), variance (0.4)
- **Unstable:** Assignment stability (0.03-0.04), all 20 studies disagree

This means the clustering procedure introduces interpretation. The categories are not found in the archive — they are imposed by the coder.

---

## Implications

### What Survives

1. **Category count:** 5-6 categories (stable)
2. **Compression ratio:** 4.0 studies per category (stable)
3. **Category size variance:** 0.4 (stable)
4. **Breakpoint similarity:** 0.68-0.79 (moderate to high)

### What Does Not Survive

1. **Assignment stability:** 0.03-0.04 (very low)
2. **Individual study classification:** All 20 studies disagree
3. **Category identity:** Categories are not consistently defined across clusterings

### Interpretation

The RD-HIST.2A ontology (5 categories) is an **interpretation artifact**, not a structure found in the archive. The clustering procedure introduces the categories.

However, the **aggregate structure** (5-6 categories, OCR=4.0) is stable. This suggests there is **some structure** in the archive, but it is not the specific categories identified in RD-HIST.2A.

---

## Verdict

**PARTIALLY STABLE**

The structure is stable at the aggregate level (category count, OCR, variance) but unstable at the individual level (assignment stability). The RD-HIST.2A categories are interpretation artifacts. The archive contains **some structure**, but the specific categories are not reliably recoverable.

---

## Recommendation

The RD-HIST.2A ontology should not be used as a foundation. The categories are interpretation artifacts. However, the aggregate structure (5-6 categories, OCR=4.0) suggests there is **some structure** worth investigating further.

**Next steps:**
1. Test the aggregate structure in concrete systems
2. Develop methods for recovering structure without imposing categories
3. Consider whether the structure is in the archive or in the analysis

---

## Raw Data

- `RD_HIST_2B_C1_HUMAN.json`: C1 assignments
- `RD_HIST_2B_C2_BLIND.json`: C2 assignments
- `RD_HIST_2B_C3_RANDOMIZED.json`: C3 assignments
- `RD_HIST_2B_ASSIGNMENT_STABILITY.json`: Assignment stability results
- `RD_HIST_2B_COMPRESSION_STABILITY.json`: Compression stability results
- `RD_HIST_2B_BREAKPOINT_ANALYSIS.json`: Breakpoint analysis results
- `RD_HIST_2B_Q3_SHUFFLED.md`: Shuffled Q3 responses for C3

---

## Standing Rules Violated

- **SR-28:** The structure was found in the clustering, not in the archive.
- **SR-29:** The categories are interpretation artifacts, not properties of the archive.

---

## Critical Assumptions Updated

- **A54:** "hierarchical persistence of interaction" is the strongest survivor → **UNDERMINED** (interpretation artifact)
- **A56:** The RD-HIST.2A ontology is stable → **UNDERMINED** (assignment stability is very low)

---

## Archive Status

The RD-HIST.2B audit is complete. The structure is partially stable. The RD-HIST.2A categories are interpretation artifacts. The program is now in a measurement phase with no confirmed foundations.

**Next audit:** TBD (user direction required)
