#!/usr/bin/env python3
"""
T077: Attractor Audit
======================
Determine whether the fertile corridor acts as an attractor across domains.

Measures per domain:
  A1 — Attraction Strength:   Do non-fertile systems sit near the corridor?
  A2 — Retention Strength:    Once fertile, how far from the edge?
  A3 — Recovery Capacity:     If perturbed, how easily does a system return?
  A4 — Drift Direction:       When systems leave, which way do they go?
  A5 — Basin Width:           How large is the region that flows into fertility?

Classification:
  Type I  — Attractor:     systems converge toward fertility
  Type II — Saddle:        easy to leave, hard to maintain
  Type III — Transit:      no attraction, only passage
  Type IV — External:      fertility maintained by external constraints
"""

import csv, json, math
from pathlib import Path
from collections import defaultdict
import itertools

OUT = Path("/home/student/sgp_core_v2/sfh_sgp_ood_outputs")

# ============================================================
# DOMAIN DATA (from T074, same as T075/T076)
# ============================================================

DOMAIN_DATA = [
    {
        "domain": "A — Physical universes",
        "configs": [
            {"name": "Our universe", "viable": True, "fertile": True,
             "C": 0.85, "P": 0.85, "G": 0.90, "R": 0.60, "S": 0.80,
             "SR": 0.90, "NP": 0.85, "RC": 0.90, "RD": 0.80, "OE": 0.80},
            {"name": "Cyclic universe (bounce)", "viable": True, "fertile": True,
             "C": 0.75, "P": 0.85, "G": 0.80, "R": 0.70, "S": 0.65,
             "SR": 0.80, "NP": 0.75, "RC": 0.85, "RD": 0.70, "OE": 0.70},
            {"name": "Empty universe (Ω<<1)", "viable": False, "fertile": False,
             "C": 0.80, "P": 0.95, "G": 0.05, "R": 0.10, "S": 0.00,
             "SR": 0.05, "NP": 0.00, "RC": 0.00, "RD": 0.00, "OE": 0.00},
            {"name": "Collapsing universe (Ω>>1)", "viable": False, "fertile": False,
             "C": 0.75, "P": 0.15, "G": 0.30, "R": 0.00, "S": 0.10,
             "SR": 0.30, "NP": 0.25, "RC": 0.20, "RD": 0.10, "OE": 0.05},
            {"name": "Thermal equilibrium", "viable": False, "fertile": False,
             "C": 0.50, "P": 0.90, "G": 0.05, "R": 0.05, "S": 0.00,
             "SR": 0.00, "NP": 0.00, "RC": 0.00, "RD": 0.00, "OE": 0.00},
            {"name": "High-dark-energy universe", "viable": False, "fertile": False,
             "C": 0.80, "P": 0.60, "G": 0.15, "R": 0.10, "S": 0.05,
             "SR": 0.15, "NP": 0.10, "RC": 0.10, "RD": 0.05, "OE": 0.05},
            {"name": "Strong-coupling universe", "viable": False, "fertile": False,
             "C": 0.40, "P": 0.30, "G": 0.50, "R": 0.10, "S": 0.15,
             "SR": 0.50, "NP": 0.45, "RC": 0.40, "RD": 0.20, "OE": 0.15},
            {"name": "Super-fertile universe (hypothetical)", "viable": True, "fertile": True,
             "C": 0.80, "P": 0.80, "G": 0.95, "R": 0.55, "S": 0.90,
             "SR": 0.95, "NP": 0.95, "RC": 0.95, "RD": 0.90, "OE": 0.95},
        ],
    },
    {
        "domain": "B — Mathematical systems",
        "configs": [
            {"name": "ZFC set theory", "viable": True, "fertile": True,
             "C": 0.80, "P": 0.90, "G": 0.90, "R": 0.70, "S": 0.70,
             "SR": 0.90, "NP": 0.90, "RC": 0.85, "RD": 0.80, "OE": 0.90},
            {"name": "Peano arithmetic (PA)", "viable": True, "fertile": True,
             "C": 0.85, "P": 0.90, "G": 0.80, "R": 0.75, "S": 0.50,
             "SR": 0.70, "NP": 0.75, "RC": 0.60, "RD": 0.40, "OE": 0.80},
            {"name": "First-order logic (FOL)", "viable": True, "fertile": False,
             "C": 1.00, "P": 0.95, "G": 0.40, "R": 0.90, "S": 0.10,
             "SR": 0.30, "NP": 0.30, "RC": 0.20, "RD": 0.10, "OE": 0.30},
            {"name": "Category theory (ETCS)", "viable": True, "fertile": True,
             "C": 0.80, "P": 0.85, "G": 0.85, "R": 0.70, "S": 0.80,
             "SR": 0.85, "NP": 0.85, "RC": 0.90, "RD": 0.90, "OE": 0.85},
            {"name": "Computation (Turing/λ)", "viable": True, "fertile": True,
             "C": 0.85, "P": 0.90, "G": 0.80, "R": 0.65, "S": 0.85,
             "SR": 0.80, "NP": 0.80, "RC": 0.85, "RD": 0.95, "OE": 0.85},
            {"name": "Inconsistent system", "viable": False, "fertile": False,
             "C": 0.05, "P": 0.10, "G": 0.95, "R": 0.00, "S": 0.10,
             "SR": 0.90, "NP": 0.95, "RC": 0.80, "RD": 0.60, "OE": 0.90},
            {"name": "Presburger arithmetic", "viable": True, "fertile": False,
             "C": 1.00, "P": 0.95, "G": 0.25, "R": 0.95, "S": 0.05,
             "SR": 0.15, "NP": 0.15, "RC": 0.10, "RD": 0.05, "OE": 0.15},
            {"name": "Decidable fragment of FOL", "viable": True, "fertile": False,
             "C": 1.00, "P": 0.95, "G": 0.15, "R": 0.95, "S": 0.05,
             "SR": 0.10, "NP": 0.10, "RC": 0.05, "RD": 0.00, "OE": 0.10},
        ],
    },
    {
        "domain": "C — Recursive substrate",
        "configs": [
            {"name": "Full 9-assumption substrate", "viable": True, "fertile": True,
             "C": 0.95, "P": 0.85, "G": 0.85, "R": 0.80, "S": 0.90,
             "SR": 0.85, "NP": 0.80, "RC": 0.80, "RD": 0.85, "OE": 0.75},
            {"name": "Original substrate (IS1↔IS2)", "viable": False, "fertile": False,
             "C": 0.20, "P": 0.30, "G": 0.40, "R": 0.10, "S": 0.35,
             "SR": 0.40, "NP": 0.35, "RC": 0.30, "RD": 0.40, "OE": 0.30},
            {"name": "OC2 only (trivial)", "viable": False, "fertile": False,
             "C": 0.60, "P": 0.30, "G": 0.05, "R": 0.10, "S": 0.00,
             "SR": 0.05, "NP": 0.00, "RC": 0.00, "RD": 0.00, "OE": 0.00},
            {"name": "Substrate without SR1", "viable": True, "fertile": False,
             "C": 0.85, "P": 0.80, "G": 0.70, "R": 0.70, "S": 0.25,
             "SR": 0.50, "NP": 0.50, "RC": 0.45, "RD": 0.30, "OE": 0.40},
            {"name": "Substrate without EC1", "viable": True, "fertile": True,
             "C": 0.85, "P": 0.80, "G": 0.75, "R": 0.70, "S": 0.60,
             "SR": 0.70, "NP": 0.70, "RC": 0.70, "RD": 0.55, "OE": 0.60},
            {"name": "Substrate without CD2", "viable": True, "fertile": False,
             "C": 0.90, "P": 0.80, "G": 0.65, "R": 0.70, "S": 0.75,
             "SR": 0.60, "NP": 0.55, "RC": 0.50, "RD": 0.60, "OE": 0.50},
        ],
    },
    {
        "domain": "D — Dynamical manifolds",
        "configs": [
            {"name": "Lorenz strange attractor", "viable": True, "fertile": False,
             "C": 0.80, "P": 0.80, "G": 0.60, "R": 0.60, "S": 0.30,
             "SR": 0.40, "NP": 0.30, "RC": 0.20, "RD": 0.20, "OE": 0.20},
            {"name": "Reaction-diffusion (Turing)", "viable": True, "fertile": True,
             "C": 0.85, "P": 0.85, "G": 0.80, "R": 0.75, "S": 0.35,
             "SR": 0.80, "NP": 0.70, "RC": 0.75, "RD": 0.30, "OE": 0.60},
            {"name": "Logistic map (r=3.8)", "viable": True, "fertile": False,
             "C": 0.75, "P": 0.65, "G": 0.65, "R": 0.30, "S": 0.15,
             "SR": 0.35, "NP": 0.30, "RC": 0.15, "RD": 0.10, "OE": 0.15},
            {"name": "Coupled oscillator (Kuramoto)", "viable": True, "fertile": False,
             "C": 0.85, "P": 0.85, "G": 0.65, "R": 0.70, "S": 0.40,
             "SR": 0.45, "NP": 0.40, "RC": 0.35, "RD": 0.25, "OE": 0.30},
            {"name": "Fixed-point collapse", "viable": False, "fertile": False,
             "C": 0.70, "P": 0.80, "G": 0.05, "R": 0.40, "S": 0.00,
             "SR": 0.00, "NP": 0.00, "RC": 0.00, "RD": 0.00, "OE": 0.00},
            {"name": "Boolean network (K=2 critical)", "viable": True, "fertile": True,
             "C": 0.80, "P": 0.80, "G": 0.80, "R": 0.60, "S": 0.50,
             "SR": 0.80, "NP": 0.75, "RC": 0.80, "RD": 0.50, "OE": 0.70},
            {"name": "Game of Life (CA)", "viable": True, "fertile": True,
             "C": 0.85, "P": 0.80, "G": 0.90, "R": 0.50, "S": 0.60,
             "SR": 0.90, "NP": 0.85, "RC": 0.90, "RD": 0.70, "OE": 0.90},
            {"name": "Unbounded divergence", "viable": False, "fertile": False,
             "C": 0.30, "P": 0.10, "G": 0.20, "R": 0.00, "S": 0.00,
             "SR": 0.10, "NP": 0.20, "RC": 0.05, "RD": 0.00, "OE": 0.10},
        ],
    },
]

