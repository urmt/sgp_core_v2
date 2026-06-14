#!/usr/bin/env python3
"""Generate all 6 figures for revised_chaos_paper.tex with exact names."""

import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy.cluster.hierarchy import linkage, fcluster
from sklearn.decomposition import PCA
from scipy.spatial.distance import pdist, squareform
from scipy.stats import pearsonr

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.05,
    "axes.linewidth": 0.6,
    "lines.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

ROOT = Path("/home/student/sgp_core_v2")
OUT = ROOT / "sfh_sgp_ood_outputs"
FIG = ROOT / "publication" / "chaos_template" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

G = {"black": "#000000", "dg": "#555555", "gray": "#888888", "lg": "#BBBBBB", "el": "#DDDDDD"}


def save(fig, name):
    for ext in ("pdf", "png"):
        if ext == "png":
            fig.savefig(FIG / f"{name}.{ext}", format="png", dpi=300)
        else:
            fig.savefig(FIG / f"{name}.{ext}", format="pdf")
    plt.close(fig)
    print(f"  Saved {name}.pdf + .png")


# --- FIG 1: Phi-space manifold ---
def fig1():
    Phi = np.load(OUT / "t030_ensemble_Phi.npy")
    flow_df = pd.read_csv(OUT / "t030_ensemble_flow.csv")
    flows = flow_df["flow_magnitude"].values

    fig = plt.figure(figsize=(7.0, 3.2))
    gs = GridSpec(1, 2, width_ratios=[1.3, 1], wspace=0.35)

    # Panel A: 3D scatter colored by flow
    ax1 = fig.add_subplot(gs[0], projection="3d")
    sc = ax1.scatter(Phi[:, 0], Phi[:, 1], Phi[:, 2],
                     c=flows, cmap="gray_r", s=14, alpha=0.85,
                     edgecolors="none", vmin=0, vmax=np.percentile(flows, 95))
    ax1.set_xlabel("$C$", fontsize=8, labelpad=4)
    ax1.set_ylabel("$F$", fontsize=8, labelpad=4)
    ax1.set_zlabel("$A$", fontsize=8, labelpad=4)
    ax1.set_title("\\textbf{(a)}", fontsize=10, loc="left", pad=-1)
    ax1.tick_params(labelsize=6)
    ax1.view_init(elev=20, azim=130)
    cb = fig.colorbar(sc, ax=ax1, shrink=0.55, pad=0.08)
    cb.set_label("Flow magnitude", fontsize=7)
    cb.ax.tick_params(labelsize=6)

    # Panel B: Flow histogram
    ax2 = fig.add_subplot(gs[1])
    ax2.hist(flows, bins=28, color=G["gray"], edgecolor="white", linewidth=0.3, alpha=0.85)
    med = np.median(flows)
    ax2.axvline(med, color=G["black"], ls="--", lw=0.8, label=f"Median = {med:.2f}")
    ax2.set_xlabel("Flow magnitude", fontsize=9)
    ax2.set_ylabel("Count", fontsize=9)
    ax2.set_title("\\textbf{(b)}", fontsize=10, loc="left")
    ax2.legend(frameon=False, fontsize=7)

    plt.tight_layout()
    save(fig, "fig1_phi_space")


