#!/usr/bin/env python3
"""
T071: Stability-Fertility Meta-Space Audit
==========================================
Search for invariant selection principles across four domains:
  A — Physical universes (parameter-space framework)
  B — Mathematical systems (foundations)
  C — Recursive substrate (T066 corrected graph)
  D — Dynamical manifolds (chaos/complex-systems null models)

Goal: Determine whether the same viability constraints govern all four.
If a common invariant exists, it becomes the first candidate for a
layer below the current 9-assumption substrate.
"""

import csv
import json
from pathlib import Path
from collections import defaultdict

OUT = Path("/home/student/sgp_core_v2/sfh_sgp_ood_outputs")

# ============================================================
# CANDIDATE INVARIANTS
# ============================================================

CANDIDATES = [
    "persistence",
    "coherence",
    "generativity",
    "recursive_closure",
    "information_growth",
    "self_modeling",
]

LABELS = {
    "persistence": "Persistence — system endures through time without collapse",
    "coherence": "Coherence — internal consistency, no contradictions",
    "generativity": "Generativity — capacity to produce novel structures",
    "recursive_closure": "Recursive closure — self-reference or self-application",
    "information_growth": "Information growth — increasing complexity over time",
    "self_modeling": "Self-modeling — system represents or examines itself",
}

# ============================================================
# DOMAIN A: PHYSICAL UNIVERSES
# ============================================================

PHYSICAL_CONFIGS = [
    {
        "name": "Our universe (low-entropy start, fine-tuned constants)",
        "stability": "high",
        "fertility": "high",
        "collapse_mode": "heat death (slow asymptotic)",
        "persistence": 0.9,
        "coherence": 0.95,
        "generativity": 0.95,
        "recursive_closure": 0.7,
        "information_growth": 0.9,
        "self_modeling": 0.8,
        "note": "Produces galaxies, stars, planets, life, consciousness. Self-modeling via observers within system.",
    },
    {
        "name": "Empty universe (Ω << 1, no structure formation)",
        "stability": "high",
        "fertility": "none",
        "collapse_mode": "eternal expansion without structure",
        "persistence": 0.95,
        "coherence": 0.95,
        "generativity": 0.1,
        "recursive_closure": 0.1,
        "information_growth": 0.1,
        "self_modeling": 0.0,
        "note": "Expands forever, no structure forms, no observers. Maximum stability, zero fertility.",
    },
    {
        "name": "Collapsing universe (Ω >> 1, recollapse)",
        "stability": "low",
        "fertility": "low",
        "collapse_mode": "big crunch",
        "persistence": 0.3,
        "coherence": 0.9,
        "generativity": 0.4,
        "recursive_closure": 0.3,
        "information_growth": 0.4,
        "self_modeling": 0.2,
        "note": "Recollapses before complex structure can emerge. Limited generativity.",
    },
    {
        "name": "Chaotic inflation (multiverse with varying constants)",
        "stability": "medium",
        "fertility": "medium",
        "collapse_mode": "pocket universes decohere",
        "persistence": 0.6,
        "coherence": 0.6,
        "generativity": 0.7,
        "recursive_closure": 0.4,
        "information_growth": 0.6,
        "self_modeling": 0.3,
        "note": "Bubble universes with different laws. Stability varies per bubble. Coherence threatened by measure problems.",
    },
    {
        "name": "Cyclic universe (bounce cosmology)",
        "stability": "medium",
        "fertility": "high",
        "collapse_mode": "bounce transition resets",
        "persistence": 0.7,
        "coherence": 0.8,
        "generativity": 0.85,
        "recursive_closure": 0.8,
        "information_growth": 0.6,
        "self_modeling": 0.7,
        "note": "Information may survive across bounces. Recursive structure via cyclic time.",
    },
]

# ============================================================
# DOMAIN B: MATHEMATICAL SYSTEMS
# ============================================================

