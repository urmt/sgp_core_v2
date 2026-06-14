"""
RD-10B.0: Representation Audit

STANDING RULE (5 sources):
> When a pattern appears, does it belong to:
> the world, the representation, the detector, the question, or the observer?

DESIGN:
1. Generate ONE world (no motif vocabulary)
2. Represent it in MULTIPLE ways:
   - Graph (adjacency matrix)
   - Time series (state trajectories)
   - State-transition network
   - Correlation matrix
   - Phase-space embedding
3. Apply the SAME detectors to each representation
4. Ask: what survives representation changes?

If the same motifs appear in all representations → world property
If different motifs appear in different representations → representation property

This is the first experiment that directly attacks representation dependence.
"""

import numpy as np
import json
from collections import defaultdict

# ============================================================
# WORLD GENERATION
# ============================================================

def generate_world(seed=42):
    """
    Generate ONE world with diverse dynamics.
    No motif vocabulary.
    """
    rng = np.random.default_rng(seed)
    
    N = 12  # agents
    D = 4   # dimensions
    
    # Interaction parameters
    connectivity = 0.6
    decay = 0.1
    coupling = 1.0
    noise = 0.05
    forcing_strength = 0.5
    nonlinearity = 2.0
    
    # Initial states
    states = rng.standard_normal((N, D))
    
    # Connectivity matrix
    mask = rng.random((N, N)) < connectivity
    np.fill_diagonal(mask, False)
    weight_matrix = mask * rng.uniform(-coupling, coupling, (N, N))
    
    # Boundary
    boundary = rng.random(N) < 0.3
    
    return {
        'N': N,
        'D': D,
        'states': states,
        'weight_matrix': weight_matrix,
        'boundary': boundary,
        'decay': decay,
        'coupling': coupling,
        'noise': noise,
        'forcing_strength': forcing_strength,
        'nonlinearity': nonlinearity,
    }

def step_world(world, t, rng):
    """Evolve world by one step."""
    N, D = world['states'].shape
    new_states = np.zeros_like(world['states'])
    
    for i in range(N):
        influence = np.zeros(D)
        for j in range(N):
            if j != i:
                diff = world['states'][j] - world['states'][i]
                weight = world['weight_matrix'][j, i]
                influence += weight * diff
        
        if world['nonlinearity'] > 0:
            influence = np.tanh(world['nonlinearity'] * influence)
        
        decay_force = -world['decay'] * world['states'][i]
        forcing = world['forcing_strength'] * np.sin(2 * np.pi * t / 50 + i)
        
        new_states[i] = world['states'][i] + decay_force + influence + forcing
        
        if world['boundary'][i]:
            new_states[i] *= 0.95
    
    new_states += world['noise'] * rng.standard_normal((N, D))
    world['states'] = new_states
    return world

def run_world(n_steps=200, seed=42):
    """Run world and collect trajectory."""
    rng = np.random.default_rng(seed)
    world = generate_world(seed)
    
    trajectory = []
    for t in range(n_steps):
        world = step_world(world, t, rng)
        trajectory.append(world['states'].copy())
    
    return np.array(trajectory), world

# ============================================================
# REPRESENTATIONS
# ============================================================

def representation_graph(trajectory, world):
    """
    Represent world as a graph.
    
    Nodes: agents
    Edges: correlation between agent trajectories
    """
    N = trajectory.shape[1]
    T = trajectory.shape[0]
    
    # Compute correlation between agents
    agent_trajectories = trajectory.reshape(T, -1)  # flatten dimensions
    
    # Each agent's trajectory (all dimensions flattened)
    agent_trajs = []
    for i in range(N):
        agent_trajs.append(trajectory[:, i, :].flatten())
    
    agent_trajs = np.array(agent_trajs)  # (N, T*D)
    
    # Correlation matrix
    corr = np.corrcoef(agent_trajs)
    
    return {
        'type': 'graph',
        'adjacency': corr,
        'N': N,
    }

def representation_timeseries(trajectory, world):
    """
    Represent world as time series.
    
    One series per agent (mean across dimensions).
    """
    N = trajectory.shape[1]
    
    # Mean state per agent over time
    ts = trajectory.mean(axis=2)  # (T, N)
    
    return {
        'type': 'timeseries',
        'series': ts,
        'N': N,
    }

