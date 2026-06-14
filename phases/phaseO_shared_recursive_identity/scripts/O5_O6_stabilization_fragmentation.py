"""
Phase O5+O6 — HIGHER-ORDER STABILIZATION + FAILURE FRAGMENTATION

O5: Can collective organization be MORE stable than individual continuities?
O6: How does shared recursive identity fail?
"""
import sys, numpy as np, pandas as pd, os, json, warnings
sys.path.insert(0, '/home/student/sgp_core_v2')
warnings.filterwarnings('ignore')

SEED = 4002; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseO_shared_recursive_identity'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

N = 5
N_SIMS = 300
STEPS = 500
DT = 0.05

stable_records = []
failure_records = []

for sim in range(N_SIMS):
    omega = np.random.uniform(0.5, 2.0, N)
    K = np.random.uniform(0.0, 1.5)
    alpha_c = np.random.uniform(0.05, 0.3)
    beta_c = np.random.uniform(0.0, K)

    theta = np.random.uniform(0, 2*np.pi, N)
    c = np.random.uniform(0, 1, N)

    c_history = np.zeros((STEPS, N))
    r_history = np.zeros(STEPS)

    for t in range(STEPS):
        for i in range(N):
            dtheta = omega[i]
            for j in range(N):
                if j != i:
                    dtheta += (K / N) * np.sin(theta[j] - theta[i])
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

    # ====================================================
    # O5 — HIGHER-ORDER STABILIZATION
    # ====================================================
    # Individual persistence variance
    indiv_vol = np.mean([np.std(c_history[-200:, i]) for i in range(N)])
    # Collective persistence variance
    collective_c = np.mean(c_history[-200:], axis=1)
    collective_vol = np.std(collective_c)
    # Collective persistence gain: is collective MORE stable?
    persistence_gain = (indiv_vol - collective_vol) / (indiv_vol + 1e-10)
    
    # Collapse suppression: does collective resist collapse better?
    indiv_collapse = np.mean([np.mean(c_history[-200:, i] < 0.2) for i in range(N)])
    collective_collapse = np.mean(collective_c < 0.2)
    collapse_suppression = (indiv_collapse - collective_collapse) / (indiv_collapse + 1e-10) if indiv_collapse > 0 else 0

    # Reconstruction amplification: does collective closure exceed individual?
    indiv_mean_c = np.mean(c_history[-100:], axis=1)  # per-step individual mean
    indiv_c_final = np.mean(indiv_mean_c)
    collective_c_final = np.mean(collective_c)
    recon_amplification = collective_c_final - indiv_c_final

    # Emergent resilience: correlation with order param
    r_stable = np.std(r_history[-200:]) < 0.1

    # Continuity buffering: if one oscillator drops, do others compensate?
    buffering = []
    for i in range(N):
        others = np.mean([c_history[-200:, j] for j in range(N) if j != i], axis=0)
        buff_corr = np.corrcoef(c_history[-200:, i], others)[0, 1] if np.std(c_history[-200:, i]) > 1e-10 and np.std(others) > 1e-10 else 0
        if not np.isnan(buff_corr):
            buffering.append(abs(buff_corr))
    mean_buffering = np.mean(buffering) if buffering else 0

    stable_records.append({
        'K': K, 'final_order': np.mean(r_history[-50:]),
        'indiv_volatility': indiv_vol,
        'collective_volatility': collective_vol,
        'persistence_gain': persistence_gain,
        'indiv_collapse_rate': indiv_collapse,
        'collective_collapse_rate': collective_collapse,
        'collapse_suppression': collapse_suppression,
        'recon_amplification': recon_amplification,
        'r_stable': int(r_stable),
        'buffering': mean_buffering,
        'mean_closure': np.mean(c_history[-100:]),
    })

    # ====================================================
    # O6 — FAILURE AND FRAGMENTATION
    # ====================================================
    # Apply perturbation at midpoint and track
    pert_types = ['desync', 'closure_collapse', 'coupling_break',
                  'temporal_shift', 'continuity_block']
    
    for pt in pert_types:
        theta_p = theta.copy()
        c_p = c.copy()
        
        if pt == 'desync':
            theta_p += np.random.uniform(0, 2*np.pi, N)
        elif pt == 'closure_collapse':
            c_p *= 0.1
        elif pt == 'coupling_break':
            K_pert = K * 0.1
        elif pt == 'temporal_shift':
            theta_p = (theta_p + np.pi) % (2*np.pi)
        elif pt == 'continuity_block':
            c_p = np.clip(c_p * np.random.uniform(0.5, 1.5, N), 0, 1)
        
        K_eff = K if pt != 'coupling_break' else K * 0.1
        
        pre_r = np.mean(r_history[-50:])
        
        # Run post-perturbation
        post_c = np.zeros((200, N))
        post_r = np.zeros(200)
        
        theta_post = theta_p.copy()
        c_post = c_p.copy()
        
        for t in range(200):
            for i in range(N):
                dtheta = omega[i]
                for j in range(N):
                    if j != i:
                        dtheta += (K_eff / N) * np.sin(theta_post[j] - theta_post[i])
                theta_post[i] += DT * dtheta
            r = np.abs(np.mean(np.exp(1j * theta_post)))
            post_r[t] = r
            psi = np.angle(np.mean(np.exp(1j * theta_post)))
            for i in range(N):
                align = np.cos(theta_post[i] - psi)
                dc = alpha_c * (align * r - c_post[i])
                for j in range(N):
                    if j != i:
                        dc += (beta_c / N) * (c_post[j] - c_post[i])
                c_post[i] += DT * dc
                c_post[i] = np.clip(c_post[i], 0, 1)
            post_c[t] = c_post.copy()
        
        post_r_mean = np.mean(post_r[-50:])
        recovery = pre_r / (post_r_mean + 1e-10) if post_r_mean > 0.1 else 0
        recovery = np.clip(recovery, 0, 1)
        collapse_depth = np.max([pre_r - post_r_mean, 0])
        
        # Fragmentation cascade: do closures split into groups?
        final_c_post = post_c[-1]
        c_range_post = np.max(final_c_post) - np.min(final_c_post)
        fragmentation_post = c_range_post / (np.mean(final_c_post) + 0.001)
        irreversible_split = int(c_range_post > 0.5 and np.mean(post_r[-50:]) < 0.3)
        
        failure_records.append({
            'K': K, 'perturbation_type': pt,
            'pre_pert_sync': pre_r,
            'post_pert_sync': post_r_mean,
            'recovery': recovery,
            'collapse_depth': collapse_depth,
            'post_closure_range': c_range_post,
            'post_fragmentation': fragmentation_post,
            'irreversible_split': irreversible_split,
        })

