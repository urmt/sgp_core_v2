# SFH-SGP Upgrade Pipeline v3 — Final Assessment

## Checklist Status

- [✓] canonical_metrics
- [✓] transform_geometry_separation
- [✓] manifold_estimators
- [✓] expanded_transforms
- [✓] null_audit
- [✓] asymptotic_scaling
- [✓] proof_language_removed
- [✓] old_vs_new_comparison

## Canonical Metric Validation
- Formula version: v1.0
- Total measurements: 96
- Total failures: 0

| Metric | Observed Min | Observed Max | Expected Range | Failures |
|--------|-------------|-------------|---------------|----------|
| m1_signed_ordinal_flow | -0.3608 | 0.9608 | [-1.0, 1.0] | 0 |
| m2_half_corr | -0.9995 | 1.0000 | [-1.0, 1.0] | 0 |
| m3_signed_compressibility | -0.5616 | 0.9569 | [-1.0, 1.0] | 0 |
| m4_amp_transition_asymmetry | 0.2394 | 0.9300 | [0.0, 1.0] | 0 |

## Intrinsic Dimension Estimates (Robust)

| dataset | levina_bickel_mle | participation_ratio | correlation_dim | tangent_pca_dim | singularity |
|---|---|---|---|---| --- |
| white_noise | 3.5326591909353917 | 2.8676570293552857 | 1.9143451526229889 | 2.72 | none |
| sine_wave | -1.4426950408889636 | 0.0 | 0.6242698454957144 | 1.0 | duplicate_state_collapse, degenerate_dimension |
| random_walk | 3.1039577501990743 | 1.0544856269866882 | 1.9970451958901465 | 2.695 | none |

## Null Audit

| Dataset | Temporal Scramble | Phase Randomize | Transform PC1 (orig) | Transform PC1 (shuffled metrics) |
|---------|------------------|----------------|---------------------|--------------------------------|
| white_noise | 0.9940 | 0.9898 | 0.9303 | 0.3225 |
| sine_wave | -0.4123 | 1.0000 | 0.6138 | 0.3609 |
| random_walk | 0.5162 | 0.9991 | 0.6436 | 0.3484 |

### Interpretation
- **white_noise**: DISTRIBUTIONAL (temporal=0.99, phase=0.99, PC1_ratio=2.88)
- **sine_wave**: DISTRIBUTIONAL (temporal=-0.41, phase=1.00, PC1_ratio=1.70)
- **random_walk**: DISTRIBUTIONAL (temporal=0.52, phase=1.00, PC1_ratio=1.85)

## Old vs New Comparison

| Dataset | Old PC1 | New PC1 | Old Eff Rank | New Eff Rank | Old MLE Dim | New MLE Dim |
|---------|---------|---------|-------------|-------------|------------|------------|
| white_noise | 0.4612 | 0.4062 | 2.8421 | 2.9089 | 3.9073 | 3.4666 |
| sine_wave | 0.9963 | 0.8965 | 1.0249 | 1.3948 | -1.4427 | -1.4427 |
| random_walk | 0.9954 | 0.9764 | 1.0300 | 1.1341 | 1.9563 | 2.7338 |

## Language Sanitization
Banned terms enumerated in `language_lock.txt`.