STABILITY_AXES = ["C", "P", "R"]
FERTILITY_AXES = ["SR", "NP", "RC", "RD", "OE"]
ALL_AXES = ["C", "P", "G", "R", "S", "SR", "NP", "RC", "RD", "OE"]
ALL_CONFIGS = []

for d in DOMAIN_DATA:
    for c in d["configs"]:
        c["domain"] = d["domain"]
        c["stability"] = round(sum(c[a] for a in STABILITY_AXES) / 3, 3)
        c["fertility"] = round(sum(c[a] for a in FERTILITY_AXES) / 5, 3)
        c["region"] = "collapse" if not c["viable"] else ("fertile" if c["fertile"] else "fortress")
        ALL_CONFIGS.append(c)

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def euclidean_d(a, b, axes):
    return math.sqrt(sum((a[ax] - b[ax]) ** 2 for ax in axes))

def centroid(configs, axes):
    n = len(configs)
    return {ax: sum(c[ax] for c in configs) / n for ax in axes}

# ============================================================
# ANALYSIS
# ============================================================

print("=" * 72)
print("T077: ATTRACTOR AUDIT")
print("=" * 72)

print(f"""
  Questions:
    A1 — Attraction Strength:   Do non-fertile systems sit near the corridor?
    A2 — Retention Strength:    Once fertile, how far from the edge?
    A3 — Recovery Capacity:     If perturbed, how easily does a system return?
    A4 — Drift Direction:       When systems leave, which way do they go?
    A5 — Basin Width:           How large is the region that flows into fertility?

  {len(ALL_CONFIGS)} configurations, 4 domains.
""")

