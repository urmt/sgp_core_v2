# RD-8A: Latent Geometry Recon

**Date:** 2026-06-10
**Status:** COMPLETE
**Directive:** Assemble every metric from all existing studies into one matrix. Let the geometry emerge from data. Determine how many dimensions actually exist.

---

## Executive Summary

Built a 60-run × 12-metric matrix from the t901 ensemble (6 friction levels × 10 reps). Applied PCA, Factor Analysis, clustering, and intrinsic dimensionality estimation.

**Key findings:**

1. **The data lives in 3–6 dimensions** (BIC-optimal: 3 factors; PCA: 6D for 90% variance; MLE intrinsic dimensionality: 5.4)
2. **PC1 (40.7%)** = Fluidity/Activity axis (friction, C, MSE, rms_velocity, msd)
3. **PC2 (16.9%)** = Perturbation Response (C_sigma, MSE, restoration, dip)
4. **PC3 (13.3%)** = Recovery Dynamics (restoration, msd, tau_rec, packing_var)
5. **PC4 (8.2%)** = Neighbor Turnover (standalone)
6. **PC5 (6.1%)** = Recovery Time (tau_rec, packing_var)
7. **Clustering**: 2 clusters (silhouette=0.307), split at μ≈0.40

**The original axes (coherence, fertility, jitter, persistence, adaptability) were wrong.** They assumed those were independent dimensions. The data shows they're projections of a smaller latent structure.

---

## 1. Data Matrix

**Source:** t901 ensemble — 60 runs, 6 friction levels (μ=0.05, 0.10, 0.20, 0.40, 0.60, 0.80), 10 reps each.

**Metrics (12):**

| Category | Metrics |
|----------|---------|
| Information-theoretic | C, I_pred, C_sigma, MSE |
| Physical observables | rms_velocity, msd, neighbor_turnover, packing_var |
| Control parameter | friction |
| Perturbation response | dip, restoration, tau_rec |

---

## 2. PCA: How Many Dimensions?

| PC | Eigenvalue | Explained | Cumulative | Interpretation |
|----|-----------|-----------|------------|----------------|
| 1 | 4.97 | 40.7% | 40.7% | **Fluidity/Activity** |
| 2 | 2.07 | 16.9% | 57.6% | **Perturbation Response** |
| 3 | 1.62 | 13.3% | 71.0% | **Recovery Dynamics** |
| 4 | 1.00 | 8.2% | 79.2% | Neighbor Turnover |
| 5 | 0.74 | 6.1% | 85.3% | Recovery Time |
| 6 | 0.58 | 4.8% | 90.1% | Packing Structure |

**90% variance requires 6 dimensions.** But the scree plot shows a natural break after PC3 (71.0%). The eigenvalue ratio PC1/PC2=2.40 > 2.0 confirms PC1 is dominant. PC9/PC10=3.90 suggests noise floor after PC9.

---

## 3. Factor Analysis: Latent Axes

BIC comparison:

| Factors | BIC | Variance Explained |
|---------|-----|-------------------|
| 1 | 1848 | 35.4% |
| 2 | 1725 | 51.4% |
| **3** | **1676** | **62.8%** |
| 4 | 1696 | 67.0% |
| 5 | 1720 | 73.4% |

**BIC-optimal: 3 factors.** The 3-factor model explains 62.8% of variance.

### Factor Loadings (3-factor model)

| Metric | F1: Fluidity | F2: Perturbation Response | F3: Recovery |
|--------|-------------|--------------------------|--------------|
| friction | **-0.867** | 0.435 | -0.163 |
| rms_velocity | **0.898** | 0.407 | 0.017 |
| C | **0.782** | -0.549 | -0.192 |
| msd | **0.714** | 0.663 | -0.089 |
| MSE | **-0.701** | 0.535 | 0.296 |
| dip | -0.568 | -0.040 | **-0.486** |
| I_pred | 0.500 | -0.474 | -0.125 |
| packing_var | 0.519 | 0.071 | -0.243 |
| C_sigma | -0.332 | 0.264 | **0.462** |
| restoration | 0.372 | -0.087 | **0.693** |
| tau_rec | -0.335 | 0.136 | **-0.463** |
| neighbor_turnover | 0.244 | 0.118 | 0.061 |

