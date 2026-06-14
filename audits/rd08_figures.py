"""RD-8: Generate state-space cartography figures."""

import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.colors import LinearSegmentedColormap

OUT = "audits"
os.makedirs(OUT, exist_ok=True)

with open(f"{OUT}/rd08_friction_sweep.json") as f:
    data = json.load(f)

# Extract arrays
mu = np.array([r["friction"] for r in data])
C = np.array([r["C"] if r["C"] is not None else np.nan for r in data])
jitter = np.array([r["jitter"] for r in data])
persist = np.array([r["persistence"] if r["persistence"] is not None else np.nan for r in data])
reorg = np.array([r["reorg_rate"] if r["reorg_rate"] is not None else np.nan for r in data])
vauto = np.array([r["v_autocorr"] if r["v_autocorr"] is not None else np.nan for r in data])
sep = np.array([r["separation"] if r["separation"] is not None else np.nan for r in data])

# ─── Figure 1: State variables vs friction (regime-colored) ───
fig, axes = plt.subplots(3, 2, figsize=(12, 10))
fig.suptitle("RD-8: State Variables Across the Friction Landscape", fontsize=14, fontweight="bold")

# Regime colors
def regime_color(m):
    if m < 0.25: return "#2196F3"   # blue = emergent
    elif m < 1.0: return "#FF9800"  # orange = transitional
    else: return "#F44336"          # red = frozen

colors = [regime_color(m) for m in mu]

vars_list = [
    (C, "Coherence (C)", 0),
    (jitter, "Jitter (RMS velocity)", 1),
    (persist, "Persistence (autocorrelation τ)", 2),
    (reorg, "Reorganization rate", 3),
    (vauto, "Velocity autocorrelation", 4),
    (sep, "Mean grain separation", 5),
]

for vals, label, idx in vars_list:
    ax = axes[idx // 2, idx % 2]
    valid = ~np.isnan(vals)
    ax.scatter(mu[valid], vals[valid], c=[colors[i] for i in np.where(valid)[0]],
               s=30, alpha=0.7, edgecolors="white", linewidths=0.5)
    
    # Regime boundaries
    ax.axvline(0.25, color="gray", linestyle="--", alpha=0.4, lw=1)
    ax.axvline(1.0, color="gray", linestyle="--", alpha=0.4, lw=1)
    ax.set_xlabel("Friction (μ)")
    ax.set_ylabel(label)
    ax.set_title(label, fontsize=11)
    
    # Regime labels
    ax.text(0.12, ax.get_ylim()[1]*0.95, "EMERGENT", ha="center", fontsize=8,
            color="#1565C0", fontweight="bold", alpha=0.7)
    ax.text(0.60, ax.get_ylim()[1]*0.95, "TRANS.", ha="center", fontsize=8,
            color="#E65100", fontweight="bold", alpha=0.7)
    ax.text(1.50, ax.get_ylim()[1]*0.95, "FROZEN", ha="center", fontsize=8,
            color="#B71C1C", fontweight="bold", alpha=0.7)

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig(f"{OUT}/rd08_fig1_state_variables.png", dpi=150, bbox_inches="tight")
plt.close()
print("Fig 1: audits/rd08_fig1_state_variables.png")

# ─── Figure 2: PCA state-space map (PC1 vs PC2) ───
# Recompute PCA
keys = ["C", "jitter", "persistence", "reorg_rate", "v_autocorr", "separation"]
valid_mask = np.array([all(not np.isnan(r[k]) for k in keys) for r in data])
M = np.array([[r[k] for k in keys] for r in data if valid_mask[0]])
stds = np.std(M, axis=0); stds[stds == 0] = 1
M_std = (M - np.mean(M, axis=0)) / stds
cov = np.cov(M_std.T)
eigvals, eigvecs = np.linalg.eigh(cov)
eigvals = eigvals[::-1]; eigvecs = eigvecs[:, ::-1]
PC = M_std @ eigvecs[:, :2]
mu_v = mu[valid_mask]
colors_v = [regime_color(m) for m in mu_v]

fig, ax = plt.subplots(figsize=(10, 7))
scatter = ax.scatter(PC[:, 0], PC[:, 1], c=mu_v, cmap="RdYlBu_r", s=40, alpha=0.8,
                     edgecolors="white", linewidths=0.5)

# Arrow showing friction direction
mean_pc_low = np.mean(PC[mu_v < 0.2], axis=0)
mean_pc_high = np.mean(PC[mu_v > 1.5], axis=0)
ax.annotate("", xy=mean_pc_high, xytext=mean_pc_low,
            arrowprops=dict(arrowstyle="->", color="black", lw=2))
ax.text((mean_pc_low[0]+mean_pc_high[0])/2 + 0.2,
        (mean_pc_low[1]+mean_pc_high[1])/2,
        "increasing μ", fontsize=10, fontweight="bold", color="black")

# Regime labels
for label, region in [("EMERGENT", PC[mu_v < 0.25]),
                       ("TRANSITIONAL", PC[(mu_v >= 0.25) & (mu_v < 1.0)]),
                       ("FROZEN", PC[mu_v >= 1.0])]:
    if len(region) > 0:
        cx, cy = np.mean(region, axis=0)
        ax.text(cx, cy + 0.15, label, ha="center", fontsize=9, fontweight="bold",
                color="black", alpha=0.8,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.7))