MATH_CONFIGS = [
    {
        "name": "Peano arithmetic (PA)",
        "consistency": "consistent (Gentzen via ε₀)",
        "generativity": "high (infinite theorems)",
        "self_reference": "limited (Gödelian self-reference at meta-level)",
        "richness": "natural numbers, recursion",
        "persistence": 0.9,
        "coherence": 0.95,
        "generativity": 0.9,
        "recursive_closure": 0.6,
        "information_growth": 0.8,
        "self_modeling": 0.5,
        "note": "Consistency provable only via stronger system. Gödel sentences show self-reference boundary.",
    },
    {
        "name": "Zermelo-Fraenkel set theory (ZFC)",
        "consistency": "assumed (no proof possible within ZFC)",
        "generativity": "very high (virtually all mathematics)",
        "self_reference": "yes (sets can contain sets, Russell's paradox contained)",
        "richness": "entire mathematical universe",
        "persistence": 0.85,
        "coherence": 0.85,
        "generativity": 0.95,
        "recursive_closure": 0.85,
        "information_growth": 0.9,
        "self_modeling": 0.7,
        "note": "Cannot prove own consistency. Self-reference via set membership. Richness enables encoding of itself.",
    },
    {
        "name": "First-order logic (FOL)",
        "consistency": "yes (soundness theorem)",
        "generativity": "yes (all semantically valid formulas)",
        "self_reference": "no (cannot express own semantics per Tarski)",
        "richness": "limited (cannot quantify over predicates)",
        "persistence": 0.95,
        "coherence": 1.0,
        "generativity": 0.6,
        "recursive_closure": 0.2,
        "information_growth": 0.4,
        "self_modeling": 0.1,
        "note": "Complete and sound. Cannot define truth within itself. No self-modeling capacity.",
    },
    {
        "name": "Category theory (ETCS/SEARS)",
        "consistency": "comparable to ZFC (relative consistency)",
        "generativity": "very high (structural mathematics)",
        "self_reference": "yes (functor categories, 2-categories, n-categories)",
        "richness": "structural relations over objects",
        "persistence": 0.85,
        "coherence": 0.85,
        "generativity": 0.9,
        "recursive_closure": 0.9,
        "information_growth": 0.85,
        "self_modeling": 0.75,
        "note": "Higher-dimensional categorical closure enables rich self-reference. Topos theory encodes logic.",
    },
    {
        "name": "Computational models (Turing machines, λ-calculus)",
        "consistency": "yes (well-defined operational semantics)",
        "generativity": "yes (all computable functions)",
        "self_reference": "yes (universal machines, fixed-point combinators)",
        "richness": "all effectively computable functions",
        "persistence": 0.9,
        "coherence": 0.95,
        "generativity": 0.85,
        "recursive_closure": 0.95,
        "information_growth": 0.7,
        "self_modeling": 0.8,
        "note": "Universal Turing machine can simulate itself. Halting problem shows self-reference limit.",
    },
]

# ============================================================
# DOMAIN C: RECURSIVE SUBSTRATE (T066 corrected graph)
# ============================================================

SUBSTRATE_CONFIGS = []

LABELS_C = {
    "SR1":  "Self-examination of outputs",
    "IS1a": "Investigative change",
    "IS2":  "Determinate outputs",
    "OC1":  "Stable structure",
    "OC2":  "Distinguishability",
    "EC1":  "Self-knowledge",
    "IC1":  "Extractable information",
    "CD1":  "Causal relations exist",
    "CD2":  "Self-affecting procedures",
}

EDGES = {
    "IS1a": ["OC2"],
    "IS2":  ["IC1", "OC1", "IS1a"],
    "OC1":  ["OC2"],
    "OC2":  [],
    "EC1":  ["SR1", "IS2", "IS1a"],
    "IC1":  ["OC1", "OC2", "IS1a"],
    "CD1":  ["OC1", "OC2"],
    "CD2":  ["CD1", "IS1a", "EC1"],
    "SR1":  ["IS2", "IS1a"],
}

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

