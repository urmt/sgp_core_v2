"""RD-8: State-Space Cartography — Friction sweep with full state-variable computation.
Friction is the master control parameter. Sweep μ ∈ [0.02, 1.5] to map
frozen↔transitional↔fluid↔jammed regimes.
"""

import sys, os, json, time
import numpy as np

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, "coherence-benchmark")

from t901_analysis import _soft_sphere_force
from metrics.total_correlation import compute_C

def _run_friction(n_grains=50, n_steps=1000, friction=0.3, seed=42):
    rng = np.random.default_rng(seed)
    radii = rng.uniform(0.8, 1.5, n_grains)
    masses = radii ** 2
    box_width = 40.0

    x = rng.uniform(2, box_width - 2, n_grains)
    y = rng.uniform(5, 30, n_grains)
    vx = rng.uniform(-0.5, 0.5, n_grains)
    vy = rng.uniform(-0.5, 0.5, n_grains)

    gy = -1.0; dt = 0.01; stiffness = 500.0; damping = 2.0

    all_x = np.zeros((n_grains, n_steps))
    all_y = np.zeros((n_grains, n_steps))
    all_vx = np.zeros((n_grains, n_steps))
    all_vy = np.zeros((n_grains, n_steps))

    for step in range(n_steps):
        fx = np.zeros(n_grains)
        fy = np.full(n_grains, gy * masses)
        for i in range(n_grains):
            for j in range(i + 1, n_grains):
                dx = x[j] - x[i]; dy = y[j] - y[i]
                if abs(dx) > 3.0 or abs(dy) > 3.0: continue
                ffx, ffy, _ = _soft_sphere_force(dx, dy, radii[i], radii[j],
                                                  stiffness, damping)
                fx[i] += ffx; fy[i] += ffy
                fx[j] -= ffx; fy[j] -= ffy
            vx[i] += fx[i] / masses[i] * dt
            vy[i] += fy[i] / masses[i] * dt
            vx[i] *= (1.0 - friction * dt)
            vy[i] *= (1.0 - friction * dt)
            x[i] += vx[i] * dt
            y[i] += vy[i] * dt
            if x[i] - radii[i] < 0: x[i] = radii[i]; vx[i] *= -0.5
            elif x[i] + radii[i] > box_width: x[i] = box_width - radii[i]; vx[i] *= -0.5
            if y[i] - radii[i] < 0: y[i] = radii[i]; vy[i] *= -0.5
        all_x[:, step] = x; all_y[:, step] = y
        all_vx[:, step] = vx; all_vy[:, step] = vy

    return all_y, all_x, all_vx, all_vy


def _bin_data(py, px, n_bins=10):
    final_x = np.nanmean(px[:, -100:], axis=1)
    order = np.argsort(final_x)
    bins = np.array_split(order, n_bins)
    return np.array([np.mean(py[b], axis=0) for b in bins])


