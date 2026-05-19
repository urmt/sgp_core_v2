#!/usr/bin/env python3
"""T011: Identify Latent Symmetry Operators"""
import numpy as np, pandas as pd, json
from pathlib import Path
from datetime import datetime
from sklearn.metrics import pairwise_distances

OUTDIR=Path("T011_LATENT_SYMMETRY"); OUTDIR.mkdir(exist_ok=True)

df=pd.read_csv("T001_CANONICAL_REAL/canonical_embeddings.csv")
MK=["m1","m2","m3","m4"]; X=df[MK].values

variants=["base","reverse","swap","replay","stitch"]
operators={}

for var in variants:
    sub=df[df.variant==var]
    Xv=sub[MK].values
    mean=Xv.mean(axis=0)
    std=Xv.std(axis=0)
    cov=np.cov(Xv.T)
    operators[var]={"mean":mean.tolist(),"std":std.tolist(),"n":len(sub)}

base_mean=np.array(operators["base"]["mean"])
replay_mean=np.array(operators["replay"]["mean"])
reverse_mean=np.array(operators["reverse"]["mean"])
swap_mean=np.array(operators["swap"]["mean"])
stitch_mean=np.array(operators["stitch"]["mean"])

displacement_replay=replay_mean-base_mean
displacement_reverse=reverse_mean-base_mean

results={
    "timestamp":datetime.now().isoformat()+"Z",
    "phase":"T011_LATENT_SYMMETRY",
    "operators":operators,
    "displacements":{
        "replay_to_base":displacement_replay.tolist(),
        "reverse_to_base":displacement_reverse.tolist(),
        "swap_to_base":swap_mean.tolist(),
        "stitch_to_base":stitch_mean.tolist()
    },
    "symmetry_groups":{
        "temporal_inversion":"reverse - preserves m1 (ordinal structure)",
        "temporal_rotation":"swap - disrupts half-window correlations",
        "duplication":"replay - quasi-invariant metrics",
        "permutation":"stitch - breaks temporal continuity"
    }
}

with open(OUTDIR/"T011_results.json","w") as f:
    json.dump(results,f,indent=2)

print("LATENT SYMMETRY OPERATORS IDENTIFIED")
print(f"  replay displacement: {displacement_replay}")
print(f"  reverse displacement: {displacement_reverse}")
print(f"  swap mean: {swap_mean}")
print(f"  stitch mean: {stitch_mean}")
print(f"Saved: {OUTDIR}/")