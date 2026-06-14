"""
Phase F5 — Transitional Geometry Analysis.
Tests whether domains shift operator class across parameter regions.
Measures operator transition boundaries and curvature changes.
"""
import numpy as np, pandas as pd, os, json, time, warnings
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import r2_score
from scipy.stats import pearsonr
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseF'
OUT = '/home/student/sgp_core_v2/phases/phaseE'
os.makedirs(f'{BASE}/processed', exist_ok=True)
os.makedirs(f'{BASE}/raw', exist_ok=True)

df = pd.read_csv('/home/student/sgp_core_v2/phases/phaseC/phaseC_metrics.csv')
df['sys_idx'] = df.groupby('domain').cumcount()
curv = pd.read_csv(f'{OUT}/processed/curvature_metrics.csv')
domains = sorted(df['domain'].unique())

COLS_BEHAV = [c for c in df.columns if c.startswith('fertility_') or c.startswith('stability_')]
COLS_DESC = ['CSR','RBS','ADI','RTP','SRD']
COLS_CURV = ['tangent_rotation','local_curvature','predictive_shear',
             'geodesic_instab','jacobian_vol','desc_switch_vel']
t0 = time.time()

print('='*70)
print('PHASE F5 — TRANSITIONAL GEOMETRY ANALYSIS')
print('='*70)

# For each domain, sort by each descriptor and compute rolling operator signatures
WINDOW = 50
transition_records = []

for domain in domains:
    m = df['domain'] == domain
    dm = df[m].copy().reset_index(drop=True)
    dc = curv[curv['domain']==domain].reset_index(drop=True)
    N = len(dm)
    Y1 = dm[COLS_BEHAV[0]].values if 'fertility_state_diversity' in dm.columns else dm[[c for c in dm.columns if c.startswith('fertility_')][0]].values
    
    for desc_idx, desc_col in enumerate(COLS_DESC):
        sd = dm.sort_values(desc_col).reset_index(drop=True)
        X_sorted = StandardScaler().fit_transform(sd[COLS_DESC].values)
        y_sorted = Y1[sd['sys_idx'].values]
        curv_sorted = dc.loc[sd['sys_idx'].values][COLS_CURV].values
        
        # Roll through parameter space
        for window_start in range(0, N - WINDOW, WINDOW // 2):
            end = min(window_start + WINDOW, N)
            X_win = X_sorted[window_start:end]
            y_win = y_sorted[window_start:end]
            curv_win = curv_sorted[window_start:end]
            
            if len(X_win) < 20 or np.std(y_win) < 1e-10: continue
            
            # Operator signatures in this window
            lr = LinearRegression().fit(X_win, y_win)
            add_r2 = r2_score(y_win, lr.predict(X_win))
            
            # Multiplicative: interaction improvement
            X_int = np.column_stack([X_win] + [X_win[:, i]*X_win[:, j] for i in range(5) for j in range(i+1,5)])
            mult_r2 = r2_score(y_win, LinearRegression().fit(X_int, y_win).predict(X_int))
            mult_gain = mult_r2 - add_r2
            
            # Topological continuity
            nbrs = NearestNeighbors(n_neighbors=min(11, len(X_win))).fit(X_win)
            _, idx = nbrs.kneighbors(X_win)
            cont_pred = np.array([y_win[idx[i, 1:]].mean() for i in range(len(X_win))])
            continuity = r2_score(y_win, cont_pred)
            
            # Mean curvature in window
            mean_curv = np.mean(curv_win, axis=0) if len(curv_win) > 0 else np.zeros(6)
            
            # Parameter range
            param_val = sd[desc_col].iloc[window_start + (end - window_start)//2]
            param_low = sd[desc_col].iloc[window_start]
            param_high = sd[desc_col].iloc[min(end-1, N-1)]
            
            transition_records.append({
                'domain': domain, 'descriptor': desc_col,
                'param_mid': param_val, 'param_low': param_low, 'param_high': param_high,
                'window_start': window_start, 'window_end': end,
                'n_systems': len(X_win),
                'additive_r2': round(add_r2, 6),
                'multiplicative_gain': round(mult_gain, 6),
                'topological_continuity': round(continuity, 6),
                'tangent_rotation_mean': round(mean_curv[0], 6),
                'local_curvature_mean': round(mean_curv[1], 6),
                'predictive_shear_mean': round(mean_curv[2], 6),
            })
    
    print(f'  {domain}: {len([r for r in transition_records if r["domain"]==domain])} windows')

trans_df = pd.DataFrame(transition_records)
trans_path = f'{BASE}/processed/operator_transition_regions.csv'
trans_df.to_csv(trans_path, index=False)
print(f'\nF5 saved: {trans_path} ({len(trans_df)} windows)')

# Detect operator shifts: where additive→multiplicative dominance changes
print('\n--- Operator Shifts (Additive → Multiplicative dominance change) ---')
shift_count = 0
for domain in domains:
    dd = trans_df[trans_df['domain']==domain].copy()
    if len(dd) < 3: continue
    for desc_col in COLS_DESC:
        dd_d = dd[dd['descriptor']==desc_col].sort_values('param_mid')
        if len(dd_d) < 3: continue
        # Detect crossing: additive_r2 - multiplicative_gain changes sign
        diff = dd_d['additive_r2'].values - dd_d['multiplicative_gain'].values
        for i in range(len(diff)-1):
            if diff[i] * diff[i+1] < 0:  # sign change between adjacent windows
                shift_count += 1
                print(f'  {domain}: additive↔multiplicative shift at {desc_col}={dd_d.iloc[i+1]["param_mid"]:.3f}')

if shift_count == 0:
    print(f'  No additive↔multiplicative transitions detected across all domains')

# Parameter ranges where curvature peaks
print('\n--- Curvature Transition Regions ---')
for curvature_metric in ['tangent_rotation_mean', 'local_curvature_mean', 'predictive_shear_mean']:
    top = trans_df.nlargest(5, curvature_metric)[['domain', 'descriptor', 'param_mid', curvature_metric]]
    print(f'\n  High {curvature_metric}:')
    for _, r in top.iterrows():
        print(f'    {r["domain"]:25s} {r["descriptor"]}={r["param_mid"]:.3f}  {curvature_metric}={r[curvature_metric]:.4f}')

f5_summary = {
    'phase': 'F5', 'seed': SEED,
    'n_windows': len(trans_df),
    'window_size': WINDOW,
    'step': WINDOW // 2,
    'n_operator_shifts': shift_count,
    'runtime_seconds': round(time.time() - t0),
}
with open(f'{BASE}/summaries/f5_summary.json', 'w') as f:
    json.dump(f5_summary, f, indent=2)
print(f'\nF5 summary saved')
print(f'F5 COMPLETE ({time.time()-t0:.0f}s)')
