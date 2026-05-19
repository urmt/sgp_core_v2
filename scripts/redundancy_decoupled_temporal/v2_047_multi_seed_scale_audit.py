import os
import json
import numpy as np
from scipy.spatial.distance import euclidean
from itertools import combinations

OUTPUT_DIR = "/home/student/sgp_core_v2/outputs/multiseed_scale_audit"
os.makedirs(OUTPUT_DIR, exist_ok=True)

SEEDS = [1,2,3,4,5,6,7,8,9,10]
SCALES = [100,250,500,1000,2000,4000,8000]

THRESHOLDS = {
    "replay_distance": 0.20,
    "stitched_distance": 0.25,
    "reverse_distance": 0.40,
    "metric_corr": 0.90
}

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from redundancy_decoupled_temporal.v2_046_metrics import (
    amplified_temporal_mass,
    directional_ngram_irreversibility,
    oriented_phase_area,
    directional_lz_complexity_gradient
)

def evolving_signal(N, seed):
    rng = np.random.default_rng(seed)
    x = np.cumsum(rng.normal(size=N))
    trend = np.linspace(0, 10, N)
    return x + trend

def replay_signal(x):
    seg = x[:len(x)//4]
    return np.tile(seg, 4)

def stitched_signal(x):
    chunks = np.array_split(x, 8)
    rng = np.random.default_rng(0)
    rng.shuffle(chunks)
    return np.concatenate(chunks)

def reverse_signal(x):
    return x[::-1]

def random_signal(N, seed):
    rng = np.random.default_rng(seed)
    return rng.normal(size=N)

def extract_metrics(x):
    return np.array([
        amplified_temporal_mass(x),
        directional_ngram_irreversibility(x),
        oriented_phase_area(x),
        directional_lz_complexity_gradient(x)
    ], dtype=float)

all_results = []

for seed in SEEDS:
    for N in SCALES:
        evo = evolving_signal(N, seed)
        rep = replay_signal(evo)
        sti = stitched_signal(evo)
        rev = reverse_signal(evo)
        rnd = random_signal(N, seed)

        M = {
            "evolving": extract_metrics(evo),
            "replay": extract_metrics(rep),
            "stitched": extract_metrics(sti),
            "reverse": extract_metrics(rev),
            "random": extract_metrics(rnd)
        }

        replay_dist = float(euclidean(M["evolving"], M["replay"]))
        stitched_dist = float(euclidean(M["evolving"], M["stitched"]))
        reverse_dist = float(euclidean(M["evolving"], M["reverse"]))

        metric_matrix = np.array(list(M.values()))
        corr = np.corrcoef(metric_matrix.T)

        upper = []
        for i,j in combinations(range(corr.shape[0]), 2):
            upper.append(abs(corr[i,j]))

        max_corr = float(np.max(upper))

        passed = (
            replay_dist > THRESHOLDS["replay_distance"] and
            stitched_dist > THRESHOLDS["stitched_distance"] and
            reverse_dist > THRESHOLDS["reverse_distance"] and
            max_corr < THRESHOLDS["metric_corr"]
        )

        result = {
            "seed": seed,
            "N": N,
            "replay_distance": replay_dist,
            "stitched_distance": stitched_dist,
            "reverse_distance": reverse_dist,
            "max_metric_corr": max_corr,
            "gate_open": bool(passed)
        }

        all_results.append(result)

gate_rate = float(np.mean([r["gate_open"] for r in all_results]))

summary = {
    "protocol": "V2_047_MULTI_SEED_SCALE_AUDIT",
    "num_trials": len(all_results),
    "gate_open_rate": gate_rate,
    "details": all_results
}

outpath = os.path.join(OUTPUT_DIR, "v2_047_results.json")
with open(outpath, "w") as f:
    json.dump(summary, f, indent=2)

print("\nV2_047 MULTI-SEED SCALE AUDIT COMPLETE\n")
print("Trials:", len(all_results))
print("Seeds:", SEEDS)
print("Scales:", SCALES)
print("Gate-open rate:", round(gate_rate, 4))

print("\nPer-trial breakdown:")
for r in all_results:
    status = "OPEN" if r["gate_open"] else "CLOSED"
    print(f"  seed={r['seed']:2d} N={r['N']:5d}  replay={r['replay_distance']:.4f}  stitched={r['stitched_distance']:.4f}  reverse={r['reverse_distance']:.4f}  corr={r['max_metric_corr']:.4f}  gate={status}")

print("\nSaved:", outpath)
