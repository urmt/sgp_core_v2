#!/usr/bin/env python3
import numpy as np
from sklearn.decomposition import PCA
from scipy.spatial.distance import euclidean
from scipy.stats import entropy
import json

np.random.seed(42)

def signals():
    t = np.linspace(0,1,512)
    return {
        "chirp": np.sin(2*np.pi*(5+20*t)*t),
        "rw": np.cumsum(np.random.randn(512)),
        "telegraph": np.sign(np.sin(2*np.pi*8*t)),
        "spikes": (np.random.rand(512)<0.03).astype(float),
        "pink": np.cumsum(np.random.randn(512)),
        "chaos": np.array([(lambda r=3.99,x0=0.2,n=512:[x0:=r*x0*(1-x0) for _ in range(n)])()]).flatten()
    }

def replay(x):
    h=len(x)//2
    return np.concatenate([x[:h],x[:h]])

def reverse(x):
    return x[::-1]

def swap(x):
    h=len(x)//2
    return np.concatenate([x[h:],x[:h]])

def stitch(x):
    q=len(x)//4
    return np.concatenate([x[:q],x[-q:],x[q:2*q],x[2*q:3*q]])

OPS = {"R": replay, "V": reverse, "W": swap, "S": stitch}

def embed(x):
    h=len(x)//2; a,b=x[:h],x[h:]
    m1=np.mean(np.abs(np.diff(x)))
    m2=np.corrcoef(a,b)[0,1] if np.std(a)>0 and np.std(b)>0 else 0
    m3=len(np.unique(np.round(x,2)))/len(x)
    m4=np.mean(np.abs(np.diff(np.abs(x))))
    return np.array([m1,m2,m3,m4])

def rollout(x, chain):
    traj=[embed(x)]; z=x.copy()
    for c in chain: z=OPS[c](z); traj.append(embed(z))
    return np.array(traj)

def curvature(traj):
    vecs=np.diff(traj,axis=0)
    if len(vecs)<2: return 0
    curvs=[]
    for i in range(len(vecs)-1):
        a,b=vecs[i],vecs[i+1]
        na,nb=np.linalg.norm(a),np.linalg.norm(b)
        if na<1e-8 or nb<1e-8: continue
        cos=np.clip(np.dot(a,b)/(na*nb),-1,1)
        curvs.append(np.arccos(cos))
    return np.mean(curvs) if curvs else 0

projection_chains=["R","RS","SR","RSS","SRS","RR"]
antisymmetry_chains=["V","W","VW","WV","VV","WW"]
sig=signals()

proj_curv,anti_curv=[],[]
proj_disp,anti_disp=[],[]

for name,x in sig.items():
    for ch in projection_chains:
        tr=rollout(x,ch)
        proj_curv.append(curvature(tr))
        proj_disp.append(euclidean(tr[0],tr[-1]))
    for ch in antisymmetry_chains:
        tr=rollout(x,ch)
        anti_curv.append(curvature(tr))
        anti_disp.append(euclidean(tr[0],tr[-1]))

proj_curv,anti_curv=np.mean(proj_curv),np.mean(anti_curv)
proj_disp,anti_disp=np.mean(proj_disp),np.mean(anti_disp)

results={"projection_curvature":float(proj_curv),"antisymmetry_curvature":float(anti_curv),"projection_displacement":float(proj_disp),"antisymmetry_displacement":float(anti_disp),"H1_projection_low_curvature":bool(proj_curv<anti_curv),"H2_projection_absorbing":bool(proj_disp<anti_disp),"H3_sector_differentiation":bool(abs(proj_curv-anti_curv)>0.1)}
print(json.dumps(results,indent=2))
with open("T042_sector_curvature_results.json","w") as f: json.dump(results,f,indent=2)