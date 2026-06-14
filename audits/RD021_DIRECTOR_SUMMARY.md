# RD-021: Director's Summary

**Date:** 2026-06-06
**To:** Dr. Westhaven
**From:** Research Team
**Re:** RD-021 Velocity-Field Intervention — Outcome V-D

---

## Bottom line

Velocity-field organization hypothesis for C is **FALSIFIED**.

- Velocity diagnostics were sharply manipulated (initial-window F=51–186 across
  align/nbrsim/entropy)
- C did not respond (F=1.15, p=0.34)
- Recovery did not respond (dip p=0.32, restoration p=0.23, τ_rec p=0.10)
- Causal models: ResC β=-2.83, p<0.0001 in restoration model that already
  controls for all 4 velocity diagnostics

---

## Why this matters

This is the **third** consecutive intervention null result. After RD-019
(density) and RD-020 (selective removal), the velocity-field hypothesis was
the last major dynamical candidate. It is now ruled out.

The convergent picture across all 3 interventions:

| Intervention | Manipulation worked? | C changed? | Recovery changed? |
|--------------|----------------------|------------|--------------------|
| RD-019 (density) | YES | NO (F=1.15) | partial (rest p=0.006) |
| RD-020 (selective) | YES | NO (F=2.03) | YES (τ_rec p=0.014) |
| RD-021 (velocity) | YES | NO (F=1.15) | NO (all n.s.) |

C survives as a real, predictive signal. Its physical identity remains
unidentified.

---

## What we have learned

1. **C is not a density-driven state.** Manipulating global density changes
   every structural descriptor (R²≥0.91) but not C.
2. **C is not a contact-topology state.** Manipulating the structural
   skeleton (selective grain removal) does not change C.
3. **C is not a velocity-field state.** Manipulating the kinematic
   organization does not change C.
4. **C is not blocked by any of the above manipulations.** C predicts
   recovery independently of all three. The within-strategy β on restoration
   was -1.998 (RD-020) and -2.83 (RD-021), both p<0.0001.

---

## What the data does not yet rule out

The remaining candidates are not "more of the same" interventions. They are
qualitatively different categories:

1. **C-calculation artifact.** If C is measuring something sensitive to a
   specific implementation choice (binning, threshold, window size), then
   changing the *contact network* or *velocity field* would never affect C
   because C is computed *after* those states are reduced to a scalar via a
   fixed pipeline. This was always the residual hypothesis.

2. **Higher-order correlation structure.** Third- and fourth-order
   interactions among grains, force chains as latent variables, or
   long-range correlations that the structural/velocity diagnostics do not
   capture. Hard to intervene on without breaking physics.

3. **A real but unmeasurable state.** C could correlate with a true physical
   variable that we have not instrumented: e.g., local entropy, force-chain
   buckling mode, contact-slip rate history, energy dissipation rate.

4. **Statistical epiphenomenon.** C could be a real but causally irrelevant
   pattern that happens to correlate with recovery because of shared
   sensitivity to the same unobserved variable (a confounder).

---

## Recommended next steps (in priority order)

### Option A (recommended): Audit the C calculation pipeline

A controlled experiment that varies the C calculation parameters:
- Number of bins (currently fixed)
- Window length (currently 50 frames for time-correlation)
- Perturbation amplitude normalization
- Replicates with shuffled time-order (null control)

This is cheap (~30s of compute), surgical, and directly addresses the
hypothesis that C is a calculation artifact. If C changes with these
parameters while recovery does not, then C is a measurement instrument
sensitivity, not a physical state.

### Option B: Higher-order intervention

Remove a *chain* of grains rather than a single grain (RD-020 tested
individual grains). Or apply a localized shear pulse (a *local*
perturbation, not a global tilt). This probes the assumption that the
relevant "structure" is non-local or cascade-like.

Cost: 60+ runs at ~5s each, ~5 minutes total. Risk: similar negative
result.

### Option C: Confound analysis

Fit a measurement-error model or partial-correlation model that explicitly
separates C's predictive power from its dependence on a hidden common cause.
This is statistically demanding and may not yield actionable insights.

---

## Recommendation

I recommend **Option A** as the immediate next experiment. We have spent
three intervention cycles confirming that C is robust to changes in
structural and dynamical state. Before launching a fourth intervention, we
should verify that C is not an instrument artifact.

If Option A confirms C is calculation-dependent, the program's reframing is
clear: C is a useful *index* but not a *physical state*, and the
restoration-prediction findings should be reported with that caveat.

If Option A confirms C is robust to calculation parameters, we proceed to
Option B (cascade intervention) and accept that C's physical mechanism may
not be approachable via the granular-dynamics intervention paradigm.

Awaiting your direction.

---

## Artifacts

- `audits/rd021_velocity_intervention.py` — simulation
- `audits/rd021_causal_models.py` — analysis
- `audits/RD021_INTERVENTION_REPORT.md` — full report
- `audits/RD021_CAUSAL_MODELS.md` — model details
- `audits/RD021_RESULTS.csv` — per-run data
- `coherence-benchmark/results/rd021_velocity_ensemble.json` — raw data
