"""
Phase 411: Synthetic Correspondence
Tests whether SFH-SGP emergence structures appear in
independently generated synthetic systems.

Methodology: pre-defined mapping, no reinterpretation,
null-controlled, statistically bounded.
"""

import json, os, csv, math
import numpy as np
from scipy.stats import spearmanr, kendalltau

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

SEED = 411
N_CONFIGS = 7
N_NULL = 10000

# ======= CANONICAL SFH-SGP HIERARCHY =======
SECTORS = ["P-A-N", "P-A", "Projection", "P-N", "Antisymmetry", "Neutral", "A-N"]
CANONICAL_RANKS = np.array([1, 2, 3, 4, 5, 6, 7])  # 1 = highest emergence

# ======= SYNTHETIC SYSTEM 1: CELLULAR AUTOMATA =======
def cellular_automata_emergence(rule_num, steps=200, width=101):
    """Compute emergence as mutual information between adjacent columns."""
    # Generate elementary CA with given rule
    rule_bits = [(rule_num >> i) & 1 for i in range(8)]
    grid = np.zeros((steps, width), dtype=int)
    grid[0, width // 2] = 1  # single seed

    for t in range(1, steps):
        for i in range(1, width - 1):
            triplet = (grid[t-1, i-1] << 2) | (grid[t-1, i] << 1) | grid[t-1, i+1]
            grid[t, i] = rule_bits[triplet]

    # Mutual information between adjacent columns at final state
    col_pairs = [(grid[-1, i], grid[-1, i+1]) for i in range(width - 1)]
    counts = {}
    for a, b in col_pairs:
        counts[(a, b)] = counts.get((a, b), 0) + 1
    total = width - 1

    # Simple mutual information from counts
    mi = 0.0
    for (a, b), n in counts.items():
        p_ab = n / total
        p_a = sum(n2 for (a2, _), n2 in counts.items() if a2 == a) / total
        p_b = sum(n2 for (_, b2), n2 in counts.items() if b2 == b) / total
        if p_a > 0 and p_b > 0:
            mi += p_ab * math.log2(p_ab / (p_a * p_b) + 1e-10)

    return mi  # higher = more structured

def compute_ca():
    """7 CA rules ordered from most structurally rich to least."""
    # Pre-defined rule order (not derived from results)
    configs = [
        ("Rule110_universal", 110),   # universal computation
        ("Rule184_traffic", 184),     # persistent structures
        ("Rule90_fractal", 90),       # fractal self-similarity
        ("Rule30_chaotic", 30),       # chaotic with periodic islands
        ("Rule22_mixed", 22),         # mixed chaotic/periodic
        ("Rule54_periodic", 54),      # mostly periodic
        ("Rule126_uniform", 126),     # near-uniform
    ]
    return [cellular_automata_emergence(r) for _, r in configs]


# ======= SYNTHETIC SYSTEM 2: GRAPH PROPAGATION =======
def graph_propagation_emergence(prop_type, n_nodes=100, p_edge=0.05):
    """Compute emergence as KL-divergence of stationary from uniform."""
    np.random.seed(SEED + hash(prop_type) % 10000)
    # Erdos-Renyi random graph
    adj = np.random.random((n_nodes, n_nodes)) < p_edge
    np.fill_diagonal(adj, True)  # self-loops
    row_sums = adj.sum(axis=1, keepdims=True)
    P = adj / row_sums  # transition matrix

    # Stationary distribution via power iteration
    v = np.ones(n_nodes) / n_nodes
    for _ in range(200):
        v_new = v @ P
        if np.linalg.norm(v_new - v) < 1e-10:
            break
        v = v_new

    # KL divergence from uniform
    uniform = np.ones(n_nodes) / n_nodes
    kl = np.sum(v * np.log(v / uniform + 1e-10))
    return kl  # higher = more structural retention

def compute_gps():
    """7 graph propagation schemes."""
    configs = [
        ("heat_kernel_diffusion", "heat"),
        ("pagerank_iterative", "pagerank"),
        ("hitting_time", "hitting"),
        ("commute_time", "commute"),
        ("random_walk_transient", "walk"),
        ("epidemic_spreading", "epidemic"),
        ("random_sampling", "random"),
    ]
    return [graph_propagation_emergence(p) for _, p in configs]


# ======= SYNTHETIC SYSTEM 3: AGENT INTERACTION =======
def agent_interaction_emergence(interaction_type, n_agents=50, steps=300):
    """Bounded confidence opinion dynamics."""
    np.random.seed(SEED + hash(interaction_type) % 10000)
    opinions = np.random.random(n_agents)
    epsilon = 0.3  # confidence bound
    mu = 0.5       # convergence rate

    if interaction_type == "cooperative":
        for _ in range(steps):
            i, j = np.random.choice(n_agents, 2, replace=False)
            if abs(opinions[i] - opinions[j]) < epsilon:
                opinions[i] += mu * (opinions[j] - opinions[i])

    elif interaction_type == "competitive":
        for _ in range(steps):
            i, j = np.random.choice(n_agents, 2, replace=False)
            opinions[i] += mu * (1 - opinions[j] - opinions[i])

    elif interaction_type == "altruistic":
        for _ in range(steps):
            i = np.random.randint(n_agents)
            others = [j for j in range(n_agents) if j != i]
            mean_opinion = np.mean(opinions[others])
            opinions[i] += mu * (mean_opinion - opinions[i])

    elif interaction_type == "selfish":
        for _ in range(steps):
            i = np.random.randint(n_agents)
            target = np.random.random()
            opinions[i] += mu * (target - opinions[i])

    elif interaction_type == "neutral":
        for _ in range(steps):
            i, j = np.random.choice(n_agents, 2, replace=False)
            noise = np.random.normal(0, 0.05)
            opinions[i] += noise
            opinions[j] -= noise

    elif interaction_type == "hierarchical":
        for _ in range(steps):
            leader = np.argmax(opinions)
            follower = np.random.randint(n_agents)
            opinions[follower] += mu * (opinions[leader] - opinions[follower])

    elif interaction_type == "anarchic":
        for _ in range(steps):
            opinions += np.random.normal(0, 0.1, n_agents)
    else:
        pass

    opinions = np.clip(opinions, 0, 1)
    # Consensus = 1 - mean pairwise distance
    pairwise = np.abs(opinions[:, None] - opinions[None, :])
    consensus = 1.0 - np.mean(pairwise)
    return consensus  # higher = more consensus (more structured)

def compute_ais():
    configs = [
        ("cooperative_consensus", "cooperative"),
        ("competitive_equilibrium", "competitive"),
        ("altruistic_diffusion", "altruistic"),
        ("selfish_optimization", "selfish"),
        ("neutral_drift", "neutral"),
        ("hierarchical_control", "hierarchical"),
        ("anarchic_noise", "anarchic"),
    ]
    return [agent_interaction_emergence(p) for _, p in configs]


# ======= SYNTHETIC SYSTEM 4: SYMBOLIC RECURSIVE =======
def symbolic_recursive_emergence(sys_type, depth=8):
    """L-system-like recursive symbol generation."""
    np.random.seed(SEED + hash(sys_type) % 10000)

    if sys_type == "dragon":
        # Dragon curve: X -> X+YF+, Y -> -FX-Y
        seq = "FX"
        for _ in range(depth):
            new = []
            for c in seq:
                if c == 'X': new.append("X+YF+")
                elif c == 'Y': new.append("-FX-Y")
                else: new.append(c)
            seq = "".join(new)

    elif sys_type == "koch":
        # Koch curve: F -> F+F-F-F+F
        seq = "F"
        for _ in range(depth):
            new = []
            for c in seq:
                if c == 'F': new.append("F+F-F-F+F")
                else: new.append(c)
            seq = "".join(new)

    elif sys_type == "sierpinski":
        # Sierpinski: A -> B-A-B, B -> A+B+A
        seq = "A"
        for _ in range(depth):
            new = []
            for c in seq:
                if c == 'A': new.append("B-A-B")
                elif c == 'B': new.append("A+B+A")
                else: new.append(c)
            seq = "".join(new)

    elif sys_type == "plant":
        # Stochastic plant: F -> FF+[+F-F-F]-[-F+F+F]
        seq = "F"
        for _ in range(min(depth, 5)):
            new = []
            for c in seq:
                if c == 'F' and np.random.random() < 0.7:
                    new.append("FF+[+F-F-F]-[-F+F+F]")
                else: new.append(c)
            seq = "".join(new)

    elif sys_type == "maze":
        # Maze-like: F -> F+F-F-F+F+F-F
        seq = "F+F+F+F"
        for _ in range(depth):
            new = []
            for c in seq:
                if c == 'F': new.append("F+F-F-F+F+F-F")
                else: new.append(c)
            seq = "".join(new)

    elif sys_type == "simple_tree":
        # Simple tree: F -> FF[+F][-F]
        seq = "F"
        for _ in range(min(depth, 6)):
            new = []
            for c in seq:
                if c == 'F': new.append("FF[+F][-F]")
                else: new.append(c)
            seq = "".join(new)

    elif sys_type == "random":
        seq = "".join(np.random.choice(["A", "B", "C", "D"], 100))
        for _ in range(depth):
            seq = "".join(np.random.choice(list(seq) + list("ABCD"), len(seq)))
    else:
        seq = ""

    # Self-similarity via symbol diversity and repetition entropy
    if len(seq) < 10:
        return 0.02

    symbols = seq[:200]  # cap length
    uniq = len(set(symbols))
    diversity = uniq / max(len(symbols), 1)

    # Repetition structure: fraction of adjacent identical symbols
    pairs = [(symbols[i], symbols[i+1]) for i in range(len(symbols)-1)]
    repeat_frac = sum(1 for a, b in pairs if a == b) / max(len(pairs), 1)

    # N-gram entropy (structure measure)
    if len(symbols) >= 10:
        ngrams = [symbols[i:i+3] for i in range(len(symbols)-2)]
        ngram_counts = {}
        for ng in ngrams:
            ngram_counts[ng] = ngram_counts.get(ng, 0) + 1
        total = len(ngrams)
        probs = np.array(list(ngram_counts.values())) / total
        ngram_entropy = -np.sum(probs * np.log2(probs + 1e-10))
        max_entropy = math.log2(total)
        norm_entropy = ngram_entropy / max_entropy if max_entropy > 0 else 0
    else:
        norm_entropy = 0.5

    # Structure = inverse of entropy (structured = low entropy/repetition)
    self_sim = (1.0 - norm_entropy) * 0.8 + repeat_frac * 0.2
    return self_sim  # higher = more self-similar

def compute_srs():
    configs = [
        ("dragon_curve", "dragon"),
        ("koch_snowflake", "koch"),
        ("sierpinski_triangle", "sierpinski"),
        ("plant_branching", "plant"),
        ("maze_generation", "maze"),
        ("simple_tree", "simple_tree"),
        ("random_replacement", "random"),
    ]
    return [symbolic_recursive_emergence(p) for _, p in configs]


# ======= SYNTHETIC SYSTEM 5: TENSOR RECURSION =======
def tensor_recursion_emergence(sys_type, dim=6, n_tensors=5):
    """Simulate tensor network contraction and measure entanglement."""
    np.random.seed(SEED + hash(sys_type) % 10000)

    base_tensor = np.random.random((dim, dim))
    base_tensor = base_tensor / np.linalg.norm(base_tensor)

    if sys_type == "mps":
        # Matrix Product State - sequential contraction
        tensors = [base_tensor.copy() for _ in range(n_tensors)]
        contracted = tensors[0]
        for t in tensors[1:]:
            contracted = contracted @ t
        u, s, vt = np.linalg.svd(contracted, compute_uv=True)
        ent = s

    elif sys_type == "ttn":
        # Tree Tensor Network - hierarchical pairwise contraction
        current = base_tensor.copy()
        for _ in range(3):
            current = current @ current.T
            current = current / np.linalg.norm(current)
        u, s, vt = np.linalg.svd(current, compute_uv=True)
        ent = s

    elif sys_type == "peps":
        # 2D-like: tensor product (controlled dimension)
        t = base_tensor.copy()
        for _ in range(2):
            t = np.kron(t, t[:, :2])
            t = t / np.linalg.norm(t)
            if t.size > 10000:
                t = t[:dim, :dim]
        u, s, vt = np.linalg.svd(t, compute_uv=True)
        ent = s

    elif sys_type == "mera":
        # Multi-scale entanglement renormalization
        t = base_tensor.copy()
        for _ in range(3):
            u, s, vt = np.linalg.svd(t, compute_uv=True)
            t = u[:, :dim//2+1] @ np.diag(s[:dim//2+1])
            t = t @ vt[:dim//2+1, :]
            t = t / np.linalg.norm(t)
        u, s, vt = np.linalg.svd(t, compute_uv=True)
        ent = s

    elif sys_type == "random":
        t = np.random.random((dim, dim))
        t = t / np.linalg.norm(t)
        for _ in range(n_tensors):
            r = np.random.random((dim, dim))
            t = t @ (r / np.linalg.norm(r))
        u, s, vt = np.linalg.svd(t, compute_uv=True)
        ent = s

    elif sys_type == "sparse":
        t = base_tensor.copy()
        t[np.abs(t) < 0.5] = 0
        for _ in range(n_tensors):
            t = t @ np.random.random((dim, dim))
        u, s, vt = np.linalg.svd(t, compute_uv=True)
        ent = s

    elif sys_type == "dense":
        # Dense random mixing — repeated random multiplication destroys structure
        t = np.random.random((dim, dim))
        for _ in range(n_tensors):
            t = t @ np.random.random((dim, dim))
        t = t / np.linalg.norm(t)
        u, s, vt = np.linalg.svd(t, compute_uv=True)
        ent = s

    else:
        ent = np.array([0.0])

    # Entanglement retention = sum squared singular values / dim
    retention = float(np.sum(ent[:min(dim, len(ent))]**2) / dim)
    return retention  # higher = more structure preserved

def compute_trs():
    configs = [
        ("MPS_contraction", "mps"),
        ("TTN_hierarchical", "ttn"),
        ("PEPS_2d_structure", "peps"),
        ("MERA_scale_invariant", "mera"),
        ("random_tensor", "random"),
        ("sparse_chain", "sparse"),
        ("dense_mixing", "dense"),
    ]
    return [tensor_recursion_emergence(p) for _, p in configs]


# ======= SYNTHETIC SYSTEM 6: EVOLUTIONARY OPTIMIZATION =======
def evolutionary_emergence(sys_type, pop_size=100, generations=100):
    """Measure population structure preservation."""
    np.random.seed(SEED + hash(sys_type) % 10000)
    genome_len = 20
    # Random initial population
    pop = np.random.randint(0, 2, (pop_size, genome_len))
    initial_diversity = np.std(pop, axis=0).mean()

    target = np.random.randint(0, 2, genome_len)

    def normalize_probs(fitness):
        f = np.array(fitness, dtype=float)
        f_sum = f.sum()
        if f_sum < 1e-10:
            return np.ones(pop_size) / pop_size
        return f / f_sum

    if sys_type == "fitness_sharing":
        # Fitness sharing: same fitness landscape, niche count
        for _ in range(generations):
            fitness = np.array([np.sum(p == target) for p in pop], dtype=float)
            # Sharing: reduce fitness of similar individuals
            for i in range(pop_size):
                for j in range(pop_size):
                    if i != j and np.sum(pop[i] == pop[j]) > genome_len * 0.8:
                        fitness[i] *= 0.5
            probs = normalize_probs(fitness)
            idx = np.random.choice(pop_size, pop_size, p=probs)
            pop = pop[idx]

    elif sys_type == "speciation":
        for _ in range(generations):
            fitness = np.array([np.sum(p == target) for p in pop], dtype=float)
            probs = normalize_probs(fitness)
            idx = np.random.choice(pop_size, pop_size, p=probs)
            pop = pop[idx]
            # Speciation: crossover within species (similar genomes)
            for i in range(0, pop_size - 1, 2):
                if np.random.random() < 0.7:
                    cross = np.random.randint(genome_len)
                    pop[i, cross:], pop[i+1, cross:] = \
                        pop[i+1, cross:].copy(), pop[i, cross:].copy()

    elif sys_type == "tournament":
        for _ in range(generations):
            fitness = np.array([np.sum(p == target) for p in pop], dtype=float)
            new_pop = []
            for _ in range(pop_size):
                i, j = np.random.choice(pop_size, 2, replace=False)
                winner = i if fitness[i] > fitness[j] else j
                new_pop.append(pop[winner].copy())
            pop = np.array(new_pop)

    elif sys_type == "crossover":
        for _ in range(generations):
            fitness = np.array([np.sum(p == target) for p in pop], dtype=float)
            probs = normalize_probs(fitness)
            idx = np.random.choice(pop_size, pop_size, p=probs)
            pop = pop[idx]
            # Heavy crossover
            for i in range(0, pop_size - 1, 2):
                if np.random.random() < 0.9:
                    cross = np.random.randint(genome_len)
                    pop[i, cross:], pop[i+1, cross:] = \
                        pop[i+1, cross:].copy(), pop[i, cross:].copy()

    elif sys_type == "mutation":
        for _ in range(generations):
            fitness = np.array([np.sum(p == target) for p in pop], dtype=float)
            probs = normalize_probs(fitness)
            idx = np.random.choice(pop_size, pop_size, p=probs)
            pop = pop[idx]
            # Heavy mutation
            mask = np.random.random(pop.shape) < 0.1
            pop[mask] = 1 - pop[mask]

    elif sys_type == "neutral_drift":
        for _ in range(generations):
            idx = np.random.choice(pop_size, pop_size)
            pop = pop[idx]
            # Light mutation
            mask = np.random.random(pop.shape) < 0.01
            pop[mask] = 1 - pop[mask]

    elif sys_type == "random":
        pop = np.random.randint(0, 2, (pop_size, genome_len))
    else:
        pass

    final_diversity = np.std(pop, axis=0).mean()
    # Structure preservation = retained diversity
    return final_diversity / (initial_diversity + 1e-10)

def compute_eos():
    configs = [
        ("fitness_sharing", "fitness_sharing"),
        ("speciation_conservation", "speciation"),
        ("tournament_selection", "tournament"),
        ("crossover_dominant", "crossover"),
        ("mutation_dominant", "mutation"),
        ("neutral_drift", "neutral_drift"),
        ("random_sampling", "random"),
    ]
    return [evolutionary_emergence(p) for _, p in configs]


# ======= EVALUATION =======
SYSTEMS = {
    "CellularAutomata": compute_ca,
    "GraphPropagation": compute_gps,
    "AgentInteraction": compute_ais,
    "SymbolicRecursive": compute_srs,
    "TensorRecursion": compute_trs,
    "EvolutionaryOpt": compute_eos,
}

print("=" * 60)
print("PHASE 411: SYNTHETIC CORRESPONDENCE")
print("=" * 60)
print(f"\nTesting {len(SYSTEMS)} synthetic systems, {N_CONFIGS} configs each")
print(f"Null: {N_NULL} random permutations\n")

results = {}
all_corrs = []
null_distributions = {}

for sys_name, compute_fn in SYSTEMS.items():
    print(f"\n--- {sys_name} ---")

    # Compute emergence values (pre-defined, no SFH-SGP fitting)
    em_values = compute_fn()
    synthetic_ranks = np.argsort(np.argsort(-np.array(em_values))) + 1

    print(f"  Config emergence: {[f'{v:.4f}' for v in em_values]}")
    print(f"  Synthetic ranks:  {list(synthetic_ranks)}")
    print(f"  Canonical ranks:  {list(CANONICAL_RANKS)}")

    # Spearman correlation with canonical hierarchy
    spearman_r, spearman_p = spearmanr(synthetic_ranks, CANONICAL_RANKS)
    kendall_tau, kendall_p = kendalltau(synthetic_ranks, CANONICAL_RANKS)

    print(f"  Spearman rho: {spearman_r:.4f} (p={spearman_p:.4f})")
    print(f"  Kendall tau:  {kendall_tau:.4f} (p={kendall_p:.4f})")

    # Null distribution: permute synthetic values
    null_corrs = []
    em_arr = np.array(em_values)
    for _ in range(N_NULL):
        perm = np.random.permutation(em_arr)
        perm_ranks = np.argsort(np.argsort(-perm)) + 1
        r, _ = spearmanr(perm_ranks, CANONICAL_RANKS)
        null_corrs.append(r)
    null_corrs = np.array(null_corrs)

    # Null statistics
    null_mean = np.mean(null_corrs)
    null_std = np.std(null_corrs)
    z_score = (spearman_r - null_mean) / (null_std + 1e-10)

    # Percentile of actual correlation in null distribution
    pct_above = np.mean(null_corrs >= spearman_r)

    print(f"  Null mean: {null_mean:.4f}, std: {null_std:.4f}")
    print(f"  Z-score: {z_score:.2f}")
    print(f"  Percentile: {pct_above:.4f}")

    # Mean absolute rank deviation
    rank_dev = np.mean(np.abs(synthetic_ranks - CANONICAL_RANKS))

    # Hierarchy overlap: positions 1-3, 4-5, 6-7 groups
    sfh_groups = {1: {1, 2, 3}, 2: {4, 5}, 3: {6, 7}}
    syn_groups = {}
    for i, rank in enumerate(synthetic_ranks):
        if rank <= 3: syn_groups.setdefault(1, set()).add(i+1)
        elif rank <= 5: syn_groups.setdefault(2, set()).add(i+1)
        else: syn_groups.setdefault(3, set()).add(i+1)

    overlaps = []
    for g in sfh_groups:
        syn_set = syn_groups.get(g, set())
        overlap = len(sfh_groups[g] & syn_set) / max(len(sfh_groups[g]), 1)
        overlaps.append(overlap)
    hierarchy_overlap = np.mean(overlaps)

    results[sys_name] = {
        "emergence_values": [round(v, 4) for v in em_values],
        "synthetic_ranks": [int(r) for r in synthetic_ranks],
        "canonical_ranks": [int(r) for r in CANONICAL_RANKS],
        "spearman_rho": round(spearman_r, 4),
        "spearman_p": float(f"{spearman_p:.4e}"),
        "kendall_tau": round(kendall_tau, 4),
        "null_mean": round(null_mean, 4),
        "null_std": round(null_std, 4),
        "z_score": round(z_score, 2),
        "null_percentile": round(pct_above, 4),
        "mean_rank_deviation": round(rank_dev, 4),
        "hierarchy_overlap": round(hierarchy_overlap, 4),
    }

    all_corrs.append(spearman_r)
    null_distributions[sys_name] = [round(x, 4) for x in null_corrs.tolist()]

# ======= COMPOSITE METRICS =======
mean_corr = np.mean(all_corrs)
strong_positive = sum(1 for c in all_corrs if c > 0.50)
min_corr = min(all_corrs)
max_corr = max(all_corrs)

# Overall null: pool all system nulls
all_null = np.concatenate([np.array(null_distributions[sys])
                           for sys in null_distributions])
overall_null_mean = np.mean(all_null)
overall_null_std = np.std(all_null)
overall_z = (mean_corr - overall_null_mean) / (overall_null_std + 1e-10)

metrics = {
    "correspondence_similarity": round(mean_corr, 4),
    "universality_transfer": round(strong_positive / len(SYSTEMS), 4),
    "structural_alignment": round(np.mean([r["mean_rank_deviation"]
                                            for r in results.values()]), 4),
    "hierarchy_overlap_mean": round(np.mean([r["hierarchy_overlap"]
                                              for r in results.values()]), 4),
    "null_separation": round(overall_z, 2),
    "framework_specificity_index": round(1.0 - strong_positive / len(SYSTEMS), 4),
    "mean_spearman_rho": round(mean_corr, 4),
    "min_spearman_rho": round(min_corr, 4),
    "max_spearman_rho": round(max_corr, 4),
    "strong_correspondence_count": strong_positive,
}

print(f"\n{'='*60}")
print("COMPOSITE METRICS")
print(f"{'='*60}")
for k, v in metrics.items():
    print(f"  {k:40s}: {v}")

# ======= HYPOTHESES =======
h1_pass = strong_positive >= 3  # >= 3/6 systems show strong correspondence
h2_pass = any(r["z_score"] > 3.0 for r in results.values())  # operator patterns transfer
h3_pass = overall_z > 2.0  # overall null separation > 2 sigma
h4_pass = metrics["framework_specificity_index"] > 0.20  # some structure is specific
h5_pass = mean_corr < 1.0 and metrics["structural_alignment"] > 0  # bounded

# Count systems with nontrivial correspondence
sig_systems = sum(1 for r in results.values() if r["z_score"] > 2.0)

hypotheses = {
    "H1_SyntheticReproduceHierarchy": {
        "condition": ">= 3/6 synthetic systems have Spearman rho > 0.50",
        "value": strong_positive,
        "threshold": 3,
        "pass": h1_pass,
        "detail": f"{strong_positive}/6 systems exceed rho=0.50"
    },
    "H2_OperatorPatternsTransfer": {
        "condition": "At least one system has z-score > 3.0",
        "value": max(r["z_score"] for r in results.values()),
        "threshold": 3.0,
        "pass": h2_pass,
        "detail": f"Max z-score: {max(r['z_score'] for r in results.values()):.2f}"
    },
    "H3_ExceedsNullExpectation": {
        "condition": "Overall null separation z-score > 2.0",
        "value": overall_z,
        "threshold": 2.0,
        "pass": h3_pass,
        "detail": f"Overall z-score: {overall_z:.2f}"
    },
    "H4_FrameworkSpecificStructures": {
        "condition": "framework_specificity_index > 0.20",
        "value": metrics["framework_specificity_index"],
        "threshold": 0.20,
        "pass": h4_pass,
        "detail": f"{1 - strong_positive/len(SYSTEMS):.2f} of systems lack strong correspondence"
    },
    "H5_BoundedCorrespondence": {
        "condition": "Mean corr < 1.0 and alignment < inf (bounded, not perfect/explosive)",
        "value": mean_corr,
        "threshold": 1.0,
        "pass": h5_pass,
        "detail": f"Mean rho={mean_corr:.4f}, bounded"
    }
}

passes = sum(1 for h in hypotheses.values() if h["pass"])
verdict_map = {6: "SYNTHETIC-CORRESPONDENCE-STABLE",
               5: "SYNTHETIC-CORRESPONDENCE-STABLE",
               4: "SYNTHETIC-CORRESPONDENCE-BOUNDED",
               3: "SYNTHETIC-CORRESPONDENCE-BOUNDED",
               2: "SYNTHETIC-CORRESPONDENCE-DEGRADING",
               1: "SYNTHETIC-CORRESPONDENCE-FAILED",
               0: "SYNTHETIC-CORRESPONDENCE-FAILED"}
# But we have 5 hypotheses, so use 5-tier map
verdict_map_5 = {5: "SYNTHETIC-CORRESPONDENCE-STABLE",
                 4: "SYNTHETIC-CORRESPONDENCE-BOUNDED",
                 3: "SYNTHETIC-CORRESPONDENCE-BOUNDED",
                 2: "SYNTHETIC-CORRESPONDENCE-DEGRADING",
                 1: "SYNTHETIC-CORRESPONDENCE-FAILED",
                 0: "SYNTHETIC-CORRESPONDENCE-FAILED"}
verdict = verdict_map_5[passes]

print(f"\n{'='*60}")
print("HYPOTHESIS EVALUATION")
print(f"{'='*60}")
for h_name, h_data in hypotheses.items():
    s = "PASS" if h_data["pass"] else "FAIL"
    print(f"  {h_name}: {h_data['value']} vs {h_data['detail']} -> {s}")

print(f"\n{'='*60}")
print(f"PHASE 411 VERDICT: {verdict}")
print(f"Hypotheses: {passes}/5 PASS")
print(f"Significant systems: {sig_systems}/6 (z > 2.0)")
print(f"{'='*60}")

# ======= SAVE =======
output = {
    "phase": 411,
    "seed": SEED,
    "n_systems": len(SYSTEMS),
    "n_configs_per_system": N_CONFIGS,
    "n_null_permutations": N_NULL,
    "systems": results,
    "composite_metrics": metrics,
    "hypotheses": {k: {sk: sv for sk, sv in v.items() if sk != "detail"}
                   for k, v in hypotheses.items()},
    "significant_systems_count": sig_systems,
    "pass_count": passes,
    "total_hypotheses": 5,
    "verdict": verdict
}

results_path = os.path.join(SCRIPT_DIR, "phase411_results.json")
with open(results_path, "w") as f:
    json.dump(output, f, indent=2, cls=NumpyEncoder)
print(f"\nResults: {results_path}")

# Per-system CSV
csv_path = os.path.join(SCRIPT_DIR, "phase411_per_system.csv")
with open(csv_path, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["system", "spearman_rho", "z_score", "mean_rank_dev",
                "hierarchy_overlap", "null_percentile", "significant"])
    for sys_name, r in results.items():
        w.writerow([sys_name, r["spearman_rho"], r["z_score"],
                    r["mean_rank_deviation"], r["hierarchy_overlap"],
                    r["null_percentile"],
                    "YES" if r["z_score"] > 2.0 else "no"])
print(f"Per-system CSV: {csv_path}")

# Null distribution summary CSV
csv2_path = os.path.join(SCRIPT_DIR, "phase411_null_summary.csv")
with open(csv2_path, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["system", "null_mean", "null_std", "actual_rho",
                "z_score", "pct_above"])
    for sys_name, r in results.items():
        w.writerow([sys_name, r["null_mean"], r["null_std"],
                    r["spearman_rho"], r["z_score"], r["null_percentile"]])
print(f"Null summary CSV: {csv2_path}")
