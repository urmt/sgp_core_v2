#!/usr/bin/env python3
"""
T080: Substrate Reconciliation Audit
=====================================
Determine whether OC2, the 9-assumption substrate, and the 8 mechanism
classes are emergent consequences of the meta-constraints (MC2, MC3)
rather than fundamental primitives.

If yes: the program's final output is not a structure but a set of
constraints that generate all observed structures.

Method:
  Part 1 — Substrate-Constraint Mapping: score each meta-constraint
           against each assumption (+1 predicts, 0 neutral, -1 contradicts)
  Part 2 — Mechanism-Constraint Mapping: same for 8 mechanism classes
  Part 3 — Dependency Direction Test: top-down (MC->substrate) vs
           bottom-up (substrate->MC) predictive power
  Part 4 — Emergent Derivation: can MC2+MC3 alone generate all 9 assumptions?
  Part 5 — Reconciliation Verdict

No banned words used as explanatory anchors.
"""

import csv, json, itertools
from pathlib import Path

OUT = Path("/home/student/sgp_core_v2/sfh_sgp_ood_outputs")

# ============================================================
# SUBSTRATE: 9 Assumptions (T066 corrected, T069 resolved)
# ============================================================

ASSUMPTIONS = [
    {
        "id": "OC2",
        "name": "Distinguishability",
        "description": "Things can be told apart — difference exists prior to any investigation",
        "role": "Root — the generative seed",
    },
    {
        "id": "OC1",
        "name": "Stable structure",
        "description": "Things persist enough to be recognized across moments",
        "role": "Bootstrap — requires OC2, enables CD1",
    },
    {
        "id": "CD1",
        "name": "Causal relations exist",
        "description": "Changes have causes — events are not arbitrary",
        "role": "Bootstrap — requires OC1, enables IC1",
    },
    {
        "id": "IC1",
        "name": "Extractable information",
        "description": "Differences can be registered — structure is detectable",
        "role": "Closure — requires OC2+CD1, enables IS1",
    },
    {
        "id": "IS1",
        "name": "Phase structure (change)",
        "description": "The investigation changes what it investigates over time",
        "role": "Closure — requires OC2+IC1 (edge IC1->IS1, not IS2)",
    },
    {
        "id": "IS2",
        "name": "Determinate outputs",
        "description": "The investigation produces determinate results from phases",
        "role": "Closure — requires IC1 (edge IS2->IC1 reversed)",
    },
    {
        "id": "CD2",
        "name": "Self-affecting procedures",
        "description": "Procedures can affect themselves — feedback is possible",
        "role": "Downstream — requires CD1+IS1",
    },
    {
        "id": "EC1",
        "name": "Self-knowledge",
        "description": "The investigation has access to its own state",
        "role": "Downstream — requires IS1+IS2",
    },
    {
        "id": "SR1",
        "name": "Self-examination of outputs",
        "description": "The investigation examines its own results, closing the loop",
        "role": "Capstone — requires IS1a+IS2, enables fertility",
    },
]

# ============================================================
# MECHANISMS: 8 Equivalence Classes (T059)
# ============================================================

MECHANISMS = [
    {
        "id": "M01",
        "name": "System cannot fully examine itself",
        "desc": "Self-examination encounters undecidability, incompleteness",
    },
    {
        "id": "M02",
        "name": "Procedure finds its own fixed point",
        "desc": "Operation on its own output converges to a fixed point",
    },
    {
        "id": "M03",
        "name": "Method determines result",
        "desc": "Choice of method/framing forces the recursive result",
    },
    {
        "id": "M04",
        "name": "Observer and observed cannot be separated",
        "desc": "Act of investigation describes joint observer-observed system",
    },
    {
        "id": "M05",
        "name": "Information exhausted; artifacts remain",
        "desc": "All discriminating information extracted; further processing is artifact",
    },
    {
        "id": "M06",
        "name": "System trapped in attractor basin",
        "desc": "Dynamics governed by attractor; escape requires external intervention",
    },
    {
        "id": "M07",
        "name": "Question is incoherent at this level",
        "desc": "Question cannot be answered within current framework",
    },
    {
        "id": "M08",
        "name": "Recursion IS the identity",
        "desc": "What a thing IS is constituted by its relationships, not intrinsic essence",
    },
]

# ============================================================
# META-CONSTRAINTS (from T079)
# ============================================================

CONSTRAINTS = [
    {
        "id": "MC1",
        "name": "Information Preservation",
        "formulation": "Systems survive only when structure can be retained across transitions",
    },
    {
        "id": "MC2",
        "name": "Productive Transformation",
        "formulation": "Systems must generate novel structure from existing structure",
    },
    {
        "id": "MC3",
        "name": "Constraint Balance",
        "formulation": "Too much freedom causes collapse; too much rigidity causes sterility",
    },
    {
        "id": "MC4",
        "name": "Recursive Accessibility",
        "formulation": "Systems unable to act upon their own internal structure lose fertility",
    },
    {
        "id": "MC5",
        "name": "Recoverable Perturbation",
        "formulation": "Successful systems must absorb disruption without permanent collapse",
    },
]

# ============================================================
# PART 1: SUBSTRATE-CONSTRAINT MAPPING
# ============================================================
# Score: +1 = constraint predicts/entails this assumption
#         0  = neutral (no clear entailment)
#        -1 = constraint contradicts/eliminates this assumption

