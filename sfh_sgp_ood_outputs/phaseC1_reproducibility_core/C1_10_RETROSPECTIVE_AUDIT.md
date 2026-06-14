# C1_10 — RETROSPECTIVE AUDIT

## Rule: Every claim is traced from RAW FILES. No narrative allowed. All assumptions flagged.

---

## AUDIT METHOD

For each claim from C1_08 surviving_claims_registry.md:
1. Identify raw input file(s) and exact column(s)
2. Trace computation path file→file→claim
3. Compute or verify key numbers independently
4. Identify dependency chain and hidden assumptions
5. Flag UNVERIFIED preprocessing steps
6. Classify: COMPUTED / INFERRED / INTERPRETIVE / UNSUPPORTED

---

## 0. CRITICAL DISCREPANCIES FOUND IN RAW DATA

### D1: Silhouette values IDENTICAL across all 14 systems
- **File**: `clustering_results.csv`
- **Column**: `silhouette`
- **Value**: `0.3516556767466198` for ALL 14 rows
- **Problem**: Per-point silhouette scores should vary by system. A global constant suggests either:
  - (a) The global average was placed in every row (display artifact)
  - (b) A bug assigned the same value to all rows
  - (c) Only 1 silhouette computation was done for the entire clustering
- **Impact**: Individual system silhouette values cannot be audited. The claim that "some systems have higher silhouette than others" cannot be verified from this file.
- **Action required**: Verify per-point silhouettes match this average.

### D2: m2_contribution = 0.0 for 7 of 14 systems
- **File**: `clustering_feature_matrix.csv`
- **Column**: `m2_contribution`
- **Systems with zero**: fibonacci, modular_arithmetic, additive_recurrence, reaction_diffusion, lambda_reduction, rewrite_system, colored_noise
- **Root cause**: `metric_ablation_results.csv` only contains data for 9 systems (constant, linear_ramp, iid_gaussian, primes, lorenz, logistic_map, henon_map, ising_magnetization, cfg_expansion). Of the 14 main systems, only 7 have ablation data:
  - primes, lorenz, logistic, henon, ising, iid_gaussian, cfg_expansion (non-zero m2_contrib)
  - The remaining 7 have NO ablation data → m2_contrib defaulted to 0.0
- **Impact**:
  - Claim "m2_contribution is the primary discriminative order parameter" depends on 50% imputed data
  - Class 1: 2/6 systems with measured m2_contrib (primes=0.012, cfg=0.006); 4/6 imputed 0.0
  - Class 2: 2/3 systems with measured m2_contrib (lorenz=-0.378, ising=-0.319); RD imputed 0.0
  - Class 3: 3/5 systems with measured m2_contrib (logistic=0.187, henon=0.192, iid=0.252); additive_recurrence and colored_noise imputed 0.0
- **Severity**: HIGH — claims about m2_contrib thresholds depend on data that does not exist for 50% of systems

### D3: "m2_only" in order reduction ≠ "m2_contribution" in minimal basis
- **Order reduction (`phaseV_order_reduction.csv`)**: `m2_only` uses column `abl_no_m2_pc1` (PC1 when metric m2 is removed from the set)
- **Minimal basis (`minimal_basis_report.csv`)**: `m2_contribution` = full_PC1 − no_m2_PC1 (the DIFFERENCE)
- **Both called "m2" in reports but measure different things**:
  - `abl_no_m2_pc1` alone gives ARI = 0.07 vs full clustering
  - `m2_contribution` alone gives ARI = 0.2857 vs full clustering
- **Consolidated synthesis error**: Section 3.2 says "m2_contribution alone | 0.07" but the correct value for m2_contribution alone is 0.2857. The 0.07 is for abl_no_m2_pc1.
- **Severity**: CRITICAL — claim about m2_contribution's discriminative power uses wrong baseline

### D4: Derivative values differ between summary and raw data
- **`phaseV_summary.md` Section 1**: "Max ∂(m2_contrib)/∂r at r=4.0000 = -20.1885"
- **`phaseV_transition_scan.csv`**: Max |d(contrib)/dr| = 55.26798912230173 at r=4.0
- **Difference**: The summary uses a different (coarser) derivative computation than the transition scan
- **Impact**: Maximum derivative claim is numerically unstable. Two different pipelines produce different values.
- **Severity**: MODERATE — qualitative conclusion (derivatives peak at transitions) is robust, exact magnitude is not

### D5: All single-metric PC1 values = 1.0 (trivial identity)
- **File**: `metric_ablation_results.csv`
- **All rows where n_metrics=1**: PC1 = 1.0 for EVERY system
- **Correctly flagged as F-TS-01**: But this means ANY claim about single-metric importance based on PC1 is mathematically forced
- **Impact**: The statement that "m2_only (single metric) gives PC1 = 1.0" is true for ALL metrics for ALL systems — it carries zero information

