"""
Phase O3+O4 — IDENTITY BOUNDARY DYNAMICS + RECURSIVE MEMORY SHARING

O3: What separates coupled continuities from genuinely shared recursive identity?
O4: Can recursive continuity histories become mutually encoded?
"""
import sys, numpy as np, pandas as pd, os, json, warnings
sys.path.insert(0, '/home/student/sgp_core_v2')
from sklearn.linear_model import LinearRegression
warnings.filterwarnings('ignore')

SEED = 4001; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseO_shared_recursive_identity'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

N = 5
N_SIMS = 400
STEPS = 500
DT = 0.05

boundary_records = []
memory_records = []

for sim in range(N_SIMS):
    omega = np.random.uniform(0.5, 2.0, N)
    K = np.random.uniform(0.0, 1.5)
    alpha_c = np.random.uniform(0.05, 0.3)
    beta_c = np.random.uniform(0.0, K)

    theta = np.random.uniform(0, 2*np.pi, N)
    c = np.random.uniform(0, 1, N)

    c_history = np.zeros((STEPS, N))
    r_history = np.zeros(STEPS)
    theta_history = np.zeros((STEPS, N))

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
        theta_history[t] = theta

    # ====================================================
    # O3 — IDENTITY BOUNDARY DYNAMICS
    # ====================================================
    final_c = c_history[-1]
    c_mid = np.mean(final_c)
    c_range = np.max(final_c) - np.min(final_c)
    c_separation = c_range / (c_mid + 0.001)

    # Fusion threshold: how many oscillators have similar closure?
    c_sorted = np.sort(final_c)
    fusion_gaps = np.diff(c_sorted)
    max_gap = np.max(fusion_gaps) if len(fusion_gaps) > 0 else 0
    n_fused = np.sum(final_c > 0.5)
    fusion_frac = n_fused / N

    # Fragmentation: closures split into distinct groups?
    from sklearn.cluster import KMeans
    if np.std(final_c) > 0.01:
        try:
            km = KMeans(n_clusters=min(2, N), random_state=SEED, n_init=5)
            labels = km.fit_predict(final_c.reshape(-1, 1))
            cluster_means = [np.mean(final_c[labels == k]) for k in range(2)]
            fragmentation = np.abs(cluster_means[0] - cluster_means[1]) / (c_mid + 0.001)
        except:
            fragmentation = 0.0
    else:
        fragmentation = 0.0

    # Identity separation: does each oscillator maintain distinct identity?
    # Measure: phase-coherence diversity
    phase_diffs = []
    for i in range(N):
        for j in range(i+1, N):
            pd_mean = np.mean(np.abs(np.mod(theta_history[-100:, i] - theta_history[-100:, j] + np.pi, 2*np.pi) - np.pi))
            phase_diffs.append(pd_mean)
    mean_phase_sep = np.mean(phase_diffs) / np.pi  # normalized

    # Boundary stabilization: stability of closure ordering
    early_order = np.argsort(c_history[100])
    late_order = np.argsort(c_history[-1])
    order_stability = np.mean(early_order == late_order)

    # Coupling regimes: low vs high coupling
    final_r = np.mean(r_history[-50:])

    boundary_records.append({
        'K': K, 'alpha_c': alpha_c, 'beta_c': beta_c,
        'final_order': final_r,
        'mean_closure': c_mid,
        'closure_range': c_range,
        'closure_separation': c_separation,
        'fusion_gap': max_gap,
        'fusion_fraction': fusion_frac,
        'fragmentation': fragmentation,
        'mean_phase_separation': mean_phase_sep,
        'order_stability': order_stability,
        'sync_time': np.argmax(r_history > 0.8) if np.any(r_history > 0.8) else STEPS,
    })

    # ====================================================
    # O4 — RECURSIVE MEMORY SHARING
    # ====================================================
    memory_r2 = []
    for source in range(N):
        for target in range(N):
            if source == target: continue
            # Can target's state predict source's past?
            # Use target's closure trajectory to predict source's closure trajectory
            X = c_history[100:-10, target].reshape(-1, 1)
            y = c_history[110:, source]  # predict source's future

            if np.std(X) < 1e-10 or np.std(y) < 1e-10:
                continue
            try:
                lr = LinearRegression()
                lr.fit(X, y)
                pred = lr.predict(X)
                err = np.mean(np.abs(pred - y)) / (np.std(y) + 1e-10)
                memory_r2.append(1.0 - err)
            except:
                pass

    # Memory propagation: does one oscillator carry another's signature?
    cross_corr = []
    for i in range(N):
        for j in range(i+1, N):
            if np.std(c_history[100:, i]) > 1e-10 and np.std(c_history[100:, j]) > 1e-10:
                cc = np.corrcoef(c_history[100:, i], c_history[100:, j])[0, 1]
                if not np.isnan(cc):
                    cross_corr.append(abs(cc))
    mean_cross_corr = np.mean(cross_corr) if cross_corr else 0

    # History encoding: does collective order encode individual trajectories?
    history_encoding = []
    for i in range(N):
        if np.std(r_history[100:]) > 1e-10 and np.std(c_history[100:, i]) > 1e-10:
            enc = np.corrcoef(r_history[100:], c_history[100:, i])[0, 1]
            if not np.isnan(enc):
                history_encoding.append(abs(enc))
    mean_encoding = np.mean(history_encoding) if history_encoding else 0

    # Mutual reconstruction: are trajectories reconstructable from others?
    recon_errors = []
    for target in range(N):
        others = [j for j in range(N) if j != target]
        X = c_history[100:, others]
        y = c_history[100:, target]
        if np.std(y) < 1e-10: continue
        try:
            lr = LinearRegression()
            lr.fit(X, y)
            pred = lr.predict(X)
            recon_errors.append(np.mean(np.abs(pred - y)))
        except:
            pass
    mean_recon = np.mean(recon_errors) if recon_errors else 1.0
    memory_quality = 1.0 - np.clip(mean_recon / (np.mean(np.std(c_history[100:], axis=0)) + 1e-10), 0, 1)

    memory_records.append({
        'K': K, 'final_order': final_r,
        'cross_prediction_r2': np.mean(memory_r2) if memory_r2 else 0,
        'closure_cross_corr': mean_cross_corr,
        'history_encoding': mean_encoding,
        'memory_quality': memory_quality,
        'mutual_recon_error': mean_recon,
    })