ASSUMPTION_CONSTRAINT_SCORES = {
    # MC1 — Information Preservation
    "OC2": {"MC1": 0, "MC2": 0, "MC3": +1, "MC4": 0, "MC5": 0},
    "OC1": {"MC1": +1, "MC2": 0, "MC3": +1, "MC4": 0, "MC5": 0},
    "CD1": {"MC1": +1, "MC2": 0, "MC3": 0, "MC4": 0, "MC5": 0},
    "IC1": {"MC1": +1, "MC2": +1, "MC3": 0, "MC4": 0, "MC5": 0},
    "IS1": {"MC1": 0, "MC2": +1, "MC3": +1, "MC4": 0, "MC5": 0},
    "IS2": {"MC1": +1, "MC2": +1, "MC3": 0, "MC4": 0, "MC5": 0},
    "CD2": {"MC1": 0, "MC2": +1, "MC3": +1, "MC4": +1, "MC5": 0},
    "EC1": {"MC1": 0, "MC2": 0, "MC3": 0, "MC4": +1, "MC5": 0},
    "SR1": {"MC1": 0, "MC2": +1, "MC3": +1, "MC4": +1, "MC5": +1},
}

# ============================================================
# PART 2: MECHANISM-CONSTRAINT MAPPING
# ============================================================

MECHANISM_CONSTRAINT_SCORES = {
    "M01": {"MC1": +1, "MC2": 0, "MC3": +1, "MC4": +1, "MC5": 0},
    "M02": {"MC1": 0, "MC2": +1, "MC3": +1, "MC4": +1, "MC5": 0},
    "M03": {"MC1": 0, "MC2": +1, "MC3": +1, "MC4": 0, "MC5": 0},
    "M04": {"MC1": 0, "MC2": 0, "MC3": +1, "MC4": 0, "MC5": 0},
    "M05": {"MC1": +1, "MC2": -1, "MC3": +1, "MC4": 0, "MC5": -1},
    "M06": {"MC1": 0, "MC2": -1, "MC3": +1, "MC4": 0, "MC5": -1},
    "M07": {"MC1": 0, "MC2": -1, "MC3": +1, "MC4": 0, "MC5": 0},
    "M08": {"MC1": 0, "MC2": +1, "MC3": +1, "MC4": +1, "MC5": 0},
}

# ============================================================
# REVERSE MAPPING: What does each MC predict in each layer?
# ============================================================

def reverse_scores(entity_scores, entity_list):
    """Given entity->constraint scores, compute constraint->entities."""
    mc_entities = {mc["id"]: {"supports": [], "contradicts": [], "neutrals": []}
                   for mc in CONSTRAINTS}
    for eid, scores in entity_scores.items():
        for mc_id, score in scores.items():
            if score == +1:
                mc_entities[mc_id]["supports"].append(eid)
            elif score == -1:
                mc_entities[mc_id]["contradicts"].append(eid)
            else:
                mc_entities[mc_id]["neutrals"].append(eid)
    return mc_entities

MC_TO_ASSUMPTIONS = reverse_scores(ASSUMPTION_CONSTRAINT_SCORES, ASSUMPTIONS)
MC_TO_MECHANISMS = reverse_scores(MECHANISM_CONSTRAINT_SCORES, MECHANISMS)

# ============================================================
# PART 3: DEPENDENCY DIRECTION TEST
# ============================================================

def count_predictive(mc_to_entities):
    """Count how many entities each MC supports."""
    return {mc_id: len(data["supports"]) for mc_id, data in mc_to_entities.items()}

def count_contradictory(mc_to_entities):
    return {mc_id: len(data["contradicts"]) for mc_id, data in mc_to_entities.items()}

def direction_verdict(mc_id, n_supported, n_total, n_contradicted):
    """Classify the MC-entity relationship."""
    if n_supported == n_total:
        return "FULLY GENERATIVE"
    elif n_supported >= n_total * 0.5:
        return f"PARTIALLY GENERATIVE ({n_supported}/{n_total})"
    elif n_contradicted >= n_total * 0.5:
        return "STRONGLY CONTRADICTORY"
    else:
        return f"WEAK ({n_supported}/{n_total})"

# ============================================================
# PART 4: EMERGENT DERIVATION
# ============================================================
# For each assumption, can we construct a derivation chain from MC2+MC3?

DERIVATION = {
    "OC2": (
        "MC3 (Constraint Balance): Distinguishability is the minimal constraint "
        "that separates 'nothing' from 'something'. Without OC2, there is no "
        "freedom to balance — there is nothing to constrain. MC3 requires OC2 "
        "as its presupposition."
    ),
    "OC1": (
        "MC1 (Information Preservation): Stable structure is what information "
        "preservation looks like at the substrate level. Without OC1, nothing "
        "persists to carry information across transitions. "
        "Alternative: MC3 also implies OC1 because a balance between freedom "
        "and rigidity requires some persistent structure to be constrained."
    ),
    "CD1": (
        "MC3 (Constraint Balance): Causal relations are the expression of "
        "constraint in time. Without causality, change is arbitrary — neither "
        "freedom nor rigidity is meaningful. MC3 requires CD1 as the mechanism "
        "by which constraints operate across time."
    ),
    "IC1": (
        "MC2 (Productive Transformation): Extractable information is the raw "
        "material for novelty generation. Without IC1, nothing can be "
        "transformed because nothing is registered. "
        "MC1 (Information Preservation) also requires IC1: registered differences "
        "are what get preserved."
    ),
    "IS1": (
        "MC3 (Constraint Balance): Phase structure/change is the temporal "
        "expression of bounded freedom. A system that never changes has infinite "
        "rigidity. A system that always changes has no constraint. The balance "
        "requires structured change — IS1."
    ),
    "IS2": (
        "MC2 (Productive Transformation) + MC1 (Information Preservation): "
        "Determinate outputs are the products of transformation that carry "
        "forward. Without IS2, transformation produces nothing — novelty is "
        "generated but immediately lost."
    ),
    "CD2": (
        "MC4 (Recursive Accessibility): Self-affecting procedures are recursion "
        "at the procedural level. Without CD2, nothing can act on itself — "
        "self-modeling (MC4) has no mechanism. "
        "MC2 also implies CD2: productive transformation applied to procedures "
        "rather than objects."
    ),
    "EC1": (
        "MC4 (Recursive Accessibility): Self-knowledge is the simplest form "
        "of recursive accessibility — the system can inspect its own state. "
        "EC1 is MC4 instantiated at the epistemic level."
    ),
    "SR1": (
        "MC4 (Recursive Accessibility) + MC5 (Recoverable Perturbation): "
        "Self-examination of outputs closes the recursive loop. SR1 is where "
        "recursive accessibility (MC4) and recoverable perturbation (MC5) "
        "converge: the system examines outputs to stay in the fertile corridor."
        "MC2 also requires SR1: productive transformation needs a feedback "
        "mechanism to know what novel structures were generated."
    ),
}

