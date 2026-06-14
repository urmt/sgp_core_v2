#!/usr/bin/env python3
"""
T067: Dependency Sufficiency Audit
===================================
For every edge in the corrected substrate (T066), evaluate whether the
parent assumption provides ENOUGH conceptual content to justify the child.

Sufficiency ≠ Legitimacy (T065). A dependency can be legitimate but
insufficient — meaning the parent is necessary but not adequate alone.
This identifies edges that may be functioning as "hidden compressions"
of multiple assumptions that should be unpacked.

Focus edges (per Director): OC2→IS1, OC1→CD1, IC1→IS2, IS2→SR1,
SR1→EC1, EC1→CD2 — plus all other edges for completeness.
"""

import csv
from pathlib import Path

OUT = Path("/home/student/sgp_core_v2/sfh_sgp_ood_outputs")

SUBSTRATE = {
    "SR1": {"label": "Self-examination of outputs",
            "statement": "The investigation can examine its own outputs as objects of analysis.",
            "domain": "self_reference"},
    "IS1": {"label": "Phase structure",
            "statement": "The investigation is a process with identifiable stages, phases, or states.",
            "domain": "investigation_structure"},
    "IS2": {"label": "Determinate outputs",
            "statement": "The investigation produces determinate results — outputs that can be compared across phases.",
            "domain": "investigation_structure"},
    "OC1": {"label": "Stable structure",
            "statement": "The phenomenon under study has some stable structure — it is not pure randomness or noise.",
            "domain": "ontological"},
    "OC2": {"label": "Distinguishability",
            "statement": "The phenomenon and the investigation of it are distinguishable (even if inseparable in practice).",
            "domain": "ontological"},
    "EC1": {"label": "Self-knowledge",
            "statement": "The investigation can have knowledge about its own state and outputs.",
            "domain": "epistemic"},
    "IC1": {"label": "Extractable information",
            "statement": "There is information about the phenomenon that the investigation can extract and process.",
            "domain": "informational"},
    "CD1": {"label": "Causal relations exist",
            "statement": "Causal, dependency, or explanatory relationships exist between elements of the phenomenon.",
            "domain": "causal"},
    "CD2": {"label": "Self-affecting procedures",
            "statement": "The investigation's procedures produce effects on the investigation itself or its object.",
            "domain": "causal"},
}

# Corrected edges from T066 (A → B means A depends on B)
CORRECTED_EDGES = {
    "SR1": ["IS2", "IS1"],
    "IS1": ["OC2"],
    "IS2": ["IC1", "OC1", "IS1"],
    "OC1": ["OC2"],
    "OC2": [],
    "EC1": ["SR1", "IS2", "IS1"],
    "IC1": ["OC1", "OC2", "IS1"],
    "CD1": ["OC1", "OC2"],
    "CD2": ["CD1", "IS1", "EC1"],
}

# ============================================================
# Building the full edge inventory
# ============================================================

def all_edges(edges_dict):
    """Return list of (child, parent) tuples."""
    result = []
    for child, parents in edges_dict.items():
        for parent in parents:
            result.append((child, parent))
    return result

EDGE_LIST = all_edges(CORRECTED_EDGES)

# ============================================================
# SUFFICIENCY EVALUATION
# ============================================================
# For each edge (child → parent), answer:
#   1. What does the child minimally require?
#   2. What does the parent provide?
#   3. Is the parent's provision sufficient for the child's requirement?
#   4. If not, what hidden assumption is being compressed?
#   5. Should BA1 or another assumption replace/extend this edge?

