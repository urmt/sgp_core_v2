import numpy as np
import pandas as pd
import json
import zlib
from scipy.signal import hilbert
from sklearn.preprocessing import RobustScaler

np.random.seed(77)

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
TRANSFORM_NAMES = ["replay", "stitch", "reverse", "swap"]

# --- M1: Signed Ordinal Flow (anchor) ---
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

# --- M2: NN Cross-Prediction Asymmetry (fixed) ---
def nn_prediction_asymmetry(x, m=5, tau=2):
    n_emb = N - (m - 1) * tau
    emb = np.column_stack([x[j*tau : n_emb + j*tau] for j in range(m)])
    fwd_preds, bwd_preds = [], []
    fwd_true, bwd_true = [], []
    fwd_offset = (m-1)*tau + 1
    for t in range(n_emb):
        q = emb[t]
        dists = np.sum((emb - q)**2, axis=1)
        dists[t] = np.inf
        nn = np.argmin(dists)
        if t + fwd_offset < N and nn + fwd_offset < N:
            fwd_preds.append(x[nn + fwd_offset])
            fwd_true.append(x[t + fwd_offset])
        if t - 1 >= 0 and nn - 1 >= 0:
            bwd_preds.append(x[nn - 1])
            bwd_true.append(x[t - 1])
    if len(fwd_preds) == 0 or len(bwd_preds) == 0:
        return 0.0
    mse_fwd = np.mean((np.array(fwd_true) - np.array(fwd_preds))**2)
    mse_bwd = np.mean((np.array(bwd_true) - np.array(bwd_preds))**2)
    return mse_fwd - mse_bwd

# --- M3: Boundary Discontinuity Energy ---
def boundary_discontinuity(x, window=32):
    dx = np.diff(x)
    e = np.convolve(dx**2, np.ones(window)/window, mode='valid')
    return float(np.max(e) / (np.median(e) + 1e-12))

# --- M4: Temporal Direction Gradient ---
def temporal_direction_gradient(x, n_windows=16):
    splits = np.array_split(x, n_windows)
    vars = np.array([np.var(s) for s in splits])
    slope = np.polyfit(np.arange(n_windows), vars, 1)[0]
    return slope

# --- Feature extraction ---
rows = []
for domain, sig in signals.items():
    for variant, tf in TRANSFORMS.items():
        x = tf(sig)
        m1 = signed_ordinal_flow(x)
        m2 = nn_prediction_asymmetry(x)
        m3 = boundary_discontinuity(x)
        m4 = temporal_direction_gradient(x)
        rows.append({"domain": domain, "variant": variant,
                     "m1": m1, "m2": m2, "m3": m3, "m4": m4})

df = pd.DataFrame(rows)
X = df[["m1","m2","m3","m4"]].values
Xn = RobustScaler().fit_transform(X)
df[["m1","m2","m3","m4"]] = Xn

metric_std = {c: float(np.std(df[c].values)) for c in ["m1","m2","m3","m4"]}
global_corr = np.corrcoef(Xn.T)

# --- Gate evaluation ---
results = []
for domain in signals.keys():
    sub = df[df.domain == domain]
    base = sub[sub.variant=="base"][["m1","m2","m3","m4"]].values[0]
    dists = {}
    for v in TRANSFORM_NAMES:
        vec = sub[sub.variant==v][["m1","m2","m3","m4"]].values[0]
        dists[v] = float(np.linalg.norm(base - vec))
    corr = np.corrcoef(sub[["m1","m2","m3","m4"]].values.T)
    finite = corr[np.isfinite(corr)]
    corr_score = float(np.max(np.abs(finite - np.eye(4)[np.isfinite(corr)])))
    gate = (dists["replay"] > 0.20 and dists["stitch"] > 0.25 and
            dists["reverse"] > 0.40 and dists["swap"] > 0.20 and corr_score < 0.90)
    results.append({"domain": domain, **{v: dists[v] for v in TRANSFORM_NAMES},
                    "corr": corr_score, "gate": bool(gate)})

print(f"\nV2_077 — Temporal Continuity Suite\nGATE: {sum(1 for r in results if r['gate'])}/5\n")
print(f"{'Domain':20s} Replay  Stitch  Reverse Swap    Corr    Gate")
for r in results:
    print(f"{r['domain']:20s} {r['replay']:.3f}  {r['stitch']:.3f}  {r['reverse']:.3f}  {r['swap']:.3f}  {r['corr']:.3f}  {'✓' if r['gate'] else '✗'}")
print(f"\nMetric std: {metric_std}")
print(f"\nGlobal corr:\n{np.round(global_corr, 3)}")

# --- Transform × Metric sensitivity matrix ---
print("\n\n=== TRANSFORM × METRIC SENSITIVITY ===")
print("Each cell = |variant - base| / (|base| + 1e-12) for raw metric")
print(f"{'Domain':20s} {'Metric':6s} {'replay':8s} {'stitch':8s} {'reverse':8s} {'swap':8s}")
df_raw = pd.DataFrame(rows)
for domain in signals.keys():
    sub = df_raw[df_raw.domain == domain]
    base_r = sub[sub.variant=="base"].iloc[0]
    for met in ["m1","m2","m3","m4"]:
        bval = abs(base_r[met]) + 1e-12
        vals = []
        for v in TRANSFORM_NAMES:
            vec = sub[sub.variant==v].iloc[0]
            vals.append(abs(vec[met] - base_r[met]) / bval)
        print(f"{domain:20s} {met:6s} {vals[0]:8.3f} {vals[1]:8.3f} {vals[2]:8.3f} {vals[3]:8.3f}")
    print()

# --- Raw table ---
print("\n=== RAW features ===")
pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 200)
print(df_raw.to_string())

summary = {"results": results, "metric_std": metric_std, "global_corr": global_corr.tolist(),
           "raw": df_raw.to_dict(orient="records")}
with open("v2_077_results.json", "w") as f:
    json.dump(summary, f, indent=2)
print("\nSaved: v2_077_results.json")
