#!/usr/bin/env python3
"""
T075: Stability/Fertility Tradeoff Audit
=========================================
Determine whether fertility and stability are:
  1. Independent
  2. Positively coupled
  3. Negatively coupled
  4. Related through a boundary regime

Hypothesis from T074: Maximum fertility occurs near the edge of
instability, not at maximum stability.
"""

import csv, json
from pathlib import Path
from collections import defaultdict
import math

OUT = Path("/home/student/sgp_core_v2/sfh_sgp_ood_outputs")

# ============================================================
# DOMAIN DATA (from T074)
# ============================================================

ALL_CONFIGS = []

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

# Flatten
for d in DOMAIN_DATA:
    for c in d["configs"]:
        c["domain"] = d["domain"]
        ALL_CONFIGS.append(c)

STABILITY_AXES = ["C", "P", "R"]
FERTILITY_AXES = ["SR", "NP", "RC", "RD", "OE"]

def composite(axes, config):
    return sum(config[a] for a in axes) / len(axes)

for c in ALL_CONFIGS:
    c["stability"] = round(composite(STABILITY_AXES, c), 3)
    c["fertility"] = round(composite(FERTILITY_AXES, c), 3)

# ============================================================
# ANALYSIS
# ============================================================

print("=" * 72)
print("T075: STABILITY/FERTILITY TRADEOFF AUDIT")
print("=" * 72)

print(f"""
  Question: Is fertility maximized by stability, opposed to stability,
  or produced at the boundary between order and instability?

  Composites:
    Stability  = (C + P + R) / 3
    Fertility  = (SR + NP + RC + RD + OE) / 5

  {len(ALL_CONFIGS)} configurations across 4 domains.
""")

# ---- A1: Global correlation ----
print(f"{'='*72}")
print("A1: GLOBAL CORRELATION")
print(f"{'='*72}")

viable_configs = [c for c in ALL_CONFIGS if c["viable"]]
fertile_configs = [c for c in ALL_CONFIGS if c["fertile"]]
merely_viable = [c for c in ALL_CONFIGS if c["viable"] and not c["fertile"]]

# Pearson correlation across all viable systems
def pearson(xs, ys):
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx)**2 for x in xs))
    dy = math.sqrt(sum((y - my)**2 for y in ys))
    return num / (dx * dy) if dx * dy > 0 else 0

s_vals = [c["stability"] for c in ALL_CONFIGS]
f_vals = [c["fertility"] for c in ALL_CONFIGS]
r_global = pearson(s_vals, f_vals)

s_viable = [c["stability"] for c in viable_configs]
f_viable = [c["fertility"] for c in viable_configs]
r_viable = pearson(s_viable, f_viable)

s_fertile = [c["stability"] for c in fertile_configs]
f_fertile = [c["fertility"] for c in fertile_configs]
r_fertile = pearson(s_fertile, f_fertile)

print(f"\n  Pearson r (all {len(ALL_CONFIGS)} configs):  {r_global:+.3f}")
print(f"  Pearson r ({len(viable_configs)} viable only): {r_viable:+.3f}")
print(f"  Pearson r ({len(fertile_configs)} fertile only): {r_fertile:+.3f}")

# Per-domain correlation
print(f"\n  Per-domain correlation (viable only):")
for d in DOMAIN_DATA:
    dname = d["domain"]
    domain_viable = [c for c in d["configs"] if c["viable"]]
    if len(domain_viable) < 3:
        continue
    ds = [c["stability"] for c in domain_viable]
    df = [c["fertility"] for c in domain_viable]
    r = pearson(ds, df)
    print(f"    {dname:<30} r = {r:+.3f} ({len(domain_viable)} viable configs)")

# ---- A2: Quadrant analysis ----
print(f"\n{'='*72}")
print("A2: QUADRANT ANALYSIS")
print(f"{'='*72}")

