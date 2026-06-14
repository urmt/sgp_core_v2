import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.kernel_ridge import KernelRidge
from sklearn.ensemble import RandomForestRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel, ConstantKernel
from sklearn.model_selection import GridSearchCV, KFold
from sklearn.cluster import KMeans
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from scipy.stats import pearsonr, linregress
from scipy.spatial.distance import cdist
import warnings
warnings.filterwarnings('ignore')

SEED = 543
rng = np.random.default_rng(int(SEED))

base = pd.read_csv('/home/student/sgp_core_v2/phases/phase516/phase516_percolation_results.csv')
y = base['stability_score'].values
N = len(base)

features = ['CSR', 'ADI', 'RBS']
X = StandardScaler().fit_transform(base[features].values)
K_CLUSTER = 6

def cluster_predict(X_train, y_train, X_test, seed):
    km = KMeans(n_clusters=K_CLUSTER, random_state=int(seed), n_init=50)
    km.fit(X_train)
    dist = cdist(X_test, km.cluster_centers_)
    lbls = np.argmin(dist, axis=1)
    tr_lbls = km.labels_
    means = {c: np.mean(y_train[tr_lbls == c]) for c in range(K_CLUSTER)}
    return np.array([means.get(l, np.mean(y_train)) for l in lbls])

inner_cv = KFold(n_splits=5, shuffle=True, random_state=42)

# Define model builders
def build_linear():
    return Pipeline([('model', LinearRegression())])

def build_poly2():
    return Pipeline([('poly', PolynomialFeatures(2, include_bias=False)), ('model', LinearRegression())])

def build_poly3():
    return Pipeline([('poly', PolynomialFeatures(3, include_bias=False)), ('model', LinearRegression())])

def build_ridge():
    return Pipeline([('model', Ridge())])

def build_krr():
    return Pipeline([('model', KernelRidge(kernel='rbf'))])

def build_rf():
    return Pipeline([('model', RandomForestRegressor(random_state=42))])

def build_gp():
    return GaussianProcessRegressor(
        kernel=ConstantKernel() * RBF() + WhiteKernel(),
        random_state=42, normalize_y=True, n_restarts_optimizer=3
    )

models_def = [
    ('Linear', build_linear, {'model__fit_intercept': [True]}),
    ('Poly2', build_poly2, {'poly__degree': [2]}),
    ('Poly3', build_poly3, {'poly__degree': [3]}),
    ('Ridge', build_ridge, {'model__alpha': np.logspace(-3, 3, 15)}),
    ('KernelRidge', build_krr, {'model__alpha': [1e-3, 1e-2, 0.1, 1.0, 10.0], 'model__gamma': np.logspace(-2, 1, 5)}),
    ('RF', build_rf, {'model__n_estimators': [50, 100, 200], 'model__max_depth': [3, 5, 10, None]}),
    ('GP', build_gp, {}),
]

results = {}

for name, builder, param_grid in models_def:
    preds = np.empty(N)
    for i in range(N):
        tr_idx = np.delete(np.arange(N), i)
        Xtr, ytr = X[tr_idx], y[tr_idx]
        Xte = X[[i]]

        if name == 'GP':
            model = builder()
            model.fit(Xtr, ytr)
            preds[i] = model.predict(Xte)[0]
        else:
            pipe = builder()
            if param_grid and len(param_grid) > 1:
                gs = GridSearchCV(pipe, param_grid, cv=inner_cv, scoring='r2', n_jobs=1, error_score='raise')
                gs.fit(Xtr, ytr)
                preds[i] = gs.predict(Xte)[0]
            else:
                pipe.fit(Xtr, ytr)
                preds[i] = pipe.predict(Xte)[0]

    r2 = r2_score(y, preds)
    r, p = pearsonr(y, preds)
    rmse = np.sqrt(mean_squared_error(y, preds))
    mae = mean_absolute_error(y, preds)
    slope, intercept, *_ = linregress(y, preds)

    results[name] = {
        'CV_R2': round(r2, 4),
        'CV_r': round(r, 4),
        'CV_p': float(f'{p:.3g}'),
        'RMSE': round(rmse, 4),
        'MAE': round(mae, 4),
        'calib_slope': round(slope, 4),
        'calib_intercept': round(intercept, 4),
    }
    print(f'  {name:15s}  R²={r2:.6f}  r={r:.6f}  RMSE={rmse:.6f}  MAE={mae:.6f}  slope={slope:.4f}')

# Cluster law
cluster_preds = np.empty(N)
for i in range(N):
    tr_idx = np.delete(np.arange(N), i)
    Xtr, ytr = X[tr_idx], y[tr_idx]
    Xte = X[[i]]
    cluster_preds[i] = cluster_predict(Xtr, ytr, Xte, SEED + i)

