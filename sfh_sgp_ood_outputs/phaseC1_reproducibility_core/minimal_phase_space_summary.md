# C1_03 — Minimal Phase Space Model
## Order Parameter: (m2_contribution, PC1_transform_geometry)

---

## 1. Surviving Coordinate System

The empirical class structure is captured by a **2-dimensional coordinate system**:

```
Order Parameter 1:  m2_contrib = full_PC1 - no_m2_PC1
                    (differential m2 dimensionality contribution)

Order Parameter 2:  PC1 = fraction of transform variance on first PC
                    (overall compactness of transform geometry)
```

These are NOT derived from theory. They are the surviving minimal pair from exhaustive search over 17 features — the pair that maximizes class recovery (agreement = 0.64 vs 0.07 for either alone).

---

## 2. Class Boundaries (Empirical)

### 14-System Data with Measured m2_contrib

| System | Cluster | PC1 | m2_contrib | Source |
|--------|---------|-----|-----------|--------|
| primes | 1 | 0.937 | 0.012 | measured |
| cfg_expansion | 1 | 0.932 | 0.006 | measured |
| lambda_reduction | 1 | 0.935 | — | not ablated |
| rewrite_system | 1 | 0.861 | — | not ablated |
| fibonacci | 1 | 0.862 | — | not ablated |
| modular_arithmetic | 1 | 0.900 | — | not ablated |
| **lorenz** | **2** | **0.507** | **-0.378** | **measured** |
| **ising_magnetization** | **2** | **0.722** | **-0.319** | **measured** |
| **reaction_diffusion** | **2** | **0.629** | — | not ablated |
| additive_recurrence | 3 | 0.856 | — | not ablated |
| logistic_map | 3 | 0.883 | 0.187 | measured |
| henon_map | 3 | 0.954 | 0.192 | measured |
| iid_gaussian | 3 | 0.929 | 0.252 | measured |
| colored_noise | 3 | 0.812 | — | not ablated |

### Inferred Class 2 m2_contrib for reaction_diffusion

RD shares with Lorenz and Ising: low PC1 (<0.75), non-noise temporal_corr (0.37), lower τ-m2 loading (0.03 vs ~0.99 for Class 3). Its m2_contrib is inferred to be negative (estimated -0.15 to -0.30).

### Inferred Class 3 m2_contrib for additive_recurrence and colored_noise

AR has temporal_corr=0.906, phase_corr=0.992, τ-m2=0.996 — matches logistic/henon signature. Inferred m2_contrib positive (>0.05).
CN has temporal_corr=0.991, phase_corr=0.998, τ-m2=0.999 — matches iid_gaussian signature. Inferred m2_contrib positive (~0.2).

---

## 3. Empirical Phase Boundaries

Based on measured systems:

```
Class 1 (ordered/structural):
  -0.02 < m2_contrib < +0.02
  PC1 > 0.85
  temporal_corr close to ±1 (ordered sequences)

Class 2 (interacting nonlinear):
  m2_contrib < -0.1        (NEGATIVE — m2 adds dimensionality)
  PC1 < 0.8
  temporal_corr is system-specific (not purely spectral)

Class 3 (recurrent/m2-driven):
  m2_contrib > +0.05       (POSITIVE — m2 adds 1D structure)
  PC1 > 0.8
  temporal_corr > 0.9 (spectrally dominated)
```

These boundaries are **approximate**. There is a transition band between Class 2 and 3 where m2_contrib crosses zero, and a density gap between Class 1 and 3 in m2_contrib space.

---

## 4. Phase Space Structure

The (m2_contrib, PC1) phase space is NOT uniformly populated:

```
m2_contrib ← negative      zero      positive →
             ┌──────────┬──────────┬──────────┐
PC1 high     │   empty   │  Class 1 │  Class 3 │
(>0.85)      │           │ (primes) │(logistic)│
             │           │ (cfg)    │ (henon)  │
             │           │          │ (noise)  │
             ├──────────┼──────────┼──────────┤
PC1 low      │  Class 2 │   empty  │   empty  │
(<0.8)       │ (lorenz) │          │          │
             │ (ising)  │          │          │
             │ (RD)     │          │          │
             └──────────┴──────────┴──────────┘
```

Key emptiness: the quadrant (negative m2_contrib, high PC1) is unpopulated — no system has m2 adding dimensionality while maintaining compact transform geometry.

---

