import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import r2_score, adjusted_rand_score
from scipy.stats import pearsonr
from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment

SEED = 541
rng = np.random.default_rng(SEED)

base = pd.read_csv('/home/student/sgp_core_v2/phases/phase516/phase516_percolation_results.csv')
y = base['stability_score'].values
N = len(base)

features = ['CSR', 'ADI', 'RBS']
X_raw = base[features].values
X_full = StandardScaler().fit_transform(X_raw)
K = 6

# ============ A. LOOCV ============
loocv_preds = np.empty(N)
loocv_labels = np.empty(N, dtype=int)
loocv_centroids = []

for i in range(N):
    train_idx = np.delete(np.arange(N), i)
    X_train = X_full[train_idx]
    y_train = y[train_idx]
    X_test = X_full[[i]]

    km = KMeans(n_clusters=K, random_state=SEED + i, n_init=100)
    km.fit(X_train)
    dist = cdist(X_test, km.cluster_centers_)
    lbl = int(np.argmin(dist[0]))
    train_lbl = km.labels_
    means = {c: np.mean(y_train[train_lbl == c]) for c in range(K)}
    loocv_preds[i] = means.get(lbl, np.mean(y_train))
    loocv_labels[i] = lbl
    loocv_centroids.append(km.cluster_centers_)

loocv_r2 = r2_score(y, loocv_preds)
loocv_r, loocv_p = pearsonr(y, loocv_preds)
loocv_rmse = np.sqrt(np.mean((y - loocv_preds)**2))
loocv_mae = np.mean(np.abs(y - loocv_preds))
loocv_res_var = np.var(y - loocv_preds)

# ============ B. Repeated Leave-3-Out ============
N_TRIALS = 500
l3o_r2s, l3o_rs, l3o_rmses, l3o_maes = [], [], [], []

for t in range(N_TRIALS):
    tidx = rng.choice(N, 3, replace=False)
    tridx = np.setdiff1d(np.arange(N), tidx)
    Xtr, ytr = X_full[tridx], y[tridx]
    Xte, yte = X_full[tidx], y[tidx]
    km = KMeans(n_clusters=K, random_state=SEED + t + 1000, n_init=50)
    km.fit(Xtr)
    dist = cdist(Xte, km.cluster_centers_)
    lbls = np.argmin(dist, axis=1)
    tr_lbl = km.labels_
    means = {c: np.mean(ytr[tr_lbl == c]) for c in range(K)}
    preds = np.array([means.get(l, np.mean(ytr)) for l in lbls])
    l3o_r2s.append(r2_score(yte, preds))
    l3o_rs.append(pearsonr(yte, preds)[0] if len(np.unique(preds)) > 1 else 0)
    l3o_rmses.append(np.sqrt(np.mean((yte - preds)**2)))
    l3o_maes.append(np.mean(np.abs(yte - preds)))

# Use median for L3O (robust to 3-point R² outliers)
l3o_med_r2 = np.nanmedian(l3o_r2s)
l3o_mad_r2 = np.nanmedian(np.abs(np.array(l3o_r2s) - l3o_med_r2))
l3o_med_r = np.nanmedian(l3o_rs)
l3o_med_rmse = np.nanmedian(l3o_rmses)
l3o_med_mae = np.nanmedian(l3o_maes)

# ============ C. Bootstrap (1000 fits) ============
N_BOOT = 1000
boot_aris, boot_centroids = [], np.zeros((N_BOOT, K, 3))
boot_coclust = np.zeros((N, N))

for b in range(N_BOOT):
    sidx = rng.choice(N, N, replace=True)
    Xb = X_full[sidx]
    km = KMeans(n_clusters=K, random_state=SEED + b + 2000, n_init=50)
    labels = km.fit_predict(Xb)
    boot_centroids[b] = km.cluster_centers_
    boot_aris.append(adjusted_rand_score(loocv_labels[sidx], labels))
    for i in range(N):
        boot_coclust[i, labels == labels[i]] += 1
boot_coclust /= N_BOOT

mean_ari = np.mean(boot_aris)
std_ari = np.std(boot_aris)

# diag coclust is always 1; measure off-diag stability per system
asn_per_sys = np.array([(boot_coclust[i].sum() - 1) / (N - 1) for i in range(N)])
mean_asn_stability = np.mean(asn_per_sys)

# centroid drift (aligned via Hungarian, first as reference)
aligned = [boot_centroids[0].copy()]
for b in range(1, N_BOOT):
    cent = boot_centroids[b].copy()
    cost = cdist(aligned[0], cent)
    ri, ci = linear_sum_assignment(cost)
    cent = cent[ci]
    aligned.append(cent)