# Find medians to split into quadrants
med_s = sorted([c["stability"] for c in viable_configs])[len(viable_configs)//2]
med_f = sorted([c["fertility"] for c in viable_configs])[len(viable_configs)//2]

# Actually use mean-based thresholds for cleaner split
mean_s = sum(c["stability"] for c in viable_configs) / len(viable_configs)
mean_f = sum(c["fertility"] for c in viable_configs) / len(viable_configs)

quadrants = {"HS/HF": [], "HS/LF": [], "LS/HF": [], "LS/LF": []}
for c in viable_configs:
    if c["stability"] >= mean_s and c["fertility"] >= mean_f:
        quadrants["HS/HF"].append(c)
    elif c["stability"] >= mean_s and c["fertility"] < mean_f:
        quadrants["HS/LF"].append(c)
    elif c["stability"] < mean_s and c["fertility"] >= mean_f:
        quadrants["LS/HF"].append(c)
    else:
        quadrants["LS/LF"].append(c)

print(f"\n  Medians: stability={med_s:.2f}, fertility={med_f:.2f}")
print(f"  Means:   stability={mean_s:.2f}, fertility={mean_f:.2f}")
print(f"\n  {'Quadrant':<10}{'Label':<35}{'Count':<8}{'Examples'}")
print(f"  {'-'*85}")
for q in ["HS/HF", "HS/LF", "LS/HF", "LS/LF"]:
    confs = quadrants[q]
    labels = {"HS/HF": "High stability, High fertility (sweet spot)",
              "HS/LF": "High stability, Low fertility (sterile fortress)",
              "LS/HF": "Low stability, High fertility (edge of chaos)",
              "LS/LF": "Low stability, Low fertility (collapse zone)"}
    examples = [c["name"][:30] for c in confs[:3]]
    if not examples:
        examples = ["(none)"]
    print(f"  {q:<10}{labels[q]:<35}{len(confs):<8}{', '.join(examples)}")

# ---- A3: Boundary search ----
print(f"\n{'='*72}")
print("A3: BOUNDARY SEARCH")
print(f"{'='*72}")

# Sort by stability, look at where fertility peaks
sorted_by_s = sorted(viable_configs, key=lambda c: c["stability"])

print(f"\n  Viable configurations ranked by stability:")
print(f"  {'Stability':<12}{'Fertility':<12}{'Name':<35}{'Category':<12}")
print(f"  {'-'*71}")
for c in sorted_by_s:
    cat = "fertile" if c["fertile"] else "merely viable"
    print(f"  {c['stability']:<12.2f}{c['fertility']:<12.2f}{c['name']:<35}{cat:<12}")

# Binned analysis: divide stability range into bins, compute mean fertility per bin
n_bins = 5
min_s = min(c["stability"] for c in viable_configs)
max_s = max(c["stability"] for c in viable_configs)
bin_width = (max_s - min_s) / n_bins

print(f"\n  Binned analysis (viable only):")
print(f"  {'Bin':<10}{'Range':<20}{'N':<6}{'Mean Fertility':<18}{'Max Fertility':<16}")
print(f"  {'-'*70}")
for i in range(n_bins):
    lo = min_s + i * bin_width
    hi = lo + bin_width
    bin_confs = [c for c in viable_configs if lo <= c["stability"] < hi]
    if not bin_confs:
        continue
    mean_f = sum(c["fertility"] for c in bin_confs) / len(bin_confs)
    max_f = max(c["fertility"] for c in bin_confs)
    print(f"  {i+1:<10}{f'[{lo:.2f}, {hi:.2f})':<20}{len(bin_confs):<6}{mean_f:<18.2f}{max_f:<16.2f}")

# Find the stability window where peak fertility occurs
print(f"\n  Maximum fertility window:")
max_fert_config = max(viable_configs, key=lambda c: c["fertility"])
print(f"    Highest fertility: {max_fert_config['fertility']:.2f} at stability {max_fert_config['stability']:.2f}")
print(f"    System: {max_fert_config['name']} ({max_fert_config['domain']})")

# Find lowest and highest stability among fertile systems
fert_s_vals = [c["stability"] for c in fertile_configs]
fert_f_vals = [c["fertility"] for c in fertile_configs]
print(f"\n  Fertile systems only:")
print(f"    Stability range:  [{min(fert_s_vals):.2f}, {max(fert_s_vals):.2f}]")
print(f"    Fertility range:  [{min(fert_f_vals):.2f}, {max(fert_f_vals):.2f}]")
print(f"    Correlation r:    {pearson(fert_s_vals, fert_f_vals):+.3f}")

# Compare fertile vs merely-viable on stability
mv_s_vals = [c["stability"] for c in merely_viable]
print(f"\n  Merely-viable systems:")
print(f"    Stability range:  [{min(mv_s_vals):.2f}, {max(mv_s_vals):.2f}]")
print(f"    Mean stability:   {sum(mv_s_vals)/len(mv_s_vals):.2f}")

print(f"\n  Fertile systems:")
print(f"    Mean stability:   {sum(fert_s_vals)/len(fert_s_vals):.2f}")

# ---- A4: Domain comparison ----
print(f"\n{'='*72}")
print("A4: DOMAIN COMPARISON")
print(f"{'='*72}")

print(f"\n  {'Domain':<30}{'Stab mean':<12}{'Fert mean':<12}{'r (viable)':<12}{'N viable':<10}")
print(f"  {'-'*76}")
for d in DOMAIN_DATA:
    dname = d["domain"]
    domain_viable = [c for c in d["configs"] if c["viable"]]
    if not domain_viable:
        continue
    ds = [c["stability"] for c in domain_viable]
    df = [c["fertility"] for c in domain_viable]
    r = pearson(ds, df)
    print(f"  {dname:<30}{sum(ds)/len(ds):<12.2f}{sum(df)/len(df):<12.2f}"
          f"{r:<12.3f}{len(domain_viable):<10}")

# ---- Summary ----
print(f"\n{'='*72}")
print("SUMMARY")
print(f"{'='*72}")

# Determine the relationship type
if abs(r_viable) < 0.2:
    rel_type = "INDEPENDENT — stability and fertility show minimal correlation"
elif r_viable > 0:
    rel_type = "POSITIVELY COUPLED — stability supports fertility"
else:
    rel_type = "NEGATIVELY COUPLED — stability opposes fertility"

# Check for boundary regime
# If the highest-fertility systems are near the middle of the stability range
# rather than at the extremes, that suggests a boundary regime
sorted_s = sorted(fert_s_vals)
mid_s = (min_s + max_s) / 2
fert_centered = sum(abs(s - mid_s) for s in fert_s_vals) / len(fert_s_vals)
mv_centered = sum(abs(s - mid_s) for s in mv_s_vals) / len(mv_s_vals)

# Compare mean distance from midpoint
print(f"\n  Relationship: {rel_type}")
print(f"\n  Boundary regime analysis:")
print(f"    Fertile systems:       mean distance from stability midpoint = {fert_centered:.3f}")
print(f"    Merely-viable systems: mean distance from stability midpoint = {mv_centered:.3f}")
if fert_centered < mv_centered:
    print(f"    Fertile systems cluster CLOSER to the stability midpoint.")
    print(f"    This is consistent with a BOUNDARY REGIME — maximum fertility")
    print(f"    occurs not at extremes but at intermediate stability.")
else:
    print(f"    Fertile systems are NOT specifically clustered at the midpoint.")
    print(f"    The tradeoff may be monotone rather than boundary-based.")

print(f"\n  Quadrant distribution (viable systems only):")
for q in ["HS/HF", "HS/LF", "LS/HF", "LS/LF"]:
    labels = {"HS/HF": "High-High (sweet spot)",
              "HS/LF": "High-Low (sterile fortress)",
              "LS/HF": "Low-High (edge of chaos)",
              "LS/LF": "Low-Low  (collapse zone)"}
    confs = quadrants[q]
    pct = len(confs) / len(viable_configs) * 100
    print(f"    {labels[q]:<35} {len(confs):d} ({pct:.0f}%)")

print(f"\n  Conclusion:")
print(f"    {'Maximum fertility occurs near the edge of instability,' if fert_centered < mv_centered else 'Fertility and stability show a monotone relationship,'}")
print(f"    {'consistent with a boundary regime where systems balance order and chaos.' if fert_centered < mv_centered else 'not specifically a boundary phenomenon.'}")

# Determine which pattern best describes the relationship
hs_hf = len(quadrants["HS/HF"])
hs_lf = len(quadrants["HS/LF"])
ls_hf = len(quadrants["LS/HF"])
ls_lf = len(quadrants["LS/LF"])

if ls_hf > hs_hf and ls_hf > hs_lf:
    tradeoff_pattern = "EDGE OF CHAOS — most fertile systems are lower-stability"
elif hs_hf > ls_hf and hs_hf > hs_lf:
    tradeoff_pattern = "SWEET SPOT — most fertile systems are high-stability"
elif hs_hf == 0 and ls_hf == 0:
    tradeoff_pattern = "STERILE LANDSCAPE — no fertile systems in viable region"
elif hs_hf > 0 and ls_hf > 0:
    tradeoff_pattern = "BIMODAL — fertility possible at both high and low stability"
else:
    tradeoff_pattern = "MIXED — no clear pattern dominates"

print(f"    Pattern: {tradeoff_pattern}")

# ============================================================
# WRITE DELIVERABLES
# ============================================================

# 1. Stability-fertility matrix (all configs)
with open(OUT / "t075_stability_fertility_matrix.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["domain", "name", "viable", "fertile",
                 "stability", "fertility", "quadrant"])
    for c in ALL_CONFIGS:
        # Assign quadrant
        if not c["viable"]:
            q = "nonviable"
        else:
            if c["stability"] >= mean_s and c["fertility"] >= mean_f:
                q = "HS/HF"
            elif c["stability"] >= mean_s:
                q = "HS/LF"
            elif c["fertility"] >= mean_f:
                q = "LS/HF"
            else:
                q = "LS/LF"
        w.writerow([c["domain"], c["name"], str(c["viable"]), str(c["fertile"]),
                     c["stability"], c["fertility"], q])

print(f"\nWrote t075_stability_fertility_matrix.csv")

# 2. Tradeoff curves
with open(OUT / "t075_tradeoff_curves.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["domain", "name", "viable", "fertile", "stability", "fertility"])
    for c in ALL_CONFIGS:
        w.writerow([c["domain"], c["name"], str(c["viable"]), str(c["fertile"]),
                     c["stability"], c["fertility"]])

print(f"Wrote t075_tradeoff_curves.csv")

# 3. Quadrant analysis
with open(OUT / "t075_quadrant_analysis.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["quadrant", "label", "count", "examples"])
    for q in ["HS/HF", "HS/LF", "LS/HF", "LS/LF"]:
        labels = {"HS/HF": "High stability, High fertility",
                  "HS/LF": "High stability, Low fertility",
                  "LS/HF": "Low stability, High fertility",
                  "LS/LF": "Low stability, Low fertility"}
        confs = quadrants[q]
        examples = "; ".join([c["name"] for c in confs[:5]])
        w.writerow([q, labels[q], len(confs), examples])

print(f"Wrote t075_quadrant_analysis.csv")

# 4. Boundary regimes
with open(OUT / "t075_boundary_regimes.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["bin", "stability_lo", "stability_hi", "n_configs",
                 "mean_fertility", "max_fertility"])
    for i in range(n_bins):
        lo = min_s + i * bin_width
        hi = lo + bin_width
        bin_confs = [c for c in viable_configs if lo <= c["stability"] < hi]
        if not bin_confs:
            continue
        w.writerow([i+1, round(lo, 2), round(hi, 2), len(bin_confs),
                     round(sum(c["fertility"] for c in bin_confs)/len(bin_confs), 2),
                     round(max(c["fertility"] for c in bin_confs), 2)])

print(f"Wrote t075_boundary_regimes.csv")

# 5. Cross-domain tradeoffs
with open(OUT / "t075_cross_domain_tradeoffs.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["domain", "n_viable", "n_fertile", "n_merely_viable",
                 "mean_stability", "mean_fertility",
                 "fertile_mean_stability", "merely_viable_mean_stability",
                 "correlation_r"])
    for d in DOMAIN_DATA:
        dname = d["domain"]
        domain_viable = [c for c in d["configs"] if c["viable"]]
        domain_fertile = [c for c in d["configs"] if c["fertile"]]
        domain_mv = [c for c in d["configs"] if c["viable"] and not c["fertile"]]
        if not domain_viable:
            continue
        ds = [c["stability"] for c in domain_viable]
        df = [c["fertility"] for c in domain_viable]
        r = pearson(ds, df)
        fms = sum(c["stability"] for c in domain_fertile)/len(domain_fertile) if domain_fertile else 0
        mvs = sum(c["stability"] for c in domain_mv)/len(domain_mv) if domain_mv else 0
        w.writerow([dname, len(domain_viable), len(domain_fertile),
                     len(domain_mv), round(sum(ds)/len(ds), 2),
                     round(sum(df)/len(df), 2), round(fms, 2),
                     round(mvs, 2), round(r, 3)])

print(f"Wrote t075_cross_domain_tradeoffs.csv")

# 6. Summary
summary = {
    "audit": "T075 — Stability/Fertility Tradeoff Audit",
    "global_correlation_r": round(r_global, 3),
    "viable_only_correlation_r": round(r_viable, 3),
    "relationship_type": rel_type,
    "quadrant_distribution": {
        "HS/HF (sweet spot)": len(quadrants["HS/HF"]),
        "HS/LF (sterile fortress)": len(quadrants["HS/LF"]),
        "LS/HF (edge of chaos)": len(quadrants["LS/HF"]),
        "LS/LF (collapse zone)": len(quadrants["LS/LF"]),
    },
    "max_fertility_system": {
        "name": max_fert_config["name"],
        "domain": max_fert_config["domain"],
        "stability": max_fert_config["stability"],
        "fertility": max_fert_config["fertility"],
    },
    "boundary_regime_found": fert_centered < mv_centered,
    "fertile_mean_distance_from_midpoint": round(fert_centered, 3),
    "merely_viable_mean_distance_from_midpoint": round(mv_centered, 3),
    "tradeoff_pattern": tradeoff_pattern,
    "conclusion": (
        "Across all four domains, fertility and stability show a "
        + ("boundary relationship: maximum fertility occurs not at extreme "
           "stability but at intermediate values, consistent with the "
           "'edge of chaos' hypothesis." if fert_centered < mv_centered
           else "monotone relationship: fertility does not specifically peak "
           "at intermediate stability." )
    ),
}

with open(OUT / "t075_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print(f"Wrote t075_summary.json")

# Markdown report
with open(OUT / "t075_report.md", "w") as f:
    f.write("""T075: Stability/Fertility Tradeoff Audit
=========================================

## Question

Is fertility maximized by stability, opposed to stability, or produced
at the boundary between order and instability?

---

## Method

30 configurations across 4 domains scored on composites:

""")
    f.write(f"Stability  = (C + P + R) / 3\n")
    f.write(f"Fertility  = (SR + NP + RC + RD + OE) / 5\n\n")

    f.write(f"""
---

## Results

### A1: Global Correlation

""")
    f.write(f"- All systems:         r = {r_global:+.3f}\n")
    f.write(f"- Viable only:         r = {r_viable:+.3f}\n")
    f.write(f"- Fertile only:        r = {r_fertile:+.3f}\n")

    f.write(f"""
### A2: Quadrant Analysis

| Quadrant | Count | Interpretation |
|----------|-------|----------------|
""")
    for q in ["HS/HF", "HS/LF", "LS/HF", "LS/LF"]:
        labels = {"HS/HF": "High stability, High fertility (sweet spot)",
                  "HS/LF": "High stability, Low fertility (sterile fortress)",
                  "LS/HF": "Low stability, High fertility (edge of chaos)",
                  "LS/LF": "Low stability, Low fertility (collapse zone)"}
        f.write(f"| {q} | {len(quadrants[q])} | {labels[q]} |\n")

    f.write(f"""
### A3: Boundary Regime

""")
    f.write(f"- Fertile systems:     mean distance from stability midpoint = {fert_centered:.3f}\n")
    f.write(f"- Merely viable:       mean distance from stability midpoint = {mv_centered:.3f}\n")
    if fert_centered < mv_centered:
        f.write("- Fertile systems cluster CLOSER to the stability midpoint.\n")
        f.write("- Pattern: EDGE OF CHAOS — maximum fertility at intermediate stability.\n")
    else:
        f.write("- Fertile systems NOT specifically clustered at midpoint.\n")

    f.write(f"""
### A4: Domain Comparison

| Domain | Mean Stability | Mean Fertility | r (viable) |
|--------|---------------|---------------|------------|
""")
    for d in DOMAIN_DATA:
        dname = d["domain"]
        domain_viable = [c for c in d["configs"] if c["viable"]]
        if not domain_viable:
            continue
        ds = [c["stability"] for c in domain_viable]
        df = [c["fertility"] for c in domain_viable]
        r = pearson(ds, df)
        f.write(f"| {dname} | {sum(ds)/len(ds):.2f} | {sum(df)/len(df):.2f} | {r:+.3f} |\n")

    f.write(f"""
---

## Interpretation

### The Boundary Hypothesis

The data supports the hypothesis that maximum fertility occurs
near, but not at, maximum stability.

Fertile systems are closer to the stability midpoint than
merely-viable systems. This is consistent with:
- Evolution favoring systems at the edge of chaos
- Innovation occurring near instability boundaries
- The book's fine-tuning logic: the viable region is narrow

### Why This Matters

If reality were optimizing for stability, we would expect:
- Highly stable systems (crystals, fixed points, complete theories)
- Low fertility (no change, no novelty)

If reality were optimizing for fertility subject to stability:
- Systems near the order-chaos boundary
- High generativity
- Moderate coherence and recoverability (traded off for novelty)

The data supports the second interpretation. Reality looks more
like a rainforest than a crystal.

### What the Substrate Shows

The 9-assumption substrate achieves stability = 0.87, fertility = 0.81.
It sits in the High-High quadrant — the sweet spot. Its stability is
not maximized (that would sacrifice its self-modeling capacity), and
its fertility is not maximized (that would require lower coherence
and recoverability).

This is consistent with a design that balances both constraints.
""")

print(f"Wrote t075_report.md")

print(f"\nT075 complete.")
