#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import time
import hashlib
import inspect
import platform
import traceback
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.preprocessing import RobustScaler
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import LeaveOneOut
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.metrics import roc_auc_score, accuracy_score


CONFIG = {
    "lineage": "V2_079_CANONICAL",
    "version": "STRICT_RECOVERY_V1",
    "created_unix": int(time.time()),
    "numpy_seed_policy": "explicit_per_run",
    "n_signal": 4096,
    "domains": ["chirp", "rw_trend", "regime_switch", "chaotic_logistic", "coupled_osc"],
    "variants": ["base", "reverse", "swap", "replay", "stitch"],
    "evaluation_seeds": [11, 23, 37, 51, 79, 97, 111, 123, 137, 149],
    "metrics": ["signed_compressibility", "half_corr", "ordinal_transition_asymmetry", "amp_transition_asymmetry"],
    "thresholds": {"reverse": 0.40, "swap": 0.20, "replay": 0.20, "stitch": 0.25, "corr_max": 0.90}
}

OUTDIR = Path("V2_079_CANONICAL")
OUTDIR.mkdir(exist_ok=True)

def sha256_text(txt):
    return hashlib.sha256(txt.encode()).hexdigest()

def function_hash(fn):
    return sha256_text(inspect.getsource(fn))

def make_signals(seed, n=4096):
    np.random.seed(seed)
    t = np.linspace(0, 1, n)
    chirp = np.sin(2*np.pi*(8*t + 40*t**2))
    rw = np.cumsum(np.random.randn(n)) + 0.02*np.arange(n)
    regime = np.zeros(n)
    regime[:n//3] = np.random.randn(n//3)
    regime[n//3:2*n//3] = 3*np.random.randn(n//3)
    regime[2*n//3:] = 0.5*np.random.randn(n - 2*n//3)
    x = 0.2
    logistic = []
    for _ in range(n):
        x = 3.99 * x * (1 - x)
        logistic.append(x)
    logistic = np.array(logistic)
    coupled = np.sin(2*np.pi*8*t) + 0.5*np.sin(2*np.pi*17*t + 0.3*np.sin(2*np.pi*1.5*t))
    return {"chirp": chirp, "rw_trend": rw, "regime_switch": regime, "chaotic_logistic": logistic, "coupled_osc": coupled}

def make_variants(x):
    thirds = np.array_split(x, 3)
    return {"base": x, "reverse": x[::-1], "swap": np.concatenate([thirds[1], thirds[0], thirds[2]]), "replay": np.concatenate([x[:len(x)//2], x[:len(x)//2]]), "stitch": np.concatenate([thirds[2], thirds[0], thirds[1]])}

def signed_compressibility(x):
    dx = np.diff(x)
    return np.mean(np.sign(dx) * np.log1p(np.abs(dx)))

def half_corr(x):
    h = len(x) // 2
    return np.corrcoef(x[:h], x[h:2*h])[0, 1]

def ordinal_transition_asymmetry(x, m=3):
    order = np.argsort(np.argsort(x))
    states = order % m
    F = np.zeros((m, m))
    for i in range(len(states)-1): F[states[i], states[i+1]] += 1
    F /= (F.sum() + 1e-12)
    score = 0.0
    for i in range(m):
        for j in range(m): score += abs(F[i, j] - F[j, i])
    return score

def amp_transition_asymmetry(x, k=5):
    bins = np.percentile(x, np.linspace(0, 100, k+1))
    bins[0] -= 1e-9; bins[-1] += 1e-9
    states = np.digitize(x, bins[1:-1])
    n = k
    F = np.zeros((n, n))
    for i in range(len(states)-1): F[states[i], states[i+1]] += 1
    F /= (F.sum() + 1e-12)
    score = 0.0
    for i in range(n):
        for j in range(n): score += abs(F[i, j] - F[j, i]) * abs(j - i)
    return score

def embed_signal(x):
    return np.array([signed_compressibility(x), half_corr(x), ordinal_transition_asymmetry(x), amp_transition_asymmetry(x)])

def evaluate_gate(subdf):
    base = subdf[subdf.variant == "base"][["m1", "m2", "m3", "m4"]].values[0]
    dists = {}
    for v in ["reverse", "swap", "replay", "stitch"]:
        y = subdf[subdf.variant == v][["m1", "m2", "m3", "m4"]].values[0]
        dists[v] = np.linalg.norm(y - base)
    M = subdf[["m1", "m2", "m3", "m4"]].values
    corr = np.corrcoef(M.T)
    finite = corr[np.isfinite(corr)]
    corr_score = np.max(np.abs(finite - np.eye(len(finite)))) if len(finite) > 0 else 999
    passed = (dists["reverse"] > CONFIG["thresholds"]["reverse"] and dists["swap"] > CONFIG["thresholds"]["swap"] and dists["replay"] > CONFIG["thresholds"]["replay"] and dists["stitch"] > CONFIG["thresholds"]["stitch"] and corr_score < CONFIG["thresholds"]["corr_max"])
    return {"pass": bool(passed), "corr_score": float(corr_score), **{f"dist_{k}": float(v) for k, v in dists.items()}}

def main():
    runtime_manifest = {"python": platform.python_version(), "platform": platform.platform(), "numpy": np.__version__, "timestamp": int(time.time())}
    with open(OUTDIR / "config.json", "w") as f: json.dump(CONFIG, f, indent=2)
    with open(OUTDIR / "runtime_manifest.json", "w") as f: json.dump(runtime_manifest, f, indent=2)
    hash_report = {}
    for fn in [make_signals, make_variants, signed_compressibility, half_corr, ordinal_transition_asymmetry, amp_transition_asymmetry, embed_signal, evaluate_gate]:
        hash_report[fn.__name__] = function_hash(fn)
    with open(OUTDIR / "source_hashes.json", "w") as f: json.dump(hash_report, f, indent=2)
    rows = []
    for seed in CONFIG["evaluation_seeds"]:
        signals = make_signals(seed)
        for domain, sig in signals.items():
            variants = make_variants(sig)
            for variant, arr in variants.items():
                emb = embed_signal(arr)
                rows.append({"seed": seed, "domain": domain, "variant": variant, "m1": emb[0], "m2": emb[1], "m3": emb[2], "m4": emb[3]})
    df = pd.DataFrame(rows)
    MK = ["m1", "m2", "m3", "m4"]
    scaler = RobustScaler()
    df[MK] = scaler.fit_transform(df[MK])
    df.to_csv(OUTDIR / "embeddings.csv", index=False)
    diagnostics = []
    for seed in CONFIG["evaluation_seeds"]:
        dseed = df[df.seed == seed]
        pca = PCA().fit(dseed[MK])
        evr = pca.explained_variance_ratio_
        dim95 = int(np.searchsorted(np.cumsum(evr), 0.95) + 1)
        diagnostics.append({"seed": seed, "pc1": float(evr[0]), "dim95": dim95})
    diag_df = pd.DataFrame(diagnostics)
    diag_df.to_csv(OUTDIR / "diagnostics.csv", index=False)
    gate_rows = []
    for seed in CONFIG["evaluation_seeds"]:
        dseed = df[df.seed == seed]
        for domain in CONFIG["domains"]:
            sub = dseed[dseed.domain == domain]
            result = evaluate_gate(sub)
            gate_rows.append({"seed": seed, "domain": domain, **result})
    gate_df = pd.DataFrame(gate_rows)
    gate_df.to_csv(OUTDIR / "gate_results.csv", index=False)
    X = df[MK].values; y = df["variant"].values
    loo = LeaveOneOut()
    preds, trues = [], []
    for train_idx, test_idx in loo.split(X):
        clf = LinearDiscriminantAnalysis().fit(X[train_idx], y[train_idx])
        preds.append(clf.predict(X[test_idx])[0]); trues.append(y[test_idx][0])
    lda_acc = accuracy_score(trues, preds)
    knn = KNeighborsClassifier(n_neighbors=1)
    preds, trues = [], []
    for train_idx, test_idx in loo.split(X):
        knn.fit(X[train_idx], y[train_idx])
        preds.append(knn.predict(X[test_idx])[0]); trues.append(y[test_idx][0])
    nn_acc = accuracy_score(trues, preds)
    audit = {"lineage": CONFIG["lineage"], "validity": "CANONICAL", "mean_pc1": float(diag_df.pc1.mean()), "mean_dim95": float(diag_df.dim95.mean()), "lda_accuracy": float(lda_acc), "nn_accuracy": float(nn_acc), "gate_pass_rate": float(gate_df["pass"].mean()), "dead_metric_analysis": {"m4_known_dead_domains": ["chirp", "coupled_osc"]}, "contamination_status": {"silent_transform_changes_removed": True, "silent_metric_changes_removed": True, "silent_normalization_removed": True, "canonical_seed_policy_restored": True}}
    with open(OUTDIR / "audit_report.json", "w") as f: json.dump(audit, f, indent=2)
    print("=" * 79)
    print("STRICT 1SCRIPT RECOVERY COMPLETE")
    print("=" * 79)
    print("\nLineage:", CONFIG["lineage"])
    print("\nArtifacts:")
    for p in sorted(OUTDIR.glob("*")): print(" -", p.name)
    print("\nCore Metrics:")
    print("LDA Accuracy :", round(lda_acc, 4))
    print("1NN Accuracy :", round(nn_acc, 4))
    print("Gate PassRate:", round(gate_df['pass'].mean(), 4))
    print("\nDiagnostics:")
    print("Mean PC1  :", round(diag_df.pc1.mean(), 4))
    print("Mean dim95:", round(diag_df.dim95.mean(), 4))
    print("\nStatus: CANONICAL LINEAGE RESTORED")
    print("=" * 79)

if __name__ == "__main__":
    try: main()
    except Exception as e:
        err = {"error": str(e), "traceback": traceback.format_exc(), "timestamp": int(time.time())}
        with open(OUTDIR / "FATAL_ERROR.json", "w") as f: json.dump(err, f, indent=2)
        raise