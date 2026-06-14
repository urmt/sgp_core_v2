#!/usr/bin/env python3
"""
T078: Meta-Space Reconstruction
================================
Construct a unified meta-space from all T072–T077 results across 4 domains.

Objectives:
  1. Unified Manifold — compress 10 metrics to few latent dimensions
  2. Basin Structure — identify corridor, basin, saddle, transition surfaces
  3. Universal Coordinates — infer what latent axes represent
  4. Reconstruction Test — verify viability/fertility/failure labels from latent space
"""

import csv, json, math
from pathlib import Path
from collections import defaultdict
import itertools

OUT = Path("/home/student/sgp_core_v2/sfh_sgp_ood_outputs")

# ============================================================
# DOMAIN DATA
# ============================================================

DOMAIN_DATA = [
    {
        "domain": "A — Physical universes",
        "configs": [
            {"name": "Our universe", "viable": True, "fertile": True,
             "C": 0.85, "P": 0.85, "G": 0.90, "R": 0.60, "S": 0.80,
             "SR": 0.90, "NP": 0.85, "RC": 0.90, "RD": 0.80, "OE": 0.80},
            {"name": "Cyclic universe (bounce)", "viable": True, "fertile": True,
             "C": 0.75, "P": 0.85, "G": 0.80, "R": 0.70, "S": 0.65,
             "SR": 0.80, "NP": 0.75, "RC": 0.85, "RD": 0.70, "OE": 0.70},
            {"name": "Empty universe (Ω<<1)", "viable": False, "fertile": False,
             "C": 0.80, "P": 0.95, "G": 0.05, "R": 0.10, "S": 0.00,
             "SR": 0.05, "NP": 0.00, "RC": 0.00, "RD": 0.00, "OE": 0.00},
            {"name": "Collapsing universe (Ω>>1)", "viable": False, "fertile": False,
             "C": 0.75, "P": 0.15, "G": 0.30, "R": 0.00, "S": 0.10,
             "SR": 0.30, "NP": 0.25, "RC": 0.20, "RD": 0.10, "OE": 0.05},
            {"name": "Thermal equilibrium", "viable": False, "fertile": False,
             "C": 0.50, "P": 0.90, "G": 0.05, "R": 0.05, "S": 0.00,
             "SR": 0.00, "NP": 0.00, "RC": 0.00, "RD": 0.00, "OE": 0.00},
            {"name": "High-dark-energy universe", "viable": False, "fertile": False,
             "C": 0.80, "P": 0.60, "G": 0.15, "R": 0.10, "S": 0.05,
             "SR": 0.15, "NP": 0.10, "RC": 0.10, "RD": 0.05, "OE": 0.05},
            {"name": "Strong-coupling universe", "viable": False, "fertile": False,
             "C": 0.40, "P": 0.30, "G": 0.50, "R": 0.10, "S": 0.15,
             "SR": 0.50, "NP": 0.45, "RC": 0.40, "RD": 0.20, "OE": 0.15},
            {"name": "Super-fertile universe (hypothetical)", "viable": True, "fertile": True,
             "C": 0.80, "P": 0.80, "G": 0.95, "R": 0.55, "S": 0.90,
             "SR": 0.95, "NP": 0.95, "RC": 0.95, "RD": 0.90, "OE": 0.95},
        ],
    },
    {
        "domain": "B — Mathematical systems",
        "configs": [
            {"name": "ZFC set theory", "viable": True, "fertile": True,
             "C": 0.80, "P": 0.90, "G": 0.90, "R": 0.70, "S": 0.70,
             "SR": 0.90, "NP": 0.90, "RC": 0.85, "RD": 0.80, "OE": 0.90},
            {"name": "Peano arithmetic (PA)", "viable": True, "fertile": True,
             "C": 0.85, "P": 0.90, "G": 0.80, "R": 0.75, "S": 0.50,
             "SR": 0.70, "NP": 0.75, "RC": 0.60, "RD": 0.40, "OE": 0.80},
            {"name": "First-order logic (FOL)", "viable": True, "fertile": False,
             "C": 1.00, "P": 0.95, "G": 0.40, "R": 0.90, "S": 0.10,
             "SR": 0.30, "NP": 0.30, "RC": 0.20, "RD": 0.10, "OE": 0.30},
            {"name": "Category theory (ETCS)", "viable": True, "fertile": True,
             "C": 0.80, "P": 0.85, "G": 0.85, "R": 0.70, "S": 0.80,
             "SR": 0.85, "NP": 0.85, "RC": 0.90, "RD": 0.90, "OE": 0.85},
            {"name": "Computation (Turing/λ)", "viable": True, "fertile": True,
             "C": 0.85, "P": 0.90, "G": 0.80, "R": 0.65, "S": 0.85,
             "SR": 0.80, "NP": 0.80, "RC": 0.85, "RD": 0.95, "OE": 0.85},
            {"name": "Inconsistent system", "viable": False, "fertile": False,
             "C": 0.05, "P": 0.10, "G": 0.95, "R": 0.00, "S": 0.10,
             "SR": 0.90, "NP": 0.95, "RC": 0.80, "RD": 0.60, "OE": 0.90},
            {"name": "Presburger arithmetic", "viable": True, "fertile": False,
             "C": 1.00, "P": 0.95, "G": 0.25, "R": 0.95, "S": 0.05,
             "SR": 0.15, "NP": 0.15, "RC": 0.10, "RD": 0.05, "OE": 0.15},
            {"name": "Decidable fragment of FOL", "viable": True, "fertile": False,
             "C": 1.00, "P": 0.95, "G": 0.15, "R": 0.95, "S": 0.05,
             "SR": 0.10, "NP": 0.10, "RC": 0.05, "RD": 0.00, "OE": 0.10},
        ],
    },
    {
        "domain": "C — Recursive substrate",
        "configs": [
            {"name": "Full 9-assumption substrate", "viable": True, "fertile": True,
             "C": 0.95, "P": 0.85, "G": 0.85, "R": 0.80, "S": 0.90,
             "SR": 0.85, "NP": 0.80, "RC": 0.80, "RD": 0.85, "OE": 0.75},
            {"name": "Original substrate (IS1↔IS2)", "viable": False, "fertile": False,
             "C": 0.20, "P": 0.30, "G": 0.40, "R": 0.10, "S": 0.35,
             "SR": 0.40, "NP": 0.35, "RC": 0.30, "RD": 0.40, "OE": 0.30},
            {"name": "OC2 only (trivial)", "viable": False, "fertile": False,
             "C": 0.60, "P": 0.30, "G": 0.05, "R": 0.10, "S": 0.00,
             "SR": 0.05, "NP": 0.00, "RC": 0.00, "RD": 0.00, "OE": 0.00},
            {"name": "Substrate without SR1", "viable": True, "fertile": False,
             "C": 0.85, "P": 0.80, "G": 0.70, "R": 0.70, "S": 0.25,
             "SR": 0.50, "NP": 0.50, "RC": 0.45, "RD": 0.30, "OE": 0.40},
            {"name": "Substrate without EC1", "viable": True, "fertile": True,
             "C": 0.85, "P": 0.80, "G": 0.75, "R": 0.70, "S": 0.60,
             "SR": 0.70, "NP": 0.70, "RC": 0.70, "RD": 0.55, "OE": 0.60},
            {"name": "Substrate without CD2", "viable": True, "fertile": False,
             "C": 0.90, "P": 0.80, "G": 0.65, "R": 0.70, "S": 0.75,
             "SR": 0.60, "NP": 0.55, "RC": 0.50, "RD": 0.60, "OE": 0.50},
        ],
    },
    {
        "domain": "D — Dynamical manifolds",
        "configs": [
            {"name": "Lorenz strange attractor", "viable": True, "fertile": False,
             "C": 0.80, "P": 0.80, "G": 0.60, "R": 0.60, "S": 0.30,
             "SR": 0.40, "NP": 0.30, "RC": 0.20, "RD": 0.20, "OE": 0.20},
            {"name": "Reaction-diffusion (Turing)", "viable": True, "fertile": True,
             "C": 0.85, "P": 0.85, "G": 0.80, "R": 0.75, "S": 0.35,
             "SR": 0.80, "NP": 0.70, "RC": 0.75, "RD": 0.30, "OE": 0.60},
            {"name": "Logistic map (r=3.8)", "viable": True, "fertile": False,
             "C": 0.75, "P": 0.65, "G": 0.65, "R": 0.30, "S": 0.15,
             "SR": 0.35, "NP": 0.30, "RC": 0.15, "RD": 0.10, "OE": 0.15},
            {"name": "Coupled oscillator (Kuramoto)", "viable": True, "fertile": False,
             "C": 0.85, "P": 0.85, "G": 0.65, "R": 0.70, "S": 0.40,
             "SR": 0.45, "NP": 0.40, "RC": 0.35, "RD": 0.25, "OE": 0.30},
            {"name": "Fixed-point collapse", "viable": False, "fertile": False,
             "C": 0.70, "P": 0.80, "G": 0.05, "R": 0.40, "S": 0.00,
             "SR": 0.00, "NP": 0.00, "RC": 0.00, "RD": 0.00, "OE": 0.00},
            {"name": "Boolean network (K=2 critical)", "viable": True, "fertile": True,
             "C": 0.80, "P": 0.80, "G": 0.80, "R": 0.60, "S": 0.50,
             "SR": 0.80, "NP": 0.75, "RC": 0.80, "RD": 0.50, "OE": 0.70},
            {"name": "Game of Life (CA)", "viable": True, "fertile": True,
             "C": 0.85, "P": 0.80, "G": 0.90, "R": 0.50, "S": 0.60,
             "SR": 0.90, "NP": 0.85, "RC": 0.90, "RD": 0.70, "OE": 0.90},
            {"name": "Unbounded divergence", "viable": False, "fertile": False,
             "C": 0.30, "P": 0.10, "G": 0.20, "R": 0.00, "S": 0.00,
             "SR": 0.10, "NP": 0.20, "RC": 0.05, "RD": 0.00, "OE": 0.10},
        ],
    },
]

