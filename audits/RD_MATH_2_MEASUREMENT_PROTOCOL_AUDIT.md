# RD-MATH.2 — Measurement Protocol Audit

**Date:** 2026-06-15
**Auditor:** OpenCode
**Trigger:** Research Director directive — "What would an actual experiment for measuring C, F, I, and Ψ look like?"

---

## Standing Constraints

- No theory generation
- No survivor promotion
- No ontology creation
- Design measurement protocols only

---

## Purpose

For each variable (C, F, I, Ψ), design a concrete measurement protocol:

- System
- Measurement procedure
- Observable
- Noise sources
- Observer assumptions
- Failure modes
- Expected range

For Ψ: do not assume measurement is possible. Ask: what observations would count as evidence for or against operationalization?

---

## Existing Measurement Infrastructure

The project already has working implementations for some metrics. This audit builds on them, not replaces them.

| Metric | Implementation | File | Status |
|--------|---------------|------|--------|
| C (normalized total correlation) | `compute_C(X, estimator)` | `coherence-benchmark/metrics/total_correlation.py` | Operational. Gaussian, KNN, KSG estimators. CI via bootstrap. |
| C_σ (statistical complexity) | `compute_statistical_complexity(X, tau)` | `coherence-benchmark/metrics/statistical_complexity.py` | Operational. H(X) − I_pred. |
| I_pred (predictive information) | `compute_predictive_information(X, tau, k)` | `coherence-benchmark/metrics/predictive_information.py` | Operational. KSG mutual information estimator. |
| TE (transfer entropy) | `compute_transfer_entropy_matrix(X, tau, k)` | `coherence-benchmark/metrics/transfer_entropy.py` | Operational. Pairwise directed information flow. |
| MSE (multiscale entropy) | `compute_mse(X, scales)` | `coherence-benchmark/metrics/multiscale_entropy.py` | Operational. |
| C ≈ −MSE | r = −0.89 | RD-019 (RD-DIAG.1) | Known relationship. Domain-specific. |

**Key finding from infrastructure:** C is already measurable in the granular simulation domain. The question is not "can we measure C?" but "does what we measure as C correspond to coherence-of-parts-in-assembly?"

---

## Variable 1: C — Coherence

### 1.1 System

**Primary system:** Granular bed simulation (50 grains, soft-sphere dynamics, gravity, friction parameter ∈ {0.05, 0.1, 0.2, 0.4, 0.6, 0.8}).

**Why this system:** It is the only system where C has been measured with known ground truth (friction controls dynamics) and where C ≈ −MSE has been validated (RD-019, r = −0.89).

**Boundary conditions:**
- 50 grains with radii ∈ [0.8, 1.5], masses = radii²
- Box width = 40.0, gravity = −1.0
- 1000 time steps, perturbation at step 500 (remove 10% of grains)
- Binning: 10 spatial bins from x-position ordering
- C measured on binned time series via `compute_C(X, "gaussian")`

### 1.2 Measurement Procedure

```
Step 1: Initialize granular bed
  - Draw radii from Uniform(0.8, 1.5), compute masses
  - Position grains randomly in box [2, 38] × [5, 30]
  - Initialize velocities from Uniform(−0.5, 0.5)

Step 2: Simulate dynamics (1000 steps, dt = 0.01)
  - At each step: compute pairwise soft-sphere forces
  - Apply gravity, damping, friction
  - Record positions and velocities for all grains

Step 3: Apply perturbation at step 500
  - Remove 10% of grains (random selection)

Step 4: Bin spatial data
  - Sort grains by final x-position
  - Split into 10 equal bins
  - For each bin: average y-position over grains in bin at each time step
  - Result: 10-component time series, 1000 time points

Step 5: Compute C
  - Window: sliding window of 75 steps, stride 25
  - For each window: compute_C(X_window, "gaussian")
  - Result: time series of C values

Step 6: Extract summary statistics
  - pre_C: mean C over [100, 500) (pre-perturbation)
  - dip: pre_C − min(C over [500, 600])
  - restoration: C_final / pre_C (post-perturbation recovery)
  - tau_rec: time to first C ≥ pre_C after perturbation
```

### 1.3 Observable

**Primary observable:** C ∈ [0, 1], the normalized total correlation of the binned spatial time series.

**Mathematical definition:**
```
C = T(X₁; ...; Xₙ) / (T(X₁; ...; Xₙ) + Σᵢ H(Xᵢ))
```
where T is total correlation (multi-information) and H(Xᵢ) is marginal entropy of component i.

