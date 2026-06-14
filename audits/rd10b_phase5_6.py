"""RD-10B Phase 5-6: Invariant vs Attractor, Cross-Domain Transfer

Standing Rules:
  - Whenever something looks fundamental, ask what makes it possible.
  - Whenever something looks recurrent, ask whether it is causal.
  - Whenever something looks like a deeper invariant, ask whether it might be an attractor instead.
"""

import numpy as np
import json
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent


# ─────────────────────────────────────────────────────────
# Cross-Domain Generators
# ─────────────────────────────────────────────────────────

def gen_granular(n_components=12, n_timepoints=800, seed=42):
    """Granular system: particles with soft-sphere interactions."""
    rng = np.random.default_rng(seed)
    X = rng.normal(0, 1, (n_components, n_timepoints))

    # Simple granular dynamics: particles interact with neighbors
    for t in range(1, n_timepoints):
        for i in range(n_components):
            # Neighbor interaction (ring)
            left = (i - 1) % n_components
            right = (i + 1) % n_components
            neighbor_force = 0.3 * (X[left, t-1] + X[right, t-1] - 2 * X[i, t-1])
            X[i, t] = 0.7 * X[i, t-1] + neighbor_force + rng.normal(0, 0.2)
    return X


def gen_reaction_diffusion(n_components=12, n_timepoints=800, seed=42):
    """Reaction-diffusion system."""
    rng = np.random.default_rng(seed)
    X = rng.normal(0, 1, (n_components, n_timepoints))

    for t in range(1, n_timepoints):
        for i in range(n_components):
            # Diffusion
            left = (i - 1) % n_components
            right = (i + 1) % n_components
            diffusion = 0.1 * (X[left, t-1] + X[right, t-1] - 2 * X[i, t-1])
            # Reaction (nonlinear)
            reaction = 0.3 * X[i, t-1] - 0.1 * X[i, t-1]**3
            X[i, t] = X[i, t-1] + diffusion + reaction + rng.normal(0, 0.1)
    return X


def gen_graph_rewriting(n_components=12, n_timepoints=800, seed=42):
    """Graph rewriting system."""
    rng = np.random.default_rng(seed)
    X = rng.normal(0, 1, (n_components, n_timepoints))

    # Dynamic adjacency
    adj = np.zeros((n_components, n_components))
    for i in range(n_components):
        for j in range(i+1, n_components):
            if rng.random() < 0.3:
                adj[i, j] = adj[j, i] = 1

    for t in range(1, n_timepoints):
        # Rewire
        if t % 10 == 0:
            i, j = rng.choice(n_components, 2, replace=False)
            adj[i, j] = adj[j, i] = 1 - adj[i, j]

        for i in range(n_components):
            neighbors = np.where(adj[i] > 0)[0]
            if len(neighbors) > 0:
                neighbor_signal = np.mean(X[neighbors, t-1])
                X[i, t] = 0.5 * X[i, t-1] + 0.3 * neighbor_signal + rng.normal(0, 0.2)
            else:
                X[i, t] = 0.5 * X[i, t-1] + rng.normal(0, 0.3)
    return X


def gen_cellular_automaton(n_components=12, n_timepoints=800, seed=42):
    """Cellular automaton (rule 30-like)."""
    rng = np.random.default_rng(seed)
    X = np.zeros((n_components, n_timepoints))
    X[:, 0] = rng.choice([-1, 1], n_components)

    for t in range(1, n_timepoints):
        for i in range(n_components):
            left = (i - 1) % n_components
            right = (i + 1) % n_components
            # Rule 30-like
            pattern = (X[left, t-1] > 0) * 4 + (X[i, t-1] > 0) * 2 + (X[right, t-1] > 0)
            X[i, t] = 1 if pattern in [1, 2, 4, 7] else -1
            X[i, t] += rng.normal(0, 0.05)  # Add noise
    return X


def gen_ecosystem(n_components=12, n_timepoints=800, seed=42):
    """Ecosystem dynamics (predator-prey like)."""
    rng = np.random.default_rng(seed)
    X = rng.uniform(0.1, 1, (n_components, n_timepoints))

    for t in range(1, n_timepoints):
        for i in range(n_components):
            # Lotka-Volterra-like
            prey = X[i, t-1]
            predator_idx = (i + 1) % n_components
            predator = X[predator_idx, t-1]

            growth = 0.5 * prey * (1 - prey)
            predation = 0.3 * prey * predator
            X[i, t] = prey + growth - predation + rng.normal(0, 0.05)
            X[i, t] = max(0.01, X[i, t])  # Clamp
    return X


