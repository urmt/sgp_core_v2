import numpy as np, pandas as pd, json, zlib
from sklearn.preprocessing import RobustScaler
from scipy.signal import hilbert, lfilter, correlate

# ---- LPC residual asymmetry ----
def lpc_residual_asymmetry(x, order=10):
    x = np.asarray(x, dtype=np.float64)
    n = len(x)
    # forward LPC via autocorrelation method
    ac = correlate(x, x, mode='full')
    ac = ac[n-1:]  # positive lags only
    r = ac[:order+1]
    R = np.zeros((order, order))
    for i in range(order):
        for j in range(order):
            R[i,j] = r[abs(i-j)]
    try:
        a = np.linalg.solve(R, -r[1:order+1])
    except np.linalg.LinAlgError:
        return 0.0
    # forward residual
    resid_fwd = x[order:] + np.convolve(x[order-1::-1], a, mode='valid')
    e_fwd = np.mean(resid_fwd**2)
    # backward LPC
    x_rev = x[::-1]
    ac = correlate(x_rev, x_rev, mode='full')
    ac = ac[n-1:]
    r = ac[:order+1]
    R = np.zeros((order, order))
    for i in range(order):
        for j in range(order):
            R[i,j] = r[abs(i-j)]
    try:
        a = np.linalg.solve(R, -r[1:order+1])
    except np.linalg.LinAlgError:
        return 0.0
    resid_bwd = x_rev[order:] + np.convolve(x_rev[order-1::-1], a, mode='valid')
    e_bwd = np.mean(resid_bwd**2)
    return (e_fwd - e_bwd) / (e_fwd + e_bwd + 1e-12)

# ---- M2: half-half correlation with anti-alias ----
def half_corr_aa(x):
    h = len(x)//2
    # simple anti-alias: gaussian filter
    from scipy.ndimage import gaussian_filter1d
    xs = gaussian_filter1d(x, sigma=2.0)
    return float(np.corrcoef(xs[:h], xs[h:])[0,1])

# ---- M4: amp transition with jitter ----
def amp_transition_jitter(x, k=5, jitter=0.05, seed=0):
    np.random.seed(seed)
    raw_bins = np.percentile(x, np.linspace(0, 100, k+1)[1:-1])
    j = np.random.uniform(-jitter, jitter, size=len(raw_bins)) * (np.max(x) - np.min(x))
    bins = raw_bins + j
    states = np.digitize(x, bins); n = k+1
    C = np.zeros((n,n))
    for i in range(len(states)-1): C[states[i], states[i+1]] += 1
    C += 1e-9
    F = C / C.sum(axis=1, keepdims=True)
    B = C.T / C.T.sum(axis=1, keepdims=True)
    asym = 0.0
    for i in range(n):
        for j in range(n): asym += (F[i,j] - B[i,j]) * (j - i)
    return asym

METRICS = {"m2": half_corr_aa, "m3": lpc_residual_asymmetry, "m4": lambda x, s=0: amp_transition_jitter(x, seed=s)}
TV = ["replay","stitch","reverse","swap"]

def make_signals(seed, N=4096):
    np.random.seed(seed)
    t = np.linspace(0,1,N)
    sigs = {}
    sigs["chirp"] = np.sin(2*np.pi*(8*t + 40*t**2))
    rw = np.cumsum(np.random.randn(N))
    sigs["rw_trend"] = rw + 0.002*np.arange(N)
    x = np.zeros(N)
    ts = np.array_split(np.arange(N), 3)
    i0,i1,i2 = len(ts[0]), len(ts[1]), len(ts[2])
    x[:i0] = np.random.randn(i0)
    x[i0:i0+i1] = 3 + 0.3*np.random.randn(i1)
    x[i0+i1:] = np.sin(np.linspace(0, 30*np.pi, i2))
    sigs["regime_switch"] = x
    r = 3.99; x = np.zeros(N); x[0] = 0.2
    for i in range(N-1): x[i+1] = r*x[i]*(1-x[i])
    sigs["chaotic_logistic"] = x
    sigs["coupled_osc"] = np.sin(2*np.pi*7*t) + 0.5*np.sin(2*np.pi*13*t + 0.2*np.sin(2*np.pi*3*t))
    return sigs