**What this actually measures:**
- The fraction of total entropy that is shared across components
- C = 0: components are independent (no coordination)
- C = 1: components are perfectly redundant (maximum coordination)
- C ≈ 0.5: components share一半 their entropy

**Proxy relationship:** C ≈ −MSE (r = −0.89). Multiscale entropy measures signal complexity; high complexity = low coherence.

### 1.4 Noise Sources

| Source | Type | Magnitude | Mitigation |
|--------|------|-----------|------------|
| Gaussian estimator bias | Systematic | C is lower bound for non-Gaussian data | Use KSG estimator for comparison; report estimator sensitivity |
| Finite sample size (T = 75 per window) | Statistical | Bootstrap CI width ≈ ±0.05 | Increase window size; report CIs |
| Binning choice (10 bins) | Structural | Unknown; bins are spatial, not functional | Test sensitivity: vary n_bins ∈ {5, 10, 20, 50} |
| Grain removal randomness | Stochastic | Different seeds produce different C trajectories | Average over replicates (n = 10 per friction level) |
| Gaussian copula assumption | Model | Underestimates C for nonlinear dependencies | Compare gaussian vs KSG estimators |
| Time non-stationarity | Structural | C measured over sliding windows assumes local stationarity | Test window size sensitivity: ∈ {25, 50, 75, 150} |

### 1.5 Observer Assumptions

1. **Spatial binning captures relevant structure.** The 10-bin decomposition by x-position is assumed to reflect the system's functional organization. This is arbitrary — different binning strategies could yield different C values.

2. **Gaussian entropy is a valid estimator.** The Gaussian copula assumes the data's dependence structure is captured by the correlation matrix. For nonlinear systems, this is a lower bound.

3. **C measures a property of the system, not the measurement.** RD-020 found that removing structural hubs did not degrade C (p = 0.09). This raises the question: does C measure the granular bed's coherence, or the coherence of the binned representation?

4. **Total correlation is the right information-theoretic measure for "parts fitting together."** Alternatives exist: dual total correlation, co-information, integration information (Φ). These measure different aspects of multi-variable dependence.

5. **The sliding window is short enough to capture dynamics but long enough for reliable estimation.** T = 75 at dt = 0.01 gives 0.75 time units of observation. If the system's characteristic timescale is longer, the window may be too short.

### 1.6 Failure Modes

| Mode | Description | Detection | Consequence |
|------|-------------|-----------|-------------|
| **Estimator collapse** | All friction levels produce similar C | Low variance across friction levels | C does not discriminate regimes |
| **MSE collapse** | C ≈ −MSE is a mathematical identity, not a physical relationship | C and MSE are perfectly correlated (r ≈ −1.0) | C adds no information beyond MSE |
| **Binning artifact** | C is determined by binning, not by grain dynamics | C is invariant to grain rearrangement within bins | C measures representation, not physics |
| **Window size dependency** | C changes qualitatively with window size | Different window sizes produce different rank orderings of friction levels | C is not scale-free |
| **Non-stationarity violation** | C changes systematically within windows | C shows trend within windows | Sliding window assumption violated |
| **Perturbation insensitivity** | C dip is identical across friction levels | No relationship between friction and dip magnitude | C does not capture resilience |

### 1.7 Expected Range

Based on existing data (60 runs: 6 friction levels × 10 replicates):

| Parameter | Expected Range | Notes |
|-----------|---------------|-------|
| pre_C | 0.3 – 0.9 | Higher friction → higher C (less mobility → more coordination) |
| dip | 0.01 – 0.15 | Larger dip for lower friction (more mobility → bigger disruption) |
| restoration | 0.85 – 1.05 | Most systems recover to ≥80% of pre-C |
| tau_rec | 50 – 400 steps | Faster recovery for higher friction |

**Empirical check:** The T901 ensemble (t901_analysis.py) produces these values. The protocol should reproduce them.

### 1.8 Protocol Validation Tests

1. **Estimator comparison:** Compute C with gaussian, knn, and ksg estimators on the same data. Report rank-ordering consistency.
2. **Binning sensitivity:** Vary n_bins ∈ {5, 10, 20, 50}. Report whether rank ordering of friction levels is preserved.
3. **Window size sensitivity:** Vary window ∈ {25, 50, 75, 150}. Report whether dip magnitude is preserved.
4. **Replicate stability:** For each friction level, report CV (coefficient of variation) of pre_C across 10 replicates.
5. **MSE comparison:** Compute both C and MSE for all runs. Report r² and whether C adds predictive power beyond MSE for recovery prediction.

---

## Variable 2: F — Fertility

### 2.1 System