ALL_AXES = ["C", "P", "G", "R", "S", "SR", "NP", "RC", "RD", "OE"]
VIABILITY_AXES = ["C", "P", "G", "R", "S"]
FERTILITY_AXES = ["SR", "NP", "RC", "RD", "OE"]

ALL_CONFIGS = []
for d in DOMAIN_DATA:
    for c in d["configs"]:
        c["domain"] = d["domain"]
        c["domain_short"] = d["domain"][0]
        c["stability"] = round(sum(c[a] for a in ["C", "P", "R"]) / 3, 3)
        c["fertility_score"] = round(sum(c[a] for a in FERTILITY_AXES) / 5, 3)
        c["region"] = "collapse" if not c["viable"] else ("fertile" if c["fertile"] else "fortress")
        ALL_CONFIGS.append(c)

N = len(ALL_CONFIGS)
M = len(ALL_AXES)

# ============================================================
# 1. UNIFIED MANIFOLD — PCA by hand
# ============================================================

print("=" * 72)
print("T078: META-SPACE RECONSTRUCTION")
print("=" * 72)

print(f"\n  {N} configurations, {M} axes, 4 domains.")

# Build data matrix (N x M)
data = [[c[ax] for ax in ALL_AXES] for c in ALL_CONFIGS]

def transpose(m):
    return list(map(list, zip(*m)))

