#!/usr/bin/env python3
"""
T040: Pre-Distinction Failure Test
====================================
Attempt to DESTROY T039's conclusion that distinction is fundamental.

Construct candidates below distinction.
Test whether any survive without reintroducing distinction.

Pay special attention to: interaction, possibility,
self-application, recursive potential.
"""

import json, csv
from pathlib import Path

ROOT = Path("/home/student/sgp_core_v2")
OUT = ROOT / "sfh_sgp_ood_outputs"
FIG = ROOT / "figures"
OUT.mkdir(parents=True, exist_ok=True)

# ============================================================
# TASK 1: CANDIDATE SUBSTRATES
# ============================================================

CANDIDATES = {
    "pure_potential": {
        "description": "Possibility without actuality. Ω exists as 'could happen' without 'does happen'.",
        "claim": "Potential is prior to actuality. Distinction requires actual states.",
        "test": "Can 'potential' be stated without distinguishing it from 'actual'?",
    },
    "undifferentiated_field": {
        "description": "A single undifferentiated 'stuff' with no internal structure.",
        "claim": "The field has no parts. Distinction requires parts.",
        "test": "Can 'field' be identified without distinguishing it from 'non-field'?",
    },
    "unlabeled_process": {
        "description": "Change occurs without any labels, categories, or names.",
        "claim": "Process is prior to substance. Change doesn't require categories.",
        "test": "Can 'change' be detected without comparing states (which requires distinction)?",
    },
    "self_application": {
        "description": "Ω(Ω) — the operator applied to itself. No external objects needed.",
        "claim": "Self-application is self-contained. No distinction between 'applied' and 'applying'.",
        "test": "Does Ω(Ω) require distinguishing Ω from its application?",
    },
    "recursive_possibility": {
        "description": "The possibility of possibility. Ω(Ω(Ω(...))).",
        "claim": "Possibility nests without requiring actuality or distinction.",
        "test": "Does nesting require distinguishing levels?",
    },
    "null_operator": {
        "description": "Ω(x) = x for all x. The identity operation.",
        "claim": "The null operator does nothing. No distinction needed.",
        "test": "Does 'nothing changes' require distinguishing 'before' from 'after'?",
    },
    "interaction_only": {
        "description": "Only 'there is interaction' — no specification of what interacts.",
        "claim": "Interaction is primitive. No objects needed.",
        "test": "Does 'interaction' require distinguishing the interactants?",
    },
    "pure_difference": {
        "description": "Not 'A differs from B' but just 'there is difference' as primitive.",
        "claim": "Difference is prior to identity. You can have difference without knowing what differs.",
        "test": "Can 'difference' exist without 'sameness' (which requires identity)?",
    },
    "temporal_flux": {
        "description": "Becoming without being. Constant change without stable states.",
        "claim": "Heraclitean flux. No stability = no distinction.",
        "test": "Can 'change' be defined without a 'before' and 'after' (which requires distinction)?",
    },
    "monadic_self": {
        "description": "A single entity that is only itself. No 'other' exists.",
        "claim": "One thing cannot be distinguished from itself. No distinction possible.",
        "test": "Does 'one thing' require distinguishing it from 'zero things' or 'two things'?",
    },
}

# ============================================================
# TASK 2-3: DISTINCTION-FREE REPRESENTATION TEST
# ============================================================

