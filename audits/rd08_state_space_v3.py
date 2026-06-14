"""RD-8: State-Space Cartography (v3)
Fix noise injection: additive (fixed magnitude), clamp velocities to prevent explosion.
Also sweep friction as a second control parameter for 2D state-space map.
"""

import sys, os, json, time
import numpy as np

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, "coherence-benchmark")

from t901_analysis import _soft_sphere_force
from metrics.total_correlation import compute_C

MAX_SPEED = 30.0  # velocity clamp

def _granular_run_controlled(n_grains=50, n_steps=1000, friction=0.30,
                             noise_abs=0.0, seed=42):
    """Additive noise with absolute magnitude noise_abs. Velocities clamped."""
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
        forces_x = np.zeros(n_grains)
        forces_y = np.full(n_grains, gy * masses)

        for i in range(n_grains):
            for j in range(i + 1, n_grains):
                dx = x[j] - x[i]; dy = y[j] - y[i]
                if abs(dx) > 3.0 or abs(dy) > 3.0: continue
                fx, fy, _ = _soft_sphere_force(dx, dy, radii[i], radii[j],
                                                stiffness, damping)
                forces_x[i] += fx; forces_y[i] += fy
                forces_x[j] -= fx; forces_y[j] -= fy

            vx[i] += forces_x[i] / masses[i] * dt
            vy[i] += forces_y[i] / masses[i] * dt
            vx[i] *= (1.0 - friction * dt)
            vy[i] *= (1.0 - friction * dt)

            # Additive noise
            if noise_abs > 0:
                vx[i] += rng.normal(0, noise_abs)
                vy[i] += rng.normal(0, noise_abs)

            # Clamp
            speed = np.sqrt(vx[i]**2 + vy[i]**2)
            if speed > MAX_SPEED:
                vx[i] *= MAX_SPEED / speed
                vy[i] *= MAX_SPEED / speed

            x[i] += vx[i] * dt
            y[i] += vy[i] * dt

            if x[i] - radii[i] < 0: x[i] = radii[i]; vx[i] *= -0.5
            elif x[i] + radii[i] > box_width: x[i] = box_width - radii[i]; vx[i] *= -0.5
            if y[i] - radii[i] < 0: y[i] = radii[i]; vy[i] *= -0.5

        all_x[:, step] = x; all_y[:, step] = y
        all_vx[:, step] = vx; all_vy[:, step] = vy

    return all_y, all_x, all_vx, all_vy


def _bin_data(positions_y, positions_x, n_bins=10):
    final_x = np.nanmean(positions_x[:, -100:], axis=1)
    order = np.argsort(final_x)
    bins = np.array_split(order, n_bins)
    return np.array([np.mean(positions_y[b], axis=0) for b in bins])