def mean_vec(matrix):
    n = len(matrix)
    if n == 0: return []
    m = len(matrix[0])
    return [sum(row[j] for row in matrix) / n for j in range(m)]

def sub_vec(v1, v2):
    return [a - b for a, b in zip(v1, v2)]

def vec_norm(v):
    return math.sqrt(sum(x*x for x in v))

def dot(v1, v2):
    return sum(a*b for a, b in zip(v1, v2))

def mat_mul(A, B):
    """A (n x m) * B (m x p) = C (n x p)"""
    n, m = len(A), len(A[0])
    p = len(B[0])
    C = [[0.0]*p for _ in range(n)]
    for i in range(n):
        for j in range(p):
            s = 0.0
            for k in range(m):
                s += A[i][k] * B[k][j]
            C[i][j] = s
    return C

# Center the data
data_T = transpose(data)
means = [sum(col)/len(col) for col in data_T]
centered = [[data[i][j] - means[j] for j in range(M)] for i in range(N)]

# Covariance matrix (M x M)
cov = [[0.0]*M for _ in range(M)]
for i in range(M):
    for j in range(M):
        cov[i][j] = sum(centered[k][i] * centered[k][j] for k in range(N)) / (N-1)

# Power iteration for eigenvalues/vectors
def power_iteration(mat, n_iter=1000):
    M_ = len(mat)
    v = [1.0/M_] * M_
    for _ in range(n_iter):
        # v = mat @ v
        w = [sum(mat[i][j] * v[j] for j in range(M_)) for i in range(M_)]
        norm = math.sqrt(sum(x*x for x in w))
        v = [x / norm for x in w]
    eigenvalue = sum(v[i] * sum(mat[i][j] * v[j] for j in range(M_)) for i in range(M_))
    return eigenvalue, v

def deflate(mat, eigenvalue, eigenvector):
    M_ = len(mat)
    result = [[mat[i][j] for j in range(M_)] for i in range(M_)]
    for i in range(M_):
        for j in range(M_):
            result[i][j] -= eigenvalue * eigenvector[i] * eigenvector[j]
    return result

# Compute all eigenvalues/vectors
eigenvalues = []
eigenvectors = []
working_cov = [row[:] for row in cov]
for k in range(M):
    ev, ev_vec = power_iteration(working_cov)
    eigenvalues.append(ev)
    eigenvectors.append(ev_vec)
    working_cov = deflate(working_cov, ev, ev_vec)

total_var = sum(eigenvalues)
explained = [ev / total_var * 100 for ev in eigenvalues]
cumulative = []
s = 0.0
for v in explained:
    s += v
    cumulative.append(s)

print(f"\n{'='*60}")
print("1. UNIFIED MANIFOLD — INTRINSIC DIMENSIONALITY")
print(f"{'='*60}")
print(f"\n  PCA on {M} axes across {N} configurations:")
print(f"\n  {'PC':<6}{'Eigenvalue':<15}{'Explained %':<15}{'Cumulative %':<15}")
print(f"  {'-'*51}")
for i in range(M):
    print(f"  PC{i+1:<4}{eigenvalues[i]:<15.4f}{explained[i]:<15.2f}{cumulative[i]:<15.2f}")

# Determine intrinsic dimensionality
thresholds = [0.7, 0.8, 0.9, 0.95]
print(f"\n  Dimensionality at variance thresholds:")
for thresh in thresholds:
    for i, cum in enumerate(cumulative):
        if cum >= thresh * 100:
            print(f"    {thresh*100:.0f}% variance: {i+1} PCs")
            break

# Kaiser criterion
n_kaiser = sum(1 for ev in eigenvalues if ev > 1.0)
print(f"  Kaiser criterion (eigenvalue > 1): {n_kaiser} PCs")

