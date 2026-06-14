"""
Phase R3+R4 — NECESSARY vs SUFFICIENT CONDITIONS + CONTINUITY DEGENERACY
Optimized for runtime.
"""
import sys, numpy as np, pandas as pd, os, json, warnings
from collections import Counter
sys.path.insert(0, '/home/student/sgp_core_v2')
warnings.filterwarnings('ignore')

BASE = '/home/student/sgp_core_v2/phases/phaseR_minimal_mechanisms'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

N_SIMS = 50; STEPS = 200; DT = 0.05; N = 5

def run_test(use_phase, K_val, use_closure, alpha_val, use_cross, beta_val, use_freq_align, use_topo_order):
    c_hist = np.zeros((STEPS, N))
    theta = np.random.uniform(0, 2*np.pi, N)
    c = np.random.uniform(0, 1, N)
    omega = np.random.uniform(0.5, 2.0, N) if use_freq_align else np.random.uniform(0.9, 1.1, N)
    for t in range(STEPS):
        if use_phase:
            for i in range(N):
                dtheta = omega[i]
                for j in range(N):
                    if j != i:
                        if use_topo_order:
                            dtheta += (K_val / N) * np.sin(theta[j] - theta[i])
                        else:
                            dtheta += (K_val / N) * np.sin(theta[j] - theta[i] + np.random.uniform(-0.3, 0.3))
                theta[i] += DT * dtheta
            theta = np.mod(theta, 2*np.pi)
        else:
            theta += DT * omega
            theta = np.mod(theta, 2*np.pi)
        r = np.abs(np.mean(np.exp(1j * theta)))
        psi = np.angle(np.mean(np.exp(1j * theta)))
        if use_closure:
            for i in range(N):
                align = np.cos(theta[i] - psi)
                dc = alpha_val * (align * r - c[i])
                if use_cross:
                    for j in range(N):
                        if j != i:
                            dc += (beta_val / N) * (c[j] - c[i])
                c[i] += DT * dc
                c[i] = np.clip(c[i], 0, 1)
        c_hist[t] = c
    return c_hist

# ====================================================
# R3: NECESSARY vs SUFFICIENT CONDITIONS
# ====================================================
print('='*70)
print('PHASE R3 — NECESSARY vs SUFFICIENT CONDITIONS')
print('='*70)

PROPERTIES = {
    'continuity_survival': lambda c: float(np.mean(c) > 0.3),
    'high_integration': lambda c: float(np.mean(c) > 0.6),
    'closure_stability': lambda c: float(np.std(c[-100:]) < 0.05),
}

mech_configs = [
    ('phase_coupling', True, 0.8, True, 0.2, True, 0.3, True, True),
    ('closure_dynamics', True, 0.8, True, 0.2, True, 0.3, True, True),
    ('cross_coupling', True, 0.8, True, 0.2, True, 0.3, True, True),
    ('reconstruction', True, 0.8, True, 0.2, False, 0.0, True, True),
    ('topology', True, 0.8, True, 0.2, True, 0.3, True, True),
    ('temporal_order', True, 0.8, True, 0.2, True, 0.3, True, True),
    ('freq_alignment', True, 0.8, True, 0.2, True, 0.3, True, True),
]

robust_class = {m: {p: [] for p in PROPERTIES} for m in [m[0] for m in mech_configs]}

for run_idx in range(N_SIMS):
    if run_idx % 25 == 0: print(f'  Run {run_idx}/{N_SIMS}')
    for mech_name, use_ph, K, use_cl, alpha, use_cr, beta, use_fa, use_to in mech_configs:
        with_hist = run_test(use_ph, K, use_cl, alpha, use_cr, beta, use_fa, use_to)
        if mech_name == 'phase_coupling':
            without_hist = run_test(False, 0.0, use_cl, alpha, use_cr, beta, use_fa, use_to)
        elif mech_name == 'closure_dynamics':
            without_hist = run_test(use_ph, K, False, 0.0, use_cr, beta, use_fa, use_to)
        elif mech_name in ('cross_coupling', 'reconstruction'):
            without_hist = run_test(use_ph, K, use_cl, alpha, False, 0.0, use_fa, use_to)
        else:
            without_hist = run_test(use_ph, K, use_cl, alpha, use_cr, beta, use_fa, False)
        present = {p: func(with_hist.mean(axis=1)) for p, func in PROPERTIES.items()}
        absent = {p: func(without_hist.mean(axis=1)) for p, func in PROPERTIES.items()}
        for prop in PROPERTIES:
            robust_class[mech_name][prop].append(
                'necessary' if present[prop] == 1.0 and absent[prop] == 0.0 else
                'sufficient' if present[prop] == 1.0 and absent[prop] == 1.0 else
                'neither'
            )

print(f'\n  {"Mechanism":20s} {"Continuity":>15s} {"Integration":>15s} {"Stability":>15s}')
print(f'  {"-"*65}')
final_classification = {}
for mech_name, _, _, _, _, _, _, _, _ in mech_configs:
    row_parts = [mech_name]
    classification_row = {}
    for prop in PROPERTIES:
        cnt = Counter(robust_class[mech_name][prop])
        top, pct = cnt.most_common(1)[0]
        pct_val = pct / N_SIMS * 100
        classification_row[prop] = f'{top.upper()} ({pct_val:.0f}%)'
        row_parts.append(f'{top.upper():>10s}')
    final_classification[mech_name] = classification_row
    print(f'  {row_parts[0]:20s} {row_parts[1]:>20s} {row_parts[2]:>20s} {row_parts[3]:>20s}')

