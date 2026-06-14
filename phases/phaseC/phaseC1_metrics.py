"""
Phase C1 — Metric Computation.
Behavioral stability, fertility, and structural descriptors for all 10 domains.
"""
import numpy as np
import pandas as pd
from scipy.stats import entropy, linregress, pearsonr
from sklearn.neighbors import NearestNeighbors
import pickle, os, warnings
warnings.filterwarnings('ignore')

OUT = '/home/student/sgp_core_v2/phases/phaseC'
with open(os.path.join(OUT, 'phaseC_systems.pkl'), 'rb') as f:
    all_systems = pickle.load(f)
print(f'Loaded {len(all_systems)} systems')

# ===================================================================
# STABILITY METRICS (from perturbation response)
# ===================================================================
def stability_generic_1d(sys, threshold=0.01):
    """Generic stability for 1D scalar trajectories."""
    traj = sys['traj'].flatten() if sys['traj'].ndim > 1 else sys['traj']
    pt = sys['pert_traj'].flatten() if sys['pert_traj'].ndim > 1 else sys['pert_traj']
    pi = sys['pert_idx']
    up = traj[pi:]
    n = min(len(pt), len(up)); pt=pt[:n]; up=up[:n]
    dists = np.abs(pt - up)
    rt = np.argmax(dists < threshold) if np.any(dists < threshold) else len(dists)
    if len(dists) > 3 and dists[0] > 1e-8:
        slope = linregress(np.arange(len(dists)), np.log(np.clip(dists, 1e-10, None))).slope
        rr = -slope
    else: rr = 0.0
    return {'stability_return_time': float(rt), 'stability_recovery_rate': float(rr),
            'stability_final_dev': float(dists[-1]), 'stability_max_dev': float(np.max(dists))}

def stability_multidim(sys, threshold=0.1, metric='euclidean'):
    """Generic stability for multi-dimensional trajectories."""
    traj = sys['traj']; pt = sys['pert_traj']; pi = sys['pert_idx']
    up = traj[pi:]
    n = min(len(pt), len(up)); pt=pt[:n]; up=up[:n]
    if metric == 'euclidean':
        dists = np.sqrt(np.sum((pt - up)**2, axis=1))
    elif metric == 'l1':
        dists = np.sum(np.abs(pt - up), axis=1)
    elif metric == 'hamming':
        dists = np.mean(pt != up, axis=1)
    else:
        dists = np.sqrt(np.sum((pt - up)**2, axis=1))
    rt = np.argmax(dists < threshold) if np.any(dists < threshold) else len(dists)
    if len(dists) > 3 and dists[0] > 1e-8:
        slope = linregress(np.arange(len(dists)), np.log(np.clip(dists, 1e-10, None))).slope
        rr = -slope
    else: rr = 0.0
    return {'stability_return_time': float(rt), 'stability_recovery_rate': float(rr),
            'stability_final_dev': float(dists[-1]), 'stability_max_dev': float(np.max(dists))}

STABILITY_FUNCS = {
    'cellular_automata':    lambda s: stability_multidim(s, threshold=0.1, metric='hamming'),
    'nonlinear_oscillator': lambda s: stability_multidim(s, threshold=0.1, metric='euclidean'),
    'graph_diffusion':      lambda s: stability_multidim(s, threshold=0.01, metric='l1'),
    'population':           lambda s: stability_generic_1d(s, threshold=0.01),
    'gray_scott':           lambda s: stability_multidim(s, threshold=0.05, metric='euclidean'),
    'kuramoto':             lambda s: stability_generic_1d(s, threshold=0.02),
    'lotka_volterra':       lambda s: stability_multidim(s, threshold=0.5, metric='euclidean'),
    'coupled_map_lattice':  lambda s: stability_multidim(s, threshold=0.1, metric='euclidean'),
    'replicator':           lambda s: stability_multidim(s, threshold=0.05, metric='l1'),
    'branching':            lambda s: stability_generic_1d(s, threshold=1.0),
}