# Elbow: find where explained drops below 1/M
elbow_dim = sum(1 for v in explained if v > 100/M)
print(f"  Elbow (> mean variance = {100/M:.1f}%): {elbow_dim} PCs")

# Project data onto top PCs
def project(data_matrix, eigenvectors, n_components, means):
    """Project data onto top n eigenvectors"""
    proj = []
    for row in data_matrix:
        centered_row = [row[j] - means[j] for j in range(len(row))]
        p = []
        for k in range(n_components):
            p.append(sum(centered_row[j] * eigenvectors[k][j] for j in range(len(row))))
        proj.append(p)
    return proj

for latent_dim in [2, 3, 4]:
    proj = project(data, eigenvectors, latent_dim, means)
    # Verify reconstruction
    # Reconstruct centered data from latent coordinates
    recon_errors = []
    for i in range(N):
        recon = [0.0]*M
        for k in range(latent_dim):
            for j in range(M):
                recon[j] += proj[i][k] * eigenvectors[k][j]
        # Add mean back
        recon = [recon[j] + means[j] for j in range(M)]
        err = math.sqrt(sum((recon[j] - data[i][j])**2 for j in range(M)))
        recon_errors.append(err)
    avg_err = sum(recon_errors) / N
    explained_frac = sum(eigenvalues[:latent_dim]) / total_var
    print(f"\n  {latent_dim}D latent space: "
          f"avg reconstruction error = {avg_err:.4f}, "
          f"explained variance = {explained_frac:.3f}")

# ============================================================
# 2. BASIN STRUCTURE IN LATENT SPACE
# ============================================================

# Use 3D latent space as the primary representation
LATENT_DIM = 3
latent_3d = project(data, eigenvectors, LATENT_DIM, means)

print(f"\n{'='*60}")
print("2. BASIN STRUCTURE")
print(f"{'='*60}")

# Cluster configurations by region in latent space
print(f"\n  Configurations in {LATENT_DIM}D latent space:")
print(f"  {'Name':<40}{'Region':<14}{'PC1':<10}{'PC2':<10}{'PC3':<10}")
print(f"  {'-'*84}")
for i, c in enumerate(ALL_CONFIGS):
    p = latent_3d[i]
    print(f"  {c['name']:<40}{c['region']:<14}"
          f"{p[0]:<10.3f}{p[1]:<10.3f}{p[2]:<10.3f}")

# Check: do regions form connected clusters in latent space?
# Compute centroid for each region
regions = ["collapse", "fortress", "fertile"]
region_centroids = {}
for region in regions:
    indices = [i for i, c in enumerate(ALL_CONFIGS) if c["region"] == region]
    if indices:
        coords = [latent_3d[i] for i in indices]
        centroid = [sum(c[k] for c in coords)/len(coords) for k in range(LATENT_DIM)]
        region_centroids[region] = centroid

print(f"\n  Region centroids in latent space:")
for region, cent in region_centroids.items():
    print(f"    {region:<12} ({cent[0]:.3f}, {cent[1]:.3f}, {cent[2]:.3f})")

# Distances between centroids
print(f"\n  Distances between region centroids:")
region_pairs = list(itertools.combinations(regions, 2))
for r1, r2 in region_pairs:
    if r1 in region_centroids and r2 in region_centroids:
        d = math.sqrt(sum((region_centroids[r1][k] - region_centroids[r2][k])**2 for k in range(LATENT_DIM)))
        print(f"    {r1} ↔ {r2}: {d:.3f}")

# Check fertile corridor connectivity in latent space
fertile_indices = [i for i, c in enumerate(ALL_CONFIGS) if c["fertile"]]
print(f"\n  Fertile system latent coordinates:")
for i in fertile_indices:
    c = ALL_CONFIGS[i]
    p = latent_3d[i]
    print(f"    {c['name']:<40} ({p[0]:.3f}, {p[1]:.3f}, {p[2]:.3f})  [{c['domain_short']}]")

# Check if fertile systems form one cluster or multiple
fertile_coords = [latent_3d[i] for i in fertile_indices]
if len(fertile_coords) >= 2:
    fert_centroid = [sum(c[k] for c in fertile_coords)/len(fertile_coords) for k in range(LATENT_DIM)]
    fert_dists = [math.sqrt(sum((c[k] - fert_centroid[k])**2 for k in range(LATENT_DIM))) for c in fertile_coords]
    fert_spread = sum(fert_dists)/len(fert_dists)
    fert_max_dev = max(fert_dists)
    print(f"\n  Fertile cluster analysis:")
    print(f"    Spread (mean distance from centroid): {fert_spread:.3f}")
    print(f"    Max deviation: {fert_max_dev:.3f}")
    
    # Check by domain
    print(f"    By domain:")
    for d_data in DOMAIN_DATA:
        dname = d_data["domain"]
        d_fert = [i for i in fertile_indices if ALL_CONFIGS[i]["domain"] == dname]
        if d_fert:
            d_coords = [latent_3d[i] for i in d_fert]
            d_cent = [sum(c[k] for c in d_coords)/len(d_coords) for k in range(LATENT_DIM)]
            d_dist = math.sqrt(sum((d_cent[k] - fert_centroid[k])**2 for k in range(LATENT_DIM)))
            print(f"      {dname[:25]:<25} centroid offset from global: {d_dist:.3f}")

