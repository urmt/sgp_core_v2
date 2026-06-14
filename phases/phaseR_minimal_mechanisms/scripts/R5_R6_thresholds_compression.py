"""
Phase R5+R6 — RECONSTRUCTION THRESHOLDS + ORGANIZATIONAL COMPRESSION

R5: Sharp boundaries for reconstruction collapse.
R6: PCA/reduced-basis analysis — simpler representation without losing prediction.
"""
import sys, numpy as np, pandas as pd, os, json, warnings
sys.path.insert(0, '/home/student/sgp_core_v2')
warnings.filterwarnings('ignore')

BASE = '/home/student/sgp_core_v2/phases/phaseR_minimal_mechanisms'
os.makedirs(f'{BASE}/outputs', exist_ok=True)
N_SIMS = 80; STEPS = 200; DT = 0.05; N = 5

# ====================================================
# R5: RECONSTRUCTION THRESHOLDS
# ====================================================
print('='*70)
print('PHASE R5 — RECONSTRUCTION THRESHOLDS')
print('Sharp boundaries for reconstruction collapse.')
print('='*70)

def run_with_params(K, alpha, beta):
    survivals = []
    final_cs = []
    for _ in range(N_SIMS):
        theta = np.random.uniform(0, 2*np.pi, N)
        c = np.random.uniform(0, 1, N)
        omega = np.random.uniform(0.5, 2.0, N)
        for t in range(STEPS):
            for i in range(N):
                dtheta = omega[i]
                for j in range(N):
                    if j != i: dtheta += (K / N) * np.sin(theta[j] - theta[i])
                theta[i] += DT * dtheta
            theta = np.mod(theta, 2*np.pi)
            r = np.abs(np.mean(np.exp(1j * theta)))
            psi = np.angle(np.mean(np.exp(1j * theta)))
            for i in range(N):
                align = np.cos(theta[i] - psi)
                dc = alpha * (align * r - c[i])
                for j in range(N):
                    if j != i: dc += (beta / N) * (c[j] - c[i])
                c[i] += DT * dc; c[i] = np.clip(c[i], 0, 1)
        final_c = np.mean(c[-50:])
        final_cs.append(final_c)
        survivals.append(int(final_c > 0.3))
    return float(np.mean(final_cs)), float(np.mean(survivals))

# Scan K (phase coupling) threshold
print('\n  K threshold scan (phase coupling strength):')
k_values = np.linspace(0, 1.0, 11)
k_records = []
for K in k_values:
    c, s = run_with_params(K, 0.2, 0.3)
    k_records.append({'param': 'K', 'value': float(K), 'mean_closure': c, 'survival_rate': s})
    marker = '<<<COLLAPSE>>>' if s < 0.5 else ''
    print(f'    K={K:.2f}: closure={c:.4f}  survival={s*100:.1f}% {marker}')

# Find exact threshold
threshold_K = min([r['value'] for r in k_records if r['survival_rate'] < 0.5], default=None)
print(f'  Threshold K ≈ {threshold_K}')

# Scan alpha (closure rate) threshold
print('\n  α threshold scan (closure dynamics rate):')
alpha_values = np.linspace(0, 0.5, 11)
a_records = []
for alpha in alpha_values:
    c, s = run_with_params(0.8, alpha, 0.3)
    a_records.append({'param': 'alpha', 'value': float(alpha), 'mean_closure': c, 'survival_rate': s})
    marker = '<<<COLLAPSE>>>' if s < 0.5 else ''
    print(f'    α={alpha:.3f}: closure={c:.4f}  survival={s*100:.1f}% {marker}')

threshold_alpha = min([r['value'] for r in a_records if r['survival_rate'] < 0.5], default=None)
print(f'  Threshold α ≈ {threshold_alpha}')

# Scan beta (cross-coupling) threshold
print('\n  β threshold scan (closure cross-coupling):')
beta_values = np.linspace(0, 0.5, 11)
b_records = []
for beta in beta_values:
    c, s = run_with_params(0.8, 0.2, beta)
    b_records.append({'param': 'beta', 'value': float(beta), 'mean_closure': c, 'survival_rate': s})
    marker = '<<<COLLAPSE>>>' if s < 0.5 else ''
    print(f'    β={beta:.3f}: closure={c:.4f}  survival={s*100:.1f}% {marker}')

threshold_beta = min([r['value'] for r in b_records if r['survival_rate'] < 0.5], default=None)
print(f'  Threshold β ≈ {threshold_beta}')

# 2D phase diagram: K vs alpha
print('\n  2D Phase Diagram (K × α) — survival rate:')
k_grid = np.linspace(0, 1.0, 8)
alpha_grid = np.linspace(0, 0.5, 8)
grid_records = []
for K in k_grid:
    row = []
    for alpha in alpha_grid:
        c, s = run_with_params(K, alpha, 0.3)
        grid_records.append({'K': float(K), 'alpha': float(alpha), 'survival_rate': s, 'mean_closure': c})
        row.append(f'{s*100:4.0f}%')
    print(f'    K={K:.2f}: ' + ' | '.join(row))

all_records = k_records + a_records + b_records + grid_records
pd.DataFrame(all_records).to_csv(f'{BASE}/outputs/R5_reconstruction_thresholds.csv', index=False)

