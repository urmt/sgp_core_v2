#!/usr/bin/env python3
"""
T069: Stage Emergence Audit
============================
Determine whether IS1b ("identifiable stages") follows from IS1a ("change")
under the existing substrate, or whether stage structure introduces genuinely
new content not derivable from the current assumption set.

Question: Does IS1b require its own generative justification, or is it
emergent from IS1a + OC2 + IS2 + the rest of the substrate?

Three possible outcomes:
  1. IS1a ⇒ IS1b (emergent)     — Path C collapses to 9 assumptions
  2. IS1a ⇏ IS1b, but existing substrate provides the gap
     (derivable via combination) — Path C still collapses to 9
  3. IS1a + substrate ⇏ IS1b (independent) — stages add content not
     available elsewhere; Path A/B/C remains an open choice
"""

import csv, copy
from pathlib import Path
from itertools import combinations

OUT = Path("/home/student/sgp_core_v2/sfh_sgp_ood_outputs")

# ============================================================
# CONCEPTUAL DECOMPOSITION
# ============================================================

print("=" * 72)
print("T069: STAGE EMERGENCE AUDIT")
print("=" * 72)

# IS1a (Change): "The investigation undergoes change across its engagement."
IS1A_REQUIREMENTS = [
    "The investigation has at least two distinguishable states",
    "There is a transition or difference between them",
    "The change is temporally ordered (before → after)",
]

# IS1b (Stages): "The investigation has identifiable ordered stages."
IS1B_REQUIREMENTS = IS1A_REQUIREMENTS + [
    "The investigation's history can be partitioned into discrete intervals",
    "Interval boundaries are identifiable (can be located)",
    "Intervals have internal coherence (what happens within a stage belongs together)",
    "Stages are ordered (stage A precedes stage B)",
]

# What existing substrate assumptions provide
SUBSTRATE_RESOURCES = {
    "OC2": {
        "label": "Distinguishability",
        "provides": [
            "Ability to distinguish temporal positions (t1 ≠ t2)",
            "Ability to distinguish states (state1 ≠ state2)",
            "Ability to distinguish intervals (stage A ≠ stage B)",
        ],
        "addresses": [
            "The investigation has at least two distinguishable states",
            "Interval boundaries are identifiable",
        ],
    },
    "IS1a": {
        "label": "Investigative change",
        "provides": [
            "Temporal ordering (before → after)",
            "State transition",
        ],
        "addresses": [
            "There is a transition or difference between states",
            "The change is temporally ordered",
        ],
    },
    "OC1": {
        "label": "Stable structure",
        "provides": [
            "The phenomenon has structure that may impose natural breakpoints",
            "Stable referents enable comparing states across time",
        ],
        "addresses": [
            "Intervals have internal coherence (phenomenon structure provides continuity)",
        ],
    },
    "IS2": {
        "label": "Determinate outputs",
        "provides": [
            "Outputs at different times can differ, marking transitions",
            "Outputs can serve as boundary markers (new output type = new stage)",
        ],
        "addresses": [
            "Interval boundaries are identifiable (output change marks boundary)",
            "Intervals have internal coherence (same output type within stage)",
        ],
    },
    "IC1": {
        "label": "Extractable information",
        "provides": [
            "Information content changes as investigation progresses",
            "New information can trigger stage transitions",
        ],
        "addresses": [
            "Interval boundaries are identifiable (information change marks boundary)",
        ],
    },
    "CD1": {
        "label": "Causal relations exist",
        "provides": [
            "Earlier stages can causally influence later stages",
            "Causal chains can span stage boundaries",
        ],
        "addresses": [
            "Stages are ordered (causal order)",
        ],
    },
    "EC1": {
        "label": "Self-knowledge",
        "provides": [
            "Awareness of stage transitions",
            "Ability to retrospectively identify stage boundaries",
        ],
        "addresses": [
            "Interval boundaries are identifiable (via self-reflection)",
        ],
    },
    "CD2": {
        "label": "Self-affecting procedures",
        "provides": [
            "Investigation's own actions can alter its trajectory",
            "Self-effects can create natural stage boundaries",
        ],
        "addresses": [
            "Interval boundaries are identifiable (self-effect marks transition)",
        ],
    },
    "SR1": {
        "label": "Self-examination of outputs",
        "provides": [
            "Post-hoc analysis can identify stages by examining output patterns",
            "Comparison across outputs reveals stage structure",
        ],
        "addresses": [
            "Interval boundaries are identifiable (via output comparison)",
            "Intervals have internal coherence (output pattern clustering)",
        ],
    },
}