**Primary system:** Same granular bed simulation as C, but measured on post-perturbation dynamics.

**Why this system:** F measures "capacity to enable further coherent experience." In the granular context, this is the system's capacity to generate new dynamical states after perturbation. The perturbation at step 500 creates a natural test: does the system have the capacity to reorganize?

**Boundary conditions:** Same as C (Section 1.1).

### 2.2 Measurement Procedure

```
Step 1: Run granular simulation (same as C protocol, steps 1-3)

Step 2: Compute F proxies from post-perturbation dynamics

  Proxy A: Transfer Entropy (TE)
    - Compute transfer entropy matrix on binned data, post-perturbation [500, 1000]
    - F_TE = mean of all off-diagonal TE values
    - Interpretation: average directed information flow between bins
    - High F_TE → bins enable future states of other bins → fertile

  Proxy B: Empowerment (E)
    - Define "actions" as bin-level velocity changes
    - Define "sensors" as bin-level position changes at lag τ = 10
    - Compute channel capacity: E = max_{P(A)} I(A; S_{t+τ})
    - Approximate via: E ≈ mean mutual information between velocity changes and future position changes
    - High E → system can generate diverse future states through its own dynamics → fertile

  Proxy C: Novelty Rate (NR)
    - Track binned time series after perturbation
    - At each time step t, compute distance to nearest neighbor in history (last 200 steps)
    - NR = fraction of steps where distance > threshold (median distance in pre-perturbation)
    - High NR → system generates states it hasn't visited before → fertile

  Proxy D: Ecological Interaction Count (EIC)
    - Define "interaction" as: two bins have correlated velocity changes (|ρ| > 0.3) at time t
    - Count distinct interaction types over post-perturbation window
    - EIC = number of bin pairs with significant correlation / total possible pairs
    - High EIC → many interaction types → fertile

Step 3: Combine into composite F score
  - Normalize each proxy to [0, 1]
  - F_composite = mean(F_TE, F_E, F_NR, F_EIC)
```

### 2.3 Observable

**Primary observables (four independent proxies):**

| Proxy | What it measures | Units | Range |
|-------|-----------------|-------|-------|
| F_TE | Directed information flow between components | nats | [0, ∞) |
| F_E | Channel capacity between actions and future states | nats | [0, ∞) |
| F_NR | Rate of visiting novel states | fraction | [0, 1] |
| F_EIC | Diversity of interaction types | ratio | [0, 1] |

**Composite:** F_composite ∈ [0, 1] (after normalization).

**What this actually measures:**
- F_TE: How much one part of the system enables future states of another part
- F_E: How much the system can generate diverse future states through its own dynamics
- F_NR: How often the system visits states it hasn't visited before
- F_EIC: How many different types of interactions the system supports

### 2.4 Noise Sources

| Source | Type | Magnitude | Mitigation |
|--------|------|-----------|------------|
| TE estimator bias (KSG) | Systematic | Underestimates for high-dimensional systems | Use low-dimensional binned representation (d = 10) |
| Empowerment approximation | Structural | True channel capacity requires optimization over action distributions; we approximate with MI | Report as lower bound |
| Novelty threshold choice | Subjective | Different thresholds → different NR values | Use adaptive threshold (median pre-perturbation distance) |
| Interaction definition (|ρ| > 0.3) | Arbitrary | Different cutoffs → different EIC | Test sensitivity: ρ ∈ {0.1, 0.2, 0.3, 0.4, 0.5} |
| Finite time series (500 post-perturbation steps) | Statistical | May not capture long-term fertility | Extend simulation if possible |
| Narrow-focus problem | Structural | All four proxies measure process-internal generativity, not relational or experiential fertility | Acknowledge limitation; this is a known gap (METRIC.2) |

### 2.5 Observer Assumptions

1. **Transfer entropy measures "enabling further experience."** TE(Y→X) measures how much Y's past reduces uncertainty about X's future. This is a specific, narrow interpretation of "enabling." It does not capture the quality or coherence of what is enabled.

2. **Empowerment can be approximated by mutual information.** True empowerment requires maximizing over action distributions. We approximate by using the system's natural action distribution. This is a lower bound.

3. **Novelty rate measures generativity.** A system that visits novel states is generating new experience. But novelty without structure is noise. F_NR does not require coherence of novelty.

4. **Ecological interaction count measures fertility of interactions.** More interaction types = more fertile. But interactions can be destructive (competition) as well as constructive (mutualism). EIC counts all interactions equally.

5. **The composite F score weights all four proxies equally.** This is arbitrary. Different applications may require different weightings.

