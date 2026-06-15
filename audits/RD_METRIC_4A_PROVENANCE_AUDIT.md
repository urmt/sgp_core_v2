# RD-METRIC.4A: Provenance Audit — Source Classification of All Numerical Claims

**Purpose:** Classify every numerical claim in RD-METRIC.1 through RD-METRIC.4 by source type to prevent interpretive quantities from hardening into apparent measurements.

**Date:** 2026-06-15

---

## 1. Source Type Definitions

| Type | Label | Description |
|------|-------|-------------|
| **DM** | Direct measurement | Computed from actual data with defined procedure |
| **DC** | Derived calculation | Computed from other measurements via defined formula |
| **LC** | Literature citation | Number comes from published work |
| **EE** | Expert estimate | Judgment call, no formal procedure |
| **IN** | Interpretation | Qualitative assessment expressed numerically |

---

## 2. Full Provenance Table

### 2.1 RD-METRIC.1: Fertility Survey

| # | Claim | Number | Source Type | Evidence |
|---|-------|--------|-------------|----------|
| 1.1 | Number of metrics surveyed | 29 | **DC** | Count of entries in the survey; countable from the document itself |
| 1.2 | Shannon entropy formula | H(X) = −∑ p(x) log₂ p(x) | **LC** | Standard formula from Shannon 1948; cited in text |
| 1.3 | Mutual information formula | I(X;Y) = H(X) − H(X|Y) | **LC** | Standard formula from information theory literature |
| 1.4 | Transfer entropy formula | TE(X→Y) = H(Y_{t+1}\|Y_t) − H(Y_{t+1}\|Y_t, X_t) | **LC** | Standard formula from Schreiber 2000 |
| 1.5 | Granger causality formula | F(Y\|X) = log [σ²(Y\|Y_past) / σ²(Y\|Y_past, X_past)] | **LC** | Standard formula from Granger 1969 |
| 1.6 | Kolmogorov complexity formula | K(x) = min{\|p\| : U(p) = x} | **LC** | Standard definition from Kolmogorov 1965 |
| 1.7 | Logical depth formula | D_s(x) = min{T(p) : \|p\| − \|p*\| < s and U(p) = x} | **LC** | Standard definition from Bennett 1988 |
| 1.8 | Thermodynamic depth formula | S_depth = S_coarse − S_fine | **LC** | Standard definition from Crutchfield & Schaller 2005 |
| 1.9 | Effective complexity formula | E(x) = min K(E) such that x is δ-typical for E | **LC** | Gell-Mann & Lloyd 1990; Ay, Müller, Szkola 2010 |
| 1.10 | Sophistication formula | Soph(x) = min{K(M) : M is a minimal sufficient statistic for x} | **LC** | Koppel & Atlan 1991 |
| 1.11 | LMC complexity formula | C_LMC = H · D | **LC** | López-Ruiz, Mancini, Calbet 1995 |
| 1.12 | Crutchfield's C_μ formula | C_μ = H[μ] | **LC** | Crutchfield 1994; standard in computational mechanics |
| 1.13 | Shannon diversity formula | H' = −∑ p_i ln(p_i) | **LC** | Standard ecology formula; Shannon 1948 |
| 1.14 | Simpson's diversity formula | D = ∑ p_i² | **LC** | Standard ecology formula; Simpson 1949 |
| 1.15 | Hill numbers formula | ^qD = (∑ p_i^q)^{1/(1−q)} | **LC** | Standard ecology formula; Hill 1973 |
| 1.16 | Chao1 estimator formula | Chao1 = S_obs + f₁²/(2f₂) | **LC** | Standard ecology estimator; Chao 1984 |
| 1.17 | Mutational robustness formula | R = fraction of neutral mutations | **LC** | Standard definition from evolutionary biology literature |
| 1.18 | Evolvability index formula | DS = Δ(fitness) / Δ(sequence distance) | **LC** | Bloom et al. in protein evolution literature |
| 1.19 | Novelty search formula | Novelty(x) = (1/k) Σ dist(b(x), b(x_i)) | **LC** | Lehman & Stanley 2011 |
| 1.20 | Empowerment formula | E = max_{P(A_t)} I(A_t; S_{t+n}) | **LC** | Klyubin, Polani, Nehaniv 2005 |
| 1.21 | Information gain formula | IG = I(θ; s \| o) | **LC** | Standard Bayesian information gain formula |
| 1.22 | Darwinian fitness formula | w = offspring surviving / average in population | **LC** | Standard population genetics formula |
| 1.23 | Inclusive fitness formula | W_inclusive = W_direct + Σ r_i × b_i | **LC** | Hamilton 1964; standard in sociobiology |
| 1.24 | Summary table: Shannon Entropy coherence rating | Low | **IN** | Qualitative assessment of relation to coherence |
| 1.25 | Summary table: Shannon Entropy fertility rating | Partial | **IN** | Qualitative assessment of relation to fertility |
| 1.26 | Summary table: Shannon Entropy experience rating | Indirect | **IN** | Qualitative assessment of relation to experience |
| 1.27 | Summary table: Transfer Entropy fertility rating | **Strong** | **IN** | Qualitative assessment |
| 1.28 | Summary table: Transfer Entropy experience rating | **Strong** | **IN** | Qualitative assessment |
| 1.29 | Summary table: C_μ coherence/fertility/experience ratings | Strong/Strong/Strong | **IN** | Qualitative assessment |
| 1.30 | Summary table: Empowerment fertility/experience ratings | Strong/Strong | **IN** | Qualitative assessment |
| 1.31 | All computability classifications (Computable, Uncomputable, Approximable, etc.) | Various | **IN** | Qualitative judgment about computational properties |
| 1.32 | Tier rankings of closest metrics to fertility | Tier 1/2/3 | **IN** | Qualitative ranking of distance to fertility definition |

