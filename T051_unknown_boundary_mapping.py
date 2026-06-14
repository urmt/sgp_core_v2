#!/usr/bin/env python3
"""
T051: Unknown Boundary Mapping
================================
Classify every statement from T037-T050 into epistemic categories.
No computation. Pure classification.
"""

import csv, json
from pathlib import Path

ROOT = Path("/home/student/sgp_core_v2")
OUT = ROOT / "sfh_sgp_ood_outputs"

# ============================================================
# COMPLETE STATEMENT INVENTORY
# ============================================================
# Categories:
#   A = Directly demonstrated by procedure
#   B = Inference from demonstrated results
#   C = Model-dependent statement
#   D = Underdetermined statement
#   E = Ontology claim

STATEMENTS = [
    # === T037 ===
    {"phase": "T037", "statement": "Geometry score = 0.69 across 1200 universes",
     "category": "A", "confidence": "high",
     "evidence": "Direct measurement from detector output."},
    {"phase": "T037", "statement": "Composition score = 0.0 across all universes",
     "category": "A", "confidence": "high",
     "evidence": "Direct measurement from detector output."},
    {"phase": "T037", "statement": "Recurrence detected in 98.3% of universes",
     "category": "A", "confidence": "high",
     "evidence": "Direct measurement from detector output."},
    {"phase": "T037", "statement": "Geometry emerges from interaction",
     "category": "D", "confidence": "low",
     "evidence": "Detector artifact identified in T044."},
    {"phase": "T037", "statement": "Distinction requires no prerequisites",
     "category": "D", "confidence": "low",
     "evidence": "Contradicted by T038/T039 circular dependency analysis."},

    # === T038 ===
    {"phase": "T038", "statement": "Distinction emerged in 995/1000 universes",
     "category": "A", "confidence": "high",
     "evidence": "Direct measurement from detector output."},
    {"phase": "T038", "statement": "Persistence emerged in 0/1000 universes",
     "category": "A", "confidence": "high",
     "evidence": "Direct measurement from detector output."},
    {"phase": "T038", "statement": "Distinction can emerge from pure Ω",
     "category": "D", "confidence": "low",
     "evidence": "Detector smuggled distinction (T039 audit)."},

    # === T039 ===
    {"phase": "T039", "statement": "28 assumptions cataloged",
     "category": "A", "confidence": "high",
     "evidence": "Direct enumeration of conceptual inventory."},
    {"phase": "T039", "statement": "34 dependency edges identified",
     "category": "A", "confidence": "high",
     "evidence": "Direct graph construction from specification."},
    {"phase": "T039", "statement": "12 circular dependency chains found",
     "category": "A", "confidence": "high",
     "evidence": "Direct graph analysis."},
    {"phase": "T039", "statement": "Distinction is foundational",
     "category": "E", "confidence": "low",
     "evidence": "Based on authored dependency graph, not measured. T048 shows graph was specified, not discovered."},
    {"phase": "T039", "statement": "Distinction cannot be produced from non-distinction",
     "category": "C", "confidence": "medium",
     "evidence": "True within the authored dependency graph, but graph may be incomplete."},

    # === T040 ===
    {"phase": "T040", "statement": "10/10 candidate substrates failed",
     "category": "A", "confidence": "high",
     "evidence": "Direct test of each candidate."},
    {"phase": "T040", "statement": "Every candidate reintroduces distinction",
     "category": "B", "confidence": "medium",
     "evidence": "Inference from 10 test failures. May miss candidates not tested."},
    {"phase": "T040", "statement": "Nothing exists below distinction",
     "category": "D", "confidence": "low",
     "evidence": "Only 10 candidates tested. Universe of possible candidates is larger."},

    # === T041 ===
    {"phase": "T041", "statement": "0/5000 universes produce distinction",
     "category": "A", "confidence": "high",
     "evidence": "Direct measurement with strict 4-criterion detector."},
    {"phase": "T041", "statement": "Distinction never emerges from interaction",
     "category": "B", "confidence": "medium",
     "evidence": "Inference from 5000-universe sample. Detector assumptions may contaminate."},
    {"phase": "T041", "statement": "Proto-geometry emerges in 85.8% of universes",
     "category": "A", "confidence": "high",
     "evidence": "Direct measurement, but detector may be artifact (T044)."},

    # === T042 ===
    {"phase": "T042", "statement": "Trajectory bundles appear in 64.7% of universes",
     "category": "A", "confidence": "high",
     "evidence": "Direct measurement with proximity detectors."},
    {"phase": "T042", "statement": "Proximity precedes distinction",
     "category": "B", "confidence": "medium",
     "evidence": "Inferred from timing of detector firings. Detectors may be contaminated."},
    {"phase": "T042", "statement": "The first stable structure is trajectory bundles",
     "category": "D", "confidence": "low",
     "evidence": "Based on contaminated detectors (T047 audit)."},

    # === T043 ===
    {"phase": "T043", "statement": "101,414 detector events recorded",
     "category": "A", "confidence": "high",
     "evidence": "Direct measurement from 10,000 universes."},
    {"phase": "T043", "statement": "Recurrence fires first (98.3%)",
     "category": "A", "confidence": "high",
     "evidence": "Direct measurement with specific detector."},
    {"phase": "T043", "statement": "73 edges in emergence graph (P>0.95)",
     "category": "A", "confidence": "high",
     "evidence": "Direct computation from pairwise order probabilities."},
    {"phase": "T043", "statement": "Recurrence is the first emergent structure",
     "category": "D", "confidence": "low",
     "evidence": "KILLED in T044 (artifact of boundedness)."},

    # === T044 ===
    {"phase": "T044", "statement": "Recurrence kills in recursive vs nonrecursive test",
     "category": "A", "confidence": "high",
     "evidence": "Direct comparison with effect size and permutation test."},
    {"phase": "T044", "statement": "Recurrence is an artifact of bounded state spaces",
     "category": "B", "confidence": "medium",
     "evidence": "Inference from T044 test D (effect=0, p=1.0)."},

    # === T045 ===
    {"phase": "T045", "statement": "Convergence rate = 0.995 in real universes",
     "category": "A", "confidence": "high",
     "evidence": "Direct measurement with 5 independent detectors."},
    {"phase": "T045", "statement": "Convergence beats all null models (14× effect)",
     "category": "A", "confidence": "high",
     "evidence": "Direct comparison with random walk, Brownian, OU models."},
    {"phase": "T045", "statement": "Convergence survives temporal shuffling",
     "category": "A", "confidence": "high",
     "evidence": "Direct comparison with shuffled trajectories."},
    {"phase": "T045", "statement": "Convergence is genuine",
     "category": "D", "confidence": "low",
     "evidence": "Detector assumes distance, arithmetic, comparison (T047 audit)."},

    # === T046 ===
    {"phase": "T046", "statement": "Convergence before constraint (7/8 detectors)",
     "category": "A", "confidence": "high",
     "evidence": "Direct pairwise order computation."},
    {"phase": "T046", "statement": "Convergence is fundamental",
     "category": "D", "confidence": "low",
     "evidence": "Detector assumptions contaminate (T047 audit)."},

    # === T047 ===
    {"phase": "T047", "statement": "All detectors smuggle hidden primitives",
     "category": "A", "confidence": "high",
     "evidence": "Direct audit of detector implementations."},
    {"phase": "T047", "statement": "No primitive is currently accepted",
     "category": "B", "confidence": "high",
     "evidence": "Inference from universal contamination of detectors."},

    # === T048 ===
    {"phase": "T048", "statement": "45 detectors cataloged",
     "category": "A", "confidence": "high",
     "evidence": "Direct inventory."},
    {"phase": "T048", "statement": "63 dependency edges identified",
     "category": "A", "confidence": "high",
     "evidence": "Direct graph construction."},
    {"phase": "T048", "statement": "Every detector imports comparison, arithmetic, distance",
     "category": "A", "confidence": "high",
     "evidence": "Direct audit of all 45 detector implementations."},
    {"phase": "T048", "statement": "Distance is the deepest imported primitive",
     "category": "C", "confidence": "medium",
     "evidence": "Based on authored prerequisite graph. Graph may be incomplete."},
    {"phase": "T048", "statement": "No detector can discover distinction",
     "category": "B", "confidence": "medium",
     "evidence": "Inference from contamination analysis. True within current detector families."},

    # === T049 ===
    {"phase": "T049", "statement": "Observation fails when comparison is removed",
     "category": "C", "confidence": "medium",
     "evidence": "True for observer MODELS, not proven for observation itself."},
    {"phase": "T049", "statement": "Observation fails when ordering is removed",
     "category": "C", "confidence": "medium",
     "evidence": "True for observer MODELS, not proven for observation itself."},
    {"phase": "T049", "statement": "Observation fails when identity is removed",
     "category": "C", "confidence": "medium",
     "evidence": "True for observer MODELS, not proven for observation itself."},
    {"phase": "T049", "statement": "Observation fails when difference is removed",
     "category": "C", "confidence": "medium",
     "evidence": "True for observer MODELS, not proven for observation itself."},
    {"phase": "T049", "statement": "Observation fails when distinction is removed",
     "category": "C", "confidence": "medium",
     "evidence": "True for observer MODELS, not proven for observation itself."},
    {"phase": "T049", "statement": "All five primitives are necessary for observation",
     "category": "D", "confidence": "low",
     "evidence": "Only proven for models, not for observation itself (T050 correction)."},

    # === T050 ===
    {"phase": "T050", "statement": "All 5 primitives are proven necessary for observer models",
     "category": "A", "confidence": "high",
     "evidence": "Direct proof from T049 model analysis."},
    {"phase": "T050", "statement": "No primitive is proven necessary for observation itself",
     "category": "A", "confidence": "high",
     "evidence": "Direct proof from T050 separation analysis."},
    {"phase": "T050", "statement": "The gap between model requirements and observation requirements cannot be closed",
     "category": "B", "confidence": "high",
     "evidence": "Inference from T050 separation analysis."},
    {"phase": "T050", "statement": "We know what models need but not what observation needs",
     "category": "B", "confidence": "high",
     "evidence": "Direct conclusion from T050 proof inventory."},
]


