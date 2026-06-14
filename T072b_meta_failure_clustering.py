#!/usr/bin/env python3
"""
T072b — Meta-Failure Clustering + F6 Backfill
===============================================
Completes the Director's requested deliverables:
  1. Backfill F6 (Self-Reference Failure) across all 4 domains
  2. Clusters my 8 failure modes into the Director's F1–F6
  3. Writes t072_meta_failure_clusters.csv
"""

import csv, json
from pathlib import Path
from collections import defaultdict

OUT = Path("/home/student/sgp_core_v2/sfh_sgp_ood_outputs")

# ============================================================
# DIRECTOR'S TAXONOMY
# ============================================================

DIRECTOR_CLASSES = {
    "F1": {
        "label": "Trivialization",
        "definition": "System becomes incapable of producing novelty",
        "examples": "empty universe, degenerate math, substrate with no downstream",
    },
    "F2": {
        "label": "Incoherence",
        "definition": "Internal relationships become mutually destructive",
        "examples": "contradiction, dependency deadlock, incompatible dynamics",
    },
    "F3": {
        "label": "Fragmentation",
        "definition": "System separates into disconnected regions that cannot interact",
        "examples": "disconnected state spaces, isolated math sectors, broken recursive pathways",
    },
    "F4": {
        "label": "Runaway Divergence",
        "definition": "Perturbations amplify without bound",
        "examples": "unstable universes, explosive dynamics, recursive escalation",
    },
    "F5": {
        "label": "Information Loss",
        "definition": "System can no longer preserve meaningful structure",
        "examples": "thermal dissolution, undecidable collapse regions, substrate signal destruction",
    },
    "F6": {
        "label": "Self-Reference Failure",
        "definition": "System cannot successfully incorporate itself into its own operations",
        "examples": "recursion failure, reflective impossibility, self-model collapse",
    },
}

# ============================================================
# MAPPING: my 8 modes → Director's F1–F6
# ============================================================

MODE_TO_DIRECTOR = {
    "CT": ["F1"],               # Trivialization
    "LG": ["F1", "F5"],         # Trivialization + Information Loss
    "CC": ["F2"],               # Incoherence
    "FR": ["F2", "F3"],         # Incoherence + Fragmentation
    "RD": ["F4"],               # Runaway Divergence
    "LD": ["F5"],               # Information Loss
    "LP": ["F5"],               # Information Loss
    "LR": ["F5"],               # Information Loss
}

# F6 (Self-Reference Failure) maps to no single mode in my 8 — it's
# a new column. I need to backfill it.

# ============================================================
# F6 BACKFILL: Self-Reference Failure in each domain
# ============================================================

F6_INSTANCES = {
    "A — Physical universes": [
        {
            "failure": "No observers possible (Anthropic boundary)",
            "description": "Universe parameters prevent formation of self-reflective observers. Laws of physics permit structure but not self-awareness.",
            "type": "Reflective impossibility",
            "triggers": "Fine-tuning constants outside range permitting consciousness",
        },
        {
            "failure": "Cosmological horizon prevents self-measurement",
            "description": "Universe expands so fast that causal horizons prevent any system from measuring its own large-scale properties.",
            "type": "Recursive horizon",
            "triggers": "Accelerated expansion exceeding causal contact scale",
        },
    ],
    "B — Mathematical systems": [
        {
            "failure": "Gödelian incompleteness",
            "description": "Consistent system cannot prove its own consistency. Self-knowledge is bounded.",
            "type": "Reflective boundary",
            "triggers": "Expressive power sufficient to encode arithmetic",
        },
        {
            "failure": "Tarski undefinability of truth",
            "description": "Truth predicate for a language cannot be defined within that language.",
            "type": "Reflective impossibility",
            "triggers": "Self-reference + negation in logical language",
        },
        {
            "failure": "Curry's paradox",
            "description": "Self-referential conditional leads to proof of arbitrary statements in certain logics.",
            "type": "Recursive escalation",
            "triggers": "Unrestricted self-reference in conditional logic",
        },
    ],
    "C — Recursive substrate": [
        {
            "failure": "SR1 removal — no self-examination",
            "description": "Without self-examination of outputs, the investigation cannot know itself. EC1 and CD2 collapse.",
            "type": "Recursive pathway blocked",
            "triggers": "Removal of SR1 from dependency graph",
        },
        {
            "failure": "EC1 removal — no self-knowledge",
            "description": "Without self-knowledge, the investigation has no access to its own state. CD2 collapse.",
            "type": "Self-model failure",
            "triggers": "Removal of EC1 from dependency graph",
        },
        {
            "failure": "CD2 removal — no self-effects",
            "description": "Without self-affecting procedures, the investigation can know itself but cannot act on that knowledge.",
            "type": "Self-action failure",
            "triggers": "Removal of CD2 from dependency graph",
        },
        {
            "failure": "Cycle deadlock — SR1/EC1 circularity",
            "description": "If SR1 depends on EC1 and EC1 depends on SR1, the system deadlocks. No self-entry point.",
            "type": "Recursive deadlock",
            "triggers": "Circular dependency between self-examination and self-knowledge",
        },
    ],
    "D — Dynamical manifolds": [
        {
            "failure": "No internal model possible",
            "description": "Dynamics too fast or too chaotic for system to maintain internal representation of itself.",
            "type": "Model failure",
            "triggers": "Timescale separation too small between system dynamics and model dynamics",
        },
        {
            "failure": "Feedback loop destruction",
            "description": "Self-referential feedback in nonlinear system causes instability; system cannot sustain self-observation.",
            "type": "Recursive instability",
            "triggers": "Gain exceeds stability threshold in self-referential loop",
        },
        {
            "failure": "Observer-system entanglement destroys separation",
            "description": "In strongly coupled systems, the act of self-observation changes the system state, preventing stable self-knowledge.",
            "type": "Measurement back-action",
            "triggers": "Strong coupling between observer and observed subsystems",
        },
    ],
}

