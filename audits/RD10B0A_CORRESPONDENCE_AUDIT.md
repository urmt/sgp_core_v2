# RD-10B.0A: Representation Correspondence Audit — Report

## Status: COMPLETE

---

## Question

> **When are two representations representations of the same world?**

---

## Standing Rule Applied

> **Whenever something looks fundamental, ask what makes it possible.**

The Representation Audit itself is now looking fundamental.
So the next question is: **What makes representation possible?**

---

## Tests

1. **Information Preservation** — Can you reconstruct one from the other?
2. **Predictive Equivalence** — Do they predict the same future states?
3. **Causal Structure** — Do they preserve causal patterns?

---

## Results

### Correspondence Scores

| Pair | Information | Causal | Combined |
|------|-------------|--------|----------|
| timeseries ↔ phasespace | 0.113 | 0.705 | 0.606 |
| graph ↔ state_transition | 0.050 | 0.724 | 0.591 |
| graph ↔ phasespace | 0.051 | 0.493 | 0.515 |
| timeseries ↔ correlation | 0.209 | 0.000 | 0.403 |
| correlation ↔ phasespace | 0.160 | 0.000 | 0.387 |
| graph ↔ timeseries | 0.078 | 0.061 | 0.379 |
| state_transition ↔ correlation | 0.053 | 0.000 | 0.351 |
| graph ↔ correlation | 0.017 | 0.000 | 0.339 |

### Key Observations

1. **Information preservation is very low** (0.01-0.21) — representations don't encode the same information
2. **Causal structure varies widely** (0.00-0.72) — some pairs preserve causal patterns, others don't
3. **Some pairs correspond much better than others** — suggesting a hierarchy of representation similarity

---

## Critical Finding

### The World-Representation Mapping Is Unstable

The same world, described by different representations, produces:
- Different information content
- Different causal structures
- Different motif measurements (from RD-10B.0)

This is the representation dependence problem, now experimentally observable.

### But Some Pairs Correspond Better

The best correspondences:
- **timeseries ↔ phasespace** (0.606) — both capture temporal dynamics
- **graph ↔ state_transition** (0.591) — both capture relational structure

The worst correspondences:
- **graph ↔ correlation** (0.339) — different aspects of the same world

This suggests that representations are not arbitrary. Some are more similar than others.

---

## The Deeper Question

> **What makes two representations representations of the same thing?**

Possible answers (to be tested):
1. **Information preservation** — they encode the same information
2. **Predictive equivalence** — they predict the same futures
3. **Intervention equivalence** — they respond the same to perturbations
4. **Causal equivalence** — they preserve causal structure

RD-10B.0A suggests that **causal structure** is the most discriminating test.

---

## Implications

### For RD-10B

1. **Detector validation must specify the representation** — detectors calibrated on one representation may not work on another
2. **Motif independence is representation-dependent** — correlations between motifs change across representations
3. **The emergence-first approach must specify the representation** — "what motifs appear?" is meaningless without "in what representation?"

### For the Program

The representation is not a neutral lens. It actively shapes what patterns appear.

This is deeper than detector dependence:
- Detector dependence: the instrument affects the measurement
- Representation dependence: the language affects what can be measured
- Correspondence dependence: what counts as "the same world" depends on the mapping

---

## Next Steps

1. **Refine predictive equivalence test** — the current test is trivially true
2. **Add intervention equivalence** — perturb the world, compare responses
3. **Test across multiple worlds** — is the correspondence hierarchy stable?
4. **Search for representation-invariant properties** — what, if anything, survives all representations?

---

## Files

- `audits/rd10b0a_correspondence_audit.py` — experiment code
- `audits/rd10b0a_results.json` — results
- `audits/RD10B0A_CORRESPONDENCE_AUDIT.md` — this report
