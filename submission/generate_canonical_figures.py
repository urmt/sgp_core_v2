"""
Generate canonical figures for submission.

Paper 1 (PRE Dimensional Collapse):
  Fig 3: Ensemble comparison — MEC vs GOE vs sparse in (α, PR, IPR) space
  Fig 4: Precision spectrum — GraphLasso precision eigenvalue spectrum
  Fig 5: Constraint summary — combined (α, PR, LC) zone geometry

Paper 2 (PRE Spectral Sustainment):
  Fig 3: RG flow schematic — conceptual renormalization flow
  Fig 4: Precision vs temporal operators — operator comparison
  Fig 5: Universality positioning — MEC relative to all ensembles

Output: figures/ (APS-compliant vector PDFs)
"""

import os, sys, warnings
import numpy as np
from numpy import linalg as la
from glob import glob
from sklearn.covariance import GraphicalLasso, LedoitWolf
from sklearn.linear_model import Ridge

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import FancyArrowPatch

warnings.filterwarnings('ignore')

FIG_DIR = 'submission/figures'
os.makedirs(FIG_DIR, exist_ok=True)
np.random.seed(42)

rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans'],
    'mathtext.fontset': 'dejavusans',
    'font.size': 9,
    'axes.labelsize': 10,
    'axes.titlesize': 11,
    'legend.fontsize': 8,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})

DATA_DIR = 'experiments/dynamics/tier2_data'

MEC_COLOR = '#2e6fad'
GOE_COLOR = '#d95f02'
SPARSE_COLOR = '#1b9e77'
PRECISION_COLOR = '#8da0cb'
TEMPORAL_COLOR = '#e78ac3'

# ── Data ──────────────────────────────────────────────────────────────────

def load_mec(data_dir=None):
    if data_dir is None:
        data_dir = DATA_DIR
    files = sorted(glob(os.path.join(data_dir, '*MEC_FRtensor*.npy')))
    if not files:
        raise FileNotFoundError(f"No MEC files in {data_dir}/")
    recordings, names = [], []
    for f in files:
        X = np.load(f).astype(np.float64)
        if X.ndim == 3:
            X = X.reshape(X.shape[0] * X.shape[1], X.shape[2])
        recordings.append(X)
        name = os.path.splitext(os.path.basename(f))[0].replace('_FRtensor', '')
        names.append(name)
    return recordings, names

# ── Metrics ────────────────────────────────────────────────────────────────

def spectral_decay_rate(eigvals):
    s = np.sort(eigvals)[::-1]
    ks = np.arange(1, len(s) + 1)
    valid = s > 1e-10
    if valid.sum() < 3:
        return 0.0
    coeffs = np.polyfit(ks[valid], np.log(s[valid]), 1)
    return float(-coeffs[0])

def participation_ratio(eigvals):
    ev = np.abs(eigvals)
    s = np.sum(ev)
    if s < 1e-15:
        return float(len(ev))
    return float((np.sum(ev) ** 2) / np.sum(ev ** 2))

def inverse_participation_ratio(eigvec):
    return float(np.sum(eigvec ** 4))

def metric_from_covariance(C):
    evals, evecs = la.eigh(C)
    evals = evals[::-1]
    evecs = evecs[:, ::-1]
    alpha = spectral_decay_rate(evals)
    PR = participation_ratio(evals)
    iprs = np.array([inverse_participation_ratio(evecs[:, i]) for i in range(C.shape[0])])
    return {'alpha': alpha, 'PR': PR, 'mean_IPR': float(np.mean(iprs)), 'evals': evals}

def correlation_metrics(X):
    X = X - X.mean(axis=0)
    X = X / (X.std(axis=0) + 1e-10)
    C = (X.T @ X) / max(X.shape[0] - 1, 1)
    return metric_from_covariance(C)