# ============================================================
# ANALYSIS 1: What does IS1b require beyond IS1a?
# ============================================================

print(f"""
--- A. STAGE REQUIREMENTS BEYOND CHANGE ---

IS1a (Change) provides:
  1. Multiple distinguishable states
  2. Transition between states
  3. Temporal ordering

IS1b (Stages) requires additionally:
  1. Partition into discrete intervals
  2. Identifiable boundaries between intervals
  3. Internal coherence within intervals
  4. Stage ordering (already provided by IS1a)

The additional requirements are:
  - Boundary identifiability: locating WHERE one stage ends and another begins
  - Interval coherence: WHAT makes a set of changes belong to the same stage
""")

# ============================================================
# ANALYSIS 2: Can existing substrate provide boundaries?
# ============================================================

print("--- B. BOUNDARY RESOURCES IN THE EXISTING SUBSTRATE ---")

boundary_sources = {}
for aid, info in SUBSTRATE_RESOURCES.items():
    boundary_contrib = [r for r in info["addresses"]
                        if "boundar" in r.lower() or "partition" in r.lower()
                        or "coherence" in r.lower() or "ordered" in r.lower()]
    if boundary_contrib:
        boundary_sources[aid] = boundary_contrib
        print(f"  {aid} ({info['label']}):")
        for c in boundary_contrib:
            print(f"    -> {c}")

print(f"\n  Boundary-relevant assumptions: {len(boundary_sources)}")
print(f"  {', '.join(sorted(boundary_sources.keys()))}")

# ============================================================
# ANALYSIS 3: Can existing substrate provide coherence?
# ============================================================

print(f"\n--- C. COHERENCE RESOURCES IN THE EXISTING SUBSTRATE ---")

coherence_sources = {}
for aid, info in SUBSTRATE_RESOURCES.items():
    coherence_contrib = [r for r in info["addresses"]
                         if "coherence" in r.lower() or "continu" in r.lower()
                         or "clustering" in r.lower() or "together" in r.lower()]
    if coherence_contrib:
        coherence_sources[aid] = coherence_contrib
        print(f"  {aid} ({info['label']}):")
        for c in coherence_contrib:
            print(f"    -> {c}")

# ============================================================
# ANALYSIS 4: Emergence test — can we derive IS1b from IS1a + others?
# ============================================================

print(f"\n--- D. EMERGENCE EVALUATION ---")

# Build a conceptual sufficiency table for IS1b requirements
requirements = [
    "distinguishable states",
    "temporal ordering",
    "state transition",
    "interval partitioning",
    "boundary identifiability",
    "interval coherence",
]

requirement_sources = {
    "distinguishable states": ["OC2"],
    "temporal ordering": ["IS1a", "OC2"],
    "state transition": ["IS1a"],
    "interval partitioning": [],  # no single assumption provides this
    "boundary identifiability": ["OC2", "IS2", "EC1", "SR1", "IC1", "CD2"],
    "interval coherence": ["OC1", "IS2", "SR1"],
}

print(f"  IS1b requirements and which assumptions address them:")
for req in requirements:
    sources = requirement_sources.get(req, [])
    covered = len(sources) > 0
    src_str = ", ".join(sources) if sources else "NONE"
    print(f"    {'✓' if covered else '✗'} {req:30s} -> {src_str}")

not_covered = [req for req in requirements if not requirement_sources.get(req, [])]

print()
if not_covered:
    print(f"  UNCOVERED REQUIREMENTS: {', '.join(not_covered)}")
else:
    print(f"  All requirements are addressed by at least one existing assumption.")

# ============================================================
# ANALYSIS 5: Three emergence scenarios
# ============================================================

print(f"""
--- E. EMERGENCE SCENARIOS ---

Scenario 1: Strong emergence (IS1a ⇒ IS1b)
  Change inherently produces discrete stages.
  Counterargument: Change can be continuous (e.g., gradual warming).
  Continuous change has no natural internal boundaries.
  Verdict: UNLIKELY. Continuous change is coherent without stages.

Scenario 2: Mediated emergence (IS1a + substrate ⇒ IS1b)
  Change + distinguishability + outputs + self-examination jointly
  provide boundary and coherence resources.
  Key question: Does the CONJUNCTION of existing assumptions entail
  stage structure without adding a new assumption?

Scenario 3: Non-emergence (IS1b is independent)
  Stage structure adds content not derivable from the current substrate.
  Would require either BA1 or treating IS1b as a root.
""")

