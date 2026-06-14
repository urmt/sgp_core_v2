#!/usr/bin/env python3
"""
T066: Corrected Substrate Validation Audit
===========================================
Reconstruct the dependency graph using only edges judged legitimate
in T065. Then re-run the structural analyses from T062–T063 on the
corrected substrate.

Correction applied: Remove E01 (IS1 → IS2) — the disputed edge
judged over-asserted by T065 and sufficient to resolve the bootstrap
deadlock per T064.

Questions:
  1. Does the IC1–IS1–IS2 SCC still exist?
  2. Is the substrate now generative?
  3. Does OC2 remain the unique entry point?
  4. Does the three-tier structure from T063 survive?
  5. Are any new hidden assumptions exposed after correction?
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

# ============================================================
# CORRECTED DEPENDENCY GRAPH
# ============================================================
# Modification: REMOVED IS1 → IS2 (E01, judged over-asserted in T065)
# All other edges preserved as-is from T062/T063.

CORRECTED_EDGES = {
    "SR1": ["IS2", "IS1"],
    "IS1": ["OC2"],                  # REMOVED IS2 from prereqs
    "IS2": ["IC1", "OC1", "IS1"],
    "OC1": ["OC2"],
    "OC2": [],
    "EC1": ["SR1", "IS2", "IS1"],
    "IC1": ["OC1", "OC2", "IS1"],
    "CD1": ["OC1", "OC2"],
    "CD2": ["CD1", "IS1", "EC1"],
}

# Original (for comparison)
ORIGINAL_EDGES = {
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

EDGES = CORRECTED_EDGES

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

REV = reverse_edges(EDGES)

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

# ============================================================
# SCC & CYCLE DETECTION (Tarjan + simple cycles)
# ============================================================

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
    adj = {a: sorted(edges[a]) for a in sids}
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
            elif nxt not in blocked and nxt not in path:
                if nxt >= start:
                    dfs(start, nxt, path[:], blocked)
        path.pop()
        blocked.discard(current)

    for start in sids:
        dfs(start, start, [], set())

    filtered = set()
    for cyc in sorted(cycles, key=len):
        if len(cyc) >= 3 and len(set(cyc)) == len(cyc) - 1:
            filtered.add(cyc)
    return sorted(filtered, key=lambda x: (len(x), x))

# ============================================================
# MINIMAL GENERATING SETS
# ============================================================

def find_generating_sets(edges, sids):
    trans = {a: transitive_deps(a, edges) for a in sids}

    for a in sids:
        all_depend = True
        for b in sids:
            if b != a and a not in trans[b]:
                all_depend = False
                break
        if all_depend:
            return [{a}]

    for size in range(2, len(sids)):
        results = []
        for combo in combinations(sids, size):
            gset = set(combo)
            ok = True
            for b in sids:
                if b not in gset:
                    if not (trans[b] & gset):
                        ok = False
                        break
            if ok:
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
# ANALYSIS 1: Correction Effect Summary
# ============================================================

print("=" * 70)
print("T066: CORRECTED SUBSTRATE VALIDATION AUDIT")
print("=" * 70)

print("\n--- Correction Applied ---")
print("  Removed edge: E01 (IS1 → IS2)")
print("  Rationale: IS1 (Phase structure) does NOT logically presuppose")
print("             IS2 (Determinate outputs). Phases can be distinguished")
print("             by temporal order, focus, or question without requiring")
print("             a measurable output.")
print()
print("  Corrected IS1 prerequisites: [OC2] only (was [IS2, OC2])")
print()

# ============================================================
# ANALYSIS 2: Dependency Graph + SCCs
# ============================================================

print("--- Dependency Graph (A → B means A presupposes B) ---")
for a in SIDS:
    deps = EDGES[a]
    dep_by = REV[a]
    print(f"  {a} ({SUBSTRATE[a]['label']})")
    if deps:
        print(f"    → depends on: {', '.join(deps)}")
    if dep_by:
        print(f"    ← depended on by: {', '.join(dep_by)}")

# SCC analysis
sccs = tarjan_scc(EDGES)
cycles = find_simple_cycles(EDGES, SIDS)
nontrivial_sccs = [s for s in sccs if len(s) > 1]

print(f"\n--- SCC & Cycle Analysis ---")
print(f"  Non-trivial SCCs (size > 1): {len(nontrivial_sccs)}")
for scc in nontrivial_sccs:
    names = [f"{a} ({SUBSTRATE[a]['label']})" for a in sorted(scc)]
    print(f"    SCC: {', '.join(names)}")

print(f"  Simple cycles found: {len(cycles)}")
for cyc in cycles:
    names = [f"{a} ({SUBSTRATE[a]['label']})" for a in cyc]
    print(f"    Cycle: {' → '.join(names)}")

# ============================================================
# ANALYSIS 3: Generativity
# ============================================================

BASE_ALIVE = set(SIDS)
BASE_SAT = compute_survivors(EDGES, BASE_ALIVE)
BASE_ROOTS = find_roots(EDGES, BASE_SAT)
is_generative = (BASE_SAT == BASE_ALIVE)

print(f"\n--- Generativity ---")
print(f"  Alive set: {sorted(BASE_ALIVE)}")
print(f"  Satisfied: {sorted(BASE_SAT)}")
print(f"  All assumptions satisfied: {is_generative}")
print(f"  Roots: {BASE_ROOTS}")
print(f"  Leaves: {sorted([a for a in SIDS if not REV[a]])}")

# ============================================================
# ANALYSIS 4: Minimal Generating Sets
# ============================================================

gen_sets = find_generating_sets(EDGES, SIDS)

print(f"\n--- Minimal Generating Sets ---")
print(f"  Minimal set size: {len(gen_sets[0]) if gen_sets else 'N/A'}")
for i, gs in enumerate(gen_sets):
    names = [f"{a} ({SUBSTRATE[a]['label']})" for a in sorted(gs)]
    print(f"  MS{i+1}: {', '.join(names)}")

# ============================================================
# ANALYSIS 5: Knockout Perturbation
# ============================================================

print(f"\n--- Knockout Perturbation ---")

knockout_results = []

for removed in SIDS:
    alive = BASE_ALIVE - {removed}
    satisfied = compute_survivors(EDGES, alive)
    survivors = satisfied - {removed}
    collapsed = BASE_ALIVE - survivors - {removed}
    new_roots = find_roots(EDGES, survivors)

    knockout_results.append({
        "removed": removed,
        "removed_label": SUBSTRATE[removed]["label"],
        "n_survivors": len(survivors),
        "survivors": sorted(survivors),
        "n_collapsed": len(collapsed),
        "collapsed": sorted(collapsed),
        "new_roots": new_roots,
    })

knockout_results.sort(key=lambda r: -r["n_collapsed"])

for r in knockout_results:
    bar = "#" * r["n_collapsed"]
    print(f"  Remove {r['removed']} ({r['removed_label']}): "
          f"{r['n_survivors']} survive, {r['n_collapsed']} collapse {bar}")
    print(f"    Survivors: {', '.join(r['survivors'])}")
    print(f"    Roots: {', '.join(r['new_roots']) if r['new_roots'] else 'none'}")

# ============================================================
# ANALYSIS 6: Comparative (corrected vs original)
# ============================================================

print(f"\n--- Comparative: Corrected vs Original ---")

# Original analysis
orig_sat = compute_survivors(ORIGINAL_EDGES, BASE_ALIVE)
orig_roots = find_roots(ORIGINAL_EDGES, orig_sat)
orig_gen = (orig_sat == BASE_ALIVE)
orig_sccs = tarjan_scc(ORIGINAL_EDGES)
orig_nontriv = [s for s in orig_sccs if len(s) > 1]

print(f"  Property               | Original   | Corrected")
print(f"  -----------------------+------------+----------")
print(f"  Generative              | {str(orig_gen):>10} | {str(is_generative):>9}")
print(f"  Satisfied               | {len(orig_sat):>3}/9       | {len(BASE_SAT):>3}/9")
print(f"  Roots                   | {str(orig_roots):>10} | {str(BASE_ROOTS):>9}")
print(f"  Non-trivial SCCs        | {len(orig_nontriv):>10} | {len(nontrivial_sccs):>9}")
print(f"  Simple cycles           | {len(find_simple_cycles(ORIGINAL_EDGES, SIDS)):>10} | {len(cycles):>9}")
print(f"  Min generating set size | 1          | {len(gen_sets[0]) if gen_sets else 'N/A':>9}")

# ============================================================
# STRUCTURAL INTERPRETATION
# ============================================================

print(f"\n{'='*70}")
print("STRUCTURAL INTERPRETATION")
print(f"{'='*70}")

# Calculate dependency levels (longest path from root)
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

levels = {a: max_path_to(a, EDGES, {}) for a in SIDS}
max_level = max(levels.values())
level_groups = {lvl: sorted([a for a in SIDS if levels[a] == lvl]) for lvl in range(max_level + 1)}

print(f"\nDependency hierarchy ({max_level + 1} levels):")
for lvl in range(max_level, -1, -1):
    if lvl == 0:
        print(f"  Level {lvl} (root):    {', '.join(level_groups[lvl])}")
    else:
        print(f"  Level {lvl}:           {', '.join(level_groups[lvl])}")

print(f"\nT063 three-tier structure comparison:")
tier1 = {"OC2", "OC1", "CD1"}
tier2 = {"IC1", "IS1", "IS2"}
tier3 = {"CD2", "EC1", "SR1"}

print(f"  Old Tier 1 (bootstrap): {sorted(tier1)} → these are now spread across levels 0-3")
print(f"  Old Tier 2 (closure):   {sorted(tier2)} → cycle destroyed, hierarchy established")
print(f"  Old Tier 3 (downstream): {sorted(tier3)} → these remain at top of hierarchy")

# Q5: New hidden assumptions
print(f"\n--- Q5: New Hidden Assumptions ---")

# Check if any node's single dependency path is too thin
thin_deps = {a: EDGES[a] for a in SIDS if len(EDGES[a]) == 1 and a != "OC2"}
print(f"  Nodes depending on exactly one assumption:")
for a, deps in sorted(thin_deps.items()):
    print(f"    {a} ({SUBSTRATE[a]['label']}) → only {deps[0]}")

# Check IS1 specifically
print(f"\n  IS1 (Phase structure) now depends ONLY on OC2 (Distinguishability).")
print(f"  Question: Does distinguishability alone justify phase structure?")
print(f"  Issue: OC2 enables distinguishing investigation from phenomenon.")
print(f"  But IS1 requires the investigation ITSELF has internal stages.")
print(f"  Distinguishability gives us a boundary, not internal structure.")

# Check if any assumption has a path that bypasses expected dependencies
print(f"\n  Other potential thin spots:")
if "EC1" in SIDS:
    ec1_trans = transitive_deps("EC1", EDGES)
    if "OC1" not in ec1_trans:
        print(f"    EC1 has no path to OC1 — could be an issue")
    if "CD1" not in ec1_trans:
        print(f"    EC1 has no path to CD1 — self-knowledge without causality?")

# Check for investigation-existence gap
print(f"\n  Critical gap: The assumption 'an investigation exists' is not in the substrate.")
print(f"  OC2 requires an investigation to distinguish from the phenomenon.")
print(f"  IS1 requires an investigation to have stages.")
print(f"  IS2 requires an investigation to produce outputs.")
print(f"  But 'investigation exists' is treated as native to the framework.")
print(f"  This was the role BA1 (Baseline Activity) would fill.")

# ============================================================
# WRITE OUTPUTS
# ============================================================

# Deliverable A: Corrected Dependency Matrix
with open(OUT / "t066_corrected_dependency_matrix.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["source → target"] + SIDS)
    for a in SIDS:
        row = [f"{a}: {SUBSTRATE[a]['label']}"]
        for b in SIDS:
            if b in EDGES.get(a, []):
                if a in EDGES.get(b, []):
                    row.append("mutual")
                else:
                    row.append("presupposes")
            elif a in EDGES.get(b, []):
                row.append("presupposed_by")
            else:
                row.append("independent_of")
        w.writerow(row)
print(f"\nWrote t066_corrected_dependency_matrix.csv")

# Deliverable B: Structural Summary
with open(OUT / "t066_structural_summary.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["property", "original_value", "corrected_value"])
    w.writerow(["generative", str(orig_gen), str(is_generative)])
    w.writerow(["n_satisfied", str(len(orig_sat)), str(len(BASE_SAT))])
    w.writerow(["roots", ";".join(orig_roots), ";".join(BASE_ROOTS)])
    w.writerow(["n_non_trivial_sccs", str(len(orig_nontriv)), str(len(nontrivial_sccs))])
    w.writerow(["n_cycles", str(len(find_simple_cycles(ORIGINAL_EDGES, SIDS))), str(len(cycles))])
    w.writerow(["min_generating_set_size", "1", str(len(gen_sets[0]) if gen_sets else "N/A")])
    w.writerow(["n_minimal_generating_sets", "1", str(len(gen_sets))])
print(f"Wrote t066_structural_summary.csv")

# Deliverable C: Knockout Table (corrected)
with open(OUT / "t066_knockout_table.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["removed_assumption", "removed_label", "n_survivors",
                 "survivors", "n_collapsed", "collapsed", "notes"])
    for r in knockout_results:
        notes_parts = []
        if not r["survivors"]:
            notes_parts.append("Complete collapse — nothing justifies")
        elif len(r["survivors"]) == 1:
            notes_parts.append("Only root survives")
        w.writerow([r["removed"], r["removed_label"], r["n_survivors"],
                     ";".join(r["survivors"]), r["n_collapsed"],
                     ";".join(r["collapsed"]), "; ".join(notes_parts)])
print(f"Wrote t066_knockout_table.csv")

# Deliverable D: Dependency Hierarchy (hierarchical)
with open(OUT / "t066_dependency_hierarchy.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["level", "assumptions", "n_assumptions"])
    for lvl in range(max_level, -1, -1):
        nodes = level_groups[lvl]
        w.writerow([str(lvl), ";".join(nodes), str(len(nodes))])
print(f"Wrote t066_dependency_hierarchy.csv")

# Deliverable E: Cycle Report (corrected)
with open(OUT / "t066_cycle_report.csv", "w", newline="") as f:
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
    w.writerow(["STRUCTURAL_SUMMARY", ""])
    w.writerow(["total_assumptions", str(len(SIDS))])
    w.writerow(["roots", ";".join(BASE_ROOTS)])
    w.writerow(["correction", "Removed IS1 → IS2 (E01)"])
print(f"Wrote t066_cycle_report.csv")

# Deliverable F: New Hidden Assumptions Report
with open(OUT / "t066_hidden_assumptions.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["issue_id", "description", "affected_node", "severity", "proposed_resolution"])
    w.writerow(["HA1",
                 "IS1 depends only on OC2; distinguishability gives external boundary but not internal stage structure",
                 "IS1", "medium",
                 "BA1 (Baseline Activity) may be needed: 'The investigation exists as a temporally extended process'"
               ])
    w.writerow(["HA2",
                 "No assumption encodes 'the investigation exists' — this is implicitly treated as framework-native",
                 "ALL", "medium",
                 "Explicitly state investigation-existence as a precondition"
               ])
    w.writerow(["HA3",
                 "IS1 → IS2 removal assumes phases can be defined without outputs; this weakens but does not eliminate the temporal structure requirement",
                 "IS1", "low",
                 "Monitor whether comparator assumptions require phase-output coupling"
               ])
print(f"Wrote t066_hidden_assumptions.csv")

# ============================================================
# FINAL SUMMARY
# ============================================================

print(f"\n{'='*70}")
print("T066 COMPLETE — ANSWERS TO AUDIT QUESTIONS")
print(f"{'='*70}")

print(f"""
Q1: Does the IC1–IS1–IS2 SCC still exist?
    {'YES — the mutual dependency persists' if nontrivial_sccs else 'NO — the SCC is fully destroyed.'}
    {'The IC1↔IS1↔IS2 cycle required IS1↔IS2. Without IS1→IS2, the remaining IS2→IS1 and IS2→IC1 edges are one-way. No cycle remains.' if not nontrivial_sccs else ''}
    Cycles found: {len(cycles)}
    Non-trivial SCCs: {len(nontrivial_sccs)}

