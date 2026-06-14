# C1_02 — Reproducibility Manifest
## SFH-SGP v3/v4/v5/PhaseU/PhaseV Reproducibility Bundle

---

## 1. Dependency Manifest

### Python Version
```
Python >= 3.9 (tested on 3.11)
```

### Core Dependencies (all via pip)
```
numpy >= 1.24
pandas >= 1.5
scikit-learn >= 1.2
```

No GPU, no special hardware, no external API calls.

---

## 2. Execution Order (Required)

All scripts run from repository root `/home/student/sgp_core_v2/`.

| Step | Script | Purpose | Time |
|------|--------|---------|------|
| 1 | `sfh_sgp_repair_pipeline.py` | v1 repair scaffold (legacy) | <1 min |
| 2 | `sfh_sgp_upgrade_pipeline_v2.py` | v2 simplified metrics (superseded) | <1 min |
| 3 | `sfh_sgp_upgrade_pipeline_v3.py` | **Canonical metrics** — produces 13 output files | ~2 min |
| 4 | `sfh_sgp_ood_universality_audit.py` | OOD v4 — 14 systems, τ-alignment, nulls | ~5 min |
| 5 | `sfh_sgp_metric_ablation_diagnostic.py` | v5 — 9 systems × 9 ablation conditions | ~3 min |
| 6 | `sfh_sgp_phaseU_classification.py` | Phase U — clustering + 7 stability/transfer/adversarial tests | ~2 min |
| 7 | `sfh_sgp_phaseV_audit.py` | Phase V — 7 order parameter tests | ~5 min |

Order matters: v3 must run first (establishes canonical metrics). Phase U and V consume v4/v5 outputs.

---

## 3. Random Seeds

All scripts use the following fixed seed:

```
SEED = 42
np.random.seed(SEED)
random.seed(SEED)
```

This applies to:
- All system generators (noise, Lorenz, Ising, RD, etc.)
- All stochastic transforms (dropout, add_noise)
- All null controls (temporal scramble, phase randomization, shuffled metrics)
- All bootstrap/perturbation procedures

Scripts verified: v3 pipeline (line 35-37), v4 OOD audit (line 41-43), v5 ablation (uses canonicals), Phase U, Phase V.

---

## 4. Output File Manifest

### Step 3 Outputs: `sfh_sgp_upgrade_v3_outputs/` (13 files)
```
canonical_metric_validation.csv
canonical_metric_summary.json
transform_space_geometry.csv
signal_manifold_geometry.csv
replay_structure.csv
asymptotic_scaling.csv
null_audit.csv
old_vs_new_comparison.csv
language_lock.txt
upgrade_checklist.json
validation_report.json
final_assessment.md
```

### Step 4 Outputs: `sfh_sgp_ood_outputs/` (6 files from v4)
```
cross_domain_reproducibility.csv
tau_alignment_matrix.csv
replay_stability_ood.csv
null_audit_ood.csv
universality_assessment.md
```

### Step 5 Outputs: `sfh_sgp_ood_outputs/` (2 files from v5)
```
metric_ablation_results.csv
metric_ablation_summary.md
```

### Step 6 Outputs: `sfh_sgp_ood_outputs/` (11 files from Phase U)
```
clustering_results.csv
clustering_feature_matrix.csv
class_stability_report.csv
classifier_transfer_report.csv
class_semantics.csv
minimal_basis_report.csv
adversarial_artifact_report.json
transition_distances.csv
dendrogram.txt
phaseU_summary.md
```

### Step 7 Outputs: `sfh_sgp_ood_outputs/` (8 files from Phase V)
```
phaseV_perturbation.csv
phaseV_metric_swaps.csv
phaseV_new_domains.csv
phaseV_order_reduction.csv
phaseV_adversarial.csv
phaseV_scale_stability.csv
phaseV_transition_scan.csv
phaseV_summary.md
```

### Consolidated (from assessment scripts)
```
final_universality_assessment.md
```

---

## 5. Dataset Provenance

All datasets are synthetic, generated at runtime by the pipeline scripts:

| System | Generator Function | Source File | Base Length |
|--------|--------------------|-------------|-------------|
| primes | `primes(n=512)` | OOD audit §A | 512 |
| fibonacci | `fibonacci(n=512)` | OOD audit §A | 512 |
| modular_arithmetic | `modular_arithmetic(n=512, K=17)` | OOD audit §A | 512 |
| additive_recurrence | `additive_recurrence(n=512, a=1.5, c=0.3)` | OOD audit §A | 512 |
| lorenz | `lorenz(n=512, σ=10, ρ=28, β=8/3, dt=0.02)` | OOD audit §B | 512 |
| logistic_map | `logistic_map(n=512, r=3.9, x0=0.5)` | OOD audit §B | 512 |
| henon_map | `henon_map(n=512, a=1.4, b=0.3)` | OOD audit §B | 512 |
| ising_magnetization | `ising(n=512, L=6, steps=5, T=2.5)` | OOD audit §B | 512 |
| reaction_diffusion | `reaction_diff(n=512, 16x16, F=0.035)` | OOD audit §B | 512 |
| cfg_expansion | `cfg_expansion(n=512)` | OOD audit §C | 512 |
| lambda_reduction | `lambda_reduction(n=512)` | OOD audit §C | 512 |
| rewrite_system | `rewrite_system(n=512)` | OOD audit §C | 512 |
| iid_gaussian | `iid_gaussian(n=512)` | OOD audit §D | 512 |
| colored_noise | `colored_noise(n=512, α=1.0)` | OOD audit §D | 512 |

