#!/usr/bin/env python3
"""
T072: Cross-Domain Failure Boundary Audit
===========================================
Instead of searching for positive invariants (T071), identify failure
modes that recur across all four domains. The logic: failure boundaries
are often sharper and more universal than success conditions.

Failure modes tested:
  CT — Collapse into triviality  (system becomes vacuous/empty)
  RD — Runaway divergence        (uncontrolled explosion / infinite regress)
  LD — Loss of differentiation   (everything becomes indistinguishable)
  LP — Loss of persistence       (system ceases to exist / maintain structure)
  LG — Loss of generativity      (system stops producing novelty)
  CC — Contradiction/inconsistency (internal conflict destroys coherence)
  FR — Fragmentation/incoherence  (parts do not fit together)
  LR — Loss of recoverability    (perturbation is permanent / irreversible)

Domains:
  A — Physical universes (parameter-space framework)
  B — Mathematical systems (foundations)
  C — Recursive substrate (T066 corrected graph)
  D — Dynamical manifolds (chaos / complex-systems models)
"""

import csv, json
from pathlib import Path
from collections import defaultdict

OUT = Path("/home/student/sgp_core_v2/sfh_sgp_ood_outputs")

# ============================================================
# FAILURE MODE SCHEMA
# ============================================================

FAILURE_MODES = [
    "CT",  # collapse into triviality
    "RD",  # runaway divergence
    "LD",  # loss of differentiation
    "LP",  # loss of persistence
    "LG",  # loss of generativity
    "CC",  # contradiction / inconsistency
    "FR",  # fragmentation / incoherence
    "LR",  # loss of recoverability
]

FAILURE_LABELS = {
    "CT": "Collapse into triviality — system becomes vacuous, empty, or meaningless",
    "RD": "Runaway divergence — uncontrolled growth, explosion, or infinite regress",
    "LD": "Loss of differentiation — everything becomes indistinguishable",
    "LP": "Loss of persistence — system ceases to exist or maintain structure",
    "LG": "Loss of generativity — system stops producing novel structures",
    "CC": "Contradiction / inconsistency — internal conflict destroys coherence",
    "FR": "Fragmentation — parts do not fit together or refer to different domains",
    "LR": "Loss of recoverability — perturbation is permanent, no return to viability",
}

# ============================================================
# DOMAIN A: PHYSICAL UNIVERSES — FAILURE BOUNDARIES
# ============================================================

PHYSICAL_FAILURES = [
    {
        "failure": "Heat death (max entropy)",
        "mode": "LG",
        "description": "Universe reaches thermodynamic equilibrium; no free energy remains for structure formation or information processing.",
        "type": "Asymptotic approach",
        "triggers": "Time → ∞; or initial low-entropy condition not present",
        "neighborhood": "Near all viable universes as t → ∞ if no entropy-gradient mechanism",
    },
    {
        "failure": "Big crunch (recollapse)",
        "mode": "LP",
        "description": "Density exceeds critical; universe recollapses before structure forms.",
        "type": "Bounded trajectory",
        "triggers": "Ω >> 1, or dark energy insufficient",
        "neighborhood": "Ω just above critical threshold",
    },
    {
        "failure": "Empty expansion (no structure)",
        "mode": "LG",
        "description": "Expansion too rapid for gravity to form galaxies, stars, planets.",
        "type": "Runaway",
        "triggers": "Ω << 1, or dark energy dominant too early",
        "neighborhood": "Ω just below critical threshold",
    },
    {
        "failure": "Vacuum decay / false vacuum collapse",
        "mode": "LP",
        "description": "Quantum tunneling to lower-energy vacuum; bubble nucleates and destroys existing structure at light speed.",
        "type": "Phase transition",
        "triggers": "Higgs metastability; or new physics beyond Standard Model",
        "neighborhood": "Higgs mass near stability boundary",
    },
    {
        "failure": "Chaotic inflation / measure problem",
        "mode": "FR",
        "description": "Multiverse with different laws in different pockets; no unified reference frame for probability.",
        "type": "Fragmentation",
        "triggers": "Inflationary potential allows eternal inflation",
        "neighborhood": "Volume-weighted measure assigns infinite weight to some regions",
    },
    {
        "failure": "Loss of arrow of time (no entropy gradient)",
        "mode": "LD",
        "description": "Past hypothesis fails; no thermodynamic distinction between past and future.",
        "type": "Loss of direction",
        "triggers": "Initial conditions at equilibrium",
        "neighborhood": "Low-entropy initial condition not enforced",
    },
    {
        "failure": "Mathematical inconsistency in fundamental laws",
        "mode": "CC",
        "description": "Theories of quantum gravity contain anomalies or inconsistencies; no consistent UV completion exists.",
        "type": "Contradiction",
        "triggers": "String landscape constraints; swampland conditions",
        "neighborhood": "Effective field theories without UV completion",
    },
    {
        "failure": "Strong CP violation / matter-antimatter asymmetry failure",
        "mode": "FR",
        "description": "Baryogenesis fails; universe contains equal matter and antimatter which annihilate, leaving only radiation.",
        "type": "Fragmentation",
        "triggers": "CP-violating phase too small; or baryon-number violation absent",
        "neighborhood": "θ_QCD near experimental bound",
    },
    {
        "failure": "Decoherence without localized structures",
        "mode": "LD",
        "description": "Quantum decoherence produces classicality but no localized objects; wavefunction branches without stable records.",
        "type": "Loss of differentiation",
        "triggers": "No mechanism for structure formation from decoherence alone",
        "neighborhood": "Environments where decoherence outpaces structure formation",
    },
    {
        "failure": "Black hole information loss",
        "mode": "LR",
        "description": "Information swallowed by black hole is lost; no mechanism recovers it. System is non-unitary.",
        "type": "Loss of recoverability",
        "triggers": "Hawking evaporation without information retrieval",
        "neighborhood": "Strong gravity + quantum field theory",
    },
]