def evaluate_edge(child, parent):
    """Returns a dict with sufficiency analysis for one edge."""
    
    # ---- IS1 → OC2 ----
    if child == "IS1" and parent == "OC2":
        return {
            "edge": "IS1 → OC2",
            "child": "Phase structure (IS1)",
            "parent": "Distinguishability (OC2)",
            "child_requires": "The investigation has identifiable stages, phases, or states — internal temporal or structural organization.",
            "parent_provides": "A boundary between investigation and phenomenon, enabling them to be treated as distinct entities.",
            "legitimate": True,
            "sufficient": False,
            "sufficiency_verdict": "INSUFFICIENT",
            "reason": (
                "OC2 supplies external demarcation (this vs that) but not internal architecture "
                "(stage A then stage B). A boundary separates two things; it does not organize "
                "either side internally. IS1 requires the latter. The leap from 'distinguishable "
                "from the phenomenon' to 'has stages' smuggles in a hidden assumption about "
                "temporal extension or internal differentiation of the investigation itself."
            ),
            "hidden_compression": (
                "OC2 → IS1 compresses: (a) distinguishability + (b) the investigation is a "
                "temporally extended process with internal differentiation. The second component "
                "is not derivable from the first."
            ),
            "candidate_correction": (
                "Either: (1) Accept IS1 as a separate root (alongside OC2), or "
                "(2) Add BA1: 'The investigation exists as an internally structured, "
                "temporally extended process' between OC2 and IS1. BA1 would depend on OC2, "
                "IS1 would depend on BA1."
            ),
            "ba1_relevance": "HIGH — this is the exact gap BA1 would fill.",
        }
    
    # ---- OC1 → OC2 ----
    if child == "OC1" and parent == "OC2":
        return {
            "edge": "OC1 → OC2",
            "child": "Stable structure (OC1)",
            "parent": "Distinguishability (OC2)",
            "child_requires": "The phenomenon has non-random structure — elements, relations, or patterns.",
            "parent_provides": "The ability to distinguish elements from each other and from background.",
            "legitimate": True,
            "sufficient": True,
            "sufficiency_verdict": "SUFFICIENT",
            "reason": (
                "Structure IS a pattern of distinctions. Without distinguishability (OC2), "
                "there are no differences to constitute structure. With distinguishability, "
                "at least minimal structure (this ≠ that) is entailed. OC2 provides the "
                "precondition for all structure without requiring additional assumptions."
            ),
            "hidden_compression": "None — this is a direct conceptual dependency.",
            "candidate_correction": "None needed.",
            "ba1_relevance": "NONE",
        }
    
    # ---- IC1 → OC1 ----
    if child == "IC1" and parent == "OC1":
        return {
            "edge": "IC1 → OC1",
            "child": "Extractable information (IC1)",
            "parent": "Stable structure (OC1)",
            "child_requires": "There is information about the phenomenon that can be extracted.",
            "parent_provides": "The phenomenon has structure — something stable to inform about.",
            "legitimate": True,
            "sufficient": True,
            "sufficiency_verdict": "SUFFICIENT",
            "reason": (
                "Information must be about something. OC1 provides the 'something' — "
                "a structured phenomenon that can bear information. Without OC1, information "
                "would be about nothing (which is incoherent). The mapping from 'structured "
                "phenomenon' to 'potential information carrier' is direct."
            ),
            "hidden_compression": "None — legitimate direct dependency.",
            "candidate_correction": "None needed.",
            "ba1_relevance": "NONE",
        }
    
    # ---- IC1 → OC2 ----
    if child == "IC1" and parent == "OC2":
        return {
            "edge": "IC1 → OC2",
            "child": "Extractable information (IC1)",
            "parent": "Distinguishability (OC2)",
            "child_requires": "Signal distinguishable from noise; this distinguishable from that.",
            "parent_provides": "The capacity to distinguish entities and states.",
            "legitimate": True,
            "sufficient": True,
            "sufficiency_verdict": "SUFFICIENT",
            "reason": (
                "Information requires at least one distinction (signal vs background, "
                "this vs that). OC2 provides the general capacity for distinction. "
                "Without OC2, information would have no basis for differentiating content. "
                "This is a clean one-to-one mapping."
            ),
            "hidden_compression": "None — legitimate direct dependency.",
            "candidate_correction": "None needed.",
            "ba1_relevance": "NONE",
        }
    
    # ---- IC1 → IS1 ----
    if child == "IC1" and parent == "IS1":
        return {
            "edge": "IC1 → IS1",
            "child": "Extractable information (IC1)",
            "parent": "Phase structure (IS1)",
            "child_requires": "Information extraction occurs through a process with stages.",
            "parent_provides": "The investigation has identifiable phases or states.",
            "legitimate": True,
            "sufficient": True,
            "sufficiency_verdict": "SUFFICIENT",
            "reason": (
                "Information extraction IS a process: it involves access, capture, "
                "and interpretation. IS1 provides the concept of a structured process "
                "with stages. The dependency is direct: extraction requires temporal "
                "or procedural structure, which IS1 supplies."
            ),
            "hidden_compression": "None — direct dependency under weaker IS1 reading.",
            "candidate_correction": "None needed.",
            "ba1_relevance": "NONE",
        }
    
    # ---- CD1 → OC1 ----
    if child == "CD1" and parent == "OC1":
        return {
            "edge": "CD1 → OC1",
            "child": "Causal relations exist (CD1)",
            "parent": "Stable structure (OC1)",
            "child_requires": "Relata with stable identity that can serve as causes and effects.",
            "parent_provides": "The phenomenon has stable entities and relations.",
            "legitimate": True,
            "sufficient": True,
            "sufficiency_verdict": "SUFFICIENT",
            "reason": (
                "Causal relata require at least momentary stability to participate in "
                "causal relations. OC1 provides the framework of stable elements. "
                "The mapping is direct: structure → entities → causal relata."
            ),
            "hidden_compression": "None — direct dependency.",
            "candidate_correction": "None needed.",
            "ba1_relevance": "NONE",
        }
    
    # ---- CD1 → OC2 ----
    if child == "CD1" and parent == "OC2":
        return {
            "edge": "CD1 → OC2",
            "child": "Causal relations exist (CD1)",
            "parent": "Distinguishability (OC2)",
            "child_requires": "Cause distinguishable from effect; relata distinguishable from each other.",
            "parent_provides": "The general capacity to distinguish entities.",
            "legitimate": True,
            "sufficient": True,
            "sufficiency_verdict": "SUFFICIENT",
            "reason": (
                "Without distinguishability, cause and effect collapse into identity. "
                "OC2 provides the precondition for any relation between distinct relata. "
                "Direct mapping."
            ),
            "hidden_compression": "None — direct dependency.",
            "candidate_correction": "None needed.",
            "ba1_relevance": "NONE",
        }
    
    # ---- IS2 → IC1 ----
    if child == "IS2" and parent == "IC1":
        return {
            "edge": "IS2 → IC1",
            "child": "Determinate outputs (IS2)",
            "parent": "Extractable information (IC1)",
            "child_requires": "Content to output — something determinate that the investigation produces.",
            "parent_provides": "Information about the phenomenon that can form the content of outputs.",
            "legitimate": True,
            "sufficient": True,
            "sufficiency_verdict": "SUFFICIENT",
            "reason": (
                "An output must have content. IC1 provides the content — extractable "
                "information about the phenomenon. Without IC1, outputs would be "
                "empty formal gestures. The mapping from 'information exists' to "
                "'outputs have content' is direct."
            ),
            "hidden_compression": "None — direct dependency.",
            "candidate_correction": "None needed.",
            "ba1_relevance": "NONE",
        }
    
    # ---- IS2 → OC1 ----
    if child == "IS2" and parent == "OC1":
        return {
            "edge": "IS2 → OC1",
            "child": "Determinate outputs (IS2)",
            "parent": "Stable structure (OC1)",
            "child_requires": "Something stable for outputs to be about and to enable cross-phase comparison.",
            "parent_provides": "Stable structure of the phenomenon that outputs can refer to.",
            "legitimate": True,
            "sufficient": True,
            "sufficiency_verdict": "SUFFICIENT",
            "reason": (
                "Determinate outputs require a stable referent. Without OC1, outputs "
                "would be about a moving target, undermining their determinacy. "
                "OC1 provides the stable structure that makes output comparison meaningful."
            ),
            "hidden_compression": "None — direct dependency.",
            "candidate_correction": "None needed.",
            "ba1_relevance": "NONE",
        }
    
    # ---- IS2 → IS1 ----
    if child == "IS2" and parent == "IS1":
        return {
            "edge": "IS2 → IS1",
            "child": "Determinate outputs (IS2)",
            "parent": "Phase structure (IS1)",
            "child_requires": "A process that produces outputs; temporal context for production.",
            "parent_provides": "The investigation as a temporally structured process with identifiable stages.",
            "legitimate": True,
            "sufficient": True,
            "sufficiency_verdict": "SUFFICIENT",
            "reason": (
                "Outputs must be produced by something. IS1 provides the producing "
                "entity — the investigation as a structured process. Without IS1, "
                "outputs would have no producer. This is the remaining direction of "
                "the former mutual dependency and it works cleanly as a one-way edge."
            ),
            "hidden_compression": "None — direct dependency.",
            "candidate_correction": "None needed.",
            "ba1_relevance": "NONE",
        }
    
    # ---- SR1 → IS2 ----
    if child == "SR1" and parent == "IS2":
        return {
            "edge": "SR1 → IS2",
            "child": "Self-examination of outputs (SR1)",
            "parent": "Determinate outputs (IS2)",
            "child_requires": "Outputs to examine — something that exists to be studied.",
            "parent_provides": "Determinate outputs produced by the investigation.",
            "legitimate": True,
            "sufficient": True,
            "sufficiency_verdict": "SUFFICIENT",
            "reason": (
                "Self-examination of outputs is incoherent without outputs to examine. "
                "IS2 supplies them. The mapping is definitional: SR1's object IS IS2. "
                "This is one of the cleanest dependencies in the substrate."
            ),
            "hidden_compression": "None — definitional dependency.",
            "candidate_correction": "None needed.",
            "ba1_relevance": "NONE",
        }
    
    # ---- SR1 → IS1 ----
    if child == "SR1" and parent == "IS1":
        return {
            "edge": "SR1 → IS1",
            "child": "Self-examination of outputs (SR1)",
            "parent": "Phase structure (IS1)",
            "child_requires": "Temporal context — examination must occur after production, at a distinguishable time.",
            "parent_provides": "The investigation as a process with temporal structure (stages).",
            "legitimate": True,
            "sufficient": True,
            "sufficiency_verdict": "SUFFICIENT",
            "reason": (
                "Self-examination is a second-order operation: it requires temporal "
                "separation from first-order production. IS1 provides exactly this — "
                "the concept of distinguishable stages. Without IS1, examination and "
                "production would be simultaneous, collapsing the self-exam distinction."
            ),
            "hidden_compression": "None — direct temporal dependency.",
            "candidate_correction": "None needed.",
            "ba1_relevance": "NONE",
        }
    
    # ---- EC1 → SR1 ----
    if child == "EC1" and parent == "SR1":
        return {
            "edge": "EC1 → SR1",
            "child": "Self-knowledge (EC1)",
            "parent": "Self-examination of outputs (SR1)",
            "child_requires": "A mechanism for acquiring knowledge about the investigation's state and outputs.",
            "parent_provides": "The act of examining the investigation's own outputs.",
            "legitimate": True,
            "sufficient": True,
            "sufficiency_verdict": "SUFFICIENT",
            "reason": (
                "Self-knowledge requires a method. SR1 provides the method — examining "
                "one's own outputs. Without SR1, EC1 would be claiming knowledge without "
                "specifying how it is acquired. The mapping from 'examination' to "
                "'knowledge via examination' is direct."
            ),
            "hidden_compression": "None — direct epistemic dependency.",
            "candidate_correction": "None needed.",
            "ba1_relevance": "NONE",
        }
    
    # ---- EC1 → IS2 ----
    if child == "EC1" and parent == "IS2":
        return {
            "edge": "EC1 → IS2",
            "child": "Self-knowledge (EC1)",
            "parent": "Determinate outputs (IS2)",
            "child_requires": "Content for self-knowledge — something to know about.",
            "parent_provides": "Determinate outputs as objects of self-knowledge.",
            "legitimate": True,
            "sufficient": True,
            "sufficiency_verdict": "SUFFICIENT",
            "reason": (
                "Self-knowledge requires content (state + outputs). IS2 supplies the "
                "output component. Without it, self-knowledge would only have state "
                "information, which is incomplete per EC1's definition."
            ),
            "hidden_compression": "None — direct content dependency.",
            "candidate_correction": "None needed.",
            "ba1_relevance": "NONE",
        }
    
    # ---- EC1 → IS1 ----
    if child == "EC1" and parent == "IS1":
        return {
            "edge": "EC1 → IS1",
            "child": "Self-knowledge (EC1)",
            "parent": "Phase structure (IS1)",
            "child_requires": "The investigation has states that can be known.",
            "parent_provides": "The investigation as having identifiable states or phases.",
            "legitimate": True,
            "sufficient": True,
            "sufficiency_verdict": "SUFFICIENT",
            "reason": (
                "Self-knowledge requires that the investigation HAS states (to know them). "
                "IS1 provides the concept of the investigation having states. The weaker "
                "reading of IS1 ('has states', not 'has multiple stages') suffices here. "
                "This edge was flagged as BORDERLINE in T065 but is sufficient under the "
                "weaker reading maintained by the corrected substrate."
            ),
            "hidden_compression": "None — direct under weaker reading.",
            "candidate_correction": "None needed — depends on consistent IS1 interpretation.",
            "ba1_relevance": "LOW — if IS1 reading is too strong, a state-concept assumption could substitute.",
        }
    
    # ---- CD2 → CD1 ----
    if child == "CD2" and parent == "CD1":
        return {
            "edge": "CD2 → CD1",
            "child": "Self-affecting procedures (CD2)",
            "parent": "Causal relations exist (CD1)",
            "child_requires": "A framework for effects — something that makes 'affecting' coherent.",
            "parent_provides": "Causal relations as the mechanism by which effects occur.",
            "legitimate": True,
            "sufficient": True,
            "sufficiency_verdict": "SUFFICIENT",
            "reason": (
                "'Affecting' IS a causal concept. Self-affecting requires causality to be "
                "coherent. CD1 provides causality. Without CD1, CD2 would be magic. "
                "Direct mapping."
            ),
            "hidden_compression": "None — direct causal dependency.",
            "candidate_correction": "None needed.",
            "ba1_relevance": "NONE",
        }
    
    # ---- CD2 → IS1 ----
    if child == "CD2" and parent == "IS1":
        return {
            "edge": "CD2 → IS1",
            "child": "Self-affecting procedures (CD2)",
            "parent": "Phase structure (IS1)",
            "child_requires": "A state to be affected — something that can receive the effect.",
            "parent_provides": "The investigation as having states that can be affected.",
            "legitimate": True,
            "sufficient": True,
            "sufficiency_verdict": "SUFFICIENT",
            "reason": (
                "An effect on the investigation requires the investigation to have a "
                "state that changes. IS1 provides the concept of investigative states. "
                "Like EC1→IS1, this works under the weaker reading."
            ),
            "hidden_compression": "None — direct under weaker reading.",
            "candidate_correction": "None needed.",
            "ba1_relevance": "NONE",
        }
    
    # ---- CD2 → EC1 ----
    if child == "CD2" and parent == "EC1":
        return {
            "edge": "CD2 → EC1",
            "child": "Self-affecting procedures (CD2)",
            "parent": "Self-knowledge (EC1)",
            "child_requires": "Detection of the effect — awareness that a self-effect has occurred.",
            "parent_provides": "Knowledge of the investigation's state, enabling before/after comparison.",
            "legitimate": True,
            "sufficient": True,
            "sufficiency_verdict": "SUFFICIENT",
            "reason": (
                "An undetected self-effect is operationally irrelevant. EC1 supplies "
                "the detection mechanism — the investigation knows its state before and "
                "after the effect, making the effect meaningful. Without EC1, the "
                "effect would occur but be unknowable."
            ),
            "hidden_compression": "None — direct operational dependency.",
            "candidate_correction": "None needed.",
            "ba1_relevance": "NONE",
        }
    
    # Fallback
    return {
        "edge": f"{child} → {parent}",
        "child": SUBSTRATE.get(child, {}).get("label", child),
        "parent": SUBSTRATE.get(parent, {}).get("label", parent),
        "sufficiency_verdict": "UNKNOWN",
        "reason": "Edge not recognized in audit.",
    }


