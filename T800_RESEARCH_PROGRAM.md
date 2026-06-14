# T800 — Research Program: Universal Coherence Metric

**Status:** Research program proposal
**Objective:** Construct a single formally defined coherence metric C from SFH-SGP's surviving axioms (A3 + A6) and demonstrate it predicts system persistence/adaptivity across physical, biological, cognitive, and social domains — outperforming existing complexity measures.

---

## Phase 1 — Metric Construction

### 1.1 Formal Definition of C

Let a system S be composed of n components {x₁ ... xₙ} with joint states described by random variables {X₁ ... Xₙ} with joint distribution P(X₁...Xₙ).

Define:

**C(S) = T(X₁; ... ; Xₙ) / H(X₁...Xₙ)**

where T is the **total correlation** (multi-information):

T(X₁; ... ; Xₙ) = Σᵢ H(Xᵢ) − H(X₁...Xₙ)

and H(X₁...Xₙ) is the joint entropy (normalizer, bounds C to [0,1]).

**Intuition:** C measures what fraction of the system's total statistical structure is irreducible to parts. If all components are independent, C = 0. If the whole completely determines the parts, C = 1.

**Why total correlation:**
- Defined entirely on state distributions (domain-agnostic)
- Requires no domain-specific parameter tuning
- Computable for any system with measurable observables
- Captures the A3 intuition: coherence = whole > sum of parts
- Known connections to complexity (LMC complexity = H × (1 − C) in certain formulations)

**Practical estimation method:**
For continuous data: binning-based histogram estimators, or k-nearest neighbor mutual information estimators (Kraskov-Stögbauer-Grassberger).

### 1.2 Dynamic Extension: C(t)

Coherence is not static. Define:

**C(t) = T(X₁(t); ... ; Xₙ(t) | X₁(t−1)...Xₙ(t−1)) / H(X₁(t)...Xₙ(t) | X₁(t−1)...Xₙ(t−1))**

Conditional total correlation: coherence of the next state given the current state. Captures whether the system evolves as a coherent whole or as independent components.

**Expected behavior for coherent systems:**
- High C: components update together, state transitions are coordinated
- Low C: components drift independently

### 1.3 Required Mathematical Work

| Work Package | Deliverable | Effort |
|:-------------|:-----------:|:------:|
| Proof that C [0,1] with well-defined extremes | Formal bounds | 1 week |
| Estimator comparison: binning vs kNN vs kernel | Estimator recommendation | 2 weeks |
| Convergence rates: how much data for stable C estimates | Sample size guidelines | 2 weeks |
| Sensitivity to discretization/partition choice | Robustness bounds | 1 week |
| Relation to existing order parameters (magnetization, density, etc.) | Mapping document | 2 weeks |
| **Total** | | **8 weeks (2 months)** |

---

## Phase 2 — Operationalization Across Domains

### 2.1 Domain: Physical Systems

| System | Observable | Components | C Prediction |
|:-------|:-----------|:-----------|:-------------|
| Ideal gas | Particle positions/momenta | n particles | Low C (independent) |
| Crystal lattice | Lattice site occupancy | n sites | High C (coordinated) |
| Magnet at T < Tc | Spin orientations | n spins | High C (aligned) |
| Magnet at T > Tc | Spin orientations | n spins | Low C (random) |
| Convective fluid | Fluid cell velocity | n cells | Medium C (patterns) |
| Driven sandpile | Grain positions | n grains | Medium C (critical) |
| Laser above threshold | Mode phases | n modes | High C (coherent) |

**Prediction:** C should track known order parameters but be computable without order parameter knowledge. C should detect phase transitions as sharp changes in coherence.

### 2.2 Domain: Biological Systems

| System | Observable | Components | C Prediction |
|:-------|:-----------|:-----------|:-------------|
| Bacterial colony | Gene expression by cell | n cells | Medium (quorum sensing) |
| Neural network (C. elegans) | Neuron firing | n neurons | High (coordinated) |
| Slime mold aggregation | Cell states | n cells | Increases during aggregation |
| Ant colony foraging | Ant position/activity | n ants | Increases during trail formation |
| Immune response | Cell type activation | n cell types | High during coordinated response |
| Ecosystem | Species abundance | n species | Medium (niche-structured) |
| Protein complex | Residue dynamics | n residues | High within folded domains |

