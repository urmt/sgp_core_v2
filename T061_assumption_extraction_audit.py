#!/usr/bin/env python3
"""
T061: Assumption Extraction Audit
==================================
Identify the hidden assumptions required by each of the 8 T059 mechanism classes.
Not predictions. Not consequences. Only preconditions — what must already be true
before the class can operate.
"""

import csv
from pathlib import Path
from itertools import combinations

OUT = Path("/home/student/sgp_core_v2/sfh_sgp_ood_outputs")

# ============================================================
# ASSUMPTION INVENTORY
# ============================================================
# Each assumption is something that must be true before the class
# can even be formulated, let alone make predictions.
# Structured as: id, domain, statement, is_fundamental (can't be reduced further)

ASSUMPTIONS = {
    # ——— Self-reference / Reflexivity ———
    "SR1": {
        "domain": "self_reference",
        "statement": "The investigation can examine its own outputs as objects of analysis.",
        "is_fundamental": True,
        "note": "Foundational enabler of the entire audit chain. Without this, no phase can use a previous phase's output as input.",
    },
    "SR2": {
        "domain": "self_reference",
        "statement": "The investigation can reflect on its own procedures and methods.",
        "is_fundamental": False,
        "note": "Stronger than SR1 — not just examining outputs but examining how those outputs were produced.",
    },
    "SR3": {
        "domain": "self_reference",
        "statement": "The investigation can detect recurrence — whether it has been in its current state before.",
        "is_fundamental": False,
        "note": "Required to recognize that recursion is happening. Without this, each phase appears novel.",
    },
    # ——— Investigation structure ———
    "IS1": {
        "domain": "investigation_structure",
        "statement": "The investigation is a process with identifiable stages, phases, or states.",
        "is_fundamental": True,
        "note": "Without phase structure, there is no trajectory to analyze. All 8 classes depend on this.",
    },
    "IS2": {
        "domain": "investigation_structure",
        "statement": "The investigation produces determinate results — outputs that can be compared across phases.",
        "is_fundamental": True,
        "note": "If results were random or incomparable, no pattern (recursive or otherwise) could be detected.",
    },
    "IS3": {
        "domain": "investigation_structure",
        "statement": "The investigation's trajectory can be represented abstractly (state space, sequence, graph).",
        "is_fundamental": False,
        "note": "Enables M02, M06. Not strictly required for M03, M07, M08 but implicitly used in their formulation.",
    },
    # ——— Ontological commitments ———
    "OC1": {
        "domain": "ontological",
        "statement": "The phenomenon under study has some stable structure — it is not pure randomness or noise.",
        "is_fundamental": True,
        "note": "Without structure, no explanation of any kind is possible. All 8 classes presuppose something to explain.",
    },
    "OC2": {
        "domain": "ontological",
        "statement": "The phenomenon and the investigation of it are distinguishable (even if inseparable in practice).",
        "is_fundamental": True,
        "note": "Even M04 (inseparability) must distinguish observer from target to then assert their inseparability. Without this distinction, no class can formulate its explanation.",
    },
    "OC3": {
        "domain": "ontological",
        "statement": "There exists an inside/outside boundary relative to the investigative system.",
        "is_fundamental": False,
        "note": "M01 requires this (inside = system, outside = external reference). M06 requires this (inside = attractor, outside = beyond basin). M08 denies this (everything is inside the recursion).",
    },
    "OC4": {
        "domain": "ontological",
        "statement": "The target has properties that are not entirely constituted by the investigation of it.",
        "is_fundamental": False,
        "note": "Assumed by M01, M02, M05, M06. Denied or weakened by M03, M04, M07, M08.",
    },
    # ——— Epistemic commitments ———
    "EC1": {
        "domain": "epistemic",
        "statement": "The investigation can have knowledge about its own state and outputs.",
        "is_fundamental": True,
        "note": "Without self-knowledge, no phase-aware analysis is possible. Required by all classes that reference prior phases, recursion detection, or convergence.",
    },
    "EC2": {
        "domain": "epistemic",
        "statement": "The investigation can know when it has reached a limit of its current method or framework.",
        "is_fundamental": False,
        "note": "Required explicitly by M07 (diagnosing malformation). Also required by M01 (knowing circularity is unresolvable) and M05 (knowing information bound reached).",
    },
    "EC3": {
        "domain": "epistemic",
        "statement": "The investigation can distinguish between different causal explanations that fit the same observations.",
        "is_fundamental": False,
        "note": "Required to formulate any of the 8 classes as distinct explanations. Without this, all classes collapse into 'something recursive happens.'",
    },
    "EC4": {
        "domain": "epistemic",
        "statement": "The investigation can communicate its results and compare them across different formulations.",
        "is_fundamental": False,
        "note": "Required for cross-class comparison (T060). Enables M03 (comparing methods) and M04 (comparing observer stances).",
    },
    # ——— Methodological commitments ———
    "MC1": {
        "domain": "methodological",
        "statement": "Multiple legitimate methods or approaches exist for investigating the phenomenon.",
        "is_fundamental": False,
        "note": "Required by M03 (method choice matters). Assumed by M07 (alternative framings exist). Not required by M01 or M08 (which treat recursion as necessary, not contingent on method).",
    },
    "MC2": {
        "domain": "methodological",
        "statement": "The choice of method constrains or shapes what can be discovered.",
        "is_fundamental": False,
        "note": "Shared by M03 (method determines) and M04 (observer determines). Also implicitly required by M07 (framing determines what recursion looks like).",
    },
    "MC3": {
        "domain": "methodological",
        "statement": "Methodological choices can be changed, and their effects observed.",
        "is_fundamental": False,
        "note": "Required for any experimental discrimination between classes. Without this, no class can be tested against another.",
    },
    # ——— Informational commitments ———
    "IC1": {
        "domain": "informational",
        "statement": "There is information about the phenomenon that the investigation can extract and process.",
        "is_fundamental": True,
        "note": "Cornerstone assumption. Without extractable information, the investigation has no raw material. All classes require this.",
    },
    "IC2": {
        "domain": "informational",
        "statement": "The available information about the phenomenon is finite.",
        "is_fundamental": False,
        "note": "Required explicitly by M05 (information exhausted). Assumed by M01 (finite system) and M02 (finite computation).",
    },
    "IC3": {
        "domain": "informational",
        "statement": "Processing information can change it — information can be lost, transformed, or degraded.",
        "is_fundamental": False,
        "note": "Required by M05 (processing consumes information). Also required by M04 (observation changes the observed) and M06 (dynamics transform state).",
    },
    # ——— Causal / Dependency ———
    "CD1": {
        "domain": "causal",
        "statement": "Causal, dependency, or explanatory relationships exist between elements of the phenomenon.",
        "is_fundamental": True,
        "note": "Without causality or dependency, no class can attribute recursion to any cause. All 8 classes depend on there being something that connects observations.",
    },
    "CD2": {
        "domain": "causal",
        "statement": "The investigation's procedures produce effects on the investigation itself or its object.",
        "is_fundamental": True,
        "note": "The audit chain exists because each phase affects the next. Without this, no class can explain why the investigation follows the trajectory it does.",
    },
    "CD3": {
        "domain": "causal",
        "statement": "Some explanations are better than others — there is a basis for preferring one account.",
        "is_fundamental": False,
        "note": "Required to formulate explanations at all. If no account is better than any other, the 8 classes are indistinguishable by any metric.",
    },
    # ——— Closure / Termination ———
    "CT1": {
        "domain": "closure",
        "statement": "The investigation can in principle reach a stopping point or recognize when further investigation is unproductive.",
        "is_fundamental": False,
        "note": "Required by M01, M02, M05 (recognition of limit). Denied implicitly by M06 (can't escape attractor), reinterpreted by M08 (stopping = recognizing recursion as answer).",
    },
    "CT2": {
        "domain": "closure",
        "statement": "External reference is in principle possible — something exists outside the investigation's current frame.",
        "is_fundamental": False,
        "note": "Required by M01 (external framework), M05 (new data), M06 (external perturbation). Denied by M08. Irrelevant to M07 (question is about framing, not external reference).",
    },
}