CROSS_DOMAIN_GENERATORS = {
    "granular": gen_granular,
    "reaction_diffusion": gen_reaction_diffusion,
    "graph_rewriting": gen_graph_rewriting,
    "cellular_automaton": gen_cellular_automaton,
    "ecosystem": gen_ecosystem,
}


# ─────────────────────────────────────────────────────────
# Original Architecture Generators
# ─────────────────────────────────────────────────────────

def gen_binding(n_components=12, n_timepoints=800, seed=42):
    """Discrete states via potential wells."""
    rng = np.random.default_rng(seed)
    n_wells = 3
    well_centers = rng.uniform(-2, 2, n_wells)
    well_width = 0.3
    barrier_height = 2.0
    X = np.zeros((n_components, n_timepoints))
    state = rng.integers(0, n_wells, n_components)
    for t in range(n_timepoints):
        for i in range(n_components):
            if rng.random() < 0.01:
                delta = rng.choice([-1, 1])
                new_state = (state[i] + delta) % n_wells
                if rng.random() < np.exp(-barrier_height):
                    state[i] = new_state
            X[i, t] = well_centers[state[i]] + rng.normal(0, well_width)
    return X


def gen_network(n_components=12, n_timepoints=800, seed=42):
    """Connected modules via ring network."""
    rng = np.random.default_rng(seed)
    adjacency = np.zeros((n_components, n_components))
    for i in range(n_components):
        for j in range(i+1, n_components):
            dist = min(abs(i-j), n_components - abs(i-j))
            if dist <= 2:
                adjacency[i, j] = adjacency[j, i] = 1.0 / dist
    X = rng.normal(0, 1, (n_components, n_timepoints))
    for t in range(1, n_timepoints):
        for i in range(n_components):
            neighbors = np.where(adjacency[i] > 0)[0]
            neighbor_signal = np.sum(adjacency[i, neighbors] * X[neighbors, t-1])
            X[i, t] = 0.5 * X[i, t-1] + 0.3 * neighbor_signal + rng.normal(0, 0.2)
    return X


def gen_cycle(n_components=12, n_timepoints=800, seed=42):
    """Self-reinforcing directed cycle."""
    rng = np.random.default_rng(seed)
    X = rng.normal(0, 1, (n_components, n_timepoints))
    for t in range(1, n_timepoints):
        for i in range(n_components):
            prev = (i - 1) % n_components
            X[i, t] = 0.6 * X[i, t-1] + 0.4 * X[prev, t-1] + rng.normal(0, 0.15)
    return X


def gen_template(n_components=12, n_timepoints=800, seed=42):
    """Information transfer via copying."""
    rng = np.random.default_rng(seed)
    n_templates = n_components // 2
    X = rng.normal(0, 1, (n_components, n_timepoints))
    for i in range(n_templates):
        for t in range(1, n_timepoints):
            X[i, t] = 0.7 * X[i, t-1] + rng.normal(0, 0.3)
    for i in range(n_templates, n_components):
        template_idx = i - n_templates
        for t in range(1, n_timepoints):
            X[i, t] = 0.8 * X[template_idx, t-1] + rng.normal(0, 0.1)
    return X


def gen_boundary(n_components=12, n_timepoints=800, seed=42):
    """Protected interior via membrane."""
    rng = np.random.default_rng(seed)
    n_inside = n_components // 2
    X = rng.normal(0, 1, (n_components, n_timepoints))
    for t in range(1, n_timepoints):
        for i in range(n_inside):
            inside_signal = np.mean(X[:n_inside, t-1])
            X[i, t] = 0.3 * X[i, t-1] + 0.5 * inside_signal + rng.normal(0, 0.1)
        for i in range(n_inside, n_components):
            inside_signal = np.mean(X[:n_inside, t-1])
            X[i, t] = 0.5 * X[i, t-1] + 0.1 * inside_signal + rng.normal(0, 0.3)
    return X


