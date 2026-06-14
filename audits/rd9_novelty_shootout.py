"""RD-9: Novelty Measurement Shootout
Attempt to destroy every novelty candidate. See if any survive.

RD-9A: Predictive Surprise (PS)
RD-9B: Surprise Persistence (SP)
RD-9C: Historical Irreversibility (HI)
RD-9D: Generative Novelty (GN)

For each: correlation audit, PCA loading, FA loading, cross-validation.
"""

import sys, os, json, time
import numpy as np
from scipy import stats, signal
from sklearn.decomposition import FactorAnalysis, PCA
from sklearn.model_selection import KFold
import warnings
warnings.filterwarnings("ignore")

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, "coherence-benchmark")

from t901_analysis import _soft_sphere_force
from metrics.total_correlation import compute_C

# ═══════════════════════════════════════════════════════════════════
# SIMULATION
# ═══════════════════════════════════════════════════════════════════

def run_sim(friction=0.3, n_grains=50, n_steps=1500, seed=42):
    """Run granular sim with extended trajectory for novelty computation."""
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


# ═══════════════════════════════════════════════════════════════════
# NOVELTY METRICS
# ═══════════════════════════════════════════════════════════════════

def predictive_surprise(all_y, all_vy, k=5, warmup=100):
    """RD-9A: Per-grain AR(k) prediction error.
    PS = mean |actual - predicted| across grains and time."""
    n_grains, T = all_y.shape
    errors = []
    
    for g in range(n_grains):
        y = all_y[g, :]
        valid = ~np.isnan(y)
        if np.sum(valid) < warmup + k + 10:
            continue
        y_clean = y[valid]
        
        # Vectorized AR(k): use matrix of lagged values
        usable = len(y_clean) - warmup - k - 1
        if usable < 10: continue
        n = usable
        
        # Build lag matrix
        lags = np.zeros((n, k))
        for j in range(k):
            lags[:, j] = y_clean[warmup+j:warmup+j+n]
        targets = y_clean[warmup+k:warmup+k+n]
        
        # Least squares: y = X @ beta
        try:
            beta = np.linalg.lstsq(lags, targets, rcond=None)[0]
            predicted = lags @ beta
            errors.extend(np.abs(targets - predicted))
        except:
            pass
    
    return float(np.mean(errors)) if errors else 0.0


def surprise_persistence(all_y, all_vy, k=5, warmup=100, threshold_percentile=90):
    """RD-9B: Autocorrelation time of surprise events.
    SP = autocorrelation lag at 1/e decay of surprise time series."""
    n_grains, T = all_y.shape
    
    # Compute surprise time series (mean across grains)
    surprise_ts = np.zeros(T - warmup)
    count = 0
    
    for g in range(n_grains):
        y = all_y[g, :]
        valid = ~np.isnan(y)
        if np.sum(valid) < warmup + k + 10:
            continue
        y_clean = y[valid]
        
        usable = len(y_clean) - warmup - k - 1
        if usable < 10: continue
        n = min(usable, len(surprise_ts))
        
        lags = np.zeros((n, k))
        for j in range(k):
            lags[:, j] = y_clean[warmup+j:warmup+j+n]
        targets = y_clean[warmup+k:warmup+k+n]
        
        try:
            beta = np.linalg.lstsq(lags, targets, rcond=None)[0]
            predicted = lags @ beta
            errs = np.abs(targets - predicted)
            surprise_ts[:n] += errs
            count += 1
        except:
            pass
    
    if count > 0:
        surprise_ts /= count
    
    # Threshold: identify "surprise events" (top 10%)
    nonzero = surprise_ts[surprise_ts > 0]
    if len(nonzero) < 10:
        return 0.0
    threshold = np.percentile(nonzero, threshold_percentile)
    surprise_binary = (surprise_ts > threshold).astype(float)
    
    # Autocorrelation of surprise events
    if np.sum(surprise_binary) < 5:
        return 0.0
    
    n = len(surprise_binary)
    acf = np.correlate(surprise_binary - np.mean(surprise_binary),
                       surprise_binary - np.mean(surprise_binary), mode='full')
    acf = acf[n-1:]
    if acf[0] > 0:
        acf /= acf[0]
    
    # Find 1/e decay
    for i in range(1, len(acf)):
        if acf[i] < 1.0 / np.e:
            return float(i)
    return float(len(acf))