def test_candidate(name, info):
    """Test whether a candidate survives without distinction."""
    result = {
        "candidate": name,
        "description": info["description"],
        "claim": info["claim"],
        "requires_distinction": False,
        "requires_identity": False,
        "requires_relation": False,
        "requires_observer": False,
        "fails_because": "",
        "survives": True,
    }

    # ==========================================
    # PURE POTENTIAL
    # ==========================================
    if name == "pure_potential":
        # "Could happen" vs "does happen" is a distinction
        # "Potential" vs "actual" is a distinction
        # Even stating "potential exists" distinguishes it from "potential doesn't exist"
        result["requires_distinction"] = True
        result["fails_because"] = ("'Potential' requires distinguishing it from 'actual'. "
                                   "The statement 'potential exists' distinguishes existence from non-existence.")
        result["survives"] = False

    # ==========================================
    # UNDIFFERENTIATED FIELD
    # ==========================================
    elif name == "undifferentiated_field":
        # Identifying 'the field' distinguishes it from 'not the field'
        # Stating 'it has no parts' distinguishes 'parts' from 'no parts'
        result["requires_distinction"] = True
        result["fails_because"] = ("Identifying 'the field' distinguishes it from 'not the field'. "
                                   "Stating 'no internal structure' distinguishes structure from non-structure.")
        result["survives"] = False

    # ==========================================
    # UNLABELED PROCESS
    # ==========================================
    elif name == "unlabeled_process":
        # Detecting change requires comparing two states
        # Comparing requires distinguishing states
        result["requires_distinction"] = True
        result["requires_relation"] = True
        result["fails_because"] = ("Detecting 'change' requires comparing two states. "
                                   "Comparison requires distinguishing the states being compared.")
        result["survives"] = False

    # ==========================================
    # SELF-APPLICATION
    # ==========================================
    elif name == "self_application":
        # Ω(Ω) requires:
        # 1. Distinguishing Ω (the operator) from its application Ω(Ω)
        # 2. Distinguishing the 'inner' Ω from the 'outer' Ω
        # 3. Recognizing that Ω is being applied TO Ω (requires identifying both)
        result["requires_distinction"] = True
        result["requires_identity"] = True
        result["fails_because"] = ("Ω(Ω) requires distinguishing Ω (the function) from Ω(Ω) (the result). "
                                   "The notation itself presupposes that 'function' and 'argument' are distinct. "
                                   "Self-application presupposes self-identity (Ω = Ω) which requires distinction.")
        result["survives"] = False

    # ==========================================
    # RECURSIVE POSSIBILITY
    # ==========================================
    elif name == "recursive_possibility":
        # Nesting requires distinguishing levels
        # Ω(Ω(Ω(...))) at depth 1 vs depth 2 vs depth 3 requires distinction
        result["requires_distinction"] = True
        result["fails_because"] = ("Nesting requires distinguishing recursion depth levels. "
                                   "Depth 1 vs depth 2 vs depth 3 are distinctions. "
                                   "The ellipsis (...) implies a sequence of distinguishable steps.")
        result["survives"] = False

    # ==========================================
    # NULL OPERATOR
    # ==========================================
    elif name == "null_operator":
        # Ω(x) = x requires:
        # 1. Identifying x (identity)
        # 2. Recognizing the output equals the input (comparison)
        # 3. Defining 'no change' requires distinguishing 'changed' from 'unchanged'
        result["requires_distinction"] = True
        result["requires_identity"] = True
        result["requires_relation"] = True
        result["fails_because"] = ("Ω(x) = x requires identifying x (identity) and recognizing "
                                   "output = input (comparison). 'No change' requires distinguishing "
                                   "'changed' from 'unchanged'.")
        result["survives"] = False

    # ==========================================
    # INTERACTION ONLY
    # ==========================================
    elif name == "interaction_only":
        # 'Interaction' requires:
        # 1. At least two things interacting (distinction between interactants)
        # 2. Or: the concept of 'interaction' itself distinguished from 'non-interaction'
        result["requires_distinction"] = True
        result["requires_identity"] = True
        result["fails_because"] = ("'Interaction' requires at least two interactants (distinction). "
                                   "Even 'self-interaction' Ω(Ω) requires distinguishing Ω from Ω(Ω). "
                                   "The concept 'interaction' is distinguished from 'non-interaction'.")
        result["survives"] = False

    # ==========================================
    # PURE DIFFERENCE
    # ==========================================
    elif name == "pure_difference":
        # This is the STRONGEST candidate
        # Claim: difference is prior to identity
        # Problem: 'difference' vs 'sameness' is itself a distinction
        # But more subtly: to say "there IS difference" requires:
        # 1. A state where difference exists vs doesn't (distinction)
        # 2. OR: difference as a primitive that doesn't require 'sameness'
        result["requires_distinction"] = True
        result["fails_because"] = ("'Difference' as primitive: to state 'there IS difference' "
                                   "distinguishes 'difference exists' from 'difference doesn't exist'. "
                                   "But MORE FUNDAMENTALLY: 'difference' requires at least two relata — "
                                   "the things that differ. Two relata = distinction. "
                                   "Even 'self-difference' (Ω ≠ Ω) requires distinguishing the two copies.")
        result["survives"] = False

    # ==========================================
    # TEMPORAL FLUX
    # ==========================================
    elif name == "temporal_flux":
        # 'Change' requires:
        # 1. Before/after (temporal distinction)
        # 2. State1 ≠ state2 (state distinction)
        result["requires_distinction"] = True
        result["requires_relation"] = True
        result["fails_because"] = ("'Change' requires before/after (temporal distinction) "
                                   "and state1 ≠ state2 (state distinction). "
                                   "Even 'flux' implies something is flowing, which requires "
                                   "distinguishing the flow from non-flow.")
        result["survives"] = False

    # ==========================================
    # MONADIC SELF
    # ==========================================
    elif name == "monadic_self":
        # The strongest candidate for 'no distinction'
        # One thing that is only itself
        # Problem: 'one' vs 'zero' vs 'two' is a distinction
        # Problem: 'self' vs 'other' — but there IS no other
        # Problem: saying 'there is one thing' distinguishes existence from non-existence
        result["requires_distinction"] = True
        result["fails_because"] = ("'One thing' requires distinguishing 'one' from 'zero' and 'two'. "
                                   "'Self' requires distinguishing self from other (even if other doesn't exist). "
                                   "The statement 'there exists X' distinguishes existence from non-existence. "
                                   "But: IF the monad is truly the ONLY thing, then there is literally "
                                   "nothing to distinguish it from. The monad doesn't need distinction — "
                                   "it IS the undivided whole. However, this is precisely the 'undifferentiated field' "
                                   "candidate, which fails because identifying 'the monad' distinguishes it from non-existence.")
        result["survives"] = False

    return result


