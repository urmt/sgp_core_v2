"""
Phase R1+R2 — MECHANISM ABLATION HIERARCHY + MINIMAL CLOSURE MODEL

R1: Sequential removal of mechanisms, measuring continuity survival.
R2: Lowest-dimension closure process preserving continuity.

Uses existing Phase Q data + targeted small simulations.
"""
import sys, numpy as np, pandas as pd, os, json, warnings
sys.path.insert(0, '/home/student/sgp_core_v2')
warnings.filterwarnings('ignore')

SEED = 7000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseR_minimal_mechanisms'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

# Load existing data
try:
    q_hier = pd.read_csv(f'{BASE}/../phaseQ_recursive_invariants/outputs/phaseQ_invariant_hierarchy.csv')
    q_minimal = pd.read_csv(f'{BASE}/../phaseQ_recursive_invariants/outputs/phaseQ_minimal_invariants.csv')
    q_null = pd.read_csv(f'{BASE}/../phaseQ_recursive_invariants/outputs/phaseQ_strict_nulls.csv')
    print(f'Loaded: hierarchy={len(q_hier)}, minimal={len(q_minimal)}, strict_nulls={len(q_null)}')
except Exception as e:
    print(f'Warning: {e}')
    q_hier = q_minimal = q_null = None

N = 5
N_SIMS = 80
STEPS = 300
DT = 0.05

# ====================================================
# R1: MECHANISM ABLATION HIERARCHY
# ====================================================
print('='*70)
print('PHASE R1 — MECHANISM ABLATION HIERARCHY')
print('Sequential mechanism removal. Where does continuity fail?')
print('='*70)

# Progressive mechanism removal from FULL to NONE
# Each condition removes one more mechanism
ablation_conditions = [
    # (name, K, alpha_c, beta_c, topology, use_phase, use_closure_cross, use_reconstruction)
    # FULL — all mechanisms
    ('0_full', 0.8, 0.2, 0.3, 'all_to_all', True, True, True),
    # Remove reconstruction (closure cross-coupling gone)
    ('1_no_reconstruction', 0.8, 0.2, 0.0, 'all_to_all', True, False, True),
    # Remove phase coupling
    ('2_no_phase_coupling', 0.0, 0.2, 0.3, 'none', False, True, True),
    # Remove closure cross-coupling
    ('3_no_closure_cross', 0.8, 0.2, 0.0, 'all_to_all', True, False, True),
    # Remove topology (sparse random)
    ('4_no_topology', 0.8, 0.2, 0.3, 'sparse_10pct', True, True, True),
    # Remove temporal ordering (random timing jitter)
    ('5_no_temporal_order', 0.8, 0.2, 0.3, 'jitter', True, True, True),
    # Remove frequency alignment (random frequencies)
    ('6_no_freq_alignment', 0.8, 0.2, 0.3, 'all_to_all', True, True, False),
    # Phase coupling only (no closure self-dynamics)
    ('7_phase_only', 0.8, 0.0, 0.0, 'all_to_all', True, False, True),
    # Closure only (no phase coupling)
    ('8_closure_only', 0.0, 0.2, 0.3, 'none', False, True, True),
    # Scalar closure value only (no phase, no cross)
    ('9_scalar_only', 0.0, 0.05, 0.0, 'none', False, False, True),
    # Bare minimum: frequency alignment only
    ('10_freq_only', 0.0, 0.0, 0.0, 'none', False, False, False),
]

ablation_records = []

for name, K, alpha_c, beta_c, topo, use_phase, use_closure_cross, use_recon in ablation_conditions:
    survivals = []
    final_closures = []
    
    for sim in range(N_SIMS):
        omega = np.random.uniform(0.5, 2.0, N)
        if 'no_freq_alignment' in name:
            # Anti-aligned frequencies
            omega = np.random.uniform(0.5, 0.6, N) if np.random.random() < 0.5 else np.random.uniform(1.9, 2.0, N)
        
        theta = np.random.uniform(0, 2*np.pi, N)
        c = np.random.uniform(0, 1, N)
        
        for t in range(STEPS):
            # Phase evolution
            if use_phase:
                for i in range(N):
                    dtheta = omega[i]
                    if topo == 'all_to_all':
                        for j in range(N):
                            if j != i:
                                dtheta += (K / N) * np.sin(theta[j] - theta[i])
                    elif topo == 'sparse_10pct':
                        for j in range(N):
                            if j != i and np.random.random() < 0.1:
                                dtheta += (K / max(1, N*0.1)) * np.sin(theta[j] - theta[i])
                    elif topo == 'jitter':
                        for j in range(N):
                            if j != i:
                                dtheta += (K / N) * np.sin(theta[j] - theta[i] + np.random.uniform(-0.3, 0.3))
                    theta[i] += DT * dtheta
                theta = np.mod(theta, 2*np.pi)
            else:
                # No phase coupling — free run
                for i in range(N):
                    theta[i] += DT * omega[i]
                theta = np.mod(theta, 2*np.pi)
            
            r = np.abs(np.mean(np.exp(1j * theta)))
            psi = np.angle(np.mean(np.exp(1j * theta)))
            
            # Closure dynamics
            if alpha_c > 0:
                for i in range(N):
                    align = np.cos(theta[i] - psi)
                    dc = alpha_c * (align * r - c[i])
                    if use_closure_cross:
                        for j in range(N):
                            if j != i:
                                dc += (beta_c / N) * (c[j] - c[i])
                    c[i] += DT * dc
                    c[i] = np.clip(c[i], 0, 1)
            # else: c stays at initial value (scalar only)
        
        final_c = np.mean(c[-50:])
        final_closures.append(final_c)
        survivals.append(int(final_c > 0.3))
    
    mean_c = float(np.mean(final_closures))
    surv_rate = float(np.mean(survivals))
    
    ablation_records.append({
        'condition': name,
        'K': K, 'alpha_c': alpha_c, 'beta_c': beta_c,
        'use_phase_coupling': int(use_phase),
        'use_closure_cross': int(use_closure_cross),
        'mean_closure': mean_c,
        'survival_rate': surv_rate,
    })
    
    print(f'  {name:35s}: closure={mean_c:.4f}  survival={surv_rate*100:.1f}%  '
          f'(K={K}, α={alpha_c}, β={beta_c}, phase={int(use_phase)}, cross={int(use_closure_cross)})')

