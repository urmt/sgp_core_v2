#!/usr/bin/env python3
"""
T079: Meta-Constraint Inference
================================
Infer the minimal set of meta-constraints that would generate the observed
terrain from T072–T078.

No substrate assumptions. No OC2. No mechanism reasoning.

We treat the T078 manifold as the observed terrain and ask:
  What constraints would have to exist for that terrain to arise?

Candidate classes (MC1–MC5):
  MC1 — Information Preservation:   systems survive only when structure is retained
  MC2 — Productive Transformation:  systems must generate novel structure
  MC3 — Constraint Balance:         too much freedom collapses, too much rigidity sterilizes
  MC4 — Recursive Accessibility:    systems unable to act on internal structure lose fertility
  MC5 — Recoverable Perturbation:   successful systems absorb disruption without permanent collapse
"""

import csv, json, math, itertools
from pathlib import Path
from collections import defaultdict

OUT = Path("/home/student/sgp_core_v2/sfh_sgp_ood_outputs")

# ============================================================
# OBSERVED FINDINGS (from T072–T078)
# ============================================================

FINDINGS = [
    # T072 — Failure Boundaries
    {"id": "F01", "source": "T072", "finding": "Generativity loss is a universal failure mode across all 4 domains"},
    {"id": "F02", "source": "T072", "finding": "Fragmentation is a universal failure mode"},
    {"id": "F03", "source": "T072", "finding": "5/6 failure classes (F1–F6) are universal; only F4 (runaway divergence) is domain-contingent"},
    {"id": "F04", "source": "T072", "finding": "Failure boundaries are sharper than success conditions"},

    # T073 — Viability Basin
    {"id": "F05", "source": "T073", "finding": "Viability constraints are ABOVE the substrate, not beneath it"},
    {"id": "F06", "source": "T073", "finding": "Three-layer architecture: Viability Basin → Mechanisms → Substrate"},
    {"id": "F07", "source": "T073", "finding": "C ≥ 0.75, P ≥ 0.65, G ≥ 0.40, R ≥ 0.30, S ≥ 0.10 defines viability basin"},
    {"id": "F08", "source": "T073", "finding": "Minimal constraint set rejects 100% nonviable with 0 false positives"},

    # T074 — Fertility
    {"id": "F09", "source": "T074", "finding": "RC (Recombination Capacity) is the best discriminator of fertile vs merely-viable"},
    {"id": "F10", "source": "T074", "finding": "Fertile signature: SR≥0.7, NP≥0.7, RC≥0.6, RD≥0.3, OE≥0.6"},
    {"id": "F11", "source": "T074", "finding": "Fertility is partially independent of viability"},
    {"id": "F12", "source": "T074", "finding": "Fertile systems show higher generativity but slightly lower coherence/recoverability"},

    # T075 — Stability/Fertility Tradeoff
    {"id": "F13", "source": "T075", "finding": "Stability and fertility are negatively coupled within viable region (r=-0.331)"},
    {"id": "F14", "source": "T075", "finding": "Boundary regime: fertile systems cluster at intermediate stability, not maximum"},
    {"id": "F15", "source": "T075", "finding": "Maximum fertility occurs at stability 0.72, not at maximum stability"},
    {"id": "F16", "source": "T075", "finding": "Edge-of-chaos quadrant (LS/HF) largest at 35% of viable systems"},

    # T076 — Boundary Geometry
    {"id": "F17", "source": "T076", "finding": "Fertile corridor with finite measurable width exists in ALL domains"},
    {"id": "F18", "source": "T076", "finding": "Corridor widths cluster near 0.05–0.10 in all domains"},
    {"id": "F19", "source": "T076", "finding": "Three-zone landscape: Collapse → Fertile Corridor → Fortress"},
    {"id": "F20", "source": "T076", "finding": "Collapse-to-viable transition is very steep in physics (9.3) and dynamics (16.5)"},
    {"id": "F21", "source": "T076", "finding": "Axis profiles show consistent progression: collapse < fortress < fertile for most axes"},

    # T077 — Attractor Dynamics
    {"id": "F22", "source": "T077", "finding": "Fertile corridor is NOT a universal attractor; 3/4 domains are saddles"},
    {"id": "F23", "source": "T077", "finding": "Drift is predominantly collapse-ward (3/4 domains)"},
    {"id": "F24", "source": "T077", "finding": "Recursive substrate is exceptional — shows near-attractor properties"},
    {"id": "F25", "source": "T077", "finding": "Fertile corridor persists even when attractors do not"},
    {"id": "F26", "source": "T077", "finding": "S gap (self-modeling) separates fertile from fortress (+0.25 to +0.65)"},

    # T078 — Meta-Space Reconstruction
    {"id": "F27", "source": "T078", "finding": "10 metrics compress to 2 latent dimensions (92.6% variance)"},
    {"id": "F28", "source": "T078", "finding": "PC1 (75.1%) = generative capacity; PC2 (17.5%) = structural stability"},
    {"id": "F29", "source": "T078", "finding": "Fertile corridor is a SINGLE connected region in latent space"},
    {"id": "F30", "source": "T078", "finding": "All 4 domains share the same fertile region in latent space (centroid offsets 0.08–0.26)"},
    {"id": "F31", "source": "T078", "finding": "Fertile corridor survives dimensional compression (90% classification in 2D)"},
    {"id": "F32", "source": "T078", "finding": "Recursive depth (RD) and self-modeling (S) form a separate minor axis (PC3)"},
]