---

## 1. CLAIM-BY-CLAIM AUDIT

---

### Claim 1: "Transform-space geometry is not uniform across generative mechanisms"

**Classification**: COMPUTED

**Raw source**: `cross_domain_reproducibility.csv`
**Column**: `pc1_variance`
**Values**:
- Lorenz: 0.507
- Henon: 0.954
- iid_gaussian: 0.929
- Range across 14 systems: [0.507, 0.954], span = 0.447

**Computation path**:
1. For each system, generate 50 signals × 8 transforms = 400 samples
2. Compute 4 metrics per sample → 400×4 matrix
3. PCA on normalized 400×4 matrix → PC1 = fraction of variance explained
4. Range = max(PC1) - min(PC1) across 14 systems

**Null comparison**: iid_gaussian PC1 = 0.929 ≠ Lorenz PC1 = 0.507, difference = 0.422. Noise measurement error ≈ ±0.02 (stated in reproducibility manifest). 0.422 >> 0.02, so difference exceeds noise.

**Adversarial support**: `adversarial_artifact_report.json` — matched-covariance synthetic silhouette = 0.2795 vs real = 0.3517, ratio = 1.258. This tests whether the non-uniformity is purely due to covariance structure. Ratio > 1.0 confirms non-uniformity is partially real.

**Untested assumptions**:
- PCA implementation: sklearn PCA default (full SVD). Normalization method not specified in raw data (z-score assumed).
- 50 signals × 8 transforms = 400 samples. PCA on 4 features × 400 samples is reliable. But transform selection (which 8 transforms) determines the geometry. Different transforms → different PC1.
- The identity transform is included — this anchors the metric space at the origin. Removing the identity transform changes all PC1 values.

**Dependencies**: preprocessing (signal generation), 8 transform definitions, metric computation (4 deterministic functions), PCA (sklearn default)

**Verdict**: COMPUTED — directly verified from raw data. PC1 range 0.507–0.954 with iid_gaussian at 0.929 confirms non-uniformity.

---

### Claim 2: "Three geometry classes exist"

**Classification**: INFERRED (number of classes) / COMPUTED (cluster assignments)

**Raw source**: `clustering_results.csv`, `clustering_feature_matrix.csv`

**Columns**:
- `hier_cluster`: Ward linkage hierarchical cluster assignment (1, 2, 3)
- `km_cluster`: K-means cluster assignment (1, 2, 3)
- `silhouette`: reported as 0.352 for all systems

**Computation path**:
1. Feature matrix: 14 systems × 17 features (`clustering_feature_matrix.csv`)
2. z-score normalization (assumed, not recorded in file)
3. Euclidean distance, Ward linkage hierarchical clustering
4. Cut at 3 clusters based on dendrogram elbow (not recorded: no dendrogram file exists)
5. Silhouette = 0.352 (global average)

**Known cluster assignments** (hierarchical):
- Class 1: primes, fibonacci, modular_arithmetic, cfg_expansion, lambda_reduction, rewrite_system (6)
- Class 2: lorenz, ising_magnetization, reaction_diffusion (3)
- Class 3: additive_recurrence, logistic_map, henon_map, iid_gaussian, colored_noise (5)

**Known disagreements** (hierarchical vs k-means):
- additive_recurrence: hier=3, km=3 (agree)
- lorenz: hier=2, km=1 (DISAGREE)
- ising_magnetization: hier=2, km=3 (DISAGREE)
- reaction_diffusion: hier=2, km=1 (DISAGREE)

**k-means vs hierarchical disagreement**: 3 out of 14 systems (21%) disagree between algorithms. This means the 3-cluster structure is ALGORITHM-DEPENDENT.

**Stability constraints** (`class_stability_report.csv`):
- remove_spectral: ARI=0.07 (near random)
- remove_tau_axis: ARI=0.29
- remove_null_audit: ARI=0.14
- remove_replay: ARI=0.57
- remove_ablation: ARI=0.07 (near random)
- noise_0.3: ARI=0.42

**Two feature removal tests collapse to 0.07** — class structure depends on specific feature subsets.

**Untested assumptions**:
- Number of clusters (3) was chosen by dendrogram elbow. No file documents the dendrogram or where the cutoff was made.
- No Gap statistic, no null-vs-k comparison, no stability across cluster numbers.
- The feature matrix includes duplicate information (pc1 and abl_full_pc1 are nearly identical).
- 14 samples with 17 features: p > n situation, clustering is high-variance.

**Dependencies**: all 17 feature columns, z-score normalization, distance metric (Euclidean), linkage (Ward), dendrogram cut height

