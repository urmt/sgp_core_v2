# C1_07 — Failure Modes Catalog
## Centralized registry of all known failure modes, degeneracies, artifacts, and caveats

---

## 1. Metric-Level Failure Modes

### F-M1-01: ZERO_DIFFERENCE_DOMINATION (m1)
**Description**: If most consecutive differences dx=0 (quantized/discrete signals), the sign product mean approaches 0 regardless of structure.
**Affects**: m1 — Signed Ordinal Flow
**Detection**: Check `count(dx == 0) / len(dx)`; if > 0.5, flag.
**Example**: Constant signal: all dx=0, sign=0, product=0, m1=0.0.
**Severity**: LOW — correctly returns 0 for no-signal, but can obscure structure in discretized signals.

### F-M1-02: OSCILLATORY_UNDERFLOW (m1)
**Description**: Period-2 oscillatory signals produce alternating sign pattern with zeros between oscillations, yielding m1 ≈ -0.33 instead of -1.0.
**Affects**: m1
**Detection**: Check if `m1 ≈ -0.33` combined with period-2 signal.
**Severity**: LOW — misclassifies oscillation structure as moderate.

### F-M2-01: DUPLICATE_STATE_COLLAPSE (m2)
**Description**: If signal contains identical blocks (replay outputs, period dividing L/2), both halves are identical → m2 = 1.0 spuriously.
**Affects**: m2 — Half Correlation
**Detection**: Check `std(x[:h]) == 0 or std(x[h:]) == 0`, or whether halves are elementwise identical.
**Example**: Replay transform produces x = [a, a] → both halves identical → m2 = 1.0.
**Severity**: HIGH — directly inflates correlation for signals that are not genuinely structured.

### F-M2-02: PERIODIC_DEGENERACY (m2)
**Description**: Periodic signals with period p dividing L/2 produce identical halves → m2 = 1.0.
**Affects**: m2
**Detection**: Check autocorrelation at lag L/2.
**Example**: Period-4 sine with L=512 → both halves identical → m2 = 1.0.
**Severity**: MODERATE — periodic structure IS a form of organization, but m2 overstates it.

### F-M2-03: CONSTANT_SEGMENT_ARTIFACT (m2)
**Description**: If either half is constant, correlation defaults to 0.0, even if the other half is structured.
**Affects**: m2
**Detection**: Check `std(x[:h]) == 0 or std(x[h:]) == 0`.
**Severity**: MODERATE — can mask genuine half-half structure.

### F-M2-04: SCALE_SENSITIVITY (m2)
**Description**: m2 varies with signal length, window size, and coarse-graining — not scale-invariant across different L.
**Affects**: m2
**Evidence**: Phase V Table 7: iid_gaussian m2 varies from -0.046 (n=64) to +0.044 (n=128), with CV up to 5.6. Logistic r=4.0 m2=0.0 at all scales.
**Severity**: LOW — does not change class assignments, but m2 values are not directly comparable across different L.

### F-M3-01: ZERO_DIFFERENCE_DOMINATION (m3)
**Description**: If most dx=0, runs count underestimates complexity. m3 approaches 1 - 2/L ≈ 1 for constant signals.
**Affects**: m3 — Signed Compressibility
**Detection**: Check fraction of dx=0.
**Example**: Constant signal: runs=1, m3 ≈ 0.996 (inflated).
**Severity**: LOW — correctly identifies constant signals as compressible.

### F-M3-02: SHORT_SIGNAL_BIAS (m3)
**Description**: For short non-alternating signals, m3 approaches 1-2/L, inflating compressibility.
**Affects**: m3
**Detection**: Check if L < 50.
**Severity**: LOW — mitigated by L=512 in this pipeline.

### F-M4-01: EQUAL_WIDTH_QUANTIZATION_ARTIFACT (m4)
**Description**: If signal is concentrated in one amplitude bin (near-constant), all transitions map to single state → m4 = 0.333 regardless of signal complexity.
**Affects**: m4 — Amplitude Transition Asymmetry
**Detection**: Check if `max(x) - min(x) < threshold`, or check bin occupancy.
**Severity**: MODERATE — constant signal produces m4=0.333, which is the same as mid-range random mixing.