**Prediction:** C should predict system persistence/robustness. Systems with C below a domain-specific threshold should be fragile. C should increase during adaptive responses.

### 2.3 Domain: Cognitive Systems

| System | Observable | Components | C Prediction |
|:-------|:-----------|:-----------|:-------------|
| EEG resting state | Electrode voltages | n electrodes | Medium-high (coherent) |
| EEG during task | Electrode voltages | n electrodes | Higher than rest (task-locked) |
| EEG during sleep | Electrode voltages | n electrodes | Lower (disconnected) |
| fMRI functional connectivity | BOLD signal regions | n regions | Medium (modular) |
| Epileptic seizure (ictal) | EEG channels | n channels | Very high (pathological lock) |
| Anesthetized state | EEG frequencies | n frequency bands | Lower than awake |
| Psychedelic state | EEG | n electrodes | Lower (disintegrated) |

**Prediction:** C should measure conscious integration. Predictions:
- C_awake > C_sleep > C_anesthesia
- C_normal < C_seizure (pathological over-coherence)
- C_psychedelic < C_normal (disintegration)

### 2.4 Domain: Social Systems

| System | Observable | Components | C Prediction |
|:-------|:-----------|:-----------|:-------------|
| Stock market | Individual stock prices | n stocks | Medium (correlated) |
| Stable vs crash market | Stock correlations | n stocks | C increases before crash (herding) |
| Social media propagation | User repost states | n users | C increases with viral content |
| Scientific collaboration | Co-authorship | n authors | Medium (community structure) |
| Political polarization | Voting patterns | n districts | C increases with polarization |
| City organization | District activities | n districts | Medium (functional divisions) |

**Prediction:** C detects collective behavior transitions. C spike precedes systemic instability (market crash, polarization cascade). C too high → brittle (all units behave identically — no diversity). C too low → fragmented (no coordination).

### 2.5 Operationalization Summary

| Domain | Observables | C max value expected | Key discriminator |
|:-------|:-----------|:--------------------:|:------------------|
| Physics | Well-defined state variables | 1.0 (crystal) | Tracks order parameters |
| Biology | Gene expression, activity | 0.8 (neural) | Predicts persistence |
| Cognition | EEG/fMRI channels | 0.7 (awake) | Tracks consciousness |
| Social | Agent states, prices | 0.6 (collective) | Detects instability |

The C values are not expected to be comparable across domains (different units, different numbers of components). The hypothesis is that **changes in C predict meaningful transitions** within each domain.

---

## Phase 3 — Benchmarking Against Existing Metrics

### 3.1 Existing Metrics for Comparison

| Metric | Domain | What It Measures | C Advantage Claim |
|:-------|:-------|:-----------------|:-----------------|
| Shannon entropy H | Any | Uncertainty/disorder | C captures structure, not just randomness |
| LMC complexity | Any | H × (1 - C) | C is the coherence term — more interpretable |
| Fractal dimension | Physical, biological | Scale-invariant geometry | C generalizes beyond geometry |
| IIT Φ | Neural | Integrated information | C is computable (Φ is NP-hard for large n) |
| Statistical complexity | Any | Predictive information | C doesn't require temporal prediction |
| Mutual information | Any | Pairwise dependencies | C captures all n-wise, not just pairwise |
| Order parameter (physics) | Physical | Symmetry breaking | C defined without knowing order parameter |
| Granger causality | Neural, econ | Directed influence | C is symmetric, measures integration |
| Synchronization index | Neural | Phase locking | C includes amplitude, not just phase |
| Algorithmic complexity | Any | Program size | C is practically computable |

### 3.2 Benchmarking Protocol

For each domain and system type:

1. Compute C and all competing metrics on the same dataset
2. For each transition (phase change, disease onset, crash, state change):
   - Does C detect it? At what lead time?
   - Do any existing metrics detect it earlier?
   - Is C's signal-to-noise ratio better?
