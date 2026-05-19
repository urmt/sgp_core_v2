import numpy as np
import json
import os
from scipy.spatial.distance import euclidean
from scipy.stats import entropy

np.random.seed(42)

OUTPUT_DIR = "/home/student/sgp_core_v2/outputs/time_order_causal_chain"
os.makedirs(OUTPUT_DIR, exist_ok=True)

N = 4000
t = np.linspace(0,40,N)

# ---------------------------------------------------
# SIGNALS
# ---------------------------------------------------

evolving = (
    np.sin(2*np.pi*(3 + 25*t/40)*t)
    * (1 + 0.8*t/40)
    + 0.3*np.sin(2*np.pi*80*(t/40)**2)
)

replay = np.tile(evolving[:1000],4)

stitched = np.concatenate([
    evolving[0:1000],
    evolving[2000:3000],
    evolving[1000:2000],
    evolving[3000:4000]
])

time_reversed = evolving[::-1]

static = np.sin(2*np.pi*5*t)

random_signal = np.random.randn(N)

cyclic_loop = np.sin(2*np.pi*3*t) + 0.2*np.sin(2*np.pi*9*t)

signals = {
    "evolving": evolving,
    "replay": replay,
    "stitched": stitched,
    "time_reversed": time_reversed,
    "static": static,
    "random": random_signal,
    "cyclic_loop": cyclic_loop
}

# ---------------------------------------------------
# DISCRETIZATION
# ---------------------------------------------------

def discretize(sig,bins=16):
    edges = np.linspace(np.min(sig),np.max(sig),bins+1)
    return np.digitize(sig,edges[:-1])

# ---------------------------------------------------
# METRIC 1:
# ORDERED CAUSAL CHAIN ENTROPY
# ---------------------------------------------------

def ordered_chain_entropy(sig):

    x = discretize(sig)

    chains = {}

    for i in range(len(x)-3):

        key = (
            x[i],
            x[i+1],
            x[i+2],
            x[i+3]
        )

        chains[key] = chains.get(key,0)+1

    vals = np.array(list(chains.values()),dtype=float)

    p = vals / np.sum(vals)

    return entropy(p)

# ---------------------------------------------------
# METRIC 2:
# IRREVERSIBLE LAG ASYMMETRY
# ---------------------------------------------------

def irreversible_lag_asymmetry(sig,maxlag=25):

    vals = []

    for lag in range(1,maxlag):

        fwd = np.corrcoef(sig[:-lag],sig[lag:])[0,1]
        rev = np.corrcoef(sig[lag:],sig[:-lag])[0,1]

        vals.append(abs(fwd-rev))

    return np.mean(vals)

# ---------------------------------------------------
# METRIC 3:
# FORWARD MOTIF ACCUMULATION
# ---------------------------------------------------

def forward_motif_accumulation(sig):

    x = discretize(sig)

    motifs = []

    for i in range(len(x)-2):

        a,b,c = x[i],x[i+1],x[i+2]

        score = (
            (b-a) +
            (c-b)
        )

        motifs.append(score)

    motifs = np.array(motifs)

    cumulative = np.cumsum(motifs)

    return np.std(cumulative) / (len(cumulative)+1e-9)

# ---------------------------------------------------
# METRIC 4:
# TEMPORAL COMPRESSION ASYMMETRY
# ---------------------------------------------------

def temporal_compression_asymmetry(sig,window=64):

    x = discretize(sig)

    fwd_complexity = []
    rev_complexity = []

    for i in range(0,len(x)-window,window):

        chunk = x[i:i+window]

        transitions = np.sum(
            chunk[1:] != chunk[:-1]
        )

        compressed = transitions / window

        fwd_complexity.append(compressed)

        rchunk = chunk[::-1]

        rtrans = np.sum(
            rchunk[1:] != rchunk[:-1]
        )

        rcompressed = rtrans / window

        rev_complexity.append(rcompressed)

    return abs(
        np.mean(fwd_complexity)
        -
        np.mean(rev_complexity)
    )

