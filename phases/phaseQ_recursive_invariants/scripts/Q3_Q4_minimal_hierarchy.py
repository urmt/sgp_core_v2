"""
Phase Q3+Q4 — MINIMAL INVARIANT SETS + INVARIANT HIERARCHY

Q3: What is the irreducible minimum for recursive continuity survival?
Q4: Rank all discovered organizational properties by persistence.
"""
import sys, numpy as np, pandas as pd, os, json, warnings
sys.path.insert(0, '/home/student/sgp_core_v2')
warnings.filterwarnings('ignore')

SEED = 6000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseQ_recursive_invariants'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

# ====================================================
# Q3: MINIMAL INVARIANT SETS
# ====================================================
print('='*70)
print('PHASE Q3 — MINIMAL INVARIANT SETS')
print('What is the irreducible minimum for recursive continuity survival?')
print('='*70)

N = 5
N_SIMS = 100
STEPS = 300
DT = 0.05

# Systematically remove organizational features
# and measure closure survival

minimal_records = []

conditions = [
    # (name, K, alpha_c, beta_c, topology_note)
    ('full_organization', 0.8, 0.2, 0.3, 'all_to_all'),
    ('no_geometry', 0.0, 0.2, 0.0, 'none'),            # no coupling, no synchronization
    ('no_synchronization', 0.0, 0.2, 0.3, 'none'),       # no phase sync but closure cross-coupling
    ('no_coupling', 0.0, 0.2, 0.0, 'none'),              # completely uncoupled
    ('no_timing_precision', 0.8, 0.2, 0.3, 'random_timing'),  # jittered coupling
    ('no_topology', 0.8, 0.2, 0.3, 'random'),            # random sparse connections
    ('no_closure_cross', 0.8, 0.2, 0.0, 'all_to_all'),   # no closure cross-coupling
    ('minimal_closure', 0.0, 0.05, 0.0, 'none'),         # bare-minimum self-closure
    ('minimal_sync_only', 0.8, 0.0, 0.0, 'all_to_all'),  # no closure dynamics
    ('minimal_both', 0.3, 0.1, 0.1, 'all_to_all'),       # low everything
]

for name, K, alpha_c, beta_c, topo in conditions:
    survivals = []
    final_closures = []
    
    for sim in range(N_SIMS):
        omega = np.random.uniform(0.5, 2.0, N)
        theta = np.random.uniform(0, 2*np.pi, N)
        c = np.random.uniform(0, 1, N)
        
        for t in range(STEPS):
            for i in range(N):
                dtheta = omega[i]
                if topo == 'all_to_all':
                    for j in range(N):
                        if j != i:
                            dtheta += (K / N) * np.sin(theta[j] - theta[i])
                elif topo == 'random':
                    # Random sparse with ~40% connectivity
                    for j in range(N):
                        if j != i and np.random.random() < 0.4:
                            dtheta += (K / max(1, N * 0.4)) * np.sin(theta[j] - theta[i])
                elif topo == 'random_timing':
                    # Jittered coupling (add noise to coupling phase)
                    for j in range(N):
                        if j != i:
                            noise = np.random.uniform(-0.1, 0.1)
                            dtheta += (K / N) * np.sin(theta[j] - theta[i] + noise)
                theta[i] += DT * dtheta
            
            r = np.abs(np.mean(np.exp(1j * theta)))
            psi = np.angle(np.mean(np.exp(1j * theta)))
            
            for i in range(N):
                align = np.cos(theta[i] - psi)
                dc = alpha_c * (align * r - c[i])
                for j in range(N):
                    if j != i:
                        dc += (beta_c / N) * (c[j] - c[i])
                c[i] += DT * dc
                c[i] = np.clip(c[i], 0, 1)
        
        final_c = np.mean(c[-50:])
        final_closures.append(final_c)
        survivals.append(int(final_c > 0.3))
    
    minimal_records.append({
        'condition': name, 'K': K, 'alpha_c': alpha_c, 'beta_c': beta_c, 'topology': topo,
        'mean_closure': float(np.mean(final_closures)),
        'survival_rate': float(np.mean(survivals)),
    })

minimal_df = pd.DataFrame(minimal_records)
minimal_df.to_csv(f'{BASE}/outputs/phaseQ_minimal_invariants.csv', index=False)

print(f'\n  {"Condition":30s} {"K":>5s} {"α":>5s} {"β":>5s} {"Mean Cl":>8s} {"Survival":>9s}')
print(f'  {"-"*62}')
for _, r in minimal_df.iterrows():
    print(f'  {r["condition"]:30s} {r["K"]:>5.1f} {r["alpha_c"]:>5.2f} {r["beta_c"]:>5.2f} '
          f'{r["mean_closure"]:>8.4f} {r["survival_rate"]*100:>7.1f}%')