# ============================================================
# CANDIDATE META-CONSTRAINTS
# ============================================================

CONSTRAINTS = [
    {
        "id": "MC1",
        "name": "Information Preservation",
        "formulation": "Systems survive only when structure can be retained across transitions",
        "mechanism": "If structure is lost, the system must start over — costs accumulate, generativity fails",
        "predicts": [
            "Collapse region exists (systems with no retention cannot persist)",
            "Recoverability is a viability axis (R ≥ 0.30)",
            "Coherence is a viability axis (C ≥ 0.75)",
            "Fragmentation is a universal failure mode",
            "Generativity loss is a universal failure mode",
        ],
    },
    {
        "id": "MC2",
        "name": "Productive Transformation",
        "formulation": "Systems must be able to generate novel structure from existing structure",
        "mechanism": "Without novelty generation, systems are sterile — they persist but cannot adapt or evolve",
        "predicts": [
            "Fortress region exists (high stability, no novelty)",
            "Generativity is a viability axis (G ≥ 0.40)",
            "Generativity loss is a universal failure mode",
            "RC (recombination) is the best fertility discriminator",
            "PC1 dominated by fertility axes (SR, NP, RC, RD, OE)",
        ],
    },
    {
        "id": "MC3",
        "name": "Constraint Balance",
        "formulation": "Too much freedom causes collapse; too much rigidity causes sterility",
        "mechanism": "Systems require bounded freedom — enough constraint for structure, enough freedom for novelty",
        "predicts": [
            "Boundary regime: fertile at intermediate stability, not extremes",
            "Fertile corridor has finite width (not a point, not the whole space)",
            "Negative correlation between stability and fertility in viable region",
            "Three-zone landscape: collapse ↔ fertile ↔ fortress",
            "Edge-of-chaos quadrant is largest (35%)",
            "Collapse-ward drift is dominant (freedom failure more common than rigidity failure)",
        ],
    },
    {
        "id": "MC4",
        "name": "Recursive Accessibility",
        "formulation": "Systems unable to act upon their own internal structure lose fertility",
        "mechanism": "Self-modeling enables self-correction, adaptation, and higher-order recombination",
        "predicts": [
            "Self-modeling (S) is a viability axis (S ≥ 0.10)",
            "S gap separates fertile from fortress (+0.25 to +0.65)",
            "Recursive substrate shows exceptional near-attractor properties",
            "Recursive depth (RD) loads on minor axis PC3 with self-modeling (S)",
            "Fertile systems have higher self-modeling than merely-viable",
            "Fertility corridor exists (requires self-correction to stay in corridor)",
        ],
    },
    {
        "id": "MC5",
        "name": "Recoverable Perturbation",
        "formulation": "Successful systems must absorb disruption without permanent collapse",
        "mechanism": "Systems that cannot recover from perturbation will eventually be destroyed by it",
        "predicts": [
            "Viability basin includes recoverability (R ≥ 0.30)",
            "Fertility corridor is saddle-like (systems can leave but can return)",
            "Recursive substrate shows highest recovery potential (0.238)",
            "Failure boundaries are sharper than success conditions",
            "Fertile systems have moderate recoverability (lower than fortress, higher than collapse)",
            "Fertile corridor persists across perturbations (corridor not destroyed by disruptions)",
        ],
    },
]

# ============================================================
# CONSTRAINT-FINDING MATRIX
# ============================================================

print("=" * 72)
print("T079: META-CONSTRAINT INFERENCE")
print("=" * 72)

print(f"\n  {len(CONSTRAINTS)} candidate meta-constraints × {len(FINDINGS)} observed findings")
print(f"  All scores independent of substrate assumptions.\n")

# Score each constraint against each finding
# +1 = supports (finding is predicted by or consistent with the constraint)
#  0 = neutral (no clear relationship)
# -1 = contradicts (finding would not be expected under this constraint)

# We need domain expertise for this scoring. Let's think carefully.
# MC1 (Info Preservation): structure retention
# MC2 (Productive Transformation): novelty generation
# MC3 (Constraint Balance): bounded freedom
# MC4 (Recursive Accessibility): self-modeling
# MC5 (Recoverable Perturbation): disruption absorption

