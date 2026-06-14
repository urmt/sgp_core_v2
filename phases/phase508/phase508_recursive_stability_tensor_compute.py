#!/usr/bin/env python3
"""
Phase 508: Recursive Stability Tensor — True Latent Decomposition
Determines whether the 5 surviving Phase 506 systems survive for the SAME
mathematical reason by eigendecomposing their Recursive Stability Tensor,
computing adversarial response geometry, and mapping collapse topology.
"""

import json
import numpy as np
import os

np.random.seed(508)

METRIC_KEYS = [
    'coherence_survival_ratio',
    'recursive_balance_strength',
    'recursive_transport_persistence',
    'asymmetry_dependence_index',
    'signature_retention_decay'
]

SHORT = {
    'coherence_survival_ratio': 'CSR',
    'recursive_balance_strength': 'RBS',
    'recursive_transport_persistence': 'RTP',
    'asymmetry_dependence_index': 'ADI',
    'signature_retention_decay': 'SRD'
}

def load_phase507():
    with open('phases/phase507/phase507_results.json') as f:
        return json.load(f)

def build_system_tensor(results):
    """Construct the 5x5 Recursive Stability Tensor R.
       
    Each column is a surviving system.
    Each row is (CSR, RBS, RTP, ADI, SRD) averaged over all adversarial
    conditions for that system.
    """
    surviving = ['EnergyMomentumConservation', 'DoubleSlitInterference',
                 'ChemicalEquilibriumNetwork', 'TurbulenceEnergyCascade',
                 'SuperconductorCoherence']
    mb = results['metrics_by_system']
    n_metrics = len(METRIC_KEYS)
    n_sys = len(surviving)
    R = np.zeros((n_metrics, n_sys))
    for j, sys in enumerate(surviving):
        conds = mb.get(sys, {})
        counts = {k: 0.0 for k in METRIC_KEYS}
        n_cond = 0
        for cname, met in conds.items():
            n_cond += 1
            for mk in METRIC_KEYS:
                counts[mk] += met.get(mk, 0.0)
        for i, mk in enumerate(METRIC_KEYS):
            R[i, j] = counts[mk] / max(n_cond, 1)
    return R, surviving

def step1_latent_decomposition(R):
    """Step 1: C = R^T R, eigendecompose, compute λ1/Σλ ratio."""
    C = R.T @ R
    eigvals, eigvecs = np.linalg.eig(C)
    idx = np.argsort(eigvals)[::-1]
    eigvals = eigvals[idx]
    eigvecs = eigvecs[:, idx]
    total = np.sum(eigvals)
    ratio = eigvals[0] / total if total > 0 else 0.0

    # Determine regime
    if ratio > 0.80:
        regime = "hidden invariant candidate"
    elif ratio >= 0.45:
        regime = "coupled recursive manifold"
    else:
        regime = "independent stabilizers"

    return {
        'C': C.tolist(),
        'eigenvalues': [float(v) for v in eigvals],
        'eigenvectors': eigvecs.tolist(),
        'lambda1_ratio': float(ratio),
        'regime': regime,
        'dominant_modes': int(np.sum(eigvals > eigvals[0] * 0.1))
    }

def build_degradation_vectors(results):
    """Step 2: For each adversarial condition build a 5-element degradation vector
       D_a = [mean(CSR), mean(RBS), mean(RTP), mean(ADI), mean(SRD)]
       averaged over all surviving systems."""
    surviving = ['EnergyMomentumConservation', 'DoubleSlitInterference',
                 'ChemicalEquilibriumNetwork', 'TurbulenceEnergyCascade',
                 'SuperconductorCoherence']
    mb = results['metrics_by_system']

    # Collect condition names
    first_sys = surviving[0]
    cond_names = list(mb.get(first_sys, {}).keys())

    D = {}
    for cond in cond_names:
        vec = []
        for mk in METRIC_KEYS:
            vals = []
            for sys in surviving:
                met = mb.get(sys, {}).get(cond, {})
                vals.append(met.get(mk, 0.0))
            vec.append(np.mean(vals))
        D[cond] = np.array(vec)
    return D, cond_names

