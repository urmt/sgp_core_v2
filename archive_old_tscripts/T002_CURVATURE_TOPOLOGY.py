#!/usr/bin/env python3
import numpy as np, pandas as pd, json
from pathlib import Path
from datetime import datetime
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import PCA
from sklearn.manifold import Isomap
from scipy.spatial.distance import cdist

OUTDIR=Path("T002_CURVATURE_TOPOLOGY"); OUTDIR.mkdir(exist_ok=True)

df=pd.read_csv("T001_CANONICAL_REAL/canonical_embeddings.csv")
MK=["m1","m2","m3","m4"]; X=df[MK].values

nbrs=NearestNeighbors(n_neighbors=9).fit(X)
distances,indices=nbrs.kneighbors(X)

curvature=[]
for i in range(len(X)):
    p=X[i]
    neigh=[X[j] for j in indices[i][1:]]
    c=0.0
    for a in neigh:
        for b in neigh:
            if np.linalg.norm(a-b)>1e-9:
                proj=np.dot(p-((a+b)/2), (a-b)/np.linalg.norm(a-b))
                c=max(c,abs(proj))
    curvature.append(c)
mean_curv=float(np.mean(curvature))

eigvals=PCA().fit(X).explained_variance_
eff_rank=float(eigvals[0]/np.sum(eigvals))

dists=cdist(X,X)
np.fill_diagonal(dists,np.inf)
min_dists=dists.min(axis=1)

from scipy.spatial import ConvexHull
try:
    vol=ConvexHull(X).volume
except:
    vol=0.0

r=0.1
n_conn=[]
for i in range(len(X)):
    ball=dists[i]<r
    n_conn.append(ball.sum())
conn_density=float(np.mean(n_conn))

results={
    "timestamp":datetime.now().isoformat()+"Z",
    "phase":"T002_CURVATURE_TOPOLOGY",
    "mean_local_curvature":mean_curv,
    "effective_rank_pc1":eff_rank,
    "convex_hull_volume":vol,
    "connection_density_10pct":conn_density,
    "min_neighbor_distance_mean":float(np.mean(min_dists)),
    "interpretation":{
        "curvature":"low=linear manifold",
        "eff_rank":"high=full dimensional",
        "conn_density":"connectedness at scale r"
    }
}

with open(OUTDIR/"T002_results.json","w") as f:
    json.dump(results,f,indent=2)

print(f"Curvature: {mean_curv:.4f}")
print(f"EffRank(PC1): {eff_rank:.4f}")
print(f"HullVol: {vol:.4f}")
print(f"ConnDensity(r=0.1): {conn_density:.1f}")
print(f"MinDist(mean): {np.mean(min_dists):.4f}")
print(f"Saved: {OUTDIR}/")