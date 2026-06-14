#!/usr/bin/env python3
"""First empirical benchmark report.

Compares C-metric against 4 competitors across 6 synthetic systems.
Produces numbers, tables, error bars, and failure analysis.
"""

import json
import sys
import time
import numpy as np

sys.path.insert(0, ".")
from metrics import *
from synthetic.generators import *
from adapters.ecosystem import EcosystemAdapter
from adapters.granular import GranularAdapter

np.random.seed(42)


def benchmark_system(name: str, X: np.ndarray) -> dict:
    print(f"  {name}...", end=" ", flush=True)
    t0 = time.time()

    n_comp, T = X.shape
    row = {"n_components": n_comp, "n_timepoints": T}

    # 1. C-metric (Gaussian) with 95% CI
    C, Cl, Cu = compute_C_ci(X, estimator="gaussian", n_bootstrap=100)
    row["C"] = {"mean": C, "ci_lo": Cl, "ci_hi": Cu}

    # 2. Predictive information
    Ip, Ipl, Ipu = compute_predictive_information_ci(X, tau=1, n_bootstrap=50)
    row["predictive_information"] = {"mean": Ip, "ci_lo": Ipl, "ci_hi": Ipu}

    # 3. Statistical complexity
    Cs, Csl, Csu = compute_statistical_complexity_ci(X, tau=1, n_bootstrap=50)
    row["statistical_complexity"] = {"mean": Cs, "ci_lo": Csl, "ci_hi": Csu}

    # 4. Multiscale entropy (scales 1, 2, 5, 10)
    mse = compute_mse(X, scales=[1, 2, 5, 10])
    row["mse"] = mse

    # 5. Transfer entropy summary
    te = compute_transfer_entropy_summary(X, tau=1)
    row["transfer_entropy"] = {
        "mean": te["mean"],
        "max": te["max"],
        "edges": te["num_directed_edges"],
    }

    elapsed = time.time() - t0
    row["elapsed_seconds"] = round(elapsed, 1)
    print(f"done ({elapsed:.1f}s)")
    return row


def print_table(results: dict):
    """Print a clean comparison table."""
    systems = list(results.keys())
    metrics = ["C", "predictive_information", "statistical_complexity"]

    print("\n" + "=" * 90)
    print("  EMPIRICAL BENCHMARK REPORT — SYNTHETIC + PILOT")
    print("=" * 90)

    # Section 1: Point estimates
    print(f"\n  {'System':25s} {'C':>10s} {'I_pred':>10s} {'C_sigma':>10s} {'TE_mean':>10s} {'MSE_s1':>10s}")
    print("  " + "-" * 75)
    for name in systems:
        r = results[name]
        C = r["C"]["mean"]
        Ip = r["predictive_information"]["mean"]
        Cs = r["statistical_complexity"]["mean"]
        TE = r["transfer_entropy"]["mean"]
        mse1 = r["mse"].get(1, 0)
        print(f"  {name:25s} {C:>10.4f} {Ip:>10.4f} {Cs:>10.4f} {TE:>10.4f} {mse1:>10.4f}")

    # Section 2: Confidence intervals
    print(f"\n  {'System':25s} {'C [95% CI]':>30s} {'I_pred [95% CI]':>30s}")
    print("  " + "-" * 85)
    for name in systems:
        r = results[name]
        C = r["C"]
        Ip = r["predictive_information"]
        print(f"  {name:25s} [{C['ci_lo']:>.4f}, {C['ci_hi']:>.4f}]    [{Ip['ci_lo']:>.4f}, {Ip['ci_hi']:>.4f}]")

    # Section 3: Monotonicity
    print("\n  Monotonicity (C ordering):")
    order = sorted(systems, key=lambda s: results[s]["C"]["mean"], reverse=True)
    vals = [results[s]["C"]["mean"] for s in order]
    chain = " > ".join([f"{s}({v:.3f})" for s, v in zip(order, vals)])
    print(f"    {chain}")

    # Check: all structured systems have C > independent
    # and fully_coupled has highest C
    try:
        s1_c = results.get("S1_independent", {}).get("C", {}).get("mean", 1)
        s2_c = results.get("S2_fully_coupled", {}).get("C", {}).get("mean", 0)
        structured = ["S3_coupled_markov", "S4_modular", "S5_sandpile", "S6_hierarchical"]
        all_gt_s1 = all(results[s]["C"]["mean"] > s1_c * 2 for s in structured)
        s2_highest = s2_c > max([results[s]["C"]["mean"] for s in structured], default=0)
        print(f"    All structured > independent: {'PASS' if all_gt_s1 else 'FAIL'}")
        print(f"    Fully coupled has highest C:  {'PASS' if s2_highest else 'FAIL'}")
    except Exception as e:
        pass

    # Section 4: Failures
    print(f"\n  Failures:")
    failures = []
    if abs(results.get("S1_independent", {}).get("C", {}).get("mean", 0)) > 0.05:
        failures.append("S1: |C| > 0.05 (should be ~0)")
    if results.get("S2_fully_coupled", {}).get("C", {}).get("mean", 0) < 0.5:
        failures.append("S2: C < 0.5 (should be ~1)")
    for s in ["S3_coupled_markov", "S4_modular", "S5_sandpile", "S6_hierarchical"]:
        if s in results:
            C = results[s]["C"]["mean"]
            if C < 0.01:
                failures.append(f"{s}: C < 0.01 (should be > 0.01)")
    if failures:
        for f in failures:
            print(f"    FAIL: {f}")
    else:
        print("    None — all systems within expected ranges")

    print("=" * 90)


if __name__ == "__main__":
    t_total = time.time()

    _Xsp = critical(system="sandpile", seed=42)
    _idx = np.random.RandomState(42).choice(_Xsp.shape[0], 15, replace=False)
    systems = {
        "S1_independent": independent(n_components=15, n_timepoints=500),
        "S2_fully_coupled": fully_coupled(n_components=10, n_timepoints=500),
        "S3_coupled_markov": coupled_markov(n_components=8, n_timepoints=1500, coupling=0.22),
        "S4_modular": modular(n_per_module=4, n_modules=3, n_timepoints=1500, within=0.4, between=0.05),
        "S5_sandpile": _Xsp[_idx, :],
        "S6_hierarchical": hierarchical(base_n=8, n_levels=3, n_timepoints=1500, micro_coupling=0.3),
        "P1_forest_succession": EcosystemAdapter().load()[0],
        "P2_granular_relaxation": GranularAdapter().load()[0],
    }

    results = {}
    for name, X in systems.items():
        results[name] = benchmark_system(name, X)

    print_table(results)

    total_time = time.time() - t_total
    print(f"\n  Total benchmark time: {total_time:.1f}s")

    # Save
    output = "results/benchmark_v1.json"
    with open(output, "w") as f:
        json.dump(results, f, indent=2)
    print(f"  Results saved to {output}")