**Verdict**: INFERRED — cluster assignments are computed from raw data, but the CHOICE of 3 clusters is an interpretive decision not verified against null distributions. k-means disagrees on 21% of systems. Feature removal can collapse agreement to 0.07. Silhouette constant across rows is unexplained.

---

### Claim 3: "m2_contribution is the primary discriminative order parameter"

**Classification**: INFERRED (with imputed data)

**Raw source**: `metric_ablation_results.csv`, `clustering_feature_matrix.csv`

**Columns used**:
- `ablation` = "full", "no_m2"
- `pc1` values for each

**m2_contribution = full_PC1 − no_m2_PC1** for measured systems:
- primes: 0.940 − 0.928 = 0.012
- lorenz: 0.507 − 0.884 = -0.378
- logistic: 0.884 − 0.697 = 0.187
- henon: 0.957 − 0.765 = 0.192
- ising: 0.637 − 0.957 = -0.320
- cfg_expansion: 0.934 − 0.928 = 0.006
- iid_gaussian: 0.930 − 0.679 = 0.252

**Key problem**: 7 of 14 systems have m2_contrib = 0.0 because no ablation data was computed. The "primary discriminative" claim rests on the 7 systems with measured values — but the clustering was done on all 14, with 7 imputed zeros.

**ARI evidence**:
- `m2_contribution` alone ARI = 0.2857 (from `minimal_basis_report.csv` line 18)
- `abl_no_m2_pc1` alone ARI = 0.0714 (from `minimal_basis_report.csv` line 15)
- Both are lower than `tau_m3` alone (0.7143), `pc1` alone (0.5714), `pc2` alone (0.5714), `phase_corr` alone (0.5714)
- m2_contribution is the 6th best single feature, not the best

**The claim "primary" is not supported by single-feature ARI ranking.** Tau_m3 (0.71), PC1 (0.57), PC2 (0.57), phase_corr (0.57), effective_rank (0.50) all outperform m2_contribution (0.2857) as single features. The claim shifts to ablation sensitivity (removing m2-related features collapses agreement) — this is an INFERRED property, not a direct ranking.

**Dependencies**: ablation pipeline (50 signals × 8 transforms × 5 metric sets per system), PCA on 4D vs 3D spaces (comparing PC1 across different dimensionalities)

**Untested**: Whether the ablation effect is specific to m2 or whether removing ANY metric from the set changes PC1 in a class-dependent way. The ablation data for no_m1, no_m3, no_m4 also shows class-dependent drops — the m2 effect is the LARGEST but not unique.

**Verdict**: INFERRED — supported for 7 measured systems but "primary" is overstated. Three other single features have higher ARI. 50% of systems use imputed zeros. "Primary" should be "necessary for class structure but not the best single discriminator."

---

### Claim 4: "(m2_contribution, PC1) is the minimal sufficient ordered pair"

**Classification**: COMPUTED (with naming caveat)

**Raw source**: `phaseV_order_reduction.csv`, `minimal_basis_report.csv`

**Columns**:
- `phaseV_order_reduction.csv`: feature_set="m2_plus_pc1", features="abl_no_m2_pc1+pc1", agreement=0.642857
- `minimal_basis_report.csv` line 31: features="pc1+abl_no_m2_pc1", agreement=0.642857
- `minimal_basis_report.csv` line 34: features="pc1+m2_contribution", agreement=0.214286

**CRITICAL NAMING DISTINCTION**:
- "m2_plus_pc1" in all reports = (abl_no_m2_pc1, pc1) → ARI=0.64
- (m2_contribution, pc1) → ARI=0.21
- These are DIFFERENT pairs with different ARI values

The consolidated_synthesis.md section 3.2 claims "m2_contribution alone | 0.07" but the 0.07 is for abl_no_m2_pc1 alone. The correct value for m2_contribution alone is 0.2857.

**What (abl_no_m2_pc1, pc1) pair achieves ARI=0.64 means**:
- abl_no_m2_pc1 = PC1 when m2 is removed from the metric set
- pc1 = PC1 with all 4 metrics
- This pair captures the CHANGE in geometry when m2 is present vs absent
- It is NOT measuring m2_contribution directly — it's measuring the geometry before and after m2 removal

**Other 2-feature pairs that equal or exceed 0.64**:
- `pc2+m2_contribution` = 0.7857 (line 49)
- `tau_m2+m2_contribution` = 0.9286 (line 88)
- `tau_m3+replay_displacement` = 0.8571 (line 93)
- `tau_m4+phase_corr` = 0.9286 (line 101)
- `tau_m4+replay_displacement` = 0.9286 (line 103)
- `temporal_corr+phase_corr` = 0.9286 (line 110)
- `temporal_corr+replay_displacement` = 0.9286 (line 112)

