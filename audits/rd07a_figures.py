"""RD-7A: Generate figures for cross-domain novelty audit."""

import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

with open("audits/rd07a_novelty_audit.json") as f:
    data = json.load(f)

with open("coherence-benchmark/results/benchmark_v1.json") as f:
    bench = json.load(f)
with open("coherence-benchmark/results/t901_ensemble.json") as f:
    t901 = json.load(f)

def get_mean(v):
    if isinstance(v, dict):
        if "mean" in v: return v["mean"]
        if "1" in v: return v["1"]
        return list(v.values())[0]
    return float(v)

sys_names = list(bench.keys())
sys_labels = ["S1", "S2", "S3", "S4", "S5", "S6", "P1", "P2"]
C_bench = np.array([get_mean(bench[s]["C"]) for s in sys_names])

# t901 data
C_t901 = np.array([r["pre_C"] for r in t901])
I_t901 = np.array([r["pre_I_pred"] for r in t901])
Cs_t901 = np.array([r["pre_C_sigma"] for r in t901])
MSE_t901 = np.array([r["pre_MSE_s1"] for r in t901])
friction_t901 = np.array([r["friction"] for r in t901])

# ─── Figure 1: Actual vs Predicted C (both domains) ───
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Cross-domain
ax = axes[0]
actual = data["cross_domain"]["actuals"]
pred = data["cross_domain"]["predictions"]
loo_pred = data["cross_domain"]["loo_predictions"]

ax.scatter(actual, pred, s=80, c="#2196F3", edgecolors="black", linewidth=0.5, zorder=5, label="In-sample")
ax.scatter(actual, loo_pred, s=80, c="#FF5722", edgecolors="black", linewidth=0.5, zorder=5, marker="D", label="LOO-CV")
lims = [min(min(actual), min(pred), min(loo_pred)) - 0.05, max(max(actual), max(pred), max(loo_pred)) + 0.05]
ax.plot(lims, lims, 'k--', alpha=0.5, label="Perfect prediction")
ax.set_xlabel("Actual C", fontsize=12)
ax.set_ylabel("Predicted C", fontsize=12)
ax.set_title(f"Cross-Domain (n=8)\nR² = {data['cross_domain']['R²']:.3f}, LOO-R² = {data['cross_domain']['LOO_R²']:.3f}",
             fontsize=12, fontweight="bold")
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)

# Annotate systems
for i, sl in enumerate(sys_labels):
    ax.annotate(sl, (actual[i], pred[i]), fontsize=8, ha="center", va="bottom",
                xytext=(0, 5), textcoords="offset points")

# Within-domain
ax = axes[1]
# Fit model
X_t = np.column_stack([I_t901, Cs_t901, MSE_t901])
y_t = C_t901
X_aug = np.column_stack([np.ones(len(y_t)), X_t])
beta = np.linalg.lstsq(X_aug, y_t, rcond=None)[0]
yhat_t = X_aug @ beta

# LOO
n = len(y_t)
ypred_loo = np.zeros(n)
for i in range(n):
    mask = np.arange(n) != i
    X_aug_m = np.column_stack([np.ones(n-1), X_t[mask]])
    beta_m = np.linalg.lstsq(X_aug_m, y_t[mask], rcond=None)[0]
    ypred_loo[i] = np.dot(np.concatenate([[1], X_t[i]]), beta_m)

scatter = ax.scatter(y_t, yhat_t, s=30, c=friction_t901, cmap="viridis", edgecolors="black", linewidth=0.3, alpha=0.7)
ax.scatter(y_t, ypred_loo, s=30, c="#FF5722", edgecolors="black", linewidth=0.3, alpha=0.4, marker="D")
lims2 = [min(y_t.min(), yhat_t.min()) - 0.02, max(y_t.max(), yhat_t.max()) + 0.02]
ax.plot(lims2, lims2, 'k--', alpha=0.5, label="Perfect prediction")
ax.set_xlabel("Actual C", fontsize=12)
ax.set_ylabel("Predicted C", fontsize=12)
ax.set_title(f"Within-Domain (n=60)\nR² = {data['within_domain']['R²']:.3f}, LOO-R² = {data['within_domain']['LOO_R²']:.3f}",
             fontsize=12, fontweight="bold")
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)
plt.colorbar(scatter, ax=ax, label="Friction μ", shrink=0.8)

