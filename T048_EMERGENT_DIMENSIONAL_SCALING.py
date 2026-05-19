#!/usr/bin/env python3
import numpy as np
from sklearn.decomposition import PCA
from scipy.stats import linregress
from scipy.spatial.distance import pdist
import json

np.random.seed(1234)

def random_signal(n):
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

scales=[64,128,256,512,1024]
pc1s,dims95,intrinsic_dims=[],[],[]

for n in scales:
    embeddings=[]
    for i in range(400):
        x=random_signal(n)
        chain=[np.random.choice(list(OPS.keys())) for _ in range(np.random.randint(1,7))]
        y=x.copy()
        for c in chain: y=OPS[c](y)
        embeddings.append(embed(y))
    X=np.array(embeddings)
    pca=PCA(); pca.fit(X)
    evr=pca.explained_variance_ratio_
    pc1s.append(evr[0])
    dims95.append(np.argmax(np.cumsum(evr)>0.95)+1)
    D=pdist(X)
    eps=np.logspace(np.log10(np.min(D[D>0])+1e-9),np.log10(np.max(D)),20)
    counts=np.array([np.mean(D<e) for e in eps])
    valid=counts>0
    slope,_,r,_,_=linregress(np.log(eps[valid]),np.log(counts[valid]+1e-9))
    intrinsic_dims.append(slope)

pc1_stability=np.std(pc1s)
dim_stability=np.std(intrinsic_dims)
scale_slope,_,r,_,_=linregress(np.log(scales),intrinsic_dims)

results={"scales":scales,"pc1s":[float(x) for x in pc1s],"dims95":[int(x) for x in dims95],"intrinsic_dims":[float(x) for x in intrinsic_dims],"pc1_stability":float(pc1_stability),"dim_stability":float(dim_stability),"scale_slope":float(scale_slope),"H1_scale_invariant_lowrank":bool(np.mean(pc1s)>0.90),"H2_dimensional_stability":bool(dim_stability<0.5),"H3_effective_dimension":bool(np.mean(intrinsic_dims)<3.0),"H4_scale_consistency":bool(abs(scale_slope)<0.5)}
print(json.dumps(results,indent=2))