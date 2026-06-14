"""
Phase A2–A4: Compute behavioral stability, fertility metrics,
AND structural descriptors independently.
"""
import numpy as np
import pandas as pd
from scipy.stats import entropy, pearsonr, linregress
from scipy.spatial.distance import pdist
from sklearn.neighbors import NearestNeighbors
import pickle
import warnings
warnings.filterwarnings('ignore')

SEED = 1001
rng = np.random.default_rng(SEED)

with open('/home/student/sgp_core_v2/phases/phaseA/phaseA_systems.pkl', 'rb') as f:
    all_systems = pickle.load(f)

print(f'Loaded {len(all_systems)} systems')

# ============================================================
# BEHAVIORAL STABILITY METRICS (from perturbation response only)
# ============================================================
def compute_stability_ca(sys):
    """Stability metrics for CA from perturbation trajectory."""
    traj = sys['traj']
    pert_traj = sys['pert_traj']
    pert_step = sys['pert_step']
    
    # Unperturbed post-perturbation trajectory
    unpert_post = traj[pert_step:]
    n_steps = min(len(pert_traj), len(unpert_post))
    pert = pert_traj[:n_steps]
    unpert = unpert_post[:n_steps]
    
    # Hamming distance over time
    hamming = np.mean(pert != unpert, axis=1)
    
    # 1. Return time: steps until hamming < 0.1
    return_time = np.argmax(hamming < 0.1) if np.any(hamming < 0.1) else len(hamming)
    
    # 2. Recovery rate: exponential fit to hamming decay
    if len(hamming) > 3 and hamming[0] > 0:
        log_h = np.log(np.clip(hamming, 1e-10, None))
        slope = linregress(np.arange(len(log_h)), log_h).slope
        recovery_rate = -slope  # positive = recovery
    else:
        recovery_rate = 0.0
    
    # 3. Final deviation
    final_dev = hamming[-1] if len(hamming) > 0 else 0.0
    
    # 4. Perturbation susceptibility: max hamming after perturbation
    max_dev = np.max(hamming) if len(hamming) > 0 else 0.0
    
    return {
        'stability_return_time': float(return_time),
        'stability_recovery_rate': float(recovery_rate),
        'stability_final_dev': float(final_dev),
        'stability_max_dev': float(max_dev),
    }

def compute_stability_osc(sys):
    """Stability metrics for oscillator from perturbation."""
    traj = sys['traj']
    pert_traj = sys['pert_traj']
    pert_idx = sys['pert_idx']
    
    unpert_post = traj[pert_idx:]
    n_steps = min(len(pert_traj), len(unpert_post))
    pert = pert_traj[:n_steps]
    unpert = unpert_post[:n_steps]
    
    # Euclidean distance in phase space
    dists = np.sqrt(np.sum((pert - unpert)**2, axis=1))
    
    return_time = np.argmax(dists < 0.1) if np.any(dists < 0.1) else len(dists)
    
    if len(dists) > 3 and dists[0] > 1e-6:
        log_d = np.log(np.clip(dists, 1e-10, None))
        slope = linregress(np.arange(len(log_d)), log_d).slope
        recovery_rate = -slope
    else:
        recovery_rate = 0.0
    
    return {
        'stability_return_time': float(return_time),
        'stability_recovery_rate': float(recovery_rate),
        'stability_final_dev': float(dists[-1]) if len(dists) > 0 else 0.0,
        'stability_max_dev': float(np.max(dists)) if len(dists) > 0 else 0.0,
    }

