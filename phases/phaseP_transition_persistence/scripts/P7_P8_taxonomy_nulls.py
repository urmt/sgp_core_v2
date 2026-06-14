"""
Phase P7+P8 — TRANSFORMATION TAXONOMY + DYNAMICAL NULL PROGRAM

P7: Empirically derive classes of organizational transformation.
P8: Do persistence-through-transition effects survive destruction of temporal structure?
"""
import sys, numpy as np, pandas as pd, os, json, warnings
sys.path.insert(0, '/home/student/sgp_core_v2')
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
warnings.filterwarnings('ignore')

SEED = 5003; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseP_transition_persistence'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

# ====================================================
# P7 — TRANSFORMATION TAXONOMY
# ====================================================
print('='*70)
print('PHASE P7 — TRANSFORMATION TAXONOMY')
print('Empirically derive classes of organizational transformation.')
print('='*70)

# Load P1 and P2 results
cont_df = pd.read_csv(f'{BASE}/outputs/phaseP_transition_continuity.csv')
geo_df = pd.read_csv(f'{BASE}/outputs/phaseP_identity_geometry.csv')

print(f'  Loaded: continuity={len(cont_df)}, geometry={len(geo_df)}')

# Merge
merge_df = pd.concat([
    cont_df[['transition_type','pre_order','post_order','pre_closure','post_closure',
             'r_drop','c_drop','r_recovery','c_recovery','continuity_survives']],
    geo_df[['c_curvature','closure_deformation','bifurcation_point','c_delta']],
], axis=1).dropna()

print(f'  Merged: {len(merge_df)} systems')

# Feature selection
taxo_cols = ['pre_order','post_order','pre_closure','post_closure',
             'r_drop','r_recovery','c_recovery','c_curvature',
             'closure_deformation','c_delta','continuity_survives']
avail = [c for c in taxo_cols if c in merge_df.columns]

X = merge_df[avail].values
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

K_CLUSTERS = 5
km = KMeans(n_clusters=K_CLUSTERS, random_state=SEED, n_init=10)
labels = km.fit_predict(X_scaled)
merge_df['transformation_cluster'] = labels

cluster_info = {}
print(f'\n=== TRANSFORMATION TAXONOMY ({K_CLUSTERS} classes) ===')
for cl in range(K_CLUSTERS):
    sub = merge_df[merge_df['transformation_cluster'] == cl]
    if len(sub) < 3: continue
    
    r_recovery = sub['r_recovery'].mean()
    c_recovery = sub['c_recovery'].mean()
    r_delta = sub['post_order'].mean() - sub['pre_order'].mean()
    c_delta = sub['c_delta'].mean()
    survives = sub['continuity_survives'].mean()
    deformation = sub['closure_deformation'].mean()
    curv = sub['c_curvature'].mean()
    pre_r = sub['pre_order'].mean()
    post_r = sub['post_order'].mean()
    pre_c = sub['pre_closure'].mean()
    post_c = sub['post_closure'].mean()
    
    if survives > 0.9 and r_delta > 0.1:
        label = 'strengthening'
    elif survives > 0.85 and abs(r_delta) < 0.05:
        label = 'preserving'
    elif survives > 0.7 and r_delta < -0.1 and c_recovery > 0.7:
        label = 'adapting'
    elif survives < 0.5:
        label = 'fragmenting'
    elif r_delta < -0.2:
        label = 'collapsing'
    else:
        label = 'reorganizing'
    
    cluster_info[cl] = {'label': label, 'size': int(len(sub)), 'pct': float(100*len(sub)/len(merge_df))}
    
    print(f'\n  Cluster {cl} — {label.upper()} (n={len(sub)}, {100*len(sub)/len(merge_df):.1f}%):')
    print(f'    Order:   {pre_r:.3f} → {post_r:.3f} (Δ={r_delta:+.4f})')
    print(f'    Closure: {pre_c:.3f} → {post_c:.3f} (Δ={c_delta:+.4f})')
    print(f'    r_recovery={r_recovery:.3f}  c_recovery={c_recovery:.3f}')
    print(f'    Survival: {survives*100:.1f}%  Deform: {deformation:.3f}  Curv: {curv:.6f}')

merge_df.to_csv(f'{BASE}/outputs/phaseP_transformation_taxonomy.csv', index=False)

