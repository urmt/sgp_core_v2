#!/usr/bin/env python3
"""
T065: Edge Legitimacy Audit
=============================
For every dependency edge in the substrate model, determine whether
the dependency is a genuine logical presupposition or an over-assertion.
"""

import csv
from pathlib import Path

OUT = Path("/home/student/sgp_core_v2/sfh_sgp_ood_outputs")

# Full edge inventory with analysis

EDGES = [
    # ============================================================
    # CRITICAL EDGES (bootstrap deadlock)
    # ============================================================
    {
        "edge_id": "E01",
        "source": "IS1",
        "target": "IS2",
        "source_label": "Phase structure",
        "target_label": "Determinate outputs",
        "statement": "Phase structure logically presupposes determinate outputs.",
        "can_formulate_without": (
            "Yes. A process can have identifiable stages (temporal ordering, "
            "state transitions) without any stage producing a determinate, "
            "comparable 'output.' Stages can be distinguished by time, by "
            "change in focus, by exhaustion of a question — none of which "
            "require an output."
        ),
        "counterargument": (
            "A 'stage' that produces nothing is not really a stage — it is a "
            "pause. The concept of phase structure implies transitions, and "
            "transitions require something to have happened, which is minimally "
            "an output."
        ),
        "verdict": "OVER-ASSERTED",
        "verdict_reason": (
            "The dependency conflates 'something happens' (which IS1 minimally "
            "requires) with 'something determinate results' (which is IS2). "
            "A phase can be defined by its question, its temporal window, or "
            "its object of focus without requiring a measurable output. "
            "IS1 depends on OC2 (distinguishability enables stage distinction) "
            "but not on IS2."
        ),
        "proposed_correction": "Remove IS1 → IS2. IS1 depends only on OC2.",
        "effect_of_removal": "Bootstraps the cycle. 9/9 assumptions satisfied. Deadlock resolved.",
        "dependency_type": "over_asserted",
    },
    {
        "edge_id": "E02",
        "source": "IS2",
        "target": "IS1",
        "source_label": "Determinate outputs",
        "target_label": "Phase structure",
        "statement": "Determinate outputs logically presuppose phase structure.",
        "can_formulate_without": (
            "Yes. An investigation can produce a single result without "
            "having identifiable phases. A one-shot measurement yields "
            "a determinate output from an undifferentiated process."
        ),
        "counterargument": (
            "An 'output' implies a process that outputs. A process with no "
            "identifiable structure is indistinguishable from no process at "
            "all. IS2 minimally requires that investigation is a process, "
            "which IS1 provides."
        ),
        "verdict": "OVER-ASSERTED",
        "verdict_reason": (
            "IS2 requires that an investigation exists (an agent that produces "
            "outputs), but it does not require that the investigation has "
            "identifiable stages. The assumption 'investigation exists' is "
            "currently not in the substrate — this edge is a proxy for that "
            "missing assumption. IS2 depends on OC1 (structure enables "
            "comparability) and OC2 (distinguishability enables outputs about "
            "the phenomenon), but not on IS1's staged nature."
        ),
        "proposed_correction": "Remove IS2 → IS1. IS2 depends only on IC1, OC1.",
        "effect_of_removal": "Bootstraps the cycle if combined with E01 removal. Alone: IS1 still depends on IS2.",
        "dependency_type": "over_asserted",
    },
    {
        "edge_id": "E03",
        "source": "IC1",
        "target": "IS1",
        "source_label": "Extractable information",
        "target_label": "Phase structure",
        "statement": "Extractable information logically presupposes phase structure.",
        "can_formulate_without": (
            "Yes. Information can exist and be extractable without the "
            "investigation having phases. The phenomenon radiates information "
            "independently of how many stages the investigation uses to capture it."
        ),
        "counterargument": (
            "Information extraction is itself a process. Any extraction "
            "involves at least one stage (access → capture). Therefore IC1 "
            "presupposes IS1 at a minimal level."
        ),
        "verdict": "OVER-ASSERTED",
        "verdict_reason": (
            "Information is a property of the phenomenon-investigation "
            "relationship, not of the investigation's internal structure. "
            "IC1 depends on OC1 (the phenomenon has structure to inform about) "
            "and OC2 (distinguishability enables information transfer). "
            "It does not depend on how many phases the investigation uses."
        ),
        "proposed_correction": "Remove IC1 → IS1. IC1 depends only on OC1, OC2.",
        "effect_of_removal": "Does not alone bootstrap the cycle. IS1 ↔ IS2 deadlock remains.",
        "dependency_type": "over_asserted",
    },
    # ============================================================
    # SELF-REFERENCE EDGES
    # ============================================================
    {
        "edge_id": "E04",
        "source": "SR1",
        "target": "IS2",
        "source_label": "Self-examination of outputs",
        "target_label": "Determinate outputs",
        "statement": "Self-examination logically presupposes determinate outputs to examine.",
        "can_formulate_without": (
            "No. Self-examination of outputs requires that outputs exist. "
            "Without IS2, there is nothing to examine."
        ),
        "counterargument": (
            "One could examine the process itself rather than its outputs. "
            "Self-examination of state (EC1) does not require outputs."
        ),
        "verdict": "LEGITIMATE",
        "verdict_reason": (
            "SR1 is specifically about examining OUTPUTS. The concept "
            "of examining outputs cannot be formulated without the concept "
            "of outputs. This is a genuine logical presupposition."
        ),
        "proposed_correction": "None — edge is correct.",
        "effect_of_removal": "SR1 would have no object to examine.",
        "dependency_type": "legitimate",
    },
    {
        "edge_id": "E05",
        "source": "SR1",
        "target": "IS1",
        "source_label": "Self-examination of outputs",
        "target_label": "Phase structure",
        "statement": "Self-examination logically presupposes a process with identifiable phases.",
        "can_formulate_without": (
            "No. Examining outputs is an act that must occur at a particular "
            "point in the investigation. The concept of 'examining at a "
            "particular time' presupposes temporal structure."
        ),
        "counterargument": (
            "The examination could be simultaneous with output production, "
            "requiring no temporal structure."
        ),
        "verdict": "LEGITIMATE",
        "verdict_reason": (
            "Self-examination is a second-order operation that requires "
            "a distinction between the examination act and what it examines. "
            "This distinction implies at least a minimal phase structure "
            "(first produce, then examine). Edge is correct."
        ),
        "proposed_correction": "None — edge is correct.",
        "effect_of_removal": "SR1 would have no temporal context for examination.",
        "dependency_type": "legitimate",
    },
    # ============================================================
    # EPISTEMIC EDGES
    # ============================================================
    {
        "edge_id": "E06",
        "source": "EC1",
        "target": "SR1",
        "source_label": "Self-knowledge",
        "target_label": "Self-examination of outputs",
        "statement": "Self-knowledge logically presupposes self-examination.",
        "can_formulate_without": (
            "No. Knowing about something requires examining it. "
            "Self-knowledge about outputs requires examining those outputs."
        ),
        "counterargument": (
            "Knowledge could be direct/intuitive rather than examination-based. "
            "One could 'just know' the investigation's state."
        ),
        "verdict": "LEGITIMATE",
        "verdict_reason": (
            "In the investigative context, knowledge is acquired through "
            "examination. EC1 without SR1 would be an unjustified claim of "
            "direct access. Edge is correct."
        ),
        "proposed_correction": "None — edge is correct.",
        "effect_of_removal": "EC1 would lack a mechanism for acquiring self-knowledge.",
        "dependency_type": "legitimate",
    },
    {
        "edge_id": "E07",
        "source": "EC1",
        "target": "IS2",
        "source_label": "Self-knowledge",
        "target_label": "Determinate outputs",
        "statement": "Self-knowledge logically presupposes determinate outputs.",
        "can_formulate_without": (
            "No. Knowledge of the investigation's state requires knowledge "
            "of what the investigation has produced. Without outputs, there "
            "is no state to know."
        ),
        "counterargument": (
            "The investigation's state could be known through introspection "
            "of its process rather than examination of its products."
        ),
        "verdict": "LEGITIMATE",
        "verdict_reason": (
            "EC1 is specifically knowledge about state AND outputs. "
            "The output component requires IS2. Edge is correct."
        ),
        "proposed_correction": "None — edge is correct.",
        "effect_of_removal": "EC1 would lack content for self-knowledge.",
        "dependency_type": "legitimate",
    },
    {
        "edge_id": "E08",
        "source": "EC1",
        "target": "IS1",
        "source_label": "Self-knowledge",
        "target_label": "Phase structure",
        "statement": "Self-knowledge logically presupposes phase structure.",
        "can_formulate_without": (
            "No. Knowledge of one's state requires the concept of having "
            "states, which is what IS1 provides."
        ),
        "counterargument": "One could have a single state without phases.",
        "verdict": "BORDERLINE",
        "verdict_reason": (
            "EC1 requires the investigation to have states. IS1 provides this. "
            "However, a single-state investigation could satisfy both. "
            "The edge is valid if IS1 is interpreted as 'has states' rather "
            "than 'has multiple phases.' Maintained as legitimate under "
            "current IS1 definition."
        ),
        "proposed_correction": "None — edge is correct under current definitions.",
        "effect_of_removal": "EC1 would lack a grounding for state concepts.",
        "dependency_type": "legitimate",
    },
    # ============================================================
    # INFORMATIONAL EDGE
    # ============================================================
    {
        "edge_id": "E09",
        "source": "IC1",
        "target": "OC1",
        "source_label": "Extractable information",
        "target_label": "Stable structure",
        "statement": "Extractable information logically presupposes stable structure.",
        "can_formulate_without": (
            "No. Information must be about something. Without stable "
            "structure (OC1), there is nothing for information to be about."
        ),
        "counterargument": "Information could be about change itself.",
        "verdict": "LEGITIMATE",
        "verdict_reason": (
            "Even information about change requires something that changes, "
            "requiring stable identity across time — which is a form of "
            "structure. Edge is correct."
        ),
        "proposed_correction": "None — edge is correct.",
        "effect_of_removal": "IC1 would be information about nothing.",
        "dependency_type": "legitimate",
    },
    {
        "edge_id": "E10",
        "source": "IC1",
        "target": "OC2",
        "source_label": "Extractable information",
        "target_label": "Distinguishability",
        "statement": "Extractable information logically presupposes distinguishability.",
        "can_formulate_without": (
            "No. Information requires a distinction between signal and "
            "background, which is a form of distinguishability."
        ),
        "counterargument": "Information could be about an undifferentiated whole.",
        "verdict": "LEGITIMATE",
        "verdict_reason": (
            "Information requires at least one distinction (this vs that, "
            "signal vs noise). Without OC2, distinguishability is absent. "
            "Edge is correct."
        ),
        "proposed_correction": "None — edge is correct.",
        "effect_of_removal": "IC1 would have no basis for distinguishing signal.",
        "dependency_type": "legitimate",
    },
    # ============================================================
    # CAUSAL EDGES
    # ============================================================
    {
        "edge_id": "E11",
        "source": "CD1",
        "target": "OC1",
        "source_label": "Causal relations exist",
        "target_label": "Stable structure",
        "statement": "Causal relations logically presuppose stable structure.",
        "can_formulate_without": (
            "No. Causality requires relata with stable identity. Without "
            "OC1, there are no stable entities to serve as causes and effects."
        ),
        "counterargument": "Causality could be pure process without stable entities.",
        "verdict": "LEGITIMATE",
        "verdict_reason": (
            "Causal relata require at least momentary stability to participate "
            "in causal relations. OC1 provides this. Edge is correct."
        ),
        "proposed_correction": "None — edge is correct.",
        "effect_of_removal": "CD1 would have nothing to causally relate.",
        "dependency_type": "legitimate",
    },
    {
        "edge_id": "E12",
        "source": "CD1",
        "target": "OC2",
        "source_label": "Causal relations exist",
        "target_label": "Distinguishability",
        "statement": "Causal relations logically presuppose distinguishability.",
        "can_formulate_without": (
            "No. Cause and effect must be distinguishable from each other. "
            "Without OC2, causal relata collapse into identity."
        ),
        "counterargument": "Self-causation is a coherent concept.",
        "verdict": "LEGITIMATE",
        "verdict_reason": (
            "Even self-causation requires distinguishing cause-aspect from "
            "effect-aspect of the same entity. The distinction still requires "
            "OC2. Edge is correct."
        ),
        "proposed_correction": "None — edge is correct.",
        "effect_of_removal": "CD1 would collapse cause and effect into one.",
        "dependency_type": "legitimate",
    },
    # ============================================================
    # SELF-EFFECT EDGES
    # ============================================================
    {
        "edge_id": "E13",
        "source": "CD2",
        "target": "CD1",
        "source_label": "Self-affecting procedures",
        "target_label": "Causal relations exist",
        "statement": "Self-effects logically presuppose causality.",
        "can_formulate_without": (
            "No. 'Affecting' is a causal concept. Without CD1, there is "
            "no framework for effects of any kind."
        ),
        "counterargument": "Self-effects could be acausal (magical, instantaneous).",
        "verdict": "LEGITIMATE",
        "verdict_reason": (
            "In the investigative context, 'affecting' implies causal "
            "influence. CD2 without CD1 would be claiming an effect without "
            "causality. Edge is correct."
        ),
        "proposed_correction": "None — edge is correct.",
        "effect_of_removal": "CD2 would lack a causal framework.",
        "dependency_type": "legitimate",
    },
    {
        "edge_id": "E14",
        "source": "CD2",
        "target": "IS1",
        "source_label": "Self-affecting procedures",
        "target_label": "Phase structure",
        "statement": "Self-effects logically presuppose phase structure.",
        "can_formulate_without": (
            "No. An effect on the investigation requires the investigation "
            "to have a state that can be affected. IS1 provides this."
        ),
        "counterargument": "A single-state system could still be affected.",
        "verdict": "LEGITIMATE",
        "verdict_reason": (
            "Like EC1 → IS1, this edge requires the weaker reading of IS1 "
            "('has states') rather than the stronger ('has multiple stages'). "
            "Maintained as legitimate."
        ),
        "proposed_correction": "None — edge is correct under current definitions.",
        "effect_of_removal": "CD2 would have no state to affect.",
        "dependency_type": "legitimate",
    },
    {
        "edge_id": "E15",
        "source": "CD2",
        "target": "EC1",
        "source_label": "Self-affecting procedures",
        "target_label": "Self-knowledge",
        "statement": "Self-effects logically presuppose self-knowledge.",
        "can_formulate_without": (
            "No. An effect must be detectable to be relevant. Detection "
            "requires the investigation to know its state before and after."
        ),
        "counterargument": "Effects could exist without being detected.",
        "verdict": "LEGITIMATE",
        "verdict_reason": (
            "In the investigative context, an undetected self-effect is "
            "operationally irrelevant. CD2 requires EC1 for the effect to "
            "enter the investigation's awareness. Edge is correct."
        ),
        "proposed_correction": "None — edge is correct.",
        "effect_of_removal": "CD2 would have undetectable effects.",
        "dependency_type": "legitimate",
    },
    # ============================================================
    # STRUCTURAL EDGE
    # ============================================================
    {
        "edge_id": "E16",
        "source": "OC1",
        "target": "OC2",
        "source_label": "Stable structure",
        "target_label": "Distinguishability",
        "statement": "Stable structure logically presupposes distinguishability.",
        "can_formulate_without": (
            "No. Structure IS a pattern of distinctions. Without "
            "distinguishability (OC2), there are no differences to "
            "constitute structure."
        ),
        "counterargument": "Structure could be intrinsic monism.",
        "verdict": "LEGITIMATE",
        "verdict_reason": (
            "A structure is defined by its parts and their relations, both "
            "of which require distinguishability. Even a simple location "
            "in a monistic whole requires distinguishing that location from "
            "the rest. Edge is correct."
        ),
        "proposed_correction": "None — edge is correct.",
        "effect_of_removal": "OC1 would be structure without distinctions.",
        "dependency_type": "legitimate",
    },
]

