"""RD-10B: Architectural Invariants Survey

Phase -1 & 0: Build 8 toy universes, define motif detection rules.
Phase 1: Motif independence analysis.

Standing Rules:
  - Whenever something looks fundamental, ask what makes it possible.
  - Whenever something looks recurrent, ask whether it is causal.
  - Whenever something looks like a deeper invariant, ask whether it might be an attractor instead.
"""

import numpy as np
import json
import sys
import os
from pathlib import Path

RNG = np.random.default_rng(42)
OUT_DIR = Path(__file__).resolve().parent
OUT_DIR.mkdir(exist_ok=True)

# ─────────────────────────────────────────────────────────
# Phase -1: Category Audit — Architectures to test
# ─────────────────────────────────────────────────────────

ARCHITECTURES = {
    "binding": {
        "description": "Discrete states via potential wells",
        "n_components": 12,
        "n_timepoints": 800,
    },
    "network": {
        "description": "Connected modules",
        "n_components": 12,
        "n_timepoints": 800,
    },
    "cycle": {
        "description": "Self-reinforcing loops",
        "n_components": 12,
        "n_timepoints": 800,
    },
    "template": {
        "description": "Information transfer via copying",
        "n_components": 12,
        "n_timepoints": 800,
    },
    "boundary": {
        "description": "Protected interior",
        "n_components": 12,
        "n_timepoints": 800,
    },
    "hierarchy": {
        "description": "Nested coordination",
        "n_components": 12,
        "n_timepoints": 800,
    },
    "recursion": {
        "description": "Self-referential representation",
        "n_components": 12,
        "n_timepoints": 800,
    },
    "formal_inference": {
        "description": "Derivation from axioms",
        "n_components": 12,
        "n_timepoints": 800,
    },
}

# ─────────────────────────────────────────────────────────
# Toy Universe Generators (one per architecture)
# ─────────────────────────────────────────────────────────

def gen_binding(n_components=12, n_timepoints=800, seed=42):
    """Discrete states via potential wells.

    Each component is trapped in a quantized potential well.
    Transitions between wells are rare (energy barriers).
    """
    rng = np.random.default_rng(seed)
    n_wells = 3
    well_centers = rng.uniform(-2, 2, n_wells)
    well_width = 0.3
    barrier_height = 2.0

    X = np.zeros((n_components, n_timepoints))
    state = rng.integers(0, n_wells, n_components)

    for t in range(n_timepoints):
        for i in range(n_components):
            # Rare transitions (barrier crossing)
            if rng.random() < 0.01:
                # Attempt transition to neighboring well
                delta = rng.choice([-1, 1])
                new_state = (state[i] + delta) % n_wells
                if rng.random() < np.exp(-barrier_height):
                    state[i] = new_state
            X[i, t] = well_centers[state[i]] + rng.normal(0, well_width)
    return X


def gen_network(n_components=12, n_timepoints=800, seed=42):
    """Connected modules via network coupling.

    Components form a network. Coupling strength depends on
    graph distance. Short-range coupling dominates.
    """
    rng = np.random.default_rng(seed)

    # Create ring network
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
    """Self-reinforcing loops.

    Components form a directed cycle. Each component drives
    the next. Output of the last feeds back to the first.
    """
    rng = np.random.default_rng(seed)
    X = rng.normal(0, 1, (n_components, n_timepoints))

    for t in range(1, n_timepoints):
        for i in range(n_components):
            prev = (i - 1) % n_components
            X[i, t] = 0.6 * X[i, t-1] + 0.4 * X[prev, t-1] + rng.normal(0, 0.15)
    return X


def gen_template(n_components=12, n_timepoints=800, seed=42):
    """Information transfer via copying.

    Half the components are "templates". The other half are
    "copies" that replicate their template with errors.
    """
    rng = np.random.default_rng(seed)
    n_templates = n_components // 2

    X = rng.normal(0, 1, (n_components, n_timepoints))

    # Templates evolve independently
    for i in range(n_templates):
        for t in range(1, n_timepoints):
            X[i, t] = 0.7 * X[i, t-1] + rng.normal(0, 0.3)

    # Copies replicate templates with error
    for i in range(n_templates, n_components):
        template_idx = i - n_templates
        for t in range(1, n_timepoints):
            X[i, t] = 0.8 * X[template_idx, t-1] + rng.normal(0, 0.1)
    return X


