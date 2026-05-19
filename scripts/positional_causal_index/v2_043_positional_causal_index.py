import numpy as np
import json
import os
from scipy.spatial.distance import euclidean

np.random.seed(42)

OUTPUT_DIR = "/home/student/sgp_core_v2/outputs/positional_causal_index"
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
# POSITIONAL CHAIN DRIFT
# ---------------------------------------------------

def positional_chain_drift(sig):

    x = discretize(sig)

    chain_positions = {}

    for i in range(len(x)-3):

        chain = (
            x[i],
            x[i+1],
            x[i+2],
            x[i+3]
        )

        pos_weight = i / len(x)

        if chain not in chain_positions:
            chain_positions[chain] = []

        chain_positions[chain].append(pos_weight)

    drifts = []

    for vals in chain_positions.values():

        vals = np.array(vals)

        drift = np.std(vals)

        drifts.append(drift)

    return np.mean(drifts)

# ---------------------------------------------------
# METRIC 2:
# FORWARD POSITIONAL ACCUMULATION
# ---------------------------------------------------

def forward_positional_accumulation(sig):

    x = discretize(sig)

    accum = 0

    for i in range(len(x)-1):

        delta = x[i+1] - x[i]

        weight = i / len(x)

        accum += delta * weight

    return abs(accum) / len(x)

# ---------------------------------------------------
# METRIC 3:
# POSITION-ORDER DIVERGENCE
# ---------------------------------------------------

def position_order_divergence(sig):

    x = discretize(sig)

    first_half = x[:len(x)//2]
    second_half = x[len(x)//2:]

    hist1 = np.bincount(first_half,minlength=20).astype(float)
    hist2 = np.bincount(second_half,minlength=20).astype(float)

    hist1 /= np.sum(hist1)
    hist2 /= np.sum(hist2)

    return np.sum(np.abs(hist1-hist2))

# ---------------------------------------------------
# METRIC 4:
# DIRECTIONAL TEMPORAL MASS
# ---------------------------------------------------

def directional_temporal_mass(sig):

    x = discretize(sig)

    mass = 0

    for i in range(len(x)-2):

        a,b,c = x[i],x[i+1],x[i+2]

        curvature = (c-b) - (b-a)

        weight = (i / len(x))**2

        mass += curvature * weight

    return abs(mass) / len(x)

# ---------------------------------------------------
# COMPUTE
# ---------------------------------------------------

results = {}

for name,sig in signals.items():

    vec = {
        "chain_drift":
            positional_chain_drift(sig),

        "forward_accumulation":
            forward_positional_accumulation(sig),

        "position_divergence":
            position_order_divergence(sig),

        "temporal_mass":
            directional_temporal_mass(sig)
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

max_corr = np.nanmax(
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
# DEAD METRIC CHECK
# ---------------------------------------------------

dead_metrics = []

for m in metric_names:

    vals = np.array([
        results[s][m]
        for s in signals.keys()
    ])

    if np.std(vals) < 1e-10:
        dead_metrics.append(m)

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

if len(dead_metrics) > 0:
    contradictions.append(
        "DEAD METRICS DETECTED"
    )

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
    "dead_metrics": dead_metrics,
    "contradictions": contradictions
}

path = os.path.join(
    OUTPUT_DIR,
    "v2_043_results.json"
)

with open(path,"w") as f:
    json.dump(output,f,indent=2)

# ---------------------------------------------------
# REPORT
# ---------------------------------------------------

print("\nV2_043 POSITIONAL CAUSAL INDEX AUDIT\n")

print("Distances:")
for k,v in distances.items():
    print(f"{k:20s}: {v:.6f}")

print("\nMax Metric Correlation:")
print(round(max_corr,6))

print("\nDead Metrics:")
for m in dead_metrics:
    print("-",m)

print("\nConditions:")
for k,v in conditions.items():
    print(f"{k:30s}: {v}")

print("\nCollapse Detected:",collapse_detected)

print("\nContradictions:")
for c in contradictions:
    print("-",c)

print("\nSaved:")
print(path)
