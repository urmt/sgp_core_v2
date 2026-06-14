# RD-021: Velocity-Field Intervention Report

**Date:** 2026-06-06
**Director:** Dr. Westhaven
**Status:** Outcome **V-D** — Velocity-field organization hypothesis FALSIFIED

---

## 1. Motivation

After RD-019 (density) and RD-020 (selective removal), the leading mechanistic
candidate for Residual(C) was that it captures some *dynamical* state — the
kinematic organization of the velocity field, rather than the structural
organization of the contact network. RD-021 tests this directly.

**Hypothesis:** C reflects the kinematic structure of the velocity field
(alignment, neighbor-similarity, entropy, correlation length).

---

## 2. Design

### Conditions (6 × 10 reps = 60 runs at μ=0.40, fixed)

| Cond | Initial velocity field | Expected effect on velocity diagnostics |
|------|------------------------|------------------------------------------|
| V0 | Thermal control (existing) | Baseline |
| V1 | Rightward drift | +alignment, +nbrsim |
| V2 | Rotational CCW | +nbrsim (orthogonal structure) |
| V3 | Linear shear (top vs bottom) | +nbrsim, +corrlen |
| V4 | Random orientations (uniform angle) | -nbrsim (no coherence) |
| V5 | Random per-grain velocity scramble | -nbrsim, -alignment, +entropy |

### Code change

- ~20 lines added to `_granular_run` for the 6 initial-velocity schemes
- Friction, contact logic, integration untouched
- 5 new velocity diagnostics computed at *two* windows: t=0 (initial) and t=100–450 (pre-perturbation)

### Diagnostics (initial + pre-perturbation)

- `vel_align`: ⟨u_i·u_j⟩ over all grain pairs
- `vel_corrlen`: exponential decay scale of velocity-direction correlation
- `vel_nbrsim`: mean ⟨u_i·u_j⟩ over contact neighbors only
- `vel_entropy`: Shannon entropy of velocity-angle histogram
- `vel_ke`: mean kinetic energy per grain

---

## 3. Manipulation validation

### Velocity diagnostics: **YES, the manipulation worked**

**Initial window (t=0):**

| Diagnostic | F | p | Significance |
|------------|---|---|--------------|
| alignment | 186.4 | <0.0001 | *** |
| nbrsim | 50.8 | <0.0001 | *** |
| entropy | 86.8 | <0.0001 | *** |
| KE | 3.3 | 0.011 | * |

**Pre-perturbation window (t=100–450):**

| Diagnostic | F | p | Significance |
|------------|---|---|--------------|
| alignment | 2.9 | 0.023 | * |
| nbrsim | 6.9 | <0.0001 | *** |
| entropy | 2.7 | 0.029 | * |
| KE | 0.9 | 0.510 | n.s. |

The large F-values at t=0 confirm the initial velocity field is sharply
manipulated. By t=100–450 (just before perturbation), friction has partially
washed out the difference — alignment drops from 0.64 → 0.14, but a residual
diagnostic difference remains (especially nbrsim, F=6.9).

### Structural descriptors: **NO change (as expected)**

| Descriptor | F | p | Significance |
|------------|---|---|--------------|
| NNdist | 2.2 | 0.067 | n.s. |
| contacts | 0.57 | 0.72 | n.s. |
| coord | 0.57 | 0.72 | n.s. |
| comps | 0.82 | 0.54 | n.s. |
| cluster | 0.64 | 0.67 | n.s. |

The structural skeleton is preserved across all 6 conditions.

### C and recovery: **NO change**

| Target | F | p | Significance |
|--------|---|---|--------------|
| pre_C | 1.15 | 0.344 | n.s. |
| dip | 1.19 | 0.325 | n.s. |
| restoration | 1.44 | 0.225 | n.s. |
| τ_rec | 1.94 | 0.103 | n.s. |

Neither C nor any recovery metric differentiates across velocity conditions.

---

## 4. Per-condition summary