No external data files. 100% synthetic.

---

## 6. Parameter Tables (Phase U Clustering)

### Clustering Configuration
- Algorithm: hierarchical (Ward linkage) + k-means (for comparison)
- Distance: Euclidean
- Number of clusters: determined by dendrogram + silhouette
- Feature set: 17 features (PCA components, τ-axes, null audit, replay, ablation)
  - pc1, pc2, effective_rank, tau_m1..tau_m4, temporal_corr, phase_corr,
    pc1_ratio, replay_displacement, abl_full_pc1, abl_no_m1..no_m4_pc1

### Stability Tests
- remove_spectral: remove phase_corr + temporal_corr
- remove_tau_axis: remove tau_m1..tau_m4
- remove_null_audit: remove temporal_corr, phase_corr, pc1_ratio
- remove_replay: remove replay_displacement
- remove_ablation: remove abl_* features
- gaussian_noise_0.3: add N(0, 0.3) noise to features, 50 replicates

### Cross-Metric Transfer
- view1: tau_axis features only
- view2: ablation features only
- 5-fold CV, classifier = RandomForest

### Minimal Basis Search
- Exhaustive search over 1, 2, 3 feature combinations of 17 features
- Agreement = Rand index with full 17-feature clustering

---

## 7. Parameter Tables (Phase V Tests)

### Perturbation Sensitivity
- System: logistic_map
- Scan range: r = [3.5, 4.0], step ≈ 0.02 (via numpy arange)
- Metric: m2_contribution = full_PC1 - no_m2_PC1
- Derivative: central difference, |d(contrib)/dr|

### Causal Metric Swaps
- Reference systems: logistic_r4.0, logistic_r3.5, iid_gaussian
- Test: m2_preserved_others_swapped — preserves m2 metrics while swapping m1,m3,m4 across systems
- Full PC1, no_m2 PC1, m2_only PC1, m2_contribution, tau_m1..tau_m4

### New Domain Classification
- Systems: ca_rule30, ca_rule110, ca_rule184, goe_random_matrix, lfsr_crypto, dfa_trace
- Features: full_pc1, no_m2_pc1, m2_contribution, temporal_corr
- Predicted class: based on Phase U cluster boundaries (m2_contrib + pc1 thresholds)

### Order Parameter Reduction
- m2_only: cluster on (abl_no_m2_pc1) alone
- m2_plus_pc1: cluster on (abl_no_m2_pc1, pc1)
- m2_plus_tau: cluster on (abl_no_m2_pc1, tau_m2)
- non_m2: cluster on (all features EXCEPT m2-related)
- Agreement measured as Rand index vs full 17-feature clustering

### Critical Transition Scan
- System: logistic_map
- r range: [3.5, 4.0], step = 0.0001 (10,000 points)
- Metric: m2_contribution (full PC1 - no_m2 PC1)
- Max derivative: max |d(contrib)/dr| using central difference

### Adversarial Engineering
- noise+recurrence: x_t = (1-α)·noise_t + α·logistic(x_{t-1}, r=3.9)
- α ∈ [0, 0.1, 0.3, 0.5, 0.7, 0.9, 0.99]
- lorenz_phase_scrambled: FFT → randomize phases → IFFT
- Metric: can any engineered system produce m2_contrib < -0.1 (Class 2-like)?

### Scale Stability
- Systems: logistic_r4.0, logistic_r3.5, iid_gaussian
- Scales: n ∈ [64, 128, 256, 512, 1024], coarse_grain ∈ [2,4,8], subsample ∈ [2,4,8]
- Metric: m2_mean, m2_cv across windows

---

## 8. Known Seed Sensitivity

The following components are deterministic given SEED=42:
- All system generators (primes, Lorenz, etc.)
- Noise-based transforms (dropout, add_noise)
- Null controls (temporal scramble, phase randomize)
- Clustering (deterministic: hierarchical Ward linkage)
- Ablation PC1 values (deterministic given data)

The following may vary with sklearn/numpy version:
- PCA sign flips (eigenvector sign is arbitrary) — only affects τ-axis sign, not alignment
- NearestNeighbors distance ties (very rare)

Expected variation between runs: < 0.01 in PC1 values, < 0.05 in τ-alignment.

---

## 9. Checksum Targets

Not computed — all data is synthetic and regenerable. Expected output files with characteristic values:

| File | Key Value | Expected |
|------|-----------|----------|
| `cross_domain_reproducibility.csv` | iid_gaussian pc1_variance | 0.93 ± 0.02 |
| `tau_alignment_matrix.csv` | mean alignment | 0.70 ± 0.05 |
| `metric_ablation_results.csv` | iid_gaussian no_m2 PC1 | 0.68 ± 0.02 |
| `clustering_results.csv` | silhouette | 0.35 ± 0.03 |
| `phaseV_transition_scan.csv` | max |d(contrib)/dr| | 55 ± 5 |