# ===================================================================
# FERTILITY METRICS (from reference trajectory only)
# ===================================================================
def compute_fertility(ref, domain):
    """Compute fertility metrics from reference trajectory."""
    ref = np.asarray(ref)
    n_total = ref.shape[0]
    if n_total < 5:
        return {'fertility_state_diversity': 0, 'fertility_novelty_rate': 0,
                'fertility_state_coverage': 0, 'fertility_transition_entropy': 0}

    if domain in ('cellular_automata', 'coupled_map_lattice'):
        # Discrete spatial state: use discretized bins per cell
        nbins = 10 if domain == 'coupled_map_lattice' else None
        if domain == 'cellular_automata':
            states_as_bytes = [r.tobytes() for r in ref]
        else:
            # Discretize each element
            states_as_bytes = []
            for r in ref:
                try:
                    key = tuple(np.digitize(r, np.linspace(r.min(), r.max(), 10)))
                    states_as_bytes.append(key)
                except Exception:
                    states_as_bytes.append(tuple(np.zeros(len(r))))
        unique = len(set(states_as_bytes))
        diversity = unique / max(1, n_total)
        seen = set()
        first_seen = [0]
        for s in states_as_bytes:
            if s not in seen: seen.add(s); first_seen.append(1)
            else: first_seen.append(0)
        novelty_rate = np.mean(first_seen[1:]) if len(first_seen) > 1 else 0
        coverage = unique / max(1, 2**ref.shape[1]) if domain == 'cellular_automata' else unique / max(1, n_total)
        trans = [(states_as_bytes[i], states_as_bytes[i+1]) for i in range(max(1, len(states_as_bytes)-1))]
        _, cnt = np.unique(trans, axis=0, return_counts=True) if len(trans) > 0 else ([], np.array([1]))
        te = entropy(cnt/cnt.sum()) if len(cnt) > 1 else 0.0

    elif domain in ('nonlinear_oscillator', 'lotka_volterra'):
        # 2D continuous space
        nbins = 20
        xd = np.digitize(ref[:,0], np.linspace(ref[:,0].min(), ref[:,0].max(), nbins))
        yd = np.digitize(ref[:,1], np.linspace(ref[:,1].min(), ref[:,1].max(), nbins))
        pairs = list(zip(xd, yd))
        unique = len(set(pairs))
        diversity = unique / min(nbins**2, max(1, n_total))
        seen = set(); first_seen = [0]
        for s in pairs:
            if s not in seen: seen.add(s); first_seen.append(1)
            else: first_seen.append(0)
        novelty_rate = np.mean(first_seen[1:])
        coverage = unique / (nbins**2)
        trans = [(xd[i], yd[i], xd[i+1], yd[i+1]) for i in range(len(xd)-1)]
        _, cnt = np.unique(trans, axis=0, return_counts=True) if len(trans) > 0 else ([], np.array([1]))
        te = entropy(cnt/cnt.sum()) if len(cnt) > 1 else 0.0

    elif domain == 'graph_diffusion':
        nbins = 10; nn = ref.shape[1]
        state_keys = [tuple(np.digitize(r, np.linspace(0,1,nbins))) for r in ref]
        unique = len(set(state_keys))
        diversity = unique / min(nbins**min(nn, 5), max(1, n_total))
        seen = set(); first_seen = [0]
        for s in state_keys:
            if s not in seen: seen.add(s); first_seen.append(1)
            else: first_seen.append(0)
        novelty_rate = np.mean(first_seen[1:])
        coverage = unique / min(nbins**min(nn, 5), max(1, n_total))
        trans = [(state_keys[i], state_keys[i+1]) for i in range(len(state_keys)-1)]
        _, cnt = np.unique(trans, axis=0, return_counts=True) if len(trans) > 0 else ([], np.array([1]))
        te = entropy(cnt/cnt.sum()) if len(cnt) > 1 else 0.0

    elif domain in ('gray_scott',):
        # 2D pattern: track mean u and pattern entropy
        ref_flat = ref  # already (n_steps, 2) with mean_u, pat_ent
        nbins = 20
        m = ref_flat[:, 0]  # mean u
        if np.std(m) > 0:
            md = np.digitize(m, np.linspace(m.min(), m.max(), nbins))
        else:
            md = np.zeros(len(m), dtype=int)
        unique = len(set(md))
        diversity = unique / nbins
        seen = set(); first_seen = [0]
        for s in md:
            if s not in seen: seen.add(s); first_seen.append(1)
            else: first_seen.append(0)
        novelty_rate = np.mean(first_seen[1:])
        coverage = unique / nbins
        trans = [(md[i], md[i+1]) for i in range(len(md)-1)]
        _, cnt = np.unique(trans, axis=0, return_counts=True) if len(trans) > 0 else ([], np.array([1]))
        te = entropy(cnt/cnt.sum()) if len(cnt) > 1 else 0.0

    elif domain in ('kuramoto', 'branching', 'population'):
        # 1D scalar
        ref_1d = ref.flatten()
        nbins = 20 if domain != 'branching' else 15
        dr = max(1e-10, np.ptp(ref_1d))
        bins = np.linspace(ref_1d.min(), ref_1d.max(), nbins) if dr > 0 else np.arange(nbins)
        disc = np.digitize(ref_1d, bins)
        unique = len(set(disc))
        diversity = unique / nbins
        seen = set(); first_seen = [0]
        for s in disc:
            if s not in seen: seen.add(s); first_seen.append(1)
            else: first_seen.append(0)
        novelty_rate = np.mean(first_seen[1:])
        coverage = unique / nbins
        trans = [(disc[i], disc[i+1]) for i in range(len(disc)-1)]
        _, cnt = np.unique(trans, axis=0, return_counts=True) if len(trans) > 0 else ([], np.array([1]))
        te = entropy(cnt/cnt.sum()) if len(cnt) > 1 else 0.0

    elif domain == 'replicator':
        # Simplex-valued trajectory (n_strat dims that sum to 1)
        nbins = 10; ns = ref.shape[1]
        state_keys = [tuple(np.digitize(r, np.linspace(0,1,nbins))) for r in ref]
        unique = len(set(state_keys))
        diversity = unique / min(nbins**ns, max(1, n_total))
        seen = set(); first_seen = [0]
        for s in state_keys:
            if s not in seen: seen.add(s); first_seen.append(1)
            else: first_seen.append(0)
        novelty_rate = np.mean(first_seen[1:])
        coverage = unique / min(nbins**min(ns, 4), max(1, n_total))
        trans = [(state_keys[i], state_keys[i+1]) for i in range(len(state_keys)-1)]
        _, cnt = np.unique(trans, axis=0, return_counts=True) if len(trans) > 0 else ([], np.array([1]))
        te = entropy(cnt/cnt.sum()) if len(cnt) > 1 else 0.0

    else:
        diversity = novelty_rate = coverage = te = 0.0

    return {'fertility_state_diversity': float(diversity), 'fertility_novelty_rate': float(novelty_rate),
            'fertility_state_coverage': float(coverage), 'fertility_transition_entropy': float(te)}

