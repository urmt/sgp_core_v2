import os
import json
import numpy as np
from scipy.signal import detrend
from scipy.fft import rfft
from itertools import combinations

OUTPUT_DIR = "/home/student/sgp_core_v2/outputs/asymptotic_orthogonality"
os.makedirs(OUTPUT_DIR, exist_ok=True)

SEEDS = [1,2,3,4,5]
SCALES = [100,250,500,1000,2000,4000,8000]

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

def random_signal(N, seed):
    rng = np.random.default_rng(seed)
    return rng.normal(size=N)

def fft_low_high(x, frac=0.05):
    X = rfft(x)
    n = len(X)
    cutoff = max(1, int(frac * n))
    low = X.copy()
    high = X.copy()
    low[cutoff:] = 0
    high[:cutoff] = 0
    low_sig = np.fft.irfft(low, n=len(x))
    high_sig = np.fft.irfft(high, n=len(x))
    return low_sig, high_sig

def extract_metrics(x):
    return np.array([
        amplified_temporal_mass(x),
        directional_ngram_irreversibility(x),
        oriented_phase_area(x),
        directional_lz_complexity_gradient(x)
    ], dtype=float)

def compute_max_corr(metrics_dict):
    """metrics_dict: signal_name -> 4-element array.
    Returns max pairwise correlation of 4 metrics across signal types.
    """
    mat = np.array(list(metrics_dict.values()))  # n_signals x 4
    if mat.shape[0] < 3:
        return 0.0, 0.0
    try:
        c = np.corrcoef(mat.T)  # 4x4
        upper = [abs(c[i,j]) for i,j in combinations(range(4),2)]
        return float(max(upper)), float(min(upper))
    except:
        return float("nan"), float("nan")

results = []

for seed in SEEDS:
    for N in SCALES:
        x = evolving_signal(N, seed)
        rep = replay_signal(x)
        sti = stitched_signal(x)
        rev = reverse_signal(x)
        rnd = random_signal(N, seed+100)

        # Raw signals
        raw_metrics = {
            "evolving": extract_metrics(x),
            "replay": extract_metrics(rep),
            "stitched": extract_metrics(sti),
            "reverse": extract_metrics(rev),
            "random": extract_metrics(rnd)
        }

        # Same transforms on detrended signal
        xd = detrend(x)
        repd = replay_signal(xd)
        stid = stitched_signal(xd)
        revd = reverse_signal(xd)
        det_metrics = {
            "evolving": extract_metrics(xd),
            "replay": extract_metrics(repd),
            "stitched": extract_metrics(stid),
            "reverse": extract_metrics(revd),
            "random": extract_metrics(rnd)
        }

        # Low frequency
        xl, xh = fft_low_high(x)
        repl = replay_signal(xl)
        stil = stitched_signal(xl)
        revl = reverse_signal(xl)
        low_metrics = {
            "evolving": extract_metrics(xl),
            "replay": extract_metrics(repl),
            "stitched": extract_metrics(stil),
            "reverse": extract_metrics(revl),
            "random": extract_metrics(rnd)
        }

        # High frequency
        reph = replay_signal(xh)
        stih = stitched_signal(xh)
        revh = reverse_signal(xh)
        high_metrics = {
            "evolving": extract_metrics(xh),
            "replay": extract_metrics(reph),
            "stitched": extract_metrics(stih),
            "reverse": extract_metrics(revh),
            "random": extract_metrics(rnd)
        }

        raw_max, raw_min = compute_max_corr(raw_metrics)
        det_max, _ = compute_max_corr(det_metrics)
        low_max, _ = compute_max_corr(low_metrics)
        high_max, _ = compute_max_corr(high_metrics)

        results.append({
            "seed": seed,
            "N": N,
            "raw_max_corr": raw_max,
            "detrended_max_corr": det_max,
            "low_freq_max_corr": low_max,
            "high_freq_max_corr": high_max,
            "raw_min_corr": raw_min
        })

summary = {
    "protocol": "V2_048_ASYMPTOTIC_ORTHOGONALITY_AUDIT",
    "results": results
}

outpath = os.path.join(OUTPUT_DIR, "v2_048_results.json")
with open(outpath, "w") as f:
    json.dump(summary, f, indent=2)

print("\nV2_048 ASYMPTOTIC ORTHOGONALITY AUDIT\n")
print(f"{'N':>5}  {'raw_max':>8}  {'detrend_max':>10}  {'low_max':>8}  {'high_max':>8}  {'raw_min':>8}")

for N in SCALES:
    rs = [r for r in results if r["N"]==N]
    rmax = np.mean([r["raw_max_corr"] for r in rs])
    dmax = np.mean([r["detrended_max_corr"] for r in rs])
    lmax = np.mean([r["low_freq_max_corr"] for r in rs])
    hmax = np.mean([r["high_freq_max_corr"] for r in rs])
    rmin = np.mean([r["raw_min_corr"] for r in rs])
    
    print(f"N={N:5d}  {rmax:.4f}     {dmax:.4f}       {lmax:.4f}     {hmax:.4f}     {rmin:.4f}")

print(f"\nSaved: {outpath}")
