#!/usr/bin/env python3
import os, json, numpy as np
from numpy.linalg import svd, pinv
from sklearn.decomposition import PCA

OUTDIR = "STRICT_PROOF_TRACK/T016_NULLSPACE"; os.makedirs(OUTDIR, exist_ok=True)
SEEDS = [11,23,37,51,79,101,149,211,307,401]

def make_signals(seed, N=4096):
    np.random.seed(seed); t=np.linspace(0,1,N)
    chirp=np.sin(2*np.pi*(8*t+32*t**2))
    rw=np.cumsum(np.random.randn(N))
    rs=np.zeros(N); idx=np.random.choice(np.arange(256,N-256),8,replace=False); idx.sort(); val,prev=0,0
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
METRIC_NAMES=["m1_ordinal_flow","m2_half_corr","m3_signed_compress","m4_amp_transition"]

base_embeds,replay_embeds,domains=[],[],[]
for seed in SEEDS:
    for domain,x in make_signals(seed).items():
        base_embeds.append(embed(x)); replay_embeds.append(embed(replay(x))); domains.append(domain)

X,Y=np.array(base_embeds),np.array(replay_embeds)
A=pinv(X)@Y
U,S,Vt=svd(A); nullvec=Vt[-1]; nullvec=nullvec/(np.linalg.norm(nullvec)+1e-12)
metric_contrib={METRIC_NAMES[i]:float(nullvec[i]) for i in range(4)}
dominant_metric=METRIC_NAMES[int(np.argmax(np.abs(nullvec)))]

domain_proj={}
for d in sorted(set(domains)):
    idx=[i for i,x in enumerate(domains) if x==d]
    xb,yr=X[idx],Y[idx]
    proj_before=xb@nullvec; proj_after=yr@nullvec
    domain_proj[d]=float(np.std(proj_after)/(np.std(proj_before)+1e-12))

global_before,global_after=X@nullvec,Y@nullvec
suppression_ratio=float(np.std(global_after)/(np.std(global_before)+1e-12))
pca=PCA().fit(X); pc1=pca.components_[0]; alignment_pc1=float(np.dot(pc1,nullvec)/(np.linalg.norm(pc1)*np.linalg.norm(nullvec)+1e-12))

H1_single_metric=bool(np.max(np.abs(nullvec))>0.8)
H2_pc1_aligned=bool(abs(alignment_pc1)>0.8)
H3_true_annihilation=bool(suppression_ratio<0.1)

result={"singular_values":[float(s) for s in S],"nullspace_vector":nullvec.tolist(),"metric_contributions":metric_contrib,"dominant_metric":dominant_metric,"suppression_ratio":suppression_ratio,"domain_suppression":domain_proj,"pc1_alignment":alignment_pc1,"H1_single_metric":H1_single_metric,"H2_pc1_aligned":H2_pc1_aligned,"H3_true_annihilation":H3_true_annihilation}
with open(os.path.join(OUTDIR,"T016_results.json"),"w") as f: json.dump(result,f,indent=2)
print("=== T016 NULLSPACE IDENTIFICATION ===")
for k,v in result.items(): print(f"{k}: {v}")
print(f"\nSaved -> {OUTDIR}")