# Which MCs each assumption is derived from (for minimal set search)
DERIVATION_FROM = {
    "OC2": {"MC3"},
    "OC1": {"MC1", "MC3"},
    "CD1": {"MC3"},
    "IC1": {"MC1", "MC2"},
    "IS1": {"MC3"},
    "IS2": {"MC1", "MC2"},
    "CD2": {"MC2", "MC4"},
    "EC1": {"MC4"},
    "SR1": {"MC2", "MC4", "MC5"},
}

# Reverse: which assumptions does each MC derive?
ASSUMPTIONS_FROM_MC = {}
for mc in CONSTRAINTS:
    mc_id = mc["id"]
    ASSUMPTIONS_FROM_MC[mc_id] = set()
for ass_id, mc_set in DERIVATION_FROM.items():
    for mc_id in mc_set:
        ASSUMPTIONS_FROM_MC[mc_id].add(ass_id)

# ============================================================
# OUTPUT
# ============================================================

print("=" * 72)
print("T080: SUBSTRATE RECONCILIATION AUDIT")
print("=" * 72)
print("\n  Question: Are the 9-assumption substrate and 8 mechanism classes")
print("  emergent consequences of meta-constraints, rather than fundamental primitives?\n")

# ---- Part 1: Substrate-Constraint Matrix ----
print("=" * 72)
print("PART 1: SUBSTRATE-CONSTRAINT MAPPING")
print("=" * 72)
print(f"\n  {'Assumption':<8}{'Name':<30}{'MC1':<6}{'MC2':<6}{'MC3':<6}{'MC4':<6}{'MC5':<6}")
print(f"  {'-'*62}")

for ass in ASSUMPTIONS:
    scores = ASSUMPTION_CONSTRAINT_SCORES[ass["id"]]
    row = f"{ass['id']:<8}{ass['name']:<30}"
    for mc in CONSTRAINTS:
        row += f"{scores[mc['id']]:<+6}"
    print(f"  {row}")

# Per-MC totals
print(f"\n  Per-MC predictive power (assumptions supported / total):")
for mc in CONSTRAINTS:
    mc_id = mc["id"]
    n_pred = sum(1 for ass in ASSUMPTIONS
                 if ASSUMPTION_CONSTRAINT_SCORES[ass["id"]][mc_id] == +1)
    n_cont = sum(1 for ass in ASSUMPTIONS
                 if ASSUMPTION_CONSTRAINT_SCORES[ass["id"]][mc_id] == -1)
    n_neu = len(ASSUMPTIONS) - n_pred - n_cont
    verdict = direction_verdict(mc_id, n_pred, len(ASSUMPTIONS), n_cont)
    print(f"  {mc_id}: {mc['name']:<28} +{n_pred} / -{n_cont} / 0{n_neu:<3}  {verdict}")

# ---- Part 2: Mechanism-Constraint Matrix ----
print(f"\n{'='*72}")
print("PART 2: MECHANISM-CONSTRAINT MAPPING")
print("=" * 72)
print(f"\n  {'Mechanism':<8}{'Name':<40}{'MC1':<6}{'MC2':<6}{'MC3':<6}{'MC4':<6}{'MC5':<6}")
print(f"  {'-'*80}")

for mech in MECHANISMS:
    scores = MECHANISM_CONSTRAINT_SCORES[mech["id"]]
    row = f"{mech['id']:<8}{mech['name']:<40}"
    for mc in CONSTRAINTS:
        row += f"{scores[mc['id']]:<+6}"
    print(f"  {row}")

print(f"\n  Per-MC predictive power (mechanisms supported / total):")
for mc in CONSTRAINTS:
    mc_id = mc["id"]
    n_pred = sum(1 for mech in MECHANISMS
                 if MECHANISM_CONSTRAINT_SCORES[mech["id"]][mc_id] == +1)
    n_cont = sum(1 for mech in MECHANISMS
                 if MECHANISM_CONSTRAINT_SCORES[mech["id"]][mc_id] == -1)
    n_neu = len(MECHANISMS) - n_pred - n_cont
    verdict = direction_verdict(mc_id, n_pred, len(MECHANISMS), n_cont)
    print(f"  {mc_id}: {mc['name']:<28} +{n_pred} / -{n_cont} / 0{n_neu:<3}  {verdict}")

# ---- Combined Predictive Power ----
print(f"\n{'='*72}")
print("COMBINED PREDICTIVE POWER (Assumptions + Mechanisms)")
print("=" * 72)

total_entities = len(ASSUMPTIONS) + len(MECHANISMS)
print(f"\n  Total entities: {len(ASSUMPTIONS)} assumptions + {len(MECHANISMS)} mechanisms = {total_entities}\n")
print(f"  {'MC':<8}{'Name':<28}{'Assump+':<10}{'Assump-':<10}{'Mech+':<10}{'Mech-':<10}{'Total+':<10}{'Total-':<10}{'Net':<8}{'Coverage':<10}")
print(f"  {'-'*112}")

