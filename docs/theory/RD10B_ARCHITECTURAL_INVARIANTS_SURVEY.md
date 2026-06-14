# RD-10B: Architectural Invariants Survey

**Status**: DESIGN COMPLETE  
**Date**: 2026-06-10  
**Purpose**: Identify recurrent architectural patterns that accompany major expansions in what differences can persist, matter, and participate in further organization. Test whether those patterns are causally necessary or merely correlated byproducts.

---

## Standing Rules

**Standing Rule 1**

> Whenever something looks fundamental, ask what makes it possible.

**Standing Rule 2**

> Whenever something looks recurrent, ask whether it is causal.

**Standing Rule 3 (RD-10B.3)**

> Whenever a pattern appears, ask whether it belongs to the world, the representation, the detector, or the question.

**Standing Rule 4 (RD-10B.0)**

> When a pattern appears, does it belong to:
> the world, the representation, the detector, the question, or the observer?

**Standing Rule 5 (RD-10B.0A)**

> What makes two representations representations of the same thing?

**Standing Rule 6 (RD-10B.0B)**

> What do you mean by "same"?

**Standing Rule 7 (RD-10B.0C)**

> Whenever something appears fundamental, first determine what work it is doing.

**Standing Rule 8 (RD-10B.0D)**

> Under what conditions does it stop working?

**Standing Rule 9 (RD-10B.0E)**

> Under what conditions is it informative vs. trivial?

**Standing Rule 10 (RD-10B.0F)**

> What assumptions are hidden in the thing doing the measuring?

**Standing Rule 11 (RD-10B.X)**

> Prioritize audits that test whether independently generated chains are converging on the same transformation.

**Standing Rule 12 (RD-10B Complete)**

> The four junctions are distinct and complementary. They work together, not as alternatives.

**Standing Rule 13 (RD-10B.J2)**

> Path independence is necessary but not sufficient. A candidate deserves promotion only when it survives detector changes, representation changes, criterion changes, world changes, and path changes.

**Standing Rule 14 (RD-10B.J3)**

> Vocabulary independence is also necessary but not sufficient. A candidate deserves promotion only when it survives detector changes, representation changes, criterion changes, world changes, path changes, and description-language changes.

**Standing Rule 15 (RD-10B.J4)**

> When multiple junctions appear, test whether they are independent or form a dependency structure. The true junction may be the structure itself, not any individual member.

**Standing Rule 16 (RD-10B.J5)**

> Dependencies and process order are different structures. A dependency graph does not uniquely imply a process chain.

**Standing Rule 17 (RD-10B.J6)**

> When a minimal generating set is found, ask whether the composition rules are genuine or artifacts of the analysis.

**Standing Rule 18 (RD-10B.J7)**

> When a generator is found, test whether it is decomposition-dependent. The genuine structure may be the isomorphism class, not any specific realization.

**Standing Rule 19 (RD-10B.J8)**

> When invariants are found, ask whether they are properties of the structure or properties of the translation between descriptions.

**Standing Rule 20 (RD-10B.M1)**

> When a migration pattern is observed, ask whether it is driven by methodology changes or by genuine regularity.

**Standing Rule 21 (RD-10B.M2)**

> The progression is not hierarchical. It is an oscillation between objects and mappings. Each time an object becomes explanatory, it is later revealed to be a mapping.

**Standing Rule 22 (RD-10B.M6b)**

> Treat descriptions as viewpoints (different perspectives on the same thing), not as claims (competing answers to the same question). Viewpoint comparison preserves tension; claim comparison causes collapse. The fundamental operation is maintaining descriptions as viewpoints.

**Standing Rule 23 (RD-10B.R1, qualified by R2)**

> When reviewing results, explicitly identify what entities are interacting before promoting any explanatory object. Experience occurs at interaction. Objects, properties, mappings, and translations are secondary manifestations of interacting structures. **But**: the archive is biased toward productive interactions. Any audit that reports "no counterexamples" should be immediately suspected of selection bias. The 0.097 correlation between interaction diversity and explanatory gain suggests that more interactions do not guarantee more explanation.

**Standing Rule 24 (RD-10B.R3)**

