"""
Phase N1+N2 — MINIMAL COUPLED CONTINUITY SYSTEMS + COUPLED TRANSITION GEOMETRY

N1: Implement ACTUAL temporal evolution of coupled recursive continuity processes.
N2: Do transitions synchronize before states do?

This is NOT static metric comparison. This is DYNAMICAL coupling.
Each system is a recursive continuity process with phase + closure dynamics.

Model: Coupled phase oscillators with recursive closure variables.
"""
import sys, numpy as np, pandas as pd, os, json, warnings
sys.path.insert(0, '/home/student/sgp_core_v2')
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseN_dynamical_coupling'
PHL = '/home/student/sgp_core_v2/phases/phaseL_observer_emergence'
os.makedirs(f'{BASE}/outputs', exist_ok=True)
os.makedirs(f'{BASE}/summaries', exist_ok=True)

print('='*70)
print('PHASE N1 — MINIMAL COUPLED CONTINUITY SYSTEMS')
print('Actual temporal evolution of coupled recursive processes')
print('='*70)

# Load Phase L organizational data
sr_df = pd.read_csv(f'{PHL}/outputs/phaseL_temporal_self_modeling.csv')
cg = sr_df[sr_df['process_regime'] == 'CG'].reset_index(drop=True)
print(f'Loaded: {cg.shape[0]} CG systems')

# ====================================================
# Coupled recursive continuity model
# ====================================================
def run_coupled_system(params_a, params_b, T=200, dt=0.1, coupling_strength=0.3, seed=SEED):
    """
    Coupled phase oscillator with recursive closure dynamics.
    
    Each system has:
    - phase theta: temporal position of the process
    - closure c: recursive self-relation
    
    Internal dynamics:
      theta_i(t+1) = theta_i(t) + omega_i*dt + coupling*sin(theta_j - theta_i)*dt + noise
      c_i(t+1) = c_i(t) + alpha_i*(tanh(beta_i*sin(theta_i)) - c_i(t))*dt
    
    Where:
      omega_i   = natural frequency  (from operator_continuity)
      beta_i    = closure feedback   (from recursive_closure)
      alpha_i   = closure rate       (from closure_persistence)
      gamma_i   = reconstruction     (from reconstruction_ability)
    """
    rng = np.random.RandomState(seed)
    
    # Extract organizational parameters
    omega_a = 0.5 + 2.0 * float(params_a.get('operator_continuity', 0.5))
    omega_b = 0.5 + 2.0 * float(params_b.get('operator_continuity', 0.5))
    beta_a = float(params_a.get('recursive_closure', 0.3))
    beta_b = float(params_b.get('recursive_closure', 0.3))
    alpha_a = float(params_a.get('closure_persistence', 0.3))
    alpha_b = float(params_b.get('closure_persistence', 0.3))
    gamma_a = float(params_a.get('reconstruction_ability', 0.3))
    gamma_b = float(params_b.get('reconstruction_ability', 0.3))
    
    # Initial conditions
    theta_a = rng.uniform(0, 2*np.pi)
    theta_b = rng.uniform(0, 2*np.pi)
    c_a = float(params_a.get('recursive_identity_score', 0.3))
    c_b = float(params_b.get('recursive_identity_score', 0.3))
    
    coupling_a = coupling_strength * gamma_a  # reconstruction modulates coupling
    coupling_b = coupling_strength * gamma_b
    
    # Temporal records
    times = np.arange(0, T*dt, dt)
    n_steps = len(times)
    traj = np.zeros((n_steps, 6))  # theta_a, theta_b, c_a, c_b, phase_diff, order_param
    
    for t_idx in range(n_steps):
        t = times[t_idx]
        
        # Phase dynamics with diffusive coupling
        noise_a = rng.normal(0, 0.02 * (1 - gamma_a + 0.01))
        noise_b = rng.normal(0, 0.02 * (1 - gamma_b + 0.01))
        
        dtheta_a = (omega_a + coupling_a * np.sin(theta_b - theta_a)) * dt + noise_a * np.sqrt(dt)
        dtheta_b = (omega_b + coupling_b * np.sin(theta_a - theta_b)) * dt + noise_b * np.sqrt(dt)
        
        theta_a += dtheta_a
        theta_b += dtheta_b
        
        # Closure dynamics (recursive self-relation)
        target_a = np.tanh(beta_a * np.sin(theta_a))
        target_b = np.tanh(beta_b * np.sin(theta_b))
        dc_a = alpha_a * (target_a - c_a) * dt
        dc_b = alpha_b * (target_b - c_b) * dt
        c_a += dc_a
        c_b += dc_b
        
        # Clamp
        c_a = np.clip(c_a, -1, 1)
        c_b = np.clip(c_b, -1, 1)
        
        # Phase difference (wrapped)
        phase_diff = np.arctan2(np.sin(theta_b - theta_a), np.cos(theta_b - theta_a))
        
        # Kuramoto order parameter
        order_param = np.abs(np.exp(1j*theta_a) + np.exp(1j*theta_b)) / 2
        
        traj[t_idx] = [theta_a, theta_b, c_a, c_b, phase_diff, order_param]
    
    return traj, times

