"""
Phase 410: Theorem-Boundary Analysis
Separates provable invariants, empirical regularities,
contingent structures, and irreducible uncertainty regions.
"""

import json, os, csv, math

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ======= ELEMENTS =======
# Each element: (id, name, type, description)
ELEMENTS = [
    # Axioms (3)
    ("A1", "Operator Existence", "Axiom",
     "Operators P, A, N exist and are distinct"),
    ("A2", "Operator Composition", "Axiom",
     "Composite operators defined by sequential application, associative"),
    ("A3", "Depth Dependence", "Axiom",
     "Emergence decreases monotonically with depth"),

    # Invariants (5)
    ("I1", "Bounded Degradation", "Invariant",
     "RSF > 0.80 under all validated perturbation types"),
    ("I2", "Recovery", "Invariant",
     "lim_{d->inf} RSF = 1.0 for decaying perturbations"),
    ("I3", "Sector Order Conservation", "Invariant",
     "Hierarchy preserved across all depths"),
    ("I4", "Operator Composition Invariant", "Invariant",
     "Emergence ratios independent of initial configuration"),
    ("I5", "Null Separation", "Invariant",
     "Signal-to-null ratio > 10x"),

    # Theorem Candidates (11)
    ("T1", "Hierarchy Existence", "Theorem Candidate",
     "P-A-N > P-A > Projection > P-N > Antisymmetry > Neutral > A-N"),
    ("T2", "Hierarchy Depth Invariance", "Theorem Candidate",
     "Ordering preserved across all validated depths"),
    ("T3", "Hierarchy Formalism Invariance", "Theorem Candidate",
     "Ordering preserved across 14 mathematical formalisms"),
    ("T4", "Coherence Stability", "Theorem Candidate",
     "Composite coherence > 0.90 through half-max depth"),
    ("T5", "Perturbation Robustness", "Theorem Candidate",
     "min RSF > 0.83 across 14 perturbation types"),
    ("T6", "Necessity Hierarchy", "Theorem Candidate",
     "ONI(P) > ONI(A) > ONI(N)"),
    ("T7", "Minimal Sufficiency", "Theorem Candidate",
     "{P, A} minimally sufficient, no single operator suffices"),
    ("T8", "Universal Hierarchy Preservation", "Theorem Candidate",
     "HPR = 1.0 across 56/57 tested conditions"),
    ("T9", "Formalism Invariance", "Theorem Candidate",
     "FIS > 0.80 for all major formalisms"),
    ("T10", "Superlinear Efficiency", "Theorem Candidate",
     "CSF(rho) > rho for rho in [0.55, 1.0]"),
    ("T11", "Irreducible Complexity", "Theorem Candidate",
     "rho_min ~ 0.55-0.60 below which CSF < 0.60"),

    # Universality Candidates (3)
    ("U1", "Operator Necessity Universality", "Universality Candidate",
     "P > A > N hierarchy universal for all recursive relational systems"),
    ("U2", "Emergence Sequence Universality", "Universality Candidate",
     "Ordered emergence sequence universal across implementations"),
    ("U3", "Depth Scaling Universality", "Universality Candidate",
     "gamma(d) = 1/(1 + k*(d-1)) universal with k as free parameter"),
]

# ======= ASSESSMENT =======
# Each element evaluated on 6 metrics.
# TDI: theorem_derivability_index [0,1]
# EDS: empirical_dependency_score [0,1]
# UC:  universality_confidence [0,1]
# CD:  contingency_density (count of contingent assumptions)
# URS: undecidability_region_size [0,1]
# PCR: proof_completeness_ratio [0,1]