def gen_boundary(n_components=12, n_timepoints=800, seed=42):
    """Protected interior via membrane.

    Half the components are "inside" (strongly coupled).
    Half are "outside" (weakly coupled to inside).
    Boundary creates internal vs external distinction.
    """
    rng = np.random.default_rng(seed)
    n_inside = n_components // 2

    X = rng.normal(0, 1, (n_components, n_timepoints))

    for t in range(1, n_timepoints):
        # Inside: strongly coupled to each other
        for i in range(n_inside):
            inside_signal = np.mean(X[:n_inside, t-1])
            X[i, t] = 0.3 * X[i, t-1] + 0.5 * inside_signal + rng.normal(0, 0.1)

        # Outside: weakly coupled, influenced by inside
        for i in range(n_inside, n_components):
            inside_signal = np.mean(X[:n_inside, t-1])
            X[i, t] = 0.5 * X[i, t-1] + 0.1 * inside_signal + rng.normal(0, 0.3)
    return X


def gen_hierarchy(n_components=12, n_timepoints=800, seed=42):
    """Nested coordination via hierarchy.

    Three levels: micro (4), meso (4), macro (4).
    Macro influences meso influences micro.
    """
    rng = np.random.default_rng(seed)
    n_micro = 4
    n_meso = 4
    n_macro = 4

    X = rng.normal(0, 1, (n_components, n_timepoints))

    for t in range(1, n_timepoints):
        # Macro: slow, independent
        for i in range(n_components - n_macro, n_components):
            X[i, t] = 0.7 * X[i, t-1] + rng.normal(0, 0.2)

        # Meso: driven by macro
        macro_signal = np.mean(X[n_components - n_macro:, t-1])
        for i in range(n_micro, n_micro + n_meso):
            X[i, t] = 0.5 * X[i, t-1] + 0.3 * macro_signal + rng.normal(0, 0.15)

        # Micro: driven by meso
        meso_signal = np.mean(X[n_micro:n_micro + n_meso, t-1])
        for i in range(n_micro):
            X[i, t] = 0.4 * X[i, t-1] + 0.4 * meso_signal + rng.normal(0, 0.1)
    return X


def gen_recursion(n_components=12, n_timepoints=800, seed=42):
    """Self-referential representation.

    Components form a representation that contains a model
    of its own interpretation process. Meta-levels emerge.
    """
    rng = np.random.default_rng(seed)
    n_base = n_components // 3
    n_meta = n_components // 3
    n_meta2 = n_components - n_base - n_meta

    X = rng.normal(0, 1, (n_components, n_timepoints))

    for t in range(1, n_timepoints):
        # Base level: independent
        for i in range(n_base):
            X[i, t] = 0.5 * X[i, t-1] + rng.normal(0, 0.3)

        # Meta level: models base level
        base_signal = np.mean(X[:n_base, t-1])
        for i in range(n_base, n_base + n_meta):
            X[i, t] = 0.6 * X[i, t-1] + 0.3 * base_signal + rng.normal(0, 0.15)

        # Meta-meta level: models meta level
        meta_signal = np.mean(X[n_base:n_base + n_meta, t-1])
        for i in range(n_base + n_meta, n_components):
            X[i, t] = 0.7 * X[i, t-1] + 0.2 * meta_signal + rng.normal(0, 0.1)
    return X


def gen_formal_inference(n_components=12, n_timepoints=800, seed=42):
    """Derivation from axioms.

    First 3 components are axioms (fixed rules).
    Remaining components derive values from axioms via inference rules.
    """
    rng = np.random.default_rng(seed)
    n_axioms = 3

    X = rng.normal(0, 1, (n_components, n_timepoints))

    # Axioms: fixed rules (slowly varying)
    for i in range(n_axioms):
        for t in range(1, n_timepoints):
            X[i, t] = 0.9 * X[i, t-1] + rng.normal(0, 0.1)

    # Derived: deterministic function of axioms
    for i in range(n_axioms, n_components):
        for t in range(1, n_timepoints):
            # Different inference rules
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
# Phase 0: Motif Detection Rules
# ─────────────────────────────────────────────────────────

