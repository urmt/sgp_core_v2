#!/usr/bin/env python3
import os, json, hashlib, numpy as np
from sklearn.decomposition import PCA
from sklearn.metrics import pairwise_distances

OUTDIR = "STRICT_T013_ATTRACTOR"; os.makedirs(OUTDIR, exist_ok=True)
N = 512; SEEDS = [11,23,37,51,79,101,149,211,307,401]

def make_signals(seed):
    np.random.seed(seed); t = np.linspace(0,1,N)
    chirp = np.sin(2*np.pi*(5*t + 20*t*t))
    rw = np.cumsum(np.random.randn(N)) + 0.002*np.arange(N)
    reg = np.concatenate([np.random.normal(-1,0.3,N//2), np.random.normal(+1,0.3,N//2)])
    x = 0.123456
    logistic = [x := 3.99*x*(1-x) for _ in range(N)]
    coupled = np.sin(2*np.pi*7*t) + 0.5*np.sin(2*np.pi*13*t + 0.3)
    return {"chirp":chirp,"rw_trend":rw,"regime_switch":reg,"chaotic_logistic":np.array(logistic),"coupled_osc":coupled}

def identity(x): return x.copy()
def reverse(x): return x[::-1]
def swap_halves(x): h=len(x)//2; return np.concatenate([x[h:],x[:h]])
def replay(x): h=len(x)//2; return np.concatenate([x[:h],x[:h]])
def stitch(x): h=len(x)//2; return np.concatenate([x[:h],x[-h:]])

TRANSFORMS = {"base":identity,"reverse":reverse,"swap":swap_halves,"replay":replay,"stitch":stitch}

def signed_ordinal_flow(x):
    dx=np.diff(x); s=np.sign(dx); return float(np.mean(s[:-1]*s[1:])) if len(s)>1 else 0.0

def half_corr(x):
    h=len(x)//2; a,b=x[:h],x[h:]; return float(np.corrcoef(a,b)[0,1]) if np.std(a)>0 and np.std(b)>0 else 0.0

def signed_compress(x):
    dx=np.diff(x); bits=(dx>0).astype(np.uint8); p=np.mean(bits); return float(-(p*np.log2(p)+(1-p)*np.log2(1-p))) if 0<p<1 else 0.0

def amp_transition(x):
    q=np.quantile(np.abs(x),0.75); high=(np.abs(x)>q).astype(int); return float(np.mean(high[:-1]!=high[1:])) if len(high)>1 else 0.0

def embed(x): return np.array([signed_ordinal_flow(x),half_corr(x),signed_compress(x),amp_transition(x)])

records=[]
for seed in SEEDS:
    sigs=make_signals(seed)
    for domain,sig in sigs.items():
        for tname,tfun in TRANSFORMS.items():
            records.append({"seed":seed,"domain":domain,"variant":tname,"embedding":embed(tfun(sig))})

fixedpoint_errors,base_to_replay,replay_to_rereplay=[],[],[]
for seed in SEEDS:
    sigs=make_signals(seed)
    for domain,sig in sigs.items():
        r1,r2=replay(sig),replay(replay(sig))
        e1,e2=embed(r1),embed(r2)
        fixedpoint_errors.append(float(np.linalg.norm(e1-e2)))
        base_to_replay.append(float(np.linalg.norm(embed(sig)-e1)))
        replay_to_rereplay.append(float(np.linalg.norm(e1-e2)))

fixedpoint_error_mean=float(np.mean(fixedpoint_errors))

replay_embeds=np.array([r["embedding"] for r in records if r["variant"]=="replay"])
other_embeds=np.array([r["embedding"] for r in records if r["variant"]!="replay"])
replay_cov=float(np.trace(np.cov(replay_embeds.T)))
other_cov=float(np.trace(np.cov(other_embeds.T)))
compression_ratio=replay_cov/other_cov

all_embeds=np.array([r["embedding"] for r in records])
pc1=float(PCA(n_components=4).fit(all_embeds).explained_variance_ratio_[0])

D=pairwise_distances(replay_embeds)
replay_cluster_radius=float(np.mean(D[np.triu_indices_from(D,1)]))

H1_fixedpoint=bool(fixedpoint_error_mean<1e-6)
H2_projection=bool(np.mean(replay_to_rereplay)<0.01*np.mean(base_to_replay))
H3_attractor=bool(compression_ratio<0.5)

results={"fixedpoint_error_mean":fixedpoint_error_mean,"base_to_replay_mean":float(np.mean(base_to_replay)),"replay_to_rereplay_mean":float(np.mean(replay_to_rereplay)),"replay_covariance":replay_cov,"other_covariance":other_cov,"compression_ratio":compression_ratio,"replay_cluster_radius":replay_cluster_radius,"pc1_explained_variance":pc1,"H1_fixedpoint":H1_fixedpoint,"H2_projection":H2_projection,"H3_attractor":H3_attractor}

json_path=os.path.join(OUTDIR,"attractor_results.json")
with open(json_path,"w") as f: json.dump(results,f,indent=2)
sha=hashlib.sha256(open(json_path,"rb").read()).hexdigest()
with open(os.path.join(OUTDIR,"attractor_results.sha256"),"w") as f: f.write(sha)
np.save(os.path.join(OUTDIR,"replay_fixedpoint.npy"),replay_embeds)

print("=== T013 ATTRACTOR / FIXED-POINT ANALYSIS ===")
for k,v in results.items(): print(f"{k}: {v}")
print(f"\nSHA256: {sha}")
print("\nDONE.")