# ===================================================================
# STRUCTURAL DESCRIPTORS (from parameters + traj, NOT ref_traj)
# ===================================================================
def desc_1d_entropy(traj, nbins=20):
    """Entropy of 1D trajectory bin distribution."""
    t = traj.flatten()
    if np.std(t) < 1e-10: return 0.0
    bins = np.linspace(t.min(), t.max(), nbins)
    disc = np.digitize(t, bins)
    counts = np.bincount(disc, minlength=nbins+1)[:nbins]
    fracs = counts / max(1, counts.sum())
    return float(entropy(fracs) / np.log(nbins))

def desc_autocorr(traj, max_lag=1):
    """Absolute lag-1 autocorrelation."""
    t = traj.flatten() if traj.ndim > 1 else traj
    if len(t) < 10: return 0.0
    if np.std(t[:-max_lag]) < 1e-10 or np.std(t[max_lag:]) < 1e-10: return 0.0
    return float(abs(np.corrcoef(t[:-max_lag], t[max_lag:])[0,1]))

def desc_spectral_entropy(traj):
    """Normalized spectral entropy."""
    t = traj.flatten() if traj.ndim > 1 else traj
    if len(t) < 10 or np.std(t) < 1e-10: return 0.0
    fft = np.abs(np.fft.fft(t - t.mean()))
    fft_n = fft / max(1, fft.sum())
    return float(entropy(fft_n) / np.log(len(fft)))