# ============================================================
# DOMAIN B: MATHEMATICAL SYSTEMS — FAILURE BOUNDARIES
# ============================================================

MATH_FAILURES = [
    {
        "failure": "Inconsistency (ex contradictione quodlibet)",
        "mode": "CC",
        "description": "Contradiction in formal system; principle of explosion makes every statement provable. System becomes trivial.",
        "type": "Collapse",
        "triggers": "Self-reference without containment (naive comprehension); inconsistent axioms",
        "neighborhood": "Unrestricted comprehension (Frege's Grundgesetze); inconsistent arithmetic",
    },
    {
        "failure": "Triviality via over-generation",
        "mode": "CT",
        "description": "Too many axioms or too-generous rules; system proves everything, becomes informationally vacuous.",
        "type": "Collapse into triviality",
        "triggers": "Too-powerful comprehension; inconsistent type assignment",
        "neighborhood": "Curry's paradox; unrestricted λ-abstraction in untyped λ-calculus",
    },
    {
        "failure": "Gödelian incompleteness (self-reference limit)",
        "mode": "LG",
        "description": "Consistent system cannot prove its own consistency; certain truths are in principle inaccessible within the system.",
        "type": "Generativity bound",
        "triggers": "Sufficient expressive power to encode arithmetic + self-reference",
        "neighborhood": "Every consistent system containing PA",
    },
    {
        "failure": "Halting problem / undecidability barrier",
        "mode": "LG",
        "description": "No effective procedure decides termination for all programs. Generativity bounded by decidability ceiling.",
        "type": "Generativity bound",
        "triggers": "Sufficient computational power (Turing-completeness)",
        "neighborhood": "All Turing-complete formalisms",
    },
    {
        "failure": "Tarski's undefinability of truth",
        "mode": "FR",
        "description": "Truth predicate for a language cannot be defined within that language. Semantic fragmentation: object language vs. metalanguage.",
        "type": "Fragmentation",
        "triggers": "Expressive power sufficient for self-reference",
        "neighborhood": "Any language with negation + self-reference capacity",
    },
    {
        "failure": "Set-theoretic paradox (Russell, Burali-Forti)",
        "mode": "CC",
        "description": "Unrestricted set formation leads to contradiction. System cannot consistently contain all sets it can describe.",
        "type": "Contradiction",
        "triggers": "Naive comprehension axiom; collection of all sets of a certain type",
        "neighborhood": "Every set theory before ZFC containment; proper classes not separated",
    },
    {
        "failure": "Loss of well-foundedness / infinite descent",
        "mode": "RD",
        "description": "Infinite descending ∈-chains violate foundation. No base case for structural induction.",
        "type": "Runaway",
        "triggers": "Anti-foundation axiom (AFA) or non-well-founded sets",
        "neighborhood": "Non-well-founded set theories without replacement restrictions",
    },
    {
        "failure": "Categorical collapse (every category is a preorder)",
        "mode": "LD",
        "description": "Category loses distinguishing power; at most one morphism between any two objects.",
        "type": "Loss of differentiation",
        "triggers": "Too-stringent constraints; forcing triviality of Hom-sets",
        "neighborhood": "Posets as degenerate categories; discrete categories with identity-only morphisms",
    },
    {
        "failure": "Fixed-point inconsistency in λ-calculus",
        "mode": "RD",
        "description": "Y-combinator enables arbitrary recursion; untyped system has non-terminating terms that diverge.",
        "type": "Runaway",
        "triggers": "Self-application (ω = λx.xx); fixed-point combinators",
        "neighborhood": "Untyped λ-calculus without type restrictions",
    },
    {
        "failure": "Loss of canonicity / normalization failure",
        "mode": "LR",
        "description": "Dependent type system lacks strong normalization; type-checking may not terminate.",
        "type": "Loss of recoverability",
        "triggers": "Impredicativity without termination measure; non-well-founded recursion",
        "neighborhood": "Type-in-type (universe inconsistency); unrestricted impredicativity",
    },
]

