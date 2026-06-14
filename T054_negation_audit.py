#!/usr/bin/env python3
"""
T054: Negation Audit
=====================
Audit the negative core from T053.
Determine whether even negation survives.
"""

import csv, json
from pathlib import Path

ROOT = Path("/home/student/sgp_core_v2")
OUT = ROOT / "sfh_sgp_ood_outputs"

# ============================================================
# NEGATIVE STATEMENTS FROM T053
# ============================================================

NEGATIVE_STATEMENTS = {
    "N01": "Geometry emergence was not demonstrated.",
    "N02": "Distinction emergence was not demonstrated without hidden assumptions.",
    "N03": "Recurrence was not demonstrated to be non-artifactual.",
    "N04": "Convergence was not demonstrated without detector contamination.",
    "N05": "No primitive was found that survives full assumption audit.",
    "N06": "The dependency graph among primitives contains circular chains.",
    "N07": "All 45 detectors import comparison, arithmetic, and distinction.",
    "N08": "The gap between model requirements and observation requirements cannot be closed.",
    "N09": "No statement from T037-T050 about 'what exists' survived audit.",
    "N10": "The only surviving statements are methodological records.",
}

# ============================================================
# TERM AUDIT
# ============================================================

TERM_AUDIT = {
    "demonstrated": {
        "requires_identity": True,
        "requires_distinction": True,
        "requires_comparison": True,
        "requires_ordering": False,
        "requires_memory": True,
        "reasoning": "Demonstration requires: (1) distinguishing demo from non-demo (distinction), (2) recognizing the demo (identity), (3) comparing result to claim (comparison), (4) retaining the demo (memory).",
    },
    "survives": {
        "requires_identity": True,
        "requires_distinction": True,
        "requires_comparison": True,
        "requires_ordering": True,
        "requires_memory": True,
        "reasoning": "Survival requires: (1) persisting across time (ordering, memory), (2) being identifiable (identity), (3) not being destroyed (distinction from non-survival).",
    },
    "audit": {
        "requires_identity": True,
        "requires_distinction": True,
        "requires_comparison": True,
        "requires_ordering": True,
        "requires_memory": True,
        "reasoning": "Audit requires: (1) examining items (identity), (2) comparing to standards (comparison), (3) recording results (memory), (4) sequencing steps (ordering).",
    },
    "gap": {
        "requires_identity": True,
        "requires_distinction": True,
        "requires_comparison": True,
        "requires_ordering": False,
        "requires_memory": False,
        "reasoning": "Gap requires: (1) two things to compare (distinction), (2) comparison between them, (3) identification of both sides (identity).",
    },
    "closed": {
        "requires_identity": True,
        "requires_distinction": True,
        "requires_comparison": True,
        "requires_ordering": True,
        "requires_memory": False,
        "reasoning": "Closing requires: (1) open state (distinction from closed), (2) transition (ordering), (3) recognizing closure (identity), (4) comparison with open state.",
    },
    "primitive": {
        "requires_identity": True,
        "requires_distinction": True,
        "requires_comparison": False,
        "requires_ordering": False,
        "requires_memory": False,
        "reasoning": "Primitive requires: (1) identifying what is primitive (identity), (2) distinguishing from non-primitive (distinction).",
    },
    "geometry": {
        "requires_identity": True,
        "requires_distinction": True,
        "requires_comparison": True,
        "requires_ordering": False,
        "requires_memory": False,
        "reasoning": "Geometry requires: (1) structures to measure (identity), (2) distinction between structures, (3) measurement (comparison).",
    },
    "found": {
        "requires_identity": True,
        "requires_distinction": True,
        "requires_comparison": False,
        "requires_ordering": False,
        "requires_memory": True,
        "reasoning": "Finding requires: (1) the found thing (identity), (2) distinguishing found from not-found (distinction), (3) retaining the finding (memory).",
    },
    "imported": {
        "requires_identity": True,
        "requires_distinction": True,
        "requires_comparison": False,
        "requires_ordering": False,
        "requires_memory": True,
        "reasoning": "Importing requires: (1) the imported thing (identity), (2) source vs destination (distinction), (3) transfer (memory).",
    },
    "cannot": {
        "requires_identity": False,
        "requires_distinction": True,
        "requires_comparison": True,
        "requires_ordering": False,
        "requires_memory": False,
        "reasoning": "Cannot requires: (1) capability vs incapability (distinction), (2) comparison with standard.",
    },
    "meaningful": {
        "requires_identity": True,
        "requires_distinction": True,
        "requires_comparison": True,
        "requires_ordering": False,
        "requires_memory": False,
        "reasoning": "Meaningful requires: (1) the meaningful thing (identity), (2) meaningful vs meaningless (distinction), (3) comparison with standard.",
    },
}