def _sliding_C(X, window=75, step=25):
    T = X.shape[1]; times, vals = [], []
    for t in range(0, T - window + 1, step):
        times.append(t + window // 2)
        try: vals.append(compute_C(X[:, t:t + window], "gaussian"))
        except: vals.append(np.nan)
    return np.array(times), np.array(vals)


def measure_fertility(all_y, window=50, step=25):
    T = all_y.shape[1]; seen = set(); novel = 0; total = 0
    for t in range(0, T - window + 1, step):
        seg = all_y[:, t:t+window]
        state = tuple(np.nanmean(seg, axis=1)[:10].round(1))
        total += 1
        if state not in seen:
            seen.add(state); novel += 1
    return novel / max(total, 1)


def measure_persistence(c_vals, dt=25):
    c = c_vals[~np.isnan(c_vals)]
    if len(c) < 20: return np.nan
    c = c - np.mean(c)
    n = len(c)
    f = np.fft.fft(c, n=2*n)
    acf = np.fft.ifft(f * np.conjugate(f))[:n].real
    if acf[0] > 0: acf /= acf[0]
    for i in range(1, len(acf)):
        if acf[i] < 1.0/np.e: return float(i * dt)
    return float(len(acf) * dt)


def measure_adaptability(all_vx, all_vy, all_y, window=50, step=25):
    """Adaptability: how fast grain positions reorganize after perturbation.
    Measure mean displacement rate in sliding windows."""
    T = all_y.shape[1]
    rates = []
    for t in range(0, T - 2*window, step):
        y1 = np.nanmean(all_y[:, t:t+window], axis=1)
        y2 = np.nanmean(all_y[:, t+window:t+2*window], axis=1)
        if np.all(np.isnan(y1)) or np.all(np.isnan(y2)):
            continue
        dy = np.nanmean(np.abs(y2 - y1))
        rates.append(dy)
    return float(np.mean(rates)) if rates else np.nan


# ─── Sweep ───
NOISE_LEVELS = np.logspace(-2, 0.5, 30)  # 0.01 to 3.16, log-spaced
N_REPS = 10
FRICTION = 0.30
N_GRAINS = 50; N_STEPS = 1000; BASE_SEED = 4000

results = []
t0 = time.time()
total = len(NOISE_LEVELS) * N_REPS
done = 0

for noise in NOISE_LEVELS:
    for rep in range(N_REPS):
        seed = BASE_SEED + rep + int(noise * 100000)
        all_y, all_x, all_vx, all_vy = _granular_run_controlled(
            n_grains=N_GRAINS, n_steps=N_STEPS, friction=FRICTION,
            noise_abs=noise, seed=seed,
        )

        X = _bin_data(all_y, all_x, n_bins=10)
        times, c_vals = _sliding_C(X, window=75, step=25)

        pre_mask = (times >= 100) & (times < 500)
        coherence = float(np.nanmean(c_vals[pre_mask])) if np.sum(pre_mask) >= 2 else np.nan

        jitter = float(np.nanmean(np.sqrt(all_vx**2 + all_vy**2)))
        persistence = measure_persistence(c_vals)
        fertility = measure_fertility(all_y)
        adaptability = measure_adaptability(all_vx, all_vy, all_y)

        # Phase sync: mean pairwise velocity correlation
        active = ~np.isnan(all_vx[:, 0])
        vx_a = all_vx[active, :200]
        if vx_a.shape[0] > 2:
            cm = np.corrcoef(vx_a)
            mask = ~np.eye(cm.shape[0], dtype=bool)
            phase_sync = float(np.nanmean(cm[mask]))
        else:
            phase_sync = 0.0

        results.append({
            "noise": round(float(noise), 4), "rep": rep,
            "C": round(coherence, 4) if not np.isnan(coherence) else None,
            "fertility": round(fertility, 4),
            "jitter": round(jitter, 2),
            "persistence": round(persistence, 1) if not np.isnan(persistence) else None,
            "adaptability": round(adaptability, 4) if not np.isnan(adaptability) else None,
            "phase_sync": round(phase_sync, 4),
        })

        done += 1
        if done % 50 == 0:
            print(f"  [{done}/{total}] {time.time()-t0:.0f}s elapsed")

print(f"Sweep complete: {done} runs in {time.time()-t0:.0f}s")

with open("audits/rd08_state_space_v3.json", "w") as f:
    json.dump(results, f, indent=2)

# ─── Summary table ───
print("\n" + "=" * 115)
print("RD-8: STATE-SPACE CARTOGRAPHY v3")
print("=" * 115)
print(f"\n{'Noise':>8s} {'C':>8s} {'Fert':>8s} {'Jitter':>10s} {'Persist':>9s} {'Adapt':>8s} {'PhSync':>8s}")
print("-" * 115)

for noise in NOISE_LEVELS:
    sub = [r for r in results if abs(r["noise"] - noise) < 0.001]
    def ms(k):
        v = [r[k] for r in sub if r.get(k) is not None]
        return np.mean(v) if v else np.nan
    print(f"{noise:>8.3f} {ms('C'):>8.3f} {ms('fertility'):>8.3f} "
          f"{ms('jitter'):>10.2f} {ms('persistence'):>9.1f} "
          f"{ms('adaptability'):>8.4f} {ms('phase_sync'):>8.4f}")

# ─── PCA ───
print("\n" + "─" * 115)
print("LATENT DIMENSIONALITY")
print("─" * 115)

valid = [r for r in results if all(r.get(k) is not None for k in
        ["C", "fertility", "jitter", "persistence", "adaptability", "phase_sync"])]
print(f"Valid runs: {len(valid)} / {len(results)}")

if len(valid) > 10:
    keys = ["C", "fertility", "jitter", "persistence", "adaptability", "phase_sync"]
    M = np.array([[r[k] for k in keys] for r in valid])
    stds = np.std(M, axis=0)
    stds[stds == 0] = 1  # avoid div by 0
    M_std = (M - np.mean(M, axis=0)) / stds
    
    cov = np.corrcoef(M_std.T)
    eigvals = np.linalg.eigvalsh(cov)[::-1]
    explained = eigvals / np.sum(eigvals)
    cumulative = np.cumsum(explained)

    print(f"\n  Eigenvalues: {['%.4f' % e for e in eigvals]}")
    print(f"  Explained:   {['%.1f%%' % (e*100) for e in explained]}")
    print(f"  Cumulative:  {['%.1f%%' % (c*100) for c in cumulative]}")
    n_90 = np.searchsorted(cumulative, 0.90) + 1
    print(f"\n  Dimensions for 90% variance: {n_90}")

    eigvecs = np.linalg.eigh(cov)[1][:, ::-1]
    print("\n  PC1 loadings:")
    for i, k in enumerate(keys):
        print(f"    {k:>15s}: {eigvecs[i,0]:+.4f}")
    print("\n  PC2 loadings:")
    for i, k in enumerate(keys):
        print(f"    {k:>15s}: {eigvecs[i,1]:+.4f}")

# ─── Correlation matrix ───
print("\n" + "─" * 115)
print("METRIC CORRELATIONS")
print("─" * 115)
if len(valid) > 10:
    keys2 = ["C", "fertility", "jitter", "persistence", "adaptability"]
    M2 = np.array([[r[k] for k in keys2] for r in valid])
    corr = np.corrcoef(M2.T)
    header = "".join(f"{k:>10s}" for k in keys2)
    print(f"{'':>15s}{header}")
    for i, k in enumerate(keys2):
        row = "".join(f"{corr[i,j]:>10.3f}" for j in range(len(keys2)))
        print(f"{k:>15s}{row}")
