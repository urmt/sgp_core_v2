# T820 — Dynamical Law Specification & Critical Test Design

**Status:** Complete
**Input:** T810 Metric Identifiability Audit
**Objective:** Convert the coherence principle from a descriptive framework into a testable dynamical hypothesis with specified equations, null models, falsification conditions, and a scale-coupling experiment.

---

## T820.1 — Dynamical Law Specification

### The Inadequacy of Three Simple Candidates

| Principle | Equation | Prediction | Why Inadequate Alone |
|:----------|:---------|:-----------|:--------------------|
| **Max-C** | dC/dt > 0 | All systems → perfect order | False: gases, turbulent fluids, high-entropy systems exist and persist at low C. Also would conflict with second law of thermodynamics. |
| **Homeostatic** | C → C* | Systems return to fixed C* after perturbation | Why C*? Different systems require different C* with no principle determining it. Risk of one free parameter per system. |
| **Bounded optimization** | max C s.t. constraints | Systems at edge of feasible C range | What are the constraints? If constraints are unmeasured, unfalsifiable. |

### The Proposed Law: Coherence-Entropy Competition

The minimal viable dynamical law that follows from A3 (coherence as active principle) without conflicting with known thermodynamics:

> **For any system S with time-dependent state distribution Pₜ, the coherence C(t) evolves as the competition between a coherence-driving force (A3) and the entropic force (second law):**

dC/dt = α·F(C, S) − β·G(C, S)

where:

| Term | Meaning | Source |
|:----:|:--------|:------|
| α·F(C, S) | **Coherence force** — pushes system toward higher C | A3 — coherence is physically active |
| β·G(C, S) | **Entropic force** — pushes system toward lower C (higher entropy) | Second law of thermodynamics |
| α | Coupling strength of coherence principle | Universal constant (SFH parameter) |
| β | Coupling strength of entropy | Fixed by thermodynamics |

**At equilibrium (dC/dt = 0):**

α·F(C_eq, S) = β·G(C_eq, S)

**Therefore:**

C_eq is determined by the balance, not by any single principle.

### Specific Functional Forms

The simplest viable forms for F and G, dimensionally consistent:

**Coherence force** F(C, S) = C·(1 − C)·γ(S)

where γ(S) represents the system's internal connectivity structure (number of components, coupling topology, interaction strength).

**Justification:** F → 0 as C → 0 (no coherence to build on) and as C → 1 (max coherence already achieved). The term peaks at C = 0.5, where coherence-building has maximum effect.

**Entropic force** G(C, S) = C

**Justification:** The tendency for coherence to decay is proportional to current coherence (simpler than alternatives). Higher-C systems have more structure to lose.

**Resulting equation:**

dC/dt = α·C·(1 − C)·γ(S) − β·C

### Equilibrium Solution (dC/dt = 0)

C_eq = 1 − β / (α·γ(S))

**Predictions:**
- C_eq increases with γ(S) (more connected systems → higher equilibrium coherence)
- C_eq decreases with β/α (stronger entropic force relative to coherence force → lower C)
- C_eq = 0 when γ(S) ≤ β/α (below minimum connectivity, no coherence possible)
- C_eq → 1 as γ(S) → ∞ (infinitely connected system → perfect coherence)

### Perturbation Dynamics

For a system displaced from equilibrium by ΔC:

d(ΔC)/dt = −[α·(2C_eq − 1)·γ(S) − β]·ΔC + O(ΔC²)

**Exponential relaxation with time constant:**

τ = 1 / |α·(2C_eq − 1)·γ(S) − β|

**Testable prediction:** Recovery time τ depends on equilibrium C_eq and connectivity γ(S) in a specific, measurable way.

### Domain-General Prediction

The same equation should describe coherence dynamics across physical, biological, cognitive, and social domains — **with the same α and β constants across all domains.** Only γ(S) (system connectivity structure) varies between domains.

This is the core falsifiable claim.

---

## T820.2 — Null Model Comparison

Each null model represents a competing explanation for coherence dynamics.

### Null 1: Pure Entropy Maximization

| Aspect | Description |
|:-------|:------------|
| **Hypothesis** | System dynamics are purely entropic. C is a derived quantity that decays monotonically toward 0. | 
| **Equation** | dC/dt = −β·C (the entropic term alone) |
| **Prediction** | C(t) = C₀·e^{−βt}. No recovery after perturbation. |
| **Distinction from SFH** | SFH predicts recovery (α > 0) toward C_eq > 0. Pure entropy predicts unrecoverable decay. |
| **What kills it** | Any system showing C recovery after perturbation. |

### Null 2: Free-Energy Minimization (FEP)