def gen_hierarchy(n_components=12, n_timepoints=800, seed=42):
    """Nested coordination via hierarchy."""
    rng = np.random.default_rng(seed)
    n_micro, n_meso, n_macro = 4, 4, 4
    X = rng.normal(0, 1, (n_components, n_timepoints))
    for t in range(1, n_timepoints):
        for i in range(n_components - n_macro, n_components):
            X[i, t] = 0.7 * X[i, t-1] + rng.normal(0, 0.2)
        macro_signal = np.mean(X[n_components - n_macro:, t-1])
        for i in range(n_micro, n_micro + n_meso):
            X[i, t] = 0.5 * X[i, t-1] + 0.3 * macro_signal + rng.normal(0, 0.15)
        meso_signal = np.mean(X[n_micro:n_micro + n_meso, t-1])
        for i in range(n_micro):
            X[i, t] = 0.4 * X[i, t-1] + 0.4 * meso_signal + rng.normal(0, 0.1)
    return X


def gen_recursion(n_components=12, n_timepoints=800, seed=42):
    """Self-referential representation."""
    rng = np.random.default_rng(seed)
    n_base = n_components // 3
    n_meta = n_components // 3
    X = rng.normal(0, 1, (n_components, n_timepoints))
    for t in range(1, n_timepoints):
        for i in range(n_base):
            X[i, t] = 0.5 * X[i, t-1] + rng.normal(0, 0.3)
        base_signal = np.mean(X[:n_base, t-1])
        for i in range(n_base, n_base + n_meta):
            X[i, t] = 0.6 * X[i, t-1] + 0.3 * base_signal + rng.normal(0, 0.15)
        meta_signal = np.mean(X[n_base:n_base + n_meta, t-1])
        for i in range(n_base + n_meta, n_components):
            X[i, t] = 0.7 * X[i, t-1] + 0.2 * meta_signal + rng.normal(0, 0.1)
    return X


def gen_formal_inference(n_components=12, n_timepoints=800, seed=42):
    """Derivation from axioms."""
    rng = np.random.default_rng(seed)
    n_axioms = 3
    X = rng.normal(0, 1, (n_components, n_timepoints))
    for i in range(n_axioms):
        for t in range(1, n_timepoints):
            X[i, t] = 0.9 * X[i, t-1] + rng.normal(0, 0.1)
    for i in range(n_axioms, n_components):
        for t in range(1, n_timepoints):
            rule_type = (i - n_axioms) % 3
            if rule_type == 0:
                X[i, t] = 0.5 * (X[0, t-1] + X[1, t-1]) + rng.normal(0, 0.05)
            elif rule_type == 1:
                X[i, t] = X[0, t-1] * X[1, t-1] + rng.normal(0, 0.05)
            else:
                X[i, t] = X[2, t-1] + 0.3 * X[i, t-1] + rng.normal(0, 0.05)
    return X


# ─────────────────────────────────────────────────────────
# Detection Functions
# ─────────────────────────────────────────────────────────

def detect_binding(X):
    n_comp, n_time = X.shape
    quantized = np.zeros_like(X)
    for i in range(n_comp):
        quantized[i] = np.digitize(X[i], np.percentile(X[i], [25, 50, 75]))
    within_vars = []
    for q in range(4):
        mask = quantized[0] == q
        if np.sum(mask) > 5:
            within_vars.append(np.var(X[0, mask]))
    between_var = np.var([np.mean(X[0, quantized[0] == q]) for q in range(4) if np.sum(quantized[0] == q) > 0])
    within_var = np.mean(within_vars) if within_vars else 1.0
    ratio = between_var / (within_var + 1e-10)
    return {"binding_ratio": float(ratio), "present": ratio > 0.5}


def detect_network(X):
    corr = np.corrcoef(X)
    n = corr.shape[0]
    half = n // 2
    within = np.mean(corr[:half, :half]) + np.mean(corr[half:, half:])
    between = np.mean(corr[:half, half:])
    modularity = (within - between) / 2
    return {"modularity": float(modularity), "present": modularity > 0.1}


def detect_cycle(X):
    n_comp, n_time = X.shape
    autocorrs = []
    for i in range(n_comp):
        ac = np.corrcoef(X[i, :-1], X[i, 1:])[0, 1]
        autocorrs.append(ac)
    mean_ac = np.mean(autocorrs)
    return {"mean_autocorrelation": float(mean_ac), "present": mean_ac > 0.6}