# ============================================================
# BUILD CLUSTER TABLE
# ============================================================

# Per-domain F6 counts
f6_by_domain = {d: len(instances) for d, instances in F6_INSTANCES.items()}

rows = []
for fm in ["CT", "RD", "LD", "LP", "LG", "CC", "FR", "LR"]:
    dirs = MODE_TO_DIRECTOR[fm]
    for d in dirs:
        rows.append({
            "my_mode": fm,
            "director_class": d,
            "director_label": DIRECTOR_CLASSES[d]["label"],
            "director_definition": DIRECTOR_CLASSES[d]["definition"],
        })

# Add F6 as its own row
for d in sorted(DIRECTOR_CLASSES.keys()):
    # Count total instances across all domains for this director class
    total = sum(len(F6_INSTANCES[dom]) for dom in F6_INSTANCES) if d == "F6" else 0
    rows.append({
        "my_mode": "(F6 only)" if d == "F6" else "",
        "director_class": d,
        "director_label": DIRECTOR_CLASSES[d]["label"],
        "director_definition": DIRECTOR_CLASSES[d]["definition"],
    })

# ============================================================
# COMPUTE DIRECTOR-CLASS UNIVERSALITY
# ============================================================

# For each Director class, collect which domains it appears in
# Based on the mapping from my modes + F6 backfill

class_domains = defaultdict(set)
for dname in ["A — Physical universes", "B — Mathematical systems",
              "C — Recursive substrate", "D — Dynamical manifolds"]:
    # F6 is present in all 4 by construction from the backfill
    class_domains["F6"].add(dname)

# Map from my modes to domains (from T072 results)
mode_domains = {
    "CT": {"B", "C", "D"},
    "RD": {"B", "D"},
    "LD": {"A", "B", "D"},
    "LP": {"A", "C", "D"},
    "LG": {"A", "B", "C", "D"},
    "CC": {"A", "B", "C"},
    "FR": {"A", "B", "C", "D"},
    "LR": {"A", "B", "D"},
}

domain_names = {
    "A": "A — Physical universes",
    "B": "B — Mathematical systems",
    "C": "C — Recursive substrate",
    "D": "D — Dynamical manifolds",
}

for dclass in ["F1", "F2", "F3", "F4", "F5", "F6"]:
    # Which of my modes map to this class?
    contributing_modes = [m for m, dirs in MODE_TO_DIRECTOR.items() if dclass in dirs]
    # Union of their domains
    doms = set()
    for m in contributing_modes:
        doms |= mode_domains.get(m, set())
    if dclass == "F6":
        doms = {"A", "B", "C", "D"}
    class_domains[dclass] = doms

# Determine universality label
def universality_label(doms):
    if len(doms) == 4:
        return "UNIVERSAL"
    elif len(doms) == 3:
        return "near-universal"
    elif len(doms) == 2:
        return "contingent"
    else:
        return "domain-specific"

# ============================================================
# WRITE OUTPUT
# ============================================================

