"""
Phase N5+N6 — EMERGENT COUPLED IDENTITIES + COUPLING FAILURE MODES

N5: Can coupled recursive processes generate higher-order recursive organization?
N6: What destroys dynamical coupling organization?

Dynamical analysis of coupled systems with perturbation experiments.
"""
import sys, numpy as np, pandas as pd, os, json, warnings
sys.path.insert(0, '/home/student/sgp_core_v2')
from scipy.stats import pearsonr
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseN_dynamical_coupling'
PHL = '/home/student/sgp_core_v2/phases/phaseL_observer_emergence'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

sr_df = pd.read_csv(f'{PHL}/outputs/phaseL_temporal_self_modeling.csv')
cg = sr_df[sr_df['process_regime'] == 'CG'].reset_index(drop=True)
sim_df = pd.read_csv(f'{BASE}/outputs/phaseN_mutual_stabilization.csv')
print(f'Loaded: {len(cg)} CG systems, {len(sim_df)} simulations')

# ====================================================
# N5: EMERGENT COUPLED IDENTITIES
# ====================================================
print('='*70)
print('PHASE N5 — EMERGENT COUPLED IDENTITIES')
print('Can coupled recursive processes form higher-order organization?')
print('='*70)

# Higher-order continuity: is the coupled system more than sum of parts?
# Measure: combined_order > max(individual_continuity)
# Higher-order = synchronization creates new continuity not present in either alone

# From existing simulation data
sim_df['higher_order_continuity'] = sim_df['final_synchronization'] - np.maximum(sim_df.get('continuity_a', 0), sim_df.get('continuity_b', 0))
sim_df['emergent_sync_bonus'] = sim_df['final_synchronization'] - (sim_df.get('continuity_a', 0) + sim_df.get('continuity_b', 0)) / 2

# Collective closure: closure correlation × synchronization
sim_df['collective_closure_emergent'] = sim_df.get('closure_correlation', 0) * sim_df['final_synchronization']

# Metastable co-continuity: synchronization that persists despite perturbation
# Proxy: phase-locked fraction × sync_window
if 'phase_locked_fraction' in sim_df.columns and 'sync_window' in sim_df.columns:
    sim_df['metastable_co_continuity'] = sim_df['phase_locked_fraction'] * sim_df['sync_window'] / sim_df['sync_window'].max()
else:
    sim_df['metastable_co_continuity'] = sim_df['final_synchronization']

print(f'\n=== EMERGENT HIGHER-ORDER CONTINUITY ===')
print(f'  Mean higher-order continuity:         {sim_df["higher_order_continuity"].mean():.4f}')
print(f'  Mean emergent sync bonus:             {sim_df["emergent_sync_bonus"].mean():.4f}')
print(f'  Mean collective closure (emergent):   {sim_df["collective_closure_emergent"].mean():.4f}')
print(f'  Mean metastable co-continuity:         {sim_df["metastable_co_continuity"].mean():.4f}')

# Fraction showing higher-order organization
higher_order_frac = (sim_df['higher_order_continuity'] > 0.1).mean()
print(f'  Fraction with higher-order (>0.1):    {higher_order_frac:.2%}')

# What predicts higher-order continuity?
print(f'\n=== WHAT ENABLES HIGHER-ORDER CONTINUITY? ===')
for col in ['coupling_strength', 'final_synchronization', 'closure_correlation']:
    if col in sim_df.columns:
        c = sim_df[col].corr(sim_df['higher_order_continuity'])
        print(f'  {col:35s}: r={c:.4f}')

# By coupling strength
print(f'\n=== HIGHER-ORDER BY COUPLING STRENGTH ===')
for cs in [0.1, 0.3, 0.5, 0.7]:
    sub = sim_df[(sim_df['coupling_strength'] > cs-0.05) & (sim_df['coupling_strength'] < cs+0.05)]
    if len(sub) > 0:
        print(f'  coupling={cs:.1f}: higher_order={sub["higher_order_continuity"].mean():.4f} frac={sub["metastable_co_continuity"].mean():.4f}')