ASSESSMENTS = {
    # === AXIOMS ===
    # A1: Operator Existence - by definition, self-evident
    "A1": {"TDI": 1.0, "EDS": 0.0, "UC": 1.0, "CD": 0, "URS": 0.0, "PCR": 1.0},
    # A2: Operator Composition - follows from definition of sequential application
    "A2": {"TDI": 1.0, "EDS": 0.0, "UC": 1.0, "CD": 0, "URS": 0.0, "PCR": 1.0},
    # A3: Depth Dependence - axiom, but empirically tested range matters
    "A3": {"TDI": 1.0, "EDS": 0.0, "UC": 1.0, "CD": 0, "URS": 0.0, "PCR": 1.0},

    # === INVARIANTS ===
    # I1: Bounded Degradation - observed across tested perturbations, not provable
    "I1": {"TDI": 0.25, "EDS": 0.85, "UC": 0.35, "CD": 4, "URS": 0.30, "PCR": 0.20},
    # I2: Recovery - observed pattern, depends on perturbation type
    "I2": {"TDI": 0.20, "EDS": 0.80, "UC": 0.30, "CD": 5, "URS": 0.35, "PCR": 0.15},
    # I3: Sector Order Conservation - follows from monotonic depth scaling if
    # sector bases are fixed and depth factor is separable
    "I3": {"TDI": 0.85, "EDS": 0.20, "UC": 0.70, "CD": 1, "URS": 0.05, "PCR": 0.70},
    # I4: Operator Composition Invariant - ratio independence of init config
    # depends on linearity of operators
    "I4": {"TDI": 0.60, "EDS": 0.40, "UC": 0.50, "CD": 2, "URS": 0.15, "PCR": 0.45},
    # I5: Null Separation - depends on operator definitions
    "I5": {"TDI": 0.30, "EDS": 0.75, "UC": 0.40, "CD": 3, "URS": 0.20, "PCR": 0.25},

    # === THEOREM CANDIDATES ===
    # T1: Hierarchy Existence - observed ordering, follows from sector
    # base values which are measured not derived
    "T1": {"TDI": 0.40, "EDS": 0.65, "UC": 0.45, "CD": 2, "URS": 0.10, "PCR": 0.30},
    # T2: Hierarchy Depth Invariance - follows from separable depth factor
    "T2": {"TDI": 0.80, "EDS": 0.25, "UC": 0.65, "CD": 1, "URS": 0.05, "PCR": 0.65},
    # T3: Hierarchy Formalism Invariance - strongly empirical, 14 formalisms
    "T3": {"TDI": 0.35, "EDS": 0.80, "UC": 0.50, "CD": 2, "URS": 0.15, "PCR": 0.25},
    # T4: Coherence Stability - threshold-dependent empirical observation
    "T4": {"TDI": 0.30, "EDS": 0.75, "UC": 0.35, "CD": 3, "URS": 0.20, "PCR": 0.20},
    # T5: Perturbation Robustness - perturbation-specific, highly empirical
    "T5": {"TDI": 0.20, "EDS": 0.85, "UC": 0.30, "CD": 4, "URS": 0.25, "PCR": 0.15},
    # T6: Necessity Hierarchy - P > A > N: partially derivable from
    # operator algebra (P selects, A filters, N neutralizes)
    "T6": {"TDI": 0.55, "EDS": 0.50, "UC": 0.55, "CD": 2, "URS": 0.10, "PCR": 0.40},
    # T7: Minimal Sufficiency - provable: two operators needed because
    # one operator cannot create diversity
    "T7": {"TDI": 0.65, "EDS": 0.40, "UC": 0.60, "CD": 1, "URS": 0.10, "PCR": 0.50},
    # T8: Universal Hierarchy Preservation - strongly empirical
    "T8": {"TDI": 0.25, "EDS": 0.85, "UC": 0.40, "CD": 3, "URS": 0.20, "PCR": 0.20},
    # T9: Formalism Invariance - empirical, 14/14 tested formalisms
    "T9": {"TDI": 0.30, "EDS": 0.80, "UC": 0.45, "CD": 2, "URS": 0.15, "PCR": 0.20},
    # T10: Superlinear Efficiency - depends on specific compression type
    "T10": {"TDI": 0.25, "EDS": 0.80, "UC": 0.30, "CD": 4, "URS": 0.25, "PCR": 0.15},
    # T11: Irreducible Complexity - threshold is empirical
    "T11": {"TDI": 0.20, "EDS": 0.85, "UC": 0.25, "CD": 4, "URS": 0.30, "PCR": 0.10},

    # === UNIVERSALITY CANDIDATES ===
    # U1: Operator Necessity Universality - speculation beyond evidence
    "U1": {"TDI": 0.25, "EDS": 0.75, "UC": 0.35, "CD": 3, "URS": 0.40, "PCR": 0.10},
    # U2: Sequence Universality - speculation, needs much more evidence
    "U2": {"TDI": 0.15, "EDS": 0.85, "UC": 0.25, "CD": 5, "URS": 0.50, "PCR": 0.05},
    # U3: Depth Scaling Universality - partially derivable from
    # recursive composition, k is empirically determined
    "U3": {"TDI": 0.50, "EDS": 0.55, "UC": 0.50, "CD": 2, "URS": 0.20, "PCR": 0.35},
}

