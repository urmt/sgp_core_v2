#!/usr/bin/env python3
"""
T063: Substrate Perturbation Audit (v2 — corrected)
=====================================================
Test robustness of T062 dependency structure by knocking out each
substrate assumption and observing what survives.

Corrected: initial satisfied set = only roots (nodes with no prerequisites).
Collapse propagates through unsatisfied dependency chains.
"""

import csv, copy
from pathlib import Path
from itertools import combinations

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

SIDS = sorted(SUBSTRATE.keys())

BASE_EDGES = {
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

# ============================================================
# CORRECTED DEPENDENCY COMPUTATION
# ============================================================

def compute_survivors(edges, alive_set):
    """Starting from root nodes (no prerequisites), iteratively add
    nodes whose ALL prerequisites are alive and satisfied.
    alive_set: set of nodes that hypothetically exist.
    Returns set of nodes that can be justified."""
    # Initial satisfied = nodes in alive_set that have literally empty prerequisite lists
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

def find_cycles(edges, active_set):
    """Find simple cycles within the active dependency graph."""
    adj = {a: [b for b in edges.get(a, []) if b in active_set] for a in active_set}
    cycles = set()

    def dfs(start, current, path, blocked):
        blocked.add(current)
        path.append(current)
        for nxt in adj.get(current, []):
            if nxt == start and len(path) >= 2:
                cyc = tuple(path + [start])
                min_idx = cyc.index(min(cyc))
                canonical = cyc[min_idx:] + cyc[:min_idx]
                cycles.add(canonical)
            elif nxt not in blocked and nxt not in path and nxt >= start:
                dfs(start, nxt, path[:], blocked)
        path.pop()
        blocked.discard(current)

    for start in sorted(adj.keys()):
        dfs(start, start, [], set())

    filtered = set()
    for cyc in cycles:
        if len(cyc) >= 3 and len(set(cyc)) == len(cyc) - 1:
            filtered.add(cyc)
    return sorted(filtered, key=lambda x: (len(x), x))

def find_roots(edges, active_set):
    return sorted([a for a in active_set if not edges.get(a, [])])

# Base reference
BASE_ALIVE = set(SIDS)
BASE_SAT = compute_survivors(BASE_EDGES, BASE_ALIVE)
BASE_CYCLES = find_cycles(BASE_EDGES, BASE_SAT)
BASE_ROOTS = find_roots(BASE_EDGES, BASE_SAT)

print(f"Base: {len(BASE_SAT)} satisfied, {len(BASE_CYCLES)} cycles, roots={BASE_ROOTS}")
print(f"  Satisfied: {sorted(BASE_SAT)}")

CYCLE_IDS = {}
for i, cyc in enumerate(BASE_CYCLES):
    CYCLE_IDS[cyc] = f"CYC{i+1}"

# ============================================================
# KNOCKOUT: remove each assumption
# ============================================================

knockout_results = []

for removed in SIDS:
    alive = BASE_ALIVE - {removed}
    satisfied = compute_survivors(BASE_EDGES, alive)
    survivors = satisfied - {removed}
    collapsed = BASE_ALIVE - survivors - {removed}
    
    surviving_cycles = find_cycles(BASE_EDGES, survivors)
    destroyed_cycles = [c for c in BASE_CYCLES if c not in surviving_cycles]
    new_roots = find_roots(BASE_EDGES, survivors)

    knockout_results.append({
        "removed": removed,
        "removed_label": SUBSTRATE[removed]["label"],
        "n_survivors": len(survivors),
        "survivors": sorted(survivors),
        "n_collapsed": len(collapsed),
        "collapsed": sorted(collapsed),
        "surviving_cycles": surviving_cycles,
        "destroyed_cycles": destroyed_cycles,
        "new_roots": new_roots,
    })

knockout_results.sort(key=lambda r: -r["n_collapsed"])

TEST_CONFIGS = [
    ("OC2 depends on IC1", {"OC2": ["IC1"]}),
    ("OC2 depends on CD1", {"OC2": ["CD1"]}),
    ("OC2 depends on OC1", {"OC2": ["OC1"]}),
    ("OC2 depends on IS1", {"OC2": ["IS1"]}),
    ("OC2 depends on IC1, OC1", {"OC2": ["IC1", "OC1"]}),
]

# ============================================================
# DELIVERABLE A: Knockout Table
# ============================================================

with open(OUT / "t063_knockout_table.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["removed_assumption", "removed_label", "n_survivors",
                 "survivors", "n_collapsed", "collapsed", "notes"])
    for r in knockout_results:
        notes_parts = []
        if not r["survivors"]:
            notes_parts.append("Complete collapse — nothing justifies")
        elif len(r["survivors"]) == 1:
            notes_parts.append(f"Only root survives")
        if r["destroyed_cycles"]:
            notes_parts.append(f"All cycles destroyed")
        w.writerow([r["removed"], r["removed_label"], r["n_survivors"],
                     ";".join(r["survivors"]), r["n_collapsed"],
                     ";".join(r["collapsed"]), "; ".join(notes_parts)])