def compute_descriptors(sys):
    """Compute all 5 descriptors for any system. Uses traj (not ref_traj)."""
    domain = sys['domain']; traj = sys['traj']; params = sys['params']

    if domain == 'cellular_automata':
        rule = params['rule']; L = params['L']
        bits = [(rule>>i)&1 for i in range(8)]
        p1 = sum(bits)/8
        csr = entropy([p1, 1-p1]) if 0 < p1 < 1 else 0.0
        rbs = sum(bits)/8.0
        adi = desc_autocorr(traj[:,0] if traj.ndim>1 and traj.shape[1]>0 else traj)
        sb = [r.tobytes() for r in traj]
        trans = [(sb[i], sb[i+1]) for i in range(min(len(sb)-1, 50))]
        _, cnt = np.unique(trans, return_counts=True) if len(set(trans)) > 1 else ([], np.array([1]))
        rtp = entropy(cnt/cnt.sum()) if len(cnt) > 1 else 0.0
        srd = float(2**L)
        return {'CSR':float(csr),'RBS':float(rbs),'ADI':float(adi),'RTP':float(rtp),'SRD':float(srd)}

    elif domain == 'nonlinear_oscillator':
        b, d, g = params['beta'], params['delta'], params['gamma']
        csr = abs(b)/(d+1e-10); rbs = abs(b)*abs(g)
        adi = desc_autocorr(traj[:100,0] if len(traj)>100 else traj[:,0]) if len(traj)>10 else 0.0
        rtp = desc_spectral_entropy(traj[:200,0] if len(traj)>200 else traj[:,0])
        srd = float(len(traj.shape)) if len(traj.shape) > 1 else 1.0
        return {'CSR':float(csr),'RBS':float(rbs),'ADI':float(adi),'RTP':float(rtp),'SRD':float(srd)}

    elif domain == 'graph_diffusion':
        adj = sys.get('adj', None)
        if adj is None: adj = np.eye(params.get('n_nodes', 10))
        deg = adj.sum(axis=1)
        dg = deg / max(1, deg.sum())
        csr = entropy(dg) if deg.sum() > 0 else 0.0
        deg_b = (adj>0).astype(float)
        num = deg_b @ deg_b @ deg_b
        den = np.diag(deg_b @ deg_b) * (np.diag(deg_b @ deg_b) - 1) + 1e-10
        rbs = float(np.mean(np.diag(num)/den))
        Lm = np.diag(deg) - adj
        ev = np.sort(np.linalg.eigvalsh(Lm))
        adi = float(ev[1]) if len(ev) > 1 else 0.0
        n = params.get('n_nodes', len(deg))
        rtp = csr / np.log(n) if n > 1 else 0.0
        srd = float(n)
        return {'CSR':float(csr),'RBS':float(rbs),'ADI':float(adi),'RTP':float(rtp),'SRD':float(srd)}

    elif domain == 'population':
        r = params['r']
        csr = desc_1d_entropy(traj, nbins=20)
        rbs = abs(r - 2.5)
        adi = desc_autocorr(traj)
        rtp = desc_spectral_entropy(traj)
        srd = float(r)
        return {'CSR':float(csr),'RBS':float(rbs),'ADI':float(adi),'RTP':float(rtp),'SRD':float(srd)}

    elif domain == 'gray_scott':
        # Use Du, Dv, F, k parameters
        Du, Dv, F, k = params['Du'], params['Dv'], params['F'], params['k']
        csr = F / (k + 1e-10)  # feed-to-kill ratio
        rbs = Du / (Dv + 1e-10)  # diffusion ratio
        adi = desc_autocorr(traj[:,0] if traj.ndim>1 and traj.shape[1]>0 else traj)
        rtp = desc_spectral_entropy(traj[:,1] if traj.ndim>1 and traj.shape[1]>1 else traj)
        L = params.get('L', 30)
        srd = float(L**2)  # grid size
        return {'CSR':float(csr),'RBS':float(rbs),'ADI':float(adi),'RTP':float(rtp),'SRD':float(srd)}

    elif domain == 'kuramoto':
        N, K, ww = params['N'], params['K'], params['w_width']
        csr = K / (ww + 1e-10)  # coupling / frequency spread
        rbs = float(K)  # coupling strength
        adi = desc_autocorr(traj)
        rtp = desc_spectral_entropy(traj)
        srd = float(N)
        return {'CSR':float(csr),'RBS':float(rbs),'ADI':float(adi),'RTP':float(rtp),'SRD':float(srd)}

    elif domain == 'lotka_volterra':
        a, b, d, g = params['alpha'], params['beta'], params['delta'], params['gamma']
        csr = a / (g + 1e-10)  # prey growth / predator death
        rbs = b * d  # interaction product
        adi = desc_autocorr(traj[:,0] if traj.ndim>1 and traj.shape[1]>0 else traj)
        rtp = desc_spectral_entropy(traj[:,1] if traj.ndim>1 and traj.shape[1]>1 else traj)
        srd = 2.0  # always 2 species
        return {'CSR':float(csr),'RBS':float(rbs),'ADI':float(adi),'RTP':float(rtp),'SRD':float(srd)}

    elif domain == 'coupled_map_lattice':
        L, r, eps = params['L'], params['r'], params['eps']
        csr = r / (eps + 1e-10)  # nonlinearity / coupling
        rbs = float(r)  # logistic parameter
        # Mean field over lattice
        mf = traj.mean(axis=1) if traj.ndim > 1 else traj
        adi = desc_autocorr(mf)
        rtp = desc_spectral_entropy(mf)
        srd = float(L)
        return {'CSR':float(csr),'RBS':float(rbs),'ADI':float(adi),'RTP':float(rtp),'SRD':float(srd)}

    elif domain == 'replicator':
        ns = params['n_strat']
        csr = float(ns) / 3.0  # normalized strategy count
        # Use trajectory mean entropy as branching measure
        t = np.clip(traj, 1e-10, 1-1e-10)
        ent = np.array([entropy(r) for r in t])
        rbs = float(np.mean(ent))
        mf = t.mean(axis=1) if t.ndim > 1 else t
        adi = desc_autocorr(mf[:,0] if mf.ndim>1 and mf.shape[1]>0 else mf)
        rtp = desc_spectral_entropy(mf[:,0] if mf.ndim>1 and mf.shape[1]>0 else mf)
        srd = float(ns)
        return {'CSR':float(csr),'RBS':float(rbs),'ADI':float(adi),'RTP':float(rtp),'SRD':float(srd)}

    elif domain == 'branching':
        lam = params['lambda']
        csr = float(lam) / 2.5  # normalized by max lambda
        rbs = float(max(0, lam - 1.0))  # supercriticality
        traj_1d = traj.flatten() if traj.ndim > 1 else traj
        adi = desc_autocorr(traj_1d)
        if len(traj_1d) > 3:
            rtp = entropy(np.diff(traj_1d[traj_1d>0]) + 1) / np.log(len(traj_1d)) if len(traj_1d[traj_1d>0]) > 2 else 0.0
        else: rtp = 0.0
        srd = 1.0  # single population
        return {'CSR':float(csr),'RBS':float(rbs),'ADI':float(adi),'RTP':float(rtp),'SRD':float(srd)}

    return {'CSR':0,'RBS':0,'ADI':0,'RTP':0,'SRD':0}