SCORES = {
    # MC1 — Information Preservation
    "MC1": {
        "F01": +1,  # generativity loss — structure retention prevents this
        "F02": +1,  # fragmentation — prevents structure retention
        "F03": +1,  # universal failure classes — info preservation is universal need
        "F04": +1,  # failure sharper than success — losing structure is catastrophic
        "F05": 0,   # viability above substrate — neutral
        "F06": 0,   # three-layer architecture — neutral
        "F07": +1,  # C≥0.75, R≥0.30 — coherence and recoverability are about retention
        "F08": 0,   # minimal set accuracy — neutral
        "F09": -1,  # RC is best discriminator — recombination is NOT about preservation
        "F10": -1,  # fertile signature includes RC, NP, OE — novelty, not preservation
        "F11": 0,   # fertility independent of viability — neutral
        "F12": -1,  # fertile lower coherence — contradicts priority on preservation
        "F13": 0,   # negative stab-fert corr — neutral
        "F14": -1,  # boundary regime — info preservation predicts monotonic, not boundary
        "F15": -1,  # max fertility at 0.72 — not at maximum stability (preservation)
        "F16": -1,  # edge of chaos largest — preservation predicts stability focus
        "F17": 0,   # fertile corridor exists — neutral
        "F18": 0,   # corridor width — neutral
        "F19": 0,   # three-zone landscape — neutral
        "F20": 0,   # collapse transition steep — neutral
        "F21": +1,  # consistent progression — preservation creates order
        "F22": -1,  # not an attractor — preservation should attract to stable
        "F23": -1,  # collapse drift — preservation should prevent this
        "F24": -1,  # recursive exceptional — should apply equally
        "F25": 0,   # corridor persists — neutral
        "F26": 0,   # S gap — neutral
        "F27": 0,   # 2 latent dimensions — neutral
        "F28": -1,  # PC1 = generative capacity — should be stability-centered
        "F29": 0,   # connected fertile region — neutral
        "F30": 0,   # domain-independent — neutral
        "F31": 0,   # survives compression — neutral
        "F32": -1,  # RD and S on PC3 — should be primary, not minor
    },
    # MC2 — Productive Transformation
    "MC2": {
        "F01": +1,  # generativity loss — productive transformation prevents this
        "F02": 0,   # fragmentation — neutral
        "F03": 0,   # universal failure — neutral
        "F04": 0,   # failure sharper — neutral
        "F05": 0,   # viability above substrate — neutral
        "F06": 0,   # three-layer — neutral
        "F07": +1,  # G≥0.40 — generativity required for viability
        "F08": 0,   # minimal set — neutral
        "F09": +1,  # RC best discriminator — transformation through recombination
        "F10": +1,  # fertile signature — novelty axes all high
        "F11": +1,  # fertility independent — transformation adds value beyond viability
        "F12": +1,  # fertile higher generativity — predicted by MC2
        "F13": 0,   # negative correlation — neutral
        "F14": +1,  # boundary regime — transformation requires freedom
        "F15": +1,  # max fertility at 0.72 — not at max stability (would kill transformation)
        "F16": +1,  # edge of chaos — transformation needs instability
        "F17": +1,  # fertile corridor exists — transformation creates the corridor
        "F18": 0,   # corridor width — neutral
        "F19": +1,  # three-zone — transformation explains the zones
        "F20": 0,   # collapse steep — neutral
        "F21": +1,  # consistent progression — transformation varies by degree
        "F22": +1,  # not an attractor — transformation is active, not convergent
        "F23": 0,   # collapse drift — neutral
        "F24": 0,   # recursive exceptional — neutral
        "F25": +1,  # corridor persists — transformation maintains it
        "F26": 0,   # S gap — neutral
        "F27": +1,  # 2 latent dims — transformation dynamics compress
        "F28": +1,  # PC1 = generative capacity — PRIMARY prediction
        "F29": +1,  # connected fertile region — transformation unifies
        "F30": +1,  # domain-independent — transformation is universal
        "F31": +1,  # survives compression — transformation is fundamental
        "F32": 0,   # RD and S on PC3 — neutral
    },
    # MC3 — Constraint Balance
    "MC3": {
        "F01": +1,  # generativity loss — balance prevents total loss
        "F02": +1,  # fragmentation — imbalance causes fragmentation
        "F03": +1,  # universal failure — imbalance is universal risk
        "F04": +1,  # failure sharper — imbalance is catastrophic
        "F05": 0,   # viability above substrate — neutral
        "F06": 0,   # three-layer — neutral
        "F07": +1,  # viability criteria — each axis is a balance point
        "F08": +1,  # minimal set works — balance creates clean separation
        "F09": 0,   # RC best discriminator — neutral
        "F10": 0,   # fertile signature — neutral
        "F11": +1,  # fertility independent — balance is not the same as viability
        "F12": +1,  # fertile lower coherence — predicted tradeoff
        "F13": +1,  # negative stab-fert corr — CORE prediction of balance
        "F14": +1,  # boundary regime — CORE prediction
        "F15": +1,  # max fertility at 0.72 — CORE prediction
        "F16": +1,  # edge of chaos largest — CORE prediction
        "F17": +1,  # fertile corridor — CORE prediction of balance
        "F18": +1,  # finite corridor width — CORE prediction
        "F19": +1,  # three-zone — CORE prediction
        "F20": 0,   # collapse steep — neutral
        "F21": +1,  # consistent progression — balance creates order
        "F22": +1,  # not an attractor — balance is maintained, not automatic
        "F23": +1,  # collapse drift — imbalance tilts one way
        "F24": 0,   # recursive exceptional — neutral
        "F25": +1,  # corridor persists — balance resists disruption
        "F26": 0,   # S gap — neutral
        "F27": 0,   # 2 latent dims — neutral
        "F28": 0,   # PC1 generative — neutral
        "F29": +1,  # connected region — balance creates single corridor
        "F30": +1,  # domain-independent — balance is universal
        "F31": +1,  # survives compression — balance is fundamental
        "F32": 0,   # RD and S — neutral
    },
    # MC4 — Recursive Accessibility
    "MC4": {
        "F01": 0,   # generativity loss — neutral (recursion enables, not required)
        "F02": 0,   # fragmentation — neutral
        "F03": 0,   # universal failure — neutral
        "F04": 0,   # failure sharper — neutral
        "F05": 0,   # viability substrate — neutral
        "F06": 0,   # three-layer — neutral
        "F07": +1,  # S≥0.10 — self-modeling required
        "F08": 0,   # minimal set — neutral
        "F09": 0,   # RC discriminator — neutral (recombination ≠ recursion)
        "F10": +1,  # RD≥0.3 in fertile signature — recursion depth needed
        "F11": 0,   # fertility independent — neutral
        "F12": 0,   # fertile lower coherence — neutral
        "F13": 0,   # negative correlation — neutral
        "F14": 0,   # boundary regime — neutral
        "F15": 0,   # max fertility — neutral
        "F16": 0,   # edge of chaos — neutral
        "F17": 0,   # fertile corridor — neutral
        "F18": 0,   # corridor width — neutral
        "F19": 0,   # three-zone — neutral
        "F20": 0,   # collapse steep — neutral
        "F21": 0,   # consistent progression — neutral
        "F22": 0,   # not an attractor — neutral
        "F23": 0,   # collapse drift — neutral
        "F24": +1,  # recursive exceptional — CORE prediction
        "F25": 0,   # corridor persists — neutral
        "F26": +1,  # S gap separates fertile from fortress — CORE prediction
        "F27": 0,   # 2 latent dims — neutral
        "F28": 0,   # PC1 = generative — neutral
        "F29": 0,   # connected region — neutral
        "F30": 0,   # domain-independent — neutral
        "F31": 0,   # survives compression — neutral
        "F32": +1,  # RD and S on PC3 — CORE prediction (they form their own axis)
    },
    # MC5 — Recoverable Perturbation
    "MC5": {
        "F01": +1,  # generativity loss — lack of recovery leads to loss
        "F02": +1,  # fragmentation — unrecovered fragmentation compounds
        "F03": +1,  # universal failure — recovery needed universally
        "F04": +1,  # failure sharper — failed recovery is decisive
        "F05": 0,   # viability substrate — neutral
        "F06": 0,   # three-layer — neutral
        "F07": +1,  # R≥0.30 — recoverability required
        "F08": 0,   # minimal set — neutral
        "F09": 0,   # RC discriminator — neutral
        "F10": 0,   # fertile signature — neutral
        "F11": +1,  # fertility independent — recovery is not the same as survival
        "F12": +1,  # fertile lower recoverability — tradeoff predicted
        "F13": 0,   # negative correlation — neutral
        "F14": 0,   # boundary regime — neutral
        "F15": 0,   # max fertility — neutral
        "F16": 0,   # edge of chaos — neutral
        "F17": +1,  # corridor exists — recovery maintains occupancy
        "F18": 0,   # corridor width — neutral
        "F19": +1,  # three-zone — recovery defines zone boundaries
        "F20": 0,   # collapse steep — neutral
        "F21": +1,  # consistent progression — recovery varies across zones
        "F22": +1,  # not an attractor — recovery ≠ attraction
        "F23": 0,   # collapse drift — neutral
        "F24": +1,  # recursive exceptional — recursion enables best recovery
        "F25": +1,  # corridor persists — recovery maintains it
        "F26": 0,   # S gap — neutral
        "F27": 0,   # 2 latent dims — neutral
        "F28": 0,   # PC1 generative — neutral
        "F29": 0,   # connected region — neutral
        "F30": 0,   # domain-independent — neutral
        "F31": 0,   # survives compression — neutral
        "F32": 0,   # RD and S — neutral
    },
}