| Cond | C_pre | dip | restoration | τ_rec | align_init | nbrsim_init | nbrsim_pre |
|------|-------|-----|-------------|-------|------------|-------------|------------|
| V0 | 0.437 | 0.072 | 1.165 | 19.0 | 0.071 | -0.225 | -0.200 |
| V1 | 0.435 | 0.105 | 1.092 | 39.0 | 0.639 | +0.313 | -0.129 |
| V2 | 0.456 | 0.101 | 1.080 | 81.5 | 0.089 | +0.079 | -0.114 |
| V3 | 0.453 | 0.078 | 1.143 | 49.5 | 0.056 | +0.182 | -0.093 |
| V4 | 0.443 | 0.116 | 1.155 | 81.5 | 0.089 | -0.183 | -0.172 |
| V5 | 0.437 | 0.073 | 1.196 | 37.0 | 0.122 | -0.195 | -0.151 |

Note: τ_rec shows wider variance due to the heavy-tailed 37-step resolution
(most runs recover in the first window).

---

## 5. Spearman correlations

**Window: initial**

| Diagnostic | vs C (r, p) | vs Rest (r, p) |
|------------|-------------|----------------|
| align_init | -0.17, 0.19 | -0.14, 0.30 |
| nbrsim_init | +0.12, 0.35 | **-0.35, 0.006** |
| entropy_init | +0.17, 0.19 | +0.12, 0.38 |
| ke_init | -0.14, 0.28 | +0.11, 0.42 |

**Window: pre-perturbation**

| Diagnostic | vs C (r, p) | vs Rest (r, p) |
|------------|-------------|----------------|
| align_pre | **+0.28, 0.032** | -0.14, 0.27 |
| nbrsim_pre | +0.16, 0.23 | -0.12, 0.35 |
| entropy_pre | -0.18, 0.17 | -0.05, 0.69 |
| ke_pre | -0.13, 0.31 | +0.05, 0.70 |

**Two correlations reach significance**, but neither follows the predicted
direction:
- Higher neighbor-similarity initially → *worse* restoration (r=-0.35, p=0.006)
- Higher pre-perturbation alignment → *higher* C (r=+0.28, p=0.032)

The first is *anti-alignment* with the velocity hypothesis. The second is
*weak* and goes the predicted direction but is the only positive signal
across 16 tests, easily within multiple-comparison noise.

---

## 6. Washout at μ=0.40

A critical finding: **at the experimental friction, initial velocity structure
is largely lost before the perturbation arrives.**

V1 (rightward drift):
- align at t=0: 0.64
- align at t=100–450: 0.14 (closer to V0=0.09)

V3 (shear):
- nbrsim at t=0: +0.18
- nbrsim at t=100–450: -0.09 (sign-flipped, now anti-aligned)

The manipulation physically happens. It is just not preserved long enough at
this friction regime to influence the *pre-perturbation* state. C measures the
pre-perturbation state, so the intervention reaches C "diluted".

---

## 7. Decision rule: V-D

**All three criteria for V-D are met:**

| Criterion | Required | Observed | Met? |
|-----------|----------|----------|------|
| Velocity diagnostics changed | YES | F=3–186 across diagnostics | YES |
| C changed | YES | F=1.15, p=0.34 | NO |
| Recovery changed | YES | all p>0.10 | NO |

**Outcome V-D: Velocity-field organization hypothesis FALSIFIED.**

C is **not** a measurement of velocity-field organization, in either the
initial or pre-perturbation window. C also does not causally affect recovery
*through* velocity — ResC remains the only consistent predictor (ΔR² +0.16 to
+0.43 across recovery targets, see RD021_CAUSAL_MODELS.md).

---

## 8. Cross-experiment summary

| Intervention | Manipulation worked? | C changed? | Recovery changed? | Outcome |
|--------------|----------------------|------------|--------------------|---------|
| RD-019 (density) | YES (R²≥0.91) | NO (p=0.43) | partial (rest p=0.006) | sparseness falsified |
| RD-020 (selective removal) | YES | NO (p=0.09) | YES (τ_rec p=0.014) | structural importance weak-form rejected |
| RD-021 (velocity) | YES | NO (p=0.34) | NO (all p>0.10) | velocity field FALSIFIED |

After 3 intervention experiments, the leading mechanistic candidates are
exhausted. C persists as a real, predictive signal, but its physical identity
remains unidentified.

---

## 9. Reproducibility

- Code: `audits/rd021_velocity_intervention.py`
- Analysis: `audits/rd021_causal_models.py`
- Data: `coherence-benchmark/results/rd021_velocity_ensemble.json`
- Total runtime: ~150s (60 runs × 2.5s/run)
- μ=0.40 fixed; physics untouched; only initial-velocity initialization
  modified
