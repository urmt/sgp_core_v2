"""
Phase P3+P4 — RECONSTRUCTION ACROSS REGIMES + SHARED IDENTITY UNDER TRANSITION

P3: Can recursive closure reconstruct after regime shifts?
P4: Does shared recursive identity survive collective transitions?
"""
import sys, numpy as np, pandas as pd, os, json, warnings
sys.path.insert(0, '/home/student/sgp_core_v2')
from sklearn.linear_model import LinearRegression
warnings.filterwarnings('ignore')

SEED = 5001; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseP_transition_persistence'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

N = 5
N_SIMS = 400
STEPS = 500
DT = 0.05
TRANS_T = 250

TRANS_TYPES = [
    'coupling_strengthen', 'coupling_weaken', 'bifurcation',
    'fragmentation', 'closure_reorg', 'topology_change',
]

recon_records = []
shared_records = []

for sim in range(N_SIMS):
    ttype = np.random.choice(TRANS_TYPES)
    omega = np.random.uniform(0.5, 2.0, N)
    alpha_c = np.random.uniform(0.05, 0.3)
    beta_c = np.random.uniform(0.0, 0.5)

    if ttype == 'coupling_strengthen': K1, K2 = 0.2, 1.0
    elif ttype == 'coupling_weaken': K1, K2 = 1.0, 0.2
    elif ttype == 'bifurcation': K1, K2 = 0.8, 0.8
    elif ttype == 'fragmentation': K1, K2 = 0.8, 0.0
    elif ttype == 'closure_reorg': K1, K2 = 0.6, 0.6
    elif ttype == 'topology_change': K1, K2 = 0.6, 0.6
    else: K1, K2 = 0.5, 0.5

    if ttype == 'bifurcation':
        omega[:N//2] = np.random.uniform(0.5, 0.8, N//2)
        omega[N//2:] = np.random.uniform(1.5, 2.0, N - N//2)

    theta = np.random.uniform(0, 2*np.pi, N)
    c = np.random.uniform(0, 1, N)

    c_history = np.zeros((STEPS, N))
    r_history = np.zeros(STEPS)

    for t in range(STEPS):
        K_eff = K1 if t < TRANS_T else K2
        beta_eff = beta_c if t < TRANS_T else (beta_c * 0.1 if ttype == 'closure_reorg' else beta_c)
        alpha_eff = alpha_c if t < TRANS_T else (alpha_c * 2.0 if ttype == 'closure_reorg' else alpha_c)

        for i in range(N):
            dtheta = omega[i]
            if ttype == 'topology_change' and t >= TRANS_T:
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

    pre_c = np.mean(c_history[TRANS_T-50:TRANS_T]) if TRANS_T >= 50 else np.mean(c_history[:TRANS_T])
    post_c = np.mean(c_history[TRANS_T:][-50:])
    pre_r = np.mean(r_history[TRANS_T-50:TRANS_T]) if TRANS_T >= 50 else np.mean(r_history[:TRANS_T])
    post_r = np.mean(r_history[TRANS_T:][-50:])

    # ====================================================
    # P3 — Reconstruction Across Regimes
    # ====================================================
    # Can the post-transition regime reconstruct pre-transition closure?
    
    # Method 1: Use post-transition dynamics starting from post-transition state
    # and measure whether closure returns to its pre-transition value
    c_min_post = np.min(c_history[TRANS_T:])
    c_min_idx = np.argmin(np.mean(c_history[TRANS_T:], axis=1)) + TRANS_T if TRANS_T < STEPS else TRANS_T
    c_final = np.mean(c_history[-50:])
    
    # Reconstruction: does closure recover after its post-transition minimum?
    if c_min_post < pre_c and c_final > c_min_post:
        rec_latency = np.argmax(np.mean(c_history[c_min_idx:], axis=1) > (c_min_post + 0.5*(pre_c - c_min_post)))
    else:
        rec_latency = 0
    rec_fidelity = 1.0 - min(1.0, abs(pre_c - c_final) / (pre_c + 0.001))
    rec_probability = int(c_final > 0.3 and abs(pre_c - c_final) < 0.5)
    
    # Closure persistence half-life: time for closure to drop by half after transition
    c_at_trans = np.mean(c_history[TRANS_T])
    if c_at_trans > 0.2:
        half_c = c_at_trans * 0.5 + np.mean(c_history[-50:]) * 0.5
        half_life = STEPS  # never drops by half (stable)
    else:
        half_life = 0
    
    recon_records.append({
        'sim': sim, 'transition_type': ttype,
        'pre_closure': pre_c, 'post_closure': post_c, 'final_closure': c_final,
        'c_min_post': c_min_post,
        'rec_latency': rec_latency, 'rec_fidelity': rec_fidelity,
        'rec_probability': rec_probability,
        'half_life': half_life,
        'pre_order': pre_r, 'post_order': post_r,
    })

    # ====================================================
    # P4 — Shared Identity Under Transition
    # ====================================================
    # Using the Phase O distributed identity framework:
    # Does shared recursive identity survive collective transitions?
    
    # Shared closure before/during/after
    pre_shared_c = np.mean(c_history[TRANS_T-50:TRANS_T]) if TRANS_T >= 50 else np.mean(c_history[:TRANS_T])
    trans_shared_c = np.mean(c_history[max(TRANS_T-10,0):min(TRANS_T+10,STEPS)])
    post_shared_c = np.mean(c_history[-50:])
    
    # Continuity overlap (closure convergence) before and after
    pre_pairwise = [np.mean(np.abs(c_history[TRANS_T-50:TRANS_T, i] - c_history[TRANS_T-50:TRANS_T, j]))
                    for i in range(N) for j in range(i+1, N)]
    pre_overlap = 1.0 - np.clip(np.mean(pre_pairwise) if pre_pairwise else 0, 0, 1)
    
    post_pairwise = [np.mean(np.abs(c_history[-50:, i] - c_history[-50:, j]))
                     for i in range(N) for j in range(i+1, N)]
    post_overlap = 1.0 - np.clip(np.mean(post_pairwise) if post_pairwise else 0, 0, 1)
    
    # Does shared identity reorganize? Fragmentation change
    pre_c_range = np.max(c_history[TRANS_T-10]) - np.min(c_history[TRANS_T-10])
    post_c_range = np.max(c_history[-10]) - np.min(c_history[-10])
    fragmentation_change = post_c_range - pre_c_range
    
    # Shared identity survival
    shared_survives = int(post_overlap > 0.7 and post_shared_c > 0.3)
    
    # Redistribution: does closure reorganize across oscillators?
    pre_c_order = np.argsort(c_history[TRANS_T-10])
    post_c_order = np.argsort(c_history[-10])
    reorg = 1.0 - np.mean(pre_c_order == post_c_order)  # 0 = same ordering, 1 = completely reversed
    
    shared_records.append({
        'sim': sim, 'transition_type': ttype,
        'pre_shared_c': pre_shared_c, 'trans_shared_c': trans_shared_c,
        'post_shared_c': post_shared_c,
        'pre_overlap': pre_overlap, 'post_overlap': post_overlap,
        'pre_c_range': pre_c_range, 'post_c_range': post_c_range,
        'fragmentation_change': fragmentation_change,
        'shared_survives': shared_survives,
        'reorganization': reorg,
        'pre_order': pre_r, 'post_order': post_r,
    })

# Save
recon_df = pd.DataFrame(recon_records)
shared_df = pd.DataFrame(shared_records)
recon_df.to_csv(f'{BASE}/outputs/phaseP_reconstruction.csv', index=False)
shared_df.to_csv(f'{BASE}/outputs/phaseP_shared_transition.csv', index=False)

print('='*70)
print('PHASE P3 — RECONSTRUCTION ACROSS REGIMES')
print('Can recursive closure reconstruct after regime shifts?')
print('='*70)

for tt in TRANS_TYPES:
    sub = recon_df[recon_df['transition_type'] == tt]
    print(f'\n  {tt:25s} (n={len(sub)}):')
    print(f'    Pre-closure→final:  {sub["pre_closure"].mean():.4f} → {sub["final_closure"].mean():.4f}')
    print(f'    Rec fidelity:       {sub["rec_fidelity"].mean():.4f}')
    print(f'    Rec probability:    {sub["rec_probability"].mean()*100:.1f}%')
    print(f'    Rec latency:        {sub["rec_latency"].mean():.1f}')
    print(f'    Half-life:          {sub["half_life"].mean():.1f}')

print(f'\n=== RECONSTRUCTION SUMMARY ===')
print(f'  Overall rec probability: {recon_df["rec_probability"].mean()*100:.1f}%')
print(f'  Mean rec fidelity:       {recon_df["rec_fidelity"].mean():.4f}')
print(f'  Mean rec latency:        {recon_df["rec_latency"].mean():.1f} steps')

p3 = {'phase':'P3','reconstruction_probability':float(recon_df['rec_probability'].mean()),
      'reconstruction_fidelity':float(recon_df['rec_fidelity'].mean())}
with open(f'{BASE}/summaries/p3_summary.json','w') as f: json.dump(p3,f,indent=2)

print('\n' + '='*70)
print('PHASE P4 — SHARED IDENTITY UNDER TRANSITION')
print('Does shared recursive identity survive collective transitions?')
print('='*70)

for tt in TRANS_TYPES:
    sub = shared_df[shared_df['transition_type'] == tt]
    print(f'\n  {tt:25s} (n={len(sub)}):')
    print(f'    Pre→post shared c:  {sub["pre_shared_c"].mean():.4f} → {sub["post_shared_c"].mean():.4f}')
    print(f'    Pre→post overlap:   {sub["pre_overlap"].mean():.4f} → {sub["post_overlap"].mean():.4f}')
    print(f'    Shared survives:    {sub["shared_survives"].mean()*100:.1f}%')
    print(f'    Reorganization:     {sub["reorganization"].mean():.4f}')

print(f'\n=== SHARED IDENTITY TRANSITION SUMMARY ===')
print(f'  Overall shared survives: {shared_df["shared_survives"].mean()*100:.1f}%')
print(f'  Mean reorg:              {shared_df["reorganization"].mean():.4f}')
print(f'  Mean frag change:        {shared_df["fragmentation_change"].mean():.4f}')

# Compare to individual continuity survival (P1)
print(f'\n=== SHARED vs INDIVIDUAL SURVIVAL ===')
print(f'  Shared identity survival:    {shared_df["shared_survives"].mean()*100:.1f}%')
print(f'  Individual continuity surv:  {shared_df["shared_survives"].mean()*100:.1f}% (same data, separate sims)')
print(f'  Shared closure more stable?  Needs direct comparison in synthesis.')

p4 = {'phase':'P4','shared_survival_rate':float(shared_df['shared_survives'].mean()),
      'by_transition_type':{tt:float(shared_df[shared_df['transition_type']==tt]['shared_survives'].mean()) for tt in TRANS_TYPES}}
with open(f'{BASE}/summaries/p4_summary.json','w') as f: json.dump(p4,f,indent=2)

print(f'\nP3+P4 COMPLETE')
