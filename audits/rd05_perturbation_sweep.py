"""RD-5: Granular Perturbation Sweep
Sweep removal fractions: 0%, 5%, 10%, 20%, 30%, 50%.
10 reps per condition. Measure C_pre, C_min, ΔC, τ_rec (95%), C_final/C_pre, Overshoot.
"""

import sys, os, json, time
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "coherence-benchmark"))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from t901_analysis import _granular_run, _bin_data, _sliding_C
from metrics.total_correlation import compute_C

# ─── Config ───
REMOVAL_LEVELS = [0.0, 0.05, 0.10, 0.20, 0.30, 0.50]
N_REPS = 10
N_GRAINS = 50
N_STEPS = 1000
REMOVAL_STEP = 500
FRICTION = 0.30
BASE_SEED = 1000

# ─── Sweep ───
results = []
all_curves = {}  # {(fraction, rep): (times, c_vals)}

t0 = time.time()
total = len(REMOVAL_LEVELS) * N_REPS
done = 0

for frac in REMOVAL_LEVELS:
    for rep in range(N_REPS):
        seed = BASE_SEED + rep + int(frac * 1000)
        n_remove_actual = max(1, int(N_GRAINS * frac)) if frac > 0 else 0

        # Run simulation
        all_y, all_x, all_vx, all_vy, radii, removed = _granular_run(
            n_grains=N_GRAINS, n_steps=N_STEPS, removal_step=REMOVAL_STEP,
            removal_fraction=frac, friction=FRICTION, seed=seed,
        )

        # Bin and compute C
        X = _bin_data(all_y, all_x, n_bins=10)
        times, c_vals = _sliding_C(X, window=75, step=25)

        # Store curve
        all_curves[(frac, rep)] = (times.copy(), c_vals.copy())

        # ─── Measurements ───
        pre_mask = (times >= 100) & (times < REMOVAL_STEP)
        pert_mask = (times >= REMOVAL_STEP) & (times <= REMOVAL_STEP + 100)
        post_mask = (times >= REMOVAL_STEP + 100) & (times <= REMOVAL_STEP + 500)
        late_mask = (times >= REMOVAL_STEP + 500)

        C_pre = float(np.nanmean(c_vals[pre_mask])) if np.sum(pre_mask) >= 2 else np.nan
        C_min = float(np.nanmin(c_vals[pert_mask])) if np.sum(pert_mask) >= 2 else np.nan
        dC = C_min - C_pre if not (np.isnan(C_pre) or np.isnan(C_min)) else np.nan

        # τ_rec: first time C >= 0.95 * C_pre after perturbation
        tau_rec = np.nan
        post_times = times[post_mask]
        post_c = c_vals[post_mask]
        threshold = 0.95 * C_pre
        for k in range(len(post_c)):
            if not np.isnan(post_c[k]) and post_c[k] >= threshold:
                tau_rec = float(post_times[k] - REMOVAL_STEP)
                break

        # C_final: mean of last 10 post-perturbation points
        post_c_valid = post_c[~np.isnan(post_c)]
        C_final = float(np.nanmean(post_c_valid[-10:])) if len(post_c_valid) >= 3 else np.nan
        C_ratio = C_final / C_pre if (not np.isnan(C_final) and not np.isnan(C_pre) and C_pre > 0) else np.nan

        # Overshoot: peak C after recovery (first time C >= 0.95*C_pre) relative to C_pre
        overshoot = np.nan
        if not np.isnan(tau_rec):
            # Find peak after the recovery point
            recovery_idx = None
            for k in range(len(post_c)):
                if not np.isnan(post_c[k]) and post_c[k] >= threshold:
                    recovery_idx = k
                    break
            if recovery_idx is not None:
                peak_after = float(np.nanmax(post_c[recovery_idx:]))
                overshoot = (peak_after - C_pre) / C_pre if C_pre > 0 else np.nan

        results.append({
            "fraction": frac,
            "rep": rep,
            "n_removed": n_remove_actual,
            "C_pre": round(C_pre, 4),
            "C_min": round(C_min, 4),
            "dC": round(dC, 4),
            "tau_rec": round(tau_rec, 1) if not np.isnan(tau_rec) else None,
            "C_final": round(C_final, 4),
            "C_ratio": round(C_ratio, 4),
            "overshoot": round(overshoot, 4) if not np.isnan(overshoot) else None,
        })

        done += 1
        if done % 10 == 0:
            elapsed = time.time() - t0
            print(f"  [{done}/{total}] {elapsed:.0f}s elapsed")

elapsed = time.time() - t0
print(f"\nSweep complete: {done} runs in {elapsed:.0f}s")

# ─── Save raw results ───
with open("audits/rd05_sweep_raw.json", "w") as f:
    json.dump(results, f, indent=2)

# ─── Summary table (mean ± std per removal level) ───
print("\n" + "=" * 90)
print("RD-5: GRANULAR PERTURBATION SWEEP RESULTS")
print("=" * 90)

header = f"{'Removal%':>10s} {'C_pre':>10s} {'C_min':>10s} {'ΔC':>10s} {'τ_rec':>10s} {'C_fin/C_pre':>12s} {'Overshoot':>12s}"
print(header)
print("-" * 90)

summary = {}
for frac in REMOVAL_LEVELS:
    subset = [r for r in results if r["fraction"] == frac]
    def safe_mean(key):
        vals = [r[key] for r in subset if r[key] is not None]
        return np.mean(vals) if vals else np.nan
    def safe_std(key):
        vals = [r[key] for r in subset if r[key] is not None]
        return np.std(vals, ddof=1) if len(vals) > 1 else 0.0

    row = {
        "fraction": frac,
        "C_pre": (safe_mean("C_pre"), safe_std("C_pre")),
        "C_min": (safe_mean("C_min"), safe_std("C_min")),
        "dC": (safe_mean("dC"), safe_std("dC")),
        "tau_rec": (safe_mean("tau_rec"), safe_std("tau_rec")),
        "C_ratio": (safe_mean("C_ratio"), safe_std("C_ratio")),
        "overshoot": (safe_mean("overshoot"), safe_std("overshoot")),
    }
    summary[frac] = row

    pct = f"{frac*100:.0f}%"
    c_pre = f"{row['C_pre'][0]:.3f}±{row['C_pre'][1]:.3f}"
    c_min = f"{row['C_min'][0]:.3f}±{row['C_min'][1]:.3f}"
    dc = f"{row['dC'][0]:.3f}±{row['dC'][1]:.3f}"
    tau = f"{row['tau_rec'][0]:.1f}±{row['tau_rec'][1]:.1f}" if not np.isnan(row['tau_rec'][0]) else "null"
    cr = f"{row['C_ratio'][0]:.3f}±{row['C_ratio'][1]:.3f}" if not np.isnan(row['C_ratio'][0]) else "null"
    ov = f"{row['overshoot'][0]:.3f}±{row['overshoot'][1]:.3f}" if not np.isnan(row['overshoot'][0]) else "null"
    print(f"{pct:>10s} {c_pre:>10s} {c_min:>10s} {dc:>10s} {tau:>10s} {cr:>12s} {ov:>12s}")

# Save summary
with open("audits/rd05_summary.json", "w") as f:
    json.dump({str(k): {kk: (v[0], v[1]) for kk, v in vv.items() if kk != "fraction"}
               for k, vv in summary.items()}, f, indent=2, default=str)

print(f"\nRaw results: audits/rd05_sweep_raw.json")
print(f"Summary: audits/rd05_summary.json")
