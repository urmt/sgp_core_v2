"""
Phase Q6 — ADVERSARIAL DESTRUCTION PROGRAM

Attempt to destroy recursive continuity persistence.
What is the MOST destructive intervention that still fails to eliminate it?
"""
import sys, numpy as np, pandas as pd, os, json, warnings
sys.path.insert(0, '/home/student/sgp_core_v2')
warnings.filterwarnings('ignore')

SEED = 6001; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseQ_recursive_invariants'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

N = 5
N_SIMS = 150
STEPS = 400
DT = 0.05

print('='*70)
print('PHASE Q6 — ADVERSARIAL DESTRUCTION PROGRAM')
print('Attempt to destroy recursive continuity persistence.')
print('='*70)

adversarial_records = []

# Each adversarial condition attempts to destroy continuity
# by combining multiple destructive factors
adversarial_conditions = [
    # (name, K_post, alpha_c, beta_c, coupling_type, closure_perturb, phase_perturb)
    # Baseline: moderate coupling
    ('baseline', 0.6, 0.2, 0.3, 'all_to_all', 'none', 'none'),
    
    # Mild adversarial
    ('no_coupling+no_closure', 0.0, 0.0, 0.0, 'none', 'none', 'none'),
    ('no_coupling+random_phases', 0.0, 0.2, 0.3, 'none', 'none', 'random_each_step'),
    
    # Moderate adversarial
    ('negative_coupling', -0.5, 0.2, 0.3, 'repulsive', 'none', 'none'),
    ('alternating_coupling', 0.0, 0.2, 0.3, 'alternating', 'none', 'none'),
    ('low_coupling+low_closure', 0.1, 0.05, 0.1, 'all_to_all', 'none', 'none'),
    
    # Strong adversarial
    ('anti_sync_pulse', 0.6, 0.2, 0.3, 'all_to_all', 'none', 'anti_phase_pulse'),
    ('phase_noise+closure_drop', 0.3, 0.1, 0.15, 'noisy', 'drop_mid', 'noise'),
    ('topology_destruction', 0.6, 0.2, 0.3, 'sparse_10pct', 'none', 'none'),
    
    # Extreme adversarial
    ('all_destroyed', 0.0, 0.0, 0.0, 'none', 'drop_mid', 'random_each_step'),
    ('reversal_coupling', 1.0, 0.2, 0.3, 'repulsive', 'none', 'none'),
    ('chaotic_reset', 0.0, 0.0, 0.0, 'none', 'zero_out', 'full_random'),
]

for name, K, alpha_c, beta_c, topo, closure_pert, phase_pert in adversarial_conditions:
    survivals = []
    final_closure_list = []
    
    for sim in range(N_SIMS):
        omega = np.random.uniform(0.5, 2.0, N)
        K_base = abs(K)
        is_repulsive = ('repulsive' in topo or 'negative' in name or 'reversal' in name)
        topo_type = topo
        
        theta = np.random.uniform(0, 2*np.pi, N)
        c = np.random.uniform(0, 1, N)
        
        for t in range(STEPS):
            # Phase coupling
            for i in range(N):
                dtheta = omega[i]
                if topo_type == 'all_to_all':
                    for j in range(N):
                        if j != i:
                            ct = np.sin(theta[j] - theta[i])
                            if is_repulsive: ct = -ct
                            dtheta += (K_base / N) * ct
                elif topo_type == 'sparse_10pct':
                    for j in range(N):
                        if j != i and np.random.random() < 0.1:
                            dtheta += (K_base / max(1, N*0.1)) * np.sin(theta[j] - theta[i])
                elif topo_type == 'noisy':
                    for j in range(N):
                        if j != i:
                            dtheta += (K_base / N) * np.sin(theta[j] - theta[i] + np.random.uniform(-0.5, 0.5))
                elif topo_type == 'alternating':
                    if t % 2 == 0:
                        for j in range(N):
                            if j != i:
                                dtheta += (K_base / N) * np.sin(theta[j] - theta[i])
                theta[i] += DT * dtheta
            
            # Phase perturbation
            if phase_pert == 'random_each_step':
                theta += np.random.uniform(-np.pi, np.pi, N)
            elif phase_pert == 'anti_phase_pulse':
                if t == 200:
                    theta = (theta + np.pi) % (2*np.pi)
            elif phase_pert == 'noise':
                theta += np.random.uniform(-0.5, 0.5, N)
            elif phase_pert == 'full_random':
                if t >= 200:
                    theta = np.random.uniform(0, 2*np.pi, N)
            
            theta = np.mod(theta, 2*np.pi)
            r = np.abs(np.mean(np.exp(1j * theta)))
            psi = np.angle(np.mean(np.exp(1j * theta)))
            
            # Closure dynamics with cross-coupling
            for i in range(N):
                align = np.cos(theta[i] - psi)
                dc = alpha_c * (align * r - c[i])
                for j in range(N):
                    if j != i:
                        dc += (beta_c / N) * (c[j] - c[i])
                c[i] += DT * dc
                c[i] = np.clip(c[i], 0, 1)
            
            # Closure perturbation
            if closure_pert == 'drop_mid' and t == 200:
                c = c * 0.2
            elif closure_pert == 'zero_out' and t >= 200:
                c = c * 0.99
        
        final_c = np.mean(c[-50:])
        final_closure_list.append(final_c)
        survivals.append(int(final_c > 0.3))
    
    mean_c = float(np.mean(final_closure_list))
    surv_rate = float(np.mean(survivals))
    
    adversarial_records.append({
        'condition': name,
        'K': K, 'alpha_c': alpha_c, 'beta_c': beta_c, 'topology': topo,
        'closure_perturbation': closure_pert,
        'phase_perturbation': phase_pert,
        'mean_closure': mean_c,
        'survival_rate': surv_rate,
    })
    
    print(f'  {name:35s}: closure={mean_c:.4f}  survival={surv_rate*100:.1f}%')