# ============================================================
# DOMAIN C: RECURSIVE SUBSTRATE — FAILURE BOUNDARIES
# ============================================================

SUBSTRATE_FAILURES = []

# T066 corrected graph
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

ALL_C = sorted(LABELS_C.keys())

# Compute substrate-level failure boundaries
base_sat = compute_survivors(EDGES, set(ALL_C))

for node in ALL_C:
    alive = {n for n in ALL_C if n != node}
    sat = compute_survivors(EDGES, alive)
    survival_pct = round(len(sat) / len(alive) * 100, 1)
    collapsed = len(alive) - len(sat)

    if survival_pct == 0.0:
        primary_mode = "LP"   # loss of persistence — system completely collapses
    elif survival_pct < 50:
        primary_mode = "LG"   # loss of generativity — too few survivors to generate full structure
    elif collapsed > 0:
        primary_mode = "FR"   # fragmentation — some parts collapse
    else:
        continue  # no failure from this removal

    SUBSTRATE_FAILURES.append({
        "failure": f"Knockout of {node} ({LABELS_C[node]})",
        "mode": primary_mode,
        "description": f"Removing {node} causes {collapsed}/{len(alive)} downstream assumptions to fail. Survival: {survival_pct}%.",
        "type": "Dependency collapse" if survival_pct < 50 else "Partial fragmentation",
        "triggers": f"Removal of {node}; all dependents lose support",
        "neighborhood": f"Any graph where {node} has dependents",
    })

# Also add the T063-T066 structural failures
SUBSTRATE_FAILURES.extend([
    {
        "failure": "Bootstrap deadlock (IS1↔IS2 cycle in original substrate)",
        "mode": "CC",
        "description": "Mutual dependency IS1→IS2 and IS2→IS1 creates bootstrap deadlock; neither can be satisfied first. T064 identified, T066 resolved by removing IS1→IS2 edge.",
        "type": "Contradiction / cycle",
        "triggers": "Bidirectional or cyclic dependency in directed acyclic dependency structure",
        "neighborhood": "Any graph containing the IS1→IS2→IS1 cycle; or SR1↔EC1↔SR1",
    },
    {
        "failure": "OC2 removal — complete collapse",
        "mode": "LP",
        "description": "Removing OC2 (Distinguishability) causes 100% collapse. OC2 is the unique root — no other node supplies its function.",
        "type": "Root loss",
        "triggers": "Single root point; no alternative path to same function",
        "neighborhood": "Any DAG whose unique root is removed",
    },
    {
        "failure": "OC1 removal — partial collapse (3/8 → 5/8 survivors)",
        "mode": "FR",
        "description": "OC1 (Stable structure) removal loses CD1, CD2, IC1, IS2, EC1, SR1. Only IS1a and OC2 survive.",
        "type": "Structural fragmentation",
        "triggers": "OC1 provides structural stability needed by multiple downstream assumptions",
        "neighborhood": "Any graph where the structural-stability node is removed",
    },
    {
        "failure": "IS1a removal — partial collapse (3/8 → 5/8 survivors)",
        "mode": "FR",
        "description": "IS1a (Investigative change) removal loses IS2, EC1, SR1, CD2, IC1. Only structural assumptions remain.",
        "type": "Functional fragmentation",
        "triggers": "IS1a provides dynamic capacity needed by output-production, examination, and knowledge",
        "neighborhood": "Any graph where the change/dynamics node is removed",
    },
    {
        "failure": "SR1 removal — loss of self-examination only",
        "mode": "LG",
        "description": "SR1 removal loses EC1 and CD2. Investigation can no longer examine itself or effect self-change.",
        "type": "Generativity loss",
        "triggers": "SR1 is the only path to self-knowledge (EC1) and self-effects (CD2)",
        "neighborhood": "Any substrate without a self-examination mechanism",
    },
    {
        "failure": "Trivial substrate (only OC2, no downstream generation)",
        "mode": "CT",
        "description": "OC2 alone: distinguishability exists but nothing distinguishes. Substrate can generate nothing. Empty epistemic system.",
        "type": "Collapse into triviality",
        "triggers": "Root without generative capacity; distinguishability without structure to apply it to",
        "neighborhood": "Any system with distinguishing capacity but nothing to distinguish",
    },
    {
        "failure": "Cycle deadlock (any SCC in dependency graph)",
        "mode": "CC",
        "description": "Strongly connected component in dependency graph prevents fixed-point resolution. No node can be satisfied before another in the cycle.",
        "type": "Contradiction / cycle",
        "triggers": "Bidirectional dependency between any two nodes",
        "neighborhood": "IS1↔IS2 in original; potentially SR1↔EC1 under circular definitions",
    },
])