> Distinguish possible interaction from actual interaction. Possible interaction is not enough. Actual interaction is required for persistent novelty. The theory is not about interaction in general — it is about actual interaction between coherent structures that persist through the interaction.

**Standing Rule 25 (RD-10B.R4)**

> Objects are frozen experience. Interactions are flowing experience. Translation is experience comparing itself to itself. When an object is later revealed to be a mapping, it was a snapshot of an ongoing experience. When a mapping is later revealed to be a deeper object, it was a trace of a deeper experience. The deepest pattern is experience → interaction → objects (as snapshots).

**Standing Rule 26 (RD-10B.R0R)**

> The strongest survivor is hierarchical persistence of interaction. A structure persists when its interactions generate conditions that preserve its continued existence. Each layer survives, becomes a building block, allows new interactions, and creates a larger persistence space. The dividing line between success and failure in the archive is persistence vs non-persistence.

**Standing Rule 27 (RD-HIST.1)**

> When the claimed object keeps changing but the actual locus remains stable, the program is repeatedly discovering the same structure under different names. The Historical Reconstruction showed: Persistence (14 studies) and Comparison (7 studies) are the two most common actual loci. The claimed objects changed; the loci did not. The final compression is: hierarchical persistence of interaction.

**Standing Rule 28 (RD-HIST.2A)**

> The archive is not the territory. It is a record of what the researchers noticed. Any audit reporting "no counterexamples" should be suspected of selection bias. 136 failures were found in the archive. The strongest survivor (persistence) was an interpretation artifact — it did not survive blind coding.

**Standing Rule 29 (RD-HIST.2B)**

> When clustering structure is stable at the aggregate level (category count, OCR, variance) but unstable at the individual level (assignment stability), the categories are interpretation artifacts, not properties of the archive. The structure is in the analysis, not the data.

**Standing Rule 30 (RD-DIAG.1)**

> Any survivor discovered entirely within a single research program must be treated as potentially program-dependent until tested under independent decompositions, independent methods, or independent research cultures.

Corollary:

> The observer may itself be a hidden fixed variable.

**Standing Rule 31 (RD-OBSERVER.1) — APPROVED**

> When evaluating any survivor, ask: Would an independent observer with different priors discover the same survivor? The overlap between independent observers becomes the evidence.

**Standing Rule 32 (RD-OBSERVER.2)**

> Multiple observers generated by a common cognitive substrate provide weaker evidence than genuinely independent observers.

Corollary:

> Observer diversity is not observer independence.

Mathematical formulation:

> E_pseudo ≤ E_independent

or

> Confidence ∝ ObserverIndependence

---

## Working Principle

Major developmental transitions appear to occur when a system acquires an architecture that allows previously fragile differences to become persistent, actionable, and composable.

---

## Research Goal

Identify the architectural properties responsible for that transformation.

---

## Non-Commitments

We are not claiming that the fundamental object is:
- Constraints
- Topology
- Information
- Lenses
- Distinguishability
- Mind
- Mathematics

All remain candidate interpretations.

---

## RD-10B Core Question

> What architectural properties repeatedly accompany large expansions in what differences can persist, matter, and participate in further organization?

---

## RD-10B Secondary Question

> Are those patterns themselves fundamental, or are they manifestations of a deeper invariant?

---

## The Most Dangerous Question

> Why do these seemingly different motifs keep showing up near major transitions?

---

## Method

### Phase -1: Category Audit

Before defining motifs, justify the category system.

Question:
> Why these motifs?

For every motif included, require justification.

For every major transition, ask:
> What recurring property do we observe before we call it a motif?

The motif list must not be theory-laden from the start.

#### Motif Justification Protocol

For each proposed motif:
1. What observable property does it describe?
2. Why is this property worth naming separately?
3. Could it be a surface manifestation of a deeper property?
4. What evidence would distinguish it from a deeper invariant?

#### Transition Analysis

For each major transition (particle → atom → molecule → replicator → cell → organism → mind → mathematics):
1. What architectural change occurs?
2. What recurring property appears?
3. Is that property best described as a "motif" or as a symptom of something deeper?