3. For each system:
   - Does C predict future persistence/adaptivity?
   - Does C outperform existing metrics in predicting outcomes?
4. Cross-domain generalization:
   - Does the same C computation procedure work across all domains with zero domain-specific tuning?
   - Do existing metrics require domain-specific parameter adjustments?

**Success criterion:** C matches or exceeds the best existing metric in at least 3 of 4 domains using the same estimator, without domain-specific tuning.

### 3.3 Known Weakness of C

Total correlation does not distinguish between:
- **Synergistic structure** (coherence from integration, like neural binding)
- **Redundant structure** (coherence from homogeneity, like crystal lattice)

A crystal and a brain could theoretically have the same C value despite very different organization.

**Mitigation:** Compute C alongside a redundancy-synergy decomposition (using partial information decomposition, PID) to distinguish these cases. SFH-SGP predicts that high-C high-synergy systems are more adaptive than high-C high-redundancy systems.

---

## Phase 4 — Experimental Protocol

### 4.1 Primary Hypothesis (from A3+A6)

> H₁: A single coherence metric C, defined as normalized total correlation and computed via the same estimator across domains, predicts system state transitions and long-term persistence better than domain-adapted complexity measures.

### 4.2 Secondary Hypothesis

> H₂: Within the set of high-C systems, those with high synergy (vs high redundancy) are more adaptive and resilient to perturbation.

### 4.3 Data Requirements

| Data Type | Source | Accessibility | Quality |
|:----------|:-------|:-------------:|:-------:|
| Ising model simulations | Generate | Immediate | Perfect |
| EEG resting/task/sleep | Open databases (PhysioNet, HBN) | Immediate | High |
| fMRI BOLD | OpenNeuro, HCP | Immediate | High |
| Stock market data | Yahoo Finance, Kaggle | Immediate | High |
| Social media cascades | Twitter API (historical), MemeTracker | Medium | Medium |
| Gene expression (bacterial) | GEO database | Immediate | High |
| Species abundance data | Ecological databases | Immediate | High |
| Sandpile model (self-organized criticality) | Generate | Immediate | Perfect |
| Slime mold aggregation | Published time series | Low | Medium |
| C. elegans neural data | OpenWorm | Immediate | High |

Estimated accessible data: **80% from open sources**, 15% from simulations, 5% requiring collaboration.

### 4.4 Work Packages

| WP | Description | Duration | Deliverables |
|:--:|:------------|:--------:|:------------|
| **WP1** | Formalization and estimator selection | 2 months | Mathematical definition, estimator code, validation on synthetic data |
| **WP2** | Physical systems benchmark | 2 months | C on Ising, fluids, SOC, laser; comparison to order parameters |
| **WP3** | Biological systems benchmark | 3 months | C on neural (C. elegans, EEG), ecological, gene expression data |
| **WP4** | Cognitive systems benchmark | 3 months | C on EEG/fMRI across conscious states, comparison to Φ |
| **WP5** | Social systems benchmark | 3 months | C on markets, social media, collaboration networks |
| **WP6** | Cross-domain synthesis | 3 months | Unified analysis: does C generalize? Redundancy-synergy decomposition |
| **Total** | | **16 months** | |

### 4.5 Success Criteria

| Level | Criterion | Evidence Required |
|:------|:----------|:-----------------|
| **Minimal** | C computable across all domains with same estimator | Code runs on physical, biological, cognitive, social data |
| **Moderate** | C detects known phase transitions in ≥50% of systems | ROC curve, AUC > 0.7 |
| **Strong** | C outperforms existing metrics in ≥3/4 domains | Direct comparison: C beats domain-adapted metric on prediction task |
| **Compelling** | C reveals novel phase transitions not captured by existing metrics | New transitions confirmed by independent evidence |
| **Definitive** | C's predictive power for system persistence generalizes without retuning | Cross-validation: same C threshold predicts fragility across domains |

**Go/No-Go gates:**
- After WP1: Metric must be computable and validated on synthetic data (α=0.05)
- After WP2: C must detect Ising phase transition (trivial baseline)
- After WP3: C must outperform at least one domain metric on biological data
- After WP6: Final assessment against Strong criterion