# What feature removals are most destructive?
baseline = minimal_df[minimal_df['condition'] == 'full_organization']['mean_closure'].values[0]
baseline_surv = minimal_df[minimal_df['condition'] == 'full_organization']['survival_rate'].values[0]

print(f'\n=== DESTRUCTIVE IMPACT (relative to full_organization: closure={baseline:.4f}, survival={baseline_surv*100:.1f}%) ===')
for _, r in minimal_df.iterrows():
    if r['condition'] == 'full_organization': continue
    c_drop = baseline - r['mean_closure']
    s_drop = baseline_surv - r['survival_rate']
    print(f'  Remove {r["condition"]:25s}: closure Δ={c_drop:+.4f}  survival Δ={s_drop:+.1f}%')

q3 = {'phase': 'Q3', 'n_conditions': len(conditions),
      'most_destructive': minimal_df.loc[minimal_df['mean_closure'].idxmin(), 'condition'],
      'least_destructive': minimal_df.loc[minimal_df[minimal_df['condition'] != 'full_organization']['mean_closure'].idxmax(), 'condition']}
with open(f'{BASE}/summaries/q3_summary.json','w') as f: json.dump(q3,f,indent=2)

# ====================================================
# Q4: INVARIANT HIERARCHY
# ====================================================
print('\n' + '='*70)
print('PHASE Q4 — INVARIANT HIERARCHY')
print('Rank all organizational properties by persistence.')
print('='*70)

# Load candidate invariants
candidates_df = pd.read_csv(f'{BASE}/outputs/phaseQ_candidate_invariants.csv')
q2_df = pd.read_csv(f'{BASE}/outputs/phaseQ_trajectory_distribution_split.csv')

# Build hierarchy from all data
hierarchy = []

# From Q2: collapse score (lower = more invariant)
for _, r in q2_df.iterrows():
    inv_score = 1.0 - abs(r['collapse']) if pd.notna(r['collapse']) else 0.5
    hierarchy.append({
        'property': r['property'],
        'invariant_score': inv_score,
        'invariant_level': 'STRONG' if inv_score > 0.8 else 'MODERATE' if inv_score > 0.5 else 'WEAK',
        'dependency': r['dependency'],
        'evidence_source': f"Phase {r['phase']}",
    })

# From Q3: how much closure survives removal
for _, r in minimal_df.iterrows():
    if r['condition'] == 'full_organization': continue
    hierarchy.append({
        'property': f"closure_under_{r['condition']}",
        'invariant_score': r['survival_rate'],
        'invariant_level': 'STRONG' if r['survival_rate'] > 0.6 else 'MODERATE' if r['survival_rate'] > 0.3 else 'WEAK',
        'dependency': 'structural',
        'evidence_source': f"Q3 minimal set (K={r['K']}, α={r['alpha_c']})",
    })

# From candidates: transition invariants
for _, r in candidates_df.iterrows():
    if r['property_type'] == 'transition_invariant' and pd.notna(r['real']):
        hierarchy.append({
            'property': r['candidate'],
            'invariant_score': r['real'],
            'invariant_level': 'STRONG' if r['real'] > 0.7 else 'MODERATE' if r['real'] > 0.4 else 'WEAK',
            'dependency': 'transition',
            'evidence_source': f"Phase {r['phase']}",
        })

hier_df = pd.DataFrame(hierarchy)
hier_df.to_csv(f'{BASE}/outputs/phaseQ_invariant_hierarchy.csv', index=False)

print(f'\n  {"Property":45s} {"Score":>7s} {"Level":>10s} {"Dependency":>15s}')
print(f'  {"-"*77}')
for _, r in hier_df.sort_values('invariant_score', ascending=False).iterrows():
    print(f'  {r["property"]:45s} {r["invariant_score"]:>7.4f} {r["invariant_level"]:>10s} {r["dependency"]:>15s}')

print(f'\n=== STRONG INVARIANTS (score > 0.8) ===')
strong = hier_df[hier_df['invariant_level'] == 'STRONG']
for _, r in strong.iterrows():
    print(f'  {r["property"]:45s} (score={r["invariant_score"]:.4f})')

print(f'\n=== WEAK/NON-INVARIANTS (score < 0.5) ===')
weak = hier_df[hier_df['invariant_level'] == 'WEAK']
for _, r in weak.iterrows():
    print(f'  {r["property"]:45s} (score={r["invariant_score"]:.4f})')

q4 = {'phase': 'Q4', 'strong_invariants': list(strong['property']),
      'weak_invariants': list(weak['property'])}
with open(f'{BASE}/summaries/q4_summary.json','w') as f: json.dump(q4,f,indent=2)

print(f'\nQ3+Q4 COMPLETE')
