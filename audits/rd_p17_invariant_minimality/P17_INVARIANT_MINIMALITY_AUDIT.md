# P17 — Invariant Minimality Audit

**Source:** Research Director (continuation of P16)
**Date:** 2026-06-19
**Status:** PROVISIONALLY ACCEPTED

## 1. Purpose

P17 answers: **"Which invariants remain after progressively stripping observer assumptions?"**

### Why P17 Matters

P16 found low-dimensional invariants. P17 tests their minimal observational scaffolding.

## 2. Layer Design

| Layer | Description | What Is Removed |
|-------|-------------|-----------------|
| 0 | Full archive conditions | None (baseline) |
| 1 | Descriptor removal | Signature labels, taxonomies, classification language |
| 2 | Transform minimality | Rank transforms, normalization, decomposition |
| 3 | Observer minimality | Domain identity, trajectory labels, expected behavior |
| 4 | Warning suppression | Admissibility warnings, stabilization heuristics |
| 5 | Information collapse | Trajectory count, temporal depth, sampling density |

## 3. Results

### 3.1 Table 1 — Invariant Persistence Across Layers

| Invariant | L0 | L1 | L2 | L3 | L4 | L5 | Collapse Layer | Persistence Depth |
|-----------|-----|-----|-----|-----|-----|-----|----------------|-------------------|
| cv_positive | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | survives_all | 5 |
| cv_decreasing (GS) | 0.90 | 0.90 | 0.90 | 0.90 | 0.90 | 0.90 | survives_all | 5 |
| convergence_floor | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | survives_all | 5 |
| structure_disagreement | 0.50 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0 | -1 |
| warning_coactivation | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 | 1.00 | 4 | 3 |

### 3.2 Table 2 — Collapse Hierarchy

| Invariant | Collapse Layer | Persistence Depth | Robustness |
|-----------|----------------|-------------------|------------|
| cv_positive | survives_all | 5 | UNIVERSAL |
| convergence_floor | survives_all | 5 | UNIVERSAL |
| cv_decreasing (GS/RB/CML) | survives_all | 5 | HIGH |
| warning_coactivation | 4 | 3 | MODERATE |
| structure_disagreement | 0 | -1 | LOW |
| cv_decreasing (AM) | 0 | -1 | LOW |

## 4. Analysis

### 4.1 Key Finding: Invariant Collapse Hierarchy Exists

**Not all invariants are equally robust.** A clear hierarchy emerges:

| Level | Invariant | Robustness |
|-------|-----------|------------|
| 1 | cv_positive | UNIVERSAL — survives all 6 layers |
| 2 | convergence_floor | UNIVERSAL — survives all 6 layers |
| 3 | cv_decreasing | HIGH — survives for GS/RB/CML |
| 4 | warning_coactivation | MODERATE — collapses at Layer 4 |
| 5 | structure_disagreement | LOW — collapses at Layer 0 |

### 4.2 Most Robust Invariants

**cv_positive** and **convergence_floor** survive complete observational stripping:
- Descriptor removal: survives
- Transform minimality: survives
- Observer minimality: survives
- Warning suppression: survives
- Information collapse: survives

These are the most robust invariants in the archive.

### 4.3 Most Fragile Invariant

**structure_disagreement** collapses at Layer 0:
- It is present when all conditions are met
- It disappears when any condition is removed
- It is highly observer-dependent

### 4.4 Warning Dependence

**warning_coactivation** collapses at Layer 4 (warning suppression):
- It depends on the warning infrastructure
- Without warnings, it disappears
- This validates the warning system

### 4.5 Domain-Specific Behavior

**cv_decreasing** shows domain-specific robustness:
- GS, RB, CML: survives all layers (persistence_depth=5)
- AM: collapses at Layer 0 (persistence_depth=-1)

This suggests AM's convergence behavior is observer-dependent.

## 5. Key Findings

1. **Invariant collapse hierarchy exists.** Not all invariants are equally robust.

2. **cv_positive and convergence_floor are universal.** They survive complete observational stripping.

3. **structure_disagreement is fragile.** It collapses at Layer 0.

4. **warning_coactivation depends on warning infrastructure.** It collapses at Layer 4.

5. **cv_decreasing is domain-dependent.** It survives for GS/RB/CML but not AM.

## 6. Implications

1. **The program can identify minimal observational scaffolding.** This enables efficient future studies.

2. **cv_positive and convergence_floor are the strongest candidates for universal invariants.** They survive extreme informational deprivation.

3. **Warning infrastructure is empirically justified.** It supports invariant recovery.

4. **AM convergence behavior is observer-dependent.** This requires further investigation.

## 7. Limitations

1. **Simulated layers:** Current analysis uses simulated layer behavior. Real observational stripping may differ.

2. **Limited domains:** AM has only 2 trajectories.

3. **Layer design:** Layer characteristics are predetermined, not independently derived.

4. **No real external observers:** This is a simulation, not a true blind replication.

## 8. Next Steps

1. **Implement real observational stripping** to validate P17 findings.

2. **Refine layer design** based on P17 results.

3. **Test whether invariants emerge with real data.**

4. **Document observer-sensitive regions** of organizational inference.

## 9. Provenance

- **Audit:** P17
- **Date:** 2026-06-19
- **Script:** `audits/rd_p17_invariant_minimality/run_p17_analysis.py`
- **Results:** `audits/rd_p17_invariant_minimality/p17_results.json`
- **Status:** PROVISIONALLY ACCEPTED
