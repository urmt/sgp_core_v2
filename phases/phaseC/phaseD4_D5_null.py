"""
Phase D4-D5 — Transferal Fertility + Null Universe Tests.
D4: Do high-fertility systems transfer better?
D5: Do transition→fertility findings survive randomization?
"""
import numpy as np, pandas as pd, warnings
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import r2_score
from sklearn.model_selection import LeaveOneOut
from scipy.stats import pearsonr, spearmanr, entropy
warnings.filterwarnings('ignore')

CSV = '/home/student/sgp_core_v2/phases/phaseC/phaseC_metrics.csv'
df = pd.read_csv(CSV)
domains = sorted(df['domain'].unique())
cols = ['CSR','RBS','ADI','RTP','SRD']
fertility_targets = [c for c in df.columns if c.startswith('fertility_')]
K = 30
N_PERM = 200  # permutations for null

print('='*70)
print('PHASE D4 — TRANSFERAL FERTILITY')
print('='*70)
print('Testing whether high-fertility systems transfer better across domains')

# Compute per-system transition metrics from D1-D2 approach (fast version)
print('\nComputing transition metrics for all systems...')
sys_ambiguity = {}
for domain in domains:
    m = df['domain'] == domain
    dm = df.loc[m].copy().reset_index(drop=True)
    N = len(dm)
    X = StandardScaler().fit_transform(dm[cols].values)
    nbrs = NearestNeighbors(n_neighbors=min(K+1, N)).fit(X)
    _, indices = nbrs.kneighbors(X)
    nb_idx = indices[:, 1:]
    
    # Use fertility_state_diversity as primary fertility metric
    t = 'fertility_state_diversity'
    y = dm[t].values
    if np.std(y) < 1e-10: continue
    
    for i in range(N):
        nb = nb_idx[i]
        if len(nb) < 5:
            sys_ambiguity[(domain, i)] = 0.0; continue
        r2_vec = np.zeros(5)
        for j, c in enumerate(cols):
            xj = dm.iloc[nb][c].values.reshape(-1, 1)
            yj = y[nb]
            if np.std(xj) < 1e-12 or np.std(yj) < 1e-12: continue
            r2_vec[j] = r2_score(yj, LinearRegression().fit(xj, yj).predict(xj))
        r2_vec = np.clip(r2_vec, 0, None)
        s = r2_vec.sum() + 1e-10
        amb = 1 - r2_vec.max() / s
        sys_ambiguity[(domain, i)] = amb

# For each domain, split systems into high-fertility and low-fertility
print('\nCross-domain transfer: high-fert vs low-fert systems')
loocv = LeaveOneOut()
all_transfer_results = []

for src_domain in domains:
    m_src = df['domain'] == src_domain
    src = df[m_src].copy()
    N_src = len(src)
    
    # Determine high/low fertility split (median)
    fert_vals = src[fertility_targets[0]].values
    med_fert = np.median(fert_vals)
    high_mask = fert_vals >= med_fert
    low_mask = fert_vals < med_fert
    
    for tgt_domain in domains:
        if tgt_domain == src_domain: continue
        m_tgt = df['domain'] == tgt_domain
        tgt = df[m_tgt].copy()
        y_tgt = tgt[fertility_targets[0]].values
        if np.std(y_tgt) < 1e-10: continue
        
        # Train on high-fert systems from src, predict tgt
        X_high = StandardScaler().fit_transform(src[cols].values[high_mask])
        y_high = fert_vals[high_mask]
        if len(X_high) < 5: continue
        lr = LinearRegression().fit(X_high, y_high)
        X_tgt = StandardScaler().fit_transform(tgt[cols].values)
        preds = lr.predict(X_tgt)
        r2_high = r2_score(y_tgt, preds)
        
        # Train on low-fert systems from src
        X_low = StandardScaler().fit_transform(src[cols].values[low_mask])
        y_low = fert_vals[low_mask]
        if len(X_low) < 5: continue
        lr = LinearRegression().fit(X_low, y_low)
        preds = lr.predict(X_tgt)
        r2_low = r2_score(y_tgt, preds)
        
        all_transfer_results.append({
            'src': src_domain, 'tgt': tgt_domain,
            'r2_high': r2_high, 'r2_low': r2_low,
            'n_high': high_mask.sum(), 'n_low': low_mask.sum(),
        })
        print(f'  {src_domain:25s} → {tgt_domain:25s}: high-R²={r2_high:.4f}, low-R²={r2_low:.4f}')