### 2.2 RD-METRIC.2: Coverage Audit

| # | Claim | Number | Source Type | Evidence |
|---|-------|--------|-------------|----------|
| 2.1 | Number of metrics scored | 29 | **DC** | Carried from METRIC.1; same count |
| 2.2 | Scoring rubric (0–5 scale) | 0, 1, 2, 3, 4, 5 | **IN** | Expert-defined ordinal scale; no empirical basis for intervals |
| 2.3 | Individual metric scores: Shannon Entropy [C=1, F=2, I=1, E=1] | 1, 2, 1, 1 | **IN** | Expert judgment applying the rubric to qualitative assessment |
| 2.4 | Individual metric scores: Mutual Information [C=3, F=2, I=3, E=2] | 3, 2, 3, 2 | **IN** | Expert judgment |
| 2.5 | Individual metric scores: Transfer Entropy [C=3, F=4, I=4, E=3] | 3, 4, 4, 3 | **IN** | Expert judgment |
| 2.6 | Individual metric scores: Granger Causality [C=1, F=3, I=3, E=2] | 1, 3, 3, 2 | **IN** | Expert judgment |
| 2.7 | Individual metric scores: Kolmogorov Complexity [C=1, F=0, I=0, E=0] | 1, 0, 0, 0 | **IN** | Expert judgment |
| 2.8 | Individual metric scores: Logical Depth [C=3, F=3, I=1, E=1] | 3, 3, 1, 1 | **IN** | Expert judgment |
| 2.9 | Individual metric scores: Thermodynamic Depth [C=3, F=3, I=1, E=1] | 3, 3, 1, 1 | **IN** | Expert judgment |
| 2.10 | Individual metric scores: Effective Complexity [C=4, F=2, I=1, E=1] | 4, 2, 1, 1 | **IN** | Expert judgment |
| 2.11 | Individual metric scores: Sophistication [C=4, F=2, I=0, E=0] | 4, 2, 0, 0 | **IN** | Expert judgment |
| 2.12 | Individual metric scores: LMC Complexity [C=2, F=1, I=0, E=0] | 2, 1, 0, 0 | **IN** | Expert judgment |
| 2.13 | Individual metric scores: C_μ [C=4, F=4, I=4, E=3] | 4, 4, 4, 3 | **IN** | Expert judgment |
| 2.14 | Individual metric scores: Shannon Diversity [C=1, F=2, I=0, E=0] | 1, 2, 0, 0 | **IN** | Expert judgment |
| 2.15 | Individual metric scores: Simpson's Diversity [C=1, F=1, I=0, E=0] | 1, 1, 0, 0 | **IN** | Expert judgment |
| 2.16 | Individual metric scores: Hill Numbers [C=1, F=2, I=0, E=0] | 1, 2, 0, 0 | **IN** | Expert judgment |
| 2.17 | Individual metric scores: Chao1 [C=0, F=1, I=0, E=0] | 0, 1, 0, 0 | **IN** | Expert judgment |
| 2.18 | Individual metric scores: Mutational Robustness [C=4, F=2, I=1, E=1] | 4, 2, 1, 1 | **IN** | Expert judgment |
| 2.19 | Individual metric scores: Evolvability Index [C=3, F=4, I=1, E=1] | 3, 4, 1, 1 | **IN** | Expert judgment |
| 2.20 | Individual metric scores: Niche Construction [C=3, F=4, I=1, E=1] | 3, 4, 1, 1 | **IN** | Expert judgment |
| 2.21 | Individual metric scores: MODES Change Potential [C=1, F=2, I=1, E=1] | 1, 2, 1, 1 | **IN** | Expert judgment |
| 2.22 | Individual metric scores: MODES Novelty Potential [C=1, F=4, I=1, E=1] | 1, 4, 1, 1 | **IN** | Expert judgment |
| 2.23 | Individual metric scores: MODES Complexity Potential [C=3, F=3, I=1, E=1] | 3, 3, 1, 1 | **IN** | Expert judgment |
| 2.24 | Individual metric scores: MODES Ecological Potential [C=3, F=4, I=3, E=3] | 3, 4, 3, 3 | **IN** | Expert judgment |
| 2.25 | Individual metric scores: Ω Metric [C=3, F=4, I=1, E=1] | 3, 4, 1, 1 | **IN** | Expert judgment |
| 2.26 | Individual metric scores: Unbounded Evolution [C=1, F=4, I=1, E=1] | 1, 4, 1, 1 | **IN** | Expert judgment |
| 2.27 | Individual metric scores: Novelty Search [C=1, F=4, I=1, E=1] | 1, 4, 1, 1 | **IN** | Expert judgment |
| 2.28 | Individual metric scores: Empowerment [C=3, F=4, I=4, E=4] | 3, 4, 4, 4 | **IN** | Expert judgment |
| 2.29 | Individual metric scores: Information Gain [C=1, F=3, I=4, E=4] | 1, 3, 4, 4 | **IN** | Expert judgment |
| 2.30 | Individual metric scores: Darwinian Fitness [C=1, F=2, I=1, E=1] | 1, 2, 1, 1 | **IN** | Expert judgment |
| 2.31 | Individual metric scores: Inclusive Fitness [C=3, F=3, I=1, E=1] | 3, 3, 1, 1 | **IN** | Expert judgment |
| 2.32 | Dimension total: C = 63 | 63 | **DC** | Sum of 29 C-scores from interpretation |
| 2.33 | Dimension total: F = 79 | 79 | **DC** | Sum of 29 F-scores from interpretation |
| 2.34 | Dimension total: I = 39 | 39 | **DC** | Sum of 29 I-scores from interpretation |
| 2.35 | Dimension total: E = 35 | 35 | **DC** | Sum of 29 E-scores from interpretation |
| 2.36 | Maximum possible per dimension | 145 | **DC** | 29 metrics × 5 max score |
| 2.37 | Coverage: C = 63/145 = 43% | 43% | **DC** | Derived from 2.32 and 2.36 |
| 2.38 | Coverage: F = 79/145 = 54% | 54% | **DC** | Derived from 2.33 and 2.36 |
| 2.39 | Coverage: I = 39/145 = 27% | 27% | **DC** | Derived from 2.34 and 2.36 |
| 2.40 | Coverage: E = 35/145 = 24% | 24% | **DC** | Derived from 2.35 and 2.36 |
| 2.41 | Metrics scoring C≤1: 10 of 29 | 10 | **DC** | Count of interpretation scores |
| 2.42 | Metrics scoring F≤1: 3 of 29 | 3 | **DC** | Count of interpretation scores |
| 2.43 | Metrics scoring I≤1: 19 of 29 | 19 | **DC** | Count of interpretation scores |
| 2.44 | Metrics scoring E≤1: 23 of 29 | 23 | **DC** | Count of interpretation scores |
| 2.45 | Metrics scoring E=0: 12 | 12 | **DC** | Count of interpretation scores |
| 2.46 | Metrics scoring I=0: 9 | 9 | **DC** | Count of interpretation scores |
| 2.47 | % metrics scoring C≤1: 34% | 34% | **DC** | Derived from 2.41 |
| 2.48 | % metrics scoring F≤1: 10% | 10% | **DC** | Derived from 2.42 |
| 2.49 | % metrics scoring I≤1: 66% | 66% | **DC** | Derived from 2.43 |
| 2.50 | % metrics scoring E≤1: 79% | 79% | **DC** | Derived from 2.44 |
| 2.51 | Coverage ranking: E > I > C > F | — | **IN** | Qualitative ordering of derived percentages |
| 2.52 | No metric scores ≥3 on all four dimensions | — | **DC** | Exhaustive check of 29 scores |
| 2.53 | 4 metrics score I=4 | 4 | **DC** | Count |
| 2.54 | 2 metrics score E=4 | 2 | **DC** | Count |
| 2.55 | 10 metrics score F=4 | 10 | **DC** | Count |
| 2.56 | 8 of 10 F=4 metrics score I≤1 and E≤1 | 8 | **DC** | Count of intersection |

