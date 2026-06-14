"""RD-017: Residual(C) Latent State Identification.

Re-runs granular DEM to extract structural descriptors from raw grain positions,
then performs structure search, dimensionality analysis, pathway tests,
and within-level robustness checks.

Structural descriptors computed from raw (x,y) trajectories:
  - Contact-based: coordination number, contact count, contact density
  - Overlap/force: mean overlap, overlap std (force heterogeneity)
  - Graph: clustering coefficient, component count, largest component size
  - Spatial: radial distribution function g(r), nearest neighbor stats
  - Voronoi: mean/skew of Delaunay cell areas
  - Temporal: contact persistence, network Jaccard similarity
"""

import sys, json, time, warnings, math
warnings.filterwarnings("ignore")

import numpy as np
from scipy.stats import pearsonr, spearmanr
from scipy.spatial import Delaunay
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cross_decomposition import PLSRegression
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import statsmodels.api as sm

sys.path.insert(0, "coherence-benchmark")
from t901_analysis import _granular_run, _bin_data, _sliding_C, measure_recovery, compute_mobility_proxies

RNG = np.random.default_rng(42)
CONTACT_DIST = 4.0  # matching neighbor_turnover threshold

# ─── Load existing ensemble ───
with open("coherence-benchmark/results/t901_ensemble.json") as f:
    raw_ensemble = json.load(f)

N_RUNS = len(raw_ensemble)
print(f"Loaded {N_RUNS} existing ensemble runs")


# ═══════════════════════════════════════════════════════════════════
# STRUCTURAL DESCRIPTOR COMPUTATION
# ═══════════════════════════════════════════════════════════════════