### 4.6 Failure Criteria

| Failure Mode | How It Would Occur | Verdict |
|:-------------|:------------------:|:--------|
| **Trivial failure** | C behaves identically to Shannon entropy | A3 falsified for this approach |
| **Inconsistent failure** | C detects transitions in some domains but not others | A6 weakened |
| **Competitive failure** | C matches but never beats existing metrics | SFH-SGP doesn't add predictive value |
| **Noise failure** | C estimates require unrealistic data volumes | A3 non-operationalizable |
| **Domain failure** | C computable only for simulated, not real, systems | A3 not empirically accessible |

---

## Phase 5 — Effort and Likelihood Assessment

### 5.1 Personnel

| Role | Time | Cost (USD) |
|:-----|:----:|:----------:|
| Principal investigator (existing) | 10% time | 0 (sunk) |
| Postdoc (complexity science) | 24 months | $120k |
| PhD student (comp-neuro) | 36 months | $90k (stipend) |
| Research assistant (coding) | 12 months | $40k |
| **Total personnel** | | **$250k** |

### 5.2 Compute and Data

| Item | Cost |
|:-----|:----:|
| Cloud compute (AWS/Google) for metric computation | $15k |
| Data access fees | $2k |
| Publication costs (open access × 4 papers) | $12k |
| Conference travel × 3 | $6k |
| **Total non-personnel** | **$35k** |

### 5.3 Total Budget

**$285k over 3 years** — comparable to a small NSF grant.

### 5.4 Likelihood Assessment

| Scenario | Probability | Description |
|:---------|:----------:|:------------|
| **C is computable and well-behaved** | 80% | Standard mutual information estimators work; C behaves as expected |
| **C detects known transitions** | 70% | Ising, sleep stages, market crashes all should show C shifts |
| **C outperforms existing metrics** | 30% | Strongest claim; existing metrics evolved for specific domains |
| **C reveals novel phenomena** | 15% | Hardest; requires existing metrics left signal on the table |
| **C definitively supports SFH-SGP** | 10% | Would require C to reveal transitions no other metric captures and to predict fragility across domains |

**Most likely outcome:** C is computable, detects known transitions, matches but doesn't consistently beat domain-adapted metrics. This would neither confirm nor disconfirm SFH-SGP — it would show coherence is a real property that existing domain measures already capture implicitly.

**Best case:** C outperforms existing metrics in at least 2 domains, revealing that a coherence-centered measure captures something existing measures miss.

**Worst case:** C estimates are too noisy at realistic data volumes, or C behaves identically to Shannon entropy, failing to add information.

---

## Summary

| Element | Content |
|:--------|:--------|
| **Research question** | Can a single coherence metric C, derived from SFH-SGP axioms A3+A6, outperform domain-adapted complexity measures across physical, biological, cognitive, and social domains? |
| **Core metric** | Normalized total correlation (multi-information) |
| **Total duration** | 16 months (active) / 3 years (with publication) |
| **Budget** | ~$285k |
| **Strongest success** | C outperforms domain-adapted metrics in ≥3 of 4 domains without retuning |
| **Likeliest outcome** | C is computable and detects known transitions but doesn't consistently beat domain metrics |
| **Falsification condition** | C is noisier than existing metrics at realistic data volumes |

---

## T800 Decision Gate

| Question | Answer | Required For |
|:---------|:-------|:-------------|
| Is C formally definable? | Yes — normalized total correlation | Proceed to WP1 |
| Is C computable on real data? | Yes — MI estimators exist for all domains | Proceed to WP2 |
| Are competing metrics known? | Yes — benchmark protocol specified | Proceed to WP3 |
| Are high-quality datasets accessible? | Yes — 80% open access | Proceed to WP4 |
| Is the budget feasible? | Yes — ~$285k | Proceed to WP5 |
| Has the inference path been audited? | Yes — T721, Distance 2 from A3+A6 | Final approval |

**Recommendation:** The T800 program is well-defined, falsifiable, and tests the shortest inference path from surviving axioms. It does not repeat the consciousness-causes-collapse error. Proceed to WP1 (metric formalization) if resources permit.