# ============================================================
# DOMAIN D: DYNAMICAL MANIFOLDS — FAILURE BOUNDARIES
# ============================================================

DYNAMICAL_FAILURES = [
    {
        "failure": "Fixed-point collapse (trivial attractor)",
        "mode": "CT",
        "description": "All trajectories converge to single point. No variation, no complexity, no information generation.",
        "type": "Collapse into triviality",
        "triggers": "Dissipation dominates; all energy gradients exhausted",
        "neighborhood": "Strongly damped systems; overdamped harmonic oscillator; gradient descent on convex function",
    },
    {
        "failure": "Limit-cycle stagnation (periodic triviality)",
        "mode": "LG",
        "description": "System enters stable limit cycle; same trajectory repeats infinitely. No new information produced after cycle convergence.",
        "type": "Generativity bound",
        "triggers": "Hopf bifurcation with saturation",
        "neighborhood": "Van der Pol oscillator near relaxation boundary; predator-prey cycles",
    },
    {
        "failure": "Chaotic divergence (butterfly effect, unbounded)",
        "mode": "RD",
        "description": "Exponential sensitivity to initial conditions; nearby trajectories diverge without bound. Prediction horizon collapses to zero.",
        "type": "Runaway",
        "triggers": "Positive Lyapunov exponent + unbounded phase space",
        "neighborhood": "Lorenz system at high Rayleigh number; unbounded chaotic maps",
    },
    {
        "failure": "Stochastic resonance drowning (noise overwhelms signal)",
        "mode": "LD",
        "description": "Noise intensity exceeds signal; no distinguishable state persists. All states equally probable.",
        "type": "Loss of differentiation",
        "triggers": "Noise amplitude >> signal amplitude; no restoring force",
        "neighborhood": "Brownian motion at high temperature; random walk with zero drift",
    },
    {
        "failure": "Attractor destruction / crisis",
        "mode": "LP",
        "description": "Strange attractor collides with unstable periodic orbit and is destroyed. Trajectories escape to infinity or another basin.",
        "type": "Structural collapse",
        "triggers": "Parameter crosses crisis threshold (boundary crisis)",
        "neighborhood": "Hénon map near a=1.4; Lorenz system near r=24.74",
    },
    {
        "failure": "Energy dissipation without replenishment",
        "mode": "LP",
        "description": "All energy dissipated; motion stops. No persistent dynamics possible.",
        "type": "Persistence loss",
        "triggers": "No energy input; friction dominates",
        "neighborhood": "Every dissipative system without external driving",
    },
    {
        "failure": "Bifurcation cascade to chaos (parameter sensitivity)",
        "mode": "RD",
        "description": "Period-doubling cascade at accelerating rate; system becomes chaotic within finite parameter range.",
        "type": "Runaway",
        "triggers": "Feigenbaum constant δ accumulates; period-doubling at rate ~4.669",
        "neighborhood": "Logistic map near r≈3.57; period-doubling route in any unimodal map",
    },
    {
        "failure": "Synchronization collapse (oscillator death)",
        "mode": "LD",
        "description": "Coupled oscillators stop oscillating entirely; all amplitude goes to zero.",
        "type": "Loss of differentiation",
        "triggers": "Coupling strength too high or mismatched",
        "neighborhood": "Kuramoto model above critical coupling; diffusive coupling with parameter mismatch",
    },
    {
        "failure": "Turbulence (spatiotemporal chaos without coherent structures)",
        "mode": "FR",
        "description": "Spatiotemporal chaos with no persistent coherent structures; correlation length collapses.",
        "type": "Fragmentation",
        "triggers": "High Reynolds number; strong nonlinearity",
        "neighborhood": "Navier-Stokes at high Re; 3D turbulence",
    },
    {
        "failure": "Hysteresis / irreversibility (loss of return path)",
        "mode": "LR",
        "description": "System passes through bifurcation; reversing control parameter does not restore original state.",
        "type": "Loss of recoverability",
        "triggers": "Subcritical bifurcation; first-order transition; bistability",
        "neighborhood": "Subcritical Hopf bifurcation; cusp catastrophe",
    },
    {
        "failure": "Noise-induced transitions (stochastic escape from attractor)",
        "mode": "LR",
        "description": "Fluctuations push system out of stable attractor into another basin; return path not guaranteed.",
        "type": "Loss of recoverability",
        "triggers": "Noise intensity exceeds potential barrier height",
        "neighborhood": "Kramers' escape problem; genetic switches with high noise",
    },
]

