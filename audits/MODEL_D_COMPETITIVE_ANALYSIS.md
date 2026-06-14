# Model D Competitive Analysis — Causal-C vs Thermometer-C

Model D (Thermometer-C):

```
Underlying dynamics → Mobility → C → Recovery
```
where C is a non-causal readout of interaction structure.

## Core Question

For every observation currently claimed as support for a causal role of C, can Model D (C-as-thermometer) explain it equally well?

---

## Observation 1: C detects perturbations at t=500 (SNR = 2.14)

| Scoring | Value | Reason |
|---------|-------|--------|
| Causal-C | Ambiguous | Perturbation detection does not require C to be causal. A thermometer detects temperature changes without causing them. |
| Thermometer-C | Ambiguous | Detection is consistent with either model — both predict that C should respond to perturbation. |

**Verdict**: **Ambiguous**. Perturbation detection is equally well explained by both models. This observation provides zero discriminating power between Model A and Model D.

**Reproducibility**: The perturbation detection claim is not in dispute. What is in dispute is its implications for causation, which are none.

---

## Observation 2: C discriminates structured vs unstructured systems

| Scoring | Value | Reason |
|---------|-------|--------|
| Causal-C | Ambiguous | Structure discrimination does not require C to be causal. C measures interaction structure; structured systems have more structure. This is definitional. |
| Thermometer-C | Ambiguous | A thermometer reads temperature; C reads interaction structure. Both are informative without being causal. |

**Verdict**: **Ambiguous**. Structure discrimination is a validity check on the metric itself, not evidence for causation. Both models require C to reflect structure; neither requires C to *control* structure.

---

## Observation 3: High-C runs always recover well (restoration > 1.0)

| Scoring | Value | Reason |
|---------|-------|--------|
| Causal-C | Better explained by A | If C causes recovery, high C should cause good recovery. This is consistent. |
| Thermometer-C | Better explained by D | The conditions that produce high C (high mobility, low friction) also happen to produce good recovery. The high C is a *symptom* of being in a regime where recovery is easy, not a *cause* of it. |

**Verdict**: **Ambiguous — but Thermometer-C provides a simpler explanation**. Under Thermometer-C, no causal link exists — C and recovery are correlated because they share a common cause (mobility). Under Causal-C, a causal link exists but is not independently verified. Occam's razor favors the model with fewer causal commitments.

**Key question**: Is there any run where C is high but mobility is low? No — high C always co-occurs with low friction (high mobility). This is consistent with the shared-cause interpretation.

---

## Observation 4: Low-C runs can recover well (5/15 with restoration > 1.2)

| Scoring | Value | Reason |
|---------|-------|--------|
| Causal-C | Better explained by D | This observation is a *falsification* of the strong C→recovery thesis. If C alone were causal, low C should always impair recovery. It does not. |
| Thermometer-C | Better explained by D | These runs have residual mobility (RMS velocity 13–15) despite high friction (0.6–0.8), enabling recovery. C merely records that these systems are not optimally structured. |

**Verdict**: **Better explained by D**. The existence of low-C runs with strong recovery is difficult for Causal-C (it requires C to be optional — sometimes recovery happens without C). For Thermometer-C, it is expected: C reflects current interaction structure, but the capacity to *reorganize* (mobility) is what determines recovery. A system can be temporarily disordered but still mobile enough to recover.

---

## Observation 5: Same C (±0.01) produces opposite ΔC sign

| Scoring | Value | Reason |
|---------|-------|--------|
| Causal-C | Better explained by D | This is a *falsification* of the claim that C alone determines recovery direction. Under Causal-C, C=0.43 should produce a predictable ΔC sign. It does not. |
| Thermometer-C | Better explained by D | C is not causal, so C=0.43 does not predict direction. Direction depends on whether the system is in a low-friction (C rises after perturbation) or high-friction (C falls after perturbation) regime. C merely tags along. |

**Verdict**: **Better explained by D**. This is the single strongest piece of evidence against Causal-C. Identical C values produce opposite outcomes. Under Thermometer-C, identical C values simply mean the interaction structure happens to be the same at two different friction levels — no surprise that recovery differs when the underlying dynamics are different.

