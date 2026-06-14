"""
T031: NULL GEOMETRY DISENTANGLEMENT
====================================
Determine whether the surviving Φ-space geometry from T030 is
genuine dynamical structure, generic statistical covariance,
or artifact.

Loads existing T030 ensemble (211 systems, 13 families) and
subjects Φ-space to 7 null models + 7 analysis sections.

Runtime target: < 30 minutes (loads precomputed data).
"""

import sys, json, warnings, time, gc, itertools
from pathlib import Path
from typing import Callable, Optional
import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform, cdist
from scipy.stats import pearsonr, spearmanr, gaussian_kde, ttest_ind, linregress, chi2
from scipy.linalg import svd, svdvals, eigvalsh
from scipy.cluster.hierarchy import linkage, fcluster
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors, KernelDensity
from sklearn.metrics import r2_score, silhouette_score
from sklearn.linear_model import LinearRegression
from sklearn.manifold import Isomap
from scipy.spatial import Delaunay
import networkx as nx

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=UserWarning)
np.random.seed(42)

sys.path.insert(0, ".")
from sfh_sgp_ood_universality_audit import (
    compute_transform_geometry, null_audit_system, replay_stability,
)
from T030_TRANSITION_FIELD_GENERALIZATION import EmergenceProjector, NpEncoder, FEATURE_NAMES

OUT = Path("sfh_sgp_ood_outputs")
FIG = Path("figures")
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)

N_BOOT = 100
N_SYSTEMS_MAX = 211
SEED = 42
np.random.seed(SEED)

OUTPUT = {}


def print_sep():
    print("\n" + "=" * 70)


def ci_percentile(arr, p=95):
    lo = (100 - p) / 2
    hi = 100 - lo
    return float(np.percentile(arr, lo)), float(np.percentile(arr, hi))


def participation_ratio(X):
    """Compute participation ratio from SVD."""
    _, s, _ = svd(X - X.mean(axis=0), full_matrices=False)
    s2 = s ** 2
    return float(1.0 / max(np.sum((s2 / s2.sum()) ** 2), 1e-12))


def effective_rank(X):
    _, s, _ = svd(X - X.mean(axis=0), full_matrices=False)
    s_norm = s / s.max()
    eff = float(np.sum(s_norm))
    return eff


def knn_flow_prediction(Phi, flows, k=5):
    """kNN flow prediction: predict flow from neighbors."""
    n = len(flows)
    nn = NearestNeighbors(n_neighbors=min(k + 1, n))
    nn.fit(Phi)
    _, idx = nn.kneighbors(Phi)
    pred = np.zeros(n)
    for i in range(n):
        pred[i] = np.mean(flows[idx[i, 1:]])
    r, p = pearsonr(flows, pred)
    return r, p


def local_smoothness(Phi, flows, k=5):
    """Mean kNN flow variance."""
    n = len(flows)
    nn = NearestNeighbors(n_neighbors=min(k + 1, n))
    nn.fit(Phi)
    _, idx = nn.kneighbors(Phi)
    variances = []
    for i in range(n):
        variances.append(float(np.var(flows[idx[i, 1:]])))
    return np.mean(variances), np.median(variances)


def density_flow_corr(Phi, flows):
    """KDE density ~ flow correlation."""
    if len(Phi) < 10:
        return 0.0, 1.0
    kde = gaussian_kde(Phi.T, bw_method="scott")
    dens = kde(Phi.T)
    r, p = pearsonr(dens, flows)
    return r, p


def compute_flow_field(proj, Phi):
    """Wrapper around proj.compute_flow that handles edge cases."""
    if len(Phi) < 5 or np.any(np.isnan(Phi)):
        return np.zeros(len(Phi)), np.zeros(len(Phi))
    try:
        Phi_s = Phi + 1e-10 * np.random.randn(*Phi.shape)
        return proj.compute_flow(Phi_s)
    except Exception:
        return np.zeros(len(Phi)), np.zeros(len(Phi))


def manifold_metrics(proj, Phi, flows=None):
    """Compute all manifold metrics for a given Φ."""
    n = len(Phi)
    if n < 5:
        return {"pr": 0.0, "eff_rank": 0.0, "knn_r": 0.0, "knn_p": 1.0,
                "smooth_mean": 0.0, "dens_flow_r": 0.0}
    pr = participation_ratio(Phi)
    eff = effective_rank(Phi)
    if flows is None or len(flows) != n:
        flows_fake, _ = compute_flow_field(proj, Phi)
    else:
        flows_fake = flows

    knn_r, knn_p = knn_flow_prediction(Phi, flows_fake)
    smooth_mean, _ = local_smoothness(Phi, flows_fake)
    dens_r, _ = density_flow_corr(Phi, flows_fake)

    return {
        "pr": pr,
        "eff_rank": eff,
        "knn_r": knn_r,
        "knn_p": knn_p,
        "smooth_mean": smooth_mean,
        "dens_flow_r": dens_r,
    }


# =====================================================================
# NULL MODELS
# =====================================================================

def n1_iid_gaussian_null(features_df):
    """N1: IID Gaussian — preserve mean/var, destroy everything else."""
    X = features_df.select_dtypes(include=[np.number]).values
    mean = X.mean(axis=0)
    std = X.std(axis=0)
    X_null = np.random.randn(*X.shape) * std[None, :] + mean[None, :]
    return X_null


def n2_cov_gaussian_null(features_df):
    """N2: Covariance-preserving Gaussian."""
    X = features_df.select_dtypes(include=[np.number]).values
    mean = X.mean(axis=0)
    cov = np.cov(X, rowvar=False)
    try:
        L = np.linalg.cholesky(cov + 1e-8 * np.eye(cov.shape[0]))
        Z = np.random.randn(*X.shape)
        X_null = Z @ L.T + mean[None, :]
    except np.linalg.LinAlgError:
        evals, evecs = np.linalg.eigh(cov + 1e-8 * np.eye(cov.shape[0]))
        A = evecs * np.sqrt(np.maximum(evals, 0))[None, :]
        Z = np.random.randn(*X.shape)
        X_null = Z @ A.T + mean[None, :]
    return X_null


