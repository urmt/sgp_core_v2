#!/usr/bin/env python3
import numpy as np
from sklearn.decomposition import PCA
from sklearn.metrics import pairwise_distances
from scipy.spatial.distance import pdist
from scipy.stats import spearmanr
import json

np.random.seed(42)

def random_signal(n=256):
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

def random_chain(depth=5):
    return [np.random.choice(list(OPS.keys())) for _ in range(depth)]

def apply_chain(x, chain):
    y=x.copy()
    for c in chain: y=OPS[c](y)
    return y

embeddings,labels=[],[]
for i in range(1000):
    x=random_signal()
    chain=random_chain(depth=np.random.randint(1,7))
    y=apply_chain(x,chain)
    embeddings.append(embed(y))
    labels.append("".join(chain))

X=np.array(embeddings)
pca=PCA(); Z=pca.fit_transform(X)
pc1=pca.explained_variance_ratio_[0]
dim95=np.argmax(np.cumsum(pca.explained_variance_ratio_)>0.95)+1

D_embed=pairwise_distances(X)
D_latent=pairwise_distances(Z[:,:2])
metric_corr=spearmanr(pdist(X),pdist(Z[:,:2])).correlation

nearest=np.argsort(D_embed,axis=1)[:,1:6]
locality_scores=[]
for i in range(len(X)):
    nbrs=nearest[i]
    chain_lengths=[len(labels[j]) for j in nbrs]
    locality_scores.append(np.std(chain_lengths))
mean_locality=np.mean(locality_scores)

traj=[]
x0=random_signal()
for d in range(1,10):
    chain=random_chain(depth=d)
    y=apply_chain(x0,chain)
    traj.append(embed(y))

traj=np.array(traj)
diffs=np.diff(traj,axis=0)
angles=[]
for i in range(len(diffs)-1):
    a,b=diffs[i],diffs[i+1]
    c=np.clip(np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b)+1e-9),-1,1)
    angles.append(np.arccos(c))
mean_curvature=np.mean(angles)

results={"pc1":float(pc1),"dim95":int(dim95),"metric_corr":float(metric_corr),"mean_locality":float(mean_locality),"mean_curvature":float(mean_curvature),"H1_lowrank_geometry":bool(pc1>0.85),"H2_metric_emergence":bool(metric_corr>0.90),"H3_locality":bool(mean_locality<1.5),"H4_low_curvature":bool(mean_curvature<1.0)}
print(json.dumps(results,indent=2))