def representation_state_transition(trajectory, world):
    """
    Represent world as state-transition network.
    
    Discretize states, count transitions.
    """
    N = trajectory.shape[1]
    D = trajectory.shape[2]
    T = trajectory.shape[0]
    
    # Discretize: bin each dimension into 3 levels
    n_bins = 3
    
    # Flatten all agents' states
    flat = trajectory.reshape(T, -1)  # (T, N*D)
    
    # Discretize
    bins = np.linspace(flat.min(), flat.max(), n_bins + 1)
    digitized = np.digitize(flat, bins) - 1
    digitized = np.clip(digitized, 0, n_bins - 1)
    
    # Convert to state labels
    n_states = n_bins ** (N * D)
    
    # Compute transitions (simplified: just use first few dimensions)
    # Full state space too large, use pairwise transitions
    transitions = defaultdict(int)
    for t in range(T - 1):
        s1 = tuple(digitized[t, :min(6, N*D)])  # limit dimensions
        s2 = tuple(digitized[t+1, :min(6, N*D)])
        transitions[(s1, s2)] += 1
    
    return {
        'type': 'state_transition',
        'transitions': dict(transitions),
        'n_states': min(n_states, 1000),
    }

def representation_correlation(trajectory, world):
    """
    Represent world as correlation structure.
    
    Correlation between dimensions across agents.
    """
    N = trajectory.shape[1]
    D = trajectory.shape[2]
    T = trajectory.shape[0]
    
    # Correlation between dimensions (across agents and time)
    flat = trajectory.reshape(T * N, D)
    corr = np.corrcoef(flat.T)
    
    return {
        'type': 'correlation',
        'matrix': corr,
        'D': D,
    }

def representation_phasespace(trajectory, world):
    """
    Represent world as phase-space embedding.
    
    Use first two agents, first two dimensions.
    """
    # Agent 0 and Agent 1, dimensions 0 and 1
    x = trajectory[:, 0, 0]
    y = trajectory[:, 0, 1]
    z = trajectory[:, 1, 0]
    
    return {
        'type': 'phasespace',
        'x': x,
        'y': y,
        'z': z,
    }

# ============================================================
# DETECTORS (same as RD-10B.3, applied to each representation)
# ============================================================

def detect_in_graph(repr_data):
    """Detect motifs in graph representation."""
    adj = repr_data['adjacency']
    N = repr_data['N']
    
    motifs = {}
    
    # Binding: mean correlation
    mask = np.triu_indices(N, k=1)
    motifs['binding'] = float(np.mean(adj[mask]))
    
    # Network: clustering coefficient approximation
    # (fraction of connected triples that form triangles)
    A = (adj > 0.3).astype(float)
    np.fill_diagonal(A, 0)
    
    triangles = np.trace(A @ A @ A) / 6
    triples = np.sum(A @ A * (1 - np.eye(N)))
    
    if triples > 0:
        motifs['network'] = float(triangles / triples)
    else:
        motifs['network'] = 0.0
    
    # Hierarchy: variance of node degrees
    degrees = A.sum(axis=1)
    motifs['hierarchy'] = float(np.std(degrees) / (np.mean(degrees) + 1e-10))
    
    return motifs

