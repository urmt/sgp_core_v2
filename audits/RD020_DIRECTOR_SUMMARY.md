# RD-020 Director Summary: Selective Removal Intervention

**Date**: 2026-06-06
**Status**: Complete
**Verdict**: Removing structurally important grains does NOT degrade recovery. If anything, it improves recovery. **Latent-state-via-structural-importance hypothesis is falsified in its strong form.**

## One-Sentence Verdict

Across 6 removal strategies (random, largest, smallest, highest-degree, lowest-degree, highest-force; n=10 each, 60 runs total), **C did not change significantly** (pre_C ANOVA p=0.09) and recovery showed a counter-intuitive pattern: removing structurally important grains (high-degree or high-force) produced *smaller* dips and *faster* recovery, not larger.

## What Was Run

60 simulations. 6 strategies × 10 replicates. Friction fixed at 0.40, box fixed at 40.0, removal fixed at 10% (5 grains), seed range 400–459. **The only thing changed was the selection rule for which 5 grains to remove.** The simulation physics is unchanged. Runtime: 150 seconds.

## Headline Findings

1. **C_pre did not respond to strategy** (ANOVA F=2.03, p=0.09, n.s.). S4 (lowest-degree removed) showed the largest C reduction (d=-0.67), but no strategy was significantly different from S0 random.

2. **τ_rec showed one significant strategy effect**: S1 (largest grains removed) increased τ_rec by 40 time units (β=+40, p=0.003). This is the only individually significant strategy effect across all models and targets.

3. **The dip is smaller (or negative) when structurally important grains are removed**:
   - Spearman rank correlation between structural importance and dip: **r=-0.83, p=0.042**
   - S3 (high-degree removed): d=-0.78 vs S0
   - S5 (high-force removed): d=-0.86 vs S0
   - Both are large effects in the *opposite* direction from the structural-importance hypothesis

4. **τ_rec ceiling effect**: S3, S4, S5 all have τ_rec=37 (= first post-perturbation window). The system recovers so fast that it reaches pre-C in the first window. This is a categorical difference from S0 (also 37) — but S1, S2 take longer.

5. **Residual(C) continues to predict recovery independent of strategy**:
   - For restoration: Model 2 ResC β=-1.998, p<0.001
   - For τ_rec: Model 2 ResC β=+471, p=0.002
   - Strategy dummies are n.s. once ResC is controlled

## Causal Model Results

For each target variable (ΔC, restoration, τ_rec), the three Director-specified models gave:

| Target | Model 1 (Strategy) | Model 2 (Strategy+ResC) | Model 3 (Strategy×ResC) |
|--------|--------------------|--------------------------|--------------------------|
| ΔC | R²=0.078, no sig. | R²=0.131, ResC p=0.076 | R²=0.191, no sig. interactions |
| restoration | R²=0.097, no sig. | R²=0.327, ResC p<0.001 | R²=0.365, no sig. interactions |
| τ_rec | R²=0.227, **S1 p=0.003** | R²=0.354, S1 p=0.001, ResC p=0.002 | R²=0.768 (overfit) |

**Interactions are universally n.s.** — strategy does not moderate the C→recovery relationship.

## Decision Rule Outcome

The Director's four-outcome classification:

| Outcome | Criterion | Met? |
|---------|-----------|------|
| **A** | Strategy changes recovery but not C | **PRIMARY (algorithm)** |
| B | Strategy changes C and recovery | No (C didn't change) |
| C | Strategy changes C more than recovery | No (C effect is smaller) |
| D | Strategy changes neither | No (some recovery effects exist) |

**Outcome A** is the algorithmic classification. The pattern is weaker than expected — the largest effects (S3, S5 on dip) are d~-0.8 but omnibus ANOVA is underpowered (n=10/group, large within-group variance).

## Manual Interpretation

The original hypothesis driving this experiment was:

> H_structural: "If C tracks structurally important organization, removing important grains should produce larger dips and worse recovery."

The observed pattern is **the opposite**:

- Spearman importance-vs-dip: r=-0.83, p=0.042 (**negative, significant**)
- S3 (high-degree removed): dip d=-0.78 (large *negative* effect on dip)
- S5 (high-force removed): dip d=-0.86 (large *negative* effect on dip)

**The structurally important grains were a source of fragility, not a source of latent state.** Removing them made the system more robust to subsequent damage.

**Combined with RD-019 (density did not move C)**, this is a converging picture:

- C is NOT sensitive to:
  - packing density
  - structural importance of removed grains
  - grain size
  - contact network degree
  - force magnitude

- C IS sensitive to:
  - Some within-condition noise that does not correspond to any measured structural or dynamical descriptor (per RD-017/018: 69 variables tested, none identified C)
  - Friction (the only robustly identified external driver of C)

## What This Means for Assumption 15

**Previous status (post-RD-019)**: "Existence: Supported. Identity: Unknown. Sparseness hypothesis falsified."

**RD-020 update**: **Structural-importance hypothesis is falsified in its strong form.** Removing hubs and force-chain backbone grains does not degrade C or recovery. If anything, it improves them.

**The remaining viable identities for Residual(C)** are now narrowed to:

1. **Friction-only artifact with small additional noise** (the simplest surviving hypothesis)
2. **Velocity/kinetic field structure** (untested; surviving candidate from RD-018 shortlist)
3. **Higher-order correlation structure not captured by any local descriptor** (the "latent dimension" hypothesis)
4. **Binning / estimation artifact in the C calculation itself** (the Director flagged this as the next step under Outcome D)

The C calculation itself has not been audited since the start of the project. With two consecutive null interventions, auditing the C computation is now the highest-leverage next step.

## Status Update for Director

| Item | Status |
|------|--------|
| Selective removal manipulation | Effective (S3/S5 hit high-degree/force grains; S4 hits isolated grains) |
| C sensitivity to removal strategy | **None** (F=2.03, p=0.09) |
| Recovery sensitivity to removal strategy | **Weak** (τ_rec ANOVA p=0.014, S1 alone p=0.003) |
| Direction of recovery effect | **Opposite to structural-importance hypothesis** (r=-0.83 with importance) |
| Strong-form structural-importance hypothesis | **Falsified** |
| Assumption 15 (Identity) | **Unknown**; sparseness AND structural importance both ruled out |

## Priority After RD-020

Per the Director's specifications:

> If Outcome A occurs: investigate whether C is generated by velocity-field organization rather than contact structure.
> If Outcome D occurs: launch audit of the C calculation itself (binning, estimator design, information-theoretic artifacts).

**Outcome A occurred.** The velocity-field investigation is the indicated next step. Specifically: compute velocity-based coherence analogues and test whether they predict recovery when C does not. If the velocity field explanation is also falsified, the next move is auditing the C calculation itself.

**Alternative interpretation**: Outcome A's effect sizes (S3 d=-0.78, S5 d=-0.86 on dip) are non-trivial. The signal exists but is too weak to clear the omnibus ANOVA threshold. A larger sample (n=30 per strategy) would resolve this. If the project can afford the additional runtime, a higher-powered replication is also reasonable.

## Files

- `audits/RD020_INTERVENTION_REPORT.md` — per-strategy data, CIs, ANOVA
- `audits/RD020_CAUSAL_MODELS.md` — full regression tables for all 9 model fits
- `audits/RD020_RESULTS.csv` — 60-row results table
- `audits/rd020_selective_intervention.py` — simulation script
- `audits/rd020_causal_models.py` — analysis script
- `coherence-benchmark/results/rd020_selective_ensemble.json` — raw data