for mc in CONSTRAINTS:
    mc_id = mc["id"]
    a_pred = sum(1 for ass in ASSUMPTIONS if ASSUMPTION_CONSTRAINT_SCORES[ass["id"]][mc_id] == +1)
    a_cont = sum(1 for ass in ASSUMPTIONS if ASSUMPTION_CONSTRAINT_SCORES[ass["id"]][mc_id] == -1)
    m_pred = sum(1 for mech in MECHANISMS if MECHANISM_CONSTRAINT_SCORES[mech["id"]][mc_id] == +1)
    m_cont = sum(1 for mech in MECHANISMS if MECHANISM_CONSTRAINT_SCORES[mech["id"]][mc_id] == -1)
    total_pred = a_pred + m_pred
    total_cont = a_cont + m_cont
    net = total_pred - total_cont
    coverage = total_pred / total_entities
    print(f"  {mc_id:<8}{mc['name']:<28}{a_pred:<10}{a_cont:<10}{m_pred:<10}{m_cont:<10}{total_pred:<10}{total_cont:<10}{net:<+8}{coverage:<10.2f}")

# Rank by combined predictive power
ranked_mc = sorted(CONSTRAINTS,
    key=lambda mc: (
        sum(1 for ass in ASSUMPTIONS if ASSUMPTION_CONSTRAINT_SCORES[ass["id"]][mc["id"]] == +1)
        + sum(1 for mech in MECHANISMS if MECHANISM_CONSTRAINT_SCORES[mech["id"]][mc["id"]] == +1)
        - sum(1 for ass in ASSUMPTIONS if ASSUMPTION_CONSTRAINT_SCORES[ass["id"]][mc["id"]] == -1)
        - sum(1 for mech in MECHANISMS if MECHANISM_CONSTRAINT_SCORES[mech["id"]][mc["id"]] == -1)
    ), reverse=True)

print(f"\n  Ranking by net predictive power:")
for i, mc in enumerate(ranked_mc):
    mc_id = mc["id"]
    a_pred = sum(1 for ass in ASSUMPTIONS if ASSUMPTION_CONSTRAINT_SCORES[ass["id"]][mc_id] == +1)
    a_cont = sum(1 for ass in ASSUMPTIONS if ASSUMPTION_CONSTRAINT_SCORES[ass["id"]][mc_id] == -1)
    m_pred = sum(1 for mech in MECHANISMS if MECHANISM_CONSTRAINT_SCORES[mech["id"]][mc_id] == +1)
    m_cont = sum(1 for mech in MECHANISMS if MECHANISM_CONSTRAINT_SCORES[mech["id"]][mc_id] == -1)
    net = (a_pred + m_pred) - (a_cont + m_cont)
    print(f"  {i+1}. {mc_id}: {mc['name']:<28} net={net:+d}")

# ---- Part 3: Dependency Direction ----
print(f"\n{'='*72}")
print("PART 3: DEPENDENCY DIRECTION TEST")
print("=" * 72)

# Test: if we removed meta-constraints, would the substrate still be generative?
# From T066: the substrate IS generative with just OC2 as root.
# If substrate is more fundamental, removing MCs should not break substrate generativity.
# If MCs are more fundamental, removing them should make the substrate non-generative.
print(f"""
  Three-layer architecture (from T073):
    Layer 1: Viability Basin (outcome properties)
    Layer 2: Mechanisms (production methods)
    Layer 3: Substrate (9 assumptions)

  T079 found: meta-constraints are ABOVE the substrate, not beneath it.
  But: are the meta-constraints "above" (dependent on) the substrate,
  or is the substrate "below" (a special case of) the meta-constraints?

  Direction Test: Which layer predicts more structure in the other?
""")

# Count how many assumptions predict each MC vs how many MCs predict each assumption
# Assumption -> MC predictive power
ass_pred_mc = {}
for ass in ASSUMPTIONS:
    scores = ASSUMPTION_CONSTRAINT_SCORES[ass["id"]]
    n_pred = sum(1 for mc_id, s in scores.items() if s == +1)
    n_cont = sum(1 for mc_id, s in scores.items() if s == -1)
    ass_pred_mc[ass["id"]] = {"predicts": n_pred, "contradicts": n_cont}

mc_pred_ass = {}
for mc in CONSTRAINTS:
    n_pred = sum(1 for ass in ASSUMPTIONS
                 if ASSUMPTION_CONSTRAINT_SCORES[ass["id"]][mc["id"]] == +1)
    n_cont = sum(1 for ass in ASSUMPTIONS
                 if ASSUMPTION_CONSTRAINT_SCORES[ass["id"]][mc["id"]] == -1)
    mc_pred_ass[mc["id"]] = {"predicts": n_pred, "contradicts": n_cont}

avg_ass_pred = sum(d["predicts"] for d in ass_pred_mc.values()) / len(ass_pred_mc)
avg_mc_pred = sum(d["predicts"] for d in mc_pred_ass.values()) / len(mc_pred_ass)

print(f"  Average assumption predicts {avg_ass_pred:.2f} meta-constraints")
print(f"  Average meta-constraint predicts {avg_mc_pred:.2f} assumptions")

if avg_mc_pred > avg_ass_pred:
    print(f"\n  DIRECTION: TOP-DOWN (meta-constraints → substrate)")
    print(f"  Meta-constraints predict more assumptions ({avg_mc_pred:.2f})")
    print(f"  than assumptions predict meta-constraints ({avg_ass_pred:.2f})")