def score_row(mc_id, finding_id):
    return SCORES.get(mc_id, {}).get(finding_id, 0)

# ============================================================
# ANALYSIS
# ============================================================

print(f"\n{'='*72}")
print("CONSTRAINT-FINDING SCORING MATRIX")
print(f"{'='*72}")

print(f"\n  Row: finding | Column: MC1–MC5 | Score: +1 (supports), 0 (neutral), -1 (contradicts)")
print(f"\n  {'Finding':<8}{'Description':<60}{'MC1':<6}{'MC2':<6}{'MC3':<6}{'MC4':<6}{'MC5':<6}")
print(f"  {'-'*98}")

for f in FINDINGS:
    fid = f["id"]
    desc = f["finding"][:58]
    mc1 = score_row("MC1", fid)
    mc2 = score_row("MC2", fid)
    mc3 = score_row("MC3", fid)
    mc4 = score_row("MC4", fid)
    mc5 = score_row("MC5", fid)
    score_str = f"{mc1:+d}{mc2:+d}{mc3:+d}{mc4:+d}{mc5:+d}"
    print(f"  {fid:<8}{desc:<60}{mc1:<+6}{mc2:<+6}{mc3:<+6}{mc4:<+6}{mc5:<+6}")

# ============================================================
# CONSTRAINT RANKING
# ============================================================