def detect_binding(X):
    """Detect discrete states via potential wells.

    Measure: variance ratio between within-state and between-state.
    High ratio = discrete states present.
    """
    n_comp, n_time = X.shape
    # Quantize each component into 4 bins
    quantized = np.zeros_like(X)
    for i in range(n_comp):
        quantized[i] = np.digitize(X[i], np.percentile(X[i], [25, 50, 75]))

    # Compute within-state vs between-state variance
    within_vars = []
    between_vars = []
    for q in range(4):
        mask = quantized[0] == q
        if np.sum(mask) > 5:
            within_vars.append(np.var(X[0, mask]))
        # Between: variance of means
    between_var = np.var([np.mean(X[0, quantized[0] == q]) for q in range(4) if np.sum(quantized[0] == q) > 0])
    within_var = np.mean(within_vars) if within_vars else 1.0

    ratio = between_var / (within_var + 1e-10)
    return {"binding_ratio": float(ratio), "present": ratio > 0.5}


def detect_network(X):
    """Detect connected modules via cross-correlation structure.

    Measure: modularity of cross-correlation matrix.
    High modularity = network structure present.
    """
    corr = np.corrcoef(X)
    n = corr.shape[0]

    # Simple modularity: compare within-block vs between-block
    half = n // 2
    within = np.mean(corr[:half, :half]) + np.mean(corr[half:, half:])
    between = np.mean(corr[:half, half:])
    modularity = (within - between) / 2

    return {"modularity": float(modularity), "present": modularity > 0.1}


def detect_cycle(X):
    """Detect self-reinforcing loops via lagged autocorrelation.

    Measure: average lag-1 autocorrelation across components.
    High autocorrelation = self-reinforcing loops present.
    """
    n_comp, n_time = X.shape
    autocorrs = []
    for i in range(n_comp):
        ac = np.corrcoef(X[i, :-1], X[i, 1:])[0, 1]
        autocorrs.append(ac)
    mean_ac = np.mean(autocorrs)

    return {"mean_autocorrelation": float(mean_ac), "present": mean_ac > 0.6}


def detect_template(X):
    """Detect information transfer via copying.

    Measure: correlation between template and copy components.
    High correlation = template copying present.
    """
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
    """Detect protected interior via internal vs external coupling.

    Measure: ratio of internal to external cross-correlation.
    High ratio = boundary present.
    """
    n_comp, n_time = X.shape
    n_inside = n_comp // 2

    # Internal correlation
    internal_corr = np.mean(np.corrcoef(X[:n_inside])[:n_inside, :n_inside])
    # External correlation
    external_corr = np.mean(np.corrcoef(X[n_inside:])[:n_comp-n_inside, :n_comp-n_inside])
    # Cross correlation
    cross_corr = np.mean(np.corrcoef(X[:n_inside, :], X[n_inside:])[:n_inside, n_comp-n_inside:])

    ratio = internal_corr / (cross_corr + 1e-10)

    return {"boundary_ratio": float(ratio), "present": ratio > 1.5}


def detect_hierarchy(X):
    """Detect nested coordination via scale-dependent correlation.

    Measure: correlation structure shows nested levels.
    Use wavelet-like decomposition: compute correlation at
    different time scales.
    """
    n_comp, n_time = X.shape
    # Compute correlation at different scales
    scales = [1, 5, 20]
    scale_corrs = []
    for s in scales:
        # Downsample
        X_ds = X[:, ::s] if s > 1 else X
        corr = np.corrcoef(X_ds)
        # Within-group correlation
        half = n_comp // 2
        within = np.mean(corr[:half, :half])
        scale_corrs.append(within)

    # Hierarchy = correlation increases at larger scales
    hierarchy_score = scale_corrs[-1] - scale_corrs[0]

    return {"hierarchy_score": float(hierarchy_score), "present": hierarchy_score > 0.1}


def detect_recursion(X):
    """Detect self-referential representation via meta-level correlation.

    Measure: correlation between base and meta levels.
    High correlation = meta-level models base level.
    """
    n_comp, n_time = X.shape
    n_base = n_comp // 3
    n_meta = n_comp // 3

    # Base-meta correlation
    base_meta_corr = np.mean(np.corrcoef(X[:n_base], X[n_base:n_base+n_meta])[:n_base, n_base:n_base+n_meta])
    # Meta-meta correlation
    meta_meta_corr = np.mean(np.corrcoef(X[n_base:n_base+n_meta], X[n_base+n_meta:])[:n_meta, :n_comp-n_base-n_meta])

    recursion_score = (base_meta_corr + meta_meta_corr) / 2

    return {"recursion_score": float(recursion_score), "present": recursion_score > 0.3}