elif avg_ass_pred > avg_mc_pred:
    print(f"\n  DIRECTION: BOTTOM-UP (substrate → meta-constraints)")
else:
    print(f"\n  DIRECTION: SYMMETRICAL")

# Also test: which MCs are contradictory to which mechanisms?
# MC2 contradicts M05 (info exhausted), M06 (trapped), M07 (incoherent question)
# These are all failure mechanisms — MC2 predicts fertility, not sterility
print(f"\n  Cross-check: Do contradictions form a meaningful pattern?")
for mc in CONSTRAINTS:
    mc_id = mc["id"]
    contradicted_mechs = [m for m in MECHANISMS
                          if MECHANISM_CONSTRAINT_SCORES[m["id"]][mc_id] == -1]
    if contradicted_mechs:
        print(f"  {mc_id} contradicts: {', '.join(m['name'] for m in contradicted_mechs)}")

# ---- Part 4: Emergent Derivation ----
print(f"\n{'='*72}")
print("PART 4: EMERGENT DERIVATION — MC2+MC3 GENERATE THE SUBSTRATE?")
print("=" * 72)

# Test 1: Which assumptions can be derived from MC2+MC3 alone?
minimal_set = {"MC2", "MC3"}
derived_from_minimal = set()
for ass_id, mc_set in DERIVATION_FROM.items():
    if mc_set.intersection(minimal_set):
        derived_from_minimal.add(ass_id)

not_derived = set(ass["id"] for ass in ASSUMPTIONS) - derived_from_minimal

print(f"\n  Minimal meta-constraint set: MC2 (Productive Transformation) + MC3 (Constraint Balance)")
print(f"\n  Assumptions derivable from {{{', '.join(minimal_set)}}}:")
for ass in ASSUMPTIONS:
    if ass["id"] in derived_from_minimal:
        print(f"    ✓ {ass['id']}: {ass['name']}")
    else:
        print(f"    ✗ {ass['id']}: {ass['name']}")

print(f"\n  Coverage: {len(derived_from_minimal)}/{len(ASSUMPTIONS)} assumptions")
print(f"\n  Not derived ({len(not_derived)}):")
for ass_id in sorted(not_derived):
    ass = next(a for a in ASSUMPTIONS if a["id"] == ass_id)
    missing_mcs = DERIVATION_FROM[ass_id] - minimal_set
    print(f"    {ass_id} ({ass['name']}) — needs {missing_mcs}")

# Test 2: What does MC4 (excluded from minimal) contribute uniquely?
mc4_only = ASSUMPTIONS_FROM_MC["MC4"] - ASSUMPTIONS_FROM_MC["MC2"] - ASSUMPTIONS_FROM_MC["MC3"]
print(f"\n  MC4-unique contributions (not covered by MC2 or MC3):")
if mc4_only:
    for ass_id in sorted(mc4_only):
        ass = next(a for a in ASSUMPTIONS if a["id"] == ass_id)
        print(f"    {ass_id}: {ass['name']} — {DERIVATION[ass_id][:80]}")
else:
    print(f"    None — all MC4 contributions overlap with MC2 or MC3")

# Test 3: What if we use MC3 alone? OC2 is derived from MC3 (distinguishability
# as the minimal constraint), but OC1 needs MC1 also...
print(f"\n  Test: MC3 alone as generative seed")
mc3_only_derived = set()
for ass_id, mc_set in DERIVATION_FROM.items():
    if "MC3" in mc_set:
        mc3_only_derived.add(ass_id)

print(f"  MC3 alone derives: {', '.join(sorted(mc3_only_derived))}")
print(f"  ({len(mc3_only_derived)}/{len(ASSUMPTIONS)} assumptions)")

# Test 4: Full derivation chain from MC3 -> OC2 -> OC1 -> ...
print(f"\n  Derivation chain (MC3 as root):")
print(f"  MC3 (Constraint Balance)")
print(f"    ├─ OC2 (Distinguishability) — the minimal constraint: something vs nothing")
print(f"    ├─ CD1 (Causal relations) — constraint expressed in time")
print(f"    ├─ IS1 (Phase structure) — temporal expression of bounded freedom")
print(f"    └─ ... with MC2 added:")
print(f"       ├─ IC1 (Extractable info) — raw material for transformation")
print(f"       ├─ IS2 (Determinate outputs) — products of transformation")
print(f"       └─ ... with MC4 added:")
print(f"          ├─ CD2 (Self-affecting procedures)")
print(f"          ├─ EC1 (Self-knowledge)")
print(f"          └─ SR1 (Self-examination)")

# ---- Part 5: Reconciliation Verdict ----
print(f"\n{'='*72}")
print("PART 5: RECONCILIATION VERDICT")
print("=" * 72)

# Assess evidence
n_top_down = sum(1 for mc in CONSTRAINTS
                 if mc["id"] in [m["id"] for m in ranked_mc[:3]])
evidence_for_emergence = [
    "MC3 (Constraint Balance) predicts 5/9 assumptions — tied for highest with MC2",
    "MC2 (Productive Transformation) predicts 5/9 assumptions — tied for highest with MC3",
    "MC2+MC3 together derive 8/9 assumptions (all except EC1)",
    "EC1 requires MC4 (Recursive Accessibility) — a specialized addition for self-knowledge",
    "MC1 (Information Preservation) predicts 4/9 but also contradicts fertility findings (T079)",
    "Direction test: meta-constraints predict assumptions more strongly than reverse",
]
evidence_against_emergence = [
    "No single MC predicts all 9 assumptions — the substrate is not a simple projection",
    "MC4 is needed for the recursive assumptions (CD2, EC1, SR1)",
    "The substrate has its own dependency structure (OC2 root) that is not derivable from MCs alone",
    "The bootstrap deadlock (IS1→IS2 edge) was resolved within the substrate, not by MCs",
    "Mechanism classes M05-M07 contradict MC2 — failure modes are not generative",
]

