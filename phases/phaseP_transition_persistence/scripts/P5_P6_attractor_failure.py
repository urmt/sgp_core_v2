"""
Phase P5+P6 — TRANSITIONAL ATTRACTOR + FAILURE CASCADES

P5: Can recursive continuity stabilize around ongoing transformation itself?
P6: What cascading failures destroy continuity through transition?
"""
import sys, numpy as np, pandas as pd, os, json, warnings
sys.path.insert(0, '/home/student/sgp_core_v2')
warnings.filterwarnings('ignore')

SEED = 5002; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseP_transition_persistence'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

N = 5
STEPS = 600
DT = 0.05

# ====================================================
# P5 — Transitional Attractor Analysis
# ====================================================
N_SIMS_P5 = 300
trans_records = []

for sim in range(N_SIMS_P5):
    omega = np.random.uniform(0.5, 2.0, N)
    K = np.random.uniform(0.0, 1.0)
    alpha_c = np.random.uniform(0.05, 0.3)
    beta_c = np.random.uniform(0.0, K)

    theta = np.random.uniform(0, 2*np.pi, N)
    c = np.random.uniform(0, 1, N)

    c_history = np.zeros((STEPS, N))
    r_history = np.zeros(STEPS)

    for t in range(STEPS):
        if t < 200: K_eff = K
        elif t < 400: K_eff = K + 0.5 * np.sin(2*np.pi * (t-200) / 100)  # oscillatory transition
        else: K_eff = K

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

    # Boundary dwell time: time spent near transition boundary
    boundary_t = [t for t in range(200, 400) if 0.3 < r_history[t] < 0.7]
    dwell_time = len(boundary_t) / 200.0  # fraction of transition window in boundary

    # Transitional persistence: does closure stabilize during transition?
    c_var_during = np.std(np.mean(c_history[200:400], axis=1))
    c_var_pre = np.std(np.mean(c_history[50:200], axis=1))
    c_var_post = np.std(np.mean(c_history[400:550], axis=1))
    trans_stabilization = c_var_during < c_var_pre or c_var_during < c_var_post
    trans_locking = int(c_var_during < 0.01)

    # Attractor analysis: does the system stay in transition?
    r_mean_pre = np.mean(r_history[50:200])
    r_mean_during = np.mean(r_history[200:400])
    r_mean_post = np.mean(r_history[400:550])
    in_transition = int(abs(r_mean_during - 0.5) < 0.2)  # stayed intermediate

    trans_records.append({
        'K': K,
        'dwell_time': dwell_time,
        'c_var_during': c_var_during,
        'c_var_pre': c_var_pre,
        'c_var_post': c_var_post,
        'trans_stabilization': int(trans_stabilization),
        'trans_locking': trans_locking,
        'r_pre': r_mean_pre, 'r_during': r_mean_during, 'r_post': r_mean_post,
        'in_transition': in_transition,
        'mean_c': np.mean(c_history[-100:]),
    })

trans_df = pd.DataFrame(trans_records)
trans_df.to_csv(f'{BASE}/outputs/phaseP_transitional_persistence.csv', index=False)

print('='*70)
print('PHASE P5 — TRANSITIONAL ATTRACTOR ANALYSIS')
print('Can recursive continuity stabilize around ongoing transformation?')
print('='*70)

print(f'\n  Dwell time (fraction in boundary):     {trans_df["dwell_time"].mean():.4f}')
print(f'  Closure variance during transition:    {trans_df["c_var_during"].mean():.6f}')
print(f'  Closure variance pre-transition:       {trans_df["c_var_pre"].mean():.6f}')
print(f'  Closure variance post-transition:      {trans_df["c_var_post"].mean():.6f}')
print(f'  Systems with trans stabilization:      {trans_df["trans_stabilization"].mean()*100:.1f}%')
print(f'  Systems with trans locking:            {trans_df["trans_locking"].mean()*100:.1f}%')
print(f'  Systems that stay in transition:       {trans_df["in_transition"].mean()*100:.1f}%')
print(f'  Mean r pre→during→post:                {trans_df["r_pre"].mean():.3f} → {trans_df["r_during"].mean():.3f} → {trans_df["r_post"].mean():.3f}')