# Validate
edge_ids = set()
for e in EDGES:
    assert e["edge_id"] not in edge_ids, f"Duplicate edge_id: {e['edge_id']}"
    edge_ids.add(e["edge_id"])

assert len(EDGES) == 16, f"Expected 16 edges, got {len(EDGES)}"

# ============================================================
# SUMMARIZE
# ============================================================

over_asserted = [e for e in EDGES if e["dependency_type"] == "over_asserted"]
legitimate = [e for e in EDGES if e["dependency_type"] == "legitimate"]
borderline = [e for e in EDGES if e["dependency_type"] == "borderline"]

print(f"Edge inventory: {len(EDGES)} total")
print(f"  Over-asserted: {len(over_asserted)}")
print(f"  Legitimate:    {len(legitimate)}")
print(f"  Borderline:    {len(borderline)}")

print(f"\nOver-asserted edges:")
for e in over_asserted:
    print(f"  {e['edge_id']}: {e['source']} → {e['target']} ({e['source_label']} → {e['target_label']})")
    print(f"    Verdict: {e['verdict_reason'][:120]}...")
    print(f"    Correction: {e['proposed_correction']}")

print(f"\nLegitimate edges:")
for e in legitimate:
    print(f"  {e['edge_id']}: {e['source']} → {e['target']}")

