# Evidence Verification

For every claim in `results/EVIDENCE_LEDGER.md`, a structured audit of supporting and contradicting evidence.

**Type key**: P = Predictive, C = Causal, E = Epistemological, M = Methodological, G = Generalization, X = Meta-scientific

---

## Claim 1: Interaction-first reconstruction outperforms data-first

| | |
|---|---|
| **Claim Type** | Methodological |
| **Supporting Evidence** | IF-3 recovers interaction structure at 90% missing interactions and 10× noise injection. Data-first methods (naive correlation, mutual information, Granger causality) fail at >50% missing data. Recovery is measured by structural similarity to ground-truth interaction graph. |
| **Contradicting Evidence** | Only tested on synthetic systems with known ground truth graph. Real systems have no ground truth. Performance depends on the assumption that interactions are pairwise and stationary. |
| **Confidence** | High (for synthetic systems) |
| **Reproducible** | Yes — IF-3 algorithm is deterministic, random seeds known |
| **Current Status** | Supported |

---

## Claim 2: Coherence detects perturbations

| | |
|---|---|
| **Claim Type** | Predictive |
| **Supporting Evidence** | SNR = 2.14 for C across 60 granular runs (perturbation at t=500). All 60 runs show a measurable C dip or rise at the perturbation boundary. The C signal-to-noise ratio exceeds all competitor metrics. |
| **Contradicting Evidence** | At friction ≤ 0.2, C rises (negative dip) rather than falling — the "dip" direction reverses. However, the perturbation is still detected (the change is measurable), so this contradicts the *direction* assumption but not the *detection* claim. |
| **Confidence** | High |
| **Reproducible** | Yes — all 60 runs saved with seeds |
| **Current Status** | Supported |

---

## Claim 3: Coherence discriminates structure

| | |
|---|---|
| **Claim Type** | Predictive |
| **Supporting Evidence** | C cleanly separates 8 structured vs unstructured testbed systems. Structured systems (coupled oscillators, flocking, granular) > 0.6 C. Unstructured systems (independent random walk, independent noise) < 0.2 C. |
| **Contradicting Evidence** | Only 8 systems tested. The structured/unstructured boundary (C ≈ 0.4) is empirically observed, not theoretically derived. |
| **Confidence** | High |
| **Reproducible** | Yes |
| **Current Status** | Supported |

---

## Claim 4: Coherence predicts resilience

| | |
|---|---|
| **Claim Type** | Predictive |
| **Supporting Evidence** | C-only model predicts ΔC (R²=0.10, p≈0.01) across 60 runs. Interaction model (C × friction) predicts ΔC (R²=0.52), τ_rec (R²=0.35), restoration (R²=0.56). High-C (Q4) runs uniformly have restoration > 1.0. |
| **Contradicting Evidence** | C-only model fails for τ_rec (R²=0.05, p≈0.09) and restoration (R²=0.04, p≈0.12). Same C (±0.01) predicts τ_rec ratios of 3–4× (37 vs 137 steps). Low-C (Q1) runs can have restoration > 1.2 (5/15). The ΔC sign (increase vs decrease) depends on friction, not C. |
| **Confidence** | Low — C predicts weakly alone, contributes in interaction, but is falsified as sufficient |
| **Reproducible** | Yes — 60 runs, fixed seeds |
| **Current Status** | **Challenged** |

---

## Claim 5: Coherence alone predicts recovery direction

| | |
|---|---|
| **Claim Type** | Predictive |
| **Supporting Evidence** | None beyond the marginal ΔC R²=0.10 |
| **Contradicting Evidence** | In C=0.43–0.44 range, ΔC sign flips from negative (C increases, friction=0.40) to positive (C decreases, friction=0.60–0.80). All 10 friction=0.05 runs have negative ΔC (C increases). All friction=0.8 runs with C < 0.40 have positive ΔC (C decreases). Direction is determined by friction, not C. |
| **Confidence** | Confident — clear, repeated pattern across 6 friction levels × 10 reps |
| **Reproducible** | Yes |
| **Current Status** | **Falsified** |

---

## Claim 6: Coherence alone predicts recovery speed

| | |
|---|---|
| **Claim Type** | Predictive |
| **Supporting Evidence** | None — R²(C→τ_rec) = 0.05 |
| **Contradicting Evidence** | 10 matched pairs with C within ±0.01 have τ_rec ratios of 3–4× (fastest = 37 steps, slowest = 187 steps). At friction=0.4, τ_rec ranges from 37 to 137 despite C variation of only ±0.03. Within friction ≥ 0.40, higher-C runs recover *more slowly* (opposite of prediction). |
| **Confidence** | Confident |
| **Reproducible** | Yes |
| **Current Status** | **Falsified** |

