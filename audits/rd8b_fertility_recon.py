"""RD-8B: Fertility Recon
Compute possibility-generation metrics from raw trajectories (RD-8 friction sweep).
Then merge with t901 metric matrix and re-run geometry.

Candidate fertility operationalizations:
1. Novel state discovery rate: how fast new y-position patterns appear
2. State-space expansion velocity: rate of explored volume growth
3. Trajectory divergence: how fast nearby trajectories separate (sensitive to initial conditions)
4. Velocity diversity: Shannon entropy of velocity distribution over time
5. Configurational richness: number of distinct local minima in position space
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

# ─── Re-run simulations with raw trajectory storage ───
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
            x[i] += vx[i] * dt; y[i] += vy[i] * dt
            if x[i] - radii[i] < 0: x[i] = radii[i]; vx[i] *= -0.5
            elif x[i] + radii[i] > box_width: x[i] = box_width - radii[i]; vx[i] *= -0.5
            if y[i] - radii[i] < 0: y[i] = radii[i]; vy[i] *= -0.5
        all_x[:, step] = x; all_y[:, step] = y
        all_vx[:, step] = vx; all_vy[:, step] = vy

    return all_y, all_x, all_vx, all_vy


# ─── Fertility metrics ───

def novel_state_rate(all_y, window=50, step=25, n_bins=8):
    """Rate of visiting previously unseen coarse-grained states."""
    T = all_y.shape[1]
    seen = set()
    novel = 0; total = 0
    
    for t in range(0, T - window + 1, step):
        seg = all_y[:, t:t+window]
        # Coarse-grain: which quantile bin each grain occupies
        state = tuple(np.nanmean(seg, axis=1)[:15].round(0).astype(int))
        total += 1
        if state not in seen:
            seen.add(state)
            novel += 1
    return novel / max(total, 1)


def state_space_volume(all_y, window=50, step=25):
    """Approximate volume of explored state space (y-positions)."""
    T = all_y.shape[1]
    all_states = []
    for t in range(0, T - window + 1, step):
        seg = all_y[:, t:t+window]
        state = np.nanmean(seg, axis=1)[:15]
        all_states.append(state)
    
    if len(all_states) < 2:
        return 0.0
    
    states_arr = np.array(all_states)
    # Bounding box volume (product of ranges)
    ranges = np.nanmax(states_arr, axis=0) - np.nanmin(states_arr, axis=0)
    return float(np.prod(ranges[ranges > 0]))


def trajectory_divergence(all_y, n_pairs=50, lag=50):
    """How fast nearby grain trajectories diverge (Lyapunov-like)."""
    n_grains, T = all_y.shape
    rng = np.random.default_rng(42)
    
    divergences = []
    for _ in range(n_pairs):
        i, j = rng.choice(n_grains, 2, replace=False)
        # Initial distance
        d0 = np.abs(all_y[i, 0] - all_y[j, 0])
        if d0 < 0.1:
            continue
        # Distance at various lags
        for t0 in range(0, T - lag - 100, 100):
            d_lag = np.abs(all_y[i, t0+lag] - all_y[j, t0+lag])
            if d0 > 0:
                divergences.append(np.log(d_lag / d0) / (lag * 0.01))
    
    return float(np.mean(divergences)) if divergences else 0.0


def velocity_entropy(all_vx, all_vy, n_bins=20, window=100, step=50):
    """Shannon entropy of velocity distribution over time."""
    T = all_vx.shape[1]
    entropies = []
    
    for t in range(0, T - window + 1, step):
        vx = all_vx[:, t:t+window].flatten()
        vy = all_vy[:, t:t+window].flatten()
        vx = vx[~np.isnan(vx)]
        vy = vy[~np.isnan(vy)]
        if len(vx) < 10:
            continue
        
        # 2D histogram
        h, _, _ = np.histogram2d(vx, vy, bins=n_bins)
        h = h / h.sum()
        h = h[h > 0]
        entropies.append(-np.sum(h * np.log2(h)))
    
    return float(np.mean(entropies)) if entropies else 0.0


def configurational_richness(all_y, window=100, step=50):
    """Number of distinct local minima configurations."""
    T = all_y.shape[1]
    configs = []
    
    for t in range(0, T - window + 1, step):
        seg = all_y[:, t:t+window]
        # For each grain, find if it has a local minimum in y
        mean_y = np.nanmean(seg, axis=1)[:15]
        # Discretize
        config = tuple(np.round(mean_y / 2.0).astype(int))
        configs.append(config)
    
    # Count unique configs
    return len(set(configs)) / max(len(configs), 1)


def state_expansion_velocity(all_y, window=50, step=25):
    """Rate at which the explored y-volume grows."""
    T = all_y.shape[1]
    volumes = []
    times = []
    
    for t in range(0, T - window + 1, step):
        seg = all_y[:, t:t+window]
        y_range = np.nanmax(seg) - np.nanmin(seg)
        volumes.append(y_range)
        times.append(t)
    
    if len(volumes) < 3:
        return 0.0
    
    # Linear fit slope
    times = np.array(times)
    volumes = np.array(volumes)
    valid = ~np.isnan(volumes) & ~np.isinf(volumes)
    if np.sum(valid) < 3:
        return 0.0
    slope, _, _, _, _ = stats.linregress(times[valid], volumes[valid])
    return float(slope)


# ─── Main sweep ───
FRICTION_LEVELS = np.linspace(0.05, 0.80, 16)  # Match t901 range
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
        
        # Fertility metrics
        nsr = novel_state_rate(all_y)
        ssv = state_space_volume(all_y)
        td = trajectory_divergence(all_y)
        ve = velocity_entropy(all_vx, all_vy)
        cr = configurational_richness(all_y)
        sev = state_expansion_velocity(all_y)
        
        # Also compute C for validation
        final_x = np.nanmean(all_x[:, -100:], axis=1)
        order = np.argsort(final_x)
        bins = np.array_split(order, 10)
        X = np.array([np.nanmean(all_y[b], axis=0) for b in bins])
        try:
            c_val = compute_C(X[:, 200:500], "gaussian")
        except:
            c_val = np.nan
        
        # Jitter
        jitter = float(np.nanmean(np.sqrt(all_vx**2 + all_vy**2)))
        
        results.append({
            "friction": round(float(fr), 4), "rep": rep,
            "C": round(c_val, 4) if not np.isnan(c_val) else None,
            "jitter": round(jitter, 2),
            "novel_state_rate": round(nsr, 4),
            "state_space_vol": round(ssv, 1) if not np.isinf(ssv) else None,
            "traj_divergence": round(td, 4),
            "velocity_entropy": round(ve, 4),
            "config_richness": round(cr, 4),
            "expansion_velocity": round(sev, 4),
        })
        
        done += 1
        if done % 40 == 0:
            print(f"  [{done}/{total}] {time.time()-t0:.0f}s elapsed")

print(f"\nSweep: {done} runs in {time.time()-t0:.0f}s")

with open("audits/rd8b_fertility_sweep.json", "w") as f:
    json.dump(results, f, indent=2)

# ─── Summary ───
print("\n" + "=" * 120)
print("RD-8B: FERTILITY RECON — SWEEP RESULTS")
print("=" * 120)
print(f"\n{'μ':>6s} {'C':>7s} {'Jitter':>8s} {'NSR':>7s} {'SSV':>10s} {'TD':>8s} {'VE':>8s} {'CR':>7s} {'SEV':>8s}")
print("-" * 120)

for fr in FRICTION_LEVELS:
    sub = [r for r in results if abs(r["friction"] - fr) < 0.001]
    def ms(k):
        v = [r[k] for r in sub if r.get(k) is not None]
        return np.mean(v) if v else np.nan
    print(f"{fr:>6.3f} {ms('C'):>7.3f} {ms('jitter'):>8.2f} {ms('novel_state_rate'):>7.3f} "
          f"{ms('state_space_vol'):>10.1f} {ms('traj_divergence'):>8.4f} "
          f"{ms('velocity_entropy'):>8.3f} {ms('config_richness'):>7.3f} "
          f"{ms('expansion_velocity'):>8.4f}")

# ─── Correlation with existing metrics ───
print("\n" + "─" * 120)
print("FERTILITY METRIC CORRELATIONS")
print("─" * 120)

fert_keys = ["novel_state_rate", "state_space_vol", "traj_divergence",
             "velocity_entropy", "config_richness", "expansion_velocity"]
all_keys = ["C", "jitter"] + fert_keys

valid = [r for r in results if all(r.get(k) is not None for k in all_keys)]
if len(valid) > 10:
    M = np.array([[r[k] for k in all_keys] for r in valid])
    corr = np.corrcoef(M.T)
    header = "".join(f"{k[:8]:>10s}" for k in all_keys)
    print(f"{'':>18s}{header}")
    for i, k in enumerate(all_keys):
        row = "".join(f"{corr[i,j]:>10.3f}" for j in range(len(all_keys)))
        print(f"{k:>18s}{row}")