# ============================================================
# 3. UNIVERSAL COORDINATES
# ============================================================

print(f"\n{'='*60}")
print("3. UNIVERSAL COORDINATES — INTERPRETING LATENT AXES")
print(f"{'='*60}")

# The eigenvectors show how each original axis contributes to each PC
print(f"\n  Eigenvector loadings (how original axes compose each PC):")
print(f"  {'Axis':<6}", end="")
for k in range(min(4, M)):
    print(f"{f'PC{k+1}':<10}", end="")
print()
print(f"  {'-'*46}")
for j in range(M):
    print(f"  {ALL_AXES[j]:<6}", end="")
    for k in range(min(4, M)):
        print(f"{eigenvectors[k][j]:<10.3f}", end="")
    print()

# For each of top 3 PCs, determine which original axes load most strongly
print(f"\n  Interpreting latent dimensions (top loadings >|0.3|):")
pc_names = {}
for k in range(min(4, M)):
    loadings = [(ALL_AXES[j], eigenvectors[k][j]) for j in range(M)]
    loadings.sort(key=lambda x: abs(x[1]), reverse=True)
    strong = [l for l in loadings if abs(l[1]) > 0.3]
    if not strong:
        strong = loadings[:3]
    pos = [l for l in strong if l[1] > 0]
    neg = [l for l in strong if l[1] < 0]
    print(f"\n  PC{k+1} (explained {explained[k]:.1f}%):")
    if pos:
        print(f"    Positive: {', '.join(f'{a}(+{v:.2f})' for a,v in pos)}")
    if neg:
        print(f"    Negative: {', '.join(f'{a}({v:.2f})' for a,v in neg)}")
    
    # Suggest an interpretation
    pos_axes = [a for a, v in pos]
    neg_axes = [a for a, v in neg]
    candidates = []
    if {'SR', 'NP', 'OE', 'RC'}.intersection(pos_axes) and {'C', 'P', 'R'}.intersection(neg_axes):
        candidates.append("Fertility vs Stability")
    if {'S', 'R'}.intersection(pos_axes) and {'G', 'NP'}.intersection(neg_axes):
        candidates.append("Structure vs Novelty")
    if {'G', 'SR', 'NP'}.intersection(pos_axes) and {'C', 'P', 'R'}.intersection(neg_axes):
        candidates.append("Generativity vs Coherence")
    if pos_axes and neg_axes:
        print(f"    Candidate interpretation: {', '.join(candidates) if candidates else 'No clear label'}")
        pc_names[k+1] = candidates[0] if candidates else None

# ============================================================
# 4. RECONSTRUCTION TEST
# ============================================================

print(f"\n{'='*60}")
print("4. RECONSTRUCTION TEST")
print(f"{'='*60}")

# Test: can we reconstruct labels from low-dimensional projections?
def nearest_centroid_classifier(latent_coords, configs, n_components):
    """Classify each point using nearest centroid in latent space."""
    # Compute region centroids in latent space
    centroids = {}
    for region in regions:
        idx = [i for i, c in enumerate(configs) if c["region"] == region]
        if idx:
            cent = [sum(latent_coords[i][k] for i in idx)/len(idx) for k in range(n_components)]
            centroids[region] = cent
    
    correct = 0
    for i, c in enumerate(configs):
        p = latent_coords[i]
        nearest = min(centroids.keys(),
                      key=lambda r: math.sqrt(sum((p[k] - centroids[r][k])**2 for k in range(n_components))))
        if nearest == c["region"]:
            correct += 1
    return correct / len(configs) if configs else 0

# Also test fertility-specific reconstruction
def nearest_fertile_classifier(latent_coords, configs, n_components):
    """Classify fertile vs non-fertile using nearest centroid."""
    fertile_idx = [i for i, c in enumerate(configs) if c["fertile"]]
    non_fertile_idx = [i for i, c in enumerate(configs) if not c["fertile"]]
    
    fert_cent = [sum(latent_coords[i][k] for i in fertile_idx)/len(fertile_idx)
                 for k in range(n_components)]
    nonf_cent = [sum(latent_coords[i][k] for i in non_fertile_idx)/len(non_fertile_idx)
                 for k in range(n_components)]
    
    correct = 0
    for i, c in enumerate(configs):
        p = latent_coords[i]
        d_fert = math.sqrt(sum((p[k] - fert_cent[k])**2 for k in range(n_components)))
        d_nonf = math.sqrt(sum((p[k] - nonf_cent[k])**2 for k in range(n_components)))
        predicted = d_fert < d_nonf
        if predicted == c["fertile"]:
            correct += 1
    return correct / len(configs) if configs else 0

