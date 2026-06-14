# C1_08 — Surviving Claims Registry
## Strict evidence inventory after adversarial testing

**Rule**: Every claim must cite specific evidence, list limitations, and note applicable failure modes. Claims without direct evidence are marked as UNSUPPORTED.

---

## Claim 1: Transform-space geometry is not uniform across generative mechanisms

**Evidence**: 14 systems produce PC1 values ranging from 0.507 (Lorenz) to 0.954 (Henon). The range is not due to noise — iid_gaussian PC1=0.93 differs from Lorenz PC1=0.51 by 0.42, well beyond measurement noise (±0.02). Adversarial matched-covariance synthetic data produces lower silhouette (0.28 vs 0.35, ratio 1.26×), confirming non-uniformity is not purely a covariance artifact.

**Limitations**: Only 14 systems. "Non-uniform" does not imply a discrete number of classes — the geometry could be a continuum. The null hypothesis of "one universal geometry" is rejected, but the alternative is underdetermined.

**Applicable failure modes**: F-CL-08 (small N), F-CL-06 (modest adversarial margin), F-CL-03 (feature-dependent)

**Status**: SUPPORTED — high confidence

---

## Claim 2: Three geometry classes exist

**Evidence**: Ward linkage hierarchical clustering on 17 features yields 3 clusters. Silhouette = 0.35. Class assignments are:
- Class 1 (6): primes, fibonacci, modular_arithmetic, cfg_expansion, lambda_reduction, rewrite_system
- Class 2 (3): lorenz, ising_magnetization, reaction_diffusion
- Class 3 (5): additive_recurrence, logistic_map, henon_map, iid_gaussian, colored_noise

Classes are stable under feature-set perturbations (remove_spectral: 0.07, remove_ablation: 0.07, remove_tau_axis: 0.29, remove_replay: 0.57, noise_0.3: 0.42). ARI vs category labels = 0.27 — classes cross-cut obvious categories.

**Limitations**: Silhouette 0.35 is modest. Feature removal can collapse agreement to 0.07. The "3" in "3 classes" depends on dendrogram cut height — 2 or 4 clusters are also valid cuts. Number 3 was chosen as the elbow before within-cluster distance rises sharply.

**Applicable failure modes**: F-CL-01 (modest silhouette), F-CL-03 (feature dependency), F-CL-08 (small N), F-CL-02 (category leakage is actually supporting)

**Status**: SUPPORTED — moderate confidence (number of classes is the weakest part)

---

## Claim 3: m2_contribution is the primary discriminative order parameter

**Evidence**: Across 9 systems with ablation data, m2_contribution = full_PC1 − no_m2_PC1 ranges from -0.378 (Lorenz) to +0.252 (iid_gaussian). Class 2 systems are NEGATIVE (m2_contrib < -0.1); Class 3 systems are POSITIVE (m2_contrib > 0.05); Class 1 systems are NEAR-ZERO (|m2_contrib| < 0.02). Removing ablation features collapses agreement to 0.07. Single-feature m2_contribution clustering gives ARI=0.29 vs full clustering — not high, but only pc1 (0.57) and tau_m3 (0.71) do better alone.

**Limitations**: m2_contribution alone aggregates only 0.07 agreement (though most of that is from zero-variance for systems not run through ablation). It is necessary but not sufficient — must be paired with PC1. Only 9 of 14 systems have measured m2_contrib; the remaining 5 are inferred from cluster membership. The metric mixes real signal with distributional artifact.

**Applicable failure modes**: F-OP-01 (necessary but not sufficient), F-TS-04 (artifact mixing), F-OP-02 (incomplete recovery)

**Status**: SUPPORTED — high confidence necessary, moderate confidence primary

---

## Claim 4: (m2_contribution, PC1) is the minimal sufficient ordered pair

**Evidence**: In minimal basis search, (pc1 + pc1_ratio + abl_no_m2_pc1) achieves agreement=1.0. In order parameter reduction, (m2_plus_pc1) achieves agreement=0.64 vs full clustering — higher than m2_only (0.07), m2_plus_tau (0.36), or non_m2 (0.07). No single feature or other pair achieves this.

**Limitations**: Recovery is 0.64, not 1.0. The pair captures 64% of class structure; 36% is in other features. Other 3-feature subsets also achieve 1.0 (e.g., effective_rank + phase_corr + abl_no_m2_pc1). The pair is minimal but not unique.

**Applicable failure modes**: F-CL-07 (basis non-uniqueness), F-OP-02 (incomplete recovery)

**Status**: SUPPORTED — moderate confidence (minimal but not unique, 64% not 100% with 2 features)

---

## Claim 5: Class 2 represents propagating interacting structure