def compute_transition_geometry(traj):
    """Compute transition-level metrics from trajectory."""
    theta_a = traj[:, 0]; theta_b = traj[:, 1]
    c_a = traj[:, 2]; c_b = traj[:, 3]
    phase_diff = traj[:, 4]; order_param = traj[:, 5]
    
    # Phase transitions (wrapping crossings)
    phase_jumps_a = np.sum(np.abs(np.diff(np.unwrap(theta_a))) > np.pi)
    phase_jumps_b = np.sum(np.abs(np.diff(np.unwrap(theta_b))) > np.pi)
    
    # Closure transitions (sign changes)
    closure_sign_changes_a = np.sum(np.diff(np.sign(c_a)) != 0)
    closure_sign_changes_b = np.sum(np.diff(np.sign(c_b)) != 0)
    
    # Synchronization time: first time order_param exceeds 0.9
    sync_idx = np.where(order_param > 0.9)[0]
    sync_time = sync_idx[0] if len(sync_idx) > 0 else len(order_param)
    
    # Final synchronization
    final_sync = order_param[-20:].mean()
    
    # Closure correlation
    closure_corr = np.corrcoef(c_a, c_b)[0, 1] if len(c_a) > 10 else 0
    if np.isnan(closure_corr): closure_corr = 0
    
    # Transition synchronization
    # Do phase jumps in A coincide with phase jumps in B?
    jumps_a = np.abs(np.diff(np.unwrap(theta_a))) > 1.0
    jumps_b = np.abs(np.diff(np.unwrap(theta_b))) > 1.0
    if len(jumps_a) > 0 and len(jumps_b) > 0:
        coincident = np.sum(jumps_a & jumps_b)
        transition_sync = coincident / (np.sum(jumps_a | jumps_b) + 1e-10)
    else:
        transition_sync = 0
    
    # Phase locking ratio
    mean_order = order_param.mean()
    
    # Closure convergence
    final_c_diff = np.abs(c_a[-20:].mean() - c_b[-20:].mean())
    
    return {
        'phase_sync_time': int(sync_time),
        'final_synchronization': float(final_sync),
        'mean_order_parameter': float(mean_order),
        'closure_correlation': float(closure_corr),
        'final_closure_diff': float(final_c_diff),
        'transition_synchronization': float(transition_sync),
        'phase_jumps_a': int(phase_jumps_a),
        'phase_jumps_b': int(phase_jumps_b),
        'closure_sign_changes_a': int(closure_sign_changes_a),
        'closure_sign_changes_b': int(closure_sign_changes_b),
    }

# ====================================================
# Run simulations for many pairs
# ====================================================
N_SIMS = 2000
T = 200; dt = 0.1
print(f'\nRunning {N_SIMS} coupled simulations (T={T}, dt={dt})...')

sim_records = []
traj_records = []

for sim_idx in range(N_SIMS):
    i = np.random.randint(0, len(cg))
    j = np.random.randint(0, len(cg))
    while j == i:
        j = np.random.randint(0, len(cg))
    
    a, b = cg.iloc[i], cg.iloc[j]
    coupling_strength = np.random.uniform(0.05, 0.8)
    
    traj, times = run_coupled_system(a, b, T=T, dt=dt, coupling_strength=coupling_strength, seed=SEED+sim_idx)
    
    geo = compute_transition_geometry(traj)
    
    sim_records.append({
        'sim_idx': sim_idx,
        'sys_idx_a': int(a['sys_idx']), 'domain_a': a['domain'],
        'sys_idx_b': int(b['sys_idx']), 'domain_b': b['domain'],
        'observer_level_a': int(a.get('observer_level', 0)),
        'observer_level_b': int(b.get('observer_level', 0)),
        'recursive_closure_a': float(a.get('recursive_closure', 0)),
        'recursive_closure_b': float(b.get('recursive_closure', 0)),
        'reconstruction_a': float(a.get('reconstruction_ability', 0)),
        'reconstruction_b': float(b.get('reconstruction_ability', 0)),
        'operator_continuity_a': float(a.get('operator_continuity', 0.5)),
        'operator_continuity_b': float(b.get('operator_continuity', 0.5)),
        'coupling_strength': coupling_strength,
        **geo,
    })
    
    # Save trajectory subset
    if sim_idx < 500:  # First 500 trajectories
        for t_idx, t in enumerate(times):
            traj_records.append({
                'sim_idx': sim_idx, 'time': t,
                'theta_a': float(traj[t_idx, 0]), 'theta_b': float(traj[t_idx, 1]),
                'c_a': float(traj[t_idx, 2]), 'c_b': float(traj[t_idx, 3]),
                'phase_diff': float(traj[t_idx, 4]),
                'order_param': float(traj[t_idx, 5]),
            })
    
    if (sim_idx + 1) % 500 == 0:
        print(f'  {sim_idx+1}/{N_SIMS}')