# ============================================================
# ANALYSIS 6: Formal derivation attempt
# ============================================================

print("--- F. FORMAL DERIVATION ATTEMPT ---")

print("""
  Given:
    1. The investigation undergoes change (IS1a)
    2. Temporal positions are distinguishable (OC2)
    3. The investigation produces determinate outputs (IS2)
    4. Outputs at different times can differ (IS2 + OC2)
    5. The investigation can examine its outputs (SR1)
    6. The investigation has self-knowledge (EC1)

  Can we derive:
    "The investigation has identifiable ordered stages"?

  Proposed derivation:
    a. The investigation at t1 produces output O1 (IS1a + IS2)
    b. The investigation at t2 produces output O2 (IS1a + IS2)
    c. O1 ≠ O2 (distinguishable via OC2)
    d. The difference O1/O2 marks a transition in investigative activity
    e. The interval [t1, t2) where output type O1 is produced is a stage
    f. The interval [t2, t3) where output type O2 is produced is a stage
    g. Stages are ordered by temporal succession (IS1a)

  Problems with this derivation:
    - Step (e) assumes output type determines stage boundaries
      - But output type could vary continuously, not discretely
      - Without criteria for "same output type," stage boundaries are arbitrary
    - Step (d) assumes output difference = activity transition
      - The same activity could produce different outputs
      - Different activities could produce the same output
    - The derivation requires a discreteness assumption not present in the substrate:
      - That changes come in discrete packets, not continuous variation

  Result: DERIVATION FAILS without additional assumptions.
  The substrate only guarantees continuous variation; stages require discreteness.
""")

# ============================================================
# ANALYSIS 7: What would make stages emergent?
# ============================================================

print("--- G. WHAT WOULD CHANGE THE VERDICT? ---")

print("""
  For stages to be emergent from the existing substrate, one of the following
  would need to be true:

  a. The substrate already contains a discreteness assumption
     - Check: IS2 (determinate outputs) — outputs are discrete entities
       -> This provides discreteness at the output level
       -> But does not guarantee output changes mark stage boundaries
     - Check: OC2 (distinguishability) — distinctions are discrete
       -> This provides boundary identifiability in principle
       -> But does not guarantee natural boundaries exist

  b. Stages are definitional rather than emergent
     - "Having stages" could mean "different things happen at different times"
     - This collapses IS1b into IS1a
     -> If IS1b IS just "the investigation is not homogeneous across time",
        then it is equivalent to IS1a and no extra assumption is needed.

  c. The derivation only requires existence, not uniqueness
     - If any partition of investigative activity constitutes stages
     - Then stages always exist trivially (every change creates two stages:
       before and after)
     - But this makes "stages" vacuous
""")

# ============================================================
# ANALYSIS 8: Structural test — what if IS1b is just IS1a + IS2?
# ============================================================

print("--- H. STRUCTURAL TEST: CAN PATH C COLLAPSE? ---")

# Test: remove IS1b, make SR1 depend on IS1a + IS2 instead
# This tests whether IS1b is actually needed structurally

print("""
  If IS1b is emergent from IS1a + IS2, then SR1 could depend on IS1a and IS2
  directly without needing IS1b as a separate node.

  Test graph (Path C without IS1b):
    SR1 → IS2, IS1a
    IS1a → OC2
    IS2 → IC1, OC1, IS1a
    ... (rest unchanged)
""")

C_NO_IS1B = {
    "SR1":  ["IS2", "IS1a"],
    "IS1a": ["OC2"],
    "IS2":  ["IC1", "OC1", "IS1a"],
    "OC1":  ["OC2"],
    "OC2":  [],
    "EC1":  ["SR1", "IS2", "IS1a"],
    "IC1":  ["OC1", "OC2", "IS1a"],
    "CD1":  ["OC1", "OC2"],
    "CD2":  ["CD1", "IS1a", "EC1"],
}

LABELS_C_NO_IS1B = {
    "SR1":  "Self-examination of outputs",
    "IS1a": "Investigative change",
    "IS2":  "Determinate outputs",
    "OC1":  "Stable structure",
    "OC2":  "Distinguishability",
    "EC1":  "Self-knowledge",
    "IC1":  "Extractable information",
    "CD1":  "Causal relations exist",
    "CD2":  "Self-affecting procedures",
}

