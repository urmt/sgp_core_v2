"""RD-9E Quick Audit: SP properties with tiny fast simulations"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'coherence-benchmark'))

from synthetic.generators import coupled_markov, modular, hierarchical, critical
from adapters.ecosystem import EcosystemAdapter

def run_tiny_sim(n_grains=20, n_steps=500, friction=0.3, seed=42):
    """Tiny granular sim for fast SP testing."""
    rng = np.random.default_rng(seed)
    all_y = rng.uniform(1, 9, n_grains)
    all_x = rng.uniform(1, 9, n_grains)
    all_vy = rng.normal(0, 0.1, n_grains)
    all_vx = rng.normal(0, 0.1, n_grains)
    radii = np.full(n_grains, 0.25)
    y_hist = np.zeros((n_grains, n_steps))
    dt = 0.005
    for t in range(n_steps):
        for i in range(n_grains):
            for j in range(i+1, n_grains):
                dx = all_x[j]-all_x[i]; dy = all_y[j]-all_y[i]
                dist = np.sqrt(dx**2+dy**2)
                overlap = radii[i]+radii[j]-dist
                if overlap > 0:
                    nx,ny = dx/(dist+1e-10), dy/(dist+1e-10)
                    fn = 50*overlap
                    dvn = (all_vx[j]-all_vx[i])*nx + (all_vy[j]-all_vy[i])*ny
                    ft = friction*fn if dvn < 0 else 0
                    all_vx[i] += (fn*nx+ft*(-ny))*dt; all_vy[i] += (fn*ny+ft*nx)*dt
                    all_vx[j] -= (fn*nx+ft*(-ny))*dt; all_vy[j] -= (fn*ny+ft*nx)*dt
        all_vx *= (1-0.1*friction); all_vy *= (1-0.1*friction)
        all_vx += rng.normal(0,0.01,n_grains); all_vy += rng.normal(0,0.01,n_grains)
        all_x += all_vx*dt; all_y += all_vy*dt
        all_x = np.clip(all_x,0.5,9.5); all_y = np.clip(all_y,0.5,9.5)
        below = all_y < 0.2
        all_y[below] = rng.uniform(8,9,np.sum(below))
        all_x[below] = rng.uniform(1,9,np.sum(below))
        all_vy[below] = 0
        y_hist[:,t] = all_y
    return y_hist

def compute_sp(ts, k=3, warmup=30, threshold_percentile=90):
    n_comp, T = ts.shape
    surprise_len = T - warmup
    if surprise_len < 10:
        return 0.0
    surprise_ts = np.zeros(surprise_len)
    count = 0
    for g in range(n_comp):
        y = ts[g, :]
        valid = ~np.isnan(y)
        if np.sum(valid) < warmup + k + 5:
            continue
        y_clean = y[valid]
        usable = len(y_clean) - warmup - k - 1
        if usable < 5:
            continue
        n = min(usable, surprise_len)
        lags = np.zeros((n, k))
        for j in range(k):
            lags[:, j] = y_clean[warmup+j:warmup+j+n]
        targets = y_clean[warmup+k:warmup+k+n]
        try:
            beta = np.linalg.lstsq(lags, targets, rcond=None)[0]
            surprise_ts[:n] += np.abs(targets - lags @ beta)
            count += 1
        except:
            pass
    if count > 0:
        surprise_ts /= count
    nonzero = surprise_ts[surprise_ts > 0]
    if len(nonzero) < 5:
        return 0.0
    threshold = np.percentile(nonzero, threshold_percentile)
    sb = (surprise_ts > threshold).astype(float)
    if np.sum(sb) < 3:
        return 0.0
    n = len(sb)
    acf = np.correlate(sb - np.mean(sb), sb - np.mean(sb), mode='full')
    acf = acf[n-1:]
    if acf[0] > 0:
        acf /= acf[0]
    for i in range(1, len(acf)):
        if acf[i] < 1.0/np.e:
            return float(i)
    return float(len(acf))

# ============================================================
# STEP 1: Continuity (tiny sim: 20 grains, 500 steps)
# ============================================================
print("=" * 70)
print("STEP 1: CONTINUITY (tiny sims: 20 grains, 500 steps)")
print("=" * 70)
t0 = time.time()
sp_all = []
for i, mu in enumerate(np.linspace(0.1, 1.5, 12)):
    sps = []
    for r in range(6):
        y = run_tiny_sim(n_grains=20, n_steps=500, friction=mu, seed=i*100+r+1000)
        sp = compute_sp(y)
        sps.append(sp)
    sp_all.extend(sps)
    print(f"  [{i+1}/12] {time.time()-t0:.0f}s μ={mu:.2f} SP={[f'{s:.1f}' for s in sps]}")

sp_all = np.array(sp_all)
print(f"\nUnique: {np.unique(sp_all)}")
print(f"Distribution:")
for v in np.unique(sp_all):
    c = np.sum(sp_all == v)
    print(f"  SP={v:.1f}: {c} ({100*c/len(sp_all):.1f}%)")
print(f"Mean={np.mean(sp_all):.3f} Std={np.std(sp_all):.3f}")

# Finer thresholds
print("\nThreshold sweep:")
for pct in [80, 85, 90, 95]:
    sp_f = []
    for i, mu in enumerate(np.linspace(0.1, 1.5, 12)):
        for r in range(6):
            y = run_tiny_sim(n_grains=20, n_steps=500, friction=mu, seed=i*100+r+1000)
            sp_f.append(compute_sp(y, threshold_percentile=pct))
    print(f"  pct={pct}: {len(np.unique(sp_f))} unique {np.unique(sp_f)}")

# ============================================================
# STEP 2: Estimator sensitivity (precompute 36 sims)
# ============================================================
print("\n" + "=" * 70)
print("STEP 2: ESTIMATOR SENSITIVITY (36 tiny sims)")
print("=" * 70)
raw = []
for mu in np.linspace(0.1, 1.5, 6):
    for r in range(6):
        raw.append(run_tiny_sim(n_grains=20, n_steps=500, friction=mu, seed=r*100+1000))

for k in [2, 3, 5]:
    sps = [compute_sp(y, k=k) for y in raw]
    print(f"  k={k}: mean={np.mean(sps):.3f} unique={np.unique(sps)}")
for pct in [80, 85, 90, 95]:
    sps = [compute_sp(y, threshold_percentile=pct) for y in raw]
    print(f"  pct={pct}: mean={np.mean(sps):.3f} unique={np.unique(sps)}")
for w in [20, 30, 50]:
    sps = [compute_sp(y, warmup=w) for y in raw]
    print(f"  warmup={w}: mean={np.mean(sps):.3f} unique={np.unique(sps)}")

# ============================================================
# STEP 3: Coarse graining
# ============================================================
print("\n" + "=" * 70)
print("STEP 3: COARSE GRAINING")
print("=" * 70)
for n_bins in [3, 5, 10]:
    sps = []
    for mu in np.linspace(0.1, 1.5, 6):
        for r in range(6):
            y = run_tiny_sim(n_grains=20, n_steps=500, friction=mu, seed=r*100+1000)
            edges = np.linspace(0, 10, n_bins + 1)
            binned = np.zeros((n_bins, y.shape[1]))
            for t in range(y.shape[1]):
                h, _ = np.histogram(y[:, t], bins=edges)
                binned[:, t] = h.astype(float)
            sps.append(compute_sp(binned))
    print(f"  bins={n_bins}: mean={np.mean(sps):.3f} unique={np.unique(sps)}")

# ============================================================
# STEP 6: Domain transfer (these are fast)
# ============================================================
print("\n" + "=" * 70)
print("STEP 6: DOMAIN TRANSFER")
print("=" * 70)

# Coupled Markov
print("\n--- Coupled Markov ---")
for c in [0.0, 0.2, 0.4, 0.6, 0.8]:
    sps = [compute_sp(coupled_markov(n_components=10, n_timepoints=500, coupling=c, seed=s)) for s in range(10)]
    print(f"  coupling={c}: {len(np.unique(sps))} unique {np.unique(sps)} mean={np.mean(sps):.3f}")

# Modular
print("\n--- Modular ---")
for w in [0.1, 0.3, 0.5, 0.7]:
    sps = [compute_sp(modular(n_per_module=4, n_modules=3, n_timepoints=500, within=w, between=0.1, seed=s)) for s in range(10)]
    print(f"  within={w}: {len(np.unique(sps))} unique {np.unique(sps)} mean={np.mean(sps):.3f}")

# Hierarchical
print("\n--- Hierarchical ---")
for mc in [0.1, 0.2, 0.4, 0.6]:
    sps = [compute_sp(hierarchical(base_n=8, n_levels=3, n_timepoints=500, micro_coupling=mc, seed=s)) for s in range(10)]
    print(f"  micro_c={mc}: {len(np.unique(sps))} unique {np.unique(sps)} mean={np.mean(sps):.3f}")

# Forest
print("\n--- Forest ---")
adapter = EcosystemAdapter(n_plots=24, n_species=20, n_years=40, drought_year=5)
sps = []
for i, (data, meta) in enumerate(adapter.load_all_plots()):
    sps.append(compute_sp(data, warmup=5))
print(f"  {len(np.unique(sps))} unique {np.unique(sps)} mean={np.mean(sps):.3f}")

# Sandpile
print("\n--- Sandpile ---")
sps = [compute_sp(critical(system='sandpile', seed=s), warmup=10) for s in range(5)]
print(f"  {len(np.unique(sps))} unique {np.unique(sps)} mean={np.mean(sps):.3f}")

# Independent noise (null)
print("\n--- Independent noise (null) ---")
from synthetic.generators import independent
sps = [compute_sp(independent(n_components=10, n_timepoints=500, seed=s)) for s in range(10)]
print(f"  {len(np.unique(sps))} unique {np.unique(sps)} mean={np.mean(sps):.3f}")

print(f"\nTotal: {time.time()-t0:.0f}s")
