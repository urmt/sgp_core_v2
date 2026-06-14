"""RD-8: State-Space Cartography (revised)
Sweep noise at meaningful amplitudes. Compute all 5 state variables from raw trajectories.
Identify regimes and map state space.
"""

import sys, os, json, time
import numpy as np
from scipy import stats, signal

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, "coherence-benchmark")

from t901_analysis import _soft_sphere_force
from metrics.total_correlation import compute_C

# ─── Modified granular run with STRONG noise injection ───
def _granular_run_noisy(n_grains=50, n_steps=1000, friction=0.3, noise_frac=0.0, seed=42):
    """noise_frac: noise amplitude as fraction of mean velocity magnitude."""
    rng = np.random.default_rng(seed)
    radii = rng.uniform(0.8, 1.5, n_grains)
    masses = radii ** 2
    box_width = 40.0

    x = rng.uniform(2, box_width - 2, n_grains)
    y = rng.uniform(5, 30, n_grains)
    vx = rng.uniform(-0.5, 0.5, n_grains)
    vy = rng.uniform(-0.5, 0.5, n_grains)

    gy = -1.0; dt = 0.01; stiffness = 500.0; damping = 2.0
    removed = np.zeros(n_grains, dtype=bool)

    all_x = np.zeros((n_grains, n_steps))
    all_y = np.zeros((n_grains, n_steps))
    all_vx = np.zeros((n_grains, n_steps))
    all_vy = np.zeros((n_grains, n_steps))

    for step in range(n_steps):
        forces_x = np.zeros(n_grains)
        forces_y = np.full(n_grains, gy * masses)

        for i in range(n_grains):
            if removed[i]: continue
            for j in range(i + 1, n_grains):
                if removed[j]: continue
                dx = x[j] - x[i]; dy = y[j] - y[i]
                if abs(dx) > 3.0 or abs(dy) > 3.0: continue
                fx, fy, ov = _soft_sphere_force(dx, dy, radii[i], radii[j], stiffness, damping)
                forces_x[i] += fx; forces_y[i] += fy
                forces_x[j] -= fx; forces_y[j] -= fy

            vx[i] += forces_x[i] / masses[i] * dt
            vy[i] += forces_y[i] / masses[i] * dt
            vx[i] *= (1.0 - friction * dt)
            vy[i] *= (1.0 - friction * dt)

            # STRONG noise: add velocity perturbation proportional to current velocity
            if noise_frac > 0:
                speed = np.sqrt(vx[i]**2 + vy[i]**2)
                noise_std = noise_frac * max(speed, 1.0)
                vx[i] += rng.normal(0, noise_std)
                vy[i] += rng.normal(0, noise_std)

            x[i] += vx[i] * dt
            y[i] += vy[i] * dt

            if x[i] - radii[i] < 0: x[i] = radii[i]; vx[i] *= -0.5
            elif x[i] + radii[i] > box_width: x[i] = box_width - radii[i]; vx[i] *= -0.5
            if y[i] - radii[i] < 0: y[i] = radii[i]; vy[i] *= -0.5

        all_x[:, step] = np.where(removed, np.nan, x)
        all_y[:, step] = np.where(removed, np.nan, y)
        all_vx[:, step] = np.where(removed, np.nan, vx)
        all_vy[:, step] = np.where(removed, np.nan, vy)

    return all_y, all_x, all_vx, all_vy


def _bin_data(positions_y, positions_x, n_bins=10):
    nan_mask = np.isnan(positions_y)
    col_means = np.nanmean(positions_y, axis=1, keepdims=True)
    positions_y = np.where(nan_mask, col_means, positions_y)
    with np.errstate(invalid="ignore"):
        final_x = np.nanmean(positions_x[:, -100:], axis=1)
    final_x = np.where(np.isnan(final_x), np.nanmean(positions_x[:, :500], axis=1), final_x)
    order = np.argsort(final_x)
    bins = np.array_split(order, n_bins)
    return np.array([np.mean(positions_y[b], axis=0) for b in bins])


