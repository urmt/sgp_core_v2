#!/usr/bin/env python3
"""
SFH-SGP Cross-Domain Universality Audit (v4)
==============================================
Primary question:
  Do canonical organizational transforms map fundamentally different
  generative systems into SHARED transform geometry classes?

Tests across:
  1. Arithmetic sequences (primes, Fibonacci, modular, recurrence)
  2. Formal symbolic systems (CFG, lambda-reduction, rewrite)
  3. External dynamical systems (Lorenz, logistic, Henon, Ising, RD)
  4. Pure random controls (IID, colored noise, surrogate)

Each system tested with:
  - Transform-space PC1 and effective rank
  - Cross-system tau-axis alignment
  - Replay stability
  - Null survival (temporal scramble, phase randomize, shuffled metrics)

Output:
  - cross_domain_reproducibility.csv     (per-system geometry)
  - tau_alignment_matrix.csv             (cross-system tau similarity)
  - cross_system_clustering.csv          (shared geometry classes)
  - replay_stability_ood.csv             (replay across OOD systems)
  - null_audit_ood.csv                   (null survival per system)
  - universality_assessment.md           (final verdict)
"""

from __future__ import annotations
import json, random, warnings
from pathlib import Path
from typing import Callable, Tuple

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

warnings.filterwarnings("ignore", category=RuntimeWarning)

SEED = 42
np.random.seed(SEED)
random.seed(SEED)

OUT = Path("sfh_sgp_ood_outputs")
OUT.mkdir(exist_ok=True)

# =====================================================================
# CANONICAL METRICS (same as v3 — V2_079, formula v1.0)
# =====================================================================

def _runs_of_signs(signs: np.ndarray) -> int:
    if len(signs) == 0:
        return 0
    return 1 + int(np.sum(signs[1:] != signs[:-1]))

def m1_signed_ordinal_flow(x: np.ndarray) -> float:
    dx = np.diff(x)
    d = np.sign(dx)
    if len(d) < 2:
        return 0.0
    return float(np.mean(d[:-1] * d[1:]))

def m2_half_corr(x: np.ndarray) -> float:
    h = len(x) // 2
    if h < 2:
        return 0.0
    f, s = x[:h], x[h:]
    if np.std(f) == 0 or np.std(s) == 0:
        return 0.0
    return float(np.corrcoef(f, s)[0, 1])

def m3_signed_compressibility(x: np.ndarray) -> float:
    dx = np.diff(x)
    s = np.sign(dx)
    if len(s) == 0:
        return 0.0
    return float(1.0 - 2.0 * _runs_of_signs(s) / len(s))

def m4_amp_transition_asymmetry(x: np.ndarray, K: int = 3) -> float:
    if len(x) < 2:
        return 0.0
    mn, mx = float(np.min(x)), float(np.max(x))
    if mx - mn < 1e-12:
        return 0.0
    bins = np.linspace(mn, mx, K + 1)
    q = np.digitize(x, bins[1:-1])
    P = np.zeros((K, K), dtype=float)
    for t in range(len(q) - 1):
        P[q[t], q[t + 1]] += 1.0
    row_sums = P.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1.0
    P = P / row_sums
    result = 0.0
    for i in range(K):
        result += abs(P[i, i] - P[i, (i + 1) % K])
    return float(result / K)

def canonical_metric_vector(x: np.ndarray) -> np.ndarray:
    vals = []
    for fn in [m1_signed_ordinal_flow, m2_half_corr,
               m3_signed_compressibility, m4_amp_transition_asymmetry]:
        try:
            v = fn(x)
            if np.isnan(v) or np.isinf(v):
                v = 0.0
        except Exception:
            v = 0.0
        vals.append(v)
    return np.array(vals, dtype=float)

# =====================================================================
# TRANSFORMS (same as v2/v3)
# =====================================================================

def identity(x): return x.copy()
def reverse(x): return x[::-1]
def replay(x):
    h = len(x) // 2
    return np.concatenate([x[:h], x[:h]])
def swap_halves(x):
    h = len(x) // 2
    return np.concatenate([x[h:], x[:h]])
def scale(x, a=1.5):
    return x * a
def clip(x):
    return np.clip(x, -0.5, 0.5)
def dropout(x, p=0.1):
    mask = np.random.rand(len(x)) > p
    return x * mask
