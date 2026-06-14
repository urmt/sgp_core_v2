#!/usr/bin/env python3
"""
T028c: MANUSCRIPT VISUALIZATIONS
=================================
Generate publication-ready figures for the transition manifold paper.

Figure 1: Φ-space scatter (C,F,A,R pairs) with flow magnitude as color
Figure 2: Geodesic MST with bottlenecks highlighted (bridge vs non-bridge)
Figure 3: Perturbation trajectories through Φ-space
Figure 4: Stability tensor heatmap (system × feature for A and R axes)
Figure 5: Flow vs collapse prediction scatter
"""

import json, warnings, itertools
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import FancyArrowPatch
from scipy.spatial.distance import pdist, squareform, cdist
from scipy.stats import pearsonr
from sklearn.neighbors import NearestNeighbors
import networkx as nx

warnings.filterwarnings("ignore")
np.random.seed(42)

OUT = Path("sfh_sgp_ood_outputs")
FIG = Path("figures")
FIG.mkdir(exist_ok=True)

ALL_SYSTEMS = [
    "primes", "fibonacci", "modular_arithmetic", "additive_recurrence",
    "lorenz", "logistic_map", "henon_map", "ising_magnetization",
    "reaction_diffusion", "cfg_expansion", "lambda_reduction",
    "rewrite_system", "iid_gaussian", "colored_noise",
]

BRIDGE_SYSTEMS = {"lorenz", "ising_magnetization", "reaction_diffusion"}
AXES = ["C", "F", "A", "R"]
COLORS = plt.cm.RdYlBu_r

# Load data
coord = pd.read_csv(OUT / "emergence_coordinates.csv")
coord = coord[coord["system"].isin(ALL_SYSTEMS)].reset_index(drop=True)
Phi = coord[AXES].values

flow_df = pd.read_csv(OUT / "emergence_flow_field.csv")
flow_map = {r["system"]: r["flow_magnitude"] for _, r in flow_df.iterrows()}
flow_vals = np.array([flow_map[s] for s in ALL_SYSTEMS])

with open(OUT / "t028_transition_manifold_results.json") as f:
    t028 = json.load(f)

# Load tensor & trajectories
tensors = np.load(OUT / "t028_stability_tensor.npy")
trajectories = np.load(OUT / "t028_trajectories.npy")

with open(OUT / "r2_collapse_forecast.json") as f:
    coll = json.load(f)
collapse_vals = np.array([
    np.mean(coll["collapse_curves"][s][:6]) for s in ALL_SYSTEMS
])

bridge_mask = np.array([s in BRIDGE_SYSTEMS for s in ALL_SYSTEMS])
n = len(ALL_SYSTEMS)

FEATURE_NAMES = [
    "pc1", "pc2", "effective_rank", "tau_m1", "tau_m2", "tau_m3", "tau_m4",
    "temporal_corr", "phase_corr", "pc1_ratio", "replay_displacement",
    "abl_full_pc1", "abl_no_m1_pc1", "abl_no_m2_pc1", "abl_no_m3_pc1",
    "abl_no_m4_pc1", "m2_contribution",
]