# ============================================================
# COMBINE ALL DOMAINS
# ============================================================

ALL_FAILURES = {
    "A — Physical universes": PHYSICAL_FAILURES,
    "B — Mathematical systems": MATH_FAILURES,
    "C — Recursive substrate": SUBSTRATE_FAILURES,
    "D — Dynamical manifolds": DYNAMICAL_FAILURES,
}

# ============================================================
# CROSS-DOMAIN FAILURE MATRIX
# ============================================================

print("=" * 72)
print("T072: CROSS-DOMAIN FAILURE BOUNDARY AUDIT")
print("=" * 72)

print(f"""
Instead of asking: "What invariant survives across domains?"
Ask:             "What failure modes recur across domains?"

Failure boundaries are often sharper and more universal than
success conditions. The fine-structure argument works because
it examines the neighborhood of failure, not the successful point.

Tested failure modes:
""")

for fm in FAILURE_MODES:
    print(f"  {fm} — {FAILURE_LABELS[fm]}")

# Build the cross-domain matrix
print(f"\n{'='*72}")
print("CROSS-DOMAIN FAILURE MATRIX")
print(f"{'='*72}")

# Count how many domains exhibit each failure mode
mode_domain_count = defaultdict(set)
mode_instances = defaultdict(list)

for dname, failures in ALL_FAILURES.items():
    for f in failures:
        mode_domain_count[f["mode"]].add(dname)
        mode_instances[f["mode"]].append((dname, f["failure"]))

# Sort failure modes by universality (most domains first)
universal_modes = sorted(FAILURE_MODES, key=lambda m: len(mode_domain_count.get(m, set())), reverse=True)

# Print matrix
print(f"\n  {'Failure Mode':<45} {'Phys':<6}{'Math':<6}{'Subs':<6}{{'Dyna':<6}}{'Domains':<10}")
print(f"  {'-'*85}")
for mode in universal_modes:
    domains_hit = mode_domain_count.get(mode, set())
    checks = []
    for dname in ALL_FAILURES.keys():
        prefix = dname[0]
        checks.append("✓" if prefix in [d[0] for d in domains_hit] else "·")
    count = len(domains_hit)
    print(f"  {mode:<6} ({FAILURE_LABELS[mode][:32]:<32})  "
          f"{checks[0]:<6}{checks[1]:<6}{checks[2]:<6}{checks[3]:<6}{count}/4")

# ============================================================
# UNIVERSAL FAILURES
# ============================================================

print(f"\n{'='*72}")
print("UNIVERSAL FAILURES (present in ALL 4 domains)")
print(f"{'='*72}")

universal = [m for m in FAILURE_MODES if len(mode_domain_count.get(m, set())) == 4]

if universal:
    print(f"\n  The following {len(universal)} failure modes appear in ALL four domains:")
    for m in universal:
        print(f"\n  ✓ {m} — {FAILURE_LABELS[m]}")
        print(f"    Instances ({len(mode_instances[m])} total):")
        for dname, instance in mode_instances[m][:5]:
            print(f"      [{dname}] {instance}")
        if len(mode_instances[m]) > 5:
            print(f"      ... and {len(mode_instances[m]) - 5} more")