### F-M4-02: FIXED_K_SENSITIVITY (m4)
**Description**: K=3 is coarse. Signals with more than 3 effective amplitude bands may be under-resolved. K is NOT tunable (V2_079 freeze).
**Affects**: m4
**Detection**: Compare with higher-K versions (non-canonical).
**Severity**: MODERATE — some signals may have their transition structure collapsed.

### F-M4-03: ROW_NORMALIZATION_ARTIFACT (m4)
**Description**: Low-population states (few or zero observations) get unreliable or default transition estimates, potentially inflating m4.
**Affects**: m4
**Detection**: Check for any state with < 10 observations.
**Severity**: LOW — mitigated by row normalization default of 1.0 for zero rows.

---

## 2. Transform-Space Failure Modes

### F-TS-01: TRIVIAL_1D_METRIC_IDENTITY
**Description**: Any single metric used alone produces PC1 = 1.0 in transform space. This is a mathematical identity (1D space trivially has 100% variance on first PC), NOT evidence of structure.
**Affects**: ALL analyses using single-metric embedding
**Detection**: `metric_set_size == 1 and PC1 ≈ 1.0`
**Severity**: CRITICAL — was a major early confound. Now explicitly flagged.

### F-TS-02: PCA_SIGN_AMBIGUITY
**Description**: PCA eigenvector signs are arbitrary. The τ-axis (PC1 loading direction) may flip between runs. Only affects sign of tau_m1..tau_m4 loadings, not their magnitudes or alignment scores.
**Affects**: τ-axis alignment, tau_* features
**Detection**: Compare tau_m1 signs across runs — may be inverted.
**Severity**: LOW — absolute cosine similarity in alignment is sign-invariant.

### F-TS-03: DISTRIBUTIONAL_ARTIFACT
**Description**: Systems with strong marginal statistics (Gaussian, colored noise) produce high PC1 that partially reflects distributional shape rather than geometric structure. IID Gaussian PC1=0.93, drops to 0.68 when m2 removed.
**Affects**: ALL systems, especially noise controls
**Detection**: Compare original PC1 vs shuffled-metrics PC1. High PC1_RATIO (> 2) indicates real structure; PC1_RATIO ≈ 1 indicates distributional.
**Severity**: HIGH — Class 3 (noise, logistic, Henon) is partially contaminated by distributional artifact. Partial separation via m2 ablation.

### F-TS-04: DISTRIBUTIONAL_PARTIAL_SEPARABILITY
**Description**: The distributional artifact is not cleanly separable from real structure. Removing m2 reduces noise PC1 from 0.93→0.68, suggesting ~25% of noise's PC1 is m2-related artifact — but m2 also carries real signal for nonlinear systems.
**Affects**: All m2_contribution interpretations
**Detection**: Compare iid_gaussian and logistic_map m2_contributions. Both positive, but for different reasons.
**Severity**: MODERATE — class boundaries are reliable; absolute magnitude of m2_contrib mixes artifact with signal.

### F-TS-05: MODEST_SAMPLE_SIZE
**Description**: n_samples=50 for transform-space PC1 estimation is modest. PC1 estimates have variance across independent runs.
**Affects**: All PC1 measurements
**Detection**: Run with n_samples=200 to compare stability.
**Severity**: LOW — PC1 values are consistent within ±0.02 across runs (verified in reproducibility manifest).

---

## 3. Clustering Failure Modes

### F-CL-01: MODEST_SILHOUETTE
**Description**: Silhouette = 0.35. Classes are not sharply separated. There is overlap between all three classes.
**Affects**: Class boundary confidence
**Detection**: None needed — always true.
**Severity**: MODERATE — class structure is real but weak. Boundaries are bands, not gaps.

### F-CL-02: CATEGORY_LEAKAGE
**Description**: ARI between clustering and category labels is only 0.27. The clustering does NOT align with obvious semantic categories (arithmetic, dynamical, symbolic, random).
**Affects**: Interpretability
**Detection**: Compute ARI vs category labels.
**Severity**: LOW — this is actually evidence the clustering finds cross-category structure.