# ============================================================
# NEGATIVE STATEMENT ANALYSIS
# ============================================================

def analyze_negative(sid, text):
    """Analyze a negative statement for dependencies."""
    # Find which terms from TERM_AUDIT appear in the statement
    imported_terms = {}
    for term, info in TERM_AUDIT.items():
        if term in text.lower():
            deps = []
            if info["requires_identity"]: deps.append("identity")
            if info["requires_distinction"]: deps.append("distinction")
            if info["requires_comparison"]: deps.append("comparison")
            if info["requires_ordering"]: deps.append("ordering")
            if info["requires_memory"]: deps.append("memory")
            imported_terms[term] = deps

    all_imports = set()
    for deps in imported_terms.values():
        all_imports.update(deps)

    # Classify: FE (failure of evidence) vs EF (evidence of failure)
    if "not demonstrated" in text or "not found" in text or "cannot be" in text:
        classification = "FE"  # failure of evidence
    elif "contains" in text or "import" in text or "survived" in text:
        classification = "EF"  # evidence of failure
    else:
        classification = "U"   # unresolved

    return {
        "sid": sid,
        "text": text,
        "imported_terms": imported_terms,
        "all_imports": list(all_imports),
        "n_imports": len(all_imports),
        "classification": classification,
    }


# ============================================================
# NEGATION COLLAPSE
# ============================================================

