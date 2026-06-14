"""RD-8: State-Space Cartography
Sweep noise levels, measure 5 state variables, identify regimes, map state space.

Operational Definitions:
- Coherence (C): Total correlation of binned y-positions (existing)
- Fertility: Rate of distinct state discovery (unique bin configurations per unit time)
- Jitter: RMS velocity of grains (mean kinetic energy proxy)
- Persistence: Autocorrelation time of C(t) (how long structure lasts)
- Adaptability: Speed of C recovery after perturbation (inverse τ_rec)
"""

import sys, os, json, time
import numpy as np
from scipy import stats, signal

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, "coherence-benchmark")

from t901_analysis import _soft_sphere_force
from metrics.total_correlation import compute_C

# ─── Modified granular run with explicit noise injection ───
def _granular_run_noisy(
    n_grains=50, n_steps=1000, removal_step=500, removal_fraction=0.0,
    friction=0.3, noise_amplitude=0.0, seed=42,
):
    """Granular run with per-step velocity noise injection.
    
    noise_amplitude: std of Gaussian noise added to velocities each step.
    """
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
        if step == removal_step and removal_fraction > 0:
            n_remove = max(1, int(n_grains * removal_fraction))
            remove_idx = rng.choice(np.where(~removed)[0], size=n_remove, replace=False)
            removed[remove_idx] = True

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

            # Inject noise
            if noise_amplitude > 0:
                vx[i] += rng.normal(0, noise_amplitude)
                vy[i] += rng.normal(0, noise_amplitude)

            x[i] += vx[i] * dt
            y[i] += vy[i] * dt

            if x[i] - radii[i] < 0: x[i] = radii[i]; vx[i] *= -0.5
            elif x[i] + radii[i] > box_width: x[i] = box_width - radii[i]; vx[i] *= -0.5
            if y[i] - radii[i] < 0: y[i] = radii[i]; vy[i] *= -0.5

        all_x[:, step] = np.where(removed, np.nan, x)
        all_y[:, step] = np.where(removed, np.nan, y)
        all_vx[:, step] = np.where(removed, np.nan, vx)
        all_vy[:, step] = np.where(removed, np.nan, vy)

    return all_y, all_x, all_vx, all_vy, radii, removed


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


# ─── State variable measurements ───

def measure_fertility(all_y, all_x, window=50, step=25, n_bins=10):
    """Fertility: rate of distinct state discovery.
    
    Discretize the binned state into a hash, count unique hashes over time.
    Fertility = unique states discovered per unit time.
    """
    T = all_y.shape[1]
    seen_states = set()
    count = 0
    for t in range(0, T - window + 1, step):
        seg_y = all_y[:, t:t+window]
        seg_x = all_x[:, t:t+window]
        X = _bin_data(seg_y, seg_x, n_bins)
        # Discretize to 3-level quantile
        state_hash = tuple(np.digitize(X.mean(axis=1), bins=[0.33, 0.66]))
        if state_hash not in seen_states:
            seen_states.add(state_hash)
            count += 1
    total_windows = len(range(0, T - window + 1, step))
    return count / max(total_windows, 1)  # fraction of windows with new states


def measure_jitter(all_vx, all_vy, removed):
    """Jitter: mean RMS velocity across active grains (time-averaged)."""
    active_vx = np.where(removed[:, None], np.nan, all_vx)
    active_vy = np.where(removed[:, None], np.nan, all_vy)
    speed = np.sqrt(active_vx**2 + active_vy**2)
    return float(np.nanmean(speed))


def measure_persistence(c_vals, dt=25):
    """Persistence: autocorrelation time of C(t).
    
    Time for autocorrelation to decay to 1/e.
    """
    c_clean = c_vals[~np.isnan(c_vals)]
    if len(c_clean) < 20:
        return np.nan
    # Remove mean
    c_centered = c_clean - np.mean(c_clean)
    # Autocorrelation via FFT
    n = len(c_centered)
    f = np.fft.fft(c_centered, n=2*n)
    acf = np.fft.ifft(f * np.conjugate(f))[:n].real
    acf = acf / acf[0] if acf[0] > 0 else acf
    # Find 1/e crossing
    threshold = 1.0 / np.e
    for i in range(1, len(acf)):
        if acf[i] < threshold:
            return float(i * dt)
    return float(len(acf) * dt)  # never decays


