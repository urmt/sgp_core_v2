"""RD-9E Step 1-3: Continuity, Estimator Sensitivity, Coarse Graining"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'coherence-benchmark'))

from synthetic.generators import coupled_markov, modular, hierarchical, critical
from adapters.ecosystem import EcosystemAdapter

def _soft_sphere_force(all_y, all_x, all_vx, all_vy, radii, dt=0.005, base_friction=0.3, base_normal=50.0):
    n_grains = len(radii)
    fx = np.zeros(n_grains)
    fy = np.zeros(n_grains) - 1.0
    for i in range(n_grains):
        for j in range(i + 1, n_grains):
            dx = all_x[j] - all_x[i]
            dy = all_y[j] - all_y[i]
            dist = np.sqrt(dx**2 + dy**2)
            overlap = radii[i] + radii[j] - dist
            if overlap > 0:
                nx, ny = dx / (dist + 1e-10), dy / (dist + 1e-10)
                fn = base_normal * overlap
                dvx = all_vx[j] - all_vx[i]
                dvy = all_vy[j] - all_vy[i]
                dvn = dvx * nx + dvy * ny
                ft = base_friction * fn if dvn < 0 else 0
                fx[i] += fn * nx + ft * (-ny)
                fy[i] += fn * ny + ft * nx
                fx[j] -= fn * nx + ft * (-ny)
                fy[j] -= fn * ny + ft * nx
    return fx, fy

def run_sim(n_grains=50, n_steps=1500, friction=0.3, seed=42):
    rng = np.random.default_rng(seed)
    radii = np.full(n_grains, 0.25)
    all_x = rng.uniform(1, 9, n_grains)
    all_y = rng.uniform(1, 9, n_grains)
    all_vx = rng.normal(0, 0.1, n_grains)
    all_vy = rng.normal(0, 0.1, n_grains)
    dt = 0.005
    y_hist = np.zeros((n_grains, n_steps))
    for t in range(n_steps):
        fx, fy = _soft_sphere_force(all_y, all_x, all_vx, all_vy, radii, dt=dt, base_friction=friction)
        all_vx += fx * dt
        all_vy += fy * dt
        all_vx *= (1 - 0.1 * friction)
        all_vy *= (1 - 0.1 * friction)
        all_x += all_vx * dt
        all_y += all_vy * dt
        all_x = np.clip(all_x, 0.5, 9.5)
        all_y = np.clip(all_y, 0.5, 9.5)
        below = all_y < 0.2
        all_y[below] = rng.uniform(8, 9, np.sum(below))
        all_x[below] = rng.uniform(1, 9, np.sum(below))
        all_vy[below] = 0
        y_hist[:, t] = all_y
    return y_hist

def compute_sp(ts, k=5, warmup=100, threshold_percentile=90):
    n_comp, T = ts.shape
    surprise_len = T - warmup
    if surprise_len < 20:
        return 0.0, np.array([])
    surprise_ts = np.zeros(surprise_len)
    count = 0
    for g in range(n_comp):
        y = ts[g, :]
        valid = ~np.isnan(y)
        if np.sum(valid) < warmup + k + 10:
            continue
        y_clean = y[valid]
        usable = len(y_clean) - warmup - k - 1
        if usable < 10:
            continue
        n = min(usable, surprise_len)
        lags = np.zeros((n, k))
        for j in range(k):
            lags[:, j] = y_clean[warmup + j:warmup + j + n]
        targets = y_clean[warmup + k:warmup + k + n]
        try:
            beta = np.linalg.lstsq(lags, targets, rcond=None)[0]
            errs = np.abs(targets - lags @ beta)
            surprise_ts[:n] += errs
            count += 1
        except:
            pass
    if count > 0:
        surprise_ts /= count
    nonzero = surprise_ts[surprise_ts > 0]
    if len(nonzero) < 10:
        return 0.0, surprise_ts
    threshold = np.percentile(nonzero, threshold_percentile)
    surprise_binary = (surprise_ts > threshold).astype(float)
    if np.sum(surprise_binary) < 5:
        return 0.0, surprise_ts
    n = len(surprise_binary)
    acf = np.correlate(surprise_binary - np.mean(surprise_binary),
                       surprise_binary - np.mean(surprise_binary), mode='full')
    acf = acf[n - 1:]
    if acf[0] > 0:
        acf /= acf[0]
    for i in range(1, len(acf)):
        if acf[i] < 1.0 / np.e:
            return float(i), surprise_ts
    return float(len(acf)), surprise_ts

# STEP 1: Continuity
print("=" * 70)
print("STEP 1: CONTINUITY CHECK")
print("=" * 70)
frictions = np.linspace(0.1, 1.5, 12)
sp_all = []
t0 = time.time()
for i, mu in enumerate(frictions):
    for r in range(6):
        seed = i * 100 + r + 1000
        y = run_sim(n_grains=50, n_steps=1500, friction=mu, seed=seed)
        sp, _ = compute_sp(y)
        sp_all.append(sp)
    elapsed = time.time() - t0
    print(f"  [{i+1}/12] {elapsed:.0f}s | μ={mu:.2f} SP_vals={[f'{sp_all[-6+j]:.1f}' for j in range(6)]}")

sp_all = np.array(sp_all)
unique_vals = np.unique(sp_all)
print(f"\nUnique SP values: {unique_vals}")
for v in unique_vals:
    c = np.sum(sp_all == v)
    print(f"  SP={v:.1f}: {c} runs ({100*c/len(sp_all):.1f}%)")
print(f"Mean: {np.mean(sp_all):.3f}, Std: {np.std(sp_all):.3f}")

# Finer thresholds
print("\n--- Finer threshold sweep ---")
for pct in [80, 85, 90, 95]:
    sp_fine = []
    for i, mu in enumerate(frictions):
        for r in range(6):
            seed = i * 100 + r + 1000
            y = run_sim(n_grains=50, n_steps=1500, friction=mu, seed=seed)
            sp, _ = compute_sp(y, threshold_percentile=pct)
            sp_fine.append(sp)
    print(f"  pct={pct}: {len(np.unique(sp_fine))} unique values {np.unique(sp_fine)}")

# STEP 2: Estimator sensitivity (smaller grid)
print("\n" + "=" * 70)
print("STEP 2: ESTIMATOR SENSITIVITY")
print("=" * 70)
# Precompute 36 time series
print("Precomputing 36 time series...")
raw_data = []
frictions2 = np.linspace(0.1, 1.5, 6)
for mu in frictions2:
    for r in range(6):
        y = run_sim(n_grains=50, n_steps=1500, friction=mu, seed=r*100+1000)
        raw_data.append((mu, y))

for k in [3, 5, 10]:
    sp_vals = [compute_sp(y, k=k)[0] for _, y in raw_data]
    print(f"  k={k}: mean={np.mean(sp_vals):.3f}, unique={np.unique(sp_vals)}")

for pct in [80, 85, 90, 95]:
    sp_vals = [compute_sp(y, threshold_percentile=pct)[0] for _, y in raw_data]
    print(f"  pct={pct}: mean={np.mean(sp_vals):.3f}, unique={np.unique(sp_vals)}")

for w in [50, 100, 200]:
    sp_vals = [compute_sp(y, warmup=w)[0] for _, y in raw_data]
    print(f"  warmup={w}: mean={np.mean(sp_vals):.3f}, unique={np.unique(sp_vals)}")

# STEP 3: Coarse graining
print("\n" + "=" * 70)
print("STEP 3: COARSE GRABINING")
print("=" * 70)
for n_bins in [5, 10, 15, 20]:
    sp_vals = []
    for mu in frictions2:
        for r in range(6):
            y_hist = run_sim(n_grains=50, n_steps=1500, friction=mu, seed=r*100+1000)
            bin_edges = np.linspace(0, 10, n_bins + 1)
            binned = np.zeros((n_bins, y_hist.shape[1]))
            for t in range(y_hist.shape[1]):
                hist, _ = np.histogram(y_hist[:, t], bins=bin_edges)
                binned[:, t] = hist.astype(float)
            sp, _ = compute_sp(binned)
            sp_vals.append(sp)
    print(f"  bins={n_bins}: mean={np.mean(sp_vals):.3f}, unique={np.unique(sp_vals)}")

print(f"\nTotal time: {time.time()-t0:.0f}s")
