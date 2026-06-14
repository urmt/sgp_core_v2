import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import r2_score, silhouette_score, davies_bouldin_score, calinski_harabasz_score, adjusted_rand_score
from scipy.stats import pearsonr, f_oneway
from scipy.spatial.distance import cdist
import warnings
warnings.filterwarnings('ignore')

SEED = 542
rng = np.random.default_rng(SEED)

base = pd.read_csv('/home/student/sgp_core_v2/phases/phase516/phase516_percolation_results.csv')
y = base['stability_score'].values
N = len(base)

features = ['CSR', 'ADI', 'RBS']
X = StandardScaler().fit_transform(base[features].values)

K_range = list(range(2, 16))

# Phase 532 reference
ref_km = KMeans(n_clusters=6, random_state=SEED, n_init=100)
ref_labels = ref_km.fit_predict(X)

rows = []

for k in K_range:
    # ============ Multi-seed metrics (25 reps) ============
    reps = 25
    cv_reps = 5  # only 5 reps for LOOCV

    sil_s, db_s, ch_s = [], [], []
    train_r2s = []
    cv_r2s, cv_rs, cv_rmses = [], [], []
    labels_set = []
    anova_fs, anova_ps = [], []

    for r in range(reps):
        km = KMeans(n_clusters=k, random_state=SEED + r + k * 100, n_init=30)
        labs = km.fit_predict(X)

        sil_s.append(silhouette_score(X, labs))
        db_s.append(davies_bouldin_score(X, labs))
        ch_s.append(calinski_harabasz_score(X, labs))
        labels_set.append(labs)

        means = {c: np.mean(y[labs == c]) for c in range(k)}
        pred = np.array([means.get(l, np.mean(y)) for l in labs])
        train_r2s.append(r2_score(y, pred))

        groups = [y[labs == c] for c in range(k) if sum(labs == c) > 1]
        if len(groups) > 1:
            f, p = f_oneway(*groups)
        else:
            f, p = 0, 1.0
        anova_fs.append(f)
        anova_ps.append(p)

        # LOOCV for first cv_reps reps only
        if r < cv_reps:
            cv_preds = np.empty(N)
            for i in range(N):
                tr_idx = np.delete(np.arange(N), i)
                Xtr, ytr = X[tr_idx], y[tr_idx]
                Xte = X[[i]]
                km_cv = KMeans(n_clusters=k, random_state=SEED + r + k * 100 + i + 5000, n_init=10)
                km_cv.fit(Xtr)
                dist = cdist(Xte, km_cv.cluster_centers_)
                lbl = int(np.argmin(dist[0]))
                tr_lbl = km_cv.labels_
                cv_means = {c: np.mean(ytr[tr_lbl == c]) for c in range(k)}
                cv_preds[i] = cv_means.get(lbl, np.mean(ytr))
            cv_r2s.append(r2_score(y, cv_preds))
            cv_rs.append(pearsonr(y, cv_preds)[0])
            cv_rmses.append(np.sqrt(np.mean((y - cv_preds) ** 2)))

    # partition stability across seeds
    ari_scores = []
    for i in range(min(reps, 10)):  # subset to reduce O(n²)
        for j in range(i + 1, min(reps, 10)):
            ari_scores.append(adjusted_rand_score(labels_set[i], labels_set[j]))
    mean_ari = np.mean(ari_scores) if ari_scores else 0

    # margin
    km = KMeans(n_clusters=k, random_state=SEED, n_init=50)
    km.fit(X)
    D = cdist(X, km.cluster_centers_)
    sd = np.sort(D, axis=1)
    margins = sd[:, 1] - sd[:, 0]
    mean_margin = np.mean(margins)

    row = {
        'k': k,
        'silhouette': round(np.mean(sil_s), 4),
        'davies_bouldin': round(np.mean(db_s), 4),
        'calinski_harabasz': round(np.mean(ch_s), 1),
        'train_R2': round(np.mean(train_r2s), 4),
        'LOOCV_R2': round(np.mean(cv_r2s), 4) if cv_r2s else 0,
        'LOOCV_R2_std': round(np.std(cv_r2s), 4) if cv_r2s else 0,
        'LOOCV_r': round(np.nanmean(cv_rs), 4) if cv_rs else 0,
        'LOOCV_RMSE': round(np.mean(cv_rmses), 4) if cv_rmses else 0,
        'ANOVA_F': round(np.mean(anova_fs), 2),
        'ANOVA_p': float(f'{np.exp(np.mean(np.log([max(p, 1e-300) for p in anova_ps]))):.3g}'),
        'seed_ARI': round(mean_ari, 4),
        'mean_margin': round(mean_margin, 4),
    }
    rows.append(row)

df_k = pd.DataFrame(rows)
df_k.to_csv('/home/student/sgp_core_v2/phases/phase542/phase542_ksweep.csv', index=False)

# ============ Analysis ============
cv_r2s = df_k['LOOCV_R2'].values
sil_s = df_k['silhouette'].values
aris = df_k['seed_ARI'].values

kmax_cv = K_range[np.argmax(cv_r2s)]
kmax_sil = K_range[np.argmax(sil_s)]
max_cv = np.max(cv_r2s)

plateau_cv = [k for k, v in zip(K_range, cv_r2s) if v > max_cv * 0.95]

k6 = df_k[df_k['k'] == 6].iloc[0]
k6_cv = k6['LOOCV_R2']
k6_sil = k6['silhouette']
k6_ari = k6['seed_ARI']
k6_f = k6['ANOVA_F']

if k6_ari > 0.9 and kmax_cv == 6 and kmax_sil == 6:
    verdict = 'STRUCTURAL-k-INVARIANT'
elif len(plateau_cv) > 2 and 6 in plateau_cv:
    verdict = 'k-PLATEAU-STRUCTURE'
elif k6_ari < 0.5:
    verdict = 'FRAGILE-k-OPTIMUM'
else:
    verdict = 'k-PLATEAU-STRUCTURE'

summary = {
    'phase': 542,
    'best_k_CV_R2': kmax_cv,
    'best_k_silhouette': kmax_sil,
    'k6_LOOCV_R2': round(k6_cv, 4),
    'k6_silhouette': round(k6_sil, 4),
    'k6_seed_ARI': round(k6_ari, 4),
    'k6_ANOVA_F': round(k6_f, 2),
    'max_LOOCV_R2': round(max_cv, 4),
    'max_silhouette': round(np.max(sil_s), 4),
    'plateau_size': len(plateau_cv),
    'plateau_ks': str(plateau_cv),
    'verdict': verdict,
}

pd.DataFrame([summary]).to_csv('/home/student/sgp_core_v2/phases/phase542/phase542_summary.csv', index=False)

print('\n=== PHASE 542 COMPLETE ===')
for k, v in summary.items():
    print(f'  {k}: {v}')
print(f'\n{"k":>3} {"sil":>7} {"DB":>7} {"CH":>8} {"trR2":>7} {"cvR2":>7} {"cvR":>6} {"F":>9} {"ARI":>6} {"margin":>7}')
print('-' * 75)
for _, r in df_k.iterrows():
    print(f'{int(r["k"]):3} {r["silhouette"]:7.4f} {r["davies_bouldin"]:7.4f} {r["calinski_harabasz"]:8.1f} {r["train_R2"]:7.4f} {r["LOOCV_R2"]:7.4f} {r["LOOCV_r"]:6.3f} {r["ANOVA_F"]:9.1f} {r["seed_ARI"]:6.4f} {r["mean_margin"]:7.4f}')
