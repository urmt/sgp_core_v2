#!/usr/bin/env python3
"""
T062: Assumption Dependency Audit (v2 — corrected)
===================================================
Analyze dependency structure among the 9 shared substrate assumptions from T061.
Find generating subsets, dependency cycles, and strongly connected components.
"""

import csv
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

# ============================================================
# BUILD DEPENDENCY GRAPH
# ============================================================
# Edge A → B means "A presupposes B" (A depends on B)
# adj[A] = list of assumptions A directly depends on

def build_edges():
    """
    Returns dict: edges[a] = [b1, b2, ...] where A → B means A presupposes B.
    """
    edges = {a: [] for a in SIDS}

    # SR1: Self-examination presupposes outputs to examine and a process
    edges["SR1"].extend(["IS2", "IS1"])

    # IS1: Phase structure presupposes outputs (phase boundaries) + distinguishability
    edges["IS1"].extend(["IS2", "OC2"])

    # IS2: Determinate outputs presuppose information + structure + process
    edges["IS2"].extend(["IC1", "OC1", "IS1"])

    # OC1: Stable structure presupposes distinguishability
    edges["OC1"].append("OC2")

    # OC2: Distinguishability — root, presupposes nothing

    # EC1: Self-knowledge presupposes examination + outputs + process
    edges["EC1"].extend(["SR1", "IS2", "IS1"])

    # IC1: Extractable information presupposes structure + distinguishability + process
    edges["IC1"].extend(["OC1", "OC2", "IS1"])

    # CD1: Causal relations presuppose structure + distinguishability
    edges["CD1"].extend(["OC1", "OC2"])

    # CD2: Self-affecting procedures presuppose causality + process + self-knowledge
    edges["CD2"].extend(["CD1", "IS1", "EC1"])

    return edges

EDGES = build_edges()

# ============================================================
# DERIVED RELATIONS
# ============================================================

def transitive_deps(start, edges):
    """All assumptions reachable by following → edges from start (i.e., what start depends on)."""
    visited = set()
    stack = [start]
    while stack:
        node = stack.pop()
        for nxt in edges.get(node, []):
            if nxt not in visited:
                visited.add(nxt)
                stack.append(nxt)
    return visited

def reverse_edges(edges):
    """Return reversed graph: edges_rev[B] = [A1, A2, ...] where A → B."""
    rev = {a: [] for a in edges}
    for a, deps in edges.items():
        for b in deps:
            rev[b].append(a)
    return rev

REV = reverse_edges(EDGES)

def find_generating_sets(edges, sids):
    """
    Find minimal subsets of S that generate all S via the dependency graph.
    "Generates" means: if we assume the generating set, every other assumption
    would have its prerequisites satisfied.
    
    A generates B if B directly or transitively presupposes A.
    
    This is equivalent to: the generating set intersects every dependency path
    from non-generators to roots.
    """
    trans = {a: transitive_deps(a, edges) for a in sids}
    
    # All minimal hitting sets: find smallest subsets that cover all S
    # A set G generates S if for every a in S, trans[a] ∩ G ≠ ∅
    # (every assumption has at least one presupposition satisfied by G)
    # PLUS G itself must be internally satisfied
    
    # For minimal sets of size 1
    for a in sids:
        # Check if all other nodes depend (directly or transitively) on a
        all_depend = True
        for b in sids:
            if b != a and a not in trans[b]:
                all_depend = False
                break
        if all_depend:
            return [{a}]
    
    # For size 2+
    for size in range(2, len(sids)):
        results = []
        for combo in combinations(sids, size):
            gset = set(combo)
            # Check: every node either IS in gset or depends on at least one member
            ok = True
            for b in sids:
                if b not in gset:
                    if not (trans[b] & gset):
                        ok = False
                        break
            if ok:
                # Check minimality
                minimal = True
                for removed in gset:
                    smaller = gset - {removed}
                    still_ok = True
                    for b in sids:
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
    
    return [set(sids)]

# ============================================================
# CYCLE DETECTION (Tarjan's algorithm for SCCs)
# ============================================================

def tarjan_scc(edges):
    """Find strongly connected components using Tarjan's algorithm."""
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
    """Find all elementary cycles (up to length 6) using Johnson's algorithm logic."""
    adj = {a: sorted(edges[a]) for a in sids}
    cycles = set()

    def dfs(start, current, path, visited, blocked):
        blocked.add(current)
        path.append(current)
        for nxt in adj.get(current, []):
            if nxt == start and len(path) >= 2:
                cyc = tuple(path + [start])
                # Rotate to canonical form
                min_idx = cyc.index(min(cyc))
                canonical = cyc[min_idx:] + cyc[:min_idx]
                cycles.add(canonical)
            elif nxt not in blocked and nxt not in path:
                # Only continue if nxt >= start (to avoid duplicate cycles)
                if nxt >= start:
                    dfs(start, nxt, path[:], visited, blocked)
        path.pop()
        if any(nxt for nxt in adj.get(current, []) if nxt not in blocked):
            pass  # unblock handled implicitly
        blocked.discard(current)

    for start in sids:
        dfs(start, start, [], set(), set())

    # Filter: only keep minimal cycles (remove those where a node appears twice is artifact)
    filtered = set()
    for cyc in sorted(cycles, key=len):
        # Only accept cycles where all nodes are distinct except start/end
        if len(cyc) >= 3 and len(set(cyc)) == len(cyc) - 1:
            filtered.add(cyc)
    return sorted(filtered, key=lambda x: (len(x), x))

