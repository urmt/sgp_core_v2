# Model D Falsification Attempt

**Objective**: Destroy Model D (C-as-thermometer) — identify every weakness, hidden assumption, statistical flaw, and observation it cannot explain.

**Model D claim**: Underlying dynamics → Mobility → C → Recovery. C is a non-causal readout. Recovery is entirely determined by mobility.

---

## Attack 1: The Interaction Term Survives Mobility Covariates

**Model D prediction**: C should have no independent predictive power after controlling for mobility. If C is purely a thermometer, conditioning on the underlying dynamics should make C and recovery conditionally independent.

**Evidence**: The C × friction interaction term for ΔC has p = 0.0015 in the baseline model. It survives (p < 0.005) when any of MSD, RMS velocity, or neighbor turnover is added as a covariate. 

**Why this attacks Model D**: Under Model D, C and recovery share a common cause (mobility). Conditioning on mobility should render C and recovery independent. It does not. The interaction term remains significant. This is a genuine contradiction.

**Model D defense**: Our mobility proxies (MSD, RMS velocity, turnover) are incomplete. They measure particle-scale kinematics, not the structural capacity to reconfigure. Friction itself is the relevant control — and when we condition on friction, the interaction term captures a nonlinear friction effect, not a C effect. The interaction term uses C:friction, which is essentially friction² (given r(C,friction) = −0.89).

**Counter-defense**: If friction² captures the same nonlinearity, then a quadratic friction model (friction + friction²) should match the interaction model. Test this directly.

**Verdict**: **The interaction surviving mobility covariates is the single strongest observational challenge to Model D.** It demands an explanation D cannot fully provide without invoking inadequate measures.

---

## Attack 2: Mobility Proxies Do Not Predict Recovery

**Model D prediction**: Mobility causes recovery. Therefore, mobility proxies should predict recovery.

**Evidence**: When added to the interaction model, NO mobility proxy significantly predicts any recovery target (all p > 0.10). The additive model C + F + MSD improves R² by only +0.03 over C + F alone (non-significant).

