#!/usr/bin/env python3
import json, zlib, numpy as np, pandas as pd
from pathlib import Path
from datetime import datetime
from sklearn.preprocessing import RobustScaler
from sklearn.decomposition import PCA
from sklearn.manifold import Isomap
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import pairwise_distances

OUTDIR=Path("T001_CANONICAL_REAL"); OUTDIR.mkdir(exist_ok=True)
SEEDS=[11,23,37,51,67,79,97,101,131,149]; DOMAINS=["chirp","rw_trend","regime_switch","chaotic_logistic","coupled_osc"]; VARIANTS=["base","reverse","swap","replay","stitch"]; MK=["m1","m2","m3","m4"]

def make_signals(seed):
    np.random.seed(seed); N=4096; t=np.linspace(0,1,N)
    chirp=np.sin(2*np.pi*(8*t+40*t*t))
    rw=np.cumsum(np.random.randn(N))*0.05+0.002*np.arange(N)
    reg=np.concatenate([np.random.randn(N//2)*0.5,np.random.randn(N//2)*2.0+3])
    x=np.zeros(N); x[0]=0.4
    for i in range(N-1): x[i+1]=3.99*x[i]*(1-x[i])
    chaotic=x-x.mean()
    coupled=np.sin(2*np.pi*11*t)+0.6*np.sin(2*np.pi*(23*t+3*t*t))
    return {"chirp":chirp,"rw_trend":rw,"regime_switch":reg,"chaotic_logistic":chaotic,"coupled_osc":coupled}

def make_variants(x):
    n=len(x); thirds=np.array_split(x,3)
    return {"base":x,"reverse":x[::-1],"swap":np.concatenate([x[n//2:],x[:n//2]]),"replay":np.concatenate([x[:n//2],x[:n//2]]),"stitch":np.concatenate([thirds[2],thirds[0],thirds[1]])}

def sof(x): s=np.sign(np.diff(x)); return float(np.mean(s[:-1]*s[1:]))
def hc(x): n=len(x)//2; a,b=x[:n],x[n:2*n]; return float(np.corrcoef(a,b)[0,1]) if np.std(a)>0 and np.std(b)>0 else 0.0
def sc(x): s=''.join('1' if v>0 else '0' for v in np.diff(x)); return len(zlib.compress(s.encode()))/len(s)
def ata(x,k=5):
    bins=np.percentile(x,np.linspace(0,100,k+1)); bins[0]-=1e-9; bins[-1]+=1e-9
    q=np.digitize(x,bins[1:-1]); n=k; F=np.zeros((n,n))
    for a,b in zip(q[:-1],q[1:]): F[a,b]+=1
    if F.sum()>0: F/=F.sum()
    return float(sum((j-i)*abs(F[i,j]-F[j,i]) for i in range(n) for j in range(i+1,n)))

rows=[]
for seed in SEEDS:
    sigs=make_signals(seed)
    for domain,signal in sigs.items():
        for variant,y in make_variants(signal).items():
            rows.append({"seed":seed,"domain":domain,"variant":variant,"m1":sof(y),"m2":hc(y),"m3":sc(y),"m4":ata(y)})

df=pd.DataFrame(rows); df[MK]=RobustScaler().fit_transform(df[MK])
df.to_csv(OUTDIR/"canonical_embeddings.csv",index=False)
X=df[MK].values
pca=PCA().fit(X); explained=pca.explained_variance_ratio_; dim95=int(np.searchsorted(np.cumsum(explained),0.95))+1
nbrs=NearestNeighbors(n_neighbors=6).fit(X); distances,indices=nbrs.kneighbors(X)
purity=float(np.mean([np.mean([df.iloc[j].variant==df.iloc[i].variant for j in indices[i][1:]]) for i in range(len(df))]))
iso=Isomap(n_neighbors=8,n_components=2).fit_transform(X); geo=pairwise_distances(iso); euc=pairwise_distances(X); geo_corr=np.corrcoef(geo.ravel(),euc.ravel())[0,1]
domain_overlap={}
for d in DOMAINS:
    sub=df[df.domain==d]; D=pairwise_distances(sub[MK].values)
    within=[D[i,j] for i in range(len(sub)) for j in range(i+1,len(sub)) if sub.iloc[i].variant==sub.iloc[j].variant]
    between=[D[i,j] for i in range(len(sub)) for j in range(i+1,len(sub)) if sub.iloc[i].variant!=sub.iloc[j].variant]
    domain_overlap[d]={"within_mean":float(np.mean(within)),"between_mean":float(np.mean(between)),"separation_ratio":float(np.mean(between)/np.mean(within))}
replay_dist=float(np.linalg.norm(df[df.variant=="replay"][MK].mean().values-df[df.variant=="base"][MK].mean().values))

results={"timestamp":datetime.utcnow().isoformat()+"Z","architecture":"V2_079_FROZEN","real_embeddings":True,"n_rows":len(df),"pca":{"dim95":dim95,"explained":explained.tolist()},"neighbor_purity":purity,"geodesic_correlation":float(geo_corr),"replay_distance":replay_dist,"domain_overlap":domain_overlap}
with open(OUTDIR/"T001_real_results.json","w") as f: json.dump(results,f,indent=2)

print(f"dim95={dim95}, PC1={explained[0]:.3f}, purity={purity:.3f}, geo_corr={geo_corr:.3f}, replay_dist={replay_dist:.3f}")
for d,v in domain_overlap.items(): print(f"  {d}: sep={v['separation_ratio']:.3f}")
print(f"Saved: {OUTDIR}/")