aligned = np.array(aligned)
aligned_mean = np.mean(aligned, axis=0)
drift = np.sqrt(np.mean((aligned - aligned_mean[np.newaxis])**2, axis=(1, 2)))
med_drift = np.median(drift)
p95_drift = np.percentile(drift, 95)

# prediction intervals (fit on bootstrap sample, predict on full data)
boot_preds = np.zeros((N_BOOT, N))
for b in range(N_BOOT):
    sidx = rng.choice(N, N, replace=True)
    Xb = X_full[sidx]
    yb = y[sidx]
    km = KMeans(n_clusters=K, random_state=SEED + b + 3000, n_init=50)
    km.fit(Xb)
    dist = cdist(X_full, km.cluster_centers_)
    lbls = np.argmin(dist, axis=1)
    means = {c: np.mean(yb[lbls[sidx] == c]) for c in range(K)}
    boot_preds[b] = np.array([means.get(l, np.mean(yb)) for l in lbls])

pi_low = np.percentile(boot_preds, 2.5, axis=0)
pi_high = np.percentile(boot_preds, 97.5, axis=0)
pi_width = pi_high - pi_low
mean_pi_width = np.mean(pi_width)

# ============ Training R² ============
full_km = KMeans(n_clusters=K, random_state=SEED, n_init=100)
full_labels = full_km.fit_predict(X_full)
full_means = {c: np.mean(y[full_labels == c]) for c in range(K)}
full_pred = np.array([full_means[c] for c in full_labels])
train_r2 = r2_score(y, full_pred)

# ============ RESULTS ============
results = {
    'phase': 541,
    'train_R2': round(train_r2, 4),
    'LOOCV_R2': round(loocv_r2, 4),
    'LOOCV_r': round(loocv_r, 4),
    'LOOCV_p': float(f'{loocv_p:.3g}'),
    'LOOCV_RMSE': round(loocv_rmse, 4),
    'LOOCV_MAE': round(loocv_mae, 4),
    'LOOCV_residual_var': round(loocv_res_var, 6),
    'L3O_median_R2': round(l3o_med_r2, 4),
    'L3O_MAD_R2': round(l3o_mad_r2, 4),
    'L3O_median_RMSE': round(l3o_med_rmse, 4),
    'L3O_median_MAE': round(l3o_med_mae, 4),
    'mean_asn_stability': round(mean_asn_stability, 4),
    'bootstrap_mean_ARI': round(mean_ari, 4),
    'bootstrap_std_ARI': round(std_ari, 4),
    'median_centroid_drift': round(med_drift, 4),
    'p95_centroid_drift': round(p95_drift, 4),
    'mean_PI_width': round(mean_pi_width, 4),
    'R2_drop': round(train_r2 - loocv_r2, 4),
}

if loocv_r2 > 0.80 and mean_asn_stability > 0.75 and med_drift < 0.5:
    verdict = 'GENERALIZABLE-CLUSTER-LAW'
elif loocv_r2 > 0.50:
    verdict = 'PARTIAL-GENERALIZATION'
else:
    verdict = 'OVERFIT-TAXONOMY'

results['verdict'] = verdict

pd.DataFrame([results]).to_csv('/home/student/sgp_core_v2/phases/phase541/phase541_summary.csv', index=False)

loocv_df = pd.DataFrame({
    'system': base['name'], 'true': y, 'pred': loocv_preds,
    'residual': y - loocv_preds, 'residual_abs': np.abs(y - loocv_preds),
    'assignment': loocv_labels, 'asn_stability': asn_per_sys,
    'PI_low': pi_low, 'PI_high': pi_high, 'PI_width': pi_width
})
loocv_df.to_csv('/home/student/sgp_core_v2/phases/phase541/phase541_loocv_results.csv', index=False)

coclust_df = pd.DataFrame(boot_coclust, index=base['name'], columns=base['name'])
coclust_df.to_csv('/home/student/sgp_core_v2/phases/phase541/phase541_coclust_matrix.csv')

l3o_df = pd.DataFrame({'R2': l3o_r2s, 'RMSE': l3o_rmses, 'MAE': l3o_maes})
l3o_df.to_csv('/home/student/sgp_core_v2/phases/phase541/phase541_l3o_results.csv', index=False)

print('\n=== PHASE 541 COMPLETE ===')
for k, v in results.items():
    print(f'  {k}: {v}')
print(f'\n  Per-system stability range: {asn_per_sys.min():.3f} – {asn_per_sys.max():.3f}')
print(f'  Systems with PI_width > 1.0: {(pi_width > 1.0).sum()} / {N}')
