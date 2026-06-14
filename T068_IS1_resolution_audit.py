#!/usr/bin/env python3
"""
T068: IS1 Resolution Audit
===========================
Evaluate three candidate interventions for the OC2 → IS1 sufficiency gap
identified in T067.

Path A — Independent IS1:   IS1 becomes a second root (no new assumptions).
Path B — BA1 Mediation:     Insert BA1 between OC2 and IS1 (10th assumption).
Path C — IS1 Refinement:    Split IS1 into change (IS1a) and stages (IS1b).

For each path, test:
  - Generativity (all assumptions satisfied?)
  - Root structure (unique vs multiple roots)
  - Cycle/SCC presence
  - Knockout resilience (OC2 removal stability)
  - What the path reveals about the nature of the gap
"""

import csv, copy
from pathlib import Path
from itertools import combinations

OUT = Path("/home/student/sgp_core_v2/sfh_sgp_ood_outputs")

# ============================================================
# SUBSTRATE DEFINITIONS
# ============================================================

# T066 corrected substrate — baseline for all comparisons
BASE_SUBSTRATE = {
    "SR1": "Self-examination of outputs",
    "IS1": "Phase structure",
    "IS2": "Determinate outputs",
    "OC1": "Stable structure",
    "OC2": "Distinguishability",
    "EC1": "Self-knowledge",
    "IC1": "Extractable information",
    "CD1": "Causal relations exist",
    "CD2": "Self-affecting procedures",
}

