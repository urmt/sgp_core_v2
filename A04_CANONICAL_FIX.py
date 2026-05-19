#!/usr/bin/env python3
import json, zlib, numpy as np, pandas as pd
from pathlib import Path
from sklearn.preprocessing import RobustScaler
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.metrics import confusion_matrix

SEEDS=[11,23,37,51,67,79,97,111,149,211]
VARIANTS=["base","reverse","swap","replay","stitch"]
MK=["m1","m2","m3","m4"]
OUTDIR=Path("A04_CANONICAL_CONFUSION")
OUTDIR.mkdir(exist_ok=True)

def make_signals(seed):
    np.random.seed(seed); N=4096; t=np.linspace(0,1,N)
    rw=np.cumsum(np.random.randn(N))+0.002*np.arange(N)
    rs=np.zeros(N)
    cuts=[0,1200,2400,3200,4096]; mus=[0,2,-1,3]
    for i in range(4): rs[cuts[i]:cuts[i+1]]=mus[i]+0.5*np.random.randn(cuts[i+1]-cuts[i])
    x=0.217; logistic=[]
    for _ in range(N): x=3.99*x*(1-x); logistic.append(x)
    logistic=np.array(logistic)
    chirp=np.sin(2*np.pi*(8*t+40*t**2))
    coupled=np.sin(2*np.pi*7*t)+0.4*np.sin(2*np.pi*(13*t+1.5*np.sin(2*np.pi*0.3*t)))
    return {"rw_trend":rw,"regime_switch":rs,"chaotic_logistic":logistic,"chirp":chirp,"coupled_osc":coupled}

def make_variants(x):
    n=len(x); thirds=np.array_split(x,3)
    return {"base":x,"reverse":x[::-1],"swap":np.concatenate([x[n//2:],x[:n//2]]),"replay":np.concatenate([x[:n//2],x[:n//2]]),"stitch":np.concatenate([thirds[2],thirds[0],thirds[1]])}

def signed_compress(x):
    q=np.sign(np.diff(x)).astype(np.int8); raw=q.tobytes(); c=len(zlib.compress(raw)); return np.sign(np.mean(q))*(len(raw)/c)
def half_corr(x):
    n=len(x)//2; return np.corrcoef(x[:n],x[n:2*n])[0,1]
def signed_ordinal_flow(x,m=5):
    if len(x)<m+1: return 0.0
    pats={}; total=0
    for i in range(len(x)-m): w=x[i:i+m]; p=tuple(np.argsort(w)); d=np.sign(w[-1]-w[0]); key=(p,d); pats[key]=pats.get(key,0)+1; total+=1
    if total==0: return 0.0
    H=0.0
    for v in pats.values(): p=v/total; H-=p*np.log2(p+1e-12)
    return H
def amp_transition_asymmetry(x,k=5):
    bins=np.percentile(x,np.linspace(0,100,k+1)); s=np.digitize(x,bins[1:-1]); F=np.zeros((k,k))
    for a,b in zip(s[:-1],s[1:]): F[a,b]+=1
    F/=F.sum()+1e-12; A=0.0
    for i in range(k):
        for j in range(i+1,k): A+=(j-i)*(F[i,j]-F[j,i])
    return A

print("Building embeddings...")
rows=[]
for seed in SEEDS:
    sigs=make_signals(seed)
    for domain,sig in sigs.items():
        for variant,y in make_variants(sig).items():
            rows.append({"seed":seed,"domain":domain,"variant":variant,"m1":signed_compress(y),"m2":half_corr(y),"m3":signed_ordinal_flow(y),"m4":amp_transition_asymmetry(y)})
df=pd.DataFrame(rows)
df[MK]=RobustScaler().fit_transform(df[MK])
print(f"  {len(df)} embeddings")

print("\n=== A04 CANONICAL CONFUSION ===")
summary={}
for domain in sorted(df.domain.unique()):
    sub=df[df.domain==domain]
    preds,trues=[],[]
    for seed in SEEDS:
        train=sub[sub.seed!=seed]; test=sub[sub.seed==seed]
        lda=LinearDiscriminantAnalysis().fit(train[MK].values,train["variant"].values)
        preds.extend(lda.predict(test[MK].values)); trues.extend(test["variant"].values)
    cm=confusion_matrix(trues,preds,labels=VARIANTS)
    acc=np.trace(cm)/np.sum(cm)
    summary[domain]={"accuracy":float(acc),"confusion_matrix":cm.tolist()}
    print(f"\n{domain}: acc={acc:.3f}")
    print(pd.DataFrame(cm,index=VARIANTS,columns=VARIANTS))

with open(OUTDIR/"canonical_confusion_summary.json","w") as f: json.dump(summary,f,indent=2)
print(f"\nSaved to {OUTDIR}")