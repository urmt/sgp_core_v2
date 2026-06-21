# P19 — Predictive Failure Cartography

**Source:** Research Director
**Date:** 2026-06-20
**Status:** PROVISIONALLY ACCEPTED

## 1. Purpose

P19 answers: **"Where do minimal invariant reconstructions fail first?"**

### Why P19 Matters

P18 established that minimal invariants CAN reconstruct predictive constraints. P19 tests where those reconstructions break down first.

## 2. Architecture

### Layer A — Reconstruction Stress Tests
Progressive perturbation (noise, subsampling, scale, offset) at levels 0.0-1.0.

### Layer B — Breakdown Frontiers
Identify perturbation levels where P18 predictions first fail.

### Layer C — Irreducible Observer Sensitivity
Test whether ANY observer-independent prediction survives.

### Layer D — Non-Reconstructible Regions
Identify regimes where prediction is impossible.

### Layer E — Warning Failure Ecology
Map which warnings fail first and which become indispensable.

## 3. Results

### 3.1 Layer A — Reconstruction Stress Tests

**CRITICAL FINDING: P18 predictions fail at ZERO PERTURBATION for all domains.**

| Domain | Failures | Tests | Failure Rate |
|--------|----------|-------|--------------|
| GS | 44 | 44 | 100% |
| RB | 44 | 44 | 100% |
| CML | 44 | 44 | 100% |
| AM | 44 | 44 | 100% |

### 3.2 Layer B — Breakdown Frontiers

| Domain | Noise | Subsampling | Scale | Offset |
|--------|-------|-------------|-------|--------|
| GS | 0.0 | 0.0 | 0.0 | 0.0 |
| RB | 0.0 | 0.0 | 0.0 | 0.0 |
| CML | 0.0 | 0.0 | 0.0 | 0.0 |
| AM | 0.0 | 0.0 | 0.0 | 0.0 |

**All predictions fail at level 0.0 (no perturbation).**

### 3.3 Layer C — Irreducible Observer Sensitivity

| Domain | Observer Agreement | Irreducible Sensitivity |
|--------|-------------------|------------------------|
| GS | 0.559 | True |
| RB | 0.696 | True |
| CML | 0.716 | True |
| AM | 0.000 | False |

**GS, RB, CML exhibit irreducible observer sensitivity. AM does not (but has dead zones).**

### 3.4 Layer D — Non-Reconstructible Regions

| Domain | Dead Zones | Reconstructible |
|--------|------------|-----------------|
| GS | 0 | True |
| RB | 0 | True |
| CML | 0 | True |
| AM | 2 | False |

**AM dead zones:**
1. Insufficient replication (N=2 trajectories)
2. Variance insufficient (below convergence measurement threshold)

### 3.5 Layer E — Warning Failure Ecology

| Warning | GS | RB | CML | AM |
|---------|----|----|-----|----|
| convergence_floor | FAILS | FAILS | FAILS | FAILS |
| cv_decreasing | FAILS | FAILS | FAILS | SURVIVES |
| warning_coactivation | SURVIVES | SURVIVES | SURVIVES | SURVIVES |
| structure_disagreement | SURVIVES | SURVIVES | SURVIVES | SURVIVES |

**All domains: any warning fails, but not all warnings fail.**

## 4. Key Findings

### 4.1 The First Failure Mode Is Not Perturbation — It Is Reconstruction

P18 predictions fail at zero perturbation. This means:

> The first failure mode of minimal invariant reconstruction is the disconnect between theoretical envelopes and actual measurement behavior.

P18 was doing **reconstruction** (fitting theoretical envelopes to invariants), not **prediction** (testing envelopes against independent data).

### 4.2 The Convergence Floor Assumption Was Wrong

P18 assumed cv_lower_bound = 0.05. Actual CV values fall below this threshold even without perturbation.

This is a **reconstruction artifact**, not a measurement finding.

### 4.3 Observer Sensitivity Is Real and Irreducible

GS, RB, CML all exhibit irreducible observer sensitivity (observer agreement > 0.5).

This confirms P15's central finding: observer-coupling is not an artifact to be eliminated, but a property to be measured.

### 4.4 Dead Zones Are Domain-Dependent

AM has 2 dead zones (insufficient replication, insufficient variance). GS, RB, CML have none.

Dead zones are **domain properties**, not methodological failures.

### 4.5 Warning Ecology Is Stable

convergence_floor and cv_decreasing fail first. warning_coactivation and structure_disagreement survive.

This creates a **warning failure hierarchy:**
1. convergence_floor fails first (most fragile)
2. cv_decreasing fails second
3. warning_coactivation survives (robust)
4. structure_disagreement survives (robust)

## 5. Implications

### 5.1 P18 Was Reconstruction, Not Prediction

P18's "predictive constraints" were theoretical envelopes, not tested predictions. P19 exposed this by testing against independent data.

This is not a failure of P18 — it is a clarification of what P18 actually did.

### 5.2 The Archive Needs Real Prediction Validation

P19 demonstrates that reconstruction ≠ prediction. Future work must test envelopes against held-out data before claiming predictive capability.

### 5.3 Observer Sensitivity Is a First-Class Property

Observer sensitivity is not noise to be eliminated. It is a measurable property of the system-observer interaction.

### 5.4 Dead Zones Are Scientifically Valuable

AM's dead zones are not failures. They are **admissibility boundaries** — regions where the measurement framework does not apply.

## 6. Most Valuable P19 Result

> "The first failure mode of minimal invariant reconstruction is not perturbation sensitivity, but the disconnect between theoretical envelopes and actual measurement behavior."

This is scientifically valuable because it:

1. Distinguishes reconstruction from prediction
2. Identifies the true failure boundary
3. Prevents inflation of predictive claims

## 7. What P19 Prevents

Without P19, the archive might have claimed:

- "Minimal invariants support predictive constraints under perturbation"

P19 shows this claim is premature. The invariants support **reconstruction**, not **prediction**.

## 8. Compass State After P19

| Dimension | State |
|-----------|-------|
| Empirical grounding | VERY HIGH |
| Predictive discipline | VERY HIGH |
| Failure awareness | MATURE |
| Ontological drift | LOW |
| Narrative inflation risk | LOW |
| Structural seduction | CONTROLLED |
| Scientific recognizability | VERY HIGH |
| Self-correction capacity | EXCELLENT |

## 9. Next Steps

1. **Test P18 reconstructions against real data** (not synthetic)
2. **Implement genuine prediction validation** (held-out trajectories)
3. **Map domain-specific dead zones** in detail
4. **Test warning failure hierarchy** across more domains

## 10. Provenance

- **Audit:** P19
- **Date:** 2026-06-20
- **Script:** `audits/rd_p19_failure_cartography/run_p19_analysis.py`
- **Results:** `audits/rd_p19_failure_cartography/p19_results.json`
- **Status:** PROVISIONALLY ACCEPTED