6. **F is measured post-perturbation.** F measures capacity *after* disruption, not *during* steady state. This is a design choice: fertility is the capacity to reorganize, not the capacity to persist.

### 2.6 Failure Modes

| Mode | Description | Detection | Consequence |
|------|-------------|-----------|-------------|
| **TE floor** | All runs produce TE ≈ 0 (bins are independent) | Mean TE < 0.01 nats | Binned representation destroys directed coupling |
| **Empowerment saturation** | All runs produce similar E | Low variance across friction levels | E does not discriminate fertility |
| **Novelty ceiling** | NR ≈ 1 for all runs (everything is novel after perturbation) | NR is not informative | Perturbation is too large; system never recovers to familiar states |
| **EIC collapse** | EIC is determined by bin count, not dynamics | EIC ≈ constant across friction levels | Interaction definition is trivial |
| **Proxy disagreement** | Four proxies give different rank orderings of friction levels | Low inter-proxy correlation | F is not a single quantity; it decomposes into independent dimensions |
| **Narrow-focus collapse** | All four proxies are correlated with C (r > 0.8) | F_composite ≈ C | F does not add information beyond coherence |

### 2.7 Expected Range

| Proxy | Expected Range | Notes |
|-------|---------------|-------|
| F_TE | 0.01 – 0.5 nats | Higher for lower friction (more mobility → more information flow) |
| F_E | 0.1 – 2.0 nats | Higher for lower friction (more mobility → more empowerment) |
| F_NR | 0.1 – 0.8 | Higher for lower friction (more mobility → more novelty) |
| F_EIC | 0.05 – 0.4 | May be relatively stable across friction levels |
| F_composite | 0.1 – 0.7 | After normalization |

### 2.8 Protocol Validation Tests

1. **Proxy independence:** Compute correlation matrix of (F_TE, F_E, F_NR, F_EIC). If r > 0.8 for any pair, those proxies are redundant.
2. **C-F separation:** Compute correlation between F_composite and C. If r > 0.8, F collapses to C.
3. **Friction sensitivity:** Report rank correlation between friction level and each F proxy. F should be anti-correlated with friction (lower friction → higher fertility).
4. **Recovery prediction:** Does F_composite predict restoration (C_final / C_pre)? If not, F is not measuring "capacity to enable further coherent experience."
5. **Ecological validity:** Compare F_composite to the number of distinct dynamical regimes observed in the post-perturbation trajectory. Higher F should correspond to more regimes.

---

## Variable 3: I — Interaction

### 3.1 System

**Primary system:** Granular bed simulation, but with a modified observation protocol.

**Why this system:** I measures "the relational event — the actual happening where a structure and an observer/environment meet." In the granular context, interaction is the contact force between grains. But the project defines I more broadly: interaction is observation, and observation is primitive experience (Assumption B). This means I must be measured as a *relational event*, not as a property of either party alone.

**Boundary conditions:** Same as C (Section 1.1), plus:

- Define "observer" as a subset of grains that sense (compute forces from) other grains
- Define "target" as the remaining grains
- I is measured as the information flow from target to observer, conditioned on observer's own dynamics

### 3.2 Measurement Procedure

```
Step 1: Run granular simulation (same as C protocol, steps 1-3)

Step 2: Partition grains into observer and target
  - Observer: first 25 grains (by index)
  - Target: remaining 25 grains
  - This partition is arbitrary (see assumptions)

Step 3: Compute I proxies

  Proxy A: Conditional Transfer Entropy (CTE)
    - Compute TE(target → observer | observer_past)
    - CTE = TE(target → observer) − TE(target → observer | observer_past)
    - This isolates the *additional* information flow from target beyond observer's own prediction
    - High CTE → target's interaction with observer is informative → strong interaction event

  Proxy B: Integration Information (Φ approximation)
    - Compute total correlation of the full 10-bin system: TC_full
    - Compute total correlation of observer bins only: TC_obs
    - Compute total correlation of target bins only: TC_tgt
    - Φ_approx = TC_full − (TC_obs + TC_tgt)
    - High Φ_approx → whole system is more than sum of parts → genuine interaction
    - NOTE: This is NOT IIT's Φ. It is a total-correlation-based approximation.

  Proxy C: Information Transmission Rate (ITR)
    - At each time step, compute mutual information between target state at t and observer state at t+1
    - ITR = mean MI over post-perturbation window
    - High ITR → target reliably informs observer → sustained interaction

  Proxy D: Interaction Asymmetry (IA)
    - Compute TE(target → observer) and TE(observer → target)
    - IA = |TE(target → observer) − TE(observer → target)| / (TE(target → observer) + TE(observer → target) + ε)
    - IA ≈ 0: symmetric interaction (genuine exchange)
    - IA ≈ 1: asymmetric interaction (one-way influence)
    - For "genuine" interaction, expect IA ≈ 0

Step 4: Combine into composite I score
  - Normalize each proxy to [0, 1]
  - I_composite = mean(I_CTE, I_Φ, I_ITR, 1 − I_IA)
  - NOTE: 1 − I_IA rewards symmetric interaction
```

