import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import r2_score
from scipy.stats import pearsonr
from scipy.spatial.distance import cdist

SEED = 541
rng = np.random.default_rng(SEED)

# ============ LOAD ============
base = pd.read_csv('/home/student/sgp_core_v2/phases/phase516/phase516_percolation_results.csv')
y = base['stability_score'].values
N = len(base)

features = ['CSR', 'ADI', 'RBS']
X_raw = base[features].values
X_full = StandardScaler().fit_transform(X_raw)
K = 6

# ============ A. LOOCV ============
loocv_preds = np.empty(N)
loocv_assignments = np.empty(N, dtype=int)

for i in range(N):
    train_idx = np.delete(np.arange(N), i)
    test_idx = np.array([i])

    X_train = X_full[train_idx]
    y_train = y[train_idx]
    X_test = X_full[test_idx]

    km = KMeans(n_clusters=K, random_state=SEED + i, n_init=100)
    km.fit(X_train)

    dist = cdist(X_test, km.cluster_centers_)
    label = int(np.argmin(dist[0]))

    train_labels = km.labels_
    means = {c: np.mean(y_train[train_labels == c]) for c in range(K)}
    loocv_preds[i] = means.get(label, np.mean(y_train))
    loocv_assignments[i] = label

loocv_r2 = r2_score(y, loocv_preds)
loocv_r, loocv_p = pearsonr(y, loocv_preds)
loocv_rmse = np.sqrt(np.mean((y - loocv_preds)**2))
loocv_mae = np.mean(np.abs(y - loocv_preds))
loocv_residual_var = np.var(y - loocv_preds)

# ============ B. Repeated Leave-3-Out (500 trials) ============
l3o_preds_list = []
l3o_r2s = []
l3o_rs = []
l3o_rmses = []
l3o_maes = []

N_TRIALS = 500

for t in range(N_TRIALS):
    test_idx = rng.choice(N, size=3, replace=False)
    train_idx = np.setdiff1d(np.arange(N), test_idx)

    X_train = X_full[train_idx]
    y_train = y[train_idx]
    X_test = X_full[test_idx]
    y_test = y[test_idx]

    km = KMeans(n_clusters=K, random_state=SEED + t + 1000, n_init=50)
    km.fit(X_train)
    dist = cdist(X_test, km.cluster_centers_)
    labels = np.argmin(dist, axis=1)
    train_labels = km.labels_
    means = {c: np.mean(y_train[train_labels == c]) for c in range(K)}
    preds = np.array([means.get(l, np.mean(y_train)) for l in labels])

    l3o_preds_list.append((test_idx, preds))
    l3o_r2s.append(r2_score(y_test, preds))
    l3o_rs.append(pearsonr(y_test, preds)[0] if len(np.unique(preds)) > 1 else 0)
    l3o_rmses.append(np.sqrt(np.mean((y_test - preds)**2)))
    l3o_maes.append(np.mean(np.abs(y_test - preds)))

l3o_mean_r2 = np.mean(l3o_r2s)
l3o_std_r2 = np.std(l3o_r2s)
l3o_mean_r = np.nanmean(l3o_rs)
l3o_mean_rmse = np.mean(l3o_rmses)
l3o_mean_mae = np.mean(l3o_maes)

# ============ C. Bootstrap (1000 fits) ============
N_BOOT = 1000
boot_centroids = np.zeros((N_BOOT, K, 3))
boot_assignments = np.zeros((N_BOOT, N), dtype=int)

for b in range(N_BOOT):
    sample_idx = rng.choice(N, size=N, replace=True)
    Xb = X_full[sample_idx]
    km = KMeans(n_clusters=K, random_state=SEED + b + 2000, n_init=50)
    km.fit(Xb)
    boot_centroids[b] = km.cluster_centers_
    boot_assignments[b] = km.labels_