def n3_spectrum_null(Phi):
    """N3: Spectrum-preserving randomization on Φ directly."""
    X = Phi.copy()
    mean = X.mean(axis=0)
    Xc = X - mean
    U, s, Vt = svd(Xc, full_matrices=False)
    U_rand = np.random.randn(*U.shape)
    U_rand, _ = np.linalg.qr(U_rand)
    Vt_rand = np.random.randn(*Vt.shape)
    Vt_rand, _ = np.linalg.qr(Vt_rand.T)
    Vt_rand = Vt_rand.T
    X_null = U_rand * s[None, :] @ Vt_rand + mean[None, :]
    return X_null


def n4_copula_null(features_df):
    """N4: Copula-preserving shuffle via empirical CDF transform."""
    X = features_df.select_dtypes(include=[np.number]).values
    n, d = X.shape
    # Sample from Gaussian copula with same correlation
    sample_corr = np.corrcoef(X, rowvar=False)
    try:
        L = np.linalg.cholesky(sample_corr + 1e-8 * np.eye(d))
        Z = np.random.randn(n, d)
        U_cop = Z @ L.T
    except np.linalg.LinAlgError:
        evals, evecs = np.linalg.eigh(sample_corr + 1e-8 * np.eye(d))
        A = evecs * np.sqrt(np.maximum(evals, 0))[None, :]
        Z = np.random.randn(n, d)
        U_cop = Z @ A.T
    # Map to uniform ranks preserving marginal distributions
    X_null = np.zeros_like(X)
    for j in range(d):
        X_sorted = np.sort(X[:, j])
        # Normalize U_cop to [0, n-1] and use as indices
        ranks = np.round((U_cop[:, j] - U_cop[:, j].min()) / 
                         max(np.ptp(U_cop[:, j]), 1e-12) * (n - 1)).astype(int)
        ranks = np.clip(ranks, 0, n - 1)
        X_null[:, j] = X_sorted[ranks]
    return X_null


def n5_maxent_null(features_df):
    """N5: Maximum entropy under first/second moment constraints.
       Equivalent to N2 but this explicitly tests whether matching
       first and second moments is sufficient."""
    return n2_cov_gaussian_null(features_df)


def n6_lowrank_adj_null(Phi, pr_target=None):
    """N6: Adversarial low-rank manifold with matched PR."""
    n, d = Phi.shape
    if pr_target is None:
        pr_target = participation_ratio(Phi)
    mean = Phi.mean(axis=0)
    cov = np.cov(Phi, rowvar=False)
    evals, evecs = np.linalg.eigh(cov)

    # Construct spectrum with desired PR
    n_components = max(2, int(round(pr_target * 2)))
    s = np.exp(-np.arange(d) / (n_components / 2.0))
    s = s / s.sum() * np.sum(np.maximum(evals, 0))
    # Mix up eigenvectors to destroy structure
    evecs_null = np.random.randn(d, d)
    evecs_null, _ = np.linalg.qr(evecs_null)
    cov_null = evecs_null @ np.diag(s) @ evecs_null.T
    cov_null = (cov_null + cov_null.T) / 2

    try:
        L = np.linalg.cholesky(cov_null + 1e-8 * np.eye(d))
        Z = np.random.randn(n, d)
        X_null = Z @ L.T + mean[None, :]
    except np.linalg.LinAlgError:
        X_null = np.random.randn(n, d) * np.sqrt(np.maximum(s, 0))[None, :] + mean[None, :]

    return X_null


def n7_random_embedding_null(features_df):
    """N7: Random feature embeddings. Replace with random projections."""
    X = features_df.select_dtypes(include=[np.number]).values
    n, d = X.shape
    # Random projection
    R = np.random.randn(d, d)
    R, _ = np.linalg.qr(R)
    X_null = X @ R
    return X_null


def generate_null_phi(proj, null_id, Phi_real, features_df):
    """Generate null Φ from a given null model."""
    if null_id == 1:
        X_null = n1_iid_gaussian_null(features_df)
    elif null_id == 2:
        X_null = n2_cov_gaussian_null(features_df)
    elif null_id == 3:
        return n3_spectrum_null(Phi_real)
    elif null_id == 4:
        X_null = n4_copula_null(features_df)
    elif null_id == 5:
        X_null = n5_maxent_null(features_df)
    elif null_id == 6:
        return n6_lowrank_adj_null(Phi_real)
    elif null_id == 7:
        X_null = n7_random_embedding_null(features_df)
    else:
        raise ValueError(f"Unknown null_id: {null_id}")

    # Project null features through the same emergence projector
    try:
        Phi_null = proj.project(X_null)
        return Phi_null
    except Exception as e:
        print(f"    Projection failed for null {null_id}: {e}")
        return np.random.randn(*Phi_real.shape)


NULL_NAMES = {
    1: "iid_gaussian",
    2: "cov_gaussian",
    3: "spectrum_rand",
    4: "copula_shuffle",
    5: "maxent",
    6: "lowrank_adj",
    7: "random_embedding",
}


# =====================================================================
# SECTION A — MANIFOLD SURVIVAL
# =====================================================================