abl_df = pd.DataFrame(ablation_records)
abl_df.to_csv(f'{BASE}/outputs/R1_ablation_hierarchy.csv', index=False)

# Determine first-failure
print(f'\n=== FIRST-FAILURE ANALYSIS ===')
full_c = abl_df[abl_df['condition'] == '0_full']['mean_closure'].values[0]
print(f'  Full model closure: {full_c:.4f} (survival={abl_df[abl_df["condition"]=="0_full"]["survival_rate"].values[0]*100:.1f}%)')
print(f'')
print(f'  Progressive removal effects:')
for _, r in abl_df.iterrows():
    if r['condition'] == '0_full': continue
    drop = full_c - r['mean_closure']
    print(f'  {r["condition"]:35s}: closure Δ={drop:+.4f} → {r["mean_closure"]:.4f} (surv={r["survival_rate"]*100:.1f}%)')

# First mechanism whose removal causes failure
print(f'\n  FIRST FAILURE MECHANISMS (where survival < 50%):')
failures = abl_df[abl_df['survival_rate'] < 0.5]
for _, r in failures.iterrows():
    print(f'    {r["condition"]:35s}: closure={r["mean_closure"]:.4f} surv={r["survival_rate"]*100:.1f}%')

r1 = {'phase': 'R1', 'n_ablations': len(ablation_conditions),
      'full_closure': float(full_c),
      'first_failure_mechanisms': list(failures['condition'])}
with open(f'{BASE}/summaries/r1_summary.json','w') as f: json.dump(r1,f,indent=2)

# ====================================================
# R2: MINIMAL CLOSURE MODEL
# ====================================================
print('\n' + '='*70)
print('PHASE R2 — MINIMAL CLOSURE MODEL')
print('Lowest-dimension closure process preserving continuity.')
print('='*70)

# Construct progressive reduction models and test each
model_records = []