def knockouts(edges, nodes):
    """Knockout each node and return survivors."""
    results = {}
    for removed in nodes:
        alive = {n for n in nodes if n != removed}
        sat = compute_survivors(edges, alive)
        results[removed] = {"survivors": len(sat), "total": len(alive),
                            "survival_pct": round(len(sat)/len(alive)*100, 1)}
    return results

ALL_SUB = sorted(LABELS_C.keys())
ko_results = knockouts(EDGES, ALL_SUB)

# Base graph measures
base_sat = compute_survivors(EDGES, set(ALL_SUB))
base_gen = len(base_sat) == len(ALL_SUB)
base_roots = [n for n in ALL_SUB if not EDGES.get(n, [])]

for node in ALL_SUB:
    # Knockout sensitivity
    ko_pct = ko_results[node]["survival_pct"]
    label = LABELS_C[node]
    n_deps = len(EDGES.get(node, {}))
    n_dependents = sum(1 for n in ALL_SUB if node in EDGES.get(n, {}))

    # Assign generative score based on out-degree and position
    if node == "OC2":
        gen_score = 1.0  # unique root, generative source
    elif n_dependents > 0:
        gen_score = 0.8  # feeds downstream
    else:
        gen_score = 0.5  # leaf

    SUBSTRATE_CONFIGS.append({
        "name": f"{node} — {label}",
        "survival_on_removal_pct": ko_pct,
        "in_degree": n_deps,
        "out_degree": n_dependents,
        "is_root": node in base_roots,
        "persistence": round(ko_pct / 100, 2),
        "coherence": 0.95 if base_gen else 0.0,
        "generativity": gen_score,
        "recursive_closure": 0.9 if node in ["SR1", "EC1", "CD2"] else 0.3,
        "information_growth": 0.8 if node in ["IS2", "EC1", "SR1"] else 0.4,
        "self_modeling": 0.9 if node in ["SR1", "EC1"] else 0.2,
        "note": f"Knockout survival: {ko_pct}%. {'Root node.' if node in base_roots else ''} {'Self-referential.' if node in ['SR1','EC1','CD2'] else ''}",
    })

# Whole-substrate aggregate
substrate_aggregate = {
    "n_assumptions": len(ALL_SUB),
    "n_roots": len(base_roots),
    "generative": base_gen,
    "mean_knockout_survival": round(sum(r["survival_pct"] for r in ko_results.values()) / len(ko_results), 1),
    "n_cycles": 0,
}

# ============================================================
# DOMAIN D: DYNAMICAL MANIFOLDS
# ============================================================