r5 = {'phase': 'R5', 'threshold_K': threshold_K, 'threshold_alpha': threshold_alpha, 'threshold_beta': threshold_beta,
      'n_conditions': len(all_records)}
with open(f'{BASE}/summaries/r5_summary.json','w') as f: json.dump(r5,f,indent=2,default=str)

# ====================================================
# R6: ORGANIZATIONAL COMPRESSION (PCA)
# ====================================================
print('\n' + '='*70)
print('PHASE R6 — ORGANIZATIONAL COMPRESSION')
print('PCA / reduced-basis analysis.')
print('='*70)

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# Generate trajectory data from full model
print('\n  Generating trajectory data...')
all_trajs = []
all_final_c = []
for _ in range(200):
    theta = np.random.uniform(0, 2*np.pi, N)
    c = np.random.uniform(0, 1, N)
    omega = np.random.uniform(0.5, 2.0, N)
    traj = np.zeros((STEPS, N))
    for t in range(STEPS):
        for i in range(N):
            dtheta = omega[i]
            for j in range(N):
                if j != i: dtheta += (0.8 / N) * np.sin(theta[j] - theta[i])
            theta[i] += DT * dtheta
        theta = np.mod(theta, 2*np.pi)
        r = np.abs(np.mean(np.exp(1j * theta)))
        psi = np.angle(np.mean(np.exp(1j * theta)))
        for i in range(N):
            align = np.cos(theta[i] - psi)
            dc = 0.2 * (align * r - c[i])
            for j in range(N):
                if j != i: dc += (0.3 / N) * (c[j] - c[i])
            c[i] += DT * dc; c[i] = np.clip(c[i], 0, 1)
        traj[t] = c
    all_trajs.append(traj.flatten())
    all_final_c.append(np.mean(c[-50:]))

X = np.array(all_trajs)
y = np.array(all_final_c)

# PCA
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
pca = PCA()
X_pca = pca.fit_transform(X_scaled)

var_ratio = pca.explained_variance_ratio_
cum_var = np.cumsum(var_ratio)

print(f'\n  PCA on trajectory data ({X.shape[1]} dims):')
print(f'  {"Component":>10s} {"Var Ratio":>12s} {"Cumulative":>12s}')
for i in range(min(10, len(var_ratio))):
    print(f'  {i+1:>10d} {var_ratio[i]:>12.4f} {cum_var[i]:>12.4f}')

# How many components for 90% variance?
n_90 = np.argmax(cum_var >= 0.90) + 1 if np.any(cum_var >= 0.90) else len(var_ratio)
n_95 = np.argmax(cum_var >= 0.95) + 1 if np.any(cum_var >= 0.95) else len(var_ratio)
n_99 = np.argmax(cum_var >= 0.99) + 1 if np.any(cum_var >= 0.99) else len(var_ratio)
print(f'\n  Components needed: {n_90} for 90% var, {n_95} for 95% var, {n_99} for 99% var')
print(f'  Compression ratio (90%): {X.shape[1]/n_90:.1f}x')
print(f'  Compression ratio (95%): {X.shape[1]/n_95:.1f}x')

# Can we predict final closure from reduced representation?
print(f'\n  Predicting final closure from PCA-reduced data:')
for n_comp in [1, 2, 3, 5, 10, 20]:
    if n_comp > X.shape[0]: continue
    pca_reduced = PCA(n_components=n_comp)
    X_reduced = pca_reduced.fit_transform(X_scaled)
    lr = LinearRegression()
    lr.fit(X_reduced, y)
    y_pred = lr.predict(X_reduced)
    r2 = r2_score(y, y_pred)
    print(f'    {n_comp:>3d} components: R² = {r2:.4f}')

# Time-domain compression: can we use only last N timesteps?
print(f'\n  Temporal compression (predict from last N timesteps only):')
for n_t in [1, 5, 10, 20, 50]:
    X_t = np.array([t[-n_t:] for t in all_trajs])
    X_t_scaled = StandardScaler().fit_transform(X_t)
    lr = LinearRegression()
    lr.fit(X_t_scaled, y)
    y_pred = lr.predict(X_t_scaled)
    r2 = r2_score(y, y_pred)
    print(f'    Last {n_t:>3d} timesteps: R² = {r2:.4f} (input dim={n_t*N})')

# Can we predict from initial conditions only?
print(f'\n  Predict from initial conditions only:')
X_init = np.hstack([np.random.uniform(0, 2*np.pi, (200, N)), np.random.uniform(0, 1, (200, N))])
lr = LinearRegression().fit(StandardScaler().fit_transform(X_init), y)
print(f'    Initial θ,c only: R² = {r2_score(y, lr.predict(StandardScaler().fit_transform(X_init))):.4f}')

r6 = {'phase': 'R6', 'n_components_trace': X.shape[1],
      'n_90pct': int(n_90), 'n_95pct': int(n_95), 'n_99pct': int(n_99),
      'compression_90x': float(X.shape[1]/n_90)}
pd.DataFrame([{'component': i+1, 'var_ratio': var_ratio[i], 'cum_var': cum_var[i]}
              for i in range(min(20, len(var_ratio)))]).to_csv(
    f'{BASE}/outputs/R6_organizational_compression.csv', index=False)
with open(f'{BASE}/summaries/r6_summary.json','w') as f: json.dump(r6,f,indent=2,default=str)

print(f'\nR5+R6 COMPLETE')