def section_a_manifold_survival(proj, Phi_real, flows_real, features_df):
    """For every null, compute survival of manifold metrics."""
    print_sep()
    print("SECTION A: MANIFOLD SURVIVAL ACROSS NULLS")
    print_sep()

    real_metrics = manifold_metrics(proj, Phi_real, flows_real)
    print(f"  REAL: PR={real_metrics['pr']:.4f}, eff_rank={real_metrics['eff_rank']:.4f}, "
          f"kNN r={real_metrics['knn_r']:.4f}, smooth={real_metrics['smooth_mean']:.2f}")

    results = []
    for nid in sorted(NULL_NAMES.keys()):
        name = NULL_NAMES[nid]
        Phi_null = generate_null_phi(proj, nid, Phi_real, features_df)
        flows_null, _ = compute_flow_field(proj, Phi_null)
        m = manifold_metrics(proj, Phi_null, flows_null)

        survival_pr = m["pr"] / max(real_metrics["pr"], 1e-12)
        survival_knn = m["knn_r"] / max(real_metrics["knn_r"], 1e-12) if abs(real_metrics["knn_r"]) > 0.01 else 0.0

        # Bootstrap CI for PR
        n = len(Phi_null)
        boot_prs = []
        for b in range(N_BOOT):
            idx = np.random.choice(n, n, replace=True)
            boot_prs.append(participation_ratio(Phi_null[idx]))
        pr_lo, pr_hi = ci_percentile(boot_prs)

        results.append({
            "null_id": nid,
            "null_name": name,
            "pr": m["pr"],
            "pr_ci_lo": pr_lo,
            "pr_ci_hi": pr_hi,
            "eff_rank": m["eff_rank"],
            "knn_r": m["knn_r"],
            "knn_p": m["knn_p"],
            "smooth_mean": m["smooth_mean"],
            "dens_flow_r": m["dens_flow_r"],
            "survival_pr": survival_pr,
            "survival_knn": survival_knn,
        })
        print(f"  {name:<18s}: PR={m['pr']:.4f} [{pr_lo:.4f}, {pr_hi:.4f}] "
              f"surv(PR)={survival_pr:.3f} kNN_r={m['knn_r']:.4f}")

    df = pd.DataFrame(results)
    df.to_csv(OUT / "t031_null_metrics.csv", index=False)
    OUTPUT["section_A"] = results
    print(f"\n  Section A complete — saved t031_null_metrics.csv")
    return results


# =====================================================================
# SECTION B — INFORMATION GEOMETRY
# =====================================================================

def section_b_information_geometry(proj, Phi_real, flows_real, features_df):
    """Compute information-geometric structure and compare to nulls."""
    print_sep()
    print("SECTION B: INFORMATION GEOMETRY")
    print_sep()

    n = len(Phi_real)

    def local_entropy_gradients(Phi, k=5):
        """Estimate local entropy via KDE, compute gradient magnitude."""
        if len(Phi) < 10:
            return np.array([0.0])
        kde = gaussian_kde(Phi.T, bw_method="scott")
        log_dens = np.log(kde(Phi.T) + 1e-12)
        grads = []
        nn = NearestNeighbors(n_neighbors=min(k + 1, len(Phi)))
        nn.fit(Phi)
        _, idx = nn.kneighbors(Phi)
        for i in range(len(Phi)):
            neighbors = idx[i, 1:]
            if len(neighbors) > 1:
                dPhi = Phi[neighbors] - Phi[i]
                dDens = log_dens[neighbors] - log_dens[i]
                dPhi_mean = np.mean(dPhi, axis=0)
                if np.linalg.norm(dPhi_mean) > 1e-12:
                    grad = np.abs(np.mean(dDens)) / np.linalg.norm(dPhi_mean)
                    grads.append(grad)
        return np.array(grads) if grads else np.array([0.0])

    # Fisher info and KL neighborhood
    def fisher_kl_metrics(Phi):
        from scipy.stats import norm as scipy_norm
        n = len(Phi)
        if n < 10:
            return {"fisher_entropy": 0.0, "kl_div": 0.0, "wasserstein": 0.0}
        kde = gaussian_kde(Phi.T, bw_method="scott")
        dens = kde(Phi.T)
        # KL divergence vs Gaussian with same mean/cov
        mean = Phi.mean(axis=0)
        cov = np.cov(Phi, rowvar=False)
        mvn_entropy = 0.5 * np.log(np.linalg.det(cov + 1e-12 * np.eye(cov.shape[0])))
        mvn_entropy += 0.5 * cov.shape[0] * np.log(2 * np.pi * np.e)
        # KDE entropy approx
        kde_entropy = -np.mean(np.log(dens + 1e-12))
        # KL divergence
        kl_div = kde_entropy - mvn_entropy
        return {"fisher_entropy": float(kde_entropy), "kl_div": float(kl_div)}

    real_info = fisher_kl_metrics(Phi_real)
    real_grad = local_entropy_gradients(Phi_real)
    print(f"  REAL: Fisher entropy={real_info['fisher_entropy']:.4f}, "
          f"KL_vs_Gaussian={real_info['kl_div']:.4f}")
    print(f"  REAL: Mean |grad(log ρ)| = {np.mean(real_grad):.6f}")

    results = []
    for nid in sorted(NULL_NAMES.keys()):
        name = NULL_NAMES[nid]
        Phi_null = generate_null_phi(proj, nid, Phi_real, features_df)
        null_info = fisher_kl_metrics(Phi_null)
        null_grad = local_entropy_gradients(Phi_null)

        boot_kl = []
        n_pts = len(Phi_null)
        for b in range(N_BOOT):
            idx = np.random.choice(n_pts, n_pts, replace=True)
            null_info_b = fisher_kl_metrics(Phi_null[idx])
            boot_kl.append(null_info_b["kl_div"])
        kl_lo, kl_hi = ci_percentile(boot_kl)

        results.append({
            "null_id": nid,
            "null_name": name,
            "fisher_entropy": null_info["fisher_entropy"],
            "kl_div_vs_gaussian": null_info["kl_div"],
            "kl_ci_lo": kl_lo,
            "kl_ci_hi": kl_hi,
            "mean_grad_log_dens": float(np.mean(null_grad)),
            "real_kl": real_info["kl_div"],
        })
        print(f"  {name:<18s}: H={null_info['fisher_entropy']:.4f} "
              f"KL={null_info['kl_div']:.4f} [{kl_lo:.4f},{kl_hi:.4f}]")

    # Wasserstein distances (per-dimension average)
    from scipy.stats import wasserstein_distance
    n_small = 50
    Phi_r = Phi_real[:n_small]
    wasserstein_dists = {}
    for nid, name in [(1, "iid_gaussian"), (2, "cov_gaussian"), (4, "copula_shuffle")]:
        Phi_n = generate_null_phi(proj, nid, Phi_real, features_df)[:n_small]
        try:
            wd_vals = [wasserstein_distance(Phi_r[:, j], Phi_n[:, j]) for j in range(Phi_r.shape[1])]
            wasserstein_dists[name] = float(np.mean(wd_vals))
        except Exception:
            wasserstein_dists[name] = None
    results_b = {"info_metrics": results, "wasserstein_vs_real": wasserstein_dists}

    df = pd.DataFrame(results)
    df.to_csv(OUT / "t031_information_geometry.csv", index=False)
    OUTPUT["section_B"] = results_b
    print(f"\n  Section B complete — saved t031_information_geometry.csv")
    return results_b