DYNAMICAL_CONFIGS = [
    {
        "name": "Lorenz attractor (chaotic system)",
        "persistence_under_perturbation": "high (strange attractor is structurally stable)",
        "structural_continuity": "high (trajectories remain on attractor)",
        "complexity_generation": "medium (deterministic chaos, bounded complexity)",
        "persistence": 0.9,
        "coherence": 0.9,
        "generativity": 0.6,
        "recursive_closure": 0.7,
        "information_growth": 0.5,
        "self_modeling": 0.2,
        "note": "Strange attractor is an invariant set. Butterfly effect = sensitivity to initial conditions, not instability of structure.",
    },
    {
        "name": "Coupled map lattice (spatiotemporal chaos)",
        "persistence_under_perturbation": "medium (local perturbations propagate)",
        "structural_continuity": "medium (pattern formation with instability)",
        "complexity_generation": "high (emergent spatial patterns)",
        "persistence": 0.7,
        "coherence": 0.7,
        "generativity": 0.8,
        "recursive_closure": 0.5,
        "information_growth": 0.7,
        "self_modeling": 0.3,
        "note": "Local coupling produces global patterns. Self-organization without central control.",
    },
    {
        "name": "Logistic map (Feigenbaum period-doubling cascade)",
        "persistence_under_perturbation": "varies (periodic windows stable, chaos sensitive)",
        "structural_continuity": "medium (universal scaling, Feigenbaum constants)",
        "complexity_generation": "medium (period-doubling route to chaos)",
        "persistence": 0.6,
        "coherence": 0.85,
        "generativity": 0.7,
        "recursive_closure": 0.8,
        "information_growth": 0.5,
        "self_modeling": 0.1,
        "note": "r parameter controls dynamics. Feigenbaum constants δ, α are universal. Period-doubling is recursive.",
    },
    {
        "name": "Reaction-diffusion systems (Turing patterns)",
        "persistence_under_perturbation": "high (pattern attractors stable)",
        "structural_continuity": "high (patterns robust to noise)",
        "complexity_generation": "high (morphogenesis, pattern formation)",
        "persistence": 0.85,
        "coherence": 0.9,
        "generativity": 0.85,
        "recursive_closure": 0.4,
        "information_growth": 0.75,
        "self_modeling": 0.2,
        "note": "Activator-inhibitor dynamics. Stable patterns emerge from homogeneous initial conditions.",
    },
    {
        "name": "Boolean network (Kauffman, NK model)",
        "persistence_under_perturbation": "medium (order-chaos transition at K=2)",
        "structural_continuity": "medium (robust in ordered regime, fragile in chaotic)",
        "complexity_generation": "high (emergent attractors)",
        "persistence": 0.75,
        "coherence": 0.8,
        "generativity": 0.8,
        "recursive_closure": 0.6,
        "information_growth": 0.65,
        "self_modeling": 0.3,
        "note": "K=2 critical regime: maximum complexity. Ordered regime устойчив, chaotic regime generative but fragile.",
    },
]

# ============================================================
# CROSS-DOMAIN ANALYSIS
# ============================================================

DOMAINS = {
    "A: Physical universes": PHYSICAL_CONFIGS,
    "B: Mathematical systems": MATH_CONFIGS,
    "C: Recursive substrate": SUBSTRATE_CONFIGS,
    "D: Dynamical manifolds": DYNAMICAL_CONFIGS,
}

print("=" * 72)
print("T071: STABILITY-FERTILITY META-SPACE AUDIT")
print("=" * 72)

# ---- Per-domain summary ----
print(f"\n{'='*72}")
print("DOMAIN SUMMARIES")
print(f"{'='*72}")

for dname, configs in DOMAINS.items():
    scores = defaultdict(list)
    for c in configs:
        for inv in CANDIDATES:
            scores[inv].append(c[inv])
    print(f"\n--- {dname} ---")
    for inv in CANDIDATES:
        vals = scores[inv]
        mean_v = sum(vals) / len(vals)
        min_v = min(vals)
        max_v = max(vals)
        print(f"  {inv:<25} mean={mean_v:.2f}  range=[{min_v:.1f}, {max_v:.1f}]")

# ---- Cross-domain invariant search ----
print(f"\n{'='*72}")
print("CROSS-DOMAIN INVARIANT SEARCH")
print(f"{'='*72}")

# For each invariant, compute across-domain mean and variance
invariant_scores = {}
for inv in CANDIDATES:
    per_domain_means = []
    for dname, configs in DOMAINS.items():
        vals = [c[inv] for c in configs]
        per_domain_means.append(sum(vals) / len(vals))
    overall_mean = sum(per_domain_means) / len(per_domain_means)
    overall_min = min(per_domain_means)
    overall_max = max(per_domain_means)
    variance = sum((m - overall_mean)**2 for m in per_domain_means) / len(per_domain_means)
    invariant_scores[inv] = {
        "overall_mean": round(overall_mean, 2),
        "mean_min": round(overall_min, 2),
        "mean_max": round(overall_max, 2),
        "cross_domain_variance": round(variance, 3),
        "stability_across_domains": "HIGH" if variance < 0.02 else
                                     "MEDIUM" if variance < 0.05 else "LOW",
    }
    print(f"\n  {inv:<25}  {LABELS[inv]}")
    print(f"  {'':25}  Mean: {overall_mean:.2f}, Range: [{overall_min:.2f}, {overall_max:.2f}], Variance: {variance:.3f}")
    for i, (dname, _) in enumerate(DOMAINS.items()):
        print(f"  {'':25}  {dname}: {per_domain_means[i]:.2f}")
    print(f"  {'':25}  Stability: {invariant_scores[inv]['stability_across_domains']}")

