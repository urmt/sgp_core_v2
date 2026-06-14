# P1: C-Mobility Decoupling Experiment

**STATUS**: Design only. Do not execute until approved.

---

## Hypothesis

Coherence (C) and mobility are independent properties that jointly determine recovery after perturbation. Specifically:

**H1**: At fixed mobility, varying C produces different recovery outcomes.
**H2**: At fixed C, varying mobility produces different recovery outcomes.
**H3**: The effect of C on recovery depends on the mobility regime (interaction).

The null hypothesis is that C and mobility are not independent — friction is a common cause and the apparent two-factor structure is a collinearity artifact.

---

## Experimental Design

### Parameters

| Parameter | Levels | Rationale |
|-----------|--------|-----------|
| Friction | 0.05, 0.40, 0.80 | Low/moderate/high, spans the recovery regime transition |
| Polydispersity | 3 levels (see below) | Modulates packing structure → C without changing friction |

### Polydispersity Levels

| Level | Radius range | Expected effect on C |
|-------|-------------|---------------------|
| Narrow | [0.95, 1.05] (≈monodisperse) | Highest C at each friction — ordered packing |
| Medium | [0.70, 1.30] | Moderate C — current baseline displacement |
| Wide | [0.50, 2.00] | Lowest C at each friction — maximally disordered |

### Design

- 3 friction × 3 polydispersity = 9 conditions
- 10 replicates per condition = 90 total runs
- Each run: 50 grains, 1000 timesteps, 10% removal at t=500
- Same contact physics as T901 (soft-sphere DEM)

### Technical Adjustments from T901

- Contact detection threshold: change from fixed 3.0 to `2 * max(radius) + 0.5` to handle large grains
- Neighbor turnover contact distance: same dynamic adjustment
- All other parameters identical to T901 for comparability

---

## Falsification Criteria

The experiment succeeds if it creates counterfactual pairs. Define success by:

### Criterion A: C-range overlap

At least 5 pairs across friction levels with |ΔC| ≤ 0.01 (same C).

Expected:
- Narrow poly at friction=0.40: C ≈ 0.46–0.48
- Wide poly at friction=0.05: C ≈ 0.46–0.49
- Overlap in C range would create same-C/different-mobility pairs

### Criterion B: Within-friction C spread

At least 0.03 C range within each friction level across polydispersity conditions.

Expected:
- At friction=0.05: C range [narrow vs wide] ≥ 0.03
- At friction=0.40: C range [narrow vs wide] ≥ 0.03
- At friction=0.80: C range [narrow vs wide] ≥ 0.02

### Criterion C: Recovery differentiation

For counterfactual pairs (same C/different friction or same friction/different C):
- |Δ(ΔC)| > 0.02 (reliably different dip)
- or |Δτ_rec| > 20 steps (reliably different recovery time)

---

## Expected Outcomes

### If C is causal (recovery = f(C))

- Within each friction level: higher C → better recovery (lower ΔC magnitude, shorter τ_rec, higher restoration)
- Across friction levels: matched-C pairs show similar recovery regardless of friction
- Interaction term in regression: negligible

### If mobility is causal (recovery = f(mobility))

- Within each friction level: C variation does NOT predict recovery differences
- Across friction levels: matched-C pairs differ in recovery if mobility differs
- Interaction term: friction dominates, C has no independent effect

### If interaction is causal (recovery = f(C × mobility))

- Within each friction level: C variation affects recovery, but the effect sign/direction depends on friction level
- At low friction (high mobility): higher C → better or neutral recovery
- At high friction (low mobility): higher C → worse recovery (C-reversal)
- Cross-friction pairs: matched-C shows different recovery, proportional to mobility difference
- Interaction term: significant and survives cross-validation

### If resolution is insufficient (collinearity persists)

- C ranges do not overlap sufficiently across friction levels
- Within-friction C variation < 0.02 (indistinguishable from noise)
- All models perform similarly (cannot distinguish C from friction)

---

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Polydispersity has weak effect on C | Medium | Pre-test with 5-run pilot at friction=0.05 before full 90-run sweep |
| Contact detection fails for large/small grains | Low | Dynamic threshold based on current max radius |
| Wide-polydisperse runs have different contact physics | Low | Small-grain rattling may increase MSD independent of friction — check MSD distribution |
| C overlap insufficient after 90 runs | Medium | If overlap < 5 pairs, add intermediate friction (0.20, 0.60) before polydispersity extremes |

---

## Decision Gates

### Gate 1 (design review)

Before any simulations:
- [ ] Design document approved by Research Director
- [ ] Pilot plan defined (5-run pilot at friction=0.05)
- [ ] Success criteria accepted

### Gate 2 (pilot)

After 5-run pilot at friction=0.05 with 3 polydispersity levels:
- [ ] Narrow-poly C > current-baseline C (polydispersity effect confirmed)
- [ ] Wide-poly C < current-baseline C
- [ ] C range across polydispersity ≥ 0.02
- [ ] Contact dynamics stable at all radii

### Gate 3 (full execution)

If pilot passes:
- [ ] Run 90-run ensemble (3 friction × 3 polydispersity × 10 replicates)
- [ ] Analyze C overlap, recovery differentiation

---

## Analysis Plan (post-execution)

### Step 1: Range validation
- Compute C range per friction × polydispersity condition
- Report overlap matrix showing same-C pairs across friction levels

### Step 2: Recovery comparison
- For each matched pair (same C, different friction): compute Δ(ΔC), Δτ_rec, Δrestoration
- Test: |mean difference| > 0 with 95% CI (bootstrap)

### Step 3: Regression on expanded ensemble
- Fit models A–D on combined T901 + P1 data (up to 150 runs)
- Test: does interaction term survive with higher statistical power?

### Step 4: Causal attribution
- If within-friction C variation predicts recovery: C has independent effect
- If matched-pair differences predict recovery: mobility has independent effect
- Report confidence in each attribution