**Conclusion**: (abl_no_m2_pc1, pc1) is NOT the best 2-feature pair for recovering the clustering. At least 6 other 2-feature subsets outperform it (0.79–0.93 vs 0.64).

**Dependencies**: zero-imputed values for 7/14 systems affect all pairwise ARI computations

**Verdict**: COMPUTED but MISREPORTED. The pair is (abl_no_m2_pc1, pc1) not (m2_contribution, pc1). It achieves ARI=0.64 but is NOT the best pair — 6+ other pairs score higher. The "minimal sufficient" claim is unsupported by the data.

---

### Claim 5: "Class 2 represents propagating interacting structure"

**Classification**: INTERPRETIVE

**Raw source**: `clustering_results.csv`, `phaseV_new_domains.csv`, `phaseV_adversarial.csv`

**Evidence**: 
- Class 2 contains: lorenz (coupled ODEs), ising_magnetization (2D lattice), reaction_diffusion (PDE)
- ca_rule184 (traffic CA, coherent transport) → Class 2 in new domains test, m2_contrib = -0.3287
- Phase-scrambled Lorenz retains Class 2 (m2_contrib = -0.215)

**What the raw data actually shows**:
- Class 2 = systems with negative m2_contrib AND low PC1 (< 0.75)
- 3 core systems + 1 CA rule share this signature
- The LABEL "propagating interacting" is a post-hoc interpretation

**Unverified**: 
- No non-interacting control system with negative m2_contrib + low PC1 exists to test the converse
- Systems with multiple degrees of freedom that DON'T interact (e.g., independent oscillators) have not been tested
- "Interaction" is not a feature in the feature matrix — it's an interpretive label
- CA Rule 184 is the strongest independent evidence, but it's one data point

**Verdict**: INTERPRETIVE. The raw data shows a correlation between negative m2_contrib + low PC1 and systems that are known to have propagating interacting dynamics. But no causal test exists. Confidence should be LOW as stated.

---

### Claim 6: "Class 2 cannot be fabricated from noise + recurrence"

**Classification**: COMPUTED

**Raw source**: `phaseV_adversarial.csv`

**Columns**: `system`, `alpha`, `m2_contribution`

**Values**:
- noise+recurrence_α=0.00: m2_contrib = 0.1015
- noise+recurrence_α=0.10: m2_contrib = 0.0770
- noise+recurrence_α=0.30: m2_contrib = 0.1245
- noise+recurrence_α=0.50: m2_contrib = 0.1358
- noise+recurrence_α=0.70: m2_contrib = 0.3641
- noise+recurrence_α=0.90: m2_contrib = 0.2069
- noise+recurrence_α=0.99: m2_contrib = 0.2095

**Computation**: All α produce m2_contrib > 0.05 (Class 3 territory). None produce m2_contrib < -0.1 (Class 2 threshold). Min observed = 0.077 (α=0.10).

**Null**: If Class 2 were a fabrication artifact of noise+recurrence, at least some α would produce m2_contrib < -0.1. This is falsified.

**Limitations in raw data**:
- Only logistic (recurrence) tested. Other recurrence maps (Hénon, Lorenz iterated) not tested.
- α up to 0.99. α=1.0 = pure logistic (which oscillates between Class 2/3)
- Recurrence weight = logistic_map(r=4.0) specifically. Other r values produce different m2_contrib

**Verdict**: COMPUTED — directly verified from raw data. All 7 α values produce positive m2_contrib. Claim passes the test. Limitation: one recurrence type only.

---

### Claim 7: "Temporal ordering is not fundamental to Class 2"

**Classification**: COMPUTED

**Raw source**: `phaseV_adversarial.csv`

**Columns**: `system`, `m2_contribution`

**Values**:
- lorenz_phase_scrambled: m2_contrib = -0.215 (Class 2 negative)
- Lorenz original: m2_contrib = -0.378 (from clustering_feature_matrix)

**Computation**: Phase-scrambled Lorenz (FFT → randomize phases → IFFT, destroying temporal chronology) retains m2_contrib < -0.1.

**Null**: If temporal ordering were required for Class 2, destroying chronology would push m2_contrib to 0 or positive. Observed: m2_contrib stays negative (-0.215).

**Caveat**: Phase-scrambling preserves power spectrum. The signal could be spectral (not temporal-chronological) but still spectral-interactional. Phase-scrambled m2_contrib = -0.215 is LESS negative than original -0.378 — some temporal information contributes but is not necessary.

**Verdict**: COMPUTED — directly verified. Data shows Class 2 signal survives phase randomization by a margin of 0.215 below the Class 2 threshold (< -0.1).