def compute_stability_graph(sys):
    """Stability metrics for graph diffusion."""
    traj = sys['traj']
    pert_traj = sys['pert_traj']
    pert_idx = sys['pert_idx']
    
    unpert_post = traj[pert_idx:]
    n_steps = min(len(pert_traj), len(unpert_post))
    pert = pert_traj[:n_steps]
    unpert = unpert_post[:n_steps]
    
    # L1 distance (probability distributions)
    dists = np.sum(np.abs(pert - unpert), axis=1)
    
    return_time = np.argmax(dists < 0.01) if np.any(dists < 0.01) else len(dists)
    
    if len(dists) > 3 and dists[0] > 1e-6:
        log_d = np.log(np.clip(dists, 1e-10, None))
        slope = linregress(np.arange(len(log_d)), log_d).slope
        recovery_rate = -slope
    else:
        recovery_rate = 0.0
    
    return {
        'stability_return_time': float(return_time),
        'stability_recovery_rate': float(recovery_rate),
        'stability_final_dev': float(dists[-1]),
        'stability_max_dev': float(np.max(dists)),
    }

def compute_stability_pop(sys):
    """Stability metrics for population/logistic."""
    traj = sys['traj']
    pert_traj = sys['pert_traj']
    pert_idx = sys['pert_idx']
    
    unpert_post = traj[pert_idx:]
    n_steps = min(len(pert_traj), len(unpert_post))
    pert = pert_traj[:n_steps]
    unpert = unpert_post[:n_steps]
    
    dists = np.abs(pert - unpert)
    
    return_time = np.argmax(dists < 0.01) if np.any(dists < 0.01) else len(dists)
    
    if len(dists) > 3 and dists[0] > 1e-6:
        log_d = np.log(np.clip(dists, 1e-10, None))
        slope = linregress(np.arange(len(log_d)), log_d).slope
        recovery_rate = -slope
    else:
        recovery_rate = 0.0
    
    return {
        'stability_return_time': float(return_time),
        'stability_recovery_rate': float(recovery_rate),
        'stability_final_dev': float(dists[-1]),
        'stability_max_dev': float(np.max(dists)),
    }

stability_funcs = {
    'cellular_automata': compute_stability_ca,
    'nonlinear_oscillator': compute_stability_osc,
    'graph_diffusion': compute_stability_graph,
    'population': compute_stability_pop,
}