# ======= CATEGORIZATION LOGIC =======
def categorize(m):
    tdi, eds = m["TDI"], m["EDS"]
    cd, urs = m["CD"], m["URS"]
    pcr = m["PCR"]

    # PROVABLE: near-proof from axioms, no empirical crutch
    if tdi >= 0.90 and eds <= 0.15:
        return "PROVABLE"

    # CONDITIONAL: provable under specific additional assumptions
    if tdi >= 0.70 and eds <= 0.40:
        return "CONDITIONAL"

    # IRREDUCIBLE: large undecidable region, low proof completeness
    if urs >= 0.40 and pcr <= 0.30:
        return "IRREDUCIBLE"

    # CONTINGENT: high contingency density, heavily empirical
    if cd >= 3 and eds >= 0.60:
        return "CONTINGENT"

    # EMPIRICAL: not provable, heavily evidence-dependent
    if eds >= 0.50 and tdi < 0.70:
        return "EMPIRICAL"

    # Fallback for mixed profiles
    if eds >= 0.40:
        return "EMPIRICAL"
    return "CONDITIONAL"


# ======= COMPUTE =======
print("=" * 60)
print("PHASE 410: THEOREM-BOUNDARY ANALYSIS")
print("=" * 60)
print(f"\nAnalyzing {len(ELEMENTS)} formal elements across 6 metrics\n")

results = {}
category_counts = {}

for eid, name, etype, desc in ELEMENTS:
    m = ASSESSMENTS[eid]
    cat = categorize(m)
    category_counts[cat] = category_counts.get(cat, 0) + 1

    results[eid] = {
        "name": name,
        "type": etype,
        "description": desc,
        "metrics": {
            "theorem_derivability_index": round(m["TDI"], 2),
            "empirical_dependency_score": round(m["EDS"], 2),
            "universality_confidence": round(m["UC"], 2),
            "contingency_density": m["CD"],
            "undecidability_region_size": round(m["URS"], 2),
            "proof_completeness_ratio": round(m["PCR"], 2)
        },
        "category": cat
    }

    print(f"  {eid:4s} {name:40s} {cat:15s} TDI={m['TDI']:.2f} EDS={m['EDS']:.2f} CD={m['CD']} URS={m['URS']:.2f}")

# ======= SUMMARY =======
print(f"\n{'='*60}")
print("CATEGORY DISTRIBUTION")
print(f"{'='*60}")
for cat in ["PROVABLE", "CONDITIONAL", "EMPIRICAL", "CONTINGENT", "IRREDUCIBLE"]:
    count = category_counts.get(cat, 0)
    pct = count / len(ELEMENTS) * 100
    print(f"  {cat:15s}: {count:2d} / {len(ELEMENTS)} ({pct:.1f}%)")

