"""RD-8A: Latent Geometry Recon — PCA, FA, UMAP, Clustering, Intrinsic Dimensionality
Uses the t901 backbone (60 runs × 12 metrics) + RD-8 physical observables at matched friction.
"""

import sys, os, json
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings("ignore")

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# ─── Load data ───
M = np.load("audits/rd8a_matrix_t901.npy")
with open("audits/rd8a_metric_names_t901.json") as f:
    metric_names = json.load(f)
with open("audits/rd8a_row_metadata.json") as f:
    metadata = json.load(f)

# Also load RD-8 for physical observables
with open("audits/rd08_friction_sweep.json") as f:
    rd08 = json.load(f)

# Match RD-8 runs to t901 by closest friction
rd08_by_fr = {}
for r in rd08:
    fr = round(r["friction"], 2)
    if fr not in rd08_by_fr:
        rd08_by_fr[fr] = []
    rd08_by_fr[fr].append(r)

# Build expanded matrix: t901 metrics + RD-8 physical observables where available
t901_frs = [m["friction"] for m in metadata]
expanded_names = metric_names + ["jitter", "persistence", "reorg_rate", "v_autocorr", "separation"]
M_expanded = []
expanded_meta = []

for i, (row, meta) in enumerate(zip(M, metadata)):
    fr = meta["friction"]
    # Find closest RD-8 friction
    best_fr = min(rd08_by_fr.keys(), key=lambda x: abs(x - fr))
    if abs(best_fr - fr) < 0.05 and len(rd08_by_fr[best_fr]) > meta["rep"]:
        r8 = rd08_by_fr[best_fr][meta["rep"]]
        exp_row = list(row) + [r8["jitter"], r8["persistence"],
                                r8["reorg_rate"], r8["v_autocorr"], r8["separation"]]
        M_expanded.append(exp_row)
        expanded_meta.append(meta)
    else:
        # Fill with NaN for RD-8 metrics
        exp_row = list(row) + [np.nan]*5
        M_expanded.append(exp_row)
        expanded_meta.append(meta)

M_expanded = np.array(M_expanded, dtype=float)
print(f"Expanded matrix: {M_expanded.shape[0]} rows × {M_expanded.shape[1]} columns")
print(f"Metrics: {expanded_names}")

# For PCA: use only columns with <20% NaN
nan_frac = np.mean(np.isnan(M_expanded), axis=0)
good_cols = nan_frac < 0.2
print(f"\nColumns with <20% NaN: {[expanded_names[i] for i in range(len(expanded_names)) if good_cols[i]]}")

# ─── Standardize ───
M_use = M_expanded[:, good_cols].copy()
names_use = [expanded_names[i] for i in range(len(expanded_names)) if good_cols[i]]

# Impute NaN with column mean (conservative)
for j in range(M_use.shape[1]):
    col = M_use[:, j]
    nan_mask = np.isnan(col)
    if np.any(nan_mask):
        col[nan_mask] = np.nanmean(col)

# Standardize
M_std = (M_use - np.mean(M_use, axis=0)) / np.std(M_use, axis=0)

print(f"\nAnalysis matrix: {M_std.shape[0]} × {M_std.shape[1]}")
print(f"Metrics: {names_use}")

# ═══════════════════════════════════════════════════════════════════════════
# 1. PCA
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("1. PCA — How many dimensions exist?")
print("=" * 80)

cov = np.cov(M_std.T)
eigvals, eigvecs = np.linalg.eigh(cov)
eigvals = eigvals[::-1]
eigvecs = eigvecs[:, ::-1]

explained = eigvals / np.sum(eigvals)
cumulative = np.cumsum(explained)

print(f"\n{'PC':>4s} {'Eigenvalue':>12s} {'Explained%':>12s} {'Cumulative%':>12s}")
print("-" * 44)
for i in range(len(eigvals)):
    marker = " ← 90%" if cumulative[i] >= 0.90 and (i == 0 or cumulative[i-1] < 0.90) else ""
    marker = " ← 80%" if cumulative[i] >= 0.80 and (i == 0 or cumulative[i-1] < 0.80) else marker
    print(f"PC{i+1:>2d} {eigvals[i]:>12.4f} {explained[i]*100:>11.1f}% {cumulative[i]*100:>11.1f}%{marker}")