def operator_metrics(A):
    λ, V = la.eig(A)
    idx = np.argsort(np.abs(λ))[::-1]
    λ = λ[idx]
    V = V[:, idx]
    for i in range(V.shape[1]):
        n = la.norm(V[:, i])
        if n > 1e-15:
            V[:, i] /= n
    IPRs = np.array([inverse_participation_ratio(V[:, i]) for i in range(V.shape[1])])
    return {
        'alpha': spectral_decay_rate(np.abs(λ)),
        'PR': participation_ratio(np.abs(λ)),
        'mean_IPR': float(np.mean(IPRs)),
        'evals': np.abs(λ),
    }

# ── Operators ──────────────────────────────────────────────────────────────

def graphical_lasso_safe(X, alpha=0.1):
    X = X - X.mean(axis=0)
    X = X / (X.std(axis=0) + 1e-10)
    T, N = X.shape
    if T < N:
        X = X[:, :max(T//2, 10)]
    model = GraphicalLasso(alpha=alpha, max_iter=100)
    try:
        model.fit(X)
        return model.precision_
    except Exception:
        return LedoitWolf().fit(X).precision_

def ridge_var(X, alpha=1.0, max_dim=60):
    X = X - X.mean(axis=0)
    X = X / (X.std(axis=0) + 1e-10)
    T, N = X.shape
    target_dim = min(N, max_dim, T // 3)
    if target_dim < 5:
        target_dim = min(N, 10)
    if N > target_dim:
        X = X[:, :target_dim]
    X1, X2 = X[:-1], X[1:]
    model = Ridge(alpha=alpha, fit_intercept=False)
    model.fit(X1, X2)
    return model.coef_.T

# ── Ensembles ──────────────────────────────────────────────────────────────

def goe_ensemble(N, n_samples=30):
    results = []
    for _ in range(n_samples):
        X = np.random.randn(2000, N)
        X = X - X.mean(axis=0)
        X = X / (X.std(axis=0) + 1e-10)
        C = (X.T @ X) / 1999
        results.append(metric_from_covariance(C))
    return results

def sparse_ensemble(N, p=0.05, n_samples=20):
    results = []
    for _ in range(n_samples):
        W = np.random.randn(N, N) * (np.random.rand(N, N) < p)
        W = (W + W.T) / 2
        np.fill_diagonal(W, N * 0.1)
        eigs = la.eigvalsh(W)
        if eigs.min() < 1e-3:
            W += (1e-3 - eigs.min()) * np.eye(N)
        C = la.inv(W)
        C = C / np.diag(C).max()
        results.append(metric_from_covariance(C))
    return results

# ═══════════════════════════════════════════════════════════════════════════
# FIGURES
# ═══════════════════════════════════════════════════════════════════════════

def fig_ensemble_comparison(mec_metrics, goe_metrics, sparse_metrics):
    """Paper 1 Fig 3: MEC vs GOE vs sparse in (alpha, PR, IPR) space."""
    print("P1 Fig 3: Ensemble comparison...")
    mec_a = [m['alpha'] for m in mec_metrics]
    mec_p = [m['PR'] for m in mec_metrics]
    mec_i = [m['mean_IPR'] for m in mec_metrics]
    goe_a = [m['alpha'] for m in goe_metrics]
    goe_p = [m['PR'] for m in goe_metrics]
    goe_i = [m['mean_IPR'] for m in goe_metrics]
    spa_a = [m['alpha'] for m in sparse_metrics]
    spa_p = [m['PR'] for m in sparse_metrics]
    spa_i = [m['mean_IPR'] for m in sparse_metrics]

    fig, axes = plt.subplots(1, 3, figsize=(10, 3.5))

    # Panel 1: alpha vs PR
    ax = axes[0]
    ax.scatter(mec_a, mec_p, c=MEC_COLOR, s=15, alpha=0.6, edgecolors='white', linewidth=0.3, label='MEC')
    ax.scatter(goe_a, goe_p, c=GOE_COLOR, s=10, alpha=0.4, marker='s', label='GOE')
    ax.scatter(spa_a, spa_p, c=SPARSE_COLOR, s=10, alpha=0.4, marker='^', label='Sparse p=0.05')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel(r'$\alpha$')
    ax.set_ylabel('PR')
    ax.legend(fontsize=7)
    ax.set_title(r'$\alpha$ vs PR')

    # Panel 2: alpha vs IPR
    ax = axes[1]
    ax.scatter(mec_a, mec_i, c=MEC_COLOR, s=15, alpha=0.6, edgecolors='white', linewidth=0.3)
    ax.scatter(goe_a, goe_i, c=GOE_COLOR, s=10, alpha=0.4, marker='s')
    ax.scatter(spa_a, spa_i, c=SPARSE_COLOR, s=10, alpha=0.4, marker='^')
    ax.set_xscale('log')
    ax.set_xlabel(r'$\alpha$')
    ax.set_ylabel('Mean IPR')
    ax.set_title(r'$\alpha$ vs IPR')

    # Panel 3: PR vs IPR
    ax = axes[2]
    ax.scatter(mec_p, mec_i, c=MEC_COLOR, s=15, alpha=0.6, edgecolors='white', linewidth=0.3)
    ax.scatter(goe_p, goe_i, c=GOE_COLOR, s=10, alpha=0.4, marker='s')
    ax.scatter(spa_p, spa_i, c=SPARSE_COLOR, s=10, alpha=0.4, marker='^')
    ax.set_xlabel('PR')
    ax.set_ylabel('Mean IPR')
    ax.set_title('PR vs IPR')

    plt.tight_layout()
    path = os.path.join(FIG_DIR, 'p1_fig3_ensemble_comparison.pdf')
    plt.savefig(path, dpi=300)
    plt.close()
    print(f"  Saved: {path}")


def fig_precision_spectrum(mec_recordings):
    """Paper 1 Fig 4: Precision matrix eigenvalue spectrum vs correlation spectrum."""
    print("P1 Fig 4: Precision spectrum...")
    corr_alphas, prec_alphas = [], []
    corr_PRs, prec_PRs = [], []
    corr_evals_list, prec_evals_list = [], []

    for i, X in enumerate(mec_recordings[:10]):
        m = correlation_metrics(X)
        corr_alphas.append(m['alpha'])
        corr_PRs.append(m['PR'])
        corr_evals_list.append(m['evals'] / m['evals'][0])
        try:
            P = graphical_lasso_safe(X, alpha=0.1)
            pm = operator_metrics(P)
            prec_alphas.append(pm['alpha'])
            prec_PRs.append(pm['PR'])
            prec_evals_list.append(pm['evals'] / pm['evals'][0])
        except Exception:
            prec_alphas.append(0)
            prec_PRs.append(0)
            prec_evals_list.append(np.array([1.0]))

    fig, axes = plt.subplots(1, 3, figsize=(10, 3.5))

    # Panel 1: Mean spectra
    ax = axes[0]
    max_rank = min(50, min(len(e) for e in corr_evals_list))
    corr_mean = np.mean([e[:max_rank] for e in corr_evals_list], axis=0)
    corr_std = np.std([e[:max_rank] for e in corr_evals_list], axis=0)
    max_rank_p = min(50, min(len(e) for e in prec_evals_list if len(e) > 1))
    prec_mean = np.mean([e[:max_rank_p] for e in prec_evals_list if len(e) > 1], axis=0)
    prec_std = np.std([e[:max_rank_p] for e in prec_evals_list if len(e) > 1], axis=0)

    ax.fill_between(range(1, max_rank+1), corr_mean-corr_std, corr_mean+corr_std, alpha=0.15, color=MEC_COLOR)
    ax.plot(range(1, max_rank+1), corr_mean, '-', color=MEC_COLOR, lw=1.5,
            label=f'Correlation ($\\alpha$={np.mean(corr_alphas):.3f})')
    ax.fill_between(range(1, max_rank_p+1), prec_mean-prec_std, prec_mean+prec_std, alpha=0.15, color=PRECISION_COLOR)
    ax.plot(range(1, max_rank_p+1), prec_mean, '-', color=PRECISION_COLOR, lw=1.5,
            label=f'Precision ($\\alpha$={np.mean(prec_alphas):.3f})')
    ax.set_yscale('log')
    ax.set_xlabel('Rank')
    ax.set_ylabel('Normalized eigenvalue')
    ax.legend(fontsize=7)
    ax.set_title('Correlation vs precision spectra')

    # Panel 2: alpha comparison
    ax = axes[1]
    valid = [i for i in range(len(prec_alphas)) if prec_alphas[i] > 0]
    ax.scatter([corr_alphas[i] for i in valid], [prec_alphas[i] for i in valid],
               c=MEC_COLOR, s=20, alpha=0.6, edgecolors='white', linewidth=0.3)
    lims = [0.001, 1]
    ax.plot(lims, lims, 'k--', alpha=0.3, lw=1)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel(r'$\alpha$ (correlation)')
    ax.set_ylabel(r'$\alpha$ (precision)')
    ax.set_title(r'$\alpha$ operator comparison')

    # Panel 3: PR comparison
    ax = axes[2]
    ax.scatter([corr_PRs[i] for i in valid], [prec_PRs[i] for i in valid],
               c=MEC_COLOR, s=20, alpha=0.6, edgecolors='white', linewidth=0.3)
    lims = [1, 200]
    ax.plot(lims, lims, 'k--', alpha=0.3, lw=1)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('PR (correlation)')
    ax.set_ylabel('PR (precision)')
    ax.set_title('PR operator comparison')

    plt.tight_layout()
    path = os.path.join(FIG_DIR, 'p1_fig4_precision_spectrum.pdf')
    plt.savefig(path, dpi=300)
    plt.close()
    print(f"  Saved: {path}")
    print(f"  Mean correlation alpha: {np.mean(corr_alphas):.3f}, PR: {np.mean(corr_PRs):.1f}")
    print(f"  Mean precision alpha: {np.mean(prec_alphas):.3f}, PR: {np.mean(prec_PRs):.1f}")


def fig_constraint_summary(mec_metrics, syn_collapse, syn_transition, syn_broad):
    """Paper 1 Fig 5: Combined constraint geometry showing allowed/forbidden zones."""
    print("P1 Fig 5: Constraint summary...")
    fig, axes = plt.subplots(1, 2, figsize=(8, 3.5))

    # Panel 1: alpha-PR with bound and zones
    ax = axes[0]
    alpha_grid = np.logspace(-2, 1.5, 200)
    PR_bound = (1 + np.exp(-alpha_grid)) / (1 - np.exp(-alpha_grid))
    ax.fill_between(alpha_grid, PR_bound, 1000, alpha=0.08, color='gray', label='Forbidden')

    mec_A = np.array([m['alpha'] for m in mec_metrics])
    mec_P = np.array([m['PR'] for m in mec_metrics])
    ax.scatter(mec_A, mec_P, c=MEC_COLOR, s=15, alpha=0.6, edgecolors='white', linewidth=0.3, label='MEC')

    # Synthetic classes
    for sdata, color, marker, label in [
        (syn_collapse, '#d95f02', '^', 'Collapse'),
        (syn_transition, '#1b9e77', 's', 'Transition'),
        (syn_broad, '#7570b3', 'D', 'Broad synthetic'),
    ]:
        if sdata:
            sA, sP = zip(*[(m['alpha'], m['PR']) for m in sdata])
            ax.scatter(sA, sP, c=color, s=10, alpha=0.4, marker=marker, label=label)

    ax.plot(alpha_grid, PR_bound, 'k--', lw=1)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel(r'$\alpha$')
    ax.set_ylabel('PR')
    ax.set_xlim(0.008, 30)
    ax.set_ylim(0.8, 500)
    ax.legend(fontsize=6, ncol=2)
    ax.set_title('Zone I: $\\alpha$-PR geometry')

    # Zone labels
    ax.text(0.02, 0.05, 'Persistence', transform=ax.transAxes, fontsize=7, color=MEC_COLOR)
    ax.text(0.6, 0.05, 'Collapse', transform=ax.transAxes, fontsize=7, color='#d95f02')

    # Panel 2: PR-LC with void
    ax = axes[1]
    void_PR = np.array([1, 15, 15, 1])
    void_LC = np.array([-10, -10, -5, -5])
    ax.fill(void_PR, void_LC, alpha=0.12, color='red', label='Convex void')

    all_PR = [m['PR'] for m in mec_metrics]
    all_LC = [m['LC'] for m in mec_metrics]
    ax.scatter(all_PR, all_LC, c=MEC_COLOR, s=15, alpha=0.6, edgecolors='white', linewidth=0.3, label='MEC')

    for sdata, color, marker in [
        (syn_collapse, '#d95f02', '^'),
        (syn_transition, '#1b9e77', 's'),
        (syn_broad, '#7570b3', 'D'),
    ]:
        if sdata:
            sPR = [m['PR'] for m in sdata]
            sLC = [m['LC'] for m in sdata]
            ax.scatter(sPR, sLC, c=color, s=10, alpha=0.4, marker=marker)

    PR_grid = np.logspace(0, 2.5, 200)
    ax.plot(PR_grid, -2 * np.log10(PR_grid) + 0.6, 'k--', lw=1, label='LC bound')
    ax.set_xscale('log')
    ax.set_xlabel('PR')
    ax.set_ylabel('LC')
    ax.set_xlim(0.8, 500)
    ax.set_ylim(-10, 1)
    ax.legend(fontsize=6)
    ax.set_title('Zone II: PR-LC geometry')

    plt.tight_layout()
    path = os.path.join(FIG_DIR, 'p1_fig5_constraint_summary.pdf')
    plt.savefig(path, dpi=300)
    plt.close()
    print(f"  Saved: {path}")


def fig_rg_schematic():
    """Paper 2 Fig 3: RG flow schematic — conceptual renormalization flow."""
    print("P2 Fig 3: RG flow schematic...")
    fig, ax = plt.subplots(figsize=(5, 4.5))

    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(-0.1, 1.1)

    # Fixed points
    ax.plot(0.15, 0.85, 'o', ms=14, color=MEC_COLOR, mec='white', mew=1.5, zorder=5)
    ax.text(0.15, 0.92, 'Broad-spectrum', ha='center', fontsize=8, color=MEC_COLOR)
    ax.text(0.15, 0.86, 'fixed point', ha='center', fontsize=7, color=MEC_COLOR)

    ax.plot(0.85, 0.15, 'o', ms=14, color='#d95f02', mec='white', mew=1.5, zorder=5)
    ax.text(0.85, 0.05, 'Collapse', ha='center', fontsize=8, color='#d95f02')
    ax.text(0.85, -0.02, 'fixed point', ha='center', fontsize=7, color='#d95f02')

    ax.plot(0.5, 0.5, 'o', ms=10, color='gray', mec='white', mew=1.5, alpha=0.5, zorder=5)
    ax.text(0.5, 0.43, 'Unstable', ha='center', fontsize=7, color='gray', alpha=0.7)

    # RG flow lines
    def flow_arrow(xstart, ystart, xend, yend, color='gray', alpha=0.4):
        ax.annotate('', xy=(xend, yend), xytext=(xstart, ystart),
                    arrowprops=dict(arrowstyle='->', color=color, alpha=alpha, lw=1.5))

    # Flow along separatrix
    for t in np.linspace(0.1, 0.85, 5):
        flow_arrow(t, t, min(t+0.08, 0.88), min(t+0.08, 0.88), alpha=0.3)

    # Flow to collapse
    for start in [(0.7, 0.35), (0.8, 0.2), (0.9, 0.1)]:
        flow_arrow(start[0], start[1], start[0]+0.05, start[1]-0.02, color='#d95f02', alpha=0.4)

    # Flow to broad
    for start in [(0.2, 0.7), (0.3, 0.8), (0.1, 0.9)]:
        flow_arrow(start[0], start[1], start[0]-0.02, start[1]+0.05, color=MEC_COLOR, alpha=0.4)

    # Axis labels
    ax.set_xlabel(r'Relevant operator $\propto \alpha$', fontsize=9)
    ax.set_ylabel(r'Irrelevant operator', fontsize=9)
    ax.set_title('RG flow in observable space', fontsize=11)

    ax.text(0.5, -0.12, r'$d(N) \sim N^{2.2}$: separation under coarse-graining',
            transform=ax.transAxes, ha='center', fontsize=7, fontstyle='italic')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])

    plt.tight_layout()
    path = os.path.join(FIG_DIR, 'p2_fig3_rg_schematic.pdf')
    plt.savefig(path, dpi=300)
    plt.close()
    print(f"  Saved: {path}")


def fig_operator_comparison(mec_recordings, mec_metrics):
    """Paper 2 Fig 4: Precision vs temporal operator comparison."""
    print("P2 Fig 4: Operator comparison...")
    prec_alphas, prec_PRs = [], []
    var_alphas, var_PRs = [], []

    for X in mec_recordings[:8]:
        try:
            P = graphical_lasso_safe(X, alpha=0.1)
            pm = operator_metrics(P)
            prec_alphas.append(pm['alpha'])
            prec_PRs.append(pm['PR'])
        except Exception:
            pass
        try:
            A = ridge_var(X, alpha=1.0)
            vm = operator_metrics(A)
            var_alphas.append(vm['alpha'])
            var_PRs.append(vm['PR'])
        except Exception:
            pass

    if not mec_metrics:
        return

    fig, axes = plt.subplots(1, 2, figsize=(7, 3.5))

    # Panel 1: Bar comparison of alpha
    ax = axes[0]
    labels = ['Correlation', 'Precision\n(GraphLasso)', 'VAR(1)\n(ridge)']
    corr_a = np.mean([m['alpha'] for m in mec_metrics])
    corr_a_std = np.std([m['alpha'] for m in mec_metrics])
    prec_a = np.mean(prec_alphas) if prec_alphas else 0
    prec_a_std = np.std(prec_alphas) if len(prec_alphas) > 1 else 0
    var_a = np.mean(var_alphas) if var_alphas else 0
    var_a_std = np.std(var_alphas) if len(var_alphas) > 1 else 0
    values = [corr_a, prec_a, var_a]
    errs = [corr_a_std, prec_a_std, var_a_std]
    colors = [MEC_COLOR, PRECISION_COLOR, TEMPORAL_COLOR]
    bars = ax.bar(labels, values, yerr=errs, color=colors, alpha=0.75, capsize=3)
    ax.set_ylabel(r'Spectral decay $\alpha$')
    ax.set_title(r'$\alpha$ by operator')
    for bar, val in zip(bars, values):
        if val > 0.001:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(errs)*0.05,
                    f'{val:.3f}', ha='center', fontsize=7)

    # Panel 2: Bar comparison of PR
    ax = axes[1]
    corr_p = np.mean([m['PR'] for m in mec_metrics])
    corr_p_std = np.std([m['PR'] for m in mec_metrics])
    prec_p = np.mean(prec_PRs) if prec_PRs else 0
    prec_p_std = np.std(prec_PRs) if len(prec_PRs) > 1 else 0
    var_p = np.mean(var_PRs) if var_PRs else 0
    var_p_std = np.std(var_PRs) if len(var_PRs) > 1 else 0
    values_p = [corr_p, prec_p, var_p]
    errs_p = [corr_p_std, prec_p_std, var_p_std]
    bars = ax.bar(labels, values_p, yerr=errs_p, color=colors, alpha=0.75, capsize=3)
    ax.set_ylabel('Participation Ratio PR')
    ax.set_title('PR by operator')
    for bar, val in zip(bars, values_p):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(errs_p)*0.05,
                    f'{val:.0f}', ha='center', fontsize=7)

    plt.tight_layout()
    path = os.path.join(FIG_DIR, 'p2_fig4_operator_comparison.pdf')
    plt.savefig(path, dpi=300)
    plt.close()
    print(f"  Saved: {path}")
    print(f"  Correlation: alpha={corr_a:.3f}, PR={corr_p:.1f}")
    print(f"  Precision:   alpha={prec_a:.3f}, PR={prec_p:.1f}")
    print(f"  VAR(1):      alpha={var_a:.3f}, PR={var_p:.1f}")