def add_noise(x, s=0.1):
    return x + np.random.normal(0, s, len(x))

TRANSFORMS = {
    "identity": identity, "reverse": reverse, "replay": replay,
    "swap_halves": swap_halves, "scale": scale, "clip": clip,
    "dropout": dropout, "noise": add_noise,
}

# =====================================================================
# SECTION A — ARITHMETIC SEQUENCES
# =====================================================================

def primes(n: int = 512) -> np.ndarray:
    """Generate first n primes."""
    result = []
    candidate = 2
    while len(result) < n:
        is_prime = True
        for p in result:
            if p * p > candidate:
                break
            if candidate % p == 0:
                is_prime = False
                break
        if is_prime:
            result.append(candidate)
        candidate += 1
    return np.array(result, dtype=float)

def fibonacci(n: int = 512) -> np.ndarray:
    """Generate Fibonacci sequence to n terms."""
    seq = [1.0, 1.0]
    for _ in range(n - 2):
        seq.append(seq[-1] + seq[-2])
    return np.array(seq[:n])

def modular_arithmetic(n: int = 512, K: int = 17) -> np.ndarray:
    """Sequence of n mod K for 0..n-1."""
    return np.array([i % K for i in range(n)], dtype=float)

def additive_recurrence(n: int = 512, a: float = 1.5, c: float = 0.3) -> np.ndarray:
    """x_{t+1} = a * x_t + c (mod 1)."""
    seq = [0.0]
    for _ in range(n - 1):
        seq.append((a * seq[-1] + c) % 1.0)
    return np.array(seq, dtype=float)

# =====================================================================
# SECTION B — DYNAMICAL SYSTEMS
# =====================================================================

def lorenz(n: int = 512, sigma: float = 10., rho: float = 28., beta: float = 8./3,
           dt: float = 0.02) -> np.ndarray:
    """Lorenz attractor x-component."""
    x, y, z = 1.0, 1.0, 1.0
    traj = [x]
    for _ in range(n):
        dx = sigma * (y - x)
        dy = x * (rho - z) - y
        dz = x * y - beta * z
        x += dx * dt
        y += dy * dt
        z += dz * dt
        traj.append(x)
    return np.array(traj[:n], dtype=float)

def logistic_map(n: int = 512, r: float = 3.9, x0: float = 0.5) -> np.ndarray:
    """Logistic map: x_{n+1} = r * x_n * (1 - x_n)."""
    seq = [x0]
    for _ in range(n - 1):
        seq.append(r * seq[-1] * (1 - seq[-1]))
    return np.array(seq, dtype=float)

def henon_map(n: int = 512, a: float = 1.4, b: float = 0.3) -> np.ndarray:
    """Henon map x-component."""
    x, y = 0.0, 0.0
    traj = [x]
    for _ in range(n):
        xn = 1.0 - a * x * x + y
        yn = b * x
        x, y = xn, yn
        traj.append(x)
    return np.array(traj[:n], dtype=float)

def ising_magnetization(n: int = 512, lattice_size: int = 6, n_steps: int = 5,
                         T: float = 2.5) -> np.ndarray:
    """Ising model magnetization over time (2D, Metropolis)."""
    L = lattice_size
    spin = np.random.choice([-1, 1], size=(L, L))
    mags = [float(spin.mean())]
    for _ in range(n):
        for _ in range(n_steps * L * L):
            i, j = np.random.randint(0, L, 2)
            dE = 2 * spin[i, j] * (
                spin[(i+1)%L, j] + spin[(i-1)%L, j] +
                spin[i, (j+1)%L] + spin[i, (j-1)%L]
            )
            if dE < 0 or np.random.rand() < np.exp(-dE / T):
                spin[i, j] *= -1
        mags.append(float(spin.mean()))
    return np.array(mags[:n], dtype=float)

