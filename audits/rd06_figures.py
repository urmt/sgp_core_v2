"""RD-6: Generate figures for ensemble resilience analysis."""

import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from scipy.special import expit

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

with open("audits/rd06_ensemble_raw.json") as f:
    results = json.load(f)

c_pre = np.array([r["C_pre"] for r in results])
collapsed = np.array([1 if r["collapsed"] else 0 for r in results])
survived = ~collapsed.astype(bool)

c_surv = c_pre[survived]
c_coll = c_pre[collapsed.astype(bool)]

# ─── Figure 1: C_pre distributions (survived vs collapsed) ───
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# Panel A: Overlapping histograms
ax = axes[0]
bins = np.linspace(0.40, 0.56, 25)
ax.hist(c_surv, bins=bins, alpha=0.6, color="steelblue", label=f"Survived (n={sum(survived)})", density=True)
ax.hist(c_coll, bins=bins, alpha=0.6, color="red", label=f"Collapsed (n={sum(collapsed)})", density=True)
ax.set_xlabel("C_pre", fontsize=12)
ax.set_ylabel("Density", fontsize=12)
ax.set_title("A. C_pre Distribution by Outcome", fontsize=13, fontweight="bold")
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

# Panel B: Violin plot
ax = axes[1]
parts = ax.violinplot([c_surv, c_coll], positions=[0, 1], showmeans=True, showmedians=True)
for pc in parts['bodies']:
    pc.set_alpha(0.5)
parts['cmeans'].set_color('black')
parts['cmedians'].set_color('orange')
ax.set_xticks([0, 1])
ax.set_xticklabels(["Survived", "Collapsed"])
ax.set_ylabel("C_pre", fontsize=12)
ax.set_title("B. C_pre Violin Plot", fontsize=13, fontweight="bold")
ax.grid(True, alpha=0.3, axis='y')

# Annotate
ax.text(0, np.mean(c_surv) + 0.005, f"μ={np.mean(c_surv):.4f}", ha='center', fontsize=9)
ax.text(1, np.mean(c_coll) + 0.005, f"μ={np.mean(c_coll):.4f}", ha='center', fontsize=9)

# Panel C: C_pre vs C_final/C_pre
ax = axes[2]
c_ratio = np.array([r["C_ratio"] for r in results])
c_ratio_surv = c_ratio[survived]
c_pre_surv = c_pre[survived]

ax.scatter(c_pre_surv, c_ratio_surv, alpha=0.4, s=20, c="steelblue", label="Survived")
ax.scatter(c_pre[collapsed.astype(bool)], np.zeros(int(sum(collapsed))), alpha=0.6, s=30, c="red", marker="x", label="Collapsed (C_ratio=0)")
# Fit line for survivors
if len(c_pre_surv) > 2:
    slope, intercept, r, p, se = stats.linregress(c_pre_surv, c_ratio_surv)
    x_fit = np.linspace(c_pre_surv.min(), c_pre_surv.max(), 100)
    ax.plot(x_fit, slope * x_fit + intercept, 'k--', alpha=0.7, label=f"r={r:.3f}, p={p:.4f}")
ax.set_xlabel("C_pre", fontsize=12)
ax.set_ylabel("C_final / C_pre", fontsize=12)
ax.set_title("C. C_pre vs Recovery Ratio", fontsize=13, fontweight="bold")
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)
ax.axhline(1.0, color='gray', linestyle=':', alpha=0.5)

plt.tight_layout()
plt.savefig("audits/rd06_fig1_distributions.png", dpi=150, bbox_inches="tight")
print("Saved: audits/rd06_fig1_distributions.png")

# ─── Figure 2: ROC curve ───
fig, ax = plt.subplots(1, 1, figsize=(7, 6))

# Compute ROC manually
thresholds = np.sort(np.unique(c_pre))[::-1]
tpr_list = [0]
fpr_list = [0]
n_pos = sum(collapsed)
n_neg = sum(survived)

for thr in thresholds:
    predicted_pos = c_pre >= thr
    tp = sum(predicted_pos & collapsed.astype(bool))
    fp = sum(predicted_pos & survived)
    tpr_list.append(tp / max(n_pos, 1))
    fpr_list.append(fp / max(n_neg, 1))

tpr_list.append(1)
fpr_list.append(1)
tpr_arr = np.array(tpr_list)
fpr_arr = np.array(fpr_list)

# AUC via trapezoid
auc = np.trapezoid(tpr_arr, fpr_arr)

