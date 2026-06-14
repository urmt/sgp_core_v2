# RD-10B.M2: Migration Map — Report

## Status: COMPLETE

---

## Objective

> Build a complete dependency graph of every explanatory migration in RD-10B. Determine whether the progression is genuine, methodological, or relational.

---

## Complete Migration Dependency Graph

| Audit | Was Explaining | Became Explanatory | Fixed Variable Exposed | Mapping Replaced |
|-------|---------------|--------------------|----------------------|------------------|
| RD-10B.3 | architectural motifs | detector time-series | detector choice | world → detector → motif |
| RD-10B.0 | motifs | world-representation pair | representation choice | world ↔ representation |
| RD-10B.0A | world identity | correspondence quality | representation pair | rep₁ ↔ rep₂ |
| RD-10B.0B | "same world" | identity criteria | criterion choice | criterion ↔ purpose |
| RD-10B.0C | identity criteria | task-purpose correspondence | task definition | task ↔ criterion |
| RD-10B.0D | causal identity | failure modes | causal criterion | criterion ↔ failure |
| RD-10B.0E | criterion domains | domain specificity | domain boundaries | criterion ↔ domain |
| RD-10B.0F | world behavior | hidden assumptions | world construction | world ↔ assumptions |
| RD-10B.X | recursion as junction | vocabulary independence | vocabulary choice | bottom-up ↔ top-down |
| RD-10B.J4 | four independent junctions | dependency structure | independence assumption | junction ↔ junction |
| RD-10B.J6 | distinction as generator | decomposition dependence | decomposition choice | decomp₁ ↔ decomp₂ |
| RD-10B.J7 | isomorphism class | translation structure | isomorphism definition | generator₁ ↔ generator₂ |
| RD-10B.J8 | translation invariants | translation itself | invariant definition | decomposition ↔ invariants |
| RD-10B.M1 | migration pattern | methodology changes | methodology | methodology ↔ explanation |

---

## Pattern Analysis

**Most common category:** object → mapping (4 times)

**All fixed variables exposed:** Every single one was a methodological or definitional choice.

**All mappings:** Every single one relates two descriptions.

---

## The Progression

### What Was Expected

```
Object → Property → Relation → Transformation → Decomposition → Translation
```

### What Was Found

```
Object → Mapping → Object → Mapping → ...
```

Each time an object becomes explanatory, it is later revealed to be a mapping. Then the mapping becomes the new object. Then the new object is revealed to be a mapping.

**This is not a hierarchy. This is an oscillation.**

---

## Verdict

### Three Possible Interpretations

**A. Genuine empirical progression:** RD-10B is discovering that reality is organized in layers, each built on the previous.

**B. Methodological artifact:** Each audit changes the tool, which changes what can be explained.

**C. Relational structure:** RD-10B is converging toward a translation structure. Not "what is fundamental?" but "what remains invariant when descriptions are translated?"

### What the Evidence Shows

The oscillation pattern (Object → Mapping → Object → Mapping) is more consistent with **C** than with A or B.

- Not A: The progression is not hierarchical
- Not B: The pattern is too regular to be accidental
- C: Each "object" is revealed to be a mapping between descriptions

### The Strongest Conclusion

RD-10B is not converging toward a deepest level. RD-10B is converging toward a translation structure.

**Not: what is fundamental?**
**But: what remains invariant when descriptions are translated?**

This is Path B: the Translation Program.

---

## Implications

### The Fork in the Road

| Path A: Organization | Path B: Translation |
|---------------------|---------------------|
| What produces fertility? | What remains invariant under translation? |
| What enables adaptive complexity? | What is preserved between descriptions? |
| Returns to granular worlds, biology | Becomes theory of representation |

RD-10B has drifted from A toward B, not because anyone planned it, but because every audit keeps pushing there.

### The Strongest Survivor

The strongest finding in RD-10B is not any junction, decomposition, or invariant. It is:

> Whenever two apparently different descriptions can be related by a mapping, explanatory power tends to migrate from the descriptions into the mapping.

This is itself a statement about translation.

---

## Files

- `audits/rd10bm2_migration_map.py` — experiment code
- `audits/rd10bm2_results.json` — results
- `audits/RD10BM2_MIGRATION_MAP.md` — this report
