"""
Phase R7+R8 — ADVERSARIAL NULL PROGRAM + MECHANISM TAXONOMY

R7: Strict nulls with randomized distributions.
R8: Mechanism taxonomy: Essential / Supporting / Decorative / Epiphenomenal.
"""
import sys, numpy as np, pandas as pd, os, json, warnings
sys.path.insert(0, '/home/student/sgp_core_v2')
warnings.filterwarnings('ignore')

BASE = '/home/student/sgp_core_v2/phases/phaseR_minimal_mechanisms'
os.makedirs(f'{BASE}/outputs', exist_ok=True)
N_SIMS = 100; STEPS = 200; DT = 0.05; N = 5

# ====================================================
# R7: ADVERSARIAL NULL PROGRAM
# ====================================================
print('='*70)
print('PHASE R7 — ADVERSARIAL NULL PROGRAM')
print('Strict nulls with randomized distributions.')
print('='*70)

def run_model(theta_init='uniform', freq_init='uniform', c_init='uniform',
              K=0.8, alpha=0.2, beta=0.3, coupling='standard', closure_type='full'):
    if c_init == 'zero':
        c = np.zeros(N)
    elif c_init == 'one':
        c = np.ones(N)
    elif c_init == 'uniform_low':
        c = np.random.uniform(0, 0.1, N)
    elif c_init == 'uniform_high':
        c = np.random.uniform(0.9, 1.0, N)
    else:
        c = np.random.uniform(0, 1, N)
    
    if theta_init == 'aligned':
        theta = np.zeros(N)
    elif theta_init == 'anti_aligned':
        theta = np.array([0, np.pi] * (N//2 + 1))[:N]
    elif theta_init == 'random':
        theta = np.random.uniform(0, 2*np.pi, N)
    else:
        theta = np.random.uniform(0, 2*np.pi, N)
    
    if freq_init == 'single':
        omega = np.ones(N)
    elif freq_init == 'bimodal':
        omega = np.array([0.5]*3 + [2.0]*(N-3))[:N]
    elif freq_init == 'broad':
        omega = np.random.uniform(0.1, 3.0, N)
    else:
        omega = np.random.uniform(0.5, 2.0, N)
    
    if coupling == 'negative':
        K = -abs(K)
    elif coupling == 'zero':
        K = 0
    
    for t in range(STEPS):
        for i in range(N):
            dtheta = omega[i]
            for j in range(N):
                if j != i:
                    if coupling == 'chaotic':
                        dtheta += (K / N) * np.sin(theta[j] - theta[i]) + 0.5 * np.random.randn()
                    else:
                        dtheta += (K / N) * np.sin(theta[j] - theta[i])
            theta[i] += DT * dtheta
        theta = np.mod(theta, 2*np.pi)
        r = np.abs(np.mean(np.exp(1j * theta)))
        psi = np.angle(np.mean(np.exp(1j * theta)))
        align_vals = [np.cos(theta[i] - psi) for i in range(N)]
        if closure_type == 'full':
            for i in range(N):
                dc = alpha * (align_vals[i] * r - c[i])
                for j in range(N):
                    if j != i: dc += (beta / N) * (c[j] - c[i])
                c[i] += DT * dc; c[i] = np.clip(c[i], 0, 1)
        elif closure_type == 'inverted':
            for i in range(N):
                dc = alpha * (0 - c[i])
                for j in range(N):
                    if j != i: dc += (beta / N) * (c[j] - c[i])
                c[i] += DT * dc; c[i] = np.clip(c[i], 0, 1)
        elif closure_type == 'anti':
            for i in range(N):
                dc = -alpha * (align_vals[i] * r - c[i])
                c[i] += DT * dc; c[i] = np.clip(c[i], 0, 1)
    return float(np.mean(c[-50:]))

null_programs = [
    # (name, theta_init, freq_init, c_init, coupling, closure_type)
    ('baseline', 'uniform', 'uniform', 'uniform', 'standard', 'full'),
    ('all_zero_closure', 'uniform', 'uniform', 'zero', 'standard', 'full'),
    ('all_one_closure', 'uniform', 'uniform', 'one', 'standard', 'full'),
    ('low_initial_closure', 'uniform', 'uniform', 'uniform_low', 'standard', 'full'),
    ('high_initial_closure', 'uniform', 'uniform', 'uniform_high', 'standard', 'full'),
    ('aligned_theta', 'aligned', 'uniform', 'uniform', 'standard', 'full'),
    ('anti_aligned_theta', 'anti_aligned', 'uniform', 'uniform', 'standard', 'full'),
    ('single_freq', 'uniform', 'single', 'uniform', 'standard', 'full'),
    ('bimodal_freq', 'uniform', 'bimodal', 'uniform', 'standard', 'full'),
    ('broad_freq', 'uniform', 'broad', 'uniform', 'standard', 'full'),
    ('negative_coupling', 'uniform', 'uniform', 'uniform', 'negative', 'full'),
    ('zero_coupling', 'uniform', 'uniform', 'uniform', 'zero', 'full'),
    ('chaotic_coupling', 'uniform', 'uniform', 'uniform', 'chaotic', 'full'),
    ('inverted_closure', 'uniform', 'uniform', 'uniform', 'standard', 'inverted'),
    ('anti_closure', 'uniform', 'uniform', 'uniform', 'standard', 'anti'),
    ('all_adversarial', 'anti_aligned', 'bimodal', 'zero', 'negative', 'inverted'),
]

print(f'\n  {"Null Program":25s} {"Closure":>8s} {"Survival":>9s} {"Null Type":>20s}')
print(f'  {"-"*62}')
null_records = []
null_types = set()
for name, ti, fi, ci, coupl, ct in null_programs:
    survivals = []
    final_cs = []
    for _ in range(N_SIMS):
        fc = run_model(ti, fi, ci, 0.8, 0.2, 0.3, coupl, ct)
        final_cs.append(fc)
        survivals.append(int(fc > 0.3))
    mean_c = float(np.mean(final_cs)); surv = float(np.mean(survivals))
    
    if surv > 0.7: ntype = 'RESILIENT'
    elif surv > 0.3: ntype = 'NEUTRAL'
    elif surv > 0.05: ntype = 'DISRUPTIVE'
    else: ntype = 'CATASTROPHIC'
    null_types.add(ntype)
    
    null_records.append({'program': name, 'mean_closure': mean_c, 'survival_rate': surv, 'null_type': ntype})
    print(f'  {name:25s} {mean_c:>8.4f} {surv*100:>7.1f}% {ntype:>20s}')

pd.DataFrame(null_records).to_csv(f'{BASE}/outputs/R7_adversarial_nulls.csv', index=False)

# Count null types
print(f'\n  NULL TYPE DISTRIBUTION:')
from collections import Counter
nt_counts = Counter([r['null_type'] for r in null_records])
for nt, cnt in nt_counts.most_common():
    print(f'    {nt}: {cnt} programs')

baseline_surv = [r['survival_rate'] for r in null_records if r['program'] == 'baseline'][0]
catastrophic = [r for r in null_records if r['null_type'] == 'CATASTROPHIC']
print(f'\n  CATASTROPHIC nulls (survival < 5%):')
for r in catastrophic:
    print(f'    {r["program"]}: closure={r["mean_closure"]:.4f} surv={r["survival_rate"]*100:.1f}%')

r7 = {'phase': 'R7', 'n_programs': len(null_programs),
      'baseline_survival': float(baseline_surv),
      'catastrophic_programs': [r['program'] for r in catastrophic],
      'resilient_programs': [r['program'] for r in null_records if r['null_type'] == 'RESILIENT']}
with open(f'{BASE}/summaries/r7_summary.json','w') as f: json.dump(r7,f,indent=2,default=str)

# ====================================================
# R8: MECHANISM TAXONOMY
# ====================================================
print('\n' + '='*70)
print('PHASE R8 — MECHANISM TAXONOMY')
print('Essential / Supporting / Decorative / Epiphenomenal')
print('='*70)

# Compile evidence from phases R1-R7
# Classification rules:
# - ESSENTIAL: removal causes survival < 50%
# - SUPPORTING: removal reduces closure by > 30%
# - DECORATIVE: removal reduces closure by 10-30%
# - EPIPHENOMENAL: removal reduces closure by < 10% or increases it

# Load R1 data
abl_df = pd.read_csv(f'{BASE}/outputs/R1_ablation_hierarchy.csv')

full_closure = abl_df[abl_df['condition'] == '0_full']['mean_closure'].values[0]
full_survival = abl_df[abl_df['condition'] == '0_full']['survival_rate'].values[0]

print(f'\n  Baseline (full model): closure={full_closure:.4f}, survival={full_survival*100:.1f}%')
print(f'\n  {"Mechanism":25s} {"△Closure":>10s} {"Survival":>10s} {"Classification":>25s}')
print(f'  {"-"*70}')

taxonomy = {
    'phase_coupling': {'condition': '2_no_phase_coupling', 'drop': None, 'survival': None, 'class': None},
    'closure_dynamics': {'condition': '7_phase_only', 'drop': None, 'survival': None, 'class': None},
    'cross_coupling': {'condition': '3_no_closure_cross', 'drop': None, 'survival': None, 'class': None},
    'reconstruction': {'condition': '1_no_reconstruction', 'drop': None, 'survival': None, 'class': None},
    'topology': {'condition': '4_no_topology', 'drop': None, 'survival': None, 'class': None},
    'temporal_order': {'condition': '5_no_temporal_order', 'drop': None, 'survival': None, 'class': None},
    'freq_alignment': {'condition': '6_no_freq_alignment', 'drop': None, 'survival': None, 'class': None},
}

for mech, info in taxonomy.items():
    row = abl_df[abl_df['condition'] == info['condition']]
    if len(row) == 0: continue
    r = row.iloc[0]
    drop = float(r['mean_closure']) - full_closure
    surv = float(r['survival_rate'])
    info['drop'] = drop
    info['survival'] = surv
    
    # Classification logic (using absolute drop relative to full)
    abs_drop = abs(drop)
    if surv < 0.5:
        cls = 'ESSENTIAL'
    elif abs_drop > 0.30 or surv < 0.7:
        cls = 'SUPPORTING'
    elif abs_drop > 0.10 or surv < 0.9:
        cls = 'DECORATIVE'
    else:
        cls = 'EPIPHENOMENAL'
    
    # Override: if removal actually INCREASES closure, it's epiphenomenal
    if drop > 0 and surv >= full_survival:
        cls = 'EPIPHENOMENAL'
    
    info['class'] = cls
    print(f'  {mech:25s} {drop:>+10.4f} {surv*100:>8.1f}% {cls:>25s}')

taxonomy_df = pd.DataFrame([
    {'mechanism': k, 'closure_delta': v['drop'], 'survival': v['survival'], 'classification': v['class']}
    for k, v in taxonomy.items()
])
taxonomy_df.to_csv(f'{BASE}/outputs/R8_mechanism_taxonomy.csv', index=False)

print(f'\n  TAXONOMY SUMMARY:')
from collections import Counter
cls_counts = Counter(v['class'] for v in taxonomy.values())
for cls, cnt in cls_counts.most_common():
    mechs = [k for k, v in taxonomy.items() if v['class'] == cls]
    print(f'    {cls}: {cnt} — {", ".join(mechs)}')

r8 = {'phase': 'R8', 'taxonomy': {k: v['class'] for k, v in taxonomy.items()}}
with open(f'{BASE}/summaries/r8_summary.json','w') as f: json.dump(r8,f,indent=2,default=str)

print(f'\nR7+R8 COMPLETE')