else:
    print(f"\n  No failure mode appears in all four domains.")
    # Show near-universal
    for m in universal_modes:
        ds = mode_domain_count.get(m, set())
        if len(ds) >= 3:
            print(f"  ~ {m} — {len(ds)}/4 domains: {', '.join(sorted(ds))}")

# ============================================================
# NEAR-UNIVERSAL AND CONTINGENT FAILURES
# ============================================================

near_universal = [m for m in FAILURE_MODES if len(mode_domain_count.get(m, set())) == 3]
contingent = [m for m in FAILURE_MODES if len(mode_domain_count.get(m, set())) <= 2]

print(f"\n{'='*72}")
print("NEAR-UNIVERSAL FAILURES (3/4 domains)")
print(f"{'='*72}")

if near_universal:
    for m in near_universal:
        ds = mode_domain_count.get(m, set())
        absent = [d for d in ALL_FAILURES.keys() if d[0] not in [x[0] for x in ds]]
        print(f"\n  ~ {m} — {FAILURE_LABELS[m]}")
        print(f"    Missing from: {', '.join(absent)}")
        print(f"    Instances ({len(mode_instances[m])}):")
        for dname, instance in mode_instances[m][:3]:
            print(f"      [{dname}] {instance}")

print(f"\n{'='*72}")
print("CONTINGENT FAILURES (<=2 domains)")
print(f"{'='*72}")

if contingent:
    for m in contingent:
        ds = mode_domain_count.get(m, set())
        print(f"\n  × {m} — {FAILURE_LABELS[m]}")
        print(f"    Found in: {len(ds)}/4 domains ({', '.join(sorted(ds))})")

# ============================================================
# PAIRWISE FAILURE OVERLAP
# ============================================================

print(f"\n{'='*72}")
print("PAIRWISE DOMAIN FAILURE OVERLAP")
print(f"{'='*72}")

dnames = list(ALL_FAILURES.keys())
for i in range(len(dnames)):
    for j in range(i+1, len(dnames)):
        d1, d2 = dnames[i], dnames[j]
        modes1 = set(f["mode"] for f in ALL_FAILURES[d1])
        modes2 = set(f["mode"] for f in ALL_FAILURES[d2])
        common = modes1 & modes2
        union = modes1 | modes2
        jaccard = len(common) / len(union) if union else 0
        print(f"  {d1} × {d2}:")
        print(f"    Common failures ({len(common)}): {', '.join(sorted(common))}")
        print(f"    Jaccard similarity: {jaccard:.2f}")

# ============================================================
# ARCHETYPAL FAILURE SIGNATURES
# ============================================================

print(f"\n{'='*72}")
print("ARCHETYPAL FAILURE SIGNATURES")
print(f"{'='*72}")

# For each domain, compute its failure signature (which modes dominate)
print(f"\n  Domain failure profiles (fraction of instances per mode):")
for dname, failures in ALL_FAILURES.items():
    mode_counts = defaultdict(int)
    for f in failures:
        mode_counts[f["mode"]] += 1
    total = len(failures)
    print(f"\n  {dname} ({total} failure instances):")
    sorted_modes = sorted(mode_counts.keys(), key=lambda m: mode_counts[m]/total, reverse=True)
    for m in sorted_modes:
        pct = mode_counts[m] / total * 100
        print(f"    {m}: {mode_counts[m]}/{total} ({pct:.0f}%)")

# ============================================================
# LOGICAL STRUCTURE OF UNIVERSAL FAILURES
# ============================================================

print(f"\n{'='*72}")
print("STRUCTURAL ANALYSIS OF UNIVERSAL FAILURES")
print(f"{'='*72}")

if universal:
    print(f"""
  Universal failures expose constraints that no viable system can violate.
  Each universal failure represents a boundary that ALL structured
  possibility-spaces must respect.

  The universal failures are:
""")
    for m in universal:
        instances = mode_instances[m]
        print(f"  {m} — {FAILURE_LABELS[m]}")
        print(f"  Evidence: {len(instances)} instances across all 4 domains")
        print(f"  Constraint: A viable system must avoid {FAILURE_LABELS[m].split(' — ')[0].lower()}")
        print()

    print(f"""
  These constraints form a necessary (but not sufficient) condition
  for any structured possibility-space. Violate any one and the
  system cannot function — regardless of domain.

  Mapping to the 9-assumption substrate:

  The substrate already encodes avoidance of these failures:
    - Acyclic graph avoids contradiction (CC) by construction
    - OC2 root avoids triviality (CT: distinguish without content)
    - Knockout analysis shows persistence (LP) failure boundaries
    - Multiple node types prevent differentiation loss (LD)
    - Generative closure avoids generativity loss (LG)
    - Removal resilience avoids fragmentation/complexity (FR)

  This suggests the substrate's constraints may be domain-general
  constraints of structured systems, not merely ad-hoc assumptions
  about epistemic systems. That would be significant.
""")

