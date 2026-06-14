"""RD-8B: Fertility Recon v2 — fixed coarse-graining.
Also: re-run geometry with fertility metrics included.
"""

import sys, os, json, time
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings("ignore")

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
                ffx, ffy, _ = _soft_sphere_force(dx, dy, radii[i], radii[j], stiffness, damping)
                fx[i] += ffx; fy[i] += ffy; fx[j] -= ffx; fy[j] -= ffy
            vx[i] += fx[i] / masses[i] * dt; vy[i] += fy[i] / masses[i] * dt
            vx[i] *= (1.0 - friction * dt); vy[i] *= (1.0 - friction * dt)
            x[i] += vx[i] * dt; y[i] += vy[i] * dt
            if x[i] - radii[i] < 0: x[i] = radii[i]; vx[i] *= -0.5
            elif x[i] + radii[i] > box_width: x[i] = box_width - radii[i]; vx[i] *= -0.5
            if y[i] - radii[i] < 0: y[i] = radii[i]; vy[i] *= -0.5
        all_x[:, step] = x; all_y[:, step] = y
        all_vx[:, step] = vx; all_vy[:, step] = vy
    return all_y, all_x, all_vx, all_vy


def _bin_data(py, px, n_bins=10):
    final_x = np.nanmean(px[:, -100:], axis=1)
    x_order = np.argsort(final_x)
    x_bins = np.array_split(x_order, n_bins)
    return np.array([np.mean(py[b], axis=0) for b in x_bins])