# ============================================================
# RUN ANALYSIS
# ============================================================

print("=" * 72)
print("T067: DEPENDENCY SUFFICIENCY AUDIT")
print("=" * 72)

results = []
for child, parent in EDGE_LIST:
    r = evaluate_edge(child, parent)
    results.append(r)
    
    verdict_symbol = "✓" if r["sufficient"] else "✗"
    print(f"\n{verdict_symbol} {r['edge']}")
    print(f"   Child:  {r['child']}")
    print(f"   Parent: {r['parent']}")
    print(f"   Sufficiency: {r['sufficiency_verdict']}")
    print(f"   Reason: {r['reason'][:150]}...")
    if not r["hidden_compression"].startswith("None"):
        print(f"   HIDDEN COMPRESSION: {r['hidden_compression'][:150]}...")
    if r["ba1_relevance"] != "NONE":
        print(f"   BA1 relevance: {r['ba1_relevance']}")

# ============================================================
# AGGREGATE RESULTS
# ============================================================

n_sufficient = sum(1 for r in results if r["sufficient"])
n_insufficient = sum(1 for r in results if not r["sufficient"])
n_hidden_compression = sum(1 for r in results if not r["hidden_compression"].startswith("None"))
n_ba1_relevant = sum(1 for r in results if r["ba1_relevance"] != "NONE")

