# One Number: P(Model D is Best | Evidence)

**Requested**: A single number — a research judgment, not a Bayesian posterior.

**Scale**: 0.0 (impossible) → 0.5 (tied with competitors) → 1.0 (overwhelmingly favored)

---

## The Number

# **0.25**

P(Model D — C-as-thermometer — is currently the best explanation | existing evidence) = **0.25**

---

## Justification

### Why not higher (why D is not 0.5 or above)

1. **The interaction term survives all mobility covariates** (p < 0.005 for ΔC and restoration). If D were the correct model, conditioning on mobility should render C and recovery conditionally independent. It does not. D's only escape is to invoke inadequate mobility measures — an untestable defense.

2. **Mobility proxies do not predict recovery** (all p > 0.10 when added to the interaction model). D's core causal claim is that mobility causes recovery. But our best mobility measures cannot demonstrate this. D must either abandon its own causal claim or admit our mobility measures are inadequate — neither option is satisfactory.

3. **C varies at fixed friction** (sd = 0.012–0.036 depending on level) and this variation correlates with recovery outcomes. If C were purely a friction proxy, this within-friction variation should be noise. The consistent direction of the within-friction C–recovery relationship across multiple friction levels (p ≈ 0.002 for three-level joint probability) suggests it is not noise.

4. **The thermometer analogy is physically misleading** in granular systems where C captures the contact network that mechanically controls force propagation. A "thermometer" that reads the mechanical structure that determines recovery is not a passive bystander.

5. **D has more untested commitments than C** (4 vs 3), not fewer. D requires: C is conditional independent given dynamics (challenged), mobility measures are adequate (unclear), mobility causes recovery (mobility proxies don't predict), and manipulation would not change recovery (untested). The parsimony advantage of D is smaller than it appears.

6. **The method audit shows the original "D wins 4–0" score was a systematic artifact** of a rubric that counted D's non-falsification as explanatory wins. Under a positive-predictive-success rubric, C wins (0.67 vs 0.50). Under an explanation-per-assumption rubric, C also wins (3.00 vs 2.50).

### Why not lower (why D is not 0.0)

1. **D survives every observational attack.** No observation definitively contradicts D. For every challenge, D has a defensible (if not elegant) response.

2. **Parsimony is real value.** D requires fewer causal commitments than C or A. If the only difference between C and D is whether the interaction is genuine synergy or correlation, D is the more conservative interpretation.

3. **The intervention experiment has not been performed.** D's critical prediction (manipulating C doesn't change recovery) is untested. Until we test it, D cannot be eliminated.

4. **Model C has not been cross-validated.** The interaction term's impressive in-sample R² may not survive out-of-sample testing. If it collapses, D becomes the default.

5. **No model has strong causal evidence.** Every model's claims about causation are untested or built on correlation. D is not uniquely weak in this regard.

---

## Comparative Ranking

| Model | P(best | evidence) | Reasoning |
|-------|:---:|-----------|
| **A: C-causal** | 0.15 | Strong version dead (direction/speed falsified). Weak version (C involved in interaction) survives but is a subset of C. |
| **B: Mobility-only** | 0.05 | Falsified — C adds information beyond friction. Retained only for completeness. |
| **C: Interaction** | **0.45** | Best predictive fit, interaction survives, 100% coverage, highest explanation rate. But cross-validation untested; collinearity concern. |
| **D: Thermometer** | **0.25** | Parsimonious, unfalsified, but challenged by interaction survival and mobility proxy failure. Most untestable. |
| **E: Something else** | 0.10 | The space of unknown models. Always assign some probability to being wrong about the model space. |

---

## Summary

**0.25** means: D is a viable contender but not the leader. The leader is Model C (interaction), with 0.45. D is a clear second, surviving all attacks but weakened by the interaction survival and mobility proxy failure.

The causal question remains the unresolved bottleneck. No model's causal claims are strongly supported. D's survival is partly a consequence of being untestable observationally, not of being confirmed.

**The truth is likely some combination of C and D**: C captures structure that is mechanically relevant (C is more than a thermometer), but D is right that C and mobility are deeply entangled and cannot be cleanly separated with current data. The pure versions of either model are probably wrong.
