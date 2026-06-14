# RD-HIST.2A — Open Coding Audit Report

## Purpose

Determine whether any currently favored survivor (persistence, interaction, translation, comparison) still emerges when all explanatory vocabulary is removed and only operational change remains.

## Method

1. Selected 20 studies: 10 from RD-HIST.1 (coded), 10 unclassified (balanced: 3 successes, 3 failures, 2 abandoned, 2 ambiguous)
2. Created blind packets: stripped all identifiers, theoretical language, narrative
3. Performed open coding with three questions:
   - Q1: What appears to be doing the explanatory work?
   - Q2: Could the same result be described without introducing a new explanatory object?
   - Q3: What changed between the beginning and the end? (one sentence, operational language only)
4. Clustered Q3 responses into emergent categories
5. Ran null compression test (A/B/C)
6. Compared to RD-HIST.1 for the 10 coded studies

## Key Findings

### 1. No Single Category Dominates

The Q3 responses cluster into 5 categories with no dominant winner:

| Category | Count | Frequency |
|----------|-------|-----------|
| Generation and Testing | 5 | 25% |
| Classification and Categorization | 4 | 20% |
| Variation and Measurement | 4 | 20% |
| Comparison and Reinterpretation | 4 | 20% |
| Removal and Degradation Testing | 3 | 15% |

**The archive does not converge on one type of change.**

### 2. Persistence Does Not Survive Blind Coding

For the 10 coded studies, RD-HIST.1's locus assignments matched blind coding in only 1 case (Study 5, RD-10B.0). The most common mismatch: RD-HIST.1 says "Persistence" but blind coding says "Classification" (3 studies).

**Persistence is an interpretation, not an operational description.**

### 3. The Ontology Carries Real Information (But May Be Overbuilt)

Null compression test results:
- Compression A (5 categories): No information lost
- Compression B (4 categories): Moderate information lost
- Compression C (2 categories: change/no-change): Almost all information lost

**The 5-category ontology is not overbuilt.** But Compression B (4 categories) preserves most structure while being simpler. The question is whether 4 or 5 categories is the right level.

### 4. All Studies Show Change

Every study in the sample involved some type of change. No study showed "no change occurred." This means Compression C (change/no-change) has zero discrimination power.

**The binary distinction is useless.** The ontology is necessary.

### 5. The Strongest Survivor

The strongest statement that survives blind coding is:

> **The archive shows multiple types of change, with generation/testing being slightly more common (25% vs 15-20% for other types).**

This is much weaker than:
- "Hierarchical persistence of interaction"
- "Persistence is the most common locus"
- "Explanatory gain occurs when a system acquires a new way to relate descriptions"

But it has the advantage of being directly supported by the data without interpretation.

## What Changed (Sorted by Frequency)

| What Changed | Count | Studies |
|--------------|-------|---------|
| Universes/worlds were generated and patterns/features were measured | 5 | 2, 11, 12, 16, 17 |
| Items were classified/categorized into groups based on shared properties | 4 | 1, 3, 4, 20 |
| A parameter was varied and the effect on outcomes was measured | 4 | 7, 8, 13, 15 |
| Multiple descriptions were compared or reinterpreted through a new lens | 4 | 5, 9, 10, 19 |
| Components were removed or degraded to test whether function persisted | 3 | 6, 14, 18 |

## Survivor Ladder

| Level | Categories | OCR | Information Lost |
|-------|------------|-----|------------------|
| Raw Q3 responses | 20 | 1.0 | None |
| Clustered responses | 5 | 4.0 | Some nuance |
| Compression A (5 categories) | 5 | 4.0 | None beyond clustering |
| Compression B (4 categories) | 4 | 5.0 | Moderate - one category lost |
| Compression C (change/no-change) | 2 | 10.0 | Almost all nuance lost |

**OCR = Studies correctly classified / Number of categories**

**Highest compression that preserves explanatory structure:** Compression B (4 categories)

## Operational Compression Ratio Analysis

The OCR measures how many studies each category captures on average:
- Raw: 1.0 (each category captures 1 study)
- Emergent/Compression A: 4.0 (each category captures 4 studies)
- Compression B: 5.0 (each category captures 5 studies)
- Compression C: 10.0 (each category captures 10 studies)

**OCR jumps between levels:**
- Raw → Emergent: 4x increase (large jump - clustering loses specificity)
- Emergent → Compression A: no change
- Compression A → Compression B: 1.25x increase (small jump - similar information)
- Compression B → Compression C: 2x increase (large jump - binary compression loses specificity)

**Key finding:** The 4-category and 5-category ontologies carry similar information (OCR 4.0 vs 5.0). The binary ontology (OCR 10.0) is too broad to be useful.

## Implications

1. **RD-HIST.1's conclusions were interpretation-sensitive.** The coding layer was not blind. When the ontology is removed, the conclusions change.

2. **Persistence is not the dominant pattern.** It was a coding artifact, not a property of the archive.

3. **The archive is methodologically diverse.** It shows multiple types of change, not one dominant type.

4. **The weakest surviving statement** is: "The archive shows multiple types of change, with generation/testing being slightly more common."

5. **This statement is safer** than any previous survivor because it makes no claim about what causes explanation, what persists, or what is fundamental. It just describes what the archive shows.

## Next Steps

1. Test whether this weaker statement survives exposure to more studies
2. Test whether the 5-category ontology is stable across different coding samples
3. Test whether the pattern holds in concrete systems (granular worlds)
4. Determine whether the methodological diversity is a feature or a bug

## Files Produced

- `RD_HIST_2A_SELECTED_STUDIES.json` — 20 selected studies
- `RD_HIST_2A_BLIND_PACKETS_MANUAL.json` — Clean blind coding packets
- `RD_HIST_2A_OPEN_CODING.json` — Q1/Q2/Q3 responses for all 20 studies
- `RD_HIST_2A_Q3_RAW.md` — Raw Q3 responses in randomized order (audit trail)
- `RD_HIST_2A_Q3_CLUSTERS.json` — Emergent categories and "what changed" table
- `RD_HIST_2A_NULL_COMPRESSION.json` — Compression test results
- `RD_HIST_2A_COMPARISON.json` — Comparison to RD-HIST.1
- `RD_HIST_2A_SURVIVOR_LADDER.json` — Information loss and OCR across compression levels
- `RD_HIST_2A_REPORT.md` — This report