# ===================================================================
# COMPUTE ALL METRICS
# ===================================================================
SEED = 2001
rng = np.random.default_rng(SEED)

rows = []
for sys in all_systems:
    domain = sys['domain']
    stab = STABILITY_FUNCS[domain](sys)
    fert = compute_fertility(sys['ref_traj'], domain)
    desc = compute_descriptors(sys)
    row = {'sys_id': sys['sys_id'], 'domain': domain, **stab, **fert, **desc}
    rows.append(row)

df = pd.DataFrame(rows)
out_csv = os.path.join(OUT, 'phaseC_metrics.csv')
df.to_csv(out_csv, index=False)

print(f'\nSaved {len(df)} systems to phaseC_metrics.csv')
print(f'Columns: {list(df.columns)}')
print(f'Domains: {df["domain"].value_counts().to_dict()}')

# LEAKAGE AUDIT
print(f'\nLEAKAGE CHECK: CSR+RBS vs targets')
for t in [c for c in df.columns if c.startswith('stability_') or c.startswith('fertility_')]:
    combined = df['CSR'].values + df['RBS'].values
    r, p = pearsonr(combined, df[t].values)
    print(f'  CSR+RBS vs {t}: r={r:.4f}, p={p:.4g}')

# Check for perfect or near-perfect predictions (flag any R² > 0.9 candidates)
print(f'\nDESCRIPTOR ANCESTRY CHECK: any target linearly determined by all 5 desc?')
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import LeaveOneOut
loo = LeaveOneOut()
for t in [c for c in df.columns if c.startswith('stability_') or c.startswith('fertility_')]:
    X = df[['CSR','RBS','ADI','RTP','SRD']].values
    y = df[t].values
    from sklearn.preprocessing import StandardScaler
    preds = np.empty(len(y))
    for tr, te in loo.split(X):
        X_tr = StandardScaler().fit_transform(X[tr]); X_te = StandardScaler().fit_transform(X[te])
        preds[te[0]] = LinearRegression().fit(X_tr, y[tr]).predict(X_te)[0]
    r2 = np.corrcoef(y, preds)[0,1]**2
    if r2 > 0.9:
        print(f'  *** HIGH-RISK: {t} LOOCV R² = {r2:.4f}')
    else:
        print(f'  {t}: LOOCV R² = {r2:.4f}')