### 3.3 Observable

**Primary observables (four independent proxies):**

| Proxy | What it measures | Units | Range |
|-------|-----------------|-------|-------|
| I_CTE | Conditional transfer entropy (interaction beyond self-prediction) | nats | [0, ∞) |
| I_Φ | Integration (whole > sum of parts) | nats | [0, ∞) |
| I_ITR | Information transmission rate | nats/step | [0, ∞) |
| I_IA | Interaction asymmetry | ratio | [0, 1] |

**Composite:** I_composite ∈ [0, 1] (after normalization).

**What this actually measures:**
- I_CTE: The additional information that flows from target to observer beyond what observer predicts from its own past
- I_Φ: How much more correlated the full system is than the sum of its parts
- I_ITR: How reliably target states inform observer states
- I_IA: Whether interaction is symmetric (genuine exchange) or asymmetric (one-way influence)

### 3.4 Noise Sources

| Source | Type | Magnitude | Mitigation |
|--------|------|-----------|------------|
| Observer partition choice | Structural | Different partitions → different I values | Test 10 random partitions; report mean and variance |
| KSG estimator bias | Systematic | Underestimates MI for high dimensions | Use low-dimensional binned representation |
| Φ approximation | Structural | Total correlation ≠ IIT's Φ; this is a rough proxy | Acknowledge limitation; this is not a direct measure |
| Finite time series | Statistical | 500 post-perturbation steps may be insufficient | Extend simulation |
| Non-stationarity | Structural | I may change over time as system reorganizes | Use sliding window; report time course |
| I_CTE vs I_ITR redundancy | Statistical | Both measure information flow, may be correlated | Compute correlation; report if r > 0.8 |

### 3.5 Observer Assumptions

1. **The observer partition is arbitrary.** The project defines "anything capable of interaction is an observer at the instant of interaction." But to measure I, we must fix an observer. The choice of which grains are "observer" vs "target" is not determined by the system.

2. **Interaction is the same as information flow.** The project defines interaction as the relational event, which is broader than information transfer. But all four proxies measure information flow. This is a limitation.

3. **Integration (Φ) approximates "genuine interaction."** If the whole is more than the sum of parts, the parts are genuinely interacting. But total correlation is not integration information. The approximation is rough.

4. **Symmetric interaction is "better" than asymmetric.** The composite rewards IA ≈ 0. But some genuine interactions are asymmetric (e.g., a sensor observing a source). The assumption that symmetry = genuineness is not justified.

5. **I can be measured independently of C and F.** RD-MATH.1 identifies that I and Ψ may be the same variable (Assumption B: Interaction ≈ Observation ≈ Primitive Experience). If so, measuring I separately from Ψ may be circular.

6. **Observer and target are distinguishable.** The protocol assumes a clean partition. In reality, every grain is simultaneously observer and target. The partition is a measurement convenience, not a physical fact.

### 3.6 Failure Modes

| Mode | Description | Detection | Consequence |
|------|-------------|-----------|-------------|
| **Partition dependence** | I varies by >50% across random partitions | High variance across 10 random partitions | I is a property of the partition, not the system |
| **Φ ≈ 0** | Whole system is no more correlated than parts | I_Φ ≈ 0 for all runs | Total correlation decomposition is trivial; no genuine interaction |
| **IA ≈ 1 for all runs** | All interaction is asymmetric | I_IA > 0.8 for all friction levels | Observer and target are not in genuine exchange |
| **I ≈ C** | Interaction collapses to coherence | I_composite correlates with C at r > 0.8 | I adds no information beyond C |
| **I ≈ F** | Interaction collapses to fertility | I_composite correlates with F at r > 0.8 | I adds no information beyond F |
| **Information-theoretic ceiling** | All four proxies are information-theoretic measures, all fail for the same reason | All proxies are correlated | The information-theoretic vocabulary cannot capture interaction as defined |

### 3.7 Expected Range