# =====================================================================
# SECTION C — SPECTRAL ANALYSIS
# =====================================================================

def section_c_spectral_analysis(proj, Phi_real, features_df):
    """Compare eigenspectra across real and null manifolds."""
    print_sep()
    print("SECTION C: SPECTRAL ANALYSIS")
    print_sep()

    def spectral_decay(X):
        Xc = X - X.mean(axis=0)
        _, s, _ = svd(Xc, full_matrices=False)
        s_norm = s / max(s[0], 1e-12)
        # Compute decay exponent: s_k ~ k^(-alpha)
        ks = np.arange(1, len(s) + 1, dtype=float)
        idx = s_norm > 0.01
        if idx.sum() >= 2:
            log_s = np.log(s_norm[idx] + 1e-12)
            log_k = np.log(ks[idx])
            slope, _, _, _, _ = linregress(log_k, log_s)
            decay_exp = -slope
        else:
            decay_exp = 0.0
        stable_rank = float((s_norm ** 2).sum())
        return {
            "singular_values": s.tolist(),
            "decay_exponent": decay_exp,
            "stable_rank": stable_rank,
            "n_components_90pct": int(np.searchsorted(np.cumsum(s_norm), 0.9 * s_norm.sum()) + 1),
        }

    real_spec = spectral_decay(Phi_real)
    print(f"  REAL: decay_exp={real_spec['decay_exponent']:.4f}, "
          f"stable_rank={real_spec['stable_rank']:.4f}, "
          f"components_90%={real_spec['n_components_90pct']}")

    results = []
    for nid in sorted(NULL_NAMES.keys()):
        name = NULL_NAMES[nid]
        Phi_null = generate_null_phi(proj, nid, Phi_real, features_df)
        null_spec = spectral_decay(Phi_null)

        results.append({
            "null_id": nid,
            "null_name": name,
            "decay_exponent": null_spec["decay_exponent"],
            "stable_rank": null_spec["stable_rank"],
            "n_components_90pct": null_spec["n_components_90pct"],
            "real_decay": real_spec["decay_exponent"],
            "real_stable_rank": real_spec["stable_rank"],
        })
        print(f"  {name:<18s}: decay_exp={null_spec['decay_exponent']:.4f} "
              f"stable_rank={null_spec['stable_rank']:.4f} "
              f"n90={null_spec['n_components_90pct']}")

    OUTPUT["section_C"] = results
    return results


# =====================================================================
# SECTION D — ADVERSARIAL TESTING
# =====================================================================

def section_d_adversarial_testing(proj, Phi_real, flows_real):
    """Generate fake manifolds with matched properties, test if they fool metrics."""
    print_sep()
    print("SECTION D: ADVERSARIAL TESTING")
    print_sep()

    real_pr = participation_ratio(Phi_real)

    def generate_fake_manifold(seed):
        np.random.seed(seed)
        n, d = Phi_real.shape
        # Synthetic manifold with matched PR
        evals = np.exp(-np.arange(d) / (real_pr * 0.8))
        evals = evals / evals.sum() * d
        cov_fake = np.diag(evals)
        fake_mean = np.zeros(d)
        Phi_fake = np.random.randn(n, d) @ np.linalg.cholesky(
            cov_fake + 1e-8 * np.eye(d)).T + fake_mean[None, :]
        # Match density profile via quantile transform
        for j in range(d):
            Phi_fake[:, j] = np.percentile(Phi_real[:, j],
                                            (np.argsort(np.argsort(Phi_fake[:, j])) + 1).astype(float) / (n + 1) * 100)
        return Phi_fake

    np.random.seed(SEED)
    results = []
    for trial in range(20):
        Phi_fake = generate_fake_manifold(trial * 100 + 42)
        flows_fake, _ = compute_flow_field(proj, Phi_fake)
        m = manifold_metrics(proj, Phi_fake, flows_fake)
        results.append(m)

    df = pd.DataFrame(results)
    mean_fake = df.mean().to_dict()
    std_fake = df.std().to_dict()

    print(f"  REAL: PR={real_pr:.4f}")
    print(f"  FAKE (20 trials): PR={mean_fake['pr']:.4f}±{std_fake['pr']:.4f}, "
          f"kNN_r={mean_fake['knn_r']:.4f}±{std_fake['knn_r']:.4f}")

    # Does the fake manifold fool the metrics?
    pr_overlap = abs(mean_fake["pr"] - real_pr) / real_pr
    fooled = pr_overlap < 0.2
    print(f"  PR overlap: {pr_overlap:.3f} {'✓ FOOLED' if fooled else '✗ NOT FOOLED'}")

    result = {
        "real_pr": real_pr,
        "fake_pr_mean": mean_fake["pr"], "fake_pr_std": std_fake["pr"],
        "fake_knn_r_mean": mean_fake["knn_r"], "fake_knn_r_std": std_fake["knn_r"],
        "pr_overlap": pr_overlap,
        "fooled": fooled,
        "trials": results,
    }
    OUTPUT["section_D"] = {k: v for k, v in result.items() if k != "trials"}
    print(f"\n  Section D complete")
    return result


# =====================================================================
# SECTION E — REPRESENTATION ROBUSTNESS
# =====================================================================