---

## Observation 6: Same C (±0.01) produces τ_rec ratio of 3–4×

| Scoring | Value | Reason |
|---------|-------|--------|
| Causal-C | Better explained by D | Same logic as Observation 5. If C were causal in recovery speed, same C implies same speed. They are not. |
| Thermometer-C | Better explained by D | C is a snapshot, not a speedometer. Recovery speed depends on mobility, which differs across friction levels even when C is momentarily the same. |

**Verdict**: **Better explained by D**. The τ_rec falsification is another strong contradiction for Causal-C.

---

## Observation 7: Interaction model (C × friction) predicts recovery

| Scoring | Value | Reason |
|---------|-------|--------|
| Causal-C | Better explained by A | The interaction can be interpreted as C having different causal effects at different friction levels. C matters more when friction is low (high mobility). |
| Thermometer-C | Better explained by D | The "interaction" is an artifact of the thermometer interpretation: C is informative about the regime (high C = low friction) and friction captures the regime. The interaction term captures a nonlinear relationship between the regime variable and recovery, not a genuine C×motion interaction. |

**Verdict**: **Ambiguous — critical unresolved question**. The interaction term is the central ambiguity. Under Causal-C, it represents genuine synergy. Under Thermometer-C, it's a statistical artifact of C being a transformation of the same variable (friction) that also predicts recovery.

**Resolution test**: Cross-validation. If the interaction term disappears under cross-validation, Thermometer-C is favored. If it survives, Causal-C is favored. This is the single most informative statistical test available on existing data.

---

## Observation 8: C outperforms competitor metrics (I_pred, C_sigma, MSE)

| Scoring | Value | Reason |
|---------|-------|--------|
| Causal-C | Ambiguous | Metric performance does not address causation. C being a better *measure* does not mean C is a better *cause*. |
| Thermometer-C | Ambiguous | A better thermometer detects state changes more reliably. This is a measurement claim, not a causation claim. |

**Verdict**: **Ambiguous**. This observation supports C's role as an informative state variable (Claim 3 in the ledger), which both models accept.

---

## Observation 9: IF-3 recovers structure at 90% missing data

| Scoring | Value | Reason |
|---------|-------|--------|
| Causal-C | Ambiguous | Reconstruction success supports the interaction-first framework generally, but does not specifically support C being causal in recovery. |
| Thermometer-C | Ambiguous | Same — the interaction-first framework stands independently of whether C is causal in recovery. |

**Verdict**: **Ambiguous**. This is an ontological claim (interaction-first epistemology), not a causal claim about recovery. Both models operate within the interaction-first framework.

---

## Summary Table

| Observation | Better explained by A (Causal-C) | Better explained by D (Thermometer-C) | Ambiguous |
|-------------|:---:|:---:|:---:|
| 1. C detects perturbations | | | ✓ |
| 2. C discriminates structure | | | ✓ |
| 3. High C → good recovery | | ✓ | |
| 4. Low C → good recovery (counterexamples) | | ✓ | |
| 5. Same C, opposite ΔC sign | | ✓ | |
| 6. Same C, 3–4× τ_rec ratio | | ✓ | |
| 7. Interaction model predicts | | | ✓ |
| 8. C outperforms competitors | | | ✓ |
| 9. IF-3 reconstruction | | | ✓ |

**Score**: Causal-C = 0 decisive observations, Thermometer-C = 4 decisive observations, Ambiguous = 5.

---

## Verdict

**Model D (Thermometer-C) explains every existing observation at least as well as Model A (Causal-C), and explains 4 observations strictly better.**

The only observation where Causal-C could potentially win is Observation 7 (the interaction model), but this requires the interaction to be genuine rather than collinear — and cross-validation has not been performed.

**Recommendation**: The default interpretation should shift from "C causes recovery" to "C is an informative state variable whose predictive power for recovery may be entirely mediated by mobility." The burden of proof is now on the Causal-C hypothesis to demonstrate that the interaction survives cross-validation and decoupling.
