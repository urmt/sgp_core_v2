#!/usr/bin/env python3
"""
T039: Pre-Distinction Assumption Audit
=======================================
Determine what must exist BEFORE distinction is possible.
Identify all hidden assumptions in T037/T038.
Find the irreducible substrate.

This is a LOGICAL audit, not a computational experiment.
"""

import json, csv
from pathlib import Path
from collections import defaultdict

ROOT = Path("/home/student/sgp_core_v2")
OUT = ROOT / "sfh_sgp_ood_outputs"
FIG = ROOT / "figures"
OUT.mkdir(parents=True, exist_ok=True)

# ============================================================
# ASSUMPTION INVENTORY
# ============================================================

ASSUMPTIONS = {
    # === T037 explicit primitives ===
    "symbols": {
        "description": "Discrete symbolic objects (integers 0-N)",
        "t037": True, "t038": False,
        "requires_distinction": False,
        "requires_relation": False,
        "requires_identity": False,
        "requires_observer": False,
    },
    "identity": {
        "description": "Objects have fixed, recoverable identity (hashable)",
        "t037": True, "t038": True,
        "requires_distinction": True,
        "requires_relation": False,
        "requires_identity": False,
        "requires_observer": False,
    },
    "state": {
        "description": "A 'state' exists at each interaction step",
        "t037": True, "t038": True,
        "requires_distinction": False,
        "requires_relation": False,
        "requires_identity": False,
        "requires_observer": False,
    },
    "memory": {
        "description": "Full trajectory is retained across steps",
        "t037": True, "t038": True,
        "requires_distinction": False,
        "requires_relation": False,
        "requires_identity": False,
        "requires_observer": False,
    },
    "ordering": {
        "description": "States are ordered sequences (position matters)",
        "t037": True, "t038": True,
        "requires_distinction": False,
        "requires_relation": False,
        "requires_identity": False,
        "requires_observer": False,
    },
    "recursion": {
        "description": "Rules apply iteratively to their own outputs",
        "t037": True, "t038": True,
        "requires_distinction": False,
        "requires_relation": False,
        "requires_identity": False,
        "requires_observer": False,
    },
    "rule_tables": {
        "description": "Deterministic input->output mapping exists",
        "t037": True, "t038": True,
        "requires_distinction": False,
        "requires_relation": False,
        "requires_identity": False,
        "requires_observer": False,
    },

    # === T038 additional primitives ===
    "continuous_state": {
        "description": "States are vectors in R^n (continuous, not discrete)",
        "t037": False, "t038": True,
        "requires_distinction": False,
        "requires_relation": False,
        "requires_identity": False,
        "requires_observer": False,
    },
    "vector_space": {
        "description": "States exist in a vector space (addition, scalar multiplication defined)",
        "t037": False, "t038": True,
        "requires_distinction": False,
        "requires_relation": False,
        "requires_identity": False,
        "requires_observer": False,
    },

    # === Measurement apparatus (hidden in both) ===
    "comparison": {
        "description": "States can be compared to each other",
        "t037": True, "t038": True,
        "requires_distinction": True,
        "requires_relation": True,
        "requires_identity": True,
        "requires_observer": False,
    },
    "similarity": {
        "description": "A notion of 'similar' vs 'different' exists",
        "t037": True, "t038": True,
        "requires_distinction": True,
        "requires_relation": True,
        "requires_identity": True,
        "requires_observer": False,
    },
    "distance": {
        "description": "A scalar distance between states is defined",
        "t037": True, "t038": True,
        "requires_distinction": True,
        "requires_relation": True,
        "requires_identity": True,
        "requires_observer": False,
    },
    "metric": {
        "description": "Distance satisfies triangle inequality and positivity",
        "t037": True, "t038": True,
        "requires_distinction": True,
        "requires_relation": True,
        "requires_identity": True,
        "requires_observer": False,
    },
    "clustering": {
        "description": "States can be grouped into clusters",
        "t037": True, "t038": True,
        "requires_distinction": True,
        "requires_relation": True,
        "requires_identity": True,
        "requires_observer": False,
    },
    "classification": {
        "description": "States can be assigned to discrete classes",
        "t037": True, "t038": True,
        "requires_distinction": True,
        "requires_relation": False,
        "requires_identity": True,
        "requires_observer": False,
    },

    # === Temporal structure (hidden in both) ===
    "time": {
        "description": "A sequence of discrete steps exists",
        "t037": True, "t038": True,
        "requires_distinction": False,
        "requires_relation": False,
        "requires_identity": False,
        "requires_observer": False,
    },
    "history": {
        "description": "The sequence of past states is accessible",
        "t037": True, "t038": True,
        "requires_distinction": False,
        "requires_relation": False,
        "requires_identity": False,
        "requires_observer": False,
    },

    # === Continuity assumptions ===
    "continuity": {
        "description": "State space is continuous (not discrete)",
        "t037": False, "t038": True,
        "requires_distinction": False,
        "requires_relation": False,
        "requires_identity": False,
        "requires_observer": False,
    },
    "topology": {
        "description": "A notion of 'nearby' states exists",
        "t037": False, "t038": True,
        "requires_distinction": False,
        "requires_relation": True,
        "requires_identity": False,
        "requires_observer": False,
    },
    "neighborhood": {
        "description": "For each state, nearby states can be identified",
        "t037": False, "t038": True,
        "requires_distinction": False,
        "requires_relation": True,
        "requires_identity": False,
        "requires_observer": False,
    },

    # === Detection criteria (hidden in both) ===
    "persistence_criteria": {
        "description": "Thresholds for what counts as 'persistent'",
        "t037": True, "t038": True,
        "requires_distinction": True,
        "requires_relation": False,
        "requires_identity": False,
        "requires_observer": True,
    },
    "closure_criteria": {
        "description": "Thresholds for what counts as 'returned'",
        "t037": True, "t038": True,
        "requires_distinction": True,
        "requires_relation": True,
        "requires_identity": False,
        "requires_observer": True,
    },
    "selfref_criteria": {
        "description": "Thresholds for what counts as 'self-referential'",
        "t037": True, "t038": True,
        "requires_distinction": True,
        "requires_relation": True,
        "requires_identity": False,
        "requires_observer": True,
    },

    # === Foundational (below distinction) ===
    "observer": {
        "description": "An external entity measures and classifies states",
        "t037": True, "t038": True,
        "requires_distinction": False,
        "requires_relation": False,
        "requires_identity": False,
        "requires_observer": False,
    },
    "measurement": {
        "description": "An act of extracting information from states",
        "t037": True, "t038": True,
        "requires_distinction": True,
        "requires_relation": False,
        "requires_identity": False,
        "requires_observer": True,
    },
    "difference": {
        "description": "Two things can be non-identical",
        "t037": True, "t038": True,
        "requires_distinction": True,
        "requires_relation": False,
        "requires_identity": True,
        "requires_observer": False,
    },
    "existence": {
        "description": "Something exists (at least one state)",
        "t037": True, "t038": True,
        "requires_distinction": False,
        "requires_relation": False,
        "requires_identity": False,
        "requires_observer": False,
    },
    "change": {
        "description": "States can differ across time steps",
        "t037": True, "t038": True,
        "requires_distinction": True,
        "requires_relation": False,
        "requires_identity": True,
        "requires_observer": False,
    },

    # === TARGET CONCEPTS (what we're trying to reach) ===
    "distinction": {
        "description": "TARGET: Two things can be non-identical (the concept itself)",
        "t037": True, "t038": True,
        "requires_distinction": False,
        "requires_relation": False,
        "requires_identity": False,
        "requires_observer": False,
    },
    "relation": {
        "description": "TARGET: A connection between two states exists",
        "t037": True, "t038": True,
        "requires_distinction": True,
        "requires_relation": False,
        "requires_identity": False,
        "requires_observer": False,
    },
}