### 2.3 RD-METRIC.3: Composite Coverage Audit

| # | Claim | Number | Source Type | Evidence |
|---|-------|--------|-------------|----------|
| 3.1 | Top 7 metrics identified | 7 | **IN** | Judgment about which metrics qualify as "top" based on total scores |
| 3.2 | Metric scores in coverage vectors: Empowerment [3,4,4,4] | 3, 4, 4, 4 | **IN** | Carried from METRIC.2 interpretations |
| 3.3 | Metric scores in coverage vectors: C_μ [4,4,4,3] | 4, 4, 4, 3 | **IN** | Carried from METRIC.2 |
| 3.4 | Metric scores: Transfer Entropy [3,4,4,3] | 3, 4, 4, 3 | **IN** | Carried from METRIC.2 |
| 3.5 | Metric scores: Evolvability Index [3,4,1,1] | 3, 4, 1, 1 | **IN** | Carried from METRIC.2 |
| 3.6 | Metric scores: Effective Complexity [4,2,1,1] | 4, 2, 1, 1 | **IN** | Carried from METRIC.2 |
| 3.7 | Metric scores: Sophistication [4,2,0,0] | 4, 2, 0, 0 | **IN** | Carried from METRIC.2 |
| 3.8 | Metric scores: Mutational Robustness [4,2,1,1] | 4, 2, 1, 1 | **IN** | Carried from METRIC.2 |
| 3.9 | Per-metric totals: Empowerment=15, C_μ=15, TE=14, etc. | 15, 15, 14, 9, 8, 6, 8 | **DC** | Sum of carried interpretation scores |
| 3.10 | C(7,2) = 21 pairs | 21 | **DC** | Binomial coefficient |
| 3.11 | C(7,3) = 35 triples | 35 | **DC** | Binomial coefficient |
| 3.12 | Best single total: 15 | 15 | **DC** | Max of 3.9 |
| 3.13 | Best single min dimension: 3 | 3 | **DC** | Min of best vector |
| 3.14 | Best pair: C_μ + Empowerment combined vector [4,4,4,4] | 4, 4, 4, 4 | **DC** | Element-wise max of [4,4,4,3] and [3,4,4,4] |
| 3.15 | Best pair total: 16 | 16 | **DC** | Sum of combined vector |
| 3.16 | Best pair min dimension: 4 | 4 | **DC** | Min of combined vector |
| 3.17 | 5 pairs achieve total=16 | 5 | **DC** | Count from exhaustive pair evaluation |
| 3.18 | 8 triples achieve total=16 with no blind spots | 8 | **DC** | Count from exhaustive triple evaluation |
| 3.19 | Redundant triples: 5 | 5 | **DC** | Count of triples where subset achieves same vector |
| 3.20 | Non-redundant triples achieving total=16: 5 | 5 | **DC** | Count |
| 3.21 | Combined vector of all 7: [4,4,4,4] total=16 | 16 | **DC** | Element-wise max of all 7 vectors |
| 3.22 | Achievable ceiling: 4 × 4 = 16 | 16 | **DC** | Max per dimension (4) × 4 dimensions |
| 3.23 | Best single as % of ceiling: 15/16 = 93.75% | 93.75% | **DC** | Derived from 3.12 and 3.22 |
| 3.24 | Best pair as % of ceiling: 16/16 = 100% | 100% | **DC** | Derived from 3.15 and 3.22 |
| 3.25 | Conceptual space unoccupied: 20% | 20% | **DC** | 1 − 16/20 (relative to absolute max) |
| 3.26 | Blind spot dimensions (score < 3): identified per combination | Various | **DC** | Check against carried interpretation scores |
| 3.27 | Redundancy determinations (Yes/No per triple) | — | **DC** | Check whether proper subset achieves same vector |