# ============================================================
# WRITE OUTPUT
# ============================================================

with open(OUT / "t065_edge_legitimacy_audit.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["edge_id", "source", "target", "source_label", "target_label",
                 "statement", "can_formulate_without", "counterargument",
                 "verdict", "verdict_reason", "proposed_correction",
                 "effect_of_removal", "dependency_type"])
    for e in EDGES:
        w.writerow([e["edge_id"], e["source"], e["target"],
                     e["source_label"], e["target_label"],
                     e["statement"], e["can_formulate_without"],
                     e["counterargument"], e["verdict"],
                     e["verdict_reason"], e["proposed_correction"],
                     e["effect_of_removal"], e["dependency_type"]])

print(f"\nWrote t065_edge_legitimacy_audit.csv")

# ============================================================
# BOOTSTRAP DEADLOCK RESOLUTION ANALYSIS
# ============================================================

print(f"\n{'='*60}")
print("BOOTSTRAP DEADLOCK — RESOLUTION PATHWAYS")
print(f"{'='*60}")

print(f"\nPathway A (edge correction — no new assumption):")
print(f"  Remove E01 (IS1 → IS2) and E02 (IS2 → IS1)")
print(f"  Result: 9-substrate model, cycle becomes generative")
print(f"  Required redefinition:")
print(f"    IS1 depends on: OC2 only")
print(f"    IS2 depends on: IC1, OC1 only")
print(f"  All 9 assumptions remain.")
print(f"  IS1-IS2 mutual dependency eliminated as over-assertion.")

