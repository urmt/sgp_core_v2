# Executive Summary — Causal Attribution Audit (RD-013)

## What is currently supported?

1. **C is an informative state variable** — detects perturbations (SNR = 2.14), discriminates structure (8 testbeds), outperforms competitors (I_pred, C_sigma, MSE).
2. **Interaction-free reconstruction** — IF-3 recovers structure at 90% missing data.
3. **Two-factor prediction** — C × friction model predicts ΔC (R² = 0.52), restoration (R² = 0.56). Interaction term survives all mobility covariates for ΔC and restoration.
4. **Collinearity is real but limited** — C and friction are correlated (r = −0.89), but the interaction term is not a mobility-mediation artifact (partial correlation controlling mobility: r = −0.77).
5. **High C ensures good recovery** — no counterexample found in 15 high-C (Q4) runs.

## What is currently challenged?

1. **C predicts resilience** — C-only model fails for τ_rec (R² = 0.05) and restoration (R² = 0.04). Same C (±0.01) produces 3–4× τ_rec ratios and opposite ΔC signs. Direction is determined by friction, not C.
2. **C and mobility are independent** — friction controls both (r(C,friction) = −0.89). Within-friction C range is narrow (sd ≤ 0.04). No experiment has decoupled them.

## What is currently unknown?

1. **C causes recovery** — zero causal evidence exists. All support is predictive. Model D (C-as-thermometer) explains every observation at least as well as Model A (C-causal), and explains 4 observations strictly better.
2. **C × mobility interaction is genuine** — the interaction survives mobility covariates but VIF (C:friction = 158) is severe. Cross-validation has not been performed.

## What single experiment would most reduce uncertainty?

**Cross-validate Model D** on the existing 60-run dataset (k-fold, bootstrap CIs, train/test split).

This requires zero new simulations, zero new data. If the interaction term collapses out-of-sample, the case for C's causal involvement is substantially weakened. If it survives, the case for a decoupling experiment (P1) is strengthened.

The P1 polydispersity × friction experiment (already designed in `experiments/P1_C_MOBILITY_DECOUPLING_DESIGN.md`) remains the definitive test, but cross-validation should precede it to determine whether new data is even worth generating.

**Expected Information Value (EIV)** of resolving "C is causally involved in recovery" = 10.0 / 10 (importance × uncertainty). This is the maximum possible score. No other assumption comes close — the next highest is 6.0.