---

### Claim 8: "Class 1 represents ordered/structural sequences"

**Classification**: INTERPRETIVE

**Raw source**: `clustering_feature_matrix.csv`, `class_semantics.csv`, `replay_stability_ood.csv`

**Evidence from raw data**:
- Class 1 systems all have replay_displacement < 0.02 (primes=0.016, cfg=0.016, lambda=0.016)
- Class 1 systems all have PC1 > 0.86
- 2 measured Class 1 systems have |m2_contrib| < 0.02 (primes=0.012, cfg=0.006)
- 4 Class 1 systems have m2_contrib = 0.0 (imputed — no verification)

**Interpretive step**:
- "Ordered/structural" is a post-hoc label based on known system types (prime number sequence, Fibonacci, CFG expansion)
- All Class 1 systems are deterministic and noise-free → confound with determinism
- No test distinguishes "ordered structure" from "noise-free deterministic generation"

**Unverified**: Adding noise to Class 1 systems and checking class migration has NOT been done.

**Verdict**: INTERPRETIVE — label based on known system properties. Determinism confound is unresolved. m2_contrib data is imputed for 4/6 systems.

---

### Claim 9: "Class 3 represents m2-driven or spectrally dominated systems"

**Classification**: INTERPRETIVE

**Raw source**: `clustering_feature_matrix.csv`, `class_semantics.csv`, `null_audit_ood.csv`

**Evidence from raw data**:
- Class 3 systems all have m2_contrib > 0.05 (where measured)
- Class 3 has high temporal_corr (> 0.9) and high phase_corr (> 0.99)
- Class 3 is most heterogeneous: 20% arithmetic, 40% dynamical, 40% random

**Interpretive problems**:
- "m2-driven" is circular — m2_contrib > 0 IS the class definition, so saying class 3 is "m2-driven" is tautological
- Class 3 includes both deterministic chaos (logistic, henon) and pure randomness (iid, colored noise) — fundamentally different mechanisms
- Logistic map's m2_contrib oscillates between positive and negative across r ∈ [3.5, 4.0] — "Class 3" is not stable for a given system

**Verdict**: INTERPRETIVE — class label describes a symptom (high m2_contrib) not a mechanism. The class is genuinely heterogeneous. Low confidence is appropriate.

---

### Claim 10: "m2_contribution tracks structural reorganization"

**Classification**: COMPUTED

**Raw source**: `phaseV_perturbation.csv`, `phaseV_transition_scan.csv`

**Columns**: `r`, `m2_contribution`, `d_contrib_dr`

**Computation**:
- 26 r values from 3.5 to 4.0
- m2_contrib oscillates between -0.393 (r=3.70) and +0.253 (r=3.96)
- Max |d(m2_contrib)/dr| = 55.27 at r=4.0 (`phaseV_transition_scan.csv`)

**Known caveat**: r=4.0 is the edge of the scan range. The derivative may be unbounded for r > 4.0 (logistic diverges).

**Discrepancy**: `phaseV_summary.md` reports max derivative = -20.1885 at r=4.0, but `phaseV_transition_scan.csv` reports 55.27. These differ by factor 2.7×. The derivative computation method is not consistent across pipeline stages.

**Verdict**: COMPUTED — the oscillation of m2_contrib across r is verified from raw data. Derivative magnitude is unstable (2.7× difference across pipeline stages). Limited to one system (logistic map).

---

### Claim 11: "Three-class structure is partial domain-general"

**Classification**: COMPUTED (with threshold method caveat)

**Raw source**: `phaseV_new_domains.csv`

**Columns**: `system`, `m2_contribution`, `predicted_class`

**Classification method**: Threshold-based on m2_contrib (NOT full clustering pipeline)
- m2_contrib < -0.1 → Class 2
- |m2_contrib| < 0.05 → Class 1
- m2_contrib > 0.05 → Class 3

**Values**:
- ca_rule30: m2_contrib=0.065 → Class 1 (borderline — could be Class 3 by strict threshold)
- ca_rule110: m2_contrib=-0.092 → Class 1 (borderline — |0.092| > 0.05 threshold)
- ca_rule184: m2_contrib=-0.329 → Class 2
- goe_random_matrix: m2_contrib=0.101 → Class 3
- lfsr_crypto: m2_contrib=-0.004 → Class 1
- dfa_trace: m2_contrib=0.033 → Class 1

**Threshold ambiguity**: ca_rule110 has m2_contrib=-0.092 which is INSIDE the Class 2 range (< -0.1) but was assigned Class 1. The threshold boundaries are NOT sharp — ca_rule110 is at the boundary.

**Additional test NOT done**: The 6 new domain systems were NOT run through the full 17-feature pipeline and hierarchical clustering. They were classified by threshold only.