print(f"\nPathway B (edge correction + assumption):")
print(f"  Remove E01 (IS1 → IS2) only")
print(f"  Add BA1 (investigative organization exists) as root")
print(f"  Add IS1 → BA1 (IS1 depends on BA1)")
print(f"  Result: 10-assumption model, cycle becomes generative")
print(f"  Required new assumption: 'Investigative processes can exhibit")
print(f"    internal organization prior to outcome determination.'")

print(f"\nPathway C (minimal correction):")
print(f"  Remove E03 (IC1 → IS1) only")
print(f"  Does NOT resolve deadlock — IS1 ↔ IS2 remains.")
print(f"  Required if IC1 → IS1 is independently over-asserted,")
print(f"  but insufficient for bootstrap.")

print(f"\nDirector question: Which hypothesis is better supported?")
print(f"  Edge-correction (Pathway A) is slightly stronger:")
print(f"    - Does not require introducing a new entity")
print(f"    - Corrects two edges shown to be over-asserted")
print(f"    - Preserves the 9-assumption substrate")
print(f"  BUT: the dependency IS1 → IS2 was not arbitrary — it encoded")
print(f"  a genuine intuition that phases and outputs are linked.")
print(f"  The audit cannot definitively choose between A and B;")
print(f"  that choice depends on whether the IS1 → IS2 dependency")
print(f"  is judged as logical (keep, add BA1) or empirical (remove).")

print(f"\nT065 complete.")