print("\nWrote t063_knockout_table.csv")

# ============================================================
# DELIVERABLE B: Cycle Resilience
# ============================================================

with open(OUT / "t063_cycle_resilience.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cycle_id", "cycle_members", "survives_without", "destroyed_by"])
    for cyc, cid in CYCLE_IDS.items():
        cyc_set = set(cyc)
        survives_without = []
        destroyed_by = []
        for r in knockout_results:
            if cyc_set.issubset(set(r["survivors"])):
                survives_without.append(r["removed"])
            else:
                destroyed_by.append(r["removed"])
        w.writerow([cid, ";".join(cyc),
                     ";".join(survives_without) if survives_without else "none",
                     ";".join(destroyed_by) if destroyed_by else "none"])

print("Wrote t063_cycle_resilience.csv")

# ============================================================
# DELIVERABLE C: Root Stability
# ============================================================

with open(OUT / "t063_root_stability.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["perturbation", "removed", "new_roots", "oc2_is_root",
                 "oc2_survives", "notes"])
    for r in knockout_results:
        oc2_surv = "OC2" in r["survivors"]
        oc2_root = "OC2" in r["new_roots"]
        notes_parts = []
        if not r["new_roots"]:
            notes_parts.append("No roots — nothing survives")
        elif len(r["new_roots"]) == 1 and r["new_roots"][0] == "OC2":
            notes_parts.append("OC2 remains unique root")
        elif "OC2" not in r["new_roots"]:
            others = ", ".join(r["new_roots"])
            notes_parts.append(f"OC2 is NOT root — alternative: {others}")
        w.writerow([f"Remove {r['removed']}", r["removed"],
                     ";".join(r["new_roots"]) if r["new_roots"] else "none",
                     str(oc2_root), str(oc2_surv), "; ".join(notes_parts)])
    
    # Model perturbation tests (Critical Issue 2)
    w.writerow([])
    w.writerow(["MODEL_PERTURBATION_TESTS", "", "", "", "", ""])

    for label, override in TEST_CONFIGS:
        alt_edges = copy.deepcopy(BASE_EDGES)
        for k, v in override.items():
            alt_edges[k] = v
        alt_alive = compute_survivors(alt_edges, BASE_ALIVE)
        alt_roots = find_roots(alt_edges, alt_alive)
        alt_cycles = find_cycles(alt_edges, alt_alive)
        output = (f"Roots: {alt_roots}, Satisfied: {len(alt_alive)}/{len(SIDS)}, "
                  f"Cycles: {len(alt_cycles)}")
        w.writerow([label, "none", ";".join(alt_roots), str("OC2" in alt_roots),
                     str("OC2" in alt_alive), output])

print("Wrote t063_root_stability.csv")

# ============================================================
# PRINT SUMMARY
# ============================================================

print(f"\n{'='*60}")
print("SUBSTRATE PERTURBATION AUDIT — CORRECTED RESULTS")
print(f"{'='*60}")

print(f"\nKnockout impact ranking (most → least destructive):")
for r in knockout_results:
    bar = "#" * r["n_collapsed"]
    print(f"  Remove {r['removed']} ({r['removed_label']}): "
          f"{r['n_survivors']} survive, {r['n_collapsed']} collapse {bar}")
    print(f"    Survivors: {', '.join(r['survivors'])}")
    print(f"    Roots: {', '.join(r['new_roots'])}")

print(f"\nCycle resilience:")
for cyc, cid in CYCLE_IDS.items():
    cyc_str = " → ".join(cyc)
    print(f"  {cid}: {cyc_str}")
    for r in knockout_results:
        if set(cyc).issubset(set(r["survivors"])):
            print(f"    Survives without: {r['removed']}")
        else:
            print(f"    Destroyed by:    {r['removed']}")
            break

print(f"\nRoot stability:")
print(f"  OC2 is root in {sum(1 for r in knockout_results if 'OC2' in r['new_roots'])}/{len(knockout_results)} knockouts")
print(f"  OC2 survives in {sum(1 for r in knockout_results if 'OC2' in r['survivors'])}/{len(knockout_results)} knockouts")

print(f"\nModel perturbation tests:")
for t_label, t_overrides in TEST_CONFIGS:
    alt_edges = copy.deepcopy(BASE_EDGES)
    for k, v in t_overrides.items():
        alt_edges[k] = v
    alt_alive = compute_survivors(alt_edges, BASE_ALIVE)
    alt_roots = find_roots(alt_edges, alt_alive)
    alt_cycles = find_cycles(alt_edges, alt_alive)
    print(f"  {t_label}:")
    print(f"    Satisfied: {sorted(alt_alive)}")
    print(f"    Roots: {alt_roots}")
    print(f"    Cycles: {len(alt_cycles)}")

print(f"\nT063 complete.")