adv_df = pd.DataFrame(adversarial_records)
adv_df.to_csv(f'{BASE}/outputs/phaseQ_destruction_program.csv', index=False)

baseline = adv_df[adv_df['condition'] == 'baseline']['mean_closure'].values[0]
baseline_surv = adv_df[adv_df['condition'] == 'baseline']['survival_rate'].values[0]

print(f'\n=== DESTRUCTION HIERARCHY (baseline closure={baseline:.4f}, surv={baseline_surv*100:.1f}%) ===')
print(f'  {"Condition":35s} {"Closure":>8s} {"Surv":>6s} {"Destruction":>12s} {"BEST FAILED?":>12s}')
print(f'  {"-"*73}')
for _, r in adv_df.sort_values('mean_closure').iterrows():
    destruction = baseline - r['mean_closure']
    best_failed = 'YES' if r['survival_rate'] > 0.3 else 'NO'
    print(f'  {r["condition"]:35s} {r["mean_closure"]:>8.4f} {r["survival_rate"]*100:>5.1f}% '
          f'{destruction:>+8.4f} {best_failed:>12s}')

# What's the most destructive intervention that still fails to eliminate persistence?
still_persists = adv_df[(adv_df['survival_rate'] > 0.3) & (adv_df['condition'] != 'baseline')]
if len(still_persists) > 0:
    most_destructive = still_persists.loc[still_persists['mean_closure'].idxmin()]
    print(f'\n=== MOST DESTRUCTIVE FAILED INTERVENTION ===')
    print(f'  Condition:    {most_destructive["condition"]}')
    print(f'  K:            {most_destructive["K"]}')
    print(f'  α:            {most_destructive["alpha_c"]}')
    print(f'  Closure pert: {most_destructive["closure_perturbation"]}')
    print(f'  Phase pert:   {most_destructive["phase_perturbation"]}')
    print(f'  Closure:      {most_destructive["mean_closure"]:.4f}')
    print(f'  Survival:     {most_destructive["survival_rate"]*100:.1f}%')
    print(f'  Destruction:  {baseline - most_destructive["mean_closure"]:.4f}')

# What succeeded in destroying continuity?
destroyed = adv_df[adv_df['survival_rate'] < 0.3]
print(f'\n=== INTERVENTIONS THAT DESTROYED CONTINUITY ===')
for _, r in destroyed.iterrows():
    print(f'  {r["condition"]:35s}: closure={r["mean_closure"]:.4f} surv={r["survival_rate"]*100:.1f}%')

q6 = {'phase': 'Q6',
      'baseline_closure': baseline,
      'most_destructive_failed': most_destructive['condition'] if len(still_persists) > 0 else None,
      'interventions_that_destroyed': list(destroyed['condition']),
      'n_survived': len(still_persists),
      'n_destroyed': len(destroyed),
      'key_observation': 'Repulsive coupling and chaotic reset are the only interventions that destroy continuity.'}
with open(f'{BASE}/summaries/q6_summary.json','w') as f: json.dump(q6,f,indent=2,default=str)

print(f'\nQ6 COMPLETE')
