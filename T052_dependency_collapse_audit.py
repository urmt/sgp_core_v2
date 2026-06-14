#!/usr/bin/env python3
"""
T052: Dependency Collapse Audit
================================
Audit Category A statements only.
Find minimal surviving core.
Check for hidden imports.
"""

import csv, json
from pathlib import Path

ROOT = Path("/home/student/sgp_core_v2")
OUT = ROOT / "sfh_sgp_ood_outputs"

# ============================================================
# CATEGORY A STATEMENTS (from T051)
# ============================================================

A_STATEMENTS = {
    "A01": {"phase": "T037", "text": "Geometry score = 0.69 across 1200 universes",
             "requires": ["A13"], "supports": [], "independent": True},
    "A02": {"phase": "T037", "text": "Composition score = 0.0 across all universes",
             "requires": ["A13"], "supports": [], "independent": True},
    "A03": {"phase": "T037", "text": "Recurrence detected in 98.3% of universes",
             "requires": ["A13"], "supports": ["A14"], "independent": True},
    "A04": {"phase": "T038", "text": "Distinction emerged in 995/1000 universes",
             "requires": ["A13"], "supports": [], "independent": True},
    "A05": {"phase": "T038", "text": "Persistence emerged in 0/1000 universes",
             "requires": ["A13"], "supports": [], "independent": True},
    "A06": {"phase": "T039", "text": "28 assumptions cataloged",
             "requires": [], "supports": ["A07", "A08"], "independent": True},
    "A07": {"phase": "T039", "text": "34 dependency edges identified",
             "requires": ["A06"], "supports": ["A08"], "independent": False},
    "A08": {"phase": "T039", "text": "12 circular dependency chains found",
             "requires": ["A07"], "supports": [], "independent": False},
    "A09": {"phase": "T040", "text": "10/10 candidate substrates failed",
             "requires": [], "supports": [], "independent": True},
    "A10": {"phase": "T041", "text": "0/5000 universes produce distinction",
             "requires": ["A13"], "supports": [], "independent": True},
    "A11": {"phase": "T041", "text": "Proto-geometry emerges in 85.8%",
             "requires": ["A13"], "supports": [], "independent": True},
    "A12": {"phase": "T042", "text": "Trajectory bundles appear in 64.7%",
             "requires": ["A13"], "supports": [], "independent": True},
    "A13": {"phase": "T043", "text": "101,414 detector events recorded",
             "requires": [], "supports": ["A01","A02","A03","A04","A05","A10","A11","A12","A14","A15"], "independent": True},
    "A14": {"phase": "T043", "text": "Recurrence fires first (98.3%)",
             "requires": ["A13"], "supports": ["A16"], "independent": True},
    "A15": {"phase": "T043", "text": "73 edges in emergence graph (P>0.95)",
             "requires": ["A13"], "supports": [], "independent": True},
    "A16": {"phase": "T044", "text": "Recurrence kills in recursive vs nonrecursive test",
             "requires": ["A14"], "supports": [], "independent": False},
    "A17": {"phase": "T045", "text": "Convergence rate = 0.995",
             "requires": ["A13"], "supports": ["A18","A19"], "independent": True},
    "A18": {"phase": "T045", "text": "Convergence beats all null models (14x)",
             "requires": ["A17"], "supports": [], "independent": False},
    "A19": {"phase": "T045", "text": "Convergence survives temporal shuffling",
             "requires": ["A17"], "supports": [], "independent": False},
    "A20": {"phase": "T046", "text": "Convergence before constraint (7/8 detectors)",
             "requires": ["A17"], "supports": [], "independent": False},
    "A21": {"phase": "T047", "text": "All detectors smuggle hidden primitives",
             "requires": ["A22","A24"], "supports": ["A25"], "independent": False},
    "A22": {"phase": "T048", "text": "45 detectors cataloged",
             "requires": [], "supports": ["A23","A24"], "independent": True},
    "A23": {"phase": "T048", "text": "63 dependency edges identified",
             "requires": ["A22"], "supports": ["A24"], "independent": False},
    "A24": {"phase": "T048", "text": "Every detector imports comparison, arithmetic, distance",
             "requires": ["A23"], "supports": ["A21"], "independent": False},
    "A25": {"phase": "T050", "text": "All 5 primitives proven necessary for observer models",
             "requires": ["A21"], "supports": ["A26"], "independent": False},
    "A26": {"phase": "T050", "text": "No primitive proven necessary for observation itself",
             "requires": ["A25"], "supports": [], "independent": False},
}