def viable_classifier(latent_coords, configs, n_components):
    """Classify viable vs non-viable using nearest centroid."""
    v_idx = [i for i, c in enumerate(configs) if c["viable"]]
    nv_idx = [i for i, c in enumerate(configs) if not c["viable"]]
    v_cent = [sum(latent_coords[i][k] for i in v_idx)/len(v_idx) for k in range(n_components)]
    nv_cent = [sum(latent_coords[i][k] for i in nv_idx)/len(nv_idx) for k in range(n_components)]
    correct = 0
    for i, c in enumerate(configs):
        p = latent_coords[i]
        d_v = math.sqrt(sum((p[k] - v_cent[k])**2 for k in range(n_components)))
        d_nv = math.sqrt(sum((p[k] - nv_cent[k])**2 for k in range(n_components)))
        predicted = d_v < d_nv
        if predicted == c["viable"]:
            correct += 1
    return correct / len(configs) if configs else 0

print(f"\n  Region classification accuracy (nearest centroid in latent space):")
print(f"  {'Latent Dim':<15}{'Region (3-class)':<22}{'Fertility (binary)':<22}{'Viability (binary)':<22}")
print(f"  {'-'*81}")
for dim in [2, 3, 4, M]:
    if dim <= 2:
        lat = latent_3d
        proj_ = [[p[0], p[1]] for p in latent_3d]
    elif dim == 3:
        proj_ = latent_3d
    elif dim == 4:
        proj_ = project(data, eigenvectors, 4, means)
    else:
        proj_ = data  # full space
    
    n_comp = min(dim, len(proj_[0])) if dim <= M else M
    
    if dim <= M:
        reg_acc = nearest_centroid_classifier(proj_, ALL_CONFIGS, n_comp)
        fert_acc = nearest_fertile_classifier(proj_, ALL_CONFIGS, n_comp)
        via_acc = viable_classifier(proj_, ALL_CONFIGS, n_comp)
        print(f"  {n_comp:<15}{reg_acc:<22.3f}{fert_acc:<22.3f}{via_acc:<22.3f}")

# Baseline: classification in full space
print(f"\n  Baseline (full {M}D space):")
reg_acc_full = nearest_centroid_classifier(data, ALL_CONFIGS, M)
fert_acc_full = nearest_fertile_classifier(data, ALL_CONFIGS, M)
via_acc_full = viable_classifier(data, ALL_CONFIGS, M)
print(f"    Region: {reg_acc_full:.3f}, Fertility: {fert_acc_full:.3f}, Viability: {via_acc_full:.3f}")

# Compare latent space to full space
print(f"\n  Reconstruction quality (3D latent vs {M}D full):")
print(f"    Region accuracy:   3D={nearest_centroid_classifier(latent_3d, ALL_CONFIGS, 3):.3f} vs full={reg_acc_full:.3f}")
print(f"    Fertility accuracy: 3D={nearest_fertile_classifier(latent_3d, ALL_CONFIGS, 3):.3f} vs full={fert_acc_full:.3f}")
print(f"    Viability accuracy: 3D={viable_classifier(latent_3d, ALL_CONFIGS, 3):.3f} vs full={via_acc_full:.3f}")

# ============================================================
# 5. FAILURE BOUNDARY TEST
# ============================================================

print(f"\n{'='*60}")
print("5. FAILURE BOUNDARY SEPARATION IN LATENT SPACE")
print(f"{'='*60}")

# Map configurations to failure modes (from T072)
# Collapse systems have at least one failure mode
# For each domain, check if collapse systems share a latent region
collapse_latent = [latent_3d[i] for i, c in enumerate(ALL_CONFIGS) if c["region"] == "collapse"]
fortress_latent = [latent_3d[i] for i, c in enumerate(ALL_CONFIGS) if c["region"] == "fortress"]
fertile_latent = [latent_3d[i] for i, c in enumerate(ALL_CONFIGS) if c["region"] == "fertile"]

print(f"\n  Separation between regions in 3D latent space:")
for r1_name, r1_coords in [("collapse", collapse_latent), ("fortress", fortress_latent), ("fertile", fertile_latent)]:
    for r2_name, r2_coords in [("collapse", collapse_latent), ("fortress", fortress_latent), ("fertile", fertile_latent)]:
        if r1_name >= r2_name:
            continue
        if not r1_coords or not r2_coords:
            continue
        # Pairwise distances between all points in region 1 and region 2
        min_d = min(math.sqrt(sum((a[k]-b[k])**2 for k in range(LATENT_DIM)))
                    for a in r1_coords for b in r2_coords)
        max_d = max(math.sqrt(sum((a[k]-b[k])**2 for k in range(LATENT_DIM)))
                    for a in r1_coords for b in r2_coords)
        # Intra-region spread
        r1_cent = [sum(c[k] for c in r1_coords)/len(r1_coords) for k in range(LATENT_DIM)]
        r1_spread = math.sqrt(sum(sum((c[k]-r1_cent[k])**2 for k in range(LATENT_DIM)) for c in r1_coords)/len(r1_coords))
        print(f"    {r1_name} ↔ {r2_name}: min={min_d:.3f}, max={max_d:.3f}, "
              f"r1_spread={r1_spread:.3f}, overlap={'POSSIBLE' if min_d < r1_spread else 'NONE'}")