If the same property manifests as boundary in one domain, closure in another, and hierarchy in another, then these may not be three motifs. They may be one latent property viewed three ways.

### Phase 0: Motif Operationalization

Before any experiments, define explicit detection rules for every motif.

For each motif, provide:

#### Detection Rule
A precise, testable definition that two researchers would agree on.

Example formats:

**Boundary**:
> A subset of states whose internal transition probabilities exceed external transition probabilities by factor k.

**Hierarchy**:
> A graph exhibiting at least n nested levels of control/influence.

**Closure**:
> A cycle whose output variables causally maintain the cycle's own existence.

**Recursion**:
> A representation that contains a model of its own interpretation process.

Without explicit detection rules, falsification is weak.

#### Measurement Protocol
How to detect the motif in a given system.

#### Threshold
What value of the detection metric counts as "present"?

### Phase 1: Motif Independence Analysis

Before testing causality, determine which motifs are statistically independent.

Question:
> Which motifs are genuinely distinct, and which are the same phenomenon viewed three ways?

If boundary, closure, and hierarchy always appear together, they may not be three things. They may be one thing viewed three ways.

Method:
1. Build diverse architectures
2. Detect motifs using Phase 0 rules
3. Compute correlation matrix
4. Cluster motifs by co-occurrence
5. Identify independent motif families

This prevents testing the same phenomenon under three labels.

### Phase 2: Pattern Discovery

Build 8 toy universes with known constraint sets. Apply recombination operations that produce specific architectural motifs. Measure:
1. **D_persist**: Differences that become persistent
2. **D_matter**: Differences that become actionable
3. **D_composable**: Differences that become composable
4. **Correlation**: Which architectural properties correlate with expansion

### Phase 3: Null-Model Comparison

For each motif, compare against null models:

#### Randomized Architectures
Generate architectures with random connectivity. Measure motif presence and D_persist.

#### Shuffled Architectures
Take real architectures. Shuffle connections while preserving degree distribution. Measure motif presence.

#### Degenerate Architectures
Remove specific motif features while preserving others. Measure effect on D_persist.

#### Minimal Architectures
What is the simplest architecture that produces the effect? Compare against slightly simpler architectures.

A motif only matters if it outperforms nulls.

### Phase 4: Causal Testing

For every motif that survives Phase 3, apply three attacks:

#### Removal Test
Remove the motif. Does the expansion disappear?

If yes: the motif is causally necessary.
If no: the motif is a correlated byproduct.

#### Replacement Test
Can a structurally different architecture produce the same effect?

If yes:
- Motif weakened
- Candidate deeper invariant strengthened

This is the critical interpretation. If boundary and hierarchy both preserve distinctions, then:
- Boundary fails replacement
- Hierarchy fails replacement
- But the deeper invariant may survive

The replacement test searches for deeper invariants, not motif uniqueness.

#### Minimality Test
What is the smallest version capable of producing the effect?

This identifies the essential features of the motif.

### Phase 5: Invariant Search

Determine whether the causally necessary motifs share a deeper common structure.

Question:
> What recurring property do boundaries, closures, hierarchies, and recursions share?

If they share a common property, that property is the candidate invariant. The motifs are merely surface manifestations.

### Phase 6: Cross-Domain Transfer

Test whether candidate invariants survive across domains:

- Granular systems
- Reaction-diffusion
- Graph rewriting
- Cellular automata
- Ecosystems

An invariant that survives locally but dies when moved across domains is not an invariant.

**Cross-domain transfer is the final gate.**

### Phase 7: Invariant vs Attractor Analysis

For every candidate pattern, test whether recurrence is better explained by:

#### Invariant Hypothesis

Same underlying property appearing in multiple forms.

Evidence for:
- Different manifestations share measurable common structure
- Removing the common structure eliminates all manifestations
- Cross-domain transfer preserves the common structure

#### Attractor Hypothesis

Different processes independently converging on similar architectures.

Evidence for:
- Manifestations arise from different starting conditions
- Different mechanisms produce the same architecture
- The architecture is a local optimum in fitness landscape

#### Test