---

## Claim 7: High coherence always implies good recovery

| | |
|---|---|
| **Claim Type** | Predictive |
| **Supporting Evidence** | All 15 high-C (Q4 ≥ 0.51) runs have restoration > 1.0 (range: 1.04–1.29). All have τ_rec ≤ 37 except one at 62. No high-C run has restoration < 1.0 or τ_rec > 100. |
| **Contradicting Evidence** | None found across 15 high-C runs. However, the claim is *always* — a single counterexample would falsify. With n=15, the probability of missing a 10% counterexample rate is ~20%. |
| **Confidence** | Tentative (n=15, but no exception found) |
| **Reproducible** | Yes |
| **Current Status** | Supported (no counterexample found) |

---

## Claim 8: Low coherence never implies good recovery

| | |
|---|---|
| **Claim Type** | Predictive |
| **Supporting Evidence** | None — the evidence is against this |
| **Contradicting Evidence** | 5/15 low-C (Q1 ≤ 0.38) runs have restoration > 1.2 (range: 1.17–1.29). These are runs at friction=0.6 or 0.8 with atypically high RMS velocity (13–15 vs 11–12 for other high-friction runs). The "good recovery" in these runs is driven by residual mobility, not C. |
| **Confidence** | Confident — 33% counterexample rate |
| **Reproducible** | Yes |
| **Current Status** | **Falsified** |

---

## Claim 9: Recovery depends on C × mobility (two-factor model)

| | |
|---|---|
| **Claim Type** | Predictive |
| **Supporting Evidence** | Model D (C + friction + C×friction) achieves R²=0.52 (ΔC), 0.35 (τ_rec), 0.56 (restoration). Outperforms C-only, friction-only, and additive across all three targets. The interaction term is significant (p < 0.05) for ΔC and restoration. Falsification strategies find evidence that both C and mobility are needed. |
| **Contradicting Evidence** | C and friction are correlated (r≈−0.74). The interaction R² improvement may be an artifact of this collinearity. Cross-validation has not been performed. In the C=0.43–0.44 range, C×friction predicts recovery direction correctly, but this is driven entirely by friction (C is nearly constant). |
| **Confidence** | Moderate — collinearity unresolved |
| **Reproducible** | Yes (regression itself is reproducible; the interpretation is not) |
| **Current Status** | Supported (with collinearity caveat) |

---

## Claim 10: C × mobility interaction survives cross-validation

| | |
|---|---|
| **Claim Type** | Predictive |
| **Supporting Evidence** | None — not yet tested |
| **Contradicting Evidence** | None — not yet tested |
| **Confidence** | N/A (no test performed) |
| **Reproducible** | N/A |
| **Current Status** | **Untested** |

---

## Claim 11: C is causally involved in recovery

| | |
|---|---|
| **Claim Type** | Causal |
| **Supporting Evidence** | C predicts ΔC (R²=0.10) and contributes to the interaction model. High-C runs always recover well (no counterexample). |
| **Contradicting Evidence** | C and friction are correlated (r≈−0.74). The predictive relationship may be entirely mediated by mobility. No intervention experiment has been performed. Friction predicts recovery at least as well as C (R²=0.18–0.30 vs 0.04–0.10). |
| **Confidence** | Unknown — no causal evidence available |
| **Reproducible** | Predictive pattern is reproducible; causal interpretation is not tested |
| **Current Status** | **Unknown** |

---

## Claim 12: Mobility causes recovery

| | |
|---|---|
| **Claim Type** | Causal |
| **Supporting Evidence** | Friction predicts ΔC (R²=0.30) and restoration (R²=0.23). All slow-recovery runs (τ_rec > 100) occur at friction ≥ 0.40. Within friction < 0.40, recovery is uniformly fast (τ_rec ≈ 37). |
| **Contradicting Evidence** | Friction also determines C. MSD mobility proxy shows weaker predictive power than friction (ΔR² ≈ 0.02–0.06 when added to friction model). At friction=0.4, some runs recover at τ_rec=37 while others at τ_rec=137 with similar MSD, suggesting friction (the parameter) captures something MSD does not. |
| **Confidence** | Low — plausible but not separable from C |
| **Reproducible** | Yes (pattern), no (causal attribution) |
| **Current Status** | Plausible |

---

## Claim 13: C × mobility interaction is genuine, not collinearity

