"""RD-8A: Latent Geometry Recon
Assemble EVERY metric from ALL existing studies into one matrix.
Let the geometry emerge from data, not from naming schemes.
"""

import sys, os, json, time
import numpy as np
from collections import OrderedDict

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# ─── Load all datasets ───

with open("coherence-benchmark/results/t901_ensemble.json") as f:
    t901 = json.load(f)

with open("audits/rd08_friction_sweep.json") as f:
    rd08 = json.load(f)

with open("audits/rd05_sweep_raw.json") as f:
    rd05 = json.load(f)

with open("audits/rd06_ensemble_raw.json") as f:
    rd06 = json.load(f)

# ─── Build unified matrix ───
# t901 is the backbone: 60 runs with the richest metric set
# RD-8 adds physical observables for matching friction levels
# RD-5/6 are at friction=0.30 only

# Index RD-8 by (friction, rep)
rd08_idx = {}
for r in rd08:
    key = (round(r["friction"], 3), r["rep"])
    rd08_idx[key] = r

# Index RD-5 by (rep) — all at friction=0.30
rd05_idx = {r["rep"]: r for r in rd05}

# Index RD-6 by (rep) — all at friction=0.30, 50% removal
rd06_idx = {r["run"]: r for r in rd06}

# Assemble rows
rows = []
metric_names = OrderedDict()

for t in t901:
    fr = t["friction"]
    rep = t["rep"]
    
    row = OrderedDict()
    row["source"] = "t901"
    row["friction"] = fr
    row["rep"] = rep
    
    # t901 metrics
    row["C"] = t["pre_C"]
    row["I_pred"] = t["pre_I_pred"]
    row["C_sigma"] = t["pre_C_sigma"]
    row["MSE"] = t["pre_MSE_s1"]
    row["rms_velocity"] = t["rms_velocity"]
    row["msd"] = t["msd"]
    row["neighbor_turnover"] = t["neighbor_turnover"]
    row["packing_var"] = t["packing_var"]
    
    # Recovery
    row["dip"] = t["dip"]
    row["restoration"] = t["restoration"]
    row["tau_rec"] = t["tau_rec"]
    
    # RD-8 physical observables (if available)
    key8 = (round(fr, 3), rep)
    if key8 in rd08_idx:
        r8 = rd08_idx[key8]
        row["jitter"] = r8["jitter"]
        row["persistence"] = r8["persistence"]
        row["reorg_rate"] = r8["reorg_rate"]
        row["v_autocorr"] = r8["v_autocorr"]
        row["separation"] = r8["separation"]
        row["collapsed"] = 1 if r8["collapsed"] else 0
        row["escaped_frac"] = r8["escaped_frac"]
    else:
        row["jitter"] = None
        row["persistence"] = None
        row["reorg_rate"] = None
        row["v_autocorr"] = None
        row["separation"] = None
        row["collapsed"] = 0
        row["escaped_frac"] = 0
    
    rows.append(row)

# Add RD-5 runs (friction=0.30, varying removal fraction)
for r5 in rd05:
    row = OrderedDict()
    row["source"] = "rd05"
    row["friction"] = 0.30
    row["rep"] = r5["rep"]
    row["C"] = r5["C_pre"]
    row["I_pred"] = None  # not measured
    row["C_sigma"] = None
    row["MSE"] = None
    row["rms_velocity"] = None
    row["msd"] = None
    row["neighbor_turnover"] = None
    row["packing_var"] = None
    row["dip"] = r5["dC"]
    row["restoration"] = None
    row["tau_rec"] = r5["tau_rec"]
    row["jitter"] = None
    row["persistence"] = None
    row["reorg_rate"] = None
    row["v_autocorr"] = None
    row["separation"] = None
    row["collapsed"] = 0
    row["escaped_frac"] = 0
    row["removal_fraction"] = r5["fraction"]
    rows.append(row)

