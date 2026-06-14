#!/usr/bin/env python3
"""
T053: Audit the Audit
======================
Verify whether even the "clean" statements from T052
are actually clean. Search for truly clean statements.
"""

import csv, json
from pathlib import Path

ROOT = Path("/home/student/sgp_core_v2")
OUT = ROOT / "sfh_sgp_ood_outputs"

# ============================================================
# SURVIVING CLEAN STATEMENTS FROM T052
# ============================================================

CLEAN_STATEMENTS = {
    "A06": "28 assumptions cataloged",
    "A09": "10/10 candidate substrates tested",
    "A13": "101,414 detector events recorded",
    "A22": "45 detectors cataloged",
}

# ============================================================
# METHODOLOGICAL TERM AUDIT
# ============================================================

METHOD_TERMS = {
    "catalog": {
        "definition": "An organized list of items",
        "requires_identity": True,
        "requires_distinction": True,
        "requires_memory": True,
        "requires_ordering": False,
        "requires_comparison": False,
        "reasoning": "Cataloging requires recognizing items (identity), separating them (distinction), and retaining the list (memory).",
    },
    "count": {
        "definition": "Determination of numerical quantity",
        "requires_identity": True,
        "requires_distinction": True,
        "requires_memory": True,
        "requires_ordering": False,
        "requires_comparison": False,
        "reasoning": "Counting requires distinguishing items (distinction), recognizing repeats (identity), and maintaining tally (memory).",
    },
    "event": {
        "definition": "Something that occurs at a specific time",
        "requires_identity": True,
        "requires_distinction": True,
        "requires_memory": True,
        "requires_ordering": True,
        "requires_comparison": False,
        "reasoning": "Events require temporal placement (ordering), recognition (identity), and separation from non-events (distinction).",
    },
    "test": {
        "definition": "A procedure applied to check a condition",
        "requires_identity": True,
        "requires_distinction": True,
        "requires_memory": True,
        "requires_ordering": True,
        "requires_comparison": True,
        "reasoning": "Testing requires applying a procedure (ordering), checking result (comparison), recognizing the test (identity), and distinguishing pass/fail (distinction).",
    },
    "detector": {
        "definition": "A procedure that produces output from input",
        "requires_identity": True,
        "requires_distinction": True,
        "requires_memory": True,
        "requires_ordering": True,
        "requires_comparison": True,
        "reasoning": "Detectors require all five: input (distinction), processing (ordering), output (comparison), recognition (identity), and state (memory).",
    },
    "record": {
        "definition": "A stored observation",
        "requires_identity": True,
        "requires_distinction": True,
        "requires_memory": True,
        "requires_ordering": False,
        "requires_comparison": False,
        "reasoning": "Recording requires storing (memory), recognizing what is stored (identity), and separating record from non-record (distinction).",
    },
}


# ============================================================
# STATEMENT DEPENDENCY ANALYSIS
# ============================================================

def audit_statement(sid, text):
    """Audit a single statement for dependencies."""
    dependencies = {}

    if "cataloged" in text:
        for term in ["catalog", "count"]:
            if term in METHOD_TERMS:
                info = METHOD_TERMS[term]
                deps = []
                if info["requires_identity"]: deps.append("identity")
                if info["requires_distinction"]: deps.append("distinction")
                if info["requires_memory"]: deps.append("memory")
                if info["requires_ordering"]: deps.append("ordering")
                if info["requires_comparison"]: deps.append("comparison")
                dependencies[term] = deps

    if "tested" in text:
        for term in ["test", "detector"]:
            if term in METHOD_TERMS:
                info = METHOD_TERMS[term]
                deps = []
                if info["requires_identity"]: deps.append("identity")
                if info["requires_distinction"]: deps.append("distinction")
                if info["requires_memory"]: deps.append("memory")
                if info["requires_ordering"]: deps.append("ordering")
                if info["requires_comparison"]: deps.append("comparison")
                dependencies[term] = deps

    if "recorded" in text:
        for term in ["event", "record", "detector"]:
            if term in METHOD_TERMS:
                info = METHOD_TERMS[term]
                deps = []
                if info["requires_identity"]: deps.append("identity")
                if info["requires_distinction"]: deps.append("distinction")
                if info["requires_memory"]: deps.append("memory")
                if info["requires_ordering"]: deps.append("ordering")
                if info["requires_comparison"]: deps.append("comparison")
                dependencies[term] = deps

    if "cataloged" in text and "detectors" in text:
        for term in ["catalog", "detector"]:
            if term in METHOD_TERMS:
                info = METHOD_TERMS[term]
                deps = []
                if info["requires_identity"]: deps.append("identity")
                if info["requires_distinction"]: deps.append("distinction")
                if info["requires_memory"]: deps.append("memory")
                if info["requires_ordering"]: deps.append("ordering")
                if info["requires_comparison"]: deps.append("comparison")
                dependencies[term] = deps

    # Collect all unique dependencies
    all_deps = set()
    for term_deps in dependencies.values():
        all_deps.update(term_deps)

    return dependencies, all_deps