all_results = {}

for domain_data in DOMAIN_DATA:
    dname = domain_data["domain"]
    dc = domain_data["configs"]

    fertile_c = [c for c in dc if c["fertile"]]
    fortress_c = [c for c in dc if c["viable"] and not c["fertile"]]
    collapse_c = [c for c in dc if not c["viable"]]
    all_viable = [c for c in dc if c["viable"]]

    print(f"\n{'='*60}")
    print(f"  DOMAIN: {dname}")
    print(f"{'='*60}")
    print(f"    Fertile: {len(fertile_c)}  |  Fortress: {len(fortress_c)}  |  Collapse: {len(collapse_c)}")

    # ---- A1: Attraction Strength ----
    # How far are non-fertile systems from the fertile centroid?
    fertile_cent = centroid(fertile_c, ALL_AXES) if fertile_c else None

    print(f"\n  A1 — Attraction Strength")
    print(f"  {'-'*60}")

    if fertile_cent:
        # Distances from each non-fertile system to the fertile centroid
        fortress_dists = []
        collapse_dists = []
        for c in fortress_c:
            d = euclidean_d(c, fertile_cent, ALL_AXES)
            fortress_dists.append((c["name"], round(d, 3)))
        for c in collapse_c:
            d = euclidean_d(c, fertile_cent, ALL_AXES)
            collapse_dists.append((c["name"], round(d, 3)))

        print(f"    Fertile centroid: "
              f"C={fertile_cent['C']:.2f} P={fertile_cent['P']:.2f} "
              f"G={fertile_cent['G']:.2f} R={fertile_cent['R']:.2f} "
              f"S={fertile_cent['S']:.2f}")

        if fortress_dists:
            avg_fort = sum(d for _, d in fortress_dists) / len(fortress_dists)
            min_fort = min(d for _, d in fortress_dists)
            print(f"    Fortress → fertile centroid:")
            print(f"      Mean distance: {avg_fort:.3f}, Min: {min_fort:.3f}")
            for name, d in sorted(fortress_dists, key=lambda x: x[1]):
                print(f"      {name:<40} {d:.3f}")
        else:
            print(f"    No fortress systems in this domain.")

        if collapse_dists:
            avg_coll = sum(d for _, d in collapse_dists) / len(collapse_dists)
            min_coll = min(d for _, d in collapse_dists)
            print(f"    Collapse → fertile centroid:")
            print(f"      Mean distance: {avg_coll:.3f}, Min: {min_coll:.3f}")
            for name, d in sorted(collapse_dists, key=lambda x: x[1]):
                print(f"      {name:<40} {d:.3f}")
        else:
            print(f"    No collapse systems in this domain.")

        # Attraction score: ratio of mean fortress distance to mean collapse distance
        # If fortress systems are closer to fertile centroid than collapse systems,
        # there's evidence of attraction toward the corridor
        if fortress_dists and collapse_dists:
            attraction_ratio = avg_fort / avg_coll if avg_coll > 0 else 999
            attraction_score = 1 / attraction_ratio if attraction_ratio > 0 else 999
            print(f"    Attraction score (fortress_mean / collapse_mean): {attraction_ratio:.3f}")
            print(f"    (Lower = stronger attraction toward fertile corridor)")
        else:
            attraction_ratio = None
            attraction_score = None
            print(f"    Cannot compute attraction ratio (missing fortress or collapse)")

    # ---- A2: Retention Strength ----
    print(f"\n  A2 — Retention Strength")
    print(f"  {'-'*60}")

    if fertile_c:
        # For each fertile system, distance to the nearest non-fertile system
        non_fertile = fortress_c + collapse_c
        retention_dists = []
        for fc in fertile_c:
            if non_fertile:
                nearest = min(euclidean_d(fc, nf, ALL_AXES) for nf in non_fertile)
            else:
                nearest = None
            retention_dists.append((fc["name"], round(nearest, 3) if nearest is not None else None))

        # Also compute distance between fertile systems (clustering)
        fert_pairwise = []
        for i in range(len(fertile_c)):
            for j in range(i+1, len(fertile_c)):
                d = euclidean_d(fertile_c[i], fertile_c[j], ALL_AXES)
                fert_pairwise.append(d)

        avg_fert_pair = sum(fert_pairwise) / len(fert_pairwise) if fert_pairwise else 0
        min_fert_pair = min(fert_pairwise) if fert_pairwise else 0
        max_fert_pair = max(fert_pairwise) if fert_pairwise else 0

        # Retention depth: average distance from fertile to nearest non-fertile
        valid_dists = [d for _, d in retention_dists if d is not None]
        if valid_dists:
            avg_retention = sum(valid_dists) / len(valid_dists)
            min_retention = min(valid_dists)
            print(f"    Distance from fertile → nearest non-fertile:")
            print(f"      Mean: {avg_retention:.3f}, Min: {min_retention:.3f}")
            for name, d in sorted(retention_dists, key=lambda x: x[1] if x[1] is not None else 999):
                print(f"      {name:<40} {d if d is not None else 'N/A'}")
            print(f"    Fertile cluster cohesion (mean pairwise distance): {avg_fert_pair:.3f}")
            print(f"    Fertile cluster range: [{min_fert_pair:.3f}, {max_fert_pair:.3f}]")
        else:
            avg_retention = 0
            min_retention = 0
            print(f"    No non-fertile systems to measure distance.")

        # Stability margin: how far is each fertile system from the corridor edges?
        fertile_sorted = sorted(fertile_c, key=lambda c: c["stability"])
        if len(fertile_sorted) >= 2:
            s_min = fertile_sorted[0]["stability"]
            s_max = fertile_sorted[-1]["stability"]
            # Distance from corridor edges
            margin_left = s_min - (min(c["stability"] for c in dc))
            margin_right = (max(c["stability"] for c in dc)) - s_max
            print(f"    Corridor margins: left={margin_left:.3f}, right={margin_right:.3f}")
        else:
            margin_left = margin_right = 0
    else:
        avg_retention = 0
        min_retention = 0
        avg_fert_pair = 0
        print(f"    No fertile systems in this domain.")

    # ---- A3: Recovery Capacity ----
    print(f"\n  A3 — Recovery Capacity")
    print(f"  {'-'*60}")

    # Recovery capacity is inferred from:
    # (1) How close fortress systems are to the fertile centroid
    # (2) Whether fortress systems are closer to fertile centroid than collapse systems
    # (3) The self-modeling (S) axis — necessary for self-correction

    if fertile_cent and fortress_c:
        # Proximity of fortress to fertile = potential for recovery
        fort_cent = centroid(fortress_c, ALL_AXES)
        fort_to_fert = euclidean_d(fort_cent, fertile_cent, ALL_AXES)
        print(f"    Fortress centroid → fertile centroid distance: {fort_to_fert:.3f}")

        # Also check the S axis specifically (self-modeling enables recovery)
        avg_s_fortress = sum(c["S"] for c in fortress_c) / len(fortress_c)
        avg_s_fertile = sum(c["S"] for c in fertile_c) / len(fertile_c) if fertile_c else 0
        print(f"    Self-modeling (S) — Fortress: {avg_s_fortress:.3f}, Fertile: {avg_s_fertile:.3f}")
        s_gap = avg_s_fertile - avg_s_fortress
        print(f"    S gap (fertile - fortress): {s_gap:+.3f}")
        # Smaller gap = easier recovery

        # Recovery potential: combination of proximity and S gap
        recovery_potential = max(0, 1 - fort_to_fert * (1 + max(0, s_gap)))
        print(f"    Recovery potential score: {recovery_potential:.3f} (higher = better)")
    elif fertile_cent:
        print(f"    No fortress systems. Recovery not testable in this domain.")
        fort_to_fert = None
        s_gap = None
        recovery_potential = None
    else:
        print(f"    No fertile systems. Recovery not testable in this domain.")
        fort_to_fert = None
        s_gap = None
        recovery_potential = None

    # ---- A4: Drift Direction ----
    print(f"\n  A4 — Drift Direction")
    print(f"  {'-'*60}")

    if fertile_cent and fertile_c:
        # For each non-fertile system, determine which side of the corridor it's on
        # (collapse side = lower stability, fortress side = higher stability)
        fertile_s_mean = sum(c["stability"] for c in fertile_c) / len(fertile_c)
        collapse_side = []
        fortress_side = []
        oscillatory = []
        for c in non_fertile:
            if c["stability"] < fertile_s_mean:
                collapse_side.append(c["name"])
            else:
                fortress_side.append(c["name"])

        print(f"    Non-fertile on collapse side  (stab < {fertile_s_mean:.2f}): {len(collapse_side)}")
        for n in collapse_side:
            print(f"      {n}")
        print(f"    Non-fertile on fortress side (stab > {fertile_s_mean:.2f}): {len(fortress_side)}")
        for n in fortress_side:
            print(f"      {n}")

        # Determine dominant drift direction
        if len(collapse_side) > len(fortress_side):
            drift = "collapse-ward"
            drift_ratio = len(collapse_side) / max(1, len(fortress_side))
        elif len(fortress_side) > len(collapse_side):
            drift = "fortress-ward"
            drift_ratio = len(fortress_side) / max(1, len(collapse_side))
        else:
            drift = "balanced"
            drift_ratio = 1.0

        print(f"    Dominant drift: {drift} (ratio {drift_ratio:.1f})")
    else:
        drift = "unknown"
        drift_ratio = 0
        fertile_s_mean = 0
        print(f"    Cannot determine drift direction.")

    # ---- A5: Basin Width ----
    print(f"\n  A5 — Basin Width")
    print(f"  {'-'*60}")

    # Basin width = the range of axis values from which fertility is reachable
    if fertile_c:
        fertile_s_range = max(c["stability"] for c in fertile_c) - min(c["stability"] for c in fertile_c)

        # For each axis, compute the range spanned by fertile systems
        axis_ranges = {}
        for ax in ALL_AXES:
            vals = [c[ax] for c in fertile_c]
            axis_ranges[ax] = max(vals) - min(vals)

        # Total basin volume (product of axis ranges)
        basin_volume = 1.0
        for ax in ALL_AXES:
            basin_volume *= axis_ranges[ax] + 0.001  # avoid zero

        print(f"    Fertile stability range: {fertile_s_range:.3f}")
        print(f"    Axis ranges within fertile corridor:")
        for ax in ALL_AXES:
            print(f"      {ax}: {axis_ranges[ax]:.3f}")
        print(f"    Basin volume (10-axis): {basin_volume:.6e}")

        # Compare fertile basin to total viable range
        if all_viable:
            viable_s_range = max(c["stability"] for c in all_viable) - min(c["stability"] for c in all_viable)
            basin_fill_ratio = fertile_s_range / viable_s_range if viable_s_range > 0 else 0
            print(f"    Basin fill ratio (fertile_stab_range / viable_stab_range): {basin_fill_ratio:.3f}")
        else:
            basin_fill_ratio = 0
    else:
        fertile_s_range = 0
        axis_ranges = {}
        basin_volume = 0
        basin_fill_ratio = 0

    # ---- CLASSIFICATION ----
    print(f"\n  {'='*50}")
    print(f"  ATTRACTOR CLASSIFICATION")
    print(f"  {'='*50}")

    # Collect evidence
    evidence = {}

    # Key discriminators:
    # Type I  (Attractor):     fertile_s_range > 0, fortress close to fertile, high S gap, collapse side drift
    # Type II (Saddle):        fertile systems exist but weak retention, fortress far, balanced/oscillatory
    # Type III (Transit):      fertile_s_range small, low retention, no attraction
    # Type IV (External):      fertile relies on S or other external axis

    if not fertile_c:
        classification = "Type IV — External (no intrinsic fertility)"
        evidence["reason"] = "no fertile systems found"
    elif len(fertile_c) < 2:
        classification = "Type III — Transit (single fertile point, no basin)"
        evidence["reason"] = "only one fertile system"
    else:
        # Compute classification metrics
        # Strong attractor: fertile cluster is well-separated from non-fertile,
        # fortress systems are close to fertile centroid, retention is high
        retention_quality = avg_retention if 'avg_retention' in dir() or 'avg_retention' in locals() else 0
        # Actually avg_retention is always defined

        # Check: do fortress systems exist and are they close to fertile?
        fortress_proximity = None
        if fortress_c and fertile_cent:
            fortress_proximity = avg_fort  # from A1

        # Check drift direction
        drift_toward_collapse = (drift == "collapse-ward")

        # Check self-modeling as potential external maintenance mechanism
        avg_s_fert = sum(c["S"] for c in fertile_c) / len(fertile_c) if fertile_c else 0

        # Decision logic
        # If S is very high in fertile but low in non-fertile, fertility may be externally maintained (Type IV)
        # If fortress is close to fertile centroid, there's attraction (Type I)
        # If fertile systems have low retention (close to edges), it's saddle-like (Type II)

        if avg_s_fert > 0.8 and fortress_proximity is not None and fortress_proximity > 0.5:
            classification = "Type IV — External (self-modeling drives fertility)"
            evidence["reason"] = f"high S in fertile ({avg_s_fert:.2f}) but fortress far from centroid ({fortress_proximity:.2f})"
        elif fortress_proximity is not None and fortress_proximity < 0.3 and avg_retention > 0.15:
            classification = "Type I — Attractor"
            evidence["reason"] = f"fortress close to fertile ({fortress_proximity:.2f}), strong retention ({avg_retention:.2f})"
        elif fortress_proximity is not None and fortress_proximity < 0.4 and avg_retention > 0.1:
            classification = "Type I — Attractor (weak)"
            evidence["reason"] = f"moderate fortress proximity ({fortress_proximity:.2f}) and retention ({avg_retention:.2f})"
        elif avg_retention < 0.1 or (fortress_proximity is not None and fortress_proximity > 0.5):
            classification = "Type II — Saddle"
            evidence["reason"] = f"low retention ({avg_retention:.2f}) or fortress far ({fortress_proximity})"
        else:
            classification = "Type III — Transit"
            evidence["reason"] = "no clear attraction or saddle signature"

        evidence["retention_mean"] = round(avg_retention, 3) if 'avg_retention' in locals() or 'avg_retention' in globals() else None
        evidence["fortress_proximity"] = round(fortress_proximity, 3) if fortress_proximity is not None else None
        evidence["basin_fill_ratio"] = round(basin_fill_ratio, 3)
        evidence["drift"] = drift
        evidence["fertile_cluster_cohesion"] = round(avg_fert_pair, 3) if 'avg_fert_pair' in locals() or 'avg_fert_pair' in globals() else None

    print(f"\n    Classification: {classification}")
    for k, v in evidence.items():
        print(f"      {k}: {v}")

    # Store results
    all_results[dname] = {
        "n_fertile": len(fertile_c),
        "n_fortress": len(fortress_c),
        "n_collapse": len(collapse_c),
        "classification": classification,
        "evidence": evidence,
        "fertile_centroid": {ax: round(fertile_cent[ax], 3) for ax in ALL_AXES} if fertile_cent else None,
        "fertile_stability_range": [round(min(c["stability"] for c in fertile_c), 3),
                                     round(max(c["stability"] for c in fertile_c), 3)] if fertile_c else None,
        "attraction_strength": {
            "fortress_distances": sorted(fortress_dists, key=lambda x: x[1]) if 'fortress_dists' in dir() or 'fortress_dists' in locals() else [],
            "collapse_distances": sorted(collapse_dists, key=lambda x: x[1]) if 'collapse_dists' in dir() or 'collapse_dists' in locals() else [],
        },
        "retention_strength": {
            "mean_distance_to_non_fertile": round(avg_retention, 3),
            "min_distance_to_non_fertile": round(min_retention, 3),
            "fertile_cluster_cohesion": round(avg_fert_pair, 3) if 'avg_fert_pair' in dir() or 'avg_fert_pair' in locals() else None,
        },
        "recovery_capacity": {
            "fortress_to_fertile_distance": round(fort_to_fert, 3) if fort_to_fert is not None else None,
            "s_gap": round(s_gap, 3) if s_gap is not None else None,
            "recovery_potential": round(recovery_potential, 3) if recovery_potential is not None else None,
        },
        "drift_direction": drift,
        "basin_width": {
            "stability_range": round(fertile_s_range, 3),
            "fill_ratio": round(basin_fill_ratio, 3),
            "axis_ranges": {ax: round(axis_ranges[ax], 3) for ax in ALL_AXES} if axis_ranges else None,
        },
    }