# Rank invariants by cross-domain stability (lowest variance first)
sorted_invs = sorted(CANDIDATES, key=lambda i: invariant_scores[i]["cross_domain_variance"])

print(f"\n  --- Invariant ranking by cross-domain stability ---")
print(f"  {'Rank':<6}{'Invariant':<25}{'Variance':<10}{'Mean':<8}{'Stability'}")
print(f"  {'-'*65}")
for rank, inv in enumerate(sorted_invs, 1):
    info = invariant_scores[inv]
    print(f"  {rank:<6}{inv:<25}{info['cross_domain_variance']:<10}{info['overall_mean']:<8}{info['stability_across_domains']}")

# ---- Pairwise domain similarity ----
print(f"\n{'='*72}")
print("PAIRWISE DOMAIN SIMILARITY")
print(f"{'='*72}")

dnames = list(DOMAINS.keys())
similarity = {}
for i in range(len(dnames)):
    for j in range(i+1, len(dnames)):
        d1, d2 = dnames[i], dnames[j]
        # Cosine similarity based on per-domain means
        v1 = [sum(c[inv] for c in DOMAINS[d1]) / len(DOMAINS[d1]) for inv in CANDIDATES]
        v2 = [sum(c[inv] for c in DOMAINS[d2]) / len(DOMAINS[d2]) for inv in CANDIDATES]
        dot = sum(a*b for a,b in zip(v1,v2))
        norm1 = sum(a*a for a in v1)**0.5
        norm2 = sum(b*b for b in v2)**0.5
        sim = dot / (norm1 * norm2) if norm1 * norm2 > 0 else 0
        similarity[f"{d1} × {d2}"] = round(sim, 3)

print(f"\n  Cosine similarity of domain profiles across candidate invariants:")
for pair, sim in sorted(similarity.items(), key=lambda x: -x[1]):
    print(f"  {pair:<55} {sim:.3f}")

# ---- Failure mode analysis ----
print(f"\n{'='*72}")
print("FAILURE MODE ANALYSIS")
print(f"{'='*72}")

# Collect failure modes across all configs
failure_modes = []
for dname, configs in DOMAINS.items():
    for c in configs:
        failed_invariants = []
        for inv in CANDIDATES:
            if c[inv] < 0.3:
                failed_invariants.append(inv)
        if failed_invariants:
            failure_modes.append({
                "domain": dname,
                "config": c["name"],
                "failed_invariants": ";".join(failed_invariants),
                "n_failed": len(failed_invariants),
                "severity": "critical" if len(failed_invariants) >= 3 else
                           "moderate" if len(failed_invariants) >= 2 else "mild",
            })

# Count failures per invariant
inv_failures = defaultdict(int)
for fm in failure_modes:
    for inv in fm["failed_invariants"].split(";"):
        inv_failures[inv] += 1

print(f"\n  Failure modes per invariant (across all domains):")
for inv, count in sorted(inv_failures.items(), key=lambda x: -x[1]):
    print(f"  {inv:<25} failed in {count} configurations")

print(f"\n  Failure mode details:")
for fm in failure_modes:
    print(f"  [{fm['severity']}] {fm['domain']} / {fm['config']}")
    print(f"         Fails: {fm['failed_invariants']}")

# ---- Level-below-substrate candidates ----
print(f"\n{'='*72}")
print("LEVEL-BELOW-SUBSTRATE CANDIDATES")
print(f"{'='*72}")

# Which invariants are:
# 1. Present across ALL domains (mean > 0.5 in every domain)
# 2. Low variance (stability across domains)
# 3. High overall mean