# ============================================================
# CLASS → ASSUMPTION MAPPING
# ============================================================

CLASS_ASSUMPTIONS = {
    "M01": {
        "name": "System cannot fully examine itself",
        "requires": [
            "SR1", "SR2", "SR3",    # must track its own examination
            "IS1", "IS2",           # must have phase structure and determinate outputs
            "OC1", "OC2", "OC3", "OC4",  # phenomenon has structure, inside/outside, target exists
            "EC1", "EC2",           # must know its limits and state
            "IC1", "IC2",           # finite information within the system
            "CD1", "CD2",           # causal dependency chain
            "CT1", "CT2",           # must be able to reach limit, external reference exists
        ],
        "rejects": [],
        "neutral": ["SR3", "IS3", "EC3", "EC4", "MC1", "MC2", "MC3", "IC3", "CD3", "CT1", "CT2"],
    },
    "M02": {
        "name": "Procedure finds its own fixed point",
        "requires": [
            "SR1", "SR2",           # must reflect on procedure
            "IS1", "IS2", "IS3",    # needs trajectory representation, not just phases
            "OC1", "OC2", "OC4",    # phenomenon has structure distinguishable from procedure
            "EC1", "EC3",           # must know convergence and distinguish explanations
            "IC1", "IC2",           # finite computation space
            "CD1", "CD2",           # causal structure linking procedure to result
            "CT1",                  # must be able to reach fixed point
        ],
        "rejects": ["MC1", "MC2", "MC3"],
        "neutral": ["SR3", "OC3", "EC2", "EC4", "IC3", "CD3", "CT2"],
    },
    "M03": {
        "name": "Method determines result",
        "requires": [
            "SR1", "SR2",           # must examine method effects
            "IS1", "IS2",           # phase structure, comparable outputs
            "OC1", "OC2",           # phenomenon has structure, distinguishable from investigation
            "EC1", "EC3", "EC4",    # must compare explanations across methods
            "MC1", "MC2", "MC3",    # multiple methods exist, constrain results, can be changed
            "IC1",                  # information exists (to have a result about)
            "CD1", "CD2", "CD3",    # method choice causes result, better/worse exists
        ],
        "rejects": ["OC4", "CT1", "CT2"],
        "neutral": ["SR3", "IS3", "OC3", "EC2", "IC2", "IC3", "CT2"],
    },
    "M04": {
        "name": "Observer and target inseparable",
        "requires": [
            "SR1", "SR2", "SR3",    # must examine observer-target dynamic
            "IS1", "IS2",           # phase structure, determinate outputs
            "OC1", "OC2",           # phenomenon has structure, must distinguish to assert inseparability
            "EC1", "EC3", "EC4",    # must compare explanations, communicate
            "IC1", "IC3",           # information exists, can be transformed by observation
            "CD1", "CD2",           # observation affects observed
            "MC3",                  # must be able to change observer stance
        ],
        "rejects": ["OC3", "OC4", "CT2"],
        "neutral": ["SR3", "IS3", "EC2", "IC2", "MC1", "MC2", "CD3", "CT1"],
    },
    "M05": {
        "name": "Information exhausted",
        "requires": [
            "SR1", "SR2", "SR3",    # must track its own information consumption
            "IS1", "IS2",           # phase structure, comparable outputs
            "OC1", "OC2", "OC4",    # phenomenon has structure with independent properties
            "EC1", "EC2",           # must know when information bound reached
            "IC1", "IC2", "IC3",    # finite information that can be consumed/degraded
            "CD1", "CD2",           # causal chain of information processing
            "CT1", "CT2",           # must recognize limit, external information exists
        ],
        "rejects": [],
        "neutral": ["SR3", "IS3", "OC3", "EC3", "EC4", "MC1", "MC2", "MC3", "CD3"],
    },
    "M06": {
        "name": "Attractor/trap dynamics",
        "requires": [
            "SR1", "SR2", "SR3",    # must detect recurrence
            "IS1", "IS2", "IS3",    # needs state space trajectory
            "OC1", "OC2", "OC3",    # phenomenon has structure with inside/outside
            "EC1",                  # must know dynamical state
            "IC1", "IC3",           # information processed and transformed
            "CD1", "CD2",           # causal dynamics
            "CT2",                  # external perturbation possible
        ],
        "rejects": ["CT1"],
        "neutral": ["OC4", "EC2", "EC3", "EC4", "IC2", "MC1", "MC2", "MC3", "CD3"],
    },
    "M07": {
        "name": "Inquiry malformed at current level",
        "requires": [
            "SR1", "SR2", "SR3",    # must examine its own framing
            "IS1", "IS2",           # phase structure, determinate outputs
            "OC1", "OC2",           # phenomenon has structure, distinct from inquiry
            "EC1", "EC2", "EC3",    # must diagnose malformation, distinguish explanations
            "IC1",                  # information exists
            "CD1", "CD2",           # framing affects results
            "MC1",                  # alternative framings exist
            "CT1",                  # can recognize need to stop/change frame
        ],
        "rejects": ["OC4", "CT2"],
        "neutral": ["SR3", "IS3", "OC3", "EC4", "IC2", "IC3", "MC2", "MC3", "CD3"],
    },
    "M08": {
        "name": "Recursion IS the phenomenon",
        "requires": [
            "SR1", "SR3",           # must detect recursion as pattern
            "IS1", "IS2",           # phase structure, determinate outputs
            "OC1", "OC2",           # phenomenon has structure, distinguishable from investigation
            "EC1", "EC3",           # must recognize recursion as informative
            "IC1",                  # information exists
            "CD1", "CD2",           # recursion is the causal/explanatory structure
            "CD3",                  # recursive explanation is better than non-recursive
        ],
        "rejects": ["OC3", "OC4", "CT1", "CT2"],
        "neutral": ["SR2", "IS3", "EC2", "EC4", "IC2", "IC3", "MC1", "MC2", "MC3"],
    },
}