# Save
sim_df.to_csv(f'{BASE}/outputs/phaseN_emergent_coupling.csv', index=False)
print(f'Saved: phaseN_emergent_coupling.csv')

# ====================================================
# N6: COUPLING FAILURE MODES
# ====================================================
print('\n' + '='*70)
print('PHASE N6 — COUPLING FAILURE MODES')
print('What destroys dynamical coupling organization?')
print('='*70)

# Run perturbation experiments on the coupled dynamics
def run_perturbed_coupled(params_a, params_b, T=200, dt=0.1, coupling_strength=0.3, 
                          perturbation_type='none', perturbation_time=50, seed=SEED):
    """Run coupled simulation with specific perturbation."""
    rng = np.random.RandomState(seed)
    
    omega_a = 0.5 + 2.0 * float(params_a.get('operator_continuity', 0.5))
    omega_b = 0.5 + 2.0 * float(params_b.get('operator_continuity', 0.5))
    beta_a = float(params_a.get('recursive_closure', 0.3))
    beta_b = float(params_b.get('recursive_closure', 0.3))
    alpha_a = float(params_a.get('closure_persistence', 0.3))
    alpha_b = float(params_b.get('closure_persistence', 0.3))
    gamma_a = float(params_a.get('reconstruction_ability', 0.3))
    gamma_b = float(params_b.get('reconstruction_ability', 0.3))
    
    theta_a = rng.uniform(0, 2*np.pi)
    theta_b = rng.uniform(0, 2*np.pi)
    c_a = float(params_a.get('recursive_identity_score', 0.3))
    c_b = float(params_b.get('recursive_identity_score', 0.3))
    
    coupling_a = coupling_strength * gamma_a
    coupling_b = coupling_strength * gamma_b
    
    times = np.arange(0, T*dt, dt)
    n_steps = len(times)
    traj = np.zeros((n_steps, 7))
    
    for t_idx in range(n_steps):
        t = times[t_idx]
        
        # Apply perturbation
        if t_idx == int(perturbation_time / dt):
            if perturbation_type == 'desync':
                theta_b += np.pi  # Anti-phase
            elif perturbation_type == 'closure_collapse':
                c_a = 0.0  # Collapse closure
            elif perturbation_type == 'coupling_break':
                coupling_a = 0  # Break coupling
            elif perturbation_type == 'temporal_shift':
                theta_a += 0.5  # Shift phase
            elif perturbation_type == 'reconstruction_block':
                gamma_a = 0; gamma_b = 0  # Block reconstruction
                coupling_a = 0; coupling_b = 0
        
        noise_a = rng.normal(0, 0.02 * (1 - gamma_a + 0.01))
        noise_b = rng.normal(0, 0.02 * (1 - gamma_b + 0.01))
        
        dtheta_a = (omega_a + coupling_a * np.sin(theta_b - theta_a)) * dt + noise_a * np.sqrt(dt)
        dtheta_b = (omega_b + coupling_b * np.sin(theta_a - theta_b)) * dt + noise_b * np.sqrt(dt)
        theta_a += dtheta_a; theta_b += dtheta_b
        
        target_a = np.tanh(beta_a * np.sin(theta_a))
        target_b = np.tanh(beta_b * np.sin(theta_b))
        c_a += alpha_a * (target_a - c_a) * dt
        c_b += alpha_b * (target_b - c_b) * dt
        c_a = np.clip(c_a, -1, 1); c_b = np.clip(c_b, -1, 1)
        
        order_param = np.abs(np.exp(1j*theta_a) + np.exp(1j*theta_b)) / 2
        
        traj[t_idx] = [theta_a, theta_b, c_a, c_b, 
                       np.arctan2(np.sin(theta_b-theta_a), np.cos(theta_b-theta_a)),
                       order_param, coupling_a]
    
    return traj, times

# Run perturbation experiments on a subset of pairs
N_PERT = 500
pert_types = ['desync', 'closure_collapse', 'coupling_break', 'temporal_shift', 'reconstruction_block']
print(f'\nRunning {N_PERT} pairs × {len(pert_types)} perturbations...')

