# RD-10B.M1: Migration Audit — Report

## Status: COMPLETE

---

## Question

> Is explanatory migration a genuine regularity or an artifact of audit construction?

---

## Part 1: Historical Reconstruction

| Audit | Initial Explanation | Later Explanation | Migrated? |
|-------|--------------------|--------------------|-----------|
| RD-5 | C predicts resilience | C is projection of MSE | YES |
| RD-9E | SP measures novelty | SP is binary artifact | YES |
| RD-10A.1-6 | Properties enable organization | Constraints more fundamental | YES |
| RD-10A.8 | Constraint set matters | Topology matters more | YES |
| RD-10A.9 | Topology is fundamental | Distinctions more fundamental | YES |
| RD-10A.10 | Distinctions are fundamental | Preservation more fundamental | YES |
| RD-10A.11 | Preservation is fundamental | Construction/preservation axis | YES |
| RD-10A.12 | Construction/preservation fundamental | Lens participation | YES |
| RD-10B.3 | Detectors measure architecture | Detectors measure time-series | YES |
| RD-10B.0 | Motifs are world properties | World-representation pair | YES |
| RD-10B.0A | Representations correspond | Correspondence varies | YES |
| RD-10B.0B | "Same world" unified | Criteria disagree | YES |
| RD-10B.0C | Criteria are competing | Criteria are task-specific tools | YES |
| RD-10B.0D | Causal identity universal | Fails 60% of time | YES |
| RD-10B.0E | Criteria have domains | Domain specificity | YES |
| RD-10B.0F | Worlds are neutral | Worlds have hidden assumptions | YES |
| RD-10B.X | Recursion is junction | Junctions may be vocabulary-dependent | YES |
| RD-10B.J4 | Junctions are independent | Junctions form dependency chain | YES |
| RD-10B.J6 | Distinction is generator | Generator is decomposition-dependent | YES |
| RD-10B.J7 | Compression is invariant | Invariant may be translation-dependent | YES |

**Migration rate: 20/20 (100%)**

---

## Part 2: Counterexample Search

Very few counterexamples found:
- C ≈ -MSE: stayed local to granular domain
- Topology result: survived but interpretation migrated
- Causal intervention result: survived as negative result

Most explanations migrated within 1-2 audits.

---

## Part 3: Null Model

**Fixed methodology chain:**
1. Measure C: C = 0.45
2. Measure MSE: MSE = 0.32
3. Check correlation: r(C, MSE) = -0.89
4. Conclusion: C ≈ -MSE
5. Next audit: Same methodology
6. Result: C ≈ -MSE again

**No migration occurred when methodology was fixed.**

**Key insight:** Migration appears when methodology changes. Migration does not appear when methodology is fixed.

---

## Part 4: Migration Topology

**Migration graph:**
- 20 migrations tracked
- 18 unique destinations
- 8 possible cycles detected

**Attractors (nodes with most incoming edges):**
- topology: 2 incoming
- All others: 1 incoming

**Most common category shifts:**
- objects → relations: 3
- relations → structure: 2
- All others: 1

---

## Verdict

### Two Possible Explanations

**A. Genuine regularity:** Explanatory power genuinely migrates upward when systems become more complex.

**B. Methodological artifact:** Each audit changes the measurement tool, which changes what can be explained.

### What the Evidence Shows

The null model suggests **B is more likely**. Migration appears when methodology changes. Migration does not appear when methodology is fixed.

### What This Does NOT Rule Out

It does not fully rule out A. It may be that methodology changes are necessary to reveal genuine migrations.

### The Strongest Conclusion

The migration pattern is **correlated with methodology changes**. Whether it is also a genuine regularity remains open.

---

## Implications

### For the Program

The migration pattern has survived more audits than any specific finding. But it may be an artifact of how audits are constructed.

### For RD-10B

The strongest finding is not any junction, decomposition, or invariant. The strongest finding is that **explanatory power migrates when methodology changes**.

### The Open Question

Is this migration:
- A property of the systems studied?
- A property of the audit methodology?
- A property of the interaction between systems and methodology?

This question cannot be resolved by further audits of the same type.

---

## Files

- `audits/rd10bm1_migration.py` — experiment code
- `audits/rd10bm1_results.json` — results
- `audits/RD10BM1_MIGRATION.md` — this report
