# C1_09 — Consolidated Synthesis
## SFH-SGP: Organizational Geometry Classification
### Phases v3/v4/v5/U/V → C1

---

## 0. Executive Summary

**What was tried**: Determine whether generative mechanisms (chaos, computation, noise, order, interaction) produce distinguishable organizational geometries in the SFH-SGP transform-metric space.

**What was found**: Yes — three classes emerge from 14 cross-domain systems, distinguished by the differential contribution of the m2 (half-correlation) metric to the transform-space geometry. The classes cross-cut semantic categories (ARI vs labels = 0.27) and survive limited adversarial testing.

**What survived**: 12 specific claims with varying confidence (2 high, 6 moderate, 4 low). The core finding — three geometry classes with m2_contribution as the primary discriminator — survives all tests.

**What was rejected**: Universal geometry (false — PC1 varies 0.51–0.95). Single-metric certainty (false — PC1=1.0 for 1 metric is trivial). Temporal ordering as fundamental (false — phase-scrambled Lorenz retains Class 2). Class 2 fabrication from noise+recurrence (false — all α produce Class 3).

**What was NOT established**: Universality, phase diagram, thermodynamic order parameter, emergence, causal mechanism linking m2_contrib to interaction degree.

---

## 1. Pipeline

### 1.1 Metrics (Frozen V2_079, v1.0)

Four deterministic metrics computed on 512-point time series:

| Metric | What it measures | Range |
|--------|-----------------|-------|
| m1 — Signed Ordinal Flow | Direction persistence in consecutive changes | [-1, +1] |
| m2 — Half Correlation | Pearson correlation between first/second halves | [-1, +1] |
| m3 — Signed Compressibility | Run-length compression via sign pattern | [-1, +1] |
| m4 — Amp Transition Asymmetry | 3-state Markov transition diagonal dominance | [0, +1] |

Each metric is O(L), deterministic, with documented failure modes.

### 1.2 Transform-Space Geometry

For each system: generate 50 signals → apply 8 transforms (identity, reverse, replay, swap_halves, scale, clip, dropout, noise) → compute 4D metric displacement vector per transform → PCA on (400 × 4) matrix → record PC1 (fraction of variance on first component).

**Ablation**: repeat with m2 removed → compute m2_contribution = full_PC1 − no_m2_PC1.

### 1.3 14 Systems

Arithmetic: primes, fibonacci, modular_arithmetic, additive_recurrence
Dynamical: lorenz, logistic_map, henon_map, ising_magnetization, reaction_diffusion
Symbolic: cfg_expansion, lambda_reduction, rewrite_system
Random: iid_gaussian, colored_noise

### 1.4 Feature Matrix (17 features per system)

PC1, PC2, effective_rank, tau_m1..tau_m4, temporal_corr, phase_corr, pc1_ratio, replay_displacement, abl_full_pc1, abl_no_m1..no_m4_pc1, m2_contribution

### 1.5 Clustering

Hierarchical Ward linkage, Euclidean distance, on z-scored 17-feature matrix. Silhouette = 0.35.

---

## 2. Three-Class Structure

| Class | Systems | m2_contrib | PC1 | Temporal | Description |
|-------|---------|-----------|-----|----------|-------------|
| 1 | primes, fib, modular, cfg, lambda, rewrite | ≈ 0 (±0.02) | > 0.86 | Strong temporal (|phase_corr| > 0.84) | Ordered/structural sequences. Deterministic, noise-free. |
| 2 | lorenz, ising, RD | NEGATIVE (< -0.1) | < 0.75 | Mixed: Lorenz -0.27, RD -0.03, Ising 0.90 | Propagating interacting nonlinear. Tightest class. |
| 3 | additive_rec, logistic, henon, iid, colored | POSITIVE (> 0.05) | > 0.81 | High (> 0.9) | m2-driven / spectrally dominated. Most heterogeneous. |

Classes are NOT aligned with semantic categories (ARI = 0.27). Class 1 combines arithmetic and symbolic. Class 2 is purely dynamical. Class 3 mixes arithmetic, dynamical, and random controls.

Class 2 is the most coherent (tight within-class distances, unique negative m2_contrib). Class 3 is the most heterogeneous (includes both pure noise and deterministic chaos).

---

## 3. Order Parameter: (m2_contribution, PC1)

### 3.1 m2_contribution is Necessary

Removing ablation features collapses class agreement to 0.07 (near random). m2_contribution alone recovers only 0.07 ARI, but it is the single feature that, when removed, causes the most agreement collapse.

### 3.2 (m2, PC1) is Minimal Sufficient Pair

Order parameter reduction shows:

| Condition | ARI vs Full |
|-----------|-------------|
| m2_contribution alone | 0.07 |
| m2 + PC1 | **0.64** |
| m2 + tau_m2 | 0.36 |
| Non-m2 features | 0.07 |

The pair (m2_contribution, PC1) achieves 64% class recovery — the highest of any 2-feature combination. No single feature or other pair beats it.

### 3.3 Phase Space Structure

```
m2_contrib  NEGATIVE     ZERO         POSITIVE
           ┌──────────┬────────────┬──────────┐
PC1 HIGH   │  empty   │  Class 1   │  Class 3 │
(>0.85)    │          │  (6 sys)   │  (5 sys) │
           ├──────────┼────────────┼──────────┤
PC1 LOW    │ Class 2  │   empty    │  empty   │
(<0.80)    │ (3 sys)  │            │          │
           └──────────┴────────────┴──────────┘
```