### F-CL-03: FEATURE_COLLAPSE_SENSITIVITY
**Description**: Removing either ablation or spectral features collapses agreement to 0.07 (near random). The class structure is fragile.
**Affects**: ALL clustering results
**Detection**: Each stability test documented in Phase U.
**Severity**: HIGH — class structure depends on specific feature sets. Not robust to arbitrary feature subsets.

### F-CL-04: REPLAY_DISPLACEMENT_AMBIGUITY
**Description**: Class 1 systems have replay_displacement ≈ 0.02 (replay barely changes metrics). This is because Class 1 signals are often periodic/repetitive, so replay (which duplicates first half) doesn't change them much. Not a signal of "structure" per se.
**Affects**: Class 1 characterization
**Detection**: Compare replay_displacement across classes.
**Severity**: LOW — correct behavior, but interpretation requires care.

### F-CL-05: GST_FEATURE_DUPLICATION
**Description**: abl_full_pc1 and pc1 are identical measurements from different runs. Both appear in the 17-feature set, inflating the effective weight of PC1 information.
**Affects**: Clustering weight distribution
**Detection**: Check correlation between abl_full_pc1 and pc1.
**Severity**: LOW — duplicates the PC1 axis but does not distort.

### F-CL-06: SYNTHETIC_MATCHED_COVARIANCE_ADVERSARIAL
**Description**: Synthetic data with matched covariance produces silhouette 0.28 vs real 0.35 (ratio 1.26×). The adversarial test PASSES but the margin is modest — 26% better than matched-covariance null.
**Affects**: Confidence that clustering is NOT a covariance artifact
**Detection**: Compare real silhouette to matched-covariance synthetic silhouette.
**Severity**: MODERATE — passes the adversarial test, but the ratio is not overwhelming.

### F-CL-07: BASIS_NON_UNIQUENESS
**Description**: Multiple different 3-feature subsets achieve perfect agreement (1.0) with full clustering. No unique minimal basis.
**Affects**: Minimal basis interpretation
**Detection**: Enumerate all 3-feature subsets with agreement=1.0.
**Severity**: LOW — many roads lead to the same clustering.

### F-CL-08: SMALL_N_SYSTEMS
**Description**: Only 14 systems. Three-class discovery on 14 data points with 17 features is high-dimensional relative to sample count.
**Affects**: Generalizability
**Detection**: None needed — p > n situation.
**Severity**: HIGH — new systems may challenge class boundaries.

---

## 4. Order Parameter Failure Modes (Phase V)

### F-OP-01: m2_NECESSARY_BUT_NOT_SUFFICIENT
**Description**: m2_contribution alone achieves only 0.07 agreement with full clustering. It is necessary (structure collapses without it) but not sufficient without PC1 paired.
**Affects**: Any claim that "m2 alone discriminates classes"
**Detection**: ARI of m2_only vs full clustering = 0.07.
**Severity**: HIGH — m2_contribution is the PRIMARY coordinate but only in a PAIR with PC1.

### F-OP-02: m2_plus_pc1_INCOMPLETE_RECOVERY
**Description**: (m2_contribution, PC1) achieves agreement 0.64, not 1.0. The pair does not fully recover the 17-feature clustering.
**Affects**: Order parameter completeness
**Detection**: ARI is 0.64, not 1.0.
**Severity**: MODERATE — the minimal sufficient pair captures ≈ 64% of class structure; remaining 36% is in other features.

### F-OP-03: TRANSITION_BAND_DEGENERACY
**Description**: The logistic map crosses m2_contrib ≈ 0 at r ≈ 3.62 and r ≈ 3.83. Systems in the transition band |m2_contrib| < 0.05 have ambiguous class membership.
**Affects**: Class assignment for boundary systems
**Detection**: Check if |m2_contrib| < 0.05.
**Severity**: MODERATE — boundary defines a transition band, not a sharp phase transition.