# ============================================================
# CROSS-DOMAIN COMPARISON
# ============================================================

print(f"\n{'='*72}")
print("CROSS-DOMAIN ATTRACTOR COMPARISON")
print(f"{'='*72}")

print(f"\n  {'Domain':<30}{'Class':<25}{'Retention':<12}{'Drift':<16}{'Fill':<10}")
print(f"  {'-'*93}")
for domain_data in DOMAIN_DATA:
    dname = domain_data["domain"]
    r = all_results[dname]
    cls = r["classification"][:15]
    ret = r["retention_strength"]["mean_distance_to_non_fertile"]
    drift = r["drift_direction"]
    fill = r["basin_width"]["fill_ratio"]
    print(f"  {dname:<30}{cls:<25}{ret:<12}{drift:<16}{fill:<10}")

# Check for attractor universality
types_found = defaultdict(list)
for dname, r in all_results.items():
    cls = r["classification"]
    if "Attractor" in cls:
        types_found["Attractor"].append(dname)
    elif "Saddle" in cls:
        types_found["Saddle"].append(dname)
    elif "Transit" in cls:
        types_found["Transit"].append(dname)
    elif "External" in cls:
        types_found["External"].append(dname)
    else:
        types_found["Other"].append(dname)

print(f"\n  Attractor type distribution:")
for t, domains in types_found.items():
    print(f"    {t}: {len(domains)} domain(s) — {', '.join(domains)}")