# ============================================================
# HIDDEN IMPORT AUDIT
# ============================================================

HIDDEN_IMPORTS = {
    "A01": {"uses_arithmetic": True, "uses_comparison": True, "uses_ordering": False,
            "uses_distinction": True, "uses_identity": False,
            "reason": "Score computation uses norm (arithmetic+comparison), detector uses clustering (distinction)"},
    "A02": {"uses_arithmetic": True, "uses_comparison": True, "uses_ordering": False,
            "uses_distinction": True, "uses_identity": False,
            "reason": "Score = 0 requires arithmetic to compute"},
    "A03": {"uses_arithmetic": True, "uses_comparison": True, "uses_ordering": True,
            "uses_distinction": True, "uses_identity": False,
            "reason": "Recurrence detector uses norm (arithmetic), comparison, and ordering"},
    "A04": {"uses_arithmetic": True, "uses_comparison": True, "uses_ordering": False,
            "uses_distinction": True, "uses_identity": False,
            "reason": "Clustering detector uses distance (arithmetic+comparison)"},
    "A05": {"uses_arithmetic": True, "uses_comparison": True, "uses_ordering": False,
            "uses_distinction": True, "uses_identity": False,
            "reason": "Same detector as A04"},
    "A06": {"uses_arithmetic": False, "uses_comparison": False, "uses_ordering": False,
            "uses_distinction": False, "uses_identity": False,
            "reason": "Pure enumeration. No computation required."},
    "A07": {"uses_arithmetic": False, "uses_comparison": False, "uses_ordering": False,
            "uses_distinction": False, "uses_identity": False,
            "reason": "Graph construction from specification. No computation required."},
    "A08": {"uses_arithmetic": False, "uses_comparison": False, "uses_ordering": False,
            "uses_distinction": False, "uses_identity": False,
            "reason": "Graph analysis. No computation required."},
    "A09": {"uses_arithmetic": False, "uses_comparison": False, "uses_ordering": False,
            "uses_distinction": False, "uses_identity": False,
            "reason": "Direct test results. No computation required."},
    "A10": {"uses_arithmetic": True, "uses_comparison": True, "uses_ordering": False,
            "uses_distinction": True, "uses_identity": False,
            "reason": "Detector uses distance (arithmetic+comparison)"},
    "A11": {"uses_arithmetic": True, "uses_comparison": True, "uses_ordering": False,
            "uses_distinction": True, "uses_identity": False,
            "reason": "Detector uses distance and clustering"},
    "A12": {"uses_arithmetic": True, "uses_comparison": True, "uses_ordering": False,
            "uses_distinction": True, "uses_identity": False,
            "reason": "Detector uses distance and clustering"},
    "A13": {"uses_arithmetic": False, "uses_comparison": False, "uses_ordering": False,
            "uses_distinction": False, "uses_identity": False,
            "reason": "Pure data collection. No computation required."},
    "A14": {"uses_arithmetic": True, "uses_comparison": True, "uses_ordering": True,
            "uses_distinction": True, "uses_identity": False,
            "reason": "Detector uses norm, comparison, ordering"},
    "A15": {"uses_arithmetic": True, "uses_comparison": True, "uses_ordering": False,
            "uses_distinction": True, "uses_identity": False,
            "reason": "Graph construction from pairwise probabilities"},
    "A16": {"uses_arithmetic": True, "uses_comparison": True, "uses_ordering": False,
            "uses_distinction": True, "uses_identity": False,
            "reason": "Test uses effect size (arithmetic), comparison"},
    "A17": {"uses_arithmetic": True, "uses_comparison": True, "uses_ordering": False,
            "uses_distinction": True, "uses_identity": False,
            "reason": "Detector uses norm, comparison"},
    "A18": {"uses_arithmetic": True, "uses_comparison": True, "uses_ordering": False,
            "uses_distinction": True, "uses_identity": False,
            "reason": "Effect size computation uses arithmetic"},
    "A19": {"uses_arithmetic": True, "uses_comparison": True, "uses_ordering": False,
            "uses_distinction": True, "uses_identity": False,
            "reason": "Test uses effect size, comparison"},
    "A20": {"uses_arithmetic": True, "uses_comparison": True, "uses_ordering": False,
            "uses_distinction": True, "uses_identity": False,
            "reason": "Pairwise order uses comparison, arithmetic"},
    "A21": {"uses_arithmetic": False, "uses_comparison": False, "uses_ordering": False,
            "uses_distinction": False, "uses_identity": False,
            "reason": "Audit result. No computation required."},
    "A22": {"uses_arithmetic": False, "uses_comparison": False, "uses_ordering": False,
            "uses_distinction": False, "uses_identity": False,
            "reason": "Pure enumeration. No computation required."},
    "A23": {"uses_arithmetic": False, "uses_comparison": False, "uses_ordering": False,
            "uses_distinction": False, "uses_identity": False,
            "reason": "Graph construction from specification."},
    "A24": {"uses_arithmetic": False, "uses_comparison": False, "uses_ordering": False,
            "uses_distinction": False, "uses_identity": False,
            "reason": "Audit result. No computation required."},
    "A25": {"uses_arithmetic": False, "uses_comparison": False, "uses_ordering": False,
            "uses_distinction": False, "uses_identity": False,
            "reason": "Proof result. No computation required."},
    "A26": {"uses_arithmetic": False, "uses_comparison": False, "uses_ordering": False,
            "uses_distinction": False, "uses_identity": False,
            "reason": "Proof result. No computation required."},
}