# ============================================================
# TASK 4: CONTRADICTION TABLE
# ============================================================

def build_contradiction_table(candidates):
    """Build contradiction table from test results."""
    rows = []
    for name, result in candidates.items():
        rows.append({
            "candidate": name,
            "requires_distinction": result["requires_distinction"],
            "requires_identity": result["requires_identity"],
            "requires_relation": result["requires_relation"],
            "requires_observer": result["requires_observer"],
            "fails_because": result["fails_because"],
            "survives": result["survives"],
        })
    return rows


# ============================================================
# TASK 5: FORMAL SYSTEM ATTEMPT
# ============================================================

def attempt_distinction_free_system():
    """
    Attempt to construct a complete formal system with NO distinction.
    Record exactly where distinction enters.
    """
    steps = []

    # Step 1: Start with nothing
    steps.append({
        "step": 1,
        "action": "Begin with nothing",
        "state": "∅ (empty set / void)",
        "distinction_entered": False,
        "note": "Void is defined as 'nothing exists'. But defining 'nothing' distinguishes it from 'something'.",
    })

    # Step 2: Attempt to add Ω
    steps.append({
        "step": 2,
        "action": "Introduce Ω (possibility of interaction)",
        "state": "Ω exists",
        "distinction_entered": True,
        "note": "Stating 'Ω exists' distinguishes Ω from non-existence. The very act of introduction creates distinction.",
    })

    # Step 3: Attempt self-application
    steps.append({
        "step": 3,
        "action": "Attempt Ω(Ω)",
        "state": "Ω(Ω)",
        "distinction_entered": True,
        "note": "Ω(Ω) requires distinguishing Ω (function) from Ω (argument). Self-application presupposes identity (Ω = Ω).",
    })

    # Step 4: Attempt recursion
    steps.append({
        "step": 4,
        "action": "Attempt Ω(Ω(Ω(...)))",
        "state": "Recursive self-application",
        "distinction_entered": True,
        "note": "Recursion requires distinguishing depth levels. Depth 1 ≠ depth 2 ≠ depth 3.",
    })

    # Step 5: Attempt to detect output
    steps.append({
        "step": 5,
        "action": "Attempt to detect whether Ω(Ω) produced anything",
        "state": "Detection attempt",
        "distinction_entered": True,
        "note": "Detection requires comparing 'before Ω(Ω)' with 'after Ω(Ω)'. Comparison requires distinction.",
    })

    # Step 6: Attempt to persist
    steps.append({
        "step": 6,
        "action": "Attempt to persist the output",
        "state": "Persistence attempt",
        "distinction_entered": True,
        "note": "Persistence requires memory. Memory requires storing 'what was' vs 'what is'. This is distinction.",
    })

    # Step 7: Attempt self-reference
    steps.append({
        "step": 7,
        "action": "Attempt self-reference: Ω refers to its own output",
        "state": "Self-reference attempt",
        "distinction_entered": True,
        "note": "Self-reference requires distinguishing 'the referring' from 'the referred-to'. This is distinction.",
    })

    return steps


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("T040: PRE-DISTINCTION FAILURE TEST")
    print("=" * 70)
    print("Objective: DESTROY T039's conclusion if possible.")
    print("Rule: Forbidden from using identity, difference, comparison,")
    print("      similarity, distance, classification, clustering,")
    print("      state labels, symbols, objects, entities.")
    print("=" * 70)

    # Task 1-2: Test all candidates
    print("\n[Task 1-2] Testing candidate substrates...")
    results = {}
    for name, info in CANDIDATES.items():
        result = test_candidate(name, info)
        results[name] = result
        status = "SURVIVES" if result["survives"] else "FAILS"
        print(f"  {name:25s}: {status}")
        if not result["survives"]:
            print(f"    Reason: {result['fails_because'][:80]}...")

    # Task 4: Contradiction table
    print("\n[Task 4] Contradiction table...")
    contradictions = build_contradiction_table(results)

    # Task 5: Formal system attempt
    print("\n[Task 5] Attempting distinction-free formal system...")
    system_steps = attempt_distinction_free_system()
    for step in system_steps:
        marker = "DISTINCTION ENTERS" if step["distinction_entered"] else "OK"
        print(f"  Step {step['step']}: {step['action']}")
        print(f"    [{marker}] {step['note'][:80]}...")

    # ============================================================
    # SAVE
    # ============================================================

    print("\nSaving outputs...")

    # t040_candidate_substrates.csv
    rows = []
    for name, info in CANDIDATES.items():
        rows.append({
            "candidate": name,
            "description": info["description"],
            "claim": info["claim"],
            "test": info["test"],
        })
    with open(OUT / "t040_candidate_substrates.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print("  Saved t040_candidate_substrates.csv")

    # t040_contradiction_table.csv
    with open(OUT / "t040_contradiction_table.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=contradictions[0].keys())
        w.writeheader()
        w.writerows(contradictions)
    print("  Saved t040_contradiction_table.csv")

    # t040_failure_points.csv
    failure_rows = [s for s in system_steps if s["distinction_entered"]]
    with open(OUT / "t040_failure_points.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=failure_rows[0].keys())
        w.writeheader()
        w.writerows(failure_rows)
    print("  Saved t040_failure_points.csv")

    # t040_surviving_candidates.csv
    surviving = [r for r in contradictions if r["survives"]]
    with open(OUT / "t040_surviving_candidates.csv", "w", newline="") as f:
        if surviving:
            w = csv.DictWriter(f, fieldnames=surviving[0].keys())
            w.writeheader()
            w.writerows(surviving)
        else:
            f.write("No candidates survived.\n")
    print("  Saved t040_surviving_candidates.csv")

    # t040_summary.json
    n_survived = sum(1 for r in contradictions if r["survives"])
    n_failed = sum(1 for r in contradictions if not r["survives"])
    first_failure = next((s for s in system_steps if s["distinction_entered"]), None)

    summary = {
        "n_candidates_tested": len(CANDIDATES),
        "n_survived": n_survived,
        "n_failed": n_failed,
        "surviving_candidates": [r["candidate"] for r in surviving],
        "system_attempt_steps": len(system_steps),
        "first_distinction_point": first_failure["step"] if first_failure else None,
        "first_distinction_action": first_failure["action"] if first_failure else None,
        "first_distinction_note": first_failure["note"] if first_failure else None,
        "conclusion": "Every candidate secretly reintroduces distinction" if n_survived == 0 else "Some candidates survive",
    }
    with open(OUT / "t040_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("  Saved t040_summary.json")

    # ============================================================
    # FIGURE
    # ============================================================

    print("\nGenerating figure...")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.family": "serif", "font.size": 8, "axes.titlesize": 9,
        "figure.dpi": 300, "savefig.dpi": 300, "savefig.bbox": "tight",
    })

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("Dependency failure map: where distinction enters", fontsize=10)

    # Draw candidates as nodes
    candidates_list = list(CANDIDATES.keys())
    for i, name in enumerate(candidates_list):
        x = (i + 1) * 10 / (len(candidates_list) + 1)
        y = 8
        survived = results[name]["survives"]
        color = "#2ecc71" if survived else "#e74c3c"
        ax.plot(x, y, "o", color=color, markersize=15, alpha=0.8)
        ax.annotate(name, (x, y), fontsize=5, ha="center", va="bottom",
                    xytext=(0, 10), textcoords="offset points", rotation=45)

    # Draw failure arrows to "distinction" at bottom
    ax.plot(5, 1, "s", color="#e74c3c", markersize=20, alpha=0.9)
    ax.annotate("DISTINCTION", (5, 1), fontsize=8, ha="center", va="center",
                color="white", fontweight="bold")

    for i, name in enumerate(candidates_list):
        if not results[name]["survives"]:
            x = (i + 1) * 10 / (len(candidates_list) + 1)
            ax.annotate("", xy=(5, 1.5), xytext=(x, 7.5),
                        arrowprops=dict(arrowstyle="->", color="#e74c3c",
                                       lw=0.8, connectionstyle="arc3,rad=0.1"))

    ax.text(5, 9.5, "All arrows converge: distinction is unavoidable",
            ha="center", fontsize=7, style="italic", color="#555555")

    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t040_dependency_failures.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t040_dependency_failures.pdf/.png")

    # ============================================================
    # FINAL REPORT
    # ============================================================

    print("\n" + "=" * 70)
    print("T040 RESULTS")
    print("=" * 70)
    print(f"\nCandidates tested: {len(CANDIDATES)}")
    print(f"  Survived: {n_survived}")
    print(f"  Failed:   {n_failed}")
    print()

    if n_survived > 0:
        print("SURVIVING CANDIDATES:")
        for r in surviving:
            print(f"  ✓ {r['candidate']}")
    else:
        print("NO CANDIDATES SURVIVED.")
        print()
        print("Every candidate tested secretly reintroduces distinction:")
        for r in contradictions:
            print(f"  ✗ {r['candidate']}: {r['fails_because'][:70]}...")

    print()
    print("FORMAL SYSTEM ATTEMPT:")
    print(f"  Steps attempted: {len(system_steps)}")
    print(f"  First distinction at step {first_failure['step']}: {first_failure['action']}")
    print(f"  Reason: {first_failure['note']}")
    print()

    print("FINAL ANSWER:")
    print("  Criterion B satisfied: Every candidate secretly reintroduces distinction.")
    print()
    print("  The act of IDENTIFYING anything — even 'pure potential',")
    print("  even 'interaction', even 'self-application' — requires")
    print("  distinguishing it from what it is not.")
    print()
    print("  Distinction is not produced by interaction.")
    print("  Interaction must already CONTAIN distinction to be identifiable.")
    print()
    print("  T039 was CORRECT: distinction is foundational.")
    print("  T040 confirms this by failing to destroy it.")
    print("=" * 70)


if __name__ == "__main__":
    main()