def step2_adversarial_geometry(D, cond_names):
    """Pairwise cosine similarity between degradation vectors."""
    n = len(cond_names)
    cos_mat = np.eye(n)
    for i in range(n):
        di = D[cond_names[i]]
        ni = np.linalg.norm(di)
        for j in range(i+1, n):
            dj = D[cond_names[j]]
            nj = np.linalg.norm(dj)
            if ni > 1e-12 and nj > 1e-12:
                cos = np.dot(di, dj) / (ni * nj)
            else:
                cos = 0.0
            cos_mat[i, j] = cos
            cos_mat[j, i] = cos

    return {
        'condition_names': cond_names,
        'cosine_similarity_matrix': cos_mat.tolist()
    }

def step3_recursive_coupling(R, surviving):
    """Step 3: Compute correlation matrix K across metrics.
       K_ij = corr(row_i, row_j) of R."""
    n_metrics = len(METRIC_KEYS)
    K = np.ones((n_metrics, n_metrics))
    for i in range(n_metrics):
        for j in range(i+1, n_metrics):
            r = np.corrcoef(R[i, :], R[j, :])[0, 1]
            if np.isnan(r):
                r = 0.0
            K[i, j] = r
            K[j, i] = r

    # Determine structure sparsity
    off_diag = np.abs(K - np.eye(n_metrics))
    mean_off = np.mean(off_diag)
    if mean_off > 0.5:
        structure = "coupled recursive stabilizers"
    elif mean_off > 0.2:
        structure = "moderately coupled"
    else:
        structure = "semi-independent mechanisms"

    return {
        'coupling_matrix': K.tolist(),
        'metric_labels': [SHORT[mk] for mk in METRIC_KEYS],
        'mean_off_diagonal_coupling': float(mean_off),
        'structure': structure
    }

def step4_collapse_topology(mb, surviving, cond_names):
    """Step 4: Approximate collapse topology.
       For each system, compute trajectory T(d) = norm(metric vector) under each
       adversarial condition d. Then compute discrete curvature (second difference)."""
    results = {}
    all_curvatures = []
    for sys in surviving:
        conds = mb.get(sys, {})
        # Build trajectory (norm of 5-metric vector for each condition)
        points = []
        used_conds = []
        for cond in cond_names:
            met = conds.get(cond, {})
            vec = [met.get(mk, 0.0) for mk in METRIC_KEYS]
            points.append(np.linalg.norm(vec))
            used_conds.append(cond)
        pts = np.array(points)

        # Discrete curvature: second derivative magnitude
        if len(pts) >= 3:
            d1 = np.diff(pts)
            d2 = np.diff(d1) if len(d1) >= 2 else np.array([0.0])
            if len(d2) > 0:
                curvature = float(np.mean(np.abs(d2)))
            else:
                curvature = 0.0
        else:
            curvature = 0.0

        # Detect discontinuities (>3 std from mean of abs differences)
        if len(pts) >= 3:
            diffs = np.abs(np.diff(pts))
            threshold = np.mean(diffs) + 3 * np.std(diffs) if np.std(diffs) > 0 else 0.0
            discontinuities = [i for i, d in enumerate(diffs) if d > threshold]
        else:
            discontinuities = []

        all_curvatures.append(curvature)
        results[sys] = {
            'trajectory_points': pts.tolist(),
            'conditions': used_conds,
            'mean_curvature': float(curvature),
            'discontinuities': discontinuities,
            'smooth_degradation': len(discontinuities) == 0
        }

    # Cluster systems by curvature similarity
    from scipy.cluster.hierarchy import linkage, fcluster
    from scipy.spatial.distance import pdist
    if len(all_curvatures) >= 4:
        X = np.array([[c] for c in all_curvatures])
        if np.std(X) > 0:
            dists = pdist(X)
            Z = linkage(dists, method='single')
            # Cut at median distance
            clusters = fcluster(Z, t=np.median(dists) if len(dists) > 0 else 1.0, criterion='distance')
        else:
            clusters = np.ones(len(all_curvatures))
    else:
        clusters = np.ones(len(all_curvatures))

    return {
        'per_system': results,
        'cluster_assignments': [int(c) for c in clusters.tolist()],
        'n_clusters': int(len(set(clusters.tolist())))
    }