def test_negation_without_imports():
    """Can negative statements exist without imported concepts?"""
    results = {}
    for sid, text in NEGATIVE_STATEMENTS.items():
        analysis = analyze_negative(sid, text)
        # Test: can the statement be rephrased without the imported concepts?
        # This is the core question.
        survives = analysis["n_imports"] == 0
        results[sid] = {
            "original": text,
            "survives_without_imports": survives,
            "imports": analysis["all_imports"],
        }
    return results


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("T054: NEGATION AUDIT")
    print("=" * 70)
    print("Auditing whether negative statements survive.")
    print("=" * 70)

    # Task 1: Term audit
    print("\n[Task 1] Term audit...\n")
    for term, info in TERM_AUDIT.items():
        deps = []
        if info["requires_identity"]: deps.append("identity")
        if info["requires_distinction"]: deps.append("distinction")
        if info["requires_comparison"]: deps.append("comparison")
        if info["requires_ordering"]: deps.append("ordering")
        if info["requires_memory"]: deps.append("memory")
        print(f"  {term:15s}: {deps}")

    # Task 2: Statement analysis
    print("\n[Task 2] Failure vs evidence classification...\n")
    analyses = []
    for sid, text in NEGATIVE_STATEMENTS.items():
        analysis = analyze_negative(sid, text)
        analyses.append(analysis)
        print(f"  {sid}: [{analysis['classification']}] {text[:60]}")
        print(f"    Imports: {analysis['all_imports']}")

    # Task 3: Negation collapse
    print("\n[Task 3] Negation collapse...\n")
    collapse_results = test_negation_without_imports()
    for sid, result in collapse_results.items():
        status = "SURVIVES" if result["survives_without_imports"] else "COLLAPSES"
        print(f"  {sid}: {status} (imports: {result['imports']})")

    # Task 4: Minimal survivor search
    print("\n[Task 4] Minimal survivor search...\n")
    surviving_positive = 0  # from T053
    surviving_negative = sum(1 for r in collapse_results.values() if r["survives_without_imports"])

    if surviving_positive > 0:
        outcome = "A: positive survivor exists"
    elif surviving_negative > 0:
        outcome = "B: negative survivor exists"
    else:
        outcome = "C: neither survives"

    print(f"  Positive survivors: {surviving_positive}")
    print(f"  Negative survivors: {surviving_negative}")
    print(f"  Outcome: {outcome}")

    # ============================================================
    # SAVE
    # ============================================================

    print("\n[Saving outputs...]\n")

    # t054_negative_dependency_audit.csv
    dep_rows = []
    for term, info in TERM_AUDIT.items():
        deps = []
        if info["requires_identity"]: deps.append("identity")
        if info["requires_distinction"]: deps.append("distinction")
        if info["requires_comparison"]: deps.append("comparison")
        if info["requires_ordering"]: deps.append("ordering")
        if info["requires_memory"]: deps.append("memory")
        dep_rows.append({
            "term": term,
            "requires_identity": info["requires_identity"],
            "requires_distinction": info["requires_distinction"],
            "requires_comparison": info["requires_comparison"],
            "requires_ordering": info["requires_ordering"],
            "requires_memory": info["requires_memory"],
            "total_imports": len(deps),
        })
    with open(OUT / "t054_negative_dependency_audit.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=dep_rows[0].keys())
        w.writeheader()
        w.writerows(dep_rows)
    print("  Saved t054_negative_dependency_audit.csv")

    # t054_failure_vs_evidence.csv
    with open(OUT / "t054_failure_vs_evidence.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["statement_id", "text", "classification", "n_imports"])
        w.writeheader()
        for a in analyses:
            w.writerow({"statement_id": a["sid"], "text": a["text"],
                        "classification": a["classification"], "n_imports": a["n_imports"]})
    print("  Saved t054_failure_vs_evidence.csv")

    # t054_negation_collapse.csv
    with open(OUT / "t054_negation_collapse.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["statement_id", "original", "survives", "imports"])
        w.writeheader()
        for sid, result in collapse_results.items():
            w.writerow({"statement_id": sid, "original": result["original"],
                        "survives": result["survives_without_imports"],
                        "imports": ", ".join(result["imports"]) if result["imports"] else "none"})
    print("  Saved t054_negation_collapse.csv")

    # t054_minimal_survivor_search.csv
    with open(OUT / "t054_minimal_survivor_search.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["category", "count", "outcome"])
        w.writeheader()
        w.writerow({"category": "positive_survivors", "count": surviving_positive, "outcome": outcome})
        w.writerow({"category": "negative_survivors", "count": surviving_negative, "outcome": outcome})
    print("  Saved t054_minimal_survivor_search.csv")

    # t054_summary.json
    summary = {
        "n_negative_statements": len(NEGATIVE_STATEMENTS),
        "n_fe_statements": sum(1 for a in analyses if a["classification"] == "FE"),
        "n_ef_statements": sum(1 for a in analyses if a["classification"] == "EF"),
        "n_u_statements": sum(1 for a in analyses if a["classification"] == "U"),
        "n_collapsed": sum(1 for r in collapse_results.values() if not r["survives_without_imports"]),
        "n_survived": surviving_negative,
        "outcome": outcome,
        "statement_classifications": {a["sid"]: a["classification"] for a in analyses},
    }
    with open(OUT / "t054_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("  Saved t054_summary.json")

    # ============================================================
    # FINAL REPORT
    # ============================================================

    print("\n" + "=" * 70)
    print("T054 RESULTS")
    print("=" * 70)

    print(f"\nNegative statements: {len(NEGATIVE_STATEMENTS)}")
    print(f"  Failure of evidence (FE): {sum(1 for a in analyses if a['classification'] == 'FE')}")
    print(f"  Evidence of failure (EF): {sum(1 for a in analyses if a['classification'] == 'EF')}")
    print(f"  Unresolved (U): {sum(1 for a in analyses if a['classification'] == 'U')}")

    print(f"\nNegation collapse:")
    for sid, result in collapse_results.items():
        status = "SURVIVES" if result["survives_without_imports"] else "COLLAPSES"
        print(f"  {sid}: {status}")

    print(f"\nMinimal survivor search:")
    print(f"  Positive survivors: {surviving_positive}")
    print(f"  Negative survivors: {surviving_negative}")
    print(f"  Outcome: {outcome}")

    print(f"\nWHAT REMAINS AFTER AUDITING BOTH AFFIRMATION AND NEGATION?")
    print()
    if surviving_negative > 0:
        print("  Some negative statements survive.")
        print("  They are the minimal justified claims.")
        print()
        for sid, result in collapse_results.items():
            if result["survives_without_imports"]:
                print(f"    {sid}: {result['original']}")
    else:
        print("  No statement survives.")
        print("  Neither positive nor negative claims are justified.")
        print("  The investigation has reached absolute zero.")
    print("=" * 70)


if __name__ == "__main__":
    main()
