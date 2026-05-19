import os
import json
import numpy as np
from scipy.signal import hilbert
from scipy.spatial.distance import euclidean

OUTDIR = "/home/student/sgp_core_v2/outputs/temporal_mass_amplification"
os.makedirs(OUTDIR, exist_ok=True)

np.random.seed(42)

N = 4000
t = np.linspace(0, 40, N)

def evolving_signal():
    carrier = np.sin(2*np.pi*(3*t + 0.4*t**2))
    mod = (1 + 0.8*t/40)
    osc = 0.35*np.sin(80*t**2)
    return mod * carrier + osc

def replay_signal():
    x = evolving_signal()
    return np.roll(x, N//3)

def stitched_signal():
    x = evolving_signal()
    segs = np.array_split(x, 8)
    order = [0,3,1,6,2,7,4,5]
    return np.concatenate([segs[i] for i in order])

def reversed_signal():
    return evolving_signal()[::-1]

def static_signal():
    return np.sin(2*np.pi*4*t)

def random_signal():
    return np.random.randn(N)

def cyclic_loop_signal():
    base = np.sin(2*np.pi*6*t)
    return np.tile(base[:500], N//500 + 1)[:N]

signals = {
    "evolving": evolving_signal(),
    "replay": replay_signal(),
    "stitched": stitched_signal(),
    "time_reversed": reversed_signal(),
    "static": static_signal(),
    "random": random_signal(),
    "cyclic_loop": cyclic_loop_signal()
}

def amplified_temporal_mass(x):
    dx = np.diff(x)
    ddx = np.diff(dx)
    pos = np.linspace(0, 1, len(ddx))
    weights = (pos**4) * np.exp(4*pos)
    return float(np.sum(np.abs(ddx) * weights) / len(ddx))

def directional_accumulation_gradient(x):
    thirds = np.array_split(x, 3)
    vals = []
    for i, seg in enumerate(thirds):
        dx = np.diff(seg)
        vals.append(np.mean(np.abs(dx)) * ((i+1)**3))
    return float(vals[-1] - vals[0])

def forward_path_density(x):
    win = 32
    motifs = []
    for i in range(0, len(x)-win, win):
        seg = x[i:i+win]
        curvature = np.mean(np.abs(np.diff(seg, n=2)))
        pos_weight = ((i / len(x)) + 1e-6)**3
        motifs.append(curvature * pos_weight)
    return float(np.sum(motifs))

def temporal_energy_skew(x):
    analytic = hilbert(x)
    amp = np.abs(analytic)
    pos = np.linspace(0, 1, len(amp))
    early = amp * ((1-pos)**4)
    late = amp * (pos**4)
    e1 = np.sum(early)
    e2 = np.sum(late)
    return float(np.abs(e2 - e1) / (e1 + e2 + 1e-12))

metric_functions = {
    "amplified_temporal_mass": amplified_temporal_mass,
    "directional_accumulation_gradient": directional_accumulation_gradient,
    "forward_path_density": forward_path_density,
    "temporal_energy_skew": temporal_energy_skew
}

results = {}
for name, sig in signals.items():
    results[name] = {}
    for metric_name, fn in metric_functions.items():
        try:
            results[name][metric_name] = float(fn(sig))
        except Exception:
            results[name][metric_name] = float("nan")

def metric_vector(name):
    return np.array([results[name][m] for m in metric_functions])

evolving_vec = metric_vector("evolving")
distances = {}
for target in ["replay", "stitched", "time_reversed"]:
    distances[target] = float(euclidean(evolving_vec, metric_vector(target)))

metric_matrix = []
for metric in metric_functions:
    metric_matrix.append([results[s][metric] for s in signals])
metric_matrix = np.array(metric_matrix)
corr = np.corrcoef(metric_matrix)
max_corr = np.max(np.abs(corr[np.triu_indices_from(corr, k=1)]))

success = {
    "replay_distance": distances["replay"] > 0.20,
    "stitched_distance": distances["stitched"] > 0.25,
    "reverse_distance": distances["time_reversed"] > 0.40,
    "metric_corr": max_corr < 0.90
}
gate_open = all(success.values())

contradictions = []
if not success["replay_distance"]: contradictions.append("REPLAY COLLAPSE DETECTED")
if not success["stitched_distance"]: contradictions.append("STITCHED COLLAPSE DETECTED")
if not success["reverse_distance"]: contradictions.append("TIME REVERSAL COLLAPSE DETECTED")
if not success["metric_corr"]: contradictions.append("METRIC REDUNDANCY DETECTED")

payload = {
    "results": results,
    "distances": distances,
    "correlation_matrix": corr.tolist(),
    "max_metric_corr": float(max_corr),
    "success": {k: bool(v) for k,v in success.items()},
    "contradictions": contradictions,
    "gate_open": bool(gate_open)
}

outfile = os.path.join(OUTDIR, "v2_044_results.json")
with open(outfile, "w") as f:
    json.dump(payload, f, indent=2)

print("\nV2_044 TEMPORAL MASS AMPLIFICATION AUDIT - RESULTS\n")
print("SUCCESS CONDITIONS:\n")
for k, v in success.items():
    if "distance" in k:
        actual = distances["replay"] if k == "replay_distance" else distances["stitched"] if k == "stitched_distance" else distances["time_reversed"]
        thresh = ">0.20" if k == "replay_distance" else ">0.25" if k == "stitched_distance" else ">0.40"
    else:
        actual = max_corr
        thresh = "<0.90"
    print(f"{k:25s} threshold={thresh:8s} actual={actual:.6f} {'PASS' if v else 'FAIL'}")

print("\nPER-METRIC ANALYSIS\n")
for metric in metric_functions:
    print(metric)
    for s in signals:
        print(f"  {s:15s}: {results[s][metric]:.8f}")
    print()

print("\nDISTANCES\n")
for k, v in distances.items():
    print(f"{k:15s}: {v:.6f}")

print("\nMAX METRIC CORRELATION")
print(max_corr)

print("\nCONTRADICTIONS")
for c in contradictions:
    print(c)

print("\nGATE STATUS")
print("OPEN" if gate_open else "CLOSED")
print(f"\nSaved to: {outfile}")