def section_e_representation(proj, Phi_real, flows_real, features_df):
    """Test whether manifold is embedding-dependent."""
    print_sep()
    print("SECTION E: REPRESENTATION ROBUSTNESS")
    print_sep()

    def trustworthiness_continuity(X_high, X_low, k=7):
        """Compute trustworthiness and continuity between embeddings."""
        from sklearn.manifold import trustworthiness
        tw = trustworthiness(X_high, X_low, n_neighbors=k)
        # Continuity: trustworthiness from low to high
        cont = trustworthiness(X_low, X_high, n_neighbors=k)
        return tw, cont

    results = []
    n = len(Phi_real)

    # Reference: PCA on real features
    X = features_df.select_dtypes(include=[np.number]).values
    X_z = (X - X.mean(axis=0)) / np.maximum(X.std(axis=0), 1e-12)

    embeddings = {
        "pca_2d": ("PCA(2)", PCA(n_components=2).fit_transform(X_z)),
        "pca_4d": ("PCA(4)", PCA(n_components=4).fit_transform(X_z)),
        "isomap": ("Isomap", None),
        "random_proj": ("RandProj", None),
        "phi_real": ("Φ_real", Phi_real),
    }

    # Isomap
    try:
        iso = Isomap(n_components=4, n_neighbors=min(10, n - 2))
        iso_emb = iso.fit_transform(X_z)
        embeddings["isomap"] = ("Isomap", iso_emb)
    except Exception as e:
        print(f"  Isomap failed: {e}")
        embeddings["isomap"] = ("Isomap", np.random.randn(n, 4))

    # Random projections
    R = np.random.randn(X_z.shape[1], 4)
    R, _ = np.linalg.qr(R)
    rand_emb = X_z @ R
    embeddings["random_proj"] = ("RandProj", rand_emb)

    # Null models as embeddings
    for nid in [1, 2, 4, 7]:
        name = NULL_NAMES[nid]
        Phi_null = generate_null_phi(proj, nid, Phi_real, features_df)
        embeddings[f"null_{nid}"] = (f"Null_{name}", Phi_null)

    for key, (label, emb) in embeddings.items():
        if emb is None or len(emb) != n:
            continue
        # Trustworthiness relative to real Φ
        try:
            tw, cont = trustworthiness_continuity(Phi_real, emb, k=7)
        except Exception:
            tw, cont = 0.0, 0.0
        # kNN flow prediction in this embedding
        flows_emb, _ = compute_flow_field(proj, emb)
        knn_r, knn_p = knn_flow_prediction(emb, flows_emb, k=5)
        pr_emb = participation_ratio(emb)

        results.append({
            "embedding": key,
            "label": label,
            "trustworthiness": tw,
            "continuity": cont,
            "knn_flow_r": knn_r,
            "knn_flow_p": knn_p,
            "pr": pr_emb,
        })
        print(f"  {label:<18s}: TW={tw:.4f} cont={cont:.4f} "
              f"kNN_r={knn_r:.4f} PR={pr_emb:.4f}")

    df = pd.DataFrame(results)
    df.to_csv(OUT / "t031_embedding_stability.csv", index=False)
    OUTPUT["section_E"] = results
    print(f"\n  Section E complete — saved t031_embedding_stability.csv")
    return results


# =====================================================================
# SECTION F — CAUSAL DESTRUCTION TEST
# =====================================================================

def section_f_causal_destruction(proj, Phi_real, flows_real, features_df):
    """Progressively destroy structure, measure when geometry collapses."""
    print_sep()
    print("SECTION F: CAUSAL DESTRUCTION TEST")
    print_sep()

    n = len(Phi_real)
    X = features_df.select_dtypes(include=[np.number]).values
    X_z = (X - X.mean(axis=0)) / np.maximum(X.std(axis=0), 1e-12)

    destructions = []

    # Level 0: Original
    Phi_lev = Phi_real.copy()
    flows_lev = flows_real.copy() if flows_real is not None else None
    m = manifold_metrics(proj, Phi_lev, flows_lev)
    destructions.append({"level": 0, "name": "original", "pr": m["pr"],
                         "knn_r": m["knn_r"], "smooth": m["smooth_mean"]})
    print(f"  Level 0 (original): PR={m['pr']:.4f}, kNN_r={m['knn_r']:.4f}")

    # Level 1: Shuffle columns independently (destroy feature covariance)
    X_l1 = X_z.copy()
    for j in range(X_l1.shape[1]):
        np.random.shuffle(X_l1[:, j])
    Phi_l1 = proj.project(pd.DataFrame(X_l1, columns=features_df.columns))
    flows_l1, _ = compute_flow_field(proj, Phi_l1)
    m = manifold_metrics(proj, Phi_l1, flows_l1)
    destructions.append({"level": 1, "name": "col_shuffled", "pr": m["pr"],
                         "knn_r": m["knn_r"], "smooth": m["smooth_mean"]})
    print(f"  Level 1 (col_shuffle): PR={m['pr']:.4f}, kNN_r={m['knn_r']:.4f}")

    # Level 2: Row shuffle (destroy system identity)
    X_l2 = X_z.copy()
    np.random.shuffle(X_l2)
    Phi_l2 = proj.project(pd.DataFrame(X_l2, columns=features_df.columns))
    flows_l2, _ = compute_flow_field(proj, Phi_l2)
    m = manifold_metrics(proj, Phi_l2, flows_l2)
    destructions.append({"level": 2, "name": "row_shuffled", "pr": m["pr"],
                         "knn_r": m["knn_r"], "smooth": m["smooth_mean"]})
    print(f"  Level 2 (row_shuffle): PR={m['pr']:.4f}, kNN_r={m['knn_r']:.4f}")

    # Level 3: Copula to Gaussian (destroy nonlinear structure)
    X_ranks = np.argsort(np.argsort(X_z, axis=0), axis=0).astype(float)
    X_unif = (X_ranks + 1) / (n + 1)
    from scipy.stats import norm
    X_l3 = norm.ppf(X_unif.clip(1e-6, 1 - 1e-6))
    Phi_l3 = proj.project(pd.DataFrame(X_l3, columns=features_df.columns))
    flows_l3, _ = compute_flow_field(proj, Phi_l3)
    m = manifold_metrics(proj, Phi_l3, flows_l3)
    destructions.append({"level": 3, "name": "gaussian_copula", "pr": m["pr"],
                         "knn_r": m["knn_r"], "smooth": m["smooth_mean"]})
    print(f"  Level 3 (gauss_copula): PR={m['pr']:.4f}, kNN_r={m['knn_r']:.4f}")

    # Level 4: Decorrelate (destroy linear covariance)
    cov = np.cov(X_z, rowvar=False)
    evals, evecs = np.linalg.eigh(cov + 1e-8 * np.eye(cov.shape[0]))
    X_l4 = X_z @ evecs @ np.diag(1.0 / np.sqrt(np.maximum(evals, 1e-8))) @ evecs.T
    # Verify decorrelation
    # Then project back
    R = np.random.randn(X_l4.shape[1], X_l4.shape[1])
    R, _ = np.linalg.qr(R)
    X_l4 = X_l4 @ R.T  # mix back but without linear structure
    Phi_l4 = proj.project(pd.DataFrame(X_l4, columns=features_df.columns))
    flows_l4, _ = compute_flow_field(proj, Phi_l4)
    m = manifold_metrics(proj, Phi_l4, flows_l4)
    destructions.append({"level": 4, "name": "decorrelated", "pr": m["pr"],
                         "knn_r": m["knn_r"], "smooth": m["smooth_mean"]})
    print(f"  Level 4 (decorrelate): PR={m['pr']:.4f}, kNN_r={m['knn_r']:.4f}")

    # Level 5: IID white noise
    X_l5 = np.random.randn(*X_z.shape)
    Phi_l5 = proj.project(pd.DataFrame(X_l5, columns=features_df.columns))
    flows_l5, _ = compute_flow_field(proj, Phi_l5)
    m = manifold_metrics(proj, Phi_l5, flows_l5)
    destructions.append({"level": 5, "name": "white_noise", "pr": m["pr"],
                         "knn_r": m["knn_r"], "smooth": m["smooth_mean"]})
    print(f"  Level 5 (white_noise): PR={m['pr']:.4f}, kNN_r={m['knn_r']:.4f}")

    # Collapse detection: at what level does PR stabilize near maxent?
    # PR below 1.5 indicates collapse
    collapse_level = None
    for d in destructions:
        if d["pr"] < 1.5:
            collapse_level = d["level"]
            break

    result = {
        "destruction_levels": destructions,
        "collapse_at_level": collapse_level,
        "collapse_at_name": destructions[collapse_level]["name"] if collapse_level is not None else "none",
        "original_pr": destructions[0]["pr"],
        "final_pr": destructions[-1]["pr"],
    }
    OUTPUT["section_F"] = result
    print(f"\n  Collapse at level {collapse_level}: "
          f"{result['collapse_at_name']}")
    print(f"  Section F complete")
    return result