### F-OP-04: DERIVATIVE_PEAK_AMBIGUITY
**Description**: The max |d(m2_contrib)/dr| = 55 at r=4.0. But r=4.0 is the signal edge — the actual derivative may be unbounded if we extended r > 4 (logistic diverges).
**Affects**: Interpretation of critical transition
**Detection**: Check if peak is at boundary of scan range.
**Severity**: LOW — the peak is real but may not represent a "critical point" in the usual sense.

### F-OP-05: CAUSAL_SWAP_METRIC_MISMATCH
**Description**: The "m2_preserved_others_swapped" test produced m2_contrib=0.0000. This appears to be a test execution issue (PC1 of 0.0 on a 4D space is not meaningful) rather than a valid result.
**Affects**: Causal swap conclusions
**Detection**: Check if m2_preserved_others_swapped PC1 ≈ 0 → test failure.
**Severity**: HIGH — causal metric swap test invalid; conclusions cannot be drawn from it.

### F-OP-06: TEMPORAL_SCALE_STABILITY_EMPTY
**Description**: Scale stability test produced m2=0.0000, CV=0.0000 for logistic at both r=4.0 and r=3.5. This is because non-overlapping window sampling for periodic signals returns identical m2 values — not evidence of stability per se.
**Affects**: Temporal scale stability claims
**Detection**: Check if m2_cv = 0.0 for clearly different-length signals → degenerate measurement.
**Severity**: MODERATE — the test is valid for noise but degenerate for periodic signals.

---

## 5. Adversarial Failure Modes

### F-AD-01: NOISE_RECURRENCE_CANNOT_FABRICATE_CLASS2
**Description**: Adding logistic recurrence to noise (α ∈ [0, 0.99]) produces m2_contrib 0.08–0.36 (Class 3). Class 2 (negative m2_contrib) cannot be fabricated from noise+recurrence.
**Affects**: Claim that Class 2 is genuine nonlinear interaction structure
**Detection**: Check all α values — none produce m2_contrib < -0.1.
**Severity**: LOW — this is NOT a failure; it supports Class 2 genuineness. Documented as success.

### F-AD-02: PHASE_SCRAMBLED_LORENZ_RETAINS_CLASS2
**Description**: Phase-scrambled Lorenz (destroyed temporal chronology) retains m2_contrib = -0.22 (Class 2). The discriminating signal is spectral/interactional, not temporal.
**Affects**: Interpretation of Class 2 as "temporal structure"
**Detection**: Compare original vs phase-scrambled Lorenz m2_contrib.
**Severity**: LOW — NOT a failure; documents that Class 2 is about spectral structure, not chronology.

### F-AD-03: MATCHED_COVARIANCE_SYNTHETIC_CLUSTERING
**Description**: Synthetic data matched to real covariance produces silhouette 0.28 vs real 0.35. The difference (ratio 1.26×) is real but modest. Some cluster structure may be covariance-driven.
**Affects**: Claims that clustering is "genuine" vs "covariance artifact"
**Detection**: Compare real vs synthetic silhouette.
**Severity**: MODERATE — passes but does not rule out partial covariance contribution.

---

## 6. Interpretation Failure Modes

### F-IN-01: CLASS_NAMES_ARE_METAPHORS
**Description**: "Ordered/structural," "interacting nonlinear," and "recurrent/m2-driven" are descriptive labels, not theoretical categories. They summarize what the systems HAVE IN COMMON, not what they ARE.
**Affects**: All qualitative interpretation
**Detection**: None.
**Severity**: MODERATE — labels may suggest more meaning than the evidence supports.

### F-IN-02: CLASS 1 INCLUDES NOISE-FREE DETERMINISTIC SYSTEMS
**Description**: All Class 1 systems (primes, Fibonacci, cfg, lambda, rewrite) are noise-free and deterministic. It is unclear whether Class 1 captures "ordered structure" or simply "non-probabilistic generation."
**Affects**: Class 1 interpretation
**Detection**: Add noise to Class 1 systems and check if they remain Class 1.
**Severity**: MODERATE — Class 1 may partially reflect lack of stochasticity.