if len(types_found) == 1:
    print(f"\n  ** UNIVERSAL ATTRACTOR TYPE **")
elif len(types_found) <= 2:
    print(f"\n  ** Partial convergence on {len(types_found)} types **")
else:
    print(f"\n  ** Domain-specific attractor types **")

# ============================================================
# WRITE DELIVERABLES
# ============================================================

# 1. Attractor profiles
with open(OUT / "t077_attractor_profiles.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["domain", "name", "region", "stability", "fertility",
                 "dist_to_fertile_centroid", "drift_side"])
    for domain_data in DOMAIN_DATA:
        dname = domain_data["domain"]
        dc = domain_data["configs"]
        fertile_c = [c for c in dc if c["fertile"]]
        fertile_cent = centroid(fertile_c, ALL_AXES) if fertile_c else None
        fertile_s_mean = sum(c["stability"] for c in fertile_c) / len(fertile_c) if fertile_c else 0

        for c in dc:
            d_cent = round(euclidean_d(c, fertile_cent, ALL_AXES), 3) if fertile_cent else ""
            if fertile_cent:
                if c["stability"] < fertile_s_mean:
                    side = "collapse"
                else:
                    side = "fortress"
            else:
                side = ""
            w.writerow([dname, c["name"], c["region"], c["stability"],
                         c["fertility"], d_cent, side])

