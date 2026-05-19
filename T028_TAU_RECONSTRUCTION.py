#!/usr/bin/env python3
import os, json, numpy as np
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity

OUTDIR = "STRICT_PROOF_TRACK/T028_TAU_RECONSTRUCTION"
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
def half_corr(x): h=len(x)//2; a,b=x[:h],x[h:h+h]; return float(np.corrcoef(a,b)[0][1]) if np.std(a)>0 and np.std(b)>0 else 0.0
def signed_compress(x): dx=np.sign(np.diff(x)); p=np.clip(np.mean(dx>0),1e-6,1-1e-6); return float(-(p*np.log2(p)+(1-p)*np.log2(1-p)))
def amp_transition(x): q=np.quantile(np.abs(x),0.75); return float(np.mean(np.abs(np.diff((np.abs(x)>q).astype(int)))))
def embed(x): return np.array([signed_ordinal_flow(x),half_corr(x),signed_compress(x),amp_transition(x)])

disp, delta_means = [], []
for seed in SEEDS:
    for domain,x in make_signals(seed).items():
        d=embed(replay(x))-embed(x)
        disp.append(d); delta_means.append(d)

disp=np.array(delta_means)
pca=PCA(); pca.fit(disp)
tau_empirical=pca.components_[0]/np.linalg.norm(pca.components_[0])
tau_variance=float(pca.explained_variance_ratio_[0])

analytic=np.mean(delta_means,axis=0)/np.linalg.norm(np.mean(delta_means,axis=0))

alignment=float(cosine_similarity([tau_empirical],[analytic])[0][0])
mean_component_error=float(np.mean(np.abs(tau_empirical-analytic)))

H1_alignment=bool(alignment>0.95)
H2_low_error=bool(mean_component_error<0.10)
H3_tau_m2=bool(abs(analytic[1])>0.90)

interpretation="If analytic τ aligns with empirical, SFH-SGP becomes analytic geometric theory."

output={"tau_empirical":tau_empirical.tolist(),"tau_analytic":analytic.tolist(),"tau_variance":tau_variance,"alignment":alignment,"mean_component_error":mean_component_error,"H1_alignment":H1_alignment,"H2_low_error":H2_low_error,"H3_tau_m2":H3_tau_m2,"interpretation":interpretation}
with open(os.path.join(OUTDIR,"T028_results.json"),"w") as f: json.dump(output,f,indent=2)
print("=== T028 TAU RECONSTRUCTION ===")
for k,v in output.items(): print(f"{k}: {v}")
print(f"\nSaved -> {OUTDIR}")