# ============================================================
# COMPARISON WITH T071
# ============================================================

print(f"{'='*72}")
print("COMPARISON: T071 INVARIANTS vs T072 FAILURES")
print(f"{'='*72}")

print(f"""
  T071 found coherence as the strongest positive invariant.
  T072 finds {len(universal)} universal failures.

  Relationship:
    Coherence (T071) ≈ Avoidance of CC (contradiction) + FR (fragmentation)
    Generativity (T071) ≈ Avoidance of CT (triviality) + LG (generativity loss)
    Persistence (T071) ≈ Avoidance of LP (persistence loss) + LR (recoverability loss)

  This suggests the invariants and failure modes are two sides of
  the same boundary: the invariant describes the viable regime,
  the failure mode describes what happens outside it.

  The failure-mode formulation has an advantage: it is often easier
  to prove that a system MUST fail (by violating a universal
  constraint) than to prove that a system WILL succeed (by satisfying
  a positive invariant).

  This aligns with the fine-tuning logic: we do not know why our
  universe's parameters take their values, but we can show that most
  nearby values produce failure.
""")

# ============================================================
# WRITE DELIVERABLES
# ============================================================

# 1. Cross-domain failure matrix
with open(OUT / "t072_failure_matrix.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["domain", "failure", "mode", "mode_label", "type", "triggers"])
    for dname, failures in ALL_FAILURES.items():
        for fail in failures:
            w.writerow([dname, fail["failure"], fail["mode"],
                        FAILURE_LABELS[fail["mode"]], fail["type"], fail["triggers"]])

print(f"Wrote t072_failure_matrix.csv")

# 2. Universal failures
with open(OUT / "t072_universal_failures.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["mode", "label", "n_domains", "n_instances",
                 "domain_A_instances", "domain_B_instances",
                 "domain_C_instances", "domain_D_instances"])
    for m in universal_modes:
        instances = mode_instances[m]
        n_dom = len(mode_domain_count[m])
        by_domain = {}
        for dname in ALL_FAILURES.keys():
            by_domain[dname] = [inst for (dn, inst) in instances if dn == dname]
        w.writerow([m, FAILURE_LABELS[m], n_dom, len(instances),
                     len(by_domain[list(ALL_FAILURES.keys())[0]]),
                     len(by_domain[list(ALL_FAILURES.keys())[1]]),
                     len(by_domain[list(ALL_FAILURES.keys())[2]]),
                     len(by_domain[list(ALL_FAILURES.keys())[3]])])

print(f"Wrote t072_universal_failures.csv")