| Proxy | Expected Range | Notes |
|-------|---------------|-------|
| I_CTE | 0.005 – 0.1 nats | Small because CTE is conditional on observer's own dynamics |
| I_Φ | 0.0 – 0.3 nats | May be near zero if system is nearly decomposable |
| I_ITR | 0.01 – 0.3 nats/step | Higher for lower friction (more coupling) |
| I_IA | 0.1 – 0.7 | Depends on partition; may be near 0.5 (symmetric) for random partitions |
| I_composite | 0.1 – 0.6 | After normalization |

### 3.8 Protocol Validation Tests

1. **Partition stability:** Run 10 random observer/target partitions. Report CV of I_composite. If CV > 0.3, I is partition-dependent.
2. **I-C separation:** Compute correlation between I_composite and C. If r > 0.8, I collapses to C.
3. **I-F separation:** Compute correlation between I_composite and F_composite. If r > 0.8, I collapses to F.
4. **Friction sensitivity:** Report rank correlation between friction and I. I should be anti-correlated with friction (lower friction → more interaction).
5. **Symmetry test:** For each friction level, report mean I_IA. If I_IA is consistently > 0.7, the observer-target partition creates artificial asymmetry.
6. **Temporal dynamics:** Plot I_composite over time (sliding window). If I shows no transient after perturbation, the relational event is not captured.

---

## Variable 4: Ψ — Experience

### 4.1 System

**Primary system:** Same granular bed simulation.

**Critical question:** Can Ψ be measured at all?

The project defines Ψ as "experiential quality — the intrinsic side of interaction" (RD-CALIBRATION.1). It takes experience as axiomatic (Assumption A: "Experience is present from the beginning"). If Ψ is intrinsic and first-person, then no third-person measurement can capture it directly.

**This protocol does not assume Ψ is measurable.** It designs observations that would count as evidence for or against operationalization.

### 4.2 Measurement Procedure

```
Step 1: Define candidate observables for Ψ

  Candidate A: Integrated Information (Φ_IIT)
    - Compute IIT's Φ (integration information) for the binned system
    - If Φ > 0, the system has irreducible causal power
    - If Φ = 0, the system is reducible to parts
    - NOTE: Φ_IIT is distinct from the Φ approximation in Section 3.
      Φ_IIT requires computing the cause-effect structure of the system.
      Implementation: use the binned time series to infer a binary model
      (above/below mean), then compute Φ via the standard IIT algorithm.
    - If Φ_IIT > 0 is necessary for Ψ, then Ψ is operationalizable.
    - If Φ_IIT = 0 for all systems that plausibly have Ψ, then Φ_IIT is not the right measure.

  Candidate B: Self-Model Compression (SMC)
    - Compute the mutual information between a system's state and its
      prediction of its own future state: I(X_t; X_{t+1})
    - High SMC → system has a good model of itself → candidate for self-experience
    - This is a proxy for "consciousness = stable self-interaction"
      (from ONTOLOGY_ASSUMPTIONS.md)
    - If SMC correlates with C and F but is not identical to either,
      it may capture something additional.

  Candidate C: Causal Density (ρ_c)
    - Compute the fraction of variable pairs with significant Granger
      causality: ρ_c = (number of significant TE pairs) / (total pairs)
    - High ρ_c → many causal interactions → candidate for "dense experience"
    - This measures the *density* of interaction, not its *quality*.

  Candidate D: Residual Entropy After Prediction (REAP)
    - Compute: REAP = H(X_t) − I(X_t; X_{t-1}) − I(X_t; X_{t-1}, X_{t-2})
    - This is the entropy that remains after accounting for first- and
      second-order prediction
    - High REAP → system has structure beyond what linear models capture
    - This is a candidate for "experience that exceeds prediction"

Step 2: Compute all four candidates for all 60 runs

Step 3: Test whether any candidate satisfies the following criteria:
  a) Varies across friction levels (discriminates regimes)
  b) Is not identical to C, F, or I (adds new information)
  c) Correlates with a phenomenological measure (see Section 4.3)
  d) Is reproducible across replicates (low CV)

Step 4: If no candidate satisfies all four criteria, Ψ is not operationalizable
  with current methods. Report this honestly.
```

### 4.3 The Phenomenological Bridge Problem

**The core issue:** Ψ is defined as first-person experience. No third-person metric can directly measure first-person experience. To bridge this gap, we need either:

**Option A: Correlation with behavioral report**
- In biological systems, subjects report their experience (e.g., "I see red")
- In granular systems, there is no subject to report
- **Verdict:** Not applicable to granular systems

**Option B: Correlation with functional signatures**
- Define Ψ operationally as: "whatever correlates with the system's capacity to integrate information, model itself, and adapt"
- This is the IIT / Global Workspace approach
- **Verdict:** This is a legitimate operationalization, but it defines Ψ functionally, not intrinsically. It measures the *functional correlates* of experience, not experience itself.