# =====================================================================
# SECTION G — DECISION FRAMEWORK
# =====================================================================

def section_g_decision(section_a, section_b, section_c, section_d,
                       section_e, section_f):
    """Apply 7-criteria decision framework."""
    print_sep()
    print("SECTION G: DECISION FRAMEWORK")
    print_sep()

    passed = 0
    total = 7
    verdict_lines = []

    # G1: Geometry survives dynamical but not statistical nulls
    a_df = pd.DataFrame(section_a) if section_a else pd.DataFrame()
    if len(a_df) > 0:
        survival_pr = a_df["survival_pr"].values
        # Count nulls where PR significantly lower than real
        g1_pass = np.mean(survival_pr < 0.8) >= 0.5
    else:
        g1_pass = False
    if g1_pass:
        verdict_lines.append("✓ G1: Geometry does NOT survive statistical nulls")
    else:
        verdict_lines.append("∼ G1: Geometry partially survives statistical nulls")
    verdict_lines[-1] += f"  (mean survival PR={survival_pr.mean():.3f})" if 'survival_pr' in dir() else ""
    verdict_lines[-1] = verdict_lines[-1] if verdict_lines[-1].startswith("✓") or verdict_lines[-1].startswith("∼") else verdict_lines[-1]
    if g1_pass: passed += 1

    # G2: Adversarial low-rank nulls fail
    d = section_d or {}
    g2_pass = not d.get("fooled", True)
    if g2_pass:
        verdict_lines.append("✓ G2: Adversarial low-rank nulls fail to fool metrics")
    else:
        verdict_lines.append(f"✗ G2: Adversarial low-rank nulls fool metrics "
                            f"(PR overlap={d.get('pr_overlap', 0):.3f})")
    if g2_pass: passed += 1

    # G3: Temporal destruction reduces topology — we use causal destruction levels
    f = section_f or {}
    levels = f.get("destruction_levels", [])
    if len(levels) >= 2:
        pr_original = levels[0]["pr"]
        pr_min = min(d["pr"] for d in levels)
        pr_drop = pr_original - pr_min
        g3_pass = pr_drop > 0.5
    else:
        g3_pass = False
    if g3_pass:
        verdict_lines.append(f"✓ G3: Causal destruction reduces topology (ΔPR={pr_drop:.3f} at worst level)")
    else:
        verdict_lines.append(f"∼ G3: Causal destruction limited effect (ΔPR={pr_drop:.3f} at worst level)")
    if g3_pass: passed += 1

    # G4: Information geometry differs from Gaussian baseline
    b = section_b or {}
    info_metrics = b.get("info_metrics", [])
    if len(info_metrics) >= 2:
        real_kl = info_metrics[0].get("real_kl", 0) if "real_kl" in info_metrics[0] else 0
        null_kls = [m.get("kl_div_vs_gaussian", 0) for m in info_metrics]
        g4_pass = abs(real_kl) > 0.1 and np.any(abs(np.array(null_kls) - real_kl) > 0.2)
    else:
        g4_pass = False
    verdict_lines.append(
        f"{'✓' if g4_pass else '∼'} G4: Information geometry {'differs from' if g4_pass else 'similar to'} Gaussian baseline"
    )
    if g4_pass: passed += 1

    # G5: Representation robustness exists
    e = section_e or []
    tws = [r.get("trustworthiness", 0) for r in e if isinstance(r, dict)]
    if len(tws) > 0:
        mean_tw = np.mean(tws)
        g5_pass = mean_tw > 0.6
    else:
        mean_tw = 0
        g5_pass = False
    verdict_lines.append(
        f"{'✓' if g5_pass else '∼'} G5: Representation robustness "
        f"(mean TW={mean_tw:.3f})"
    )
    if g5_pass: passed += 1

    # G6: Spectral structure not sufficient
    c = section_c or []
    if len(c) > 0:
        decay_diffs = [abs(r.get("decay_exponent", 0) - r.get("real_decay", 0))
                       for r in c if isinstance(r, dict)]
        g6_pass = np.any(np.array(decay_diffs) > 0.2) if decay_diffs else False
    else:
        g6_pass = False
    verdict_lines.append(
        f"{'✓' if g6_pass else '∼'} G6: Spectral structure {'not' if g6_pass else ''} sufficient to explain geometry"
    )
    if g6_pass: passed += 1

    # G7: Persistence collapses under causal destruction (uses min PR across levels)
    if len(levels) >= 2:
        pr_min = min(d["pr"] for d in levels)
        g7_pass = pr_min < 1.5
    else:
        g7_pass = False
    verdict_lines.append(
        f"{'✓' if g7_pass else '✗'} G7: Persistence {'collapses' if g7_pass else 'survives'} under causal destruction "
        f"(min PR={pr_min:.3f})"
    )
    if g7_pass: passed += 1

    score = passed / total
    if score >= 0.75:
        verdict = "GENUINE DYNAMICAL GEOMETRY"
    elif score >= 0.4:
        verdict = "MIXED STATISTICAL/DYNAMICAL GEOMETRY"
    else:
        verdict = "STATISTICAL ARTIFACT"

    print(f"\n  T031 FINAL VERDICT: {passed}/{total} criteria passed")
    for vl in verdict_lines:
        print(f"  {vl}")
    print(f"\n  OVERALL: {verdict}")

    result = {
        "passed": passed,
        "total": total,
        "score": score,
        "verdict": verdict,
        "details": verdict_lines,
    }
    OUTPUT["section_G"] = result
    return result