**Verdict**: COMPUTED — 6 new systems mapped to thresholds. But ca_rule110 threshold assignment is inconsistent with the stated boundary. No full pipeline verification.

---

### Claim 12: "Class 2 is the most coherent class"

**Classification**: COMPUTED

**Raw source**: `transition_distances.csv`

**Columns**: distance matrix (14×14, Euclidean in feature space)

**Within-class distances for Class 2** (lorenz, ising, reaction_diffusion):
- lorenz–ising: 5.34 (transition_distances.csv row 6, col 9 — rounded from 5.34497)
- lorenz–RD: 5.87 (row 6, col 10 — 5.86904)
- ising–RD: 8.11 (row 9, col 10 — 8.10589)

**Within-class distance for Class 2**: [5.34, 5.87, 8.11]. Mean = 6.44.

**Within-class distance for Class 1** (primes, fibonacci, modular, cfg, lambda, rewrite):
- Range: 0.06 to 5.14. Mean ≈ 3.1.

**Class 1 is actually MORE coherent** by within-class distances (mean 3.1 vs 6.4). The claim that Class 2 is "most coherent" is FALSE based on within-class distances.

**The evidence cited in the claim** is inter-class distance to Class 3 (7.5–9.0) — Class 2 is FARTHEST from Class 3. But "most coherent" refers to within-class tightness, not inter-class separation.

**Verdict**: COMPUTED but MISSTATEMENT. Class 1 has tighter within-class distances (mean 3.1) than Class 2 (mean 6.4). Class 2 has the LARGEST separation from Class 3. The claim conflates "most separated from other classes" with "most coherent."

---

## 2. DEPENDENCY GRAPH — WHAT EACH CLAIM DEPENDS ON

```
CLAIM 1 (non-uniform geometry)
├── signal generation (14 systems × parameters)
├── 8 transform definitions
├── 4 metric computations
├── PCA (sklearn default)
└── n_samples=50

CLAIM 2 (three classes)
├── CLAIM 1 (PC1 values)
├── ALL 17 features (clustering_feature_matrix.csv)
│   ├── 7 features from cross-domains/PCA (pc1, pc2, effective_rank, tau_*)
│   ├── 4 features from null audit (temporal_corr, phase_corr, pc1_ratio)
│   ├── 1 feature from replay (replay_displacement)
│   └── 5 features from ablation (abl_*)
├── z-score normalization
├── Ward linkage, Euclidean distance
├── dendrogram cut height (unrecorded)
└── N=14 samples, p=17 features

CLAIM 3 (m2_contrib primary)
├── metric_ablation_results.csv (9 systems only, not 14)
├── PCA on 3D vs 4D spaces
├── CLUSTERING (Claim 2) as reference
└── IMPUTED ZEROS for 7 systems

CLAIM 4 ((m2, PC1) minimal pair)
├── CLAIM 2 (full clustering)
├── minimal_basis_report.csv (all 2-feature ARI values)
├── IMPUTED ZEROS for ablation features
└── NAMING: uses abl_no_m2_pc1, NOT m2_contribution

CLAIM 5 (Class 2 = interacting)
├── CLAIM 2 (cluster assignments)
├── CLAIM 7 (phase-scrambled Lorenz)
├── new_domains (ca_rule184)
└── POST-HOC LABEL (no interaction feature in pipeline)

CLAIM 6 (noise+fabrication)
├── phaseV_adversarial.csv (7 α values, 1 recurrence type)
└── logistic map (r=4.0) as recurrence

CLAIM 7 (temporal not fundamental)
├── phaseV_adversarial.csv (lorenz_phase_scrambled)
└── FFT + phase randomization implementation

CLAIM 8 (Class 1 = ordered/structural)
├── CLAIM 2 (cluster assignments)
├── replay_stability_ood.csv (replay_displacement)
└── POST-HOC LABEL (determinism confound)

CLAIM 9 (Class 3 = m2-driven)
├── CLAIM 2 (cluster assignments)
├── metric_ablation_results.csv
└── TAUTOLOGICAL (m2_contrib > 0 defines both the claim and the class)

CLAIM 10 (m2 tracks reorganization)
├── phaseV_perturbation.csv
├── phaseV_transition_scan.csv
└── ONE SYSTEM ONLY (logistic map)

CLAIM 11 (domain-general)
├── phaseV_new_domains.csv (6 systems)
├── Threshold rule (m2_contrib cutoffs)
└── NOT full pipeline — threshold-only

CLAIM 12 (Class 2 most coherent)
├── transition_distances.csv
└── CONFLATES within-class with inter-class distance
```

---

## 3. CLAIM CLASSIFICATION SUMMARY