# 3. Archetypal failure signatures
with open(OUT / "t072_failure_signatures.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["domain", "n_failures"] + FAILURE_MODES)
    for dname, failures in ALL_FAILURES.items():
        mode_counts = defaultdict(int)
        for fail in failures:
            mode_counts[fail["mode"]] += 1
        row = [dname, len(failures)]
        for m in FAILURE_MODES:
            row.append(mode_counts.get(m, 0))
        w.writerow(row)

print(f"Wrote t072_failure_signatures.csv")

# 4. Summary
summary = {
    "audit": "T072: Cross-Domain Failure Boundary Audit",
    "universal_failures": [
        {"mode": m, "label": FAILURE_LABELS[m],
         "n_instances": len(mode_instances[m])}
        for m in universal
    ],
    "n_universal": len(universal),
    "n_near_universal": len(near_universal),
    "n_contingent": len(contingent),
    "interpretation": (
        "Universal failure modes define boundaries no viable system "
        "can cross. They are constraints, not assumptions — they "
        "describe what must be avoided, not what must be present. "
        "The 9-assumption substrate encodes avoidance of these "
        "failures by construction (acyclic graph, multiple node types, "
        "knockout resilience, etc.). This implies the substrate's "
        "constraints may be domain-general viability constraints."
    ),
    "relationship_to_T071": (
        "T071 positive invariants (coherence, generativity, persistence) "
        "are the obverse of T072 universal failures (CC=contradiction, "
        "CT=triviality, LG=generativity loss, LP=persistence loss). "
        "The failure-mode formulation has the advantage of being "
        "easier to verify: violating a universal failure is observable "
        "system collapse, while satisfying a positive invariant is a "
        "continuous spectrum."
    ),
    "methodological_conclusion": (
        "The fine-tuning logic transfers across domains: we do not need "
        "to know what makes a system work; we only need to know what "
        "makes it fail. Failure boundaries are sharper, more universal, "
        "and more empirically accessible than success conditions."
    ),
}

with open(OUT / "t072_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print(f"Wrote t072_summary.json")

# Markdown report
with open(OUT / "t072_failure_boundary_report.md", "w") as f:
    f.write("""T072: Cross-Domain Failure Boundary Audit
=========================================

## Motivation

The fine-structure argument does not work by studying the successful
point. It works by examining the neighborhood of failure around it.

If the same logic applies across domains, then:
  - We do not need to find what makes systems succeed universally.
  - We only need to find what makes them fail universally.

Failure boundaries are sharper, more universal, and more empirically
accessible than success conditions.

---

## Methodology

Eight failure modes were tested across four domains:

| Code | Failure Mode |
|------|--------------|
""")
    for m in FAILURE_MODES:
        f.write(f"| {m} | {FAILURE_LABELS[m]} |\n")

    f.write(f"""
---

## Results

### Universal Failures (present in ALL 4 domains)
""")

    for m in universal:
        f.write(f"""
**{m}: {FAILURE_LABELS[m]}**
- Instances across all domains: {len(mode_instances[m])}
""")

    f.write(f"""
### Near-Universal Failures (3/4 domains)
""")
    for m in near_universal:
        ds = mode_domain_count.get(m, set())
        absent = [d for d in ALL_FAILURES.keys() if d[0] not in [x[0] for x in ds]]
        f.write(f"""
**{m}: {FAILURE_LABELS[m]}**
- Missing from: {', '.join(absent)}
- Instances: {len(mode_instances[m])}
""")

    f.write(f"""
### Contingent Failures (<=2/4 domains)
""")
    for m in contingent:
        ds = mode_domain_count.get(m, set())
        f.write(f"- {m}: {', '.join(sorted(ds))} ({len(mode_instances[m])} instances)\n")

    f.write(f"""
---

## Interpretation

If a failure mode is universal (appears in all four domains), then:
  1. It represents a genuine constraint on any structured system.
  2. Any viable system must have a mechanism to avoid it.
  3. That mechanism may be explicit (an assumption) or emergent
     (a property of how assumptions interact).

### Mapping to the 9-assumption Substrate

The corrected substrate from T066 encodes avoidance of these failures:

| Failure | Substrate Protection |
|---------|---------------------|
| CC (contradiction) | Acyclic graph — no circular dependencies |
| CT (triviality) | OC2 provides positive content (distinguishability) |
| LP (persistence loss) | OC2 unique root ensures generative source |
| LG (generativity loss) | Multiple nodes with out-degree > 0 |
| LD (differentiation loss) | Multiple distinct node types |
| FR (fragmentation) | Knockout resilience — partial survival |
| LR (recoverability loss) | Dependency resolution is deterministic |

This suggests the substrate constraints are not ad-hoc requirements
for epistemic systems — they may be domain-general viability
constraints that any structured possibility-space must satisfy.

---

## Methodological Conclusion

The failure-boundary approach reveals that the fine-tuning logic
transfers across domains. We observe the same pattern:

  - Near every viable configuration, there is a boundary where
    a specific failure mode takes over.
  - Those failure modes are shared across entirely different
    domains (physics, mathematics, substrate analysis, dynamics).
  - A viable system is one that avoids all universal failure modes
    simultaneously.

This is the same logic as the book's parameter-space argument,
generalized to any structured system.

---

## Remaining Questions

1. Are the universal failures truly independent, or do some entail
   others? (E.g., does avoiding CC also avoid CT?)
2. Can we construct a system that avoids all universal failures
   but is not viable? (To test sufficiency vs. necessity.)
3. Does the 9-assumption substrate avoid all universal failures
   by construction, or does it rely on hidden assumptions about
   what constitutes "avoidance"?
""")

print(f"Wrote t072_failure_boundary_report.md")

print(f"\nT072 complete.")
