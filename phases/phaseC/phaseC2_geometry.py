"""
Phase C2 — Per-Domain Geometry Discovery (optimized).
Intrinsic dimensionality, manifold topology, descriptor dominance, predictive structure.
"""
import numpy as np, pandas as pd, warnings
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import LeaveOneOut, cross_val_score
from sklearn.metrics import r2_score
from scipy.stats import pearsonr
warnings.filterwarnings('ignore')

CSV = '/home/student/sgp_core_v2/phases/phaseC/phaseC_metrics.csv'
df = pd.read_csv(CSV)
domains = sorted(df['domain'].unique())
cols = ['CSR','RBS','ADI','RTP','SRD']
targets = [c for c in df.columns if c.startswith('stability_') or c.startswith('fertility_')]

print('='*70); print('PHASE C2 — PER-DOMAIN GEOMETRY DISCOVERY'); print('='*70)

summary = []
for domain in domains:
    m = df['domain'] == domain; N = m.sum()
    X = StandardScaler().fit_transform(df.loc[m, cols].values)
    
    print(f'\n{"─"*60}'); print(f'DOMAIN: {domain}  (N={N})'); print(f'{"─"*60}')
    
    # 1. Intrinsic dim (PCA)
    pca = PCA().fit(X); ev = pca.explained_variance_ratio_
    cv = np.cumsum(ev)
    n90 = int(np.argmax(cv >= 0.90) + 1) if np.any(cv >= 0.90) else 5
    n95 = int(np.argmax(cv >= 0.95) + 1) if np.any(cv >= 0.95) else 5
    print(f'  Intrinsic dim: 90%={n90}, 95%={n95}, PC1={ev[0]:.4f}, PC2={ev[1]:.4f}')
    print(f'  Loadings: ' + ' '.join(f'{c}:{pca.components_[0,i]:+.3f}' for i,c in enumerate(cols)))
    
    # 2. Hopkins clustering statistic (sample)
    from sklearn.neighbors import NearestNeighbors
    nbrs = NearestNeighbors(n_neighbors=2).fit(X)
    w_sum = nbrs.kneighbors(X)[0][:,1].sum()
    Xu = np.random.uniform(X.min(axis=0), X.max(axis=0), size=(min(500,N),5))
    b_sum = NearestNeighbors(n_neighbors=1).fit(X).kneighbors(Xu)[0][:,0].sum()
    hopkins = b_sum / (b_sum + w_sum + 1e-10)
    print(f'  Hopkins: {hopkins:.4f}  (clustered if <0.5)')
    
    # 3. Local linearity (reconstruction from 5-NN)
    nbrs5 = NearestNeighbors(n_neighbors=6).fit(X)
    idx5 = nbrs5.kneighbors(X, return_distance=False)
    local_r2 = []
    for i in range(min(200, N)):
        nb = idx5[i, 1:]
        if len(nb) < 3: continue
        pred = X[nb].mean(axis=0)
        r2 = 1 - np.sum((X[i]-pred)**2) / (np.sum((X[i]-X.mean(axis=0))**2)+1e-10)
        local_r2.append(r2)
    lin_r2 = np.mean(local_r2) if local_r2 else 0
    print(f'  Local linearity: {lin_r2:.4f}  (linear if >0.9)')
    
    # 4. Full-model LOOCV for all targets (efficient)
    print(f'  Predictive LOOCV:')
    loo = LeaveOneOut()
    target_r2 = {}; target_coefs = {}
    for t in targets:
        y = y_orig = df.loc[m, t].values
        if np.std(y) < 1e-10:
            print(f'    {t:30s}: CONSTANT'); target_r2[t] = 0; continue
        p = np.empty(N); all_coefs = np.zeros((N, 5))
        for fi, (tr, te) in enumerate(loo.split(X)):
            X_tr = StandardScaler().fit_transform(df.loc[m, cols].values[tr])
            X_te = StandardScaler().fit(df.loc[m, cols].values[tr]).transform(df.loc[m, cols].values[te])
            lr = LinearRegression().fit(X_tr, y[tr])
            p[te[0]] = lr.predict(X_te)[0]
            all_coefs[fi] = lr.coef_
        r2 = r2_score(y, p); r, _ = pearsonr(y, p)
        target_r2[t] = r2
        target_coefs[t] = all_coefs.mean(axis=0)
        print(f'    {t:30s}: R²={r2:.4f}, r={r:.4f}')
    
    # 5. Descriptor importance (from mean |coef| across targets)
    mean_abs_coef = np.abs(np.mean([target_coefs[t] for t in targets if t in target_coefs], axis=0))
    desc_imp = {c: mean_abs_coef[i] for i,c in enumerate(cols)}
    best_desc = max(desc_imp, key=desc_imp.get)
    print(f'  Descriptor importance (mean |coef|):')
    for c in cols: print(f'    {c}: {desc_imp[c]:.4f}')
    print(f'  Best descriptor: {best_desc}')
    
    # 6. Geometry type
    geo = f'{"LINEAR" if lin_r2>0.9 else "NL"}/{"CLUST" if hopkins<0.5 else "DISP"}/{"P1" if ev[0]>0.5 else "BAL"}/{best_desc}'
    mean_r2 = np.mean([v for v in target_r2.values() if v > -1])
    print(f'  Geometry: {geo}  |  Mean R²={mean_r2:.4f}')
    
    summary.append({'domain':domain,'N':N,'n95':n95,'PC1':ev[0],'hopkins':hopkins,
                    'linearity':lin_r2,'best_desc':best_desc,'mean_r2':mean_r2,'geo':geo})

print(f'\n{"="*70}')
print('CROSS-DOMAIN COMPARISON')
print(f'{"="*70}')
print(f'{"Domain":25s} {"dim":4s} {"PC1":6s} {"Hopk":6s} {"Lin":6s} {"Best":6s} {"R²":6s}  Geometry')
print(f'{"─"*70}')
for r in summary:
    print(f'{r["domain"]:25s} {r["n95"]:4d} {r["PC1"]:.3f} {r["hopkins"]:.3f} {r["linearity"]:.3f} {r["best_desc"]:6s} {r["mean_r2"]:.3f}  {r["geo"]}')
print(f'\nMean effective dim: {np.mean([r["n95"] for r in summary]):.1f}')
print(f'Mean PC1 variance:  {np.mean([r["PC1"] for r in summary]):.3f}')
print(f'Mean Hopkins:       {np.mean([r["hopkins"] for r in summary]):.3f}')
print(f'Mean linearity:     {np.mean([r["linearity"] for r in summary]):.3f}')
print(f'Mean R²:            {np.mean([r["mean_r2"] for r in summary]):.3f}')
print(f'\nBest descriptor distribution:')
for b in set(r['best_desc'] for r in summary):
    cnt = sum(1 for r in summary if r['best_desc'] == b)
    print(f'  {b}: {cnt} domains')
