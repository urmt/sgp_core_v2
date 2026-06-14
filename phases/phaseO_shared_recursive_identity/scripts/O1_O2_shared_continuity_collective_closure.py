"""
Phase O1+O2 — SHARED CONTINUITY + COLLECTIVE CLOSURE

O1: Can multiple recursive continuities generate higher-order continuity?
O2: Can closure become organizationally shared?

N-oscillator model (N=3,5,10) with all-to-all coupling.
Tracks collective order, shared closure, distributed reconstruction.
"""
import sys, numpy as np, pandas as pd, os, json, warnings
sys.path.insert(0, '/home/student/sgp_core_v2')
from sklearn.linear_model import LinearRegression
warnings.filterwarnings('ignore')

SEED = 4000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseO_shared_recursive_identity'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

N_OSCILLATORS = [3, 5, 10]
N_SIMS = 300
STEPS = 500
DT = 0.05

all_records = []
all_trajs = []
closure_records = []

for N in N_OSCILLATORS:
    for sim in range(N_SIMS):
        omega = np.random.uniform(0.5, 2.0, N)
        K = np.random.uniform(0.0, 1.0)
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
            psi = np.angle(np.mean(np.exp(1j * theta)))
            r_history[t] = r

            for i in range(N):
                align = np.cos(theta[i] - psi)
                dc = alpha_c * (align * r - c[i])
                for j in range(N):
                    if j != i:
                        dc += (beta_c / N) * (c[j] - c[i])
                c[i] += DT * dc
                c[i] = np.clip(c[i], 0, 1)
            c_history[t] = c.copy()

        # === O1 METRICS ===
        final_r = np.mean(r_history[-50:])
        sync_steps = np.argmax(r_history > 0.8) if np.any(r_history > 0.8) else STEPS
        shared_c = np.mean(c_history[-50:])
        c_std_final = np.mean(np.std(c_history[-50:], axis=1))
        closure_div = np.mean(np.std(c_history[-100:], axis=0))

        # Continuity overlap
        pairwise_diffs = [np.mean(np.abs(c_history[-50:, i] - c_history[-50:, j]))
                          for i in range(N) for j in range(i+1, N)]
        mean_pair_diff = np.mean(pairwise_diffs) if pairwise_diffs else 0
        continuity_overlap = 1.0 - np.clip(mean_pair_diff, 0, 1)

        r_vol = np.std(r_history[-200:]) if STEPS >= 200 else np.std(r_history)
        collective_persist = 1.0 - r_vol

        # Shared closure emergence (order-closure coupling)
        if np.std(r_history[-200:]) > 1e-10 and np.std(np.mean(c_history[-200:], axis=1)) > 1e-10:
            sce = np.corrcoef(r_history[-200:], np.mean(c_history[-200:], axis=1))[0, 1]
        else:
            sce = 0.0
        if np.isnan(sce): sce = 0.0

        # Coupling-closure link (correlation over FULL trajectory)
        if np.std(r_history) > 1e-10 and np.std(np.mean(c_history, axis=1)) > 1e-10:
            cc_r = np.corrcoef(r_history, np.mean(c_history, axis=1))[0, 1]
        else:
            cc_r = 0.0
        if np.isnan(cc_r): cc_r = 0.0

        all_records.append({
            'N': N, 'sim': sim, 'K': K, 'alpha_c': alpha_c, 'beta_c': beta_c,
            'final_order': final_r, 'sync_time': sync_steps,
            'shared_closure': shared_c, 'closure_divergence': closure_div,
            'continuity_overlap': continuity_overlap,
            'collective_persistence': collective_persist,
            'r_volatility': r_vol,
            'shared_closure_emergence': sce,
            'coupling_closure_r': cc_r,
            'mean_pairwise_diff': mean_pair_diff,
        })

        if sim < 15:
            for t in range(0, STEPS, 25):
                all_trajs.append({
                    'N': N, 'sim': sim, 'step': t, 'K': K,
                    'order_param': r_history[t],
                    'shared_closure': np.mean(c_history[t]),
                    'c_std': np.std(c_history[t]),
                })

        # === O2 METRICS ===
        # Cross-prediction of closure
        cross_pred_errors = []
        for target in range(N):
            others = [j for j in range(N) if j != target]
            if not others: continue
            X = c_history[100:, others]
            y = c_history[100:, target]
            if np.std(y) < 1e-10:
                cross_pred_errors.append(0.5); continue
            try:
                lr = LinearRegression()
                lr.fit(X, y)
                pred = lr.predict(X)
                err = np.mean(np.abs(pred - y)) / (np.std(y) + 1e-10)
                cross_pred_errors.append(err)
            except:
                cross_pred_errors.append(1.0)
        mean_cross_pred = np.mean(cross_pred_errors) if cross_pred_errors else 1.0

        collective_c = np.mean(c_history[-100:])
        final_c_vals = c_history[-1]
        c_range = np.max(final_c_vals) - np.min(final_c_vals)
        c_mid = np.mean(final_c_vals) if np.mean(final_c_vals) > 0 else 0.001
        closure_conv = 1.0 - np.clip(c_range / c_mid, 0, 1)
        high_c_frac = np.mean(final_c_vals > 0.5)

        closure_records.append({
            'N': N, 'sim': sim, 'K': K, 'alpha_c': alpha_c, 'beta_c': beta_c,
            'collective_closure': collective_c,
            'cross_prediction_error': mean_cross_pred,
            'closure_convergence': closure_conv,
            'high_closure_frac': high_c_frac,
            'final_order': final_r,
        })

    print(f'  N={N}: {N_SIMS} simulations done')