print(f"\n{'='*72}")
print("CONSTRAINT RANKING")
print(f"{'='*72}")

mc_scores = {}
for mc in CONSTRAINTS:
    mc_id = mc["id"]
    total = sum(score_row(mc_id, f["id"]) for f in FINDINGS)
    supports = sum(1 for f in FINDINGS if score_row(mc_id, f["id"]) == 1)
    contradictions = sum(1 for f in FINDINGS if score_row(mc_id, f["id"]) == -1)
    neutrals = sum(1 for f in FINDINGS if score_row(mc_id, f["id"]) == 0)
    mc_scores[mc_id] = {
        "total": total,
        "supports": supports,
        "contradictions": contradictions,
        "neutrals": neutrals,
        "robustness": supports / max(1, supports + contradictions),
        "coverage": supports / len(FINDINGS),
    }

print(f"\n  {'Rank':<6}{'Constraint':<30}{'Total':<8}{'Support':<10}{'Against':<10}{'Neutral':<10}{'Robust':<10}{'Coverage':<10}")
print(f"  {'-'*94}")
ranked = sorted(CONSTRAINTS, key=lambda mc: mc_scores[mc["id"]]["total"], reverse=True)
for i, mc in enumerate(ranked):
    ms = mc_scores[mc["id"]]
    print(f"  {i+1:<6}{mc['id']+': '+mc['name']:<30}"
          f"{ms['total']:<+8}{ms['supports']:<10}{ms['contradictions']:<10}"
          f"{ms['neutrals']:<10}{ms['robustness']:<10.2f}{ms['coverage']:<10.2f}")

# ============================================================
# MINIMAL CONSTRAINT SET
# ============================================================

print(f"\n{'='*72}")
print("MINIMAL CONSTRAINT SET SEARCH")
print(f"{'='*72}")

# Search for smallest set that covers all findings with positive support
# "Covers" = at least one constraint in the set scores +1 for the finding
finding_ids = [f["id"] for f in FINDINGS]
mc_ids = [mc["id"] for mc in CONSTRAINTS]

def set_covers(mc_subset):
    """Check if a subset of constraints covers all findings positively."""
    covered = set()
    for mc_id in mc_subset:
        for fid in finding_ids:
            if score_row(mc_id, fid) == 1:
                covered.add(fid)
    return covered

print(f"\n  Searching for minimal constraint set...")
print(f"  All findings must be positively covered by at least one constraint.\n")

# Try all subsets from size 1 upward
found_minimal = None
for size in range(1, len(mc_ids) + 1):
    for subset in itertools.combinations(mc_ids, size):
        covered = set_covers(subset)
        if len(covered) == len(finding_ids):
            found_minimal = subset
            break
    if found_minimal:
        break

if found_minimal:
    print(f"  Minimal constraint set (size {len(found_minimal)}):")
    for mc_id in found_minimal:
        mc = next(m for m in CONSTRAINTS if m["id"] == mc_id)
        ms = mc_scores[mc_id]
        print(f"    {mc_id}: {mc['name']} "
              f"(total={ms['total']:+d}, supports={ms['supports']}, against={ms['contradictions']})")