cbar = plt.colorbar(scatter, ax=ax, label="Friction (μ)")
ax.set_xlabel(f"PC1 ({eigvals[1]/np.sum(eigvals)*100:.1f}% variance) — fluidity axis", fontsize=11)
ax.set_ylabel(f"PC2 ({eigvals[0]/np.sum(eigvals)*100:.1f}% variance) — jitter axis", fontsize=11)
ax.set_title("RD-8: State-Space Map (PCA Projection)", fontsize=13, fontweight="bold")
ax.axhline(0, color="gray", ls=":", alpha=0.3)
ax.axvline(0, color="gray", ls=":", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUT}/rd08_fig2_pca_map.png", dpi=150, bbox_inches="tight")
plt.close()
print("Fig 2: audits/rd08_fig2_pca_map.png")

# ─── Figure 3: PCA variance explained + loadings ───
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

explained = eigvals / np.sum(eigvals)
cumulative = np.cumsum(explained)
x = range(1, len(explained)+1)
ax1.bar(x, explained*100, color=["#1976D2", "#FF9800", "#4CAF50", "#9C27B0", "#F44336", "#607D8B"])
ax1.plot(x, cumulative*100, "ko-", markersize=6)
ax1.axhline(90, color="red", ls="--", alpha=0.5, label="90% threshold")
ax1.set_xlabel("Principal Component")
ax1.set_ylabel("Variance Explained (%)")
ax1.set_title("Scree Plot", fontsize=12)
ax1.set_xticks(x)
ax1.legend()

# Loadings
eigvecs_sorted = eigvecs[:, ::-1]
x_pos = np.arange(len(keys))
width = 0.35
ax2.bar(x_pos - width/2, eigvecs_sorted[:, 0], width, label="PC1", color="#1976D2", alpha=0.8)
ax2.bar(x_pos + width/2, eigvecs_sorted[:, 1], width, label="PC2", color="#FF9800", alpha=0.8)
ax2.set_xticks(x_pos)
ax2.set_xticklabels(keys, rotation=45, ha="right")
ax2.set_ylabel("Loading")
ax2.set_title("PCA Loadings", fontsize=12)
ax2.legend()
ax2.axhline(0, color="gray", ls=":", alpha=0.3)

plt.tight_layout()
plt.savefig(f"{OUT}/rd08_fig3_pca_detail.png", dpi=150, bbox_inches="tight")
plt.close()
print("Fig 3: audits/rd08_fig3_pca_detail.png")

# ─── Figure 4: Correlation heatmap ───
fig, ax = plt.subplots(figsize=(8, 7))
M2 = np.array([[r[k] for k in keys] for r in data])
valid_all = ~np.isnan(M2).any(axis=1)
M2 = M2[valid_all]
corr = np.corrcoef(M2.T)
im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
ax.set_xticks(range(len(keys))); ax.set_yticks(range(len(keys)))
ax.set_xticklabels(keys, rotation=45, ha="right")
ax.set_yticklabels(keys)
for i in range(len(keys)):
    for j in range(len(keys)):
        ax.text(j, i, f"{corr[i,j]:.2f}", ha="center", va="center", fontsize=10,
                color="white" if abs(corr[i,j]) > 0.6 else "black")
plt.colorbar(im, ax=ax, label="Pearson r")
ax.set_title("RD-8: Metric Correlation Matrix", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{OUT}/rd08_fig4_correlations.png", dpi=150, bbox_inches="tight")
plt.close()
print("Fig 4: audits/rd08_fig4_correlations.png")

print("\nAll figures saved.")
