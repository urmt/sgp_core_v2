"""
Phase P1+P2 — CONTINUITY THROUGH TRANSITION + IDENTITY GEOMETRY

P1: Can recursive continuity persist THROUGH organizational transformation?
P2: What kinds of transformations preserve identity?

Systems undergo regime transitions (coupling shifts, bifurcations, fragmentation).
Tests whether closure continuity survives the transition.
"""
import sys, numpy as np, pandas as pd, os, json, warnings
sys.path.insert(0, '/home/student/sgp_core_v2')
warnings.filterwarnings('ignore')

SEED = 5000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseP_transition_persistence'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

N = 5
N_SIMS = 500
STEPS = 500
DT = 0.05
TRANS_T = 250  # transition midpoint

# Transition types
TRANS_TYPES = [
    'coupling_strengthen',   # K1=0.2 → K2=1.0
    'coupling_weaken',       # K1=1.0 → K2=0.2
    'bifurcation',           # split into two subgroups
    'fragmentation',         # K1=0.8 → K2=0.0
    'closure_reorg',         # change alpha_c/beta_c parameters
    'topology_change',       # all-to-all → ring
]

cont_records = []
traj_records = []
geo_records = []

for sim in range(N_SIMS):
    ttype = np.random.choice(TRANS_TYPES)
    omega = np.random.uniform(0.5, 2.0, N)
    alpha_c = np.random.uniform(0.05, 0.3)
    beta_c = np.random.uniform(0.0, 0.5)
    
    # Set pre/post coupling based on transition type
    if ttype == 'coupling_strengthen': K1, K2 = 0.2, 1.0
    elif ttype == 'coupling_weaken': K1, K2 = 1.0, 0.2
    elif ttype == 'bifurcation': K1, K2 = 0.8, 0.8
    elif ttype == 'fragmentation': K1, K2 = 0.8, 0.0
    elif ttype == 'closure_reorg': K1, K2 = 0.6, 0.6
    elif ttype == 'topology_change': K1, K2 = 0.6, 0.6
    else: K1, K2 = 0.5, 0.5
    
    theta = np.random.uniform(0, 2*np.pi, N)
    c = np.random.uniform(0, 1, N)
    
    # For bifurcation: two subgroups with different natural frequencies
    if ttype == 'bifurcation':
        omega[:N//2] = np.random.uniform(0.5, 0.8, N//2)
        omega[N//2:] = np.random.uniform(1.5, 2.0, N - N//2)
    
    c_history = np.zeros((STEPS, N))
    r_history = np.zeros(STEPS)
    theta_history = np.zeros((STEPS, N))
    
    for t in range(STEPS):
        K_eff = K1 if t < TRANS_T else K2
        beta_eff = beta_c if t < TRANS_T else (beta_c * 0.1 if ttype == 'closure_reorg' else beta_c)
        alpha_eff = alpha_c if t < TRANS_T else (alpha_c * 2.0 if ttype == 'closure_reorg' else alpha_c)
        
        for i in range(N):
            dtheta = omega[i]
            if ttype == 'topology_change' and t >= TRANS_T:
                # Ring topology: only connect to nearest neighbors
                for j in [i-1, (i+1) % N]:
                    dtheta += (K_eff / 2) * np.sin(theta[j] - theta[i])
            else:
                for j in range(N):
                    if j != i:
                        dtheta += (K_eff / N) * np.sin(theta[j] - theta[i])
            theta[i] += DT * dtheta
        
        r = np.abs(np.mean(np.exp(1j * theta)))
        r_history[t] = r
        psi = np.angle(np.mean(np.exp(1j * theta)))
        
        for i in range(N):
            align = np.cos(theta[i] - psi)
            dc = alpha_eff * (align * r - c[i])
            for j in range(N):
                if j != i:
                    dc += (beta_eff / N) * (c[j] - c[i])
            c[i] += DT * dc
            c[i] = np.clip(c[i], 0, 1)
        c_history[t] = c.copy()
        theta_history[t] = theta
    
    # ====================================================
    # P1 — Continuity Through Transition
    # ====================================================
    pre_r = np.mean(r_history[:TRANS_T][-50:]) if TRANS_T >= 50 else np.mean(r_history[:TRANS_T])
    post_r = np.mean(r_history[TRANS_T:][-50:]) if STEPS - TRANS_T >= 50 else np.mean(r_history[TRANS_T:])
    pre_c = np.mean(c_history[:TRANS_T][-50:]) if TRANS_T >= 50 else np.mean(c_history[:TRANS_T])
    post_c = np.mean(c_history[TRANS_T:][-50:]) if STEPS - TRANS_T >= 50 else np.mean(c_history[TRANS_T:])
    
    # Continuity survival: does closure persist through transformation?
    c_through_trans = np.corrcoef(c_history[TRANS_T-20:TRANS_T+20])  # during transition
    c_drop = max(0, pre_c - np.min(c_history[max(TRANS_T-5,0):min(TRANS_T+5,STEPS)]))
    c_recovery = 1.0 - max(0, pre_c - post_c) / (pre_c + 0.001)
    continuity_survives = int(post_c > 0.3 and abs(pre_c - post_c) < 0.5)
    
    # Order parameter continuity
    r_drop = max(0, pre_r - np.min(r_history[max(TRANS_T-5,0):min(TRANS_T+5,STEPS)]))
    r_recovery = min(1.0, post_r / (pre_r + 0.001))
    
    cont_records.append({
        'sim': sim, 'transition_type': ttype,
        'K1': K1, 'K2': K2,
        'pre_order': pre_r, 'post_order': post_r, 'r_drop': r_drop, 'r_recovery': r_recovery,
        'pre_closure': pre_c, 'post_closure': post_c, 'c_drop': c_drop, 'c_recovery': c_recovery,
        'continuity_survives': continuity_survives,
    })
    
    # Save trajectory for subset
    if sim < 30:
        for t in range(0, STEPS, 10):
            traj_records.append({
                'sim': sim, 'transition_type': ttype, 'step': t,
                'order_param': r_history[t], 'shared_closure': np.mean(c_history[t]),
                'c_std': np.std(c_history[t]),
                'in_transition': int(t >= TRANS_T),
            })
    
    # ====================================================
    # P2 — Identity Transformation Geometry
    # ====================================================
    # Continuity curvature: how smooth is the transition?
    window = 20
    c_smooth = c_history[max(TRANS_T-window,0):min(TRANS_T+window,STEPS)]
    if len(c_smooth) > 3:
        c_curvature = np.mean(np.abs(np.diff(c_smooth, n=2, axis=0))) if len(c_smooth) > 3 else 0
        if np.isnan(c_curvature) or np.size(c_curvature) == 0: c_curvature = 0
        if hasattr(c_curvature, '__iter__'): c_curvature = np.mean(c_curvature)
    else:
        c_curvature = 0
    
    # Closure deformation: shape change of closure distribution
    pre_c_dist = np.std(c_history[max(TRANS_T-30,0)])
    post_c_dist = np.std(c_history[min(TRANS_T+30,STEPS-1)])
    closure_deformation = abs(pre_c_dist - post_c_dist) / (pre_c_dist + 0.001)
    
    # Bifurcation detection: do closures split during transition?
    pre_c_range = np.max(c_history[max(TRANS_T-10,0)]) - np.min(c_history[max(TRANS_T-10,0)])
    post_c_range = np.max(c_history[min(TRANS_T+10,STEPS-1)]) - np.min(c_history[min(TRANS_T+10,STEPS-1)])
    bifurcation_point = int(post_c_range > 2 * pre_c_range and pre_c_range > 0.01)
    
    geo_records.append({
        'sim': sim, 'transition_type': ttype,
        'c_curvature': c_curvature,
        'closure_deformation': closure_deformation,
        'bifurcation_point': bifurcation_point,
        'pre_c_range': pre_c_range, 'post_c_range': post_c_range,
        'r_delta': post_r - pre_r,
        'c_delta': post_c - pre_c,
    })

# Save P1
cont_df = pd.DataFrame(cont_records)
traj_df = pd.DataFrame(traj_records)
cont_df.to_csv(f'{BASE}/outputs/phaseP_transition_continuity.csv', index=False)
traj_df.to_csv(f'{BASE}/outputs/phaseP_transition_trajectories.csv', index=False)

print('='*70)
print('PHASE P1 — CONTINUITY THROUGH TRANSITION')
print('Can recursive continuity persist THROUGH organizational transformation?')
print('='*70)

for tt in TRANS_TYPES:
    sub = cont_df[cont_df['transition_type'] == tt]
    print(f'\n  {tt:25s} (n={len(sub)}):')
    print(f'    Pre-order→post-order:  {sub["pre_order"].mean():.4f} → {sub["post_order"].mean():.4f}  '
          f'Δr={sub["r_drop"].mean():.4f}  rec={sub["r_recovery"].mean():.4f}')
    print(f'    Pre-closure→post-clos: {sub["pre_closure"].mean():.4f} → {sub["post_closure"].mean():.4f}  '
          f'Δc={sub["c_drop"].mean():.4f}  rec={sub["c_recovery"].mean():.4f}')
    print(f'    Continuity survives:   {sub["continuity_survives"].mean()*100:.1f}%')

print(f'\n=== OVERALL ===')
print(f'  Continuity survival rate: {cont_df["continuity_survives"].mean()*100:.1f}%')
print(f'  Mean r drop: {cont_df["r_drop"].mean():.4f}  Mean r recovery: {cont_df["r_recovery"].mean():.4f}')
print(f'  Mean c drop: {cont_df["c_drop"].mean():.4f}  Mean c recovery: {cont_df["c_recovery"].mean():.4f}')

p1 = {'phase':'P1','continuity_survival_rate':float(cont_df['continuity_survives'].mean()),
      'by_transition_type':{tt:float(cont_df[cont_df['transition_type']==tt]['continuity_survives'].mean()) for tt in TRANS_TYPES}}
with open(f'{BASE}/summaries/p1_summary.json','w') as f: json.dump(p1,f,indent=2)

# ====================================================
# P2 OUTPUT
# ====================================================
geo_df = pd.DataFrame(geo_records)
geo_df.to_csv(f'{BASE}/outputs/phaseP_identity_geometry.csv', index=False)

print('\n' + '='*70)
print('PHASE P2 — IDENTITY TRANSFORMATION GEOMETRY')
print('What kinds of transformations preserve identity?')
print('='*70)

for tt in TRANS_TYPES:
    sub = geo_df[geo_df['transition_type'] == tt]
    print(f'\n  {tt:25s} (n={len(sub)}):')
    print(f'    Curvature:              {sub["c_curvature"].mean():.6f}')
    print(f'    Closure deformation:    {sub["closure_deformation"].mean():.4f}')
    print(f'    Bifurcation point:      {sub["bifurcation_point"].mean()*100:.1f}%')
    print(f'    c_delta:                {sub["c_delta"].mean():.4f}')

# What predicts continuity survival?
print(f'\n=== PREDICTORS OF CONTINUITY SURVIVAL ===')
survivors = cont_df[cont_df['continuity_survives'] == 1]
non_survivors = cont_df[cont_df['continuity_survives'] == 0]
print(f'  {"Metric":30s} {"Survivors":>12s} {"Non-survivors":>15s}')
for col in ['pre_order','post_order','r_drop','c_drop','r_recovery']:
    sv = survivors[col].mean() if len(survivors) > 0 else 0
    nsv = non_survivors[col].mean() if len(non_survivors) > 0 else 0
    print(f'  {col:30s} {sv:12.4f} {nsv:15.4f}')

# Identity preservation by transition type
print(f'\n=== TRANSFORMATION PRESERVATION HIERARCHY ===')
preservation = geo_df.groupby('transition_type').agg(
    n=('sim','count'),
    c_delta_mean=('c_delta','mean'),
    deform_mean=('closure_deformation','mean'),
    bif_pct=('bifurcation_point','mean'),
).sort_values('c_delta_mean', ascending=False)
for idx, row in preservation.iterrows():
    print(f'  {idx:25s}: c_delta={row["c_delta_mean"]:+.4f}  deform={row["deform_mean"]:.4f}  '
          f'bifurc={row["bif_pct"]*100:.1f}%')

p2 = {'phase':'P2',
      'preservation_hierarchy':{tt:float(geo_df[geo_df['transition_type']==tt]['c_delta'].mean()) for tt in TRANS_TYPES}}
with open(f'{BASE}/summaries/p2_summary.json','w') as f: json.dump(p2,f,indent=2)

print(f'\nP1+P2 COMPLETE')