def compute_structural_descriptors(x, y, vx, vy, radii, removed, T_pre=500):
    """Compute structural descriptors from raw grain trajectories.

    Returns dict of scalar descriptors averaged over pre-perturbation period.
    """
    active = ~removed
    n_active = int(active.sum())
    if n_active < 5:
        return {}

    # Only pre-perturbation
    x_p = np.nan_to_num(x[active, :T_pre], nan=0.0)
    y_p = np.nan_to_num(y[active, :T_pre], nan=0.0)
    rad = radii[active]

    dt_sample = max(1, T_pre // 100)  # sample ~100 time points
    timepoints = range(0, T_pre, dt_sample)
    n_tp = len(timepoints)

    # Accumulators
    coord_nums = []
    overlaps = []
    contact_counts = []
    nn_dists_all = []

    # Graph accumulators
    comp_sizes_all = []
    n_components_all = []
    clustering_coeffs = []

    # Temporal accumulators
    prev_contact_set = None
    jaccards = []

    # Structural accumulators
    delaunay_areas_all = []
    g_r_accum = None
    g_r_bins = np.linspace(0, 6, 31)  # g(r) histogram bins
    g_r_counts = np.zeros(len(g_r_bins) - 1)

    for t in timepoints:
        pos = np.column_stack([x_p[:, t], y_p[:, t]])

        # -- Contact detection (pairwise distance < contact_dist) --
        contacts = set()
        contact_overlaps = []
        for i in range(n_active):
            for j in range(i + 1, n_active):
                dij = np.linalg.norm(pos[i] - pos[j])
                if dij < CONTACT_DIST:
                    contacts.add((i, j))
                    ov = max(0, rad[i] + rad[j] - dij)
                    contact_overlaps.append(ov)

        k = len(contacts)
        contact_counts.append(k)
        coord_nums.append(2.0 * k / n_active if n_active > 0 else 0)
        if contact_overlaps:
            overlaps.extend(contact_overlaps)

        # -- Nearest neighbor distances --
        for i in range(n_active):
            dists = [np.linalg.norm(pos[i] - pos[j]) for j in range(n_active) if j != i]
            if dists:
                nn_dists_all.append(min(dists))

        # -- Graph connectivity (from contact network) --
        if k > 0:
            adj = {i: set() for i in range(n_active)}
            for (i, j) in contacts:
                adj[i].add(j)
                adj[j].add(i)

            visited = set()
            comps = []
            for i in range(n_active):
                if i not in visited:
                    stack = [i]
                    comp = set()
                    while stack:
                        v = stack.pop()
                        if v not in visited:
                            visited.add(v)
                            comp.add(v)
                            stack.extend(adj[v] - visited)
                    comps.append(comp)
            comp_sizes = [len(c) for c in comps]
            comp_sizes_all.extend(comp_sizes)
            n_components_all.append(len(comps))

            # Local clustering coefficient (transitivity)
            total_triangles = 0
            total_triples = 0
            for i in range(n_active):
                neigh = list(adj[i])
                d = len(neigh)
                if d >= 2:
                    possible = d * (d - 1) / 2
                    actual = 0
                    for ii, ni in enumerate(neigh):
                        for nj in neigh[ii+1:]:
                            if nj in adj[ni]:
                                actual += 1
                    total_triangles += actual
                    total_triples += possible
            if total_triples > 0:
                clustering_coeffs.append(total_triangles / total_triples)
        else:
            comp_sizes_all.append(1)
            n_components_all.append(n_active)
            clustering_coeffs.append(0.0)

        # -- Temporal Jaccard similarity --
        if prev_contact_set is not None:
            inter = len(contacts & prev_contact_set)
            union = len(contacts | prev_contact_set)
            jaccards.append(inter / union if union > 0 else 1.0)
        prev_contact_set = contacts

        # -- Delaunay/Voronoi areas --
        if n_active >= 4:
            try:
                tri = Delaunay(pos)
                # Compute areas of each triangle
                for simplex in tri.simplices:
                    p = pos[simplex]
                    area = 0.5 * abs(np.cross(p[1] - p[0], p[2] - p[0]))
                    delaunay_areas_all.append(area)
            except Exception:
                pass

        # -- Radial distribution g(r) --
        for i in range(n_active):
            for j in range(i + 1, n_active):
                dij = np.linalg.norm(pos[i] - pos[j])
                if dij < 6.0:
                    bin_idx = int(dij / (6.0 / (len(g_r_bins) - 1)))
                    if 0 <= bin_idx < len(g_r_counts):
                        g_r_counts[bin_idx] += 1.0 / n_tp

    # Normalize g(r) by expected uniform density
    # avg density = n_active / box_area. Box ~ 40 x (30-5) ≈ 40×25 = 1000
    box_area = 40.0 * 30.0
    density = n_active / box_area
    r_vals = (g_r_bins[:-1] + g_r_bins[1:]) / 2
    shell_volumes = 4.0 * np.pi * r_vals ** 2 * (g_r_bins[1] - g_r_bins[0])  # 2D: 2πr*dr
    g_r = np.where(shell_volumes > 0,
                   g_r_counts / (density * shell_volumes * n_active * n_tp / 2), 0)

    descriptors = {}

    # Contact-based
    descriptors["mean_coordination"] = np.mean(coord_nums) if coord_nums else np.nan
    descriptors["coord_std"] = np.std(coord_nums) if coord_nums else np.nan
    descriptors["mean_contact_count"] = np.mean(contact_counts) if contact_counts else np.nan
    descriptors["contact_density"] = np.mean(contact_counts) / (n_active * (n_active - 1) / 2) if contact_counts else np.nan

    # Overlap/force
    descriptors["mean_overlap"] = np.mean(overlaps) if overlaps else np.nan
    descriptors["overlap_std"] = np.std(overlaps) if overlaps else np.nan
    descriptors["overlap_cv"] = (np.std(overlaps) / np.mean(overlaps)) if overlaps and np.mean(overlaps) > 0 else np.nan

    # Nearest neighbor
    descriptors["mean_nn_dist"] = np.mean(nn_dists_all) if nn_dists_all else np.nan
    descriptors["nn_dist_std"] = np.std(nn_dists_all) if nn_dists_all else np.nan
    descriptors["nn_dist_skew"] = float(pd_skew(nn_dists_all)) if nn_dists_all and len(nn_dists_all) > 5 else np.nan

    # Graph connectivity
    descriptors["mean_clustering"] = np.mean(clustering_coeffs) if clustering_coeffs else np.nan
    descriptors["clustering_std"] = np.std(clustering_coeffs) if clustering_coeffs else np.nan
    descriptors["mean_n_components"] = np.mean(n_components_all) if n_components_all else np.nan
    descriptors["mean_largest_comp"] = np.mean(comp_sizes_all) / n_active if comp_sizes_all else np.nan

    # Structural
    descriptors["mean_delaunay_area"] = np.mean(delaunay_areas_all) if delaunay_areas_all else np.nan
    descriptors["delaunay_area_std"] = np.std(delaunay_areas_all) if delaunay_areas_all else np.nan
    descriptors["delaunay_area_cv"] = (np.std(delaunay_areas_all) / np.mean(delaunay_areas_all)) if delaunay_areas_all and np.mean(delaunay_areas_all) > 0 else np.nan

    # g(r) features
    descriptors["g_r_peak_height"] = np.max(g_r) if len(g_r) > 0 and np.any(np.isfinite(g_r)) else np.nan
    descriptors["g_r_peak_pos"] = r_vals[np.argmax(g_r)] if len(g_r) > 0 and np.any(np.isfinite(g_r)) else np.nan
    descriptors["g_r_second_peak"] = np.sort(g_r)[-2] if len(g_r) > 3 and np.any(np.isfinite(g_r)) else np.nan

    # Temporal stability
    descriptors["contact_jaccard_mean"] = np.mean(jaccards) if jaccards else np.nan
    descriptors["contact_jaccard_std"] = np.std(jaccards) if jaccards else np.nan

    return descriptors


def pd_skew(arr):
    """Simple skewness."""
    n = len(arr)
    if n < 3:
        return np.nan
    mean = np.mean(arr)
    std = np.std(arr, ddof=0)
    if std == 0:
        return 0.0
    return np.mean((arr - mean) ** 3) / (std ** 3)


# ═══════════════════════════════════════════════════════════════════
# GENERATE STRUCTURAL DESCRIPTORS FOR ALL 60 RUNS
# ═══════════════════════════════════════════════════════════════════

print("\nRe-running 60 DEM simulations to extract structural descriptors...")
print("(This takes ~2-3 minutes for all 60 runs)\n")

t0 = time.time()
friction_levels = [0.05, 0.1, 0.2, 0.4, 0.6, 0.8]
all_descriptors = []

for fi, friction in enumerate(friction_levels):
    for rep in range(10):
        seed = rep + 100 * fi
        idx = fi * 10 + rep
        y, x, vx, vy, radii, removed = _granular_run(
            n_grains=50, n_steps=1000, removal_step=500,
            removal_fraction=0.1, friction=friction, seed=seed,
        )

        desc = compute_structural_descriptors(x, y, vx, vy, radii, removed, T_pre=500)
        desc["friction"] = friction
        desc["rep"] = rep
        desc["seed"] = seed
        all_descriptors.append(desc)

        if (rep + 1) % 5 == 0:
            elapsed = time.time() - t0
            print(f"  friction={friction:.2f}, rep={rep+1}/10  ({elapsed:.0f}s)")

print(f"\nAll 60 runs complete in {time.time() - t0:.0f}s")

# ═══════════════════════════════════════════════════════════════════
# MERGE WITH EXISTING ENSEMBLE DATA
# ═══════════════════════════════════════════════════════════════════

descriptor_names = [k for k in all_descriptors[0].keys() if k not in ("friction", "rep", "seed")]
print(f"\nComputed {len(descriptor_names)} structural descriptors per run:")
for i, name in enumerate(descriptor_names):
    vals = [d[name] for d in all_descriptors]
    n_valid = sum(1 for v in vals if not (isinstance(v, float) and np.isnan(v)))
    mean_v = np.nanmean(vals)
    print(f"  {i+1:2d}. {name:>25s}  n_valid={n_valid:2d}  mean={mean_v:.4f}")

# Build data matrix
struct_matrix = np.full((N_RUNS, len(descriptor_names)), np.nan)
for i, desc in enumerate(all_descriptors):
    for j, name in enumerate(descriptor_names):
        struct_matrix[i, j] = desc.get(name, np.nan)

# Existing ensemble data
friction_vals = np.array([r["friction"] for r in raw_ensemble])
pre_C = np.array([r["pre_C"] for r in raw_ensemble])
dip = np.array([r["dip"] for r in raw_ensemble])
restoration = np.array([r["restoration"] for r in raw_ensemble])
tau_rec = np.array([r["tau_rec"] for r in raw_ensemble])
msd = np.array([r["msd"] for r in raw_ensemble])
rms_vel = np.array([r["rms_velocity"] for r in raw_ensemble])
turnover = np.array([r["neighbor_turnover"] for r in raw_ensemble])
pack_var = np.array([r["packing_var"] for r in raw_ensemble])
I_pred = np.array([r["pre_I_pred"] for r in raw_ensemble])
C_sigma = np.array([r["pre_C_sigma"] for r in raw_ensemble])
MSE_s1 = np.array([r["pre_MSE_s1"] for r in raw_ensemble])

# Compute Residual(C) = C - E[C | friction]
good_cf = ~(np.isnan(pre_C) | np.isnan(friction_vals))
X_cf = sm.add_constant(friction_vals[good_cf])
m_c_f = sm.OLS(pre_C[good_cf], X_cf).fit()
residual_C = np.full(N_RUNS, np.nan)
residual_C[good_cf] = m_c_f.resid
print(f"\nResidual(C) computed: C ~ friction, R² = {m_c_f.rsquared:.4f}")
print(f"  Residual(C) range: [{np.nanmin(residual_C):.4f}, {np.nanmax(residual_C):.4f}]")


# ═══════════════════════════════════════════════════════════════════
# D1: STRUCTURE SEARCH — rank all variables by correlation with Residual(C)
# ═══════════════════════════════════════════════════════════════════

print("\n" + "=" * 78)
print("  D1: STRUCTURE SEARCH — correlation with Residual(C)")
print("=" * 78)

# Combine structural descriptors + existing mobility + competitor metrics
all_var_names = descriptor_names + [
    "msd", "rms_velocity", "neighbor_turnover", "packing_var",
    "pre_I_pred", "pre_C_sigma", "pre_MSE_s1",
]
all_var_vals = np.column_stack([struct_matrix] + [
    msd, rms_vel, turnover, pack_var, I_pred, C_sigma, MSE_s1,
])

results_table = []
for j, name in enumerate(all_var_names):
    vals = all_var_vals[:, j]
    valid = ~(np.isnan(residual_C) | np.isnan(vals))
    n_v = valid.sum()
    if n_v < 10:
        continue
    r_p, p_p = pearsonr(residual_C[valid], vals[valid])
    r_s, p_s = spearmanr(residual_C[valid], vals[valid])

    # Univariate R² for predicting residual(C)
    X_u = vals[valid].reshape(-1, 1)
    y_u = residual_C[valid]
    m_u = LinearRegression().fit(X_u, y_u)
    r2_u = r2_score(y_u, m_u.predict(X_u))

    results_table.append({
        "name": name, "r": r_p, "p": p_p, "rho": r_s, "r2": r2_u, "n": n_v,
    })

results_table.sort(key=lambda x: abs(x["r"]), reverse=True)

print(f"\n  {'Rank':>4s}  {'Variable':>30s}  {'Pearson r':>10s}  {'p-value':>10s}  {'Spearman ρ':>10s}  {'R²':>8s}  {'n':>4s}")
print(f"  {'-' * 82}")

for rank, row in enumerate(results_table, 1):
    sig = " ***" if row["p"] < 0.001 else " **" if row["p"] < 0.01 else " *" if row["p"] < 0.05 else ""
    print(f"  {rank:>4d}  {row['name']:>30s}  {row['r']:>+10.4f}  {row['p']:>10.4e}{sig}  {row['rho']:>+10.4f}  {row['r2']:>8.4f}  {row['n']:>4d}")

# Identify top hits
top_hits = [r for r in results_table if r["p"] < 0.05]
print(f"\n  Significant correlations (p < 0.05): {len(top_hits)} / {len(results_table)}")
for r in top_hits:
    print(f"    {r['name']:>30s}: r={r['r']:+.4f}, p={r['p']:.4e}, R²={r['r2']:.4f}")


# ═══════════════════════════════════════════════════════════════════
# D2: DIMENSIONALITY ANALYSIS
# ═══════════════════════════════════════════════════════════════════

print("\n" + "=" * 78)
print("  D2: DIMENSIONALITY — PCA and factor structure of structural descriptors")
print("=" * 78)

# Use only structural descriptors (not mobility proxies)
struct_valid = ~np.any(np.isnan(struct_matrix), axis=1)
struct_clean = struct_matrix[struct_valid]

if struct_clean.shape[0] > struct_clean.shape[1]:
    scaler = StandardScaler()
    struct_scaled = scaler.fit_transform(struct_clean)

    # PCA
    pca = PCA()
    pca_scores = pca.fit_transform(struct_scaled)

    print(f"\n  PCA on {len(descriptor_names)} structural descriptors, n={struct_clean.shape[0]}:")
    print(f"\n  {'PC':>4s}  {'Eigenvalue':>12s}  {'Variance %':>12s}  {'Cumulative %':>14s}")
    print(f"  {'-' * 46}")

    ev = pca.explained_variance_
    evr = pca.explained_variance_ratio_
    cum = np.cumsum(evr)

    for i in range(min(10, len(ev))):
        print(f"  {i+1:>4d}  {ev[i]:>12.4f}  {evr[i]:>12.4f}  {cum[i]:>14.4f}")

    # How many PCs to explain 80% variance?
    n_80 = np.searchsorted(cum, 0.80) + 1
    print(f"\n  PCs needed for 80% variance: {n_80}")
    print(f"  Variance explained by PC1: {evr[0]:.4f} ({evr[0]*100:.1f}%)")

    # Does PC1 correlate with Residual(C)?
    rc_for_pca = residual_C[struct_valid]
    valid_rc = ~np.isnan(rc_for_pca)
    r_pc1_rc, p_pc1_rc = pearsonr(pca_scores[valid_rc, 0], rc_for_pca[valid_rc])
    print(f"  PC1 vs Residual(C): r = {r_pc1_rc:+.4f}, p = {p_pc1_rc:.4e}")

    # Top loadings on PC1
    pc1_loadings = pca.components_[0]
    loading_table = [(descriptor_names[i], pc1_loadings[i]) for i in range(len(descriptor_names))]
    loading_table.sort(key=lambda x: abs(x[1]), reverse=True)

    print(f"\n  Top 10 PC1 loadings:")
    print(f"  {'Variable':>25s}  {'Loading':>10s}")
    print(f"  {'-' * 37}")
    for name, loading in loading_table[:10]:
        print(f"  {name:>25s}  {loading:>+10.4f}")

    # H1: single factor? Check if PC1 dominates
    is_single_factor = evr[0] > 0.35 and evr[1] < evr[0] / 2
    verdict_d2 = (
        "Single-factor" if is_single_factor
        else "Multi-factor" if n_80 > 3
        else "Indeterminate"
    )
    print(f"\n  Verdict: {verdict_d2}")
    print(f"  (PC1 = {evr[0]*100:.1f}%, PC2 = {evr[1]*100:.1f}%, ratio = {evr[0]/evr[1]:.2f})")
else:
    print(f"  Insufficient data: n={struct_clean.shape[0]}, p={struct_clean.shape[1]}")
    verdict_d2 = "Indeterminate"

# Also: PLS regression — predict Residual(C) from structural descriptors
print(f"\n  ── PLS: predict Residual(C) from structural descriptors ──")

struct_for_pls = struct_matrix.copy()
rc_for_pls = residual_C.copy()

# Remove rows with any NaN
pls_valid = ~(np.isnan(rc_for_pls) | np.any(np.isnan(struct_for_pls), axis=1))
if pls_valid.sum() > 20:
    X_pls = StandardScaler().fit_transform(struct_for_pls[pls_valid])
    y_pls = rc_for_pls[pls_valid]

    pls = PLSRegression(n_components=min(5, X_pls.shape[1]))
    pls.fit(X_pls, y_pls)
    y_pred_pls = pls.predict(X_pls)
    pls_r2 = r2_score(y_pls, y_pred_pls)

    # Cross-validated PLS
    from sklearn.model_selection import cross_val_score
    pls_cv = PLSRegression(n_components=min(3, X_pls.shape[1]))
    cv_scores = cross_val_score(pls_cv, X_pls, y_pls, cv=5, scoring='r2')
    print(f"  PLS (n_comp=3): train R² = {pls_r2:.4f}, CV R² = {np.mean(cv_scores):.4f} ± {np.std(cv_scores):.4f}")

    # PLS1 loadings
    pls1_w = pls.x_weights_[:, 0]
    pls_top = [(descriptor_names[i], pls1_w[i]) for i in range(len(descriptor_names))]
    pls_top.sort(key=lambda x: abs(x[1]), reverse=True)
    print(f"\n  Top PLS1 weights for predicting Residual(C):")
    for name, w in pls_top[:8]:
        print(f"    {name:>25s}: {w:+.4f}")
else:
    print(f"  Insufficient complete cases: {pls_valid.sum()}")


# ═══════════════════════════════════════════════════════════════════
# D3: RECOVERY PATHWAY — mediation-style analysis
# ═══════════════════════════════════════════════════════════════════

print("\n" + "=" * 78)
print("  D3: RECOVERY PATHWAY — does Residual(C) act through known observables?")
print("=" * 78)

# For each target and each candidate mediator:
candidate_mediators = descriptor_names + [
    "msd", "rms_velocity", "neighbor_turnover", "packing_var",
]

targets = [("dip", "ΔC"), ("restoration", "restoration"), ("tau_rec", "τ_rec")]
target_vals = {"dip": dip, "restoration": restoration, "tau_rec": tau_rec}

for tname, tlabel in targets:
    y_t = target_vals[tname]
    print(f"\n  Target: {tlabel}")

    # Direct effect: Residual(C) → recovery
    valid_direct = ~(np.isnan(residual_C) | np.isnan(y_t))
    X_d = sm.add_constant(residual_C[valid_direct])
    m_direct = sm.OLS(y_t[valid_direct], X_d).fit()
    direct_effect = m_direct.params[1] if len(m_direct.params) > 1 else 0
    direct_p = m_direct.pvalues[1] if len(m_direct.pvalues) > 1 else 1
    direct_r2 = m_direct.rsquared

    print(f"    Direct: Residual(C) → {tlabel}: β = {direct_effect:+.4f}, p = {direct_p:.4e}, R² = {direct_r2:.4f}")

    # For each candidate mediator: Residual(C) → mediator → recovery
    mediator_results = []
    for med_name in candidate_mediators:
        med_idx = all_var_names.index(med_name) if med_name in all_var_names else -1
        if med_idx < 0:
            continue
        med_vals = all_var_vals[:, med_idx]

        valid = ~(np.isnan(residual_C) | np.isnan(med_vals) | np.isnan(y_t))
        if valid.sum() < 20:
            continue

        # Step 1: Residual(C) → mediator (a path)
        X_a = sm.add_constant(residual_C[valid])
        m_a = sm.OLS(med_vals[valid], X_a).fit()
        a_coef = m_a.params[1] if len(m_a.params) > 1 else 0
        a_p = m_a.pvalues[1] if len(m_a.pvalues) > 1 else 1
        a_r2 = m_a.rsquared

        # Step 2: Residual(C) + mediator → recovery (b path + direct')
        X_b = sm.add_constant(np.column_stack([residual_C[valid], med_vals[valid]]))
        m_b = sm.OLS(y_t[valid], X_b).fit()
        b_coef = m_b.params[2] if len(m_b.params) > 2 else 0
        b_p = m_b.pvalues[2] if len(m_b.pvalues) > 2 else 1
        c_prime = m_b.params[1] if len(m_b.params) > 1 else 0  # direct' after mediator

        # Indirect effect = a * b
        indirect = a_coef * b_coef
        remaining = c_prime  # residual direct effect after controlling for mediator

        mediator_results.append({
            "mediator": med_name,
            "a_coef": a_coef, "a_p": a_p, "a_r2": a_r2,
            "b_coef": b_coef, "b_p": b_p,
            "indirect": indirect,
            "remaining_direct": remaining,
        })

    mediator_results.sort(key=lambda x: abs(x["indirect"]), reverse=True)

    print(f"    Top mediators (by indirect effect):")
    print(f"    {'Mediator':>25s}  {'a (RC→M)':>10s}  {'b (M→Y|RC)':>10s}  {'Indirect':>10s}  {'Direct\'':>10s}")
    print(f"    {'-' * 69}")
    for mr in mediator_results[:10]:
        sig_a = "*" if mr["a_p"] < 0.05 else " "
        sig_b = "*" if mr["b_p"] < 0.05 else " "
        print(f"    {mr['mediator']:>25s}  {mr['a_coef']:>+10.4f}{sig_a}  {mr['b_coef']:>+10.4f}{sig_b}  {mr['indirect']:>+10.4f}  {mr['remaining_direct']:>+10.4f}")

    # Summary: what fraction of Residual(C)'s effect is mediated?
    # Compare direct effect vs remaining direct after best mediator
    if mediator_results:
        best = mediator_results[0]
        print(f"    Direct effect (no mediator): β = {direct_effect:+.4f}")
        print(f"    Direct' after '{best['mediator']}': β = {best['remaining_direct']:+.4f}")
        frac_mediated = 1 - (best["remaining_direct"] / direct_effect) if abs(direct_effect) > 0.001 else 0
        print(f"    Fraction mediated: {frac_mediated:.2%}")


# ═══════════════════════════════════════════════════════════════════
# D4: WITHIN-LEVEL TEST — does Residual(C) predict recovery within friction?
# ═══════════════════════════════════════════════════════════════════

print("\n" + "=" * 78)
print("  D4: WITHIN-LEVEL — Residual(C) vs recovery within each friction level")
print("=" * 78)

print(f"\n  {'Friction':>8s}  {'N':>4s}  {'r(ΔC)':>10s}  {'p(ΔC)':>10s}  {'r(Rest.)':>10s}  {'p(Rest.)':>10s}  {'r(τ)':>10s}  {'p(τ)':>10s}")
print(f"  {'-' * 78}")

within_results = {}
for fl in friction_levels:
    mask = np.abs(friction_vals - fl) < 0.01
    n_l = int(mask.sum())

    rcs = residual_C[mask]
    dips = dip[mask]
    rests = restoration[mask]
    taus = tau_rec[mask]

    r_dip = p_dip = r_rest = p_rest = r_tau = p_tau = np.nan

    valid_d = ~(np.isnan(rcs) | np.isnan(dips))
    if valid_d.sum() >= 5:
        r_dip, p_dip = pearsonr(rcs[valid_d], dips[valid_d])

    valid_r = ~(np.isnan(rcs) | np.isnan(rests))
    if valid_r.sum() >= 5:
        r_rest, p_rest = pearsonr(rcs[valid_r], rests[valid_r])

    valid_t = ~(np.isnan(rcs) | np.isnan(taus))
    if valid_t.sum() >= 5:
        r_tau, p_tau = pearsonr(rcs[valid_t], taus[valid_t])

    sig_d = " *" if p_dip < 0.05 else "  "
    sig_r = " *" if p_rest < 0.05 else "  "
    sig_t = " *" if p_tau < 0.05 else "  "

    print(f"  {fl:>8.2f}  {n_l:>4d}  {r_dip:>+10.4f}{sig_d}  {p_dip:>10.4e}  {r_rest:>+10.4f}{sig_r}  {p_rest:>10.4e}  {r_tau:>+10.4f}{sig_t}  {p_tau:>10.4e}")

    within_results[fl] = {"r_dip": r_dip, "p_dip": p_dip, "r_rest": r_rest, "p_rest": p_rest, "r_tau": r_tau, "p_tau": p_tau}

# Aggregated within-level correlation (Fisher z-transform)
def fisher_z(r):
    return 0.5 * np.log((1 + r) / (1 - r + 1e-10))

def inv_fisher(z):
    return np.tanh(z)

z_dips = []
z_restr = []
z_taus = []
for fl in friction_levels:
    wr = within_results[fl]
    if not np.isnan(wr["r_dip"]):
        z_dips.append(fisher_z(wr["r_dip"]))
        z_restr.append(fisher_z(wr["r_rest"]))
        z_taus.append(fisher_z(wr["r_tau"]))

if z_dips:
    mean_z_dip = np.mean(z_dips)
    mean_r_dip = inv_fisher(mean_z_dip)
    mean_z_rest = np.mean(z_restr)
    mean_r_rest = inv_fisher(mean_z_rest)
    mean_z_tau = np.mean(z_taus)
    mean_r_tau = inv_fisher(mean_z_tau)

    print(f"\n  ── Fisher z-aggregated within-level correlations ──")
    print(f"  Mean r(ΔC) = {mean_r_dip:+.4f}")
    print(f"  Mean r(Rest.) = {mean_r_rest:+.4f}")
    print(f"  Mean r(τ) = {mean_r_tau:+.4f}")

    # Contrast with pooled (across-level) correlations
    valid_pooled = ~(np.isnan(residual_C) | np.isnan(dip))
    r_pool_dip, p_pool_dip = pearsonr(residual_C[valid_pooled], dip[valid_pooled])
    r_pool_rest, p_pool_rest = pearsonr(residual_C[valid_pooled], restoration[valid_pooled])
    r_pool_tau, p_pool_tau = pearsonr(residual_C[valid_pooled], tau_rec[valid_pooled])

    print(f"\n  ── Pooled (across-level) correlations ──")
    print(f"  Pooled r(ΔC) = {r_pool_dip:+.4f} (p={p_pool_dip:.4e})")
    print(f"  Pooled r(Rest.) = {r_pool_rest:+.4f} (p={p_pool_rest:.4e})")
    print(f"  Pooled r(τ) = {r_pool_tau:+.4f} (p={p_pool_tau:.4e})")

    print(f"\n  ── Within vs Across comparison ──")
    print(f"  ΔC:       within r={mean_r_dip:+.4f} vs across r={r_pool_dip:+.4f}")
    print(f"  Restoration: within r={mean_r_rest:+.4f} vs across r={r_pool_rest:+.4f}")
    print(f"  τ_rec:    within r={mean_r_tau:+.4f} vs across r={r_pool_tau:+.4f}")

    # Verdict
    if all(abs(z) < 0.3 for z in z_dips):
        verdict_within = "WEAK WITHIN LEVELS — Residual(C) effect is primarily between-level (friction-driven contrast)"
    elif any(p < 0.05 for fl in friction_levels for wr in [within_results[fl]] for p in [wr.get("p_dip", 1)] if not isinstance(p, float)):
        verdict_within = "SURVIVES WITHIN — at least one level shows significant within-level correlation"
    else:
        verdict_within = "MIXED — some levels show signal, others don't"

    print(f"\n  Verdict: {verdict_within}")


# ═══════════════════════════════════════════════════════════════════
# SAVE STRUCTURAL DESCRIPTORS
# ═══════════════════════════════════════════════════════════════════

# Save for reproducibility
output = []
for i in range(N_RUNS):
    record = {"friction": float(friction_vals[i]), "rep": raw_ensemble[i].get("rep", i)}
    for j, name in enumerate(descriptor_names):
        val = struct_matrix[i, j]
        record[name] = None if (isinstance(val, float) and np.isnan(val)) else float(val)
    record["residual_C"] = None if np.isnan(residual_C[i]) else float(residual_C[i])
    output.append(record)

with open("audits/rd017_structural_descriptors.json", "w") as f:
    json.dump(output, f, indent=2)
print(f"\nSaved structural descriptors to audits/rd017_structural_descriptors.json")

# Print versions for report-building
print("\n\n══════════════════════════════════════════════════════════")
print("  RD-017 ANALYSIS COMPLETE — Key numbers for reports")
print("══════════════════════════════════════════════════════════\n")

# D1 top 5
print("D1 TOP 5 CORRELATES OF RESIDUAL(C):")
for r in results_table[:5]:
    print(f"  {r['name']:>25s}: r={r['r']:+.4f}, p={r['p']:.4e}")

# D2 verdict
print(f"\nD2: {verdict_d2}, PC1={evr[0]*100:.1f}%")

# D3 top mediators for restoration
print(f"\nD3: Restoration best mediators:")
for mr in mediator_results[:3]:
    print(f"  {mr['mediator']:>25s}: indirect={mr['indirect']:+.4f}, remaining={mr['remaining_direct']:+.4f}")

# D4 verdict
print(f"\nD4: {verdict_within}")
print(f"  Within ΔC: {mean_r_dip:+.4f} vs across ΔC: {r_pool_dip:+.4f}")