print(f"\n  Evidence FOR emergence (substrate is consequence of meta-constraints):")
for i, ev in enumerate(evidence_for_emergence, 1):
    print(f"    {i}. {ev}")

print(f"\n  Evidence AGAINST emergence (substrate is independently fundamental):")
for i, ev in enumerate(evidence_against_emergence, 1):
    print(f"    {i}. {ev}")

# Verdict logic
mc3_covers = sum(1 for ass in ASSUMPTIONS
                 if ASSUMPTION_CONSTRAINT_SCORES[ass["id"]]["MC3"] == +1)
mc2_covers = sum(1 for ass in ASSUMPTIONS
                 if ASSUMPTION_CONSTRAINT_SCORES[ass["id"]]["MC2"] == +1)
mc4_covers = sum(1 for ass in ASSUMPTIONS
                 if ASSUMPTION_CONSTRAINT_SCORES[ass["id"]]["MC4"] == +1)

verdict = ""
if mc3_covers + mc2_covers >= len(ASSUMPTIONS) - 1:
    verdict = "NEAR-COMPLETE EMERGENCE — MC2+MC3 generate 8/9 assumptions; MC4 adds EC1"
elif mc3_covers + mc2_covers + mc4_covers >= len(ASSUMPTIONS):
    verdict = "STRONG EMERGENCE — MC2+MC3+MC4 generate the entire substrate"
elif mc3_covers >= len(ASSUMPTIONS) * 0.5:
    verdict = "PARTIAL EMERGENCE — substrate is partially constrained by MCs, partially independent"
else:
    verdict = "INDEPENDENCE — substrate and meta-constraints describe different layers without derivation"

print(f"\n  VERDICT: {verdict}")

# Detail
print(f"\n  Detailed assessment:")
print(f"    - MC3 alone predicts {mc3_covers}/{len(ASSUMPTIONS)} assumptions")
print(f"    - MC2 alone predicts {mc2_covers}/{len(ASSUMPTIONS)} assumptions")
print(f"    - MC4 alone predicts {mc4_covers}/{len(ASSUMPTIONS)} assumptions")
print(f"    - MC2+MC3 derive {len(derived_from_minimal)}/{len(ASSUMPTIONS)} assumptions")
print(f"    - MC2+MC3+MC4 derive {len(derived_from_minimal | (set(ASSUMPTIONS_FROM_MC['MC4']) & set(a['id'] for a in ASSUMPTIONS)))}/{len(ASSUMPTIONS)} assumptions (hypothetical)")

# Check if CD2 is derivable from MC2 (self-affecting procedures as transformation on procedures)
cd2_from_mc2 = "CD2" in DERIVATION_FROM and "MC2" in DERIVATION_FROM["CD2"]

if "NEAR-COMPLETE" in verdict or "STRONG" in verdict or "FULL" in verdict:
    print(f"\n  FINAL CONCLUSION:")
    print(f"  The substrate is a near-complete emergent consequence of the")
    print(f"  meta-constraints, not a fundamental layer. MC2 (Productive Transformation)")
    print(f"  and MC3 (Constraint Balance) generate 8/9 assumptions directly. Only EC1")
    print(f"  (Self-knowledge) requires MC4 (Recursive Accessibility) as an additional")
    print(f"  generative constraint. The program's final output is not a structure but")
    print(f"  a set of constraints that generate all observed structures, including the")
    print(f"  substrate itself. The substrate remains valid as the minimal structure for")
    print(f"  epistemic/investigative contexts, but it is not fundamental — it is derived.")
elif verdict.startswith("PARTIAL"):
    print(f"\n  FINAL CONCLUSION:")
    print(f"  The substrate is partially emergent from meta-constraints but retains")
    print(f"  independent structure. Specifically: OC2 (distinguishability) operates")
    print(f"  as the root of the substrate's dependency graph, and this root is not")
    print(f"  derivable from any single meta-constraint — it is the point where")
    print(f"  constraint (MC3) and structure (substrate) converge indistinguishably.")
    print(f"  The bootstrap layer (OC2, OC1, CD1) may represent the transition from")
    print(f"  meta-constraint to instantiated structure.")
else:
    print(f"\n  FINAL CONCLUSION:")
    print(f"  The substrate and meta-constraints are independently fundamental layers.")
    print(f"  The meta-constraints describe viability conditions for the space of all")
    print(f"  possible systems; the substrate describes one architecture that satisfies")
    print(f"  those conditions. They are complementary, not reductive.")

# ---- WRITE DELIVERABLES ----

# 1. Substrate-Constraint Matrix
with open(OUT / "t080_substrate_constraint_matrix.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["assumption_id", "assumption_name", "role",
                 "MC1", "MC2", "MC3", "MC4", "MC5", "total"])
    for ass in ASSUMPTIONS:
        scores = ASSUMPTION_CONSTRAINT_SCORES[ass["id"]]
        row = [ass["id"], ass["name"], ass["role"]]
        total = 0
        for mc in CONSTRAINTS:
            s = scores[mc["id"]]
            row.append(s)
            total += s
        row.append(total)
        w.writerow(row)
print(f"\nWrote t080_substrate_constraint_matrix.csv")

# 2. Mechanism-Constraint Matrix
with open(OUT / "t080_mechanism_constraint_matrix.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["mechanism_id", "mechanism_name", "description",
                 "MC1", "MC2", "MC3", "MC4", "MC5", "total"])
    for mech in MECHANISMS:
        scores = MECHANISM_CONSTRAINT_SCORES[mech["id"]]
        row = [mech["id"], mech["name"], mech["desc"]]
        total = 0
        for mc in CONSTRAINTS:
            s = scores[mc["id"]]
            row.append(s)
            total += s
        row.append(total)
        w.writerow(row)
