# RD-10B.0D: Failure-Mode Audit — Report

## Status: COMPLETE

---

## Question

> **Under what conditions does each criterion stop working?**

---

## Standing Rule Applied

> **Whenever something looks fundamental, ask what makes it possible.**
> **Under what conditions does it stop working?**

---

## Results

### Success/Failure Rates

| Criterion | Successes | Failures | Failure Rate |
|-----------|-----------|----------|--------------|
| predictive | 10/10 | 0/10 | 0% |
| intervention | 10/10 | 0/10 | 0% |
| counterfactual | 10/10 | 0/10 | 0% |
| information | 10/10 | 0/10 | 0% |
| causal | 4/10 | 6/10 | 60% |

### Failure Mode: Causal Identity

**When it fails:** When the system lacks long-range dependencies (dependencies are random).

**What becomes invisible:** Long-range dependencies.

**Invariant under:** Time reversal.

**Broken by:** Randomness.

### Invariant Transformations

| Criterion | Invariant Under | Broken By |
|-----------|-----------------|-----------|
| predictive | temporal_reversal | chaos |
| intervention | agent_permutation | uniform_response |
| counterfactual | deterministic_systems | stochasticity |
| information | deterministic_transformations | information_loss |
| causal | time_reversal | randomness |

---

## Critical Finding

### Causal Identity Is the Most Fragile

Causal identity fails 60% of the time. All other criteria succeed 100%.

The failure mode is informative: **causal identity is uninformative when dependencies are random.**

This means:
- Causal identity is only useful for systems with structured dependencies
- For random systems, causal identity provides no information
- The other criteria are more robust

### The Failure Is the Discovery

The program has repeatedly learned:

> **The most reliable discoveries come from asking: "Under what conditions does this stop working?"**

Causal identity stops working when dependencies are random.
This is not a bug. It is a boundary condition.

---

## Implications

### For RD-10B

1. **Causal identity is context-dependent** — it only works for systems with structured dependencies
2. **Other criteria are more robust** — they succeed even when causal identity fails
3. **The failure mode is informative** — it reveals the boundary conditions of causal reasoning

### For the Program

The deepest insights come from studying failure modes, not successes.

When a criterion fails, it reveals:
- What distinctions become invisible
- What transformations break it
- What boundary conditions limit its applicability

---

## The Deeper Lesson

> **Under what conditions does this stop working?**

That question has repeatedly produced deeper insights than attempts to identify the next foundation.

Causal identity stops working when dependencies are random.
This is a discovery about the limits of causal reasoning.

---

## Files

- `audits/rd10b0d_failure_mode.py` — experiment code
- `audits/rd10b0d_results.json` — results
- `audits/RD10B0D_FAILURE_MODE.md` — this report
