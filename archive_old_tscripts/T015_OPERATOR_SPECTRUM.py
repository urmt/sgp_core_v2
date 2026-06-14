#!/usr/bin/env python3
import os, json, numpy as np
from sklearn.decomposition import PCA
from numpy.linalg import svd, eigvals

OUTDIR = "STRICT_PROOF_TRACK/T015_OPERATOR_SPECTRUM"; os.makedirs(OUTDIR, exist_ok=True)
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

base_embeds, replay_embeds = [], []
for seed in SEEDS:
    for domain, x in make_signals(seed).items():
        base_embeds.append(embed(x)); replay_embeds.append(embed(replay(x)))

base_embeds=np.array(base_embeds); replay_embeds=np.array(replay_embeds)
X,Y=base_embeds,replay_embeds
A=np.linalg.pinv(X)@Y
evals=eigvals(A)
singular_values=svd(A,compute_uv=False)
spectral_radius=float(np.max(np.abs(evals)))
rank_est=int(np.sum(singular_values>1e-6))
A2=A@A
idempotency_error=float(np.linalg.norm(A2-A))
pca=PCA().fit(X); v1=pca.components_[0]; Av=A@v1; alignment=float(np.dot(v1,Av)/(np.linalg.norm(v1)*np.linalg.norm(Av)+1e-12))
sv_ratio=float(singular_values[-1]/(singular_values[0]+1e-12))
H1_projection=bool(idempotency_error<0.1)
H2_spectral_filter=bool(sv_ratio<0.2)
H3_invariant_direction=bool(alignment>0.95)

result={"spectral_radius":spectral_radius,"rank_estimate":rank_est,"singular_values":[float(s) for s in singular_values],"sv_ratio":sv_ratio,"idempotency_error":idempotency_error,"principal_alignment":alignment,"H1_projection":H1_projection,"H2_spectral_filter":H2_spectral_filter,"H3_invariant_direction":H3_invariant_direction}
with open(os.path.join(OUTDIR,"T015_results.json"),"w") as f: json.dump(result,f,indent=2)
print("=== T015 OPERATOR SPECTRUM ===")
for k,v in result.items(): print(f"{k}: {v}")
print(f"\nSaved -> {OUTDIR}")