def detect_in_timeseries(repr_data):
    """Detect motifs in time-series representation."""
    ts = repr_data['series']  # (T, N)
    N = ts.shape[1]
    
    motifs = {}
    
    # Binding: pairwise correlation
    corr = np.corrcoef(ts.T)
    mask = np.triu_indices(N, k=1)
    motifs['binding'] = float(np.mean(corr[mask]))
    
    # Recursion: autocorrelation
    mean_ts = ts.mean(axis=1)
    if len(mean_ts) > 20:
        autocorr = np.corrcoef(mean_ts[:-10], mean_ts[10:])[0, 1]
        motifs['recursion'] = float(abs(autocorr))
    else:
        motifs['recursion'] = 0.0
    
    # Cycle: dominant frequency
    if len(mean_ts) > 20:
        fft = np.fft.rfft(mean_ts - mean_ts.mean())
        power = np.abs(fft)**2
        if power.sum() > 0:
            motifs['cycle'] = float(power[1:].max() / power.sum())
        else:
            motifs['cycle'] = 0.0
    else:
        motifs['cycle'] = 0.0
    
    # Template: self-similarity
    if len(mean_ts) > 30:
        first = mean_ts[:len(mean_ts)//2]
        second = mean_ts[len(mean_ts)//2:]
        min_len = min(len(first), len(second))
        if min_len > 5:
            corr = np.corrcoef(first[:min_len], second[:min_len])[0, 1]
            motifs['template'] = float(abs(corr))
        else:
            motifs['template'] = 0.0
    else:
        motifs['template'] = 0.0
    
    return motifs

def detect_in_state_transition(repr_data):
    """Detect motifs in state-transition representation."""
    transitions = repr_data['transitions']
    
    motifs = {}
    
    # Binding: how many transitions share source states?
    sources = defaultdict(int)
    for (s1, s2), count in transitions.items():
        sources[s1] += count
    
    if sources:
        source_counts = list(sources.values())
        motifs['binding'] = float(np.std(source_counts) / (np.mean(source_counts) + 1e-10))
    else:
        motifs['binding'] = 0.0
    
    # Recursion: do states transition back to themselves?
    self_transitions = sum(count for (s1, s2), count in transitions.items() if s1 == s2)
    total = sum(transitions.values())
    motifs['recursion'] = float(self_transitions / (total + 1e-10))
    
    # Network: branching factor
    if sources:
        motifs['network'] = float(np.mean(list(sources.values())))
    else:
        motifs['network'] = 0.0
    
    return motifs

def detect_in_correlation(repr_data):
    """Detect motifs in correlation representation."""
    corr = repr_data['matrix']
    D = repr_data['D']
    
    motifs = {}
    
    # Binding: mean off-diagonal correlation
    mask = ~np.eye(D, dtype=bool)
    motifs['binding'] = float(np.mean(np.abs(corr[mask])))
    
    # Hierarchy: variance of correlations
    motifs['hierarchy'] = float(np.std(corr[mask]))
    
    return motifs

def detect_in_phasespace(repr_data):
    """Detect motifs in phase-space representation."""
    x = repr_data['x']
    y = repr_data['y']
    z = repr_data['z']
    
    motifs = {}
    
    # Cycle: autocorrelation in x
    if len(x) > 20:
        autocorr = np.corrcoef(x[:-10], x[10:])[0, 1]
        motifs['cycle'] = float(abs(autocorr))
    else:
        motifs['cycle'] = 0.0
    
    # Recursion: autocorrelation in y
    if len(y) > 20:
        autocorr = np.corrcoef(y[:-10], y[10:])[0, 1]
        motifs['recursion'] = float(abs(autocorr))
    else:
        motifs['recursion'] = 0.0
    
    # Binding: correlation between x and y
    if len(x) > 10:
        motifs['binding'] = float(abs(np.corrcoef(x, y)[0, 1]))
    else:
        motifs['binding'] = 0.0
    
    return motifs

# ============================================================
# MAIN EXPERIMENT
# ============================================================

def run_representation_audit(n_steps=200, seed=42):
    """
    Run representation audit.
    
    ONE world, MULTIPLE representations, SAME detectors.
    """
    print("RD-10B.0: Representation Audit")
    print("="*60)
    
    # 1. Generate and run ONE world
    print("\n1. Generating world...")
    trajectory, world = run_world(n_steps=n_steps, seed=seed)
    print(f"   Trajectory shape: {trajectory.shape}")
    
    # 2. Create representations
    print("\n2. Creating representations...")
    representations = {
        'graph': representation_graph(trajectory, world),
        'timeseries': representation_timeseries(trajectory, world),
        'state_transition': representation_state_transition(trajectory, world),
        'correlation': representation_correlation(trajectory, world),
        'phasespace': representation_phasespace(trajectory, world),
    }
    
    for name, repr_data in representations.items():
        print(f"   {name}: {repr_data['type']}")
    
    # 3. Apply detectors to each representation
    print("\n3. Applying detectors...")
    
    detector_map = {
        'graph': detect_in_graph,
        'timeseries': detect_in_timeseries,
        'state_transition': detect_in_state_transition,
        'correlation': detect_in_correlation,
        'phasespace': detect_in_phasespace,
    }
    
    all_motifs = {}
    for repr_name, repr_data in representations.items():
        detector = detector_map[repr_name]
        motifs = detector(repr_data)
        all_motifs[repr_name] = motifs
        print(f"   {repr_name}: {list(motifs.keys())}")
    
    # 4. Analysis: what survives representation changes?
    print("\n4. Analysis: What survives representation changes?")
    
    # Collect all motif names
    all_motif_names = set()
    for motifs in all_motifs.values():
        all_motif_names.update(motifs.keys())
    
    print("\n   Motif presence across representations:")
    for motif in sorted(all_motif_names):
        present_in = []
        for repr_name, motifs in all_motifs.items():
            if motif in motifs and motifs[motif] > 0.1:  # threshold
                present_in.append(repr_name)
        print(f"   {motif}: {len(present_in)}/{len(representations)} representations")
        if present_in:
            print(f"      Present in: {present_in}")
    
    # 5. Quantitative comparison
    print("\n5. Quantitative comparison:")
    
    for motif in sorted(all_motif_names):
        values = {}
        for repr_name, motifs in all_motifs.items():
            if motif in motifs:
                values[repr_name] = motifs[motif]
        
        if values:
            vals = list(values.values())
            print(f"\n   {motif}:")
            for repr_name, val in values.items():
                print(f"      {repr_name}: {val:.4f}")
            print(f"      Range: {max(vals) - min(vals):.4f}")
            print(f"      CV: {np.std(vals)/(np.mean(vals)+1e-10):.4f}")
    
    return {
        'trajectory_shape': list(trajectory.shape),
        'representations': list(representations.keys()),
        'motifs': all_motifs,
    }

# ============================================================
# RUN
# ============================================================

if __name__ == '__main__':
    results = run_representation_audit()
    
    with open('/home/student/sgp_core_v2/audits/rd10b0_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nSaved to audits/rd10b0_results.json")