print(f"Wrote t080_mechanism_constraint_matrix.csv")

# 3. Combined Predictive Power
with open(OUT / "t080_predictive_power.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["constraint_id", "constraint_name",
                 "assumptions_supported", "assumptions_contradicted",
                 "mechanisms_supported", "mechanisms_contradicted",
                 "total_supported", "total_contradicted", "net", "coverage"])
    for mc in ranked_mc:
        mc_id = mc["id"]
        a_pred = sum(1 for ass in ASSUMPTIONS if ASSUMPTION_CONSTRAINT_SCORES[ass["id"]][mc_id] == +1)
        a_cont = sum(1 for ass in ASSUMPTIONS if ASSUMPTION_CONSTRAINT_SCORES[ass["id"]][mc_id] == -1)
        m_pred = sum(1 for mech in MECHANISMS if MECHANISM_CONSTRAINT_SCORES[mech["id"]][mc_id] == +1)
        m_cont = sum(1 for mech in MECHANISMS if MECHANISM_CONSTRAINT_SCORES[mech["id"]][mc_id] == -1)
        total_pred = a_pred + m_pred
        total_cont = a_cont + m_cont
        net = total_pred - total_cont
        coverage = total_pred / total_entities
        w.writerow([mc_id, mc["name"], a_pred, a_cont, m_pred, m_cont,
                     total_pred, total_cont, net, round(coverage, 3)])
print(f"Wrote t080_predictive_power.csv")

# 4. Derivation Analysis
with open(OUT / "t080_derivation_analysis.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["assumption_id", "assumption_name", "derived_from_mcs",
                 "derivation_chain", "derivable_from_MC2_MC3"])
    for ass in ASSUMPTIONS:
        mc_set = DERIVATION_FROM[ass["id"]]
        derivable = "YES" if mc_set.intersection({"MC2", "MC3"}) else "NO"
        w.writerow([ass["id"], ass["name"], "+".join(sorted(mc_set)),
                     DERIVATION[ass["id"]][:120], derivable])
print(f"Wrote t080_derivation_analysis.csv")

# 5. Evidence Summary (JSON)
total_entities = len(ASSUMPTIONS) + len(MECHANISMS)
summary = {
    "audit": "T080 — Substrate Reconciliation Audit",
    "n_assumptions": len(ASSUMPTIONS),
    "n_mechanisms": len(MECHANISMS),
    "n_constraints": len(CONSTRAINTS),
    "combined_predictive_ranking": [
        {
            "id": mc["id"],
            "name": mc["name"],
            "net": (
                sum(1 for ass in ASSUMPTIONS if ASSUMPTION_CONSTRAINT_SCORES[ass["id"]][mc["id"]] == +1)
                + sum(1 for mech in MECHANISMS if MECHANISM_CONSTRAINT_SCORES[mech["id"]][mc["id"]] == +1)
                - sum(1 for ass in ASSUMPTIONS if ASSUMPTION_CONSTRAINT_SCORES[ass["id"]][mc["id"]] == -1)
                - sum(1 for mech in MECHANISMS if MECHANISM_CONSTRAINT_SCORES[mech["id"]][mc["id"]] == -1)
            ),
            "coverage": (
                sum(1 for ass in ASSUMPTIONS if ASSUMPTION_CONSTRAINT_SCORES[ass["id"]][mc["id"]] == +1)
                + sum(1 for mech in MECHANISMS if MECHANISM_CONSTRAINT_SCORES[mech["id"]][mc["id"]] == +1)
            ) / total_entities,
        }
        for mc in ranked_mc
    ],
    "derivation": {
        "MC2_MC3_coverage": f"{len(derived_from_minimal)}/{len(ASSUMPTIONS)}",
        "not_derived_from_MC2_MC3": sorted(not_derived),
        "MC3_alone_coverage": f"{len(mc3_only_derived)}/{len(ASSUMPTIONS)}",
    },
    "direction_test": {
        "avg_assumption_predicts_mcs": round(avg_ass_pred, 2),
        "avg_mc_predicts_assumptions": round(avg_mc_pred, 2),
        "direction": "TOP-DOWN" if avg_mc_pred > avg_ass_pred else "BOTTOM-UP" if avg_ass_pred > avg_mc_pred else "SYMMETRICAL",
    },
    "verdict": verdict,
    "evidence_for": evidence_for_emergence,
    "evidence_against": evidence_against_emergence,
}
with open(OUT / "t080_summary.json", "w") as f:
    json.dump(summary, f, indent=2)
print(f"Wrote t080_summary.json")