ax.plot(fpr_arr, tpr_arr, 'b-', linewidth=2, label=f"ROC (AUC = {auc:.3f})")
ax.plot([0, 1], [0, 1], 'k--', alpha=0.5, label="Chance")
ax.set_xlabel("False Positive Rate", fontsize=12)
ax.set_ylabel("True Positive Rate", fontsize=12)
ax.set_title("ROC: C_pre Predicting Collapse", fontsize=13, fontweight="bold")
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)
ax.set_xlim(-0.02, 1.02)
ax.set_ylim(-0.02, 1.02)

# Add annotations
ax.text(0.6, 0.3, f"AUC = {auc:.3f}\n(Chance = 0.500)\nNo discrimination",
        fontsize=11, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig("audits/rd06_fig2_roc.png", dpi=150, bbox_inches="tight")
print("Saved: audits/rd06_fig2_roc.png")

# ─── Figure 3: Logistic regression curve ───
fig, ax = plt.subplots(1, 1, figsize=(7, 5))

# Fit logistic regression
from scipy.optimize import minimize

def neg_loglik(params, x, y):
    w, b = params
    p = expit(w * x + b)
    p = np.clip(p, 1e-10, 1 - 1e-10)
    return -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))

res = minimize(neg_loglik, [0, -3], args=(c_pre, collapsed.astype(float)), method='Nelder-Mead')
w_opt, b_opt = res.x

x_fit = np.linspace(c_pre.min() - 0.01, c_pre.max() + 0.01, 200)
p_fit = expit(w_opt * x_fit + b_opt)

# Scatter with jitter
jitter = np.random.default_rng(42).uniform(-0.02, 0.02, len(collapsed))
ax.scatter(c_pre[survived], jitter[survived] + 0, alpha=0.3, s=15, c="steelblue", label="Survived")
ax.scatter(c_pre[collapsed.astype(bool)], jitter[collapsed.astype(bool)] + 1, alpha=0.5, s=25, c="red", marker="x", label="Collapsed")
ax.plot(x_fit, p_fit * 1, 'k-', linewidth=2, label=f"Logistic fit (OR={np.exp(w_opt):.1f}/unit)")

ax.set_xlabel("C_pre", fontsize=12)
ax.set_ylabel("P(Collapse)", fontsize=12)
ax.set_title("Logistic Regression: collapse ~ C_pre", fontsize=13, fontweight="bold")
ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
ax.set_yticklabels(["Survive", "0.25", "0.5", "0.75", "Collapse"])
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)
ax.set_ylim(-0.1, 1.1)

plt.tight_layout()
plt.savefig("audits/rd06_fig3_logistic.png", dpi=150, bbox_inches="tight")
print("Saved: audits/rd06_fig3_logistic.png")

# ─── Figure 4: Effect size summary ───
fig, ax = plt.subplots(1, 1, figsize=(8, 4))

metrics = ["Welch's t\n(C_pre: surv vs coll)", "Cohen's d\n(effect size)", "AUC\n(ROC)", "Rank-biserial\nr"]
values = [-0.631, -0.123, 0.473, -0.027]
ci_lows = [-1.5, -0.502, 0.365, -0.15]
ci_highs = [0.24, 0.253, 0.577, 0.10]
null_lines = [0, 0, 0.5, 0]

x_pos = np.arange(len(metrics))
colors = ["steelblue" if v != 0.473 else "coral" for v in values]

for i, (m, v, lo, hi, nl) in enumerate(zip(metrics, values, ci_lows, ci_highs, null_lines)):
    ax.errorbar(i, v, yerr=[[v-lo], [hi-v]], fmt='o', color=colors[i], 
                markersize=10, capsize=6, capthick=2, linewidth=2)
    ax.axhline(nl, xmin=i/len(metrics)-0.1, xmax=i/len(metrics)+0.1, 
               color='gray', linestyle=':', alpha=0.5)

ax.set_xticks(x_pos)
ax.set_xticklabels(metrics, fontsize=10)
ax.set_title("RD-6: Effect Sizes with 95% CIs", fontsize=13, fontweight="bold")
ax.grid(True, alpha=0.3, axis='y')
ax.axhline(0, color='gray', linestyle='-', alpha=0.3)

# Add p-value annotations
p_vals = [0.532, None, 0.682, None]
for i, p in enumerate(p_vals):
    if p is not None:
        ax.text(i, values[i] + (ci_highs[i] - values[i]) + 0.05, f"p={p}", 
                ha='center', fontsize=9, color='gray')

plt.tight_layout()
plt.savefig("audits/rd06_fig4_effect_sizes.png", dpi=150, bbox_inches="tight")
print("Saved: audits/rd06_fig4_effect_sizes.png")

print("\nAll figures generated.")
