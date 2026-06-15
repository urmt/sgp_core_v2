# RD-OSC.2A — Artifact Audit Report

**Date:** 2026-06-15  
**Auditor:** OpenCode (self-correction)  
**Trigger:** Research Director directive — "The conclusion is ahead of the evidence."

---

## Summary of Findings

| # | Finding | Severity | Impact on "100% agreement" claim |
|---|---------|----------|----------------------------------|
| 1 | Information leakage in blind packets | **HIGH** | Coders saw RD labels ("interaction", "persistence", "distinction", "topology", "constraint", "junction", "motif", "surprise", "novelty") and "gain" in 6 packets |
| 2 | Blind packets pre-determine coding | **HIGH** | Packets are so descriptive that coders paraphrase the packet, not independently observe |
| 3 | Clustering by same agent that ran coders | **HIGH** | Not independent clustering — analyst assigned clusters post-hoc |
| 4 | No assignment matrices | **HIGH** | "Agreement" is analyst assignment, not coder clustering |
| 5 | No clustering algorithm specified | **MEDIUM** | No reproducibility check |
| 6 | No random seeds | **LOW** | Not applicable for manual clustering |
| 7 | High paraphrase similarity (0.78 max) | **MEDIUM** | Coders paraphrase packets, not independently observe |

---

## Finding 1: Information Leakage in Blind Packets

The blind packets contain RD labels that were supposed to be hidden:

| Label | Studies containing it |
|-------|----------------------|
| interaction | S01, S02, S03, S17, S18, S19, S20 |
| persistence | S01, S08, S18, S20 |
| distinction | S01, S02, S10 |
| topology | S09 |
| constraint | S09 |
| junction | S14 |
| motif | S11 |
| surprise | S08 |
| novelty | S07, S18 |
| gain | S05, S08, S09, S12, S17, S20 |

**Impact:** The packets are not truly blind. Coders could have been influenced by these labels.

---

## Finding 2: Blind Packets Pre-Determine Coding

The packets are so descriptive that coders paraphrase the packet, not independently observe.

**Example — S08:**
- Packet: "SP was shown to be a binary artifact of discretization. The phenomenon was not real."
- Coder 1: "An observed phenomenon was tested against measurement parameters and found to be a binary artifact of how the data was discretized, not a real feature."
- Coder 2: "A phenomenon observed in initial measurements was shown to be a binary artifact of how the data was discretized, not a real effect."
- Coder 3: "A phenomenon that looked real turned out to be a side effect of how the data was binned — it disappeared when the binning changed."

All three coders are paraphrasing the packet. The "agreement" is agreement with the packet, not independent observation.

**Paraphrase similarity scores:**
- S08: C1-C2 = 0.78
- S18: C1-C2 = 0.74
- S20: C1-C2 = 0.73
- S10: C1-C2 = 0.72

---

## Finding 3: Clustering by Same Agent That Ran Coders

The OSCILLATION_ANALYSIS.md says:

> "After reading all 60 responses (3 coders × 20 studies) without predefined categories, the following clusters emerged from the content"

This means:
1. The same agent that dispatched the coders also did the clustering
2. Clustering was done AFTER seeing all responses (post-hoc)
3. No independent clustering agent was used
4. No algorithm was specified

---

## Finding 4: No Assignment Matrices

The analysis shows a table of Study → Cluster, but this is the ANALYST assignment, not the CODER assignment.

The coders did not assign clusters. The coders only answered "What changed between the beginning and end of this study?"

The analyst then:
1. Read all 60 responses
2. Defined 15 clusters
3. Assigned each study to a cluster
4. Computed "agreement" based on this assignment

This is not inter-coder agreement. This is the analyst's self-agreement.

---

## Finding 5: No Clustering Algorithm Specified

No distance metric. No linkage method. No reproducibility check.

The "15 clusters" are a manual categorization by one agent, not a computational result.

---

## Verdict

**The "100% inter-coder agreement" claim is not supported by the artifacts.**

What the artifacts show:
1. Three coders received non-blind packets (containing RD labels)
2. The packets were so descriptive that coders paraphrased them
3. One agent (the same one that ran the coders) manually clustered the responses
4. That agent then declared "100% agreement" based on its own clustering

This is not independent blind coding. This is paraphrase detection with post-hoc categorization.

---

## Corrected Status

**RD-OSC.2 STATUS: PROVISIONAL — AWAITING ARTIFACT REVIEW**

The following claims are FROZEN:
- "15 clusters emerged from blind coding"
- "100% inter-coder agreement"
- "Oscillation structure: real but not periodic"
- "15/20 studies show explanation increase"
- "The archive documents its own oscillation"
- "Structured phases (construction → destruction → evaluation → deepening → critique → discovery → meta-discovery → synthesis → ontology)"

**Status: QUALITATIVE INTERPRETATION, NOT ESTABLISHED FINDING**

---

## Recommendations

1. **Redesign blind packets** — Remove all RD labels. Describe only raw data and observations, not interpretations.
2. **Use independent clustering** — A separate agent (not the one that ran the coders) should do the clustering.
3. **Generate assignment matrices** — Coders should assign clusters, not just describe changes.
4. **Specify algorithm** — Use a computational clustering method with explicit distance metric and linkage.
5. **Compute agreement from matrices** — Not from post-hoc analyst assignment.

---

## Artifact

`/home/student/sgp_core_v2/audits/RD_OSC_2A_ARTIFACT_AUDIT.md`
