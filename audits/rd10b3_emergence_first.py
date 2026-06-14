"""
RD-10B.3: Emergence-First Worlds

DESIGN PHILOSOPHY:
- Generate worlds with NO motif vocabulary
- Observe major transitions
- Record what changes
- Only afterward attempt categorization
- The question must not select the answer

STANDING RULE:
> Whenever a pattern appears, ask whether it belongs to the world,
> the representation, or the detector.

This experiment adds: the question itself.

APPROACH:
1. Generate 50 diverse worlds (no motif labels)
2. Run each for 200 steps
3. Record raw state at each step
4. After all runs: compute transition points
5. At each transition: what changed?
6. Post-hoc: which motifs appear?

The world generation is the key design.
We want worlds that are:
- Diverse (different dynamics)
- Not built to exhibit any motif
- Capable of major transitions
"""

import numpy as np
import json
import random
from collections import defaultdict

# ============================================================
# WORLD GENERATORS (no motif vocabulary)
# ============================================================

def generate_world(world_id, rng):
    """
    Generate a world with no motif labels.
    
    The world is defined by:
    - N agents
    - State dimension D
    - Interaction function (emerges from parameters)
    - Boundary conditions
    - External forcing
    
    None of these are labeled with motif names.
    """
    N = rng.integers(5, 20)
    D = rng.integers(2, 8)
    
    # Interaction parameters (no motif names!)
    connectivity = rng.uniform(0.1, 0.9)
    decay = rng.uniform(0.01, 0.3)
    coupling = rng.uniform(0.0, 2.0)
    noise = rng.uniform(0.0, 0.1)
    forcing_strength = rng.uniform(0.0, 1.0)
    nonlinearity = rng.uniform(0.0, 3.0)
    
    # Initial states
    states = rng.standard_normal((N, D))
    
    # Connectivity matrix (random, no motif structure)
    mask = rng.random((N, N)) < connectivity
    np.fill_diagonal(mask, False)
    weight_matrix = mask * rng.uniform(-coupling, coupling, (N, N))
    
    # Boundary: which agents are "inside" (no motif label)
    boundary = rng.random(N) < 0.3
    
    return {
        'id': world_id,
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
        'connectivity': connectivity,
    }

def step_world(world, t, rng):
    """
    Evolve world by one step.
    
    The dynamics are generic, not motif-specific.
    """
    N, D = world['states'].shape
    new_states = np.zeros_like(world['states'])
    
    for i in range(N):
        # Influence from neighbors
        influence = np.zeros(D)
        for j in range(N):
            if j != i:
                diff = world['states'][j] - world['states'][i]
                weight = world['weight_matrix'][j, i]
                influence += weight * diff
        
        # Nonlinear response
        if world['nonlinearity'] > 0:
            influence = np.tanh(world['nonlinearity'] * influence)
        
        # Decay
        decay_force = -world['decay'] * world['states'][i]
        
        # External forcing (sinusoidal, different per agent)
        forcing = world['forcing_strength'] * np.sin(2 * np.pi * t / 50 + i)
        
        # Update
        new_states[i] = world['states'][i] + decay_force + influence + forcing
        
        # Boundary effect: boundary agents have lower variance
        if world['boundary'][i]:
            new_states[i] *= 0.95
    
    # Add noise
    new_states += world['noise'] * rng.standard_normal((N, D))
    
    world['states'] = new_states
    return world

# ============================================================
# MEASUREMENT (no motif vocabulary — just raw observables)
# ============================================================

def measure_raw(history, world):
    """
    Measure raw observables — no motif names.
    """
    N, D = world['states'].shape
    
    # State statistics
    mean_state = np.mean(world['states'])
    std_state = np.std(world['states'])
    
    # Pairwise correlations
    corr_matrix = np.corrcoef(world['states'].T)
    mean_corr = np.mean(corr_matrix[np.triu_indices_from(corr_matrix, k=1)])
    
    # Variance across agents
    agent_variance = np.mean(np.var(world['states'], axis=1))
    
    # Variance across dimensions
    dim_variance = np.mean(np.var(world['states'], axis=0))
    
    # Connectivity (nonzero weights)
    nonzero = np.count_nonzero(world['weight_matrix'])
    total = world['weight_matrix'].size
    density = nonzero / total
    
    # Boundary fraction
    boundary_frac = np.mean(world['boundary'])
    
    # State entropy (binned)
    flat = world['states'].flatten()
    hist, _ = np.histogram(flat, bins=20)
    probs = hist / hist.sum()
    probs = probs[probs > 0]
    entropy = -np.sum(probs * np.log(probs))
    
    return {
        'mean_state': float(mean_state),
        'std_state': float(std_state),
        'mean_corr': float(mean_corr),
        'agent_variance': float(agent_variance),
        'dim_variance': float(dim_variance),
        'density': float(density),
        'boundary_frac': float(boundary_frac),
        'entropy': float(entropy),
    }

