"""RD-022: Measurement Audit of C.

Re-runs the canonical 60-run ensemble with stored seeds, caches the binned
time series, then computes C using 8 estimator variants.

Variants:
  E0 - baseline:             n_bins=10, window=75, step=25
  E1 - half window:          window=37
  E2 - double window:        window=150
  E3 - half bins:            n_bins=5
  E4 - double bins:          n_bins=20
  E5 - shifted bin edges:    n_bins=10 with half-bin shift
  E6 - bootstrap C:          resample timepoints, average 50 C values
  E7 - leave-one-bin-out:    mean C across 10 leave-out computations

For each variant, we compute pre_C, dip, restoration, tau_rec (sliding-C +
recovery pipeline) and then Residual(C) (within friction level).

Output: audits/RD022_master_table.json
"""

import json
import sys
import time
import numpy as np
from scipy import stats

sys.path.insert(0, "coherence-benchmark")
from t901_analysis import _granular_run, measure_recovery  # noqa
from metrics import compute_C  # noqa

SEP = "=" * 78
FRICTION_LEVELS = [0.05, 0.1, 0.2, 0.4, 0.6, 0.8]
N_REPS = 10
N_GRAINS = 50
N_STEPS = 1000
REMOVAL_STEP = 500
REMOVAL_FRACTION = 0.1
BASELINE_N_BINS = 10
BASELINE_WINDOW = 75
BASELINE_STEP = 25
PERT_START = 500

VARIANT_SPECS = {
    "E0": {"n_bins": 10, "window": 75, "step": 25, "bin_shift": 0.0, "kind": "baseline"},
    "E1": {"n_bins": 10, "window": 37, "step": 25, "bin_shift": 0.0, "kind": "half_window"},
    "E2": {"n_bins": 10, "window": 150, "step": 25, "bin_shift": 0.0, "kind": "double_window"},
    "E3": {"n_bins": 5,  "window": 75, "step": 25, "bin_shift": 0.0, "kind": "half_bins"},
    "E4": {"n_bins": 20, "window": 75, "step": 25, "bin_shift": 0.0, "kind": "double_bins"},
    "E5": {"n_bins": 10, "window": 75, "step": 25, "bin_shift": 0.5, "kind": "shifted_bins"},
    "E6": {"n_bins": 10, "window": 75, "step": 25, "bin_shift": 0.0, "kind": "bootstrap"},
    "E7": {"n_bins": 10, "window": 75, "step": 25, "bin_shift": 0.0, "kind": "leave_one_out"},
}


# ─── Binning ───

def bin_data(positions_y, positions_x, n_bins=BASELINE_N_BINS, bin_shift=0.0):
    """Binning with optional half-bin shift.

    Baseline uses argsort by final x-position and equal-split into n_bins.
    With bin_shift=0.5, we offset the split point by half a bin width.
    """
    nan_mask = np.isnan(positions_y)
    col_means = np.nanmean(positions_y, axis=1, keepdims=True)
    positions_y = np.where(nan_mask, col_means, positions_y)
    with np.errstate(invalid="ignore"):
        final_x = np.nanmean(positions_x[:, -100:], axis=1)
    final_x = np.where(np.isnan(final_x), np.nanmean(positions_x[:, :500], axis=1), final_x)
    order = np.argsort(final_x)
    n = len(order)
    bin_size = n / n_bins
    offset = int(round(bin_shift * bin_size)) % n
    if offset == 0:
        bins = np.array_split(order, n_bins)
    else:
        rolled = np.roll(order, -offset)
        bins = np.array_split(rolled, n_bins)
    return np.array([np.mean(positions_y[b], axis=0) for b in bins])


# ─── Sliding C with bootstrap and leave-one-bin-out ───