def fig_universality_positioning(mec_recordings, mec_names):
    """Paper 2 Fig 5: Universality positioning — MEC vs all ensembles."""
    print("P2 Fig 5: Universality positioning...")
    N_avg = int(np.mean([X.shape[1] for X in mec_recordings if X.shape[1] >= 50]))

    # MEC metrics
    mec_a_list, mec_pr_list, mec_ipr_list = [], [], []
    for X in mec_recordings:
        m = correlation_metrics(X)
        mec_a_list.append(m['alpha'])
        mec_pr_list.append(m['PR'])
        mec_ipr_list.append(m['mean_IPR'])
    mec_a = np.mean(mec_a_list)
    mec_pr = np.mean(mec_pr_list)
    mec_ipr = np.mean(mec_ipr_list)

    # Ensembles
    goe = goe_ensemble(N_avg, n_samples=50)
    sparse = sparse_ensemble(N_avg, p=0.05, n_samples=30)
    sparse_01 = sparse_ensemble(N_avg, p=0.10, n_samples=30)
    sparse_02 = sparse_ensemble(N_avg, p=0.20, n_samples=30)

    def distance(mec_m, ens_m):
        da = abs(mec_m['alpha'] - np.mean([m['alpha'] for m in ens_m])) / (np.std([m['alpha'] for m in ens_m]) + 1e-10)
        dp = abs(mec_m['PR'] - np.mean([m['PR'] for m in ens_m])) / (np.std([m['PR'] for m in ens_m]) + 1e-10)
        di = abs(mec_m['mean_IPR'] - np.mean([m['mean_IPR'] for m in ens_m])) / (np.std([m['mean_IPR'] for m in ens_m]) + 1e-10)
        return np.sqrt(da**2 + dp**2 + di**2)

    mec_centroid = {'alpha': mec_a, 'PR': mec_pr, 'mean_IPR': mec_ipr}
    distances = {
        'GOE': distance(mec_centroid, goe),
        'Sparse p=0.05': distance(mec_centroid, sparse),
        'Sparse p=0.10': distance(mec_centroid, sparse_01),
        'Sparse p=0.20': distance(mec_centroid, sparse_02),
    }

    fig, ax = plt.subplots(figsize=(5, 3.5))
    names = list(distances.keys())
    vals = list(distances.values())
    colors_bar = [GOE_COLOR, SPARSE_COLOR, '#a6cee3', '#b2df8a']
    bars = ax.barh(names, vals, color=colors_bar, alpha=0.75, edgecolor='white')
    ax.axvline(1, color='gray', ls='--', alpha=0.5, label=r'$1\sigma$')
    ax.axvline(2, color='gray', ls=':', alpha=0.5, label=r'$2\sigma$')
    ax.set_xlabel('Mahalanobis distance $d$ from MEC')
    ax.set_title('MEC vs random ensembles')
    ax.legend(fontsize=7)
    for bar, val in zip(bars, vals):
        ax.text(val + 0.05, bar.get_y() + bar.get_height()/2,
                f'{val:.2f}$\\sigma$', va='center', fontsize=8)

    plt.tight_layout()
    path = os.path.join(FIG_DIR, 'p2_fig5_universality_positioning.pdf')
    plt.savefig(path, dpi=300)
    plt.close()
    print(f"  Saved: {path}")
    for k, v in distances.items():
        print(f"  {k}: {v:.2f}sigma")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def compute_synthetic_metrics():
    np.random.seed(42)
    results = []
    for label, n_samples, n_dim, n_time in [
        ('collapse', 8, 100, 1000),
        ('transition', 6, 100, 1000),
        ('broad', 5, 200, 1000),
    ]:
        for _ in range(n_samples):
            if label == 'collapse':
                X = np.random.randn(n_time, n_dim) * 0.1
                mode = np.random.randn(n_dim)
                X += np.outer(np.sin(np.linspace(0, 4*np.pi, n_time)) * 5, mode)
            elif label == 'transition':
                X = np.random.randn(n_time, n_dim) * 0.3
                for i in range(5):
                    mode = np.random.randn(n_dim)
                    X += np.outer(np.sin(np.linspace(0, (i+2)*np.pi, n_time)) * 3/(i+1), mode)
            else:
                cov = np.eye(n_dim) * 0.1
                for i in range(n_dim):
                    for j in range(i+1, n_dim):
                        if np.random.rand() < 0.05:
                            cov[i,j] = cov[j,i] = np.random.randn() * 0.3
                X = np.random.multivariate_normal(np.zeros(n_dim), cov, size=n_time)
            m = correlation_metrics(X)
            U, s, Vt = la.svd(X - X.mean(axis=0), full_matrices=False)
            cumvar = np.cumsum(s**2) / np.sum(s**2)
            n_95 = int(np.searchsorted(cumvar, 0.95) + 1)
            X_proj = U[:, :n_95] @ np.diag(s[:n_95]) @ Vt[:n_95, :]
            lc = np.log10(np.sum((X - X_proj)**2) / np.sum(X**2))
            results.append({'alpha': m['alpha'], 'PR': m['PR'], 'LC': lc, 'type': label})
    return [r for r in results if r['type'] == 'collapse'], \
           [r for r in results if r['type'] == 'transition'], \
           [r for r in results if r['type'] == 'broad']