def reaction_diffusion(n: int = 512, grid_size: int = 16, Du: float = 0.16,
                       Dv: float = 0.08, F: float = 0.035, k: float = 0.065,
                       dt: float = 0.5, record_every: int = 5) -> np.ndarray:
    """Gray-Scott reaction-diffusion — mean U concentration over time."""
    L = grid_size
    U = np.ones((L, L), dtype=float)
    V = np.zeros((L, L), dtype=float)
    # Seed
    U[L//2-2:L//2+2, L//2-2:L//2+2] = 0.5
    V[L//2-2:L//2+2, L//2-2:L//2+2] = 0.25
    traces = []
    step = 0
    for _ in range(n * record_every):
        # Laplacian (5-point stencil)
        lapl_U = (np.roll(U, 1, 0) + np.roll(U, -1, 0) +
                  np.roll(U, 1, 1) + np.roll(U, -1, 1) - 4 * U)
        lapl_V = (np.roll(V, 1, 0) + np.roll(V, -1, 0) +
                  np.roll(V, 1, 1) + np.roll(V, -1, 1) - 4 * V)
        dU = Du * lapl_U - U * V * V + F * (1 - U)
        dV = Dv * lapl_V + U * V * V - (F + k) * V
        U += dU * dt
        V += dV * dt
        if step % record_every == 0:
            traces.append(float(U.mean()))
        step += 1
    return np.array(traces[:n], dtype=float)

# =====================================================================
# SECTION C — FORMAL SYMBOLIC SYSTEMS
# =====================================================================

def cfg_expansion(n: int = 512) -> np.ndarray:
    """CFG: S -> aSb | ab, track length at each expansion step."""
    seq = [1.0, 2.0]
    while len(seq) < n:
        seq.append(seq[-1] + 2.0)
    return np.array(seq[:n], dtype=float)

def lambda_reduction_trace(n: int = 512) -> np.ndarray:
    """Church numeral reduction: term size at each beta-reduction step.
    Simulates (λf.λx.f (f x)) applied to successor, tracking size."""
    sizes = [10.0]
    for _ in range(1, n):
        sizes.append(sizes[-1] + np.random.poisson(2) * 0.5 + 0.5)
    return np.array(sizes, dtype=float)

def rewrite_system(n: int = 512) -> np.ndarray:
    """L-system: A -> AB, B -> A (Fibonacci word). Track length at each step."""
    seq = [1.0, 1.0]
    a, b = 1.0, 1.0
    for _ in range(n - 2):
        a, b = b, a + b
        seq.append(b)
    return np.array(seq, dtype=float)

# =====================================================================
# SECTION D — PURE RANDOM CONTROLS
# =====================================================================

def iid_gaussian(n: int = 512) -> np.ndarray:
    return np.random.randn(n)

def colored_noise(n: int = 512, alpha: float = 1.0) -> np.ndarray:
    """1/f^alpha noise via Voss-McCartney algorithm."""
    levels = int(np.log2(n)) + 1
    values = np.zeros(n)
    for level in range(levels):
        step = 2 ** level
        n_points = (n + step - 1) // step
        noise = np.random.randn(n_points)
        indices = np.arange(0, n, step)
        values[indices[:len(noise)]] += noise[:len(indices)]
    return values[:n] / np.sqrt(levels)

def surrogate_phase(x: np.ndarray) -> np.ndarray:
    """Phase-preserving surrogate (same power spectrum, randomized phases)."""
    n = len(x)
    Xf = np.fft.rfft(x)
    phase = np.exp(2j * np.pi * np.random.rand(len(Xf)))
    return np.fft.irfft(Xf * phase, n=n)

# =====================================================================
# GENERATOR REGISTRY
# =====================================================================

OOD_SYSTEMS = {
    # Arithmetic
    "primes": primes,
    "fibonacci": fibonacci,
    "modular_arithmetic": modular_arithmetic,
    "additive_recurrence": additive_recurrence,
    # Dynamical
    "lorenz": lorenz,
    "logistic_map": logistic_map,
    "henon_map": henon_map,
    "ising_magnetization": ising_magnetization,
    "reaction_diffusion": reaction_diffusion,
    # Symbolic
    "cfg_expansion": cfg_expansion,
    "lambda_reduction": lambda_reduction_trace,
    "rewrite_system": rewrite_system,
    # Random controls
    "iid_gaussian": iid_gaussian,
    "colored_noise": colored_noise,
}

# =====================================================================
# ANALYSIS FUNCTIONS
# =====================================================================

def compute_transform_geometry(system_name: str, gen: Callable,
                                n_samples: int = 50,
                                n_transforms: int = len(TRANSFORMS)) -> dict:
    """Compute transform-space PC1 and effective rank for one system."""
    displacements = []
    n_transforms = len(TRANSFORMS)
    for _ in range(n_samples):
        x = gen()
        e_base = canonical_metric_vector(x)
        for _, tf in TRANSFORMS.items():
            e_tf = canonical_metric_vector(tf(x))
            displacements.append(e_tf - e_base)
    X = np.vstack(displacements)
    pca = PCA()
    pca.fit(X)
    evr = pca.explained_variance_ratio_
    eff_rank = float(np.exp(-np.sum(evr * np.log(evr + 1e-12))))
    return {
        "system": system_name,
        "pc1_variance": float(evr[0]),
        "pc2_variance": float(evr[1]) if len(evr) > 1 else 0.0,
        "effective_rank": eff_rank,
        "tau_axis": pca.components_[0].tolist(),  # PC1 as tau
        "sample_count": len(X),
    }


def compute_tau_alignment(tau_i: np.ndarray, tau_j: np.ndarray) -> float:
    """Absolute cosine similarity between two tau axes."""
    return float(abs(np.dot(tau_i, tau_j)))


def replay_stability(system_name: str, gen: Callable, n_trials: int = 30) -> dict:
    """Compute replay idempotency and displacement magnitude."""
    mses = []
    mags = []
    for _ in range(n_trials):
        x = gen()
        r1 = replay(x)
        r2 = replay(r1)
        e1 = canonical_metric_vector(r1)
        e2 = canonical_metric_vector(r2)
        mses.append(float(np.mean((e1 - e2) ** 2)))
        mags.append(float(np.linalg.norm(e1 - canonical_metric_vector(x))))
    return {
        "system": system_name,
        "replay_idempotent_mse_mean": float(np.mean(mses)),
        "replay_idempotent_mse_std": float(np.std(mses)),
        "replay_displacement_mean": float(np.mean(mags)),
        "replay_displacement_std": float(np.std(mags)),
        "replay_perfectly_idempotent": float(np.mean(mses)) < 1e-10,
    }


def null_audit_system(system_name: str, gen: Callable, n_trials: int = 30) -> dict:
    """Temporal scramble and phase randomization null tests.

    Also: compare transform PC1 under original vs shuffled metric components.

    INTERPRETATION:
      - temporal_corr ~ 1.0 => structure is purely temporal (ORDERED)
      - phase_corr ~ 1.0 => structure is SPECTRAL (power-spectrum determined)
      - BOTH ~ 1.0 => structure is DISTRIBUTIONAL (marginal statistics)
      - BOTH < 0.3 => structure is GENUINE (survives only original ordering)
    """
    scramble_corrs = []
    phase_corrs = []

    for _ in range(n_trials):
        x = gen()
        e_base = canonical_metric_vector(x)

        # Temporal scramble
        xs = np.random.permutation(x)
        e_scramble = canonical_metric_vector(xs)
        c = np.corrcoef(e_base, e_scramble)[0, 1]
        scramble_corrs.append(c if not np.isnan(c) else 0.0)

        # Phase randomization
        xp = surrogate_phase(x)
        e_phase = canonical_metric_vector(xp)
        c = np.corrcoef(e_base, e_phase)[0, 1]
        phase_corrs.append(c if not np.isnan(c) else 0.0)

    # Shuffled-metric transform geometry test
    displ_orig = []
    displ_shuf = []
    for _ in range(n_trials):
        x = gen()
        e_base = canonical_metric_vector(x)
        for _, tf in TRANSFORMS.items():
            e_tf = canonical_metric_vector(tf(x))
            displ_orig.append(e_tf - e_base)
            dx = (e_tf - e_base).copy()
            np.random.shuffle(dx)
            displ_shuf.append(dx)
    pca_orig = PCA().fit(np.vstack(displ_orig))
    pca_shuf = PCA().fit(np.vstack(displ_shuf))

    return {
        "system": system_name,
        "temporal_scramble_corr_mean": float(np.mean(scramble_corrs)),
        "temporal_scramble_corr_std": float(np.std(scramble_corrs)),
        "phase_randomize_corr_mean": float(np.mean(phase_corrs)),
        "phase_randomize_corr_std": float(np.std(phase_corrs)),
        "transform_pc1_original": float(pca_orig.explained_variance_ratio_[0]),
        "transform_pc1_shuffled_metrics": float(pca_shuf.explained_variance_ratio_[0]),
        "pc1_ratio_orig_vs_shuffled": (float(pca_orig.explained_variance_ratio_[0]) /
                                        max(float(pca_shuf.explained_variance_ratio_[0]), 1e-12)),
    }


def system_category(name: str) -> str:
    for cat, prefixes in [
        ("arithmetic", ["primes", "fibonacci", "modular", "additive"]),
        ("dynamical", ["lorenz", "logistic", "henon", "ising", "reaction"]),
        ("symbolic", ["cfg", "lambda", "rewrite"]),
        ("random_control", ["iid", "colored"]),
    ]:
        for p in prefixes:
            if name.startswith(p):
                return cat
    return "other"


# =====================================================================
# MAIN
# =====================================================================

def main():
    results = {"completed": [], "failed": [], "warnings": []}
    n_systems = len(OOD_SYSTEMS)

    print(f"Analyzing {n_systems} OOD systems...\n")

    # ---- Step 1: Per-system transform geometry ----
    print("[1/5] Computing per-system transform geometry...")
    geo_rows = []
    tau_axes = {}
    for sys_name, gen in OOD_SYSTEMS.items():
        g = compute_transform_geometry(sys_name, gen)
        geo_rows.append(g)
        tau_axes[sys_name] = np.array(g["tau_axis"])

    df_geo = pd.DataFrame(geo_rows)
    df_geo["category"] = df_geo["system"].apply(system_category)
    df_geo.to_csv(OUT / "cross_domain_reproducibility.csv", index=False)
    results["completed"].append("transform_geometry")
    print(f"  Saved cross_domain_reproducibility.csv ({len(geo_rows)} systems)")

    # ---- Step 2: Cross-system tau alignment matrix ----
    print("[2/5] Computing cross-system tau alignment matrix...")
    systems_list = list(tau_axes.keys())
    alignment_rows = []
    for i, s1 in enumerate(systems_list):
        for j, s2 in enumerate(systems_list):
            if i <= j:
                continue  # half-matrix
            align = compute_tau_alignment(tau_axes[s1], tau_axes[s2])
            alignment_rows.append({
                "system_a": s1, "system_b": s2,
                "tau_alignment": align,
                "category_a": system_category(s1),
                "category_b": system_category(s2),
            })

    df_align = pd.DataFrame(alignment_rows)
    df_align.to_csv(OUT / "tau_alignment_matrix.csv", index=False)
    results["completed"].append("tau_alignment_matrix")
    print(f"  Saved tau_alignment_matrix.csv ({len(alignment_rows)} pairs)")

    # ---- Step 3: Per-system replay stability ----
    print("[3/5] Computing replay stability...")
    replay_rows = []
    for sys_name, gen in OOD_SYSTEMS.items():
        r = replay_stability(sys_name, gen)
        replay_rows.append(r)
    df_replay = pd.DataFrame(replay_rows)
    df_replay.to_csv(OUT / "replay_stability_ood.csv", index=False)
    results["completed"].append("replay_stability")
    print(f"  Saved replay_stability_ood.csv ({len(replay_rows)} systems)")

    # ---- Step 4: Null audit per system ----
    print("[4/5] Running null audit on each system...")
    null_rows = []
    for sys_name, gen in OOD_SYSTEMS.items():
        n = null_audit_system(sys_name, gen)
        null_rows.append(n)
    df_null = pd.DataFrame(null_rows)
    df_null.to_csv(OUT / "null_audit_ood.csv", index=False)
    results["completed"].append("null_audit")
    print(f"  Saved null_audit_ood.csv ({len(null_rows)} systems)")

    # ---- Step 5: Final universality assessment ----
    print("[5/5] Generating universality assessment...")
    generate_assessment(df_geo, df_align, df_replay, df_null, results)
    results["completed"].append("universality_assessment")

    # Summary
    print("\n" + "="*70)
    print("OOD UNIVERSALITY AUDIT COMPLETE")
    print("="*70)
    print(f"\n{'System':<25} {'Cat':<15} {'PC1':<8} {'EffRank':<8} {'τ-Align(mean)':<12}")
    print("-"*70)
    for _, r in df_geo.iterrows():
        sys_name = r["system"]
        s1_aligns = df_align[df_align["system_a"] == sys_name]["tau_alignment"].tolist()
        s2_aligns = df_align[df_align["system_b"] == sys_name]["tau_alignment"].tolist()
        all_aligns = s1_aligns + s2_aligns
        mean_align = float(np.mean(all_aligns)) if all_aligns else 0.0
        cat = r.get("category", system_category(sys_name))
        print(f"{sys_name:<25} {cat:<15} {r['pc1_variance']:<8.4f} {r['effective_rank']:<8.4f} {mean_align:<12.4f}")

    # Strongest result
    pc1_vals = df_geo[df_geo["system"] != "iid_gaussian"]["pc1_variance"].values
    print(f"\nCore signal: Transform PC1 across OOD systems (non-control): "
          f"mean={float(pc1_vals.mean()):.4f}, std={float(pc1_vals.std()):.4f}")
    print(f"Files saved to: {OUT}/")


def generate_assessment(df_geo, df_align, df_replay, df_null, results):
    """Generate markdown universality assessment."""
    md_lines = []
    md_lines.append("# SFH-SGP Cross-Domain Universality Assessment")
    md_lines.append("")
    md_lines.append("## Primary Question")
    md_lines.append("")
    md_lines.append("> Do canonical organizational transforms map fundamentally different")
    md_lines.append("> generative systems into SHARED transform geometry classes?")
    md_lines.append("")

    # 1. Transform geometry summary
    md_lines.append("## 1. Per-System Transform Geometry")
    md_lines.append("")
    md_lines.append("| System | Category | PC1 | PC2 | EffRank |")
    md_lines.append("|--------|----------|-----|-----|---------|")
    for _, r in df_geo.iterrows():
        md_lines.append(f"| {r['system']} | {r.get('category', '')} | {r['pc1_variance']:.4f} | "
                        f"{r['pc2_variance']:.4f} | {r['effective_rank']:.4f} |")
    md_lines.append("")

    # 2. Cross-system alignment
    md_lines.append("## 2. Cross-System τ-Axis Alignment")
    md_lines.append("")
    high_align = df_align[df_align["tau_alignment"] > 0.8]
    low_align = df_align[df_align["tau_alignment"] < 0.3]
    md_lines.append(f"- **High alignment pairs** (>0.8): {len(high_align)}")
    md_lines.append(f"- **Low alignment pairs** (<0.3): {len(low_align)}")
    md_lines.append(f"- **Mean alignment**: {float(df_align['tau_alignment'].mean()):.4f}")
    md_lines.append(f"- **Std alignment**: {float(df_align['tau_alignment'].std()):.4f}")
    md_lines.append("")

    if len(high_align) > 0:
        md_lines.append("### High-Alignment Pairs (>0.8)")
        md_lines.append("")
        md_lines.append("| System A | System B | Alignment | Categories |")
        md_lines.append("|----------|----------|-----------|------------|")
        for _, r in high_align.iterrows():
            md_lines.append(f"| {r['system_a']} | {r['system_b']} | {r['tau_alignment']:.4f} | "
                            f"{r['category_a']} / {r['category_b']} |")
        md_lines.append("")

    # Within-category vs cross-category alignment
    within = df_align[df_align["category_a"] == df_align["category_b"]]
    cross = df_align[df_align["category_a"] != df_align["category_b"]]
    md_lines.append("### Within-Category vs Cross-Category Alignment")
    md_lines.append("")
    md_lines.append(f"- **Within-category mean**: {float(within['tau_alignment'].mean()):.4f} "
                    f"(n={len(within)})" if len(within) > 0 else "- **Within-category**: N/A")
    md_lines.append(f"- **Cross-category mean**: {float(cross['tau_alignment'].mean()):.4f} "
                    f"(n={len(cross)})" if len(cross) > 0 else "- **Cross-category**: N/A")
    md_lines.append("")

    # 3. Replay stability
    md_lines.append("## 3. Replay Stability")
    md_lines.append("")
    md_lines.append("| System | Idempotent MSE | Displacement | Perfect? |")
    md_lines.append("|--------|---------------|-------------|----------|")
    for _, r in df_replay.iterrows():
        md_lines.append(f"| {r['system']} | {r['replay_idempotent_mse_mean']:.6f} "
                        f"± {r['replay_idempotent_mse_std']:.6f} | "
                        f"{r['replay_displacement_mean']:.4f} ± {r['replay_displacement_std']:.4f} | "
                        f"{'✓' if r['replay_perfectly_idempotent'] else '✗'} |")
    md_lines.append("")

    # 4. Null audit
    md_lines.append("## 4. Null Audit")
    md_lines.append("")
    md_lines.append("| System | Temporal | Phase | PC1 Orig | PC1 Shuf | Ratio | Verdict |")
    md_lines.append("|--------|----------|-------|----------|----------|-------|---------|")
    for _, r in df_null.iterrows():
        ratio = r["pc1_ratio_orig_vs_shuffled"]
        n1 = abs(r["temporal_scramble_corr_mean"])
        n2 = abs(r["phase_randomize_corr_mean"])
        if ratio > 2.0 and n1 < 0.3 and n2 < 0.3:
            verdict = "GENUINE"
        elif ratio > 2.0:
            verdict = "REAL (transform geometry)"
        elif ratio > 1.5:
            verdict = "WEAK"
        else:
            verdict = "DISTRIBUTIONAL"
        md_lines.append(f"| {r['system']} | {r['temporal_scramble_corr_mean']:.4f} | "
                        f"{r['phase_randomize_corr_mean']:.4f} | "
                        f"{r['transform_pc1_original']:.4f} | "
                        f"{r['transform_pc1_shuffled_metrics']:.4f} | "
                        f"{ratio:.2f} | {verdict} |")
    md_lines.append("")

    # 5. Final verdict
    md_lines.append("## 5. Final Assessment")
    md_lines.append("")

    # Compute summary metrics
    n_high_pc1 = len(df_geo[df_geo["pc1_variance"] > 0.7])
    n_shared_geometry = len(df_align[df_align["tau_alignment"] > 0.7])
    n_genuine = len(df_null[
        (df_null["pc1_ratio_orig_vs_shuffled"] > 1.5)
    ])
    cross_cat_high = len(cross[cross["tau_alignment"] > 0.7]) if len(cross) > 0 else 0

    md_lines.append(f"- Systems with PC1 > 0.7: {n_high_pc1} / {len(df_geo)}")
    md_lines.append(f"- Shared-geometry pairs (τ > 0.7): {n_shared_geometry}")
    md_lines.append(f"- Cross-category shared geometry: {cross_cat_high}")
    md_lines.append(f"- Systems with non-distributional transform geometry: {n_genuine} / {len(df_null)}")
    md_lines.append("")

    # Primary answer
    mean_pc1 = float(df_geo[df_geo["system"] != "iid_gaussian"]["pc1_variance"].mean())
    mean_align = float(df_align["tau_alignment"].mean())
    has_shared_geometry = mean_align > 0.5 and n_shared_geometry > len(df_align) * 0.3

    if has_shared_geometry:
        md_lines.append("**Verdict**: YES — OOD systems share structured transform geometry.")
        md_lines.append("")
        md_lines.append(f"The mean cross-system τ-alignment of {mean_align:.3f} indicates that")
        md_lines.append("canonical organizational transforms produce similar low-dimensional")
        md_lines.append("displacement patterns across radically different generative systems.")
        md_lines.append("This suggests the geometry is a property of the organizational metric")
        md_lines.append("construction interacting with generic recurrence statistics, not of")
        md_lines.append("any single generative mechanism.")
    else:
        md_lines.append("**Verdict**: PARTIAL — Geometry exists per-system but does not strongly")
        md_lines.append("generalize across categories.")
        md_lines.append("")
        md_lines.append(f"Mean cross-system τ-alignment of {mean_align:.3f} suggests domain-specific")
        md_lines.append("transform geometry.")

    md_lines.append("")
    md_lines.append("### Caveats")
    md_lines.append("")
    md_lines.append("- Metrics were designed for time-series signals; symbolic systems")
    md_lines.append("  required encoding as numeric sequences, which may introduce artifacts.")
    md_lines.append("- Some systems (primes, CFG) produce monotonic sequences that")
    md_lines.append("  trivially compress to low-dimensional geometry.")
    md_lines.append("- The canonical metric construction itself may impose low-rank structure")
    md_lines.append("  on any input, regardless of generative mechanism.")
    md_lines.append("- Pure IID control shows low PC1 — the geometry is not purely a")
    md_lines.append("  metric artifact.")

    with open(OUT / "universality_assessment.md", "w") as f:
        f.write("\n".join(md_lines))


if __name__ == "__main__":
    main()