def _sliding_C(X, window=75, step=25):
    T = X.shape[1]; times, vals = [], []
    for t in range(0, T - window + 1, step):
        times.append(t + window // 2)
        try: vals.append(compute_C(X[:, t:t + window], "gaussian"))
        except: vals.append(np.nan)
    return np.array(times), np.array(vals)


def persistence(c_vals, dt=25):
    c = c_vals[~np.isnan(c_vals)]
    if len(c) < 20: return np.nan
    c = c - np.mean(c)
    f = np.fft.fft(c, n=2*len(c))
    acf = np.fft.ifft(f * np.conjugate(f))[:len(c)].real
    if acf[0] > 0: acf /= acf[0]
    for i in range(1, len(acf)):
        if acf[i] < 1.0/np.e: return float(i * dt)
    return float(len(acf) * dt)


def reorganization_rate(all_y, window=50, step=25):
    """Rate of position reorganization across windows."""
    T = all_y.shape[1]; rates = []
    for t in range(0, T - 2*window, step):
        y1 = np.nanmean(all_y[:, t:t+window], axis=1)
        y2 = np.nanmean(all_y[:, t+window:t+2*window], axis=1)
        rates.append(np.nanmean(np.abs(y2 - y1)))
    return float(np.mean(rates)) if rates else np.nan


def velocity_autocorrelation(all_vx, lag=50):
    """Mean velocity autocorrelation at lag steps."""
    T = all_vx.shape[1]
    acorrs = []
    for i in range(all_vx.shape[0]):
        v = all_vx[i, :T-lag]
        v_lag = all_vx[i, lag:]
        valid = ~(np.isnan(v) | np.isnan(v_lag))
        if np.sum(valid) > 10:
            c = np.corrcoef(v[valid], v_lag[valid])[0,1]
            if not np.isnan(c):
                acorrs.append(c)
    return float(np.mean(acorrs)) if acorrs else np.nan


def mean_separation(all_y):
    """Mean pairwise grain separation in y. Higher = more spread."""
    y_final = np.nanmean(all_y[:, -100:], axis=1)
    valid = y_final[~np.isnan(y_final)]
    if len(valid) < 2: return np.nan
    diffs = []
    for i in range(len(valid)):
        for j in range(i+1, min(len(valid), i+20)):  # sample
            diffs.append(abs(valid[i] - valid[j]))
    return float(np.mean(diffs))


# ─── Sweep ───
FRICTION_LEVELS = np.concatenate([
    np.linspace(0.02, 0.10, 5),   # fluid
    np.linspace(0.15, 0.40, 6),   # transitional
    np.linspace(0.50, 1.00, 6),   # frozen
    np.linspace(1.20, 2.00, 5),   # jammed
])
N_REPS = 8
N_GRAINS = 50; N_STEPS = 1000; BASE_SEED = 5000

results = []
t0 = time.time()
total = len(FRICTION_LEVELS) * N_REPS
done = 0

for fr in FRICTION_LEVELS:
    for rep in range(N_REPS):
        seed = BASE_SEED + rep + int(fr * 10000)
        all_y, all_x, all_vx, all_vy = _run_friction(
            n_grains=N_GRAINS, n_steps=N_STEPS, friction=fr, seed=seed)

        X = _bin_data(all_y, all_x, n_bins=10)
        times, c_vals = _sliding_C(X, window=75, step=25)

        pre_mask = (times >= 100) & (times < 500)
        C = float(np.nanmean(c_vals[pre_mask])) if np.sum(pre_mask) >= 2 else np.nan

        # State variables
        jitter = float(np.nanmean(np.sqrt(all_vx**2 + all_vy**2)))
        persist = persistence(c_vals)
        reorg = reorganization_rate(all_y)
        v_auto = velocity_autocorrelation(all_vx, lag=50)
        sep = mean_separation(all_y)

        # Neighbor turnover: fraction of neighbor pairs that change per 100 steps
        # Simplified: use position reorganization rate as proxy

        # Collapse detection: if C < 0.05 or all grains escaped
        escaped = np.sum(np.isnan(all_y[:, -1])) / N_GRAINS
        collapsed = escaped > 0.5 or (not np.isnan(C) and C < 0.05)

        results.append({
            "friction": round(float(fr), 4), "rep": rep,
            "C": round(C, 4) if not np.isnan(C) else None,
            "jitter": round(jitter, 2),
            "persistence": round(persist, 1) if not np.isnan(persist) else None,
            "reorg_rate": round(reorg, 4) if not np.isnan(reorg) else None,
            "v_autocorr": round(v_auto, 4) if not np.isnan(v_auto) else None,
            "separation": round(sep, 2) if not np.isnan(sep) else None,
            "collapsed": collapsed,
            "escaped_frac": round(float(escaped), 3),
        })

        done += 1
        if done % 40 == 0:
            print(f"  [{done}/{total}] {time.time()-t0:.0f}s elapsed")

print(f"\nSweep: {done} runs in {time.time()-t0:.0f}s")

with open("audits/rd08_friction_sweep.json", "w") as f:
    json.dump(results, f, indent=2)

# ─── Summary ───
print("\n" + "=" * 120)
print("RD-8: STATE-SPACE CARTOGRAPHY — FRICTION SWEEP")
print("=" * 120)
print(f"\n{'μ':>6s} {'C':>8s} {'Jitter':>10s} {'Persist':>9s} {'Reorg':>8s} {'V_Auto':>8s} {'Sep':>7s} {'Esc%':>6s} {'Collapse':>9s}")
print("-" * 120)

for fr in FRICTION_LEVELS:
    sub = [r for r in results if abs(r["friction"] - fr) < 0.001]
    def ms(k):
        v = [r[k] for r in sub if r.get(k) is not None]
        return (np.mean(v), np.std(v)) if v else (np.nan, 0)
    c_m, _ = ms("C"); j_m, _ = ms("jitter"); p_m, _ = ms("persistence")
    r_m, _ = ms("reorg_rate"); va_m, _ = ms("v_autocorr"); s_m, _ = ms("separation")
    esc = np.mean([r["escaped_frac"] for r in sub])
    n_coll = sum(1 for r in sub if r["collapsed"])
    print(f"{fr:>6.3f} {c_m:>8.3f} {j_m:>10.2f} {p_m:>9.1f} {r_m:>8.4f} "
          f"{va_m:>8.4f} {s_m:>7.2f} {esc:>6.1%} {n_coll:>3d}/{len(sub)}")

# ─── Regime classification ───
print("\n" + "─" * 120)
print("REGIME CLASSIFICATION (based on μ)")
print("─" * 120)

# Classify each friction level
for fr in FRICTION_LEVELS:
    sub = [r for r in results if abs(r["friction"] - fr) < 0.001 and not r["collapsed"]]
    if len(sub) < 3:
        continue
    c_vals = [r["C"] for r in sub if r.get("C") is not None]
    j_vals = [r["jitter"] for r in sub]
    p_vals = [r["persistence"] for r in sub if r.get("persistence") is not None]
    
    c_mean = np.mean(c_vals) if c_vals else 0
    j_mean = np.mean(j_vals)
    p_mean = np.mean(p_vals) if p_vals else 0
    
    # Regime heuristics (will refine after seeing data)
    if j_mean < 12:
        regime = "FROZEN"
    elif j_mean > 25:
        regime = "CHAOTIC"
    elif c_mean > 0.45 and p_mean > 100:
        regime = "EMERGENT"
    else:
        regime = "TRANSITIONAL"
    
    print(f"  μ={fr:.3f}: C={c_mean:.3f}, J={j_mean:.1f}, P={p_mean:.0f} → {regime}")

# ─── PCA ───
print("\n" + "─" * 120)
print("LATENT DIMENSIONALITY")
print("─" * 120)

valid = [r for r in results if all(r.get(k) is not None for k in
        ["C", "jitter", "persistence", "reorg_rate", "v_autocorr", "separation"])
        and not r["collapsed"]]
print(f"Valid (non-collapsed) runs: {len(valid)} / {len(results)}")

if len(valid) > 10:
    keys = ["C", "jitter", "persistence", "reorg_rate", "v_autocorr", "separation"]
    M = np.array([[r[k] for k in keys] for r in valid])
    stds = np.std(M, axis=0); stds[stds == 0] = 1
    M_std = (M - np.mean(M, axis=0)) / stds

    cov = np.corrcoef(M_std.T)
    eigvals = np.linalg.eigvalsh(cov)[::-1]
    explained = eigvals / np.sum(eigvals)
    cumulative = np.cumsum(explained)

    print(f"\n  Eigenvalues: {['%.4f' % e for e in eigvals]}")
    print(f"  Explained:   {['%.1f%%' % (e*100) for e in explained]}")
    print(f"  Cumulative:  {['%.1f%%' % (c*100) for c in cumulative]}")
    n_90 = np.searchsorted(cumulative, 0.90) + 1
    print(f"  Dimensions for 90% variance: {n_90}")

    eigvecs = np.linalg.eigh(cov)[1][:, ::-1]
    for pc in range(min(3, len(keys))):
        print(f"\n  PC{pc+1} loadings:")
        for i, k in enumerate(keys):
            print(f"    {k:>15s}: {eigvecs[i,pc]:+.4f}")

# ─── Correlation matrix ───
print("\n" + "─" * 120)
print("METRIC CORRELATIONS")
print("─" * 120)
if len(valid) > 10:
    keys2 = ["C", "jitter", "persistence", "reorg_rate", "v_autocorr", "separation"]
    M2 = np.array([[r[k] for k in keys2] for r in valid])
    corr = np.corrcoef(M2.T)
    header = "".join(f"{k:>12s}" for k in keys2)
    print(f"{'':>16s}{header}")
    for i, k in enumerate(keys2):
        row = "".join(f"{corr[i,j]:>12.3f}" for j in range(len(keys2)))
        print(f"{k:>16s}{row}")