# ============================================================
# BEHAVIORAL FERTILITY METRICS (from unperturbed trajectory)
# ============================================================
def compute_fertility_all(sys):
    """Generic fertility metrics from reference trajectory."""
    domain = sys['domain']
    ref = sys['ref_traj']
    
    if domain == 'cellular_automata':
        # State is binary lattice — flatten
        states = ref
        n_total = states.shape[0]
        
        # 1. State diversity: number of distinct states
        state_bytes = [s.tobytes() for s in states]
        unique_states = len(set(state_bytes))
        state_diversity = unique_states / n_total
        
        # 2. Novelty rate
        seen = set()
        first_seen = []
        for s in state_bytes:
            if s not in seen:
                seen.add(s)
                first_seen.append(1)
            else:
                first_seen.append(0)
        novelty_rate = np.mean(first_seen[1:])  # fraction of new state appearances
        
        # 3. State-space coverage (fraction of possible 2^L states visited)
        coverage = unique_states / (2**states.shape[1])
        
        # 4. Transition entropy (entropy of state transitions)
        transitions = [(state_bytes[i], state_bytes[i+1]) for i in range(len(state_bytes)-1)]
        _, counts = np.unique(transitions, axis=0, return_counts=True)
        trans_entropy = entropy(counts / counts.sum()) if len(counts) > 1 else 0.0
        extra = {}
        
    elif domain == 'nonlinear_oscillator':
        n_total = ref.shape[0]
        # Discretize phase space into bins
        nbins = 20
        x_disc = np.digitize(ref[:, 0], np.linspace(ref[:, 0].min(), ref[:, 0].max(), nbins))
        v_disc = np.digitize(ref[:, 1], np.linspace(ref[:, 1].min(), ref[:, 1].max(), nbins))
        state_pairs = list(zip(x_disc, v_disc))
        unique_states = len(set(state_pairs))
        state_diversity = unique_states / min(nbins**2, n_total)
        
        seen = set()
        first_seen = [0]
        for s in state_pairs:
            seen.add(s)
            first_seen.append(1 if len(seen) > len(set(state_pairs[:state_pairs.index(s)])) else 0)
        novelty_rate = np.mean(first_seen[1:])
        coverage = unique_states / (nbins**2)
        
        # Phase-space volume (via convex hull approximate)
        vol = np.prod(np.ptp(ref, axis=0)) if ref.shape[0] > 1 else 0
        
        # 4. Lyapunov-like divergence: correlation dimension estimate
        if ref.shape[0] > 10:
            nbrs = NearestNeighbors(n_neighbors=3).fit(ref)
            dists, _ = nbrs.kneighbors(ref)
            mean_nn_dist = np.mean(dists[:, 1])  # mean distance to second nearest neighbor
        else:
            mean_nn_dist = 0
        
        trans_pairs = [(x_disc[i], v_disc[i], x_disc[i+1], v_disc[i+1]) for i in range(len(x_disc)-1)]
        _, counts = np.unique(trans_pairs, axis=0, return_counts=True)
        trans_entropy = entropy(counts / counts.sum()) if len(counts) > 1 else 0.0
        
        extra = {'fertility_phase_vol': float(vol), 'fertility_nn_dist': float(mean_nn_dist)}
        
    elif domain == 'graph_diffusion':
        n_total = ref.shape[0]
        nbins = 10
        n_nodes = ref.shape[1]
        # Discretize each node's concentration
        state_key = lambda r: tuple(np.digitize(r, np.linspace(0, 1, nbins)))
        state_keys = [state_key(r) for r in ref]
        unique_states = len(set(state_keys))
        state_diversity = unique_states / min(nbins**n_nodes, n_total)
        
        seen = set()
        first_seen = [0]
        for s in state_keys:
            if s not in seen:
                seen.add(s)
                first_seen.append(1)
            else:
                first_seen.append(0)
        novelty_rate = np.mean(first_seen[1:])
        coverage = unique_states / min(nbins**min(n_nodes, 5), n_total)
        
        # Transition entropy
        trans_pairs = [(state_keys[i], state_keys[i+1]) for i in range(len(state_keys)-1)]
        _, counts = np.unique(trans_pairs, axis=0, return_counts=True)
        trans_entropy = entropy(counts / counts.sum()) if len(counts) > 1 else 0.0
        extra = {}
        
    else:  # population
        n_total = ref.shape[0]
        nbins = 30
        pops_disc = np.digitize(ref, np.linspace(0, 1, nbins)).flatten()
        unique_states = len(set(pops_disc))
        state_diversity = unique_states / nbins
        
        seen = set()
        first_seen = []
        for p in pops_disc:
            seen.add(p)
            first_seen.append(1 if len(seen) > len(set(list(pops_disc[:list(pops_disc).index(p)]))) else 0)
        novelty_rate = np.mean(first_seen[1:])
        coverage = unique_states / nbins
        
        # Transition entropy
        trans_pairs = [(pops_disc[i], pops_disc[i+1]) for i in range(len(pops_disc)-1)]
        _, counts = np.unique(trans_pairs, axis=0, return_counts=True)
        trans_entropy = entropy(counts / counts.sum()) if len(counts) > 1 else 0.0
        extra = {}

    results = {
        'fertility_state_diversity': float(state_diversity),
        'fertility_novelty_rate': float(novelty_rate),
        'fertility_state_coverage': float(coverage),
        'fertility_transition_entropy': float(trans_entropy),
    }
    results.update(extra)
    return results