pd.DataFrame([{'mechanism': k, **v} for k, v in final_classification.items()]).to_csv(
    f'{BASE}/outputs/R3_necessary_sufficient.csv', index=False)
with open(f'{BASE}/summaries/r3_summary.json','w') as f:
    json.dump({'phase': 'R3', 'classification': final_classification}, f, indent=2, default=str)

# ====================================================
# R4: CONTINUITY DEGENERACY
# ====================================================
print('\n' + '='*70)
print('PHASE R4 — CONTINUITY DEGENERACY')
print('='*70)

architectures = [
    ('full_5osc', 5, 0.8, 0.2, 0.3, 'all_to_all', 'full'),
    ('big_10osc', 10, 0.5, 0.15, 0.2, 'all_to_all', 'full'),
    ('tiny_2osc', 2, 0.3, 0.1, 0.1, 'all_to_all', 'full'),
    ('sparse_5osc', 5, 0.8, 0.2, 0.3, 'sparse_3pct', 'full'),
    ('weak_coupling', 5, 0.2, 0.2, 0.3, 'all_to_all', 'full'),
    ('strong_coupling', 5, 2.0, 0.2, 0.3, 'all_to_all', 'full'),
    ('slow_closure', 5, 0.8, 0.05, 0.1, 'all_to_all', 'full'),
    ('fast_closure', 5, 0.8, 0.5, 0.6, 'all_to_all', 'full'),
    ('phase_only_surr', 5, 0.8, 0.0, 0.0, 'all_to_all', 'none'),
    ('freq_engine', 5, 0.0, 0.0, 0.0, 'none', 'none'),
    ('scalar_drift', 5, 0.0, 0.05, 0.0, 'none', 'self'),
    ('noisy_closure', 5, 0.0, 0.02, 0.0, 'none', 'noise'),
]

arch_records = []
print(f'\n  {"Architecture":20s} {"Closure":>8s} {"Survival":>9s} {"Class":>15s}')
print(f'  {"-"*52}')
for name, N_a, K, alpha, beta, topo, ctype in architectures:
    survivals = []
    final_cs = []
    for sim in range(N_SIMS):
        theta = np.random.uniform(0, 2*np.pi, N_a)
        c = np.random.uniform(0, 1, N_a)
        omega = np.random.uniform(0.5, 2.0, N_a)
        for t in range(STEPS):
            for i in range(N_a):
                dtheta = omega[i]
                if topo == 'all_to_all':
                    for j in range(N_a):
                        if j != i: dtheta += (K / N_a) * np.sin(theta[j] - theta[i])
                elif topo.startswith('sparse'):
                    pct = float(topo.split('_')[1].replace('pct','')) / 100.0
                    for j in range(N_a):
                        if j != i and np.random.random() < pct:
                            dtheta += (K / (N_a * pct)) * np.sin(theta[j] - theta[i])
                theta[i] += DT * dtheta
            theta = np.mod(theta, 2*np.pi)
            r = np.abs(np.mean(np.exp(1j * theta)))
            psi = np.angle(np.mean(np.exp(1j * theta)))
            if ctype == 'full':
                for i in range(N_a):
                    align = np.cos(theta[i] - psi)
                    dc = alpha * (align * r - c[i])
                    for j in range(N_a):
                        if j != i: dc += (beta / N_a) * (c[j] - c[i])
                    c[i] += DT * dc; c[i] = np.clip(c[i], 0, 1)
            elif ctype == 'self':
                for i in range(N_a): c[i] += DT * alpha * (0.5 - c[i]); c[i] = np.clip(c[i], 0, 1)
            elif ctype == 'noise':
                for i in range(N_a): c[i] += DT * 0.01 * np.random.randn(); c[i] = np.clip(c[i], 0, 1)
        final_c = np.mean(c[-50:])
        final_cs.append(final_c)
        survivals.append(int(final_c > 0.3))
    mean_c = float(np.mean(final_cs)); surv_rate = float(np.mean(survivals))
    dclass = 'robust' if surv_rate > 0.8 else 'marginal' if surv_rate > 0.5 else 'fragile' if surv_rate > 0.2 else 'failed'
    arch_records.append({'architecture': name, 'mean_closure': mean_c, 'survival_rate': surv_rate, 'degeneracy_class': dclass})
    print(f'  {name:20s} {mean_c:>8.4f} {surv_rate*100:>7.1f}% {dclass:>15s}')

pd.DataFrame(arch_records).to_csv(f'{BASE}/outputs/R4_continuity_degeneracy.csv', index=False)

full_row = [r for r in arch_records if 'full_' in r['architecture']]
if full_row:
    full_surv = full_row[0]['survival_rate']
    degenerate = [r for r in arch_records if abs(r['survival_rate'] - full_surv) < 0.10]
    print(f'\n  DEGENERACY: {len(degenerate)} archs within 10% survival of full model')
    for r in degenerate:
        print(f'    {r["architecture"]}')

r4 = {'phase': 'R4', 'n_architectures': len(architectures),
      'degenerate_count': len(degenerate) if full_row else 0}
with open(f'{BASE}/summaries/r4_summary.json','w') as f: json.dump(r4,f,indent=2,default=str)

print(f'\nR3+R4 COMPLETE')
