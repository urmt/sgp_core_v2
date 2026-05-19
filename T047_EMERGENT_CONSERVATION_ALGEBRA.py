#!/usr/bin/env python3
import numpy as np
from sklearn.decomposition import PCA
from scipy.stats import spearmanr
import json

np.random.seed(7)

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

trajectories=[]
for i in range(400):
    x0=random_signal(); traj=[]
    y=x0.copy()
    for t in range(10):
        y=np.random.choice(list(OPS.values()))(y)
        traj.append(embed(y))
    trajectories.append(np.array(traj))

all_states=np.concatenate(trajectories,axis=0)
global_var=np.var(all_states,axis=0)

traj_drift=[]
for k in range(4):
    drifts=[np.mean(np.abs(np.diff(traj[:,k]))) for traj in trajectories]
    traj_drift.append(np.mean(drifts))
traj_drift=np.array(traj_drift)

conservation_scores=global_var/(traj_drift+1e-9)

flow_vectors=np.concatenate([np.diff(traj,axis=0) for traj in trajectories],axis=0)
pca=PCA(); pca.fit(flow_vectors)
tau=pca.components_[0]
mean_alignment=np.mean([abs(np.dot(v,tau)/(np.linalg.norm(v)*np.linalg.norm(tau)+1e-9)) for v in flow_vectors])

corrs=[abs(spearmanr(np.concatenate([traj[:-1,k] for traj in trajectories]),np.concatenate([np.linalg.norm(np.diff(traj,axis=0),axis=1) for traj in trajectories])).correlation) for k in range(4)]
max_coupled_metric=int(np.argmax(corrs))

commuting=0; total=0
for a in OPS.keys():
    for b in OPS.keys():
        x=random_signal()
        d=np.linalg.norm(embed(OPS[a](OPS[b](x)))-embed(OPS[b](OPS[a](x))))
        if d<0.1: commuting+=1
        total+=1
commutation_ratio=commuting/total

results={"conservation_scores":conservation_scores.tolist(),"mean_alignment":float(mean_alignment),"flow_metric_couplings":corrs,"max_coupled_metric":max_coupled_metric,"commutation_ratio":float(commutation_ratio),"H1_conserved_quantity":bool(np.max(conservation_scores)>5.0),"H2_flow_alignment":bool(mean_alignment>0.75),"H3_semigroup_structure":bool(commutation_ratio>0.50),"H4_flow_coupling":bool(np.max(corrs)>0.50)}
print(json.dumps(results,indent=2))