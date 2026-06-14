#!/usr/bin/env python3
"""
T064: Bootstrap Completion Audit
==================================
Find the smallest additional assumption that makes the IC1-IS1-IS2
cycle generative rather than merely self-referential.
"""

import csv, copy
from pathlib import Path

OUT = Path("/home/student/sgp_core_v2/sfh_sgp_ood_outputs")

SUBSTRATE = {
    "SR1": "The investigation can examine its own outputs as objects of analysis.",
    "IS1": "The investigation is a process with identifiable stages, phases, or states.",
    "IS2": "The investigation produces determinate results — outputs that can be compared across phases.",
    "OC1": "The phenomenon under study has some stable structure — it is not pure randomness or noise.",
    "OC2": "The phenomenon and the investigation of it are distinguishable (even if inseparable in practice).",
    "EC1": "The investigation can have knowledge about its own state and outputs.",
    "IC1": "There is information about the phenomenon that the investigation can extract and process.",
    "CD1": "Causal, dependency, or explanatory relationships exist between elements of the phenomenon.",
    "CD2": "The investigation's procedures produce effects on the investigation itself or its object.",
}

SIDS = sorted(SUBSTRATE.keys())

BASE = {
    "SR1": ["IS2", "IS1"],
    "IS1": ["IS2", "OC2"],
    "IS2": ["IC1", "OC1", "IS1"],
    "OC1": ["OC2"],
    "OC2": [],
    "EC1": ["SR1", "IS2", "IS1"],
    "IC1": ["OC1", "OC2", "IS1"],
    "CD1": ["OC1", "OC2"],
    "CD2": ["CD1", "IS1", "EC1"],
}

CYCLE_NODES = {"IC1", "IS1", "IS2"}
CYCLE = ("IC1", "IS1", "IS2", "IC1")

def compute_survivors(edges, alive_set):
    satisfied = {a for a in alive_set if not edges.get(a, [])}
    changed = True
    while changed:
        changed = False
        for node in alive_set:
            if node not in satisfied:
                reqs = edges.get(node, [])
                if all(r in satisfied for r in reqs):
                    satisfied.add(node)
                    changed = True
    return satisfied

def cycle_is_generative(edges, alive_set):
    """A cycle is generative if all its members are satisfied."""
    sat = compute_survivors(edges, alive_set)
    return CYCLE_NODES.issubset(sat)

def find_single_edge_breaks():
    """Test removing each single edge from the cycle to see if it
    becomes generative."""
    results = []
    for src in list(BASE.keys()) + [None]:
        for tgt in SIDS:
            if src is None:
                continue
            if tgt not in BASE.get(src, []):
                continue
            new_edges = {k: list(v) for k, v in BASE.items()}
            new_edges[src] = [x for x in new_edges[src] if x != tgt]
            generative = cycle_is_generative(new_edges, set(SIDS))
            survivors = compute_survivors(new_edges, set(SIDS))
            results.append({
                "change": f"Remove {src}→{tgt}",
                "generative": generative,
                "survivors": sorted(survivors),
                "n_survivors": len(survivors),
            })
    return results

def find_single_node_additions():
    """Test adding one new root assumption with one new edge
    into a cycle member."""
    results = []
    # CANDIDATE new assumptions (roots)
    candidates = [
        ("INV", "An investigative process exists"),
        ("OUT", "Outputs are directly observable"),
        ("INFO", "Information is directly accessible from the phenomenon"),
        ("PHASE", "Phase transitions are primitive givens"),
        ("ACT", "An investigative act occurs"),
        ("STATE", "State transitions can occur"),
        ("OP", "A distinction can be operationalized"),
    ]

    for nid, nlabel in candidates:
        # Add as root, add one edge from nid to each cycle node
        for cycle_target in CYCLE_NODES:
            new_edges = {k: list(v) for k, v in BASE.items()}
            new_edges[nid] = []
            new_edges[cycle_target] = list(new_edges[cycle_target]) + [nid]
            alive = set(SIDS) | {nid}
            generative = cycle_is_generative(new_edges, alive)
            survivors = compute_survivors(new_edges, alive)
            results.append({
                "assumption": nid,
                "assumption_label": nlabel,
                "edge_to": cycle_target,
                "generative": generative,
                "n_survivors": len(survivors - {nid}),
                "survivors": sorted(survivors - {nid}),
                "note": "",
            })
    return results


