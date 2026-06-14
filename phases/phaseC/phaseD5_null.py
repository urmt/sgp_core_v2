"""
Phase D5 — Null Universe Tests (optimized).
"""
import numpy as np, pandas as pd, warnings, time
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import r2_score
from scipy.stats import pearsonr
warnings.filterwarnings('ignore')

CSV = '/home/student/sgp_core_v2/phases/phaseC/phaseC_metrics.csv'
df = pd.read_csv(CSV)
cols = ['CSR','RBS','ADI','RTP','SRD']
target = 'fertility_state_diversity'
K, N_PERM = 30, 200

# Focus on 3 domains: 2 positive signal, 1 negative, 1 null
focus_domains = ['branching', 'population', 'graph_diffusion', 'cellular_automata']

print('='*70)
print('PHASE D5 — NULL UNIVERSE TESTS (OPTIMIZED)')
print(f'{N_PERM} permutations, {len(focus_domains)} domains, target={target}')
print('='*70)

# Precompute neighbor structure + ambiguity for each domain (true + reusable)
domain_data = {}
for domain in focus_domains:
    m = df['domain'] == domain
    dm = df[m].copy().reset_index(drop=True)
    N = len(dm)
    X = StandardScaler().fit_transform(dm[cols].values)
    nbrs = NearestNeighbors(n_neighbors=min(K+1, N)).fit(X)
    _, indices = nbrs.kneighbors(X)
    nb_idx = indices[:, 1:]  # precomputed neighbors for all permutations
    
    y = dm[target].values
    domain_data[domain] = {'dm': dm, 'N': N, 'X': X, 'nb_idx': nb_idx, 'y': y}

def compute_ambiguity(y, nb_idx, dm):
    N = len(y)
    amb = np.zeros(N)
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
        amb[i] = 1 - r2_vec.max() / (r2_vec.sum() + 1e-10)
    return amb

# True effects
print(f'\nTrue effects:')
true_r = {}
for d in focus_domains:
    dd = domain_data[d]
    amb = compute_ambiguity(dd['y'], dd['nb_idx'], dd['dm'])
    r, _ = pearsonr(amb, dd['y'])
    true_r[d] = r
    print(f'  {d}: r={r:.4f}')

# Null test 1: Shuffle fertility (within domain)
print(f'\nNull 1 — Shuffle fertility ({N_PERM} perms)...')
t0 = time.time()
null1 = {d: [] for d in focus_domains}
for perm in range(N_PERM):
    for d in focus_domains:
        dd = domain_data[d]
        y_shuff = dd['y'].copy()
        np.random.shuffle(y_shuff)
        amb = compute_ambiguity(y_shuff, dd['nb_idx'], dd['dm'])
        r, _ = pearsonr(amb, y_shuff)
        null1[d].append(r)
    if (perm+1) % 50 == 0: print(f'  {perm+1}/{N_PERM} ({time.time()-t0:.0f}s)', flush=True)
print(f'  Done in {time.time()-t0:.0f}s')

print(f'\nNull 1 Results:')
print(f'  {"Domain":20s} {"True r":8s} {"Null μ":8s} {"Null σ":8s} {"p":8s}')
for d in focus_domains:
    nc = np.array(null1[d])
    p = (np.sum(np.abs(nc) >= np.abs(true_r[d])) + 1) / (N_PERM + 1)
    print(f'  {d:20s} {true_r[d]:+.4f}  {nc.mean():+.4f}  {nc.std():.4f}  {p:.4f}')

# Null test 2: Shuffle descriptor labels
print(f'\nNull 2 — Shuffle descriptors ({N_PERM} perms)...')
t0 = time.time()
null2 = {d: [] for d in focus_domains}
for perm in range(N_PERM):
    cols_shuff = cols.copy()
    np.random.shuffle(cols_shuff)
    for d in focus_domains:
        dd = domain_data[d]
        dm_s = dd['dm'].copy()
        for orig, shuff in zip(cols, cols_shuff):
            dm_s[orig] = dd['dm'][shuff].values
        amb = compute_ambiguity(dd['y'], dd['nb_idx'], dm_s)
        r, _ = pearsonr(amb, dd['y'])
        null2[d].append(r)
    if (perm+1) % 50 == 0: print(f'  {perm+1}/{N_PERM} ({time.time()-t0:.0f}s)', flush=True)
print(f'  Done in {time.time()-t0:.0f}s')

print(f'\nNull 2 Results:')
for d in focus_domains:
    nc = np.array(null2[d])
    p = (np.sum(np.abs(nc) >= np.abs(true_r[d])) + 1) / (N_PERM + 1)
    print(f'  {d:20s} {true_r[d]:+.4f}  {nc.mean():+.4f}  {nc.std():.4f}  {p:.4f}')

# Null test 3: Random neighborhoods
print(f'\nNull 3 — Random neighborhoods ({N_PERM} perms)...')
t0 = time.time()
null3 = {d: [] for d in focus_domains}
for perm in range(N_PERM):
    for d in focus_domains:
        dd = domain_data[d]
        N = dd['N']
        rnb = np.array([np.random.choice(N, min(K, N-1), replace=False) for _ in range(N)])
        amb = compute_ambiguity(dd['y'], rnb, dd['dm'])
        r, _ = pearsonr(amb, dd['y'])
        null3[d].append(r)
    if (perm+1) % 50 == 0: print(f'  {perm+1}/{N_PERM} ({time.time()-t0:.0f}s)', flush=True)
print(f'  Done in {time.time()-t0:.0f}s')

print(f'\nNull 3 Results:')
for d in focus_domains:
    nc = np.array(null3[d])
    p = (np.sum(np.abs(nc) >= np.abs(true_r[d])) + 1) / (N_PERM + 1)
    print(f'  {d:20s} {true_r[d]:+.4f}  {nc.mean():+.4f}  {nc.std():.4f}  {p:.4f}')

# Summary
print(f'\n{"="*70}')
print('SIGNIFICANCE SUMMARY')
print('='*70)
print(f'{"Domain":20s} {"True r":8s} {"p(fert)":8s} {"p(desc)":8s} {"p(nbr)":8s} {"Verdict":10s}')
for d in focus_domains:
    p1 = (np.sum(np.abs(np.array(null1[d])) >= np.abs(true_r[d])) + 1) / (N_PERM + 1)
    p2 = (np.sum(np.abs(np.array(null2[d])) >= np.abs(true_r[d])) + 1) / (N_PERM + 1)
    p3 = (np.sum(np.abs(np.array(null3[d])) >= np.abs(true_r[d])) + 1) / (N_PERM + 1)
    sig = 'SIG' if all(p < 0.05 for p in [p1, p2, p3]) else 'ns'
    print(f'  {d:20s} {true_r[d]:+.4f}  {p1:.4f}   {p2:.4f}   {p3:.4f}   {sig:10s}')

print(f'\n{"="*70}')
print('D5 COMPLETE')
print('='*70)
