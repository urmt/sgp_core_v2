#!/usr/bin/env python3
import os, json, hashlib, numpy as np
from sklearn.decomposition import PCA
from sklearn.cross_decomposition import CCA
from scipy.stats import entropy
from scipy.spatial.distance import pdist

ROOT="T041_LATENT_MANIFOLD_RECOVERY"
os.makedirs(ROOT, exist_ok=True)
SEED=79
rng=np.random.default_rng(SEED)

N=512; t=np.linspace(0,1,N)
signals={"chirp":np.sin(2*np.pi*(3*t+10*t*t)),"rw":np.cumsum(rng.normal(size=N)),"telegraph":np.sign(np.sin(2*np.pi*8*t)),"spikes":(rng.random(N)<0.03).astype(float),"square":np.sign(np.sin(2*np.pi*5*t))}

def R(x): h=len(x)//2; return np.concatenate([x[:h],x[:h]])
def S(x): q=len(x)//4; return np.concatenate([x[:q],x[2*q:3*q],x[q:2*q],x[3*q:]])
def W(x): h=len(x)//2; return np.concatenate([x[h:],x[:h]])
def V(x): return x[::-1]
OPS={"R":R,"S":S,"W":W,"V":V}

def embed(x):
    h=len(x)//2; a,b=x[:h],x[h:]; dx=np.diff(x)
    m1=np.mean(np.sign(dx[:-1])*np.sign(dx[1:])) if len(dx)>1 else 0.0
    m2=np.corrcoef(a,b)[0,1] if np.std(a)>1e-8 and np.std(b)>1e-8 else 0.0
    m3=len(np.unique(np.round(x,2)))/len(x); m4=np.mean(np.abs(dx))
    return np.array([m1,m2,m3,m4])

def H(x,bins=64): hist,_=np.histogram(x,bins=bins,density=True); hist+=1e-12; return entropy(hist)
def LV(x): return np.mean(np.abs(np.diff(x)))
def SE(x): ps=np.abs(np.fft.rfft(x))**2; ps/=np.sum(ps)+1e-12; return entropy(ps)
def C(x): q=np.round((x-np.mean(x))/(np.std(x)+1e-8),2); return len(np.unique(q))/len(q)
def info(x): return np.array([H(x),LV(x),SE(x),C(x)])

G,I,labels=[],[],[]
for name,sig in signals.items():
    g0=embed(sig); i0=info(sig)
    for op_name,op in OPS.items():
        y=op(sig); G.append(embed(y)-g0); I.append(info(y)-i0); labels.append(f"{name}_{op_name}")

G,I=np.array(G),np.array(I)
cca=CCA(n_components=2); cca.fit(G,I); Gc,Ic=cca.transform(G,I); latent=0.5*(Gc+Ic)

pca=PCA().fit(latent)
pc1=float(pca.explained_variance_ratio_[0])
dim95=int(np.searchsorted(np.cumsum(pca.explained_variance_ratio_),0.95))+1
curvature=float(np.std(pdist(latent))/(np.mean(pdist(latent))+1e-8))

projection_idx=[i for i,l in enumerate(labels) if "_R" in l or "_S" in l]
antisym_idx=[i for i,l in enumerate(labels) if "_W" in l or "_V" in l]
proj_centroid=np.mean(latent[projection_idx],axis=0)
anti_centroid=np.mean(latent[antisym_idx],axis=0)
family_sep=float(np.linalg.norm(proj_centroid-anti_centroid))
within_proj=float(np.mean(np.linalg.norm(latent[projection_idx]-proj_centroid,axis=1)))
within_anti=float(np.mean(np.linalg.norm(latent[antisym_idx]-anti_centroid,axis=1)))
cluster_ratio=family_sep/(within_proj+within_anti+1e-8)

H1_lowrank_latent=bool(pc1>0.90)
H2_family_separation=bool(cluster_ratio>2.0)
H3_low_curvature=bool(curvature<1.0)

RESULTS={"latent_pc1":pc1,"latent_dim95":dim95,"latent_curvature":curvature,"family_separation":family_sep,"cluster_ratio":cluster_ratio,"checks":{"H1_lowrank_latent":H1_lowrank_latent,"H2_family_separation":H2_family_separation,"H3_low_curvature":H3_low_curvature}}

with open(os.path.join(ROOT,"T041_RESULTS.json"),"w") as f: json.dump(RESULTS,f,indent=2)
sha=hashlib.sha256(json.dumps(RESULTS,sort_keys=True).encode()).hexdigest()
with open(os.path.join(ROOT,"T041.sha256"),"w") as f: f.write(sha)
print(f"\n=== T041 LATENT MANIFOLD RECOVERY ===\n{json.dumps(RESULTS,indent=2)}\nSHA256: {sha}")