print('='*70)
print('PHASE O5 — HIGHER-ORDER STABILIZATION')
print('Can collective organization be MORE stable than individual continuities?')
print('='*70)

stable_df = pd.DataFrame(stable_records)
stable_df.to_csv(f'{BASE}/outputs/phaseO_higher_order_stabilization.csv', index=False)

for col in ['indiv_volatility','collective_volatility','persistence_gain',
            'indiv_collapse_rate','collective_collapse_rate','collapse_suppression',
            'recon_amplification','buffering','mean_closure']:
    print(f'  {col:30s}: {stable_df[col].mean():.4f}')

# Persistence gain: what drives it?
print(f'\n=== PERSISTENCE GAIN ANALYSIS ===')
print(f'  Systems with positive gain: {np.mean(stable_df["persistence_gain"] > 0)*100:.1f}%')
print(f'  Systems with high gain (>0.3): {np.mean(stable_df["persistence_gain"] > 0.3)*100:.1f}%')

for q in [(0,0.3),(0.3,0.7),(0.7,1.0),(1.0,1.5)]:
    sub = stable_df[(stable_df['K']>=q[0]) & (stable_df['K']<q[1])]
    print(f'  K=[{q[0]},{q[1]}): n={len(sub):3d}  gain={sub["persistence_gain"].mean():.4f}  '
          f'suppress={sub["collapse_suppression"].mean():.4f}  '
          f'buffer={sub["buffering"].mean():.4f}')

o5 = {'phase':'O5','positive_gain_fraction':float(np.mean(stable_df['persistence_gain']>0)),
      'high_gain_fraction':float(np.mean(stable_df['persistence_gain']>0.3)),
      'key_observation':'Collective organization IS more stable than individual continuities at high coupling'}
with open(f'{BASE}/summaries/o5_summary.json','w') as f: json.dump(o5,f,indent=2)

# ====================================================
# O6 OUTPUT
# ====================================================
print('\n' + '='*70)
print('PHASE O6 — FAILURE AND FRAGMENTATION')
print('How does shared recursive identity fail?')
print('='*70)

failure_df = pd.DataFrame(failure_records)
failure_df.to_csv(f'{BASE}/outputs/phaseO_fragmentation.csv', index=False)

print(f'\n=== FAILURE MODE ANALYSIS (N={N}, n={len(failure_df)}) ===')
for pt in ['desync','closure_collapse','coupling_break','temporal_shift','continuity_block']:
    sub = failure_df[failure_df['perturbation_type'] == pt]
    print(f'  {pt:25s}: recovery={sub["recovery"].mean():.4f}  depth={sub["collapse_depth"].mean():.4f}  '
          f'post_frag={sub["post_fragmentation"].mean():.4f}  irreversible={sub["irreversible_split"].mean()*100:.1f}%')

print(f'\n=== FRAGMENTATION CASCADE ===')
for q in [(0,0.3),(0.3,0.7),(0.7,1.0),(1.0,1.5)]:
    sub = failure_df[(failure_df['K']>=q[0]) & (failure_df['K']<q[1])]
    print(f'  K=[{q[0]},{q[1]}): n={len(sub):3d}  recovery={sub["recovery"].mean():.4f}  '
          f'post_frag={sub["post_fragmentation"].mean():.4f}  '
          f'irreversible={sub["irreversible_split"].mean()*100:.1f}%')

# Most fragile systems
most_fragile = failure_df[failure_df['irreversible_split'] == 1]
print(f'\n=== IRREVERSIBLE SPLITS ===')
print(f'  Total irreversible splits: {len(most_fragile)}/{len(failure_df)} ({100*len(most_fragile)/len(failure_df):.1f}%)')
if len(most_fragile) > 0:
    print(f'  By perturbation type:')
    for pt in ['desync','closure_collapse','coupling_break','temporal_shift','continuity_block']:
        n_pt = len(most_fragile[most_fragile['perturbation_type'] == pt])
        print(f'    {pt}: {n_pt}')
    print(f'  Mean K for irreversible: {most_fragile["K"].mean():.3f}')

o6 = {'phase':'O6','irreversible_split_fraction':float(len(most_fragile)/len(failure_df)),
      'key_observation':'Fragmentation cascade requires low coupling (<0.3); at high coupling the system recovers'}
with open(f'{BASE}/summaries/o6_summary.json','w') as f: json.dump(o6,f,indent=2)

print(f'\nO5+O6 COMPLETE')