For each candidate pattern:
1. Can the pattern arise from multiple independent pathways?
2. Do different implementations share measurable common structure?
3. Is the pattern a local optimum in the fitness landscape?

If the pattern arises from multiple independent pathways and is a local optimum: **Attractor Hypothesis** supported.

If the pattern shares measurable common structure across domains: **Invariant Hypothesis** supported.

Both hypotheses may be true for different patterns. This is not a forced choice.

---

## The 8 Architectures (as observations, not primitives)

| Architecture | Description | Detection Rule (Draft) |
|-------------|-------------|----------------------|
| Binding | Discrete states via potential wells | States cluster into discrete energy levels with gaps > kT |
| Network | Connected modules | Graph with >n nodes and >m edges, modularity score > threshold |
| Cycle | Self-reinforcing loops | Closed path where output causally maintains input |
| Template | Information transfer via copying | State S₁ generates S₂ where S₂ preserves S₁'s structure with fidelity > threshold |
| Boundary | Protected interior | Internal transition rate / external transition rate > factor k |
| Hierarchy | Nested coordination | Graph exhibits ≥n nested levels of control/influence |
| Recursion | Self-referential representation | Representation contains model of its own interpretation |
| Formal inference | Derivation from axioms | System generates statements provable from axioms via rules |

We do not assume these are on the same ontological level. We observe whether they recur near major transitions.

**Note**: These detection rules are drafts. Phase 0 will refine them into precise, testable definitions.

---

## Success Criterion

A pattern graduates from "interesting motif" to "candidate invariant or attractor" only after:

1. **Category-justified**: Motif is not a theory-laden assumption (Phase -1)
2. **Operationalized**: Explicit detection rule exists (Phase 0)
3. **Independent**: Statistically independent from other motifs (Phase 1)
4. **Outperforms nulls**: Beats randomized/shuffled/degenerate/minimal architectures (Phase 3)
5. **Survives removal**: Expansion disappears when motif is removed (Phase 4)
6. **Survives replacement**: No other structure can serve the same function (Phase 4)
7. **Minimal**: Smallest version capable of producing the effect identified (Phase 4)
8. **Cross-domain**: Survives across granular, reaction-diffusion, graph rewriting, CA, ecosystems (Phase 6)
9. **Interpreted**: Classified as invariant or attractor based on Phase 7 evidence

---

## The Updated Phases

| Phase | Purpose |
|-------|---------|
| -1 | Category audit — justify why these motifs |
| 0 | Motif operationalization |
| 1 | Motif independence analysis |
| 2 | Pattern discovery |
| 3 | Null-model comparison |
| 4 | Causal testing |
| 5 | Invariant search |
| 6 | Cross-domain transfer |
| 7 | Invariant vs Attractor analysis |

---

## What Would Constitute Progress

### Minimum Progress
Identify which architectural motifs recur near major transitions.

### Medium Progress
Determine which motifs are causally necessary vs. correlated byproducts.

### Maximum Progress
Discover a deeper invariant that explains why all causally necessary motifs share common structure.

---

## The Meta-Lesson

The program's strongest habit has been ruthless falsification.

RD-5 through RD-9 were valuable not because they found answers, but because they killed answers.

RD-10B should inherit that habit rather than becoming a catalog of recurring motifs.

---

## What We Will Not Claim

RD-10B will not claim to have found the deepest object.

RD-10B will identify patterns, test their causality, and ask what makes them possible.

That is the tradition. That is the engine.

---

## The Methodological Commitment

Progress has come from finding deeper invariants, not from declaring victory when one appears.

RD-10B continues that standing rule:

> Whenever something looks fundamental, ask what makes it possible.

RD-10B adds a second rule:

> Whenever something looks recurrent, ask whether it is causal.

And a third rule:

> Whenever something looks like a deeper invariant, ask whether it might be an attractor instead.

That is the rule. For RD-10B. For everything that follows.

---

## Falsification Table

Before execution, specify what would force us to revise the framework.