def replay(x): return np.concatenate([x[:len(x)//2], x[:len(x)//2]])
def stitch(x):
    ts = np.array_split(x, 3)
    return np.concatenate([ts[2], ts[0], ts[1]])
def reverse(x): return x[::-1]
def swap_halves(x): return np.concatenate([x[len(x)//2:], x[:len(x)//2]])
TR = {"base": lambda x: x, "replay": replay, "stitch": stitch, "reverse": reverse, "swap": swap_halves}

def compute_gate(active_keys, sigs, noise_sigma=0, scale=1.0, dc=0, seed=0):
    rows = []
    for domain, sig in sigs.items():
        x = sig * scale + dc
        if noise_sigma > 0:
            np.random.seed(seed + hash(domain) % 10000)
            x += np.random.randn(len(x)) * noise_sigma
        for variant, tf in TR.items():
            y = tf(x.copy())
            r = {"domain": domain, "variant": variant}
            for mk in active_keys:
                if mk == "m4":
                    r[mk] = amp_transition_jitter(y, seed=seed+hash(domain+variant)%10000)
                else:
                    r[mk] = METRICS[mk](y)
            rows.append(r)
    df = pd.DataFrame(rows)
    Xn = RobustScaler().fit_transform(df[active_keys].values)
    df[active_keys] = Xn
    nd = len(active_keys)
    passes = 0
    for domain in sigs.keys():
        sub = df[df.domain == domain]
        base = sub[sub.variant=="base"][active_keys].values[0]
        dists = {}
        for v in TV:
            vec = sub[sub.variant==v][active_keys].values[0]
            dists[v] = float(np.linalg.norm(base - vec))
        c = np.corrcoef(sub[active_keys].values.T)
        eye = np.eye(nd)
        mask = np.isfinite(c)
        diff = np.abs(c[mask] - eye[mask])
        cs = float(np.max(diff)) if len(diff) > 0 else 1.0
        gate = (dists["replay"] > 0.20 and dists["stitch"] > 0.25 and
                dists["reverse"] > 0.40 and dists["swap"] > 0.20 and cs < 0.90)
        if gate: passes += 1
    return passes

all_keys = ["m2","m3","m4"]
seeds = [11, 23, 37, 51, 79, 101, 149, 211, 307, 401]

# Phase A: Multi-seed
print("=== PHASE A: MULTI-SEED ===")
total = 0; full = 0; worst = 10
for s in seeds:
    sigs = make_signals(s)
    p = compute_gate(all_keys, sigs, seed=s)
    total += p
    if p==5: full+=1
    worst = min(worst, p)
    print(f"  {s}: {p}/5")
print(f"  mean={total/len(seeds):.2f} full_pass={full}/10 worst={worst}")

# Phase B: Noise
print("\n=== PHASE B: NOISE ===")
for sigma in [0.01, 0.05, 0.10]:
    t = 0
    for s in seeds:
        sigs = make_signals(s)
        p = compute_gate(all_keys, sigs, noise_sigma=sigma, seed=s)
        t += p
    print(f"  sigma={sigma:.2f}: avg={t/len(seeds):.2f}")

# Phase C: Robustness
print("\n=== PHASE C: ROBUSTNESS ===")
for label, kw in [("scale_0.1", {"scale":0.1}), ("scale_10", {"scale":10.0}),
                  ("dc_5", {"dc":5.0}), ("quantize",{})]:
    t = 0
    for s in seeds:
        sigs = make_signals(s)
        if label=="quantize":
            for k in sigs: sigs[k] = np.round(sigs[k]*10000).astype(np.int16).astype(np.float64)/10000.0
        p = compute_gate(all_keys, sigs, **kw, seed=s)
        t += p
    print(f"  {label}: avg={t/len(seeds):.2f}")
for N in [2048,8192]:
    t = 0
    for s in seeds:
        sigs = make_signals(s, N=N)
        p = compute_gate(all_keys, sigs, seed=s)
        t += p
    print(f"  N={N}: avg={t/len(seeds):.2f}")

# Phase D: Correlation analysis (seed 79 detail)
print("\n=== PHASE D: CORRELATION (seed 79) ===")
sig = make_signals(79)
rows = []
for domain, s in sig.items():
    for variant, tf in TR.items():
        y = tf(s.copy())
        rows.append({"domain":domain,"variant":variant,
                     "m2":half_corr_aa(y),"m3":lpc_residual_asymmetry(y),
                     "m4":amp_transition_jitter(y,seed=0)})
df = pd.DataFrame(rows)
Xn = RobustScaler().fit_transform(df[all_keys].values)
df[all_keys] = Xn
for domain in sig.keys():
    sub = df[df.domain==domain]
    c = np.corrcoef(sub[all_keys].values.T)
    print(f"  {domain}: corr matrix")
    for i, mk in enumerate(all_keys):
        row_vals = " ".join(f"{c[i,j]:.3f}" for j in range(len(all_keys)))
        print(f"    {mk}: {row_vals}")
    # condition number of correlation matrix
    eig = np.linalg.eigvalsh(c)
    cond = eig[-1]/eig[0] if eig[0] > 1e-12 else np.inf
    print(f"    condition_number={cond:.2f}")