# ============================================================
# VALIDATION
# ============================================================

all_class_assumptions = set()
for cid, cdata in CLASS_ASSUMPTIONS.items():
    for r in cdata["requires"]:
        all_class_assumptions.add(r)

# Only report missing assumptions that are actually used
missing = all_class_assumptions - set(ASSUMPTIONS.keys())
if missing:
    print(f"WARNING: {len(missing)} assumptions referenced but not defined: {missing}")

defined = set(ASSUMPTIONS.keys())
unused = defined - all_class_assumptions
if unused:
    print(f"NOTE: {len(unused)} assumptions defined but not used by any class: {unused}")

print(f"Assumption inventory: {len(ASSUMPTIONS)} total, {len(all_class_assumptions)} referenced by classes")

# ============================================================
# DELIVERABLE 1: Assumption Inventory
# ============================================================

with open(OUT / "t061_assumption_inventory.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["assumption_id", "domain", "statement", "is_fundamental", "note",
                 "required_by", "rejected_by", "neutral_for"])
    for aid in sorted(ASSUMPTIONS.keys()):
        a = ASSUMPTIONS[aid]
        required_by = sorted([cid for cid, cd in CLASS_ASSUMPTIONS.items() if aid in cd["requires"]])
        rejected_by = sorted([cid for cid, cd in CLASS_ASSUMPTIONS.items() if aid in cd["rejects"]])
        neutral_for = sorted([cid for cid, cd in CLASS_ASSUMPTIONS.items()
                              if aid not in cd["requires"] and aid not in cd["rejects"]])
        w.writerow([aid, a["domain"], a["statement"], str(a["is_fundamental"]),
                     a.get("note", ""),
                     ";".join(required_by) if required_by else "",
                     ";".join(rejected_by) if rejected_by else "",
                     ";".join(neutral_for) if neutral_for else ""])