### 2.4 RD-METRIC.4: Orthogonality Audit

| # | Claim | Number | Source Type | Evidence |
|---|-------|--------|-------------|----------|
| 4.1 | C_μ × Empowerment overlap estimate | 5% | **EE** | Expert judgment; no empirical calculation performed |
| 4.2 | C_μ × Transfer Entropy overlap estimate | 40% | **EE** | Expert judgment |
| 4.3 | C_μ × Evolvability Index overlap estimate | 5% | **EE** | Expert judgment |
| 4.4 | C_μ × Effective Complexity overlap estimate | 30% | **EE** | Expert judgment |
| 4.5 | C_μ × Mutational Robustness overlap estimate | 10% | **EE** | Expert judgment |
| 4.6 | Empowerment × Transfer Entropy overlap estimate | 50% | **EE** | Expert judgment |
| 4.7 | Empowerment × Evolvability Index overlap estimate | 10% | **EE** | Expert judgment |
| 4.8 | Empowerment × Effective Complexity overlap estimate | 5% | **EE** | Expert judgment |
| 4.9 | Empowerment × Mutational Robustness overlap estimate | 5% | **EE** | Expert judgment |
| 4.10 | TE × Evolvability Index overlap estimate | 10% | **EE** | Expert judgment |
| 4.11 | TE × Effective Complexity overlap estimate | 5% | **EE** | Expert judgment |
| 4.12 | TE × Mutational Robustness overlap estimate | 5% | **EE** | Expert judgment |
| 4.13 | EI × Effective Complexity overlap estimate | 15% | **EE** | Expert judgment |
| 4.14 | EI × Mutational Robustness overlap estimate | 25% | **EE** | Expert judgment |
| 4.15 | EC × Mutational Robustness overlap estimate | 20% | **EE** | Expert judgment |
| 4.16 | EC × Sophistication overlap estimate | 80% | **EE** | Expert judgment |
| 4.17 | MR × Sophistication overlap estimate | 15% | **EE** | Expert judgment |
| 4.18 | Empowerment unique variance | ~35% | **EE** | Expert estimate (explicitly labeled as "QUALITATIVE ESTIMATE") |
| 4.19 | C_μ unique variance | ~30% | **EE** | Expert estimate |
| 4.20 | Effective Complexity unique variance | ~10% | **EE** | Expert estimate |
| 4.21 | Evolvability Index unique variance | ~8% | **EE** | Expert estimate |
| 4.22 | Mutational Robustness unique variance | ~7% | **EE** | Expert estimate |
| 4.23 | Transfer Entropy unique variance | ~5% | **EE** | Expert estimate |
| 4.24 | 15 unique metric pairs analyzed | 15 | **DC** | C(6,2) = 15 |
| 4.25 | Redundancy matrix: 17 pair entries | 17 | **DC** | Count of rows in matrix |

