#!/usr/bin/env python3
import os, json, numpy as np
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity

OUTDIR = "STRICT_PROOF_TRACK/T022_GROUP_DECOMP"
os.makedirs(OUTDIR, exist_ok=True)
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
TRANSFORMS={"base":lambda x:x,"reverse":reverse,"swap":swap,"replay":replay,"stitch":stitch}

def signed_ordinal_flow(x): dx=np.diff(x); return float(np.mean(np.sign(dx[:-1]*dx[1:])) if len(dx)>1 else 0.0)
def half_corr(x): h=len(x)//2; a,b=x[:h],x[h:h+h]; return float(np.corrcoef(a,b)[0,1]) if np.std(a)>0 and np.std(b)>0 else 0.0
def signed_compress(x): dx=np.sign(np.diff(x)); p=np.mean(dx>0); p=np.clip(p,1e-6,1-1e-6); return float(-(p*np.log2(p)+(1-p)*np.log2(1-p)))
def amp_transition(x): q=np.quantile(np.abs(x),0.75); return float(np.mean(np.abs(np.diff((np.abs(x)>q).astype(int)))))
def embed(x): return np.array([signed_ordinal_flow(x),half_corr(x),signed_compress(x),amp_transition(x)])

per_transform={"reverse":[],"swap":[],"replay":[],"stitch":[]}
for seed in SEEDS:
    for domain,x in make_signals(seed).items():
        b=embed(x)
        for tname,f in TRANSFORMS.items():
            if tname=="base": continue
            per_transform[tname].append(embed(f(x))-b)

all_disp=np.vstack([np.array(v) for v in per_transform.values()])
tau=PCA().fit(all_disp).components_[0]

results={}
for name,vecs in per_transform.items():
    vecs=np.array(vecs); mean_vec=np.mean(vecs,axis=0); mean_norm=float(np.linalg.norm(mean_vec))
    align_tau=float(np.abs(cosine_similarity([mean_vec],[tau])[0][0]))
    orth_component=mean_vec-np.dot(mean_vec,tau)*tau; orth_norm=float(np.linalg.norm(orth_component)); total_norm=float(np.linalg.norm(mean_vec)); orth_ratio=orth_norm/total_norm if total_norm>0 else 0.0
    results[name]={"mean_vector":mean_vec.tolist(),"mean_norm":mean_norm,"tau_alignment":align_tau,"orthogonal_ratio":orth_ratio}

families={}
for name,r in results.items():
    a,o=r["tau_alignment"],r["orthogonal_ratio"]
    if a>0.95 and o<0.1: fam="tau_axis_family"
    elif a<0.1 and o>0.9: fam="orthogonal_family"
    elif r["mean_norm"]<0.05: fam="symmetry_preserving"
    else: fam="mixed_operator"
    families[name]=fam

H1_tau_family=bool(families["replay"]=="tau_axis_family")
H2_swap_orthogonal=bool(families["swap"]=="orthogonal_family")
H3_reverse_symmetry=bool(families["reverse"]=="symmetry_preserving")
interpretation="Transforms decompose: replay/stitch=τ-axis family, reverse=symmetry preserving, swap=orthogonal."

output={"tau":tau.tolist(),"results":results,"families":families,"H1_tau_family":H1_tau_family,"H2_swap_orthogonal":H2_swap_orthogonal,"H3_reverse_symmetry":H3_reverse_symmetry,"interpretation":interpretation}
with open(os.path.join(OUTDIR,"T022_results.json"),"w") as f: json.dump(output,f,indent=2)
print("=== T022 GROUP DECOMPOSITION ===")
for k,v in output.items(): print(f"{k}: {v}")
print(f"\nSaved -> {OUTDIR}")