cr2 = r2_score(y, cluster_preds)
cr, cp = pearsonr(y, cluster_preds)
crmse = np.sqrt(mean_squared_error(y, cluster_preds))
cmae = mean_absolute_error(y, cluster_preds)
cslope, cint, *_ = linregress(y, cluster_preds)

results['ClusterLaw'] = {
    'CV_R2': round(cr2, 4),
    'CV_r': round(cr, 4),
    'CV_p': float(f'{cp:.3g}'),
    'RMSE': round(crmse, 4),
    'MAE': round(cmae, 4),
    'calib_slope': round(cslope, 4),
    'calib_intercept': round(cint, 4),
}
print(f'  {"ClusterLaw":15s}  R²={cr2:.6f}  r={cr:.6f}  RMSE={crmse:.6f}  MAE={cmae:.6f}  slope={cslope:.4f}')

# ============ Verdict ============
smooth_models = [m for m in results if m != 'ClusterLaw']
smooth_best = max(smooth_models, key=lambda m: results[m]['CV_R2'])
smooth_best_r2 = results[smooth_best]['CV_R2']

if smooth_best_r2 - cr2 > 0.02:
    verdict = 'CONTINUOUS-GEOMETRIC-STRUCTURE'
elif cr2 - smooth_best_r2 > 0.02:
    verdict = 'GENUINE-CATEGORICAL-ORGANIZATION'
else:
    verdict = 'CONTINUOUS-GEOMETRIC-STRUCTURE'

print(f'\nBest smooth: {smooth_best} (R²={smooth_best_r2:.4f})')
print(f'ClusterLaw: R²={cr2:.4f}')
print(f'Verdict: {verdict}')

# ============ Save ============
results_df = pd.DataFrame(results).T
results_df.index.name = 'model'
results_df.to_csv('/home/student/sgp_core_v2/phases/phase543/phase543_model_comparison.csv')
results_df.reset_index(inplace=True)

summary = {
    'phase': 543,
    'best_model': smooth_best,
    'best_CV_R2': round(smooth_best_r2, 4),
    'cluster_law_CV_R2': round(cr2, 4),
    'best_smooth_model': smooth_best,
    'best_smooth_CV_R2': round(smooth_best_r2, 4),
    'linear_CV_R2': results['Linear']['CV_R2'],
    'R2_delta_smooth_vs_cluster': round(smooth_best_r2 - cr2, 4),
    'verdict': verdict,
}

pd.DataFrame([summary]).to_csv('/home/student/sgp_core_v2/phases/phase543/phase543_summary.csv', index=False)

# ============ Residual diagnostics ============
full_km = KMeans(n_clusters=K_CLUSTER, random_state=SEED, n_init=100)
full_km.fit(X)
D = cdist(X, full_km.cluster_centers_)
sd = np.sort(D, axis=1)
d1, d2, d3 = sd[:, 0], sd[:, 1], sd[:, 2]
margin = d2 - d1
spread = (d1 + d2) / (d1 + d2 + d3 + 1e-8)
hybridity = (1.0 / (1.0 + margin)) * (1.0 - spread)

features_all = ['CSR', 'ADI', 'RBS', 'RTP', 'SRD']
from itertools import combinations
all_subsets = []
for r in range(2, 6):
    all_subsets.extend(list(combinations(features_all, r)))
consensus_matrix = np.zeros((N, N))
for subset in all_subsets:
    idx = [features_all.index(f) for f in subset]
    Xsub = StandardScaler().fit_transform(base[features_all].values[:, idx])
    km = KMeans(n_clusters=K_CLUSTER, random_state=SEED, n_init=50)
    sl = km.fit_predict(Xsub)
    for i in range(N):
        consensus_matrix[i, sl == sl[i]] += 1
consensus_matrix /= len(all_subsets)
consensus_per_sys = np.array([(consensus_matrix[i].sum() - 1) / (N - 1) for i in range(N)])

resid_diag = pd.DataFrame({
    'system': base['name'],
    'true': y,
    'pred_cluster': cluster_preds,
    'pred_linear': results['Linear'].get('pred', np.nan),
    'residual_cluster': y - cluster_preds,
    'hybridity': hybridity,
    'margin': margin,
    'spread': spread,
    'consensus': consensus_per_sys,
})
resid_diag.to_csv('/home/student/sgp_core_v2/phases/phase543/phase543_residual_diagnostics.csv', index=False)

print('\nResidual vs interface (cluster law):')
for metric in ['hybridity', 'margin', 'spread', 'consensus']:
    r, p = pearsonr(y - cluster_preds, resid_diag[metric].values)
    print(f'  residual vs {metric:10s}: r={r:+.4f}  p={p:.3g}')

print('\n=== PHASE 543 COMPLETE ===')