print("Wrote t061_assumption_inventory.csv")

# ============================================================
# DELIVERABLE 2: Shared Assumption Matrix
# ============================================================

class_ids = sorted(CLASS_ASSUMPTIONS.keys())
assumption_ids = sorted(ASSUMPTIONS.keys())

with open(OUT / "t061_shared_assumption_matrix.csv", "w", newline="") as f:
    w = csv.writer(f)
    header = ["assumption_id", "domain", "statement"] + class_ids + ["n_classes"]
    w.writerow(header)
    for aid in assumption_ids:
        a = ASSUMPTIONS[aid]
        row = [aid, a["domain"], a["statement"]]
        n = 0
        for cid in class_ids:
            if aid in CLASS_ASSUMPTIONS[cid]["requires"]:
                row.append("REQUIRES")
                n += 1
            elif aid in CLASS_ASSUMPTIONS[cid]["rejects"]:
                row.append("REJECTS")
            else:
                row.append("neutral")
        row.append(str(n))
        w.writerow(row)

print("Wrote t061_shared_assumption_matrix.csv")

# ============================================================
# DELIVERABLE 3: Dependency Graph
# ============================================================
# Two kinds of relationships:
#   1. "requires" — one assumption logically presupposes another
#   2. "contradicts" — one assumption's truth implies another's falsehood
#   3. "co_occurs" — frequently present together in classes