def main():
    print("=" * 60)
    print("Canonical Figure Generation")
    print("=" * 60)

    recordings, names = load_mec()
    print(f"\nLoaded {len(recordings)} recordings\n")

    # MEC metrics
    mec_metrics = []
    for X, name in zip(recordings, names):
        m = correlation_metrics(X)
        U, s, Vt = la.svd(X - X.mean(axis=0), full_matrices=False)
        cumvar = np.cumsum(s**2) / np.sum(s**2)
        n_95 = int(np.searchsorted(cumvar, 0.95) + 1)
        X_proj = U[:, :n_95] @ np.diag(s[:n_95]) @ Vt[:n_95, :]
        lc = np.log10(np.sum((X - X_proj)**2) / np.sum(X**2))
        mec_metrics.append({'alpha': m['alpha'], 'PR': m['PR'], 'LC': lc, 'mean_IPR': m['mean_IPR']})

    # Ensembles for comparison
    N_avg = max(50, int(np.mean([X.shape[1] for X in recordings])))
    goe_metrics = goe_ensemble(N_avg, n_samples=50)
    sparse_metrics = sparse_ensemble(N_avg, p=0.05, n_samples=30)
    print(f"Ensembles at N={N_avg}")

    # Synthetic metrics
    syn_collapse, syn_transition, syn_broad = compute_synthetic_metrics()

    # Generate figures
    fig_ensemble_comparison(mec_metrics, goe_metrics, sparse_metrics)
    fig_precision_spectrum(recordings)
    fig_constraint_summary(mec_metrics, syn_collapse, syn_transition, syn_broad)
    fig_rg_schematic()
    fig_operator_comparison(recordings, mec_metrics)
    fig_universality_positioning(recordings, names)

    print(f"\nAll figures saved to {FIG_DIR}/")

if __name__ == '__main__':
    main()
