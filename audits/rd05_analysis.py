"""RD-5 Analysis: Re-measure with fine-grained windows, generate curves and table."""

import sys, os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, "coherence-benchmark")

from t901_analysis import _granular_run, _bin_data, _sliding_C

# ─── Re-run sweep with fine-grained C measurement ───
REMOVAL_LEVELS = [0.0, 0.05, 0.10, 0.20, 0.30, 0.50]
N_REPS = 10
N_GRAINS = 50
N_STEPS = 1000
REMOVAL_STEP = 500
FRICTION = 0.30
BASE_SEED = 1000

# Store all curves for plotting
all_curves = {}  # {(frac, rep): (times, c_vals)}

for frac in REMOVAL_LEVELS:
    for rep in range(N_REPS):
        seed = BASE_SEED + rep + int(frac * 1000)
        all_y, all_x, _, _, _, _ = _granular_run(
            n_grains=N_GRAINS, n_steps=N_STEPS, removal_step=REMOVAL_STEP,
            removal_fraction=frac, friction=FRICTION, seed=seed,
        )
        X = _bin_data(all_y, all_x, n_bins=10)
        # Fine-grained C: window=50, step=10 for better time resolution
        times, c_vals = _sliding_C(X, window=50, step=10)
        all_curves[(frac, rep)] = (times.copy(), c_vals.copy())

print("Curves computed. Generating analysis...")

# ─── Re-measure with fine-grained data ───
results = []
for frac in REMOVAL_LEVELS:
    for rep in range(N_REPS):
        times, c_vals = all_curves[(frac, rep)]

        # Pre-perturbation: steps 100-490
        pre_mask = (times >= 100) & (times < REMOVAL_STEP)
        C_pre = float(np.nanmean(c_vals[pre_mask]))

        # Perturbation response: steps 500-550 (immediate post-removal)
        pert_mask = (times >= REMOVAL_STEP) & (times <= REMOVAL_STEP + 50)
        C_min = float(np.nanmin(c_vals[pert_mask])) if np.sum(pert_mask) >= 1 else np.nan
        dC = C_min - C_pre

        # Broader perturbation window: 500-600
        pert_broad_mask = (times >= REMOVAL_STEP) & (times <= REMOVAL_STEP + 100)
        C_min_broad = float(np.nanmin(c_vals[pert_broad_mask])) if np.sum(pert_broad_mask) >= 1 else np.nan

        # τ_rec: first time C >= 0.95 * C_pre after perturbation (steps 500+)
        post_mask = times > REMOVAL_STEP
        post_times = times[post_mask]
        post_c = c_vals[post_mask]
        threshold = 0.95 * C_pre

        tau_rec = np.nan
        for k in range(len(post_c)):
            if not np.isnan(post_c[k]) and post_c[k] >= threshold:
                tau_rec = float(post_times[k] - REMOVAL_STEP)
                break

        # C_final: mean of last 50 steps
        late_mask = times >= (N_STEPS - 100)
        C_final = float(np.nanmean(c_vals[late_mask])) if np.sum(late_mask) >= 3 else np.nan
        C_ratio = C_final / C_pre if C_pre > 0 else np.nan

        # Overshoot: peak C after first crossing of 0.95*C_pre
        overshoot = np.nan
        if not np.isnan(tau_rec):
            recovery_idx = None
            for k in range(len(post_c)):
                if not np.isnan(post_c[k]) and post_c[k] >= threshold:
                    recovery_idx = k
                    break
            if recovery_idx is not None:
                peak_after = float(np.nanmax(post_c[recovery_idx:]))
                overshoot = (peak_after - C_pre) / C_pre

        results.append({
            "fraction": frac, "rep": rep,
            "C_pre": round(C_pre, 4), "C_min": round(C_min, 4),
            "dC": round(dC, 4), "C_min_broad": round(C_min_broad, 4),
            "tau_rec": round(tau_rec, 1) if not np.isnan(tau_rec) else None,
            "C_final": round(C_final, 4), "C_ratio": round(C_ratio, 4),
            "overshoot": round(overshoot, 4) if not np.isnan(overshoot) else None,
        })

# ─── Summary table ───
print("\n" + "=" * 95)
print("RD-5: GRANULAR PERTURBATION SWEEP — FINE-GRAINED MEASUREMENTS")
print("=" * 95)
print(f"{'Removal%':>10s} {'C_pre':>10s} {'C_min':>10s} {'ΔC':>10s} {'τ_rec':>10s} {'C_fin/C_pre':>12s} {'Overshoot':>12s}")
print("-" * 95)

