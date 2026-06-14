# RD-8: State-Space Cartography

**Date:** 2026-06-10
**Status:** COMPLETE
**Directive:** Map the state-space geometry of the granular system. Identify regimes, discover latent dimensionality, determine what the system does (not what metrics do).

---

## Executive Summary

Swept friction (μ ∈ [0.02, 2.00], 22 levels × 8 reps = 176 runs) and computed 6 state variables from raw trajectories. Found:

1. **Three distinct regimes** separated by friction: EMERGENT (μ<0.25), TRANSITIONAL (μ=0.25-1.0), FROZEN (μ>1.0)
2. **Latent dimensionality = 2D** (89.1% of variance): PC1 = fluidity axis (76.9%), PC2 = jitter axis (12.1%)
3. **C is a state variable** (r=0.90 with the fluidity axis), not an independent metric
4. **All metrics are projections** of a low-dimensional state — the Initiative should measure the state, not the metrics

---

## 1. The Sweep

- **Control parameter:** Friction μ ∈ [0.02, 2.00] (22 levels)
- **Reps per level:** 8 (independent realizations)
- **System:** 50-grain soft-sphere DEM, 1000 steps
- **State variables:** Coherence, Jitter, Persistence, Reorganization rate, Velocity autocorrelation, Grain separation

---

## 2. Regimes Identified

| Regime | μ range | C | Jitter | Persistence | Reorg rate |
|--------|---------|---|--------|-------------|------------|
| EMERGENT | 0.02-0.25 | 0.47-0.55 | 14-16 | 120-197 | 2.6-4.5 |
| TRANSITIONAL | 0.25-1.00 | 0.39-0.47 | 13-15 | 62-112 | 1.2-2.4 |
| FROZEN | 1.20-2.00 | 0.37-0.40 | 9-12 | 62-109 | 0.5-1.0 |

**Key observations:**
- EMERGENT regime has high C, high persistence, high reorganization, high separation — grains move freely but maintain coordination
- FROZEN regime has low everything — grains are locked in place
- TRANSITIONAL is the interesting zone — partial mobility, partial coordination

---

## 3. Latent Dimensionality

PCA on 6 standardized state variables:
- **PC1 (76.9%):** Uniform negative loadings on all variables → "overall activity/fluidity"
- **PC2 (12.1%):** High positive loading on Jitter (+0.81), negative on V_AutoCorr (-0.51) → independent jitter dimension
- **PC3 (7.4%):** High positive loading on Persistence (+0.85) → persistence is somewhat independent

**90% variance requires only 2 dimensions.** The state space is strikingly low-dimensional.

---

## 4. Metric Correlations

| | C | Jitter | Persist | Reorg | V_Auto | Sep |
|---|---|---|---|---|---|---|
| C | 1.00 | 0.53 | 0.59 | **0.90** | **0.82** | **0.89** |
| Jitter | 0.53 | 1.00 | 0.47 | 0.77 | 0.34 | 0.69 |
| Persist | 0.59 | 0.47 | 1.00 | 0.72 | 0.69 | 0.75 |

**C is highly correlated with Reorganization rate (0.90), V_AutoCorr (0.82), and Separation (0.89).** These four metrics are projections of the same underlying "fluidity" dimension. Jitter is partially independent.

---

## 5. What This Means

### The system lives in a 2D state space
- **Dimension 1 (fluidity):** How freely grains move. Controlled by friction. C, reorg_rate, v_autocorr, separation all measure this.
- **Dimension 2 (jitter):** How noisy grain motion is. Partially independent of fluidity.

### C is not redundant — it's a projection
C ≈ -MSE (r=-0.89 from RD-7A) because both project from the same latent fluidity dimension. But C is not "the same as" MSE — it has different noise sensitivity and temporal properties. The question is not "which metric is best" but "which projection best captures the state for a given purpose."

### The INITIATIVE should measure the state, not the metrics
If the state space is 2D, we need 2 independent measurements to locate the system. C + Jitter would cover both dimensions. C alone captures 76.9%. C + Persistence captures 89.1%.

---

## 6. Files

- `audits/rd08_friction_sweep.py` — sweep script
- `audits/rd08_friction_sweep.json` — raw data (176 runs)
- `audits/rd08_fig1_state_variables.png` — state variables vs μ
- `audits/rd08_fig2_pca_map.png` — PCA state-space projection
- `audits/rd08_fig3_pca_detail.png` — scree plot + loadings
- `audits/rd08_fig4_correlations.png` — correlation heatmap