**Option C: Correlation with recovery dynamics**
- If Ψ ≈ f(C, F, I), then Ψ should predict recovery (C_final / C_pre)
- Test: does any candidate (Φ_IIT, SMC, ρ_c, REAP) predict recovery better than C, F, or I alone?
- If yes: the candidate captures something additional that contributes to "experienced value"
- If no: Ψ does not add information beyond its components
- **Verdict:** This is the most testable approach for the granular system.

**Option D: Cross-domain validation**
- Measure the same candidate (e.g., Φ_IIT) in multiple systems: granular bed, neural network, gene regulatory network, cellular automaton
- If Φ_IIT consistently predicts recovery across all systems, it is a candidate for Ψ
- If it only works in the granular system, it is domain-specific
- **Verdict:** Requires multiple systems; not feasible in current audit.

### 4.4 Observable

**Primary observables (four candidates):**

| Candidate | What it measures | Units | Range |
|-----------|-----------------|-------|-------|
| Φ_IIT | Integrated information (irreducible causal power) | bits | [0, ∞) |
| SMC | Self-model compression (self-prediction quality) | nats | [0, ∞) |
| ρ_c | Causal density (fraction of significant causal pairs) | ratio | [0, 1] |
| REAP | Residual entropy beyond second-order prediction | nats | [0, ∞) |

**What these actually measure (honestly):**

| Candidate | What it captures | What it does NOT capture |
|-----------|-----------------|-------------------------|
| Φ_IIT | Irreducible causal structure | Whether that structure is "experienced" |
| SMC | Self-prediction quality | Whether self-prediction constitutes self-awareness |
| ρ_c | Density of causal interactions | Quality or coherence of those interactions |
| REAP | Structure beyond linear prediction | Whether that structure is phenomenal |

**All four candidates measure functional correlates, not experience itself.** This is an honest assessment.

### 4.5 Noise Sources

| Source | Type | Magnitude | Mitigation |
|--------|------|-----------|------------|
| Φ_IIT computational intractability | Structural | Φ requires exponential computation over all partitions; approximate with binned system | Use approximation; acknowledge it is NOT true Φ_IIT |
| SMC non-stationarity | Statistical | Self-prediction quality changes over time | Use sliding window; report time course |
| ρ_c threshold sensitivity | Arbitrary | Different Granger causality thresholds → different ρ_c | Test sensitivity: p ∈ {0.01, 0.05, 0.10} |
| REAP model misspecification | Structural | Second-order linear model may not capture nonlinear structure | Use nonlinear models (e.g., kernel regression) |
| All candidates are observer-relative | Structural | Every candidate requires defining what counts as a "variable" and what counts as "prediction" | Acknowledge; this is a fundamental limitation |
| Experience may not be functional | Philosophical | If Ψ is not functional, no functional measure can capture it | Acknowledge; this is a hard boundary |

### 4.6 Observer Assumptions

1. **Ψ has functional correlates.** If Ψ is purely intrinsic with no functional consequences, then no measurement protocol can detect it. The protocol assumes Ψ has at least indirect functional signatures.

2. **Φ_IIT approximates experience.** IIT claims Φ > 0 is necessary and sufficient for consciousness. This is controversial. The protocol uses Φ_IIT as a candidate, not as ground truth.

3. **Self-prediction relates to self-experience.** SMC assumes that a system that models itself has something like self-experience. This is a strong philosophical assumption.

4. **Recovery prediction is a valid test.** If Ψ ≈ f(C, F, I), then Ψ should predict recovery. But the compass equation is untested. If Ψ is not a function of C, F, I, then recovery prediction is not a valid test.

5. **The granular system is a valid test bed.** The project assumes that principles discovered in granular systems generalize. This is untested.

6. **Third-person measurement of first-person phenomena is possible in principle.** This is the hard problem of consciousness. The protocol does not solve it; it designs observations that would count as evidence.

### 4.7 Failure Modes