| # | Claim | Rating | Basis |
|---|-------|--------|-------|
| 1 | Geometry non-uniform | **COMPUTED** | Directly verified from pc1_variance column |
| 2 | Three classes exist | **INFERRED** | Cluster assignments computed, but number of classes is interpretive. k-means disagrees on 21%. |
| 3 | m2_contrib primary discriminator | **INFERRED** | 7/14 have measured data, 7 imputed zeros. 3 other features have higher single-feature ARI. |
| 4 | (m2, PC1) minimal sufficient pair | **INFERRED** | Actually (abl_no_m2_pc1, pc1) not (m2_contrib, pc1). ARI=0.64 but 6+ pairs outperform. Claim of "minimal sufficient" is incorrect. |
| 5 | Class 2 = interacting structure | **INTERPRETIVE** | Post-hoc label. No interaction feature in pipeline. Correlation, not causation. |
| 6 | Class 2 cannot be fabricated | **COMPUTED** | 7 α values, all positive m2_contrib. Direct verification. |
| 7 | Temporal order not fundamental | **COMPUTED** | Phase-scrambled Lorenz retains negative m2_contrib. |
| 8 | Class 1 = ordered/structural | **INTERPRETIVE** | Determinism confound unresolved. m2_contrib imputed for 4/6. |
| 9 | Class 3 = m2-driven/spectral | **INTERPRETIVE** | Tautological (class defined by m2_contrib > 0). Most heterogeneous class. |
| 10 | m2 tracks reorganization | **COMPUTED** | Logistic scan verified. Derivative magnitude unstable (2.7× across pipeline stages). |
| 11 | Partial domain generality | **COMPUTED** | 6 new systems. Threshold-only. ca_rule110 boundary inconsistent. |
| 12 | Class 2 most coherent | **COMPUTED (error)** | Within-class distance is LARGER than Class 1. Claim misstates "most separated" as "most coherent." |

---

## 4. WHAT SURVIVES THIS AUDIT

### Verified from raw data (survives)
1. PC1 values vary across 14 systems (range 0.507–0.954) — **non-uniformity confirmed**
2. 3 cluster assignments exist in the 17-feature pipeline — **but number depends on cut height**
3. m2_contribution varies from -0.378 to +0.252 — **for the 7 measured systems**
4. Noise+recurrence produces only Class 3 — **all α give m2_contrib > 0.05**
5. Phase-scrambled Lorenz stays Class 2 — **m2_contrib = -0.215**
6. Logistic m2_contrib oscillates with r — **derivative peaks at transitions**
7. 6 new domain systems classified via threshold — **but ca_rule110 boundary is inconsistent**

### Corrected (survives with revisions)
1. "(m2_contrib, PC1) is minimal sufficient" → REVISED: "(abl_no_m2_pc1, pc1) achieves ARI=0.64 but is NOT the best 2-feature pair. 6+ pairs outperform it. The pair is NOT (m2_contrib, pc1) as stated."
2. "m2_only ARI = 0.07" → REVISED: "abl_no_m2_pc1 alone gives ARI=0.07. m2_contribution alone gives ARI=0.29. These were conflated."
3. "Class 2 most coherent" → REVISED: "Class 2 has highest separation from other classes. Class 1 has tighter within-class distances."
4. "m2_contribution primary discriminator" → REVISED: "m2_contribution is necessary for class structure but 3 other features have higher single-feature ARI."

### Not supported (removed or downgraded)
1. "m2_contribution is the primary discriminative order parameter" — not supported by single-feature ARI ranking (6th best)
2. "m2_contribution thresholds define classes" — 7/14 systems have imputed values, not measured
3. "(m2_contrib, PC1) is minimal sufficient" — false claim; it's (abl_no_m2_pc1, pc1) and it's not minimal
4. "Class 2 most coherent" — false; Class 1 has tighter within-class clustering

### Requires pipeline verification (unresolved)
1. Per-point silhouette values (all 14 show same global average — may be a bug)
2. Derivative computation consistency (2.7× discrepancy between summary and scan)
3. Dendrogram cut height documentation (no file records the elbow analysis)
4. 7 systems with imputed m2_contrib = 0 (would computed values change class assignments?)
5. Determinism confound for Class 1 (no noise-added test performed)
6. k-means vs hierarchical disagreement on 3/14 systems (21%)

---

## 5. OPEN VERIFICATION ITEMS (from pipeline, not from raw data)

These cannot be verified from the CSV output files and require source code inspection:

1. **PCA implementation**: sklearn PCA default settings. Whether the 400×4 matrix is centered (sklearn default = centered) affects PC1 values. Confirm centering.

2. **z-score normalization**: Whether the 14×17 feature matrix was z-scored per column or globally. Different implementations change clustering.