| | |
|---|---|
| **Claim Type** | Causal / Statistical |
| **Supporting Evidence** | Interaction model (C×friction) outperforms additive model (C + friction) on all targets: ΔR² ≈ +0.10 for ΔC, +0.07 for τ_rec, +0.06 for restoration. The sign reversal is consistent with an interaction: friction modulates the C→recovery relationship. |
| **Contradicting Evidence** | C and friction correlated at r≈−0.74. The interaction may capture a nonlinear (e.g., quadratic) C→recovery effect. Within each friction level, the C range is narrow (±0.02–0.03), making the interaction estimate unreliable. Cross-validation not performed. When mobility proxies are added to the interaction model, results depend on which proxy is used. |
| **Confidence** | Unknown |
| **Reproducible** | Numerically yes; interpretation uncertain |
| **Current Status** | **Unknown** |

---

## Claim 14: C and mobility can be independently measured

| | |
|---|---|
| **Claim Type** | Methodological |
| **Supporting Evidence** | Within a fixed friction level, C varies by ±0.02–0.03 due to random seed variation (same friction, different microstructure). MSD also varies within friction levels (sd ≈ 2–4). This suggests at least some independence in their realizations. |
| **Contradicting Evidence** | In the current design, friction controls BOTH C and MSD (r(C, friction) = −0.74, r(MSD, friction) = −0.36). No experiment has independently manipulated one while holding the other fixed. The within-friction C variation (±0.02–0.03) may be too small to detect independent effects. |
| **Confidence** | Low — requires decoupling experiment |
| **Reproducible** | Measurement is reproducible; independence is not tested |
| **Current Status** | **Challenged** |

---

## Claim 15: Results generalize beyond granular systems

| | |
|---|---|
| **Claim Type** | Generalization |
| **Supporting Evidence** | Forest succession model shows C perturbation response consistent with granular. C structure discrimination works across 8 testbeds including neural and opinion models. |
| **Contradicting Evidence** | The C×mobility × recovery relationship has only been tested on granular (60 runs at 6 friction levels). No non-granular system has a mobility analogue. The sign reversal (C increase after removal) may be specific to granular physics — it has not been observed in forest succession where C always drops. |
| **Confidence** | Low |
| **Reproducible** | C measurement across testbeds is reproducible; recovery generalization is not tested |
| **Current Status** | Weakly Supported |

---

## Claim 16: C outperforms competitor metrics

| | |
|---|---|
| **Claim Type** | Comparative / Predictive |
| **Supporting Evidence** | SNR(C) = 2.14 vs SNR(I_pred) = 0.18 vs SNR(C_sigma) = 0.0 vs SNR(MSE) = −0.80 for perturbation detection. C uniquely detects the perturbation boundary in granular runs. |
| **Contradicting Evidence** | Only tested on one system (granular) for perturbation detection. Competitor metrics may perform differently with different parameter choices (e.g., different tau for predictive information). C_sigma has high variance at high friction (0.3–1.2 vs near-zero at low friction), creating false perturbation signatures. |
| **Confidence** | High (for perturbation detection on granular) |
| **Reproducible** | Yes |
| **Current Status** | Supported |

---

## Claim 17: Coherence metric is independent of SFH ontology

| | |
|---|---|
| **Claim Type** | Meta-scientific |
| **Supporting Evidence** | C computation uses only information theory (Gaussian KDE, total correlation ratio). The code imports scipy and numpy. No SFH-specific operations, assumptions, or parameters. |
| **Contradicting Evidence** | The *interpretation* of C ("systems with higher C are more structured") is consistent with SFH but does not require it. The metric works for any multivariate time series regardless of philosophical framework. |
| **Confidence** | Logical certainty (the metric code contains no ontological references) |
| **Reproducible** | Yes — inspect the code |
| **Current Status** | Asserted (logical, not empirical) |

---

## Summary

| Claim | Type | Status | Reproducible |
|-------|------|--------|-------------|
| IF-3 reconstruction | M | Supported | Y |
| C detects perturbations | P | Supported | Y |
| C discriminates structure | P | Supported | Y |
| C predicts resilience | P | **Challenged** | Y |
| C predicts direction | P | **Falsified** | Y |
| C predicts speed | P | **Falsified** | Y |
| High C → good recovery | P | Supported | Y |
| Low C → poor recovery | P | **Falsified** | Y |
| Recovery = C × mobility | P | Supported* | Y |
| Survives cross-validation | P | **Untested** | — |
| C is causal | C | **Unknown** | — |
| Mobility causes recovery | C | Plausible | — |
| Interaction is genuine | C | **Unknown** | — |
| C and mobility independent | M | **Challenged** | — |
| Generalization | G | Weakly Supported | — |
| C outperforms competitors | P | Supported | Y |
| Metric independent of ontology | X | Asserted | Y |

\* With collinearity caveat.

**All predictive claims are reproducible (60-run fixed-seed ensemble). All causal claims remain unresolved.** No experiment has manipulated C independently of dynamics.
