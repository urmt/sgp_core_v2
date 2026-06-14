"""RD-7: Generate figures for variance decomposition."""

import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from scipy import stats

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

with open("audits/rd07_variance_decomposition.json") as f:
    data = json.load(f)

metrics = data["metrics"]
targets = data["targets"]

# ─── Figure 1: Correlation heatmap (t901) ───
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# t901 correlation matrix
corr = np.array(data["correlations_t901"])
ax = axes[0]
im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1, aspect="equal")
ax.set_xticks(range(4))
ax.set_yticks(range(4))
ax.set_xticklabels(metrics, fontsize=11, rotation=45, ha="right")
ax.set_yticklabels(metrics, fontsize=11)
for i in range(4):
    for j in range(4):
        color = "white" if abs(corr[i, j]) > 0.5 else "black"
        ax.text(j, i, f"{corr[i,j]:.2f}", ha="center", va="center", fontsize=12, color=color, fontweight="bold")
ax.set_title("t901 Ensemble (n=60)\nWithin-system correlations", fontsize=12, fontweight="bold")
plt.colorbar(im, ax=ax, shrink=0.8, label="Pearson r")

# Benchmark correlation matrix
corr_b = np.array(data["correlations_bench"])
ax = axes[1]
im = ax.imshow(corr_b, cmap="RdBu_r", vmin=-1, vmax=1, aspect="equal")
ax.set_xticks(range(4))
ax.set_yticks(range(4))
ax.set_xticklabels(metrics, fontsize=11, rotation=45, ha="right")
ax.set_yticklabels(metrics, fontsize=11)
for i in range(4):
    for j in range(4):
        color = "white" if abs(corr_b[i, j]) > 0.5 else "black"
        ax.text(j, i, f"{corr_b[i,j]:.2f}", ha="center", va="center", fontsize=12, color=color, fontweight="bold")
ax.set_title("Benchmark Systems (n=8)\nCross-system correlations", fontsize=12, fontweight="bold")
plt.colorbar(im, ax=ax, shrink=0.8, label="Pearson r")

fig.suptitle("RD-7: Cross-Metric Correlation Matrices", fontsize=14, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("audits/rd07_fig1_correlations.png", dpi=150, bbox_inches="tight")
print("Saved: audits/rd07_fig1_correlations.png")

# ─── Figure 2: Variance partition diagram (Venn-style bar chart) ───
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

colors_unique = ["#2196F3", "#4CAF50", "#FF9800", "#E91E63"]  # C, I_pred, C_σ, MSE
color_shared = "#9E9E9E"
color_unexplained = "#E0E0E0"

for ti, t in enumerate(["dip", "restoration", "tau_rec"]):
    ax = axes[ti]
    key = f"partial_r2_{t}"
    r2_full = data[key]["r2_full"]
    unique = data[key]["unique"]
    shared = data[key]["shared"]
    unexplained = data[key]["unexplained"]

    # Stacked bar
    bottom = 0
    vals = [unique[m] for m in metrics]
    for i, (v, m) in enumerate(zip(vals, metrics)):
        ax.bar(0, v, bottom=bottom, color=colors_unique[i], width=0.6, label=f"{m} unique ({v*100:.1f}%)")
        if v > 0.01:
            ax.text(0.35, bottom + v/2, f"{v*100:.1f}%", ha="left", va="center", fontsize=9, fontweight="bold")
        bottom += v

    ax.bar(0, shared, bottom=bottom, color=color_shared, width=0.6, label=f"Shared ({shared*100:.1f}%)")
    if shared > 0.01:
        ax.text(0.35, bottom + shared/2, f"{shared*100:.1f}%", ha="left", va="center", fontsize=9)
    bottom += shared

    ax.bar(0, unexplained, bottom=bottom, color=color_unexplained, width=0.6, label=f"Unexplained ({unexplained*100:.1f}%)")
    ax.text(0.35, bottom + unexplained/2, f"{unexplained*100:.1f}%", ha="left", va="center", fontsize=9)

    ax.set_ylim(0, 1.05)
    ax.set_xticks([])
    ax.set_ylabel("Variance fraction", fontsize=11)
    ax.set_title(f"Target: {targets[ti]}\nTotal R² = {r2_full:.3f}", fontsize=12, fontweight="bold")
    ax.legend(fontsize=8, loc="upper right", bbox_to_anchor=(1.6, 1.0))
    ax.grid(True, alpha=0.3, axis="y")

fig.suptitle("RD-7: Variance Decomposition — Unique vs Shared vs Unexplained", fontsize=14, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("audits/rd07_fig2_variance_partition.png", dpi=150, bbox_inches="tight")
print("Saved: audits/rd07_fig2_variance_partition.png")

# ─── Figure 3: Partial R² by metric (grouped bar chart) ───
fig, ax = plt.subplots(1, 1, figsize=(10, 6))

x = np.arange(len(targets))
width = 0.18
multiplier = 0

for i, m in enumerate(metrics):
    vals = [data[f"partial_r2_{t}"]["unique"][m] for t in ["dip", "restoration", "tau_rec"]]
    offset = width * multiplier
    bars = ax.bar(x + offset, vals, width, label=m, color=colors_unique[i], edgecolor="white", linewidth=0.5)
    for bar, v in zip(bars, vals):
        if v > 0.005:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                    f"{v:.3f}", ha="center", va="bottom", fontsize=8, fontweight="bold")
    multiplier += 1

ax.set_ylabel("Unique R² (partial)", fontsize=12)
ax.set_title("RD-7: Unique Variance Explained by Each Metric", fontsize=13, fontweight="bold")
ax.set_xticks(x + width * 1.5)
ax.set_xticklabels(targets, fontsize=11)
ax.legend(fontsize=10, loc="upper right")
ax.grid(True, alpha=0.3, axis="y")
ax.set_ylim(0, 0.12)

plt.tight_layout()
plt.savefig("audits/rd07_fig3_partial_r2.png", dpi=150, bbox_inches="tight")
print("Saved: audits/rd07_fig3_partial_r2.png")

# ─── Figure 4: C novelty gauge ───
fig, axes = plt.subplots(1, 3, figsize=(14, 4))

for ti, t in enumerate(["dip", "restoration", "tau_rec"]):
    ax = axes[ti]
    key = f"partial_r2_{t}"
    r2_full = data[key]["r2_full"]
    c_unique = data[key]["unique"]["C"]
    novelty = c_unique / r2_full if r2_full > 0 else 0

    # Gauge-like visualization
    theta = np.linspace(0, np.pi, 100)
    r_outer = 1.0
    r_inner = 0.6

    # Background arc (full explained variance)
    for th in theta:
        ax.plot([r_inner * np.cos(th), r_outer * np.cos(th)],
                [r_inner * np.sin(th), r_outer * np.sin(th)],
                color="#E0E0E0", linewidth=0.5)

    # C's portion
    n_fill = int(novelty * 100)
    for th in theta[:n_fill]:
        ax.plot([r_inner * np.cos(th), r_outer * np.cos(th)],
                [r_inner * np.sin(th), r_outer * np.sin(th)],
                color="#2196F3", linewidth=1.5)

    # Labels
    ax.text(0, 0.15, f"{novelty*100:.0f}%", ha="center", va="center", fontsize=24, fontweight="bold", color="#2196F3")
    ax.text(0, -0.1, f"of R²={r2_full:.3f}", ha="center", va="center", fontsize=10, color="gray")
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-0.4, 1.3)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(f"{targets[ti]}", fontsize=12, fontweight="bold")