# ============================================================
# DELIVERABLE A: Dependency Matrix
# ============================================================

def relation(a, b, edges):
    """Determine relation from A to B: presupposes, supports, independent, or mutual."""
    if b in edges.get(a, []):
        if a in edges.get(b, []):
            return "mutual"
        return "presupposes"
    if a in edges.get(b, []):
        if b in edges.get(a, []):
            return "mutual"
        return "presupposed_by"
    return "independent_of"

matrix = {a: {b: relation(a, b, EDGES) for b in SIDS} for a in SIDS}

with open(OUT / "t062_assumption_dependency_matrix.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["source → target"] + SIDS)
    for a in SIDS:
        row = [f"{a}: {SUBSTRATE[a]['label']}"]
        for b in SIDS:
            row.append(matrix[a][b])
        w.writerow(row)

print("Wrote t062_assumption_dependency_matrix.csv")

# ============================================================
# DELIVERABLE B: Minimal Substrate Candidates
# ============================================================

gen_sets = find_generating_sets(EDGES, SIDS)

# Show roots
roots = sorted([a for a in SIDS if not EDGES[a]])
leaves = sorted([a for a in SIDS if not REV[a]])

print(f"\nRoots (depend on nothing): {roots}")
print(f"Leaves (nothing depends on them): {leaves}")

# For each generating set, compute what it generates
trans = {a: transitive_deps(a, EDGES) for a in SIDS}

with open(OUT / "t062_minimal_substrate_candidates.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["candidate_set_id", "n_generators", "generator_ids", "generator_names",
                 "n_generated", "generated_ids", "generated_names"])
    
    if not gen_sets[0]:
        w.writerow(["NONE", 0, "", "", 0, "", ""])
    
    for i, gset in enumerate(gen_sets):
        gen_ids = sorted(gset)
        gen_names = [f"{a}: {SUBSTRATE[a]['label']}" for a in gen_ids]
        
        # Assumptions that transitively depend on at least one generator
        generated = set()
        for b in SIDS:
            if b not in gset and (trans[b] & gset):
                generated.add(b)
        gened_ids = sorted(generated)
        gened_names = [f"{a}: {SUBSTRATE[a]['label']}" for a in gened_ids]
        
        # Also add info about what other assumptions the generators presuppose
        # (So even the generators might depend on each other)
        internal_deps = set()
        for a in gset:
            internal_deps |= trans[a] & gset - {a}
        
        w.writerow([
            f"MS{i+1}", len(gen_ids),
            ";".join(gen_ids), "; ".join(gen_names),
            len(gened_ids), ";".join(gened_ids), "; ".join(gened_names),
        ])
    
    # Add roots as a candidate (if they generate everything)
    roots_generated = set()
    for b in SIDS:
        if b not in roots and (trans[b] & set(roots)):
            roots_generated.add(b)
    w.writerow([
        "ROOTS", len(roots),
        ";".join(roots), "; ".join(f"{a}: {SUBSTRATE[a]['label']}" for a in roots),
        len(roots_generated), ";".join(sorted(roots_generated)),
        "; ".join(f"{a}: {SUBSTRATE[a]['label']}" for a in sorted(roots_generated))
    ])

print(f"Wrote t062_minimal_substrate_candidates.csv ({len(gen_sets)} minimal sets)")
print(f"  Minimal generating set size: {len(gen_sets[0]) if gen_sets else 'N/A'}")
for i, gs in enumerate(gen_sets):
    print(f"  MS{i+1}: {', '.join(sorted(gs))}")

# ============================================================
# DELIVERABLE C: Cycle Report
# ============================================================

sccs = tarjan_scc(EDGES)
cycles = find_simple_cycles(EDGES, SIDS)

# Separate singleton and non-singleton SCCs
nontrivial_sccs = [s for s in sccs if len(s) > 1]
singleton_sccs = [s for s in sccs if len(s) == 1]

# Build condensation DAG
condensation_node_map = {}
condensation_edges = {}
for scc in sccs:
    rep = min(scc)
    for node in scc:
        condensation_node_map[node] = rep
for scc in sccs:
    rep = min(scc)
    condensation_edges[rep] = set()
    for node in scc:
        for nxt in EDGES.get(node, []):
            if condensation_node_map[nxt] != rep:
                condensation_edges[rep].add(condensation_node_map[nxt])

print(f"\nCycle report:")
print(f"  Non-trivial SCCs (size > 1): {len(nontrivial_sccs)}")
for scc in nontrivial_sccs:
    names = [f"{a} ({SUBSTRATE[a]['label']})" for a in sorted(scc)]
    print(f"    SCC: {', '.join(names)}")