# ---------------------------------------------------
# COMPUTE
# ---------------------------------------------------

results = {}

for name,sig in signals.items():

    vec = {
        "chain_entropy":
            ordered_chain_entropy(sig),

        "lag_asymmetry":
            irreversible_lag_asymmetry(sig),

        "motif_accumulation":
            forward_motif_accumulation(sig),

        "compression_asymmetry":
            temporal_compression_asymmetry(sig)
    }

    results[name] = vec

# ---------------------------------------------------
# DISTANCES
# ---------------------------------------------------

evec = np.array(
    list(results["evolving"].values())
)

distances = {}

for k,v in results.items():

    if k == "evolving":
        continue

    distances[k] = euclidean(
        evec,
        np.array(list(v.values()))
    )

# ---------------------------------------------------
# METRIC CORRELATION
# ---------------------------------------------------

metric_names = list(results["evolving"].keys())

metric_matrix = []

for m in metric_names:

    metric_matrix.append([
        results[s][m]
        for s in signals.keys()
    ])

metric_matrix = np.array(metric_matrix)

corr = np.corrcoef(metric_matrix)

max_corr = np.max(
    np.abs(
        corr[np.triu_indices_from(corr,1)]
    )
)

# ---------------------------------------------------
# SUCCESS CONDITIONS
# ---------------------------------------------------

conditions = {

    "replay_distance_pass":
        distances["replay"] > 0.20,

    "stitched_distance_pass":
        distances["stitched"] > 0.25,

    "reverse_distance_pass":
        distances["time_reversed"] > 0.40,

    "metric_corr_pass":
        max_corr < 0.90
}

collapse_detected = not all(
    conditions.values()
)

# ---------------------------------------------------
# CONTRADICTIONS
# ---------------------------------------------------

contradictions = []

if distances["replay"] < 0.20:
    contradictions.append(
        "REPLAY COLLAPSE"
    )

if distances["stitched"] < 0.25:
    contradictions.append(
        "STITCHED COLLAPSE"
    )

if distances["time_reversed"] < 0.40:
    contradictions.append(
        "TIME REVERSAL COLLAPSE"
    )

if max_corr >= 0.90:
    contradictions.append(
        "METRIC REDUNDANCY DETECTED"
    )

# ---------------------------------------------------
# DEAD METRIC CHECK
# ---------------------------------------------------

dead_metrics = []

for m in metric_names:

    vals = [
        results[s][m]
        for s in signals.keys()
    ]

    if np.std(vals) < 1e-8:
        dead_metrics.append(m)

# ---------------------------------------------------
# SAVE
# ---------------------------------------------------

output = {
    "results": results,
    "distances": distances,
    "metric_correlations": corr.tolist(),
    "max_metric_corr": float(max_corr),
    "conditions": {k: bool(v) for k,v in conditions.items()},
    "collapse_detected": bool(collapse_detected),
    "contradictions": contradictions,
    "dead_metrics": dead_metrics
}

path = os.path.join(
    OUTPUT_DIR,
    "v2_042_results.json"
)

with open(path,"w") as f:
    json.dump(output,f,indent=2)

# ---------------------------------------------------
# REPORT
# ---------------------------------------------------

print("\nV2_042 TIME-ORDER CAUSAL CHAIN AUDIT\n")

print("Distances:")
for k,v in distances.items():
    print(f"{k:20s}: {v:.6f}")

print("\nMax Metric Correlation:")
print(round(max_corr,6))

print("\nConditions:")
for k,v in conditions.items():
    print(f"{k:30s}: {v}")

print("\nDead Metrics:")
for m in dead_metrics:
    print("-",m)

print("\nCollapse Detected:",collapse_detected)

print("\nContradictions:")
for c in contradictions:
    print("-",c)

print("\nSaved:")
print(path)