fig.suptitle("RD-7: C's Novelty Score — % of Explained Variance Uniquely Due to C",
             fontsize=13, fontweight="bold", y=1.05)
plt.tight_layout()
plt.savefig("audits/rd07_fig4_novelty_gauge.png", dpi=150, bbox_inches="tight")
print("Saved: audits/rd07_fig4_novelty_gauge.png")

# ─── Figure 5: Friction dominance ───
fig, ax = plt.subplots(1, 1, figsize=(8, 5))

target_labels_short = ["ΔC (dip)", "Restoration", "τ_rec"]
r2_with_f = [0.4469, 0.5836, 0.3274]
r2_without_f = [0.1274, 0.1738, 0.0897]
friction_contrib = [r2_with_f[i] - r2_without_f[i] for i in range(3)]

x = np.arange(3)
width = 0.35

bars1 = ax.bar(x - width/2, r2_without_f, width, label="Metrics only (C + I_pred + C_σ + MSE)", color="#2196F3", alpha=0.8)
bars2 = ax.bar(x + width/2, friction_contrib, width, label="Friction contribution", color="#FF5722", alpha=0.8, bottom=r2_without_f)

for i in range(3):
    ax.text(x[i] - width/2, r2_without_f[i] + 0.01, f"{r2_without_f[i]:.3f}", ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.text(x[i] + width/2, r2_with_f[i] + 0.01, f"{r2_with_f[i]:.3f}", ha="center", va="bottom", fontsize=10, fontweight="bold")

ax.set_ylabel("Total R²", fontsize=12)
ax.set_title("RD-7: Friction Dominates Recovery Prediction\n(Metrics explain 9-17%; adding friction → 33-58%)", fontsize=13, fontweight="bold")
ax.set_xticks(x)
ax.set_xticklabels(target_labels_short, fontsize=11)
ax.legend(fontsize=10, loc="upper right")
ax.grid(True, alpha=0.3, axis="y")
ax.set_ylim(0, 0.7)

plt.tight_layout()
plt.savefig("audits/rd07_fig5_friction_dominance.png", dpi=150, bbox_inches="tight")
print("Saved: audits/rd07_fig5_friction_dominance.png")

print("\nAll figures generated.")