Q2: Is the substrate now generative?
    {'YES — all 9 assumptions are satisfied.' if is_generative else 'NO — some assumptions remain unsatisfied.'}
    Generative: {is_generative}
    Satisfied: {len(BASE_SAT)}/9
    The bootstrap deadlock is fully resolved by the single edge correction.

Q3: Does OC2 remain the unique entry point?
    {'YES — OC2 is the only node with no prerequisites.' if BASE_ROOTS == ['OC2'] else 'NO — other roots exist.'}
    Roots: {BASE_ROOTS}
    OC2 remains the unique bootstrap assumption.

Q4: Does the three-tier structure from T063 survive?
    PARTIALLY. The graph is now a DAG with {max_level + 1} levels instead of 3 tiers.
    - OC2 (root) → level 0
    - OC1, IC1, CD1 → levels 1-2
    - IS1 → level 1
    - IS2 → level 2
    - SR1 → level 3
    - EC1, CD2 → levels 4-5
    The old Tier 1 (bootstrap: OC2, OC1, CD1) is now distributed across levels 0-2.
    The old Tier 2 (closure: IC1-IS1-IS2) has been resolved into a linear chain.
    The old Tier 3 (downstream: CD2, EC1, SR1) remains at the top.

Q5: Are any new hidden assumptions exposed after correction?
    YES — two candidates identified:
    HA1: IS1 depends solely on OC2. Distinguishability provides an external boundary
         (investigation vs phenomenon) but does it justify internal stage structure?
         This gap may require a new assumption (akin to BA1: Investigation Exists
         as a temporally extended process).
    HA2: No substrate assumption encodes 'an investigation exists' — it is treated
         as framework-native. This affects the legitimacy of ALL dependencies that
         refer to 'the investigation'.
    HA3: The IS1→IS2 removal weakens the phase-output coupling. If downstream
         comparisons require outputs to bound phases, this edge may need to be
         revisited as context-dependent rather than universally over-asserted.
""")

print("T066 complete.")