# ============================================================
# EVIDENCE REQUIREMENTS FOR CATEGORY D
# ============================================================

D_EVIDENCE = {
    "Distinction can emerge from pure Ω": {
        "to_C": "A detector that does not import distinction successfully detects it.",
        "to_B": "Multiple independent assumption-free detectors agree on distinction emergence.",
    },
    "The first stable structure is trajectory bundles": {
        "to_C": "Assumption-free detectors confirm trajectory bundles as first structure.",
        "to_B": "Multiple independent detector families agree on trajectory bundles.",
    },
    "Recurrence is the first emergent structure": {
        "to_C": "Recurrence survives all audits with clean detectors.",
        "to_B": "Recurrence is confirmed by multiple independent detector families.",
    },
    "Convergence is genuine": {
        "to_C": "Convergence detectors pass full assumption audit.",
        "to_B": "Convergence is confirmed by assumption-free detectors.",
    },
    "Convergence is fundamental": {
        "to_C": "Convergence appears without any imported primitives.",
        "to_B": "Convergence is confirmed by assumption-free detectors and beats all nulls.",
    },
    "Nothing exists below distinction": {
        "to_C": "Exhaustive search of all possible substrates.",
        "to_B": "Strong evidence from diverse candidate tests.",
    },
    "All five primitives are necessary for observation": {
        "to_C": "Observation is proven to require each primitive (not just models).",
        "to_B": "Strong evidence from diverse observation scenarios.",
    },
}


