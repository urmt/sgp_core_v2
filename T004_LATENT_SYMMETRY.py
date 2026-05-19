#!/usr/bin/env python3
import numpy as np, pandas as pd, json
from pathlib import Path
from datetime import datetime
from sklearn.metrics import pairwise_distances

OUTDIR=Path("T004_LATENT_SYMMETRY"); OUTDIR.mkdir(exist_ok=True)

df=pd.read_csv("T001_CANONICAL_REAL/canonical_embeddings.csv")
MK=["m1","m2","m3","m4"]; X=df[MK].values

variants=["base","reverse","swap","replay","stitch"]
symmetry_groups={}

for var in variants:
    sub=df[df.variant==var]
    Xv=sub[MK].values
    D=pairwise_distances(Xv)
    within=D[np.triu_indices(len(sub),k=1)]
    symmetry_groups[var]={
        "mean_within_distance":float(np.mean(within)),
        "std_within_distance":float(np.std(within)),
        "n_samples":len(sub)
    }

corr_matrix=np.corrcoef(X.T)
eigenvectors=np.linalg.eig(corr_matrix)[1]

results={
    "timestamp":datetime.now().isoformat()+"Z",
    "phase":"T004_LATENT_SYMMETRY",
    "variant_geometry":symmetry_groups,
    "metric_correlation_matrix":corr_matrix.tolist(),
    "eigenvectors":eigenvectors.tolist(),
    "interpretation":{
        "reverse":"temporal inversion - preserves ordinal structure",
        "swap":"rotation in time - disrupts half_corr",
        "replay":"duplication - quasi-invariant",
        "stitch":"permutation - breaks temporal continuity",
        "base":"canonical reference"
    }
}

with open(OUTDIR/"T004_results.json","w") as f:
    json.dump(results,f,indent=2)

print("Variant geometry:")
for v,g in symmetry_groups.items():
    print(f"  {v:10s}: mean={g['mean_within_distance']:.4f}, std={g['std_within_distance']:.4f}")
print(f"\nMetric correlations:\n{corr_matrix}")
print(f"Saved: {OUTDIR}/")