summary = {}
for frac in REMOVAL_LEVELS:
    subset = [r for r in results if r["fraction"] == frac]
    # Exclude collapses (C_final=0) for means
    valid = [r for r in subset if r["C_final"] is not None and r["C_final"] > 0]

    def mean_std(key, data=valid):
        vals = [r[key] for r in data if r[key] is not None]
        if not vals:
            return (np.nan, 0.0)
        return (np.mean(vals), np.std(vals, ddof=1) if len(vals) > 1 else 0.0)

    row = {k: mean_std(k) for k in ["C_pre", "C_min", "dC", "tau_rec", "C_ratio", "overshoot"]}
    summary[frac] = row
    n_collapse = len(subset) - len(valid)

    pct = f"{frac*100:.0f}%"
    cp = f"{row['C_pre'][0]:.3f}±{row['C_pre'][1]:.3f}"
    cm = f"{row['C_min'][0]:.3f}±{row['C_min'][1]:.3f}"
    dc = f"{row['dC'][0]:.3f}±{row['dC'][1]:.3f}"
    tr = f"{row['tau_rec'][0]:.0f}±{row['tau_rec'][1]:.0f}" if not np.isnan(row['tau_rec'][0]) else "FAIL"
    cr = f"{row['C_ratio'][0]:.3f}±{row['C_ratio'][1]:.3f}" if not np.isnan(row['C_ratio'][0]) else "FAIL"
    ov = f"{row['overshoot'][0]:.3f}±{row['overshoot'][1]:.3f}" if not np.isnan(row['overshoot'][0]) else "FAIL"
    collapse_note = f"  [{n_collapse} collapsed]" if n_collapse > 0 else ""
    print(f"{pct:>10s} {cp:>10s} {cm:>10s} {dc:>10s} {tr:>10s} {cr:>12s} {ov:>12s}{collapse_note}")

# ─── Recovery curves figure ───
fig, axes = plt.subplots(2, 3, figsize=(15, 9), sharey=True)
axes = axes.flatten()

colors = plt.cm.viridis(np.linspace(0.1, 0.9, N_REPS))

for idx, frac in enumerate(REMOVAL_LEVELS):
    ax = axes[idx]
    for rep in range(N_REPS):
        times, c_vals = all_curves[(frac, rep)]
        ax.plot(times, c_vals, color=colors[rep], alpha=0.6, linewidth=0.8)

    # Mark perturbation
    ax.axvline(REMOVAL_STEP, color="red", linestyle="--", alpha=0.5, label="Perturbation")
    # Mark 95% threshold for the first rep
    times0, c_vals0 = all_curves[(frac, 0)]
    C_pre_0 = float(np.nanmean(c_vals0[(times0 >= 100) & (times0 < REMOVAL_STEP)]))
    ax.axhline(0.95 * C_pre_0, color="gray", linestyle=":", alpha=0.4)

    ax.set_title(f"Removal: {frac*100:.0f}%", fontsize=11, fontweight="bold")
    ax.set_xlabel("Step")
    if idx % 3 == 0:
        ax.set_ylabel("C(t)")
    ax.set_xlim(0, N_STEPS)
    ax.set_ylim(0, 1.0)
    ax.grid(True, alpha=0.3)

axes[0].legend(fontsize=8, loc="lower right")
fig.suptitle("RD-5: Recovery Curves — All Removal Fractions", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("audits/rd05_recovery_curves.png", dpi=150, bbox_inches="tight")
print(f"\nFigure saved: audits/rd05_recovery_curves.png")

# ─── ΔC vs removal fraction ───
fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

fracs = []
dc_means = []
dc_stds = []
tau_means = []
tau_stds = []
ov_means = []
ov_stds = []
collapse_fractions = []

for frac in REMOVAL_LEVELS:
    subset = [r for r in results if r["fraction"] == frac]
    valid = [r for r in subset if r["C_final"] is not None and r["C_final"] > 0]
    fracs.append(frac * 100)

    dc_vals = [r["dC"] for r in valid]
    dc_means.append(np.mean(dc_vals) if dc_vals else 0)
    dc_stds.append(np.std(dc_vals, ddof=1) if len(dc_vals) > 1 else 0)

    tau_vals = [r["tau_rec"] for r in valid if r["tau_rec"] is not None]
    tau_means.append(np.mean(tau_vals) if tau_vals else 0)
    tau_stds.append(np.std(tau_vals, ddof=1) if len(tau_vals) > 1 else 0)

    ov_vals = [r["overshoot"] for r in valid if r["overshoot"] is not None]
    ov_means.append(np.mean(ov_vals) if ov_vals else 0)
    ov_stds.append(np.std(ov_vals, ddof=1) if len(ov_vals) > 1 else 0)

    collapse_fractions.append((len(subset) - len(valid)) / len(subset))

ax1.errorbar(fracs, dc_means, yerr=dc_stds, fmt="o-", color="steelblue", capsize=4, label="ΔC")
ax1.set_xlabel("Removal %")
ax1.set_ylabel("ΔC (C_min − C_pre)")
ax1.set_title("Perturbation Magnitude vs ΔC")
ax1.grid(True, alpha=0.3)
ax1.axhline(0, color="gray", linestyle=":", alpha=0.5)

ax2.errorbar(fracs, ov_means, yerr=ov_stds, fmt="s-", color="coral", capsize=4, label="Overshoot")
ax2.set_xlabel("Removal %")
ax2.set_ylabel("Overshoot (peak − C_pre) / C_pre")
ax2.set_title("Perturbation Magnitude vs Overshoot")
ax2.grid(True, alpha=0.3)

# Add collapse fraction on secondary axis
ax2b = ax2.twinx()
ax2b.bar(fracs, collapse_fractions, width=3, alpha=0.2, color="red", label="Collapse rate")
ax2b.set_ylabel("Collapse fraction", color="red")
ax2b.set_ylim(0, 1)
ax2b.tick_params(axis="y", labelcolor="red")

fig2.suptitle("RD-5: Perturbation Response Scaling", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("audits/rd05_scaling.png", dpi=150, bbox_inches="tight")
print(f"Figure saved: audits/rd05_scaling.png")

# Save results
with open("audits/rd05_fine_results.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"Results saved: audits/rd05_fine_results.json")
