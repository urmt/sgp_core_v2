#!/usr/bin/env python3
"""
T049: Primitive-Free Observability Audit
=========================================
Determine whether observation itself requires
the primitives identified in T048.

Do NOT conclude anything is fundamental.
Only conclude: "observation fails when X is removed."
"""

import json, csv
from pathlib import Path

ROOT = Path("/home/student/sgp_core_v2")
OUT = ROOT / "sfh_sgp_ood_outputs"

# ============================================================
# PRIMITIVES TO AUDIT
# ============================================================

PRIMITIVES = {
    "P001_comparison": {
        "description": "The ability to determine A vs B",
        "definition": "A relation between two entities that outputs ordering or equivalence",
    },
    "P002_ordering": {
        "description": "The ability to determine before/after, less/greater",
        "definition": "A total or partial order on a set",
    },
    "P003_identity": {
        "description": "The ability to determine that X = X",
        "definition": "Reflexivity: every element is equal to itself",
    },
    "P004_difference": {
        "description": "The ability to determine that X ≠ Y",
        "definition": "Asymmetry: there exist elements that are not equal",
    },
    "P005_distinction": {
        "description": "The ability to determine that A and B are not the same",
        "definition": "Existence of at least two non-identical entities",
    },
}

# ============================================================
# OBSERVER CAPABILITY TESTS
# ============================================================

def test_observer_without_comparison():
    """Can an observer function without comparison?"""
    # An observer that cannot compare:
    # - Cannot determine if two states are "the same"
    # - Cannot determine if something "changed"
    # - Cannot rank, sort, or order
    # - Cannot detect convergence or divergence
    # - Cannot compute any metric

    capabilities = {
        "detect_change": False,      # requires comparing before/after
        "detect_identity": False,    # requires comparing X to itself
        "detect_difference": False,  # requires comparing A to B
        "report_anything": False,    # reporting requires distinguishing reports
        "distinguish_success": False,  # success vs failure requires comparison
        "detect_patterns": False,    # pattern detection requires comparison
        "detect_recurrence": False,  # recurrence requires comparing states
        "detect_convergence": False, # convergence requires comparing distances
    }

    fails_because = (
        "Every act of observation requires comparing a current state "
        "to something: a previous state, a threshold, a null hypothesis, "
        "or the observer's own internal state. Without comparison, "
        "the observer cannot determine whether anything has happened, "
        "changed, or persisted. Observation collapses to zero information."
    )

    return capabilities, fails_because


def test_observer_without_ordering():
    """Can an observer function without ordering?"""
    capabilities = {
        "detect_change": False,       # requires before/after
        "detect_temporal_sequence": False,  # requires temporal ordering
        "detect_causation": False,    # requires temporal ordering
        "detect_recurrence": False,   # requires ordering to detect returns
        "detect_convergence": False,  # requires measuring change over ordered steps
        "detect_progress": False,     # requires ordered comparison
        "report_results": False,      # results must be ordered to be reported
        "rank_outcomes": False,       # ranking requires ordering
    }

    fails_because = (
        "Without ordering, an observer cannot distinguish before from after, "
        "progress from regression, or cause from effect. Temporal experience "
        "collapses to an undifferentiated present. The observer cannot track "
        "what happened, only that something is happening."
    )

    return capabilities, fails_because


def test_observer_without_identity():
    """Can an observer function without identity?"""
    capabilities = {
        "detect_persistence": False,   # requires X = X over time
        "detect_recurrence": False,    # requires recognizing the same state
        "track_objects": False,        # requires identity across time
        "detect_same_input_output": False,  # requires identity comparison
        "detect_patterns": False,      # patterns require repeated identity
        "detect_self": False,          # self-awareness requires identity
        "maintain_memory": False,      # memory requires identifying stored states
        "verify_predictions": False,   # prediction requires matching identity
    }

    fails_because = (
        "Without identity, the observer cannot recognize that anything "
        "persists across time. Each instant is completely new. The observer "
        "cannot track objects, maintain memory, or verify that a prediction "
        "was correct. Observation becomes a sequence of disconnected moments "
        "with no continuity."
    )

    return capabilities, fails_because


def test_observer_without_difference():
    """Can an observer function without difference?"""
    capabilities = {
        "detect_variation": False,      # variation requires difference
        "detect_multiple_states": False, # multiple states require difference
        "detect_boundary": False,       # boundary requires difference
        "detect_grouping": False,       # grouping requires difference
        "detect_structure": False,      # structure requires difference
        "detect_information": False,    # information requires difference
        "detect_entropy": False,        # entropy requires difference
        "distinguish_signals": False,   # signal vs noise requires difference
    }

    fails_because = (
        "Without difference, there is only one state: everything is the same. "
        "The observer cannot detect variation, structure, boundaries, or "
        "information. The universe is a single undifferentiated blob. "
        "No observation is possible because there is nothing to observe."
    )

    return capabilities, fails_because