def sliding_C_baseline(X, window, step, pert_start=PERT_START):
    """Standard sliding-C pipeline returning (times, cvals)."""
    T = X.shape[1]
    times, vals = [], []
    for t in range(0, T - window + 1, step):
        seg = X[:, t:t + window]
        times.append(t + window // 2)
        try:
            vals.append(compute_C(seg, "gaussian"))
        except Exception:
            vals.append(np.nan)
    return np.array(times), np.array(vals)


def sliding_C_bootstrap(X, window, step, n_boot=50, seed=42):
    """Bootstrap C: at each window, resample timepoints with replacement,
    compute C, average across n_boot bootstrap samples."""
    T = X.shape[1]
    times, vals = [], []
    rng = np.random.default_rng(seed)
    for t in range(0, T - window + 1, step):
        seg = X[:, t:t + window]
        times.append(t + window // 2)
        boot_vals = []
        for _ in range(n_boot):
            idx = rng.integers(0, window, size=window)
            sample = seg[:, idx]
            try:
                boot_vals.append(compute_C(sample, "gaussian"))
            except Exception:
                boot_vals.append(np.nan)
        vals.append(np.nanmean(boot_vals))
    return np.array(times), np.array(vals)


def sliding_C_loo(X, window, step):
    """Leave-one-bin-out C: at each window, compute C n_bins times, each
    time leaving out one bin, then average. Returns (times, cvals)."""
    T = X.shape[1]
    n_bins = X.shape[0]
    times, vals = [], []
    for t in range(0, T - window + 1, step):
        seg = X[:, t:t + window]
        times.append(t + window // 2)
        loo_vals = []
        for i in range(n_bins):
            keep = [j for j in range(n_bins) if j != i]
            try:
                loo_vals.append(compute_C(seg[keep, :], "gaussian"))
            except Exception:
                loo_vals.append(np.nan)
        vals.append(np.nanmean(loo_vals))
    return np.array(times), np.array(vals)


# ─── Recovery measurement (re-use t901_analysis implementation) ───

# measure_recovery imported from t901_analysis above


# ─── Apply a single variant to one (cached) binned matrix ───

def apply_variant(spec, binned):
    """Apply one estimator variant to a binned time series.
    Returns pre_C, dip, restoration, tau_rec, plus raw cvals."""
    n_bins, win, step = spec["n_bins"], spec["window"], spec["step"]
    shift = spec["bin_shift"]
    kind = spec["kind"]

    # Re-bin if this variant uses a different n_bins or shift
    if n_bins != BASELINE_N_BINS or shift != 0.0:
        # Need raw positions. The binned matrix doesn't store them.
        # We'll re-bin in the calling code before calling apply_variant.
        # Here we just assume binned is already correct.
        pass

    if kind == "bootstrap":
        times, cvals = sliding_C_bootstrap(binned, win, step, n_boot=50)
    elif kind == "leave_one_out":
        times, cvals = sliding_C_loo(binned, win, step)
    else:
        times, cvals = sliding_C_baseline(binned, win, step)

    rec = measure_recovery(times, cvals, pert_start=PERT_START)
    return {
        "pre_C": rec["pre_C"],
        "dip": rec["dip"],
        "restoration": rec["restoration"],
        "tau_rec": rec["tau_rec"],
        "cvals": cvals,
        "times": times,
    }


# ─── Residuals (within-friction) ───

def compute_residuals(master, variant_key):
    """Add Residual(C) within friction level for given variant."""
    c_vals = np.array([r[variant_key]["pre_C"] for r in master])
    for f in FRICTION_LEVELS:
        idx = [i for i, r in enumerate(master) if r["friction"] == f]
        level_mean = np.nanmean(c_vals[idx])
        for i in idx:
            master[i][variant_key]["res_C"] = c_vals[i] - level_mean
    return master


# ─── Main ───

def main():
    t_start = time.time()
    print(SEP)
    print("  RD-022: MEASUREMENT AUDIT OF C")
    print(SEP)
    print(f"\n  Baseline: n_bins={BASELINE_N_BINS}, window={BASELINE_WINDOW}, step={BASELINE_STEP}")
    print(f"  Perturbation at step {REMOVAL_STEP}")
    print(f"  6 friction × 10 reps = 60 runs")
    print(f"  8 estimator variants per run")
    print(f"  Total C estimates: 60 × 8 = 480\n")

    # ─── Stage 1: Re-run granular sim, cache binned data for all 5 bin configs ───
    print(SEP)
    print("  STAGE 1: Re-run granular simulations, cache binned time series")
    print(SEP)

    # We need to cache binned data for: 5 bins, 10 bins (no shift), 10 bins (shifted), 20 bins
    binned_cache = {}  # key: (friction, rep, n_bins, shift) -> np.array

    run_count = 0
    t0 = time.time()
    for fi, friction in enumerate(FRICTION_LEVELS):
        for rep in range(N_REPS):
            seed = rep + 100 * fi  # matches t901_analysis.generate_ensemble
            y, x, vx, vy, radii, removed = _granular_run(
                n_grains=N_GRAINS, n_steps=N_STEPS,
                removal_step=REMOVAL_STEP, removal_fraction=REMOVAL_FRACTION,
                friction=friction, seed=seed,
            )
            # Cache binned for all 4 (n_bins, shift) combinations we need
            for nb, sh in [(5, 0.0), (10, 0.0), (10, 0.5), (20, 0.0)]:
                binned_cache[(friction, rep, nb, sh)] = bin_data(y, x, n_bins=nb, bin_shift=sh)
            run_count += 1
            if run_count % 10 == 0:
                print(f"    {run_count}/60 runs cached (t={time.time()-t0:.0f}s)")

    print(f"\n  Cached binned data for {run_count} runs × 4 bin configs ({time.time()-t0:.0f}s)")

    # ─── Stage 2: Apply all 8 variants ───
    print(f"\n{SEP}")
    print("  STAGE 2: Apply 8 estimator variants")
    print(SEP)

    master = []
    t0 = time.time()
    for fi, friction in enumerate(FRICTION_LEVELS):
        for rep in range(N_REPS):
            row = {
                "friction": friction, "rep": rep, "seed": rep + 100 * fi,
            }
            for vkey, spec in VARIANT_SPECS.items():
                nb, sh = spec["n_bins"], spec["bin_shift"]
                binned = binned_cache[(friction, rep, nb, sh)]
                res = apply_variant(spec, binned)
                row[vkey] = res
            master.append(row)
        print(f"  friction {friction:.2f}: 10 reps done ({time.time()-t0:.0f}s)")

    # ─── Stage 3: Residuals ───
    print(f"\n{SEP}")
    print("  STAGE 3: Compute Residual(C) for each variant")
    print(SEP)
    for vkey in VARIANT_SPECS.keys():
        master = compute_residuals(master, vkey)
    print(f"  Residuals added for all 8 variants")

    # ─── Save master table (without cvals/times for size) ───
    print(f"\n{SEP}")
    print("  STAGE 4: Save master table")
    print(SEP)
    out = []
    for r in master:
        flat = {
            "friction": r["friction"],
            "rep": r["rep"],
            "seed": r["seed"],
        }
        for vkey in VARIANT_SPECS.keys():
            flat[f"{vkey}_pre_C"] = r[vkey]["pre_C"]
            flat[f"{vkey}_dip"] = r[vkey]["dip"]
            flat[f"{vkey}_restoration"] = r[vkey]["restoration"]
            flat[f"{vkey}_tau_rec"] = r[vkey]["tau_rec"]
            flat[f"{vkey}_res_C"] = r[vkey]["res_C"]
            flat[f"{vkey}_cvals_mean"] = float(np.nanmean(r[vkey]["cvals"]))
            flat[f"{vkey}_cvals_std"] = float(np.nanstd(r[vkey]["cvals"]))
            flat[f"{vkey}_cvals_n"] = int(np.sum(~np.isnan(r[vkey]["cvals"])))
        out.append(flat)

    out_path = "audits/RD022_master_table.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"  Wrote {out_path} ({len(out)} rows × {len(out[0])} fields)")

    # Quick summary
    print(f"\n{SEP}")
    print("  QUICK SUMMARY: pre_C per variant (mean ± sd across 60 runs)")
    print(SEP)
    print(f"  {'Variant':<8s}  {'mean(C)':>8s}  {'sd(C)':>8s}  {'mean(res_C)':>11s}  {'sd(res_C)':>9s}")
    for vkey in VARIANT_SPECS.keys():
        c = np.array([r[f"{vkey}_pre_C"] for r in out])
        r = np.array([r[f"{vkey}_res_C"] for r in out])
        print(f"  {vkey:<8s}  {np.mean(c):>8.4f}  {np.std(c, ddof=1):>8.4f}  "
              f"{np.mean(r):>11.5f}  {np.std(r, ddof=1):>9.5f}")

    print(f"\n  Total runtime: {time.time()-t_start:.0f}s")
    return out_path


if __name__ == "__main__":
    main()