SIDS_C_NO_IS1B = sorted(LABELS_C_NO_IS1B.keys())

def compute_survivors(edges, alive_set):
    satisfied = {a for a in alive_set if not edges.get(a, [])}
    changed = True
    while changed:
        changed = False
        for node in alive_set:
            if node not in satisfied:
                if all(r in satisfied for r in edges.get(node, [])):
                    satisfied.add(node)
                    changed = True
    return satisfied

def tarjan_scc(edges):
    index_counter = [0]
    stack = []
    index = {}
    lowlink = {}
    on_stack = {}
    sccs = []
    def strongconnect(v):
        index[v] = index_counter[0]
        lowlink[v] = index_counter[0]
        index_counter[0] += 1
        stack.append(v)
        on_stack[v] = True
        for w in edges.get(v, []):
            if w not in index:
                strongconnect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif on_stack.get(w, False):
                lowlink[v] = min(lowlink[v], index[w])
        if lowlink[v] == index[v]:
            scc = set()
            while True:
                w = stack.pop()
                on_stack[w] = False
                scc.add(w)
                if w == v:
                    break
            sccs.append(scc)
    for v in edges:
        if v not in index:
            strongconnect(v)
    return sccs

alive = set(SIDS_C_NO_IS1B)
sat = compute_survivors(C_NO_IS1B, alive)
is_gen = sat == alive
sccs = tarjan_scc(C_NO_IS1B)
nontriv = [s for s in sccs if len(s) > 1]
roots = sorted([a for a in alive if not C_NO_IS1B.get(a, [])])

print(f"  Generative: {is_gen} ({len(sat)}/{len(alive)} satisfied)")
print(f"  SCCs:       {len(nontriv)}")
print(f"  Roots:      {roots}")
print()
if is_gen:
    print("  Result: Path C collapses to 9 assumptions.")
    print("  IS1b is NOT structurally necessary when SR1 directly depends on IS1a + IS2.")
else:
    print("  Result: Path C cannot collapse — IS1b is structurally necessary.")

# ============================================================
# ANALYSIS 9: The conceptual crux
# ============================================================

print(f"""
--- I. CONCEPTUAL CRUX ---

The stage emergence question reduces to:

  IS1b is a claim about DISCRETE BOUNDARIES in investigative activity.
  The existing substrate provides CONTINUOUS CHANGE (IS1a) and
  DISCRETE OUTPUTS (IS2), but no principle linking them.

  The missing link is:
    "Output type changes correspond to stage boundaries in investigative activity."

  This is neither obviously true nor obviously false:
    - True if: the investigation's activity is determined by what it outputs
    - False if: the investigation's activity includes unexpressed changes
      that produce no output change

  The existing substrate does not resolve this because it does not specify
  the relationship between investigative activity and output production.

  Three positions:

  1. Activity = output production
     Then IS1a + IS2 entails IS1b (output change = stage boundary)
     Consequence: 9-assumption substrate, OC2 unique root

  2. Activity ⊆ output production
     Activity may include unexpressed changes
     Then IS1b requires additional content not in substrate
     Consequence: 10-assumption substrate (BA1 or independent IS1b)

  3. Activity ⊇ output production + more
     Activity includes internal processing not reflected in outputs
     Then IS1b clearly requires additional content
     Consequence: 10-assumption substrate

  The choice between these is not structural — it is a claim about the
  relationship between investigative activity and its outputs.
""")

# ============================================================
# ANALYSIS 10: Implication for SR1
# ============================================================

print("--- J. SR1 DEPENDENCY ANALYSIS ---")

print("""
  SR1 (Self-examination of outputs) requires stages because:
    "The investigation examines its own outputs as objects of analysis."

  This requires:
    1. Outputs exist (IS2) ✓
    2. Outputs are produced BEFORE examination (temporal ordering) — IS1a ✓
    3. There is a distinction between the production phase and the examination
       phase (stage separation)
    
  The third requirement is the key:
    - Production and examination must be distinguishable activities
    - They need not be temporally separated if they are functionally distinct
    - But SR1's definition implies temporal ordering (first produce, then examine)

  Possibilities:
    a. SR1 only requires functional distinction, not temporal stages
       -> IS1a (change) suffices: the investigation changes from producing
          to examining
       -> No IS1b needed

    b. SR1 requires temporal stage separation
       -> IS1b is structurally necessary for SR1
       -> But IS1b might still be derivable from IS1a + IS2 if output
          change marks the production→examination transition

  The stronger position is (a): SR1 requires distinguishable activities
  (producing vs examining), which is a functional distinction, not a
  temporal one. The investigation can produce and examine simultaneously
  if it treats its outputs as objects while producing them.
  
  If (a) is accepted, IS1b is not required even for SR1.
""")

