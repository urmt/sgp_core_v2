# RD-10B.J5: Dependency Topology Audit — Report

## Status: COMPLETE

---

## Question

> What is the structure of the dependency among the four junctions?

---

## Dependency Matrix

|  | distinction | constraint | preservation | recursion |
|--|-------------|------------|--------------|-----------|
| distinction | -- | -- | -- | -- |
| constraint | YES | -- | -- | -- |
| preservation | YES | YES | -- | -- |
| recursion | YES | YES | YES | -- |

---

## Dependency Counts

| Junction | Depends on | Depended by |
|----------|------------|-------------|
| distinction | nothing | constraint, preservation, recursion |
| constraint | distinction | preservation, recursion |
| preservation | distinction, constraint | recursion |
| recursion | distinction, constraint, preservation | nothing |

---

## Topology Analysis

- **Root**: distinction (no dependencies)
- **Leaf**: recursion (depended on by nothing)
- **Cycles**: None
- **Symmetric pairs**: None
- **Asymmetric pairs**: All 6 pairs

---

## Topological Order

From root to leaf: distinction → constraint → preservation → recursion

This is a **linear chain** (Outcome A).

---

## Interpretation

### What This Shows

The four junctions form a strict dependency hierarchy:

1. **Distinction** is primitive (depends on nothing)
2. **Constraint** depends on distinction
3. **Preservation** depends on distinction and constraint
4. **Recursion** depends on all three

### What This Does NOT Show

This does not show that the junctions form a process chain. Dependencies and process order are different structures.

A dependency graph tells us what requires what.
A process chain tells us what transforms into what.

### The Narrow Claim

The narrow claim that survives:

> The four candidate junctions are not independent. They form a strict dependency hierarchy with distinction at the root and recursion at the leaf.

### The Compression

The compression hypothesis gains support. If recursion depends on all three others, and distinction depends on none, then the four junctions are not four independent discoveries — they are four aspects of a single dependency structure.

---

## Files

- `audits/rd10bj5_topology.py` — experiment code
- `audits/rd10bj5_results.json` — results
- `audits/RD10BJ5_TOPOLOGY.md` — this report