**Why this attacks Model D**: Model D attributes recovery to mobility. If our mobility measures cannot predict recovery, either:
1. Our mobility measures are terrible (admitting we haven't tested D's core claim), or
2. Mobility does not actually cause recovery (contradicting D's core claim)

**Model D defense**: Friction IS the mobility measure. The calligraphic mobility proxies (MSD, RMS velocity) are noisy kinematic measures that do not capture the structural mobility that matters. Friction — a parameter we set — predicts recovery consistently (R² = 0.18–0.30). Under D, friction is the mobility control, and the mobility proxies are red herrings.

**Counter-defense**: If friction is the only valid mobility measure, then the mobility→recovery causal claim rests on a single parameter (friction). But friction also determines C (r = −0.89). Under D, C is a friction-proxy. This means the entire model reduces to: friction predicts recovery, and everything else is redundant. This is actually Model B, which is falsified (C adds information beyond friction).

**Verdict**: **Model D cannot simultaneously claim (a) mobility causes recovery, and (b) our mobility measures are adequate, without explaining why mobility proxies fail to predict recovery.** The only way out is to admit friction is the only valid mobility measure — but then D collapses into B, which is falsified.

---

## Attack 3: C Varies at Fixed Friction

**Model D prediction**: C is determined by the underlying dynamics (captured by friction). At fixed friction, C should be approximately constant.

**Evidence**: At friction = 0.05, C ranges from 0.514 to 0.552 (sd = 0.012). At friction = 0.80, C ranges from 0.338 to 0.445 (sd = 0.036). There is meaningful C variation at fixed friction, driven by microstructure differences (random seed).

**Why this attacks Model D**: If C were purely a friction-proxy, within-friction C variation should be noise. But this within-friction C variation correlates with recovery differences. At friction = 0.40, higher-C runs have systematically different recovery than lower-C runs. If C were a thermometer, within-friction C variation should carry no information about recovery.

**Model D defense**: Within-friction C variation is small (sd ≤ 0.04) and may reflect differences in microstructure that also affect recovery through non-C pathways. The correlation between within-friction C and recovery may be spurious (n = 10 per level).

**Counter-defense**: "Small" depends on the signal. If a C range of 0.34–0.55 across friction levels produces detectable recovery differences, then a C range of 0.02–0.04 within a friction level could plausibly produce within-friction recovery differences. The within-friction reversal at friction ≥ 0.40 (higher C → slower recovery) is reproducible across multiple levels and runs.

**Verdict**: **Within-friction C variation challenges D because it means C captures structure beyond what friction imposes.** D must argue this variation is either noise or redundant with non-C microstructure effects. The available evidence does not settle this, but the burden is on D to show the within-friction C–recovery correlation is spurious.

---

## Attack 4: C Captures Mechanically Relevant Structure

**Model D assumption**: C is a passive readout that does not feed back into dynamics.

**Physical reality**: In the granular DEM, interaction structure (what C measures) determines contact forces. Contact forces determine particle motion. Particle motion determines future interaction structure. **C is not passive — it captures the contact topology that mechanically controls force propagation.**

**Why this attacks Model D**: If C measures the contact network, and the contact network controls how forces propagate after perturbation, then C IS mechanically involved in recovery. The concept of "thermometer" breaks down because the thing being measured (interaction structure) is the same thing that determines the system's mechanical response.

**Model D defense**: The thermometer analogy is limited. What D claims is that C is not independently manipulable — you cannot change C without changing the dynamics. The lack of independent manipulability is the defining feature of a non-causal variable, not whether it captures mechanically relevant structure.

**Counter-defense**: This conflates "not independently manipulable" with "not causal." In complex systems, many causal variables are not independently manipulable (e.g., temperature in a gas is not independently manipulable at fixed volume — you can't change temperature without changing pressure or volume — yet temperature causes pressure changes). The lack of an independent manipulation handle does not establish non-causality.

**Verdict**: **The physical feedback loop between C (interaction structure) and dynamics (particle motion) makes the thermometer analogy misleading.** C is not a passive bystander in the granular system. The philosophical claim of non-causality rests on the manipulability criterion, which is debated in the causation literature.

---

## Attack 5: What Observation Would Be Impossible If Model D Were True?

This is the critical question.

If Model D is true (C is non-causal, recovery is driven by mobility), then the following observations should be impossible:

### 5.1 The clean decoupling experiment

If we fix friction (mobility) and vary polydispersity to shift C, and observe that recovery CHANGES — this would be impossible under D. If C is non-causal, changing C while holding dynamics fixed should not change recovery.

**Status**: Untested. This is the P1 experiment design.

### 5.2 C predicts recovery in a system with zero mobility variation

Take a system where mobility is perfectly uniform across components and cannot change. If C varies across this system and predicts recovery, this is impossible under D.

**Status**: Untested. No such system exists in our testbed.

### 5.3 C predicts recovery better than any possible mobility measure

If we find a mobility measure that demonstrably captures all relevant dynamics, and C still adds predictive power — this is impossible under D.

**Status**: Partially tested. Our best mobility measure (friction, augmented by MSD) does not make C conditionally independent of recovery. But our mobility measures may be inadequate.

### 5.4 Cross-validation: interaction survives

If we cross-validate the interaction model (C × friction) and it consistently outperforms the additive and friction-only models on held-out data — this does NOT falsify D, because D can explain it as C being a non-causal but informative proxy.

**Status**: Untested, and even if confirmed, D can accommodate it.

### 5.5 The sign reversal persists when conditioned on mobility

If we find C=0.44 at friction=0.4 (C increase after perturbation) and C=0.44 at friction=0.6 (C decrease after perturbation), and we can show this is not explained by any mobility difference — this would challenge D.

**Status**: This is exactly what we observe. D's explanation is that the friction difference IS the mobility difference, so the sign reversal is expected. This is consistent with D.

### Summary of impossible observations

| Observation | Would falsify D? | Status |
|-------------|:---:|:--------|
| C manipulation changes recovery at fixed dynamics | **Yes** | Untested (P1) |
| C predicts recovery when mobility is perfectly controlled | **Yes** | Untested (need better mobility measures) |
| C predicts recovery in zero-mobility-variation system | **Yes** | Untested |
| C × interaction survives cross-validation | No | Untested |
| Sign reversal at fixed mobility | Yes | Untested |

**Model D is currently unfalsifiable by existing observational evidence alone.** Every observation we have can be explained by D if we accept that our mobility measures are incomplete. The only definitive falsification requires an intervention experiment where C is manipulated independently.

**This unfalsifiability is itself a weakness.** A model that can explain any observational result is epistemically suspect. D is only a useful scientific model to the extent that it makes testable predictions. Currently, its only testable predictions require interventions we have not performed.

---

## Attack 6: Hidden Assumptions of Model D

| Assumption | Why it's hidden | Why it's problematic |
|------------|-----------------|---------------------|
| Our mobility measures capture all relevant dynamics | Not stated explicitly | If they don't, C's residual predictive power is expected even under D |
| C does not feed back into dynamics | Physically false in granular DEM | D requires ignoring the known physics of the system |
| Friction = mobility | Unstated equivalence | Friction is a parameter that controls damping, not a measure of reconfiguration capacity |
| Mobile systems always recover | Assumed without evidence | At friction=0.05 (maximally mobile), restoration = 1.19–1.27. At friction=0.80 (minimally mobile), restoration = 0.87–1.28. Some low-mobility runs recover better than high-mobility runs. |
| C is a scalar | C treats all interactions as equal | Directional or hierarchical structure may matter for recovery but be invisible to C |

---

## Attack 7: Selection Effects

1. **The 60-run design has 6 friction levels × 10 reps.** Ten reps per condition is minimal for reliable within-condition inference.
2. **"Same C" comparisons across friction levels select runs at the tails of within-friction C distributions.** C=0.44 at friction=0.4 is at the high end; C=0.44 at friction=0.6 is at the low end. These are extreme runs, not representative of typical behavior at each friction level.
3. **The sign reversal (Attack 5 of T902) uses C=0.43–0.44,** which only covers a narrow range of the C spectrum. The reversal may be a local phenomenon that does not generalize to other C values.
4. **Low-friction runs all have high C and fast recovery.** There is no run with high friction, high C, and fast recovery — because high friction produces low C. The quadrant analysis is based on median splits that may not reflect natural categories.

---

## Attack 8: Statistical Weaknesses

1. **n = 60** is small for comparing four competing models with interaction terms.
2. **The interaction term p-values (0.0015–0.07)** are sensitive to outliers. With n=60 a single influential point could change significance.
3. **No correction for multiple comparisons** across three recovery targets and multiple mobility proxies.
4. **Mobility proxies are redundant** with each other (MSD and RMS velocity: r = 0.91) and partially redundant with friction (RMS velocity × friction: r = −0.61). Adding them to the model inflates VIF.
5. **Cross-validation has not been performed.** The reported R² values are in-sample and may overfit, especially for the interaction model with its VIF of 158.

---

## Verdict

Model D is **not dead**. It survives all observational falsification attempts because it can always invoke inadequate mobility measures.

But D is **wounded** by:

1. The interaction surviving mobility covariates (Attack 1) — this is a genuine statistical challenge.
2. Mobility proxies failing to predict recovery (Attack 2) — D's core causal claim is empirically unsupported.
3. The physical feedback loop (Attack 4) — the thermometer analogy is misleading in a system where C captures mechanically relevant structure.

**Most damaging**: D's only escape from Attack 1 and Attack 2 is to claim our mobility measures are inadequate. This is a defensible position but it makes D untestable with current data. A model that cannot be tested observationally is not a good scientific model — it's a philosophical position.

**Final question**: If we treat D as aggressively as we treated A, we must conclude that D has not been falsified (unlike A), but it has been weakened. The decisive test for D is not observational — it's the intervention experiment (P1). Until then, D remains plausible but unfalsified, which is the same status we gave to A's weaker claims.