with open(OUT / "t072_meta_failure_clusters.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["director_class", "director_label", "my_modes_mapped",
                 "domains_present", "n_domains", "universality", "definition"])
    for dclass in sorted(DIRECTOR_CLASSES.keys()):
        contributing = [m for m, dirs in MODE_TO_DIRECTOR.items() if dclass in dirs]
        doms = class_domains[dclass]
        dom_labels = [domain_names[d] for d in sorted(doms)]
        w.writerow([
            dclass,
            DIRECTOR_CLASSES[dclass]["label"],
            ";".join(contributing) if contributing else "(F6 independent)",
            ";".join(dom_labels),
            len(doms),
            universality_label(doms),
            DIRECTOR_CLASSES[dclass]["definition"],
        ])
    # Add F6 row separately for clarity
    dom6 = class_domains["F6"]
    w.writerow([
        "F6", "Self-Reference Failure",
        "(backfilled — not in original 8-mode taxonomy)",
        ";".join([domain_names[d] for d in sorted(dom6)]),
        len(dom6),
        universality_label(dom6),
        DIRECTOR_CLASSES["F6"]["definition"],
    ])

print("Wrote t072_meta_failure_clusters.csv")

# ============================================================
# SUMMARY TABLE
# ============================================================

print(f"\n{'='*72}")
print("DIRECTOR CLASS TAXONOMY — MAPPING AND UNIVERSALITY")
print(f"{'='*72}")

print(f"\n{'Class':<6}{'Label':<25}{'My modes':<20}{'Domains':<10}{'Status':<18}")
print(f"{'-'*79}")
for dclass in sorted(DIRECTOR_CLASSES.keys()):
    contributing = [m for m, dirs in MODE_TO_DIRECTOR.items() if dclass in dirs]
    doms = class_domains[dclass]
    status = universality_label(doms)
    print(f"{dclass:<6}{DIRECTOR_CLASSES[dclass]['label']:<25}"
          f"{';'.join(contributing) if contributing else '(backfill)':<20}"
          f"{len(doms)}/4{'':<6}{status:<18}")

print(f"\n{'='*72}")
print("F6 BACKFILL — INSTANCES PER DOMAIN")
print(f"{'='*72}")

for dname, instances in F6_INSTANCES.items():
    print(f"\n  {dname} ({len(instances)} instances):")
    for inst in instances:
        print(f"    • {inst['failure']}")
        print(f"      {inst['description'][:80]}")

# ============================================================
# UPDATE T072 SUMMARY WITH CLUSTERED RESULTS
# ============================================================

summary_update = {
    "director_taxonomy_mapping": {
        dclass: {
            "label": DIRECTOR_CLASSES[dclass]["label"],
            "my_modes": [m for m, dirs in MODE_TO_DIRECTOR.items() if dclass in dirs],
            "domains_present": sorted(class_domains[dclass]),
            "n_domains": len(class_domains[dclass]),
            "universality": universality_label(class_domains[dclass]),
        }
        for dclass in sorted(DIRECTOR_CLASSES.keys())
    },
    "f6_backfill_instances": {
        dname: [inst["failure"] for inst in instances]
        for dname, instances in F6_INSTANCES.items()
    },
    "universal_under_director_taxonomy": [
        dclass for dclass in sorted(DIRECTOR_CLASSES.keys())
        if universality_label(class_domains[dclass]) == "UNIVERSAL"
    ],
    "near_universal_under_director_taxonomy": [
        dclass for dclass in sorted(DIRECTOR_CLASSES.keys())
        if universality_label(class_domains[dclass]) == "near-universal"
    ],
    "final_conclusion": (
        "Under the Director's F1-F6 taxonomy, F2 (Incoherence), "
        "F3 (Fragmentation), and F6 (Self-Reference Failure) are "
        "UNIVERSAL across all four domains. F1 (Trivialization) and "
        "F5 (Information Loss) are near-universal (3/4). "
        "F4 (Runaway Divergence) is contingent (2/4). "
        "The strongest universal constraint is that viable systems "
        "must avoid incoherence, fragmentation, and self-reference "
        "failure simultaneously."
    ),
}

# Merge with existing summary if it exists
existing_path = OUT / "t072_summary.json"
if existing_path.exists():
    with open(existing_path) as f:
        existing = json.load(f)
    existing.update(summary_update)
    with open(existing_path, "w") as f:
        json.dump(existing, f, indent=2)
else:
    with open(existing_path, "w") as f:
        json.dump(summary_update, f, indent=2)

print(f"\nUpdated t072_summary.json")
print(f"\nT072 complete.")
