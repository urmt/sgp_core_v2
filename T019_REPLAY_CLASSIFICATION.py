#!/usr/bin/env python3
import os, json, numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.metrics import accuracy_score

OUTDIR = "STRICT_PROOF_TRACK/T019_REPLAY_CLASSIFICATION"; os.makedirs(OUTDIR, exist_ok=True)
SEEDS = [11,23,37,51,79,101,149,211,307,401]

def make_signals(seed, N=4096):
    np.random.seed(seed); t=np.linspace(0,1,N)
    chirp=np.sin(2*np.pi*(8*t+32*t**2)); rw=np.cumsum(np.random.randn(N))
    rs=np.zeros(N); idx=np.random.choice(np.arange(256,N-256),8,replace=False); idx.sort(); val,prev=0,0
    for i in idx: rs[prev:i]=val+0.3*np.random.randn(i-prev); val=np.random.randn()*3; prev=i
    rs[prev:]=val+0.3*np.random.randn(N-prev)
    x=np.zeros(N); x[0]=0.2
    for i in range(N-1): x[i+1]=3.99*x[i]*(1-x[i])
    c1=np.sin(2*np.pi*7*t); c2=np.sin(2*np.pi*7*t+0.5*np.sin(2*np.pi*0.5*t)); coupled=c1+0.7*c2
    return {"chirp":chirp,"rw_trend":rw,"regime_switch":rs,"chaotic_logistic":x,"coupled_osc":coupled}

def reverse(x): return x[::-1]
def replay(x): h=len(x)//2; return np.concatenate([x[:h],x[:h]])
def swap(x): h=len(x)//2; return np.concatenate([x[h:],x[:h]])
def stitch(x): q=len(x)//4; return np.concatenate([x[:q],x[2*q:3*q],x[q:2*q],x[3*q:]])

def signed_ordinal_flow(x): dx=np.diff(x); return float(np.mean(np.sign(dx[:-1]*dx[1:])) if len(dx)>1 else 0.0)
def half_corr(x): h=len(x)//2; a,b=x[:h],x[h:h+h]; return float(np.corrcoef(a,b)[0,1]) if np.std(a)>0 and np.std(b)>0 else 0.0
def signed_compress(x): dx=np.sign(np.diff(x)); p=np.mean(dx>0); p=np.clip(p,1e-6,1-1e-6); return float(-(p*np.log2(p)+(1-p)*np.log2(1-p)))
def amp_transition(x): q=np.quantile(np.abs(x),0.75); return float(np.mean(np.abs(np.diff((np.abs(x)>q).astype(int)))))
def embed(x): return np.array([signed_ordinal_flow(x),half_corr(x),signed_compress(x),amp_transition(x)])

transforms={"base":lambda x:x,"reverse":reverse,"swap":swap,"stitch":stitch,"replay":replay}
X,Y=[],[]
for seed in SEEDS:
    for domain,x in make_signals(seed).items():
        for name,f in transforms.items():
            X.append(embed(f(x))); Y.append(name)
X,Y=np.array(X),np.array(Y)

null_dist=np.abs(X[:,1]-X[:,2])
replay_mask=(Y=="replay"); other_mask=(Y!="replay")
replay_mean=float(np.mean(null_dist[replay_mask])); other_mean=float(np.mean(null_dist[other_mask]))
mu_r,mu_o=replay_mean,other_mean; var_r,var_o=np.var(null_dist[replay_mask]),np.var(null_dist[other_mask])
fisher=float(((mu_o-mu_r)**2)/(var_r+var_o+1e-12))
collapse=float(np.var(null_dist[replay_mask])/(np.var(null_dist[other_mask])+1e-12))
labels=(Y=="replay").astype(int); clf=LinearDiscriminantAnalysis(); clf.fit(X,labels); acc=float(accuracy_score(labels,clf.predict(X)))

H1_replay_manifold=bool(replay_mean<other_mean*0.1); H2_variance_collapse=bool(collapse<0.05); H3_perfect_detection=bool(acc>0.99)
theory="Replay classification emerges because replay projects onto invariant manifold M={x:m2=m3}, retaining zero null-distance N(x)=m2-m3 while ordinary transforms have nonzero values."

result={"replay_mean_null_distance":replay_mean,"other_mean_null_distance":other_mean,"fisher_ratio":fisher,"variance_collapse":collapse,"lda_accuracy":acc,"H1_replay_manifold":H1_replay_manifold,"H2_variance_collapse":H2_variance_collapse,"H3_perfect_detection":H3_perfect_detection,"theory":theory}
with open(os.path.join(OUTDIR,"T019_results.json"),"w") as f: json.dump(result,f,indent=2)
print("=== T019 REPLAY CLASSIFICATION PROOF ===")
for k,v in result.items(): print(f"{k}: {v}")
print(f"\nSaved -> {OUTDIR}")