print(f"\nWrote t077_attractor_profiles.csv")

# 2. Basin widths
with open(OUT / "t077_basin_widths.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["domain", "axis", "fertile_min", "fertile_max", "range"])
    for domain_data in DOMAIN_DATA:
        dname = domain_data["domain"]
        dc = domain_data["configs"]
        fertile_c = [c for c in dc if c["fertile"]]
        for ax in ALL_AXES:
            vals = [c[ax] for c in fertile_c]
            w.writerow([dname, ax, round(min(vals), 3), round(max(vals), 3),
                         round(max(vals)-min(vals), 3)])

print(f"Wrote t077_basin_widths.csv")

# 3. Recovery tests
with open(OUT / "t077_recovery_tests.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["domain", "metric", "value"])
    for domain_data in DOMAIN_DATA:
        dname = domain_data["domain"]
        r = all_results[dname]
        rc = r["recovery_capacity"]
        w.writerow([dname, "fortress_to_fertile_distance", rc["fortress_to_fertile_distance"]])
        w.writerow([dname, "s_gap", rc["s_gap"]])
        w.writerow([dname, "recovery_potential", rc["recovery_potential"]])

print(f"Wrote t077_recovery_tests.csv")

# 4. Drift patterns
with open(OUT / "t077_drift_patterns.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["domain", "direction", "collapse_side_count", "fortress_side_count", "ratio"])
    for domain_data in DOMAIN_DATA:
        dname = domain_data["domain"]
        dc = domain_data["configs"]
        fertile_c = [c for c in dc if c["fertile"]]
        if fertile_c:
            fertile_s_mean = sum(c["stability"] for c in fertile_c) / len(fertile_c)
            non_fertile = [c for c in dc if not c["fertile"]]
            cs = len([c for c in non_fertile if c["stability"] < fertile_s_mean])
            fs = len([c for c in non_fertile if c["stability"] >= fertile_s_mean])
            ratio = round(cs / max(1, fs), 2)
            drift = "collapse-ward" if cs > fs else ("fortress-ward" if fs > cs else "balanced")
            w.writerow([dname, drift, cs, fs, ratio])

print(f"Wrote t077_drift_patterns.csv")

# 5. Cross-domain attractors
with open(OUT / "t077_cross_domain_attractors.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["domain", "classification", "retention", "drift", "basin_fill",
                 "fertile_stab_min", "fertile_stab_max"])
    for domain_data in DOMAIN_DATA:
        dname = domain_data["domain"]
        r = all_results[dname]
        fsr = r["fertile_stability_range"]
        w.writerow([dname, r["classification"],
                     r["retention_strength"]["mean_distance_to_non_fertile"],
                     r["drift_direction"], r["basin_width"]["fill_ratio"],
                     fsr[0] if fsr else "", fsr[1] if fsr else ""])

print(f"Wrote t077_cross_domain_attractors.csv")

# 6. Attractor report (markdown)
with open(OUT / "t077_attractor_report.md", "w") as f:
    f.write("""T077: Attractor Audit — Report
================================

## Question

Does the fertile corridor act as an attractor across domains?

---

## Classification Scheme

| Type | Name | Description |
|------|------|-------------|
| I | Attractor | Systems converge toward fertility |
| II | Saddle | Easy to leave, hard to maintain |
| III | Transit | No attraction, only passage |
| IV | External | Maintained by external constraints |

---

## Per-Domain Results

""")
    for domain_data in DOMAIN_DATA:
        dname = domain_data["domain"]
        r = all_results[dname]
        f.write(f"### {dname}\n\n")
        f.write(f"- Classification: **{r['classification']}**\n")
        f.write(f"- Fertile systems: {r['n_fertile']}\n")
        f.write(f"- Average retention (dist to non-fertile): {r['retention_strength']['mean_distance_to_non_fertile']}\n")
        f.write(f"- Fertile cluster cohesion: {r['retention_strength']['fertile_cluster_cohesion']}\n")
        f.write(f"- Drift direction: {r['drift_direction']}\n")
        f.write(f"- Basin fill ratio: {r['basin_width']['fill_ratio']}\n")
        rc = r['recovery_capacity']
        f.write(f"- Recovery potential: {rc['recovery_potential']}\n")
        f.write("\n")

    f.write("""---

## Cross-Domain Summary

""")
    for t, domains in types_found.items():
        f.write(f"- {t}: {len(domains)} — {', '.join(domains)}\n")

    f.write("""
---

## Interpretation

The attractor classification reveals whether the fertile corridor is:

1. A **destination** (Type I) — systems move toward it naturally
2. A **tightrope** (Type II) — systems can be there but easily leave
3. A **waypoint** (Type III) — systems pass through without staying
4. A **construction** (Type IV) — systems must be built to stay there

The distribution across domains tells us whether attractor dynamics are
universal or domain-specific.
""")

print(f"Wrote t077_attractor_report.md")

# 7. Summary JSON
summary = {
    "audit": "T077 — Attractor Audit",
    "question": "Does the fertile corridor act as an attractor across domains?",
    "per_domain_classification": {
        dname: r["classification"] for dname, r in all_results.items()
    },
    "type_distribution": {t: len(ds) for t, ds in types_found.items()},
    "drift_patterns": {dname: r["drift_direction"] for dname, r in all_results.items()},
    "retention_strengths": {dname: r["retention_strength"]["mean_distance_to_non_fertile"] for dname, r in all_results.items()},
    "recovery_potentials": {dname: r["recovery_capacity"]["recovery_potential"] for dname, r in all_results.items()},
    "basin_fill_ratios": {dname: r["basin_width"]["fill_ratio"] for dname, r in all_results.items()},
    "universal_attractor_type": len(types_found) == 1,
    "attractor_type_if_universal": list(types_found.keys())[0] if len(types_found) == 1 else None,
    "conclusion": (
        f"The fertile corridor shows {len(types_found)} distinct attractor type(s) "
        f"across the 4 domains."
    ),
}

with open(OUT / "t077_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print(f"Wrote t077_summary.json")
print(f"\nT077 complete.")