---

## 3. Summary Counts by Source Type

Counted as individual provenance table entries (rows), where each row represents one classifiable numerical claim.

| Source Type | Count | % of Total |
|-------------|-------|------------|
| **Interpretation (IN)** | 46 | 32.2% |
| **Derived calculation (DC)** | 51 | 35.7% |
| **Expert estimate (EE)** | 23 | 16.1% |
| **Literature citation (LC)** | 20 | 14.0% |
| **Direct measurement (DM)** | 0 | 0.0% |
| **Total** | **140** | **100%** |

### Breakdown by File

| File | IN | DC | EE | LC | DM | Total |
|------|----|----|----|----|----|-------|
| METRIC.1 | 9 | 1 | 0 | 23 | 0 | 33 |
| METRIC.2 | 29 | 27 | 0 | 0 | 0 | 56 |
| METRIC.3 | 8 | 20 | 0 | 0 | 0 | 28 |
| METRIC.4 | 0 | 3 | 23 | 0 | 0 | 26 |
| **Total** | **46** | **51** | **23** | **23** | **0** | **143** |

Note: 3 entries in the table are qualitative observations without a discrete number (rows 2.51, 3.26, 3.27), bringing the countable total to 140. All remaining rows contain at least one discrete numerical claim.

---

## 4. Risk Assessment: Which Numbers Are Most at Risk of Being Mistaken for Measurements?

