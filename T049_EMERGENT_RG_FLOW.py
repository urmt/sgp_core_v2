#!/usr/bin/env python3
import numpy as np
from sklearn.decomposition import PCA
from scipy.spatial.distance import pdist
from scipy.stats import pearsonr
import json

np.random.seed(77)

def random_signal(n=1024):
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

def coarse_grain(x,factor=2):
    n=len(x)//factor
    return np.array([np.mean(x[i*factor:(i+1)*factor]) for i in range(n)])

def embed(x):
    h=len(x)//2; a,b=x[:h],x[h:]
    m1=np.mean(np.diff(x>np.median(x)))
    m2=np.corrcoef(a,b)[0,1]
    if np.isnan(m2): m2=0.0
    fft=np.abs(np.fft.rfft(x)); p=fft/(fft.sum()+1e-9)
    m3=-np.sum(p*np.log(p+1e-9))
    m4=np.std(np.diff(x))
    return np.array([m1,m2,m3,m4])

def apply_chain(x,chain):
    y=x.copy()
    for c in chain: y=OPS[c](y)
    return y

fine_embeddings,coarse_embeddings=[],[]
for i in range(500):
    x=random_signal()
    chain=[np.random.choice(list(OPS.keys())) for _ in range(np.random.randint(1,8))]
    y=apply_chain(x,chain)
    fine_embeddings.append(embed(y))
    coarse_embeddings.append(embed(coarse_grain(y,2)))

fine_embeddings=np.array(fine_embeddings)
coarse_embeddings=np.array(coarse_embeddings)

pca_f=PCA(); pca_f.fit(fine_embeddings)
pca_c=PCA(); pca_c.fit(coarse_embeddings)
pc1_f=pca_f.explained_variance_ratio_[0]
pc1_c=pca_c.explained_variance_ratio_[0]
tau_f=pca_f.components_[0]
tau_c=pca_c.components_[0]
tau_alignment=np.abs(np.dot(tau_f,tau_c)/(np.linalg.norm(tau_f)*np.linalg.norm(tau_c)))

Df=pdist(fine_embeddings)
Dc=pdist(coarse_embeddings)
metric_corr=pearsonr(Df,Dc)[0]

mean_flow_diff=np.mean(np.linalg.norm(fine_embeddings-coarse_embeddings,axis=1))

replay_fine,replay_coarse=[],[]
for i in range(200):
    x=random_signal()
    y=replay(x)
    replay_fine.append(embed(y))
    replay_coarse.append(embed(coarse_grain(y)))
replay_shift=np.mean(np.linalg.norm(np.array(replay_fine)-np.array(replay_coarse),axis=1))

results={"fine_pc1":float(pc1_f),"coarse_pc1":float(pc1_c),"tau_alignment":float(tau_alignment),"metric_corr":float(metric_corr),"mean_flow_diff":float(mean_flow_diff),"replay_shift":float(replay_shift),"H1_rg_invariant_tau":bool(tau_alignment>0.90),"H2_metric_preservation":bool(metric_corr>0.90),"H3_lowrank_preserved":bool(pc1_f>0.90 and pc1_c>0.90),"H4_replay_fixedpoint_rg":bool(replay_shift<0.25)}
print(json.dumps(results,indent=2))