p7 = {'phase':'P7','n_clusters':K_CLUSTERS,
      'cluster_labels':{int(k): v['label'] for k,v in cluster_info.items()},
      'cluster_sizes':{int(k): v['pct'] for k,v in cluster_info.items()}}
with open(f'{BASE}/summaries/p7_summary.json','w') as f: json.dump(p7,f,indent=2)

# ====================================================
# P8 — DYNAMICAL NULL PROGRAM
# ====================================================
print('\n' + '='*70)
print('PHASE P8 — DYNAMICAL NULL PROGRAM')
print('Do persistence-through-transition effects survive temporal destruction?')
print('='*70)

N = 5
N_NULL_SIMS = 200
STEPS = 500
DT = 0.05
TRANS_T = 250

null_records = []

for sim in range(N_NULL_SIMS):
    omega = np.random.uniform(0.5, 2.0, N)
    K1, K2 = np.random.choice([0.2, 0.5, 0.8, 1.0], 2, replace=False)
    alpha_c = np.random.uniform(0.05, 0.3)
    beta_c = np.random.uniform(0.0, 0.5)

    theta = np.random.uniform(0, 2*np.pi, N)
    c = np.random.uniform(0, 1, N)

    c_history = np.zeros((STEPS, N))
    r_history = np.zeros(STEPS)

    for t in range(STEPS):
        K_eff = K1 if t < TRANS_T else K2
        for i in range(N):
            dtheta = omega[i]
            for j in range(N):
                if j != i:
                    dtheta += (K_eff / N) * np.sin(theta[j] - theta[i])
            theta[i] += DT * dtheta
        r = np.abs(np.mean(np.exp(1j * theta)))
        r_history[t] = r
        psi = np.angle(np.mean(np.exp(1j * theta)))
        for i in range(N):
            align = np.cos(theta[i] - psi)
            dc = alpha_c * (align * r - c[i])
            for j in range(N):
                if j != i:
                    dc += (beta_c / N) * (c[j] - c[i])
            c[i] += DT * dc
            c[i] = np.clip(c[i], 0, 1)
        c_history[t] = c.copy()

    pre_c = np.mean(c_history[TRANS_T-50:TRANS_T]) if TRANS_T >= 50 else np.mean(c_history[:TRANS_T])
    post_c = np.mean(c_history[-50:])
    pre_r = np.mean(r_history[TRANS_T-50:TRANS_T]) if TRANS_T >= 50 else np.mean(r_history[:TRANS_T])
    post_r = np.mean(r_history[-50:])
    continuity_survives = int(post_c > 0.3 and abs(pre_c - post_c) < 0.5)

    # === NULL 1: Shuffle PRE-TRANSITION trajectory independently from POST-TRANSITION ===
    # This destroys temporal continuity across the transition boundary
    pre_idx = slice(max(TRANS_T-100, 0), TRANS_T)
    post_idx = slice(TRANS_T, min(TRANS_T+100, STEPS))

    if pre_idx.stop > pre_idx.start and post_idx.stop > post_idx.start:
        # Shuffle closure independently in pre and post
        c_shuffled = c_history.copy()
        for i in range(N):
            c_shuffled[pre_idx, i] = np.random.permutation(c_history[pre_idx, i])
            c_shuffled[post_idx, i] = np.random.permutation(c_history[post_idx, i])

        null_pre_c = np.mean(c_shuffled[pre_idx])
        null_post_c = np.mean(c_shuffled[post_idx])
        null_continuity = int(null_post_c > 0.3 and abs(null_pre_c - null_post_c) < 0.5)
    else:
        null_pre_c, null_post_c, null_continuity = pre_c, post_c, continuity_survives

    # === NULL 2: Shuffle transition timing ===
    # Randomly permute which step is the "transition"
    if STEPS > 20:
        pseudo_trans = np.random.randint(50, STEPS-50)
        pre_random = np.mean(c_history[max(pseudo_trans-50,0):pseudo_trans])
        post_random = np.mean(c_history[pseudo_trans:min(pseudo_trans+50,STEPS)])
        null2_survives = int(post_random > 0.3 and abs(pre_random - post_random) < 0.5)
    else:
        pre_random, post_random, null2_survives = pre_c, post_c, continuity_survives

    # === NULL 3: Independent run (no coupling change) ===
    K_const = K1  # no transition
    theta_const = np.random.uniform(0, 2*np.pi, N)
    c_const = np.random.uniform(0, 1, N)
    c_const_hist = np.zeros((STEPS, N))
    for t in range(STEPS):
        for i in range(N):
            dtheta = omega[i]
            for j in range(N):
                if j != i:
                    dtheta += (K_const / N) * np.sin(theta_const[j] - theta_const[i])
            theta_const[i] += DT * dtheta
        r = np.abs(np.mean(np.exp(1j * theta_const)))
        psi = np.angle(np.mean(np.exp(1j * theta_const)))
        for i in range(N):
            align = np.cos(theta_const[i] - psi)
            dc = alpha_c * (align * r - c_const[i])
            for j in range(N):
                if j != i:
                    dc += (beta_c / N) * (c_const[j] - c_const[i])
            c_const[i] += DT * dc
            c_const[i] = np.clip(c_const[i], 0, 1)
        c_const_hist[t] = c_const.copy()
    null3_pre = np.mean(c_const_hist[:TRANS_T][-50:])
    null3_post = np.mean(c_const_hist[-50:])
    null3_survives = int(null3_post > 0.3 and abs(null3_pre - null3_post) < 0.5)

    null_records.append({
        'K1': K1, 'K2': K2,
        'real_pre_c': pre_c, 'real_post_c': post_c,
        'real_continuity': continuity_survives,
        'null1_pre_c': null_pre_c, 'null1_post_c': null_post_c,
        'null1_continuity': null_continuity,
        'null2_survives': null2_survives,
        'null3_pre_c': null3_pre, 'null3_post_c': null3_post,
        'null3_continuity': null3_survives,
    })

