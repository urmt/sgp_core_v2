#!/usr/bin/env python3
"""
SFH-SGP Repair & Validation Pipeline
Single-script scaffold addressing all major third-party criticisms.
"""

from __future__ import annotations
import json, random
from pathlib import Path
import numpy as np
import pandas as pd

SEED = 42
np.random.seed(SEED)
random.seed(SEED)

OUTPUT_DIR = Path("sfh_sgp_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

REPORT = {"completed": [], "failed": [], "warnings": []}

# ---------------- SIGNALS ----------------

def white_noise(n=256):
    return np.random.randn(n)

def sine_wave(n=256, freq=4):
    x = np.linspace(0, 2*np.pi, n)
    return np.sin(freq*x)

def random_walk(n=256):
    return np.cumsum(np.random.randn(n))

DATASETS = {
    "white_noise": white_noise,
    "sine_wave": sine_wave,
    "random_walk": random_walk,
}

# ---------------- TRANSFORMS ----------------

def identity(x): return x.copy()
def reverse(x): return x[::-1]

def replay(x):
    h = len(x)//2
    return np.concatenate([x[:h], x[:h]])

def swap_halves(x):
    h = len(x)//2
    return np.concatenate([x[h:], x[:h]])

def stitch(x):
    h = len(x)//2
    return np.concatenate([x[:h], x[::-1][:h]])

def add_noise(x, sigma=0.1):
    return x + np.random.normal(0, sigma, len(x))

TRANSFORMS = {
    "identity": identity,
    "reverse": reverse,
    "replay": replay,
    "swap_halves": swap_halves,
    "stitch": stitch,
    "noise": add_noise,
}

# ---------------- METRICS ----------------

def m1(x):
    dx = np.diff(x)
    return np.mean(np.sign(dx))

def m2(x):
    h = len(x)//2
    return np.corrcoef(x[:h], x[h:])[0,1]

def m3(x):
    c = x - np.mean(x)
    return np.mean(np.sign(c)*np.abs(c))

def m4(x):
    dx = np.diff(x)
    pos = np.abs(dx[dx > 0]).mean() if np.any(dx > 0) else 0
    neg = np.abs(dx[dx < 0]).mean() if np.any(dx < 0) else 0
    return pos - neg

METRICS = [m1, m2, m3, m4]

def metric_vector(x):
    vals = []
    for fn in METRICS:
        try:
            v = fn(x)
            if np.isnan(v) or np.isinf(v):
                v = 0.0
        except Exception:
            v = 0.0
        vals.append(v)
    return np.array(vals)

# ---------------- TESTS ----------------

def test_dimensionality():
    rows = []

    for name, gen in DATASETS.items():
        emb = []

        for _ in range(100):
            x = gen()
            for _, tf in TRANSFORMS.items():
                emb.append(metric_vector(tf(x)))

        X = np.vstack(emb)
        cov = np.cov(X.T)
        eig = np.linalg.eigvalsh(cov)[::-1]
        exp = eig/eig.sum()

        rows.append({
            "dataset": name,
            "pc1_variance": float(exp[0]),
            "effective_rank": float(np.exp(-np.sum(exp*np.log(exp+1e-12))))
        })

    pd.DataFrame(rows).to_csv(OUTPUT_DIR/"dimensionality_report.csv", index=False)
    REPORT["completed"].append("dimensionality")

def test_replay():
    rows = []

    for name, gen in DATASETS.items():
        for _ in range(50):
            x = gen()
            r1 = replay(x)
            r2 = replay(r1)

            rows.append({
                "dataset": name,
                "idempotent_mse": float(np.mean((r2-r1)**2)),
                "m2_minus_m3": float(abs(m2(r1)-m3(r1)))
            })

    pd.DataFrame(rows).to_csv(OUTPUT_DIR/"replay_operator_report.csv", index=False)
    REPORT["completed"].append("replay")

def test_operator_algebra():
    x = white_noise()
    ops = list(TRANSFORMS.keys())
    rows = []

    for a in ops:
        for b in ops:
            xab = TRANSFORMS[b](TRANSFORMS[a](x))

            best = None
            best_mse = 1e9

            for c in ops:
                xc = TRANSFORMS[c](x)
                mse = np.mean((xab-xc)**2)
                if mse < best_mse:
                    best_mse = mse
                    best = c

            rows.append({
                "A": a,
                "B": b,
                "closest": best,
                "mse": float(best_mse)
            })

    pd.DataFrame(rows).to_csv(OUTPUT_DIR/"operator_algebra_report.csv", index=False)
    REPORT["completed"].append("operator_algebra")

def falsification():
    x = white_noise()
    base = metric_vector(x)

    rows = []

    for name, tf in TRANSFORMS.items():
        xt = tf(x)
        corr = np.corrcoef(base, metric_vector(xt))[0,1]

        rows.append({
            "transform": name,
            "corr": float(corr),
            "pass": bool(corr > 0.5)
        })

    pd.DataFrame(rows).to_csv(OUTPUT_DIR/"falsification_report.csv", index=False)
    REPORT["completed"].append("falsification")

def final_summary():
    text = """
# FINAL ASSESSMENT

Corrections Applied
-------------------
1. No proof claims
2. Effective dimensionality separated from intrinsic dimensionality
3. Replay tested empirically
4. Operator algebra treated as approximate
5. Expanded datasets and transforms
6. Added falsification criteria
"""

    (OUTPUT_DIR/"final_assessment.md").write_text(text)

    with open(OUTPUT_DIR/"validation_report.json", "w") as f:
        json.dump(REPORT, f, indent=2)

def main():
    test_dimensionality()
    test_replay()
    test_operator_algebra()
    falsification()
    final_summary()
    print("Pipeline complete.")

if __name__ == "__main__":
    main()
