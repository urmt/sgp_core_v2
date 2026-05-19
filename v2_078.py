import numpy as np
import pandas as pd
import json
import zlib
from scipy.signal import hilbert
from sklearn.preprocessing import RobustScaler

np.random.seed(78)

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

TRANSFORMS = {"base": lambda x: x, "replay": replay, "stitch": stitch,
              "reverse": reverse, "swap": swap_halves}
TV = ["replay", "stitch", "reverse", "swap"]

# M1: signed ordinal flow
def ordinal_sequence(x, d=3):
    seq = [np.argsort(x[i:i+d]) for i in range(len(x)-d)]
    uniq = {tuple(p):i for i,p in enumerate(sorted(set(tuple(s) for s in seq)))}
    return np.array([uniq[tuple(s)] for s in seq])

def signed_ordinal_flow(x):
    seq = ordinal_sequence(x)
    n = len(np.unique(seq))
    P = np.zeros((n,n))
    for a,b in zip(seq[:-1], seq[1:]):
        P[a,b] += 1
    P += 1e-9
    P /= P.sum(axis=1, keepdims=True)
    F = P - P.T
    w = 0.0
    for i in range(n):
        for j in range(n):
            w += F[i,j] * (j - i)
    return w

# M2: half-half correlation (repetition detection)
def half_corr(x):
    half = len(x)//2
    a, b = x[:half], x[half:]
    return float(np.corrcoef(a, b)[0,1])

# M3: signed compressibility
def signed_compress(x):
    xf = zlib.compress(np.asarray(x, dtype=np.float32).tobytes())
    xr = zlib.compress(np.asarray(x[::-1], dtype=np.float32).tobytes())
    return len(xf) - len(xr)

# M4: signed phase anisotropy
def signed_phase(x):
    z = hilbert(x)
    phase = np.unwrap(np.angle(z))
    vel = np.diff(phase)
    acc = np.diff(vel)
    fwd = np.mean(np.abs(acc[acc > 0])) if np.any(acc > 0) else 0
    rev = np.mean(np.abs(acc[acc < 0])) if np.any(acc < 0) else 0
    return fwd - rev

rows = []
for domain, sig in signals.items():
    for variant, tf in TRANSFORMS.items():
        x = tf(sig)
        rows.append({"domain": domain, "variant": variant,
                     "m1": signed_ordinal_flow(x), "m2": half_corr(x),
                     "m3": signed_compress(x), "m4": signed_phase(x)})

df = pd.DataFrame(rows)
Xn = RobustScaler().fit_transform(df[["m1","m2","m3","m4"]].values)
df[["m1","m2","m3","m4"]] = Xn

metric_std = {c: float(np.std(df[c].values)) for c in ["m1","m2","m3","m4"]}
global_corr = np.corrcoef(Xn.T)

results = []
for domain in signals.keys():
    sub = df[df.domain == domain]
    base = sub[sub.variant=="base"][["m1","m2","m3","m4"]].values[0]
    dists = {}
    for v in TV:
        vec = sub[sub.variant==v][["m1","m2","m3","m4"]].values[0]
        dists[v] = float(np.linalg.norm(base - vec))
    corr = np.corrcoef(sub[["m1","m2","m3","m4"]].values.T)
    finite = corr[np.isfinite(corr)]
    corr_score = float(np.max(np.abs(finite - np.eye(4)[np.isfinite(corr)])))
    gate = (dists["replay"] > 0.20 and dists["stitch"] > 0.25 and
            dists["reverse"] > 0.40 and dists["swap"] > 0.20 and corr_score < 0.90)
    results.append({"domain": domain, **{v: dists[v] for v in TV},
                    "corr": corr_score, "gate": bool(gate)})

print(f"\nV2_078 — Half-Corr + Restored Compress\nGATE: {sum(1 for r in results if r['gate'])}/5\n")
print(f"{'Domain':20s} Replay  Stitch  Reverse Swap    Corr    Gate")
for r in results:
    print(f"{r['domain']:20s} {r['replay']:.3f}  {r['stitch']:.3f}  {r['reverse']:.3f}  {r['swap']:.3f}  {r['corr']:.3f}  {'✓' if r['gate'] else '✗'}")
print(f"\nMetric std: {metric_std}")
print(f"\nGlobal corr:\n{np.round(global_corr, 3)}")

print("\n\n=== TRANSFORM × METRIC SENSITIVITY ===")
print(f"{'Domain':20s} {'Met':4s} {'replay':8s} {'stitch':8s} {'reverse':8s} {'swap':8s}")
df_raw = pd.DataFrame(rows)
for domain in signals.keys():
    sub = df_raw[df_raw.domain == domain]
    base_r = sub[sub.variant=="base"].iloc[0]
    for met in ["m1","m2","m3","m4"]:
        bval = abs(base_r[met]) + 1e-12
        vals = []
        for v in TV:
            vec = sub[sub.variant==v].iloc[0]
            vals.append(abs(vec[met] - base_r[met]) / bval)
        print(f"{domain:20s} {met:4s} {vals[0]:8.3f} {vals[1]:8.3f} {vals[2]:8.3f} {vals[3]:8.3f}")
    print()

print("\n=== RAW features ===")
pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 200)
print(df_raw.to_string())

summary = {"results": results, "metric_std": metric_std, "global_corr": global_corr.tolist(),
           "raw": df_raw.to_dict(orient="records")}
with open("v2_078_results.json", "w") as f:
    json.dump(summary, f, indent=2)
print("\nSaved: v2_078_results.json")