def _sliding_C(X, window=75, step=25):
    T = X.shape[1]
    times, vals = [], []
    for t in range(0, T - window + 1, step):
        seg = X[:, t:t + window]
        times.append(t + window // 2)
        try: vals.append(compute_C(seg, "gaussian"))
        except Exception: vals.append(np.nan)
    return np.array(times), np.array(vals)


# ─── State variables ───

def measure_fertility(all_y, window=50, step=25):
    """Fertility: rate of novel state discovery."""
    T = all_y.shape[1]
    seen = set()
    novel = 0
    total = 0
    for t in range(0, T - window + 1, step):
        seg = all_y[:, t:t+window]
        # Coarse-grained state: which bin has the most grains?
        state = tuple(np.argmax(np.nanmean(seg, axis=1)[:10]) for _ in range(3))  # top-3 bins
        total += 1
        if state not in seen:
            seen.add(state)
            novel += 1
    return novel / max(total, 1)


def measure_persistence(c_vals, dt=25):
    """Persistence: autocorrelation time of C(t) (1/e decay)."""
    c_clean = c_vals[~np.isnan(c_vals)]
    if len(c_clean) < 20:
        return np.nan
    c_centered = c_clean - np.mean(c_clean)
    n = len(c_centered)
    f = np.fft.fft(c_centered, n=2*n)
    acf = np.fft.ifft(f * np.conjugate(f))[:n].real
    if acf[0] > 0:
        acf = acf / acf[0]
    threshold = 1.0 / np.e
    for i in range(1, len(acf)):
        if acf[i] < threshold:
            return float(i * dt)
    return float(len(acf) * dt)


# ─── Sweep ───
NOISE_LEVELS = np.linspace(0.0, 2.0, 25)  # Much wider range: 0 to 2.0
N_REPS = 10
FRICTION = 0.30
N_GRAINS = 50
N_STEPS = 1000
BASE_SEED = 4000

results = []
t0 = time.time()
total = len(NOISE_LEVELS) * N_REPS
done = 0

for noise in NOISE_LEVELS:
    for rep in range(N_REPS):
        seed = BASE_SEED + rep + int(noise * 10000)
        
        all_y, all_x, all_vx, all_vy = _granular_run_noisy(
            n_grains=N_GRAINS, n_steps=N_STEPS, friction=FRICTION,
            noise_frac=noise, seed=seed,
        )
        
        X = _bin_data(all_y, all_x, n_bins=10)
        times, c_vals = _sliding_C(X, window=75, step=25)
        
        # State variables
        pre_mask = (times >= 100) & (times < 500)
        coherence = float(np.nanmean(c_vals[pre_mask])) if np.sum(pre_mask) >= 2 else np.nan
        fertility = measure_fertility(all_y)
        
        # Jitter: mean speed
        speed = np.sqrt(all_vx**2 + all_vy**2)
        jitter = float(np.nanmean(speed))
        
        # Persistence
        persistence = measure_persistence(c_vals)
        
        # Adaptability: from perturbation (remove 10% at step 500)
        # Actually, let's measure it from the C trajectory itself
        # How fast does C return to baseline after fluctuations?
        c_clean = c_vals[~np.isnan(c_vals)]
        if len(c_clean) > 20:
            # Measure typical fluctuation recovery time
            c_mean = np.mean(c_clean)
            # Find times C drops below 95% of mean
            below = c_clean < 0.95 * c_mean
            # Count transitions (drops and recoveries)
            transitions = np.sum(np.diff(below.astype(int)) != 0)
            adaptability = transitions / len(c_clean)  # fraction of time in transition
        else:
            adaptability = np.nan
        
        # Phase coherence: how synchronized are grain oscillations?
        # Use pairwise velocity correlation
        active = ~np.isnan(all_vx[:, 0])
        vx_active = all_vx[active, :]
        if vx_active.shape[0] > 2:
            # Correlation matrix of velocities
            corr_mat = np.corrcoef(vx_active[:, :200])  # first 200 steps
            n_grains_active = corr_mat.shape[0]
            if n_grains_active > 1:
                # Mean off-diagonal correlation
                mask = ~np.eye(n_grains_active, dtype=bool)
                phase_sync = float(np.nanmean(corr_mat[mask]))
            else:
                phase_sync = 0.0
        else:
            phase_sync = 0.0
        
        results.append({
            "noise": round(float(noise), 4),
            "rep": rep,
            "C": round(coherence, 4) if not np.isnan(coherence) else None,
            "fertility": round(fertility, 4),
            "jitter": round(jitter, 4),
            "persistence": round(persistence, 1) if not np.isnan(persistence) else None,
            "adaptability": round(adaptability, 4) if not np.isnan(adaptability) else None,
            "phase_sync": round(phase_sync, 4),
        })
        
        done += 1
        if done % 50 == 0:
            elapsed = time.time() - t0
            print(f"  [{done}/{total}] {elapsed:.0f}s elapsed")

elapsed = time.time() - t0
print(f"\nSweep complete: {done} runs in {elapsed:.0f}s")

# Save
with open("audits/rd08_state_space_v2.json", "w") as f:
    json.dump(results, f, indent=2)

# ─── Summary ───
print("\n" + "=" * 110)
print("RD-8: STATE-SPACE CARTOGRAPHY — NOISE SWEEP v2 (STRONG NOISE)")
print("=" * 110)

print(f"\n{'Noise':>8s} {'C':>8s} {'Fertility':>10s} {'Jitter':>8s} {'Persist':>8s} {'Adapt':>8s} {'PhaseSync':>10s}")
print("-" * 110)

for noise in NOISE_LEVELS:
    subset = [r for r in results if abs(r["noise"] - noise) < 0.001]
    def ms(key):
        vals = [r[key] for r in subset if r.get(key) is not None]
        return (np.mean(vals), np.std(vals)) if vals else (np.nan, 0)
    
    c_m, _ = ms("C")
    f_m, _ = ms("fertility")
    j_m, _ = ms("jitter")
    p_m, _ = ms("persistence")
    a_m, _ = ms("adaptability")
    ps_m, _ = ms("phase_sync")
    
    print(f"{noise:>8.3f} {c_m:>8.3f} {f_m:>10.3f} {j_m:>8.2f} {p_m:>8.1f} {a_m:>8.4f} {ps_m:>10.4f}")

# ─── PCA on all metrics ───
print("\n" + "─" * 110)
print("LATENT DIMENSIONALITY ANALYSIS")
print("─" * 110)

# Build matrix of all metrics
valid = [r for r in results if all(r.get(k) is not None for k in ["C", "fertility", "jitter", "persistence", "phase_sync"])]
if len(valid) > 10:
    metric_keys = ["C", "fertility", "jitter", "persistence", "phase_sync"]
    M = np.array([[r[k] for k in metric_keys] for r in valid])
    # Standardize
    M_std = (M - np.mean(M, axis=0)) / np.std(M, axis=0)
    # PCA
    cov = np.corrcoef(M_std.T)
    eigenvalues = np.linalg.eigvalsh(cov)[::-1]
    explained = eigenvalues / np.sum(eigenvalues)
    cumulative = np.cumsum(explained)
    
    print(f"\n  Eigenvalues: {['%.3f' % e for e in eigenvalues]}")
    print(f"  Explained:   {['%.1f%%' % (e*100) for e in explained]}")
    print(f"  Cumulative:  {['%.1f%%' % (c*100) for c in cumulative]}")
    
    # How many dimensions for 90% variance?
    n_90 = np.searchsorted(cumulative, 0.90) + 1
    print(f"\n  Dimensions for 90% variance: {n_90}")
    print(f"  Dimensions for 80% variance: {np.searchsorted(cumulative, 0.80) + 1}")
    
    # Loadings
    eigvecs = np.linalg.eigh(cov)[1][:, ::-1]
    print(f"\n  PC1 loadings:")
    for i, k in enumerate(metric_keys):
        print(f"    {k:>15s}: {eigvecs[i, 0]:+.4f}")
    print(f"\n  PC2 loadings:")
    for i, k in enumerate(metric_keys):
        print(f"    {k:>15s}: {eigvecs[i, 1]:+.4f}")

print(f"\nRaw data: audits/rd08_state_space_v2.json")