Transition band: |m2_contrib| < 0.05 — logistic map crosses this at r ≈ 3.62 and r ≈ 3.83. Empty quadrant: (negative m2_contrib, high PC1) has no observed systems.

---

## 4. Adversarial Validation

### 4.1 Temporal ordering is NOT fundamental (HIGH confidence)
Phase-scrambled Lorenz (FFT → randomize phases → IFFT, destroying chronology) retains m2_contrib = -0.22 (Class 2). The signal is interactional/spectral, not temporal.

### 4.2 Class 2 cannot be fabricated from noise (MODERATE confidence)
Noise + logistic recurrence at α ∈ [0, 0.99] produces m2_contrib 0.08–0.36 (all Class 3). No α produces negative m2_contrib.

### 4.3 Matched-covariance adversarial passes (MODERATE confidence)
Synthetic data matched to real covariance produces silhouette 0.28 vs real 0.35 (ratio 1.26×). Classes are not purely a covariance artifact.

### 4.4 New domain classification (LOW confidence)
6 new systems (CA rules, random matrix, LFSR, DFA) classified via m2_contrib thresholds: ca_rule184 → Class 2 (m2_contrib = -0.33). Consistent with expectations.

---

## 5. Key Corrections Made

| Original Claim | Status | Replacement |
|----------------|--------|-------------|
| "One universal geometry" | REJECTED (Phase U) | Three-class structure |
| "Universality of organization" | REJECTED (Phase V) | Partial domain generality, low confidence |
| "Phase diagram" | REJECTED (Phase V) | Empirical phase space with transition bands |
| "Order parameter" | QUALIFIED (Phase V) | (m2_contrib, PC1) is minimal pair, not a thermodynamic order parameter |
| "m2 alone discriminates" | REJECTED (Phase V) | m2 + PC1 together achieve 0.64 |
| "PC1 = 1.0 is structure" | REJECTED (Phase U) | Single-metric PC1 = 1.0 is trivial identity |
| "Class 3 = recurrent" | QUALIFIED (C1) | Class 3 is heterogeneous; "m2-driven" is more accurate but still limited |

---

## 6. Failure Modes Summary

6 CRITICAL/HIGH severity failure modes constrain all claims:

| Failure | What it means |
|---------|---------------|
| F-IN-05: No universality | Any claim about "universal geometry classes" is unsupported — only 14+6 systems tested |
| F-CL-08: Small N (14) | New systems may challenge boundaries at any time |
| F-CL-03: Feature-dependent | Class structure collapses with removal of ablation or spectral features |
| F-OP-01: m2 necessary not sufficient | m2 alone discriminates nothing; only paired with PC1 |
| F-TS-03: Distributional artifact | Class 3 PC1 is partially distributional, partially real |
| F-OP-02: (m2, PC1) incomplete | Only 64% recovery; 36% of class structure is in other features |

---

## 7. What Survives (Confidence-Weighted)

| # | Claim | Confidence |
|---|-------|------------|
| 1 | Geometry is non-uniform across generative mechanisms | HIGH |
| 7 | Temporal ordering not fundamental to Class 2 | HIGH |
| 2 | Three classes exist | MODERATE |
| 3 | m2_contribution is the primary discriminative axis | MODERATE |
| 4 | (m2, PC1) is minimal sufficient ordered pair | MODERATE |
| 6 | Class 2 cannot be fabricated from noise+recurrence | MODERATE |
| 8 | Class 1 = ordered/structural sequences | MODERATE |
| 10 | m2_contribution tracks structural reorganization | MODERATE |
| 12 | Class 2 is the most coherent class | MODERATE |
| 5 | Class 2 = propagating interacting structure | LOW |
| 9 | Class 3 = m2-driven/spectrally dominated | LOW |
| 11 | Partial domain generality | LOW |

---

## 8. Open Questions (Not Addressed)

1. **Why does m2 behave differently across classes?** — m2_contribution is correlational. The mechanism by which interacting nonlinear systems produce negative m2_contrib is unknown.

2. **Are there more than 3 classes?** — 4+ cluster cuts are possible. The choice of 3 is based on dendrogram elbow + interpretability.

3. **Do larger systems (N ≫ 14) maintain the same structure?** — Only 14 systems tested. Generalization is unproven.

4. **Is the structure continuous or discrete?** — Silhouette 0.35 and transition bands suggest continuous variation with cluster-like density concentrations.

5. **What is the null distribution for "number of classes"?** — The Gap statistic or other null-vs-k estimate was not computed.

6. **What about non-numeric generative mechanisms?** — Only time-series-cast systems tested. No graphs, images, or other data modalities.

---

## 9. Deliverables

| Document | Location |
|----------|----------|
| Metric spec (frozen) | `canonical_metric_spec.md` |
| Full reproducibility manifest | `reproducibility_manifest.md` |
| Minimal phase space model | `minimal_phase_space_summary.md` |
| Clean-room reimplementation spec | `clean_room_reimplementation_spec.md` |
| Failure modes catalog | `failure_modes_catalog.md` |
| Surviving claims registry | `surviving_claims_registry.md` |
| NotebookLM brief | `../sfh_sgp_notebooklm_brief.md` |

All in `phaseC1_reproducibility_core/` except the NotebookLM brief.