| Aspect | Description |
|:-------|:------------|
| **Hypothesis** | Systems minimize variational free energy F. C correlates with F but has no independent causal role. |
| **Equation** | dF/dt ≤ 0. C may increase or decrease as a side effect of F-minimization. |
| **Prediction** | C dynamics are indirect consequences of F-minimization. C should sometimes decrease when F requires it. |
| **Distinction from SFH** | SFH predicts C has its own dynamics separable from F. FEP predicts C is enslaved to F. |
| **What kills it** | Showing that C dynamics cannot be reduced to F-minimization — C changes when F is stationary, or C drives F changes. |

### Null 3: Predictive Processing / Bayesian Brain

| Aspect | Description |
|:-------|:------------|
| **Hypothesis** | Neural/social systems minimize prediction error. Apparent coherence is a byproduct of shared generative models. |
| **Equation** | Prediction error minimization (various forms). No explicit C. |
| **Prediction** | What looks like C-restoration is actually model-updating. C has no independent dynamics. |
| **Distinction from SFH** | SFH predicts C-restoration in non-predictive systems (ecosystems, physical structures). PP is domain-restricted. |
| **What kills it** | C-restoration in systems that do not perform prediction (ecosystems after drought, sandpile after avalanche). |

### Null 4: Network Adaptation (Efficiency-Robustness Tradeoff)

| Aspect | Description |
|:-------|:------------|
| **Hypothesis** | Systems tune network structure to balance efficiency and robustness. C is a side effect. |
| **Equation** | d(network)/dt = argmax(efficiency + λ·robustness). No explicit C. |
| **Prediction** | C changes are consequences of network optimization. Different optimization targets → different C levels. |
| **Distinction from SFH** | SFH predicts C as the optimization target. Network adaptation predicts C as a byproduct. |
| **What kills it** | Showing that C optimization predicts network changes better than efficiency-robustness tradeoff. |

### Discrimination Table

| Empirical finding | SFH | Entropy max | FEP | Predictive proc | Network adapt |
|:-----------------|:---:|:-----------:|:---:|:---------------:|:-------------:|
| C recovers after perturbation | ✓ | ✗ | ? | ? | ? |
| Same C-dynamics α,β across domains | ✓ | ✗ | ✗ | ✗ | ✗ |
| C predicts persistence better than competitors | ✓ | ✗ | ? | ? | ✓ |
| C drives F, not just F drives C | ✓ | ✗ | ✗ | ✗ | ✗ |
| C restoration in non-predictive systems | ✓ | ✗ | ✗ | ✗ | ? |
| Cross-scale C propagation (T820.4) | ✓ | ✗ | ✗ | ✗ | ✗ |

---

## T820.3 — Critical Failure Conditions

### Level 1: Program-Weakening Failures

These would not falsify the coherence principle entirely but would reduce its scope.

| Failure condition | Empirical signature | Consequence |
|:------------------|:--------------------|:------------|
| **F1: No cross-domain α,β** | Best-fit α,β differ significantly (p < 0.01) across domains | A6 weakened. Coherence dynamics are domain-specific. SFH reduces to disparate local principles. |
| **F2: C redundant with entropy** | C(t) = 1 − H_norm(t) within noise bounds across all systems | C has no independence from entropy. The coherence principle collapses to neg-entropy. |
| **F3: Persistence predicted equally by any metric** | C's predictive power for persistence is not significantly better than H, Φ, or LMC | C is a useful metric but not distinctive. H0 (descriptive only) established. |
| **F4: No C restoration in adaptive systems** | Perturbed neural/ecological/social systems show no C recovery | A3 dynamical claim fails. C is purely descriptive. |

### Level 2: Program-Falsifying Failures

These would force abandonment of the coherence-principle as a scientific hypothesis.

| Failure condition | Empirical signature | Consequence |
|:------------------|:--------------------|:------------|
| **F5: C decreases reliably under perturbation with no recovery** | All perturbed systems show dC/dt < 0 with no restoration, across domains | Coherence force α = 0. A3 has no dynamical content. **Program falsified.** |
| **F6: C dynamics fully explained by simpler null model** | Bayesian model comparison favors entropy/FEP/network null across all domains | Coherence principle adds no explanatory power. **Occam's razor eliminates it.** |
| **F7: Scale coupling never detected** | No cross-scale C propagation after exhaustive search in multiple systems with adequate power (1 − β = 0.95) | A6 falsified. **Cross-scale principle unsupported.** |
| **F8: C never predicts persistence** | C(S) and persistence P(S) show no correlation (r ≈ 0) across any domain | The entire "coherence → stability" chain fails. **H0 descriptive fails too.** |

### Decision Rules

| Scenario | Verdict | Action |
|:---------|:--------|:-------|
| F5 or F6 or F7 or F8 confirmed | **FALSIFIED** | Abandon coherence-principle program. Publish null results. |
| F1 + F2 + F3 confirmed, F4 undetermined | **WEAKENED** | Coherence is domain-specific, entropy-linked, and not predictively distinctive. Continue only if new formulation found. |
| F1 confirmed only | **PARTIAL** | Coherence operates differently across domains. Retain A3, question A6. Domain-specific research possible. |
| No failures confirmed | **STRONG** | Proceed to full T800 benchmarking. |
| F4 fails (restoration observed) but F1-F3 not tested | **ENCOURAGING** | A3 dynamical claim supported. Continue to cross-domain tests. |

