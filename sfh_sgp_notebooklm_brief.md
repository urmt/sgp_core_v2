# SFH-SGP: A Self-Correcting Empirical Investigation of Organizational Geometry

## Narrative Brief for Deep Discussion

---

### 1. Origin & Initial Hypothesis

The SFH-SGP framework proposed that *canonical organizational transforms* (identity, reverse, replay, swap_halves, scale, clip, dropout, noise) applied to generative systems produce low-dimensional displacement patterns in a 4-metric space (signed ordinal flow, half-correlation, signed compressibility, amplitude transition asymmetry). The initial aspiration — stated explicitly in the SystemsAnalysis spec — was to test whether this constitutes a form of "universal organizational geometry."

### 2. What Failed / Corrected

**Universality claim → refuted.** Cross-domain OOD testing (14 systems across arithmetic, dynamical, symbolic, and random domains) showed two distinct τ-axis geometry classes, not one universal manifold. Cross-category alignment (ARI=0.27) is moderate — classes do not reduce to domain labels.

**Metric artifact discovered.** IID Gaussian noise produces PC1=0.9287 in transform space. The metric construction itself imposes low-rank structure on any input. Single-metric PC1 is identically 1.0 for all systems — a mathematical triviality of 1D metric space, not structure.

**"Temporal ordering is fundamental" → weakened.** Phase-scrambled Lorenz (power spectrum preserved, temporal sequence destroyed) retains its Class 2 geometry signature. The discriminating information is not chronology.

**Simplified metrics superseded.** V2 metrics produced artificially high PC1 (sine_wave PC1=0.996). Canonical V2_079 metrics corrected this to PC1=0.897 and correctly classified sine_wave as degenerate (duplicate state collapse + degenerate dimension).

### 3. What Survived

**Transform-space organization exists.** Across 14 OOD systems, mean non-control PC1=0.83. Transform displacements are consistently low-dimensional. This is partially metric construction but not reducible to it.

**m2_half_corr functions as a differential structure probe.** The central discovery: m2 contributes dimensionality **oppositely** for:
- Noise/recurrent systems: m2 adds 1D structure (positive contribution)
- Interacting nonlinear systems: m2 adds dimensionality (negative contribution)

This differential behavior survives adversarial testing — you cannot fabricate Class 2 (negative m2_contrib) from noise + engineered recurrence.

**Three organizational geometry classes appear separable:**

| Class | Members | Signature |
|-------|---------|-----------|
| 1 — Ordered/structural | primes, fibonacci, modular, cfg_expansion, lambda, rewrite | Balanced metrics, shuffle-destroyable, ordered or monotonic |
| 2 — Interacting nonlinear | **Lorenz, Ising, reaction-diffusion, Rule 184 CA** | Negative m2_contrib, lower PC1, higher effective rank |
| 3 — Recurrent/m2-driven | additive_recurrence, logistic_map, henon_map, iid_gaussian, colored_noise | Positive m2_contrib, high PC1, noise collapses here |

**Class 2 is NOT "chaos"** — it includes Rule 184 (coherent transport, not chaos). The shared feature across Class 2 members is *propagating interacting structure*: systems where localized entities move, interact, and produce long-range correlations.

**A paired order parameter (m2_contrib, PC1) tracks transitions between classes.** m2_contrib is necessary but not sufficient for class recovery; PC1 is its essential companion. Together they achieve 0.64 class recovery vs. 0.07 for either alone.

**Cross-metric transfer succeeds.** Classes trained on one metric view predict held-out metric views at 0.78–0.93 accuracy — the class structure is not an artifact of a specific metric subset.

**Transition behavior approximates organizational phase transitions.** The logistic map, scanned from r=3.5 to r=4.0, shows m2_contrib oscillating between +0.30 and -0.34 with |d(contrib)/dr| reaching 55 at transition boundaries. m2_contrib tracks structural reorganization, not monotonic drift.

**Adversarial synthetic test:** covariance-matched synthetic data clusters at silhouette=0.28 vs. real data at 0.35 (ratio 1.26×). Real clustering is modestly but consistently better.

### 4. Current Best Claims

1. **Canonical organizational transforms produce structured metric displacements** on any input. PC1 > 0.8 for 12/14 systems. This is partially a property of the transform-metric pairing.

2. **m2_contribution is a necessary order parameter** for organizational geometry. It separates interacting nonlinear systems from recurrent/noise-collapse systems. It is transition-sensitive, not reducible to chronology, and not fabricable from noise+recurrence.

3. **Three organizational geometry phases exist** with identifiable signatures. Class membership is partially transferable across metric views and partially stable under perturbation.

4. **Propagating interacting structure** is the most consistent empirical correlate of Class 2, not chaos or high dimensionality per se.

5. **The paired coordinate (m2_contrib, PC1)** is the minimal sufficient basis for class recovery.

### 5. What Remains Unsupported

- Universal mathematical ontology
- Symbolic computation emergence
- "Logic creates reality" claims
- Universal algebra or continuity equation
- Consciousness or self-proving mathematics
- Any claim stronger than "reusable measurement-conditioned geometry classes"

### 6. Next Phase: Consolidation

The program must now **stop expanding, start consolidating**:
- Independent clean-room reimplementation
- Metric-definition freeze
- Reproducibility package with all CSVs, scripts, and parameters
- Minimal formal model of the (m2, PC1) order parameter space
- External benchmark datasets for blind classification
- Statistical power analysis on class separability
- Only after consolidation: broader theoretical interpretation

### 7. Output Artifacts (all in sfh_sgp_ood_outputs/)

- `final_universality_assessment.md` — Final v4+v5 synthesized assessment
- `phaseU_summary.md` — Clustering, stability, transfer, minimal basis, adversarial, transitions
- `phaseV_summary.md` — Perturbation, metric swaps, new domains, order reduction, adversarial engineering, scale stability
- `metric_ablation_summary.md` — Per-system metric dominance analysis
- `adversarial_artifact_report.json` — Covariance-matched synthetic cluster comparison
- 25+ CSV/JSON data files with raw measurements

### 8. Key Open Questions for Discussion

1. Is Class 2 genuinely about *propagating interacting structure*, or is there a more parsimonious explanation?
2. The m2 + PC1 pair achieves 0.64 class recovery. What third feature closes the gap to 1.0?
3. Why does phase-scrambled Lorenz preserve Class 2? What spectral/interactional invariant survives temporal destruction?
4. The logistic map derivative (|d(contrib)/dr| = 55) — is this a genuine organizational phase transition or a metric artifact of the bifurcation structure?
5. What is the formal relationship between m2_contribution and established complexity measures (Lyapunov exponent, mutual information, statistical complexity)?
6. Class 3 contains both deterministic chaotic maps and IID noise — what distinguishes them within the class?
7. Is Minimal basis (3 features → 1.0 agreement) robust under cross-validation, or is it overfit to 14 systems?
8. Can Rule 184's Class 2 membership be predicted from its known analytical properties (density, current, fundamental diagram)?
