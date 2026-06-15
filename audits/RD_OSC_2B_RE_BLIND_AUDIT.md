# RD-OSC.2B — Re-Blind Audit Report

**Date:** 2026-06-15  
**Auditor:** OpenCode (self-correction)  
**Trigger:** Research Director directive — "True blindness requires three layers."

---

## Summary

| Metric | Original RD-OSC.2 | Re-Blind RD-OSC.2B |
|--------|-------------------|---------------------|
| Packet blinding | 13/20 contained RD labels | 0/20 contained RD labels (residual: "structure", "level", "confirmed") |
| Packet-constrained coding | Max similarity 0.78 | Max similarity 0.53 |
| Clustering agent | Same as coder dispatcher | Independent |
| Coder-assigned cluster agreement | Not measured | **0.0%** (0/20) |
| Analyst-assigned cluster agreement | 100% (post-hoc) | 100% (post-hoc) |
| Substance agreement (manual) | Not measured | **100%** (20/20) |
| Oscillation in shuffled sequence | Claimed structured | **No oscillation** |

---

## Key Finding 1: Substance Agreement Is Real

All 3 coders describe the same findings for all 20 studies. Manual inspection confirms:

- S01: All three describe five criteria tested, some scored high, some low
- S04: All three describe measurement variants predicting the same outcome
- S07: All three describe every shift involving element links
- S12: All three describe causal criterion failing 60%
- S18: All three describe enormous difference space, tiny retained subset

**The coders reliably identify the same findings.**

---

## Key Finding 2: Label Agreement Is Zero

When coders assign their own cluster labels, agreement is 0.0%:

- Coder A: 10 clusters
- Coder B: 5 clusters
- Coder C: 10 clusters

Zero studies have all 3 coders assigning the same cluster label.

**The coders disagree on how to categorize findings, even though they agree on what the findings are.**

---

## Key Finding 3: "100% Agreement" Was Measuring the Wrong Thing

The original RD-OSC.2 claimed "100% inter-coder agreement." This was based on:

1. The same agent that dispatched the coders also did the clustering
2. That agent assigned cluster labels to the coders' responses
3. That agent then declared "100% agreement" based on its own assignment

The re-blind audit reveals this was **analyst self-agreement**, not coder agreement.

When we use the coders' own cluster assignments, agreement is 0%.

When we check substance (manual inspection), agreement is 100%.

**"Agreement" depends on what you mean by "agreement."**

---

## Key Finding 4: No Oscillation in Shuffled Sequence

The shuffled sequence shows no periodic pattern:

- 18 clusters for 20 studies (almost one per study)
- All runs are length 1 (no consecutive repeats)
- No periodic structure

The original oscillation claim (construction → destruction → evaluation → deepening → critique → discovery → meta-discovery → synthesis → ontology) was based on:

1. Non-random study selection (designed to maximize diversity)
2. Chronological ordering (which imposed a narrative structure)
3. Post-hoc clustering (which imposed categories after seeing results)

**When the order is randomized, the oscillation disappears.**

---

## Verdict

### What Survives

1. **Substance agreement is real.** Three independent coders reliably identify the same findings when blinded to RD terminology, conclusions, and identity.

2. **The coders' descriptions are constrained by packet construction.** But less so than the original (max similarity 0.53 vs 0.78).

3. **The studies are genuinely distinct.** Between-study similarity (0.269) is substantially lower than within-study similarity (0.510).

### What Does Not Survive

1. **"100% inter-coder agreement" (as originally claimed).** The coders do not agree on cluster labels. The 100% was analyst self-agreement.

2. **Oscillation structure.** The apparent oscillation was an artifact of chronological ordering and non-random selection.

3. **Structured phases (construction → destruction → evaluation → etc.).** This was a narrative imposed by the analyst, not a measured structure.

### What Remains Under Test

1. **Whether oscillation exists in the CHRONOLOGICAL sequence.** The shuffled sequence shows no oscillation, but the chronological sequence might. This requires a separate test.

2. **Whether the coders' cluster labels can be reconciled.** The coders agree on substance but disagree on labels. Whether this means "no structure" or "different perspectives on the same structure" is unclear.

---

## Corrected Status

**RD-OSC.2B STATUS: COMPLETE**

The following claims are ESTABLISHED:
- Substance agreement is real (100%)
- Label agreement is zero (0%)
- Oscillation in shuffled sequence: not found

The following claims are FROZEN:
- "15 clusters emerged from blind coding" → Now: 18 clusters from independent analysis, 0% coder label agreement
- "100% inter-coder agreement" → Now: 100% substance agreement, 0% label agreement
- "Oscillation structure: real but not periodic" → Now: No oscillation in shuffled sequence
- "Structured phases (construction → destruction → etc.)" → Now: QUALITATIVE INTERPRETATION, NOT ESTABLISHED FINDING

---

## Artifact

`/home/student/sgp_core_v2/audits/RD_OSC_2B_RE_BLIND_AUDIT.md`
