#!/usr/bin/env python3
"""
T090: Substrate Independence Audit
===================================
Objective: Determine whether the 9 substrate assumptions are:
1. Markov artifacts (specific to this simulator)
2. Generic dynamical-system properties (appear across substrates)
3. True substrate primitives (persist across radically different implementations)

Substrates:
  1. Markov chain (baseline, from T082)
  2. Cellular automaton (1D elementary CA)
  3. Random Boolean network (RBN)
  4. Coupled map lattice (CML)

For each:
  - Generate N random configurations
  - Measure all 9 assumptions (adapted to the substrate)
  - Compute prevalence and compare cross-substrate

Decision rule:
  - Appears everywhere (>= 80% in all substrates) → candidate primitive
  - Appears only in Markov → simulator artifact
  - Appears in some but not others → implementation-dependent
"""

import csv, json, math, random
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np

OUT = Path("/home/student/sgp_core_v2/sfh_sgp_ood_outputs")
random.seed(42)
np.random.seed(42)

N_PER_SUBSTRATE = 500
RUN_STEPS = 200

ASS_IDS = ["OC2", "OC1", "CD1", "IC1", "IS1", "IS2", "CD2", "EC1", "SR1"]

# ============================================================
# GENERIC ASSUMPTION MEASUREMENTS (substrate-independent)
# ============================================================