print(f"\n{'='*72}")
print("AGGREGATE RESULTS")
print(f"{'='*72}")
print(f"  Total edges evaluated:     {len(results)}")
print(f"  Sufficient:                {n_sufficient}")
print(f"  Insufficient:              {n_insufficient}")
print(f"  Hidden compressions found: {n_hidden_compression}")
print(f"  BA1-relevant edges:        {n_ba1_relevant}")

if n_insufficient > 0:
    print(f"\n  Insufficient edges:")
    for r in results:
        if not r["sufficient"]:
            print(f"    {r['edge']}: {r['sufficiency_verdict']}")
            print(f"      {r['reason']}")

# ============================================================
# FOCUS EDGE ANALYSIS (per Director)
# ============================================================

focus_edges = [
    ("IS1", "OC2"),   # denoted OC2→IS1 in Director's notation
    ("CD1", "OC1"),   # denoted OC1→CD1
    ("IS2", "IC1"),   # denoted IC1→IS2
    ("SR1", "IS2"),   # denoted IS2→SR1
    ("EC1", "SR1"),   # denoted SR1→EC1
    ("CD2", "EC1"),   # denoted EC1→CD2
]

focus_labels = [
    "OC2 → IS1",
    "OC1 → CD1",
    "IC1 → IS2",
    "IS2 → SR1",
    "SR1 → EC1",
    "EC1 → CD2",
]

