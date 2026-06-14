"""
Phase F2 — Operator Tests.
Six behavioral tests (Composition, Closure, Associativity, Scaling, Transport, Symmetry)
applied to each domain to classify operator geometry type.
"""
import numpy as np, pandas as pd, os, json, time, warnings
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import r2_score
from scipy.stats import pearsonr
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseF'
OUT = '/home/student/sgp_core_v2/phases/phaseE'
os.makedirs(f'{BASE}/raw', exist_ok=True)
os.makedirs(f'{BASE}/processed', exist_ok=True)

df = pd.read_csv('/home/student/sgp_core_v2/phases/phaseC/phaseC_metrics.csv')
df['sys_idx'] = df.groupby('domain').cumcount()
domains = sorted(df['domain'].unique())

COLS_DESC = ['CSR','RBS','ADI','RTP','SRD']
COLS_BEHAV = [c for c in df.columns if c.startswith('fertility_') or c.startswith('stability_')]
curv_df = pd.read_csv(f'{OUT}/processed/curvature_metrics.csv')

t0 = time.time()
print('='*70)
print('PHASE F2 — OPERATOR TESTS')
print('='*70)

def safe_r2(y_true, y_pred):
    if np.std(y_true) < 1e-10: return 0.0
    return r2_score(y_true, y_pred)

test_records = []

for domain in domains:
    m = df['domain'] == domain
    dm = df[m].copy().reset_index(drop=True)
    N = len(dm)
    X = StandardScaler().fit_transform(dm[COLS_DESC].values)
    Y = dm[COLS_BEHAV].values
    Y1 = Y[:, 0]  # primary behavior
    
    # Curvature
    dc = curv_df[curv_df['domain']==domain].reset_index(drop=True)
    C = dc[[c for c in dc.columns if c not in ('sys_idx','domain')]].values
    
    # Neighbors
    nbrs = NearestNeighbors(n_neighbors=min(21, N)).fit(X)
    _, idx = nbrs.kneighbors(X)
    nb_idx = idx[:, 1:]
    
    # ---- TEST A: COMPOSITION ----
    # Can local behaviors combine predictably?
    # Test: interpolate between pairs, measure prediction error
    comp_errors = []
    for _ in range(300):
        i, j = np.random.randint(0, N, 2)
        alpha = np.random.random()
        # Linear interpolation in descriptor space
        x_int = X[i] * alpha + X[j] * (1 - alpha)
        # Expected behavior from interpolation
        y_int = Y1[i] * alpha + Y1[j] * (1 - alpha)
        # Find nearest actual system to interpolated point
        dists = np.linalg.norm(X - x_int, axis=1)
        nearest = np.argmin(dists)
        if nearest in (i, j): continue
        y_actual = Y1[nearest]
        comp_errors.append(abs(y_int - y_actual))
    composition_error = np.mean(comp_errors) if comp_errors else 0
    composition_fidelity = 1 / (1 + composition_error)  # normalize
    
    # ---- TEST B: CLOSURE ----
    # Do transformations stay within family bounds?
    # Test: randomly perturb descriptors, check if behavior stays in observed range
    y_min, y_max = Y1.min(), Y1.max()
    closure_rate = 0
    for _ in range(500):
        i = np.random.randint(0, N)
        noise = np.random.normal(0, 0.5, size=5)
        x_pert = X[i] + noise
        # Predict behavior at perturbed point via nearest neighbor
        dists = np.linalg.norm(X - x_pert, axis=1)
        nearest = np.argmin(dists)
        y_pert = Y1[nearest]
        if y_min <= y_pert <= y_max:
            closure_rate += 1
    closure_score = closure_rate / 500
    
    # ---- TEST C: ASSOCIATIVITY ----
    # Does ordering of transformations matter?
    # Test: apply two descriptor changes in different orders
    assoc_errors = []
    for _ in range(300):
        i = np.random.randint(0, N)
        # Two random directions
        d1 = np.random.normal(0, 0.3, size=5)
        d2 = np.random.normal(0, 0.3, size=5)
        
        # Order 1: d1 then d2
        x1 = X[i] + d1 + d2
        dists1 = np.linalg.norm(X - x1, axis=1)
        y1 = Y1[np.argmin(dists1)]
        
        # Order 2: d2 then d1
        x2 = X[i] + d2 + d1
        dists2 = np.linalg.norm(X - x1, axis=1)  # same as x1 (commutative in descriptor space)
        y2 = Y1[np.argmin(dists2)]
        
        # Note: descriptor addition is commutative, so x1 == x2
        # Associativity violation comes from the composition function, not descriptors
        # True test: does composition of BEHAVIOR changes depend on order?
        y_base = Y1[i]
        change_d1 = Y1[np.argmin(np.linalg.norm(X - (X[i] + d1), axis=1))] - y_base
        change_d2 = Y1[np.argmin(np.linalg.norm(X - (X[i] + d2), axis=1))] - y_base
        
        # Apply changes in different orders
        composed_1 = y_base + change_d1 + change_d2
        composed_2 = y_base + change_d2 + change_d1
        assoc_errors.append(abs(composed_1 - composed_2))
    associativity_violation = np.mean(assoc_errors) if assoc_errors else 0
    associativity_score = 1 / (1 + associativity_violation)
    
    # ---- TEST D: SCALING ----
    # Does geometry preserve under magnification?
    # Test: fit linear models at different descriptor scales, compare coefficients
    scale_stabilities = []
    for scale in [0.1, 0.5, 1.0, 2.0, 5.0]:
        X_scaled = X * scale
        lr = LinearRegression().fit(X_scaled, Y1)
        # Coefficient stability: how much does the coefficient vector change?
        if len(scale_stabilities) > 0:
            prev_coef = scale_stabilities[-1]['coef']
            coef_change = np.linalg.norm(lr.coef_ - prev_coef)
        else:
            coef_change = 0
        scale_stabilities.append({'scale': scale, 'coef': lr.coef_, 'r2': lr.score(X_scaled, Y1)})
    scaling_stability = 1 / (1 + np.mean([
        scale_stabilities[i+1]['coef'] - scale_stabilities[i]['coef']
        for i in range(len(scale_stabilities)-1)
    ])) if len(scale_stabilities) > 1 else 0
    # Actually use the R² to measure scaling preservation
    r2s = [s['r2'] for s in scale_stabilities]
    scaling_preservation = 1 - np.std(r2s) / (np.mean(r2s) + 1e-10)
    
    # ---- TEST E: TRANSPORT ----
    # Can predictive models move across regions?
    # Test: split descriptor space into two halves, train on one, predict on other
    for desc_idx in range(5):
        desc_vals = dm[COLS_DESC[desc_idx]].values
        median = np.median(desc_vals)
        lo = desc_vals <= median
        hi = desc_vals > median
        if sum(lo) < 10 or sum(hi) < 10:
            transport_r2 = 0
        else:
            model = Ridge(alpha=1.0).fit(X[lo], Y1[lo])
            yp = model.predict(X[hi])
            transport_r2 = safe_r2(Y1[hi], yp)
        break
    
    # Transport test: train on half of descriptor space, predict other
    # Use PCA first component to split
    from sklearn.decomposition import PCA
    pca = PCA(n_components=1).fit(X)
    X_pc1 = pca.transform(X).flatten()
    median_pc = np.median(X_pc1)
    lo_pc = X_pc1 <= median_pc
    hi_pc = X_pc1 > median_pc
    if sum(lo_pc) >= 10 and sum(hi_pc) >= 10:
        model = Ridge(alpha=1.0).fit(X[lo_pc], Y1[lo_pc])
        yp_hi = model.predict(X[hi_pc])
        transport_fwd = safe_r2(Y1[hi_pc], yp_hi)
        model = Ridge(alpha=1.0).fit(X[hi_pc], Y1[hi_pc])
        yp_lo = model.predict(X[lo_pc])
        transport_rev = safe_r2(Y1[lo_pc], yp_lo)
        transport_score = (transport_fwd + transport_rev) / 2
    else:
        transport_score = 0
    
    # ---- TEST F: SYMMETRY ----
    # Which transformations preserve behavior?
    # Test: find descriptor directions that minimize behavioral change
    sym_scores = []
    for _ in range(100):
        direction = np.random.normal(0, 1, size=5)
        direction /= np.linalg.norm(direction) + 1e-10
        proj = X @ direction
        if np.std(proj) < 1e-10: continue
        # Behavioral variance explained by this direction
        r2_dir = safe_r2(Y1, LinearRegression().fit(proj.reshape(-1,1), Y1).predict(proj.reshape(-1,1)))
        sym_scores.append(r2_dir)
    # Low R² = direction is symmetric (behavior doesn't change along it)
    symmetry_score = 1 - np.mean(sym_scores) if sym_scores else 0.5
    
    # === RECORD ===
    test_records.append({
        'domain': domain, 'N': N,
        'composition_fidelity': round(composition_fidelity, 6),
        'closure_score': round(closure_score, 6),
        'associativity_score': round(associativity_score, 6),
        'scaling_preservation': round(scaling_preservation, 6),
        'transport_score': round(transport_score, 6),
        'symmetry_score': round(symmetry_score, 6),
    })
    print(f'  {domain}: comp={composition_fidelity:.3f}  clos={closure_score:.3f}  assoc={associativity_score:.3f}  scale={scaling_preservation:.3f}  trans={transport_score:.3f}  sym={symmetry_score:.3f}')