# Does closure vary less during transition than before?
print(f'\n=== VARIANCE COMPARISON ===')
print(f'  c_var_during < c_var_pre:  {np.mean(trans_df["c_var_during"] < trans_df["c_var_pre"])*100:.1f}%')
print(f'  c_var_during < c_var_post: {np.mean(trans_df["c_var_during"] < trans_df["c_var_post"])*100:.1f}%')

p5 = {'phase':'P5','trans_stabilization_rate':float(trans_df['trans_stabilization'].mean()),
      'transitional_locking_rate':float(trans_df['trans_locking'].mean()),
      'stayed_in_transition_rate':float(trans_df['in_transition'].mean())}
with open(f'{BASE}/summaries/p5_summary.json','w') as f: json.dump(p5,f,indent=2)

# ====================================================
# P6 — Failure Cascades
# ====================================================
print('\n' + '='*70)
print('PHASE P6 — FAILURE CASCADES')
print('What cascading failures destroy continuity through transition?')
print('='*70)

N_SIMS_P6 = 300
fail_records = []

for sim in range(N_SIMS_P6):
    omega = np.random.uniform(0.5, 2.0, N)
    K = np.random.uniform(0.0, 1.0)
    alpha_c = np.random.uniform(0.05, 0.3)
    beta_c = np.random.uniform(0.0, K)

    theta = np.random.uniform(0, 2*np.pi, N)
    c = np.random.uniform(0, 1, N)

    # Run pre-transition to establish baseline
    c_pre = np.zeros((200, N))
    r_pre = np.zeros(200)
    theta_p = theta.copy()
    c_p = c.copy()

    for t in range(200):
        for i in range(N):
            dtheta = omega[i]
            for j in range(N):
                if j != i:
                    dtheta += (K / N) * np.sin(theta_p[j] - theta_p[i])
            theta_p[i] += DT * dtheta
        r = np.abs(np.mean(np.exp(1j * theta_p)))
        r_pre[t] = r
        psi = np.angle(np.mean(np.exp(1j * theta_p)))
        for i in range(N):
            align = np.cos(theta_p[i] - psi)
            dc = alpha_c * (align * r - c_p[i])
            for j in range(N):
                if j != i:
                    dc += (beta_c / N) * (c_p[j] - c_p[i])
            c_p[i] += DT * dc
            c_p[i] = np.clip(c_p[i], 0, 1)
        c_pre[t] = c_p.copy()

    base_c = np.mean(c_pre[-50:])
    base_r = np.mean(r_pre[-50:])

    # Apply multiple perturbation types in cascade
    perturbation_types = [
        'temporal_disruption', 'closure_collapse', 'coupling_fragmentation',
        'desync_shock', 'all_disruption',
    ]

    for pt_name in perturbation_types:
        theta_pt = theta_p.copy()
        c_pt = c_p.copy()
        K_pt = K
        omega_pt = omega.copy()

        # Apply perturbation
        if pt_name == 'temporal_disruption':
            theta_pt = theta_pt + np.random.uniform(-np.pi, np.pi, N)
        elif pt_name == 'closure_collapse':
            c_pt = c_pt * 0.3
        elif pt_name == 'coupling_fragmentation':
            K_pt = K_pt * 0.1
        elif pt_name == 'desync_shock':
            omega_pt = omega_pt + np.random.uniform(-2, 2, N)
        elif pt_name == 'all_disruption':
            theta_pt = theta_pt + np.pi
            c_pt = c_pt * 0.1
            K_pt = K_pt * 0.05
            omega_pt = omega_pt + np.random.uniform(-3, 3, N)

        theta_pt = np.mod(theta_pt, 2*np.pi)

        # Run post-perturbation for 300 steps
        post_c = np.zeros((300, N))
        post_r = np.zeros(300)

        for t in range(300):
            for i in range(N):
                dtheta = omega_pt[i]
                for j in range(N):
                    if j != i:
                        dtheta += (K_pt / N) * np.sin(theta_pt[j] - theta_pt[i])
                theta_pt[i] += DT * dtheta

            r = np.abs(np.mean(np.exp(1j * theta_pt)))
            post_r[t] = r
            psi = np.angle(np.mean(np.exp(1j * theta_pt)))

            for i in range(N):
                align = np.cos(theta_pt[i] - psi)
                dc = alpha_c * (align * r - c_pt[i])
                for j in range(N):
                    if j != i:
                        dc += (beta_c / N) * (c_pt[j] - c_pt[i])
                c_pt[i] += DT * dc
                c_pt[i] = np.clip(c_pt[i], 0, 1)
            post_c[t] = c_pt.copy()

        # Metrics
        post_c_final = np.mean(post_c[-50:])
        post_r_final = np.mean(post_r[-50:])

        recovery_r = min(1.0, post_r_final / (base_r + 0.001))
        recovery_c = min(1.0, post_c_final / (base_c + 0.001))

        # Continuity collapse cascade
        c_drop = max(0, base_c - np.min(post_c))
        cascade_depth = c_drop / (base_c + 0.001)
        irreversible = int(post_c_final < 0.2 and base_c > 0.4)

        # Identity branching: do closures split?
        final_c_range = np.max(post_c[-1]) - np.min(post_c[-1])
        branching = int(final_c_range > 0.5 and np.mean(post_r[-50:]) < 0.4)

        fail_records.append({
            'perturbation_type': pt_name, 'K': K,
            'base_c': base_c, 'base_r': base_r,
            'post_c': post_c_final, 'post_r': post_r_final,
            'recovery_c': recovery_c, 'recovery_r': recovery_r,
            'cascade_depth': cascade_depth,
            'final_c_range': final_c_range,
            'irreversible': irreversible,
            'branching': branching,
        })