def find_node_replacement(modify, old_dep, new_dep):
    """Test replacing one dependency with a new root assumption."""
    new_edges = {k: list(v) for k, v in BASE.items()}
    nid = "NEW"
    new_edges[nid] = []
    deps = list(new_edges[modify])
    if old_dep in deps:
        deps.remove(old_dep)
    deps.append(nid)
    deps.append(old_dep)  # Actually, let me try just REPLACING
    # Reset: just remove old_dep and add nid
    deps = [d for d in new_edges[modify] if d != old_dep] + [nid]
    new_edges[modify] = deps
    alive = set(SIDS) | {nid}
    survivors = compute_survivors(new_edges, alive)
    return {
        "modification": f"Replace {modify}→{old_dep} with {modify}→NEW",
        "generative": CYCLE_NODES.issubset(survivors),
        "n_survivors": len(survivors - {nid}),
        "survivors": sorted(survivors - {nid}),
    }

# ============================================================
# SEARCH
# ============================================================

base_gen = cycle_is_generative(BASE, set(SIDS))
print(f"Base cycle generative: {base_gen}")
print(f"Base survivors: {sorted(compute_survivors(BASE, set(SIDS)))}")

# Strategy 1: Single edge removal
edge_breaks = find_single_edge_breaks()
working_breaks = [r for r in edge_breaks if r["generative"]]

print(f"\n=== Strategy 1: Single edge removal ===")
print(f"Edges that make cycle generative when removed:")
for r in working_breaks:
    print(f"  {r['change']}: {r['n_survivors']} survivors → {', '.join(r['survivors'])}")

# Strategy 2: Single node addition with single edge into cycle
node_adds = find_single_node_additions()
working_adds = [r for r in node_adds if r["generative"]]

print(f"\n=== Strategy 2: Add root + edge into cycle ===")
print(f"Candidates that make cycle generative:")
for r in working_adds:
    print(f"  Add '{r['assumption']}' ({r['assumption_label']}), "
          f"edge to {r['edge_to']}: {r['n_survivors']} survivors")

if not working_adds:
    print("  None — adding dependencies only makes satisfaction harder")
    print("  (AND logic: more prerequisites = harder to satisfy)")
    print("\n  => Additional assumption must REPLACE, not supplement, an edge")

# Strategy 3: Single dependency replacement
print(f"\n=== Strategy 3: Dependency replacement ===")
replacements = []
for modify in CYCLE_NODES:
    for old_dep in BASE[modify]:
        # Find which edge, if replaced by a root, makes the cycle generative
        r = find_node_replacement(modify, old_dep, None)
        replacements.append(r)

for r in replacements:
    print(f"  {r['modification']}: generative={r['generative']}, "
          f"{r['n_survivors']} survivors: {', '.join(r['survivors'])}")

# ============================================================
# DETAILED ANALYSIS
# ============================================================

print(f"\n{'='*60}")
print("BOOTSTRAP COMPLETION — DETAILED FINDINGS")
print(f"{'='*60}")

print(f"\nWhy the cycle fails to boot:")
print(f"  IS1 → IS2, OC2     (needs IS2, then IS2 needs IS1 → deadlock)")
print(f"  IS2 → IC1, OC1, IS1 (needs IC1, then IC1 needs IS1 → deadlock)")
print(f"  IC1 → OC1, OC2, IS1 (needs IS1, then IS1 needs IS2 → deadlock)")
print(f"\n  Mutual dependency IS1 ↔ IS2 is the irreducible block.")
print(f"  IC1 is downstream of IS1 — it cannot be the entry point.")

print(f"\nEdges that break the cycle when removed:")
for r in working_breaks:
    print(f"  Remove {r['change']}")
    print(f"    → {r['n_survivors']} survivors: {', '.join(r['survivors'])}")

