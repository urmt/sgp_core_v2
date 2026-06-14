# T810 — Metric Identifiability Audit

**Objective:** Determine whether C (normalized total correlation) can be motivated from SFH-SGP specifically, or whether it collapses into existing complexity/information-theoretic measures that any framework would propose.

---

## T810.1 — Mathematical Relationships to Existing Metrics

### Notation

C(S) = T(X₁; ... ; Xₙ) / H(X₁...Xₙ)

T = Σᵢ H(Xᵢ) − H(X₁...Xₙ)

H_joint = H(X₁...Xₙ)

### Metric Comparison Table

| Metric | Formula | Relationship to C | What distinguishes them |
|:-------|:--------|:-----------------:|:-----------------------|
| **Shannon entropy H** | −Σ p log p | C = T / H_joint. C = 1 − (H_joint / Σ Hᵢ) | H measures total uncertainty; C measures fraction of structure that is shared. C can increase while H decreases (ordering) or increase while H increases (integration). |
| **LMC complexity** | C_LMC = H × D | Similar form: C_LMC = H × (some distance-from-uniform). Ours replaces D with T/ΣHᵢ. | LMC peaks at intermediate H (edge of chaos). C peaks at maximum integration (crystal, brain). Different maxima. |
| **Mutual information (pairwise)** | I(Xᵢ; Xⱼ) = Hᵢ + Hⱼ − Hᵢⱼ | For n=2: C = I / H_joint. For n>2: C captures all n-wise interactions. | Pairwise MI misses triplet and higher interactions. C includes them. Example: three XOR-coupled variables have zero pairwise MI but nonzero C. |
| **IIT Φ** | min over partitions of (H(parts) − H(whole)) | C and Φ both use total correlation. C uses the actual partition; Φ searches for the minimum information partition. | Φ is NP-hard (search over partitions). C is O(n) to compute (uses natural decomposition). Φ is causal; C is associative. |
| **Statistical complexity C_μ** | I(past; future) — predictive information | Different domain: C_μ is temporal; C is compositional. | Can both be high independently. A system can have high compositional integration (crystal) but zero temporal complexity (fully periodic). |
| **Predictive information** | I(past; future) | Same object as C_μ. C is over components, not time. | Non-overlapping. One measures across space, one across time. |
| **Network integration** | Global efficiency, clustering, modularity | Graph-theoretic; C is information-theoretic. | C works on any state distribution. Network measures require a graph structure. C captures dynamics, not just topology. |
| **Granger causality** | F_{X→Y} = ln(σ²_reduced / σ²_full) | Directed, pairwise. C is undirected, n-wise. | C is symmetric (doesn't distinguish cause/effect). GC requires temporal ordering. They measure different aspects of interaction. |
| **Synchronization index** | PLV = |⟨exp(iΔφ)⟩| | Phase-only. C includes amplitude and phase structure. | C captures full joint distribution; PLV captures only phase alignment. |
| **Normalized compression distance** | NCD(x,y) = (C(xy) − min(C(x),C(y))) / max(C(x),C(y)) | NCD is pairwise; C is n-wise. | NCD measures distance between two strings. C measures integration of n components. |

---

## T810.2 — Equivalence Conditions

### When C equals (or approximates) another metric

| Condition | C becomes... | Explanation |
|:----------|:-------------|:------------|
| **Two variables only** | Normalized mutual information | C(n=2) = I(X₁; X₂) / H(X₁,X₂). All higher-order terms vanish. |
| **Gaussian variables** | Function of correlation matrix | For Gaussians: I(Xᵢ; Xⱼ) = −½ ln(1 − ρ²ᵢⱼ). T = −½ ln det(R) where R = correlation matrix. C = (−½ ln det(R)) / H_joint(distribution-dependent). |
| **Binary variables** | Capped by entropy ratio | C_max for n binary vars = 1 − (nH(1/n) / n) where H(1/n) is per-variable entropy. |
| **Pairwise-independent structure with no higher-order interactions** | Sum of normalized pairwise MI | If no triple+ interactions, C = Σᵢ<ⱼ Iᵢⱼ / H_joint. Higher-order terms vanish. |
| **Fully factorizable distribution** | 0 | P(X₁...Xₙ) = ∏ P(Xᵢ) → T = 0 → C = 0. | 
| **Fully deterministic, single-state system** | 0/0 (limit → 1) | H_joint → 0, T → 0. Limit depends on approach rate. |
| **Maximum entropy, n i.i.d. variables** | 0 | Independent → C = 0. |
| **Full correlation, each variable copies first** | 1 | H(Xᵢ) = H(X₁) for all i, H_joint = H(X₁) → T = nH(X₁) − H(X₁) = (n−1)H(X₁), C = (n−1)/n → 1 as n→∞. |

### When C and Φ diverge

C and Φ are identical only when the system's natural decomposition equals the minimum information partition. This occurs when:
- The system has no meaningful subsystem structure (all components equally coupled)
- There is no "weakest link" in the integration

In most real systems, Φ < C (often much less) because the optimal partition finds a subsystem that is relatively independent.

**Example:** A system of two strongly coupled clusters with a weak connection between clusters:
- C (using the natural decomposition into all n units) is high
- Φ (searching for the MIP) will find the weak link between clusters → low Φ
- C tells you the system is integrated; Φ tells you there's a bottleneck

---

## T810.3 — Predictions C Can Make That Competitors Cannot

### Prediction 1: Coherence-gradient-driven reorganization

**Claim:** Systems reorganize to increase or maintain C within a preferred range. This is not "entropy maximization" (which would drive C to 0) — it is the opposite.

**Standard metrics cannot make this prediction:** Entropy predicts dispersal (C → 0). Φ (as defined) makes no directional claim about system evolution. Statistical complexity (C_μ) makes no claim about system preferences.

**How to test:** Simulate an initial system with components at moderate C. Subject it to noise. Does C return to its initial value (homeostasis) or decay to 0 (entropy dominance)?

**SFH-specificity:** This follows directly from A3 (coherence as physically active organizing principle). Without A3, there is no reason to expect C to be maintained rather than decay.

---

### Prediction 2: Redundancy-synergy decomposition predicts failure mode

**Claim:** Two systems can have equal C but different robustness profiles. C decomposed into redundant vs synergistic components predicts the failure type.

| C decomposition | High redundancy | High synergy |
|:----------------|:---------------|:-------------|
| **Example** | Crystal lattice | Neural network |
| **C value** | High | High |
| **Failure mode** | Brittle (one defect propagates) | Graceful degradation (components compensate) |
| **Recovery** | Needs external restructuring | Self-repair possible |
| **SFH prediction** | Low adaptivity despite high C | High adaptivity with high C |

**Standard metrics cannot distinguish this:** Entropy, LMC complexity, network integration, Φ all give a single scalar. Only partial information decomposition (PID) resolves redundancy vs synergy, and PID is rarely applied outside neuroscience.

**How to test:** Compute C with PID decomposition on systems with known failure modes. Verify that the R/S ratio predicts failure type.

**SFH-specificity:** A3 (coherence meaningful) + A5 (self-modeling) predicts that self-modeling systems develop synergistic (not redundant) coherence. A crystal has coherence without self-modeling → redundant, brittle. A brain has coherence with self-modeling → synergistic, adaptive.

---

### Prediction 3: Cross-scale C covariance is causal

**Claim:** If A6 is true (scale-continuous principles), then changing C at one scale should cause C to change at adjacent scales. This goes beyond correlation to causation.

**Standard metrics cannot make this prediction:** Power-law correlations are known but causal cross-scale coupling is not predicted by any standard theory.

**How to test:** Perturb a system at the micro scale and measure C at the meso scale. Does locally reducing coherence (e.g., disordering a subset of components) reduce coherence at higher organizational levels?

**SFH-specificity:** Requires A6 (scale continuity) which is specific to SFH. Standard complexity science treats scales as independent levels of description.

---

### Prediction 4: C has a preferred baseline across domains

**Claim:** Different systems across different domains converge on similar C values when they are in stable, persistent states — not because of shared local constraints, but because coherence itself has a preferred value.

**Standard metrics cannot make this prediction:** Entropy has no preferred value (it's system-size-dependent). Φ has no preferred value. Statistical complexity can vary arbitrarily.

**How to test:** Compute C on stable configurations of physical, biological, cognitive, and social systems. Do C values cluster around a specific regime (e.g., the "edge of criticality" range)?

**Caution:** This prediction is vulnerable to the "universal scaling" critique — apparent clustering may reflect mathematical constraints (C bounded [0,1], natural systems neither fully ordered nor fully random).

---

### Summary: Distinguishing predictions

| Prediction | SFH-derived | Competitor can match | Testable |
|:-----------|:-----------:|:-------------------:|:--------:|
| C-gradient drives reorganization | A3 (coherence active) | No | Simulation |
| R/S decomposition → failure mode | A3+A5 | No (no prediction) | Existing data |
| Cross-scale C covariance causal | A6 | No (assumes scale independence) | Perturbation experiment |
| C has preferred baseline | A3+A6 | Partially (criticality theory) | Observational |

---

## T810.4 — What Specifically SFH-Inspired Structure Does C Have?

### The honest answer: The metric itself is not uniquely SFH.

Normalized total correlation is a standard information-theoretic quantity. It can be (and has been) defined, studied, and applied without any reference to consciousness, projection, or fundamental coherence.

**What makes its application SFH-inspired is not the formula but:**

| Aspect | SFH derivation | Non-SFH derivation |
|:-------|:---------------|:-------------------|
| **Why compute C** | Coherence is physically meaningful (A3) — C measures it | Total correlation quantifies statistical dependency |
| **Why compute across domains** | Principles are scale-continuous (A6) — same C applies everywhere | Cross-domain comparison may reveal patterns |
| **Why expect C to predict persistence** | Coherence gradients drive reorganization (A3 active principle) | Integration might correlate with robustness |
| **Why expect R/S decomposition to distinguish systems** | Self-modeling (A5) produces synergistic coherence | Just a further analysis |
| **Why expect cross-scale covariance** | A6 posits causal continuity across scales | No particular expectation |

### The uniquely SFH-derived claim

> **C is not just a description. It is causally relevant. Coherence organizes matter.**

This means:
- C gradients produce forces (like temperature gradients produce heat flow)
- Systems evolve toward higher C (like systems evolve toward lower free energy)
- C has a preferred range (like pH has a preferred range in biological systems)
- C at one scale constrains C at adjacent scales (scale coupling)

These claims go beyond "C is a useful statistic." They posit coherence as an active physical principle — analogous to how thermodynamics posits entropy as active (second law), not just descriptive.

**If C is treated purely descriptively (a statistic like any other), there is nothing SFH-specific about it. The SFH content is entirely in the causal claim: that C gradients drive system reorganization.**

---

## T810.5 — Pre-Registration Template for T800 Benchmarks

### Mandatory pre-registration fields

```
PROTOCOL ID: T800_WP[#]_[DOMAIN]_[DATE]

1. DOMAIN:
   [Physical / Biological / Cognitive / Social]

2. DATASETS (pre-specified):
   - Dataset 1: [Name, source, citation]
   - Dataset 2: [Name, source, citation]
   - Dataset 3: [Name, source, citation]
   (No additional datasets without protocol amendment)

3. PRIMARY OUTCOME:
   [Specific prediction, e.g., "C_awake > C_anesthesia in EEG"]

4. SECONDARY OUTCOMES:
   [e.g., "C correlates with behavioral performance"]

5. COMPARISON METRICS (pre-specified):
   - Metric 1: [Name, reference implementation]
   - Metric 2: [Name, reference implementation]
   - Metric 3: [Name, reference implementation]

6. SUCCESS CRITERION:
   [Quantitative: e.g., "C's AUC > 0.7 and exceeds Φ's AUC by 0.05+"]

7. FAILURE CRITERION:
   [Quantitative: e.g., "C's AUC < 0.5 (not better than chance)"]

8. C COMPUTATION (frozen before testing):
   - Estimator: [kNN / histogram / kernel]
   - Parameters: [k, bin width, kernel bandwidth]
   - Discretization method: [if continuous data]
   - Number of components n: [fixed for each dataset]

9. MULTIPLE COMPARISON CORRECTION:
   [Bonferroni / FDR / other]

10. PRE-REGISTRATION DATE:
    [Date]

11. ANY DATA SEEN PRIOR TO REGISTRATION:
    [Yes/No — if Yes, specify what]
```

### Required before any T800 benchmark begins

1. Freeze C estimator and all parameters
2. List all datasets and outcomes
3. List all comparison metrics with reference implementations
4. Specify success/failure criteria numerically
5. Register. Then compute. Do not iterate.

---

## T810 — Decision Gate

| Question | Answer | Verdict |
|:---------|:-------|:--------|
| Is C identical to an existing metric? | No — n-wise total correlation captures higher-order interactions that pairwise MI, Φ (different partition), and network measures miss | C is formally distinct |
| Can C be motivated without SFH? | Yes — information theory defines total correlation without SFH | **Identifiability problem** |
| Does SFH add anything to the motivation? | Yes — the causal claim (C gradients drive reorganization) and the scale-coupling claim (A6) are SFH-specific | **This is the distinctive content** |
| Can the SFH-specific claims be tested? | Yes — Prediction 1 (C-gradient reorganization) and Prediction 3 (cross-scale causation) are testable | Proceed to T800 with caution |
| Is pre-registration feasible? | Yes — template provided | Required before any benchmark |

### Verdict

> C as a descriptive statistic is not uniquely SFH-derived. Any information theorist could define it.
>
> The SFH-specific content is the **causal claim**: C gradients drive system reorganization, and C at one scale constrains C at adjacent scales.
>
> **Therefore T800 should test two things simultaneously:**
> 1. Does C predict persistence better than competitors? (descriptive test)
> 2. Do systems reorganize to maintain preferred C? (causal test — SFH-specific)
>
> If only (1) succeeds, SFH is not supported.
> If (2) also succeeds, SFH gains distinctive support.
>
> Pre-register both tests before touching data.
