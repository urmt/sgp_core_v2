# PHASE J — ORGANIZATIONAL INVARIANTS

## Purpose
Investigate what organizational properties remain invariant under recursive transformational processes. Test for organizational conservation laws.

## Core Research Question
What organizational properties remain conserved while preserving coherent generativity?

## Scripts

| Script | Purpose | Runtime |
|--------|---------|---------|
| `J1_J2_invariants_conservation.py` | Measure transformational invariants; classify conservation vs collapse modes | ~30s |
| `J3_J4_recursive_conservation_laws.py` | Recursive composition chains; operator conservation law testing | ~30s |
| `J5_J6_symmetry_nulls.py` | Symmetry tests (composition, reversibility); null program | ~60s |
| `J7_synthesis.py` | Final synthesis, invariant taxonomy, primary conclusion | ~10s |

## Outputs

| File | Contents | Rows |
|------|----------|------|
| `outputs/phaseJ_transform_invariants.csv` | Property invariance scores across 157 compositions | 1099 |
| `outputs/phaseJ_conservation_collapse.csv` | Conservation classification (maintained/dead/mixed) | 157 |
| `outputs/phaseJ_recursive_conservation.csv` | 200 recursive chains × 6 steps tracking property evolution | 1200 |
| `outputs/phaseJ_operator_laws.csv` | 10 operator conservation law metrics | 10 |
| `outputs/phaseJ_symmetry.csv` | 33 domain-pair symmetry measures | 33 |
| `outputs/phaseJ_nulls.csv` | 30 null iterations × 3 null types | 30 |
| `summaries/phaseJ_synthesis.md` | Full synthesis report | — |
| `summaries/phaseJ_synthesis.json` | Structured synthesis data | — |

## Dependencies
- Phase I: `phaseI_composition_results.csv`, `phaseI_recursive_identity.csv`, `phaseI_operator_signatures.csv`, `phaseI_transition_geometry.csv`
- Phase H2: `recovery_metrics.csv`, `persistence_metrics.csv` (optional)
- Phase C, E, G: for per-domain property extraction

## Key Findings

### 1. Invariant Hierarchy
```
STRONG:  operator_continuity (0.962), coherence (0.960)
WEAK:    reconstruction (0.686), CG_rate (0.650), fertility (0.623)
FRAGILE: reversibility/closure (0.602)
```
Organizational process geometry is deeply conserved. Generative capacity is fragile.

### 2. Conservation vs Collapse
- **maintained_CG**: 24.2% — preserves both geometry and generativity
- **dead_coherence**: 7.6% — geometry preserved but CG collapses
- **mixed_collapse**: 68.2% — partially disrupted

The form-function gap (geometry outlives generativity by 0.111) confirms that organizational geometry is more robust than generative capacity.

### 3. Recursive Convergence
Under repeated composition, organizational properties CONVERGE toward ecosystem averages. CG rate variance shrinks to 30.7% of initial by step 5. Continuity variance shrinks to 13.0%. Identity decays under repeated transformation.

### 4. No Absolute Conservation Laws
The strongest operator (resonance_locking) only preserves 63.7% of CG. No operator conserves CG at >85%. CG is genuinely fragile — there are no organizational conservation laws for generativity.

### 5. Symmetry
Composition is perfectly symmetric (A∘B = B∘A). Geometry and CG are correlated (r=0.545, p<0.001) but not identical. Form-function gap is positive for ALL operators.

### 6. Null Verdict
1/3 nulls survived (shuffled labels within pairs, z=2.49). 2/3 failed (shuffled properties, shuffled pairs). Invariance patterns are largely consistent with random domain pairings at the ecosystem level.

### Primary Conclusion
Organizational process geometry is recursively conserved. But coherent GENERATIVITY is not conserved — it is actively maintained through specific operator configurations (recursive_feedback + resonance_locking at 0.989). CG is a specific organizational configuration, not an attractor of compositional dynamics.