# ============================================================
# DEPENDENCY GRAPH
# ============================================================

def build_dependency_graph():
    """Build directed dependency graph from assumptions."""
    edges = []
    for name, info in ASSUMPTIONS.items():
        if info["requires_distinction"]:
            edges.append((name, "distinction"))
        if info["requires_relation"]:
            edges.append((name, "relation"))
        if info["requires_identity"]:
            edges.append((name, "identity"))
        if info["requires_observer"]:
            edges.append((name, "observer"))
    return edges


# ============================================================
# ROOT ANALYSIS
# ============================================================

def root_analysis():
    """Classify each assumption."""
    results = {}
    for name, info in ASSUMPTIONS.items():
        deps = []
        if info["requires_distinction"]:
            deps.append("distinction")
        if info["requires_relation"]:
            deps.append("relation")
        if info["requires_identity"]:
            deps.append("identity")
        if info["requires_observer"]:
            deps.append("observer")

        # Check for circularity
        is_circular = False
        if "distinction" in deps and name in ["identity", "difference", "comparison",
                                                "similarity", "distance", "metric",
                                                "clustering", "classification",
                                                "measurement", "persistence_criteria",
                                                "closure_criteria", "selfref_criteria"]:
            is_circular = True

        if not deps:
            classification = "FOUNDATIONAL"
        elif is_circular:
            classification = "CIRCULAR"
        elif all(d not in ASSUMPTIONS or not ASSUMPTIONS[d].get("requires_distinction", False)
                 for d in deps):
            classification = "DERIVED"
        else:
            classification = "UNRESOLVED"

        results[name] = {
            "description": info["description"],
            "dependencies": deps,
            "classification": classification,
            "t037_present": info["t037"],
            "t038_present": info["t038"],
        }
    return results


