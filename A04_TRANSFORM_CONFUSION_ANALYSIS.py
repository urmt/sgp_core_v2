#!/usr/bin/env python3
import json, numpy as np, pandas as pd
from pathlib import Path
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import RobustScaler

SEEDS = [11, 23, 37, 51, 67, 79, 97, 111, 149, 211]
VARIANTS = ["base", "reverse", "swap", "replay", "stitch"]
MK = ["m1", "m2", "m3", "m4"]
OUTDIR = Path("A04_TRANSFORM_CONFUSION")
OUTDIR.mkdir(exist_ok=True)

def make_signals(seed):
    np.random.seed(seed); N=4096; t=np.linspace(0,1,N)
    rw = np.cumsum(np.random.randn(N)) + 20*t
    rs = np.zeros(N)
    for i in range(8): rs[i*N//8:(i+1)*N//8] = np.random.randn()*3 + 0.3*np.random.randn(N//8)
    x=0.2; logistic=[]
    for _ in range(N): x=3.99*x*(1-x); logistic.append(x)
    logistic=np.array(logistic)
    chirp=np.sin(2*np.pi*(8*t+40*t**2))
    coupled=np.sin(2*np.pi*7*t)+0.5*np.sin(2*np.pi*(13*t+2*np.sin(2*np.pi*0.5*t)))
    return {"rw_trend":rw,"regime_switch":rs,"chaotic_logistic":logistic,"chirp":chirp,"coupled_osc":coupled}

def make_variants(x):
    n=len(x); thirds=np.array_split(x,3)
    return {"base":x,"reverse":x[::-1],"swap":np.concatenate([x[n//2:],x[:n//2]]),"replay":np.concatenate([x[:n//2],x[:n//2]]),"stitch":np.concatenate([thirds[2],thirds[0],thirds[1]])}

def signed_compressibility(x):
    dx=np.diff(x); p=np.mean(dx>0); return -(p*np.log2(p+1e-12)+(1-p)*np.log2(1-p+1e-12))
def half_corr(x):
    n=len(x)//2; return np.corrcoef(x[:n],x[n:2*n])[0,1]
def pred_asymmetry(x,m=4,tau=1):
    N=len(x)-(m-1)*tau-1
    if N<10: return 0.0
    emb=np.column_stack([x[i:i+N] for i in range(0,m*tau,tau)])
    y=x[m*tau:m*tau+N]
    try:
        w_f=np.linalg.lstsq(emb,y,rcond=None)[0]
        pred_f=emb@w_f
        xr=x[::-1]
        emb_b=np.column_stack([xr[i:i+N] for i in range(0,m*tau,tau)])
        yb=xr[m*tau:m*tau+N]
        w_b=np.linalg.lstsq(emb_b,yb,rcond=None)[0]
        pred_b=emb_b@w_b
        ef=np.mean((y-pred_f)**2); eb=np.mean((yb-pred_b)**2)
        return np.log((eb+1e-9)/(ef+1e-9))
    except: return 0.0
def amp_transition_asymmetry(x,k=5):
    bins=np.percentile(x,np.linspace(0,100,k+1)); s=np.digitize(x,bins[1:-1]); n=k; F=np.zeros((n,n))
    for a,b in zip(s[:-1],s[1:]): F[a,b]+=1
    F/=F.sum()+1e-12; A=0.0
    for i in range(n):
        for j in range(i+1,n): A+=(j-i)*(F[i,j]-F[j,i])
    return A

print("Building embeddings...")
rows=[]
for seed in SEEDS:
    sigs=make_signals(seed)
    for domain,sig in sigs.items():
        for variant,y in make_variants(sig).items():
            rows.append({"seed":seed,"domain":domain,"variant":variant,"m1":signed_compressibility(y),"m2":half_corr(y),"m3":pred_asymmetry(y),"m4":amp_transition_asymmetry(y)})
df=pd.DataFrame(rows)
df[MK]=RobustScaler().fit_transform(df[MK])
print(f"  {len(df)} embeddings")

print("\n=== A04 TRANSFORM CONFUSION ANALYSIS ===")
summary={}
for domain in sorted(df.domain.unique()):
    sub=df[df.domain==domain].copy()
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

with open(OUTDIR/"transform_confusion_summary.json","w") as f: json.dump(summary,f,indent=2)
print(f"\nSaved to {OUTDIR}")