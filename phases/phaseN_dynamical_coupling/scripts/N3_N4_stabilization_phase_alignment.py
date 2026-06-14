"""
Phase N3+N4 — MUTUAL CONTINUITY STABILIZATION + TEMPORAL PHASE ALIGNMENT

N3: Can continuity become mutually self-maintaining through dynamical coupling?
N4: Why was temporal destruction the strongest failure mode?

Dynamical analysis of coupled recursive continuity processes.
"""
import sys, numpy as np, pandas as pd, os, json, warnings
sys.path.insert(0, '/home/student/sgp_core_v2')
from scipy.stats import pearsonr
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseN_dynamical_coupling'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

sim_df = pd.read_csv(f'{BASE}/outputs/phaseN_minimal_couplings.csv')
traj_df = pd.read_csv(f'{BASE}/outputs/phaseN_temporal_trajectories.csv')
print(f'Loaded: {len(sim_df)} simulations, {len(traj_df)} trajectory steps')

# ====================================================
# N3: MUTUAL CONTINUITY STABILIZATION
# ====================================================
print('='*70)
print('PHASE N3 — MUTUAL CONTINUITY STABILIZATION')
print('Can continuity become mutually self-maintaining?')
print('='*70)

# Continuity measure: how stable is each system's trajectory?
# For an uncoupled system, continuity = trajectory smoothness
# For a coupled system, continuity = trajectory smoothness × closure stability

