#!/usr/bin/env python3
import os, json, numpy as np
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity

OUTDIR = "STRICT_PROOF_TRACK/T027_REMOVE_M2"
os.makedirs(OUTDIR, exist_ok=True)
SEEDS = [11,23,37,51,79]

def make_signals(seed, N=4096):
    np.random.seed(seed); t=np.linspace(0,1,N)
    sigs={}
    sigs["chirp"]=np.sin(2*np.pi*(8*t+32*t**2))
    sigs["rw_trend"]=np.cumsum(np.random.randn(N))
    sigs["telegraph"]=np.random.choice([-1,1],size=N)
    spikes=np.zeros(N); idx=np.random.choice(np.arange(N),40); spikes[idx]=np.random.randn(40)*5; sigs["spikes"]=spikes
    sigs["pink_noise"]=np.cumsum(np.random.randn(N))/np.std(np.cumsum(np.random.randn(N)))
    sigs["square"]=np.sign(np.sin(2*np.pi*10*t))
    x=np.zeros(N); x[0]=0.2
    for i in range(N-1): x[i+1]=3.99*x[i]*(1-x[i])
    sigs["chaotic_logistic"]=x
    return sigs

def replay(x): h=len(x)//2; return np.concatenate([x[:h],x[:h]])

def signed_ordinal_flow(x): dx=np.diff(x); return float(np.mean(np.sign(dx[:-1]*dx[1:])) if len(dx)>1 else 0.0)
def half_corr(x): h=len(x)//2; a,b=x[:h],x[h:h+h]; return float(np.corrcoef(a,b)[0,1]) if np.std(a)>0 and np.std(b)>0 else 0.0
def signed_compress(x): dx=np.sign(np.diff(x)); p=np.clip(np.mean(dx>0),1e-6,1-1e-6); return float(-(p*np.log2(p)+(1-p)*np.log2(1-p)))
def amp_transition(x): q=np.quantile(np.abs(x),0.75); return float(np.mean(np.abs(np.diff((np.abs(x)>q).astype(int)))))

def embed_full(x): return np.array([signed_ordinal_flow(x),half_corr(x),signed_compress(x),amp_transition(x)])
def embed_nom2(x): return np.array([signed_ordinal_flow(x),signed_compress(x),amp_transition(x)])

full_disp, nom2_disp = [], []
for seed in SEEDS:
    for domain,x in make_signals(seed).items():
        full_disp.append(embed_full(replay(x))-embed_full(x))
        nom2_disp.append(embed_nom2(replay(x))-embed_nom2(x))

full_disp, nom2_disp = np.array(full_disp), np.array(nom2_disp)
pca_full, pca_nom2 = PCA().fit(full_disp), PCA().fit(nom2_disp)

tau_full_var=float(pca_full.explained_variance_ratio_[0])
tau_nom2_var=float(pca_nom2.explained_variance_ratio_[0])
tau_full=pca_full.components_[0]
tau_nom2=pca_nom2.components_[0]

alignments_full=[abs(cosine_similarity([full_disp[i]],[tau_full])[0][0]) for i in range(len(full_disp))]
alignments_nom2=[abs(cosine_similarity([nom2_disp[i]],[tau_nom2])[0][0]) for i in range(len(nom2_disp))]
mean_align_full, mean_align_nom2 = float(np.mean(alignments_full)), float(np.mean(alignments_nom2))

tau_collapse=tau_full_var-tau_nom2_var
align_collapse=mean_align_full-mean_align_nom2

H1_tau_destroyed=bool(tau_nom2_var<0.80)
H2_alignment_destroyed=bool(mean_align_nom2<0.80)
H3_m2_critical=bool(tau_collapse>0.15)

interpretation="If removing m2 destroys τ, theorem validated. If τ survives, theorem incomplete."

output={"tau_full_variance":tau_full_var,"tau_nom2_variance":tau_nom2_var,"mean_align_full":mean_align_full,"mean_align_nom2":mean_align_nom2,"tau_collapse":tau_collapse,"align_collapse":align_collapse,"H1_tau_destroyed":H1_tau_destroyed,"H2_alignment_destroyed":H2_alignment_destroyed,"H3_m2_critical":H3_m2_critical,"interpretation":interpretation}
with open(os.path.join(OUTDIR,"T027_results.json"),"w") as f: json.dump(output,f,indent=2)
print("=== T027 REMOVE M2 ABLATION ===")
for k,v in output.items(): print(f"{k}: {v}")
print(f"\nSaved -> {OUTDIR}")