sim_df = pd.DataFrame(sim_records)
traj_df = pd.DataFrame(traj_records)

# Save
sim_df.to_csv(f'{BASE}/outputs/phaseN_minimal_couplings.csv', index=False)
traj_df.to_csv(f'{BASE}/outputs/phaseN_temporal_trajectories.csv', index=False)
print(f'\nSaved: phaseN_minimal_couplings.csv ({len(sim_df)} sims)')
print(f'Saved: phaseN_temporal_trajectories.csv ({len(traj_df)} steps)')

# ====================================================
# N1 Analysis
# ====================================================
print(f'\n=== N1: COUPLED DYNAMICS RESULTS ===')
print(f'  Mean final synchronization:         {sim_df["final_synchronization"].mean():.4f}')
print(f'  Mean order parameter:               {sim_df["mean_order_parameter"].mean():.4f}')
print(f'  Mean phase sync time:               {sim_df["phase_sync_time"].mean():.1f}')
print(f'  Mean closure correlation:           {sim_df["closure_correlation"].mean():.4f}')
print(f'  Mean closure diff (final):          {sim_df["final_closure_diff"].mean():.4f}')
print(f'  Mean transition synchronization:    {sim_df["transition_synchronization"].mean():.4f}')

# ====================================================
# N2: Coupled transition geometry
# ====================================================
print('\n' + '='*70)
print('PHASE N2 — COUPLED TRANSITION GEOMETRY')
print('Do transitions synchronize before states do?')
print('='*70)

# Transitions = phase jumps (wrapping)
# States = instantaneous order parameter
# Hypothesis: transition_synchronization > state_synchronization at early times

# Compare transition sync to state sync
print(f'\n=== TRANSITIONS vs STATES ===')
print(f'  Transition synchronization:  {sim_df["transition_synchronization"].mean():.4f}')
print(f'  Final state synchronization: {sim_df["final_synchronization"].mean():.4f}')
print(f'  Transition > State: {sim_df["transition_synchronization"].mean() > sim_df["final_synchronization"].mean()}')

# Early vs late: split trajectory into thirds
early_unsync = (sim_df['phase_sync_time'] > 50).mean()
print(f'  Fraction synchronizing after time 50: {early_unsync:.2%}')

# What predicts transition synchronization?
print(f'\n=== WHAT PREDICTS TRANSITION SYNCHRONIZATION? ===')
from scipy.stats import pearsonr
preds = ['recursive_closure_a', 'recursive_closure_b', 'reconstruction_a', 'reconstruction_b',
         'operator_continuity_a', 'operator_continuity_b', 'coupling_strength']
for col in preds:
    if col in sim_df.columns:
        c, p = pearsonr(sim_df[col], sim_df['transition_synchronization'])
        print(f'  {col:35s}: r={c:.4f} p={p:.4e}')

# Does closure correlation predict synchronization?
c, p = pearsonr(sim_df['closure_correlation'], sim_df['final_synchronization'])
print(f'  closure_correlation -> final_sync: r={c:.4f} p={p:.4e}')

# Closure dynamics
print(f'\n  Closure sign changes (A): {sim_df["closure_sign_changes_a"].mean():.1f}')
print(f'  Closure sign changes (B): {sim_df["closure_sign_changes_b"].mean():.1f}')
print(f'  Phase jumps (A): {sim_df["phase_jumps_a"].mean():.1f}')
print(f'  Phase jumps (B): {sim_df["phase_jumps_b"].mean():.1f}')

# Save transition geometry data
sim_df.to_csv(f'{BASE}/outputs/phaseN_transition_geometry.csv', index=False)
print(f'\nSaved: phaseN_transition_geometry.csv')

# Summaries
n1_summary = {
    'phase': 'N1',
    'n_simulations': N_SIMS,
    'mean_final_sync': float(sim_df['final_synchronization'].mean()),
    'mean_order_param': float(sim_df['mean_order_parameter'].mean()),
    'mean_sync_time': float(sim_df['phase_sync_time'].mean()),
    'mean_closure_corr': float(sim_df['closure_correlation'].mean()),
}
n2_summary = {
    'phase': 'N2',
    'mean_transition_sync': float(sim_df['transition_synchronization'].mean()),
    'mean_state_sync': float(sim_df['final_synchronization'].mean()),
    'transitions_before_states': bool(sim_df['transition_synchronization'].mean() > sim_df['final_synchronization'].mean()),
}
for name, data in [('n1', n1_summary), ('n2', n2_summary)]:
    with open(f'{BASE}/summaries/{name}_summary.json', 'w') as f:
        json.dump(data, f, indent=2)

print(f'\nN1+N2 COMPLETE')