def compute_assumptions(history, n_actual, T_matrix, params):
    """
    Compute all 9 assumptions from substrate-agnostic data.
    
    Args:
        history: list of state IDs (integers) over time
        n_actual: total number of distinct states ever visited
        T_matrix: list-of-lists or dict, T[i] = list of possible next states from state i
        params: dict with substrate-specific parameters
    """
    em = {}
    n = len(history) if history else 0
    
    # --- helpers ---
    def _unique_ratio():
        return len(set(history)) / max(1, n_actual)
    
    def _entropy():
        if n < 2:
            return 0.0
        counts = Counter(history)
        ent = 0.0
        for c in counts.values():
            p = c / n
            if p > 0:
                ent -= p * math.log2(p)
        return ent / max(1, math.log2(len(counts)))
    
    def _self_correlation():
        if n < 4:
            return 0.0
        lag = min(3, n // 2)
        matches = sum(1 for i in range(n - lag) if history[i] == history[i + lag])
        return matches / max(1, n - lag)
    
    def _transition_diversity():
        if n < 2:
            return 0.0
        trans = list(zip(history[:-1], history[1:]))
        return len(set(trans)) / max(1, len(trans))
    
    def _convergence():
        cycle = _cycle_length()
        return 1.0 if cycle <= 1 else (1.0 / cycle if cycle > 0 else 0)
    
    def _cycle_length():
        if n < 4:
            return max(1, len(set(history)))
        recent = history[-20:]
        seen = {}
        for i, s in enumerate(recent):
            if s in seen:
                return i - seen[s]
            seen[s] = i
        return max(1, len(set(history)))
    
    def _detect_cycle():
        if n < 6:
            return False
        recent = history[-6:]
        return len(recent) == 6 and len(set(recent)) <= 3
    
    # Compute metrics from history
    metrics = {}
    metrics["unique_ratio"] = _unique_ratio()
    metrics["entropy"] = _entropy()
    metrics["self_correlation"] = _self_correlation()
    metrics["transition_diversity"] = _transition_diversity()
    metrics["convergence"] = _convergence()
    metrics["cycle_length"] = _cycle_length()
    
    # Map T_matrix to transition map
    trans_map = {}
    if T_matrix is not None:
        for i in range(len(T_matrix)):
            next_states = [j for j, p in enumerate(T_matrix[i]) if p > 0.01]
            if next_states:
                trans_map[i] = next_states
    
    # Count state expansions
    state_expansions = max(0, n_actual - params.get("base_n_states", n_actual))
    
    # --- OC2: Distinguishability ---
    # Unique transition sets / n_states
    if n_actual >= 2 and trans_map:
        trans_sets = [set(trans_map.get(s, [])) for s in trans_map]
        unique_trans_types = len(set(tuple(sorted(t)) for t in trans_sets))
        em["OC2"] = min(1.0, unique_trans_types / max(1, len(trans_map)))
    else:
        em["OC2"] = 0.0
    
    # --- OC1: Boundedness ---
    if n >= 10:
        recent = history[-20:]
        recurrence = len(set(recent)) / max(1, len(recent))
        em["OC1"] = 1.0 - recurrence
    else:
        em["OC1"] = 0.0
    
    # --- CD1: Causal Relations ---
    if n >= 5:
        trans = list(zip(history[:-1], history[1:]))
        state_outcomes = defaultdict(list)
        for s, ns in trans:
            state_outcomes[s].append(ns)
        consistency = 0.0
        for s, outs in state_outcomes.items():
            if len(outs) >= 2:
                most_common = Counter(outs).most_common(1)[0][1]
                consistency += most_common / len(outs)
        consistency /= max(1, len(state_outcomes))
        # Determinism from params or estimate from consistency
        determinism = params.get("determinism", consistency)
        em["CD1"] = determinism * 0.4 + consistency * 0.6
    else:
        em["CD1"] = 0.0
    
    # --- IC1: Extractable Information ---
    if n_actual >= 2 and trans_map:
        future_div = 0.0
        for s, outcomes in trans_map.items():
            future_div += len(outcomes) / max(1, n_actual)
        future_div /= max(1, len(trans_map))
        em["IC1"] = min(1.0, future_div * 1.5)
    else:
        em["IC1"] = 0.0
    
    # --- IS1: Phase Structure ---
    if n >= 10:
        blocks = [history[i:i+5] for i in range(0, n - 4, 5)]
        if len(blocks) >= 2:
            changes = sum(1 for i in range(1, len(blocks)) if set(blocks[i]) != set(blocks[i-1]))
            em["IS1"] = min(1.0, changes / max(1, len(blocks) - 1))
        else:
            em["IS1"] = 0.0
    else:
        em["IS1"] = 0.0
    
    # --- IS2: Coincidence ---
    if n >= 5:
        recent = history[-10:]
        if len(set(recent)) <= 2:
            em["IS2"] = 1.0
        else:
            em["IS2"] = min(0.5, 5.0 / len(set(recent)))
    else:
        em["IS2"] = 0.0
    
    # --- CD2: Self-Constraint ---
    # Uses self_model parameters if available, else history-derived
    sm_level = params.get("self_model_level", 0)
    sm_influence = params.get("self_model_influence", 0.0)
    sc = metrics["self_correlation"]
    cycle_l = metrics["cycle_length"]
    score = (min(1.0, sm_level / 2) * 0.4 + sm_influence * 0.3 +
             min(1.0, sc * 1.5) * 0.15 +
             (1.0 if cycle_l > 2 else 0.0) * 0.15)
    em["CD2"] = min(1.0, score)
    
    # --- EC1: Environmental Coupling ---
    em["EC1"] = min(1.0, (sm_level / 3) * 0.5 + sm_influence * 0.3 + sc * 0.2)
    
    # --- SR1: Self-Reference ---
    if sm_level < 2:
        em["SR1"] = sm_level * 0.3
    else:
        em["SR1"] = min(1.0, (sm_level / 3) * 0.3 + sm_influence * 0.3 +
                        (1.0 if cycle_l > 1 else 0.0) * 0.2 + sc * 0.2)
    
    return em


# ============================================================
# SUBSTRATE 1: MARKOV CHAIN (baseline)
# ============================================================

def generate_markov_configs(n):
    """Generate n random Markov chain configurations."""
    configs = []
    for _ in range(n):
        configs.append({
            "base_n_states": random.choice([3, 4, 5, 6]),
            "determinism": random.uniform(0.2, 0.95),
            "connectivity": random.uniform(0.3, 0.9),
            "novelty_drive": random.uniform(0.1, 0.5),
            "boundary_strength": random.uniform(0.3, 0.9),
            "self_model_level": random.choice([0, 1, 2, 3]),
            "self_model_influence": random.uniform(0.0, 0.6),
        })
    return configs


def run_markov(params):
    """Run a Markov chain, return history, n_actual, T_matrix, params."""
    # Same logic as T082's GeneratedSystem
    base_n = params.get("base_n_states", 4)
    determinism = params.get("determinism", 0.7)
    connectivity = params.get("connectivity", 0.5)
    novelty_drive = params.get("novelty_drive", 0.3)
    boundary_strength = params.get("boundary_strength", 0.7)
    self_model_level = params.get("self_model_level", 0)
    sm_influence = params.get("self_model_influence", 0.0)
    
    n_actual = base_n
    T = np.zeros((base_n, base_n))
    mask = np.random.random((base_n, base_n)) < connectivity
    np.fill_diagonal(mask, True)
    raw = np.random.random((base_n, base_n)) * mask
    if determinism > 0.8:
        for i in range(base_n):
            if np.random.random() < determinism:
                raw[i] = 0
                raw[i, np.random.randint(base_n)] = 1
    row_sums = raw.sum(axis=1)
    row_sums[row_sums == 0] = 1
    T = raw / row_sums[:, np.newaxis]
    
    history = []
    visit_counts = Counter()
    current_n = base_n
    current_T = T.copy()
    
    for step in range(RUN_STEPS):
        if not history:
            history.append(0)
            visit_counts[0] += 1
            continue
        
        current = history[-1]
        
        # Self-model modulation
        if self_model_level > 0 and np.random.random() < sm_influence:
            if self_model_level == 1:
                recent = history[-min(3, len(history)):]
                if len(set(recent)) == 1:
                    current = random.choice(range(current_n))
            elif self_model_level == 2:
                if visit_counts[current] > max(current_n, 3):
                    candidates = [s for s in range(current_n) if visit_counts[s] < visit_counts[current]]
                    if candidates:
                        current = random.choice(candidates)
            elif self_model_level >= 3:
                if len(history) >= 6:
                    recent6 = history[-6:]
                    if len(recent6) == 6 and len(set(recent6)) <= 3:
                        candidates = [s for s in range(current_n) if visit_counts.get(s, 0) < 2]
                        if candidates:
                            current = random.choice(candidates)
        
        # Novelty drive
        if np.random.random() < novelty_drive:
            if boundary_strength <= 0.9 and np.random.random() < (1.0 - boundary_strength) * 0.3:
                new_id = current_n
                current_n += 1
                old_T = current_T
                new_T = np.zeros((current_n, current_n))
                new_T[:old_T.shape[0], :old_T.shape[0]] = old_T
                for i in range(current_n):
                    conn = np.random.random(current_n) < connectivity
                    conn[i] = True
                    raw2 = np.random.random(current_n) * conn
                    if raw2.sum() == 0:
                        raw2[i] = 1
                    new_T[i] = raw2 / raw2.sum()
                current_T = new_T
                visit_counts[new_id] = 0
                history.append(new_id)
                continue
        
        next_state = np.random.choice(current_n, p=current_T[current])
        history.append(next_state)
        visit_counts[next_state] += 1
    
    return history, current_n, current_T.tolist()


# ============================================================
# SUBSTRATE 2: CELLULAR AUTOMATON
# ============================================================

def generate_ca_configs(n):
    configs = []
    for _ in range(n):
        configs.append({
            "rule": random.randint(0, 255),
            "width": random.randint(10, 30),
            "initial_density": random.uniform(0.2, 0.8),
            "noise_rate": random.choice([0.0, 0.001, 0.005, 0.01, 0.05]),
        })
    return configs


def elementary_ca_step(grid, rule, width, noise_rate=0.0):
    """Apply elementary CA rule to 1D binary grid with periodic boundaries."""
    new_grid = [0] * width
    for i in range(width):
        left = grid[(i - 1) % width]
        center = grid[i]
        right = grid[(i + 1) % width]
        idx = (left << 2) | (center << 1) | right
        new_grid[i] = 1 if (rule >> idx) & 1 else 0
    if noise_rate > 0:
        for i in range(width):
            if np.random.random() < noise_rate:
                new_grid[i] = 1 - new_grid[i]
    return new_grid


def run_ca(params):
    width = params["width"]
    rule = params["rule"]
    initial_density = params["initial_density"]
    noise_rate = params.get("noise_rate", 0.0)
    
    # Initial state
    grid = [1 if np.random.random() < initial_density else 0 for _ in range(width)]
    
    # Run
    history_hashes = []
    all_grids = []
    
    for step in range(RUN_STEPS):
        grid_hash = hash(tuple(grid))
        history_hashes.append(grid_hash)
        all_grids.append(grid)
        grid = elementary_ca_step(grid, rule, width, noise_rate)
    
    # Build T_matrix from state transitions
    state_ids = list(set(history_hashes))
    id_map = {h: i for i, h in enumerate(state_ids)}
    history_ids = [id_map[h] for h in history_hashes]
    n_actual = len(state_ids)
    
    # Build transition matrix
    T_matrix = [[0.0] * n_actual for _ in range(n_actual)]
    for i in range(len(history_ids) - 1):
        s = history_ids[i]
        ns = history_ids[i + 1]
        T_matrix[s][ns] += 1.0
    for i in range(n_actual):
        row_sum = sum(T_matrix[i])
        if row_sum > 0:
            T_matrix[i] = [v / row_sum for v in T_matrix[i]]
        else:
            T_matrix[i][i] = 1.0
    
    return history_ids, n_actual, T_matrix


# ============================================================
# SUBSTRATE 3: RANDOM BOOLEAN NETWORK
# ============================================================

def generate_rbn_configs(n):
    configs = []
    for _ in range(n):
        configs.append({
            "n_nodes": random.randint(5, 15),
            "k": random.randint(1, 4),
            "p_bias": random.uniform(0.2, 0.8),
            "update_mode": random.choice(["sync", "async"]),
        })
    return configs


def run_rbn(params):
    n_nodes = params["n_nodes"]
    k = params["k"]
    p_bias = params["p_bias"]
    update_mode = params.get("update_mode", "sync")
    
    # Build network: each node gets k random inputs (can include self)
    connections = []
    for i in range(n_nodes):
        inputs = [random.randint(0, n_nodes - 1) for _ in range(k)]
        connections.append(inputs)
    
    # Build Boolean functions: for each node, a truth table for its k inputs
    functions = []
    for i in range(n_nodes):
        tt = [1 if np.random.random() < p_bias else 0 for _ in range(2**k)]
        functions.append(tt)
    
    # Initial state
    state = [random.randint(0, 1) for _ in range(n_nodes)]
    
    def state_hash(s):
        return sum(s[i] << i for i in range(n_nodes))
    
    history_ids = []
    state_to_id = {}
    id_counter = 0
    transitions = []  # list of (from_id, to_id)
    
    for step in range(RUN_STEPS):
        sid = state_hash(state)
        if sid not in state_to_id:
            state_to_id[sid] = id_counter
            id_counter += 1
        current_id = state_to_id[sid]
        history_ids.append(current_id)
        
        # Compute next state
        next_state = [0] * n_nodes
        if update_mode == "sync":
            for i in range(n_nodes):
                input_vals = [state[j] for j in connections[i]]
                idx = sum(input_vals[j] << (k - 1 - j) for j in range(k))
                next_state[i] = functions[i][idx]
        else:  # async: update one random node at a time
            order = list(range(n_nodes))
            random.shuffle(order)
            next_state = state.copy()
            for i in order:
                input_vals = [next_state[j] for j in connections[i]]
                idx = sum(input_vals[j] << (k - 1 - j) for j in range(k))
                next_state[i] = functions[i][idx]
        
        # Record transition
        nsid = state_hash(next_state)
        if nsid not in state_to_id:
            state_to_id[nsid] = id_counter
            id_counter += 1
        next_id = state_to_id[nsid]
        transitions.append((current_id, next_id))
        
        state = next_state
    
    n_actual = id_counter
    
    # Build T_matrix
    T_matrix = [[0.0] * n_actual for _ in range(n_actual)]
    for s, ns in transitions:
        T_matrix[s][ns] += 1.0
    for i in range(n_actual):
        row_sum = sum(T_matrix[i])
        if row_sum > 0:
            T_matrix[i] = [v / row_sum for v in T_matrix[i]]
        else:
            T_matrix[i][i] = 1.0
    
    return history_ids, n_actual, T_matrix


# ============================================================
# SUBSTRATE 4: COUPLED MAP LATTICE
# ============================================================

def generate_cml_configs(n):
    configs = []
    for _ in range(n):
        configs.append({
            "n_sites": random.randint(5, 20),
            "coupling": random.uniform(0.0, 1.0),
            "map_type": random.choice(["logistic", "tent", "sine"]),
            "noise_level": random.uniform(0.0, 0.05),
        })
    return configs


def local_map(x, map_type):
    if map_type == "logistic":
        r = 3.8  # chaotic regime
        return r * x * (1 - x)
    elif map_type == "tent":
        mu = 1.8
        return mu * min(x, 1 - x)
    elif map_type == "sine":
        return abs(math.sin(math.pi * x))
    return x


def run_cml(params):
    n_sites = params["n_sites"]
    coupling = params["coupling"]
    map_type = params["map_type"]
    noise_level = params.get("noise_level", 0.0)
    
    # Number of bins for discretization
    n_bins = 4
    
    # Initial state: random values in [0, 1]
    values = [np.random.random() for _ in range(n_sites)]
    
    def discretize(vals):
        """Convert continuous vector to a discrete state ID."""
        bin_indices = tuple(min(int(v * n_bins), n_bins - 1) for v in vals)
        hash_val = hash(bin_indices)
        return hash_val
    
    history_ids = []
    state_to_id = {}
    id_counter = 0
    transitions = []
    
    for step in range(RUN_STEPS):
        sid = discretize(values)
        if sid not in state_to_id:
            state_to_id[sid] = id_counter
            id_counter += 1
        current_id = state_to_id[sid]
        history_ids.append(current_id)
        
        # Diffusive coupling
        new_vals = [0.0] * n_sites
        for i in range(n_sites):
            left = values[(i - 1) % n_sites]
            right = values[(i + 1) % n_sites]
            coupled = (1 - coupling) * local_map(values[i], map_type) + \
                      coupling * 0.5 * (local_map(left, map_type) + local_map(right, map_type))
            if noise_level > 0:
                coupled += np.random.normal(0, noise_level)
            new_vals[i] = max(0.0, min(1.0, coupled))
        
        values = new_vals
        
        nsid = discretize(values)
        if nsid not in state_to_id:
            state_to_id[nsid] = id_counter
            id_counter += 1
        next_id = state_to_id[nsid]
        transitions.append((current_id, next_id))
    
    n_actual = id_counter
    
    T_matrix = [[0.0] * n_actual for _ in range(n_actual)]
    for s, ns in transitions:
        T_matrix[s][ns] += 1.0
    for i in range(n_actual):
        row_sum = sum(T_matrix[i])
        if row_sum > 0:
            T_matrix[i] = [v / row_sum for v in T_matrix[i]]
        else:
            T_matrix[i][i] = 1.0
    
    return history_ids, n_actual, T_matrix


# ============================================================
# SUBSTRATE RUNNER
# ============================================================

SUBSTRATES = {
    "Markov": {
        "generate": generate_markov_configs,
        "run": run_markov,
        "markov_like": True,
    },
    "Cellular Automaton": {
        "generate": generate_ca_configs,
        "run": run_ca,
        "markov_like": False,
    },
    "Boolean Network": {
        "generate": generate_rbn_configs,
        "run": run_rbn,
        "markov_like": False,
    },
    "Coupled Map Lattice": {
        "generate": generate_cml_configs,
        "run": run_cml,
        "markov_like": False,
    },
}


# ============================================================
# MAIN
# ============================================================

print("=" * 72)
print("T090: SUBSTRATE INDEPENDENCE AUDIT")
print("=" * 72)

all_results = {}  # substrate_name -> list of assumption dicts

for sub_name, sub_def in SUBSTRATES.items():
    print(f"\n{'─'*72}")
    print(f"Substrate: {sub_name}")
    print(f"{'─'*72}")
    
    configs = sub_def["generate"](N_PER_SUBSTRATE)
    results = []
    
    for i, params in enumerate(configs):
        try:
            history, n_actual, T_matrix = sub_def["run"](params)
            em = compute_assumptions(history, n_actual, T_matrix, params)
            results.append(em)
        except Exception as e:
            pass  # skip failed runs
    
    all_results[sub_name] = results
    print(f"  Generated {len(results)}/{N_PER_SUBSTRATE} valid runs")
    
    # Prevalence at >= 0.2
    print(f"\n  Prevalence (>= 0.2):")
    for aid in ASS_IDS:
        vals = [r[aid] for r in results]
        pct = np.mean([v >= 0.2 for v in vals]) * 100
        mean_v = np.mean(vals)
        print(f"    {aid:<6}: {pct:6.1f}%  (mean={mean_v:.3f})")

# ============================================================
# CROSS-SUBSTRATE COMPARISON
# ============================================================

print(f"\n{'='*72}")
print("CROSS-SUBSTRATE COMPARISON")
print("=" * 72)

# Build comparison table
print(f"\n{'Assumption':<8} ", end="")
for sub_name in SUBSTRATES:
    print(f"{sub_name[:12]:<12} ", end="")
print(f"{'Verdict':<20}")
print(f"{'─'* (8 + 14 * len(SUBSTRATES) + 20)}")

for aid in ASS_IDS:
    prevalences = {}
    print(f"{aid:<8} ", end="")
    for sub_name in SUBSTRATES:
        results = all_results[sub_name]
        vals = [r[aid] for r in results]
        pct = np.mean([v >= 0.2 for v in vals]) * 100
        prevalences[sub_name] = pct
        print(f"{pct:<12.1f} ", end="")
    
    # Determine verdict
    all_high = all(p >= 80 for p in prevalences.values())
    markov_only = prevalences.get("Markov", 0) >= 80 and \
                  all(p < 80 for n, p in prevalences.items() if n != "Markov")
    some_high = sum(1 for p in prevalences.values() if p >= 80)
    
    if all_high:
        verdict = "Candidate primitive"
    elif markov_only:
        verdict = "Markov artifact"
    elif some_high >= 2:
        verdict = "Implementation-dependent"
    else:
        verdict = "Substrate-specific"
    
    print(f"{verdict:<20}")

# ============================================================
# ENRICHMENT COMPARISON (Markov vs non-Markov)
# ============================================================

print(f"\n{'='*72}")
print("MEAN VALUES: Markov vs non-Markov substrates")
print("=" * 72)

print(f"\n{'Assumption':<8} {'Markov mean':<12} {'Non-Markov mean':<16} {'Ratio':<8} {'Artifact?':<12}")
print(f"{'─'*56}")

markov_results = all_results["Markov"]
non_markov_names = [n for n in SUBSTRATES if n != "Markov"]
non_markov_results = []
for nm in non_markov_names:
    non_markov_results.extend(all_results[nm])

for aid in ASS_IDS:
    m_vals = [r[aid] for r in markov_results]
    nm_vals = [r[aid] for r in non_markov_results]
    m_mean = np.mean(m_vals)
    nm_mean = np.mean(nm_vals)
    ratio = m_mean / nm_mean if nm_mean > 0 else float('inf')
    artifact = abs(m_mean - nm_mean) < 0.15
    print(f"{aid:<8} {m_mean:<12.3f} {nm_mean:<16.3f} {ratio:<8.3f} {'No' if not artifact else 'Yes':<12}")

# ============================================================
# CLASSIFICATION
# ============================================================

print(f"\n{'='*72}")
print("FINAL CLASSIFICATION")
print("=" * 72)

for aid in ASS_IDS:
    prevalences = {}
    for sub_name in SUBSTRATES:
        results = all_results[sub_name]
        vals = [r[aid] for r in results]
        pct = np.mean([v >= 0.2 for v in vals]) * 100
        mean_v = np.mean(vals)
        prevalences[sub_name] = {"pct_02": round(pct, 1), "mean": round(mean_v, 3)}
    
    all_high = all(p["pct_02"] >= 80 for p in prevalences.values())
    markov_pct = prevalences.get("Markov", {}).get("pct_02", 0)
    non_markov_high = sum(1 for n, p in prevalences.items() if n != "Markov" and p["pct_02"] >= 80)
    
    if all_high:
        verdict = "Primitive (appears everywhere)"
    elif markov_pct >= 80 and non_markov_high == 0:
        verdict = "Markov artifact"
    elif non_markov_high >= 1:
        verdict = f"Implementation-dependent (in {1+non_markov_high}/{len(SUBSTRATES)} substrates)"
    else:
        verdict = "Substrate-specific"
    
    print(f"\n  {aid}:")
    for sub_name in SUBSTRATES:
        p = prevalences[sub_name]
        print(f"    {sub_name:<20}: >=0.2={p['pct_02']:6.1f}%, mean={p['mean']:.3f}")
    print(f"    >>> {verdict}")

# ============================================================
# SPECIFIC: TARGET THE 6 HIGH-PREVALENCE ASSUMPTIONS
# ============================================================

print(f"\n{'='*72}")
print("SPECIFIC: THE 6 TARGET ASSUMPTIONS FROM T089")
print("=" * 72)

target_6 = ["OC2", "OC1", "CD1", "IC1", "IS1", "IS2"]
print(f"\n{'Assumption':<8} ", end="")
for sub_name in SUBSTRATES:
    print(f"{sub_name[:12]:<12} ", end="")
print(f"{'Verdict':<20}")
print(f"{'─'* (8 + 14 * len(SUBSTRATES) + 20)}")

for aid in target_6:
    print(f"{aid:<8} ", end="")
    all_high = True
    for sub_name in SUBSTRATES:
        results = all_results[sub_name]
        vals = [r[aid] for r in results]
        pct = np.mean([v >= 0.2 for v in vals]) * 100
        print(f"{pct:<12.1f} ", end="")
        if pct < 80:
            all_high = False
    
    if all_high:
        verdict = "Generic dynamical property"
    else:
        verdict = "Substrate-dependent"
    print(f"{verdict:<20}")


# ============================================================
# DETAILED PER-SUBSTRATE STATS
# ============================================================

print(f"\n{'='*72}")
print("DETAILED PER-SUBSTRATE (>= 0.5 threshold)")
print("=" * 72)

for sub_name, results in all_results.items():
    print(f"\n  {sub_name}:")
    print(f"  {'Assumption':<8} {'%>=0.5':<8} {'mean':<8} {'std':<8}")
    print(f"  {'─'*32}")
    for aid in ASS_IDS:
        vals = [r[aid] for r in results]
        pct_05 = np.mean([v >= 0.5 for v in vals]) * 100
        print(f"  {aid:<8} {pct_05:<8.1f} {np.mean(vals):<8.3f} {np.std(vals):<8.3f}")


# ============================================================
# WRITE OUTPUTS
# ============================================================

# Per-substrate prevalence
with open(OUT / "t090_prevalence.csv", "w", newline="") as f:
    w = csv.writer(f)
    header = ["substrate", "n", "threshold"] + ASS_IDS
    w.writerow(header)
    for sub_name, results in all_results.items():
        for thresh in [0.2, 0.5]:
            row = [sub_name, len(results), thresh]
            for aid in ASS_IDS:
                vals = [r[aid] for r in results]
                pct = np.mean([v >= thresh for v in vals]) * 100
                row.append(round(pct, 1))
            w.writerow(row)

# Per-substrate means
with open(OUT / "t090_means.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["substrate", "n"] + ASS_IDS)
    for sub_name, results in all_results.items():
        row = [sub_name, len(results)]
        for aid in ASS_IDS:
            vals = [r[aid] for r in results]
            row.append(round(np.mean(vals), 3))
        w.writerow(row)

# Summary JSON
summary = {
    "audit": "T090 — Substrate Independence Audit",
    "objective": "Determine whether 9 substrate assumptions are Markov artifacts, generic dynamical properties, or true primitives",
    "n_per_substrate": N_PER_SUBSTRATE,
    "n_actual": {name: len(r) for name, r in all_results.items()},
    "substrates": list(SUBSTRATES.keys()),
    "verdicts": {},
}

# Prevalence data
for sub_name, results in all_results.items():
    for thresh_key, thresh in [("at_02", 0.2), ("at_05", 0.5)]:
        key = f"{sub_name}_{thresh_key}"
        summary[key] = {}
        for aid in ASS_IDS:
            vals = [r[aid] for r in results]
            pct = np.mean([v >= thresh for v in vals]) * 100
            summary[key][aid] = round(pct, 1)

for aid in ASS_IDS:
    verdicts_02 = {}
    all_high = True
    for sub_name in SUBSTRATES:
        results = all_results[sub_name]
        vals = [r[aid] for r in results]
        pct = np.mean([v >= 0.2 for v in vals]) * 100
        verdicts_02[sub_name] = round(pct, 1)
        if pct < 80:
            all_high = False
    
    markov_pct = verdicts_02.get("Markov", 0)
    non_markov_high = sum(1 for n, p in verdicts_02.items() if n != "Markov" and p >= 80)
    
    if all_high:
        verdict = "primitive"
    elif markov_pct >= 80 and non_markov_high == 0:
        verdict = "markov_artifact"
    elif non_markov_high >= 1:
        verdict = "implementation_dependent"
    else:
        verdict = "substrate_specific"
    
    summary["verdicts"][aid] = {
        "prevalence_by_substrate_02": verdicts_02,
        "verdict": verdict,
    }

with open(OUT / "t090_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print(f"\nWrote t090_prevalence.csv")
print(f"Wrote t090_means.csv")
print(f"Wrote t090_summary.json")
print(f"\nT090 complete.")