# How many for 90%?
n_90 = np.searchsorted(cumulative, 0.90) + 1
n_80 = np.searchsorted(cumulative, 0.80) + 1
n_95 = np.searchsorted(cumulative, 0.95) + 1
print(f"\nDimensions for 80% variance: {n_80}")
print(f"Dimensions for 90% variance: {n_90}")
print(f"Dimensions for 95% variance: {n_95}")

# ─── Loading tables ───
print("\n--- PCA Loadings ---")
for pc in range(min(n_90 + 1, len(names_use))):
    loadings = eigvecs[:, pc]
    sorted_idx = np.argsort(np.abs(loadings))[::-1]
    print(f"\nPC{pc+1} ({explained[pc]*100:.1f}%):")
    for idx in sorted_idx[:8]:
        print(f"    {names_use[idx]:>20s}: {loadings[idx]:+.4f}")

# ═══════════════════════════════════════════════════════════════════════════
# 2. FACTOR ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("2. FACTOR ANALYSIS — Latent axis identification")
print("=" * 80)

from sklearn.decomposition import FactorAnalysis

best_bic = np.inf
best_n = 1
fa_results = {}

for n_factors in range(1, min(n_90 + 3, len(names_use))):
    fa = FactorAnalysis(n_components=n_factors, random_state=42, max_iter=1000)
    fa.fit(M_std)
    
    # BIC approximation (negative log-likelihood)
    loglike = fa.score(M_std) * M_std.shape[0]
    n_params = n_factors * M_std.shape[1] + M_std.shape[1]  # loadings + noise
    bic = -2 * loglike + n_params * np.log(M_std.shape[0])
    
    fa_results[n_factors] = {
        "bic": bic,
        "loadings": fa.components_.T,
        "noise": fa.noise_variance_,
        "explained": 1 - fa.noise_variance_.mean() / np.var(M_std, axis=0).mean()
    }
    
    print(f"\nFactors={n_factors}: BIC={bic:.1f}, est. variance explained={fa_results[n_factors]['explained']:.1%}")
    
    if bic < best_bic:
        best_bic = bic
        best_n = n_factors

print(f"\n>>> Best factor model: {best_n} factors (BIC={best_bic:.1f})")

# Print loadings for best model
fa_best = FactorAnalysis(n_components=best_n, random_state=42, max_iter=1000)
fa_best.fit(M_std)
print(f"\n--- Factor Loadings ({best_n} factors) ---")
header = "".join(f"{'F'+str(i+1):>10s}" for i in range(best_n))
print(f"{'Metric':>20s}{header}")
for i, name in enumerate(names_use):
    row = "".join(f"{fa_best.components_[j, i]:>10.3f}" for j in range(best_n))
    print(f"{name:>20s}{row}")

# ═══════════════════════════════════════════════════════════════════════════
# 3. UMAP
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("3. UMAP — Nonlinear latent structure")
print("=" * 80)

try:
    import umap
    
    reducer = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.1, random_state=42)
    embedding = reducer.fit_transform(M_std)
    
    # Save embedding
    np.save("audits/rd8a_umap_embedding.npy", embedding)
    
    print(f"UMAP embedding: {embedding.shape}")
    
    # Correlate UMAP axes with original metrics
    print("\n--- UMAP axis correlations with metrics ---")
    for axis in range(2):
        print(f"\nUMAP-{axis+1}:")
        for i, name in enumerate(names_use):
            r, p = stats.pearsonr(embedding[:, axis], M_std[:, i])
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
            print(f"    {name:>20s}: r={r:+.3f} {sig}")

except ImportError:
    print("UMAP not installed. Skipping.")
    embedding = None

# ═══════════════════════════════════════════════════════════════════════════
# 4. CLUSTERING
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("4. CLUSTERING — Regime identification")
print("=" * 80)

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# Try k=2 to k=6
for k in range(2, 7):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(M_std)
    sil = silhouette_score(M_std, labels)
    
    # Friction distribution per cluster
    frictions = np.array([m["friction"] for m in metadata])
    print(f"\nk={k}: silhouette={sil:.3f}")
    for c in range(k):
        mask = labels == c
        fr_mean = np.mean(frictions[mask])
        fr_range = fr_min, fr_max = np.min(frictions[mask]), np.max(frictions[mask])
        print(f"  Cluster {c}: n={np.sum(mask)}, friction μ∈[{fr_min:.2f},{fr_max:.2f}] (mean={fr_mean:.2f})")