tr = pd.DataFrame(all_transfer_results)
if len(tr) > 0:
    print(f'\nSummary:')
    print(f'  Mean high-fert transfer R²: {tr["r2_high"].mean():.4f}')
    print(f'  Mean low-fert transfer R²:  {tr["r2_low"].mean():.4f}')
    high_wins = (tr['r2_high'] > tr['r2_low']).sum()
    low_wins = (tr['r2_low'] > tr['r2_high']).sum()
    print(f'  High-fert wins: {high_wins}/{len(tr)}, low-fert wins: {low_wins}/{len(tr)}')

# D4b: High-ambiguity systems — do they transfer better?
print(f'\nCross-domain transfer: high-amb vs low-amb systems')
tr_amb = []
for src_domain in domains:
    m_src = df['domain'] == src_domain
    src = df[m_src].copy().reset_index(drop=True)
    N_src = len(src)
    
    amb_vals = np.array([sys_ambiguity.get((src_domain, i), 0) for i in range(N_src)])
    med_amb = np.median(amb_vals)
    high_mask = amb_vals >= med_amb
    low_mask = amb_vals < med_amb
    
    if high_mask.sum() < 5 or low_mask.sum() < 5: continue
    fert_src = src[fertility_targets[0]].values
    
    for tgt_domain in domains:
        if tgt_domain == src_domain: continue
        m_tgt = df['domain'] == tgt_domain
        tgt = df[m_tgt].copy()
        y_tgt = tgt[fertility_targets[0]].values
        if np.std(y_tgt) < 1e-10: continue
        
        X_h = StandardScaler().fit_transform(src[cols].values[high_mask])
        y_h = fert_src[high_mask]
        lr = LinearRegression().fit(X_h, y_h)
        r2_h = r2_score(y_tgt, lr.predict(StandardScaler().fit_transform(tgt[cols].values)))
        
        X_l = StandardScaler().fit_transform(src[cols].values[low_mask])
        y_l = fert_src[low_mask]
        lr = LinearRegression().fit(X_l, y_l)
        r2_l = r2_score(y_tgt, lr.predict(StandardScaler().fit_transform(tgt[cols].values)))
        
        tr_amb.append({'src': src_domain, 'tgt': tgt_domain, 'r2_high_amb': r2_h, 'r2_low_amb': r2_l})

tra = pd.DataFrame(tr_amb)
if len(tra) > 0:
    print(f'  Mean high-amb transfer R²: {tra["r2_high_amb"].mean():.4f}')
    print(f'  Mean low-amb transfer R²:  {tra["r2_low_amb"].mean():.4f}')

print(f'\n{"="*70}')
print('PHASE D5 — NULL UNIVERSE TESTS')
print('='*70)