print(f"\n{'='*72}")
print("FOCUS EDGES (Director-specified)")
print(f"{'='*72}")

all_focus_sufficient = True
for (child, parent), label in zip(focus_edges, focus_labels):
    r = evaluate_edge(child, parent)
    status = "SUFFICIENT" if r["sufficient"] else "INSUFFICIENT"
    if not r["sufficient"]:
        all_focus_sufficient = False
    print(f"\n  {label}: {status}")
    print(f"    {r['reason'][:200]}")
    if not r["hidden_compression"].startswith("None"):
        print(f"    Compression: {r['hidden_compression'][:200]}")

# ============================================================
# BA1 RELEVANCE ASSESSMENT
# ============================================================

print(f"\n{'='*72}")
print("BA1 RELEVANCE ASSESSMENT")
print(f"{'='*72}")

ba1_edges = [r for r in results if r["ba1_relevance"] != "NONE"]
if ba1_edges:
    print(f"\n  BA1 is relevant to {len(ba1_edges)} edge(s):")
    for r in ba1_edges:
        print(f"    {r['edge']} — Relevance: {r['ba1_relevance']}")
        print(f"      {r['candidate_correction'][:200]}")
else:
    print(f"\n  BA1 is not required for any edge in the corrected substrate.")

# Overall BA1 assessment
print(f"\n  Overall BA1 assessment:")
print(f"    Before T066: BA1 was needed to resolve bootstrap deadlock.")
print(f"    After T066:  BA1 is NOT needed for generativity.")
print(f"    After T067:  BA1 is {'needed to address IS1 insuffiency' if not all_focus_sufficient else 'not needed'}.")
if not all_focus_sufficient:
    print(f"    The single insufficient edge (IS1→OC2) is exactly the gap BA1 would fill.")
    print(f"    BA1 re-enters on evidential grounds — not as a bootstrap rescue mechanism,")
    print(f"    but as a dependency-sufficiency correction.")

