"""
Phase B5: Null universe tests (optimized).
Phase B6: Meta-predictive geometry synthesis.
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from scipy.stats import pearsonr
from scipy.spatial.distance import pdist, squareform
import warnings
warnings.filterwarnings('ignore')

SEED = 2002
rng = np.random.default_rng(SEED)

df = pd.read_csv('/home/student/sgp_core_v2/phases/phaseA/phaseA_metrics.csv')
domains = sorted(df['domain'].unique())
desc_cols = ['CSR', 'RBS', 'ADI', 'RTP', 'SRD']
targets_valid = ['stability_return_time', 'stability_recovery_rate', 'stability_final_dev',
                 'stability_max_dev', 'fertility_state_diversity', 'fertility_transition_entropy']
TARGET = 'fertility_state_diversity'

def clean(df, domain=None, target=None):
    m = pd.Series(True, index=df.index)
    if domain: m &= df['domain'] == domain
    if target: m &= df[target].notna() & np.isfinite(df[target].values)
    for c in desc_cols: m &= df[c].notna() & np.isfinite(df[c].values)
    return m

# Precompute all data to avoid repeated cleaning
data = {}
for d in domains:
    m = clean(df, domain=d, target=TARGET)
    data[d] = {
        'X': StandardScaler().fit_transform(df.loc[m, desc_cols]),
        'y': df.loc[m, TARGET].values,
    }

def cross_r2(d1, d2, y_shuf=None):
    """Compute R² for d1→d2 transfer."""
    X_tr, y_tr = data[d1]['X'], data[d1]['y']
    X_te = data[d2]['X']
    y_te = data[d2]['y'] if y_shuf is None else rng.permutation(data[d2]['y'])
    lr = LinearRegression().fit(X_tr, y_tr)
    return r2_score(y_te, lr.predict(X_te))

# ============================================================
# PHASE B5a: Global null (shuffle domain labels)
# ============================================================
print('='*70)
print('PHASE B5 — NULL UNIVERSE TESTS')
print(('='*70))
N_NULL = 500

true_vals = []
for d1 in domains:
    for d2 in domains:
        if d1 != d2:
            true_vals.append(cross_r2(d1, d2))
true_mean = np.mean(true_vals)
print(f'\nTrue mean cross-domain R²: {true_mean:.4f}')

# Null: shuffle domain labels
null_means = []
for _ in range(N_NULL):
    df_n = df.copy()
    df_n['domain'] = rng.permutation(df_n['domain'].values)
    n_vals = []
    for d1 in domains:
        for d2 in domains:
            if d1 == d2: continue
            m1 = clean(df_n, domain=d1, target=TARGET)
            m2 = clean(df_n, domain=d2, target=TARGET)
            if m1.sum() < 10 or m2.sum() < 10: continue
            X_tr = StandardScaler().fit_transform(df_n.loc[m1, desc_cols])
            X_te = StandardScaler().fit_transform(df_n.loc[m2, desc_cols])
            lr = LinearRegression().fit(X_tr, df_n.loc[m1, TARGET].values)
            n_vals.append(r2_score(df_n.loc[m2, TARGET].values, lr.predict(X_te)))
    null_means.append(np.mean(n_vals))

null_means = np.array(null_means)
p_null = np.mean(null_means >= true_mean)
print(f'Null mean: {np.mean(null_means):.4f}  95th: {np.percentile(null_means, 95):.4f}  p={p_null:.4f}')
print(f'{"SIGNIFICANT" if p_null < 0.05 else "NOT SIGNIFICANT"}')

# ============================================================
# PHASE B5b: Pairwise null (oscillator ↔ population)
# ============================================================
print('\nPairwise null (oscillator ↔ population):')
pair = ('nonlinear_oscillator', 'population')
pair_true = [cross_r2(pair[0], pair[1]), cross_r2(pair[1], pair[0])]
pair_mean = np.mean(pair_true)
print(f'  True mean: {pair_mean:.4f}')

null_pairs = []
for _ in range(N_NULL):
    df_n = df.copy()
    df_n['domain'] = rng.permutation(df_n['domain'].values)
    v = []
    for d1, d2 in [pair, (pair[1], pair[0])]:
        m1 = clean(df_n, domain=d1, target=TARGET)
        m2 = clean(df_n, domain=d2, target=TARGET)
        if m1.sum() < 10 or m2.sum() < 10: continue
        X_tr = StandardScaler().fit_transform(df_n.loc[m1, desc_cols])
        X_te = StandardScaler().fit_transform(df_n.loc[m2, desc_cols])
        lr = LinearRegression().fit(X_tr, df_n.loc[m1, TARGET].values)
        v.append(r2_score(df_n.loc[m2, TARGET].values, lr.predict(X_te)))
    null_pairs.append(np.mean(v))

null_pairs = np.array(null_pairs)
p_pair = np.mean(null_pairs >= pair_mean)
print(f'  Null mean: {np.mean(null_pairs):.4f}  p={p_pair:.4f}')
print(f'  {"SIGNIFICANT" if p_pair < 0.05 else "NOT SIGNIFICANT"}')

# ============================================================
# PHASE B5c: Surrogate test (shuffle test target)
# ============================================================
print('\nSurrogate test (shuffle target within test domain):')
surr_vals = []
for _ in range(N_NULL):
    sv = []
    for d1 in domains:
        for d2 in domains:
            if d1 == d2: continue
            X_tr, y_tr = data[d1]['X'], data[d1]['y']
            X_te = data[d2]['X']
            y_te_shuf = rng.permutation(data[d2]['y'])
            lr = LinearRegression().fit(X_tr, y_tr)
            sv.append(r2_score(y_te_shuf, lr.predict(X_te)))
    surr_vals.append(np.mean(sv))

surr_vals = np.array(surr_vals)
p_surr = np.mean(surr_vals >= true_mean)
print(f'  Surrogate mean: {np.mean(surr_vals):.4f}  p={p_surr:.4f}')
print(f'  {"SIGNIFICANT" if p_surr < 0.05 else "NOT SIGNIFICANT"}')

# ============================================================
# PHASE B6: META-PREDICTIVE GEOMETRY
# ============================================================
print('\n' + '='*70)
print('PHASE B6 — META-PREDICTIVE GEOMETRY')
print('='*70)

# Compute domain property vectors
prop_vecs = {}
for d in domains:
    m = clean(df, domain=d, target=TARGET)
    sub = df.loc[m]
    # Use descriptor means as property vector
    props = [sub[c].mean() for c in desc_cols]
    # Also add target mean
    props.append(sub[TARGET].mean())
    prop_vecs[d] = props

dnames = list(prop_vecs.keys())
prop_arr = np.array([prop_vecs[d] for d in dnames])
prop_dist = squareform(pdist(prop_arr))

# Transfer success matrix (mean R² of both directions, capped at 0)
trans_success = np.zeros((len(dnames), len(dnames)))
for i, d1 in enumerate(dnames):
    for j, d2 in enumerate(dnames):
        if i == j: continue
        v = np.mean([cross_r2(d1, d2), cross_r2(d2, d1)])
        trans_success[i,j] = max(0, v)

# Correlation between property distance and transfer success
pairs_dist, pairs_trans = [], []
for i in range(len(dnames)):
    for j in range(i+1, len(dnames)):
        pairs_dist.append(prop_dist[i,j])
        pairs_trans.append(trans_success[i,j] + trans_success[j,i])

r, p = pearsonr(pairs_dist, pairs_trans)
print(f'\nProperty distance ↔ Transfer success: r={r:.4f}  p={p:.4f}')
print(f'  {"Closer domains transfer better" if r < -0.3 else "No clear relationship"}')

# Per-domain properties
print('\nDomain properties:')
cols = desc_cols + ['target_mean']
print(f'{"Domain":25s}', end='')
for c in cols:
    print(f'{c:>12s}', end='')
print()
for d in dnames:
    print(f'{d:25s}', end='')
    for v in prop_vecs[d]:
        print(f'{v:12.4f}', end='')
    print()

# Final assessment
print('\n=== TRANSFER GEOMETRY ASSESSMENT ===')
print(f'Mean cross-domain R²:      {true_mean:.4f} ({"positive" if true_mean > 0 else "NEGATIVE"})')
print(f'Best cross-domain pair:     oscillator ↔ population (~0.4 for fertility)')
print(f'Null significance:          {"YES" if p_null < 0.05 else "NO"}')
print(f'Pair significance:          {"YES" if p_pair < 0.05 else "NO"}')
print(f'Surrogate significance:     {"YES" if p_surr < 0.05 else "NO"}')

# ============ Save ============
for label, arr in [('null', null_means), ('surr', surr_vals), ('pair_null', null_pairs)]:
    pd.DataFrame({label: arr}).to_csv(f'/home/student/sgp_core_v2/phases/phaseB/phaseB5_{label}.csv', index=False)

pd.DataFrame([{
    'phase': 'B5',
    'true_mean_R2': round(true_mean, 4),
    'null_mean_R2': round(float(np.mean(null_means)), 4),
    'null_p': round(float(p_null), 4),
    'surr_p': round(float(p_surr), 4),
    'pair_p': round(float(p_pair), 4),
    'property_transfer_r': round(float(r), 4),
}]).to_csv('/home/student/sgp_core_v2/phases/phaseB/phaseB5_summary.csv', index=False)

print('\n=== PHASES B5–B6 COMPLETE ===')
PYEOF
python3 /home/student/sgp_core_v2/phases/phaseB/phaseB5_null.py