def historical_irreversibility(all_y, window=200, step=50):
    """RD-9C: KL divergence between forward and reversed trajectory distributions.
    Simplified: compare entropy of forward vs backward velocity distributions."""
    n_grains, T = all_y.shape
    
    # Compute velocity
    all_vy = np.diff(all_y, axis=1)
    
    # Forward: distribution of velocities in first half
    fwd = all_vy[:, :T//2].flatten()
    fwd = fwd[~np.isnan(fwd)]
    
    # Backward: distribution of velocities in second half (reversed)
    bwd = all_vy[:, T//2:].flatten()
    bwd = bwd[~np.isnan(bwd)]
    
    if len(fwd) < 100 or len(bwd) < 100:
        return 0.0
    
    # Discretize into bins
    all_v = np.concatenate([fwd, bwd])
    bins = np.linspace(np.percentile(all_v, 1), np.percentile(all_v, 99), 30)
    
    hist_fwd, _ = np.histogram(fwd, bins=bins, density=True)
    hist_bwd, _ = np.histogram(bwd, bins=bins, density=True)
    
    # Add epsilon to avoid log(0)
    eps = 1e-10
    hist_fwd = hist_fwd + eps
    hist_bwd = hist_bwd + eps
    
    # Normalize
    hist_fwd /= hist_fwd.sum()
    hist_bwd /= hist_bwd.sum()
    
    # KL divergence (symmetrized = JS divergence)
    kl_fb = np.sum(hist_fwd * np.log(hist_fwd / hist_bwd))
    kl_bf = np.sum(hist_bwd * np.log(hist_bwd / hist_fwd))
    
    return float((kl_fb + kl_bf) / 2)


def generative_novelty(all_y, all_x, all_vy, warmup=100, surprise_pct=90, window=50):
    """RD-9D: Does surprise expand future state-space volume?
    GN = V_future(after surprise) - V_baseline(before surprise)"""
    n_grains, T = all_y.shape
    
    # Compute surprise time series (simplified: use velocity variance as proxy)
    # High local variance = surprising dynamics
    k = 5
    surprise_ts = np.zeros(T)
    
    for g in range(n_grains):
        y = all_y[g, :]
        valid = ~np.isnan(y)
        if np.sum(valid) < warmup + k + 10:
            continue
        y_clean = y[valid]
        usable = len(y_clean) - warmup - k - 1
        if usable < 10: continue
        n = min(usable, T - warmup)
        
        lags = np.zeros((n, k))
        for j in range(k):
            lags[:, j] = y_clean[warmup+j:warmup+j+n]
        targets = y_clean[warmup+k:warmup+k+n]
        
        try:
            beta = np.linalg.lstsq(lags, targets, rcond=None)[0]
            predicted = lags @ beta
            errs = np.abs(targets - predicted)
            surprise_ts[warmup:warmup+n] += errs
        except:
            pass
    
    # Threshold
    nonzero = surprise_ts[surprise_ts > 0]
    if len(nonzero) < 10:
        return 0.0
    threshold = np.percentile(nonzero, surprise_pct)
    surprise_events = np.where(surprise_ts > threshold)[0]
    surprise_events = surprise_events[surprise_events > warmup + window]
    surprise_events = surprise_events[surprise_events < T - window]
    
    if len(surprise_events) < 3:
        return 0.0
    
    # For each surprise event, compare future vs baseline volume
    gn_values = []
    for t_surp in surprise_events[:15]:
        baseline_y = all_y[:, max(0, t_surp-window):t_surp]
        future_y = all_y[:, t_surp:min(T, t_surp+window)]
        
        if baseline_y.size == 0 or future_y.size == 0:
            continue
        
        vol_baseline = np.nanmax(baseline_y) - np.nanmin(baseline_y)
        vol_future = np.nanmax(future_y) - np.nanmin(future_y)
        
        if vol_baseline > 0:
            gn_values.append((vol_future - vol_baseline) / vol_baseline)
    
    return float(np.mean(gn_values)) if gn_values else 0.0


# ═══════════════════════════════════════════════════════════════════
# EXISTING METRICS (from t901 pipeline)
# ═══════════════════════════════════════════════════════════════════

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


def existing_metrics(all_y, all_x, all_vx, all_vy, friction):
    """Compute the t901 metric set for comparison."""
    T = all_y.shape[1]
    
    # C
    X = _bin_data(all_y, all_x, n_bins=10)
    _, c_vals = _sliding_C(X, window=75, step=25)
    pre_mask = np.arange(len(c_vals)) * 25 + 37
    C = float(np.nanmean(c_vals[(pre_mask >= 100) & (pre_mask < 500)]))
    
    # Physical
    jitter = float(np.nanmean(np.sqrt(all_vx**2 + all_vy**2)))
    msd = float(np.nanmean((all_y[:, -1] - all_y[:, 0])**2))
    rms_v = float(np.nanmean(np.sqrt(all_vx**2 + all_vy**2)))
    
    # MSE (prediction error from lag-1)
    mse_vals = []
    for g in range(all_y.shape[0]):
        y = all_y[g, :]
        valid = ~np.isnan(y)
        if np.sum(valid) < 10: continue
        y_clean = y[valid]
        pred = y_clean[:-1]
        actual = y_clean[1:]
        mse_vals.append(np.mean((actual - pred)**2))
    mse = float(np.mean(mse_vals)) if mse_vals else 0.0
    
    # Packing variance (std of y-positions at final time)
    y_final = all_y[:, -1]
    packing_var = float(np.nanstd(y_final))
    
    # Neighbor turnover (simplified: how many neighbors change per 100 steps)
    # Use position correlation between time windows
    if T > 200:
        y1 = np.nanmean(all_y[:, :100], axis=1)
        y2 = np.nanmean(all_y[:, 100:200], axis=1)
        valid = ~np.isnan(y1) & ~np.isnan(y2)
        if np.sum(valid) > 5:
            turnover = 1 - np.corrcoef(y1[valid], y2[valid])[0,1]
        else:
            turnover = 0
    else:
        turnover = 0
    
    return {
        "C": C, "jitter": jitter, "msd": msd, "MSE": mse,
        "rms_velocity": rms_v, "packing_var": packing_var,
        "neighbor_turnover": turnover, "friction": friction,
    }


# ═══════════════════════════════════════════════════════════════════
# MAIN SWEEP
# ═══════════════════════════════════════════════════════════════════

FRICTION_LEVELS = np.linspace(0.05, 0.80, 12)
N_REPS = 6
N_GRAINS = 50; N_STEPS = 1000; BASE_SEED = 7000

results = []
t0 = time.time()
total = len(FRICTION_LEVELS) * N_REPS
done = 0

print("RD-9: NOVELTY MEASUREMENT SHOOTOUT")
print("=" * 80)

for fr in FRICTION_LEVELS:
    for rep in range(N_REPS):
        seed = BASE_SEED + rep + int(fr * 10000)
        all_y, all_x, all_vx, all_vy = run_sim(
            friction=fr, n_grains=N_GRAINS, n_steps=N_STEPS, seed=seed)
        
        # Existing metrics
        existing = existing_metrics(all_y, all_x, all_vx, all_vy, fr)
        
        # Novelty metrics
        ps = predictive_surprise(all_y, all_vy)
        sp = surprise_persistence(all_y, all_vy)
        hi = historical_irreversibility(all_y)
        gn = generative_novelty(all_y, all_x, all_vy)
        
        row = {
            "friction": round(float(fr), 4), "rep": rep,
            **existing,
            "PS": round(ps, 4),
            "SP": round(sp, 2),
            "HI": round(hi, 6),
            "GN": round(gn, 4),
        }
        results.append(row)
        
        done += 1
        if done % 20 == 0:
            elapsed = time.time() - t0
            print(f"  [{done}/{total}] {elapsed:.0f}s | μ={fr:.2f} PS={ps:.3f} SP={sp:.1f} HI={hi:.5f} GN={gn:.4f}")

elapsed = time.time() - t0
print(f"\nSweep: {done} runs in {elapsed:.0f}s")

with open("audits/rd9_novelty_shootout.json", "w") as f:
    json.dump(results, f, indent=2)

# ═══════════════════════════════════════════════════════════════════
# STEP 1: CORRELATION AUDIT
# ═══════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("STEP 1: CORRELATION AUDIT")
print("=" * 80)

keys_all = ["friction", "C", "MSE", "rms_velocity", "msd", "packing_var",
            "neighbor_turnover", "PS", "SP", "HI", "GN"]

valid = [r for r in results if all(r.get(k) is not None for k in keys_all)]
print(f"Valid runs: {len(valid)} / {len(results)}")

M = np.array([[r[k] for k in keys_all] for r in valid])
M_std = (M - np.mean(M, axis=0)) / np.std(M, axis=0)

corr = np.corrcoef(M_std.T)
print(f"\n{'':>18s}", end="")
for k in keys_all:
    print(f"{k[:7]:>9s}", end="")
print()
for i, k in enumerate(keys_all):
    print(f"{k:>18s}", end="")
    for j in range(len(keys_all)):
        print(f"{corr[i,j]:>9.3f}", end="")
    print()

# Focus: correlations of novelty metrics with existing
print("\n--- Novelty metric correlations with existing ---")
novelty_keys = ["PS", "SP", "HI", "GN"]
existing_keys = ["friction", "C", "MSE", "rms_velocity", "msd"]

for nk in novelty_keys:
    nk_idx = keys_all.index(nk)
    print(f"\n{nk}:")
    for ek in existing_keys:
        ek_idx = keys_all.index(ek)
        r = corr[nk_idx, ek_idx]
        print(f"  vs {ek:>15s}: r={r:+.3f}")

# ═══════════════════════════════════════════════════════════════════
# STEP 2: REGRESSION AGAINST F1/F2/F3
# ═══════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("STEP 2: REGRESSION AGAINST EXISTING FACTORS")
print("=" * 80)

# First, get F1/F2/F3 from existing metrics only
existing_metric_keys = ["friction", "C", "MSE", "rms_velocity", "msd",
                         "packing_var", "neighbor_turnover"]
M_exist = np.array([[r[k] for k in existing_metric_keys] for r in valid])
M_exist_std = (M_exist - np.mean(M_exist, axis=0)) / np.std(M_exist, axis=0)

# PCA on existing
cov_exist = np.cov(M_exist_std.T)
eigvals_exist, eigvecs_exist = np.linalg.eigh(cov_exist)
eigvals_exist = eigvals_exist[::-1]; eigvecs_exist = eigvecs_exist[:, ::-1]
F = M_exist_std @ eigvecs_exist[:, :3]  # F1, F2, F3

print("F1-F3 from existing metrics:")
for nk in novelty_keys:
    y = np.array([r[nk] for r in valid])
    try:
        beta = np.linalg.lstsq(F, y, rcond=None)[0]
        y_pred = F @ beta
        ss_res = np.sum((y - y_pred)**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    except:
        r2 = 0
    residual_var = 1 - r2
    print(f"  {nk}: R²(F1,F2,F3)={r2:.4f}, residual_var={residual_var:.4f} ({residual_var*100:.1f}%)")

# ═══════════════════════════════════════════════════════════════════
# STEP 3-4: PCA + FA WITH EACH NOVELTY METRIC
# ═══════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("STEP 3-4: PCA + FA WITH EACH NOVELTY METRIC")
print("=" * 80)

for nk in novelty_keys:
    print(f"\n--- Adding {nk} ---")
    
    # Build matrix: existing + this novelty
    keys_test = existing_metric_keys + [nk]
    M_test = np.array([[r[k] for k in keys_test] for r in valid])
    M_test_std = (M_test - np.mean(M_test, axis=0)) / np.std(M_test, axis=0)
    
    # PCA
    cov_test = np.cov(M_test_std.T)
    eigvals_test, eigvecs_test = np.linalg.eigh(cov_test)
    eigvals_test = eigvals_test[::-1]; eigvecs_test = eigvecs_test[:, ::-1]
    explained_test = eigvals_test / np.sum(eigvals_test)
    cumulative_test = np.cumsum(explained_test)
    
    n_90 = np.searchsorted(cumulative_test, 0.90) + 1
    
    # Loading of novelty metric on each PC
    nk_idx = len(existing_metric_keys)  # last column
    print(f"  90% variance: {n_90} dimensions")
    for pc in range(min(5, len(keys_test))):
        loading = eigvecs_test[nk_idx, pc]
        print(f"  PC{pc+1} ({explained_test[pc]*100:.1f}%): {nk} loading = {loading:+.4f}")
    
    # FA
    best_bic = np.inf; best_nf = 1
    for nf in range(1, 6):
        fa = FactorAnalysis(n_components=nf, random_state=42, max_iter=1000)
        fa.fit(M_test_std)
        score = fa.score(M_test_std) * M_test_std.shape[0]
        n_params = nf * M_test_std.shape[1] + M_test_std.shape[1]
        bic = -2*score + n_params * np.log(M_test_std.shape[0])
        if bic < best_bic:
            best_bic = bic; best_nf = nf
    print(f"  FA best: {best_nf} factors (BIC={best_bic:.1f})")
    
    # FA loadings for best model
    fa_best = FactorAnalysis(n_components=best_nf, random_state=42, max_iter=1000)
    fa_best.fit(M_test_std)
    for f in range(best_nf):
        loading = fa_best.components_[f, nk_idx]
        if abs(loading) > 0.2:
            print(f"  F{f+1}: {nk} loading = {loading:+.4f}")

# ═══════════════════════════════════════════════════════════════════
# STEP 5: CROSS-VALIDATION
# ═══════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("STEP 5: CROSS-VALIDATION (5-fold)")
print("=" * 80)

kf = KFold(n_splits=5, shuffle=True, random_state=42)

for nk in novelty_keys:
    print(f"\n--- {nk} ---")
    
    keys_test = existing_metric_keys + [nk]
    M_test = np.array([[r[k] for k in keys_test] for r in valid])
    M_test_std = (M_test - np.mean(M_test, axis=0)) / np.std(M_test, axis=0)
    
    fold_dims = []
    fold_loadings = []
    
    for train_idx, test_idx in kf.split(M_test_std):
        M_train = M_test_std[train_idx]
        
        cov_train = np.cov(M_train.T)
        eigvals_train, eigvecs_train = np.linalg.eigh(cov_train)
        eigvals_train = eigvals_train[::-1]; eigvecs_train = eigvecs_train[:, ::-1]
        explained_train = eigvals_train / np.sum(eigvals_train)
        cumulative_train = np.cumsum(explained_train)
        
        n_90_fold = np.searchsorted(cumulative_train, 0.90) + 1
        fold_dims.append(n_90_fold)
        
        # Loading on test data
        M_test_fold = M_test_std[test_idx]
        eigvecs_test_fold = np.linalg.eigvalsh(np.cov(M_train.T))[::-1]
        
        # Loading of novelty metric on PC1 in training
        loading_pc1 = eigvecs_train[len(existing_metric_keys), 0]
        fold_loadings.append(loading_pc1)
    
    dims_stable = len(set(fold_dims)) == 1
    loadings_consistent = np.std(fold_loadings) < 0.1
    
    print(f"  Dimensions across folds: {fold_dims} (stable: {dims_stable})")
    print(f"  PC1 loadings across folds: {[f'{l:.3f}' for l in fold_loadings]}")
    print(f"  Loadings std: {np.std(fold_loadings):.4f} (consistent: {loadings_consistent})")
    
    # Verdict
    if dims_stable and loadings_consistent:
        print(f"  VERDICT: SURVIVES cross-validation")
    else:
        print(f"  VERDICT: COLLAPSES under cross-validation")

# ═══════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("RD-9 SUMMARY: NOVELTY SHOOTOUT VERDICTS")
print("=" * 80)

for nk in novelty_keys:
    y = np.array([r[nk] for r in valid])
    try:
        beta = np.linalg.lstsq(F, y, rcond=None)[0]
        y_pred = F @ beta
        ss_res = np.sum((y - y_pred)**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    except:
        r2 = 0
    
    # Max correlation with existing
    nk_idx = keys_all.index(nk)
    max_corr_with_existing = max(abs(corr[nk_idx, j])
                                  for j in range(len(keys_all))
                                  if keys_all[j] not in novelty_keys)
    
    print(f"\n{nk}:")
    print(f"  R²(F1,F2,F3): {r2:.4f}")
    print(f"  Max |r| with existing: {max_corr_with_existing:.3f}")
    print(f"  Residual unexplained: {(1-r2)*100:.1f}%")
    
    if r2 > 0.5:
        print(f"  → LIKELY COLLAPSES into existing factors")
    elif r2 > 0.3:
        print(f"  → PARTIAL overlap with existing factors")
    else:
        print(f"  → POTENTIALLY INDEPENDENT — needs further investigation")
