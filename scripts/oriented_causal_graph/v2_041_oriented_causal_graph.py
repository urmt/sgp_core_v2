import numpy as np
import json
import os
from scipy.spatial.distance import euclidean
from scipy.stats import entropy

np.random.seed(42)

OUTPUT_DIR = "/home/student/sgp_core_v2/outputs/oriented_causal_graph"
os.makedirs(OUTPUT_DIR, exist_ok=True)

N = 4000
t = np.linspace(0, 40, N)

# ---------------------------------------------------
# SIGNALS
# ---------------------------------------------------

evolving = (
    np.sin(2*np.pi*(3 + 25*t/40)*t)
    * (1 + 0.8*t/40)
    + 0.3*np.sin(2*np.pi*80*(t/40)**2)
)

replay = np.tile(evolving[:1000], 4)

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
# STATE DISCRETIZATION
# ---------------------------------------------------

def discretize(sig, bins=12):
    edges = np.linspace(np.min(sig), np.max(sig), bins+1)
    return np.digitize(sig, edges[:-1])

# ---------------------------------------------------
# METRIC 1:
# DIRECTED TRANSITION IMBALANCE
# ---------------------------------------------------

def directed_transition_imbalance(sig):

    x = discretize(sig)

    forward = {}
    backward = {}

    for i in range(len(x)-1):
        a = x[i]
        b = x[i+1]

        forward[(a,b)] = forward.get((a,b),0)+1
        backward[(b,a)] = backward.get((b,a),0)+1

    imbalance = 0

    for edge in set(list(forward.keys()) + list(backward.keys())):
        f = forward.get(edge,0)
        b = backward.get(edge,0)

        imbalance += abs(f - b)

    return imbalance / len(x)

# ---------------------------------------------------
# METRIC 2:
# ORIENTED CYCLE FLOW
# ---------------------------------------------------

def oriented_cycle_flow(sig):

    x = discretize(sig)

    clockwise = 0
    counter = 0

    for i in range(len(x)-2):

        a,b,c = x[i],x[i+1],x[i+2]

        if a < b < c:
            clockwise += 1

        elif a > b > c:
            counter += 1

    total = clockwise + counter + 1e-9

    return abs(clockwise - counter) / total

# ---------------------------------------------------
# METRIC 3:
# FORWARD PREDICTION GAIN
# ---------------------------------------------------

def forward_prediction_gain(sig):

    x = discretize(sig)

    past = x[:-2]
    future = x[2:]

    reverse_past = x[2:]
    reverse_future = x[:-2]

    joint_forward = np.histogram2d(past,future,bins=12)[0]
    joint_reverse = np.histogram2d(reverse_past,reverse_future,bins=12)[0]

    pf = joint_forward.flatten()
    pr = joint_reverse.flatten()

    pf = pf / (np.sum(pf)+1e-9)
    pr = pr / (np.sum(pr)+1e-9)

    return entropy(pr+1e-12, pf+1e-12)

# ---------------------------------------------------
# METRIC 4:
# GRAPH FLOW DIVERGENCE
# ---------------------------------------------------

def graph_flow_divergence(sig):

    x = discretize(sig)

    outflow = {}
    inflow = {}

    for i in range(len(x)-1):

        a = x[i]
        b = x[i+1]

        outflow[a] = outflow.get(a,0)+1
        inflow[b] = inflow.get(b,0)+1

    states = sorted(set(list(outflow.keys()) + list(inflow.keys())))

    div = 0

    for s in states:
        o = outflow.get(s,0)
        inf = inflow.get(s,0)

        div += abs(o - inf)

    return div / len(x)

# ---------------------------------------------------
# COMPUTE
# ---------------------------------------------------

results = {}

for name,sig in signals.items():

    vec = {
        "transition_imbalance": directed_transition_imbalance(sig),
        "cycle_flow": oriented_cycle_flow(sig),
        "prediction_gain": forward_prediction_gain(sig),
        "flow_divergence": graph_flow_divergence(sig)
    }

    results[name] = vec

# ---------------------------------------------------
# DISTANCES
# ---------------------------------------------------

evec = np.array(list(results["evolving"].values()))

distances = {}

for k,v in results.items():

    if k == "evolving":
        continue

    distances[k] = euclidean(
        evec,
        np.array(list(v.values()))
    )

# ---------------------------------------------------
# CORRELATIONS
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

max_corr = np.max(np.abs(corr[np.triu_indices_from(corr,1)]))

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

collapse_detected = not all(conditions.values())

# ---------------------------------------------------
# CONTRADICTIONS
# ---------------------------------------------------

contradictions = []

if distances["time_reversed"] < 0.40:
    contradictions.append(
        "TIME REVERSAL COLLAPSE"
    )

if max_corr >= 0.90:
    contradictions.append(
        "METRIC REDUNDANCY DETECTED"
    )

if distances["replay"] < 0.20:
    contradictions.append(
        "REPLAY COLLAPSE"
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
    "contradictions": contradictions
}

path = os.path.join(
    OUTPUT_DIR,
    "v2_041_results.json"
)

with open(path,"w") as f:
    json.dump(output,f,indent=2)

# ---------------------------------------------------
# REPORT
# ---------------------------------------------------

print("\nV2_041 ORIENTED CAUSAL GRAPH AUDIT\n")

print("Distances:")
for k,v in distances.items():
    print(f"{k:20s}: {v:.6f}")

print("\nMax Metric Correlation:")
print(round(max_corr,6))

print("\nConditions:")
for k,v in conditions.items():
    print(f"{k:30s}: {v}")

print("\nCollapse Detected:", collapse_detected)

print("\nContradictions:")
for c in contradictions:
    print("-", c)

print("\nSaved:")
print(path)