fail_df = pd.DataFrame(fail_records)
fail_df.to_csv(f'{BASE}/outputs/phaseP_failure_cascades.csv', index=False)

print(f'\n=== CASCADE FAILURE MODES (n={len(fail_df)}) ===')
for pt in ['temporal_disruption','closure_collapse','coupling_fragmentation','desync_shock','all_disruption']:
    sub = fail_df[fail_df['perturbation_type'] == pt]
    print(f'  {pt:25s}: rec_c={sub["recovery_c"].mean():.4f}  rec_r={sub["recovery_r"].mean():.4f}  '
          f'cascade={sub["cascade_depth"].mean():.4f}  '
          f'irrev={sub["irreversible"].mean()*100:.1f}%  branch={sub["branching"].mean()*100:.1f}%')

print(f'\n=== BY COUPLING STRENGTH ===')
for q in [(0,0.3),(0.3,0.7),(0.7,1.0)]:
    sub = fail_df[(fail_df['K']>=q[0]) & (fail_df['K']<q[1])]
    print(f'  K=[{q[0]},{q[1]}): n={len(sub):3d}  rec_c={sub["recovery_c"].mean():.4f}  '
          f'cascade={sub["cascade_depth"].mean():.4f}  '
          f'irrev={sub["irreversible"].mean()*100:.1f}%')

# Most destructive combination
print(f'\n=== MOST DESTRUCTIVE ===')
worst = fail_df.loc[fail_df['cascade_depth'].idxmax()]
print(f'  Worst cascade: {worst["perturbation_type"]} at K={worst["K"]:.3f} '
      f'(depth={worst["cascade_depth"]:.4f})')

p6 = {'phase':'P6','irreversible_failure_rate':float(fail_df['irreversible'].mean()),
      'cascade_depth_mean':float(fail_df['cascade_depth'].mean())}
with open(f'{BASE}/summaries/p6_summary.json','w') as f: json.dump(p6,f,indent=2)

print(f'\nP5+P6 COMPLETE')