# --- FIG 2: Flow topology / ridge structure ---
def fig2():
    Phi = np.load(OUT / "t030_ensemble_Phi.npy")
    flow_df = pd.read_csv(OUT / "t030_ensemble_flow.csv")
    flows = flow_df["flow_magnitude"].values

    pca = PCA(n_components=2)
    Phi2 = pca.fit_transform(Phi)

    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.0))

    # Panel A: Flow in PCA space
    ax = axes[0]
    sc = ax.scatter(Phi2[:, 0], Phi2[:, 1], c=flows, cmap="gray_r",
                    s=12, edgecolors="none", alpha=0.85,
                    vmin=0, vmax=np.percentile(flows, 95))
    plt.colorbar(sc, ax=ax, shrink=0.7, label="Flow")
    ax.set_xlabel("PC1", fontsize=9)
    ax.set_ylabel("PC2", fontsize=9)
    ax.set_title("\\textbf{(a)}", fontsize=10, loc="left")

    # Panel B: Ridge vs tail
    ax = axes[1]
    med = np.median(flows)
    ridge = flows > med
    tail = ~ridge
    ax.scatter(Phi2[ridge, 0], Phi2[ridge, 1], c=G["black"], s=14,
               marker="o", label=f"Ridge (flow > {med:.2f})",
               edgecolors="white", linewidths=0.3)
    ax.scatter(Phi2[tail, 0], Phi2[tail, 1], c=G["lg"], s=9,
               marker="s", label="Tail",
               edgecolors="white", linewidths=0.3)
    ax.set_xlabel("PC1", fontsize=9)
    ax.set_ylabel("PC2", fontsize=9)
    ax.set_title("\\textbf{(b)}", fontsize=10, loc="left")
    ax.legend(frameon=False, fontsize=7, loc="upper right")

    plt.tight_layout()
    save(fig, "fig2_topology")


# --- FIG 3: Null-model survival ---
def fig3():
    df = pd.read_csv(OUT / "t031_null_metrics.csv")
    real_pr = 1.9458

    fig, ax = plt.subplots(figsize=(3.5, 3.8))

    names = df["null_name"].values
    surv = df["survival_pr"].values
    ci_lo = df["pr_ci_lo"].values / real_pr
    ci_hi = df["pr_ci_hi"].values / real_pr

    y = np.arange(len(names))
    colors = [G["black"] if s < 0.8 else G["gray"] for s in surv]

    err_lo = np.abs(surv - ci_lo)
    err_hi = np.abs(ci_hi - surv)

    ax.barh(y, surv, xerr=[err_lo, err_hi],
            color=colors, edgecolor="white", linewidth=0.3,
            capsize=2, error_kw={"elinewidth": 0.5})
    ax.axvline(1.0, color=G["black"], ls="--", lw=0.6, label="Real PR baseline")
    ax.axvline(0.8, color=G["dg"], ls=":", lw=0.5, label="Collapse threshold (0.8)")
    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=7)
    ax.set_xlabel("Survival PR ratio", fontsize=9)
    ax.set_title("\\textbf{(a)}", fontsize=10, loc="left")
    ax.legend(frameon=False, fontsize=6, loc="lower right")
    ax.set_xlim(0.5, 1.8)

    plt.tight_layout()
    save(fig, "fig3_null_survival")


# --- FIG 4: Causal destruction ---
def fig4():
    # Manually from T031 output
    levels = ["Original", "Col shuffle", "Row shuffle", "Gauss copula", "Decorrelated", "White noise"]
    prs = [1.9458, 2.2811, 1.4235, 1.8143, 2.4103, 2.6066]
    knn = [0.9093, 0.7107, 0.8871, 0.8957, 0.9026, 0.8237]

    fig, ax = plt.subplots(figsize=(3.5, 3.0))

    x = np.arange(len(levels))
    ax.plot(x, prs, "o-", color=G["black"], markersize=6, lw=1.0, label="PR")
    ax.axhline(1.5, color=G["dg"], ls="--", lw=0.6, label="Collapse (PR=1.5)")

    # Highlight row-shuffle
    ax.plot(x[2], prs[2], "s", color=G["black"], markersize=9, zorder=5)
    ax.annotate("Row shuffle\n(PR=1.42)", xy=(x[2], prs[2]),
                xytext=(x[2] + 1.2, prs[2] + 0.35),
                fontsize=7, arrowprops=dict(arrowstyle="->", lw=0.6))

    # Annotate white-noise rebound
    ax.annotate("White noise\nrebound", xy=(x[5], prs[5]),
                xytext=(x[5] - 0.3, prs[5] + 0.25),
                fontsize=6, arrowprops=dict(arrowstyle="->", lw=0.5))

    ax.set_xlabel("Destruction level", fontsize=9)
    ax.set_ylabel("Participation ratio", fontsize=9)
    ax.set_title("\\textbf{(a)}", fontsize=10, loc="left")
    ax.legend(frameon=False, fontsize=7)
    ax.set_xticks(x)
    ax.set_xticklabels(levels, fontsize=6, rotation=30, ha="right")

    plt.tight_layout()
    save(fig, "fig4_causal_destruction")