# ============================================================
# EVIDENCE REQUIREMENTS FOR CATEGORY E
# ============================================================

E_TESTABILITY = {
    "Distinction is fundamental reality": {
        "testable": "Untestable",
        "reason": "Ontology claim about fundamental reality. No empirical test can confirm or deny.",
    },
}


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("T051: UNKNOWN BOUNDARY MAPPING")
    print("=" * 70)
    print("Classifying all statements from T037-T050.")
    print("=" * 70)

    # Category counts
    cats = {}
    for s in STATEMENTS:
        cats.setdefault(s["category"], []).append(s)

    print(f"\nTotal statements: {len(STATEMENTS)}")
    for cat in ["A", "B", "C", "D", "E"]:
        count = len(cats.get(cat, []))
        print(f"  Category {cat}: {count}")

    # Save category files
    category_names = {
        "A": "Directly demonstrated by procedure",
        "B": "Inference from demonstrated results",
        "C": "Model-dependent statement",
        "D": "Underdetermined statement",
        "E": "Ontology claim",
    }

    for cat in ["A", "B", "C", "D", "E"]:
        stmts = cats.get(cat, [])
        with open(OUT / f"t051_category_{cat.lower()}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["phase", "statement", "confidence", "evidence"])
            w.writeheader()
            for s in stmts:
                w.writerow({k: s[k] for k in ["phase", "statement", "confidence", "evidence"]})
        print(f"  Saved t051_category_{cat.lower()}.csv ({len(stmts)} statements)")

    # Full inventory
    with open(OUT / "t051_statement_inventory.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["phase", "statement", "category", "confidence", "evidence"])
        w.writeheader()
        for s in STATEMENTS:
            w.writerow(s)
    print("  Saved t051_statement_inventory.csv")

    # Confidence audit
    confidence_rows = []
    for s in STATEMENTS:
        confidence_rows.append({
            "phase": s["phase"],
            "statement": s["statement"][:60],
            "category": s["category"],
            "confidence": s["confidence"],
        })
    with open(OUT / "t051_confidence_audit.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["phase", "statement", "category", "confidence"])
        w.writeheader()
        w.writerows(confidence_rows)
    print("  Saved t051_confidence_audit.csv")

    # Summary
    summary = {
        "total_statements": len(STATEMENTS),
        "by_category": {cat: len(stmts) for cat, stmts in cats.items()},
        "category_definitions": category_names,
        "key_findings": {
            "A_statements": "All are direct measurements or procedures.",
            "B_statements": "Inferences from measurements. May be contaminated.",
            "C_statements": "True for models, not proven for observation.",
            "D_statements": "Underdetermined. Cannot be resolved with current evidence.",
            "E_statements": "Ontology claims. Untestable.",
        },
        "boundary_map": {
            "KNOWN": f"{len(cats.get('A', []))} statements directly demonstrated",
            "INFERRED": f"{len(cats.get('B', []))} statements inferred from demonstrations",
            "MODEL_DEPENDENT": f"{len(cats.get('C', []))} statements true only for models",
            "UNDERDETERMINED": f"{len(cats.get('D', []))} statements that cannot be resolved",
            "ONTOLOGICAL": f"{len(cats.get('E', []))} statements that are untestable",
        },
        "evidence_requirements": D_EVIDENCE,
    }
    with open(OUT / "t051_summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print("  Saved t051_summary.json")

    # ============================================================
    # FINAL REPORT
    # ============================================================

    print("\n" + "=" * 70)
    print("T051 RESULTS: UNKNOWN BOUNDARY MAP")
    print("=" * 70)

    print(f"\nTotal statements classified: {len(STATEMENTS)}")

    print(f"\nKNOWN (Category A): {len(cats.get('A', []))}")
    for s in cats.get("A", []):
        print(f"  [{s['phase']}] {s['statement'][:70]}")

    print(f"\nINFERRED (Category B): {len(cats.get('B', []))}")
    for s in cats.get("B", []):
        print(f"  [{s['phase']}] {s['statement'][:70]}")

    print(f"\nMODEL-DEPENDENT (Category C): {len(cats.get('C', []))}")
    for s in cats.get("C", []):
        print(f"  [{s['phase']}] {s['statement'][:70]}")

    print(f"\nUNDERDETERMINED (Category D): {len(cats.get('D', []))}")
    for s in cats.get("D", []):
        print(f"  [{s['phase']}] {s['statement'][:70]}")

    print(f"\nONTOLOGICAL (Category E): {len(cats.get('E', []))}")
    for s in cats.get("E", []):
        print(f"  [{s['phase']}] {s['statement'][:70]}")

    print(f"\nEVIDENCE NEEDED TO UPGRADE Category D → C or B:")
    for stmt, req in D_EVIDENCE.items():
        print(f"  {stmt[:50]}...")
        print(f"    To C: {req['to_C'][:70]}")
        print(f"    To B: {req['to_B'][:70]}")
        print()

    print("=" * 70)


if __name__ == "__main__":
    main()
