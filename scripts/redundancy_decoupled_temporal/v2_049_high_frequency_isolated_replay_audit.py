import os
import json
import numpy as np
from scipy.fft import rfft
from scipy.spatial.distance import euclidean
from itertools import combinations

OUTPUT_DIR = "/home/student/sgp_core_v2/outputs/high_frequency_isolated"
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
    walk = np.cumsum(rng.normal(size=N))
    trend = np.linspace(0, 10, N)
    return walk + trend

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

def high_frequency_component(x, frac=0.05):
    X = rfft(x)
    n = len(X)
    cutoff = int(frac * n)
    X[:cutoff] = 0
    return np.fft.irfft(X, n=len(x))

def extract_metrics(x):
    return np.array([
        amplified_temporal_mass(x),
        directional_ngram_irreversibility(x),
        oriented_phase_area(x),
        directional_lz_complexity_gradient(x)
    ], dtype=float)

results = []

for seed in SEEDS:
    for N in SCALES:
        evo = high_frequency_component(evolving_signal(N, seed))
        rep = high_frequency_component(replay_signal(evo))
        sti = high_frequency_component(stitched_signal(evo))
        rev = high_frequency_component(reverse_signal(evo))

        M = {
            "evolving": extract_metrics(evo),
            "replay": extract_metrics(rep),
            "stitched": extract_metrics(sti),
            "reverse": extract_metrics(rev)
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

        gate = (
            replay_dist > THRESHOLDS["replay_distance"] and
            stitched_dist > THRESHOLDS["stitched_distance"] and
            reverse_dist > THRESHOLDS["reverse_distance"] and
            max_corr < THRESHOLDS["metric_corr"]
        )

        results.append({
            "seed": seed,
            "N": N,
            "replay_distance": replay_dist,
            "stitched_distance": stitched_dist,
            "reverse_distance": reverse_dist,
            "max_metric_corr": max_corr,
            "gate_open": bool(gate)
        })

gate_rate = float(np.mean([r["gate_open"] for r in results]))

summary = {
    "protocol": "V2_049_HIGH_FREQUENCY_ISOLATED_REPLAY_AUDIT",
    "gate_open_rate": gate_rate,
    "results": results
}

outpath = os.path.join(OUTPUT_DIR, "v2_049_results.json")
with open(outpath, "w") as f:
    json.dump(summary, f, indent=2)

print("\nV2_049 HIGH-FREQUENCY ISOLATED REPLAY AUDIT\n")
print(f"Gate-open rate: {gate_rate:.4f} ({int(gate_rate*len(results))}/{len(results)})")
print(f"\nPer-trial breakdown:\n")
print(f"{'seed':>4} {'N':>5} {'replay':>8} {'stitch':>8} {'reverse':>8} {'corr':>8} {'gate':>6}")
for r in results:
    status = "OPEN" if r["gate_open"] else "CLOSED"
    print(f"{r['seed']:4d} {r['N']:5d} {r['replay_distance']:>8.3f} {r['stitched_distance']:>8.3f} {r['reverse_distance']:>8.3f} {r['max_metric_corr']:>8.4f} {status:>6}")

print(f"\nSaved: {outpath}")