# --- FIG 5: Embedding robustness ---
def fig5():
    df = pd.read_csv(OUT / "t031_embedding_stability.csv")

    fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.8))

    emb = df["embedding"].values
    tw = df["trustworthiness"].values
    knn = df["knn_flow_r"].values
    pr = df["pr"].values

    y = np.arange(len(emb))

    # Panel A: Trustworthiness
    ax = axes[0]
    ax.barh(y, tw, color=G["gray"], edgecolor="white", linewidth=0.3)
    ax.set_yticks(y)
    ax.set_yticklabels(emb, fontsize=6)
    ax.set_xlabel("Trustworthiness", fontsize=8)
    ax.set_title("\\textbf{(a)}", fontsize=10, loc="left")
    ax.axvline(0.6, color=G["dg"], ls="--", lw=0.5, label="Threshold")
    ax.legend(frameon=False, fontsize=6)

    # Panel B: kNN flow prediction
    ax = axes[1]
    ax.barh(y, knn, color=G["dg"], edgecolor="white", linewidth=0.3)
    ax.set_yticks(y)
    ax.set_yticklabels([])
    ax.set_xlabel("kNN flow $r$", fontsize=8)
    ax.set_title("\\textbf{(b)}", fontsize=10, loc="left")

    # Panel C: PR
    ax = axes[2]
    ax.barh(y, pr, color=G["lg"], edgecolor="white", linewidth=0.3)
    ax.set_yticks(y)
    ax.set_yticklabels([])
    ax.set_xlabel("PR", fontsize=8)
    ax.set_title("\\textbf{(c)}", fontsize=10, loc="left")

    plt.tight_layout()
    save(fig, "fig5_embedding_robustness")


# --- FIG 6: Decision framework ---
def fig6():
    criteria = ["G1: Stat null survival", "G2: Adversarial fail",
                "G3: Causal destruction", "G4: Info geometry",
                "G5: Representation", "G6: Spectral insuff.",
                "G7: Min collapse"]
    status = [0, 1, 1, 1, 1, 1, 1]  # 0=partial, 1=pass
    confidence = [0.55, 0.90, 0.85, 0.82, 0.79, 0.78, 0.85]

    fig, ax = plt.subplots(figsize=(3.5, 3.5))

    y = np.arange(len(criteria))
    colors = [G["black"] if s == 1 else G["lg"] for s in status]

    ax.barh(y, confidence, color=colors, edgecolor="white", linewidth=0.3)
    ax.set_yticks(y)
    ax.set_yticklabels(criteria, fontsize=7)
    ax.set_xlabel("Evidence confidence", fontsize=9)
    ax.axvline(0.5, color=G["dg"], ls="--", lw=0.5, label="Threshold (0.5)")
    ax.set_xlim(0, 1.05)

    for i, (s, c) in enumerate(zip(status, confidence)):
        label = "PASS" if s == 1 else "PARTIAL"
        ax.text(c + 0.02, i, label, va="center", fontsize=6,
                fontweight="bold",
                color=G["black"] if s == 1 else G["dg"])

    ax.set_title("\\textbf{(a)}", fontsize=10, loc="left")
    ax.legend(frameon=False, fontsize=6)

    plt.tight_layout()
    save(fig, "fig6_decision_framework")


if __name__ == "__main__":
    print("Generating 6 figures for revised_chaos_paper.tex ...")
    fig1()
    fig2()
    fig3()
    fig4()
    fig5()
    fig6()
    print("Done.")
