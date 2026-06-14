# Prediction vs Causation

Explicit separation of what is known predictively versus causally for each model.

---

## Model A: C-causal

**Claim**: Coherence C is a causal driver of recovery. Higher C → better recovery because C mechanically facilitates interaction structure restoration.

### What we know (predictive)

- C predicts ΔC with R² = 0.10 (p ≈ 0.01)
- High-C (Q4) runs always have restoration > 1.0 (0 counterexamples in 15)
- C contributes to the interaction model: C + friction + C:friction reaches R² = 0.52 (ΔC)
- C outperforms competitor metrics (I_pred, C_sigma, MSE) for perturbation detection

### What we do not know (causal)

- Whether the predictive relationship is causal or merely correlational
- Whether manipulating C directly (without changing friction/dynamics) would change recovery
- Whether the interaction term reflects genuine C×motion synergy or C-as-friction-proxy

### What would falsify Model A

| Falsification | Status | Experiment |
|---------------|--------|------------|
| Manipulate C without changing recovery | **Untested** | Intervention: fix friction, vary polydispersity to shift C; measure recovery |
| C fails to predict recovery when friction is controlled | **Partial** — within-friction, C sometimes reverses (higher C → slower recovery at friction ≥ 0.4) |
| Same C produces opposite recovery | **Confirmed** — C=0.43–0.44 predicts both ΔC increase and decrease depending on friction |
| C not necessary for good recovery | **Confirmed** — 5/15 low-C runs have restoration > 1.2 |

**Model A is already partially falsified.** The last two rows are fatal to the strong version of Model A (C alone determines recovery). A weaker version (C partially causes recovery, interacting with friction) remains possible but cannot be distinguished from Model D without an intervention experiment.

---

## Model B: Mobility-only

**Claim**: Only mobility matters. C is a downstream consequence of mobility with no independent role in recovery.

### What we know (predictive)

- Friction predicts ΔC (R² = 0.30), τ_rec (R² = 0.18), restoration (R² = 0.23)
- Low friction (high mobility) always produces fast recovery (τ_rec ≈ 37)
- C and friction are correlated at r = −0.89

### What we do not know (causal)

- Whether friction's predictive power is causal (friction is a parameter we set, so it is intervention-defined, but we have not tested whether the friction → recovery pathway is mediated by mobility or by C)
- Whether mobility proxies (MSD, RMS velocity) capture the same information that friction provides or something different

### What would falsify Model B

| Falsification | Status | Experiment |
|---------------|--------|------------|
| C predicts recovery when friction is fixed | **Mixed** — within-friction, C sometimes reverses (higher C → slower τ_rec at friction ≥ 0.4) |
| Additive model (C + friction) outperforms friction-only | **Confirmed** — ΔR² = +0.13 (ΔC), +0.13 (τ_rec), +0.27 (restoration) over friction-only |
| Interaction model outperforms additive | **Confirmed** — ΔR² ≈ +0.09 (ΔC), +0.04 (τ_rec), +0.06 (restoration) over additive |
| C adds information when mobility is controlled | **Confirmed** — interaction term survives addition of MSD, RMS velocity, and turnover |

**Model B is falsified by the additive and interaction model results.** C adds information beyond friction alone (ΔR² = +0.13–0.27 for C+F vs friction-only). However, "adds information" ≠ "is causal" — C could simply be a better measure of friction's effects on structure.

---

## Model C: Interaction (C × Mobility)

**Claim**: Coherence and mobility jointly determine recovery. C matters more when mobility is high; mobility matters more when C is low.

### What we know (predictive)

- Interaction model (C + friction + C:friction) achieves highest R² for all three targets
- Interaction term is significant for ΔC (p = 0.0015) and restoration (p = 0.0057)
- Interaction survives addition of any mobility covariate for ΔC and restoration
- Sign reversal is consistent with interaction: C helps at low friction, hurts at high friction

### What we do not know (causal)

- Whether the interaction is genuine (C and mobility synergize) or an artifact of the C–friction correlation
- Whether cross-validation would shrink the interaction term
- Whether the interaction would survive decoupling C and mobility

### What would falsify Model C

| Falsification | Status | Experiment |
|---------------|--------|------------|
| Cross-validation: interaction R² drops to additive model levels | **Untested** | k-fold CV on existing 60-run dataset |
| Decoupling: when C and mobility are independently varied, interaction disappears | **Untested** | Polydispersity × friction experiment (P1) |
| Interaction not significant out-of-sample | **Untested** | Holdout validation |

**Model C remains the best-supported predictive model but is untested causally.** All falsifications are untested. The model's predictive success is robust to mobility covariates, but whether this reflects genuine synergy or C as a friction proxy cannot be resolved with current data.

---

## Model D: C-as-thermometer (state descriptor)

**Claim**: C is an informative but non-causal state variable. It measures interaction structure. Recovery is driven by the underlying dynamics (mobility). C tags along.

### What we know (predictive)

- Everything currently known is consistent with Model D
- C detects perturbations (a thermometer detects temperature changes)
- C discriminates structure (a thermometer discriminates hot from cold)
- C predicts recovery (temperature predicts ice melting, but doesn't cause it)
- High-C conditions = good recovery (because same conditions that produce high structure also produce high mobility)

### What we do not know (causal)

- Whether C is genuinely non-causal or only appears non-causal because we haven't tested it
- Whether C could serve as a useful target for intervention (e.g., if we artificially made a system more coherent, would it recover better?)
- Whether C has any causal effect at all, even a small one

### What would falsify Model D

| Falsification | Status | Experiment |
|---------------|--------|------------|
| Manipulating C (fixing dynamics) changes recovery | **Untested** | Intervention: vary polydispersity at fixed friction |
| Interaction term survives decoupling | **Untested** | P1 experiment |
| C predicts recovery in systems where C and mobility are demonstrably independent | **Untested** | P1 experiment or a different system |
| C has predictive power beyond what mobility proxies can explain | **Partially tested** — mobility proxies add nothing beyond C + friction, but the reverse could also mean mobility proxies are poor |

**Model D is the most parsimonious model given current evidence.** It requires fewer causal commitments than Models A or C while explaining all observations. It is falsifiable only through intervention experiments that decouple C from underlying dynamics.

---

## Summary Comparison

| Aspect | A: C-causal | B: Mobility-only | C: Interaction | D: Thermometer |
|--------|:---:|:---:|:---:|:---:|
| Parsimony | Low | High | Low | **Highest** |
| Supported by evidence | **Partially falsified** | **Falsified** | Best predictive fit | **Consistent with all** |
| Causal commitments | Strong | Strong | Strong | **None** |
| Testable with current data | Some tests done | Some tests done | Cross-validation | Only intervention |
| Intervention needed? | Yes | No (friction is already an intervention) | Yes | **Yes** |
| Falsifiable? | **Already partially falsified** | **Already falsified** | Yes (CV + decoupling) | Yes (intervention) |

### What we can conclude

1. **C alone is not sufficient** to predict recovery direction or speed (Model A partially falsified).
2. **Mobility alone is not sufficient** to predict recovery — C adds information beyond friction (Model B falsified).
3. **C × friction interaction is robust** to mobility covariates for ΔC and restoration (Model C's predictive claim supported, causal claim untested).
4. **Model D explains everything Model C explains**, without requiring C to be causal.

### What we cannot conclude

1. Whether C causes, partially causes, merely predicts, or merely describes recovery — this requires an intervention experiment.
2. Whether the interaction term is genuine synergy or an artifact of correlated predictors — this requires cross-validation and/or decoupling.