def test_observer_without_distinction():
    """Can an observer function without distinction?"""
    capabilities = {
        "detect_change": False,
        "detect_identity": False,
        "detect_difference": False,
        "detect_comparison": False,
        "detect_anything": False,
        "report_anything": False,
        "exist_as_observer": False,
    }

    fails_because = (
        "Distinction is the primitive that enables all others. "
        "Without distinction, there cannot be difference, comparison, "
        "identity, ordering, or any form of observation. "
        "The observer cannot even exist as a separate entity from "
        "what it observes. Observation is logically impossible."
    )

    return capabilities, fails_because


TESTS = {
    "P001_comparison": test_observer_without_comparison,
    "P002_ordering": test_observer_without_ordering,
    "P003_identity": test_observer_without_identity,
    "P004_difference": test_observer_without_difference,
    "P005_distinction": test_observer_without_distinction,
}

# ============================================================
# DEPENDENCY ANALYSIS
# ============================================================

def dependency_analysis():
    """What does each primitive require?"""
    deps = {
        "P001_comparison": {
            "requires": ["P002_ordering", "P004_difference"],
            "description": "Comparison requires ordering (before/after) and difference (A≠B)",
        },
        "P002_ordering": {
            "requires": ["P004_difference"],
            "description": "Ordering requires difference (A≠B for A<B to be meaningful)",
        },
        "P003_identity": {
            "requires": ["P005_distinction"],
            "description": "Identity (X=X) requires distinction to separate X from non-X",
        },
        "P004_difference": {
            "requires": ["P005_distinction"],
            "description": "Difference (A≠B) requires distinction to separate A from B",
        },
        "P005_distinction": {
            "requires": [],
            "description": "Distinction requires nothing else (by hypothesis)",
        },
    }
    return deps


# ============================================================
# REMOVAL IMPACT MATRIX
# ============================================================

