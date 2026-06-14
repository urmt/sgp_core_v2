"""
Phase G3 — Transition Dynamics.
Analyzes transitions between organizational regions.
Measures bifurcation structure, curvature changes, operator shifts.
"""
import numpy as np, pandas as pd, os, json, time, warnings
from sklearn.neighbors import NearestNeighbors
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseG'
OUT = '/home/student/sgp_core_v2/phases/phaseE'
os.makedirs(f'{BASE}/processed', exist_ok=True)

phase = pd.read_csv(f'{BASE}/processed/coherence_fertility_phase_space.csv')
curv = pd.read_csv(f'{OUT}/processed/curvature_metrics.csv')
df = pd.read_csv('/home/student/sgp_core_v2/phases/phaseC/phaseC_metrics.csv')
df['sys_idx'] = df.groupby('domain').cumcount()
merged = phase.merge(curv, on=['sys_idx','domain']).merge(
    df[['sys_idx','domain','CSR','RBS','ADI','RTP','SRD']], on=['sys_idx','domain'])
domains = sorted(merged['domain'].unique())
COLS_DESC = ['CSR','RBS','ADI','RTP','SRD']
COLS_CURV = ['tangent_rotation','local_curvature','predictive_shear','geodesic_instab','jacobian_vol','desc_switch_vel']

t0 = time.time()
print('='*70)
print('PHASE G3 — TRANSITION DYNAMICS')
print('='*70)

# For each domain, sort by each descriptor, track region transitions
region_order = {'constrained_generative': 0, 'rigid_coherence': 1,
                'chaotic_fertility': 2, 'collapse': 3}
trans_records = []

for domain in domains:
    dm = merged[merged['domain'] == domain].copy().reset_index(drop=True)
    N = len(dm)
    
    for desc in COLS_DESC:
        sd = dm.sort_values(desc).reset_index(drop=True)
        regions = sd['region'].values
        last_region = regions[0]
        region_transitions = 0
        transition_points = []
        
        for i in range(1, N):
            if regions[i] != last_region:
                region_transitions += 1
                transition_points.append({
                    'pos': i,
                    'from': last_region,
                    'to': regions[i],
                    'param_val': sd[desc].iloc[i],
                })
                last_region = regions[i]
        
        # Curvature in transition windows
        curv_at_trans = []
        for tp in transition_points:
            start = max(0, tp['pos'] - 10)
            end = min(N, tp['pos'] + 10)
            win_curv = sd[COLS_CURV].iloc[start:end].mean().to_dict()
            win_curv['domain'] = domain
            win_curv['descriptor'] = desc
            win_curv['param_val'] = tp['param_val']
            win_curv['transition_from'] = tp['from']
            win_curv['transition_to'] = tp['to']
            curv_at_trans.append(win_curv)
        
        trans_records.append({
            'domain': domain, 'descriptor': desc,
            'n_transitions': region_transitions,
            'transition_rate': region_transitions / N,
            'n_systems': N,
        })

trans_df = pd.DataFrame(trans_records)
trans_df.to_csv(f'{BASE}/processed/transition_dynamics.csv', index=False)
print(f'Transition dynamics saved: {len(trans_df)} rows')

# Which descriptors drive most transitions?
print('\nTransitions per descriptor (across all domains):')
desc_trans = trans_df.groupby('descriptor')['n_transitions'].sum().sort_values(ascending=False)
for d, n in desc_trans.items():
    print(f'  {d}: {n} transitions')

# Which domains have most transitions?
print('\nTransitions per domain:')
dom_trans = trans_df.groupby('domain')['n_transitions'].sum().sort_values(ascending=False)
for d, n in dom_trans.items():
    print(f'  {d}: {n} transitions')

# Bifurcation analysis: find descriptor values where multiple regions coexist
print('\nBifurcation regions (descriptor ranges with highest region diversity):')
for domain in domains:
    dm = merged[merged['domain'] == domain].copy().reset_index(drop=True)
    for desc in COLS_DESC:
        sd = dm.sort_values(desc).reset_index(drop=True)
        n_regions_in_window = []
        for i in range(0, len(sd) - 50, 10):
            win = sd['region'].iloc[i:i+50]
            n_regions_in_window.append((i + 25, win.nunique()))
        max_bif = max(n_regions_in_window, key=lambda x: x[1]) if n_regions_in_window else (0, 0)
        if max_bif[1] >= 3:  # 3+ regions coexist
            param_val = sd[desc].iloc[min(max_bif[0], len(sd)-1)]
            print(f'  {domain:25s} {desc}: {max_bif[1]} regions at {desc}={param_val:.3f}')

g3_summary = {
    'phase': 'G3', 'seed': SEED,
    'n_transition_records': len(trans_df),
    'total_transitions': int(trans_df['n_transitions'].sum()),
    'avg_transition_rate': float(trans_df['transition_rate'].mean()),
    'runtime_seconds': round(time.time() - t0),
}
with open(f'{BASE}/summaries/g3_summary.json', 'w') as f:
    json.dump(g3_summary, f, indent=2)
print(f'\nG3 COMPLETE ({time.time()-t0:.1f}s)')
