"""RD-8A: Figures for Latent Geometry Recon."""

import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

OUT = "audits"

# Load data
M = np.load(f"{OUT}/rd8a_matrix_t901.npy")
with open(f"{OUT}/rd8a_metric_names_t901.json") as f:
    metric_names = json.load(f)
with open(f"{OUT}/rd8a_row_metadata.json") as f:
    metadata = json.load(f)

# Standardize
M_std = (M - np.mean(M, axis=0)) / np.std(M, axis=0)
frictions = np.array([m["friction"] for m in metadata])

# PCA
cov = np.cov(M_std.T)
eigvals, eigvecs = np.linalg.eigh(cov)
eigvals = eigvals[::-1]; eigvecs = eigvecs[:, ::-1]
explained = eigvals / np.sum(eigvals)
cumulative = np.cumsum(explained)
PC = M_std @ eigvecs[:, :2]

# ─── Figure 1: Scree plot with participation ratio ───
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

colors = ["#1976D2" if i < 3 else "#FF9800" if i < 6 else "#9C27B0" for i in range(len(eigvals))]
ax1.bar(range(1, len(eigvals)+1), explained*100, color=colors, alpha=0.8, edgecolor="white")
ax1.plot(range(1, len(eigvals)+1), cumulative*100, "ko-", markersize=6)
ax1.axhline(90, color="red", ls="--", alpha=0.5, label="90%")
ax1.axhline(80, color="orange", ls="--", alpha=0.5, label="80%")
ax1.set_xlabel("Principal Component", fontsize=11)
ax1.set_ylabel("Variance Explained (%)", fontsize=11)
ax1.set_title("Scree Plot — PCA", fontsize=12, fontweight="bold")
ax1.set_xticks(range(1, len(eigvals)+1))
ax1.legend(fontsize=9)

# Eigenvalue spectrum
ax2.semilogy(range(1, len(eigvals)+1), eigvals, "ko-", markersize=8, linewidth=2)
ax2.axhline(1.0, color="red", ls="--", alpha=0.5, label="Kaiser criterion (λ=1)")
ax2.set_xlabel("Principal Component", fontsize=11)
ax2.set_ylabel("Eigenvalue (log scale)", fontsize=11)
ax2.set_title("Eigenvalue Spectrum", fontsize=12, fontweight="bold")
ax2.set_xticks(range(1, len(eigvals)+1))
ax2.legend(fontsize=9)

plt.tight_layout()
plt.savefig(f"{OUT}/rd8a_fig1_scree.png", dpi=150, bbox_inches="tight")
plt.close()
print("Fig 1: audits/rd8a_fig1_scree.png")