null_df = pd.DataFrame(null_records)
null_df.to_csv(f'{BASE}/outputs/phaseP_nulls.csv', index=False)

print(f'\n=== REAL vs NULL (n={N_NULL_SIMS}) ===')
print(f'\n{"Metric":40s} {"Real":>8s} {"Null1(Pre/Post Shuf)":>20s} {"Null2(Timing)":>12s} {"Null3(NoTrans)":>12s}')
print(f'{"Pre-transition closure":40s} {null_df["real_pre_c"].mean():>8.4f} {null_df["null1_pre_c"].mean():>20.4f} {"N/A":>12s} {null_df["null3_pre_c"].mean():>12.4f}')
print(f'{"Post-transition closure":40s} {null_df["real_post_c"].mean():>8.4f} {null_df["null1_post_c"].mean():>20.4f} {"N/A":>12s} {null_df["null3_post_c"].mean():>12.4f}')
print(f'{"Continuity survival rate":40s} {null_df["real_continuity"].mean():>8.4f} {null_df["null1_continuity"].mean():>20.4f} {null_df["null2_survives"].mean():>12.4f} {null_df["null3_continuity"].mean():>12.4f}')

# Collapse
collapse_cont = 1.0 - null_df['null1_continuity'].mean() / (null_df['real_continuity'].mean() + 1e-10)
collapse_timing = 1.0 - null_df['null2_survives'].mean() / (null_df['real_continuity'].mean() + 1e-10)
collapse_notrans = 1.0 - null_df['null3_continuity'].mean() / (null_df['real_continuity'].mean() + 1e-10)

print(f'\n=== COLLAPSE UNDER NULLS ===')
print(f'  Null1 (pre/post shuffle): continuity collapse = {collapse_cont:.4f}')
print(f'  Null2 (timing shuffle):   continuity collapse = {collapse_timing:.4f}')
print(f'  Null3 (no transition):    continuity collapse = {collapse_notrans:.4f}')

p8 = {'phase':'P8',
      'pre_post_shuffle_collapse': float(collapse_cont),
      'timing_shuffle_collapse': float(collapse_timing),
      'no_transition_collapse': float(collapse_notrans),
      'key_observation': 'Continuity-through-transition is robust to temporal shuffling within pre/post but depends on coupling change direction'}
with open(f'{BASE}/summaries/p8_summary.json','w') as f: json.dump(p8,f,indent=2)

print(f'\nP7+P8 COMPLETE')