def detect_formal_inference(X):
    """Detect derivation from axioms via deterministic relationships.

    Measure: predictability of derived components from axioms.
    High predictability = formal inference present.
    """
    n_comp, n_time = X.shape
    n_axioms = 3

    r2_scores = []
    for i in range(n_axioms, n_comp):
        # Simple linear prediction from axioms
        A = X[:n_axioms, :-1].T
        y = X[i, 1:]
        # Least squares
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
# Run All Architectures
# ─────────────────────────────────────────────────────────

def run_all():
    """Generate all architectures and detect motifs."""
    results = {}
    all_detections = {}

    for arch_name, arch_config in ARCHITECTURES.items():
        print(f"Running {arch_name}...")
        gen_func = GENERATORS[arch_name]
        X = gen_func(
            n_components=arch_config["n_components"],
            n_timepoints=arch_config["n_timepoints"],
            seed=42,
        )

        # Detect all motifs
        detections = {}
        for motif_name, detect_func in DETECTORS.items():
            det = detect_func(X)
            detections[motif_name] = det

        all_detections[arch_name] = detections

        # Compute coherence (mean pairwise correlation)
        corr = np.corrcoef(X)
        n = corr.shape[0]
        # Upper triangle excluding diagonal
        mask = np.triu(np.ones((n, n), dtype=bool), k=1)
        C_mean = float(np.mean(corr[mask]))

        results[arch_name] = {
            "description": arch_config["description"],
            "C_mean": C_mean,
            "detections": detections,
        }

    return results, all_detections


def compute_independence(all_detections):
    """Phase 1: Compute motif independence via correlation matrix."""
    arch_names = list(all_detections.keys())
    motif_names = list(DETECTORS.keys())

    # Build detection matrix: rows=architectures, cols=motifs
    # Use the primary metric for each motif
    primary_metrics = {
        "binding": "binding_ratio",
        "network": "modularity",
        "cycle": "mean_autocorrelation",
        "template": "mean_copy_correlation",
        "boundary": "boundary_ratio",
        "hierarchy": "hierarchy_score",
        "recursion": "recursion_score",
        "formal_inference": "inference_r2",
    }

    matrix = np.zeros((len(arch_names), len(motif_names)))
    for i, arch in enumerate(arch_names):
        for j, motif in enumerate(motif_names):
            metric = primary_metrics[motif]
            matrix[i, j] = all_detections[arch][motif].get(metric, 0)

    # Normalize
    for j in range(matrix.shape[1]):
        col = matrix[:, j]
        col_range = np.max(col) - np.min(col)
        if col_range > 0:
            matrix[:, j] = (col - np.min(col)) / col_range

    # Compute correlation matrix between motifs
    if matrix.shape[0] > 2:
        corr_matrix = np.corrcoef(matrix.T)
    else:
        corr_matrix = np.eye(len(motif_names))

    return {
        "matrix": matrix.tolist(),
        "correlation": corr_matrix.tolist(),
        "arch_names": arch_names,
        "motif_names": motif_names,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("RD-10B: Architectural Invariants Survey")
    print("Phase -1 & 0: Build toy universes, detect motifs")
    print("=" * 60)

    results, all_detections = run_all()

    # Phase 1: Independence analysis
    independence = compute_independence(all_detections)

    # Save results
    output = {
        "results": results,
        "independence": independence,
    }

    with open(OUT_DIR / "rd10b_results.json", "w") as f:
        json.dump(output, f, indent=2, default=str)

    # Print summary
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)

    for arch_name, data in results.items():
        print(f"\n{arch_name}:")
        print(f"  C_mean: {data['C_mean']:.4f}")
        for motif, det in data["detections"].items():
            present = "PRESENT" if det.get("present", False) else "absent"
            print(f"  {motif}: {present}")

    print("\n" + "=" * 60)
    print("MOTIF INDEPENDENCE (correlation matrix)")
    print("=" * 60)
    corr = np.array(independence["correlation"])
    motifs = independence["motif_names"]
    print(f"{'':>20}", end="")
    for m in motifs:
        print(f"{m[:8]:>10}", end="")
    print()
    for i, m in enumerate(motifs):
        print(f"{m:>20}", end="")
        for j in range(len(motifs)):
            print(f"{corr[i,j]:>10.3f}", end="")
        print()

    print(f"\nResults saved to {OUT_DIR / 'rd10b_results.json'}")
