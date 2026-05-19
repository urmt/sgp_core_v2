#!/usr/bin/env python3
import numpy as np
from sklearn.decomposition import PCA
from scipy.stats import entropy
import json

np.random.seed(123)

N=400; L=256
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

OPS=[replay,reverse,stitch,swap]

def embed(x):
    h=len(x)//2; a,b=x[:h],x[h:]
    m1=np.mean(np.sign(np.diff(x))) if len(x)>1 else 0
    m2=np.corrcoef(a,b)[0,1] if np.std(a)>0 and np.std(b)>0 else 0
    m3=np.mean(np.abs(np.diff(x)))
    fft=np.abs(np.fft.rfft(x)); p=fft/(fft.sum()+1e-12); m4=entropy(p)
    return np.array([m1,m2,m3,m4])

trajectories=[]
for s in states:
    x=s.copy(); traj=[]
    for step in range(20):
        x=np.random.choice(OPS)(x)
        traj.append(embed(x))
    trajectories.append(np.array(traj))

T=np.array(trajectories)
within_var=T.var(axis=1).mean(axis=0)
between_var=T.mean(axis=1).var(axis=0)
scores=between_var/(within_var+1e-12)

means=T.mean(axis=1)
pca=PCA().fit(means)
pc1=pca.explained_variance_ratio_[0]

metric_names=["m1_flow","m2_halfcorr","m3_compress","m4_entropy"]
most_conserved=metric_names[np.argmax(scores)]

step_means=T.mean(axis=0)
temporal_drift=np.mean(np.linalg.norm(step_means-step_means[0],axis=1))

results={"conservation_scores":scores.tolist(),"most_conserved":most_conserved,"trajectory_pc1":float(pc1),"temporal_drift":float(temporal_drift),"H1_conserved_quantity":bool(np.max(scores)>5.0),"H2_lowrank_trajectory":bool(pc1>0.8),"H3_temporal_stability":bool(temporal_drift<0.5)}
print(json.dumps(results,indent=2))