# ============================================================
# 6. INFERRED LATENT AXES
# ============================================================

print(f"\n{'='*60}")
print("6. INFERRED LATENT AXES — CANDIDATE UNIVERSAL COORDINATES")
print(f"{'='*60}")

# Based on eigenvector analysis, suggest what each latent dimension represents
print(f"\n  Candidate universal coordinate system:")
for k in range(LATENT_DIM):
    label = pc_names.get(k+1, f"PC{k+1} (unnamed)")
    var_frac = explained[k]
    loadings = [(ALL_AXES[j], eigenvectors[k][j]) for j in range(M)]
    loadings.sort(key=lambda x: abs(x[1]), reverse=True)
    top3 = loadings[:3]
    print(f"\n    PC{k+1} ({label}, {var_frac:.1f}% variance):")
    for ax, v in top3:
        dir_str = "+" if v > 0 else ""
        print(f"      {dir_str}{v:.3f} × {ax}")

# Propose minimal coordinate system
highest_loadings = {}
for k in range(LATENT_DIM):
    loadings = [(ALL_AXES[j], abs(eigenvectors[k][j])) for j in range(M)]
    loadings.sort(key=lambda x: x[1], reverse=True)
    highest_loadings[f"PC{k+1}"] = loadings[:2]

# Which axes are most important across ALL top PCs?
axis_importance = {ax: 0.0 for ax in ALL_AXES}
for k in range(LATENT_DIM):
    for j in range(M):
        axis_importance[ALL_AXES[j]] += abs(eigenvectors[k][j]) * explained[k]

total_imp = sum(axis_importance.values())
for ax in sorted(axis_importance, key=axis_importance.get, reverse=True):
    axis_importance[ax] = axis_importance[ax] / total_imp * 100

print(f"\n  Axis importance (weighted by explained variance):")
print(f"  {'Axis':<6}{'Importance %':<16}")
print(f"  {'-'*22}")
for ax in sorted(axis_importance, key=axis_importance.get, reverse=True):
    print(f"  {ax:<6}{axis_importance[ax]:<16.1f}")

# Top 3 most important axes
top_axes = sorted(axis_importance, key=axis_importance.get, reverse=True)[:3]
print(f"\n  Top 3 axes (candidate minimal coordinate system):")
for ax in top_axes:
    print(f"    {ax} ({axis_importance[ax]:.1f}%)")

# ============================================================
# WRITE DELIVERABLES
# ============================================================

# 1. Unified manifold coordinates
with open(OUT / "t078_unified_manifold.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["domain", "name", "region", "viable", "fertile",
                 "PC1", "PC2", "PC3"] + ALL_AXES)
    for i, c in enumerate(ALL_CONFIGS):
        p = latent_3d[i]
        w.writerow([c["domain"], c["name"], c["region"], str(c["viable"]),
                     str(c["fertile"]), round(p[0], 3), round(p[1], 3),
                     round(p[2], 3)] + [c[ax] for ax in ALL_AXES])

print(f"\nWrote t078_unified_manifold.csv")

# 2. PCA results
with open(OUT / "t078_pca_results.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["PC", "eigenvalue", "explained_pct", "cumulative_pct"])
    for i in range(M):
        w.writerow([f"PC{i+1}", round(eigenvalues[i], 4),
                     round(explained[i], 2), round(cumulative[i], 2)])

print(f"Wrote t078_pca_results.csv")

# 3. Eigenvector loadings
with open(OUT / "t078_eigenvector_loadings.csv", "w", newline="") as f:
    w = csv.writer(f)
    header = ["axis"] + [f"PC{i+1}" for i in range(M)]
    w.writerow(header)
    for j in range(M):
        row = [ALL_AXES[j]] + [round(eigenvectors[i][j], 4) for i in range(M)]
        w.writerow(row)

print(f"Wrote t078_eigenvector_loadings.csv")

# 4. Latent space assignments
with open(OUT / "t078_latent_assignments.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["domain", "name", "PC1", "PC2", "PC3",
                 "region", "nearest_region_centroid", "fertile_centroid_dist"])
    fertile_cent = [sum(latent_3d[i][k] for i in fertile_indices)/len(fertile_indices)
                    for k in range(LATENT_DIM)] if fertile_indices else [0]*LATENT_DIM
    for i, c in enumerate(ALL_CONFIGS):
        p = latent_3d[i]
        # Nearest region centroid
        nearest_reg = min(region_centroids.keys(),
                          key=lambda r: math.sqrt(sum((p[k] - region_centroids[r][k])**2 for k in range(LATENT_DIM))))
        d_fert = math.sqrt(sum((p[k] - fertile_cent[k])**2 for k in range(LATENT_DIM)))
        w.writerow([c["domain"], c["name"],
                     round(p[0], 3), round(p[1], 3), round(p[2], 3),
                     c["region"], nearest_reg, round(d_fert, 3)])

print(f"Wrote t078_latent_assignments.csv")

