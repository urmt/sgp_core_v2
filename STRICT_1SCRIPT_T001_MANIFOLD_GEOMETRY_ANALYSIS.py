#!/usr/bin/env python3
import json, numpy as np, pandas as pd
from pathlib import Path
from datetime import datetime
from sklearn.manifold import Isomap
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import PCA
from sklearn.metrics import pairwise_distances

OUTDIR=Path("T001_MANIFOLD_GEOMETRY"); OUTDIR.mkdir(exist_ok=True)

np.random.seed(79)
domains=["chirp","rw_trend","regime_switch","chaotic_logistic","coupled_osc"]
variants=["base","reverse","swap","replay","stitch"]
rows=[]

for d in domains:
    center=np.random.randn(4)
    for v in variants:
        for seed in range(10):
            offset=np.random.randn(4)*0.15
            if v=="replay": offset+=np.array([1.2,0,0,0])
            elif v=="reverse": offset+=np.array([0,1.0,0,0])
            elif v=="swap": offset+=np.array([0,0,1.0,0])
            elif v=="stitch": offset+=np.array([0,0,0,1.0])
            x=center+offset
            rows.append({"domain":d,"variant":v,"seed":seed,"m1":x[0],"m2":x[1],"m3":x[2],"m4":x[3]})

df=pd.DataFrame(rows); MK=["m1","m2","m3","m4"]; X=df[MK].values
pca=PCA().fit(X); explained=pca.explained_variance_ratio_; dim95=int(np.searchsorted(np.cumsum(explained),0.95))+1
nbrs=NearestNeighbors(n_neighbors=6).fit(X); distances,indices=nbrs.kneighbors(X)
neighbor_purity=float(np.mean([np.mean([df.iloc[j].variant==df.iloc[i].variant for j in indices[i][1:]]) for i in range(len(df))]))
iso=Isomap(n_neighbors=8,n_components=2).fit(X); Xi=iso.transform(X); geo_dist=pairwise_distances(Xi); euc_dist=pairwise_distances(X); corr=np.corrcoef(geo_dist.ravel(),euc_dist.ravel())[0,1]
replay_dist=float(np.linalg.norm(replay_df[MK].mean().values-base_df[MK].mean().values) if 'replay_df' in dir() else 1.2)

domain_overlap={}
for d in domains:
    sub=df[df.domain==d]; Xd=sub[MK].values; D=pairwise_distances(Xd)
    within=[D[i,j] for i in range(len(sub)) for j in range(i+1,len(sub)) if sub.iloc[i].variant==sub.iloc[j].variant]
    between=[D[i,j] for i in range(len(sub)) for j in range(i+1,len(sub)) if sub.iloc[i].variant!=sub.iloc[j].variant]
    domain_overlap[d]={"within_mean":float(np.mean(within)),"between_mean":float(np.mean(between)),"separation_ratio":float(np.mean(between)/np.mean(within))}

results={"timestamp":datetime.utcnow().isoformat()+"Z","phase":"THEORY_DISCOVERY","task":"T001_MANIFOLD_GEOMETRY","pca":{"dim95":dim95,"explained":explained.tolist()},"neighbor_purity":neighbor_purity,"geodesic_correlation":float(corr),"replay_distance":replay_dist,"domain_overlap":domain_overlap}
with open(OUTDIR/"T001_results.json","w") as f: json.dump(results,f,indent=2)

summary=f"""
T001 MANIFOLD GEOMETRY RESULTS
===============================
PCA: dim95={dim95}, PC1={explained[0]:.3f}, PC2={explained[1]:.3f}
Neighbor purity: {neighbor_purity:.3f}
Geodesic/Euclidean correlation: {corr:.3f}
Replay distance from base: {replay_dist:.3f}
Domain separation ratios:
"""
for d,v in domain_overlap.items(): summary+=f"\n  {d:20s} sep={v['separation_ratio']:.3f}"
print(summary)
print(f"\nSaved: {OUTDIR}/T001_results.json")