def run_model(model_type, params, n_sims=200):
    survivals = []
    final_cs = []
    for _ in range(n_sims):
        if model_type == 'full_recursive':
            # Full N-oscillator Kuramoto + closure
            N_m = params.get('N', 5)
            K_m = params.get('K', 0.8)
            alpha = params.get('alpha', 0.2)
            beta = params.get('beta', 0.3)
            omega = np.random.uniform(0.5, 2.0, N_m)
            theta = np.random.uniform(0, 2*np.pi, N_m)
            c = np.random.uniform(0, 1, N_m)
            for t in range(300):
                for i in range(N_m):
                    dtheta = omega[i]
                    for j in range(N_m):
                        if j != i: dtheta += (K_m / N_m) * np.sin(theta[j] - theta[i])
                    theta[i] += DT * dtheta
                theta = np.mod(theta, 2*np.pi)
                r = np.abs(np.mean(np.exp(1j * theta)))
                psi = np.angle(np.mean(np.exp(1j * theta)))
                for i in range(N_m):
                    align = np.cos(theta[i] - psi)
                    dc = alpha * (align * r - c[i])
                    for j in range(N_m):
                        if j != i: dc += (beta / N_m) * (c[j] - c[i])
                    c[i] += DT * dc
                    c[i] = np.clip(c[i], 0, 1)
            final_c = np.mean(c[-50:])

        elif model_type == 'phase_only':
            # No closure dynamics, closure is just alignment with collective phase
            N_m = params.get('N', 5)
            K_m = params.get('K', 0.8)
            omega = np.random.uniform(0.5, 2.0, N_m)
            theta = np.random.uniform(0, 2*np.pi, N_m)
            theta_hist = np.zeros((300, N_m))
            for t in range(300):
                for i in range(N_m):
                    dtheta = omega[i]
                    for j in range(N_m):
                        if j != i: dtheta += (K_m / N_m) * np.sin(theta[j] - theta[i])
                    theta[i] += DT * dtheta
                theta = np.mod(theta, 2*np.pi)
                theta_hist[t] = theta
            # Closure = cos(alignment with collective phase)
            psi_final = np.angle(np.mean(np.exp(1j * theta)))
            alignments = [np.cos(theta[i] - psi_final) for i in range(N_m)]
            final_c = float(np.mean([max(0, a) for a in alignments]))  # non-negative alignment

        elif model_type == 'frequency_only':
            # No coupling, no phase dynamics — closure is pure frequency alignment
            N_m = params.get('N', 5)
            omega = np.random.uniform(0.5, 2.0, N_m)
            # "Closure" = how aligned frequencies are (inverse variance)
            freq_alignment = 1.0 - np.std(omega) / np.mean(omega) if np.mean(omega) > 0 else 0
            final_c = float(np.clip(freq_alignment, 0, 1))

        elif model_type == 'scalar_closure':
            # Single scalar closure value, no phase, no coupling
            alpha = params.get('alpha', 0.05)
            c = np.random.uniform(0, 1)
            for t in range(300):
                dc = alpha * (0.5 - c)  # drift toward 0.5
                c += DT * dc
                c = np.clip(c, 0, 1)
            final_c = float(c)

        elif model_type == 'no_dynamics':
            # Static random closure
            final_c = float(np.random.uniform(0, 1))

        elif model_type == 'minimal_coupled':
            # Minimal: 2 oscillators, weak coupling, no closure cross
            N_m = 2
            K_m = params.get('K', 0.2)
            alpha = params.get('alpha', 0.1)
            omega = np.random.uniform(0.5, 2.0, N_m)
            theta = np.random.uniform(0, 2*np.pi, N_m)
            c = np.random.uniform(0, 1, N_m)
            for t in range(300):
                for i in range(N_m):
                    dtheta = omega[i]
                    for j in range(N_m):
                        if j != i: dtheta += (K_m / 2) * np.sin(theta[j] - theta[i])
                    theta[i] += DT * dtheta
                theta = np.mod(theta, 2*np.pi)
                r = np.abs(np.mean(np.exp(1j * theta)))
                psi = np.angle(np.mean(np.exp(1j * theta)))
                for i in range(N_m):
                    align = np.cos(theta[i] - psi)
                    dc = alpha * (align * r - c[i])
                    c[i] += DT * dc
                    c[i] = np.clip(c[i], 0, 1)
            final_c = float(np.mean(c[-50:]))
        
        final_cs.append(final_c)
        survivals.append(int(final_c > 0.3))
    
    return float(np.mean(final_cs)), float(np.mean(survivals))

model_types = [
    ('full_recursive', {'N': 5, 'K': 0.8, 'alpha': 0.2, 'beta': 0.3}),
    ('minimal_coupled', {'N': 2, 'K': 0.2, 'alpha': 0.1}),
    ('phase_only', {'N': 5, 'K': 0.8}),
    ('frequency_only', {'N': 5}),
    ('scalar_closure', {'alpha': 0.05}),
    ('no_dynamics', {}),
]

print(f'\n  {"Model":30s} {"Closure":>8s} {"Survival":>9s} {"Preserves":>20s}')
print(f'  {"-"*67}')
for mtype, params in model_types:
    c, s = run_model(mtype, params)
    if s > 0.7: preserves = 'continuity'
    elif s > 0.3: preserves = 'weak'
    else: preserves = 'failed'
    model_records.append({'model': mtype, 'mean_closure': c, 'survival_rate': s, 'preserves': preserves})
    print(f'  {mtype:30s} {c:>8.4f} {s*100:>7.1f}% {preserves:>20s}')

model_df = pd.DataFrame(model_records)
model_df.to_csv(f'{BASE}/outputs/R2_minimal_models.csv', index=False)

print(f'\n  MINIMAL MODEL THAT PRESERVES CONTINUITY:')
minimal_preserving = model_df[(model_df['survival_rate'] > 0.3) & (model_df['model'] != 'full_recursive')]
if len(minimal_preserving) > 0:
    simplest = minimal_preserving.loc[minimal_preserving['survival_rate'].idxmin()]
    print(f'    {simplest["model"]}: closure={simplest["mean_closure"]:.4f} surv={simplest["survival_rate"]*100:.1f}%')
    print(f'  (Lower than this, continuity fails)')

r2 = {'phase': 'R2', 'models_tested': list(model_df['model']),
      'simplest_preserving': str(minimal_preserving.to_dict('records')) if len(minimal_preserving) > 0 else 'none'}
with open(f'{BASE}/summaries/r2_summary.json','w') as f: json.dump(r2,f,indent=2,default=str)

print(f'\nR1+R2 COMPLETE')
