#!/usr/bin/env python3
import numpy as np
from sklearn.decomposition import PCA
from scipy.stats import spearmanr
import json

np.random.seed(123)

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

states,times=[],[]
for i in range(250):
    x0=random_signal()
    y=x0.copy()
    for t in range(8):
        y=np.random.choice(list(OPS.values()))(y)
        states.append(embed(y)); times.append(t)

X=np.array(states); times=np.array(times)
pca=PCA(); Z=pca.fit_transform(X)
pc1=pca.explained_variance_ratio_[0]
latent_time_corr=spearmanr(Z[:,0],times).correlation

forward_steps,backward_steps=[],[]
for i in range(250):
    for t in range(7):
        idx=i*8+t
        next_idx=i*8+t+1
        dz=Z[next_idx,0]-Z[idx,0]
        if dz>0: forward_steps.append(dz)
        else: backward_steps.append(dz)

mean_forward=np.mean(forward_steps) if forward_steps else 0.0
mean_backward=np.mean(np.abs(backward_steps)) if backward_steps else 0.0
causal_bias=mean_forward/(mean_backward+1e-9)

replay_fixed_error=np.mean([np.linalg.norm(embed(replay(replay(x)))-embed(replay(x))) for x in [random_signal() for _ in range(300)]])

results={"pc1":float(pc1),"latent_time_corr":float(latent_time_corr),"causal_bias":float(causal_bias),"replay_fixed_error":float(replay_fixed_error),"H1_temporal_order":bool(abs(latent_time_corr)>0.70),"H2_causal_flow":bool(causal_bias>2.0),"H3_irreversibility":bool(replay_fixed_error<0.05)}
print(json.dumps(results,indent=2))