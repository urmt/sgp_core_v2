# Steelman Model A — The Strongest Case for Causal Coherence

**Objective**: Present the most persuasive defense of Model A (C is causally involved in recovery) as if arguing before a skeptical review panel.

**Constraints**: No strawmen. No rhetorical tricks. Only legitimate arguments.

---

## Argument 1: The Interaction Term Survives All Mobility Covariates

This is the single strongest quantitative argument for C's involvement.

When we fit:
```
Recovery ~ C + friction + C:friction + mobility_proxy
```

The C × friction interaction term remains significant (p < 0.005) for ΔC and restoration, regardless of which mobility proxy we add (MSD, RMS velocity, neighbor turnover). None of the mobility proxies significantly predict recovery themselves (all p > 0.10).

**Panel interpretation**: If C were purely a non-causal thermometer that tracks mobility, then conditioning on mobility should make the C term disappear. It does not. The interaction survives. This is direct statistical evidence against conditional independence — the core claim of the thermometer model.

**Counterargument**: Our mobility proxies may be incomplete. C may capture residual dynamics.

**Rebuttal**: This requires the panel to accept that ALL three mobility proxies (MSD, RMS velocity, neighbor turnover) are simultaneously inadequate. These are standard kinematic measures that capture different aspects of motion. If none of them can substitute for C's predictive contribution, the claim that C is merely tracking "dynamics we haven't measured" becomes an untestable appeal to ignorance. At some point, the interaction surviving all available mobility measures becomes evidence for C's independent role.

---

## Argument 2: Strong Feedback in Granular Physics

The thermometer analogy breaks down for granular systems.

In the granular DEM, what C measures (total correlation of bin-averaged y-positions) reflects the contact network topology. This contact network is mechanically real — it determines:
- Which grains support each other
- How forces propagate through the packing
- Which grains are load-bearing
- How the packing reconfigures after removal

**Panel interpretation**: C is not measuring a passive property. It is measuring the interaction topology that mechanically controls force propagation. When grains are removed, the remaining contact network determines which grains shift and how quickly the system stabilizes. C IS the structural quantity that determines recovery, not merely a correlate of it.

**Counterargument**: C is still a consequence of dynamics (how grains settled), not an independent cause.

**Rebuttal**: This confuses "historically determined" with "non-causal." The contact network at t=500 is historically determined by 500 steps of settling, but at t=500 it is physically real and mechanically consequential. The fact that C's value was caused by past dynamics does not mean C has no causal effect on future dynamics. This is the distinction between **originating cause** and **proximate cause**. The thermometer really is a poor analogy — a better one is the elastic modulus of a material, which is historically determined but causally relevant to deformation response.

---

## Argument 3: C Varies at Fixed Friction

Within each friction level, C varies by ±0.02–0.04 due to microstructure (random seed). This C variation is not caused by friction — it reflects differences in grain packing geometry that arise from the initial conditions.

**Panel interpretation**: If C were entirely friction-determined, within-friction C should be constant. It is not. The fact that random seed produces measurable C variation, and this variation correlates with recovery differences, is direct evidence that C captures structure beyond what friction explains.

**Counterargument**: The within-friction C range is small (sd ≤ 0.04) and the correlation with recovery within friction is weak.

**Rebuttal**: "Small" is relative to the across-friction range (0.20). But if a C shift of 0.20 across friction levels produces a restoration shift of ~0.20, then a C shift of 0.04 within a friction level should produce a restoration shift of ~0.04 — detectable with n=10 if the signal-to-noise ratio is adequate. The within-friction reversal (higher C → slower τ_rec at friction ≥ 0.40) is consistent across 3 friction levels (0.40, 0.60, 0.80), which is unlikely by chance (p ≈ 0.125 per level, ~0.002 for three levels together).

---

## Argument 4: C Works Across Systems Without Friction

C discriminates structure across 8 testbeds including coupled oscillators, flocking, neural systems, and opinion dynamics — none of which have a friction parameter. If C were merely a friction proxy, it should fail on non-granular systems.

**Panel interpretation**: C's success across diverse systems demonstrates it captures a general property of interaction structure, not a system-specific parameter. This general property (interaction structure) is predictively useful for recovery in granular systems. If this property is generally useful, it is likely because interaction structure plays a causal role in how complex systems respond to perturbation, not because it happens to correlate with friction in one particular system.