def detect_template(X):
    n_comp, n_time = X.shape
    n_templates = n_comp // 2
    copy_corrs = []
    for i in range(n_templates, n_comp):
        template_idx = i - n_templates
        corr = np.corrcoef(X[template_idx], X[i])[0, 1]
        copy_corrs.append(corr)
    mean_copy_corr = np.mean(copy_corrs)
    return {"mean_copy_correlation": float(mean_copy_corr), "present": mean_copy_corr > 0.5}


def detect_boundary(X):
    n_comp, n_time = X.shape
    n_inside = n_comp // 2
    internal_corr = np.mean(np.corrcoef(X[:n_inside])[:n_inside, :n_inside])
    cross_corr = np.mean(np.corrcoef(X[:n_inside, :], X[n_inside:])[:n_inside, n_comp-n_inside:])
    ratio = internal_corr / (cross_corr + 1e-10)
    return {"boundary_ratio": float(ratio), "present": ratio > 1.5}


def detect_hierarchy(X):
    n_comp, n_time = X.shape
    scales = [1, 5, 20]
    scale_corrs = []
    for s in scales:
        X_ds = X[:, ::s] if s > 1 else X
        corr = np.corrcoef(X_ds)
        half = n_comp // 2
        within = np.mean(corr[:half, :half])
        scale_corrs.append(within)
    hierarchy_score = scale_corrs[-1] - scale_corrs[0]
    return {"hierarchy_score": float(hierarchy_score), "present": hierarchy_score > 0.1}


def detect_recursion(X):
    n_comp, n_time = X.shape
    n_base = n_comp // 3
    n_meta = n_comp // 3
    base_meta_corr = np.mean(np.corrcoef(X[:n_base], X[n_base:n_base+n_meta])[:n_base, n_base:n_base+n_meta])
    meta_meta_corr = np.mean(np.corrcoef(X[n_base:n_base+n_meta], X[n_base+n_meta:])[:n_meta, :n_comp-n_base-n_meta])
    recursion_score = (base_meta_corr + meta_meta_corr) / 2
    return {"recursion_score": float(recursion_score), "present": recursion_score > 0.3}