**Interpretation:**
- **F1 (Fluidity/Activity):** friction, rms_velocity, C, msd, MSE load heavily. This is the system's thermal/kinetic state.
- **F2 (Perturbation Response):** C, MSE, msd load. How the system responds to being disturbed.
- **F3 (Recovery Dynamics):** restoration, C_sigma, tau_rec, dip. How the system recovers.

---

## 4. Clustering

| k | Silhouette | Cluster boundaries |
|---|-----------|-------------------|
| **2** | **0.307** | μ∈[0.05,0.40] vs μ∈[0.40,0.80] |
| 3 | 0.299 | μ<0.40, μ=0.40-0.60, μ=0.60-0.80 |

The data naturally splits into two regimes at μ≈0.40. This matches the t901 observation that μ=0.40 is transitional.

---

## 5. Intrinsic Dimensionality

| Method | Estimate |
|--------|----------|
| MLE (k=5) | 6.32 |
| MLE (k=10) | 5.39 |
| MLE (k=15) | 5.01 |
| MLE (k=20) | 4.66 |
| Participation Ratio | 4.39 |
| PCA (90% variance) | 6 |

**The data intrinsically lives in ~5 dimensions.** The participation ratio (4.39) suggests the effective dimensionality is even lower than the PCA estimate.

---

## 6. What's Actually There

### The 3 core dimensions (BIC-optimal):

1. **Fluidity** (40.7%): How freely grains move. Controlled by friction. C, MSE, rms_velocity, msd all project onto this.
2. **Perturbation Response** (16.9%): How the system responds to being disturbed. C, MSE, msd, C_sigma project.
3. **Recovery Dynamics** (13.3%): How the system recovers. restoration, tau_rec, dip project.

### Additional dimensions (for 90% variance):

4. **Neighbor Turnover** (8.2%): Standalone dimension, loads -0.74 on neighbor_turnover
5. **Recovery Time** (6.1%): tau_rec, packing_var
6. **Packing Structure** (4.8%): packing_var loads -0.71

### What C actually is:
C loads heavily on F1 (0.782) and F2 (-0.549). It's a **projection of fluidity and perturbation response**. It's not a dimension — it's a mixture of two latent factors.

### What MSE actually is:
MSE loads on F1 (-0.701) and F2 (0.535). It's the **same two factors as C, but with opposite signs**. This explains why C ≈ -MSE (r=-0.89).

---

## 7. Implications for the Initiative

### The original axes were wrong
The Director's hypothesis (coherence, fertility, jitter, persistence, adaptability as independent dimensions) was a reasonable guess. The data shows:
- **C** is not a dimension — it's a projection of fluidity + perturbation response
- **Fertility** was not measured in t901 — unknown whether it's a real dimension
- **Jitter** was partially captured by rms_velocity — it loads on F1 (fluidity)
- **Persistence** was partially captured by packing_var — it loads on F3 (recovery)
- **Adaptability** was partially captured by tau_rec — it loads on F3 (recovery)

### What the Initiative should do
1. **Measure the 3 core dimensions directly**: Fluidity (C + rms_velocity), Perturbation Response (C_sigma + MSE), Recovery (restoration + tau_rec)
2. **Test whether fertility is a 4th dimension**: It wasn't measured — this is an open question
3. **Use the 3-factor model as the state description**: Not 5 named axes, but 3 latent factors

---

## 8. Files

- `audits/rd8a_assemble_matrix.py` — matrix assembly
- `audits/rd8a_geometry_recon.py` — PCA, FA, clustering, ID estimation
- `audits/rd8a_matrix_t901.npy` — 60×12 metric matrix
- `audits/rd8a_metric_names_t901.json` — metric names
- `audits/rd8a_row_metadata.json` — friction/rep per row
- `audits/rd8a_fig1_scree.png` — scree plot + eigenvalue spectrum
- `audits/rd8a_fig2_loadings.png` — PCA loading heatmap
- `audits/rd8a_fig3_factors.png` — FA loadings (3 factors)
- `audits/rd8a_fig4_pca_map.png` — PCA state-space projection
- `audits/rd8a_fig5_correlations.png` — correlation matrix
- `audits/rd8a_fig6_intrinsic_dim.png` — intrinsic dimensionality estimates
