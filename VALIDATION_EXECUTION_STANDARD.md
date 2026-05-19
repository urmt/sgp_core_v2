# VALIDATION EXECUTION STANDARD — SGP-CORE V2

**Date:** 2025-05-13

---

## Two-Phase Execution

### PHASE A: Quick Validation

**Purpose:** Sanity check before large runs

Requirements:
- N ≤ 1000
- k-range ≤ 100
- Trials ≤ 10
- Time < 60 seconds
- Must pass null comparison

**Must include:**
1. Runtime check (no crashes)
2. Output sanity (D(k) in valid range)
3. Model convergence (fit succeeds)
4. Null comparison (effect size computed)
5. Metadata generation (provenance logged)

**Pass Criteria:** All checks pass → Proceed to PHASE B  
**Fail Criteria:** Any check fails → STOP, diagnose, retry

### PHASE B: Full Execution

**Requirements:**
- N ≤ 10000
- k-range ≤ 500
- Trials ≥ 100
- Full null suite

**Pass Criteria:** 
- Effect size > null with p < 0.05
- Bootstrap stability (CV < 0.2)
- Reproducible with different seeds

---

## Execution Template

```python
def run_experiment(config):
    # PHASE A: Quick validation
    if not quick_validation(config):
        print("VALIDATION FAILED - STOPPING")
        return None
    
    # PHASE B: Full execution
    results = full_execution(config)
    
    # Always compare with null
    null_comparison = compare_with_null(results)
    
    if not null_comparison.significant():
        print("No significant effect - STOPPING")
        return null_comparison
    
    return results
```

---

## Required Checks

| Check | Failure Action |
|-------|---------------|
| Runtime | STOP |
| D(k) range | STOP |
| Convergence | STOP |
| Null effect | STOP |
| Bootstrap stability | FLAG |

---

## Metadata Requirements

Every run MUST log:
- Config parameters
- RNG seed
- Runtime duration
- System specs
- Input hash
- Output hash

---

## Status

**STANDARD DEFINED**  
All pipelines must follow this protocol