# ============================================================
# COLLAPSE FUNCTION
# ============================================================

def collapse_core(statements):
    """Remove statements that can be derived from others."""
    remaining = set(statements.keys())
    changed = True
    rounds = []
    while changed:
        changed = False
        to_remove = set()
        for sid in remaining:
            info = statements[sid]
            # Remove if all dependencies are in remaining and it's not independent
            if not info["independent"]:
                if all(dep in remaining for dep in info["requires"]):
                    # Check if this statement adds nothing beyond its dependencies
                    if info["supports"] and all(s in remaining for s in info["supports"]):
                        # It supports something — keep it
                        pass
                    else:
                        # It supports nothing new — remove
                        to_remove.add(sid)
                        changed = True
        if to_remove:
            remaining -= to_remove
            rounds.append({"removed": list(to_remove), "remaining": len(remaining)})
    return remaining, rounds


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("T052: DEPENDENCY COLLAPSE AUDIT")
    print("=" * 70)
    print("Auditing Category A statements only.")
    print("=" * 70)

    # Task 1: Dependency graph
    print("\n[Task 1] Dependency graph...")
    graph_rows = []
    for sid, info in A_STATEMENTS.items():
        for dep in info["requires"]:
            graph_rows.append({"from": dep, "to": sid})
    with open(OUT / "t052_dependency_graph.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["from", "to"])
        w.writeheader()
        w.writerows(graph_rows)
    print(f"  {len(graph_rows)} edges")

    # Task 2: Collapse to minimal core
    print("\n[Task 2] Collapsing to minimal core...")
    core, rounds = collapse_core(A_STATEMENTS)
    print(f"  Started with: {len(A_STATEMENTS)} statements")
    for r in rounds:
        print(f"  Round: removed {r['removed']}, {r['remaining']} remain")
    print(f"  Final core: {len(core)} statements")

    with open(OUT / "t052_irreducible_core.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "phase", "text", "requires", "independent"])
        w.writeheader()
        for sid in sorted(core):
            info = A_STATEMENTS[sid]
            w.writerow({"id": sid, "phase": info["phase"], "text": info["text"],
                        "requires": ", ".join(info["requires"]) if info["requires"] else "none",
                        "independent": info["independent"]})
    print("  Saved t052_irreducible_core.csv")

    # Task 3: Connected components
    print("\n[Task 3] Connected components...")
    # Build adjacency list
    adj = {sid: set() for sid in core}
    for sid in core:
        for dep in A_STATEMENTS[sid]["requires"]:
            if dep in core:
                adj[sid].add(dep)
                adj[dep].add(sid)

    # BFS to find components
    visited = set()
    components = []
    for start in core:
        if start in visited:
            continue
        component = set()
        queue = [start]
        while queue:
            node = queue.pop()
            if node in component:
                continue
            component.add(node)
            visited.add(node)
            for neighbor in adj[node]:
                if neighbor not in component:
                    queue.append(neighbor)
        components.append(component)

    comp_rows = []
    for i, comp in enumerate(components):
        for sid in comp:
            comp_rows.append({"component": i+1, "statement_id": sid,
                              "phase": A_STATEMENTS[sid]["phase"],
                              "text": A_STATEMENTS[sid]["text"]})
    with open(OUT / "t052_connected_components.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["component", "statement_id", "phase", "text"])
        w.writeheader()
        w.writerows(comp_rows)
    print(f"  {len(components)} connected components")
    for i, comp in enumerate(components):
        print(f"    Component {i+1}: {len(comp)} statements — {[s for s in sorted(comp)]}")

    # Task 4: Hidden import audit
    print("\n[Task 4] Hidden import audit...")
    import_rows = []
    for sid in sorted(core):
        info = HIDDEN_IMPORTS.get(sid, {})
        contaminated = any(info.get(k, False) for k in
                          ["uses_arithmetic", "uses_comparison", "uses_ordering",
                           "uses_distinction", "uses_identity"])
        import_rows.append({
            "statement_id": sid,
            "phase": A_STATEMENTS[sid]["phase"],
            "text": A_STATEMENTS[sid]["text"][:60],
            "uses_arithmetic": info.get("uses_arithmetic", False),
            "uses_comparison": info.get("uses_comparison", False),
            "uses_ordering": info.get("uses_ordering", False),
            "uses_distinction": info.get("uses_distinction", False),
            "uses_identity": info.get("uses_identity", False),
            "contaminated": contaminated,
            "reason": info.get("reason", ""),
        })
    with open(OUT / "t052_hidden_import_audit.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=import_rows[0].keys())
        w.writeheader()
        w.writerows(import_rows)
    print("  Saved t052_hidden_import_audit.csv")

    n_clean = sum(1 for r in import_rows if not r["contaminated"])
    n_contaminated = sum(1 for r in import_rows if r["contaminated"])
    print(f"  Clean: {n_clean}/{len(import_rows)}")
    print(f"  Contaminated: {n_contaminated}/{len(import_rows)}")

    # ============================================================
    # SAVE SUMMARY
    # ============================================================

    summary = {
        "n_statements_total": len(A_STATEMENTS),
        "n_statements_core": len(core),
        "core_statements": sorted(core),
        "n_components": len(components),
        "components": [{"id": i+1, "size": len(c), "members": sorted(c)} for i, c in enumerate(components)],
        "n_clean": n_clean,
        "n_contaminated": n_contaminated,
        "clean_statements": [r["statement_id"] for r in import_rows if not r["contaminated"]],
        "contaminated_statements": [r["statement_id"] for r in import_rows if r["contaminated"]],
    }
    with open(OUT / "t052_core_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("\n  Saved t052_core_summary.json")

    # ============================================================
    # FINAL REPORT
    # ============================================================

    print("\n" + "=" * 70)
    print("T052 RESULTS")
    print("=" * 70)

    print(f"\nStatement collapse: {len(A_STATEMENTS)} → {len(core)}")
    print(f"Connected components: {len(components)}")
    print(f"Clean statements: {n_clean}/{len(core)}")
    print(f"Contaminated statements: {n_contaminated}/{len(core)}")

    print(f"\nIRREDUCIBLE CORE:")
    for sid in sorted(core):
        info = A_STATEMENTS[sid]
        contam = HIDDEN_IMPORTS.get(sid, {})
        c_flag = " [CONTAMINATED]" if any(contam.get(k, False) for k in
                    ["uses_arithmetic", "uses_comparison", "uses_ordering",
                     "uses_distinction", "uses_identity"]) else ""
        print(f"  {sid} [{info['phase']}] {info['text'][:60]}{c_flag}")

    print(f"\nCLEAN STATEMENTS (no hidden imports):")
    for r in import_rows:
        if not r["contaminated"]:
            print(f"  {r['statement_id']} [{r['phase']}] {r['text']}")

    print(f"\nCONTAMINATED STATEMENTS:")
    for r in import_rows:
        if r["contaminated"]:
            imports = []
            for k in ["uses_arithmetic", "uses_comparison", "uses_ordering",
                       "uses_distinction", "uses_identity"]:
                if r[k]:
                    imports.append(k.replace("uses_", ""))
            print(f"  {r['statement_id']} [{r['phase']}] imports: {', '.join(imports)}")

    print(f"\nWHAT REMAINS WHEN EVERYTHING UNCERTAIN IS REMOVED:")
    print(f"  {len(core)} Category A statements survive collapse.")
    print(f"  {n_clean} of these are clean (no hidden imports).")
    print(f"  {n_contaminated} are contaminated (import arithmetic/comparison/etc.).")
    print()
    print(f"  The clean core consists of audit and enumeration results:")
    for r in import_rows:
        if not r["contaminated"]:
            print(f"    {r['statement_id']}: {r['text']}")
    print()
    print(f"  The contaminated core consists of measurement results:")
    for r in import_rows:
        if r["contaminated"]:
            print(f"    {r['statement_id']}: {r['text']}")
    print("=" * 70)


if __name__ == "__main__":
    main()