candidates_below = []
for inv in sorted_invs:
    info = invariant_scores[inv]
    per_domain = []
    for dname, configs in DOMAINS.items():
        per_domain.append(sum(c[inv] for c in configs) / len(configs))
    all_above_half = all(m > 0.5 for m in per_domain)
    mean_above_7 = info["overall_mean"] > 0.7

    if all_above_half and mean_above_7:
        candidates_below.append({
            "invariant": inv,
            "label": LABELS[inv],
            "mean": info["overall_mean"],
            "variance": info["cross_domain_variance"],
            "reason": f"Present in all domains (min {min(per_domain):.2f}), high overall mean ({info['overall_mean']:.2f}), low cross-domain variance ({info['cross_domain_variance']:.3f})",
        })

print(f"\n  Invariants that survive cross-domain filter (present in ALL domains, mean > 0.7):")
for cb in candidates_below:
    print(f"\n  ✓ {cb['invariant']}")
    print(f"    {cb['label']}")
    print(f"    Mean: {cb['mean']:.2f}, Variance: {cb['variance']:.3f}")
    print(f"    {cb['reason']}")

if not candidates_below:
    print(f"\n  No invariant passes the strict filter. Checking relaxed filter (mean > 0.5):")
    for inv in sorted_invs:
        info = invariant_scores[inv]
        per_domain = []
        for dname, configs in DOMAINS.items():
            per_domain.append(sum(c[inv] for c in configs) / len(configs))
        all_above_half = all(m > 0.5 for m in per_domain)
        if all_above_half:
            candidates_below.append({
                "invariant": inv,
                "label": LABELS[inv],
                "mean": info["overall_mean"],
                "variance": info["cross_domain_variance"],
                "reason": f"Present in all domains but mean {info['overall_mean']:.2f} below 0.7 threshold",
            })
            print(f"\n  ~ {inv}")
            print(f"    {LABELS[inv]}")
            print(f"    Mean: {info['overall_mean']:.2f}, Variance: {info['cross_domain_variance']:.3f}")

# ---- Final synthesis ----
print(f"\n{'='*72}")
print("SYNTHESIS")
print(f"{'='*72}")

print(f"""
  Cross-domain invariants identified:
""")

for cb in candidates_below:
    print(f"    {cb['invariant']} — {cb['label']}")

# Determine the best candidate for the level below substrate
if candidates_below:
    best = candidates_below[0]  # lowest variance first
    print(f"""
  Best candidate for level-below-substrate: {best['invariant']}

  Rationale:
    - Present across all four domains (universal)
    - Lowest cross-domain variance ({best['variance']:.3f})
    - High overall mean ({best['mean']:.2f})
    - Failure in any domain correlates with system collapse

  What this means for the substrate:
    If {best['invariant']} is a genuine invariant across all viable
    systems, then it must be presumed as a condition of possibility
    for the recursive substrate, not derived from it. This would place
    it below the current 9-assumption substrate, which assumes
    {best['invariant']} without encoding it explicitly.

  Gap in the current 9-assumption model:
    The current substrate assumes structures that persist (OC1),
    distinguish (OC2), and generate (IS1a, IS2). But it does not
    explicitly encode what makes {best['invariant']} possible.
    Assumption OC1 (Stable structure) implies persistence but does
    not guarantee it — OC1 says structures persist, not what makes
    persistence possible.

  Implication:
    The 9-assumption substrate operates within a stable regime
    defined by the invariant. If the invariant is genuine, the
    substrate is not universal — it is conditional on the invariant
    holding. This does not invalidate the substrate, but it does
    bound its scope.
""")
else:
    print(f"""
  No invariant demonstrates true universality across all four domains.
  The most stable invariants each fail in at least one domain:

""")
    for inv in sorted_invs:
        info = invariant_scores[info]
        print(f"    {inv}: variance={info['cross_domain_variance']:.3f}, mean={info['overall_mean']:.2f}")

    print(f"""
  Possible interpretations:
    1. The domains are genuinely incommensurable — no single invariant
       governs all viable systems.
    2. The scoring is too coarse to detect the invariant.
    3. The invariant is not among the six candidates tested.
    4. The invariant is domain-specific and the cross-domain search
       is the wrong abstraction level.
""")

