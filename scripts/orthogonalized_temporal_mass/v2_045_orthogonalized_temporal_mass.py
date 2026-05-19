import os
import json
import numpy as np
from scipy.signal import hilbert
from scipy.stats import entropy
from scipy.spatial.distance import euclidean

OUTDIR = "/home/student/sgp_core_v2/outputs/orthogonalized_temporal_mass"
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
    return float(np.sum(np.abs(ddx) * weights))

def directional_phase_dispersion(x):
    analytic = hilbert(x)
    phase = np.unwrap(np.angle(analytic))
    dphase = np.diff(phase)
    pos = np.linspace(0, 1, len(dphase))
    weighted = dphase * (pos**3)
    thirds = np.array_split(weighted, 3)
    means = [np.std(s) for s in thirds]
    return float(means[-1] - means[0])

def positional_transition_entropy(x):
    bins = np.digitize(x, np.quantile(x, [0.2,0.4,0.6,0.8]))
    transitions = {}
    for i in range(len(bins)-1):
        key = (bins[i], bins[i+1])
        pos_weight = ((i / len(bins))**3) + 1e-9
        transitions[key] = transitions.get(key, 0) + pos_weight
    vals = np.array(list(transitions.values()))
    probs = vals / np.sum(vals)
    return float(entropy(probs))

def late_stage_instability(x):
    win = 64
    vals = []
    for i in range(0, len(x)-win, win):
        seg = x[i:i+win]
        instability = np.std(np.diff(seg))
        pos = i / len(x)
        vals.append(instability * (pos**5))
    vals = np.array(vals)
    split = len(vals)//2
    early = np.mean(vals[:split])
    late = np.mean(vals[split:])
    return float(late - early)

metric_functions = {
    "amplified_temporal_mass": amplified_temporal_mass,
    "directional_phase_dispersion": directional_phase_dispersion,
    "positional_transition_entropy": positional_transition_entropy,
    "late_stage_instability": late_stage_instability
}

results = {}
for name, sig in signals.items():
    results[name] = {}
    for metric_name, fn in metric_functions.items():
        try:
            results[name][metric_name] = float(fn(sig))
        except Exception:
            results[name][metric_name] = float("nan")

def vec(name):
    return np.array([results[name][m] for m in metric_functions])

evolving_vec = vec("evolving")
distances = {}
for target in ["replay", "stitched", "time_reversed"]:
    distances[target] = float(euclidean(evolving_vec, vec(target)))

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

outfile = os.path.join(OUTDIR, "v2_045_results.json")
with open(outfile, "w") as f:
    json.dump(payload, f, indent=2)

print("\nV2_045 ORTHOGONALIZED TEMPORAL MASS AUDIT - RESULTS\n")
print("SUCCESS CONDITIONS\n")
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

print("\nCORRELATION MATRIX\n")
print(corr)
print("\nMAX METRIC CORRELATION")
print(max_corr)

print("\nCONTRADICTIONS")
for c in contradictions:
    print(c)

print("\nGATE STATUS")
print("OPEN" if gate_open else "CLOSED")
print(f"\nSaved to: {outfile}")