# ============================================================
# NEGATIVE CORE EXTRACTION
# ============================================================

NEGATIVE_STATEMENTS = [
    "Geometry emergence was not demonstrated without detector contamination.",
    "Distinction emergence was not demonstrated without hidden assumptions.",
    "Recurrence was not demonstrated to be non-artifactual.",
    "Convergence was not demonstrated without detector contamination.",
    "No primitive was found that survives full assumption audit.",
    "The dependency graph among primitives contains circular chains.",
    "All 45 detectors import comparison, arithmetic, and distinction.",
    "The gap between model requirements and observation requirements cannot be closed.",
    "No statement from T037-T050 about 'what exists' survived audit.",
    "The only surviving statements are methodological records.",
]


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("T053: AUDIT THE AUDIT")
    print("=" * 70)
    print("Verifying whether even 'clean' statements are truly clean.")
    print("=" * 70)

    # Task 1-2: Audit each clean statement
    print("\n[Task 1-2] Auditing methodology dependencies...\n")
    method_deps = {}
    for name, info in METHOD_TERMS.items():
        deps = []
        if info["requires_identity"]: deps.append("identity")
        if info["requires_distinction"]: deps.append("distinction")
        if info["requires_memory"]: deps.append("memory")
        if info["requires_ordering"]: deps.append("ordering")
        if info["requires_comparison"]: deps.append("comparison")
        method_deps[name] = deps
        print(f"  {name:15s}: requires {deps if deps else 'NOTHING'}")

    # Audit each statement
    print("\n[Task 1-2] Statement dependency audit...\n")
    statement_results = {}
    for sid, text in CLEAN_STATEMENTS.items():
        deps_by_term, all_deps = audit_statement(sid, text)
        statement_results[sid] = {
            "text": text,
            "dependencies_by_term": deps_by_term,
            "all_dependencies": list(all_deps),
            "clean": len(all_deps) == 0,
        }
        status = "CLEAN" if len(all_deps) == 0 else f"DEPENDS ON: {all_deps}"
        print(f"  {sid}: {text}")
        print(f"    → {status}")
        for term, deps in deps_by_term.items():
            if deps:
                print(f"      {term}: {deps}")

    # Task 3: Search for truly clean statement
    print("\n[Task 3] Searching for truly clean statements...\n")
    clean_found = []
    for sid, result in statement_results.items():
        if result["clean"]:
            clean_found.append(sid)

    if clean_found:
        print(f"  Found {len(clean_found)} clean statements: {clean_found}")
    else:
        print("  No clean statements found.")
        print("  All surviving statements depend on imported concepts.")

    # Task 4: Negative core
    print("\n[Task 4] Negative core extraction...\n")
    print("  Negative statements (what was NOT demonstrated):")
    for i, stmt in enumerate(NEGATIVE_STATEMENTS, 1):
        print(f"    N{i:02d}: {stmt}")

    # ============================================================
    # SAVE
    # ============================================================

    print("\n[Saving outputs...]\n")

    # t053_methodology_dependencies.csv
    meth_rows = []
    for name, deps in method_deps.items():
        meth_rows.append({
            "term": name,
            "requires_identity": "identity" in deps,
            "requires_distinction": "distinction" in deps,
            "requires_memory": "memory" in deps,
            "requires_ordering": "ordering" in deps,
            "requires_comparison": "comparison" in deps,
            "total_dependencies": len(deps),
        })
    with open(OUT / "t053_methodology_dependencies.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=meth_rows[0].keys())
        w.writeheader()
        w.writerows(meth_rows)
    print("  Saved t053_methodology_dependencies.csv")

    # t053_methodology_collapse.csv
    collapse_rows = []
    for sid, result in statement_results.items():
        collapse_rows.append({
            "statement_id": sid,
            "text": result["text"],
            "clean": result["clean"],
            "n_dependencies": len(result["all_dependencies"]),
            "dependencies": ", ".join(result["all_dependencies"]) if result["all_dependencies"] else "none",
        })
    with open(OUT / "t053_methodology_collapse.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=collapse_rows[0].keys())
        w.writeheader()
        w.writerows(collapse_rows)
    print("  Saved t053_methodology_collapse.csv")

    # t053_clean_statement_search.csv
    with open(OUT / "t053_clean_statement_search.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["statement_id", "text", "clean"])
        w.writeheader()
        for sid, text in CLEAN_STATEMENTS.items():
            clean = statement_results[sid]["clean"]
            w.writerow({"statement_id": sid, "text": text, "clean": clean})
    print("  Saved t053_clean_statement_search.csv")

    # t053_negative_core.csv
    with open(OUT / "t053_negative_core.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "statement"])
        w.writeheader()
        for i, stmt in enumerate(NEGATIVE_STATEMENTS, 1):
            w.writerow({"id": f"N{i:02d}", "statement": stmt})
    print("  Saved t053_negative_core.csv")

    # t053_summary.json
    summary = {
        "n_clean_statements_found": len(clean_found),
        "clean_statements": clean_found,
        "n_negative_statements": len(NEGATIVE_STATEMENTS),
        "methodology_dependencies": method_deps,
        "statement_audit": {sid: {"clean": r["clean"], "deps": r["all_dependencies"]}
                           for sid, r in statement_results.items()},
        "verdict": "No positive statement survives full audit. Only negative statements remain.",
    }
    with open(OUT / "t053_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("  Saved t053_summary.json")

    # ============================================================
    # FINAL REPORT
    # ============================================================

    print("\n" + "=" * 70)
    print("T053 RESULTS")
    print("=" * 70)

    print(f"\nMethodological terms audited: {len(METHOD_TERMS)}")
    for name, deps in method_deps.items():
        print(f"  {name:15s}: {deps if deps else 'CLEAN'}")

    print(f"\nClean statements found: {len(clean_found)}/4")
    for sid, result in statement_results.items():
        status = "CLEAN" if result["clean"] else f"CONTAMINATED ({result['all_dependencies']})"
        print(f"  {sid}: {result['text']} → {status}")

    print(f"\nNegative core: {len(NEGATIVE_STATEMENTS)} statements")
    for i, stmt in enumerate(NEGATIVE_STATEMENTS, 1):
        print(f"  N{i:02d}: {stmt}")

    print(f"\nFINAL ANSWER:")
    print(f"  No positive statement survives full audit.")
    print(f"  All 'clean' statements from T052 depend on")
    print(f"  imported concepts (identity, distinction, memory).")
    print()
    print(f"  The only surviving statements are negative:")
    print(f"  'X was not demonstrated.'")
    print(f"  'Y remains unresolved.'")
    print(f"  'Z cannot currently be established.'")
    print()
    print(f"  These do not claim existence.")
    print(f"  They claim absence of evidence.")
    print(f"  That is the honest terminus.")
    print("=" * 70)


if __name__ == "__main__":
    main()