def detect_formal_inference(X):
    n_comp, n_time = X.shape
    n_axioms = 3
    r2_scores = []
    for i in range(n_axioms, n_comp):
        A = X[:n_axioms, :-1].T
        y = X[i, 1:]
        try:
            coeffs = np.linalg.lstsq(A, y, rcond=None)[0]
            predicted = A @ coeffs
            ss_res = np.sum((y - predicted) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r2 = 1 - ss_res / (ss_tot + 1e-10)
            r2_scores.append(r2)
        except:
            r2_scores.append(0)
    mean_r2 = np.mean(r2_scores)
    return {"inference_r2": float(mean_r2), "present": mean_r2 > 0.5}


DETECTORS = {
    "binding": detect_binding,
    "network": detect_network,
    "cycle": detect_cycle,
    "template": detect_template,
    "boundary": detect_boundary,
    "hierarchy": detect_hierarchy,
    "recursion": detect_recursion,
    "formal_inference": detect_formal_inference,
}


def compute_d_persist(X):
    n_comp, n_time = X.shape
    persistences = []
    for i in range(n_comp):
        ac = np.corrcoef(X[i, :-1], X[i, 1:])[0, 1]
        persistences.append(max(0, ac))
    return float(np.mean(persistences))


# ─────────────────────────────────────────────────────────
# Phase 5: Invariant vs Attractor Analysis
# ─────────────────────────────────────────────────────────

def run_invariant_attractor():
    """Test whether recurrence is explained by invariants or attractors."""
    # For each motif, test if it arises from multiple independent pathways
    results = {}

    # Original generators (defined inline)
    def gen_b(seed): return gen_binding(seed=seed)
    def gen_n(seed): return gen_network(seed=seed)
    def gen_c(seed): return gen_cycle(seed=seed)
    def gen_t(seed): return gen_template(seed=seed)
    def gen_bo(seed): return gen_boundary(seed=seed)
    def gen_h(seed): return gen_hierarchy(seed=seed)
    def gen_r(seed): return gen_recursion(seed=seed)
    def gen_f(seed): return gen_formal_inference(seed=seed)

    original_generators = {
        "binding": gen_b,
        "network": gen_n,
        "cycle": gen_c,
        "template": gen_t,
        "boundary": gen_bo,
        "hierarchy": gen_h,
        "recursion": gen_r,
        "formal_inference": gen_f,
    }

    for motif_name in DETECTORS:
        # Test with different seeds
        pathway_results = []
        for seed in [42, 123, 456, 789, 101]:
            X = original_generators[motif_name](seed)
            det = DETECTORS[motif_name](X)
            pathway_results.append(det.get("present", False))

        # Test with cross-domain generators
        cross_domain_results = []
        for domain_name, gen_func in CROSS_DOMAIN_GENERATORS.items():
            X = gen_func(seed=42)
            det = DETECTORS[motif_name](X)
            cross_domain_results.append(det.get("present", False))

        results[motif_name] = {
            "pathway_consistency": np.mean(pathway_results),
            "cross_domain_presence": np.mean(cross_domain_results),
            "n_pathways": len(pathway_results),
            "n_domains": len(cross_domain_results),
        }

    return results


# ─────────────────────────────────────────────────────────
# Phase 6: Cross-Domain Transfer
# ─────────────────────────────────────────────────────────

def run_cross_domain():
    """Test if motifs transfer across domains."""
    results = {}

    for domain_name, gen_func in CROSS_DOMAIN_GENERATORS.items():
        print(f"  {domain_name}...")
        X = gen_func(seed=42)
        detections = {}
        for motif_name, detect_func in DETECTORS.items():
            det = detect_func(X)
            detections[motif_name] = det

        present = [m for m, d in detections.items() if d.get("present", False)]
        d_persist = compute_d_persist(X)

        results[domain_name] = {
            "present": present,
            "d_persist": d_persist,
            "detections": {m: {"present": d["present"]} for m, d in detections.items()},
        }

    return results


# ─────────────────────────────────────────────────────────
# Main Execution
# ─────────────────────────────────────────────────────────

def gen_formal_inference(n_components=12, n_timepoints=800, seed=42):
    """Derivation from axioms."""
    rng = np.random.default_rng(seed)
    n_axioms = 3
    X = rng.normal(0, 1, (n_components, n_timepoints))
    for i in range(n_axioms):
        for t in range(1, n_timepoints):
            X[i, t] = 0.9 * X[i, t-1] + rng.normal(0, 0.1)
    for i in range(n_axioms, n_components):
        for t in range(1, n_timepoints):
            rule_type = (i - n_axioms) % 3
            if rule_type == 0:
                X[i, t] = 0.5 * (X[0, t-1] + X[1, t-1]) + rng.normal(0, 0.05)
            elif rule_type == 1:
                X[i, t] = X[0, t-1] * X[1, t-1] + rng.normal(0, 0.05)
            else:
                X[i, t] = X[2, t-1] + 0.3 * X[i, t-1] + rng.normal(0, 0.05)
    return X


if __name__ == "__main__":
    print("=" * 60)
    print("RD-10B Phase 5-6: Invariant vs Attractor, Cross-Domain")
    print("=" * 60)

    # Phase 5: Invariant vs Attractor
    print("\nPhase 5: Invariant vs Attractor Analysis")
    invariant_attractor = run_invariant_attractor()

    # Phase 6: Cross-Domain Transfer
    print("\nPhase 6: Cross-Domain Transfer")
    cross_domain = run_cross_domain()

    # Save results
    output = {
        "invariant_attractor": invariant_attractor,
        "cross_domain": {k: {"present": v["present"], "d_persist": v["d_persist"]} for k, v in cross_domain.items()},
    }

    with open(OUT_DIR / "rd10b_phase5_6_results.json", "w") as f:
        json.dump(output, f, indent=2, default=str)

    # Print summary
    print("\n" + "=" * 60)
    print("INVARIANT vs ATTRACTOR SUMMARY")
    print("=" * 60)
    for motif, data in invariant_attractor.items():
        print(f"  {motif}:")
        print(f"    Pathway consistency: {data['pathway_consistency']:.2f}")
        print(f"    Cross-domain presence: {data['cross_domain_presence']:.2f}")

    print("\n" + "=" * 60)
    print("CROSS-DOMAIN TRANSFER SUMMARY")
    print("=" * 60)
    for domain, data in cross_domain.items():
        print(f"  {domain}: {data['present']} (D_persist={data['d_persist']:.3f})")

    print(f"\nResults saved to {OUT_DIR / 'rd10b_phase5_6_results.json'}")