# ============================================================
# COLLAPSE TEST
# ============================================================

def collapse_test(analysis):
    """Find smallest irreducible substrate."""
    # Start with all assumptions
    remaining = set(ASSUMPTIONS.keys())

    # Iteratively remove assumptions that are DERIVED
    # (can be defined using lower assumptions)
    changed = True
    rounds = []
    while changed:
        changed = False
        to_remove = set()
        for name in remaining:
            info = analysis[name]
            if info["classification"] == "DERIVED":
                # Check if all dependencies are still in remaining
                if all(d in remaining for d in info["dependencies"]):
                    to_remove.add(name)
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
    print("T039: PRE-DISTINCTION ASSUMPTION AUDIT")
    print("=" * 70)

    # Task 1: Assumption inventory
    print("\n[Task 1] Assumption inventory...")
    inventory_rows = []
    for name, info in ASSUMPTIONS.items():
        inventory_rows.append({
            "assumption": name,
            "description": info["description"],
            "t037_present": info["t037"],
            "t038_present": info["t038"],
            "requires_distinction": info["requires_distinction"],
            "requires_relation": info["requires_relation"],
            "requires_identity": info["requires_identity"],
            "requires_observer": info["requires_observer"],
        })
    with open(OUT / "t039_assumption_inventory.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=inventory_rows[0].keys())
        w.writeheader()
        w.writerows(inventory_rows)
    print(f"  {len(ASSUMPTIONS)} assumptions cataloged")
    print("  Saved t039_assumption_inventory.csv")

    # Task 2: Dependency graph
    print("\n[Task 2] Dependency graph...")
    edges = build_dependency_graph()
    with open(OUT / "t039_dependency_graph.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["from", "to"])
        w.writeheader()
        for e in edges:
            w.writerow({"from": e[0], "to": e[1]})
    print(f"  {len(edges)} dependency edges")
    print("  Saved t039_dependency_graph.csv")

    # Task 3: Root analysis
    print("\n[Task 3] Root analysis...")
    analysis = root_analysis()

    foundations = [n for n, a in analysis.items() if a["classification"] == "FOUNDATIONAL"]
    derived = [n for n, a in analysis.items() if a["classification"] == "DERIVED"]
    circular = [n for n, a in analysis.items() if a["classification"] == "CIRCULAR"]
    unresolved = [n for n, a in analysis.items() if a["classification"] == "UNRESOLVED"]

    print(f"  FOUNDATIONAL:  {len(foundations)} — {foundations}")
    print(f"  DERIVED:       {len(derived)} — {derived}")
    print(f"  CIRCULAR:      {len(circular)} — {circular}")
    print(f"  UNRESOLVED:    {len(unresolved)} — {unresolved}")

    # Save foundational
    with open(OUT / "t039_foundational_assumptions.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["assumption", "description", "dependencies"])
        w.writeheader()
        for name in foundations:
            w.writerow({
                "assumption": name,
                "description": analysis[name]["description"],
                "dependencies": ", ".join(analysis[name]["dependencies"]),
            })
    print("  Saved t039_foundational_assumptions.csv")

    # Save circular
    with open(OUT / "t039_circular_dependencies.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["assumption", "description", "circular_chain"])
        w.writeheader()
        for name in circular:
            w.writerow({
                "assumption": name,
                "description": analysis[name]["description"],
                "circular_chain": " -> ".join(analysis[name]["dependencies"] + [name]),
            })
    print("  Saved t039_circular_dependencies.csv")

    # Task 4: Collapse test
    print("\n[Task 4] Collapse test...")
    irreducible, rounds = collapse_test(analysis)
    print(f"  Irreducible substrate ({len(irreducible)} assumptions): {sorted(irreducible)}")
    for i, r in enumerate(rounds):
        print(f"  Round {i+1}: removed {r['removed']}, {r['remaining']} remain")

    # Save irreducible substrate
    substrate = {
        "irreducible_assumptions": sorted(irreducible),
        "n_irreducible": len(irreducible),
        "details": {a: analysis[a] for a in sorted(irreducible)},
        "collapse_rounds": rounds,
        "t037_had": sorted(set(ASSUMPTIONS.keys()) - irreducible),
        "t038_had": sorted(set(ASSUMPTIONS.keys()) - irreducible),
    }
    with open(OUT / "t039_irreducible_substrate.json", "w") as f:
        json.dump(substrate, f, indent=2)
    print("  Saved t039_irreducible_substrate.json")

    # ============================================================
    # FIGURES
    # ============================================================

    print("\nGenerating figures...")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.family": "serif", "font.size": 8, "axes.titlesize": 9,
        "figure.dpi": 300, "savefig.dpi": 300, "savefig.bbox": "tight",
    })

    # Fig 1: Dependency graph (text-based)
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("Assumption dependency graph", fontsize=10)

    # Layout: foundations at bottom, derived above, circular at top
    positions = {}
    layers = {
        0: foundations,
        1: [a for a in derived if "state" in a or "time" in a or "memory" in a or "ordering" in a or "recursion" in a or "existence" in a],
        2: [a for a in derived if "continuous" in a or "vector" in a or "topology" in a or "neighborhood" in a],
        3: [a for a in derived if "comparison" in a or "similarity" in a or "distance" in a or "metric" in a or "clustering" in a],
        4: circular,
    }

    for layer, nodes in layers.items():
        for i, name in enumerate(sorted(nodes)):
            x = (i + 1) * 10 / (len(nodes) + 1)
            y = layer * 2 + 1
            positions[name] = (x, y)

    # Draw nodes
    colors = {"FOUNDATIONAL": "#2ecc71", "DERIVED": "#3498db", "CIRCULAR": "#e74c3c", "UNRESOLVED": "#f39c12"}
    for name, pos in positions.items():
        cls = analysis[name]["classification"]
        color = colors.get(cls, "gray")
        ax.plot(pos[0], pos[1], "o", color=color, markersize=12, alpha=0.8)
        ax.annotate(name, pos, fontsize=5, ha="center", va="bottom",
                    xytext=(0, 8), textcoords="offset points")

    # Draw edges
    for e in edges:
        if e[0] in positions and e[1] in positions:
            ax.annotate("", xy=positions[e[1]], xytext=positions[e[0]],
                        arrowprops=dict(arrowstyle="->", color="gray", lw=0.5))

    # Legend
    for cls, color in colors.items():
        ax.plot([], [], "o", color=color, markersize=8, label=cls)
    ax.legend(loc="upper left", fontsize=6)

    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t039_dependency_graph.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t039_dependency_graph.pdf/.png")

    # Fig 2: Reduction tree
    fig, ax = plt.subplots(figsize=(8, 5))
    n_removed = [0] + [len(r["remaining"]) for r in rounds]
    n_remaining = [len(ASSUMPTIONS)] + [r["remaining"] for r in rounds]
    ax.plot(range(len(n_remaining)), n_remaining, "o-", color="#555555", markersize=6)
    ax.set_xlabel("Reduction round")
    ax.set_ylabel("Assumptions remaining")
    ax.set_title("Assumption reduction: from full inventory to irreducible substrate")
    ax.set_xticks(range(len(n_remaining)))
    ax.set_xticklabels([f"R{i}" for i in range(len(n_remaining))])
    ax.axhline(y=len(irreducible), color="red", ls="--", lw=0.6,
               label=f"Irreducible ({len(irreducible)} assumptions)")
    ax.legend(frameon=False)
    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t039_reduction_tree.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t039_reduction_tree.pdf/.png")

    # ============================================================
    # FINAL REPORT
    # ============================================================

    print("\n" + "=" * 70)
    print("T039 RESULTS")
    print("=" * 70)

    print(f"\nAssumptions cataloged: {len(ASSUMPTIONS)}")
    print(f"  Foundational: {len(foundations)}")
    print(f"  Derived: {len(derived)}")
    print(f"  Circular: {len(circular)}")
    print(f"  Unresolved: {len(unresolved)}")

    print(f"\nCircular dependencies (assumption requires what it defines):")
    for name in circular:
        chain = " -> ".join(analysis[name]["dependencies"] + [name])
        print(f"  {name}: {chain}")

    print(f"\nIrreducible substrate ({len(irreducible)} assumptions):")
    for name in sorted(irreducible):
        cls = analysis[name]["classification"]
        deps = analysis[name]["dependencies"]
        print(f"  [{cls}] {name}: {analysis[name]['description']}")
        if deps:
            print(f"         requires: {', '.join(deps)}")

    print(f"\nWhat T037 smuggled:")
    smuggled_37 = [a for a in sorted(ASSUMPTIONS.keys()) if a not in irreducible and ASSUMPTIONS[a]["t037"]]
    for s in smuggled_37:
        print(f"  - {s}")

    print(f"\nWhat T038 smuggled (additional):")
    smuggled_38 = [a for a in sorted(ASSUMPTIONS.keys()) if a not in irreducible and ASSUMPTIONS[a]["t038"] and not ASSUMPTIONS[a]["t037"]]
    for s in smuggled_38:
        print(f"  - {s}")

    # Determine which criterion is satisfied
    print(f"\nFINAL ANSWER:")
    if "distinction" in irreducible:
        criterion = "B: distinction is itself irreducible"
    else:
        criterion = "A: irreducible substrate below distinction found"

    print(f"  Criterion satisfied: {criterion}")
    print(f"  Deepest surviving assumption: {sorted(irreducible)[0]}")
    print("=" * 70)

    # Save summary
    summary = {
        "n_assumptions": len(ASSUMPTIONS),
        "n_foundational": len(foundations),
        "n_derived": len(derived),
        "n_circular": len(circular),
        "n_unresolved": len(unresolved),
        "foundational": foundations,
        "derived": derived,
        "circular": circular,
        "unresolved": unresolved,
        "irreducible_substrate": sorted(irreducible),
        "t037_smuggled": smuggled_37,
        "t038_smuggled": smuggled_38,
        "criterion_satisfied": criterion,
        "deepest_assumption": sorted(irreducible)[0] if irreducible else None,
    }
    with open(OUT / "t039_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("\nSaved t039_summary.json")


if __name__ == "__main__":
    main()