---

## T820.4 — Scale-Coupling Test Design

### The Most Distinctive Surviving A6 Prediction

If A6 (scale-continuous principles) is true, then:

> **Perturbing coherence at one scale should produce measurable coherence changes at neighboring scales, beyond what standard causal models predict.**

This is the highest-information experiment remaining because:
- No null model predicts it
- It directly tests the SFH-specific claim (descriptive metrics do not imply cross-scale causation)
- It can be performed on simulated and real systems

### Experimental Design

**Core idea:** Take a multi-scale system, measure C independently at two neighboring scales, perturb one scale, measure C at the other, and compare to null model predictions.

**Systems to test:**

| System | Micro scale | Meso scale | Perturbation |
|:-------|:------------|:-----------|:-------------|
| Neural culture | Single neuron firing | Local field potential (population) | Optogenetic stimulation of neuron subset |
| Ecosystem | Species abundance (local patch) | Community structure (regional) | Remove/reseed a patch |
| Social network | Individual activity | Group coordination | Deactivate a node subset |
| Granular material | Grain positions | Force chain network | Remove grains |
| Simulated: multi-scale RK | Individual component states | Coarse-grained aggregates | Perturb components with noise |

### Formal Hypothesis

H_scale: |ΔC_meso / ΔC_micro| > |ΔC_meso / ΔC_micro|null

where the null models are:
- **Null A (independence):** ΔC_meso ≈ 0 (no cross-scale effect)
- **Null B (entropic propagation):** ΔC_meso is predicted by entropy flow alone (no coherence-specific propagation)
- **Null C (linear response):** ΔC_meso follows standard causal influence (no coherence amplification)

### Protocol

```
1. Select system with at least two resolvable scales (micro, meso)
2. Measure C_micro and C_meso at baseline
3. Perturb micro scale (reduce coherence: add noise to components)
4. Measure C_meso immediately after perturbation
5. Measure C_meso at T = [0.1τ, 0.5τ, τ, 2τ, 5τ] where τ is the system's
   characteristic relaxation time
6. Compare to null model predictions
7. Reverse experiment: perturb meso scale, measure C_micro
```

### Predicted SFH-specific Signature

If A6 cross-scale coupling exists:
1. C_meso change > null prediction (amplification)
2. C_meso change occurs faster than standard causal propagation would predict
3. C_meso change correlates with C_micro change even after controlling for shared entropy
4. A similar effect in the reverse direction (meso → micro)

### Statistical Criteria

| Measure | Criterion |
|:--------|:----------|
| Effect size | Cohen's d > 0.5 |
| Significance | p < 0.01 (Bonferroni corrected for 5 time points) |
| Bayesian factor | BF > 10 vs each null model |
| Replication | Effect in ≥3 of 5 system types |

---

## Decision Summary

| Element | Outcome |
|:--------|:--------|
| **Dynamical law** | dC/dt = α·C·(1−C)·γ(S) − β·C — coherence-entropy competition. Universal α,β. |
| **H0** | C is descriptive only |
| **H1** | C is local dynamical (recovery after perturbation, same α,β within domain) |
| **H2** | C is cross-scale dynamical (α,β universal across domains, scale coupling) |
| **Critical failure** | F5: no C recovery ever → falsified. F7: no scale coupling → A6 falsified. |
| **Highest-information test** | T820.4: perturb coherence at one scale, measure propagation to neighboring scale |
| **Next step if T820 succeeds** | T800 benchmarking with pre-registered protocols |
| **Next step if T820 fails** | Abandon coherence-principle program. Publish null results. |

---

## T820 Deliverable Summary

| Section | File | Content |
|:--------|:-----|:--------|
| T820.1 | This document | Dynamical law: dC/dt = α·C·(1−C)·γ − β·C. Equilibrium solution C_eq = 1 − β/(αγ). Perturbation relaxation τ. |
| T820.2 | This document | Four null models (entropy max, FEP, predictive proc, network adapt). Discrimination table. |
| T820.3 | This document | 8 failure conditions (Level 1: weakening. Level 2: falsifying). Decision rules. |
| T820.4 | This document | Scale-coupling experiment: perturb micro-C, measure meso-C. Compare to null models. |

---

### The Question After T820

**Is coherence a genuine dynamical order parameter with cross-scale explanatory power, or merely a useful descriptive statistic?**

The dynamical law in T820.1 converts this philosophical question into an empirical one.

If systems reliably restore C after perturbation, using the same relaxation kinetics across domains, coherence has dynamical reality.

If not, coherence remains a descriptive statistic — interesting but not causally explanatory.

T820.4 (scale coupling) is the highest information experiment because it tests the SFH-exclusive prediction that no null model makes.