# ======= COMPOSITE METRICS =======
all_tdi = [ASSESSMENTS[e[0]]["TDI"] for e in ELEMENTS]
all_eds = [ASSESSMENTS[e[0]]["EDS"] for e in ELEMENTS]
all_uc  = [ASSESSMENTS[e[0]]["UC"] for e in ELEMENTS]
all_cd  = [ASSESSMENTS[e[0]]["CD"] for e in ELEMENTS]
all_urs = [ASSESSMENTS[e[0]]["URS"] for e in ELEMENTS]
all_pcr = [ASSESSMENTS[e[0]]["PCR"] for e in ELEMENTS]

composite = {
    "mean_theorem_derivability_index": round(sum(all_tdi) / len(all_tdi), 2),
    "mean_empirical_dependency_score": round(sum(all_eds) / len(all_eds), 2),
    "mean_universality_confidence": round(sum(all_uc) / len(all_uc), 2),
    "mean_contingency_density": round(sum(all_cd) / len(all_cd), 2),
    "mean_undecidability_region_size": round(sum(all_urs) / len(all_urs), 2),
    "mean_proof_completeness_ratio": round(sum(all_pcr) / len(all_pcr), 2),
    "provable_fraction": round(category_counts.get("PROVABLE", 0) / len(ELEMENTS), 2),
    "empirical_fraction": round((category_counts.get("EMPIRICAL", 0) + category_counts.get("CONTINGENT", 0)) / len(ELEMENTS), 2),
    "irreducible_fraction": round(category_counts.get("IRREDUCIBLE", 0) / len(ELEMENTS), 2)
}

print(f"\n{'='*60}")
print("COMPOSITE METRICS")
print(f"{'='*60}")
for k, v in composite.items():
    print(f"  {k:40s}: {v}")

# ======= HYPOTHESIS EVALUATION =======
provable_count = category_counts.get("PROVABLE", 0)
empirical_count = category_counts.get("EMPIRICAL", 0) + category_counts.get("CONTINGENT", 0)
irreducible_count = category_counts.get("IRREDUCIBLE", 0)

# H1: Certain emergence invariants are formally derivable
# -> At minimum the axioms themselves are provable. Check if any non-axiom
# elements (invariants or theorem candidates) are provable or conditional.
non_axiom_provable = sum(1 for e in ELEMENTS if e[2] != "Axiom"
                         and results[e[0]]["category"] in ("PROVABLE", "CONDITIONAL"))
h1_pass = non_axiom_provable >= 3

# H2: Some Tier 1 structures are empirical but non-universal
h2_pass = empirical_count >= 5

# H3: Predictive ceilings arise from theorem-level constraints
# -> Check if irreducible elements exist (they set prediction limits)
h3_pass = irreducible_count >= 1

# H4: Formal undecidability regions exist within recursive space
# -> Check if any element has URS >= 0.30 (non-trivial undecidable region)
undecidable_count = sum(1 for e in ELEMENTS if ASSESSMENTS[e[0]]["URS"] >= 0.30)
h4_pass = undecidable_count >= 3

# H5: Necessary and contingent emergence structures are separable
# -> We must have both provable/conditional AND contingent categories
# with clear separation
provable_or_cond = category_counts.get("PROVABLE", 0) + category_counts.get("CONDITIONAL", 0)
contingent_or_emp = category_counts.get("CONTINGENT", 0) + category_counts.get("EMPIRICAL", 0)
h5_pass = provable_or_cond >= 3 and contingent_or_emp >= 5