# Add RD-6 runs (friction=0.30, 50% removal)
for r6 in rd06:
    row = OrderedDict()
    row["source"] = "rd06"
    row["friction"] = 0.30
    row["rep"] = r6["run"]
    row["C"] = r6["C_pre"]
    row["I_pred"] = None
    row["C_sigma"] = None
    row["MSE"] = None
    row["rms_velocity"] = None
    row["msd"] = None
    row["neighbor_turnover"] = None
    row["packing_var"] = None
    row["dip"] = r6["dC"]
    row["restoration"] = None
    row["tau_rec"] = r6["tau_rec"]
    row["jitter"] = None
    row["persistence"] = None
    row["reorg_rate"] = None
    row["v_autocorr"] = None
    row["separation"] = None
    row["collapsed"] = 1 if r6["collapsed"] else 0
    row["escaped_frac"] = 0
    row["removal_fraction"] = 0.50
    rows.append(row)

print(f"Total rows: {len(rows)}")
print(f"Sources: {sum(1 for r in rows if r['source']=='t901')} t901, "
      f"{sum(1 for r in rows if r['source']=='rd05')} rd05, "
      f"{sum(1 for r in rows if r['source']=='rd06')} rd06")

# ─── Identify columns with sufficient non-null values ───
all_keys = list(rows[0].keys())
exclude = {"source", "rep", "removal_fraction"}
candidate_keys = [k for k in all_keys if k not in exclude]

# Count non-null per key
counts = {}
for k in candidate_keys:
    n = sum(1 for r in rows if r.get(k) is not None)
    counts[k] = n

print("\nMetric completeness:")
for k, n in counts.items():
    pct = n / len(rows) * 100
    print(f"  {k:>20s}: {n:>4d}/{len(rows)} ({pct:.0f}%)")

# Use only metrics available in ≥80% of rows from the t901 backbone
# (RD-5/6 only have C and recovery metrics — that's fine, they're valuable)
# For the matrix: use metrics where at least 50 rows have values
min_count = 50
usable = [k for k in candidate_keys if counts[k] >= min_count and k not in ("collapsed", "escaped_frac")]
print(f"\nUsable metrics (≥{min_count} non-null): {usable}")

# ─── Build numeric matrix ───
# Strategy: use t901 rows as primary (richest), supplement with RD-5/6
# For PCA/FA: only rows where ALL usable metrics are non-null

# First: t901-only matrix (cleanest)
t901_rows = [r for r in rows if r["source"] == "t901"]
t901_usable = [k for k in usable if counts[k] >= len(t901_rows)]

M_t901 = []
for r in t901_rows:
    row_vals = [r[k] for k in t901_usable]
    if all(v is not None for v in row_vals):
        M_t901.append(row_vals)
M_t901 = np.array(M_t901)
print(f"\nt901 matrix: {M_t901.shape[0]} rows × {M_t901.shape[1]} columns")
print(f"  Metrics: {t901_usable}")

# Full matrix (t901 + RD-8, filling gaps)
full_rows = [r for r in rows if r["source"] in ("t901", "rd08")]
full_usable = [k for k in usable if k in t901_usable or counts[k] >= len(full_rows) * 0.5]

M_full = []
for r in full_rows:
    row_vals = [r.get(k) for k in full_usable]
    if all(v is not None for v in row_vals):
        M_full.append(row_vals)
M_full = np.array(M_full)
print(f"\nFull matrix (t901+rd08): {M_full.shape[0]} rows × {M_full.shape[1]} columns")
print(f"  Metrics: {full_usable}")

# ─── Save matrix for analysis ───
np.save("audits/rd8a_matrix_t901.npy", M_t901)
np.save("audits/rd8a_matrix_full.npy", M_full)
with open("audits/rd8a_metric_names_t901.json", "w") as f:
    json.dump(t901_usable, f)
with open("audits/rd8a_metric_names_full.json", "w") as f:
    json.dump(full_usable, f)
with open("audits/rd8a_row_metadata.json", "w") as f:
    meta = []
    for r in t901_rows:
        row_vals = [r[k] for k in t901_usable]
        if all(v is not None for v in row_vals):
            meta.append({"source": r["source"], "friction": r["friction"],
                         "rep": r["rep"]})
    json.dump(meta, f)

print(f"\nSaved: audits/rd8a_matrix_t901.npy, audits/rd8a_matrix_full.npy")
print(f"Metric names: audits/rd8a_metric_names_t901.json, audits/rd8a_metric_names_full.json")
print(f"Row metadata: audits/rd8a_row_metadata.json")
