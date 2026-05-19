#!/usr/bin/env python3
import numpy as np
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from scipy.spatial.distance import pdist,squareform
import json

np.random.seed(2025)

def random_signal(n=512):
    return np.random.randn(n)

def replay(x):
    h=len(x)//2
    return np.concatenate([x[:h],x[:h]])

def reverse(x):
    return x[::-1]

def swap(x):
    h=len(x)//2
    return np.concatenate([x[h:],x[:h]])

def stitch(x):
    h=len(x)//2
    return np.concatenate([x[:h],x[::-1][:h]])

OPS={"R":replay,"V":reverse,"W":swap,"S":stitch}

def embed(x):
    h=len(x)//2; a,b=x[:h],x[h:]
    m1=np.mean(np.diff(x>np.median(x)))
    m2=np.corrcoef(a,b)[0,1]
    if np.isnan(m2): m2=0.0
    fft=np.abs(np.fft.rfft(x)); p=fft/(fft.sum()+1e-9)
    m3=-np.sum(p*np.log(p+1e-9))
    m4=np.std(np.diff(x))
    return np.array([m1,m2,m3,m4])

states=[]
for i in range(1500):
    x=random_signal()
    depth=np.random.randint(1,7)
    ops=np.random.choice(list(OPS.keys()),size=depth)
    y=x.copy()
    for op in ops: y=OPS[op](y)
    states.append(embed(y))

X=np.array(states)
pca=PCA(n_components=2); Z=pca.fit_transform(X)

nbrs=NearestNeighbors(n_neighbors=12).fit(Z)
dists,idx=nbrs.kneighbors(Z)

local_metric_stability,local_curvatures,transport_errors=[],[],[]
for i in range(len(Z)):
    neigh=Z[idx[i]]
    centered=neigh-neigh.mean(0)
    cov=np.cov(centered.T)
    eig=np.sort(np.linalg.eigvalsh(cov))[::-1]
    ratio=eig[0]/eig[1] if eig[1]>1e-9 else np.inf
    local_metric_stability.append(ratio)
    angles=[]
    base=neigh[0]
    for j in range(1,len(neigh)-1):
        a,b=neigh[j]-base,neigh[j+1]-base
        na,nb=np.linalg.norm(a),np.linalg.norm(b)
        if na<1e-9 or nb<1e-9: continue
        angles.append(np.arccos(np.clip(np.dot(a,b)/(na*nb),-1,1)))
    if len(angles)>0: local_curvatures.append(np.mean(angles))
    d0=np.linalg.norm(neigh[1]-base)
    transported=base+(neigh[2]-neigh[1])
    d1=np.linalg.norm(transported-neigh[2])
    transport_errors.append(abs(d1-d0))

D_high=squareform(pdist(X))
D_low=squareform(pdist(Z))
corr=np.corrcoef(D_high.flatten(),D_low.flatten())[0,1]

results={"metric_corr":float(corr),"mean_metric_stability":float(np.mean(local_metric_stability)),"mean_curvature":float(np.mean(local_curvatures)),"mean_transport_error":float(np.mean(transport_errors)),"pc1":float(pca.explained_variance_ratio_[0]),"H1_metric_preserved":bool(corr>0.95),"H2_local_anisotropy":bool(np.mean(local_metric_stability)>3.0),"H3_transport_consistency":bool(np.mean(transport_errors)<0.5),"H4_low_curvature":bool(np.mean(local_curvatures)<1.0)}
print(json.dumps(results,indent=2))