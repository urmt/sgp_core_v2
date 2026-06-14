"""
Create condensed blinded data summaries for observer execution.
Each observer gets the same condensed data + their unique framework prompt.
"""

import json
import os
import statistics

BASE = "/home/student/sgp_core_v2"
OUT = f"{BASE}/audits/rd_observer2/blinded"

with open(f"{OUT}/dataset_granular_ensemble.json") as f:
    t901 = json.load(f)
with open(f"{OUT}/dataset_system_results.json") as f:
    t081 = json.load(f)
with open(f"{OUT}/dataset_historical_summary.txt") as f:
    hist = f.read()

# Condensed T901: summary stats per condition
conditions = {}
for run in t901:
    c = run["condition"]
    if c not in conditions:
        conditions[c] = {k: [] for k in run if k not in ("run_id", "condition")}
    for k, v in run.items():
        if k not in ("run_id", "condition"):
            conditions[c][k].append(v)

t901_summary = {}
for c, vars_dict in sorted(conditions.items()):
    t901_summary[f"condition_{c}"] = {}
    for var, vals in vars_dict.items():
        t901_summary[f"condition_{c}"][var] = {
            "mean": round(statistics.mean(vals), 4),
            "stdev": round(statistics.stdev(vals), 4) if len(vals) > 1 else 0,
            "min": round(min(vals), 4),
            "max": round(max(vals), 4),
        }

# Condensed T081: summary stats across all systems
numeric_vars = {}
for row in t081[:50]:  # first 50 systems
    for k, v in row.items():
        if k == "system_id":
            continue
        try:
            fv = float(v)
            if k not in numeric_vars:
                numeric_vars[k] = []
            numeric_vars[k].append(fv)
        except (ValueError, TypeError):
            pass

t081_summary = {}
for var, vals in sorted(numeric_vars.items())[:20]:  # top 20 variables
    t081_summary[var] = {
        "mean": round(statistics.mean(vals), 4),
        "stdev": round(statistics.stdev(vals), 4) if len(vals) > 1 else 0,
        "min": round(min(vals), 4),
        "max": round(max(vals), 4),
    }

# Correlation structure (simple pairwise for T901)
# Pick top 5 most variable variables
variances = {}
for var in ["metric_A", "metric_B", "metric_C", "metric_D", "metric_E",
            "metric_F", "metric_G", "metric_H", "metric_I", "metric_J", "metric_K"]:
    vals = [r[var] for r in t901]
    variances[var] = statistics.variance(vals) if len(vals) > 1 else 0
top_vars = sorted(variances, key=variances.get, reverse=True)[:5]

# Compute pairwise correlations for top variables
def correlation(x, y):
    n = len(x)
    if n < 3:
        return 0
    mx, my = statistics.mean(x), statistics.mean(y)
    num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    dx = sum((xi - mx) ** 2 for xi in x)
    dy = sum((yi - my) ** 2 for yi in y)
    if dx == 0 or dy == 0:
        return 0
    return num / (dx * dy) ** 0.5

correlations = {}
for i, v1 in enumerate(top_vars):
    for v2 in top_vars[i + 1:]:
        x = [r[v1] for r in t901]
        y = [r[v2] for r in t901]
        correlations[f"{v1}_vs_{v2}"] = round(correlation(x, y), 3)

condensed = f"""=== DATASET 1: Granular Simulation Ensemble (CONDENSED) ===
60 runs of a particle simulation with 11 measured variables per run.
Each run has a run_id, a condition parameter (0.05 to 0.8), and 10 metric variables (A through K).
6 conditions x 10 replicates.

Summary statistics per condition (mean +/- stdev):
{json.dumps(t901_summary, indent=2)}

Top 5 most variable metrics: {top_vars}
Pairwise correlations among top 5:
{json.dumps(correlations, indent=2)}

First 10 runs (raw):
{json.dumps(t901[:10], indent=2)}

=== DATASET 2: System Evaluation Results (CONDENSED) ===
240 systems evaluated across 37 variables. First 50 systems shown.
Variables are anonymized as var_N (some are boolean flags, some are numeric).

Summary statistics (numeric variables, top 20):
{json.dumps(t081_summary, indent=2)}

First 5 systems (raw):
{json.dumps(t081[:5], indent=2)}

=== DATASET 3: Historical Study Summary ===
Summary of 236 studies investigating complex system behavior.
Terminology has been anonymized.

{hist}
"""

with open(f"{OUT}/condensed_data.txt", "w") as f:
    f.write(condensed)

print(f"Condensed data written: {len(condensed)} characters")