# 5. Reconstruction accuracy
with open(OUT / "t078_reconstruction_accuracy.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["latent_dim", "region_accuracy", "fertility_accuracy", "viability_accuracy"])
    for dim in [2, 3, 4, M]:
        n_comp = min(dim, M)
        if n_comp == 2:
            proj_ = [[p[0], p[1]] for p in latent_3d]
        elif n_comp == 3:
            proj_ = latent_3d
        elif n_comp == 4:
            proj_ = project(data, eigenvectors, 4, means)
        else:
            proj_ = data
        reg = nearest_centroid_classifier(proj_, ALL_CONFIGS, n_comp)
        fert = nearest_fertile_classifier(proj_, ALL_CONFIGS, n_comp)
        via = viable_classifier(proj_, ALL_CONFIGS, n_comp)
        w.writerow([n_comp, round(reg, 3), round(fert, 3), round(via, 3)])

print(f"Wrote t078_reconstruction_accuracy.csv")

# 6. Transition surfaces
with open(OUT / "t078_transition_surfaces.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["boundary", "min_latent_distance", "overlap_possible"])
    pairs = [("collapse", "fortress"), ("collapse", "fertile"), ("fortress", "fertile")]
    for r1, r2 in pairs:
        c1 = [latent_3d[i] for i, c in enumerate(ALL_CONFIGS) if c["region"] == r1]
        c2 = [latent_3d[i] for i, c in enumerate(ALL_CONFIGS) if c["region"] == r2]
        if c1 and c2:
            min_d = min(math.sqrt(sum((a[k]-b[k])**2 for k in range(LATENT_DIM)))
                        for a in c1 for b in c2)
            # Check if r1 spread overlaps with min distance
            r1_cent = [sum(c[k] for c in c1)/len(c1) for k in range(LATENT_DIM)]
            r1_spread = math.sqrt(sum(sum((c[k]-r1_cent[k])**2 for k in range(LATENT_DIM)) for c in c1)/len(c1))
            overlap = "YES" if min_d < r1_spread else "NO"
            w.writerow([f"{r1}_to_{r2}", round(min_d, 3), overlap])

print(f"Wrote t078_transition_surfaces.csv")

# 7. Summary JSON
summary = {
    "audit": "T078 — Meta-Space Reconstruction",
    "intrinsic_dimensionality": {
        "variables": M,
        "kaiser_criterion": n_kaiser,
        "elbow_dimension": elbow_dim,
        "variance_70pct": next(i+1 for i, c in enumerate(cumulative) if c >= 70),
        "variance_90pct": next(i+1 for i, c in enumerate(cumulative) if c >= 90),
    },
    "pca": {
        "explained_variances": [round(v, 2) for v in explained],
        "cumulative_variances": [round(c, 2) for c in cumulative],
    },
    "fertile_corridor_in_latent": {
        "n_fertile_systems": len(fertile_indices),
        "cluster_spread": round(fert_spread, 3),
        "max_deviation": round(fert_max_dev, 3),
    },
    "region_separation": {
        "collapse_fortress": round(
            min(math.sqrt(sum((a[k]-b[k])**2 for k in range(LATENT_DIM)))
                for a in collapse_latent for b in fortress_latent), 3) if collapse_latent and fortress_latent else None,
        "collapse_fertile": round(
            min(math.sqrt(sum((a[k]-b[k])**2 for k in range(LATENT_DIM)))
                for a in collapse_latent for b in fertile_latent), 3) if collapse_latent and fertile_latent else None,
        "fortress_fertile": round(
            min(math.sqrt(sum((a[k]-b[k])**2 for k in range(LATENT_DIM)))
                for a in fortress_latent for b in fertile_latent), 3) if fortress_latent and fertile_latent else None,
    },
    "reconstruction_accuracy": {
        "2D_region": round(nearest_centroid_classifier([[p[0], p[1]] for p in latent_3d], ALL_CONFIGS, 2), 3),
        "2D_fertility": round(nearest_fertile_classifier([[p[0], p[1]] for p in latent_3d], ALL_CONFIGS, 2), 3),
        "2D_viability": round(viable_classifier([[p[0], p[1]] for p in latent_3d], ALL_CONFIGS, 2), 3),
        "3D_region": round(nearest_centroid_classifier(latent_3d, ALL_CONFIGS, 3), 3),
        "3D_fertility": round(nearest_fertile_classifier(latent_3d, ALL_CONFIGS, 3), 3),
        "3D_viability": round(viable_classifier(latent_3d, ALL_CONFIGS, 3), 3),
        "full_region": round(reg_acc_full, 3),
        "full_fertility": round(fert_acc_full, 3),
        "full_viability": round(via_acc_full, 3),
    },
    "top_3_axes_by_importance": top_axes,
    "fertile_corridor_connected": fert_spread < 1.0,
    "conclusion": (
        f"The meta-space has intrinsic dimensionality ~{n_kaiser} "
        f"(Kaiser) or ~{elbow_dim} (elbow), compressing {M} metrics. "
        f"The fertile corridor is {'' if fert_spread < 1.0 else 'not '}a single connected cluster "
        f"in latent space. Top axes: {', '.join(top_axes)}."
    ),
}

with open(OUT / "t078_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print(f"Wrote t078_summary.json")
print(f"\nT078 complete.")
