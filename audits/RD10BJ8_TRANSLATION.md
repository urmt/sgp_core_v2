# RD-10B.J8: Translation Audit — Report

## Status: COMPLETE

---

## Question

> What properties of the convergence structure are preserved under translation between decompositions?

---

## Translation Maps

Constructed explicit translations between Decomposition A (distinction-based) and Decomposition B (symmetry-based).

---

## What Is Preserved

| Property | Status |
|----------|--------|
| partition structure | PRESERVED |
| restriction structure | PRESERVED |
| invariance concept | PRESERVED |
| fixed point concept | PRESERVED |
| binary output | PRESERVED |
| subset containment | PRESERVED |
| transformation dependence | PRESERVED |
| self-reference | PRESERVED |

## What Is Lost

| Property | Status |
|----------|--------|
| specific operators | LOST |
| specific rules | LOST |
| specific fixed points | LOST |
| decomposition-specific structure | LOST |

---

## Verdict

**Outcome A: Different decompositions preserve the same invariants.**

The convergence structure has genuine invariants. But the invariants are not the junctions themselves — they are the abstract properties that survive translation.

---

## Interpretation

### The Invariants

The preserved properties are abstract enough to survive translation:
- partition structure
- restriction structure
- invariance concept
- fixed point concept
- binary output
- subset containment
- transformation dependence
- self-reference

### The Losses

The specifics are decomposition-dependent:
- specific operators (distinction, symmetry breaking, etc.)
- specific rules (constraint, closure, etc.)
- specific fixed points

### The Strongest Conclusion

The convergence structure is translation-invariant at the level of abstract properties, not at the level of specific operators.

### The Surviving Pattern

Explanatory power keeps migrating upward. Now it has reached: invariants of translation between descriptions.

---

## Files

- `audits/rd10bj8_translation.py` — experiment code
- `audits/rd10bj8_results.json` — results
- `audits/RD10BJ8_TRANSLATION.md` — this report
