import numpy as np
import json
from scipy.signal import hilbert
from scipy.stats import entropy
from itertools import product
from pathlib import Path

np.random.seed(42)

OUTPUT_DIR = Path("/home/student/sgp_core_v2/outputs/geometry_stabilization")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

N = 4000
NUM_TRAJECTORIES = 250
WINDOW = 64

def generate_evolving(n):
    t = np.linspace(0, 1, n)
    trend = 0.4 * t
    chirp = np.sin(2 * np.pi * (4*t + 12*t**2))
    noise = np.cumsum(np.random.randn(n)) * 0.01
    return chirp + trend + noise

def replay_signal(x):
    return np.tile(x[:len(x)//4], 4)

def stitched_signal(x):
    chunks = np.array_split(x, 8)
    np.random.shuffle(chunks)
    return np.concatenate(chunks)

def reverse_signal(x):
    return x[::-1]

def amplified_temporal_mass(x):
    dx = np.gradient(x)
    w = np.linspace(1, 10, len(x))**2
    return float(np.sum(np.abs(dx) * w))

def directional_ngram_irreversibility(x, bins=8, ngram=3):
    q = np.digitize(x, np.histogram(x, bins=bins)[1][:-1])

    def grams(seq):
        return list(zip(*[seq[i:] for i in range(ngram)]))

    fwd = grams(q)
    rev = grams(q[::-1])

    vocab = list(set(fwd + rev))

    pf = np.array([fwd.count(v)+1 for v in vocab], dtype=float)
    pr = np.array([rev.count(v)+1 for v in vocab], dtype=float)

    pf /= pf.sum()
    pr /= pr.sum()

    return float(entropy(pf, pr))

def oriented_phase_area(x):
    analytic = hilbert(x)
    phase = np.unwrap(np.angle(analytic))
    amp = np.abs(analytic)
    return float(np.mean(np.gradient(phase) * amp))

def directional_lz_complexity_gradient(x):
    binary = (x > np.median(x)).astype(int)

    def lz(seq):
        s = ''.join(map(str, seq))
        i, c, l = 0, 1, 1
        while True:
            if i + l > len(s):
                return c
            sub = s[i:i+l]
            prev = s[:i]
            if sub in prev:
                l += 1
            else:
                c += 1
                i += l
                l = 1

    early = lz(binary[:len(binary)//2])
    late = lz(binary[len(binary)//2:])
    return float(late - early)

METRICS = {
    "mass": amplified_temporal_mass,
    "ngram": directional_ngram_irreversibility,
    "phase": oriented_phase_area,
    "lz": directional_lz_complexity_gradient
}

all_vectors = []

for seed in range(NUM_TRAJECTORIES):
    np.random.seed(seed)
    evo = generate_evolving(N)

    variants = {
        "evolving": evo,
        "replay": replay_signal(evo),
        "stitched": stitched_signal(evo),
        "reverse": reverse_signal(evo)
    }

    for label, sig in variants.items():
        vec = []
        for name, fn in METRICS.items():
            try:
                val = float(fn(sig))
            except:
                val = np.nan
            vec.append(val)

        all_vectors.append({
            "seed": seed,
            "label": label,
            "vector": vec
        })

matrix = np.array([x["vector"] for x in all_vectors])
corr = np.corrcoef(matrix.T)
max_corr = float(np.max(np.abs(corr[np.triu_indices_from(corr, k=1)])))

def mean_vector(label):
    rows = [x["vector"] for x in all_vectors if x["label"] == label]
    return np.mean(rows, axis=0)

evo_v = mean_vector("evolving")
rep_v = mean_vector("replay")
sti_v = mean_vector("stitched")
rev_v = mean_vector("reverse")

replay_distance = float(np.linalg.norm(evo_v - rep_v))
stitched_distance = float(np.linalg.norm(evo_v - sti_v))
reverse_distance = float(np.linalg.norm(evo_v - rev_v))

gate_open = bool(
    replay_distance > 0.20 and
    stitched_distance > 0.25 and
    reverse_distance > 0.40 and
    max_corr < 0.90
)

results = {
    "num_trajectories": NUM_TRAJECTORIES,
    "N": N,
    "replay_distance": replay_distance,
    "stitched_distance": stitched_distance,
    "reverse_distance": reverse_distance,
    "max_metric_corr": max_corr,
    "gate_open": gate_open,
    "correlation_matrix": corr.tolist()
}

outpath = OUTPUT_DIR / "v2_050_results.json"
with open(outpath, "w") as f:
    json.dump(results, f, indent=2)

print("\nV2_050 GEOMETRY STABILIZATION AUDIT\n")
print(f"Trajectories per family: {NUM_TRAJECTORIES}")
print(f"N: {N}")
print(f"\nReplay distance:   {replay_distance:.3f}")
print(f"Stitched distance: {stitched_distance:.3f}")
print(f"Reverse distance:  {reverse_distance:.3f}")
print(f"Max correlation:   {max_corr:.3f}")
print(f"\nGATE OPEN: {gate_open}")
print(f"\nSaved to: {outpath}")
