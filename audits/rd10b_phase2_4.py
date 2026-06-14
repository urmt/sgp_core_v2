"""RD-10B Phase 2-4: Pattern Discovery, Null Models, Causal Testing

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
# Toy Universe Generators (improved)
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


GENERATORS = {
    "binding": gen_binding,
    "network": gen_network,
    "cycle": gen_cycle,
    "template": gen_template,
    "boundary": gen_boundary,
    "hierarchy": gen_hierarchy,
    "recursion": gen_recursion,
    "formal_inference": gen_formal_inference,
}


# ─────────────────────────────────────────────────────────
# Null Models
# ─────────────────────────────────────────────────────────

def gen_random(n_components=12, n_timepoints=800, seed=42):
    """Random noise. No structure."""
    rng = np.random.default_rng(seed)
    return rng.normal(0, 1, (n_components, n_timepoints))


def gen_shuffled(X):
    """Shuffle each component independently."""
    X_shuffled = X.copy()
    for i in range(X.shape[0]):
        rng = np.random.default_rng(42 + i)
        rng.shuffle(X_shuffled[i])
    return X_shuffled


def gen_degenerate_binding(n_components=12, n_timepoints=800, seed=42):
    """Binding without energy barriers (continuous)."""
    rng = np.random.default_rng(seed)
    n_wells = 3
    well_centers = rng.uniform(-2, 2, n_wells)
    well_width = 0.3

    X = np.zeros((n_components, n_timepoints))
    for t in range(n_timepoints):
        for i in range(n_components):
            # Continuous transitions (no barrier)
            state = rng.integers(0, n_wells)
            X[i, t] = well_centers[state] + rng.normal(0, well_width)
    return X


def gen_degenerate_boundary(n_components=12, n_timepoints=800, seed=42):
    """Boundary without membrane (no inside/outside distinction)."""
    rng = np.random.default_rng(seed)
    X = rng.normal(0, 1, (n_components, n_timepoints))
    for t in range(1, n_timepoints):
        # All components coupled equally (no boundary)
        global_signal = np.mean(X[:, t-1])
        for i in range(n_components):
            X[i, t] = 0.5 * X[i, t-1] + 0.3 * global_signal + rng.normal(0, 0.2)
    return X


def gen_degenerate_hierarchy(n_components=12, n_timepoints=800, seed=42):
    """Hierarchy without nested control (flat structure)."""
    rng = np.random.default_rng(seed)
    X = rng.normal(0, 1, (n_components, n_timepoints))
    for t in range(1, n_timepoints):
        # All components at same level (flat)
        global_signal = np.mean(X[:, t-1])
        for i in range(n_components):
            X[i, t] = 0.5 * X[i, t-1] + 0.3 * global_signal + rng.normal(0, 0.2)
    return X


# ─────────────────────────────────────────────────────────
# Detection Functions
# ─────────────────────────────────────────────────────────

def detect_binding(X):
    """Discrete states via potential wells."""
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
    """Connected modules via cross-correlation structure."""
    corr = np.corrcoef(X)
    n = corr.shape[0]
    half = n // 2
    within = np.mean(corr[:half, :half]) + np.mean(corr[half:, half:])
    between = np.mean(corr[:half, half:])
    modularity = (within - between) / 2
    return {"modularity": float(modularity), "present": modularity > 0.1}


def detect_cycle(X):
    """Self-reinforcing loops via lagged autocorrelation."""
    n_comp, n_time = X.shape
    autocorrs = []
    for i in range(n_comp):
        ac = np.corrcoef(X[i, :-1], X[i, 1:])[0, 1]
        autocorrs.append(ac)
    mean_ac = np.mean(autocorrs)
    return {"mean_autocorrelation": float(mean_ac), "present": mean_ac > 0.6}


def detect_template(X):
    """Information transfer via copying."""
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
    """Protected interior via internal vs external coupling."""
    n_comp, n_time = X.shape
    n_inside = n_comp // 2
    internal_corr = np.mean(np.corrcoef(X[:n_inside])[:n_inside, :n_inside])
    cross_corr = np.mean(np.corrcoef(X[:n_inside, :], X[n_inside:])[:n_inside, n_comp-n_inside:])
    ratio = internal_corr / (cross_corr + 1e-10)
    return {"boundary_ratio": float(ratio), "present": ratio > 1.5}


def detect_hierarchy(X):
    """Nested coordination via scale-dependent correlation."""
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
    """Self-referential representation via meta-level correlation."""
    n_comp, n_time = X.shape
    n_base = n_comp // 3
    n_meta = n_comp // 3
    base_meta_corr = np.mean(np.corrcoef(X[:n_base], X[n_base:n_base+n_meta])[:n_base, n_base:n_base+n_meta])
    meta_meta_corr = np.mean(np.corrcoef(X[n_base:n_base+n_meta], X[n_base+n_meta:])[:n_meta, :n_comp-n_base-n_meta])
    recursion_score = (base_meta_corr + meta_meta_corr) / 2
    return {"recursion_score": float(recursion_score), "present": recursion_score > 0.3}


def detect_formal_inference(X):
    """Derivation from axioms via deterministic relationships."""
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


# ─────────────────────────────────────────────────────────
# Phase 2: Pattern Discovery
# ─────────────────────────────────────────────────────────

def run_pattern_discovery():
    """Run all architectures and detect motifs."""
    results = {}
    for arch_name, gen_func in GENERATORS.items():
        print(f"  {arch_name}...")
        X = gen_func(seed=42)
        detections = {}
        for motif_name, detect_func in DETECTORS.items():
            det = detect_func(X)
            detections[motif_name] = det
        results[arch_name] = detections
    return results


# ─────────────────────────────────────────────────────────
# Phase 3: Null-Model Comparison
# ─────────────────────────────────────────────────────────

def run_null_models():
    """Compare each architecture against null models."""
    null_results = {}

    # Random null
    print("  Random null...")
    X_random = gen_random(seed=42)
    null_results["random"] = {m: f(X_random) for m, f in DETECTORS.items()}

    # Shuffled nulls (for each architecture)
    for arch_name, gen_func in GENERATORS.items():
        print(f"  Shuffled {arch_name}...")
        X = gen_func(seed=42)
        X_shuffled = gen_shuffled(X)
        null_results[f"shuffled_{arch_name}"] = {m: f(X_shuffled) for m, f in DETECTORS.items()}

    # Degenerate nulls
    print("  Degenerate binding...")
    X_deg_bind = gen_degenerate_binding(seed=42)
    null_results["degenerate_binding"] = {m: f(X_deg_bind) for m, f in DETECTORS.items()}

    print("  Degenerate boundary...")
    X_deg_bound = gen_degenerate_boundary(seed=42)
    null_results["degenerate_boundary"] = {m: f(X_deg_bound) for m, f in DETECTORS.items()}

    print("  Degenerate hierarchy...")
    X_deg_hier = gen_degenerate_hierarchy(seed=42)
    null_results["degenerate_hierarchy"] = {m: f(X_deg_hier) for m, f in DETECTORS.items()}

    return null_results


# ─────────────────────────────────────────────────────────
# Phase 4: Causal Testing (Removal Test)
# ─────────────────────────────────────────────────────────

def run_removal_test(arch_name, motif_to_remove):
    """Remove a motif and measure effect on D_persist."""
    gen_func = GENERATORS[arch_name]
    X_original = gen_func(seed=42)

    # Detect original motif presence
    original_det = DETECTORS[motif_to_remove](X_original)
    original_present = original_det.get("present", False)

    # Compute D_persist for original
    d_persist_original = compute_d_persist(X_original)

    # Create modified version with motif removed
    X_modified = remove_motif(arch_name, motif_to_remove, X_original)

    # Detect motif in modified version
    modified_det = DETECTORS[motif_to_remove](X_modified)
    modified_present = modified_det.get("present", False)

    # Compute D_persist for modified
    d_persist_modified = compute_d_persist(X_modified)

    return {
        "original_present": original_present,
        "modified_present": modified_present,
        "d_persist_original": d_persist_original,
        "d_persist_modified": d_persist_modified,
        "reduction": d_persist_original - d_persist_modified,
    }


def remove_motif(arch_name, motif_name, X):
    """Remove a specific motif from architecture."""
    X_mod = X.copy()
    n_comp, n_time = X.shape

    if motif_name == "binding":
        # Remove discrete states by smoothing
        for i in range(n_comp):
            kernel = np.ones(5) / 5
            X_mod[i] = np.convolve(X[i], kernel, mode='same')

    elif motif_name == "network":
        # Remove network coupling by decorrelating
        for i in range(n_comp):
            rng = np.random.default_rng(42 + i)
            X_mod[i] = rng.permutation(X[i])

    elif motif_name == "cycle":
        # Remove cycle by breaking feedback
        for i in range(n_comp):
            X_mod[i, 1:] = X[i, :-1]  # Remove temporal autocorrelation

    elif motif_name == "template":
        # Remove template copying
        n_templates = n_comp // 2
        for i in range(n_templates, n_comp):
            rng = np.random.default_rng(42 + i)
            X_mod[i] = rng.normal(0, 1, n_time)

    elif motif_name == "boundary":
        # Remove boundary by equalizing coupling
        global_signal = np.mean(X, axis=0)
        for i in range(n_comp):
            X_mod[i] = 0.5 * X_mod[i] + 0.3 * global_signal

    elif motif_name == "hierarchy":
        # Remove hierarchy by flattening
        global_signal = np.mean(X, axis=0)
        for i in range(n_comp):
            X_mod[i] = 0.5 * X_mod[i] + 0.3 * global_signal

    elif motif_name == "recursion":
        # Remove recursion by removing meta-levels
        n_base = n_comp // 3
        for i in range(n_base, n_comp):
            rng = np.random.default_rng(42 + i)
            X_mod[i] = rng.normal(0, 1, n_time)

    elif motif_name == "formal_inference":
        # Remove formal inference by decorrelating derived from axioms
        n_axioms = 3
        for i in range(n_axioms, n_comp):
            rng = np.random.default_rng(42 + i)
            X_mod[i] = rng.normal(0, 1, n_time)

    return X_mod


def compute_d_persist(X):
    """Compute D_persist: how many differences persist over time."""
    n_comp, n_time = X.shape
    # Compute lag-1 autocorrelation for each component
    persistences = []
    for i in range(n_comp):
        ac = np.corrcoef(X[i, :-1], X[i, 1:])[0, 1]
        persistences.append(max(0, ac))  # Clamp negative to 0
    return float(np.mean(persistences))


# ─────────────────────────────────────────────────────────
# Main Execution
# ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("RD-10B Phase 2-4: Discovery, Nulls, Causal Testing")
    print("=" * 60)

    # Phase 2: Pattern Discovery
    print("\nPhase 2: Pattern Discovery")
    discovery = run_pattern_discovery()

    # Phase 3: Null-Model Comparison
    print("\nPhase 3: Null-Model Comparison")
    nulls = run_null_models()

    # Phase 4: Causal Testing (Removal Test)
    print("\nPhase 4: Causal Testing (Removal)")
    removal_results = {}
    for arch_name in GENERATORS:
        removal_results[arch_name] = {}
        for motif_name in DETECTORS:
            if arch_name != motif_name:  # Only test removal when motif differs from architecture
                result = run_removal_test(arch_name, motif_name)
                removal_results[arch_name][motif_name] = result

    # Save results
    output = {
        "discovery": {k: {m: {"present": d["present"]} for m, d in v.items()} for k, v in discovery.items()},
        "nulls": {k: {m: {"present": d["present"]} for m, d in v.items()} for k, v in nulls.items()},
        "removal": removal_results,
    }

    with open(OUT_DIR / "rd10b_phase2_4_results.json", "w") as f:
        json.dump(output, f, indent=2, default=str)

    # Print summary
    print("\n" + "=" * 60)
    print("DISCOVERY SUMMARY")
    print("=" * 60)
    for arch_name, detections in discovery.items():
        present = [m for m, d in detections.items() if d.get("present", False)]
        print(f"  {arch_name}: {present}")

    print("\n" + "=" * 60)
    print("NULL MODEL SUMMARY")
    print("=" * 60)
    for null_name, detections in nulls.items():
        present = [m for m, d in detections.items() if d.get("present", False)]
        print(f"  {null_name}: {present}")

    print("\n" + "=" * 60)
    print("REMOVAL TEST SUMMARY")
    print("=" * 60)
    for arch_name, tests in removal_results.items():
        for motif_name, result in tests.items():
            if result["reduction"] > 0.1:
                print(f"  {arch_name} - {motif_name}: reduction={result['reduction']:.3f}")

    print(f"\nResults saved to {OUT_DIR / 'rd10b_phase2_4_results.json'}")
