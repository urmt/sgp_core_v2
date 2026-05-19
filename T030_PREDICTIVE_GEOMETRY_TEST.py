#!/usr/bin/env python3
import os, json, hashlib, numpy as np
from sklearn.decomposition import PCA

ROOT="T030_PREDICTIVE_GEOMETRY"
os.makedirs(ROOT, exist_ok=True)
SEED=79
rng=np.random.default_rng(SEED)

def signed_ordinal_flow(x):
    d = np.diff(x)
    return np.mean(np.sign(d[:-1]) * np.sign(d[1:])) if len(d) > 1 else 0.0

def half_corr(x):
    n = len(x)//2
    a, b = x[:n], x[n:2*n]
    if np.std(a) == 0 or np.std(b) == 0:
        return 0.0
    return np.corrcoef(a, b)[0, 1]

def signed_compress(x):
    q = np.round((x - np.mean(x)) / (np.std(x) + 1e-8), 2)
    return -np.mean(np.abs(np.diff(q)))

def amp_transition(x):
    return np.mean(np.abs(np.diff(x)))

def embed(x):
    return np.array([
        signed_ordinal_flow(x),
        half_corr(x),
        signed_compress(x),
        amp_transition(x)
    ])

N = 512
t = np.linspace(0, 1, N)

x_logistic = np.zeros(N)
x_logistic[0] = 0.2
for i in range(N-1):
    x_logistic[i+1] = 3.99 * x_logistic[i] * (1 - x_logistic[i])

signals = {
    "chirp": np.sin(2*np.pi*(3*t + 12*t*t)),
    "rw_trend": np.cumsum(rng.normal(size=N)) + 0.002*np.arange(N),
    "telegraph": np.sign(np.sin(2*np.pi*8*t)),
    "pink_noise": np.cumsum(rng.normal(size=N)),
    "square": np.sign(np.sin(2*np.pi*5*t)),
    "chaotic_logistic": x_logistic
}

def reverse(x): return x[::-1]
def replay(x): h = len(x)//2; return np.concatenate([x[:h], x[:h]])
def stitch(x): q = len(x)//4; return np.concatenate([x[:q], x[2*q:3*q], x[q:2*q], x[3*q:]])
def swap(x): h = len(x)//2; return np.concatenate([x[h:], x[:h]])
def jitter(x): return x + 0.01 * rng.normal(size=len(x))
def blur(x): 
    k = np.ones(9)/9
    return np.array([np.mean(x[max(0,i-4):i+5]) for i in range(len(x))])
def decimate(x): y = x[::2]; return np.repeat(y, 2)[:len(x)]

OPERATORS = {
    "reverse": reverse,
    "replay": replay,
    "stitch": stitch,
    "swap": swap,
    "jitter": jitter,
    "blur": blur,
    "decimate": decimate
}

PREDICTIONS = {
    "reverse": np.array([0,0,0,0]),
    "replay": np.array([0,1,0.25,0]),
    "stitch": np.array([0,0.7,0.15,0]),
    "swap": np.array([0.5,0,0,0]),
    "jitter": np.array([0.1,0,-0.5,0.2]),
    "blur": np.array([0,0,0.7,-0.7]),
    "decimate": np.array([0,-0.8,0.2,-0.3])
}
for k in PREDICTIONS:
    v = PREDICTIONS[k]
    PREDICTIONS[k] = v / np.linalg.norm(v) if np.linalg.norm(v) > 0 else v

empirical = {}
for opname, op in OPERATORS.items():
    disps = []
    for sig in signals.values():
        d = embed(op(sig)) - embed(sig)
        disps.append(d)
    dmean = np.mean(disps, axis=0)
    empirical[opname] = dmean / np.linalg.norm(dmean) if np.linalg.norm(dmean) > 0 else dmean

alignments = {}
for opname in OPERATORS:
    pred, emp = PREDICTIONS[opname], empirical[opname]
    if np.linalg.norm(pred) == 0 and np.linalg.norm(emp) == 0:
        align = 1.0
    elif np.linalg.norm(pred) == 0 or np.linalg.norm(emp) == 0:
        align = 0.0
    else:
        align = abs(float(np.dot(pred, emp)))
    alignments[opname] = align

X = np.array([empirical[k] for k in empirical])
coords = PCA(n_components=2).fit(X).transform(X)
families = {}
for i, opname in enumerate(empirical):
    x, y = coords[i]
    families[opname] = "tau_family" if abs(x) > 0.7 else ("orthogonal_family" if abs(y) > 0.5 else "symmetry_family")

mean_alignment = np.mean(list(alignments.values()))
H1_prediction_valid = bool(mean_alignment > 0.75)
H2_replay_best = bool(alignments["replay"] == max(alignments.values()))
H3_family_structure = bool(len(set(families.values())) >= 2)

RESULTS = {
    "seed": SEED,
    "alignments": alignments,
    "mean_alignment": float(mean_alignment),
    "families": families,
    "coords": coords.tolist(),
    "checks": {
        "H1_prediction_valid": H1_prediction_valid,
        "H2_replay_best": H2_replay_best,
        "H3_family_structure": H3_family_structure
    }
}

with open(os.path.join(ROOT, "T030_RESULTS.json"), "w") as f:
    json.dump(RESULTS, f, indent=2)

sha = hashlib.sha256(json.dumps(RESULTS, sort_keys=True).encode()).hexdigest()
with open(os.path.join(ROOT, "T030.sha256"), "w") as f:
    f.write(sha)

print("\n=== T030 PREDICTIVE GEOMETRY ===\nPrediction Alignments:")
for k, v in alignments.items():
    print(f"{k:10s}: {v:.4f}")
print(f"\nMean alignment: {round(mean_alignment,4)}\nFamilies:")
for k, v in families.items():
    print(f"{k:10s}: {v}")
print(f"\nChecks: H1={H1_prediction_valid}, H2={H2_replay_best}, H3={H3_family_structure}")
print(f"\nSHA256: {sha}")