# Save
continuity_df = pd.DataFrame(all_records)
traj_df = pd.DataFrame(all_trajs)
closure_df = pd.DataFrame(closure_records)
continuity_df.to_csv(f'{BASE}/outputs/phaseO_shared_continuity.csv', index=False)
traj_df.to_csv(f'{BASE}/outputs/phaseO_shared_continuity_trajectories.csv', index=False)
closure_df.to_csv(f'{BASE}/outputs/phaseO_collective_closure.csv', index=False)

# ====================================================
# O1 OUTPUT
# ====================================================
print('='*70)
print('PHASE O1 — SHARED CONTINUITY FORMATION')
print('='*70)
for N in N_OSCILLATORS:
    sub = continuity_df[continuity_df['N'] == N]
    print(f'\n  N={N}:')
    print(f'    Final order:            {sub["final_order"].mean():.4f}')
    print(f'    Shared closure:         {sub["shared_closure"].mean():.4f}')
    print(f'    Continuity overlap:     {sub["continuity_overlap"].mean():.4f}')
    print(f'    Collective persistence: {sub["collective_persistence"].mean():.4f}')
    print(f'    Coupling-closure corr:  {sub["coupling_closure_r"].mean():.4f}')
    print(f'    Sync time:              {sub["sync_time"].mean():.1f}')

print('\n=== EFFECT OF COUPLING ===')
for q in [(0,0.2),(0.2,0.5),(0.5,0.8),(0.8,1.0)]:
    sub = continuity_df[(continuity_df['K']>=q[0]) & (continuity_df['K']<q[1])]
    print(f'  K=[{q[0]},{q[1]}): n={len(sub):3d}  order={sub["final_order"].mean():.3f}  '
          f'shared_c={sub["shared_closure"].mean():.3f}  overlap={sub["continuity_overlap"].mean():.3f}')

sc = continuity_df[(continuity_df['continuity_overlap']>0.7) &
                   (continuity_df['shared_closure']>0.5) &
                   (continuity_df['final_order']>0.8)]
print(f'\nShared continuity systems: {len(sc)}/{len(continuity_df)} ({100*len(sc)/len(continuity_df):.1f}%)')

# ====================================================
# O2 OUTPUT
# ====================================================
print('\n' + '='*70)
print('PHASE O2 — COLLECTIVE RECURSIVE CLOSURE')
print('='*70)
for N in N_OSCILLATORS:
    sub = closure_df[closure_df['N'] == N]
    print(f'\n  N={N}:')
    print(f'    Collective closure:      {sub["collective_closure"].mean():.4f}')
    print(f'    Cross-pred error:         {sub["cross_prediction_error"].mean():.4f}')
    print(f'    Closure convergence:      {sub["closure_convergence"].mean():.4f}')
    print(f'    High closure fraction:    {sub["high_closure_frac"].mean():.4f}')

shared_cl = closure_df[(closure_df['closure_convergence']>0.7) &
                       (closure_df['cross_prediction_error']<0.5) &
                       (closure_df['collective_closure']>0.4)]
print(f'\nDistributed closure systems: {len(shared_cl)}/{len(closure_df)} ({100*len(shared_cl)/len(closure_df):.1f}%)')

o1 = {'phase':'O1','N_sims':N_SIMS,'shared_continuity_fraction':float(len(sc)/len(continuity_df))}
o2 = {'phase':'O2','shared_closure_fraction':float(len(shared_cl)/len(closure_df))}
with open(f'{BASE}/summaries/o1_summary.json','w') as f: json.dump(o1,f,indent=2)
with open(f'{BASE}/summaries/o2_summary.json','w') as f: json.dump(o2,f,indent=2)
print(f'\nO1+O2 COMPLETE')
