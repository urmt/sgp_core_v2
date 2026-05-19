#!/usr/bin/env python3
import os, json, hashlib, numpy as np
from sklearn.decomposition import PCA

ROOT="T035_SPECTRAL_SEMIGROUP"
os.makedirs(ROOT, exist_ok=True)
SEED=79
rng=np.random.default_rng(SEED)

def m1(x): d=np.diff(x); return np.mean(np.sign(d[:-1])*np.sign(d[1:])) if len(d)>1 else 0.0
def m2(x): n=len(x)//2; a,b=x[:n],x[n:2*n]; return np.corrcoef(a,b)[0,1] if np.std(a)>0 and np.std(b)>0 else 0.0
def m3(x): q=np.round((x-np.mean(x))/(np.std(x)+1e-8),2); return -np.mean(np.abs(np.diff(q)))
def m4(x): return np.mean(np.abs(np.diff(x)))
def E(x): return np.array([m1(x),m2(x),m3(x),m4(x)])

def R(x): h=len(x)//2; return np.concatenate([x[:h],x[:h]])
def S(x): q=len(x)//4; return np.concatenate([x[:q],x[2*q:3*q],x[q:2*q],x[3*q:]])
def W(x): h=len(x)//2; return np.concatenate([x[h:],x[:h]])
def V(x): return x[::-1]
OPS={"R":R,"S":S,"W":W,"V":V}

N=512; t=np.linspace(0,1,N)
signals={"chirp":np.sin(2*np.pi*(3*t+10*t*t)),"rw":np.cumsum(rng.normal(size=N)),"telegraph":np.sign(np.sin(2*np.pi*7*t)),"pink":np.cumsum(rng.normal(size=N))}

D={}
for name,op in OPS.items():
    disp=[E(op(sig))-E(sig) for sig in signals.values()]
    D[name]=np.mean(disp,axis=0)

names=list(D.keys())
SIM=np.zeros((4,4))
for i,a in enumerate(names):
    for j,b in enumerate(names):
        va, vb = D[a], D[b]
        na, nb = np.linalg.norm(va), np.linalg.norm(vb)
        SIM[i,j]=np.dot(va,vb)/(na*nb) if na>1e-8 and nb>1e-8 else 0

M=np.stack([D[k] for k in names])
pca=PCA(n_components=4); pca.fit(M)
spec_pc1=float(pca.explained_variance_ratio_[0])
tau=pca.components_[0]

proj_scores={}
for k,v in D.items():
    n=np.linalg.norm(v)
    proj_scores[k]=float(np.dot(v,tau)/n) if n>1e-8 else 0.0

projection_family=[k for k,v in proj_scores.items() if abs(v)>0.8]
symmetry_family=[k for k,v in proj_scores.items() if abs(v)<=0.8]

eigvals=np.sort(np.abs(np.linalg.eig(SIM)[0]))[::-1]
spectral_gap=float(eigvals[0]/(eigvals[1]+1e-8))

H1_lowrank_spectrum=bool(spec_pc1>0.90)
H2_projection_family=bool("R" in projection_family and "S" in projection_family)
H3_symmetry_family=bool("V" in symmetry_family)
H4_spectral_gap=bool(spectral_gap>2.0)

RESULTS={"spec_pc1":spec_pc1,"tau":tau.tolist(),"similarity_matrix":SIM.tolist(),"projection_scores":proj_scores,"projection_family":projection_family,"symmetry_family":symmetry_family,"eigenvalues":eigvals.tolist(),"spectral_gap":spectral_gap,"checks":{"H1_lowrank_spectrum":H1_lowrank_spectrum,"H2_projection_family":H2_projection_family,"H3_symmetry_family":H3_symmetry_family,"H4_spectral_gap":H4_spectral_gap}}

with open(os.path.join(ROOT,"T035_RESULTS.json"),"w") as f: json.dump(RESULTS,f,indent=2)
sha=hashlib.sha256(json.dumps(RESULTS,sort_keys=True).encode()).hexdigest()
with open(os.path.join(ROOT,"T035.sha256"),"w") as f: f.write(sha)

print(f"\n=== T035 SPECTRAL SEMIGROUP ===\nspec_pc1: {round(spec_pc1,6)}\nspectral_gap: {round(spectral_gap,6)}\nProjection family: {projection_family}\nSymmetry family: {symmetry_family}\nChecks: H1={H1_lowrank_spectrum}, H2={H2_projection_family}, H3={H3_symmetry_family}, H4={H4_spectral_gap}\nSHA256: {sha}")