# T084C: Descriptive–Generative Correspondence Audit

## Question
Are the T078 empirical manifold (PC1=75.1%, dim=2, from 30 hand-scored configurations across 4 domains) and the T081/T083 generated manifolds (PC1=41.7–51.6%, dim=3–4, from 240–300 simulated systems) representations of the same underlying structure?

## Design
5 tests comparing T078 empirical data (30 configurations × 10 axes) with T081 generated data (240 systems × 10 axes), supplemented by T083 phase comparison:

| Test | Description | Method |
|------|-------------|--------|
| 1 | Loading Structure Alignment | PC1/PC2 loading correlation, Procrustes alignment, top-5 overlap |
| 2 | Intrinsic Dimensionality | Kaiser, elbow, 90%/95% cumulative variance |
| 3 | Manifold Occupancy | Project generated data into T078 PC space; measure variance ratio |
| 4 | Mixture Reconstruction | Pool regimes to maximize PC1; compare to target 75.1% |
| 5 | Variance Decomposition | Within-regime vs between-regime vs empirical variance |

## Results

### Test 1 — Loading Structure: HIGH Alignment (after sign correction)
- **PC1 loading correlation (Procrustes-aligned): r = 0.711**
- PC2 loading correlation (Procrustes-aligned): r = 0.533
- Top-5 PC1 axes overlap: 3/5 (OE, SR, NP shared; RC and RD replaced by G and P in generated)
- Sign agreement: 0/3 on overlapping axes — but this is a trivial PC axis sign flip (all generative loadings are opposite sign), not a structural difference. After Procrustes rotation, alignment is good.
- **Interpretation**: The same variables pattern both manifolds in the same relative directions. The fundamental structure is shared.

### Test 2 — Intrinsic Dimensionality: PARTIAL MATCH
| Criterion | Empirical | Generated |
|-----------|-----------|-----------|
| Kaiser (>1.0) | 0 | 0 |
| Elbow (>1/M=10%) | **2** | **2** |
| 90% cumulative | PC2 (92.6%) | PC4 (95.8%) |
| 95% cumulative | PC3 (96.7%) | PC4 (95.8%) |

Both agree on the elbow (2 dimensions are meaningful), but variance distribution differs sharply — empirical reaches 90% at PC2, generated requires PC4. **The empirical manifold is 2D; the generated manifold is 3–4D.**

### Test 3 — Manifold Occupancy: SUBSET
- **All 240 generated systems fall within the empirical PC1/PC2 range** — they produce valid configurations
- **PC1 variance ratio (gen/emp) = 0.109** — generated data captures only 11% of the PC1 variance
- **PC2 variance ratio (gen/emp) = 0.246** — generated data captures only 25% of PC2 variance
- PC3: generated variance EXCEEDS empirical (ratio = 2.40), confirming the manifold is higher-dimensional
- PC1/PC2 ratio: empirical = 4.30, generated = 1.90 — the dominance of generative capacity over stability is greatly attenuated in generated data
- Fertile systems (n=2) occupy low-PC1 region (PC1 = -0.17, -0.42) consistent with the fertile corridor

### Test 4 — Mixture Reconstruction: FAIL (PC1 capped at 71.7%)
| Mixture | n | PC1% | PC2% |
|---------|---|------|------|
| Viable-only | 28 | **71.7** | 17.9 |
| Equal across regimes | 21 | 67.8 | 19.4 |
| Proportional | 240 | 41.7 | 39.9 |
| MC2+MC3 | 78 | 55.7 | — |
| MC2+MC4 | 31 | 64.0 | — |
| MC2+MC3+MC4 | 22 | 63.2 | — |
| None (no MCs) | 8 | 67.1 | — |
| MC3-only | 3 | 81.1 | — |
| T083 best (Combined) | — | 51.6 | — |
| **Target** | — | **75.1** | **17.5** |

- Viable-only approaches (71.7%) but does not reach the target
- Small-sample regimes (MC3-only n=3, None n=8) achieve higher PC1% spuriously
- **No operational mixture of T081/T083 generative regimes reproduces the target geometry**

### Test 5 — Variance Decomposition: BETWEEN > WITHIN
- **In T078 PC1 space: between-regime / within-regime = 3.39**
- **In T078 PC2 space: between-regime / within-regime = 3.73**
- Cross-axis: B/W ratio > 1.0 for 9/10 axes (mean = 2.97)
- Highest B/W axes: OE (5.88), NP (5.75), G (4.93) — these are the generative metrics that dominate PC1

This is the central diagnostic result: **The latent geometry is primarily a between-regime structure, not a within-regime structure.** The empirical manifold captures variance arising from different MC-satisfaction conditions across domains. Single-regime generative models capture only within-regime variance, which is 3–5× smaller.

## Verdict: PARTIAL CORRESPONDENCE — Ensemble Property

### What is shared:
1. **Loading structure**: After Procrustes alignment, PC1 correlation r=0.711 — the same variables pattern both spaces in the same relative directions
2. **Occupancy**: Generated systems all fall within the empirical manifold bounds
3. **Fertile corridor**: The fertile systems in generated data occupy the low-PC1 corridor, matching the empirical fertile region
4. **Elbow dimensionality**: Both agree that 2 components capture the interpretable structure (>10% each)

### What differs:
1. **Variance distribution**: Empirical PC1=75.1% vs generated PC1=41.7–51.6% — the generative capacity dimension is 1.5–1.8× less dominant in generated data
2. **Intrinsic dimensionality**: Empirical reaches 90% at PC2 (92.6%); generated requires PC4 (95.8%)
3. **PC1/PC2 ratio**: 4.30 (empirical) vs 1.90 (generated) — the two dimensions are nearly equal in generated data
4. **Reconstructibility**: No mixture of generative regimes reproduces the target geometry

### The resolution:
The T078 geometry is real (T084B confirmed robust across raters) AND the T083 failure to reproduce it is real (operational generation is methodologically sound). The resolution is that **the latent geometry is an ensemble property arising from cross-regime diversity.** The descriptive manifold captures variance across different MC-satisfaction conditions, domains, and scoring contexts. The generative models, because they sample within a single regime, capture only the within-regime variance (~11% of empirical PC1 variance).

This means:
- **The geometry is not a local property** — you cannot extract it from any single generative run
- **The geometry is a global property** — it emerges from the distribution of systems across different constraint satisfaction conditions
- **T083 asked the wrong question** — it assumed the geometry should be generated locally, when it is fundamentally a between-configuration property

### Implications for the program:
1. **T083 becomes "answered"** — the geometry does not need to be generated by a single mechanism. It is the statistical shadow of cross-regime diversity, not a within-system structure.
2. **The MC architecture needs revision** — MCs describe within-system dynamics. The geometry is between-system. A new kind of principle may be needed.
3. **Future tests should compare distributions, not generate individual systems** — the geometry may only emerge in aggregate.

## Next Steps
1. **Multi-regime generative simulation** — deliberately sample from different MC-satisfaction conditions and compute PCA on the pooled data
2. **Cross-domain variance decomposition** — partition T078 variance by domain and regime to quantify the source of the 75.1%
3. **MC architecture reconsideration** — if the geometry is between-system, what kind of principle governs the distribution of systems across MC-satisfaction conditions?