**Counterargument**: C's cross-system success validates C as a state measure, not as a cause.

**Rebuttal**: The distinction between "state measure" and "cause" is not as sharp as models A and D suggest. In complex systems, state variables that capture collective organization often have causal relevance because they determine macroscopic response. Temperature causes pressure changes (not merely predicts them). The order parameter in phase transitions controls system behavior (not merely describes it). The burden should be on the skeptic to show why C is different from every other collective state variable in statistical mechanics.

---

## Argument 5: The Threshold Behavior

High-C runs uniformly recover well (restoration > 1.0 for all 15 Q4 runs). No counterexample exists. Low-C runs have variable outcomes (5/15 recover well, 10/15 recover poorly).

**Panel interpretation**: This is consistent with C being a **necessary but not sufficient** condition for good recovery. High C ensures good recovery (necessary: without high C, recovery is variable). Low C does not guarantee poor recovery (not sufficient: other factors like residual mobility can compensate).

**Counterargument**: This is the same pattern as high friction ensuring poor recovery (necessary but not sufficient). C and friction are correlated.

**Rebuttal**: The necessity pattern is real regardless of the friction correlation. The question is whether high C ensures good recovery BECAUSE of C (causal) or BECAUSE of the conditions that produce high C (associative). This is the causal identification problem. But in a policy context: if we observe a system with high C, we can predict good recovery with high confidence regardless of the causal mechanism. This makes C practically useful even before the causal question is resolved.

---

## Argument 6: The Comparison to Competitor Metrics is Informative

C outperforms I_pred (SNR 2.14 vs 0.18), C_sigma (2.14 vs 0.0), and MSE (2.14 vs −0.80) for perturbation detection.

**Panel interpretation**: C detects the perturbation boundary with high signal-to-noise ratio. This means C captures a real change in the system at the perturbation time. If C were merely a passive thermometer, the perturbation detector would be a thermometer that detects events — which is still useful. But the relevant point for causation is that C responds to perturbation BEFORE any mobility change is detectable at the aggregate level, suggesting C is an early indicator of a process that mobility measures miss.

**Counterargument**: Early detection doesn't imply causation. Smoke detectors detect fires early but don't cause them.

**Rebuttal**: The smoke detector analogy works for FIRE detection. But the claim is not that C detects recovery — it's that C is involved in recovery. The early response to perturbation is consistent with C being part of the causal chain (interaction structure reorganizes → forces redistribute → system recovers), not merely a downstream readout.

---

## Summary: The Strongest Case

1. **The interaction survives all mobility covariates** (p < 0.005 for ΔC and restoration). This is the quantitative bedrock. If the thermometer model were correct, mobility should absorb C's contribution. It does not.

2. **Granular physics makes C mechanically relevant.** The contact network C measures literally determines how forces propagate. Calling this a "thermometer" ignores the known physics.

3. **C varies at fixed friction and this variation matters.** Microstructure differences produce real C differences, which correlate with recovery outcomes.

4. **C generalizes across systems without friction,** suggesting it captures a general property of interaction structure — not a friction-specific artifact.

5. **No mobility proxy predicts recovery.** The model that claims "mobility causes recovery" cannot demonstrate this with any of its three mobility measures. This is a failure of the thermometer model's positive prediction, not a strength.

### Is Model A wounded?

Yes. The claim that "C alone determines recovery" is decisively falsified (same C produces opposite outcomes). The claim that "C is sufficient for good recovery" is falsified by low-C runs that recover well.

### Is Model A dead?

No. A weaker version survives: **"C is causally involved in recovery as part of a multi-factor interaction with mobility."** This version:
- Has the best predictive fit of any model (R² = 0.52–0.56)
- Is consistent with all observations
- Makes testable predictions (intervention would change recovery)
- Is supported by the physics of the system

### What would kill this weaker version?

1. **Cross-validation collapse**: If the interaction term does not survive out-of-sample testing, the case weakens significantly.
2. **Intervention experiment fails**: If manipulating C at fixed friction does not change recovery, C is not causally involved.
3. **A better mobility measure**: If a mobility measure is found that absorbs C's predictive contribution, the thermometer model wins.

None of these have been demonstrated. The weaker version of Model A remains viable.