else:
    print(f"  No single set covers all findings. Partial coverage:")
    # Show best coverage for single constraints
    for mc in sorted(CONSTRAINTS, key=lambda m: len(set_covers([m["id"]])), reverse=True):
        covered = len(set_covers([mc["id"]]))
        print(f"    {mc['id']}: {covered}/{len(finding_ids)} findings covered")

# Uncovered findings (even with minimal set)
if found_minimal:
    uncovered = []
    for fid in finding_ids:
        covered = any(score_row(mc_id, fid) == 1 for mc_id in found_minimal)
        if not covered:
            uncovered.append(fid)
    if uncovered:
        print(f"\n  WARNING: {len(uncovered)} findings uncovered by minimal set:")
        for fid in uncovered:
            f = next(x for x in FINDINGS if x["id"] == fid)
            print(f"    {fid}: {f['finding']}")
    else:
        print(f"\n  All findings covered by minimal set.")

# ============================================================
# SUBSTRATE-INDEPENDENCE TEST
# ============================================================

print(f"\n{'='*72}")
print("SUBSTRATE-INDEPENDENCE TEST")
print(f"{'='*72}")

# Which constraints would survive if substrate-specific findings
# (F05, F06, F24, F32) were removed?
substrate_dependent_findings = ["F05", "F06", "F24", "F32"]
remaining_findings = [f for f in FINDINGS if f["id"] not in substrate_dependent_findings]

print(f"\n  Removing substrate-specific findings: {', '.join(substrate_dependent_findings)}")
print(f"  Remaining: {len(remaining_findings)} findings\n")

# Re-score without substrate findings
mc_independent = {}
for mc in CONSTRAINTS:
    mc_id = mc["id"]
    supports = sum(1 for f in remaining_findings if score_row(mc_id, f["id"]) == 1)
    contradictions = sum(1 for f in remaining_findings if score_row(mc_id, f["id"]) == -1)
    mc_independent[mc_id] = {
        "supports": supports,
        "contradictions": contradictions,
        "net": supports - contradictions,
    }

print(f"  {'Constraint':<30}{'Supports':<12}{'Against':<12}{'Net':<10}")
print(f"  {'-'*64}")
for mc in sorted(CONSTRAINTS, key=lambda m: mc_independent[m["id"]]["net"], reverse=True):
    ms = mc_independent[mc["id"]]
    print(f"  {mc['id']+': '+mc['name']:<30}{ms['supports']:<12}{ms['contradictions']:<12}{ms['net']:<+10}")

survivors = [mc for mc in CONSTRAINTS if mc_independent[mc["id"]]["net"] > 0]
print(f"\n  Survivors (positive net score without substrate): {len(survivors)}")
for mc in survivors:
    print(f"    ✓ {mc['id']}: {mc['name']}")
if len(survivors) < len(CONSTRAINTS):
    eliminated = [mc for mc in CONSTRAINTS if mc_independent[mc["id"]]["net"] <= 0]
    print(f"  Eliminated:")
    for mc in eliminated:
        print(f"    ✗ {mc['id']}: {mc['name']}")

# ============================================================
# CROSS-DOMAIN UNIVERSALITY
# ============================================================

print(f"\n{'='*72}")
print("CROSS-DOMAIN UNIVERSALITY OF CONSTRAINTS")
print(f"{'='*72}")

# All constraints should be domain-independent — they're meta-constraints
# But some findings are domain-specific. Check which constraints
# are consistent with cross-domain findings.

cross_domain_findings = [f for f in FINDINGS if "all" in f["finding"].lower() or "universal" in f["finding"].lower() or "domain-independent" in f["finding"].lower() or "all 4" in f["finding"].lower()]
if not cross_domain_findings:
    # Manually select cross-domain findings
    cross_domain_ids = {"F01", "F03", "F05", "F06", "F17", "F18", "F19", "F22", "F25", "F27", "F29", "F30", "F31"}
    cross_domain_findings = [f for f in FINDINGS if f["id"] in cross_domain_ids]

print(f"\n  Cross-domain findings ({len(cross_domain_findings)}):")
for f in cross_domain_findings:
    print(f"    {f['id']}: {f['finding'][:70]}")

print(f"\n  Constraint universality (support for cross-domain findings):")
print(f"  {'Constraint':<30}{'Cross supports':<16}{'Cross coverage':<16}")
print(f"  {'-'*62}")
for mc in sorted(CONSTRAINTS, key=lambda m: mc_scores[m["id"]]["total"], reverse=True):
    mc_id = mc["id"]
    cross_supports = sum(1 for f in cross_domain_findings if score_row(mc_id, f["id"]) == 1)
    cross_total = len(cross_domain_findings)
    print(f"  {mc_id+': '+mc['name']:<30}{cross_supports:<16}{f'{cross_supports/cross_total:.2f}':<16}")

# ============================================================
# CONSTRAINT SYNERGY ANALYSIS
# ============================================================