pert_records = []
for sim_idx in range(N_PERT):
    i = np.random.randint(0, len(cg))
    j = np.random.randint(0, len(cg))
    while j == i: j = np.random.randint(0, len(cg))
    a, b = cg.iloc[i], cg.iloc[j]
    cs = np.random.uniform(0.1, 0.6)
    
    for pt in pert_types:
        traj, times = run_perturbed_coupled(a, b, T=200, dt=0.1, coupling_strength=cs,
                                           perturbation_type=pt, perturbation_time=50,
                                           seed=SEED+sim_idx*10+pert_types.index(pt))
        
        # Measure recovery
        pre_pert = traj[:50, 5].mean()  # sync before perturbation
        post_pert = traj[50:, 5].mean()  # sync after
        final_sync = traj[-50:, 5].mean()  # final recovery
        
        # Recovery fraction
        if pre_pert > 0.01:
            recovery = min(1.0, final_sync / pre_pert)
        else:
            recovery = final_sync
        
        # Collapse depth
        min_sync = traj[50:100, 5].min() if len(traj) > 100 else traj[50:, 5].min()
        collapse_depth = pre_pert - min_sync
        
        pert_records.append({
            'sim_idx': sim_idx, 'perturbation_type': pt,
            'coupling_strength': cs,
            'pre_pert_sync': pre_pert, 'post_pert_sync': post_pert,
            'final_sync': final_sync, 'recovery': recovery,
            'collapse_depth': collapse_depth,
        })
    
    if (sim_idx + 1) % 100 == 0:
        print(f'  {sim_idx+1}/{N_PERT}')

pert_df = pd.DataFrame(pert_records)

print(f'\n=== FAILURE MODE ANALYSIS ===')
for pt in pert_types:
    sub = pert_df[pert_df['perturbation_type'] == pt]
    print(f'\n  {pt:25s}:')
    print(f'    Pre-pert sync:    {sub["pre_pert_sync"].mean():.4f}')
    print(f'    Post-pert sync:   {sub["post_pert_sync"].mean():.4f}')
    print(f'    Recovery:         {sub["recovery"].mean():.4f}')
    print(f'    Collapse depth:   {sub["collapse_depth"].mean():.4f}')

# Most destructive perturbation
worst_pert = pert_df.groupby('perturbation_type')['recovery'].mean().idxmin()
worst_recovery = pert_df.groupby('perturbation_type')['recovery'].mean().min()
print(f'\n  Most destructive perturbation: {worst_pert} (recovery={worst_recovery:.4f})')

# Fragmentation thresholds: at what coupling strength do perturbations cause irreversible damage?
print(f'\n=== FRAGMENTATION THRESHOLDS ===')
for pt in pert_types:
    sub = pert_df[pert_df['perturbation_type'] == pt]
    for cs in [0.1, 0.3, 0.5]:
        csub = sub[(sub['coupling_strength'] > cs-0.05) & (sub['coupling_strength'] < cs+0.05)]
        if len(csub) > 0:
            print(f'  {pt:25s} coupling={cs:.1f}: recovery={csub["recovery"].mean():.4f}')

# Save
pert_df.to_csv(f'{BASE}/outputs/phaseN_failure_modes.csv', index=False)
print(f'\nSaved: phaseN_failure_modes.csv')

# Summaries
n5_summary = {
    'phase': 'N5',
    'n_simulations': len(sim_df),
    'mean_higher_order_continuity': float(sim_df['higher_order_continuity'].mean()),
    'fraction_higher_order': float(higher_order_frac),
    'mean_collective_closure_emergent': float(sim_df['collective_closure_emergent'].mean()),
}
n6_summary = {
    'phase': 'N6',
    'most_destructive': worst_pert,
    'worst_recovery': float(worst_recovery),
    'n_perturbations': len(pert_df),
}
for name, data in [('n5', n5_summary), ('n6', n6_summary)]:
    with open(f'{BASE}/summaries/{name}_summary.json', 'w') as f:
        json.dump(data, f, indent=2)

print(f'\nN5+N6 COMPLETE')