# Define logical dependency relationships between assumptions
DEPENDENCIES = [
    # Structural dependencies
    ("SR2", "SR1", "requires"),      # examining methods requires examining outputs
    ("SR3", "SR1", "requires"),      # detecting recurrence requires examining outputs
    ("IS3", "IS1", "requires"),      # trajectory representation requires identifiable states
    ("IS3", "IS2", "requires"),      # trajectory requires comparable outputs
    ("EC2", "EC1", "requires"),      # knowing limits requires knowing state
    ("EC3", "EC1", "requires"),      # distinguishing explanations requires knowing state
    ("EC4", "EC3", "requires"),      # communicating requires ability to distinguish
    ("MC2", "MC1", "requires"),      # method constrains requires multiple methods exist
    ("MC3", "MC1", "requires"),      # changing methods requires multiple methods exist
    ("IC3", "IC1", "requires"),      # processing changes info requires info exists
    ("IC2", "IC1", "requires"),      # finite info requires info exists
    ("CD3", "CD1", "requires"),      # preferring explanations requires causal structure
    ("CT2", "OC3", "requires"),      # external reference requires inside/outside boundary
    
    # Contradictions
    ("OC3", "OC4", "contradicts"),   # if inside/outside exists with target inside, target may not have independent properties
    ("MC1", "CT1", "contradicts_weak"),  # if multiple methods exist, which one determines stopping?
    
    # Co-occurrence (assumptions that share explanatory burden)
    ("SR1", "IS2", "co_occurs"),     # examining outputs and having determinate outputs
    ("OC1", "IC1", "co_occurs"),     # structure and extractable information
    ("CD1", "CD2", "co_occurs"),     # causal existence and procedural effects
    ("MC2", "MC3", "co_occurs"),     # constraint and mutability of method
]

# Add co-occurrence edges for assumptions that are frequently required together
co_occurrence_pairs = [
    ("SR1", "SR2"), ("SR1", "EC1"), ("IS1", "IS2"),
    ("OC1", "OC2"), ("IC1", "CD1"), ("CD1", "CD2"),
    ("EC1", "EC3"), ("MC1", "MC2"), ("MC1", "MC3"),
]

for a, b in co_occurrence_pairs:
    DEPENDENCIES.append((a, b, "co_occurs"))