# ============================================================
# STRUCTURAL DESCRIPTORS (from system parameters/constitution)
# ============================================================
def compute_descriptors_ca(sys):
    """Structural descriptors for CA from rule + initial dynamics.
    Uses traj (NOT ref_traj) to avoid leakage with fertility metrics."""
    rule = sys['rule']
    L = sys['L']
    traj = sys['traj']  # original pre-perturbation trajectory
    
    # CSR: complexity of the rule table (entropy of output bits)
    rule_bits = [(rule >> i) & 1 for i in range(8)]
    p1 = sum(rule_bits) / 8
    csr = entropy([p1, 1-p1]) if 0 < p1 < 1 else 0.0
    
    # RBS: branching in state space — use rule lambda parameter
    # (fraction of 1s in rule output)
    rbs = float(sum(rule_bits)) / 8.0
    
    # ADI: autocorrelation of a short trajectory (using traj[0], NOT ref_traj)
    state = traj[:, 0] if traj.shape[0] > 1 else traj[:, 0] if len(traj.shape) > 1 else np.array([0])
    if len(state) > 5 and np.std(state[:-1]) > 0 and np.std(state[1:]) > 0:
        lag1 = np.corrcoef(state[:-1], state[1:])[0, 1]
        adi = float(np.abs(lag1))
    else:
        adi = 0.0
    
    # RTP: topological path entropy — use unique transitions in traj
    state_bytes = [r.tobytes() for r in traj]
    trans = [(state_bytes[i], state_bytes[i+1]) for i in range(min(len(state_bytes)-1, 50))]
    if len(set(trans)) > 1:
        _, cnt = np.unique(trans, return_counts=True)
        rtp = entropy(cnt / cnt.sum())
    else:
        rtp = 0.0
    
    # SRD: state-space size (NOT trajectory-based — purely structural)
    srd = float(2**L)  # total possible states
    
    return {
        'CSR': csr,
        'RBS': rbs,
        'ADI': adi,
        'RTP': rtp,
        'SRD': srd,
    }

def compute_descriptors_osc(sys):
    """Structural descriptors for oscillator. Uses traj (not ref_traj)."""
    params = sys['params']
    traj = sys['traj']  # original trajectory, NOT fertility's ref_traj
    
    # CSR: complexity of nonlinearity (beta magnitude / damping)
    csr = abs(params['beta']) / (params['delta'] + 1e-10)
    
    # RBS: nonlinearity × drive strength (bifurcation potential)
    rbs = abs(params['beta']) * abs(params['gamma'])
    
    # ADI: autocorrelation of trajectory (first 100 steps only, from traj)
    if len(traj) > 10:
        x = traj[:100, 0] if len(traj) > 100 else traj[:, 0]
        if np.std(x[:-1]) > 1e-10 and np.std(x[1:]) > 1e-10:
            lag1 = np.corrcoef(x[:-1], x[1:])[0, 1]
            adi = float(abs(lag1))
        else:
            adi = 0.0
    else:
        adi = 0.0
    
    # RTP: spectral entropy (from traj)
    if len(traj) > 10:
        x = traj[:200, 0] if len(traj) > 200 else traj[:, 0]
        xd = x - x.mean()
        fft = np.abs(np.fft.fft(xd))
        fft_n = fft / (fft.sum() + 1e-10)
        rtp = entropy(fft_n) / np.log(len(fft))
    else:
        rtp = 0.0
    
    # SRD: phase-space dimension (purely structural, not trajectory-based)
    srd = float(len(traj.shape)) if len(traj.shape) > 1 else 1.0
    
    return {
        'CSR': csr,
        'RBS': rbs,
        'ADI': adi,
        'RTP': rtp,
        'SRD': srd,
    }

def compute_descriptors_graph(sys):
    """Structural descriptors for graph diffusion."""
    adj = sys['adj']
    n = sys['n_nodes']
    
    # CSR: graph complexity (entropy of degree distribution)
    deg = adj.sum(axis=1)
    deg_frac = deg / (deg.sum() + 1e-10)
    csr = entropy(deg_frac) if deg.sum() > 0 else 0.0
    
    # RBS: branching structure (connectedness / clustering)
    # Use average clustering coefficient
    deg_bin = (adj > 0).astype(float)
    num = deg_bin @ deg_bin @ deg_bin
    den = np.diag(deg_bin @ deg_bin) * (np.diag(deg_bin @ deg_bin) - 1) + 1e-10
    clust = np.mean(np.diag(num) / den)
    rbs = clust
    
    # ADI: spectral gap (Fiedler eigenvalue)
    L_mat = np.diag(deg) - adj
    eigvals = np.sort(np.linalg.eigvalsh(L_mat))
    adi = float(eigvals[1]) if len(eigvals) > 1 else 0.0
    
    # RTP: path diversity (entropy of shortest path lengths)
    # Approximate via degree entropy
    rtp = csr / np.log(n) if n > 1 else 0.0
    
    # SRD: state richness (n_nodes)
    srd = float(n)
    
    return {
        'CSR': csr,
        'RBS': rbs,
        'ADI': adi,
        'RTP': rtp,
        'SRD': srd,
    }

