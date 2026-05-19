#!/usr/bin/env python3
import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from scipy.stats import entropy
import json

np.random.seed(42)

N=500; L=256
states=np.random.randn(N,L)

def replay(x):
    h=len(x)//2
    return np.concatenate([x[:h],x[:h]])

def reverse(x):
    return x[::-1]

def stitch(x):
    h=len(x)//2
    return np.concatenate([x[:h],x[-h:]])

def swap(x):
    h=len(x)//2
    return np.concatenate([x[h:],x[:h]])

OPS={"R":replay,"V":reverse,"S":stitch,"W":swap}

def embed(x):
    h=len(x)//2; a,b=x[:h],x[h:]
    m1=np.mean(np.sign(np.diff(x))) if len(x)>1 else 0
    m2=np.corrcoef(a,b)[0,1] if np.std(a)>0 and np.std(b)>0 else 0
    m3=np.mean(np.abs(np.diff(x)))
    fft=np.abs(np.fft.rfft(x)); p=fft/(fft.sum()+1e-12); m4=entropy(p)
    return np.array([m1,m2,m3,m4])

trajectories=[]
for s in states:
    x=s.copy()
    for step in range(12):
        op=np.random.choice(list(OPS.keys()))
        x=OPS[op](x)
        trajectories.append(embed(x))

X=np.array(trajectories)
pca=PCA().fit(X)
pc1=pca.explained_variance_ratio_[0]
dim95=np.argmax(np.cumsum(pca.explained_variance_ratio_)>0.95)+1

kmeans=KMeans(n_clusters=2,random_state=0).fit(X)
cluster_sizes=np.bincount(kmeans.labels_)
balance=np.min(cluster_sizes)/np.max(cluster_sizes)

centroid=X.mean(axis=0)
distances=np.linalg.norm(X-centroid,axis=1)
attractor_radius=distances.mean()

results={"pc1":float(pc1),"dim95":int(dim95),"cluster_balance":float(balance),"attractor_radius":float(attractor_radius),"H1_lowrank_emergence":bool(pc1>0.8),"H2_sector_emergence":bool(balance>0.2),"H3_attractor_emergence":bool(attractor_radius<2.0)}
print(json.dumps(results,indent=2))