hypotheses = {
    "H1_FormallyDerivableInvariants": {
        "description": "Certain emergence invariants are formally derivable",
        "condition": f"Non-axiom provable/conditional elements >= 3",
        "value": non_axiom_provable,
        "threshold": 3,
        "pass": h1_pass
    },
    "H2_EmpiricalNonUniversal": {
        "description": "Some Tier 1 structures are empirical but non-universal",
        "condition": f"Empirical/contingent elements >= 5",
        "value": empirical_count,
        "threshold": 5,
        "pass": h2_pass
    },
    "H3_PredictiveCeilingsTheoremLevel": {
        "description": "Predictive ceilings arise from theorem-level constraints",
        "condition": f"Irreducible elements >= 1",
        "value": irreducible_count,
        "threshold": 1,
        "pass": h3_pass
    },
    "H4_UndecidabilityRegionsExist": {
        "description": "Formal undecidability regions exist within recursive emergence",
        "condition": f"Elements with URS >= 0.30 >= 3",
        "value": undecidable_count,
        "threshold": 3,
        "pass": h4_pass
    },
    "H5_NecessaryContingentSeparable": {
        "description": "Necessary and contingent structures are separable",
        "condition": f"Provable/conditional >= 3 AND contingent/empirical >= 5",
        "value": {"provable_or_conditional": provable_or_cond, "contingent_or_empirical": contingent_or_emp},
        "threshold": {"provable_or_conditional": 3, "contingent_or_empirical": 5},
        "pass": h5_pass
    }
}

passes = sum(1 for h in hypotheses.values() if h["pass"])
verdict_map = {5: "THEOREM-BOUNDARY-STABLE", 4: "THEOREM-BOUNDARY-BOUNDED",
               3: "THEOREM-BOUNDARY-DEGRADING", 2: "THEOREM-BOUNDARY-FAILED",
               1: "THEOREM-BOUNDARY-FAILED", 0: "THEOREM-BOUNDARY-FAILED"}
verdict = verdict_map[passes]

print(f"\n{'='*60}")
print("HYPOTHESIS EVALUATION")
print(f"{'='*60}")
for h_name, h_data in hypotheses.items():
    s = "PASS" if h_data["pass"] else "FAIL"
    print(f"  {h_name}: {h_data['value']} vs {h_data['condition']} -> {s}")

print(f"\n{'='*60}")
print(f"PHASE 410 VERDICT: {verdict}")
print(f"Hypotheses: {passes}/5 PASS")
print(f"{'='*60}")

# ======= SAVE =======
output = {
    "phase": 410,
    "name": "THEOREM-BOUNDARY",
    "elements_analyzed": len(ELEMENTS),
    "results": results,
    "category_distribution": category_counts,
    "composite_metrics": composite,
    "hypotheses": {k: {sk: sv for sk, sv in v.items() if sk != "description"} for k, v in hypotheses.items()},
    "pass_count": passes,
    "total_hypotheses": 5,
    "verdict": verdict
}

results_path = os.path.join(SCRIPT_DIR, "phase410_results.json")
with open(results_path, "w") as f:
    json.dump(output, f, indent=2)
print(f"\nResults: {results_path}")

# CSV: per-element detail
csv_path = os.path.join(SCRIPT_DIR, "phase410_per_element.csv")
with open(csv_path, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id", "name", "type", "category",
                "TDI", "EDS", "UC", "CD", "URS", "PCR"])
    for eid, name, etype, desc in ELEMENTS:
        m = ASSESSMENTS[eid]
        cat = results[eid]["category"]
        w.writerow([eid, name, etype, cat,
                    m["TDI"], m["EDS"], m["UC"], m["CD"], m["URS"], m["PCR"]])
print(f"Per-element CSV: {csv_path}")

# CSV: hypothesis detail
csv2_path = os.path.join(SCRIPT_DIR, "phase410_hypotheses.csv")
with open(csv2_path, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["hypothesis", "condition", "value", "threshold", "pass"])
    for h_name, h_data in hypotheses.items():
        w.writerow([h_name, h_data["condition"],
                    str(h_data["value"]), str(h_data["threshold"]),
                    "PASS" if h_data["pass"] else "FAIL"])
print(f"Hypothesis CSV: {csv2_path}")