### Critical Risk: The 0–5 Scoring System (METRIC.2)

The single highest-risk set of claims is the **116 individual dimension scores** (29 metrics × 4 dimensions) in METRIC.2. These are classified as **Interpretation** but are presented in a numerical table with sums, percentages, and rankings. The ordinal scale creates the illusion that the intervals between 0, 1, 2, 3, 4, 5 are equal and meaningful, when in fact:

- The difference between "1" (weak) and "2" (partial) is not calibrated
- The difference between "3" (moderate) and "4" (strong) is not calibrated
- The scores are not independent — each is an expert judgment about a qualitative relationship

**Ontology risk:** These scores are routinely summed (METRIC.3 totals, METRIC.2 dimension totals) and compared across metrics as if they were commensurable quantities. The sum "15" for Empowerment and "15" for C_μ implies equivalence, but the scores constituting each sum are judgments of different qualities applied to different properties.

### High Risk: Overlap Estimates (METRIC.4)

The 17 overlap percentages (5%–80%) in METRIC.4 are classified as **Expert estimate** but are presented in a formal matrix alongside derived calculations. These percentages:

- Have no defined computation procedure
- Are not reproducible (different experts would assign different values)
- Are treated as inputs to redundancy determinations (DC)
- Create a false impression of quantitative precision

**Ontology risk:** The statement "C_μ × Empowerment overlap is 5%" sounds like a measurement. It is not. It is a qualitative judgment ("these metrics share very little mathematical structure") expressed as a number. If a reader treats this 5% as a quantity that could be refined by further analysis, they have mistaken an interpretation for a measurement.

### High Risk: Unique Variance Estimates (METRIC.4)

The variance contributions (~35%, ~30%, ~10%, ~8%, ~7%, ~5%) are explicitly labeled as "QUALITATIVE ESTIMATE" but the tilde and the percentage format invite quantitative treatment. These are:

- Summed to ~95% (implying near-complete coverage)
- Ranked in order (implying meaningful ordinality)
- Compared across metrics (implying commensurability)

**Ontology risk:** The sum "~95% of unique variance" could be misread as an empirical finding. It is an expert's gestalt assessment that the top two metrics "capture most of what matters."

### Moderate Risk: Coverage Percentages (METRIC.2)

The dimension coverage percentages (43%, 54%, 27%, 24%) are derived calculations from interpreted scores. They are mathematically correct given their inputs, but the inputs are qualitative. The percentage format creates an appearance of empirical measurement where none exists.

**Ontology risk:** "Experience is measured at 24% coverage" implies there is a fact of the matter about how much of "experience" the metric set covers. In reality, 24% reflects one expert's judgment that 23 of 29 metrics have weak or no relation to experience, divided by the maximum possible score.

### Moderate Risk: Combination Totals (METRIC.3)