# =====================================================================
# FIGURE 1: Φ-space scatter (C-F and A-R pairs)
# =====================================================================
def fig1_phi_space():
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    pairs = [("C", "F"), ("A", "R")]
    titles = ["Coherence–Fluctuation (C–F) plane", "Ablation–Replay (A–R) plane"]

    for ax_idx, (x_ax, y_ax) in enumerate(pairs):
        ax = axes[ax_idx]
        xi, yi = AXES.index(x_ax), AXES.index(y_ax)

        scatter = ax.scatter(Phi[:, xi], Phi[:, yi], c=flow_vals,
                             cmap=COLORS, s=120, edgecolors="k", linewidths=0.5,
                             vmin=flow_vals.min(), vmax=flow_vals.max())

        for i in range(n):
            label = ALL_SYSTEMS[i].replace("_", " ")
            offset = 3
            dx, dy = 0.02 * (Phi[:, xi].max() - Phi[:, xi].min()), 0.02 * (Phi[:, yi].max() - Phi[:, yi].min())
            ax.annotate(label, (Phi[i, xi], Phi[i, yi]),
                        textcoords="offset points", xytext=(5, 5),
                        fontsize=7, alpha=0.9)

        # Highlight bridge systems
        for i in np.where(bridge_mask)[0]:
            ax.scatter(Phi[i, xi], Phi[i, yi], s=180, facecolors="none",
                       edgecolors="red", linewidths=2, zorder=5)

        ax.set_xlabel(f"{x_ax} (coherence)", fontsize=12)
        ax.set_ylabel(f"{y_ax} (fluctuation)" if y_ax == "F" else
                       f"{y_ax} (ablation)" if y_ax == "A" else
                       f"{y_ax} (replay)", fontsize=12)
        ax.set_title(titles[ax_idx], fontsize=13)
        ax.axhline(0, color="gray", linestyle="--", alpha=0.3)
        ax.axvline(0, color="gray", linestyle="--", alpha=0.3)
        ax.grid(alpha=0.2)

    cbar = fig.colorbar(scatter, ax=axes, orientation="horizontal",
                        pad=0.05, aspect=40)
    cbar.set_label("Flow magnitude (transition rate)", fontsize=11)

    plt.tight_layout()
    fig.savefig(FIG / "fig1_phi_space.png", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  Saved {FIG / 'fig1_phi_space.png'}")

# =====================================================================
# FIGURE 2: Geodesic MST with bottlenecks
# =====================================================================
def fig2_geodesic_mst():
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))

    dist_mat = squareform(pdist(Phi))

    G = nx.Graph()
    for i in range(n):
        G.add_node(i, system=ALL_SYSTEMS[i], flow=flow_vals[i])
    for d, i, j in sorted([(dist_mat[i, j], i, j) for i in range(n) for j in range(i+1, n)]):
        G.add_edge(i, j, weight=d)

    mst = nx.minimum_spanning_tree(G, weight="weight")
    pos = {i: Phi[i, :2] for i in range(n)}

    # Draw MST edges colored by weight
    mst_edges = list(mst.edges(data=True))
    max_w = max(e[2]["weight"] for e in mst_edges)
    for i, j, attr in mst_edges:
        w = attr["weight"]
        color = plt.cm.Reds(w / max_w)
        ax.plot([pos[i][0], pos[j][0]], [pos[i][1], pos[j][1]],
                color=color, linewidth=1 + 3 * w / max_w, alpha=0.7, zorder=1)

    # Node scatter with flow coloring
    sizes = 100 + 200 * (flow_vals - flow_vals.min()) / (flow_vals.max() - flow_vals.min() + 1e-10)
    ax.scatter(Phi[:, 0], Phi[:, 1], c=flow_vals, cmap=COLORS,
               s=sizes, edgecolors="k", linewidths=0.8, zorder=3)

    # Highlight bridge nodes
    for i in np.where(bridge_mask)[0]:
        ax.scatter(Phi[i, 0], Phi[i, 1], s=sizes[i] + 50, facecolors="none",
                   edgecolors="red", linewidths=2.5, zorder=4)

    # Labels
    for i in range(n):
        label = ALL_SYSTEMS[i].replace("_", " ")
        ax.annotate(label, (Phi[i, 0], Phi[i, 1]),
                    textcoords="offset points", xytext=(4, 4),
                    fontsize=7, alpha=0.9, zorder=5)

    # Mark bottleneck edges
    sorted_edges = sorted(mst_edges, key=lambda e: e[2]["weight"], reverse=True)
    for (i, j, attr) in sorted_edges[:3]:
        mid = ((pos[i][0] + pos[j][0]) / 2, (pos[i][1] + pos[j][1]) / 2)
        ax.annotate(f"d={attr['weight']:.2f}", mid,
                    textcoords="offset points", xytext=(0, -12),
                    fontsize=8, color="darkred", ha="center",
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                              edgecolor="red", alpha=0.7))

    ax.set_xlabel("C (coherence)", fontsize=12)
    ax.set_ylabel("F (fluctuation)", fontsize=12)
    ax.set_title("Geodesic MST: transition bottlenecks", fontsize=14)
    ax.grid(alpha=0.2)

    cbar = fig.colorbar(plt.cm.ScalarMappable(norm=mcolors.Normalize(
                        vmin=flow_vals.min(), vmax=flow_vals.max()), cmap=COLORS),
                        ax=ax, shrink=0.8)
    cbar.set_label("Flow magnitude", fontsize=11)

    plt.tight_layout()
    fig.savefig(FIG / "fig2_geodesic_mst.png", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  Saved {FIG / 'fig2_geodesic_mst.png'}")

# =====================================================================
# FIGURE 3: Perturbation trajectories
# =====================================================================
def fig3_trajectories():
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Show trajectories in C-F plane
    ax = axes[0]
    for i in range(n):
        traj = trajectories[i]
        alpha = 0.4 + 0.6 * (flow_vals[i] - flow_vals.min()) / (flow_vals.max() - flow_vals.min() + 1e-10)
        ax.plot(traj[:, 0], traj[:, 1], "-", alpha=alpha, linewidth=0.8)
        ax.scatter(traj[0, 0], traj[0, 1], c="k", s=15, zorder=3)
        ax.scatter(traj[-1, 0], traj[-1, 1], c="red" if ALL_SYSTEMS[i] in BRIDGE_SYSTEMS else "gray",
                   s=12, zorder=3)

    for i in np.where(bridge_mask)[0]:
        traj = trajectories[i]
        ax.plot(traj[:, 0], traj[:, 1], "-", color="red", linewidth=1.5, alpha=0.8)
        ax.scatter(traj[0, 0], traj[0, 1], color="red", s=30, marker="o", zorder=4, label="Bridge start" if i == np.where(bridge_mask)[0][0] else "")
        ax.scatter(traj[-1, 0], traj[-1, 1], color="darkred", s=30, marker="s", zorder=4, label="Bridge end" if i == np.where(bridge_mask)[0][0] else "")

    ax.set_xlabel("C", fontsize=12)
    ax.set_ylabel("F", fontsize=12)
    ax.set_title("Φ-space trajectories under perturbation (C–F)", fontsize=13)
    ax.grid(alpha=0.2)

    # Show trajectories in A-R plane
    ax = axes[1]
    for i in range(n):
        traj = trajectories[i]
        alpha = 0.4 + 0.6 * (flow_vals[i] - flow_vals.min()) / (flow_vals.max() - flow_vals.min() + 1e-10)
        ax.plot(traj[:, 2], traj[:, 3], "-", alpha=alpha, linewidth=0.8)
        ax.scatter(traj[0, 2], traj[0, 3], c="k", s=15, zorder=3)

    for i in np.where(bridge_mask)[0]:
        traj = trajectories[i]
        ax.plot(traj[:, 2], traj[:, 3], "-", color="red", linewidth=1.5, alpha=0.8)
        ax.scatter(traj[0, 2], traj[0, 3], color="red", s=30, marker="o", zorder=4)
        ax.scatter(traj[-1, 2], traj[-1, 3], color="darkred", s=30, marker="s", zorder=4)

    ax.set_xlabel("A", fontsize=12)
    ax.set_ylabel("R", fontsize=12)
    ax.set_title("Φ-space trajectories under perturbation (A–R)", fontsize=13)
    ax.grid(alpha=0.2)

    plt.tight_layout()
    fig.savefig(FIG / "fig3_trajectories.png", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  Saved {FIG / 'fig3_trajectories.png'}")

# =====================================================================
# FIGURE 4: Stability tensor heatmap (A and R axes only)
# =====================================================================
def fig4_stability_heatmap():
    fig, axes = plt.subplots(2, 1, figsize=(16, 10))

    for row, ax_name in enumerate(["A", "R"]):
        ax = axes[row]
        ax_idx = AXES.index(ax_name)

        # Sort systems by flow
        order = np.argsort(flow_vals)
        sens_data = np.abs(tensors[order, ax_idx, :])

        im = ax.imshow(sens_data, aspect="auto", cmap="YlOrRd",
                       interpolation="nearest")

        ax.set_yticks(range(n))
        ax.set_yticklabels([ALL_SYSTEMS[i] for i in order], fontsize=8)
        ax.set_xticks(range(17))
        ax.set_xticklabels(FEATURE_NAMES, rotation=45, ha="right", fontsize=7)
        ax.set_title(f"|∂{ax_name}/∂ε| — system × feature sensitivity", fontsize=13)

        # Mark bridge systems
        bridge_order_positions = [pos for pos, i in enumerate(order) if ALL_SYSTEMS[i] in BRIDGE_SYSTEMS]
        for bp in bridge_order_positions:
            ax.axhline(y=bp - 0.5, color="red", linewidth=2, alpha=0.5)

        cbar = fig.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label("|∂Φ/∂ε|", fontsize=10)

    plt.tight_layout()
    fig.savefig(FIG / "fig4_stability_heatmap.png", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  Saved {FIG / 'fig4_stability_heatmap.png'}")

# =====================================================================
# FIGURE 5: Flow vs collapse prediction
# =====================================================================
def fig5_flow_collapse():
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))

    r, p = pearsonr(flow_vals, collapse_vals)
    ax.scatter(flow_vals, collapse_vals, c=flow_vals, cmap=COLORS,
               s=100, edgecolors="k", linewidths=0.5, zorder=3)

    # Highlight bridge
    for i in np.where(bridge_mask)[0]:
        ax.scatter(flow_vals[i], collapse_vals[i], s=160, facecolors="none",
                   edgecolors="red", linewidths=2, zorder=4)

    # Labels
    for i in range(n):
        label = ALL_SYSTEMS[i].replace("_", " ")
        ax.annotate(label, (flow_vals[i], collapse_vals[i]),
                    textcoords="offset points", xytext=(5, 5), fontsize=8, alpha=0.9)

    # Regression line
    m, b = np.polyfit(flow_vals, collapse_vals, 1)
    x_line = np.linspace(flow_vals.min() - 0.5, flow_vals.max() + 0.5, 100)
    ax.plot(x_line, m * x_line + b, "--", color="gray", alpha=0.6, linewidth=1)

    ax.set_xlabel("Flow magnitude", fontsize=13)
    ax.set_ylabel("Mean collapse value", fontsize=13)
    ax.set_title(f"Flow → Collapse prediction (r={r:.3f}, p={p:.5f})", fontsize=14)
    ax.grid(alpha=0.2)

    plt.tight_layout()
    fig.savefig(FIG / "fig5_flow_collapse.png", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  Saved {FIG / 'fig5_flow_collapse.png'}")

# =====================================================================
# FIGURE 6: Bridge system comparison radar
# =====================================================================
def fig6_bridge_radar():
    fig, ax = plt.subplots(1, 1, figsize=(8, 8), subplot_kw=dict(polar=True))

    categories = ["Flow", "Curvature", "Density", "C", "F", "A", "R"]
    N = len(categories)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    # Get data
    with open(OUT / "emergence_energy_landscape.json") as f:
        landscape = json.load(f)
    curv_map = {s: landscape["curvature_per_system"][s]["mean_curvature"]
                for s in ALL_SYSTEMS}
    dens_map = {s: landscape["density_per_system"].get(s, 0) for s in ALL_SYSTEMS}

    bridge_systems = list(BRIDGE_SYSTEMS)
    non_bridge = [s for s in ALL_SYSTEMS if s not in BRIDGE_SYSTEMS]

    colors = ["red", "darkred", "coral"]
    for idx, sys_name in enumerate(bridge_systems):
        i = ALL_SYSTEMS.index(sys_name)
        values = [
            flow_vals[i], curv_map[sys_name], dens_map[sys_name],
            Phi[i, 0], Phi[i, 1], Phi[i, 2], Phi[i, 3],
        ]
        values_norm = (np.array(values) - np.mean(values)) / (np.std(values) + 1e-10)
        values_norm = np.concatenate([values_norm, values_norm[:1]])
        ax.plot(angles, values_norm, "o-", linewidth=2, label=sys_name, color=colors[idx])
        ax.fill(angles, values_norm, alpha=0.1, color=colors[idx])

    # Non-bridge mean
    n_values = []
    for cat_idx, cat in enumerate(categories):
        vals = []
        for s in non_bridge:
            i = ALL_SYSTEMS.index(s)
            if cat == "Flow":
                vals.append(flow_vals[i])
            elif cat == "Curvature":
                vals.append(curv_map[s])
            elif cat == "Density":
                vals.append(dens_map[s])
            elif cat in AXES:
                vals.append(Phi[i, AXES.index(cat)])
        n_values.append(np.mean(vals))
    n_values = (np.array(n_values) - np.mean(n_values)) / (np.std(n_values) + 1e-10)
    n_values = np.concatenate([n_values, n_values[:1]])
    ax.plot(angles, n_values, "s--", linewidth=1.5, label="Non-bridge (mean)", color="gray", alpha=0.6)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=11)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    ax.set_title("Bridge system profile across metrics", fontsize=14, pad=20)

    plt.tight_layout()
    fig.savefig(FIG / "fig6_bridge_radar.png", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  Saved {FIG / 'fig6_bridge_radar.png'}")

# =====================================================================
# MAIN
# =====================================================================
def main():
    print("=" * 70)
    print("T028c: MANUSCRIPT VISUALIZATIONS")
    print("=" * 70)

    print("\n  Figure 1: Φ-space scatter")
    fig1_phi_space()

    print("\n  Figure 2: Geodesic MST")
    fig2_geodesic_mst()

    print("\n  Figure 3: Perturbation trajectories")
    fig3_trajectories()

    print("\n  Figure 4: Stability tensor heatmap")
    fig4_stability_heatmap()

    print("\n  Figure 5: Flow vs collapse")
    fig5_flow_collapse()

    print("\n  Figure 6: Bridge radar plot")
    fig6_bridge_radar()

    print(f"\n{'=' * 70}")
    print(f"All figures saved to {FIG}/")
    print(f"{'=' * 70}")

if __name__ == "__main__":
    main()