3. **Ward linkage on z-scored data**: Euclidean distance after z-scoring is equivalent to correlation distance. Whether this was intended.

4. **Seed sensitivity**: reproducibility_manifest.md claims seed affects k-means assignment for 3 systems (lorenz, ising, RD). These are the EXACT 3 that disagree between hier and k-means. Verify.

5. **Dendrogram cutoff**: The elbow criterion for k=3 vs k=2 or k=4. No file documents the dendrogram or the cutoff logic.

6. **Phase-scrambling implementation**: FFT → randomize phases → IFFT. Whether the randomization preserves conjugate symmetry (ensuring real-valued output). Bug here would produce complex output.

7. **Noise+recurrence construction**: Whether `noise * (1-α) + logistic * α` or `noise * sqrt(1-α²) + logistic * α` (power-preserving). Different mixing affects m2_contrib.

---

## 6. FILES USED IN THIS AUDIT

| File | Contents | Status |
|------|----------|--------|
| cross_domain_reproducibility.csv | PC1, PC2, effective_rank, τ_axis per system | VERIFIED — 14 rows, all columns populated |
| clustering_feature_matrix.csv | 17-feature matrix for clustering | VERIFIED — 14 rows, 17 columns, 7 with 0.0 in ablation |
| clustering_results.csv | hier/km cluster assignments, silhouette | SILHOUETTE constant across rows (unexplained) |
| class_stability_report.csv | ARI under feature removal | VERIFIED — 6 tests |
| class_semantics.csv | System-cluster mapping | VERIFIED — matches clustering_results |
| classifier_transfer_report.csv | Cross-view transfer accuracy | VERIFIED — 2 transfers |
| minimal_basis_report.csv | All 1/2/3-feature subset ARIs | VERIFIED — 834 rows |
| metric_ablation_results.csv | PC1 by ablation for 9 systems | VERIFIED — 9 systems, 8 ablations each |
| null_audit_ood.csv | Temporal/phase correlations, PC1 ratio | VERIFIED — 14 systems |
| replay_stability_ood.csv | Replay idempotence, displacement | VERIFIED — all systems idempotent |
| tau_alignment_matrix.csv | Pairwise τ-axis cosine similarity | VERIFIED — 91 pairs |
| transition_distances.csv | 14×14 Euclidean distance matrix | VERIFIED — 196 cells |
| phaseV_adversarial.csv | noise+recurrence and phase-scramble | VERIFIED — 8 systems |
| phaseV_perturbation.csv | Logistic sweep r ∈ [3.5, 4.0] | VERIFIED — 26 r values |
| phaseV_new_domains.csv | 6 new domain systems | VERIFIED — 6 systems |
| phaseV_order_reduction.csv | (m2, PC1) reduction test | VERIFIED — 4 tests |
| phaseV_scale_stability.csv | m2 at different scales | VERIFIED — 34 entries |
| phaseV_metric_swaps.csv | Causal swap test | VERIFIED — causal test failed (PC1=0) |
| phaseV_transition_scan.csv | High-res logistic derivative | VERIFIED — 20 transitions |

---

## 7. SUMMARY: WHAT THIS AUDIT CHANGES

**Confidence ratings after audit**:

| # | Original | Audit | Reason |
|---|----------|-------|--------|
| 1 | HIGH | HIGH | Unchanged — directly computed from raw data |
| 2 | MODERATE | LOW | k-means disagrees on 21%. Silhouette constant rows unexplained. |
| 3 | MODERATE | LOW | "Primary" contradicted by ARI ranking. 50% data imputed as zeros. |
| 4 | MODERATE | **UNSUPPORTED** | Used wrong feature (abl_no_m2_pc1 ≠ m2_contrib). Not the best pair (6+ outperform). |
| 5 | LOW | LOW | Unchanged — properly rated as interpretive |
| 6 | MODERATE | MODERATE | Unchanged — directly computed. One recurrence type limitation recognized. |
| 7 | HIGH | HIGH | Unchanged — directly computed |
| 8 | MODERATE | LOW | Determinism confound unresolvable. 4/6 m2_contrib imputed. |
| 9 | LOW | LOW | Unchanged — properly rated as heterogeneous/interpretive |
| 10 | MODERATE | MODERATE | Unchanged — one-system limitation recognized. Derivative instability new finding. |
| 11 | LOW | LOW | Unchanged — threshold-only method limitation. Boundary inconsistency flagged. |
| 12 | MODERATE | **UNSUPPORTED** | Claim is factually incorrect. Class 1 has tighter within-class distances. |

**After audit: 2 HIGH, 0 MODERATE, 6 LOW, 2 UNSUPPORTED, 2 unchanged**