def detect_transition(history, key):
    """
    Detect transitions in a raw observable.
    
    Returns: list of (time, magnitude) tuples.
    """
    values = [h[key] for h in history]
    if len(values) < 10:
        return []
    
    arr = np.array(values)
    mean = arr.mean()
    std = arr.std()
    
    if std == 0:
        return []
    
    # Find large changes (3x rolling std)
    window = 10
    transitions = []
    
    for i in range(window, len(arr)):
        local_mean = arr[max(0, i-window):i].mean()
        local_std = arr[max(0, i-window):i].std()
        
        if local_std > 0:
            z = (arr[i] - local_mean) / local_std
            if abs(z) > 2.5:
                transitions.append((i, abs(z), key))
    
    return transitions

# ============================================================
# POST-HOC MOTIF DETECTION
# ============================================================

def detect_motifs_posthoc(history, world):
    """
    After observing the world, ask: what motifs appear?
    
    This is the post-hoc categorization step.
    The motifs are discovered, not assumed.
    """
    N, D = world['states'].shape
    
    # Build state-transition representation
    states = [h['mean_state'] for h in history]
    arr = np.array(states)
    
    if len(arr) < 20:
        return {}
    
    motifs = {}
    
    # 1. Binding: do agents stay together?
    agent_means = []
    for i in range(N):
        agent_i = []
        for h in history:
            agent_i.append(h.get('mean_state', 0))
        agent_means.append(agent_i)
    
    if len(agent_means) >= 2:
        agent_arr = np.array(agent_means)
        corr = np.corrcoef(agent_arr)
        mean_pairwise = np.mean(corr[np.triu_indices_from(corr, k=1)])
        motifs['binding'] = float(mean_pairwise)
    
    # 2. Network: is there structure in correlations?
    if len(history) > 10:
        # Build adjacency from state correlations
        last_N_states = [h.get('mean_state', 0) for h in history[-N:]]
        if len(last_N_states) >= N:
            state_arr = np.array(last_N_states).reshape(N, -1)
            if state_arr.shape[1] > 1:
                corr = np.corrcoef(state_arr)
                motifs['network'] = float(np.mean(np.abs(corr[np.triu_indices_from(corr, k=1)])))
    
    # 3. Hierarchy: is there variance structure?
    variances = [h.get('agent_variance', 0) for h in history[-20:]]
    if len(variances) > 5:
        motifs['hierarchy'] = float(np.std(variances) / (np.mean(variances) + 1e-10))
    
    # 4. Recursion: does the system revisit states?
    if len(arr) > 20:
        # Autocorrelation at lag 10
        autocorr = np.corrcoef(arr[:-10], arr[10:])[0, 1]
        motifs['recursion'] = float(abs(autocorr))
    
    # 5. Template: is there a repeating pattern?
    if len(arr) > 30:
        # Compare first half to second half
        first = arr[:len(arr)//2]
        second = arr[len(arr)//2:]
        min_len = min(len(first), len(second))
        if min_len > 5:
            corr = np.corrcoef(first[:min_len], second[:min_len])[0, 1]
            motifs['template'] = float(abs(corr))
    
    # 6. Cycle: does the system oscillate?
    if len(arr) > 20:
        fft = np.fft.rfft(arr - arr.mean())
        power = np.abs(fft)**2
        if power.sum() > 0:
            dominant = power[1:].max() / power.sum()
            motifs['cycle'] = float(dominant)
    
    return motifs

# ============================================================
# MAIN EXPERIMENT
# ============================================================

def run_emergence_first(n_worlds=50, n_steps=200, seed=42):
    """
    Run emergence-first experiment.
    
    1. Generate worlds with no motif vocabulary
    2. Observe transitions
    3. Post-hoc: which motifs appear?
    """
    rng = np.random.default_rng(seed)
    
    all_results = []
    
    for world_id in range(n_worlds):
        print(f"  World {world_id+1}/{n_worlds}...", end='', flush=True)
        
        # Generate world
        world = generate_world(world_id, rng)
        
        # Run
        history_raw = []
        transitions = []
        
        for t in range(n_steps):
            world = step_world(world, t, rng)
            raw = measure_raw(history_raw, world)
            history_raw.append(raw)
            
            # Detect transitions in raw observables
            for key in ['mean_state', 'std_state', 'mean_corr', 'entropy']:
                t_list = detect_transition(history_raw, key)
                transitions.extend(t_list)
        
        # Post-hoc motif detection
        motifs = detect_motifs_posthoc(history_raw, world)
        
        # Store results
        all_results.append({
            'id': world_id,
            'N': int(world['N']),
            'D': int(world['D']),
            'coupling': float(world['coupling']),
            'decay': float(world['decay']),
            'nonlinearity': float(world['nonlinearity']),
            'transitions': transitions,
            'motifs': motifs,
            'final_state': {
                'mean': float(np.mean(world['states'])),
                'std': float(np.std(world['states'])),
            }
        })
        
        print(f" ({len(transitions)} transitions, {len(motifs)} motifs)")
    
    return all_results

def analyze_emergence_first(results):
    """
    Analyze emergence-first results.
    
    Key question: do the same motifs appear near transitions?
    """
    print("\n" + "="*70)
    print("EMERGENCE-FIRST ANALYSIS")
    print("="*70)
    
    # 1. How many worlds have transitions?
    worlds_with_transitions = sum(1 for r in results if len(r['transitions']) > 0)
    print(f"\nWorlds with transitions: {worlds_with_transitions}/{len(results)}")
    
    # 2. Which motifs appear?
    motif_counts = defaultdict(int)
    for r in results:
        for m in r['motifs']:
            motif_counts[m] += 1
    
    print("\nMotif frequency (post-hoc detection):")
    for m, count in sorted(motif_counts.items(), key=lambda x: -x[1]):
        print(f"  {m}: {count}/{len(results)} ({100*count/len(results):.0f}%)")
    
    # 3. Do motifs correlate with transitions?
    print("\nMotif-transcript correlation:")
    for m in sorted(motif_counts.keys()):
        with_transitions = sum(1 for r in results if m in r['motifs'] and len(r['transitions']) > 0)
        without_transitions = sum(1 for r in results if m in r['motifs'] and len(r['transitions']) == 0)
        total = motif_counts[m]
        
        if total > 0:
            pct = with_transitions / total * 100
            print(f"  {m}: {with_transitions}/{total} have transitions ({pct:.0f}%)")
    
    # 4. World parameters that predict transitions
    print("\nWorld parameters:")
    coupling_with = [r['coupling'] for r in results if len(r['transitions']) > 0]
    coupling_without = [r['coupling'] for r in results if len(r['transitions']) == 0]
    
    if coupling_with and coupling_without:
        print(f"  Coupling: with transitions={np.mean(coupling_with):.3f}, without={np.mean(coupling_without):.3f}")
    
    nonlin_with = [r['nonlinearity'] for r in results if len(r['transitions']) > 0]
    nonlin_without = [r['nonlinearity'] for r in results if len(r['transitions']) == 0]
    
    if nonlin_with and nonlin_without:
        print(f"  Nonlinearity: with transitions={np.mean(nonlin_with):.3f}, without={np.mean(nonlin_without):.3f}")
    
    # 5. Motif co-occurrence
    print("\nMotif co-occurrence (if both present in same world):")
    motif_pairs = defaultdict(int)
    for r in results:
        ms = list(r['motifs'].keys())
        for i in range(len(ms)):
            for j in range(i+1, len(ms)):
                motif_pairs[(ms[i], ms[j])] += 1
    
    for (m1, m2), count in sorted(motif_pairs.items(), key=lambda x: -x[1])[:10]:
        print(f"  {m1} + {m2}: {count}")
    
    return {
        'worlds_with_transitions': worlds_with_transitions,
        'motif_counts': dict(motif_counts),
        'motif_pairs': {str(k): v for k, v in motif_pairs.items()},
    }

# ============================================================
# RUN
# ============================================================

if __name__ == '__main__':
    import sys
    
    n_worlds = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    n_steps = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    
    print(f"RD-10B.3: Emergence-First Worlds")
    print(f"  Worlds: {n_worlds}, Steps: {n_steps}")
    print(f"  Standing rule: patterns may belong to world, representation, detector, or question")
    print()
    
    results = run_emergence_first(n_worlds=n_worlds, n_steps=n_steps)
    analysis = analyze_emergence_first(results)
    
    # Save
    with open('/home/student/sgp_core_v2/audits/rd10b3_results.json', 'w') as f:
        json.dump({'results': results, 'analysis': analysis}, f, indent=2)
    
    print("\nSaved to audits/rd10b3_results.json")