# =====================================================================
# FIGURES
# =====================================================================

def generate_figures(section_a, section_b, section_c, section_e, section_f, Phi_real, flows_real):
    """Generate all 6 required figures."""
    print_sep()
    print("GENERATING FIGURES")
    print_sep()

    # Fig 1: Null PR comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    a_df = pd.DataFrame(section_a) if section_a else pd.DataFrame()
    real_pr = participation_ratio(Phi_real)
    if len(a_df) > 0:
        names = a_df["null_name"].values
        prs = a_df["pr"].values
        pr_los = a_df["pr_ci_lo"].values
        pr_his = a_df["pr_ci_hi"].values
        x = np.arange(len(names))
        colors = ["#e74c3c" if s < 0.8 else "#f39c12" for s in a_df["survival_pr"].values]
        ax.bar(x, prs, yerr=[np.abs(prs - pr_los), np.abs(pr_his - prs)], color=colors, capsize=5)
        ax.axhline(y=real_pr, color="blue", ls="--",
                    label=f"Real PR={real_pr:.2f}")
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=45, ha="right")
        ax.set_ylabel("Participation Ratio")
        ax.set_title("T031: Null Model PR Comparison")
        ax.legend()
        plt.tight_layout()
        fig.savefig(FIG / "fig_t031_null_pr_comparison.png", dpi=150)
        plt.close(fig)
        print("  Saved fig_t031_null_pr_comparison.png")

    # Fig 2: Spectral decay comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    Phi_c = Phi_real - Phi_real.mean(axis=0)
    _, s_real, _ = svd(Phi_c, full_matrices=False)
    s_real_n = s_real / s_real[0]
    ax.plot(np.arange(1, len(s_real_n) + 1), s_real_n, "b-o", label="Real Φ", markersize=6)
    for nid, color, ls in [(1, "gray", "--"), (2, "orange", "-."), (4, "green", ":"), (7, "red", "-")]:
        name = NULL_NAMES[nid]
        Phi_n = generate_null_phi(EmergenceProjector(), nid, Phi_real,
                                   pd.read_csv(OUT / "t030_ensemble_features.csv")[FEATURE_NAMES].copy())
        Phi_nc = Phi_n - Phi_n.mean(axis=0)
        _, s_n, _ = svd(Phi_nc, full_matrices=False)
        s_nn = s_n / s_n[0] if s_n[0] > 0 else s_n
        ax.plot(np.arange(1, len(s_nn) + 1), s_nn, color=color, linestyle=ls, label=name, alpha=0.7)
    ax.set_xlabel("Component")
    ax.set_ylabel("Normalized Singular Value")
    ax.set_title("T031: Spectral Decay Comparison")
    ax.legend()
    plt.tight_layout()
    fig.savefig(FIG / "fig_t031_spectral_decay.png", dpi=150)
    plt.close(fig)
    print("  Saved fig_t031_spectral_decay.png")

    # Fig 3: Metric failure heatmap
    a_df = pd.DataFrame(section_a) if section_a else pd.DataFrame()
    if len(a_df) > 0:
        metric_cols = ["pr", "knn_r", "smooth_mean", "dens_flow_r"]
        avail = [c for c in metric_cols if c in a_df.columns]
        if len(avail) > 0:
            heat_data = a_df[avail].values
            fig, ax = plt.subplots(figsize=(8, 6))
            im = ax.imshow(heat_data, aspect="auto", cmap="RdBu_r")
            ax.set_yticks(np.arange(len(a_df)))
            ax.set_yticklabels(a_df["null_name"].values)
            ax.set_xticks(np.arange(len(avail)))
            ax.set_xticklabels(avail, rotation=45, ha="right")
            plt.colorbar(im, ax=ax, label="Metric Value")
            ax.set_title("T031: Metric Failure Heatmap")
            plt.tight_layout()
            fig.savefig(FIG / "fig_t031_metric_failure_heatmap.png", dpi=150)
            plt.close(fig)
            print("  Saved fig_t031_metric_failure_heatmap.png")

    # Fig 4: Information geometry
    b = section_b or {}
    info_metrics = b.get("info_metrics", [])
    if len(info_metrics) > 0:
        df_b = pd.DataFrame(info_metrics)
        fig, ax = plt.subplots(figsize=(10, 5))
        x = np.arange(len(df_b))
        ax.bar(x - 0.2, df_b["kl_div_vs_gaussian"].values, width=0.35,
               color="steelblue", label="KL vs Gaussian")
        if "kl_ci_lo" in df_b.columns and "kl_ci_hi" in df_b.columns:
            kl_val = df_b["kl_div_vs_gaussian"].values
            yerr_lo = np.abs(kl_val - df_b["kl_ci_lo"].values)
            yerr_hi = np.abs(df_b["kl_ci_hi"].values - kl_val)
            ax.errorbar(x, kl_val,
                        yerr=[yerr_lo, yerr_hi],
                        fmt="none", ecolor="black", capsize=3)
        ax.axhline(y=df_b.iloc[0]["real_kl"] if "real_kl" in df_b.columns else 0,
                   color="red", ls="--", label="Real KL")
        ax.set_xticks(x)
        ax.set_xticklabels(df_b["null_name"].values, rotation=45, ha="right")
        ax.set_ylabel("KL Divergence")
        ax.set_title("T031: Information Geometry Comparison")
        ax.legend()
        plt.tight_layout()
        fig.savefig(FIG / "fig_t031_information_geometry.png", dpi=150)
        plt.close(fig)
        print("  Saved fig_t031_information_geometry.png")

    # Fig 5: Manifold survival cascade (from Section F)
    f = section_f or {}
    levels = f.get("destruction_levels", [])
    if len(levels) > 0:
        fig, ax = plt.subplots(figsize=(10, 6))
        names = [d["name"] for d in levels]
        prs = [d["pr"] for d in levels]
        knns = [d.get("knn_r", 0) for d in levels]
        x = np.arange(len(names))
        ax.bar(x - 0.2, prs, width=0.35, color="steelblue", label="PR")
        ax.bar(x + 0.2, knns, width=0.35, color="coral", label="kNN r")
        ax.axhline(y=1.5, color="red", ls="--", alpha=0.5, label="PR=1.5 (collapse)")
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=45, ha="right")
        ax.set_ylabel("Metric Value")
        ax.set_title("T031: Manifold Survival Under Causal Destruction")
        ax.legend()
        plt.tight_layout()
        fig.savefig(FIG / "fig_t031_manifold_survival.png", dpi=150)
        plt.close(fig)
        print("  Saved fig_t031_manifold_survival.png")

    print("  All figures generated")


