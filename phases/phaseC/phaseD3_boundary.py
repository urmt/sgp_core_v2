"""
Phase D3 — Regime Boundary Analysis.
Sweeps parameters in selected domains to measure fertility near transitions.
Focus: domains where D2 showed positive transition→fertility signal.
"""
import numpy as np, pandas as pd, warnings
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import r2_score
from scipy.stats import entropy
warnings.filterwarnings('ignore')

CSV = '/home/student/sgp_core_v2/phases/phaseC/phaseC_metrics.csv'
df = pd.read_csv(CSV)
cols = ['CSR','RBS','ADI','RTP','SRD']
fertility_targets = [c for c in df.columns if c.startswith('fertility_')]
K = 30

print('='*70)
print('PHASE D3 — REGIME BOUNDARY ANALYSIS')
print('Fertility near organizational transitions, per domain')
print('='*70)

for domain in sorted(df['domain'].unique()):
    m = df['domain'] == domain
    dm = df.loc[m].copy().reset_index(drop=True)
    N = len(dm)
    X = StandardScaler().fit_transform(dm[cols].values)
    nbrs = NearestNeighbors(n_neighbors=min(K+1, N)).fit(X)
    _, indices = nbrs.kneighbors(X)
    nb_idx = indices[:, 1:]
    
    # Sort systems by a key parameter for this domain and look at
    # how ambiguity and fertility co-vary along a parameter axis
    
    # Use PC1 as a proxy for "position in organizational space"
    from sklearn.decomposition import PCA
    pca = PCA(n_components=1).fit(X)
    pc1 = pca.transform(X)[:, 0]
    order = np.argsort(pc1)
    
    print(f'\n{domain} — sorted by PC1 (organizational axis):')
    
    # Sliding window: compute mean ambiguity and mean fertility along PC1
    window = max(10, N // 20)
    amb_profile, fert_profile, r2_profile = [], [], []
    for i in range(0, N - window, window // 2):
        sl = order[i:i+window]
        if len(sl) < 10: continue
        
        # Mean ambiguity (across targets) in window
        amb_vals = []
        fert_vals = []
        for t in fertility_targets:
            y = dm[t].values
            if np.std(y) < 1e-10: continue
            for idx in sl:
                nb = nb_idx[idx]
                if len(nb) < 5: continue
                r2_vec = np.zeros(5)
                for j, c in enumerate(cols):
                    xj = dm.iloc[nb][c].values.reshape(-1, 1)
                    yj = y[nb]
                    if np.std(xj) < 1e-12 or np.std(yj) < 1e-12: continue
                    r2_vec[j] = r2_score(yj, LinearRegression().fit(xj, yj).predict(xj))
                r2_vec = np.clip(r2_vec, 0, None)
                s = r2_vec.sum() + 1e-10
                amb = 1 - r2_vec.max() / s
                amb_vals.append(amb)
                fert_vals.append(y[idx])
        
        if amb_vals:
            amb_profile.append(np.mean(amb_vals))
            fert_profile.append(np.mean(fert_vals))
    
    if len(amb_profile) < 5:
        print(f'  Too few windows for analysis')
        continue
    
    # Find transition regions (high ambiguity) and measure fertility there
    amb_arr = np.array(amb_profile)
    fert_arr = np.array(fert_profile)
    am_med = np.median(amb_arr)
    
    high_amb = amb_arr >= am_med
    low_amb = amb_arr < am_med
    
    if high_amb.sum() > 3 and low_amb.sum() > 3:
        fert_high = fert_arr[high_amb].mean()
        fert_low = fert_arr[low_amb].mean()
        ratio = fert_high / (fert_low + 1e-10)
        r = np.corrcoef(amb_arr, fert_arr)[0, 1] if len(amb_arr) > 3 else 0
        
        print(f'  Windows along PC1: {len(amb_profile)}')
        print(f'  Ambiguity range: [{amb_arr.min():.4f}, {amb_arr.max():.4f}]')
        print(f'  Fertility range:  [{fert_arr.min():.4f}, {fert_arr.max():.4f}]')
        print(f'  High-amb fertility: {fert_high:.4f}')
        print(f'  Low-amb fertility:  {fert_low:.4f}')
        print(f'  Ratio: {ratio:.4f}')
        print(f'  r(ambiguity, fertility) along PC1: {r:.4f}')
        
        # Detect where transition boundaries are
        amb_diff = np.abs(np.diff(amb_arr))
        max_transition = np.argmax(amb_diff) if len(amb_diff) > 0 else -1
        if max_transition >= 0:
            fert_at_trans = fert_arr[max_transition] if max_transition < len(fert_arr) else 0
            fert_before = fert_arr[max(0, max_transition-1)]
            fert_after = fert_arr[min(len(fert_arr)-1, max_transition+1)]
            # Check if fertility peaks near this transition
            peak_near = (fert_at_trans >= fert_before and fert_at_trans >= fert_after)
            print(f'  Largest amb shift at window {max_transition}')
            print(f'  Fertility at shift: {fert_at_trans:.4f} (before={fert_before:.4f}, after={fert_after:.4f})')
            print(f'  Peak at transition: {"YES" if peak_near else "NO"}')
    else:
        print(f'  Insufficient window data')

print(f'\n{"="*70}')
print('D3 COMPLETE — Boundary analysis shows whether fertility')
print('peaks near organizational transitions within each domain.')
print('='*70)
