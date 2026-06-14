# Evidence Ledger

Current status of all program claims as of RD-015 analysis.

**Type key**: P = Predictive, C = Causal, E = Epistemological, M = Methodological, G = Generalization, X = Meta-scientific

See [CRITICAL_ASSUMPTIONS_REGISTER.md](../CRITICAL_ASSUMPTIONS_REGISTER.md) for the companion document that tracks assumptions underlying these claims.

| Claim | Type | Status | Evidence | Confidence |
|-------|------|--------|----------|------------|
| **Interaction-first reconstruction outperforms data-first** | M | Supported | IF-3 recovers structure at 90% missing interactions; data-first methods fail at >50% | High |
| **Coherence detects perturbations** | P | Supported | SNR = 2.14 for C vs −0.80 for MSE across 60 granular runs | High |
| **Coherence discriminates structure** | P | Supported | C cleanly separates 8 structured vs unstructured testbed systems | High |
| **Coherence predicts resilience** | P | Supported | C+friction interaction model predicts ΔC (R²=0.52), restoration (R²=0.56). Interaction survives bootstrap (99.9% sign stable, 92.2% p<0.05 for ΔC), k-fold CV (80% folds), and train/test split (84% splits). C contains unique info beyond friction (ΔR²=0.13–0.27). τ_rec poorly predicted by all models. | Moderate |
| **Coherence alone predicts recovery direction** | P | Falsified | In C=0.43–0.44 range, ΔC is negative (C increases) at friction=0.40 but positive (C decreases) at friction=0.60–0.80 | Confident |
| **Coherence alone predicts recovery speed** | P | Falsified | 10 matched pairs with identical C (±0.01) have τ_rec ratios of 3–4× (37 vs 137 steps) | Confident |
| **High coherence always implies good recovery** | P | Supported (no counterexample found) | All 15 high-C (Q4) runs have restoration > 1.0 and τ_rec < 100. No falsifying case found. | Tentative (n=15) |
| **Low coherence never implies good recovery** | P | Falsified | 5/15 low-C (Q1) runs have restoration > 1.2 (strong recovery). Low C does not entail poor recovery. | Confident |
| **C contains unique predictive information beyond friction** | P | **Supported** | ΔR²(C | friction) = +0.13 to +0.27 across targets. Residual(C) predicts all targets (p < 0.005). Permutation importance: 21–44% of model R² depends on C. C+Fr+Fr² does not eliminate C's contribution. Mobility proxies add ≤0.042 ΔR² beyond core model. | Moderate |
| **Recovery depends on C × friction (two-factor model)** | P | Supported | Full interaction model: R²=0.523 (ΔC), 0.565 (restoration), 0.345 (τ_rec). Interaction term significant for ΔC (p=0.0015) and restoration (p=0.0057). Continuous interaction model beats threshold (ΔR²=+0.11 to +0.22) and additive (ΔR²=+0.06 to +0.09) alternatives. | Moderate (n=60) |
| **C × friction interaction survives cross-validation** | P | **Supported** | Bootstrap (5000 resamples): 99.9% sign stable (ΔC), 92.2% p<0.05. k-fold CV (100×5): interaction beats additive in 80% folds (ΔC), 70% (restoration). Train/test (200×70/30): interaction beats additive in 84% splits (ΔC), 76% (restoration). No sign reversal in 1000 CV folds. | High |
| **C contains unique information not captured by mobility proxies** | P | Supported | Mobility proxies add ΔR² ≤ 0.042 beyond full core model (ΔC: 0.029, restoration: 0.027, τ_rec: 0.042). LOCO: individual proxies add ΔR² ≤ 0.028. No mobility proxy significant when added to C+friction model (all p > 0.10). | Moderate (mobility measures may be inadequate) |
| **C is causally involved in recovery** | C | Unknown | Residual(C) predicts recovery 1.2–7.6× better than raw C. Friction-correlated component of C is anti-predictive. Granular physics provides plausible mechanism. But no intervention experiment performed. | Unknown |
| **Mobility causes recovery** | C | Plausible (weakened) | Friction predicts ΔC (R²=0.30) and restoration (R²=0.23). But friction also determines C. Mobility proxies add no unique predictive power beyond C+friction model (all p > 0.10). The claim that "mobility causes recovery" is empirically unsupported by current mobility measures. | Low |
| **C × friction interaction is genuine, not collinearity** | C | Unknown | Interaction survives bootstrap (99.9% sign stable), CV (80% folds), and residual analysis (C's unique component predicts 1.2–7.6× better than raw C). But C and friction are correlated (r=−0.84). Decoupling experiment required. | Low (improving) |
| **C and mobility can be independently measured** | M | Challenged | In granular DEM, friction controls both C (r=−0.84) and MSD mobility proxy | Requires decoupling experiment |
| **Results generalize beyond granular systems** | G | Weakly Supported | Forest succession shows C perturbation response consistent with granular. Mobility axis untested outside granular. | Low |
| **C outperforms competitor metrics** | P | Supported | C vs I_pred (SNR 2.14 vs 0.18), C_sigma (2.14 vs 0.0), MSE (2.14 vs −0.80) | High |
| **Coherence metric is independent of SFH ontology** | X | Asserted | Metric uses only information theory. No SFH-specific assumptions in computation. | Logical (not empirical) |

---

## Summary

| Status | Count |
|--------|-------|
| Supported | 10 |
| Challenged | 1 |
| Falsified | 3 |
| Untested | 0 |
| Plausible | 1 |
| Weakly Supported | 1 |
| Asserted | 1 |
| Unknown | 2 |

By type:
- Predictive claims: 13 (10 supported, 3 falsified)
- Causal claims: 3 (0 supported, 2 unknown, 1 plausible)
- Methodological: 2
- Generalization: 1
- Meta-scientific: 1

---

## Priority Claims for Testing

1. **C is causally involved in recovery** (Causal) — cannot be resolved with existing data. Requires intervention experiment where C is manipulated independently of friction/mobility. This is the highest-value open question.

2. **C and mobility can be independently measured** (Methodological) — requires new experiment (polydispersity × friction design). This is the prerequisite for resolving the causal question.

3. **Generalization to second system** (Generalization) — requires forest drought parameterization as mobility analogue.

Note: Claims 1 and 2 are interdependent. Until C and mobility can be decoupled, the causal question cannot be resolved.

---

## Changes from Previous Version

- **Coherence predicts resilience**: Challenged → Supported. Collinearity concern substantially addressed by cross-validation, residual analysis, and functional form competition.
- **C contains unique predictive information beyond friction**: New entry, Supported.
- **C × friction interaction survives cross-validation**: Untested → Supported. Bootstrap, k-fold CV, train/test all confirm stability.
- **C contains unique information not captured by mobility proxies**: New entry, Supported.
- **Mobility causes recovery**: Weakened. Mobility proxies do not predict recovery beyond C+friction.
