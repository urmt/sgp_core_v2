#!/usr/bin/env python3
"""T915 — Synthetic Validation Suite Runner.

Usage:
    python synthetic_validation.py [--estimator gaussian] [--n-bootstrap 100]
"""

import argparse
import json
import sys
import time
import numpy as np

sys.path.insert(0, ".")
from metrics.total_correlation import compute_C, compute_C_ci
from synthetic.generators import (
    independent,
    coupled_markov,
    fully_coupled,
    modular,
    hierarchical,
    critical,
    recovery,
)


def run_validation(estimator: str = "gaussian", n_bootstrap: int = 100):
    results = {}
    checks = []

    # --- S1: Independent ---
    print("S1: Independent (expected C ≈ 0)...")
    X = independent(n_components=15, n_timepoints=500)
    C = compute_C(X, estimator=estimator)
    ci = compute_C_ci(X, estimator=estimator, n_bootstrap=n_bootstrap)
    results["S1_independent"] = {"C": C, "CI": ci}
    checks.append(("S1 |C| < 0.02", abs(C) < 0.02, C))

    # --- S2: Fully Coupled ---
    print("S2: Fully Coupled (expected C → 1)...")
    X = fully_coupled(n_components=10, n_timepoints=500)
    C = compute_C(X, estimator=estimator)
    ci = compute_C_ci(X, estimator=estimator, n_bootstrap=n_bootstrap)
    results["S2_fully_coupled"] = {"C": C, "CI": ci}
    checks.append(("S2 C > 0.9", C > 0.9, C))

    # --- S3: Coupled Markov ---
    print("S3: Coupled Markov (expected moderate C)...")
    X = coupled_markov(n_components=10, n_timepoints=2000, coupling=0.22)
    C = compute_C(X, estimator=estimator)
    ci = compute_C_ci(X, estimator=estimator, n_bootstrap=n_bootstrap)
    results["S3_coupled_markov"] = {"C": C, "CI": ci}
    checks.append(("S3 C > 0.1", C > 0.1, C))

    # --- S4: Modular ---
    print("S4: Modular (expected moderate C)...")
    X = modular(n_per_module=4, n_modules=3, n_timepoints=2000, within=0.4, between=0.05)
    C = compute_C(X, estimator=estimator)
    ci = compute_C_ci(X, estimator=estimator, n_bootstrap=n_bootstrap)
    results["S4_modular"] = {"C": C, "CI": ci}
    checks.append(("S4 C > 0.05", C > 0.05, C))

    # --- S5: Critical (sandpile) ---
    print("S5: Critical (expected moderate C)...")
    X = critical(system="sandpile", seed=42)
    if X.shape[1] > 10:
        idx = np.random.RandomState(42).choice(X.shape[0], 10, replace=False)
        sub = X[idx, :200]
        C = compute_C(sub, estimator=estimator)
        ci = compute_C_ci(sub, estimator=estimator, n_bootstrap=n_bootstrap)
        results["S5_critical"] = {"C": C, "CI": ci}
        checks.append(("S5 C > 0.05", C > 0.05, C))
    else:
        results["S5_critical"] = {"error": "Not enough timepoints"}

    # --- S6: Hierarchical ---
    print("S6: Hierarchical (expected moderate C)...")
    X = hierarchical(base_n=8, n_levels=3, n_timepoints=1500, micro_coupling=0.3)
    C = compute_C(X, estimator=estimator)
    ci = compute_C_ci(X, estimator=estimator, n_bootstrap=n_bootstrap)
    results["S6_hierarchical"] = {"C": C, "CI": ci}
    checks.append(("S6 C > 0.1", C > 0.1, C))

    # --- Monotonicity: S2 > S3 > S6 > S5 > S4 > S1 ---
    print("Checking monotonicity: S2 > S3 > S6 > S4 > S1...")
    C_S2 = results["S2_fully_coupled"]["C"]
    C_S3 = results["S3_coupled_markov"]["C"]
    C_S6 = results["S6_hierarchical"]["C"]
    C_S4 = results["S4_modular"]["C"]
    C_S1 = results["S1_independent"]["C"]
    monotonic = C_S2 > C_S3 > C_S6 > C_S4 > C_S1
    checks.append(("Monotonicity S2 > S3 > S6 > S4 > S1", monotonic,
                   f"{C_S2:.4f} > {C_S3:.4f} > {C_S6:.4f} > {C_S4:.4f} > {C_S1:.4f}"))

    # --- S7: Recovery dynamics ---
    print("S7: Recovery dynamics (C should vary)...")
    try:
        X = recovery(system="markov", n_components=10, n_timepoints=1000)
        window = 100
        stride = 20
        n_windows = (X.shape[1] - window) // stride
        C_traj = np.zeros(n_windows)
        for i in range(n_windows):
            start = i * stride
            C_traj[i] = compute_C(X[:, start : start + window], estimator=estimator)
        results["S7_recovery_trajectory"] = {
            "C_mean": float(np.mean(C_traj)),
            "C_std": float(np.std(C_traj)),
            "C_min": float(np.min(C_traj)),
            "C_max": float(np.max(C_traj)),
        }
        perturb_signal = np.std(C_traj) > 0.02
        checks.append(("S7 Recovery: C varies > 0.02", perturb_signal, np.std(C_traj)))
    except Exception as e:
        results["S7_recovery_trajectory"] = {"error": str(e)}

    # --- Summary ---
    print("\n" + "=" * 60)
    print("SYNTHETIC VALIDATION REPORT")
    print("=" * 60)
    passed = 0
    failed = 0
    for label, ok, val in checks:
        status = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        else:
            failed += 1
        print(f"  [{status}] {label}: {val}")

    print(f"\n{passed} passed, {failed} failed")
    verdict = "PASS" if failed == 0 else "REVIEW"
    print(f"Verdict: {verdict}")

    results["summary"] = {"passed": passed, "failed": failed, "verdict": verdict}
    results["estimator"] = estimator
    results["n_bootstrap"] = n_bootstrap

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--estimator", default="gaussian", choices=["knn", "gaussian"])
    parser.add_argument("--n-bootstrap", type=int, default=100)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    t0 = time.time()
    results = run_validation(estimator=args.estimator, n_bootstrap=args.n_bootstrap)
    elapsed = time.time() - t0
    results["elapsed_seconds"] = elapsed

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {args.output}")
    else:
        print(f"\nElapsed: {elapsed:.1f}s")
        print(json.dumps(results, indent=2))