print(f"\n{'='*72}")
print("CONSTRAINT SYNERGY ANALYSIS")
print(f"{'='*72}")

# Check pairwise synergies: do pairs of constraints cover more findings together?
print(f"\n  Pairwise coverage (unique findings covered by each pair):")
pairs = list(itertools.combinations(mc_ids, 2))
pair_scores = []
for p in pairs:
    covered = set_covers(p)
    pair_scores.append((p, len(covered)))
pair_scores.sort(key=lambda x: x[1], reverse=True)

print(f"  {'Pair':<15}{'Unique Coverage':<20}")
print(f"  {'-'*35}")
for p, score in pair_scores[:5]:
    print(f"  {p[0]}+{p[1]:<8}{score}/{len(finding_ids)}")

# Best synergy: which pair has the highest joint coverage?
best_pair, best_score = pair_scores[0]
print(f"\n  Best synergy: {best_pair[0]}+{best_pair[1]} "
      f"({best_score}/{len(finding_ids)} findings)")
# What does each add uniquely?
indiv_coverages = [(mc_id, len(set_covers([mc_id]))) for mc_id in mc_ids]
for mc_id in best_pair:
    alone = len(set_covers([mc_id]))
    print(f"    {mc_id} alone: {alone}/{len(finding_ids)}")

# ============================================================
# WRITE DELIVERABLES
# ============================================================

# 1. Full constraint matrix
with open(OUT / "t079_constraint_matrix.csv", "w", newline="") as f:
    w = csv.writer(f)
    header = ["finding_id", "finding"] + [mc["id"] for mc in CONSTRAINTS] + ["total"]
    w.writerow(header)
    for finding in FINDINGS:
        fid = finding["id"]
        row = [fid, finding["finding"]]
        total = 0
        for mc in CONSTRAINTS:
            s = score_row(mc["id"], fid)
            row.append(s)
            total += s
        row.append(total)
        w.writerow(row)

print(f"\nWrote t079_constraint_matrix.csv")

# 2. Meta-constraint scores
with open(OUT / "t079_meta_constraints.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["constraint_id", "name", "formulation", "total_score",
                 "supports", "contradictions", "neutrals",
                 "robustness", "coverage",
                 "substrate_independent_net",
                 "cross_domain_coverage"])
    for mc in CONSTRAINTS:
        ms = mc_scores[mc["id"]]
        si = mc_independent[mc["id"]]["net"]
        cd = sum(1 for f in cross_domain_findings if score_row(mc["id"], f["id"]) == 1) / max(1, len(cross_domain_findings))
        w.writerow([mc["id"], mc["name"], mc["formulation"],
                     ms["total"], ms["supports"], ms["contradictions"], ms["neutrals"],
                     round(ms["robustness"], 3), round(ms["coverage"], 3),
                     si, round(cd, 3)])

print(f"Wrote t079_meta_constraints.csv")

# 3. Minimal constraint set
with open(OUT / "t079_minimal_constraint_set.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["rank", "constraint_id", "name", "total_score",
                 "single_coverage"])
    for i, mc in enumerate(ranked):
        ms = mc_scores[mc["id"]]
        alone = len(set_covers([mc["id"]]))
        w.writerow([i+1, mc["id"], mc["name"],
                     ms["total"], f"{alone}/{len(finding_ids)}"])

print(f"Wrote t079_minimal_constraint_set.csv")

# 4. Summary JSON
summary = {
    "audit": "T079 — Meta-Constraint Inference",
    "n_constraints": len(CONSTRAINTS),
    "n_findings": len(FINDINGS),
    "constraint_ranking": [
        {
            "id": mc["id"],
            "name": mc["name"],
            "total_score": mc_scores[mc["id"]]["total"],
            "supports": mc_scores[mc["id"]]["supports"],
            "contradictions": mc_scores[mc["id"]]["contradictions"],
            "robustness": mc_scores[mc["id"]]["robustness"],
            "coverage": mc_scores[mc["id"]]["coverage"],
        }
        for mc in ranked
    ],
    "minimal_constraint_set": list(found_minimal) if found_minimal else None,
    "minimal_set_size": len(found_minimal) if found_minimal else None,
    "minimal_set_covers_all": len(set_covers(found_minimal)) == len(finding_ids) if found_minimal else False,
    "substrate_independent_survivors": [
        {"id": mc["id"], "name": mc["name"], "net": mc_independent[mc["id"]]["net"]}
        for mc in survivors
    ],
    "substrate_eliminated": [
        {"id": mc["id"], "name": mc["name"], "net": mc_independent[mc["id"]]["net"]}
        for mc in eliminated
    ] if len(survivors) < len(CONSTRAINTS) else [],
    "best_pair_synergy": {
        "pair": list(best_pair),
        "coverage": f"{best_score}/{len(finding_ids)}",
    },
    "conclusion": (
        f"The highest-ranked constraint is {ranked[0]['id']}: {ranked[0]['name']} "
        f"(score={mc_scores[ranked[0]['id']]['total']:+d}). "
        + (f"The minimal constraint set requires {len(found_minimal)} constraint(s): "
           f"{', '.join(found_minimal)}."
           if found_minimal else "No single minimal set found.")
        + f" After removing substrate-specific findings, {len(survivors)} constraint(s) survive: "
        + ", ".join(mc["id"] for mc in survivors) + "."
    ),
}