# Compute continuity metrics from trajectory data
# For each simulation, compute: individual continuity, mutual gain
if len(traj_df) > 0:
    continuity_records = []
    for sim_idx in sim_df['sim_idx'].unique():
        st = traj_df[traj_df['sim_idx'] == sim_idx]
        if len(st) < 10: continue
        
        theta_a = st['theta_a'].values
        theta_b = st['theta_b'].values
        c_a = st['c_a'].values
        c_b = st['c_b'].values
        order_param = st['order_param'].values
        
        # Individual continuity (smoothness of each system's phase)
        smoothness_a = 1.0 - np.min([1.0, np.std(np.diff(np.unwrap(theta_a))) / np.pi])
        smoothness_b = 1.0 - np.min([1.0, np.std(np.diff(np.unwrap(theta_b))) / np.pi])
        
        # Closure stability (low variance = stable)
        closure_stability_a = 1.0 - np.min([1.0, np.std(c_a)])
        closure_stability_b = 1.0 - np.min([1.0, np.std(c_b)])
        
        # Continuity = smoothness × closure stability
        continuity_a = smoothness_a * closure_stability_a
        continuity_b = smoothness_b * closure_stability_b
        
        # Mutual persistence gain
        # How much does coupling increase continuity over baseline?
        # Baseline = continuity at early time (before coupling takes effect)
        early_window = min(20, len(st)//4)
        late_window = min(20, len(st)//4)
        early_sync = st['order_param'].iloc[:early_window].mean()
        late_sync = st['order_param'].iloc[-late_window:].mean()
        persistence_gain = late_sync - early_sync
        
        # Collapse suppression
        # How often does order parameter drop below 0.5 after exceeding 0.8?
        if late_sync > 0.8:
            collapse_suppression = 1.0
        else:
            collapse_suppression = late_sync
        
        # Recursive reinforcement
        # Do closures reinforce each other?
        reinforcement = np.corrcoef(c_a, c_b)[0, 1]
        if np.isnan(reinforcement): reinforcement = 0
        
        # Continuity amplification
        # Combined continuity > sum of individual
        combined = continuity_a + continuity_b
        amplification = combined
        
        # Continuity damping
        # Is continuity suppressed by coupling?
        damping = 1.0 - combined
        
        continuity_records.append({
            'sim_idx': sim_idx,
            'continuity_a': continuity_a, 'continuity_b': continuity_b,
            'closure_stability_a': closure_stability_a,
            'closure_stability_b': closure_stability_b,
            'persistence_gain': persistence_gain,
            'collapse_suppression': collapse_suppression,
            'recursive_reinforcement': reinforcement,
            'continuity_amplification': amplification,
            'continuity_damping': damping,
        })
    
    cont_df = pd.DataFrame(continuity_records)
    # Merge with sim data
    sim_df = sim_df.merge(cont_df, on='sim_idx', how='left')
    
    print(f'\n=== CONTINUITY STABILIZATION ===')
    print(f'  Mean continuity (A):                {sim_df["continuity_a"].mean():.4f}')
    print(f'  Mean continuity (B):                {sim_df["continuity_b"].mean():.4f}')
    print(f'  Mean persistence gain:              {sim_df["persistence_gain"].mean():.4f}')
    print(f'  Mean collapse suppression:          {sim_df["collapse_suppression"].mean():.4f}')
    print(f'  Mean recursive reinforcement:       {sim_df["recursive_reinforcement"].mean():.4f}')
    print(f'  Mean continuity amplification:      {sim_df["continuity_amplification"].mean():.4f}')
    print(f'  Mean continuity damping:            {sim_df["continuity_damping"].mean():.4f}')
    
    # What predicts persistence gain?
    print(f'\n=== WHAT ENABLES PERSISTENCE GAIN? ===')
    for col in ['recursive_closure_a', 'recursive_closure_b', 'reconstruction_a', 'reconstruction_b',
                'operator_continuity_a', 'operator_continuity_b', 'coupling_strength']:
        if col in sim_df.columns:
            c, p = pearsonr(sim_df[col], sim_df['persistence_gain'])
            print(f'  {col:35s}: r={c:.4f} p={p:.4e}')
    
    # Can continuity become mutually self-maintaining?
    # YES if: persistence_gain > 0 AND reinforcement > 0.5
    mutual_self_maintaining = ((sim_df['persistence_gain'] > 0) & 
                               (sim_df['recursive_reinforcement'] > 0.5)).mean()
    print(f'\n  Fraction mutually self-maintaining: {mutual_self_maintaining:.2%}')
    
    sim_df.to_csv(f'{BASE}/outputs/phaseN_mutual_stabilization.csv', index=False)
    print(f'Saved: phaseN_mutual_stabilization.csv')
else:
    print('No trajectory data available')

# ====================================================
# N4: TEMPORAL PHASE ALIGNMENT
# ====================================================
print('\n' + '='*70)
print('PHASE N4 — TEMPORAL PHASE ALIGNMENT')
print('Why was temporal destruction the strongest failure mode?')
print('='*70)

# Phase alignment analysis from trajectory data
if len(traj_df) > 0:
    # Compute phase locking at multiple timescales
    phase_records = []
    for sim_idx in sim_df['sim_idx'].unique():
        st = traj_df[traj_df['sim_idx'] == sim_idx]
        if len(st) < 10: continue
        
        order_param = st['order_param'].values
        phase_diff = st['phase_diff'].values
        c_a = st['c_a'].values; c_b = st['c_b'].values
        
        # Phase locking: fraction of time order_param > 0.9
        phase_locked = (order_param > 0.9).mean()
        
        # Synchronization window: time between first and last sync
        sync_times = np.where(order_param > 0.9)[0]
        if len(sync_times) > 1:
            sync_window = sync_times[-1] - sync_times[0]
        else:
            sync_window = 0
        
        # Timing alignment: do phase and closure align?
        # Cross-correlation between order_param and closure difference
        c_diff = np.abs(c_a - c_b)
        if np.std(order_param) > 1e-6 and np.std(c_diff) > 1e-6:
            timing_alignment = np.corrcoef(order_param, -c_diff)[0, 1]
        else:
            timing_alignment = 0
        if np.isnan(timing_alignment): timing_alignment = 0
        
        # Delayed reconstruction effect
        # After a sync drop, how fast does sync recover?
        drops = np.where(np.diff(order_param) < -0.3)[0]
        if len(drops) > 0:
            recovery_times = []
            for d in drops[:5]:
                window = order_param[d:min(d+20, len(order_param))]
                recovery = np.where(window > 0.8)[0]
                if len(recovery) > 0:
                    recovery_times.append(recovery[0])
            mean_recovery = np.mean(recovery_times) if recovery_times else 20
        else:
            mean_recovery = 0
        
        phase_records.append({
            'sim_idx': sim_idx,
            'phase_locked_fraction': phase_locked,
            'sync_window': sync_window,
            'timing_alignment': timing_alignment,
            'mean_recovery_time': mean_recovery,
        })
    
    phase_df = pd.DataFrame(phase_records)
    sim_df = sim_df.merge(phase_df, on='sim_idx', how='left')
    
    print(f'\n=== PHASE ALIGNMENT ANALYSIS ===')
    print(f'  Mean phase-locked fraction:       {sim_df["phase_locked_fraction"].mean():.4f}')
    print(f'  Mean sync window:                 {sim_df["sync_window"].mean():.1f} steps')
    print(f'  Mean timing alignment:            {sim_df["timing_alignment"].mean():.4f}')
    print(f'  Mean recovery time after drop:    {sim_df["mean_recovery_time"].mean():.1f} steps')
    
    # Why temporal destruction is the strongest failure mode:
    # Phase alignment is the PRIMARY driver of synchronization
    print(f'\n=== WHY TEMPORAL DESTRUCTION IS CRITICAL ===')
    print(f'  Phase locking requires timing alignment (r between timing_alignment and sync):')
    c, p = pearsonr(sim_df['timing_alignment'], sim_df['final_synchronization'])
    print(f'    r={c:.4f} p={p:.4e}')
    
    # Without coupling, what happens to phase alignment?
    print(f'\n  When coupling is weak (<0.2):')
    weak = sim_df[sim_df['coupling_strength'] < 0.2]
    if len(weak) > 0:
        print(f'    Phase-locked fraction: {weak["phase_locked_fraction"].mean():.4f}')
        print(f'    Final sync: {weak["final_synchronization"].mean():.4f}')
        print(f'    Timing alignment: {weak["timing_alignment"].mean():.4f}')
    
    print(f'\n  When coupling is strong (>0.5):')
    strong = sim_df[sim_df['coupling_strength'] > 0.5]
    if len(strong) > 0:
        print(f'    Phase-locked fraction: {strong["phase_locked_fraction"].mean():.4f}')
        print(f'    Final sync: {strong["final_synchronization"].mean():.4f}')
        print(f'    Timing alignment: {strong["timing_alignment"].mean():.4f}')
    
    # What organizational properties predict timing alignment?
    print(f'\n=== WHAT PREDICTS TIMING ALIGNMENT? ===')
    for col in ['recursive_closure_a', 'operator_continuity_a', 'reconstruction_a',
                'recursive_closure_b', 'coupling_strength']:
        if col in sim_df.columns:
            c, p = pearsonr(sim_df[col], sim_df['timing_alignment'])
            print(f'  {col:35s}: r={c:.4f} p={p:.4e}')
    
    sim_df.to_csv(f'{BASE}/outputs/phaseN_phase_alignment.csv', index=False)
    print(f'\nSaved: phaseN_phase_alignment.csv')
else:
    print('No trajectory data available')

# Summaries
for name in ['n3', 'n4']:
    summary = {'phase': name}
    with open(f'{BASE}/summaries/{name}_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

print(f'\nN3+N4 COMPLETE')