def _sliding_C(X, window=75, step=25):
    T = X.shape[1]; times, vals = [], []
    for t in range(0, T - window + 1, step):
        times.append(t + window // 2)
        try: vals.append(compute_C(X[:, t:t + window], "gaussian"))
        except: vals.append(np.nan)
    return np.array(times), np.array(vals)


# ─── FIXED fertility metrics ───

def novel_state_rate(all_y, n_bins=10, window=100, step=50):
    """Coarse-grained state = y-position quantile pattern.
    Use coarse bins (10 bins, 100-step windows) so states repeat."""
    T = all_y.shape[1]
    seen = set()
    novel = 0; total = 0
    
    for t in range(0, T - window + 1, step):
        seg = all_y[:, t:t+window]
        mean_y = np.nanmean(seg, axis=1)
        # Discretize into 10 bins
        state = tuple(np.digitize(mean_y, bins=np.linspace(0, 50, 10)))
        total += 1
        if state not in seen:
            seen.add(state)
            novel += 1
    return novel / max(total, 1)


def state_space_coverage(all_y, n_bins=10):
    """Fraction of possible coarse-grained states actually visited."""
    T = all_y.shape[1]
    visited = set()
    
    for t in range(0, T - 50, 25):
        seg = all_y[:, t:t+100]
        mean_y = np.nanmean(seg, axis=1)
        state = tuple(np.digitize(mean_y, bins=np.linspace(0, 50, n_bins)))
        visited.add(state)
    
    # Total possible states (approximate)
    total_possible = min(10000, n_bins ** min(15, all_y.shape[0]))
    return len(visited) / total_possible


def trajectory_divergence(all_y, n_pairs=100, lag=50):
    """Lyapunov-like divergence of grain trajectories."""
    n_grains, T = all_y.shape
    rng = np.random.default_rng(42)
    divergences = []
    for _ in range(n_pairs):
        i, j = rng.choice(n_grains, 2, replace=False)
        d0 = np.abs(all_y[i, 0] - all_y[j, 0])
        if d0 < 0.5: continue
        for t0 in range(0, T - lag - 200, 50):
            d_lag = np.abs(all_y[i, t0+lag] - all_y[j, t0+lag])
            if d0 > 0 and d_lag > 0:
                divergences.append(np.log(d_lag / d0) / (lag * 0.01))
    return float(np.mean(divergences)) if divergences else 0.0


def velocity_entropy(all_vx, all_vy, n_bins=15):
    """Shannon entropy of velocity distribution."""
    vx = all_vx.flatten()
    vy = all_vy.flatten()
    valid = ~(np.isnan(vx) | np.isnan(vy))
    vx, vy = vx[valid], vy[valid]
    if len(vx) < 100: return 0.0
    h, _, _ = np.histogram2d(vx, vy, bins=n_bins)
    h = h / h.sum()
    h = h[h > 0]
    return float(-np.sum(h * np.log2(h)))


def expansion_velocity(all_y, window=100, step=50):
    """Rate of y-volume growth."""
    T = all_y.shape[1]
    volumes, times = [], []
    for t in range(0, T - window + 1, step):
        seg = all_y[:, t:t+window]
        volumes.append(np.nanmax(seg) - np.nanmin(seg))
        times.append(t)
    if len(volumes) < 3: return 0.0
    times = np.array(times, dtype=float)
    volumes = np.array(volumes, dtype=float)
    valid = ~np.isnan(volumes) & ~np.isinf(volumes)
    if np.sum(valid) < 3: return 0.0
    slope, _, _, _, _ = stats.linregress(times[valid], volumes[valid])
    return float(slope)


def configurational_diversity(all_y, window=50, step=25):
    """Number of distinct configuration clusters in trajectory space."""
    T = all_y.shape[1]
    states = []
    for t in range(0, T - window + 1, step):
        seg = all_y[:, t:t+window]
        mean_y = np.nanmean(seg, axis=1)[:10]
        states.append(mean_y)
    
    if len(states) < 5: return 0.0
    states_arr = np.array(states)
    
    # K-means with k=5, measure inertia (lower = more clustered)
    from sklearn.cluster import KMeans
    km = KMeans(n_clusters=5, random_state=42, n_init=10)
    labels = km.fit_predict(states_arr)
    
    # Count distinct clusters actually used
    n_used = len(set(labels))
    # Also: mean distance to cluster center (lower = tighter clusters)
    return float(n_used / 5.0)


# ─── Main sweep ───
FRICTION_LEVELS = np.linspace(0.05, 0.80, 16)
N_REPS = 10
N_GRAINS = 50; N_STEPS = 1000; BASE_SEED = 6000

results = []
t0 = time.time()
total = len(FRICTION_LEVELS) * N_REPS
done = 0

for fr in FRICTION_LEVELS:
    for rep in range(N_REPS):
        seed = BASE_SEED + rep + int(fr * 10000)
        all_y, all_x, all_vx, all_vy = _run_friction(
            n_grains=N_GRAINS, n_steps=N_STEPS, friction=fr, seed=seed)
        
        # C
        X = _bin_data(all_y, all_x, n_bins=10)
        _, c_vals = _sliding_C(X, window=75, step=25)
        pre_mask = np.arange(len(c_vals)) * 25 + 37
        c_val = float(np.nanmean(c_vals[(pre_mask >= 100) & (pre_mask < 500)]))
        
        # Fertility
        nsr = novel_state_rate(all_y)
        ssc = state_space_coverage(all_y)
        td = trajectory_divergence(all_y)
        ve = velocity_entropy(all_vx, all_vy)
        sev = expansion_velocity(all_y)
        cd = configurational_diversity(all_y)
        
        # Physical
        jitter = float(np.nanmean(np.sqrt(all_vx**2 + all_vy**2)))
        
        results.append({
            "friction": round(float(fr), 4), "rep": rep,
            "C": round(c_val, 4),
            "jitter": round(jitter, 2),
            "novel_state_rate": round(nsr, 4),
            "state_coverage": round(ssc, 6),
            "traj_divergence": round(td, 4),
            "velocity_entropy": round(ve, 4),
            "expansion_velocity": round(sev, 4),
            "config_diversity": round(cd, 4),
        })
        
        done += 1
        if done % 40 == 0:
            print(f"  [{done}/{total}] {time.time()-t0:.0f}s elapsed")

print(f"\nSweep: {done} runs in {time.time()-t0:.0f}s")

with open("audits/rd8b_fertility_v2.json", "w") as f:
    json.dump(results, f, indent=2)

# ─── Summary ───
print("\n" + "=" * 125)
print("RD-8B v2: FERTILITY RECON")
print("=" * 125)
print(f"\n{'μ':>6s} {'C':>7s} {'Jitter':>8s} {'NSR':>7s} {'Coverage':>10s} {'TD':>8s} {'VE':>8s} {'ExpVel':>8s} {'ConfigD':>8s}")
print("-" * 125)

for fr in FRICTION_LEVELS:
    sub = [r for r in results if abs(r["friction"] - fr) < 0.001]
    def ms(k):
        v = [r[k] for r in sub if r.get(k) is not None]
        return np.mean(v) if v else np.nan
    print(f"{fr:>6.3f} {ms('C'):>7.3f} {ms('jitter'):>8.2f} {ms('novel_state_rate'):>7.3f} "
          f"{ms('state_coverage'):>10.6f} {ms('traj_divergence'):>8.4f} "
          f"{ms('velocity_entropy'):>8.3f} {ms('expansion_velocity'):>8.4f} "
          f"{ms('config_diversity'):>8.4f}")

# ─── Correlations ───
print("\n" + "─" * 125)
print("CORRELATION MATRIX (fertility + existing)")
print("─" * 125)

keys = ["C", "jitter", "novel_state_rate", "state_coverage", "traj_divergence",
        "velocity_entropy", "expansion_velocity", "config_diversity"]
valid = [r for r in results if all(r.get(k) is not None for k in keys)]
if len(valid) > 10:
    M = np.array([[r[k] for k in keys] for r in valid])
    corr = np.corrcoef(M.T)
    header = "".join(f"{k[:7]:>10s}" for k in keys)
    print(f"{'':>20s}{header}")
    for i, k in enumerate(keys):
        row = "".join(f"{corr[i,j]:>10.3f}" for j in range(len(keys)))
        print(f"{k:>20s}{row}")

# ─── Re-run geometry with fertility metrics ───
print("\n" + "=" * 125)
print("RE-RUNNING GEOMETRY WITH FERTILITY METRICS")
print("=" * 125)

# Merge with t901 matrix
with open("audits/rd8a_metric_names_t901.json") as f:
    t901_names = json.load(f)
with open("audits/rd8a_row_metadata.json") as f:
    t901_meta = json.load(f)

M_t901 = np.load("audits/rd8a_matrix_t901.npy")

# Match RD-8B to t901 by friction
rd08b_by_fr = {}
for r in results:
    fr = round(r["friction"], 2)
    if fr not in rd08b_by_fr:
        rd08b_by_fr[fr] = []
    rd08b_by_fr[fr].append(r)

fert_keys = ["novel_state_rate", "state_coverage", "traj_divergence",
             "velocity_entropy", "expansion_velocity", "config_diversity"]

expanded_names = t901_names + fert_keys
M_expanded = []

for i, (row, meta) in enumerate(zip(M_t901, t901_meta)):
    fr = meta["friction"]
    best_fr = min(rd08b_by_fr.keys(), key=lambda x: abs(x - fr))
    if abs(best_fr - fr) < 0.06 and len(rd08b_by_fr[best_fr]) > meta["rep"]:
        rb = rd08b_by_fr[best_fr][meta["rep"]]
        exp_row = list(row) + [rb[k] for k in fert_keys]
    else:
        exp_row = list(row) + [np.nan] * len(fert_keys)
    M_expanded.append(exp_row)

M_expanded = np.array(M_expanded, dtype=float)

# Impute NaN
for j in range(M_expanded.shape[1]):
    col = M_expanded[:, j]
    nan_mask = np.isnan(col)
    if np.any(nan_mask):
        col[nan_mask] = np.nanmean(col)

# Standardize
M_std = (M_expanded - np.mean(M_expanded, axis=0)) / np.std(M_expanded, axis=0)

# PCA
cov = np.cov(M_std.T)
eigvals, eigvecs = np.linalg.eigh(cov)
eigvals = eigvals[::-1]; eigvecs = eigvecs[:, ::-1]
explained = eigvals / np.sum(eigvals)
cumulative = np.cumsum(explained)

print(f"\nMatrix: {M_std.shape[0]} runs × {M_std.shape[1]} metrics")
print(f"Metrics: {expanded_names}")
print(f"\n{'PC':>4s} {'Explained%':>12s} {'Cumulative%':>12s}")
print("-" * 30)
for i in range(len(eigvals)):
    marker = " ←" if cumulative[i] >= 0.90 and (i == 0 or cumulative[i-1] < 0.90) else ""
    print(f"PC{i+1:>2d} {explained[i]*100:>11.1f}% {cumulative[i]*100:>11.1f}%{marker}")

# Loadings for top PCs
n_90 = np.searchsorted(cumulative, 0.90) + 1
print(f"\nDimensions for 90% variance: {n_90}")

for pc in range(min(n_90, len(expanded_names))):
    loadings = eigvecs[:, pc]
    sorted_idx = np.argsort(np.abs(loadings))[::-1]
    top3 = [(expanded_names[idx], loadings[idx]) for idx in sorted_idx[:5]]
    print(f"\nPC{pc+1} ({explained[pc]*100:.1f}%):")
    for name, val in top3:
        print(f"    {name:>25s}: {val:+.4f}")

# ─── Key question: do fertility metrics load on a NEW factor? ───
print("\n" + "─" * 125)
print("KEY QUESTION: Do fertility metrics load on a new factor?")
print("─" * 125)

# Check loadings of fertility metrics on each PC
for pc in range(min(5, len(expanded_names))):
    fert_loadings = [(expanded_names[i], eigvecs[i, pc]) for i in range(len(expanded_names))
                     if expanded_names[i] in fert_keys]
    max_fert = max(abs(l) for _, l in fert_loadings)
    existing_loadings = [(expanded_names[i], eigvecs[i, pc]) for i in range(len(expanded_names))
                         if expanded_names[i] not in fert_keys]
    max_exist = max(abs(l) for _, l in existing_loadings) if existing_loadings else 0
    
    if max_fert > 0.3:
        print(f"\nPC{pc+1} ({explained[pc]*100:.1f}%):")
        for name, val in sorted(fert_loadings, key=lambda x: abs(x[1]), reverse=True):
            if abs(val) > 0.2:
                print(f"  FERTILITY: {name:>25s}: {val:+.4f}")
        for name, val in sorted(existing_loadings, key=lambda x: abs(x[1]), reverse=True)[:3]:
            if abs(val) > 0.3:
                print(f"  EXISTING:  {name:>25s}: {val:+.4f}")
