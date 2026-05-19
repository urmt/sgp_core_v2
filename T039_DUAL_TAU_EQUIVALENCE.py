#!/usr/bin/env python3
import os, json, hashlib, numpy as np
from sklearn.decomposition import PCA
from scipy.stats import entropy

ROOT="T039_DUAL_TAU_EQUIVALENCE"
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
    m4=np.mean(np.abs(np.diff(x)))
    return np.array([m1,m2,m3,m4])

def shannon_entropy(x,bins=64): hist,_=np.histogram(x,bins=bins,density=True); hist+=1e-12; return entropy(hist)
def spectral_entropy(x): ps=np.abs(np.fft.rfft(x))**2; ps/=np.sum(ps)+1e-12; return entropy(ps)
def local_variation(x): return np.mean(np.abs(np.diff(x)))
def compression_proxy(x): q=np.round((x-np.mean(x))/(np.std(x)+1e-8),2); return len(np.unique(q))/len(q)
def info_vec(x): return np.array([shannon_entropy(x),local_variation(x),spectral_entropy(x),compression_proxy(x)])

geom_disp,info_disp=[],[]
for name,sig in signals.items():
    e0=embed(sig); i0=info_vec(sig)
    for op_name,op in OPS.items():
        y=op(sig); geom_disp.append(embed(y)-e0); info_disp.append(info_vec(y)-i0)

geom_disp,info_disp=np.array(geom_disp),np.array(info_disp)
geom_pca,info_pca=PCA().fit(geom_disp),PCA().fit(info_disp)
tau_geom=geom_pca.components_[0]/np.linalg.norm(geom_pca.components_[0])
tau_info=info_pca.components_[0]/np.linalg.norm(info_pca.components_[0])
alignment=float(abs(np.dot(tau_geom,tau_info)))

geom_proj=geom_disp@tau_geom
info_proj=info_disp@tau_info
cross_corr=float(np.corrcoef(geom_proj,info_proj)[0,1])

H1_tau_equivalence=bool(alignment>0.90)
H2_cross_correlation=bool(abs(cross_corr)>0.90)
H3_dual_lowrank=bool(geom_pca.explained_variance_ratio_[0]>0.90 and info_pca.explained_variance_ratio_[0]>0.90)

RESULTS={"tau_geom":tau_geom.tolist(),"tau_info":tau_info.tolist(),"alignment":alignment,"cross_correlation":cross_corr,"geom_pc1":float(geom_pca.explained_variance_ratio_[0]),"info_pc1":float(info_pca.explained_variance_ratio_[0]),"checks":{"H1_tau_equivalence":H1_tau_equivalence,"H2_cross_correlation":H2_cross_correlation,"H3_dual_lowrank":H3_dual_lowrank}}

with open(os.path.join(ROOT,"T039_RESULTS.json"),"w") as f: json.dump(RESULTS,f,indent=2)
sha=hashlib.sha256(json.dumps(RESULTS,sort_keys=True).encode()).hexdigest()
with open(os.path.join(ROOT,"T039.sha256"),"w") as f: f.write(sha)
print(f"\n=== T039 DUAL TAU EQUIVALENCE ===\n{json.dumps(RESULTS,indent=2)}\nSHA256: {sha}")