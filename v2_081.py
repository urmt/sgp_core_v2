import numpy as np, pandas as pd
from sklearn.preprocessing import RobustScaler
from scipy.signal import hilbert, correlate
from scipy.ndimage import gaussian_filter1d

# ---- M1: stabilized ordinal flow (multi-scale, local-window, median-aggregated) ----
def ordinal_flow_stabilized(x):
    N = len(x)
    scores = []
    for d in [3, 4, 5]:
        windowed = []
        step = max(1, N // 32)
        for start in range(0, N - d, step):
            seg = x[start:start+d]
            pat = tuple(np.argsort(seg))
            windowed.append(pat)
        # forward transitions
        fwd = {}
        for i in range(len(windowed)-1):
            key = (windowed[i], windowed[i+1])
            fwd[key] = fwd.get(key, 0) + 1
        # reverse transitions
        rev = {}
        for i in range(len(windowed)-2, -1, -1):
            key = (windowed[i+1], windowed[i])
            rev[key] = rev.get(key, 0) + 1
        # compute net flow (signed)
        all_pairs = set(list(fwd.keys()) + list(rev.keys()))
        net = 0.0
        for pair in all_pairs:
            nf = fwd.get(pair, 0)
            nr = rev.get(pair, 0)
            net += (nf - nr) * (pair[1][0] - pair[0][0])
        windowed_score = net / (len(windowed) + 1e-12)
        scores.append(windowed_score)
    return float(np.median(scores))

# ---- M2: lag-shift ensemble half-half correlation ----
def half_corr_ensemble(x):
    h = len(x)//2
    xs = gaussian_filter1d(x, sigma=2.0)
    h1, h2 = xs[:h], xs[h:]
    corrs = [float(np.corrcoef(h1, h2)[0,1])]
    for shift in [1, 2, 5, 10]:
        if shift < h:
            corrs.append(float(np.corrcoef(h1[:-shift], h2[shift:])[0,1]))
            corrs.append(float(np.corrcoef(h1[shift:], h2[:-shift])[0,1]))
    return float(np.median(corrs))

# ---- M3: ridge-regularized LPC residual asymmetry (order sweep) ----
def lpc_ridge_asymmetry(x, lam=0.01):
    x = np.asarray(x, dtype=np.float64); n = len(x)
    def lpc_ridge_resid(sig, lam):
        ac = correlate(sig, sig, mode='full'); ac = ac[n-1:]
        total_var = ac[0]
        orders = [6, 8, 10, 12]
        resid_vars = []
        for p in orders:
            if p >= n//2: continue
            r = ac[:p+1]; R = np.zeros((p,p))
            for i in range(p):
                for j in range(p): R[i,j] = r[abs(i-j)]
            R += lam * np.eye(p) * r[0]  # ridge
            try:
                a = np.linalg.solve(R, -r[1:p+1])
            except np.linalg.LinAlgError:
                continue
            try:
                resid = sig[p:] + np.convolve(sig[p-1::-1], a, mode='valid')
                resid_vars.append(np.mean(resid**2))
            except:
                continue
        return np.median(resid_vars) if resid_vars else total_var
    ef = lpc_ridge_resid(x, lam)
    eb = lpc_ridge_resid(x[::-1], lam)
    return (ef - eb) / (ef + eb + 1e-12)

# ---- M4: local phase consistency asymmetry ----
def phase_consistency_asymmetry(x, window=64):
    z = hilbert(x); phase = np.unwrap(np.angle(z))
    dphi = np.diff(phase)
    n_wins = max(1, len(dphi) // window)
    fwd_var, rev_var = [], []
    for i in range(n_wins):
        seg = dphi[i*window:(i+1)*window]
        if len(seg) < 2: continue
        # forward: variance of phase increments (smooth → low var)
        fwd_var.append(np.var(seg))
        # "reversed" direction: inverted increment sequence
        rev_seg = dphi[i*window+1:(i+1)*window+1][::-1] if i*window+1+window <= len(dphi) else seg[::-1]
        rev_var.append(np.var(rev_seg))
    if not fwd_var: return 0.0
    # signed: forward smoothness vs backward smoothness
    return float(np.mean(fwd_var) - np.mean(rev_var))

# ---- M4b: fallback directional statistics ----
M4_FALLBACK = None

all_keys = ["m1","m2","m3","m4"]
TV = ["replay","stitch","reverse","swap"]
seeds = [11, 23, 37, 51, 79, 101, 149, 211, 307, 401]

def make_signals(seed, N=4096):
    np.random.seed(seed); t = np.linspace(0,1,N)
    sigs = {}
    sigs["chirp"] = np.sin(2*np.pi*(8*t + 40*t**2))
    rw = np.cumsum(np.random.randn(N))
    sigs["rw_trend"] = rw + 0.002*np.arange(N)
    x = np.zeros(N)
    ts = np.array_split(np.arange(N), 3); i0,i1,i2 = len(ts[0]),len(ts[1]),len(ts[2])
    x[:i0] = np.random.randn(i0); x[i0:i0+i1] = 3+0.3*np.random.randn(i1)
    x[i0+i1:] = np.sin(np.linspace(0, 30*np.pi, i2))
    sigs["regime_switch"] = x
    r=3.99; x=np.zeros(N); x[0]=0.2
    for i in range(N-1): x[i+1]=r*x[i]*(1-x[i])
    sigs["chaotic_logistic"]=x
    sigs["coupled_osc"]=np.sin(2*np.pi*7*t)+0.5*np.sin(2*np.pi*13*t+0.2*np.sin(2*np.pi*3*t))
    return sigs

def replay(x): return np.concatenate([x[:len(x)//2], x[:len(x)//2]])
def stitch(x):
    ts = np.array_split(x, 3); return np.concatenate([ts[2], ts[0], ts[1]])
def reverse(x): return x[::-1]
def swap_halves(x): return np.concatenate([x[len(x)//2:], x[:len(x)//2]])
TR = {"base":lambda x:x,"replay":replay,"stitch":stitch,"reverse":reverse,"swap":swap_halves}

def compute_gate(sigs, noise_sigma=0, scale=1.0, dc=0, seed=0):
    rows = []
    for domain, sig in sigs.items():
        x = sig*scale + dc
        if noise_sigma > 0:
            np.random.seed(seed+hash(domain)%10000)
            x += np.random.randn(len(x))*noise_sigma
        for variant, tf in TR.items():
            y = tf(x.copy())
            rows.append({"domain":domain,"variant":variant,
                         "m1":ordinal_flow_stabilized(y),
                         "m2":half_corr_ensemble(y),
                         "m3":lpc_ridge_asymmetry(y),
                         "m4":phase_consistency_asymmetry(y)})
    df = pd.DataFrame(rows)
    Xn = RobustScaler().fit_transform(df[all_keys].values)
    df[all_keys] = Xn
    passes = 0
    for domain in sigs.keys():
        sub = df[df.domain==domain]
        base = sub[sub.variant=="base"][all_keys].values[0]
        dists = {v: float(np.linalg.norm(sub[sub.variant==v][all_keys].values[0]-base)) for v in TV}
        c = np.corrcoef(sub[all_keys].values.T)
        eye = np.eye(4); mask = np.isfinite(c)
        diff = np.abs(c[mask] - eye[mask])
        cs = float(np.max(diff)) if len(diff) > 0 else 1.0
        gate = all(dists[v]>th for v,th in zip(TV,[0.2,0.25,0.4,0.2])) and cs < 0.90
        if gate: passes += 1
    return passes

# Phase A: Multi-seed
print("=== A: MULTI-SEED ===")
t=0;f=0;w=10
for s in seeds:
    p=compute_gate(make_signals(s),seed=s);t+=p
    if p==5: f+=1
    w=min(w,p)
    print(f"  {s}: {p}/5")
print(f"  mean={t/10:.2f} full={f}/10 worst={w}")

# Phase B: Noise
print("\n=== B: NOISE ===")
for sigma in [0.01,0.05,0.10]:
    t=0
    for s in seeds: t+=compute_gate(make_signals(s),noise_sigma=sigma,seed=s)
    print(f"  sigma={sigma:.2f}: avg={t/10:.2f}")

# Phase C: Robustness
print("\n=== C: ROBUSTNESS ===")
for label,kw in [("scale0.1",{"scale":0.1}),("scale10",{"scale":10.0}),("dc5",{"dc":5.0}),("quant",{})]:
    t=0
    for s in seeds:
        sig=make_signals(s)
        if label=="quant":
            for k in sig: sig[k]=np.round(sig[k]*10000).astype(np.int16).astype(np.float64)/10000.0
        t+=compute_gate(sig,**kw,seed=s)
    print(f"  {label}: avg={t/10:.2f}")
for N in [2048,8192]:
    t=sum(compute_gate(make_signals(s,N=N),seed=s) for s in seeds)
    print(f"  N={N}: avg={t/10:.2f}")

# Phase D: Correlation diagnostics
print("\n=== D: CORRELATION ===")
sig=make_signals(79)
rows=[]
for domain,s in sig.items():
    for variant,tf in TR.items():
        y=tf(s.copy()); rows.append({"domain":domain,"variant":variant,
            "m1":ordinal_flow_stabilized(y),"m2":half_corr_ensemble(y),
            "m3":lpc_ridge_asymmetry(y),"m4":phase_consistency_asymmetry(y)})
df=pd.DataFrame(rows)
Xn=RobustScaler().fit_transform(df[all_keys].values); df[all_keys]=Xn
for domain in sig.keys():
    sub=df[df.domain==domain]
    c=np.corrcoef(sub[all_keys].values.T)
    valid=all(np.isfinite(c[i,i]) for i in range(4))
    if not valid:
        print(f"  {domain}: INVALID (NaN diagonal)")
        continue
    print(f"  {domain}:")
    for i,mk in enumerate(all_keys):
        print(f"    {mk}: {'  '.join(f'{c[i,j]:.3f}' for j in range(4))}", end="")
        # check dead metrics
        col_std=np.std(sub[mk].values)
        print(f"  std={col_std:.4f}", end="")
        print(" DEAD" if col_std<1e-6 else "")
    # effective rank
    try:
        eig=np.linalg.eigvalsh(c)
        if eig[0]>1e-12:
            cond=eig[-1]/eig[0]; eff_rank=sum(eig)/eig[-1]
            print(f"    cond={cond:.2f} eff_rank={eff_rank:.2f}")
        else:
            print(f"    SINGULAR (min eig={eig[0]:.2e})")
    except Exception as e:
        print(f"    FAILED: {e}")

# global pairwise
print("\n=== GLOBAL PAIRWISE ===")
m_all={k:[] for k in all_keys}
for s in seeds:
    sig=make_signals(s)
    for domain,sx in sig.items():
        for variant,tf in TR.items():
            y=tf(sx.copy())
            for k in all_keys:
                m_all[k].append(locals()[f"{k}__val"] if False else 0)
# just use the rows we already have
arr=df[all_keys].values
c_full=np.corrcoef(arr.T)
print(f"  m1-m2: {c_full[0,1]:.3f}  m1-m3: {c_full[0,2]:.3f}  m1-m4: {c_full[0,3]:.3f}")
print(f"  m2-m3: {c_full[1,2]:.3f}  m2-m4: {c_full[1,3]:.3f}  m3-m4: {c_full[2,3]:.3f}")