# ============================================================
# WRITE OUTPUTS
# ============================================================

with open(OUT / "t067_sufficiency_evaluation.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["edge", "child", "parent", "child_requires", "parent_provides",
                 "legitimate", "sufficient", "sufficiency_verdict", "reason",
                 "hidden_compression", "candidate_correction", "ba1_relevance"])
    for r in sorted(results, key=lambda x: (not x["sufficient"], x["edge"])):
        w.writerow([r["edge"], r["child"], r["parent"],
                     r["child_requires"], r["parent_provides"],
                     str(r["legitimate"]), str(r["sufficient"]),
                     r["sufficiency_verdict"], r["reason"],
                     r["hidden_compression"], r["candidate_correction"],
                     r["ba1_relevance"]])

print(f"\nWrote t067_sufficiency_evaluation.csv")

# Summary
with open(OUT / "t067_summary.json", "w") as f:
    import json
    summary = {
        "total_edges": len(results),
        "sufficient": n_sufficient,
        "insufficient": n_insufficient,
        "hidden_compressions": n_hidden_compression,
        "ba1_relevant_edges": n_ba1_relevant,
        "insufficient_edges": [
            {"edge": r["edge"], "reason": r["reason"]}
            for r in results if not r["sufficient"]
        ],
        "ba1_assessment": {
            "needed_for_generativity": False,
            "needed_for_sufficiency": not all_focus_sufficient,
            "gap": "IS1→OC2 is insufficient — OC2 provides boundary but not internal structure",
            "evidence_base": "T066 corrected the bootstrap artifact. T067 reveals a dependency-sufficiency gap at the same location.",
        }
    }
    json.dump(summary, f, indent=2)

print(f"Wrote t067_summary.json")

print(f"\n{'='*72}")
print("T067 complete.")
print(f"{'='*72}")