## 5. Transition Bands (Bifurcation-like Behavior)

The logistic map, scanned across r ∈ [3.5, 4.0], traces a continuous path through this phase space:

```
r=3.5 (period-4):  m2_contrib = -0.248, PC1 = 0.714   →  Class 2-like
r=3.62 (chaotic):  m2_contrib = +0.021, PC1 = 0.911   →  transition band
r=3.68 (chaotic):  m2_contrib = -0.349, PC1 = 0.629   →  Class 2-like
r=3.74 (chaotic):  m2_contrib = -0.119, PC1 = 0.741   →  Class 2-like
r=3.80 (chaotic):  m2_contrib = +0.163, PC1 = 0.760   →  Class 3-like
r=3.86 (chaotic):  m2_contrib = -0.313, PC1 = 0.617   →  Class 2-like
r=3.92 (chaotic):  m2_contrib = +0.087, PC1 = 0.896   →  Class 3-like
r=3.98 (chaotic):  m2_contrib = +0.129, PC1 = 0.886   →  Class 3-like
r=4.00 (chaotic):  m2_contrib = -0.292, PC1 = 0.630   →  Class 2-like
```

The path oscillates across the Class 2/3 boundary. Max |d(contrib)/dr| = 55 at r=4.0 boundary. The derivative peaks track the logistic map's periodic windows and band merging points.

**Transition Band**: defined as |m2_contrib| < 0.05, where a system can shift between negative and positive m2_contrib under small parameter perturbations. For logistic map, this band is crossed at r ≈ 3.62 and r ≈ 3.83.

---

## 6. Separation Metrics

| Metric | Value | Meaning |
|--------|-------|---------|
| Silhouette (all 17 features) | 0.35 | Moderate — classes are not sharply separated |
| Intra/inter distance ratio | 0.95 | Classes are denser within than between, but weakly |
| Inter-class distance (Class 2–3) | 7.5–9.0 | Largest separation |
| Inter-class distance (Class 1–2) | 5.8–8.2 | Moderate |
| Inter-class distance (Class 1–3) | 4.7–5.9 | Weakest separation |
| Within-class distance (Class 1) | 0.06–5.15 | Wide spread (primes→fibonacci) |
| Within-class distance (Class 2) | 5.34–5.87 | Tightest cluster |
| Within-class distance (Class 3) | 0.85–5.17 | Wide spread (noise→logistic) |

Class 2 is the most coherent (tight within-class, distant from others).
Class 3 is the most heterogeneous (includes both noise and logistic/henon).

---

## 7. Minimal Basis Recovery

The 3-feature minimal basis that perfectly recovers full clustering:
```
{pc1, pc1_ratio, abl_no_m2_pc1}
```

This can be interpreted as:
- `pc1`: overall transform compactness
- `pc1_ratio = orig_PC1 / shuffled_PC1`: null survival ratio
- `abl_no_m2_pc1`: transform geometry without m2 (directly related to m2_contrib)

The 3-feature basis maps back to (m2_contrib, PC1) since:
```
m2_contrib = full_PC1 - abl_no_m2_pc1
pc1_ratio = PC1 / shuffled_PC1
```

---

## 8. Stability Under Feature Removal

| Removed Feature Group | Agreement | Interpretation |
|-----------------------|-----------|----------------|
| spectral features | 0.07 | Class structure collapses without spectral/temporal info |
| τ-axis features | 0.29 | τ features contribute but aren't essential alone |
| null audit features | 0.14 | Null survival is critical |
| replay displacement | 0.57 | Replay is moderately important |
| ablation features | 0.07 | Ablation (m2_contrib) is ESSENTIAL |
| gaussian_noise_0.3 | 0.42 | Structure partially survives noise |

The class structure is **fragile**: removing either ablation or spectral features collapses agreement to near-random (0.07).

---

## 9. Formal Summary

The organizational geometry phase space is minimally described by:

```
(x₁, x₂) = (m2_contrib, PC1)

Class 1:  x₁ ≈ 0,   x₂ > 0.85     (6 systems observed)
Class 2:  x₁ < -0.1, x₂ < 0.8     (3 systems observed)
Class 3:  x₁ > 0.05, x₂ > 0.8     (5 systems observed)

Transition band: |x₁| < 0.05  (logistic map crosses this)
Empty region:    x₁ < -0.1, x₂ > 0.85  (no observed systems)
```

This is an empirical model. No theoretical derivation is offered.