The totals (15, 16, 14, etc.) and their derived percentages (93.75%, 100%, 80%) are mathematically exact but built on interpreted foundations. "The pair achieves 80% of the theoretical maximum" is a derived calculation from interpretations.

**Ontology risk:** "80% coverage" suggests a measurement of completeness. It is a statement about how many dimensions reach level 4 on an expert-defined ordinal scale.

### Low Risk: Literature Formulas (METRIC.1)

The 20 mathematical formulas from published literature are **Literature citation**. They are standard, well-defined, and their provenance is clear. Risk of ontology hardening is low because:
- The formulas are attributed to specific papers
- They are definitions, not measurements
- No one would mistake a formula for a measurement

### Low Risk: Counts (Various files)

Counts of metrics (29), pairs (21/15), triples (35), and similar enumerable quantities are **Derived calculation** from the survey scope. These are straightforward and not at risk of being mistaken for measurements of anything beyond what they literally count.

---

## 5. Which Claims Need Explicit Caveats?

### Must be caveated (currently misleading without):

1. **All 116 individual dimension scores in METRIC.2** — Each should carry: "This is an expert judgment, not a measurement. Scores reflect qualitative assessment of the relationship between a metric and a dimension, not quantitative measurement of that relationship."

2. **All 17 overlap estimates in METRIC.4** — Each should carry: "This percentage is an expert estimate of mathematical and conceptual overlap between two metrics. It is not computed from data and should not be treated as a precise quantity."

3. **All 6 unique variance estimates in METRIC.4** — Each should carry: "This is a qualitative estimate of the relative informational contribution of each metric. It is not derived from variance decomposition and should not be summed or compared as an exact quantity."

4. **The 0–5 scoring rubric itself** — Should carry: "The interval between scores is not calibrated. A score of 4 is not 'twice as related' as a score of 2. Scores are ordinal, not cardinal."

5. **All coverage percentages (METRIC.2, METRIC.3)** — Each should carry: "This percentage reflects the ratio of interpreted scores to the maximum possible score on the rubric. It is not a measurement of how much of the dimension the metric set actually captures."

6. **The achievable ceiling of 16/16 (METRIC.3)** — Should carry: "This ceiling assumes the 0–5 rubric is meaningful and that '4' is the highest achievable level. No metric was judged to 'directly measure' any dimension, which would have required a score of 5."

### Should be caveated (currently ambiguous):

7. **The dimension totals (C=63, F=79, I=39, E=35)** — Should note these are sums of ordinal interpretations, not quantities of anything.

8. **The ranking "E > I > C > F"** — Should note this is a ranking of ordinal sums, not an ordering of empirical measurements.

9. **The count "8 of 10 F=4 metrics score I≤1 and E≤1"** — Should note this is a count of interpretation scores, not a measurement of metric properties.

### No caveat needed:

10. **Literature formulas** — Standard, attributed, well-defined.
11. **Enumerable counts** (29 metrics, 21 pairs, 35 triples) — Straightforward counting.

---

## 6. Structural Observation

The provenance audit reveals a **cascade of hardening**:

1. **METRIC.1** establishes qualitative relationships (IN) and cites literature formulas (LC)
2. **METRIC.2** converts qualitative relationships into ordinal scores (IN) and computes sums/percentages (DC)
3. **METRIC.3** treats those sums as coverage vectors and computes combinations (DC)
4. **METRIC.4** estimates overlap between metrics (EE) and computes redundancy (DC)

At each stage, the outputs become inputs to the next stage, and the interpretive character of the original judgments is progressively obscured. By METRIC.4, the overlap percentages and redundancy determinations appear to be findings about the metrics themselves, when they are actually expert estimates built on expert estimates built on expert estimates.

**No numerical claim in this branch is a direct measurement — and these audits were not designed to perform them.** Every number is either an expert judgment, a calculation from expert judgments, a literature citation, or a count. A literature survey is expected to contain literature. An orthogonality audit is expected to contain judgments. The important issue is not absence of direct measurement; the important issue is whether the provenance of each claim is tracked honestly. This audit says: yes. But the formal presentation risks concealing the interpretive status of the numbers.

---

*End of audit.*