fig.suptitle("RD-7A: Can C Be Reconstructed from Competitors?", fontsize=14, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("audits/rd07a_fig1_actual_vs_predicted.png", dpi=150, bbox_inches="tight")
print("Saved: audits/rd07a_fig1_actual_vs_predicted.png")

# ─── Figure 2: Residuals analysis ───
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# Residual histogram
ax = axes[0]
resid = np.array(data["cross_domain"]["residuals"])
ax.hist(resid, bins=8, color="#2196F3", alpha=0.7, edgecolor="black")
ax.axvline(0, color="red", linestyle="--", alpha=0.7)
ax.set_xlabel("Residual (Actual − Predicted)", fontsize=11)
ax.set_ylabel("Count", fontsize=11)
ax.set_title("Cross-Domain Residuals", fontsize=12, fontweight="bold")
ax.grid(True, alpha=0.3)

# Residuals by friction (within-domain)
ax = axes[1]
resid_t = y_t - yhat_t
frictions = sorted(set(friction_t901))
positions = list(range(len(frictions)))
data_by_f = [resid_t[friction_t901 == f] for f in frictions]

bp = ax.boxplot(data_by_f, positions=positions, widths=0.5, patch_artist=True)
for patch, f in zip(bp["boxes"], frictions):
    patch.set_facecolor(plt.cm.viridis(f / max(frictions)))
    patch.set_alpha(0.6)
ax.axhline(0, color="red", linestyle="--", alpha=0.7)
ax.set_xticks(positions)
ax.set_xticklabels([f"μ={f:.2f}" for f in frictions], fontsize=9, rotation=45)
ax.set_ylabel("Residual", fontsize=11)
ax.set_title("Within-Domain Residuals by Friction", fontsize=12, fontweight="bold")
ax.grid(True, alpha=0.3, axis="y")

# Residual vs predicted
ax = axes[2]
ax.scatter(yhat_t, resid_t, s=25, c=friction_t901, cmap="viridis", edgecolors="black", linewidth=0.3, alpha=0.7)
ax.axhline(0, color="red", linestyle="--", alpha=0.7)
ax.set_xlabel("Predicted C", fontsize=11)
ax.set_ylabel("Residual", fontsize=11)
ax.set_title("Residuals vs Predicted (within-domain)", fontsize=12, fontweight="bold")
ax.grid(True, alpha=0.3)

fig.suptitle("RD-7A: Residual Analysis", fontsize=14, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("audits/rd07a_fig2_residuals.png", dpi=150, bbox_inches="tight")
print("Saved: audits/rd07a_fig2_residuals.png")

# ─── Figure 3: LOO-CV comparison ───
fig, ax = plt.subplots(1, 1, figsize=(8, 5))

categories = ["Cross-Domain\n(8 systems)", "Within-Domain\n(60 runs)"]
r2_vals = [data["cross_domain"]["R²"], data["within_domain"]["R²"]]
loo_vals = [data["cross_domain"]["LOO_R²"], data["within_domain"]["LOO_R²"]]

x = np.arange(len(categories))
width = 0.3

bars1 = ax.bar(x - width/2, r2_vals, width, label="R² (in-sample)", color="#2196F3", alpha=0.8)
bars2 = ax.bar(x + width/2, loo_vals, width, label="LOO-CV R²", color="#FF5722", alpha=0.8)

for bar, val in zip(bars1, r2_vals):
    ax.text(bar.get_x() + bar.get_width()/2, max(val, 0) + 0.02, f"{val:.3f}",
            ha="center", va="bottom", fontsize=10, fontweight="bold")
for bar, val in zip(bars2, loo_vals):
    ypos = val + 0.02 if val >= 0 else val - 0.05
    ax.text(bar.get_x() + bar.get_width()/2, ypos, f"{val:.3f}",
            ha="center", va="bottom" if val >= 0 else "top", fontsize=10, fontweight="bold")

ax.axhline(0, color="gray", linestyle="-", alpha=0.3)
ax.axhline(1.0, color="gray", linestyle=":", alpha=0.3, label="Perfect (R²=1)")
ax.set_ylabel("R²", fontsize=12)
ax.set_title("RD-7A: Reconstruction Quality\n(C ~ I_pred + C_σ + MSE + TE)", fontsize=13, fontweight="bold")
ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=11)
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3, axis="y")
ax.set_ylim(-1.0, 1.2)

plt.tight_layout()
plt.savefig("audits/rd07a_fig3_loo_comparison.png", dpi=150, bbox_inches="tight")
print("Saved: audits/rd07a_fig3_loo_comparison.png")

# ─── Figure 4: C vs MSE scatter (the dominant relationship) ───
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Cross-domain
ax = axes[0]
MSE_bench = np.array([get_mean(bench[s]["mse"]) for s in sys_names])
ax.scatter(MSE_bench, C_bench, s=100, c="#2196F3", edgecolors="black", linewidth=0.5, zorder=5)
r, p = stats.pearsonr(MSE_bench, C_bench)
x_fit = np.linspace(MSE_bench.min(), MSE_bench.max(), 100)
slope, intercept, _, _, _ = stats.linregress(MSE_bench, C_bench)
ax.plot(x_fit, slope * x_fit + intercept, 'r--', alpha=0.7, label=f"r = {r:.3f}")
for i, sl in enumerate(sys_labels):
    ax.annotate(sl, (MSE_bench[i], C_bench[i]), fontsize=9, ha="center", va="bottom",
                xytext=(0, 5), textcoords="offset points")
ax.set_xlabel("MSE", fontsize=12)
ax.set_ylabel("C", fontsize=12)
ax.set_title(f"Cross-Domain: C vs MSE\nr = {r:.3f}", fontsize=12, fontweight="bold")
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

# Within-domain
ax = axes[1]
ax.scatter(MSE_t901, C_t901, s=25, c=friction_t901, cmap="viridis", edgecolors="black", linewidth=0.3, alpha=0.7)
r_t, p_t = stats.pearsonr(MSE_t901, C_t901)
slope_t, intercept_t, _, _, _ = stats.linregress(MSE_t901, C_t901)
x_fit_t = np.linspace(MSE_t901.min(), MSE_t901.max(), 100)
ax.plot(x_fit_t, slope_t * x_fit_t + intercept_t, 'r--', alpha=0.7, label=f"r = {r_t:.3f}")
ax.set_xlabel("MSE", fontsize=12)
ax.set_ylabel("C", fontsize=12)
ax.set_title(f"Within-Domain: C vs MSE\nr = {r_t:.3f}", fontsize=12, fontweight="bold")
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)
plt.colorbar(ax.collections[0], ax=ax, label="Friction μ", shrink=0.8)

fig.suptitle("RD-7A: C vs MSE — The Dominant Relationship", fontsize=14, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("audits/rd07a_fig4_c_vs_mse.png", dpi=150, bbox_inches="tight")
print("Saved: audits/rd07a_fig4_c_vs_mse.png")

print("\nAll figures generated.")
