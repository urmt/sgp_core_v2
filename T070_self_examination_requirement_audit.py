#!/usr/bin/env python3
"""
T070: Self-Examination Requirement Audit
==========================================
Evaluate the weakest structure that still satisfies SR1, testing four
levels of interpretive demand on what "self-examination of outputs"
minimally requires.

Level 1: outputs only           — SR1 ← IS2
Level 2: outputs + change       — SR1 ← IS2 + IS1a
Level 3: outputs + ordering     — SR1 ← IS2 + temporal ordering (via OC2)
Level 4: outputs + stages       — SR1 ← IS2 + IS1b (discrete stages)

For each level:
  - Can SR1 still be formulated?
  - What capability is lost?
  - Are downstream assumptions (EC1, CD2) affected?
  - Is the graph still generative?
"""

import csv
from pathlib import Path

OUT = Path("/home/student/sgp_core_v2/sfh_sgp_ood_outputs")

# ============================================================
# BASE DEFINITIONS (Path C collapsed — 9 assumptions)
# ============================================================

LABELS = {
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

SIDS = sorted(LABELS.keys())

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

def find_roots(edges, alive_set):
    return sorted([a for a in alive_set if not edges.get(a, [])])

def analyze_graph(edges, label_map, sids, label):
    alive = set(sids)
    sat = compute_survivors(edges, alive)
    gen = sat == alive
    roots = find_roots(edges, sat)
    return {"label": label, "generative": gen, "n_sat": len(sat),
            "n_total": len(sids), "roots": roots}

# ============================================================
# Common edges (everything except SR1)
# ============================================================

COMMON = {
    "IS1a": ["OC2"],
    "IS2":  ["IC1", "OC1", "IS1a"],
    "OC1":  ["OC2"],
    "OC2":  [],
    "EC1":  ["SR1", "IS2", "IS1a"],
    "IC1":  ["OC1", "OC2", "IS1a"],
    "CD1":  ["OC1", "OC2"],
    "CD2":  ["CD1", "IS1a", "EC1"],
}

# ============================================================
# LEVEL DEFINITIONS
# ============================================================

LEVELS = []

# ---- Level 1: outputs only ----
LEVELS.append({
    "name": "Level 1 — outputs only",
    "sr1_definition": "The investigation can examine its own outputs as objects of analysis.",
    "sr1_requires": "Outputs exist (IS2)",
    "sr1_does_not_require": "Investigative change, temporal ordering, stage separation",
    "edges": {**COMMON, "SR1": ["IS2"]},
    "capability_notes": (
        "SR1 has outputs to examine but no process that examines them. "
        "Examination requires an examiner — some entity that does the examining. "
        "IS2 only provides the objects, not the subject. Without IS1a (change), "
        "the investigation has no active dimension; it is a static output-producer. "
        "Self-examination requires the investigation to DO something with its outputs, "
        "which demands activity."
    ),
})

# ---- Level 2: outputs + change ----
LEVELS.append({
    "name": "Level 2 — outputs + change",
    "sr1_definition": "The investigation can examine its own outputs as objects of analysis.",
    "sr1_requires": "Outputs exist (IS2) + investigation undergoes change (IS1a)",
    "sr1_does_not_require": "Temporal ordering of production vs examination, discrete stages",
    "edges": {**COMMON, "SR1": ["IS2", "IS1a"]},
    "capability_notes": (
        "SR1 has outputs (IS2) and an active investigative process (IS1a). "
        "The investigation can turn its attention to its outputs because it is "
        "a dynamic process capable of different functional orientations. "
        "IS1a provides the capacity for the investigation to BE in the state "
        "of examining rather than producing. No temporal or stage separation "
        "required — the shift is functional, not temporal."
    ),
})

# ---- Level 3: outputs + ordering ----
LEVELS.append({
    "name": "Level 3 — outputs + ordering",
    "sr1_definition": "The investigation can examine its own outputs as objects of analysis.",
    "sr1_requires": "Outputs exist (IS2) + temporal ordering (production before examination)",
    "sr1_does_not_require": "Discrete stages with identifiable boundaries",
    "edges": {**COMMON, "SR1": ["IS2", "IS1a"]},
    "capability_notes": (
        "Temporal ordering is already implicit in IS1a (change requires before/after). "
        "This level adds no structural change from Level 2 — ordering is a specification "
        "of IS1a, not an additional dependency. The investigation must produce outputs "
        "before it can examine them, but this ordering follows from IS1a + IS2 alone. "
        "No additional edge required."
    ),
})

# ---- Level 4: outputs + discrete stages ----
LEVELS.append({
    "name": "Level 4 — outputs + stages",
    "sr1_definition": "The investigation can examine its own outputs as objects of analysis.",
    "sr1_requires": "Outputs exist (IS2) + discrete identifiable stages (IS1b)",
    "sr1_does_not_require": "Nothing weaker",
    "edges": {**COMMON, "SR1": ["IS2", "IS1b"]},
    "capability_notes": (
        "Requires explicit stage separation: a production phase and an examination phase. "
        "These must be discrete and identifiable. This level demands IS1b as a separate "
        "assumption (or its equivalent via BA1). Production and examination are not just "
        "functionally distinct but temporally separated with a recognizable boundary."
    ),
})

# ============================================================
# ANALYSIS
# ============================================================

print("=" * 72)
print("T070: SELF-EXAMINATION REQUIREMENT AUDIT")
print("=" * 72)

print(f"""
--- SR1 DEFINITION ---
"{LEVELS[0]['sr1_definition']}"

The term "self-examination of outputs" decomposes into:
  - SELF:   the investigation is the agent doing the examining
  - EXAMINATION:  active engagement with outputs as objects of analysis
  - OUTPUTS: things produced by the investigation that can be examined

The critical interpretive question:
  Does "examination" imply a distinct phase separable from production,
  or does it describe a functional orientation the investigation can
  adopt at any time?
""")

# ============================================================
# STRUCTURAL TEST
# ============================================================

print("\n--- STRUCTURAL TEST ---")

# Also need IS1b for Level 4 testing
FULL_SIDS = sorted(list(SIDS) + ["IS1b"])
FULL_LABELS = dict(LABELS)
FULL_LABELS["IS1b"] = "Identifiable stages"

FULL_COMMON = {
    "IS1a": ["OC2"],
    "IS1b": ["IS1a"],
    "IS2":  ["IC1", "OC1", "IS1a"],
    "OC1":  ["OC2"],
    "OC2":  [],
    "EC1":  ["SR1", "IS2", "IS1a"],
    "IC1":  ["OC1", "OC2", "IS1a"],
    "CD1":  ["OC1", "OC2"],
    "CD2":  ["CD1", "IS1a", "EC1"],
}

level_configs = [
    (LEVELS[0], {**COMMON, "SR1": ["IS2"]}, list(SIDS)),
    (LEVELS[1], {**COMMON, "SR1": ["IS2", "IS1a"]}, list(SIDS)),
    (LEVELS[2], {**COMMON, "SR1": ["IS2", "IS1a"]}, list(SIDS)),
    (LEVELS[3], {**FULL_COMMON, "SR1": ["IS2", "IS1b"]}, list(FULL_SIDS)),
]

for i, (level, edges, sids) in enumerate(level_configs):
    alive = set(sids)
    sat = compute_survivors(edges, alive)
    gen = sat == alive
    roots = find_roots(edges, sat)
    level["gen"] = gen
    level["sat"] = len(sat)
    level["total"] = len(sids)
    level["roots"] = roots
    print(f"  {level['name']}: generative={gen}, "
          f"{len(sat)}/{len(sids)} satisfied, roots={roots}")

# ============================================================
# CONCEPTUAL TEST
# ============================================================

print(f"\n--- CONCEPTUAL TEST ---")

sr1_components = {
    "outputs exist": {
        "provided_by": ["IS2"],
        "necessary": True,
        "sufficient_alone": False,
        "reason": "Without outputs, there is nothing to examine."
    },
    "examiner exists": {
        "provided_by": ["IS1a"],
        "necessary": True,
        "sufficient_alone": False,
        "reason": "Examination requires an active entity that does the examining. IS2 alone provides outputs but no examiner."
    },
    "examiner can orient to outputs": {
        "provided_by": ["IS1a", "OC2"],
        "necessary": True,
        "sufficient_alone": False,
        "reason": "The investigation must be able to treat outputs as objects of analysis rather than as production byproducts. This requires the investigation to be capable of different functional orientations (IS1a) and to distinguish outputs from the phenomenon (OC2)."
    },
    "production precedes examination": {
        "provided_by": ["IS1a (implicitly)"],
        "necessary": False,
        "sufficient_alone": False,
        "reason": "Temporal ordering is implicit in IS1a (change implies before/after). But ordering is not strictly necessary — the investigation can examine an output while producing it if examination is a functional orientation rather than a temporal phase."
    },
    "discrete stage separation": {
        "provided_by": ["IS1b", "BA1"],
        "necessary": False,
        "sufficient_alone": False,
        "reason": "Stage separation is the strongest requirement. It is necessary only if examination cannot coexist with production — if examining precludes producing and vice versa. This is a claim about cognitive or procedural capacity, not about logical necessity."
    },
}

print(f"\n  SR1 component analysis:")
print(f"  {'Component':<45} {'Necessary':<12} {'Sufficient alone':<18}")
print(f"  {'-'*75}")
for comp, info in sr1_components.items():
    nec = "YES" if info["necessary"] else "no"
    suf = "YES" if info["sufficient_alone"] else "no"
    print(f"  {comp:<45} {nec:<12} {suf:<18}")
    print(f"  {'':>45} {info['reason'][:100]}")

# ============================================================
# MINIMAL SR1 FORMULATION
# ============================================================

print(f"\n--- MINIMAL SR1 ---")

print(f"""
  The weakest formulation of SR1 that remains coherent:

    SR1_min: "The investigation can adopt a functional orientation toward
              its own outputs, treating them as objects of analysis."

  This requires:
    1. Outputs exist (IS2) — the objects
    2. The investigation undergoes change (IS1a) — the capacity for
       different functional orientations
    3. Outputs and phenomenon are distinguishable (OC2) — so outputs
       can be isolated as objects

  It does NOT require:
    - Temporal separation between production and examination
    - Discrete stage boundaries
    - A distinct examination phase

  The minimal dependency set for SR1 is therefore:
    SR1 ← IS2 + IS1a

  IS1a provides the dynamic capacity; IS2 provides the objects;
  OC2 (already presupposed by both) ensures outputs can be treated
  as distinct objects.
""")

# ============================================================
# LEVEL-BY-LEVEL ASSESSMENT
# ============================================================

print("--- LEVEL-BY-LEVEL ASSESSMENT ---")

level_assessments = [
    {
        "level": 1,
        "name": "outputs only",
        "coherent": False,
        "loss": "No examining agent",
        "structural": "Generative but SR1 is vacuous — no entity examines",
        "verdict": "REJECTED — outputs without an examiner is not self-examination",
    },
    {
        "level": 2,
        "name": "outputs + change",
        "coherent": True,
        "loss": "No explicit temporal ordering (but ordering is implicit in change)",
        "structural": "Fully generative, 9 assumptions, OC2 unique root",
        "verdict": "ACCEPTABLE — minimal coherent formulation",
    },
    {
        "level": 3,
        "name": "outputs + ordering",
        "coherent": True,
        "loss": "No discrete stages (but ordering adds nothing beyond IS1a)",
        "structural": "Identical to Level 2 — ordering is implicit in IS1a",
        "verdict": "EQUIVALENT TO LEVEL 2 — no structural distinction",
    },
    {
        "level": 4,
        "name": "outputs + stages",
        "coherent": True,
        "loss": "Requires additional assumption (IS1b or BA1)",
        "structural": "Generative with 10 assumptions, or 9 if IS1b derived",
        "verdict": "STRONGER THAN NECESSARY — adds requirement not forced by SR1 definition",
    },
]

for a in level_assessments:
    status = "✓" if a["coherent"] else "✗"
    print(f"\n  {status} Level {a['level']} — {a['name']}")
    print(f"     Coherent:      {a['coherent']}")
    print(f"     Capability loss: {a['loss']}")
    print(f"     Structural:     {a['structural']}")
    print(f"     Verdict:        {a['verdict']}")

# ============================================================
# EC1 DOWNSTREAM IMPACT
# ============================================================

print(f"\n--- EC1 DOWNSTREAM IMPACT ---")

print("""
  EC1 (Self-knowledge) depends on SR1. If SR1 is weakened, does EC1
  lose required capabilities?

  EC1 definition: "The investigation can have knowledge about its own
  state and outputs."

  EC1 requires FROM SR1:
    - A method for acquiring knowledge about outputs
    - Access to output content

  EC1 does NOT require from SR1:
    - Temporal stage separation
    - Discrete examination phases

  Verdict: EC1 is satisfied by Level 2 (outputs + change).
  The downstream chain (SR1 → EC1 → CD2) remains intact.

  If Level 2 is accepted:
    - EC1 ← SR1 + IS2 + IS1a  (all satisfied)
    - CD2 ← CD1 + IS1a + EC1  (all satisfied)
    - Entire graph generative at 9 assumptions.
""")

# ============================================================
# CD2 DOWNSTREAM IMPACT
# ============================================================

print("--- CD2 DOWNSTREAM IMPACT ---")

print("""
  CD2 (Self-affecting procedures) depends on EC1. If EC1 is satisfied
  by Level 2 SR1, CD2 is unaffected.

  Full chain:
    CD2 → CD1, IS1a, EC1
    EC1 → SR1, IS2, IS1a
    SR1 → IS2, IS1a    (Level 2)
    IS1a → OC2
    IS2 → IC1, OC1, IS1a

  This chain resolves completely. No gaps.
""")

# ============================================================
# WHAT IS ACTUALLY LOST AT EACH LEVEL
# ============================================================

print("--- WHAT IS ACTUALLY LOST ---")

print("""
  Moving from Level 4 (stages) to Level 2 (change) loses:
    1. The guarantee that examination is a SEPARATE PHASE from production
       - Level 4: production stops, examination begins
       - Level 2: examination is a functional re-orientation that can
         coexist with production

    2. The guarantee that stages have IDENTIFIABLE BOUNDARIES
       - Level 4: you can point to the moment production ended
       - Level 2: the shift is functional, not necessarily bounded

    3. The guarantee that STAGES ARE DISCRETE
       - Level 4: stages are atomic units
       - Level 2: activity changes continuously; "examination" is a
         gradient, not a switch

  What is NOT lost:
    1. The capacity to examine outputs
    2. The capacity to know one's own state (EC1)
    3. The capacity for self-effects (CD2)
    4. Graph generativity
    5. OC2's unique-root status

  The losses are all about discretization — imposing sharp boundaries
  on what may be a continuous process. If the investigation's activity
  is continuous, the discretization is an approximation, not a
  structural necessity.
""")

# ============================================================
# FINAL SYNTHESIS
# ============================================================

print(f"\n{'='*72}")
print("SYNTHESIS")
print(f"{'='*72}")

print(f"""
  Substrate status after T070 (assuming Level 2 accepted):

    Total assumptions:    9
    Generative:          YES
    Roots:               OC2 (unique)
    Cycles:              0
    IS1b:                ELIMINATED (not structurally required)
    BA1:                 NOT REQUIRED (no bootstrap or sufficiency gap)

  Remaining dependencies:

    OC2 (Distinguishability)
     ├── OC1 (Stable structure)
     │    ├── CD1 (Causal relations)
     │    │    └── CD2 (Self-affecting procedures)
     │    └── IC1 (Extractable information)
     │         └── IS2 (Determinate outputs)
     └── IS1a (Investigative change)
          ├── IS2
          ├── EC1 (Self-knowledge)
          │    └── CD2
          ├── IC1
          └── SR1 (Self-examination of outputs)
               └── EC1

  This is a clean DAG with OC2 as the single generative source.
  
  The strongest unresolved question is no longer structural:
    It is whether Level 2 SR1 is INTERPRETIVELY ADEQUATE.
  
  That is a question about what "self-examination" means,
  not about what the substrate requires.
""")

# ============================================================
# WRITE OUTPUTS
# ============================================================

with open(OUT / "t070_level_comparison.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["level", "name", "coherent", "generative", "n_assumptions",
                 "roots", "capability_loss", "verdict"])
    for a in level_assessments:
        lc = level_configs[a["level"] - 1]
        _, edges, sids = lc
        alive = set(sids)
        sat = compute_survivors(edges, alive)
        gen = sat == alive
        roots = find_roots(edges, sat)
        w.writerow([a["level"], a["name"], str(a["coherent"]), str(gen),
                     len(sids), ";".join(roots), a["loss"], a["verdict"]])

print(f"Wrote t070_level_comparison.csv")

with open(OUT / "t070_sr1_component_analysis.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["component", "provided_by", "necessary", "sufficient_alone", "reason"])
    for comp, info in sr1_components.items():
        w.writerow([comp, ";".join(info["provided_by"]),
                     str(info["necessary"]), str(info["sufficient_alone"]),
                     info["reason"]])

print(f"Wrote t070_sr1_component_analysis.csv")

# Final summary
with open(OUT / "t070_summary.json", "w") as f:
    import json
    json.dump({
        "audit": "T070 — Self-Examination Requirement Audit",
        "accepted_level": 2,
        "accepted_name": "outputs + change",
        "n_assumptions": 9,
        "generative": True,
        "unique_root": "OC2",
        "eliminated_assumptions": ["IS1b"],
        "unrequired_assumptions": ["BA1"],
        "remaining_open_question": (
            "Whether Level 2 SR1 is interpretively adequate — "
            "a definitional question, not a structural one."
        ),
    }, f, indent=2)

print(f"Wrote t070_summary.json")

print(f"\nT070 complete.")