test_df = pd.DataFrame(test_records)
test_path = f'{BASE}/raw/composition_tests.csv'
test_df.to_csv(test_path, index=False)
print(f'\nF2 saved: {test_path} ({len(test_df)} rows)')

# Interpret each domain's operator type
print('\n--- Operator Type Classification ---')
for _, r in test_df.iterrows():
    scores = {
        'additive': r['composition_fidelity'],
        'multiplicative': (1 - r['scaling_preservation']) * (1 - r['associativity_score']),
        'hierarchical': (1 - r['transport_score']) * (1 - r['closure_score']),
        'topological': r['closure_score'] * r['symmetry_score'],
        'network': r['transport_score'] * (1 - r['symmetry_score']),
        'symmetry_dominated': r['symmetry_score'],
    }
    best = max(scores, key=scores.get)
    print(f'  {r["domain"]:25s}: {best}  ({", ".join(f"{k}={v:.2f}" for k,v in sorted(scores.items(), key=lambda x:-x[1])[:3])})')

f2_summary = {
    'phase': 'F2', 'seed': SEED,
    'n_domains': len(domains),
    'tests': ['composition_fidelity','closure_score','associativity_score',
              'scaling_preservation','transport_score','symmetry_score'],
    'runtime_seconds': round(time.time() - t0),
}
with open(f'{BASE}/summaries/f2_summary.json', 'w') as f:
    json.dump(f2_summary, f, indent=2)
print(f'\nF2 summary saved')
print(f'F2 COMPLETE ({time.time()-t0:.0f}s)')