# Compute true ambiguity→fertility correlation per domain from D1-D2 output
# We recompute here using the same method, but for the primary target only (fast)
true_corrs = {}
primary_target = fertility_targets[0]
for domain in domains:
    m = df['domain'] == domain
    dm = df[m].copy().reset_index(drop=True)
    N = len(dm)
    X = StandardScaler().fit_transform(dm[cols].values)
    nbrs = NearestNeighbors(n_neighbors=min(K+1, N)).fit(X)
    _, indices = nbrs.kneighbors(X)
    nb_idx = indices[:, 1:]
    y = dm[primary_target].values
    if np.std(y) < 1e-10:
        true_corrs[domain] = 0.0; continue
    amb_vals = np.zeros(N)
    for i in range(N):
        nb = nb_idx[i]
        if len(nb) < 5: continue
        r2_vec = np.zeros(5)
        for j, c in enumerate(cols):
            xj = dm.iloc[nb][c].values.reshape(-1, 1)
            yj = y[nb]
            if np.std(xj) < 1e-12 or np.std(yj) < 1e-12: continue
            r2_vec[j] = r2_score(yj, LinearRegression().fit(xj, yj).predict(xj))
        r2_vec = np.clip(r2_vec, 0, None)
        amb_vals[i] = 1 - r2_vec.max() / (r2_vec.sum() + 1e-10)
    r, _ = pearsonr(amb_vals, y)
    true_corrs[domain] = r

print(f'\nTRUE effects (mean r across targets):')
for d in domains:
    print(f'  {d:25s}: r={true_corrs[d]:+.4f}')

# Null test 1: Shuffle fertility within domain
print(f'\nNull Test 1 — Shuffle fertility within domain ({N_PERM} perms):')
null_corrs = {d: [] for d in domains}
for _ in range(N_PERM):
    for domain in domains:
        m = df['domain'] == domain
        dm = df[m].copy().reset_index(drop=True)
        N = len(dm)
        y_shuff = dm[fertility_targets[0]].values.copy()
        np.random.shuffle(y_shuff)
        
        X = StandardScaler().fit_transform(dm[cols].values)
        nbrs = NearestNeighbors(n_neighbors=min(K+1, N)).fit(X)
        _, indices = nbrs.kneighbors(X)
        nb_idx = indices[:, 1:]
        
        amb_vals = np.zeros(N)
        for i in range(N):
            nb = nb_idx[i]
            if len(nb) < 5: continue
            r2_vec = np.zeros(5)
            for j, c in enumerate(cols):
                xj = dm.iloc[nb][c].values.reshape(-1, 1)
                yj = y_shuff[nb]
                if np.std(xj) < 1e-12 or np.std(yj) < 1e-12: continue
                r2_vec[j] = r2_score(yj, LinearRegression().fit(xj, yj).predict(xj))
            r2_vec = np.clip(r2_vec, 0, None)
            amb_vals[i] = 1 - r2_vec.max() / (r2_vec.sum() + 1e-10)
        
        r, _ = pearsonr(amb_vals, y_shuff)
        null_corrs[domain].append(r)

# Compute p-values
print(f'  {"Domain":25s} {"True r":8s} {"Null mean":10s} {"Null std":10s} {"p-value":8s}')
for d in domains:
    nc = np.array(null_corrs[d])
    p = (np.sum(np.abs(nc) >= np.abs(true_corrs[d])) + 1) / (N_PERM + 1)
    print(f'  {d:25s} {true_corrs[d]:+.4f}  {nc.mean():+.4f}     {nc.std():.4f}     {p:.4f}')

# Null test 2: Shuffle descriptor labels
print(f'\nNull Test 2 — Shuffle descriptor column labels ({N_PERM} perms):')
null_desc_corrs = {d: [] for d in domains}
for _ in range(N_PERM):
    cols_shuff = cols.copy()
    np.random.shuffle(cols_shuff)
    df_shuff = df.copy()
    # Remap descriptor columns
    for orig, shuff in zip(cols, cols_shuff):
        df_shuff[orig] = df[shuff].values
    
    for domain in domains:
        m = df_shuff['domain'] == domain
        dm = df_shuff[m].copy().reset_index(drop=True)
        N = len(dm)
        X = StandardScaler().fit_transform(dm[cols].values)
        nbrs = NearestNeighbors(n_neighbors=min(K+1, N)).fit(X)
        _, indices = nbrs.kneighbors(X)
        nb_idx = indices[:, 1:]
        
        y = dm[fertility_targets[0]].values
        amb_vals = np.zeros(N)
        for i in range(N):
            nb = nb_idx[i]
            if len(nb) < 5: continue
            r2_vec = np.zeros(5)
            for j, c in enumerate(cols):
                xj = dm.iloc[nb][c].values.reshape(-1, 1)
                yj = y[nb]
                if np.std(xj) < 1e-12 or np.std(yj) < 1e-12: continue
                r2_vec[j] = r2_score(yj, LinearRegression().fit(xj, yj).predict(xj))
            r2_vec = np.clip(r2_vec, 0, None)
            amb_vals[i] = 1 - r2_vec.max() / (r2_vec.sum() + 1e-10)
        
        r, _ = pearsonr(amb_vals, y)
        null_desc_corrs[domain].append(r)