with open(OUT / "t061_dependency_graph.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["source", "target", "relationship", "description"])
    for src, tgt, rel in DEPENDENCIES:
        desc = {
            "requires": f"{ASSUMPTIONS[src]['statement'][:80]}... → enables → {ASSUMPTIONS[tgt]['statement'][:80]}",
            "contradicts": f"{ASSUMPTIONS[src]['statement'][:80]}... ← cannot both hold with → {ASSUMPTIONS[tgt]['statement'][:80]}",
            "co_occurs": f"{ASSUMPTIONS[src]['statement'][:80]}... ← typically paired with → {ASSUMPTIONS[tgt]['statement'][:80]}",
        }.get(rel, rel)
        w.writerow([src, tgt, rel, desc])

print(f"Wrote t061_dependency_graph.csv ({len(DEPENDENCIES)} edges)")

# ============================================================
# ANALYSIS
# ============================================================

print(f"\n{'='*60}")
print("ASSUMPTION EXTRACTION AUDIT — SUMMARY")
print(f"{'='*60}")

# How many assumptions per class
print(f"\nAssumption count per class:")
for cid in class_ids:
    cd = CLASS_ASSUMPTIONS[cid]
    n_req = len(cd["requires"])
    n_rej = len(cd["rejects"])
    print(f"  {cid} ({cd['name']}): {n_req} required, {n_rej} rejected")

# Shared assumptions
print(f"\nShared assumptions (required by 5+ classes):")
for aid in assumption_ids:
    req_by = [cid for cid in class_ids if aid in CLASS_ASSUMPTIONS[cid]["requires"]]
    if len(req_by) >= 5:
        print(f"  {aid} ({ASSUMPTIONS[aid]['domain']}): {len(req_by)} classes — {', '.join(req_by)}")

# Unique assumptions
print(f"\nUnique or near-unique assumptions (1-2 classes):")
for aid in assumption_ids:
    req_by = [cid for cid in class_ids if aid in CLASS_ASSUMPTIONS[cid]["requires"]]
    if 0 < len(req_by) <= 2:
        print(f"  {aid}: {', '.join(req_by)} — {ASSUMPTIONS[aid]['statement'][:100]}")

# Classes with fewest assumptions
fewest = min(class_ids, key=lambda cid: len(CLASS_ASSUMPTIONS[cid]["requires"]))
most = max(class_ids, key=lambda cid: len(CLASS_ASSUMPTIONS[cid]["requires"]))
print(f"\nFewest assumptions: {fewest} ({CLASS_ASSUMPTIONS[fewest]['name']}) — {len(CLASS_ASSUMPTIONS[fewest]['requires'])} required")
print(f"Most assumptions:  {most} ({CLASS_ASSUMPTIONS[most]['name']}) — {len(CLASS_ASSUMPTIONS[most]['requires'])} required")

# Fundamental assumptions
fundamental = [aid for aid, a in ASSUMPTIONS.items() if a["is_fundamental"]]
print(f"\nFundamental assumptions (substrate candidates):")
for aid in fundamental:
    a = ASSUMPTIONS[aid]
    req_by = [cid for cid in class_ids if aid in CLASS_ASSUMPTIONS[cid]["requires"]]
    print(f"  {aid}: {a['statement']}")
    print(f"         Required by: {', '.join(req_by)}")

# Check: do all classes share a common core?
common_core = [aid for aid in assumption_ids
               if all(aid in CLASS_ASSUMPTIONS[cid]["requires"] for cid in class_ids)]
print(f"\nCommon core (required by ALL 8 classes):")
if common_core:
    for aid in common_core:
        print(f"  {aid}: {ASSUMPTIONS[aid]['statement']}")
else:
    print("  None — no single assumption is required by all 8 classes.")

# Almost-common core (6+)
near_core = [aid for aid in assumption_ids
             if len([cid for cid in class_ids if aid in CLASS_ASSUMPTIONS[cid]["requires"]]) >= 6]
print(f"\nNear-common core (required by 6+ classes):")
for aid in near_core:
    req_by = [cid for cid in class_ids if aid in CLASS_ASSUMPTIONS[cid]["requires"]]
    print(f"  {aid}: required by {', '.join(req_by)}")
    print(f"       {ASSUMPTIONS[aid]['statement']}")

print(f"\nT061 complete. No classes ranked. No classes eliminated. Only preconditions extracted.")