# Best clustering (highest silhouette)
best_k = 2
best_sil = -1
for k in range(2, 7):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(M_std)
    sil = silhouette_score(M_std, labels)
    if sil > best_sil:
        best_sil = sil
        best_k = k

km_final = KMeans(n_clusters=best_k, random_state=42, n_init=10)
labels_final = km_final.fit_predict(M_std)
np.save("audits/rd8a_cluster_labels.npy", labels_final)
print(f"\n>>> Best clustering: k={best_k} (silhouette={best_sil:.3f})")

# ═══════════════════════════════════════════════════════════════════════════
# 5. INTRINSIC DIMENSIONALITY
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("5. INTRINSIC DIMENSIONALITY — How many dimensions does the data actually live in?")
print("=" * 80)

# Method 1: Maximum Likelihood Estimation (Levina & Bickel)
def mle_id(X, k_neighbors=10):
    """Maximum Likelihood Estimator for intrinsic dimensionality (Levina & Bickel 2004)."""
    n, d = X.shape
    from sklearn.neighbors import NearestNeighbors
    nn = NearestNeighbors(n_neighbors=k_neighbors + 1).fit(X)
    distances, _ = nn.kneighbors(X)
    distances = distances[:, 1:]  # exclude self
    
    # For each point, estimate ID
    ids = []
    for i in range(n):
        log_ratios = np.log(distances[i, -1] / distances[i, :-1])
        valid = log_ratios > 0
        if np.sum(valid) > 0:
            ids.append(1.0 / np.mean(log_ratios[valid]))
    return np.median(ids)

# Try different k
print("\nMLE intrinsic dimensionality estimates:")
for k in [5, 10, 15, 20]:
    if k < M_std.shape[0]:
        dim_est = mle_id(M_std, k_neighbors=k)
        print(f"  k={k}: ID = {dim_est:.2f}")

# Method 2: PCA eigenvalue ratio
# If data is d-dimensional, eigenvalues should drop sharply after d
print(f"\nPCA eigenvalue ratio test:")
for i in range(len(eigvals) - 1):
    ratio = eigvals[i] / eigvals[i+1]
    if ratio > 2.0:
        print(f"  PC{i+1}/PC{i+2} ratio = {ratio:.2f} > 2.0 → possible dimension boundary")

# Method 3: Participation ratio
print(f"\nParticipation ratio (inverse of Herfindahl index):")
h = np.sum(eigvals**2) / (np.sum(eigvals))**2
pr = 1.0 / h
print(f"  Participation ratio = {pr:.2f}")
print(f"  (If data were uniformly d-dimensional, PR = d)")

# ═══════════════════════════════════════════════════════════════════════════
# 6. CORRELATION STRUCTURE
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("6. CORRELATION MATRIX")
print("=" * 80)

corr = np.corrcoef(M_use.T)
print(f"\n{'':>20s}", end="")
for name in names_use:
    print(f"{name[:8]:>10s}", end="")
print()
for i, name in enumerate(names_use):
    print(f"{name:>20s}", end="")
    for j in range(len(names_use)):
        print(f"{corr[i,j]:>10.3f}", end="")
    print()

# ═══════════════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("SUMMARY: LATENT GEOMETRY RECON")
print("=" * 80)
print(f"""
Data: {M_std.shape[0]} runs × {M_std.shape[1]} metrics
Metrics: {', '.join(names_use)}

PCA:
  Dimensions for 80% variance: {n_80}
  Dimensions for 90% variance: {n_90}
  PC1 explains {explained[0]*100:.1f}% — loads on: {', '.join(names_use[i] for i in np.argsort(np.abs(eigvecs[:,0]))[::-1][:4])}

Factor Analysis:
  Best model: {best_n} factors (BIC={best_bic:.1f})

Clustering:
  Best: k={best_k} clusters (silhouette={best_sil:.3f})

Intrinsic Dimensionality (MLE, k=10): {mle_id(M_std, 10):.2f}
Participation Ratio: {pr:.2f}

INTERPRETATION:
  The data lives in approximately {n_90} dimensions at 90% variance.
  Factor analysis suggests {best_n} latent factors.
  The intrinsic dimensionality estimate is {mle_id(M_std, 10):.1f}.
""")