print(f"  Simple cycles found: {len(cycles)}")
for cyc in cycles:
    names = [f"{a} ({SUBSTRATE[a]['label']})" for a in cyc]
    print(f"    Cycle: {' → '.join(names)}")

# Condensation depth
def longest_path_len(node, memo=None):
    if memo is None:
        memo = {}
    if node in memo:
        return memo[node]
    max_len = 0
    for nxt in condensation_edges.get(node, []):
        max_len = max(max_len, 1 + longest_path_len(nxt, memo))
    memo[node] = max_len
    return max_len

root_cond = [r for r in roots]
if root_cond:
    depth = max(longest_path_len(condensation_node_map[r]) for r in root_cond)
    print(f"  Condensation DAG depth (from roots): {depth}")

with open(OUT / "t062_cycle_report.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["section", "detail"])
    
    w.writerow(["NONTRIVIAL_SCCs", f"{len(nontrivial_sccs)} found"])
    for scc in nontrivial_sccs:
        names = [f"{a} ({SUBSTRATE[a]['label']})" for a in sorted(scc)]
        w.writerow(["SCC", "; ".join(names)])
    
    w.writerow([])
    w.writerow(["SIMPLE_CYCLES", f"{len(cycles)} found"])
    for cyc in cycles:
        names = [f"{a} ({SUBSTRATE[a]['label']})" for a in cyc]
        w.writerow(["CYCLE", " → ".join(names)])
    
    w.writerow([])
    w.writerow(["CONDENSATION", f"{len(sccs)} SCCs → {len(condensation_edges)} DAG nodes"])
    w.writerow(["CONDENSATION_DEPTH", str(depth) if root_cond else "N/A"])
    
    w.writerow([])
    w.writerow(["STRUCTURAL_SUMMARY", ""])
    w.writerow(["total_assumptions", str(len(SIDS))])
    w.writerow(["roots", ";".join(roots)])
    w.writerow(["leaves", ";".join(leaves)])
    w.writerow(["non_trivial_sccs", str(len(nontrivial_sccs))])
    w.writerow(["simple_cycles", str(len(cycles))])
    w.writerow(["min_generating_set_size", str(len(gen_sets[0])) if gen_sets else "N/A"])
    w.writerow(["n_minimal_generating_sets", str(len(gen_sets))])

print(f"\nWrote t062_cycle_report.csv")

# ============================================================
# FINAL SUMMARY
# ============================================================

print(f"\n{'='*60}")
print("ASSUMPTION DEPENDENCY AUDIT — SUMMARY")
print(f"{'='*60}")

print(f"\nDependency graph (A → B means A presupposes B):\n")
for a in SIDS:
    deps = EDGES[a]
    dep_by = REV[a]
    trans_deps = transitive_deps(a, EDGES) - set(deps) - {a}
    print(f"  {a} ({SUBSTRATE[a]['label']})")
    if deps:
        print(f"    → depends on: {', '.join(deps)}")
    if trans_deps:
        print(f"    → transitively: {', '.join(sorted(trans_deps))}")
    if dep_by:
        print(f"    ← depended on by: {', '.join(dep_by)}")
    print()

print(f"\nRoots: {', '.join(roots)}")
print(f"Leaves: {', '.join(leaves)}")

print(f"\nCondensation DAG ({len(sccs)} SCCs → {len(condensation_edges)} DAG nodes):")
# Print condensation in topological order
topo_order = []
visited = set()
def topo_dfs(node):
    if node in visited:
        return
    visited.add(node)
    for nxt in condensation_edges.get(node, []):
        topo_dfs(nxt)
    topo_order.append(node)
for n in sorted(condensation_edges.keys()):
    topo_dfs(n)
# Add isolated nodes
for n in condensation_node_map.values():
    if n not in topo_order:
        topo_order.append(n)

for node in reversed(topo_order):
    scc_members = [a for a in SIDS if condensation_node_map[a] == node]
    label = ", ".join(f"{a}" for a in sorted(scc_members))
    if len(scc_members) > 1:
        label = f"[{label}] (SCC)"
    children = sorted(condensation_edges.get(node, []))
    if children:
        child_labels = []
        for c in children:
            cm = [a for a in SIDS if condensation_node_map[a] == c]
            child_labels.append(", ".join(sorted(c)))
        print(f"    {label} → {', '.join(child_labels)}")
    else:
        print(f"    {label} (leaf)")

print(f"\nCompression evaluation:")
print(f"  T058: 70 candidates")
print(f"  T059:  8 mechanism classes")
print(f"  T061:  9 shared substrate assumptions")
print(f"  T062:  {len(roots)} root(s): {', '.join(roots)}")
print(f"         {len(gen_sets[0]) if gen_sets else 0}-assumption minimal generating sets exist")
print(f"         {len(nontrivial_sccs)} non-trivial SCC(s) in the substrate itself")

print(f"\nT062 complete. No truth tested. No elimination. Only dependency structure.")