def main():
    print("Starting Phase 508: Recursive Stability Tensor analysis...")

    # Load Phase 507 data
    p507 = load_phase507()
    mb = p507['metrics_by_system']

    # Build tensor
    R, surviving = build_system_tensor(p507)
    print(f"Systems: {surviving}")
    print(f"Tensor shape: {R.shape}")

    # ---- Step 1 ----
    print("\n--- Step 1: Latent Decomposition ---")
    s1 = step1_latent_decomposition(R)
    print(f"Eigenvalues: {s1['eigenvalues']}")
    print(f"λ₁/Σλ = {s1['lambda1_ratio']:.4f}")
    print(f"Regime: {s1['regime']}")
    print(f"Dominant modes: {s1['dominant_modes']}")

    # ---- Step 2 ----
    print("\n--- Step 2: Adversarial Response Geometry ---")
    D, cond_names = build_degradation_vectors(p507)
    s2 = step2_adversarial_geometry(D, cond_names)
    print(f"Conditions: {cond_names}")
    cmat = np.array(s2['cosine_similarity_matrix'])
    # Pairwise cosines across conditions
    for i in range(len(cond_names)):
        for j in range(i+1, len(cond_names)):
            print(f"  cos(θ) {cond_names[i]} vs {cond_names[j]}: {cmat[i,j]:.4f}")

    # ---- Step 3 ----
    print("\n--- Step 3: Recursive Coupling Matrix ---")
    s3 = step3_recursive_coupling(R, surviving)
    print("Correlation matrix K (rows/cols: CSR,RBS,RTP,ADI,SRD):")
    K = np.array(s3['coupling_matrix'])
    for i in range(len(METRIC_KEYS)):
        row = "  ".join(f"{K[i,j]:.3f}" for j in range(len(METRIC_KEYS)))
        print(f"  {SHORT[METRIC_KEYS[i]]}: {row}")
    print(f"Mean off-diagonal coupling: {s3['mean_off_diagonal_coupling']:.4f}")
    print(f"Structure: {s3['structure']}")

    # ---- Step 4 ----
    print("\n--- Step 4: Collapse Topology ---")
    s4 = step4_collapse_topology(mb, surviving, cond_names)
    for sys, d in s4['per_system'].items():
        print(f"  {sys}: curvature={d['mean_curvature']:.4f}, "
              f"discontinuities={d['discontinuities']}, "
              f"smooth={d['smooth_degradation']}")
    print(f"Cluster assignments: {s4['cluster_assignments']}")
    print(f"Number of clusters: {s4['n_clusters']}")

    # ---- Summary ----
    print("\n" + "="*70)
    print("PHASE 508 RESULTS SUMMARY")
    print("="*70)
    print(f"Systems analyzed: {surviving}")
    print(f"λ₁/Σλ = {s1['lambda1_ratio']:.4f} — {s1['regime']}")
    print(f"Dominant recursive modes: {s1['dominant_modes']}")
    print(f"Coupling structure: {s3['structure']} (mean off-diag={s3['mean_off_diagonal_coupling']:.4f})")
    print(f"Collapse clusters: {s4['n_clusters']}")
    if s1['lambda1_ratio'] >= 0.45 and s1['lambda1_ratio'] <= 0.80:
        print("Prediction CONFIRMED: bounded recursive phase space.")
    elif s1['lambda1_ratio'] > 0.80:
        print("Prediction DEVIATES: single invariant dominates.")
    else:
        print("Prediction DEVIATES: independent stabilizers.")
    print("="*70)

    # Save results
    results = {
        'phase': 508,
        'seed': 508,
        'tier': 3,
        'surviving_systems': surviving,
        'recursive_stability_tensor': R.tolist(),
        'metric_labels': [SHORT[mk] for mk in METRIC_KEYS],
        'step1_latent_decomposition': s1,
        'step2_adversarial_geometry': s2,
        'step3_recursive_coupling': s3,
        'step4_collapse_topology': s4,
        'interpretation': s1['regime'],
        'dominant_modes': s1['dominant_modes'],
        'lambda1_ratio': s1['lambda1_ratio']
    }

    out = 'phases/phase508/phase508_results.json'
    with open(out, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {out}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