### F-IN-03: CLASS 3 INCLUDES BOTH NOISE AND CHAOS
**Description**: Class 3 contains both iid_gaussian/colored_noise (pure randomness) and logistic/Henon (deterministic chaos) and additive_recurrence (deterministic recurrent). These are fundamentally different generative mechanisms.
**Affects**: Class 3 interpretation as "recurrent/m2-driven"
**Detection**: Semantic analysis from Phase U — Cluster 3: 20% arithmetic, 40% dynamical, 40% random.
**Severity**: MODERATE — Class 3 is the most heterogeneous class.

### F-IN-04: NOT A "PHASE DIAGRAM"
**Description**: The (m2_contrib, PC1) space is NOT a thermodynamic phase diagram. There is no free energy, no order parameter in the statistical mechanical sense, and no proven relationship between geometry class and physical phases.
**Affects**: All phase/order-parameter language
**Detection**: None.
**Severity**: MODERATE — the language is evocative but potentially misleading.

### F-IN-05: NO UNIVERSALITY CLAIM
**Description**: The three-class structure has been demonstrated on 14 systems + 6 new domains. This is NOT evidence of "universality" in the systematic sense (not tested on all possible generative mechanisms).
**Affects**: Universality claims
**Detection**: None.
**Severity**: CRITICAL — any claim of "universal geometry classes" is unsupported.

---

## 7. Engineering Failure Modes

### F-EN-01: STOCHASTIC_λ_TRACE
**Description**: lambda_reduction_trace uses Poisson noise in its trace generation (`np.random.poisson(2) * 0.5 + 0.5`). It is not a deterministic symbolic system despite being categorized as "symbolic."
**Affects**: λ-reduction's classification
**Detection**: Check generator code.
**Severity**: LOW — still produces Class 1-like behavior.

### F-EN-02: ISING_M_SIZE_BIAS
**Description**: Ising model uses L=6 lattice, which may be too small for critical dynamics. Larger lattices may produce different m2_contrib values.
**Affects**: Ising's Class 2 assignment
**Detection**: Check with L=12, L=24.
**Severity**: LOW — L=6 at T=2.5 produces reliable magnetization dynamics above critical temperature.

### F-EN-03: RD_SEED_SENSITIVITY
**Description**: Reaction-diffusion system depends on initial seed pattern. Different seeds may produce different dynamics (spontaneous pattern formation vs. extinction).
**Affects**: RD's Class 2 assignment
**Detection**: Run with multiple seeds.
**Severity**: LOW — F=0.035 reliably produces Turing patterns.

### F-EN-04: NEW_DOMAIN_CA_RULE_SELECTION
**Description**: Only 3 CA rules tested (30, 110, 184). CA Rule 184 was classified as Class 2, but many other CA rules (e.g., Rule 90, Rule 150) may behave differently.
**Affects**: CA classification claims
**Detection**: Test more CA rules.
**Severity**: LOW — the finding that Rule 184 (coherent transport) maps to Class 2 is a single data point, not a CA-wide result.

---

## 8. Summary: Critical-Only View

The following failures invalidate or seriously weaken a claim:

| ID | Severity | What it invalidates |
|----|----------|-------------------|
| F-TS-01 | CRITICAL | Single-metric PC1 = 1.0 is NOT structure (explicitly flagged, avoided) |
| F-TS-03 | HIGH | Class 3 PC1 partially distributional (mitigated by m2 ablation) |
| F-CL-03 | HIGH | Class structure depends on specific feature set |
| F-CL-08 | HIGH | Only 14 systems — may not generalize |
| F-OP-01 | HIGH | m2 alone discriminates nothing; only (m2, PC1) pair works |
| F-OP-05 | HIGH | Causal metric swap test invalid |
| F-IN-05 | CRITICAL | "Universality" not established |
| F-CL-06 | MODERATE | Adversarial covariance test passes but margin is modest |
| F-OP-02 | MODERATE | (m2, PC1) only recovers 64% of class structure |

**Surviving claims** (NOT invalidated by any known failure mode): three-class structure exists; m2_contribution discriminates; Class 2 is genuine nonlinear interaction structure (cannot be fabricated from noise+recurrence); temporal ordering is not fundamental to Class 2.
