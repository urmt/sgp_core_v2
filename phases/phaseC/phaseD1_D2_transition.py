"""
Phase D1-D2 — Transitional Fertility.
Tests: does fertility peak near organizational geometry transitions?
"""
import numpy as np, pandas as pd, warnings, time
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import r2_score
from scipy.stats import pearsonr, spearmanr, entropy
warnings.filterwarnings('ignore')

CSV = '/home/student/sgp_core_v2/phases/phaseC/phaseC_metrics.csv'
df = pd.read_csv(CSV)
domains = sorted(df['domain'].unique())
cols = ['CSR','RBS','ADI','RTP','SRD']
fertility_targets = [c for c in df.columns if c.startswith('fertility_')]
K = 30

print('='*70)
print('PHASE D1 — GEOMETRY TRANSITION DETECTION')
print(f'{len(df)} systems, {len(domains)} domains, k={K} neighbors')
print('='*70)

all_rows = []
for domain in domains:
    t0 = time.time()
    m = df['domain'] == domain
    dm = df.loc[m].copy().reset_index(drop=True)
    N = len(dm)
    X = StandardScaler().fit_transform(dm[cols].values)
    nbrs = NearestNeighbors(n_neighbors=min(K+1, N)).fit(X)
    _, indices = nbrs.kneighbors(X)
    nb_idx = indices[:, 1:]
    
    for t in fertility_targets:
        y = dm[t].values
        if np.std(y) < 1e-10:
            for i in range(N):
                all_rows.append(dict(sys_idx=i, domain=domain, target=t,
                    best_desc='NONE', desc_entropy=0.0, ambiguity=0.0, dominance=0.0,
                    fertility=float(y[i]), nbr_pred_r2=0.0, top_r2=0.0,
                    r2_CSR=0.0, r2_RBS=0.0, r2_ADI=0.0, r2_RTP=0.0, r2_SRD=0.0))
            continue
        
        for i in range(N):
            nb = nb_idx[i]
            if len(nb) < 5:
                all_rows.append(dict(sys_idx=i, domain=domain, target=t,
                    best_desc='NONE', desc_entropy=0.0, ambiguity=0.0, dominance=0.0,
                    fertility=float(y[i]), nbr_pred_r2=0.0, top_r2=0.0,
                    r2_CSR=0.0, r2_RBS=0.0, r2_ADI=0.0, r2_RTP=0.0, r2_SRD=0.0))
                continue
            
            r2_vec = np.zeros(5)
            for j, c in enumerate(cols):
                xj = dm.iloc[nb][c].values.reshape(-1, 1)
                yj = y[nb]
                if np.std(xj) < 1e-12 or np.std(yj) < 1e-12: continue
                p = LinearRegression().fit(xj, yj).predict(xj)
                r2_vec[j] = r2_score(yj, p)
            
            r2_vec = np.clip(r2_vec, 0, None)
            s = r2_vec.sum() + 1e-10
            best = np.argmax(r2_vec)
            de = entropy(r2_vec / s + 1e-10) / np.log(5)
            amb = 1 - r2_vec[best] / s
            
            # Held-out prediction using best descriptor model
            bc = cols[best]
            lr = LinearRegression().fit(dm.iloc[nb][bc].values.reshape(-1,1), y[nb])
            pred = lr.predict(dm.iloc[[i]][bc].values.reshape(-1,1))[0]
            npr2 = 1 - (y[i]-pred)**2 / (np.var(y) + 1e-10)
            
            all_rows.append(dict(sys_idx=i, domain=domain, target=t,
                best_desc=bc, desc_entropy=float(de), ambiguity=float(amb),
                dominance=float(r2_vec[best]/s), fertility=float(y[i]),
                nbr_pred_r2=float(npr2), top_r2=float(r2_vec[best]),
                r2_CSR=float(r2_vec[0]), r2_RBS=float(r2_vec[1]),
                r2_ADI=float(r2_vec[2]), r2_RTP=float(r2_vec[3]), r2_SRD=float(r2_vec[4])))
    
    print(f'  {domain}: {N} systems, {len(fertility_targets)} targets → {time.time()-t0:.1f}s')

rd = pd.DataFrame(all_rows)
print(f'\nTotal profiles: {len(rd)}')
print(f'Best descriptor distribution:\n{rd["best_desc"].value_counts().to_dict()}')

print(f'\n{"="*70}')
print('PHASE D2 — FERTILITY VS TRANSITIONALITY')
print('='*70)

print('\nGLOBAL correlations (fertility vs transition metrics):')
for m in ['desc_entropy', 'ambiguity', 'dominance', 'top_r2']:
    r, p = pearsonr(rd[m], rd['fertility'])
    rho, rp = spearmanr(rd[m], rd['fertility'])
    print(f'  fertility × {m:15s}: r={r:.4f} (p={p:.4g})  ρ={rho:.4f} (p={rp:.4g})')

print('\nPER-DOMAIN (fertility × ambiguity, by target):')
for domain in domains:
    dm = rd[rd['domain'] == domain]
    vals = []
    for t in fertility_targets:
        sub = dm[dm['target'] == t]
        if len(sub) < 10: continue
        r, p = pearsonr(sub['ambiguity'], sub['fertility'])
        vals.append(r)
        if abs(r) > 0.12 or p < 0.01:
            print(f'  {domain:25s} {t[:30]:30s}: r={r:.4f} (p={p:.4g})')
    print(f'  {domain:25s} {"(mean)":30s}: mean r={np.mean(vals):.4f} (over {len(vals)} targets)')

print('\nHIGH vs LOW ambiguity — fertility comparison:')
for t in fertility_targets:
    sub = rd[rd['target'] == t]
    med = sub['ambiguity'].median()
    h = sub[sub['ambiguity'] >= med]['fertility'].mean()
    l = sub[sub['ambiguity'] < med]['fertility'].mean()
    r, p = pearsonr(sub['ambiguity'], sub['fertility'])
    print(f'  {t:35s}: hi={h:.4f} lo={l:.4f} Δ={h-l:+.4f}  r={r:.4f} p={p:.4g}')

print('\nPER-DOMAIN high-vs-low ambiguity:')
for domain in domains:
    sub = rd[(rd['domain']==domain) & (rd['target']==fertility_targets[0])]
    if len(sub) < 20: continue
    med = sub['ambiguity'].median()
    h = sub[sub['ambiguity'] >= med]['fertility'].mean()
    l = sub[sub['ambiguity'] < med]['fertility'].mean()
    r, _ = pearsonr(sub['ambiguity'], sub['fertility'])
    print(f'  {domain:25s}: hi={h:.4f} lo={l:.4f} Δ={h-l:+.4f}  r={r:.4f}')

print(f'\n{"="*70}')
print('D1-D2 COMPLETE')
print('='*70)