# ─── Figure 2: PCA loading heatmap ───
fig, ax = plt.subplots(figsize=(10, 7))
n_show = min(8, len(metric_names))
loadings = eigvecs[:, :n_show]
im = ax.imshow(loadings.T, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
ax.set_xticks(range(len(metric_names)))
ax.set_xticklabels(metric_names, rotation=45, ha="right", fontsize=9)
ax.set_yticks(range(n_show))
ax.set_yticklabels([f"PC{i+1} ({explained[i]*100:.1f}%)" for i in range(n_show)])
for i in range(len(metric_names)):
    for j in range(n_show):
        ax.text(i, j, f"{loadings[i,j]:.2f}", ha="center", va="center", fontsize=8,
                color="white" if abs(loadings[i,j]) > 0.5 else "black")
plt.colorbar(im, ax=ax, label="Loading")
ax.set_title("RD-8A: PCA Loading Heatmap", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{OUT}/rd8a_fig2_loadings.png", dpi=150, bbox_inches="tight")
plt.close()
print("Fig 2: audits/rd8a_fig2_loadings.png")

# ─── Figure 3: Factor Analysis loadings ───
from sklearn.decomposition import FactorAnalysis
fa = FactorAnalysis(n_components=3, random_state=42, max_iter=1000)
fa.fit(M_std)

fig, ax = plt.subplots(figsize=(10, 7))
fa_loadings = fa.components_.T
n_metrics = len(metric_names)
x = np.arange(n_metrics)
w = 0.25
ax.bar(x - w, fa_loadings[:, 0], w, label="F1: Fluidity/Activity", color="#1976D2", alpha=0.8)
ax.bar(x, fa_loadings[:, 1], w, label="F2: Perturbation Response", color="#FF9800", alpha=0.8)
ax.bar(x + w, fa_loadings[:, 2], w, label="F3: Recovery Dynamics", color="#4CAF50", alpha=0.8)
ax.set_xticks(x)
ax.set_xticklabels(metric_names, rotation=45, ha="right", fontsize=9)
ax.set_ylabel("Factor Loading", fontsize=11)
ax.set_title("RD-8A: Factor Analysis — 3 Latent Factors (BIC=1676)", fontsize=13, fontweight="bold")
ax.legend(fontsize=10)
ax.axhline(0, color="gray", ls=":", alpha=0.3)
ax.axhline(0.5, color="gray", ls="--", alpha=0.3)
ax.axhline(-0.5, color="gray", ls="--", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUT}/rd8a_fig3_factors.png", dpi=150, bbox_inches="tight")
plt.close()
print("Fig 3: audits/rd8a_fig3_factors.png")

# ─── Figure 4: PCA state-space map (PC1 vs PC2, colored by friction) ───
fig, ax = plt.subplots(figsize=(10, 7))
sc = ax.scatter(PC[:, 0], PC[:, 1], c=frictions, cmap="RdYlBu_r", s=60, alpha=0.8,
                edgecolors="white", linewidths=0.5)

# Regime boundaries
mean_low = np.mean(PC[frictions < 0.2], axis=0)
mean_high = np.mean(PC[frictions > 0.5], axis=0)
ax.annotate("", xy=mean_high, xytext=mean_low,
            arrowprops=dict(arrowstyle="->", color="black", lw=2.5))
ax.text((mean_low[0]+mean_high[0])/2 + 0.15, (mean_low[1]+mean_high[1])/2,
        "increasing μ", fontsize=11, fontweight="bold")

# Label cluster centers
for label, fr_range, color in [
    ("EMERGENT\n(μ<0.2)", frictions < 0.2, "#1565C0"),
    ("TRANS.\n(μ=0.2-0.5)", (frictions >= 0.2) & (frictions <= 0.5), "#E65100"),
    ("FROZEN\n(μ>0.5)", frictions > 0.5, "#B71C1C"),
]:
    mask = fr_range
    if np.sum(mask) > 0:
        cx, cy = np.mean(PC[mask], axis=0)
        ax.text(cx, cy + 0.12, label, ha="center", fontsize=9, fontweight="bold",
                color=color, bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8))

cbar = plt.colorbar(sc, ax=ax, label="Friction (μ)")
ax.set_xlabel(f"PC1 ({explained[0]*100:.1f}% variance) — Fluidity Axis", fontsize=12)
ax.set_ylabel(f"PC2 ({explained[1]*100:.1f}% variance) — Perturbation Response", fontsize=12)
ax.set_title("RD-8A: State-Space Map (PCA Projection)", fontsize=13, fontweight="bold")
ax.axhline(0, color="gray", ls=":", alpha=0.2)
ax.axvline(0, color="gray", ls=":", alpha=0.2)
plt.tight_layout()
plt.savefig(f"{OUT}/rd8a_fig4_pca_map.png", dpi=150, bbox_inches="tight")
plt.close()
print("Fig 4: audits/rd8a_fig4_pca_map.png")

# ─── Figure 5: Correlation matrix ───
fig, ax = plt.subplots(figsize=(10, 9))
corr = np.corrcoef(M_std.T)
im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
ax.set_xticks(range(len(metric_names)))
ax.set_yticks(range(len(metric_names)))
ax.set_xticklabels(metric_names, rotation=45, ha="right", fontsize=9)
ax.set_yticklabels(metric_names, fontsize=9)
for i in range(len(metric_names)):
    for j in range(len(metric_names)):
        ax.text(j, i, f"{corr[i,j]:.2f}", ha="center", va="center", fontsize=8,
                color="white" if abs(corr[i,j]) > 0.5 else "black")
plt.colorbar(im, ax=ax, label="Pearson r")
ax.set_title("RD-8A: Metric Correlation Matrix", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{OUT}/rd8a_fig5_correlations.png", dpi=150, bbox_inches="tight")
plt.close()
print("Fig 5: audits/rd8a_fig5_correlations.png")

# ─── Figure 6: Intrinsic dimensionality (participation ratio by # components) ───
fig, ax = plt.subplots(figsize=(8, 5))
# Compute participation ratio for first k components
pr_values = []
for k in range(1, len(eigvals)+1):
    h = np.sum(eigvals[:k]**2) / (np.sum(eigvals[:k]))**2
    pr_values.append(1.0 / h)
ax.plot(range(1, len(eigvals)+1), pr_values, "ko-", markersize=8, linewidth=2)
ax.axhline(5.39, color="blue", ls="--", alpha=0.5, label="MLE ID = 5.39")
ax.axhline(4.39, color="red", ls="--", alpha=0.5, label="PR = 4.39")
ax.set_xlabel("Number of PCA Components", fontsize=11)
ax.set_ylabel("Participation Ratio", fontsize=11)
ax.set_title("Intrinsic Dimensionality Estimates", fontsize=12, fontweight="bold")
ax.legend(fontsize=10)
ax.set_xticks(range(1, len(eigvals)+1))
plt.tight_layout()
plt.savefig(f"{OUT}/rd8a_fig6_intrinsic_dim.png", dpi=150, bbox_inches="tight")
plt.close()
print("Fig 6: audits/rd8a_fig6_intrinsic_dim.png")

print("\nAll figures saved.")
