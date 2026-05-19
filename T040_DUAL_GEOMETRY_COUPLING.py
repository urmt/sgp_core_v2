#!/usr/bin/env python3
import os, json, hashlib, numpy as np
from sklearn.decomposition import PCA
from scipy.stats import entropy
from sklearn.cross_decomposition import CCA

ROOT="T040_DUAL_GEOMETRY_COUPLING"
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
    h=len(x)//2; a,b=x[:h],x[h:]
    dx=np.diff(x); m1=np.mean(np.sign(dx[:-1])*np.sign(dx[1:])) if len(dx)>1 else 0.0
    m2=np.corrcoef(a,b)[0,1] if np.std(a)>1e-8 and np.std(b)>1e-8 else 0.0
    q=np.round(x,2); m3=len(np.unique(q))/len(q)
    m4=np.mean(np.abs(dx))
    return np.array([m1,m2,m3,m4])

def H(x,bins=64): hist,_=np.histogram(x,bins=bins,density=True); hist+=1e-12; return entropy(hist)
def LV(x): return np.mean(np.abs(np.diff(x)))
def SE(x): ps=np.abs(np.fft.rfft(x))**2; ps/=np.sum(ps)+1e-12; return entropy(ps)
def C(x): q=np.round((x-np.mean(x))/(np.std(x)+1e-8),2); return len(np.unique(q))/len(q)
def info(x): return np.array([H(x),LV(x),SE(x),C(x)])

G,I=[],[]
for name,sig in signals.items():
    g0=embed(sig); i0=info(sig)
    for op_name,op in OPS.items():
        y=op(sig); G.append(embed(y)-g0); I.append(info(y)-i0)

G,I=np.array(G),np.array(I)
pcaG, pcaI=PCA().fit(G), PCA().fit(I)
tauG, tauI=pcaG.components_[0], pcaI.components_[0]

cca=CCA(n_components=1); cca.fit(G,I)
Gc,Ic=cca.transform(G,I)
coupling=float(np.corrcoef(Gc[:,0],Ic[:,0])[0,1])

projG=G@tauG; projI=I@tauI
flow_corr=float(np.corrcoef(projG,projI)[0,1])

H1_dual_coupling=bool(abs(coupling)>0.90)
H2_lowrank_duality=bool(pcaG.explained_variance_ratio_[0]>0.90 and pcaI.explained_variance_ratio_[0]>0.90)
H3_flow_linkage=bool(abs(flow_corr)>0.50)

RESULTS={"geom_pc1":float(pcaG.explained_variance_ratio_[0]),"info_pc1":float(pcaI.explained_variance_ratio_[0]),"cca_coupling":coupling,"flow_correlation":flow_corr,"tau_geom":tauG.tolist(),"tau_info":tauI.tolist(),"checks":{"H1_dual_coupling":H1_dual_coupling,"H2_lowrank_duality":H2_lowrank_duality,"H3_flow_linkage":H3_flow_linkage}}

with open(os.path.join(ROOT,"T040_RESULTS.json"),"w") as f: json.dump(RESULTS,f,indent=2)
sha=hashlib.sha256(json.dumps(RESULTS,sort_keys=True).encode()).hexdigest()
with open(os.path.join(ROOT,"T040.sha256"),"w") as f: f.write(sha)
print(f"\n=== T040 DUAL GEOMETRY COUPLING ===\n{json.dumps(RESULTS,indent=2)}\nSHA256: {sha}")