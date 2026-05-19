#!/usr/bin/env python3
import os, json, numpy as np
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors

OUTDIR = "STRICT_PROOF_TRACK/T014_REPLAY_DYNAMICS"; os.makedirs(OUTDIR, exist_ok=True)
SEEDS = [11,23,37,51,79,101,149,211,307,401]

def make_signals(seed, N=4096):
    np.random.seed(seed); t = np.linspace(0,1,N)
    chirp = np.sin(2*np.pi*(8*t + 32*t**2))
    rw = np.cumsum(np.random.randn(N))
    rs = np.zeros(N); idx = np.random.choice(np.arange(256,N-256),8,replace=False); idx.sort(); val,prev=0,0
    for i in idx: rs[prev:i]=val+0.3*np.random.randn(i-prev); val=np.random.randn()*3; prev=i
    rs[prev:]=val+0.3*np.random.randn(N-prev)
    x=np.zeros(N); x[0]=0.2
    for i in range(N-1): x[i+1]=3.99*x[i]*(1-x[i])
    c1=np.sin(2*np.pi*7*t); c2=np.sin(2*np.pi*7*t+0.5*np.sin(2*np.pi*0.5*t)); coupled=c1+0.7*c2
    return {"chirp":chirp,"rw_trend":rw,"regime_switch":rs,"chaotic_logistic":x,"coupled_osc":coupled}

def replay(x): h=len(x)//2; return np.concatenate([x[:h],x[:h]])

def signed_ordinal_flow(x): dx=np.diff(x); return float(np.mean(np.sign(dx[:-1]*dx[1:])) if len(dx)>1 else 0.0)
def half_corr(x): h=len(x)//2; a,b=x[:h],x[h:h+h]; return float(np.corrcoef(a,b)[0,1]) if np.std(a)>0 and np.std(b)>0 else 0.0
def signed_compress(x): dx=np.sign(np.diff(x)); p=np.mean(dx>0); p=np.clip(p,1e-6,1-1e-6); return float(-(p*np.log2(p)+(1-p)*np.log2(1-p)))
def amp_transition(x): q=np.quantile(np.abs(x),0.75); return float(np.mean(np.abs(np.diff((np.abs(x)>q).astype(int)))))
def embed(x): return np.array([signed_ordinal_flow(x),half_corr(x),signed_compress(x),amp_transition(x)])

records=[]
for seed in SEEDS:
    sigs=make_signals(seed)
    for domain,x in sigs.items():
        states,current=[],x.copy()
        for k in range(6): states.append(embed(current)); current=replay(current)
        states=np.array(states)
        step_dists=[float(np.linalg.norm(states[i+1]-states[i])) for i in range(len(states)-1)]
        contraction_ratio=float(np.mean(step_dists[1:])/(step_dists[0]+1e-12))
        records.append({"domain":domain,"states":states,"step_dists":step_dists,"contraction_ratio":contraction_ratio})

all_states=np.concatenate([r["states"] for r in records],axis=0)
pca=PCA().fit(all_states); pc1=float(pca.explained_variance_ratio_[0]); dim95=int(np.searchsorted(np.cumsum(pca.explained_variance_ratio_),0.95)+1)
nbrs=NearestNeighbors(n_neighbors=6).fit(all_states); dist,_=nbrs.kneighbors(all_states); local_dim=float(np.mean(np.log(5)/np.log((dist[:,-1]+1e-12)/(dist[:,1]+1e-12))))
cov=np.cov(all_states.T); eigvals=np.linalg.eigvalsh(cov); eigvals=eigvals[eigvals>1e-8]; jacobian_rank=int(len(eigvals))

H1_contraction=bool(np.mean([r["contraction_ratio"] for r in records])<1.0)
H2_lowrank=bool(jacobian_rank<=2)
H3_stabilizer=bool(pc1>0.95 and dim95<=2)

result={"pc1":pc1,"dim95":dim95,"local_dim":local_dim,"jacobian_rank":jacobian_rank,"mean_contraction_ratio":float(np.mean([r["contraction_ratio"] for r in records])),"H1_contraction":H1_contraction,"H2_lowrank":H2_lowrank,"H3_stabilizer":H3_stabilizer}
with open(os.path.join(OUTDIR,"T014_results.json"),"w") as f: json.dump(result,f,indent=2)

print("=== T014 REPLAY DYNAMICS ===")
for k,v in result.items(): print(f"{k}: {v}")
print(f"\nSaved -> {OUTDIR}")