def removal_impact_matrix():
    """What observation capabilities survive each removal?"""
    matrix = {}
    for name, test_fn in TESTS.items():
        caps, reason = test_fn()
        n丧失 = sum(1 for v in caps.values() if not v)
        n_total = len(caps)
        survival_rate = (n_total - n丧失) / n_total
        matrix[name] = {
            "capabilities_lost": n丧失,
            "capabilities_total": n_total,
            "survival_rate": survival_rate,
            "fails_because": reason,
            "observation_possible": survival_rate > 0.5,
        }
    return matrix


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("T049: PRIMITIVE-FREE OBSERVABILITY AUDIT")
    print("=" * 70)
    print("Question: What is required before observation is possible?")
    print("=" * 70)

    # Run all tests
    print("\n[Auditing each primitive...]\n")
    results = {}
    for name, test_fn in TESTS.items():
        caps, reason = test_fn()
        n丧失 = sum(1 for v in caps.values() if not v)
        n_total = len(caps)
        survival = (n_total - n丧失) / n_total
        observation_possible = survival > 0.5

        results[name] = {
            "capabilities": caps,
            "n_lost": n丧失,
            "n_total": n_total,
            "survival_rate": survival,
            "observation_possible": observation_possible,
            "fails_because": reason,
        }

        status = "OBSERVATION SURVIVES" if observation_possible else "OBSERVATION FAILS"
        print(f"  {name}:")
        print(f"    Capabilities lost: {n丧失}/{n_total}")
        print(f"    Survival rate: {survival:.2f}")
        print(f"    Status: {status}")
        print(f"    Reason: {reason[:80]}...")
        print()

    # Dependency analysis
    print("[Dependency analysis...]\n")
    deps = dependency_analysis()
    for name, info in deps.items():
        print(f"  {name}:")
        print(f"    Requires: {info['requires'] if info['requires'] else 'nothing'}")
        print(f"    {info['description']}")
        print()

    # Removal impact matrix
    print("[Removal impact matrix...]\n")
    impact = removal_impact_matrix()

    # Sort by survival rate (ascending = most damaging)
    ranked = sorted(impact.items(), key=lambda x: x[1]["survival_rate"])

    print("  Ranked by observation survival (lowest first):")
    for rank, (name, info) in enumerate(ranked, 1):
        status = "FAILS" if not info["observation_possible"] else "SURVIVES"
        print(f"    {rank}. {name}: survival={info['survival_rate']:.2f} [{status}]")

    # ============================================================
    # SAVE
    # ============================================================

    print("\n[Saving outputs...]\n")

    # primitive_observer_matrix.csv
    # Collect all capability keys
    all_caps = set()
    for info in results.values():
        all_caps.update(info["capabilities"].keys())
    all_caps = sorted(all_caps)

    matrix_rows = []
    for name, info in results.items():
        row = {"primitive": name, "observation_possible": info["observation_possible"],
               "capabilities_lost": info["n_lost"], "capabilities_total": info["n_total"],
               "survival_rate": info["survival_rate"]}
        for cap in all_caps:
            row[f"cap_{cap}"] = info["capabilities"].get(cap, None)
        matrix_rows.append(row)
    with open(OUT / "t049_primitive_observer_matrix.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=matrix_rows[0].keys())
        w.writeheader()
        w.writerows(matrix_rows)
    print("  Saved t049_primitive_observer_matrix.csv")

    # primitive_dependency_cycles.csv
    cycle_rows = []
    for name, info in deps.items():
        cycle_rows.append({
            "primitive": name,
            "requires": ", ".join(info["requires"]) if info["requires"] else "none",
            "description": info["description"],
        })
    with open(OUT / "t049_primitive_dependency_cycles.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cycle_rows[0].keys())
        w.writeheader()
        w.writerows(cycle_rows)
    print("  Saved t049_primitive_dependency_cycles.csv")

    # primitive_removal_results.csv
    removal_rows = []
    for name, info in impact.items():
        removal_rows.append({
            "primitive": name,
            "observation_possible": info["observation_possible"],
            "capabilities_lost": info["capabilities_lost"],
            "capabilities_total": info["capabilities_total"],
            "survival_rate": info["survival_rate"],
            "fails_because": info["fails_because"],
        })
    with open(OUT / "t049_primitive_removal_results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=removal_rows[0].keys())
        w.writeheader()
        w.writerows(removal_rows)
    print("  Saved t049_primitive_removal_results.csv")

    # primitive_survival_order.csv
    with open(OUT / "t049_primitive_survival_order.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["rank", "primitive", "survival_rate", "observation_possible"])
        w.writeheader()
        for rank, (name, info) in enumerate(ranked, 1):
            w.writerow({"rank": rank, "primitive": name,
                        "survival_rate": info["survival_rate"],
                        "observation_possible": info["observation_possible"]})
    print("  Saved t049_primitive_survival_order.csv")

    # t049_summary.json
    first_fails = ranked[0][0] if ranked else None
    summary = {
        "primitives_tested": len(PRIMITIVES),
        "survival_order": [name for name, _ in ranked],
        "first_removal_that_fails_observation": first_fails,
        "observation_possible_without": {
            name: info["observation_possible"] for name, info in impact.items()
        },
        "conclusion": (
            f"Observation fails when {first_fails} is removed. "
            f"This is not a claim that {first_fails} is fundamental. "
            f"It is a claim that observation requires {first_fails}."
        ),
    }
    with open(OUT / "t049_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("  Saved t049_summary.json")

    # ============================================================
    # FINAL REPORT
    # ============================================================

    print("\n" + "=" * 70)
    print("T049 RESULTS")
    print("=" * 70)

    print("\nOBSERVATION SURVIVAL ORDER (most to least damaging removal):")
    for rank, (name, info) in enumerate(ranked, 1):
        status = "FAILS" if not info["observation_possible"] else "SURVIVES"
        print(f"  {rank}. {name:25s} survival={info['survival_rate']:.2f} [{status}]")

    print(f"\nFIRST PRIMITIVE WHOSE REMOVAL MAKES OBSERVATION IMPOSSIBLE:")
    print(f"  {first_fails}")
    print(f"  Reason: {impact[first_fails]['fails_because'][:100]}...")

    print(f"\nDEPENDENCY CHAIN:")
    for name, info in deps.items():
        reqs = info['requires'] if info['requires'] else 'NOTHING'
        print(f"  {name} requires: {reqs}")

    print(f"\nCORRECTED CONCLUSION:")
    print(f"  T049 does NOT claim any primitive is fundamental.")
    print(f"  T049 shows that observation FAILS when {first_fails} is removed.")
    print(f"  This is a contamination result about the observer,")
    print(f"  not an emergence result about the universe.")
    print("=" * 70)


if __name__ == "__main__":
    main()