# ============================================================
# WRITE DELIVERABLES
# ============================================================

# 1. Cross-domain matrix
with open(OUT / "t071_cross_domain_matrix.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["domain", "config", *CANDIDATES])
    for dname, configs in DOMAINS.items():
        for c in configs:
            w.writerow([dname, c["name"]] + [c[inv] for inv in CANDIDATES])

print(f"\nWrote t071_cross_domain_matrix.csv")

# 2. Invariant candidates
with open(OUT / "t071_invariant_candidates.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["invariant", "label", "overall_mean", "cross_domain_variance",
                 "stability", "domain_A_mean", "domain_B_mean", "domain_C_mean", "domain_D_mean",
                 "is_candidate"])
    for inv in sorted_invs:
        info = invariant_scores[inv]
        per_domain_values = []
        for dname, configs in DOMAINS.items():
            per_domain_values.append(round(sum(c[inv] for c in configs) / len(configs), 2))
        is_cand = "YES" if inv in [cb["invariant"] for cb in candidates_below] else "no"
        w.writerow([inv, LABELS[inv], info["overall_mean"], info["cross_domain_variance"],
                     info["stability_across_domains"]] + per_domain_values + [is_cand])

print(f"Wrote t071_invariant_candidates.csv")

# 3. Failure modes
with open(OUT / "t071_failure_modes.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["domain", "config", "failed_invariants", "n_failed", "severity"])
    for fm in failure_modes:
        w.writerow([fm["domain"], fm["config"], fm["failed_invariants"],
                     fm["n_failed"], fm["severity"]])

print(f"Wrote t071_failure_modes.csv")

# 4. Meta-space report (structured data)
report = {
    "audit": "T071 — Stability-Fertility Meta-Space Audit",
    "domains_compared": list(DOMAINS.keys()),
    "candidate_invariants_tested": CANDIDATES,
    "invariant_rankings": {inv: invariant_scores[inv] for inv in sorted_invs},
    "pairwise_similarities": similarity,
    "level_below_substrate_candidates": candidates_below,
    "n_failure_modes": len(failure_modes),
    "conclusion": (
        f"Best candidate for level-below-substrate: {candidates_below[0]['invariant']}"
        if candidates_below else "No invariant demonstrates true universality"
    ),
}

with open(OUT / "t071_summary.json", "w") as f:
    json.dump(report, f, indent=2)

print(f"Wrote t071_summary.json")

# ---- External formatted report ----
with open(OUT / "t071_meta_space_report.md", "w") as f:
    f.write("""T071: Stability-Fertility Meta-Space Audit
=========================================

## Objective

Determine whether the same viability constraints govern:
- physical universes,
- mathematical systems,
- recursive epistemic substrates,
- dynamical manifolds.

If a common invariant exists, it becomes the first candidate for a
level below the current 9-assumption substrate.

---

## Methodology

Six candidate invariants were tested across four domains:

| Invariant | Definition |
|-----------|------------|
| Persistence | System endures through time without collapse |
| Coherence | Internal consistency, no contradictions |
| Generativity | Capacity to produce novel structures |
| Recursive closure | Self-reference or self-application |
| Information growth | Increasing complexity over time |
| Self-modeling | System represents or examines itself |

Each domain had 4-5 configurations scored 0.0-1.0 per invariant.
""")

    f.write(f"\n## Domain A: Physical Universes\n\n")
    f.write("| Universe | Persist | Coher | Gener | Recurs | InfoG | SelfM |\n")
    f.write("|----------|---------|-------|-------|--------|-------|-------|\n")
    for c in PHYSICAL_CONFIGS:
        f.write(f"| {c['name']} | {c['persistence']} | {c['coherence']} | {c['generativity']} | {c['recursive_closure']} | {c['information_growth']} | {c['self_modeling']} |\n")

    f.write(f"\n## Domain B: Mathematical Systems\n\n")
    f.write("| System | Persist | Coher | Gener | Recurs | InfoG | SelfM |\n")
    f.write("|--------|---------|-------|-------|--------|-------|-------|\n")
    for c in MATH_CONFIGS:
        f.write(f"| {c['name']} | {c['persistence']} | {c['coherence']} | {c['generativity']} | {c['recursive_closure']} | {c['information_growth']} | {c['self_modeling']} |\n")

    f.write(f"\n## Domain C: Recursive Substrate (T066 corrected)\n\n")
    f.write(f"| Node | Persist | Coher | Gener | Recurs | InfoG | SelfM | Role |\n")
    f.write(f"|------|---------|-------|-------|--------|-------|-------|------|\n")
    for c in SUBSTRATE_CONFIGS:
        f.write(f"| {c['name']} | {c['persistence']} | {c['coherence']} | {c['generativity']} | {c['recursive_closure']} | {c['information_growth']} | {c['self_modeling']} | KO survival {c['survival_on_removal_pct']}% |\n")

    f.write(f"\n## Domain D: Dynamical Manifolds\n\n")
    f.write("| System | Persist | Coher | Gener | Recurs | InfoG | SelfM |\n")
    f.write("|--------|---------|-------|-------|--------|-------|-------|\n")
    for c in DYNAMICAL_CONFIGS:
        f.write(f"| {c['name']} | {c['persistence']} | {c['coherence']} | {c['generativity']} | {c['recursive_closure']} | {c['information_growth']} | {c['self_modeling']} |\n")

    f.write(f"""
## Cross-Domain Results

### Invariant rankings by cross-domain stability
""")

    for rank, inv in enumerate(sorted_invs, 1):
        info = invariant_scores[inv]
        f.write(f"\n**{rank}. {inv}** — mean={info['overall_mean']:.2f}, variance={info['cross_domain_variance']:.3f}, stability={info['stability_across_domains']}\n")

    f.write(f"""
### Pairwise domain similarities
""")
    for pair, sim in sorted(similarity.items(), key=lambda x: -x[1]):
        f.write(f"- {pair}: {sim:.3f}\n")

    if candidates_below:
        best = candidates_below[0]
        f.write(f"""
### Level-Below-Substrate Candidate

**{best['invariant']}** — {best['label']}

- Mean across all domains: {best['mean']:.2f}
- Cross-domain variance: {best['variance']:.3f}
- Status: **Candidate for layer below current 9-assumption substrate**
""")

    f.write("""
### Gap Analysis

If the invariant is genuine, the current 9-assumption substrate is
conditional on it — the substrate operates WITHIN a regime where the
invariant holds, but does not encode what makes the invariant possible.

This means:
1. The substrate is not universal — it is domain-specific to epistemic
   systems that already satisfy the invariant.
2. The invariant is a precondition for the substrate, not a consequence
   of it.
3. A complete model would need to make the invariant explicit, placing
   it below the current assumption layer.

But — and this is critical — making the invariant explicit does not
necessarily require adding a 10th assumption to the substrate. The
substrate's own assumptions may already imply the invariant without
needing to state it. The invariant would then be a property of the
substrate's regime, not a missing assumption within it.

This is the same pattern as T066-T069: the dependency structure was
complete; the apparent gaps were over-asserted edges or
interpretation-dependent requirements.
""")

    f.write("""
### Open Questions

1. Is the invariant genuinely universal across all possible systems,
   or is it an artifact of our domain selection?
2. Does the invariant follow from the existing 9 assumptions
   (making it a derived property), or does it require separate
   encoding (making it a 10th assumption)?
3. Can we construct a counterexample — a viable system that violates
   the invariant? If so, the invariant is not universal.
""")

print(f"Wrote t071_meta_space_report.md")

print(f"\nT071 complete.")