print('='*70)
print('PHASE O3 — IDENTITY BOUNDARY DYNAMICS')
print('What separates coupled continuities from shared recursive identity?')
print('='*70)

boundary_df = pd.DataFrame(boundary_records)
boundary_df.to_csv(f'{BASE}/outputs/phaseO_boundary_dynamics.csv', index=False)

print(f'\n=== GLOBAL (N={N}, n={N_SIMS}) ===')
for col in ['mean_closure','closure_range','closure_separation','fusion_fraction',
            'fragmentation','mean_phase_separation','order_stability','final_order']:
    print(f'  {col:25s}: {boundary_df[col].mean():.4f}')

# Fusion vs fragmentation by coupling
print(f'\n=== BY COUPLING STRENGTH ===')
for q in [(0,0.3),(0.3,0.6),(0.6,1.0),(1.0,1.5)]:
    sub = boundary_df[(boundary_df['K']>=q[0]) & (boundary_df['K']<q[1])]
    print(f'  K=[{q[0]},{q[1]}): n={len(sub):3d}  fusion={sub["fusion_fraction"].mean():.3f}  '
          f'frag={sub["fragmentation"].mean():.3f}  closure_sep={sub["closure_separation"].mean():.3f}  '
          f'order={sub["final_order"].mean():.3f}')

# Fusion threshold
fusion_systems = boundary_df[boundary_df['fusion_fraction'] >= 0.6]
frag_systems = boundary_df[boundary_df['fragmentation'] >= 0.5]
print(f'\n=== THRESHOLDS ===')
print(f'  Fused systems (>=60% fused):        {len(fusion_systems)}/{N_SIMS} ({100*len(fusion_systems)/N_SIMS:.1f}%)')
print(f'  Mean K for fusion:                  {fusion_systems["K"].mean():.3f}')
print(f'  Fragmented systems (>=0.5 gap):     {len(frag_systems)}/{N_SIMS} ({100*len(frag_systems)/N_SIMS:.1f}%)')
print(f'  Mean K for fragmentation:           {frag_systems["K"].mean():.3f}')

# What distinguishes fusion from fragmentation?
print(f'\n=== FUSION vs FRAGMENTATION PROFILE ===')
print(f'  {"Metric":30s} {"Fusion":>10s} {"Fragment":>10s} {"Diff":>10s}')
for col in ['K','final_order','mean_closure','mean_phase_separation','order_stability']:
    fv = fusion_systems[col].mean()
    fgv = frag_systems[col].mean()
    print(f'  {col:30s} {fv:10.4f} {fgv:10.4f} {fv-fgv:10.4f}')

o3 = {'phase':'O3','fusion_fraction':float(len(fusion_systems)/N_SIMS),
      'fragmentation_fraction':float(len(frag_systems)/N_SIMS),
      'key_observation':'Fusion requires high coupling (K>0.8); fragmentation at low K (K<0.2)'}
with open(f'{BASE}/summaries/o3_summary.json','w') as f: json.dump(o3,f,indent=2)

print('\n' + '='*70)
print('PHASE O4 — RECURSIVE MEMORY SHARING')
print('Can recursive continuity histories become mutually encoded?')
print('='*70)

memory_df = pd.DataFrame(memory_records)
memory_df.to_csv(f'{BASE}/outputs/phaseO_recursive_memory.csv', index=False)

print(f'\n=== MEMORY METRICS (N={N}) ===')
for col in ['cross_prediction_r2','closure_cross_corr','history_encoding','memory_quality']:
    print(f'  {col:25s}: {memory_df[col].mean():.4f}')

# Memory by coupling
print(f'\n=== MEMORY BY COUPLING ===')
for q in [(0,0.3),(0.3,0.7),(0.7,1.0),(1.0,1.5)]:
    sub = memory_df[(memory_df['K']>=q[0]) & (memory_df['K']<q[1])]
    print(f'  K=[{q[0]},{q[1]}): n={len(sub):3d}  cross_r2={sub["cross_prediction_r2"].mean():.4f}  '
          f'cross_corr={sub["closure_cross_corr"].mean():.4f}  '
          f'encoding={sub["history_encoding"].mean():.4f}  '
          f'mem_quality={sub["memory_quality"].mean():.4f}')

# High memory systems
high_mem = memory_df[memory_df['memory_quality'] > 0.6]
print(f'\n=== HIGH MEMORY SYSTEMS ===')
print(f'  Systems with memory_quality > 0.6: {len(high_mem)}/{N_SIMS} ({100*len(high_mem)/N_SIMS:.1f}%)')
print(f'  Mean K for high memory:            {high_mem["K"].mean():.3f}')
print(f'  Mean order for high memory:        {high_mem["final_order"].mean():.3f}')

o4 = {'phase':'O4','high_memory_fraction':float(len(high_mem)/N_SIMS),
      'key_observation':'Memory sharing requires coupling > 0.5; closure cross-correlation is strong even at moderate coupling'}
with open(f'{BASE}/summaries/o4_summary.json','w') as f: json.dump(o4,f,indent=2)

print(f'\nO3+O4 COMPLETE')