BASE_EDGES = {
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

SIDS_BASE = sorted(BASE_SUBSTRATE.keys())

# ============================================================
# PATH A: Independent IS1
# ============================================================

# IS1 becomes a root — depends on nothing
A_SUBSTRATE = dict(BASE_SUBSTRATE)
A_EDGES = copy.deepcopy(BASE_EDGES)
A_EDGES["IS1"] = []  # remove OC2 dependency
SIDS_A = sorted(A_SUBSTRATE.keys())

# ============================================================
# PATH B: BA1 Mediation
# ============================================================

# BA1: "The investigation exists as an organized activity persisting across states."
# BA1 depends on OC2; IS1 depends on BA1 instead of OC2.
B_SUBSTRATE = dict(BASE_SUBSTRATE)
B_SUBSTRATE["BA1"] = "Baseline investigative activity"
B_EDGES = copy.deepcopy(BASE_EDGES)
B_EDGES["IS1"] = ["BA1"]    # reroute
B_EDGES["BA1"] = ["OC2"]    # BA1 grounded in distinguishability
SIDS_B = sorted(B_SUBSTRATE.keys())

# ============================================================
# PATH C: IS1 Refinement (split)
# ============================================================

# IS1a (Change):  "The investigation undergoes change across its engagement."
#   — depends on OC2 (distinguishability enables change detection)
# IS1b (Stages):  "The investigation has identifiable ordered stages."
#   — depends on IS1a (stages are a refinement of change)
#
# Edge reallocation (which downstream nodes need which version):
#   SR1 → IS1b  (ordered stages required for produce-then-examine)
#   IS2 → IS1a  (process producer)
#   EC1 → IS1a  (states)
#   IC1 → IS1a  (extraction process)
#   CD2 → IS1a  (state to affect)

C_SUBSTRATE = {
    "SR1":  "Self-examination of outputs",
    "IS1a": "Investigative change",
    "IS1b": "Identifiable stages",
    "IS2":  "Determinate outputs",
    "OC1":  "Stable structure",
    "OC2":  "Distinguishability",
    "EC1":  "Self-knowledge",
    "IC1":  "Extractable information",
    "CD1":  "Causal relations exist",
    "CD2":  "Self-affecting procedures",
}
SIDS_C = sorted(C_SUBSTRATE.keys())

C_EDGES = {
    "SR1":  ["IS2", "IS1b"],
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

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

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

def reverse_edges(edges):
    rev = {a: [] for a in edges}
    for a, deps in edges.items():
        for b in deps:
            rev[b].append(a)
    return rev

def transitive_deps(start, edges):
    visited = set()
    stack = [start]
    while stack:
        node = stack.pop()
        for nxt in edges.get(node, []):
            if nxt not in visited:
                visited.add(nxt)
                stack.append(nxt)
    return visited

def find_roots(edges, active_set):
    return sorted([a for a in active_set if not edges.get(a, [])])

def find_leaves(edges, active_set):
    rev = reverse_edges(edges)
    return sorted([a for a in active_set if not rev.get(a, [])])

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

def find_simple_cycles(edges, sids):
    adj = {a: sorted(edges[a]) for a in sids if a in edges}
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
    for cyc in sorted(cycles, key=len):
        if len(cyc) >= 3 and len(set(cyc)) == len(cyc) - 1:
            filtered.add(cyc)
    return sorted(filtered, key=lambda x: (len(x), x))

def max_path_to(node, edges, memo=None):
    if memo is None:
        memo = {}
    if node in memo:
        return memo[node]
    prereqs = edges.get(node, [])
    if not prereqs:
        memo[node] = 0
        return 0
    max_len = 0
    for p in prereqs:
        max_len = max(max_len, 1 + max_path_to(p, edges, memo))
    memo[node] = max_len
    return max_len

def analyze_path(label, substrate, edges, sids):
    """Run full structural analysis on one path."""
    alive = set(sids)
    satisfied = compute_survivors(edges, alive)
    is_gen = (satisfied == alive)
    roots = find_roots(edges, satisfied)
    leaves = find_leaves(edges, satisfied)
    sccs = tarjan_scc(edges)
    nontriv = [s for s in sccs if len(s) > 1]
    cycles = find_simple_cycles(edges, satisfied)
    gen_sets = find_generating_sets(edges, sids, satisfied)
    levels = {a: max_path_to(a, edges, {}) for a in sids}
    n_roots = len(roots)

    # Knockout: remove OC2
    oc2_alive = alive - {"OC2"} if "OC2" in alive else alive - {a for a in alive if "OC2" in a}
    oc2_sat = compute_survivors(edges, oc2_alive)
    oc2_roots = find_roots(edges, oc2_sat)
    oc2_n_survivors = len(oc2_sat)

    return {
        "label": label,
        "n_assumptions": len(sids),
        "generative": is_gen,
        "n_satisfied": len(satisfied),
        "roots": roots,
        "n_roots": n_roots,
        "unique_root": "OC2" if n_roots == 1 and "OC2" in roots else ("OC2+IS1" if sorted(roots) == ["IS1", "OC2"] else str(roots)),
        "leaves": leaves,
        "n_scc": len(nontriv),
        "n_cycles": len(cycles),
        "min_gen_set_size": len(gen_sets[0]) if gen_sets else "N/A",
        "n_gen_sets": len(gen_sets) if gen_sets else 0,
        "max_depth": max(levels.values()) if levels else 0,
        "oc2_knockout_survivors": oc2_n_survivors,
        "oc2_knockout_roots": oc2_roots,
    }

def find_generating_sets(edges, sids, satisfied):
    """Find minimal subsets that generate all satisfied nodes."""
    trans = {a: transitive_deps(a, edges) for a in satisfied}
    for a in satisfied:
        all_depend = True
        for b in satisfied:
            if b != a and a not in trans[b]:
                all_depend = False
                break
        if all_depend:
            return [{a}]
    for size in range(2, len(satisfied)):
        results = []
        for combo in combinations(satisfied, size):
            gset = set(combo)
            ok = True
            for b in satisfied:
                if b not in gset:
                    if not (trans[b] & gset):
                        ok = False
                        break
            if ok:
                minimal = True
                for removed in gset:
                    smaller = gset - {removed}
                    still_ok = True
                    for b in satisfied:
                        if b not in smaller:
                            if not (trans[b] & smaller):
                                still_ok = False
                                break
                    if still_ok:
                        minimal = False
                        break
                if minimal:
                    results.append(gset)
        if results:
            return results
    return [set(satisfied)]

# ============================================================
# RUN ANALYSIS ON ALL PATHS
# ============================================================

paths = [
    ("Baseline (T066 corrected)", BASE_SUBSTRATE, BASE_EDGES, SIDS_BASE),
    ("Path A — Independent IS1", A_SUBSTRATE, A_EDGES, SIDS_A),
    ("Path B — BA1 Mediation", B_SUBSTRATE, B_EDGES, SIDS_B),
    ("Path C — IS1 Refinement", C_SUBSTRATE, C_EDGES, SIDS_C),
]

results = []
for label, sub, edges, sids in paths:
    r = analyze_path(label, sub, edges, sids)
    results.append(r)

# ============================================================
# PRINT RESULTS
# ============================================================

print("=" * 72)
print("T068: IS1 RESOLUTION AUDIT — THREE PATHS COMPARED")
print("=" * 72)

# Table header
print(f"\n{'Property':<30} {'Baseline':<14} {'Path A':<14} {'Path B':<14} {'Path C':<14}")
print("-" * 72)
for prop in ["n_assumptions", "generative", "n_satisfied",
             "unique_root", "n_roots", "leaves",
             "n_scc", "n_cycles", "min_gen_set_size",
             "max_depth", "oc2_knockout_survivors"]:
    vals = []
    for r in results:
        v = r[prop]
        if isinstance(v, bool):
            v = str(v)
        elif isinstance(v, list):
            v = ";".join(v)
        vals.append(str(v)[:13])
    print(f"{prop:<30} {vals[0]:<14} {vals[1]:<14} {vals[2]:<14} {vals[3]:<14}")

# ============================================================
# DETAILED PER-PATH OUTPUT
# ============================================================

for r in results:
    print(f"\n{'='*72}")
    print(f"{r['label']}")
    print(f"{'='*72}")
    print(f"  Generative:    {r['generative']} ({r['n_satisfied']}/{r['n_assumptions']} satisfied)")
    print(f"  Roots:         {r['roots']}")
    print(f"  Leaves:        {r['leaves']}")
    print(f"  SCCs:          {r['n_scc']}")
    print(f"  Cycles:        {r['n_cycles']}")
    print(f"  Min gen set:   size {r['min_gen_set_size']}, {r['n_gen_sets']} set(s)")
    print(f"  Max depth:     {r['max_depth']}")
    print(f"  OC2 knockout:  {r['oc2_knockout_survivors']} survivors, roots: {r['oc2_knockout_roots']}")

# ============================================================
# COMPARATIVE ASSESSMENT
# ============================================================

print(f"\n{'='*72}")
print("COMPARATIVE ASSESSMENT")
print(f"{'='*72}")

print(f"""
What changes across the three paths:
""")

# Path A assessment
surv_a = results[1]["oc2_knockout_survivors"]
print(f"Path A — Independent IS1:")
print(f"  Trade-off: Loses unique root (now OC2 + IS1). But no new assumptions.")
print(f"  Structural change: Minimal — single edge deletion.")
print(f"  OC2 knockout: {'complete' if surv_a == 0 else f'{surv_a} survive'}.")
print(f"  Interpretation: Treats phase structure as primitive — a co-equal")
print(f"    foundation with distinguishability.")
print(f"  Cost: Weakens OC2's unique-root finding from T062/T063/T066.")
print(f"  Benefit: Zero substrate expansion. Does not hide the gap behind a label.")
print()

# Path B assessment
print(f"Path B — BA1 Mediation:")
print(f"  Trade-off: Expands to 10 assumptions. Preserves OC2 as unique root.")
print(f"  BA1 depends on OC2, IS1 depends on BA1.")
print(f"  Structural change: Single edge rerouted through new node.")
print(f"  OC2 knockout: Still complete (BA1 dies, IS1 dies, everything downstream dies).")
print(f"  Interpretation: The gap is a missing intermediate concept.")
print(f"  Risk: BA1 may be parasitic — if BA1 is just 'what IS1 minimally requires',")
print(f"    it adds no information. BA1 must have independent content.")
print(f"  Cost: Expands substrate. BA1's independence must be argued.")
print()

# Path C assessment
print(f"Path C — IS1 Refinement:")
print(f"  Trade-off: Substrate grows to 10 assumptions. Two IS1 variants.")
print(f"  IS1a (Change): depends on OC2 — change as distinguishable difference")
print(f"    in investigative state.")
print(f"  IS1b (Stages): depends on IS1a — ordering is a refinement of change.")
print(f"  Key insight: Only SR1 requires IS1b. All other nodes use IS1a.")
print(f"  This means the sufficiency gap is really about IS1a → IS1b,")
print(f"    not OC2 → IS1. OC2 → IS1a may be sufficient.")
print(f"  Test: If OC2 → IS1a is accepted, then the gap shrinks to:")
print(f"    'Does change (IS1a) imply stages (IS1b)?'")
print(f"  That is a much weaker demand on the substrate.")
print()

# ============================================================
# THE SUFFICIENCY QUESTION REVISITED
# ============================================================

print(f"{'='*72}")
print("SUFFICIENCY RE-EVALUATION (Path C insight)")
print(f"{'='*72}")

print(f"""
Path C reveals that T067's insufficiency finding may be an artifact of
IS1's definitional breadth.

IS1 (Phase structure) bundles two distinct concepts:
  1. The investigation undergoes change (IS1a)
  2. The investigation has identifiable ordered stages (IS1b)

When these are separated:

  OC2 → IS1a:  Does distinguishability imply change?
    Possible argument: If the investigation is distinguishable from the
    phenomenon (OC2), and the investigation engages with the phenomenon,
    then each engagement changes the investigation's relationship to the
    phenomenon. Change is the temporal expression of distinguishability.
    -> MAY BE SUFFICIENT.

  IS1a → IS1b:  Does change imply stages?
    Not automatically. Change can be continuous. Stages require discrete
    boundaries. This IS a genuine gap — but it is a gap within IS1,
    not a gap across the whole substrate.
    -> REQUIRES FURTHER ANALYSIS.

Implication:
  If OC2 → IS1a is accepted as sufficient, then the only remaining gap
  is IS1a → IS1b, which only SR1 depends on. This means the sufficiency
  problem is localized not just to one edge, but to a single downstream
  dependency chain (SR1 → IS1b → IS1a → OC2), not the entire graph.
""")

# ============================================================
# FINAL COMPARISON
# ============================================================

print(f"{'='*72}")
print("HEAD-TO-HEAD COMPARISON")
print(f"{'='*72}")

paths_data = [
    (results[0], "Baseline (reference)"),
    (results[1], "Path A — cheapest structural cost"),
    (results[2], "Path B — preserves OC2 uniqueness"),
    (results[3], "Path C — most explanatory refinement"),
]

print(f"""
Criteria                | Baseline | Path A | Path B | Path C
------------------------+----------+--------+--------+-------
Generative              | {str(results[0]['generative']):>8} | {str(results[1]['generative']):>6} | {str(results[2]['generative']):>6} | {str(results[3]['generative']):>6}
Unique root             | {results[0]['unique_root']:>8} | {results[1]['unique_root']:>6} | {results[2]['unique_root']:>6} | {results[3]['unique_root']:>6}
Cycles                  | {results[0]['n_cycles']:>8} | {results[1]['n_cycles']:>6} | {results[2]['n_cycles']:>6} | {results[3]['n_cycles']:>6}
Assumptions             | {results[0]['n_assumptions']:>8} | {results[1]['n_assumptions']:>6} | {results[2]['n_assumptions']:>6} | {results[3]['n_assumptions']:>6}
New entities            | 0        | 0      | BA1    | IS1a/IS1b
OC2 knockout survivors  | {results[0]['oc2_knockout_survivors']:>8} | {results[1]['oc2_knockout_survivors']:>6} | {results[2]['oc2_knockout_survivors']:>6} | {results[3]['oc2_knockout_survivors']:>6}
""")

print(f"\n{'='*72}")
print("CONCLUSION")
print(f"{'='*72}")

print(f"""
The three paths are structurally equivalent in generativity — all produce
fully satisfied substrate graphs with no cycles.

They differ in:
  1. Root uniqueness (Path A loses it)
  2. Assumption count (B and C add 1)
  3. Explanatory granularity (C provides the most)

No path is eliminable at this stage. Each captures a different
interpretation of the gap:

  Path A: The gap is irreducible — IS1 is just primitive.
  Path B: The gap is bridgeable — BA1 fills it.
  Path C: The gap is within IS1 — the real problem is change→stages,
          not distinguishability→change.

The choice depends on what kind of gap T067 identified, which is a
conceptual question, not a structural one.
""")

print("T068 complete.")

# ============================================================
# WRITE OUTPUTS
# ============================================================

with open(OUT / "t068_path_comparison.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["property", "baseline", "path_A_independent_IS1", "path_B_BA1_mediation", "path_C_IS1_refinement"])
    for prop in ["n_assumptions", "generative", "n_satisfied",
                 "roots", "n_roots", "leaves",
                 "n_scc", "n_cycles", "min_gen_set_size",
                 "n_gen_sets", "max_depth", "oc2_knockout_survivors",
                 "unique_root"]:
        w.writerow([prop] + [str(r[prop]) for r in results])

print(f"Wrote t068_path_comparison.csv")

# Per-path edge list
for label, sub, edges, sids in paths:
    safe = label.lower().replace(" ", "_").replace("—", "").strip()
    with open(OUT / f"t068_{safe}_edges.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["source", "target", "source_label", "target_label"])
        for src in sorted(edges.keys()):
            for tgt in edges[src]:
                sl = sub.get(src, src)
                tl = sub.get(tgt, tgt)
                w.writerow([src, tgt, sl, tl])

print(f"Wrote per-path edge lists to t068_*_edges.csv")