# assignment stability for each system: fraction of bootstraps where it co-clusters with its LOOCV neighbors
# simpler: compute pairwise co-clustering matrix
coclust = np.zeros((N, N))
for b in range(N_BOOT):
    labels = boot_assignments[b]
    for i in range(N):
        coclust[i, labels == labels[i]] += 1
coclust /= N_BOOT

# assignment stability per system
asn_stability = np.array([coclust[i, i] for i in range(N)])
mean_asn_stability = np.mean(asn_stability)

# centroid drift
centroid_mean = np.mean(boot_centroids, axis=0)
centroid_drift = np.sqrt(np.mean((boot_centroids - centroid_mean[np.newaxis, ...])**2, axis=(1, 2)))
mean_centroid_drift = np.mean(centroid_drift)
p95_centroid_drift = np.percentile(centroid_drift, 95)

# prediction interval width per system
boot_preds = np.zeros((N_BOOT, N))
for b in range(N_BOOT):
    labels = boot_assignments[b]
    means = {c: np.mean(y[labels == c]) for c in range(K)}
    boot_preds[b] = np.array([means.get(l, np.mean(y)) for l in labels])

pi_low = np.percentile(boot_preds, 2.5, axis=0)
pi_high = np.percentile(boot_preds, 97.5, axis=0)
pi_width = pi_high - pi_low
mean_pi_width = np.mean(pi_width)

# ============ Training R² (full fit) ============
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
    'LOOCV_residual_var': round(loocv_residual_var, 6),
    'L3O_mean_R2': round(l3o_mean_r2, 4),
    'L3O_std_R2': round(l3o_std_r2, 4),
    'L3O_mean_RMSE': round(l3o_mean_rmse, 4),
    'L3O_mean_MAE': round(l3o_mean_mae, 4),
    'mean_asn_stability': round(mean_asn_stability, 4),
    'mean_centroid_drift': round(mean_centroid_drift, 4),
    'p95_centroid_drift': round(p95_centroid_drift, 4),
    'mean_PI_width': round(mean_pi_width, 4),
    'R2_drop': round(train_r2 - loocv_r2, 4),
}

if loocv_r2 > 0.80 and mean_asn_stability > 0.75 and mean_centroid_drift < 0.5:
    verdict = 'GENERALIZABLE-CLUSTER-LAW'
elif loocv_r2 > 0.50:
    verdict = 'PARTIAL-GENERALIZATION'
else:
    verdict = 'OVERFIT-TAXONOMY'

results['verdict'] = verdict

# ============ SAVE ============
pd.DataFrame([results]).to_csv('/home/student/sgp_core_v2/phases/phase541/phase541_summary.csv', index=False)

# detailed outputs
loocv_df = pd.DataFrame({'system': base['name'], 'true': y, 'pred': loocv_preds, 'residual': y - loocv_preds, 'assignment': loocv_assignments, 'asn_stability': asn_stability, 'PI_low': pi_low, 'PI_high': pi_high, 'PI_width': pi_width})
loocv_df.to_csv('/home/student/sgp_core_v2/phases/phase541/phase541_loocv_results.csv', index=False)

coclust_df = pd.DataFrame(coclust, index=base['name'], columns=base['name'])
coclust_df.to_csv('/home/student/sgp_core_v2/phases/phase541/phase541_coclust_matrix.csv')

l3o_df = pd.DataFrame({'R2': l3o_r2s, 'RMSE': l3o_rmses, 'MAE': l3o_maes})
l3o_df.to_csv('/home/student/sgp_core_v2/phases/phase541/phase541_l3o_results.csv', index=False)

print('\n=== PHASE 541 COMPLETE ===')
for k, v in results.items():
    print(f'  {k}: {v}')
print(f'\n  Per-system prediction summary:')
print(f'    R2 reached per system: {(loocv_r2 > 0.80)}')
print(f'    Mean PI width: {mean_pi_width:.4f}')
print(f'    Max PI width: {pi_width.max():.4f}')
