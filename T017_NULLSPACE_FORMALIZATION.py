#!/usr/bin/env python3
import os, json, numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

OUTDIR = "STRICT_PROOF_TRACK/T017_NULLSPACE_FORMALIZATION"; os.makedirs(OUTDIR, exist_ok=True)
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

BASE,REPLAY,DOMAINS=[],[],[]
for seed in SEEDS:
    for d,x in make_signals(seed).items():
        BASE.append(embed(x)); REPLAY.append(embed(replay(x))); DOMAINS.append(d)
BASE,REPLAY=np.array(BASE),np.array(REPLAY)

null_axis=np.array([0.0,0.706,-0.702,0.0]); null_axis/=np.linalg.norm(null_axis)
base_proj=BASE@null_axis; replay_proj=REPLAY@null_axis
collapse_ratio=float(np.var(replay_proj)/(np.var(base_proj)+1e-12))
mutual_proxy=float(np.corrcoef(base_proj,replay_proj)[0,1])

base_diff=np.abs(BASE[:,1]-BASE[:,2]); replay_diff=np.abs(REPLAY[:,1]-REPLAY[:,2])
base_abs,replay_abs=float(np.mean(base_diff)),float(np.mean(replay_diff))
alignment_gain=base_abs/(replay_abs+1e-12)

reg=LinearRegression(); reg.fit(base_proj.reshape(-1,1),replay_proj)
r2=float(r2_score(replay_proj,reg.predict(base_proj.reshape(-1,1))))

domain_results={}
for d in sorted(set(DOMAINS)):
    idx=[i for i,x in enumerate(DOMAINS) if x==d]
    bp,rp=base_proj[idx],replay_proj[idx]
    domain_results[d]={"collapse_ratio":float(np.var(rp)/(np.var(bp)+1e-12)),"corr":float(np.corrcoef(bp,rp)[0,1])}

H1_nullspace_confirmed=bool(collapse_ratio<0.05)
H2_alignment_manifold=bool(alignment_gain>5.0)
H3_information_destroyed=bool(abs(mutual_proxy)<0.2)

result={"collapse_ratio":collapse_ratio,"mutual_proxy_corr":mutual_proxy,"base_abs_m2_minus_m3":base_abs,"replay_abs_m2_minus_m3":replay_abs,"alignment_gain":alignment_gain,"regression_r2":r2,"domain_results":domain_results,"H1_nullspace_confirmed":H1_nullspace_confirmed,"H2_alignment_manifold":H2_alignment_manifold,"H3_information_destroyed":H3_information_destroyed}
with open(os.path.join(OUTDIR,"T017_results.json"),"w") as f: json.dump(result,f,indent=2)
print("=== T017 NULLSPACE FORMALIZATION ===")
for k,v in result.items(): print(f"{k}: {v}")
print(f"\nSaved -> {OUTDIR}")