print(f"\nBootstrap completion candidates:")
print(f"  If we REPLACE a single cycle-edge with a new root assumption:")
for r in replacements:
    if r["generative"]:
        print(f"  {r['modification']}")
        print(f"    → {r['n_survivors']} survivors: {', '.join(r['survivors'])}")

# Determine which replacement is "smallest"
print(f"\nMinimal candidate analysis:")
gen_replacements = [r for r in replacements if r["generative"]]
if gen_replacements:
    best = max(gen_replacements, key=lambda x: x["n_survivors"])
    print(f"  Most generative: {best['modification']} ({best['n_survivors']} survivors)")
    smallest_assump = best['modification']
    print(f"\n  This corresponds to the assumption:")
    if "IS1→IS2" in best['modification']:
        print(f"    'Phase structure does not require determinate outputs'")
        print(f"    Paraphrase: A process can have identifiable stages")
        print(f"    without yet producing measurable outputs.")
    elif "IS1→OC2" in best['modification']:
        print(f"    'Phase structure is primitive'")
        print(f"    Paraphrase: The investigation's stage-like character")
        print(f"    is a given, not derived from distinguishability.")
    elif "IS2→IS1" in best['modification']:
        print(f"    'Outputs do not require phase structure'")
        print(f"    Paraphrase: An investigation can produce results")
        print(f"    without having predefined phases.")
    elif "IS2→IC1" in best['modification']:
        print(f"    'Outputs are directly observable'")
        print(f"    Paraphrase: The investigation's outputs are givens,")
        print(f"    not derived from extractable information.")
    elif "IS2→OC1" in best['modification']:
        print(f"    'Output comparability is primitive'")
        print(f"    Paraphrase: Results can be compared across phases")
        print(f"    without appealing to underlying stable structure.")
    elif "IC1→IS1" in best['modification']:
        print(f"    'Information does not require phase structure'")
        print(f"    Paraphrase: Information about the phenomenon")
        print(f"    can exist independently of investigative phases.")

# ============================================================
# WRITE OUTPUT
# ============================================================

with open(OUT / "t064_bootstrap_completion.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["analysis_type", "modification", "generative", "n_survivors",
                 "survivors", "interpretation"])

    for r in edge_breaks:
        interp = ""
        if r["generative"]:
            interp = "Fixes cycle by removing mutual dependency"
        w.writerow(["edge_removal", r["change"], str(r["generative"]),
                     r["n_survivors"], ";".join(r["survivors"]), interp])

    for r in node_adds:
        interp = ""
        if r["generative"]:
            interp = "Fixes cycle by providing entry edge"
        w.writerow(["node_addition", f"Add {r['assumption']}→{r['edge_to']}",
                     str(r["generative"]), r["n_survivors"],
                     ";".join(r["survivors"]), interp])

    for r in replacements:
        interp = ""
        if r["generative"]:
            interp = "Fixes cycle by replacing edge with root"
        w.writerow(["dependency_replacement", r["modification"],
                     str(r["generative"]), r["n_survivors"],
                     ";".join(r["survivors"]), interp])

print(f"\nWrote t064_bootstrap_completion.csv")

# ============================================================
# FINAL ANSWER
# ============================================================

print(f"\n{'='*60}")
print("BOOTSTRAP COMPLETION AUDIT — ANSWER")
print(f"{'='*60}")

# Find the single minimal change
best = max(gen_replacements, key=lambda x: x["n_survivors"])
print(f"\nThe cycle becomes generative by replacing ONE edge with a new root.")
print(f"Best result: {best['modification']}")
print(f"  → {best['n_survivors']} of 9 assumptions satisfied")
print(f"  → Survivors: {', '.join(best['survivors'])}")
print(f"\nThe missing assumption is the one that would replace the removed edge.")
print(f"\nIn natural language: the substrate is missing an assumption about the")
print(f"primitive observability of investigative structure — the cycle is closed")
print(f"because every entry point requires something that requires it back.")
print(f"\nT064 complete.")