**Evidence**: Systems in Class 2 share a mechanism: multiple degrees of freedom interacting coherently over time. Lorenz (3 coupled ODEs), Ising (2D lattice with thermal fluctuations), reaction_diffusion (PDE with coupled species). All have m2_contrib < -0.1 (m2 ADDS dimensionality — removing m2 RAISES PC1). ca_rule184 (traffic CA, coherent transport) classified as Class 2 in new-domain test (m2_contrib = -0.33). Phase-scrambled Lorenz retains Class 2 (m2_contrib = -0.22) — discriminating signal is interactional/spectral, not chronological.

**Limitations**: Only 3 core systems + 1 CA. "Interacting" is a post-hoc label — the clustering did not use interaction as a feature. The mechanism linking negative m2_contrib to interaction degree is not proven; it is a correlation. Phase-scrambling retention could indicate the signal is spectral rather than interactional per se.

**Applicable failure modes**: F-IN-01 (labels are metaphors), F-AD-02 (phase-scrambled retention is real but requires careful interpretation)

**Status**: SUPPORTED — low confidence (strongest evidence is ca_rule184 + adversarial, but theoretical mechanism is speculative)

---

## Claim 6: Class 2 cannot be fabricated from noise + recurrence

**Evidence**: Adversarial test: noise + logistic recurrence at α = 0 to 0.99 produced m2_contrib from 0.08 to 0.36 — all positive (Class 3-like). No α produced negative m2_contrib. The closest was α=0.10 with m2_contrib=0.077.

**Limitations**: Only one recurrence type tested (logistic). A different recurrence (e.g., Lorenz iterated map, Hénon within noise) might produce different results. The test covered α up to 0.99; at exactly α=1.0 it is pure logistic (which oscillates between Class 2 and 3 depending on r).

**Applicable failure modes**: F-AD-01 (this is the test — it passes)

**Status**: SUPPORTED — moderate confidence (one recurrence type, but many α values)

---

## Claim 7: Temporal ordering is not fundamental to Class 2

**Evidence**: Phase-scrambled Lorenz (FFT → randomize phases → IFFT, destroying temporal chronology) retains m2_contrib = -0.22 (Class 2). The m2 metric only compares halves — it does not use sequential ordering within each half. The discriminating signal survives phase randomization because it is carried by the interaction of spectral components.

**Limitations**: Phase-scrambling preserves the power spectrum. The claim should be "temporal chronology is not required" not "temporal ordering is irrelevant." The signal could still be spectral-temporal (order of frequencies matters).

**Applicable failure modes**: F-AD-02 (passes the test)

**Status**: SUPPORTED — high confidence (direct adversarial evidence)

---

## Claim 8: Class 1 represents ordered/structural sequences

**Evidence**: Class 1 systems are all sequences generated by deterministic rules: primes (number-theoretic), fibonacci (recurrence), modular (periodic), cfg_expansion (length doubling), lambda_reduction (monotonic), rewrite (Fibonacci word). All have |m2_contrib| < 0.02 (nearly zero — removing m2 does not change PC1 meaningfully). All have high PC1 (> 0.86). All have replay_displacement < 0.02 (replay barely changes metrics).

**Limitations**: All Class 1 systems are noise-free and deterministic. It is unclear whether noise-free determinism produces Class 1, or ordered structure does. Class 1 includes both arithmetic and symbolic systems — the label "ordered/structural" may conflate multiple subtypes. Tau-axis loadings are dominated by m1 and m3 (sign-based metrics), reflecting orderly sign alternation.

**Applicable failure modes**: F-IN-02 (determinism confound), F-CL-04 (replay displacement ambiguity)

**Status**: SUPPORTED — moderate confidence (determinism confound not resolved)

---

## Claim 9: Class 3 represents m2-driven or spectrally dominated systems

**Evidence**: Class 3 systems all have positive m2_contrib (m2 adds dimensionality — removing it LOWERS PC1). They share high temporal_corr (> 0.9) and high phase_corr (> 0.99), indicating the metric vector is determined by marginal statistics rather than temporal order. Includes both deterministic chaos (logistic, Henon) and pure randomness (Gaussian, colored noise).

**Limitations**: Class 3 is the most heterogeneous class (20% arithmetic, 40% dynamical, 40% random). The label "m2-driven" is more of a measurement artifact than a mechanism — m2 happens to correlate with spectral dominance. The positive m2_contrib for noise is partially a distributional artifact (see F-TS-03). Logistic map's m2_contrib oscillates between negative and positive across r ∈ [3.5, 4.0], so "Class 3" is not a stable property of the logistic map as a system.