with open(OUT / "t079_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print(f"Wrote t079_summary.json")

# 5. Constraint report (markdown)
with open(OUT / "t079_constraint_report.md", "w") as f:
    f.write("""T079: Meta-Constraint Inference — Report
========================================

## Method

32 findings from T072–T078 were scored against 5 candidate meta-constraints.

Scoring: +1 = supports (finding predicted or consistent)
         0  = neutral (no clear relationship)
         -1 = contradicts (finding would not be expected)

No substrate assumptions. No OC2. No mechanism reasoning.

---

## Constraint Ranking

| Rank | Constraint | Score | Supports | Against | Robustness | Coverage |
|------|-----------|-------|----------|---------|------------|----------|
""")
    for i, mc in enumerate(ranked):
        ms = mc_scores[mc["id"]]
        f.write(f"| {i+1} | {mc['id']}: {mc['name']} | {ms['total']:+d} | {ms['supports']} | {ms['contradictions']} | {ms['robustness']:.2f} | {ms['coverage']:.2f} |\n")

    f.write(f"""

---

## Minimal Constraint Set

""")
    if found_minimal:
        f.write(f"Minimal set (size {len(found_minimal)}): {', '.join(found_minimal)}\n\n")
        for mc_id in found_minimal:
            mc = next(m for m in CONSTRAINTS if m["id"] == mc_id)
            f.write(f"**{mc_id}**: {mc['name']}\n")
            f.write(f"{mc['formulation']}\n\n")
    else:
        f.write("No single minimal set covers all findings.\n")

    f.write("""
## Substrate Independence Test

Findings removed: F05 (viability above substrate), F06 (three-layer architecture),
F24 (recursive exceptional), F32 (RD/S on PC3).

""")
    f.write(f"Survivors (positive net without substrate): {len(survivors)}\n")
    for mc in survivors:
        f.write(f"- ✓ **{mc['id']}: {mc['name']}** (net={mc_independent[mc['id']]['net']:+d})\n")
    if len(survivors) < len(CONSTRAINTS):
        f.write(f"\nEliminated: {len(eliminated)}\n")
        for mc in eliminated:
            f.write(f"- ✗ {mc['id']}: {mc['name']} (net={mc_independent[mc['id']]['net']:+d})\n")

    f.write("""

---

## What Survives Without the Substrate

If the substrate disappeared — no OC2, no 9 assumptions, no mechanism classes —
the constraints that would remain are those whose explanatory power does not
depend on substrate-specific findings.

Those surviving constraints are the strongest candidates yet for the deepest
layer of the entire program.

""")

    f.write(f"Best pairwise synergy: {best_pair[0]}+{best_pair[1]} "
            f"covers {best_score}/{len(finding_ids)} findings.\n\n")

    f.write("""
## Interpretations

### MC3 (Constraint Balance) — Top Ranked

The idea that fertility requires a balance between too much freedom (collapse)
and too much rigidity (fortress) is the single hypothesis most consistent with
the entire T072–T078 dataset. It predicts the boundary regime, the finite
corridor width, the negative stability-fertility correlation, the three-zone
landscape, and the dominance of collapse-ward drift.

### MC2 (Productive Transformation) — Strong Support

The idea that systems must generate novel structure predicts the dominance of
fertility axes in PC1, the existence of the fertile corridor, its connectedness
across domains, and its survival under dimensional compression.

### MC1 (Information Preservation) — Mixed

Information preservation predicts viability correctly (coherence, recoverability)
but contradicts many fertility findings (lower coherence in fertile systems,
boundary regime, negative correlation). It is necessary but not sufficient.

### MC4 (Recursive Accessibility) — Narrow but Deep

Recursive accessibility has the narrowest coverage (many neutrals) but its
specific predictions (S gap, recursive exceptional, RD/S on PC3) are strongly
confirmed. It is the most specialized constraint.

### MC5 (Recoverable Perturbation) — Solid but Secondary

Recoverable perturbation predicts the saddle-like dynamics and the corridor's
persistence, but does not directly predict the geometric structure of the
meta-space. It may be a consequence of other constraints rather than a
fundamental one.
""")

print(f"Wrote t079_constraint_report.md")
print(f"\nT079 complete.")