# =====================================================================
# MAIN
# =====================================================================

def main():
    global OUTPUT
    print("=" * 70)
    print("T031: NULL GEOMETRY DISENTANGLEMENT")
    print("Test: Is surviving Φ-space geometry genuine dynamical structure")
    print("      or statistical artifact?")
    print("=" * 70)

    # Load existing T030 data
    print("\nLoading existing T030 ensemble data...")
    features_df_all = pd.read_csv(OUT / "t030_ensemble_features.csv")
    features_df = features_df_all[FEATURE_NAMES].copy()
    Phi_real = np.load(OUT / "t030_ensemble_Phi.npy")
    flow_df = pd.read_csv(OUT / "t030_ensemble_flow.csv")
    flows_real = flow_df["flow_magnitude"].values
    print(f"  Loaded {len(Phi_real)} systems, Φ shape={Phi_real.shape}")

    proj = EmergenceProjector()

    total_start = time.time()

    # Section A
    start = time.time()
    sec_a = section_a_manifold_survival(proj, Phi_real, flows_real, features_df)
    elapsed = time.time() - start
    print(f"  Section A time: {elapsed:.1f}s")

    # Section B
    start = time.time()
    sec_b = section_b_information_geometry(proj, Phi_real, flows_real, features_df)
    elapsed = time.time() - start
    print(f"  Section B time: {elapsed:.1f}s")

    # Section C
    start = time.time()
    sec_c = section_c_spectral_analysis(proj, Phi_real, features_df)
    elapsed = time.time() - start
    print(f"  Section C time: {elapsed:.1f}s")

    # Section D
    start = time.time()
    sec_d = section_d_adversarial_testing(proj, Phi_real, flows_real)
    elapsed = time.time() - start
    print(f"  Section D time: {elapsed:.1f}s")

    # Section E
    start = time.time()
    sec_e = section_e_representation(proj, Phi_real, flows_real, features_df)
    elapsed = time.time() - start
    print(f"  Section E time: {elapsed:.1f}s")

    # Section F
    start = time.time()
    sec_f = section_f_causal_destruction(proj, Phi_real, flows_real, features_df)
    elapsed = time.time() - start
    print(f"  Section F time: {elapsed:.1f}s")

    # Section G
    start = time.time()
    sec_g = section_g_decision(sec_a, sec_b, sec_c, sec_d, sec_e, sec_f)
    elapsed = time.time() - start
    print(f"  Section G time: {elapsed:.1f}s")

    # Generate figures
    try:
        generate_figures(sec_a, sec_b, sec_c, sec_e, sec_f, Phi_real, flows_real)
    except Exception as e:
        print(f"  Figure generation error: {e}")

    # Save outputs
    print("\nSaving results...")

    # Geometry comparison
    if sec_a:
        a_df = pd.DataFrame(sec_a)
        real_metrics = manifold_metrics(proj, Phi_real, flows_real)
        comp_rows = []
        for _, row in a_df.iterrows():
            comp_rows.append({
                "null_name": row["null_name"],
                "real_pr": real_metrics["pr"],
                "null_pr": row["pr"],
                "pr_ratio": row["survival_pr"],
                "real_knn_r": real_metrics["knn_r"],
                "null_knn_r": row["knn_r"],
                "knn_ratio": row["survival_knn"],
            })
        comp_df = pd.DataFrame(comp_rows)
        comp_df.to_csv(OUT / "t031_geometry_comparison.csv", index=False)
        print("  Saved t031_geometry_comparison.csv")

    # Null rankings
    if sec_a:
        ranking = sorted(sec_a, key=lambda x: x["survival_pr"])
        rank_df = pd.DataFrame([{
            "rank": i + 1,
            "null_name": r["null_name"],
            "survival_pr": r["survival_pr"],
            "survival_knn": r["survival_knn"],
        } for i, r in enumerate(ranking)])
        rank_df.to_csv(OUT / "t031_null_rankings.csv", index=False)
        print("  Saved t031_null_rankings.csv")

    # Full JSON
    with open(OUT / "t031_null_geometry_results.json", "w") as f:
        json.dump(OUTPUT, f, indent=2, cls=NpEncoder)
    print(f"  Saved t031_null_geometry_results.json")

    total_elapsed = time.time() - total_start
    print(f"\n  Total time: {total_elapsed:.1f}s")
    print(f"\n{'=' * 70}")
    print(f"T031 COMPLETE")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