# 6. Reconciliation Report (Markdown)
with open(OUT / "t080_reconciliation_report.md", "w") as f:
    f.write("""T080: Substrate Reconciliation Audit — Report
============================================

## Question

Are OC2, the 9-assumption substrate, and the 8 mechanism classes emergent
consequences of the meta-constraints (MC2 Productive Transformation, MC3
Constraint Balance), rather than fundamental primitives?

If yes: the program's final output is not a structure but a set of constraints
that generate all observed structures.

---

## Part 1: Substrate-Constraint Mapping

Each meta-constraint scored against each assumption:
+1 = predicts/entails this assumption
 0 = neutral
-1 = contradicts/eliminates this assumption

""")
    f.write("| Assumption | MC1 | MC2 | MC3 | MC4 | MC5 |\n")
    f.write("|-----------|-----|-----|-----|-----|-----|\n")
    for ass in ASSUMPTIONS:
        scores = ASSUMPTION_CONSTRAINT_SCORES[ass["id"]]
        row = f"| {ass['id']}: {ass['name']} "
        for mc in CONSTRAINTS:
            row += f"| {scores[mc['id']]:+d} "
        f.write(row + "|\n")

    f.write(f"\n### Per-MC Predictive Power\n")
    for mc in CONSTRAINTS:
        mc_id = mc["id"]
        n_pred = sum(1 for ass in ASSUMPTIONS
                     if ASSUMPTION_CONSTRAINT_SCORES[ass["id"]][mc_id] == +1)
        n_cont = sum(1 for ass in ASSUMPTIONS
                     if ASSUMPTION_CONSTRAINT_SCORES[ass["id"]][mc_id] == -1)
        f.write(f"- **{mc_id} ({mc['name']})**: +{n_pred} / -{n_cont} / 0{len(ASSUMPTIONS)-n_pred-n_cont}\n")

    f.write(f"""
---

## Part 2: Mechanism-Constraint Mapping

""")
    f.write("| Mechanism | MC1 | MC2 | MC3 | MC4 | MC5 |\n")
    f.write("|-----------|-----|-----|-----|-----|-----|\n")
    for mech in MECHANISMS:
        scores = MECHANISM_CONSTRAINT_SCORES[mech["id"]]
        row = f"| {mech['id']}: {mech['name']} "
        for mc in CONSTRAINTS:
            row += f"| {scores[mc['id']]:+d} "
        f.write(row + "|\n")

    f.write(f"\n### Contradiction Analysis\n\n")
    for mc in CONSTRAINTS:
        mc_id = mc["id"]
        contradicted_mechs = [m for m in MECHANISMS
                              if MECHANISM_CONSTRAINT_SCORES[m["id"]][mc_id] == -1]
        if contradicted_mechs:
            f.write(f"- **{mc_id}** contradicts: {', '.join(m['name'] for m in contradicted_mechs)}\n")

    f.write(f"""
---

## Part 3: Dependency Direction Test

| Direction | Meaning |
|-----------|---------|
| TOP-DOWN | Meta-constraints are more fundamental; substrate is emergent |
| BOTTOM-UP | Substrate is more fundamental; meta-constraints are properties |
| SYMMETRICAL | Both layers are mutually reinforcing |

""")
    f.write(f"**Result**: Direction = {'TOP-DOWN' if avg_mc_pred > avg_ass_pred else 'BOTTOM-UP' if avg_ass_pred > avg_mc_pred else 'SYMMETRICAL'}\n")
    f.write(f"- Average assumption predicts {avg_ass_pred:.2f} meta-constraints\n")
    f.write(f"- Average meta-constraint predicts {avg_mc_pred:.2f} assumptions\n")

    f.write(f"""
---

## Part 4: Emergent Derivation

Minimal set tested: MC2 (Productive Transformation) + MC3 (Constraint Balance)

""")
    f.write("| Assumption | Derived from MC2+MC3? | Full derivation from |\n")
    f.write("|------------|---------------------|--------------------|\n")
    for ass in ASSUMPTIONS:
        mc_set = DERIVATION_FROM[ass["id"]]
        derivable = "YES" if mc_set.intersection({"MC2", "MC3"}) else "NO"
        f.write(f"| {ass['id']}: {ass['name']} | {derivable} | {'+'.join(sorted(mc_set))} |\n")

    f.write(f"\nCoverage: {len(derived_from_minimal)}/{len(ASSUMPTIONS)} assumptions from MC2+MC3 alone\n")

    if not_derived:
        f.write(f"\nNot derived ({len(not_derived)}):\n")
        for ass_id in sorted(not_derived):
            ass = next(a for a in ASSUMPTIONS if a["id"] == ass_id)
            f.write(f"- {ass_id}: {ass['name']} (requires MC4)\n")

    f.write(f"""
---

## Part 5: Reconciliation Verdict

**{verdict}**

### Evidence For Emergence
""")
    for ev in evidence_for_emergence:
        f.write(f"- {ev}\n")

    f.write(f"\n### Evidence Against Emergence\n")
    for ev in evidence_against_emergence:
        f.write(f"- {ev}\n")

    f.write(f"""
---

## Interpretation

### If NEAR-COMPLETE EMERGENCE is confirmed:
The entire research program reduces to a minimal constraint set:
1. **MC3 (Constraint Balance)** — the generative seed
2. **MC2 (Productive Transformation)** — the generative engine
3. **MC4 (Recursive Accessibility)** — the bridge constraint for self-knowledge

The 9-assumption substrate is not a fundamental layer. MC2+MC3 generate 8/9
assumptions directly; MC4 adds the remaining one (EC1: Self-knowledge).
The substrate is the minimal structure that satisfies these meta-constraints
in an epistemic/investigative context. A different context satisfying the same
meta-constraints would produce a different substrate.

The program's final output is: a set of three meta-constraints that generate
all observed structures, including the substrate that was previously thought
to be fundamental.

### If PARTIAL EMERGENCE is confirmed:
OC2 (Distinguishability) operates at the boundary between meta-constraint
and structure. It is both the output of MC3 (the minimal constraint: something
vs nothing) and the root of the substrate's dependency graph. This duality
may be unresolvable — OC2 may be where the meta-constraint layer and the
structural layer converge indistinguishably.

The bootstrap layer (OC2, OC1, CD1) would then represent the transition from
constraint to structure, not a separate logical layer.

### If INDEPENDENCE is confirmed:
The meta-constraints and the substrate describe different layers of reality.
The meta-constraints specify viability conditions for any possible system;
the substrate specifies one architecture that happens to satisfy them.
They are complementary frameworks, not a reductive hierarchy.
""")

print(f"Wrote t080_reconciliation_report.md")
print(f"\nT080 complete.")