| Mode | Description | Detection | Consequence |
|------|-------------|-----------|-------------|
| **All candidates = 0** | Φ_IIT, SMC, ρ_c, REAP are all zero or near-zero | All values < ε | Granular system has no candidate for Ψ; wrong test bed |
| **All candidates correlate perfectly with C** | r(Φ, C) > 0.9, r(SMC, C) > 0.9, etc. | High correlation with C | Ψ collapses to C; no independent experience measure |
| **No candidate predicts recovery** | None of the four candidates predicts restoration beyond C, F, I alone | ΔR² < 0.01 when adding candidate to C+F+I model | Ψ does not add information; compass equation may be wrong |
| **Candidates disagree on rank ordering** | Φ_IIT ranks friction levels differently than SMC | Low inter-candidate correlation | Ψ is not a single quantity; it decomposes into independent dimensions |
| **Φ_IIT is computationally intractable** | Cannot compute Φ_IIT for 10-bin system in reasonable time | Runtime > 1 hour per run | Use approximation; acknowledge it is not true Φ |
| **Philosophical dead end** | No functional correlate can bridge to phenomenal experience | All candidates fail all four criteria | Ψ is not operationalizable with current methods. Report this. |

### 4.8 Expected Range

| Candidate | Expected Range | Notes |
|-----------|---------------|-------|
| Φ_IIT (approximate) | 0.0 – 0.5 bits | May be zero for decomposable systems |
| SMC | 0.1 – 2.0 nats | Higher for more predictable systems |
| ρ_c | 0.0 – 0.3 | Depends on Granger causality threshold |
| REAP | 0.01 – 0.5 nats | Higher for more complex systems |

**Honest expectation:** At least some candidates will fail. The protocol is designed to determine *which* candidates fail and *how*, not to guarantee success.

### 4.9 Evidence Criteria

**Evidence FOR operationalization:**
1. At least one candidate satisfies all four criteria (Section 4.2, Step 3)
2. The candidate adds predictive power beyond C, F, I alone (ΔR² > 0.05 for recovery prediction)
3. The candidate is reproducible across replicates (CV < 0.3)
4. The candidate discriminates friction levels (rank correlation |ρ| > 0.5)

**Evidence AGAINST operationalization:**
1. No candidate satisfies all four criteria
2. All candidates are identical to C, F, or I (r > 0.9)
3. No candidate adds predictive power beyond C, F, I
4. All candidates are unstable across replicates (CV > 0.5)

**Honest conclusion if evidence is against:** Ψ is not operationalizable in the granular system with current methods. This does not mean Ψ does not exist; it means third-person measurement cannot capture it in this domain. The protocol should report this as a finding, not a failure.

---

## Cross-Variable Protocol Summary

### Measurement Dependencies

```
C ← measurable independently (total correlation of binned time series)
F ← requires C (fertility is capacity to enable further coherent experience; "coherent" references C)
I ← requires C and F (interaction is the relational event between coherent structures)
Ψ ← requires C, F, and I (experience is the intrinsic side of interaction)
```

**If C is mismeasured, all downstream variables are mismeasured.** The protocol must validate C first.

### Composite Protocol

| Step | Variable | Metric | Validation |
|------|----------|--------|------------|
| 1 | C | compute_C(X, "gaussian") | Estimator comparison, binning sensitivity |
| 2 | F | F_composite(F_TE, F_E, F_NR, F_EIC) | Proxy independence, C-F separation |
| 3 | I | I_composite(I_CTE, I_Φ, I_ITR, I_IA) | Partition stability, I-C separation |
| 4 | Ψ | Candidate selection (Φ_IIT, SMC, ρ_c, REAP) | Recovery prediction, cross-candidate agreement |

### What This Protocol Can and Cannot Do

**CAN:**
- Measure C with known estimator properties and bootstrap CIs
- Measure F as four independent proxies of process-internal generativity
- Measure I as four independent proxies of relational information flow
- Test whether Ψ has functional correlates in the granular system
- Determine whether Ψ adds information beyond C, F, I

**CANNOT:**
- Measure Ψ as intrinsic experience (the hard problem)
- Determine whether C measures "coherence-of-parts-in-assembly" or "coherence-of-binned-representation"
- Determine whether the observer-target partition for I is physically meaningful
- Bridge the gap between third-person measurement and first-person experience
- Validate that the compass equation Ψ ≈ f(C, F, I) has the right functional form

### Recommended Next Steps

1. **Run the C validation tests** (Section 1.8) to establish measurement reliability
2. **Run the F proxy independence test** (Section 2.8) to determine if F is one quantity or four
3. **Run the I partition stability test** (Section 3.8) to determine if I is observer-dependent
4. **Run the Ψ evidence criteria** (Section 4.9) to determine if operationalization is possible
5. **If all variables pass validation**, compute the compass equation Ψ ≈ f(C, F, I) and test it against recovery
6. **If any variable fails**, report the failure honestly and determine whether the failure is in the measurement or in the concept

---

## Artifact

`/home/student/sgp_core_v2/audits/RD_MATH_2_MEASUREMENT_PROTOCOL_AUDIT.md`