def compute_descriptors_pop(sys):
    """Structural descriptors for population/logistic. Uses traj, not ref_traj."""
    r = sys['r']
    traj = sys['traj']  # original trajectory
    
    # CSR: complexity = entropy of trajectory bins (from traj, not ref_traj)
    nbins = 20
    bins = np.linspace(0, 1, nbins)
    disc = np.digitize(traj, bins).flatten()
    counts = np.bincount(disc, minlength=nbins+1)[:nbins]
    fracs = counts / (counts.sum() + 1e-10)
    csr = entropy(fracs) / np.log(nbins)
    
    # RBS: bifurcation complexity — r parameter itself
    rbs = abs(r - 2.5)  # distance from simple stable regime
    
    # ADI: autocorrelation (from traj)
    if len(traj) > 10:
        x = traj.flatten()
        if np.std(x[:-1]) > 1e-10 and np.std(x[1:]) > 1e-10:
            lag1 = np.corrcoef(x[:-1], x[1:])[0, 1]
            adi = float(abs(lag1))
        else:
            adi = 0.0
    else:
        adi = 0.0
    
    # RTP: spectral entropy (from traj)
    if len(traj) > 10:
        x = traj.flatten() - traj.flatten().mean()
        fft = np.abs(np.fft.fft(x))
        fft_n = fft / (fft.sum() + 1e-10)
        rtp = entropy(fft_n) / np.log(len(fft))
    else:
        rtp = 0.0
    
    # SRD: parameter range (purely structural)
    srd = float(r)
    
    return {
        'CSR': csr,
        'RBS': rbs,
        'ADI': adi,
        'RTP': rtp,
        'SRD': srd,
    }

descriptor_funcs = {
    'cellular_automata': compute_descriptors_ca,
    'nonlinear_oscillator': compute_descriptors_osc,
    'graph_diffusion': compute_descriptors_graph,
    'population': compute_descriptors_pop,
}

# ============================================================
# COMPUTE ALL METRICS FOR ALL SYSTEMS
# ============================================================
rows = []
for sys in all_systems:
    domain = sys['domain']
    
    # Behavioral stability
    stab = stability_funcs[domain](sys)
    
    # Behavioral fertility
    fert = compute_fertility_all(sys)
    
    # Structural descriptors
    desc = descriptor_funcs[domain](sys)
    
    row = {
        'sys_id': sys['sys_id'],
        'domain': domain,
        **stab,
        **fert,
        **desc,
    }
    rows.append(row)

df = pd.DataFrame(rows)
df.to_csv('/home/student/sgp_core_v2/phases/phaseA/phaseA_metrics.csv', index=False)

print(f'\nSaved {len(df)} systems with metrics.')
print(f'Columns: {list(df.columns)}')
print(f'\nDomains: {df["domain"].value_counts().to_dict()}')
print(f'\nStability metrics: {[c for c in df.columns if "stability" in c]}')
print(f'Fertility metrics: {[c for c in df.columns if "fertility" in c]}')
print(f'Descriptors: {[c for c in df.columns if c in ["CSR","RBS","ADI","RTP","SRD"]]}')

# Quick check: no perfect relationships
print(f'\nLEAKAGE CHECK: CSR+RBS vs stability metrics')
for m in [c for c in df.columns if 'stability' in c]:
    combined = df['CSR'].values + df['RBS'].values
    r, p = pearsonr(combined, df[m].values)
    print(f'  CSR+RBS vs {m}: r={r:.4f}, p={p:.4g}')
