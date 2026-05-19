#!/usr/bin/env python3
import os, json, hashlib, numpy as np
from sklearn.decomposition import PCA

ROOT="T031_STRUCTURED_OPERATOR_CLOSURE"
os.makedirs(ROOT, exist_ok=True)
SEED=79
rng=np.random.default_rng(SEED)

def signed_ordinal_flow(x):
    d=np.diff(x)
    return np.mean(np.sign(d[:-1])*np.sign(d[1:])) if len(d)>1 else 0.0

def half_corr(x):
    n=len(x)//2
    a,b=x[:n],x[n:2*n]
    if np.std(a)==0 or np.std(b)==0: return 0.0
    return np.corrcoef(a,b)[0,1]

def signed_compress(x):
    q=np.round((x-np.mean(x))/(np.std(x)+1e-8),2)
    return -np.mean(np.abs(np.diff(q)))

def amp_transition(x):
    return np.mean(np.abs(np.diff(x)))

def embed(x):
    return np.array([signed_ordinal_flow(x),half_corr(x),signed_compress(x),amp_transition(x)])

N=512
t=np.linspace(0,1,N)

x_logistic=np.zeros(N); x_logistic[0]=0.2
for i in range(N-1): x_logistic[i+1]=3.99*x_logistic[i]*(1-x_logistic[i])

signals={"chirp":np.sin(2*np.pi*(3*t+12*t*t)),"rw_trend":np.cumsum(rng.normal(size=N))+0.002*np.arange(N),"telegraph":np.sign(np.sin(2*np.pi*8*t)),"pink_noise":np.cumsum(rng.normal(size=N)),"square":np.sign(np.sin(2*np.pi*5*t)),"chaotic_logistic":x_logistic}

def identity(x): return x
def reverse(x): return x[::-1]
def replay(x): h=len(x)//2; return np.concatenate([x[:h],x[:h]])
def stitch(x): q=len(x)//4; return np.concatenate([x[:q],x[2*q:3*q],x[q:2*q],x[3*q:]])
def swap(x): h=len(x)//2; return np.concatenate([x[h:],x[:h]])
OPS={"I":identity,"V":reverse,"R":replay,"S":stitch,"W":swap}

tau_disps=[]
for sig in signals.values():
    e0=embed(sig)
    for opname in ["R","S"]:
        e1=embed(OPS[opname](sig))
        tau_disps.append(e1-e0)

tau=np.linalg.norm(PCA(n_components=1).fit(np.array(tau_disps)).components_[0])
tau=PCA(n_components=1).fit(np.array(tau_disps)).components_[0]
tau=tau/np.linalg.norm(tau)
tau_var=float(PCA(n_components=1).fit(np.array(tau_disps)).explained_variance_ratio_[0])

pairs=[("R","S"),("S","R"),("R","V"),("V","R"),("S","V"),("V","S"),("R","W"),("W","R"),("S","W"),("W","S")]
results={}
for A,B in pairs:
    aligns,mags=[],[]
    for sig in signals.values():
        e0=embed(sig)
        d=embed(OPS[A](OPS[B](sig)))-e0
        mag=float(np.linalg.norm(d))
        mags.append(mag)
        aligns.append(abs(float(np.dot(d/mag,tau))) if mag>1e-12 else 0.0)
    results[f"{A}{B}"]={"mean_alignment":float(np.mean(aligns)),"std_alignment":float(np.std(aligns)),"mean_magnitude":float(np.mean(mags))}

absorption={}
for sn,sig in signals.items():
    r=embed(replay(sig))
    rs=embed(replay(stitch(sig)))
    sr=embed(stitch(replay(sig)))
    absorption[sn]={"R_after_S":float(np.linalg.norm(rs-r)),"S_after_R":float(np.linalg.norm(sr-r))}

tau_align=np.mean([results[k]["mean_alignment"] for k in ["RS","SR","RV","VR","SV","VS"]])
orth_align=np.mean([results[k]["mean_alignment"] for k in ["RW","WR","SW","WS"]])
mean_absorb=np.mean([np.mean([v["R_after_S"],v["S_after_R"]]) for v in absorption.values()])

H1_tau_closure=bool(tau_align>0.90)
H2_replay_absorbing=bool(mean_absorb<0.15)
H3_orthogonal_breaks=bool(orth_align<tau_align)

RESULTS={"seed":SEED,"tau_variance":tau_var,"tau_vector":tau.tolist(),"composition_results":results,"absorption":absorption,"summary":{"tau_family_alignment":float(tau_align),"orthogonal_alignment":float(orth_align),"mean_absorption_distance":float(mean_absorb)},"checks":{"H1_tau_closure":H1_tau_closure,"H2_replay_absorbing":H2_replay_absorbing,"H3_orthogonal_breaks":H3_orthogonal_breaks}}

with open(os.path.join(ROOT,"T031_RESULTS.json"),"w") as f: json.dump(RESULTS,f,indent=2)
sha=hashlib.sha256(json.dumps(RESULTS,sort_keys=True).encode()).hexdigest()
with open(os.path.join(ROOT,"T031.sha256"),"w") as f: f.write(sha)

print("\n=== T031 STRUCTURED OPERATOR CLOSURE ===\nτ variance:",round(tau_var,4))
print("\nComposition:")
for k,v in results.items(): print(f"{k}: align={v['mean_alignment']:.4f}, mag={v['mean_magnitude']:.4f}")
print("\nAbsorption:",{k:{"R(Sx)":v["R_after_S"],"S(Rx)":v["S_after_R"]} for k,v in absorption.items()})
print(f"\nChecks: H1={H1_tau_closure}, H2={H2_replay_absorbing}, H3={H3_orthogonal_breaks}\nSHA256: {sha}")