**Applicable failure modes**: F-IN-03 (heterogeneous class), F-TS-03 (distributional artifact contamination), F-TS-04 (partial separability)

**Status**: SUPPORTED — low confidence (class is a mixed bag; may be an artifact category)

---

## Claim 10: m2_contribution tracks structural reorganization

**Evidence**: For the logistic map, m2_contrib oscillates between negative and positive across r ∈ [3.5, 4.0]. The derivative peaks at periodic window boundaries: max |d(m2_contrib)/dr| = 55 at r ≈ 4.0. This tracks known periodic window dynamics in the logistic map's bifurcation structure.

**Limitations**: The derivative peak at r=4.0 is at the edge of the scan range — may be unbounded. Only one system (logistic) was scanned at high resolution. The relationship between m2_contrib peaks and specific bifurcation points (period-doubling, band merging, crisis) has not been precisely mapped.

**Applicable failure modes**: F-OP-04 (edge-of-range derivative), F-OP-03 (transition band)

**Status**: SUPPORTED — moderate confidence (one system, one scan)

---

## Claim 11: Three-class structure is partial domain-general

**Evidence**: 6 new domain systems (CA rules 30, 110, 184; GOE random matrix; LFSR; DFA) were classified using m2_contrib thresholds without retraining. ca_rule184 (coherent transport) → Class 2 (m2_contrib = -0.33). lfsr_crypto → Class 1 (m2_contrib = -0.004). dfa_trace → Class 1 (m2_contrib = 0.03). ca_rule30 → borderline Class 1 (m2_contrib = 0.06). ca_rule110 → borderline Class 1 (m2_contrib = -0.09). goe_random_matrix → Class 3 (m2_contrib = 0.10). The classification is consistent with expectations.

**Limitations**: Only 6 systems tested. Threshold-based classification (predefined m2_contrib cutoffs) is coarser than full clustering. goe_random_matrix PC1=0.74 is lower than typical Class 3 — may be a new subclass. ca_rule110 m2_contrib=-0.09 is near Class 2 boundary — its classification is ambiguous.

**Applicable failure modes**: F-IN-04 (thresholds are not physical phase boundaries)

**Status**: SUPPORTED — low confidence (small number of new domains; threshold method)

---

## Claim 12: Class 2 represents the most coherent class

**Evidence**: Class 2 has the lowest within-class distance (5.34–5.87) and highest inter-class distance to Class 3 (7.5–9.0). In cross-metric transfer, dynamical systems (mostly Class 2) achieve highest classification accuracy. The three Class 2 members all share negative m2_contrib, which no Class 1 or Class 3 system has.

**Limitations**: Only 3 systems in Class 2 — the "most coherent" label may reflect low sample count rather than genuine tightness. Adding more interacting nonlinear systems (e.g., Chua circuit, FitzHugh-Nagumo, Susceptible-Infected-Recovered) could increase within-class variance.

**Applicable failure modes**: F-CL-08 (small N), F-OP-03 (boundary ambiguity)

**Status**: SUPPORTED — moderate confidence (small N, but negative m2_contrib is a clear discriminator)

---

## Summary: What Survives

| # | Claim | Confidence | Key Evidence |
|---|-------|------------|-------------|
| 1 | Geometry is non-uniform | HIGH | PC1 range 0.51–0.95, adversarial passes |
| 2 | Three classes exist | MODERATE | Silhouette 0.35, stability tests, cross-category |
| 3 | m2_contrib is primary axis | MODERATE | Ablation collapse to 0.07, range -0.38 to +0.25 |
| 4 | (m2, PC1) is minimal pair | MODERATE | Order reduction ARI 0.64 vs 0.07 |
| 5 | Class 2 = interacting structure | LOW | ca_rule184 match, negative m2_contrib only class |
| 6 | Class 2 cannot be fabricated | MODERATE | Noise+recurrence all positive |
| 7 | Temporal order not fundamental | HIGH | Phase-scrambled Lorenz retains Class 2 |
| 8 | Class 1 = ordered/structural | MODERATE | Noise-free, deterministic, m2 near zero |
| 9 | Class 3 = m2-driven/spectral | LOW | Positive m2_contrib, high temporal corr, heterogeneous |
| 10 | m2_contrib tracks reorganization | MODERATE | Logistic scan derivative peaks at transitions |
| 11 | Partial domain generality | LOW | 6 new domains, threshold classification |
| 12 | Class 2 is most coherent | MODERATE | Tightest cluster, negative m2_contrib unique |

**NOT supported**: "Universality," "phase diagram," "order parameter in thermodynamic sense," "emergence," "one universal geometry," any claim about mechanism (m2_contrib is correlational, not causal).