# ============================================================
# DELIVERABLE SUMMARY
# ============================================================

print(f"\n{'='*72}")
print("T069 SUMMARY")
print(f"{'='*72}")

print(f"""
Primary question: Does IS1b follow from IS1a + existing substrate?

Result: INCONCLUSIVE — depends on two unresolved claims:

  Claim 1 — Output-activity link:
    Does output change necessarily mark activity boundaries?
    Position 1 (yes):  IS1b emergent, Path C collapses to 9
    Position 2 (no):   IS1b carries independent content

  Claim 2 — SR1 stage requirement:
    Does SR1 require temporal stage separation or only functional distinction?
    Position 1 (functional): No IS1b needed
    Position 2 (temporal):   IS1b needed for SR1 branch

Combined possibilities:

  Claim1\\Claim2    | Functional (SR1) | Temporal (SR1)
  ------------------+------------------+----------------
  Output=Activity   | 9 assumptions   | 9 assumptions
  Output≠Activity   | 9? or 10?       | 10 assumptions

  The strongest case for 9 assumptions requires BOTH:
    (a) Output change = activity boundary
    (b) SR1 only needs functional distinction

  The weakest case (10 assumptions) follows from:
    Either output ≠ activity AND SR1 needs temporal stages
""")

# ============================================================
# WRITE OUTPUTS
# ============================================================

# Deliverable A: Requirement mapping
with open(OUT / "t069_stage_requirements.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["requirement", "source_assumptions", "covered", "notes"])
    for req in requirements:
        sources = requirement_sources.get(req, [])
        covered = "YES" if sources else "NO"
        note = ""
        if req == "distinguishable states":
            note = "OC2 provides the general capacity for distinction"
        elif req == "interval partitioning":
            note = "No single assumption provides this — requires conjunction"
        elif req == "boundary identifiability":
            note = "Multiple sources but requires criteria for boundary placement"
        elif req == "interval coherence":
            note = "What makes a set of changes 'belong together'?"
        w.writerow([req, ";".join(sources) if sources else "NONE", covered, note])

print(f"Wrote t069_stage_requirements.csv")

# Deliverable B: Derivation test
with open(OUT / "t069_derivation_test.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["test", "result", "detail"])
    w.writerow(["Strong emergence (IS1a => IS1b)", "FAIL",
                 "Continuous change is coherent without discrete stages"])
    w.writerow(["Mediated emergence (IS1a + substrate => IS1b)", "INCONCLUSIVE",
                 "Depends on output-activity link and SR1 stage requirement"])
    w.writerow(["Non-emergence (IS1b independent)", "POSSIBLE",
                 "If output ≠ activity OR SR1 requires temporal stages"])
    w.writerow(["Structural collapse test (remove IS1b)", str(is_gen),
                 f"{'9-assumption substrate viable' if is_gen else 'IS1b structurally necessary'}"])
    w.writerow(["Path C_no_IS1B generative", str(is_gen), ""])
    w.writerow(["Path C_no_IS1B roots", ";".join(roots), ""])

print(f"Wrote t069_derivation_test.csv")

# Deliverable C: Decision framework
with open(OUT / "t069_decision_matrix.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["output_activity_link", "sr1_stage_requirement",
                 "n_assumptions", "path_choice", "notes"])
    w.writerow(["output=activity boundary", "functional", "9",
                 "Path C collapsed", "IS1b emergent, no new assumptions"])
    w.writerow(["output=activity boundary", "temporal", "9",
                 "Path C collapsed", "IS1b derived from IS1a+IS2, stages are output-change patterns"])
    w.writerow(["output≠activity", "functional", "9 or 10",
                 "Path A or C", "IS1a may suffice for SR1, IS1b optional"])
    w.writerow(["output≠activity", "temporal", "10",
                 "Path B or C", "IS1b has independent content; BA1 or second root required"])

print(f"Wrote t069_decision_matrix.csv")

print(f"\nT069 complete.")
