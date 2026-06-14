"""RD-018: Targeted diagnostics to characterize Residual(C).

Beyond RD-017's 22 structural descriptors, this analysis computes four new
diagnostic families from the existing DEM ensemble:

  A. Force chain topology — force magnitudes, chain detection, fabric tensor
  B. Non-affine displacements (D2_min) — standard granular diagnostic
  C. Alternate binning schemes — C from y-bins, random bins, radius bins
  D. Contact network motifs — triadic profiles, community structure, persistence

Each is correlated with Residual(C) to narrow its physical identity.
"""

import sys, json, time, warnings, math
warnings.filterwarnings("ignore")

import numpy as np
from scipy.stats import pearsonr, spearmanr
from scipy.spatial import Delaunay, distance
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import statsmodels.api as sm

sys.path.insert(0, "coherence-benchmark")
from t901_analysis import _granular_run, _bin_data, _sliding_C, measure_recovery, compute_mobility_proxies
from metrics.total_correlation import compute_C

RNG = np.random.default_rng(42)
CONTACT_DIST = 4.0
STIFFNESS = 500.0

# ─── Load existing ensemble ───
with open("coherence-benchmark/results/t901_ensemble.json") as f:
    raw_ensemble = json.load(f)

N_RUNS = len(raw_ensemble)
print(f"Loaded {N_RUNS} existing ensemble runs")

# ─── Existing ensemble data ───
friction_vals = np.array([r["friction"] for r in raw_ensemble])
pre_C = np.array([r["pre_C"] for r in raw_ensemble])
dip = np.array([r["dip"] for r in raw_ensemble])
restoration = np.array([r["restoration"] for r in raw_ensemble])
tau_rec = np.array([r["tau_rec"] for r in raw_ensemble])
msd = np.array([r["msd"] for r in raw_ensemble])
rms_vel = np.array([r["rms_velocity"] for r in raw_ensemble])
turnover = np.array([r["neighbor_turnover"] for r in raw_ensemble])
pack_var = np.array([r["packing_var"] for r in raw_ensemble])

# Residual(C)
good_cf = ~(np.isnan(pre_C) | np.isnan(friction_vals))
X_cf = sm.add_constant(friction_vals[good_cf])
m_c_f = sm.OLS(pre_C[good_cf], X_cf).fit()
residual_C = np.full(N_RUNS, np.nan)
residual_C[good_cf] = m_c_f.resid
print(f"Residual(C): C ~ friction, R² = {m_c_f.rsquared:.4f}")
print(f"  Range: [{np.nanmin(residual_C):.4f}, {np.nanmax(residual_C):.4f}]")


# ═══════════════════════════════════════════════════════════════════
# HELPER: recompute contact forces from stored positions
# ═══════════════════════════════════════════════════════════════════

def compute_contact_forces(xy, radii, n_active):
    """Compute contact forces from grain positions.

    Args:
        xy: (n_active, 2) array of positions
        radii: (n_active,) array of radii
    Returns:
        force_mags: list of contact force magnitudes
        contacts: set of (i,j) tuples with overlap > 0
    """
    forces = []
    contacts = set()
    for i in range(n_active):
        for j in range(i + 1, n_active):
            dx = xy[j, 0] - xy[i, 0]
            dy = xy[j, 1] - xy[i, 1]
            dist = math.sqrt(dx*dx + dy*dy)
            overlap = radii[i] + radii[j] - dist
            if overlap > 0:
                fn = STIFFNESS * overlap
                forces.append(fn)
                contacts.add((i, j))
    return np.array(forces), contacts


# ═══════════════════════════════════════════════════════════════════
# A: FORCE CHAIN TOPOLOGY
# ═══════════════════════════════════════════════════════════════════