def measure_adaptability(c_vals, times, pert_step=500):
    """Adaptability: speed of C recovery after perturbation.
    
    Inverse of τ_rec (time to return to 95% of pre-perturbation C).
    Higher = more adaptable.
    """
    pre_mask = (times >= 100) & (times < pert_step)
    post_mask = times > pert_step
    
    if np.sum(pre_mask) < 2 or np.sum(post_mask) < 2:
        return np.nan, np.nan
    
    C_pre = np.mean(c_vals[pre_mask])
    threshold = 0.95 * C_pre
    
    post_times = times[post_mask]
    post_c = c_vals[post_mask]
    
    tau_rec = np.nan
    for k in range(len(post_c)):
        if not np.isnan(post_c[k]) and post_c[k] >= threshold:
            tau_rec = float(post_times[k] - pert_step)
            break
    
    if np.isnan(tau_rec) or tau_rec <= 0:
        return 0.0, tau_rec  # no recovery or instant recovery
    
    return 1.0 / tau_rec, tau_rec  # adaptability = inverse recovery time


# ─── Sweep ───
NOISE_LEVELS = np.linspace(0.0, 0.5, 20)  # 0 to 0.5
N_REPS = 10
FRICTION = 0.30
N_GRAINS = 50
N_STEPS = 1000
BASE_SEED = 3000

results = []
t0 = time.time()
total = len(NOISE_LEVELS) * N_REPS
done = 0

for noise in NOISE_LEVELS:
    for rep in range(N_REPS):
        seed = BASE_SEED + rep + int(noise * 10000)
        
        all_y, all_x, all_vx, all_vy, radii, removed = _granular_run_noisy(
            n_grains=N_GRAINS, n_steps=N_STEPS, removal_step=500,
            removal_fraction=0.0, friction=FRICTION, noise_amplitude=noise, seed=seed,
        )
        
        X = _bin_data(all_y, all_x, n_bins=10)
        times, c_vals = _sliding_C(X, window=75, step=25)
        
        # State variables
        coherence = float(np.nanmean(c_vals[(times >= 100) & (times < 500)]))
        fertility = measure_fertility(all_y, all_x)
        jitter = measure_jitter(all_vx, all_vy, removed)
        persistence = measure_persistence(c_vals)
        adaptability, tau_rec = measure_adaptability(c_vals, times, pert_step=500)
        
        # Additional diagnostics
        speed_std = float(np.nanstd(np.sqrt(all_vx**2 + all_vy**2)))
        y_range = float(np.nanmean(np.nanmax(all_y, axis=0) - np.nanmin(all_y, axis=0)))
        
        results.append({
            "noise": round(float(noise), 4),
            "rep": rep,
            "C": round(coherence, 4),
            "fertility": round(fertility, 4),
            "jitter": round(jitter, 4),
            "persistence": round(persistence, 1) if not np.isnan(persistence) else None,
            "adaptability": round(adaptability, 4) if not np.isnan(adaptability) else None,
            "tau_rec": round(tau_rec, 1) if not np.isnan(tau_rec) else None,
            "speed_std": round(speed_std, 4),
            "y_range": round(y_range, 4),
        })
        
        done += 1
        if done % 50 == 0:
            elapsed = time.time() - t0
            print(f"  [{done}/{total}] {elapsed:.0f}s elapsed")

elapsed = time.time() - t0
print(f"\nSweep complete: {done} runs in {elapsed:.0f}s")

# Save raw
with open("audits/rd08_state_space_raw.json", "w") as f:
    json.dump(results, f, indent=2)

# ─── Summary by noise level ───
print("\n" + "=" * 100)
print("RD-8: STATE-SPACE CARTOGRAPHY — NOISE SWEEP")
print("=" * 100)

print(f"\n{'Noise':>8s} {'C':>8s} {'Fertility':>10s} {'Jitter':>8s} {'Persist':>8s} {'Adapt':>8s} {'SpeedStd':>10s} {'Y_range':>8s}")
print("-" * 100)

for noise in NOISE_LEVELS:
    subset = [r for r in results if abs(r["noise"] - noise) < 0.001]
    def ms(key):
        vals = [r[key] for r in subset if r.get(key) is not None]
        return (np.mean(vals), np.std(vals)) if vals else (np.nan, 0)
    
    c_m, c_s = ms("C")
    f_m, f_s = ms("fertility")
    j_m, j_s = ms("jitter")
    p_m, p_s = ms("persistence")
    a_m, a_s = ms("adaptability")
    s_m, s_s = ms("speed_std")
    y_m, y_s = ms("y_range")
    
    print(f"{noise:>8.3f} {c_m:>7.3f} {f_m:>10.3f} {j_m:>8.3f} {p_m:>8.1f} {a_m:>8.4f} {s_m:>10.3f} {y_m:>8.3f}")

print(f"\nRaw data: audits/rd08_state_space_raw.json")