| Hypothesis | Observation That Would Damage It |
|-----------|--------------------------------|
| Motifs recur near transitions | No architectural patterns recur across domains |
| Motifs are causally necessary | Removing motifs does not reduce D_persist |
| Invariants exist | No common structure shared across causally necessary motifs |
| Attractors explain recurrence | Patterns arise from single pathway, not multiple independent convergences |
| Cross-domain transfer works | Invariants survive locally but die when moved |
| Category system is valid | Phase -1 reveals motifs are not natural categories |

---

## Phase Consolidation

Phase 5 (Invariant Search) and Phase 7 (Invariant vs Attractor) are partially overlapping. Determining whether something is an invariant often already requires distinguishing it from an attractor explanation.

**Consolidated**: Phase 5 now includes both invariant search and attractor testing. Phase 7 is removed as a separate phase.

| Phase | Purpose |
|-------|---------|
| -1 | Category audit |
| 0 | Motif operationalization |
| 1 | Motif independence analysis |
| 2 | Pattern discovery |
| 3 | Null-model comparison |
| 4 | Causal testing |
| 5 | Invariant vs Attractor analysis |
| 6 | Cross-domain transfer |

---

## The Decision

RD-10B is ready enough to begin exploratory execution.

No further methodology layers will be added.

**Action**: Start running the program. Let reality push back. Then revise.

---

## Summary: Context After RD-10B Complete

### What We Know

1. **Post-hoc detectors are artifacts of the representation**: They measure time-series properties (pairwise correlation, autocorrelation, dominant frequency), not architectural features. (RD-10B.3)

2. **Motifs are properties of the world-representation pair, not the world alone**: Same world, different representations → different motifs. (RD-10B.0)

3. **"Same world" is purpose-relative**: Different identity criteria (predictive, intervention, counterfactual, information, causal) disagree on what counts as the same world. (RD-10B.0B)

4. **Identity criteria have domains**: Each criterion is informative under specific conditions and trivial or misleading under others. No criterion is universally applicable. (RD-10B.0E)

5. **Worlds are not neutral observers**: They have hidden assumptions that advantage some criteria and disadvantage others. (RD-10B.0F)

6. **The same transformation appears from both ends of the compositional ladder**: Recursion, constraint, preservation, and distinction are all genuine junctions — the same structure appears independently from the physical chain and the logical chain, and resists further reduction. (RD-10B.X/Y/Z/W)

7. **The four junctions are distinct and complementary**: They work together, not as alternatives. (RD-10B Complete)

8. **The four junctions are path-independent**: They appear across 11 alternative ladders from both directions. However, path independence is necessary but not sufficient. Vocabulary convergence and compression convergence remain risks. (RD-10B.J2)

9. **The four junctions are vocabulary-independent**: They appear across 5 different vocabularies (structural, dynamical, information, categorical, computational), with different forms in different vocabularies. This is evidence against vocabulary convergence. However, vocabulary independence is also not sufficient. (RD-10B.J3)

10. **The convergence structure is compressible and isomorphism-invariant**: Different decompositions yield different generators, but all generators are isomorphic (they all distinguish elements of a space and produce a partition label). The specific generator (distinction) was an artifact of the decomposition choice. The genuine structure is the isomorphism class, not any specific realization. (RD-10B.J7)

11. **Migration pattern is correlated with methodology changes**: Migration rate is 100% across 20 audits, but the null model shows migration appears only when methodology changes. Migration may be a methodological artifact, not a genuine regularity. (RD-10B.M1)

12. **The progression is an oscillation, not a hierarchy**: The progression is not Object → Property → Relation → Transformation → Decomposition → Translation. It is Object → Mapping → Object → Mapping. Each time an object becomes explanatory, it is later revealed to be a mapping. RD-10B is converging toward a translation structure, not a deepest level. (RD-10B.M2)

### What We Don't Know

1. **Whether to pursue Path A or Path B**: Path A (Organization Program) returns to granular worlds and biology. Path B (Translation Program) becomes a theory of representation and equivalence. RD-10B has drifted toward B.

2. **What remains invariant under translation**: We have identified some candidates (partition structure, restriction structure, etc.), but we have not yet tested whether these are genuine invariants or artifacts of our translation maps.

3. **How to characterize the translation structure**: We know RD-10B is converging toward a translation structure, but we have not yet found a clean characterization of what that structure is.