def compute_force_diagnostics(x, y, radii, removed, T_pre=500):
    """Force chain diagnostics from pre-perturbation grain trajectories.

    Returns dict of force-related descriptors.
    """
    active = ~removed
    n_active = int(active.sum())
    if n_active < 5:
        return {}

    x_p = np.nan_to_num(x[active, :T_pre], nan=0.0)
    y_p = np.nan_to_num(y[active, :T_pre], nan=0.0)
    rad = radii[active]

    dt_sample = max(1, T_pre // 100)
    timepoints = range(0, T_pre, dt_sample)

    all_force_mags = []
    all_force_cvs = []
    mean_force_over_time = []
    contact_counts_A = []  # avoid name collision

    # Fabric tensor accumulators
    phi_xx_list, phi_yy_list, phi_xy_list = [], [], []

    # Force chain detection
    chain_lengths = []

    for t in timepoints:
        xy = np.column_stack([x_p[:, t], y_p[:, t]])
        force_mags, contacts = compute_contact_forces(xy, rad, n_active)

        if len(force_mags) > 0:
            all_force_mags.extend(force_mags.tolist())
            mean_f = np.mean(force_mags)
            std_f = np.std(force_mags)
            all_force_cvs.append(std_f / mean_f if mean_f > 0 else 0)
            mean_force_over_time.append(mean_f)

            # Contact count
            contact_counts_A.append(len(contacts))

            # Fabric tensor: (1/N_c) * sum(n_i * n_j) over all contacts
            # where n is the unit normal vector
            phi_xx, phi_yy, phi_xy = 0.0, 0.0, 0.0
            n_contacts = len(contacts)
            if n_contacts > 0:
                for (i, j) in contacts:
                    dx = xy[j, 0] - xy[i, 0]
                    dy = xy[j, 1] - xy[i, 1]
                    d = math.sqrt(dx*dx + dy*dy)
                    if d > 0:
                        nx, ny = dx/d, dy/d
                        phi_xx += nx*nx
                        phi_yy += ny*ny
                        phi_xy += nx*ny
                phi_xx /= n_contacts
                phi_yy /= n_contacts
                phi_xy /= n_contacts
            phi_xx_list.append(phi_xx)
            phi_yy_list.append(phi_yy)
            phi_xy_list.append(phi_xy)

            # Force chain detection: find chains of particles with force > threshold
            # A chain is a connected component in the graph where edges have force > median
            if len(force_mags) > 3:
                threshold = np.median(force_mags)
                # Build graph of strong contacts
                strong_adj = {i: set() for i in range(n_active)}
                for idx, (i, j) in enumerate(contacts):
                    if force_mags[idx] > threshold:
                        strong_adj[i].add(j)
                        strong_adj[j].add(i)

                # Find connected components (chains)
                visited = set()
                for i in range(n_active):
                    if i not in visited and strong_adj[i]:
                        stack = [i]
                        chain = set()
                        while stack:
                            v = stack.pop()
                            if v not in visited:
                                visited.add(v)
                                chain.add(v)
                                stack.extend(strong_adj[v] - visited)
                        if len(chain) >= 2:
                            chain_lengths.append(len(chain))
        else:
            contact_counts_A.append(0)

    descriptors = {}

    # Force magnitude statistics
    if all_force_mags:
        descriptors["force_mean"] = float(np.mean(all_force_mags))
        descriptors["force_std"] = float(np.std(all_force_mags))
        descriptors["force_cv"] = float(np.std(all_force_mags) / max(np.mean(all_force_mags), 1e-10))
        descriptors["force_skew"] = float(pd_skew(all_force_mags)) if len(all_force_mags) > 3 else np.nan
        descriptors["force_max"] = float(np.max(all_force_mags))
        descriptors["force_median"] = float(np.median(all_force_mags))
    else:
        for k in ["force_mean", "force_std", "force_cv", "force_skew", "force_max", "force_median"]:
            descriptors[k] = np.nan

    # Force temporal stability
    if mean_force_over_time:
        descriptors["force_temporal_cv"] = float(np.std(mean_force_over_time) / max(np.mean(mean_force_over_time), 1e-10))
        # Trend in force over time
        ft = np.array(mean_force_over_time)
        if len(ft) > 5:
            from scipy.stats import linregress
            trend = linregress(np.arange(len(ft)), ft)
            descriptors["force_trend"] = float(trend.slope)
            descriptors["force_trend_p"] = float(trend.pvalue)
        else:
            descriptors["force_trend"] = 0.0
            descriptors["force_trend_p"] = 1.0
    else:
        descriptors["force_temporal_cv"] = np.nan
        descriptors["force_trend"] = np.nan
        descriptors["force_trend_p"] = np.nan

    # Force CV over time
    if all_force_cvs:
        descriptors["force_cv_temporal_cv"] = float(np.std(all_force_cvs) / max(np.mean(all_force_cvs), 1e-10))
    else:
        descriptors["force_cv_temporal_cv"] = np.nan

    # Fabric anisotropy: phi_max - phi_min (deviator)
    if phi_xx_list:
        mean_phi_xx = np.mean(phi_xx_list)
        mean_phi_yy = np.mean(phi_yy_list)
        mean_phi_xy = np.mean(phi_xy_list)
        # Fabric deviator = sqrt((phi_xx - phi_yy)^2 + 4*phi_xy^2) / (phi_xx + phi_yy)
        dev = math.sqrt((mean_phi_xx - mean_phi_yy)**2 + 4*mean_phi_xy**2) / max(mean_phi_xx + mean_phi_yy, 1e-10)
        descriptors["fabric_anisotropy"] = float(dev)
        descriptors["fabric_xx"] = float(mean_phi_xx)
        descriptors["fabric_xy"] = float(mean_phi_xy)
        # Principal direction
        descriptors["fabric_angle"] = float(0.5 * math.atan2(2*mean_phi_xy, mean_phi_xx - mean_phi_yy))
    else:
        for k in ["fabric_anisotropy", "fabric_xx", "fabric_xy", "fabric_angle"]:
            descriptors[k] = np.nan

    # Force chain length
    if chain_lengths:
        descriptors["chain_mean_length"] = float(np.mean(chain_lengths))
        descriptors["chain_max_length"] = float(np.max(chain_lengths))
        descriptors["chain_n_chains"] = float(len(chain_lengths))
    else:
        descriptors["chain_mean_length"] = 0.0
        descriptors["chain_max_length"] = 0.0
        descriptors["chain_n_chains"] = 0.0

    return descriptors


# ═══════════════════════════════════════════════════════════════════
# B: NON-AFFINE DISPLACEMENTS (D²_min)
# ═══════════════════════════════════════════════════════════════════

def compute_non_affine_displacements(x, y, radii, removed, T_pre=500):
    """Compute D²_min — standard non-affine displacement diagnostic.

    For each grain over each time interval, computes the best-fit affine
    deformation gradient F that maps the grain's neighborhood from t to t+dt,
    then D²_min is the mean squared residual.

    Returns dict of D²_min statistics.
    """
    active = ~removed
    n_active = int(active.sum())
    if n_active < 5:
        return {}

    x_p = np.nan_to_num(x[active, :T_pre], nan=0.0)
    y_p = np.nan_to_num(y[active, :T_pre], nan=0.0)
    rad = radii[active]

    # Compute D²_min with dt = 5 timesteps (small enough to capture affine deformation)
    dt = 5
    step = 10
    max_t = T_pre - dt

    all_D2 = []
    all_theta = []  # rotation angle from affine deformation

    for t in range(0, max_t, step):
        xy_t = np.column_stack([x_p[:, t], y_p[:, t]])
        xy_tdt = np.column_stack([x_p[:, t + dt], y_p[:, t + dt]])
        displacements = xy_tdt - xy_t

        for i in range(n_active):
            # Find neighbors within contact distance
            neigh = []
            for j in range(n_active):
                if j == i:
                    continue
                dij = np.linalg.norm(xy_t[i] - xy_t[j])
                if dij < CONTACT_DIST * 1.5:  # slightly larger than contact dist
                    neigh.append(j)

            if len(neigh) < 3:
                continue

            # Build matrices for least-squares affine fit
            # We want F (2x2) that maps dr_i(t) → dr_i(t+dt) + d_i
            # dr_j = r_j - r_i
            neigh_arr = np.array(neigh)
            Nn = len(neigh_arr)

            # Reference positions relative to grain i
            dr0 = xy_t[neigh_arr] - xy_t[i]  # (Nn, 2)
            # Displacements of neighbors relative to grain i displacement
            du = xy_tdt[neigh_arr] - xy_tdt[i]  # (Nn, 2)

            # Solve F @ dr0.T ≈ du.T with least squares
            # F = du.T @ dr0 @ inv(dr0.T @ dr0) if well-conditioned
            A = dr0.T @ dr0  # (2, 2)
            try:
                cond = np.linalg.cond(A)
                if cond > 1e8:
                    continue
                F = np.linalg.solve(A, dr0.T @ du).T  # (2, 2)
            except np.linalg.LinAlgError:
                continue

            # Predicted affine displacements
            du_affine = dr0 @ F.T  # (Nn, 2)

            # Non-affine residual
            du_non_affine = du - du_affine
            D2 = np.mean(np.sum(du_non_affine**2, axis=1))
            all_D2.append(float(D2))

            # Rotation angle from F (polar decomposition)
            # F = R * U, extract rotation via atan2(F[1,0] - F[0,1], F[0,0] + F[1,1])
            theta = math.atan2(F[1, 0] - F[0, 1], F[0, 0] + F[1, 1])
            all_theta.append(theta)

    descriptors = {}
    if all_D2:
        descriptors["D2_min_mean"] = float(np.mean(all_D2))
        descriptors["D2_min_std"] = float(np.std(all_D2))
        descriptors["D2_min_cv"] = float(np.std(all_D2) / max(np.mean(all_D2), 1e-10))
        descriptors["D2_min_skew"] = float(pd_skew(all_D2)) if len(all_D2) > 3 else np.nan
        descriptors["D2_min_max"] = float(np.max(all_D2))
        descriptors["D2_min_median"] = float(np.median(all_D2))
    else:
        for k in ["D2_min_mean", "D2_min_std", "D2_min_cv", "D2_min_skew", "D2_min_max", "D2_min_median"]:
            descriptors[k] = np.nan

    if all_theta:
        descriptors["rotation_mean"] = float(np.mean(all_theta))
        descriptors["rotation_std"] = float(np.std(all_theta))
    else:
        descriptors["rotation_mean"] = np.nan
        descriptors["rotation_std"] = np.nan

    return descriptors


# ═══════════════════════════════════════════════════════════════════
# C: ALTERNATE BINNING SCHEMES
# ═══════════════════════════════════════════════════════════════════

def compute_C_alternate_binning(x, y, radii, removed, T_pre=500):
    """Compute C from different binning schemes.

    Standard: bin by x-position (as in _bin_data)
    Alternate: bin by y-position, by grain radius, by random assignment

    Returns C values for each scheme + correlations with standard C.
    """
    active = ~removed
    n_active = int(active.sum())
    if n_active < 5:
        return {}

    y_full = np.nan_to_num(y[active, :T_pre], nan=0.0)
    x_full = np.nan_to_num(x[active, :T_pre], nan=0.0)
    rad = radii[active]

    n_bins = min(10, n_active // 3)
    descriptors = {}

    # Helper: compute C from a binning order
    def _c_from_order(order):
        bins = np.array_split(order, n_bins)
        binned = np.array([np.mean(y_full[b], axis=0) for b in bins])
        try:
            return float(compute_C(binned, "gaussian"))
        except Exception:
            return np.nan

    # Standard C (x-binning)
    with np.errstate(invalid="ignore"):
        final_x = np.nanmean(x_full[:, -100:], axis=1)
    final_x = np.where(np.isnan(final_x), np.nanmean(x_full[:, :100], axis=1), final_x)
    x_order = np.argsort(final_x)
    C_x = _c_from_order(x_order)

    # Y-binning
    with np.errstate(invalid="ignore"):
        final_y = np.nanmean(y_full[:, -100:], axis=1)
    final_y = np.where(np.isnan(final_y), np.nanmean(y_full[:, :100], axis=1), final_y)
    y_order = np.argsort(final_y)
    C_y = _c_from_order(y_order)

    # Radius-binning
    mean_rad = np.mean(rad) if len(rad) > 0 else 0.5
    rad_order = np.argsort(rad)
    C_rad = _c_from_order(rad_order)

    # Random binning (shuffle x-order)
    rng_local = np.random.default_rng(42)
    rand_order = x_order.copy()
    rng_local.shuffle(rand_order)
    C_rand = _c_from_order(rand_order)

    # Store
    descriptors["C_x_bin"] = C_x if not np.isnan(C_x) else np.nan
    descriptors["C_y_bin"] = C_y if not np.isnan(C_y) else np.nan
    descriptors["C_rad_bin"] = C_rad if not np.isnan(C_rad) else np.nan
    descriptors["C_rand_bin"] = C_rand if not np.isnan(C_rand) else np.nan

    return descriptors


# ═══════════════════════════════════════════════════════════════════
# D: CONTACT NETWORK MOTIFS (beyond RD-017)
# ═══════════════════════════════════════════════════════════════════

def compute_network_motifs(x, y, radii, removed, T_pre=500):
    """Compute contact network motif statistics.

    Beyond RD-017's basic graph metrics, compute:
    - Triadic motif profiles (counts of specific 3-node subgraph types)
    - Community structure (modularity via Newman's algorithm)
    - Contact lifetime distributions
    - Percolation threshold (fraction of contacts needed for spanning cluster)
    """
    active = ~removed
    n_active = int(active.sum())
    if n_active < 5:
        return {}

    x_p = np.nan_to_num(x[active, :T_pre], nan=0.0)
    y_p = np.nan_to_num(y[active, :T_pre], nan=0.0)
    rad = radii[active]

    dt_sample = max(1, T_pre // 100)
    timepoints = range(0, T_pre, dt_sample)

    # Motif accumulators
    # For 3-node directed subgraphs, we count:
    # M1: empty (0 edges)
    # M2: single edge (1 edge)
    # M3: two-edge path (2 edges, open triangle)
    # M4: triangle (3 edges, closed)
    # In undirected network, only 3 types: 0, 1, 2, 3 edges

    motif_0, motif_1, motif_2, motif_3 = [], [], [], []

    # Modularity (standard Newman)
    modularities = []

    # Contact lifetime: how long each contact persists
    prev_contacts = None
    contact_first_seen = {}  # (i,j) -> first time index
    contact_lifetimes = []

    # Percolation: fraction of contacts (sorted by force) needed for spanning cluster
    # spanning cluster = component connecting top to bottom of box
    percolation_thresholds = []

    for ti, t in enumerate(timepoints):
        xy = np.column_stack([x_p[:, t], y_p[:, t]])
        _, contacts = compute_contact_forces(xy, rad, n_active)

        # Motif counting in undirected contact graph
        # Build adjacency
        adj = {i: set() for i in range(n_active)}
        for (i, j) in contacts:
            adj[i].add(j)
            adj[j].add(i)

        k_edges = len(contacts)

        # Count triadic motifs (all triples of distinct nodes)
        n_triads_0 = n_triads_1 = n_triads_2 = n_triads_3 = 0
        for i in range(n_active):
            for j in range(i+1, n_active):
                has_ij = (j in adj[i])
                for k in range(j+1, n_active):
                    has_ik = (k in adj[i])
                    has_jk = (k in adj[j])
                    n_e = int(has_ij) + int(has_ik) + int(has_jk)
                    if n_e == 0:
                        n_triads_0 += 1
                    elif n_e == 1:
                        n_triads_1 += 1
                    elif n_e == 2:
                        n_triads_2 += 1
                    else:
                        n_triads_3 += 1

        total_triads = n_triads_0 + n_triads_1 + n_triads_2 + n_triads_3
        if total_triads > 0:
            motif_0.append(n_triads_0 / total_triads)
            motif_1.append(n_triads_1 / total_triads)
            motif_2.append(n_triads_2 / total_triads)
            motif_3.append(n_triads_3 / total_triads)

        # Modularity (Newman's Q)
        if k_edges > 0:
            m = k_edges
            Q = 0.0
            degrees = {i: len(adj[i]) for i in range(n_active)}
            for a in range(n_active):
                for b in adj[a]:
                    if b > a:
                        Q += 1.0 - (degrees[a] * degrees[b]) / (2 * m)
            Q /= m
            modularities.append(Q)

        # Contact lifetimes (track contact persistence)
        if prev_contacts is not None:
            # New contacts at this time
            for c in contacts:
                if c not in contact_first_seen:
                    contact_first_seen[c] = ti
            # Contacts that disappeared
            disappeared = prev_contacts - contacts
            for c in disappeared:
                if c in contact_first_seen:
                    lifetime = ti - contact_first_seen[c]
                    if lifetime > 0:
                        contact_lifetimes.append(lifetime)
                    del contact_first_seen[c]
        prev_contacts = contacts

        # Percolation threshold: can we find a spanning cluster?
        # A spanning cluster connects y < 5 to y > 25
        if k_edges > 5:
            # Compute forces and sort by magnitude
            force_mags = []
            for (i, j) in contacts:
                dx = xy[j, 0] - xy[i, 0]
                dy = xy[j, 1] - xy[i, 1]
                d = math.sqrt(dx*dx + dy*dy)
                overlap = max(0, rad[i] + rad[j] - d)
                fn = STIFFNESS * overlap
                force_mags.append((fn, i, j))
            force_mags.sort(key=lambda x: x[0], reverse=True)

            # Greedily add strongest contacts and check spanning
            dsu_parent = list(range(n_active))
            dsu_rank = [0] * n_active
            def dsu_find(x):
                while dsu_parent[x] != x:
                    dsu_parent[x] = dsu_parent[dsu_parent[x]]
                    x = dsu_parent[x]
                return x
            def dsu_union(a, b):
                ra, rb = dsu_find(a), dsu_find(b)
                if ra == rb:
                    return
                if dsu_rank[ra] < dsu_rank[rb]:
                    dsu_parent[ra] = rb
                elif dsu_rank[ra] > dsu_rank[rb]:
                    dsu_parent[rb] = ra
                else:
                    dsu_parent[rb] = ra
                    dsu_rank[ra] += 1

            # Check which grains cross top/bottom thresholds
            y_coords = xy[:, 1]
            top_grains = [i for i in range(n_active) if y_coords[i] > 25]
            bottom_grains = [i for i in range(n_active) if y_coords[i] < 5]

            threshold_found = False
            for frac in np.linspace(0.05, 1.0, 20):
                n_strong = max(1, int(frac * len(force_mags)))
                dsu_parent = list(range(n_active))
                dsu_rank = [0] * n_active
                for idx in range(n_strong):
                    _, i, j = force_mags[idx]
                    dsu_union(i, j)
                # Check spanning
                if top_grains and bottom_grains:
                    top_roots = set(dsu_find(g) for g in top_grains)
                    spanning = any(dsu_find(g) in top_roots for g in bottom_grains)
                    if spanning:
                        percolation_thresholds.append(frac)
                        threshold_found = True
                        break
            if not threshold_found:
                percolation_thresholds.append(1.0)

    descriptors = {}

    # Triadic motif profiles
    if motif_0:
        descriptors["motif_empty"] = float(np.mean(motif_0))
        descriptors["motif_single"] = float(np.mean(motif_1))
        descriptors["motif_path"] = float(np.mean(motif_2))
        descriptors["motif_triangle"] = float(np.mean(motif_3))
        descriptors["triangle_ratio"] = float(np.mean(motif_3) / max(np.mean(motif_2), 1e-10))
    else:
        for k in ["motif_empty", "motif_single", "motif_path", "motif_triangle", "triangle_ratio"]:
            descriptors[k] = np.nan

    # Modularity
    if modularities:
        descriptors["modularity_mean"] = float(np.mean(modularities))
        descriptors["modularity_std"] = float(np.std(modularities))
    else:
        descriptors["modularity_mean"] = np.nan
        descriptors["modularity_std"] = np.nan

    # Contact lifetimes
    if contact_lifetimes:
        descriptors["contact_lifetime_mean"] = float(np.mean(contact_lifetimes))
        descriptors["contact_lifetime_std"] = float(np.std(contact_lifetimes))
        descriptors["contact_lifetime_cv"] = float(np.std(contact_lifetimes) / max(np.mean(contact_lifetimes), 1e-10))
    else:
        for k in ["contact_lifetime_mean", "contact_lifetime_std", "contact_lifetime_cv"]:
            descriptors[k] = np.nan

    # Percolation threshold
    if percolation_thresholds:
        descriptors["percolation_threshold"] = float(np.mean(percolation_thresholds))
    else:
        descriptors["percolation_threshold"] = np.nan

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
    return float(np.mean((arr - mean) ** 3) / (std ** 3))


# ═══════════════════════════════════════════════════════════════════
# MAIN: RE-RUN ALL 60 SIMULATIONS WITH NEW DIAGNOSTICS
# ═══════════════════════════════════════════════════════════════════

print("\n" + "=" * 78)
print("  RD-018: TARGETED DIAGNOSTICS FOR RESIDUAL(C)")
print("=" * 78)
print("\n  Re-running 60 DEM simulations with 4 diagnostic families...\n")

t0 = time.time()
friction_levels = [0.05, 0.1, 0.2, 0.4, 0.6, 0.8]

# Collect all diagnostic names
all_A_names = [
    "force_mean", "force_std", "force_cv", "force_skew", "force_max", "force_median",
    "force_temporal_cv", "force_trend", "force_trend_p", "force_cv_temporal_cv",
    "fabric_anisotropy", "fabric_xx", "fabric_xy", "fabric_angle",
    "chain_mean_length", "chain_max_length", "chain_n_chains",
]
all_B_names = [
    "D2_min_mean", "D2_min_std", "D2_min_cv", "D2_min_skew",
    "D2_min_max", "D2_min_median",
    "rotation_mean", "rotation_std",
]
all_C_names = ["C_x_bin", "C_y_bin", "C_rad_bin", "C_rand_bin"]
all_D_names = [
    "motif_empty", "motif_single", "motif_path", "motif_triangle", "triangle_ratio",
    "modularity_mean", "modularity_std",
    "contact_lifetime_mean", "contact_lifetime_std", "contact_lifetime_cv",
    "percolation_threshold",
]
all_new_names = all_A_names + all_B_names + all_C_names + all_D_names

# Storage
new_matrix = np.full((N_RUNS, len(all_new_names)), np.nan)

for fi, friction in enumerate(friction_levels):
    for rep in range(10):
        seed = rep + 100 * fi
        idx = fi * 10 + rep

        y, x, vx, vy, radii, removed = _granular_run(
            n_grains=50, n_steps=1000, removal_step=500,
            removal_fraction=0.1, friction=friction, seed=seed,
        )

        # A: Force chain diagnostics
        desc_A = compute_force_diagnostics(x, y, radii, removed, T_pre=500)

        # B: Non-affine displacements
        desc_B = compute_non_affine_displacements(x, y, radii, removed, T_pre=500)

        # C: Alternate binning C
        desc_C = compute_C_alternate_binning(x, y, radii, removed, T_pre=500)

        # D: Contact network motifs
        desc_D = compute_network_motifs(x, y, radii, removed, T_pre=500)

        # Merge into new_matrix row
        for j, name in enumerate(all_new_names):
            val = np.nan
            if name in desc_A:
                val = desc_A[name]
            elif name in desc_B:
                val = desc_B[name]
            elif name in desc_C:
                val = desc_C[name]
            elif name in desc_D:
                val = desc_D[name]
            new_matrix[idx, j] = val

        if (rep + 1) % 5 == 0:
            elapsed = time.time() - t0
            print(f"  friction={friction:.2f}, rep={rep+1}/10  ({elapsed:.0f}s)")

print(f"\nAll 60 runs complete in {time.time() - t0:.0f}s\n")


# ═══════════════════════════════════════════════════════════════════
# ANALYSIS: CORRELATE EACH NEW DIAGNOSTIC WITH RESIDUAL(C)
# ═══════════════════════════════════════════════════════════════════

print("=" * 78)
print("  CORRELATION OF NEW DIAGNOSTICS WITH RESIDUAL(C)")
print("=" * 78)

corr_table = []
for j, name in enumerate(all_new_names):
    vals = new_matrix[:, j]
    valid = ~(np.isnan(residual_C) | np.isnan(vals))
    n_v = valid.sum()
    if n_v < 10:
        continue
    r_p, p_p = pearsonr(residual_C[valid], vals[valid])
    r_s, p_s = spearmanr(residual_C[valid], vals[valid])
    X_u = vals[valid].reshape(-1, 1)
    y_u = residual_C[valid]
    m_u = LinearRegression().fit(X_u, y_u)
    r2_u = r2_score(y_u, m_u.predict(X_u))

    corr_table.append({
        "name": name, "r": r_p, "p": p_p, "rho": r_s, "r2": r2_u, "n": n_v,
    })

corr_table.sort(key=lambda x: abs(x["r"]), reverse=True)

print(f"\n  {'Rank':>4s}  {'Variable':>30s}  {'Pearson r':>10s}  {'p-value':>10s}  {'Spearman ρ':>10s}  {'R²':>8s}  {'n':>4s}")
print(f"  {'-' * 82}")

for rank, row in enumerate(corr_table, 1):
    sig = " ***" if row["p"] < 0.001 else " **" if row["p"] < 0.01 else " *" if row["p"] < 0.05 else ""
    print(f"  {rank:>4d}  {row['name']:>30s}  {row['r']:>+10.4f}  {row['p']:>10.4e}{sig}  {row['rho']:>+10.4f}  {row['r2']:>8.4f}  {row['n']:>4d}")

top_hits = [r for r in corr_table if r["p"] < 0.05]
print(f"\n  Significant correlations (p < 0.05): {len(top_hits)} / {len(corr_table)}")
for r in top_hits:
    print(f"    {r['name']:>30s}: r={r['r']:+.4f}, p={r['p']:.4e}, R²={r['r2']:.4f}")


# ═══════════════════════════════════════════════════════════════════
# ANALYSIS BY FAMILY
# ═══════════════════════════════════════════════════════════════════

print("\n" + "=" * 78)
print("  BREAKDOWN BY DIAGNOSTIC FAMILY")
print("=" * 78)

families = [
    ("A: Force Chain", all_A_names),
    ("B: Non-Affine Disp.", all_B_names),
    ("C: Alt. Binning", all_C_names),
    ("D: Network Motifs", all_D_names),
]

for fname, fvars in families:
    hits = [r for r in corr_table if r["name"] in fvars and r["p"] < 0.05]
    best = [r for r in corr_table if r["name"] in fvars]
    best.sort(key=lambda x: abs(x["r"]), reverse=True)

    max_r = best[0]["r"] if best else 0
    max_p = best[0]["p"] if best else 1
    max_r2 = best[0]["r2"] if best else 0

    print(f"\n  {fname}:")
    print(f"    Significant: {len(hits)}/{len(fvars)}")
    print(f"    Best: {best[0]['name'] if best else 'N/A'} (r={max_r:+.4f}, p={max_p:.4e}, R²={max_r2:.4f})")

    # Within-family ranking
    for r in best[:5]:
        print(f"      {r['name']:>30s}: r={r['r']:+.4f}, p={r['p']:.4e}, R²={r['r2']:.4f}")


# ═══════════════════════════════════════════════════════════════════
# ANALYSIS: COMPARE C FROM DIFFERENT BINNING SCHEMES
# ═══════════════════════════════════════════════════════════════════

print("\n" + "=" * 78)
print("  C COMPARISON ACROSS BINNING SCHEMES")
print("=" * 78)

c_indices = {name: j for j, name in enumerate(all_new_names) if name in all_C_names}
if len(c_indices) >= 2:
    c_names = list(c_indices.keys())
    print(f"\n  {'Scheme':>15s}  {'vs x-bin r':>12s}  {'vs std. pre_C r':>16s}  {'Mean C':>10s}")
    print(f"  {'-' * 57}")

    for cname in c_names:
        cvals = new_matrix[:, c_indices[cname]]
        valid_c = ~np.isnan(cvals)
        if valid_c.sum() < 10:
            continue
        mean_c = np.nanmean(cvals)

        # Correlation with standard pre_C
        v_both = valid_c & ~np.isnan(pre_C)
        r_with_preC, _ = pearsonr(cvals[v_both], pre_C[v_both]) if v_both.sum() > 5 else (np.nan, 1)

        # Correlation with x-bin C
        if cname != "C_x_bin":
            x_idx = c_indices["C_x_bin"]
            xvals = new_matrix[:, x_idx]
            v_both = valid_c & ~np.isnan(xvals)
            r_with_x, _ = pearsonr(cvals[v_both], xvals[v_both]) if v_both.sum() > 5 else (np.nan, 1)
        else:
            r_with_x = 1.0

        print(f"  {cname:>15s}  {r_with_x:>+12.4f}  {r_with_preC:>+16.4f}  {mean_c:>10.4f}")

    # Residual(C) from each binning scheme
    print(f"\n  Residual(C)-like from each binning:")
    print(f"  {'Scheme':>15s}  {'r with std Res(C)':>18s}  {'R²(C~friction)':>16s}")
    print(f"  {'-' * 53}")

    for cname in c_names:
        cvals = new_matrix[:, c_indices[cname]]
        valid_c = ~(np.isnan(cvals) | np.isnan(friction_vals))
        if valid_c.sum() < 10:
            continue
        X = sm.add_constant(friction_vals[valid_c])
        m = sm.OLS(cvals[valid_c], X).fit()
        rc = np.full(N_RUNS, np.nan)
        rc[valid_c] = m.resid

        v_both = valid_c & ~np.isnan(residual_C)
        if v_both.sum() > 5:
            r_rc, _ = pearsonr(rc[v_both], residual_C[v_both])
        else:
            r_rc = np.nan

        print(f"  {cname:>15s}  {r_rc:>+18.4f}  {m.rsquared:>16.4f}")


# ═══════════════════════════════════════════════════════════════════
# ANALYSIS: WITHIN-LEVEL FORCE/NON-AFFINE PREDICTORS
# ═══════════════════════════════════════════════════════════════════

print("\n" + "=" * 78)
print("  WITHIN-LEVEL ANALYSIS: do new diagnostics predict recovery within friction?")
print("=" * 78)

# Find best predictors (excluding alt binning which is a C variant)
best_predictors = [r for r in corr_table if r["name"] not in all_C_names]
best_predictors.sort(key=lambda x: abs(x["r"]), reverse=True)

for target_name, target_vals, tlabel in [
    ("dip", dip, "ΔC"), ("restoration", restoration, "Restoration"),
]:
    print(f"\n  Target: {tlabel}")
    print(f"  {'Variable':>25s}  {'Within r':>10s}  {'Within p':>10s}  {'Pooled r':>10s}  {'Pooled p':>10s}  {'r|Res(C)':>8s}")
    print(f"  {'─' * 76}")

    for row in best_predictors[:6]:
        vals = new_matrix[:, all_new_names.index(row["name"])]
        within_rs = []
        within_ps = []
        for fl in friction_levels:
            mask = np.abs(friction_vals - fl) < 0.01
            d_vals = vals[mask]
            tvs = target_vals[mask]
            valid = ~(np.isnan(d_vals) | np.isnan(tvs))
            if valid.sum() >= 5:
                r_w, p_w = pearsonr(d_vals[valid], tvs[valid])
                within_rs.append(r_w)
                within_ps.append(p_w)

        if within_rs:
            mean_within = np.mean(within_rs)
            # Pooled (across all friction levels)
            valid_all = ~(np.isnan(vals) | np.isnan(target_vals))
            if valid_all.sum() >= 10:
                r_pool, p_pool = pearsonr(vals[valid_all], target_vals[valid_all])
            else:
                r_pool, p_pool = np.nan, 1

            # Partial correlation: diagnostic vs recovery controlling for Residual(C)
            valid_partial = ~(np.isnan(vals) | np.isnan(target_vals) | np.isnan(residual_C))
            if valid_partial.sum() >= 15:
                r_dt, _ = pearsonr(vals[valid_partial], target_vals[valid_partial])
                r_dr, _ = pearsonr(vals[valid_partial], residual_C[valid_partial])
                r_tr, _ = pearsonr(target_vals[valid_partial], residual_C[valid_partial])
                r_partial = (r_dt - r_dr * r_tr) / (math.sqrt(1 - r_dr**2) * math.sqrt(1 - r_tr**2) + 1e-10)
            else:
                r_partial = np.nan

            print(f"  {row['name']:>25s}  {mean_within:>+10.4f}  {np.mean(within_ps):>10.4e}  {r_pool:>+10.4f}  {p_pool:>10.4e}  {r_partial:>+8.4f}")


# ═══════════════════════════════════════════════════════════════════
# SAVE DIAGNOSTIC DATA
# ═══════════════════════════════════════════════════════════════════

output = []
for i in range(N_RUNS):
    record = {
        "friction": float(friction_vals[i]),
        "rep": raw_ensemble[i].get("rep", i),
        "residual_C": None if np.isnan(residual_C[i]) else float(residual_C[i]),
    }
    for j, name in enumerate(all_new_names):
        val = new_matrix[i, j]
        record[name] = None if (isinstance(val, float) and np.isnan(val)) else float(val)
    output.append(record)

with open("audits/rd018_diagnostics.json", "w") as f:
    json.dump(output, f, indent=2)
print(f"\nSaved diagnostics to audits/rd018_diagnostics.json")


# ═══════════════════════════════════════════════════════════════════
# KEY FINDINGS SUMMARY
# ═══════════════════════════════════════════════════════════════════

print("\n\n" + "=" * 78)
print("  RD-018 KEY FINDINGS")
print("=" * 78)

print(f"\n  D1 (Force Chain): Best correlate of Residual(C):")
force_hits = [r for r in corr_table if r["name"] in all_A_names]
force_hits.sort(key=lambda x: abs(x["r"]), reverse=True)
if force_hits:
    print(f"    {force_hits[0]['name']}: r={force_hits[0]['r']:+.4f}, R²={force_hits[0]['r2']:.4f}")

print(f"\n  D2 (Non-Affine): Best correlate of Residual(C):")
na_hits = [r for r in corr_table if r["name"] in all_B_names]
na_hits.sort(key=lambda x: abs(x["r"]), reverse=True)
if na_hits:
    print(f"    {na_hits[0]['name']}: r={na_hits[0]['r']:+.4f}, R²={na_hits[0]['r2']:.4f}")

print(f"\n  D3 (Alt Binning): Best correlate of Residual(C):")
bin_hits = [r for r in corr_table if r["name"] in all_C_names]
bin_hits.sort(key=lambda x: abs(x["r"]), reverse=True)
if bin_hits:
    print(f"    {bin_hits[0]['name']}: r={bin_hits[0]['r']:+.4f}, R²={bin_hits[0]['r2']:.4f}")

print(f"\n  D4 (Network Motifs): Best correlate of Residual(C):")
motif_hits = [r for r in corr_table if r["name"] in all_D_names]
motif_hits.sort(key=lambda x: abs(x["r"]), reverse=True)
if motif_hits:
    print(f"    {motif_hits[0]['name']}: r={motif_hits[0]['r']:+.4f}, R²={motif_hits[0]['r2']:.4f}")

# Overall best from new diagnostics
print(f"\n  Overall best new correlate: ", end="")
if corr_table:
    best = corr_table[0]
    print(f"{best['name']} (r={best['r']:+.4f}, R²={best['r2']:.4f})")

# Compare with RD-017's best (pre_MSE_s1, R²=0.176)
rd017_best_r2 = 0.176
if corr_table:
    new_best_r2 = corr_table[0]["r2"] if corr_table else 0
    print(f"\n  RD-017 best R²: {rd017_best_r2:.4f} (pre_MSE_s1)")
    print(f"  RD-018 best R²: {new_best_r2:.4f} ({corr_table[0]['name'] if corr_table else 'N/A'})")
    print(f"  Improvement: {new_best_r2 - rd017_best_r2:+.4f}")

print(f"\n  Total new diagnostics: {len(all_new_names)}")
print(f"  Significant (p<0.05): {len(top_hits)}")
print(f"  Time: {time.time() - t0:.0f}s")