print(f'  {"Domain":25s} {"True r":8s} {"Null mean":10s} {"p-value":8s}')
for d in domains:
    nc = np.array(null_desc_corrs[d])
    p = (np.sum(np.abs(nc) >= np.abs(true_corrs[d])) + 1) / (N_PERM + 1)
    print(f'  {d:25s} {true_corrs[d]:+.4f}  {nc.mean():+.4f}     {p:.4f}')

# Null test 3: Randomize neighborhoods
print(f'\nNull Test 3 — Random neighborhoods ({N_PERM} perms):')
null_nbr_corrs = {d: [] for d in domains}
for _ in range(N_PERM):
    for domain in domains:
        m = df['domain'] == domain
        dm = df[m].copy().reset_index(drop=True)
        N = len(dm)
        X = StandardScaler().fit_transform(dm[cols].values)
        # Random neighborhoods (instead of nearest neighbors)
        nb_idx = np.array([np.random.choice(N, min(K, N-1), replace=False) for _ in range(N)])
        
        y = dm[fertility_targets[0]].values
        amb_vals = np.zeros(N)
        for i in range(N):
            nb = nb_idx[i]
            if len(nb) < 5: continue
            r2_vec = np.zeros(5)
            for j, c in enumerate(cols):
                xj = dm.iloc[nb][c].values.reshape(-1, 1)
                yj = y[nb]
                if np.std(xj) < 1e-12 or np.std(yj) < 1e-12: continue
                r2_vec[j] = r2_score(yj, LinearRegression().fit(xj, yj).predict(xj))
            r2_vec = np.clip(r2_vec, 0, None)
            amb_vals[i] = 1 - r2_vec.max() / (r2_vec.sum() + 1e-10)
        
        r, _ = pearsonr(amb_vals, y)
        null_nbr_corrs[domain].append(r)

print(f'  {"Domain":25s} {"True r":8s} {"Null mean":10s} {"p-value":8s}')
for d in domains:
    nc = np.array(null_nbr_corrs[d])
    p = (np.sum(np.abs(nc) >= np.abs(true_corrs[d])) + 1) / (N_PERM + 1)
    print(f'  {d:25s} {true_corrs[d]:+.4f}  {nc.mean():+.4f}     {p:.4f}')

print(f'\n{"="*70}')
print('NULL SIGNIFICANCE SUMMARY')
print('='*70)
print('A finding is significant if p < 0.05 in ALL three null tests.')
print()
for d in domains:
    p1 = (np.sum(np.abs(np.array(null_corrs[d])) >= np.abs(true_corrs[d])) + 1) / (N_PERM + 1)
    p2 = (np.sum(np.abs(np.array(null_desc_corrs[d])) >= np.abs(true_corrs[d])) + 1) / (N_PERM + 1)
    p3 = (np.sum(np.abs(np.array(null_nbr_corrs[d])) >= np.abs(true_corrs[d])) + 1) / (N_PERM + 1)
    sig = all(p < 0.05 for p in [p1, p2, p3])
    print(f'  {d:25s}: true r={true_corrs[d]:+.4f}  p_fert={p1:.4f}  p_desc={p2:.4f}  p_nbr={p3:.4f}  {"SIGNIFICANT" if sig else "ns"}')

print(f'\n{"="*70}')
print('D4-D5 COMPLETE')
print('='*70)
