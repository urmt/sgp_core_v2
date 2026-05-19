import numpy as np
import pandas as pd
import json
import zlib
from scipy.signal import hilbert
from scipy.spatial.distance import pdist, squareform
from sklearn.preprocessing import RobustScaler

np.random.seed(73)

N = 4096
t = np.linspace(0, 1, N)

signals = {}
signals["chirp"] = np.sin(2*np.pi*(8*t + 40*t**2))
rw = np.cumsum(np.random.randn(N))
signals["rw_trend"] = rw + 0.002*np.arange(N)
x = np.zeros(N)
x[:N//3] = np.random.randn(N//3)
x[N//3:2*N//3] = 3 + 0.3*np.random.randn(N//3)
x[2*N//3:] = np.sin(np.linspace(0, 30*np.pi, N - 2*N//3))
signals["regime_switch"] = x
r = 3.99; x = np.zeros(N); x[0] = 0.2
for i in range(N-1): x[i+1] = r*x[i]*(1-x[i])
signals["chaotic_logistic"] = x
signals["coupled_osc"] = (
    np.sin(2*np.pi*7*t) + 0.5*np.sin(2*np.pi*13*t + 0.2*np.sin(2*np.pi*3*t))
)

def replay(x): return np.concatenate([x[:len(x)//2], x[:len(x)//2]])
def stitch(x):
    thirds = np.array_split(x, 3)
    return np.concatenate([thirds[2], thirds[0], thirds[1]])
def reverse(x): return x[::-1]
def swap_halves(x):
    return np.concatenate([x[len(x)//2:], x[:len(x)//2]])

TRANSFORMS = {
    "base": lambda x: x, "replay": replay,
    "stitch": stitch, "reverse": reverse,
    "swap": swap_halves
}

# M1: ordinal transition cycle flux (directional, combinatorial)
def ordinal_sequence(x, d=3):
    seq = [tuple(np.argsort(x[i:i+d])) for i in range(len(x)-d)]
    uniq = {p:i for i,p in enumerate(sorted(set(seq)))}
    return np.array([uniq[s] for s in seq])

def transition_matrix(seq, n):
    P = np.zeros((n,n))
    for a,b in zip(seq[:-1], seq[1:]):
        P[a,b] += 1
    P += 1e-9
    P /= P.sum(axis=1, keepdims=True)
    return P

def cycle_flux(P):
    return np.sum(np.abs(P - P.T))

# M2: third-order time irreversibility (directional, moment-based)
def time_irreversibility(x, max_lag=5):
    xc = x - np.mean(x)
    scores = []
    for tau in range(1, max_lag+1):
        fwd = np.mean(xc[:-tau]**2 * xc[tau:])
        bwd = np.mean(xc[:-tau] * xc[tau:]**2)
        scores.append(abs(fwd - bwd))
    return np.mean(scores)

# M3: directional compressibility (information-theoretic)
def compressibility_asymmetry(x):
    xf = zlib.compress(np.asarray(x, dtype=np.float32).tobytes())
    xr = zlib.compress(np.asarray(x[::-1], dtype=np.float32).tobytes())
    return abs(len(xf) - len(xr))

# M4: phase-space temporal anisotropy (frequency-domain)
def phase_anisotropy(x):
    z = hilbert(x)
    phase = np.unwrap(np.angle(z))
    vel = np.diff(phase)
    acc = np.diff(vel)
    fwd = np.mean(np.abs(acc[acc > 0])) if np.any(acc > 0) else 0
    rev = np.mean(np.abs(acc[acc < 0])) if np.any(acc < 0) else 0
    return abs(fwd - rev)

rows = []
for domain, sig in signals.items():
    for variant, tf in TRANSFORMS.items():
        x = tf(sig)
        seq = ordinal_sequence(x)
        n = len(np.unique(seq))
        P = transition_matrix(seq, n)
        m1 = cycle_flux(P)
        m2 = time_irreversibility(x)
        m3 = compressibility_asymmetry(x)
        m4 = phase_anisotropy(x)
        rows.append({"domain": domain, "variant": variant,
                     "m1": m1, "m2": m2, "m3": m3, "m4": m4})

df = pd.DataFrame(rows)
X = df[["m1","m2","m3","m4"]].values
Xn = RobustScaler().fit_transform(X)
df[["m1","m2","m3","m4"]] = Xn

metric_std = {c: float(np.std(df[c].values)) for c in ["m1","m2","m3","m4"]}
global_corr = np.corrcoef(Xn.T)

results = []
for domain in signals.keys():
    sub = df[df.domain == domain]
    base = sub[sub.variant=="base"][["m1","m2","m3","m4"]].values[0]
    dists = {}
    for v in ["replay","stitch","reverse","swap"]:
        vec = sub[sub.variant==v][["m1","m2","m3","m4"]].values[0]
        dists[v] = float(np.linalg.norm(base - vec))
    corr = np.corrcoef(sub[["m1","m2","m3","m4"]].values.T)
    finite = corr[np.isfinite(corr)]
    corr_score = float(np.max(np.abs(finite - np.eye(4)[np.isfinite(corr)])))
    gate = (
        dists["replay"] > 0.20 and dists["stitch"] > 0.25 and
        dists["reverse"] > 0.40 and dists["swap"] > 0.20 and
        corr_score < 0.90
    )
    results.append({
        "domain": domain, "replay": dists["replay"],
        "stitch": dists["stitch"], "reverse": dists["reverse"],
        "swap": dists["swap"], "corr": corr_score, "gate": bool(gate)
    })

print(f"\nV2_073 — Time Irreversibility + Swap Halves\nGATE: {sum(1 for r in results if r['gate'])}/5\n")
print(f"{'Domain':20s} Replay  Stitch  Reverse Swap    Corr    Gate")
for r in results:
    print(f"{r['domain']:20s} {r['replay']:.3f}  {r['stitch']:.3f}  {r['reverse']:.3f}  {r['swap']:.3f}  {r['corr']:.3f}  {'✓' if r['gate'] else '✗'}")
print(f"\nMetric std: {metric_std}")
print(f"\nGlobal corr:\n{np.round(global_corr, 3)}")

# print raw features for diagnosis
print("\n\n=== RAW (pre-normalization) feature table ===")
df_raw = pd.DataFrame(rows)
pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 200)
print(df_raw.to_string())

summary = {
    "results": results,
    "metric_std": metric_std,
    "global_corr": global_corr.tolist(),
    "raw": df_raw.to_dict(orient="records")
}
with open("v2_073_results.json", "w") as f:
    json.dump(summary, f, indent=2)
print("\nSaved: v2_073_results.json")
