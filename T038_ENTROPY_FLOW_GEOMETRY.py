#!/usr/bin/env python3
import os, json, hashlib, numpy as np
from scipy.stats import entropy
from sklearn.decomposition import PCA

ROOT="T038_ENTROPY_FLOW_GEOMETRY"
os.makedirs(ROOT, exist_ok=True)
SEED=79
rng=np.random.default_rng(SEED)

N=512; t=np.linspace(0,1,N)
signals={"chirp":np.sin(2*np.pi*(3*t+10*t*t)),"rw":np.cumsum(rng.normal(size=N)),"telegraph":np.sign(np.sin(2*np.pi*8*t)),"spikes":(rng.random(N)<0.03).astype(float),"square":np.sign(np.sin(2*np.pi*5*t))}

def R(x): h=len(x)//2; return np.concatenate([x[:h],x[:h]])
def S(x): q=len(x)//4; return np.concatenate([x[:q],x[2*q:3*q],x[q:2*q],x[3*q:]])
def W(x): h=len(x)//2; return np.concatenate([x[h:],x[:h]])
def V(x): return x[::-1]
OPS={"R":R,"S":S,"W":W,"V":V}

def shannon_entropy(x,bins=64): hist,_=np.histogram(x,bins=bins,density=True); hist+=1e-12; return entropy(hist)
def local_variation(x): return np.mean(np.abs(np.diff(x)))
def spectral_entropy(x): ps=np.abs(np.fft.rfft(x))**2; ps/=np.sum(ps)+1e-12; return entropy(ps)
def compression_proxy(x): q=np.round((x-np.mean(x))/(np.std(x)+1e-8),2); return len(np.unique(q))/len(q)

rows=[]
for name,sig in signals.items():
    base={"H":shannon_entropy(sig),"LV":local_variation(sig),"SE":spectral_entropy(sig),"C":compression_proxy(sig)}
    for op_name,op in OPS.items():
        y=op(sig)
        after={"H":shannon_entropy(y),"LV":local_variation(y),"SE":spectral_entropy(y),"C":compression_proxy(y)}
        rows.append({"signal":name,"operator":op_name,"dH":after["H"]-base["H"],"dLV":after["LV"]-base["LV"],"dSE":after["SE"]-base["SE"],"dC":after["C"]-base["C"]})

X=np.array([[r["dH"],r["dLV"],r["dSE"],r["dC"]] for r in rows])
pca=PCA().fit(X)
pc1=float(pca.explained_variance_ratio_[0])
tau=pca.components_[0]

proj=[r for r in rows if r["operator"] in ["R","S"]]
anti=[r for r in rows if r["operator"] in ["W","V"]]
def avg(rows,key): return float(np.mean([r[key] for r in rows]))
summary={"projection":{"dH":avg(proj,"dH"),"dLV":avg(proj,"dLV"),"dSE":avg(proj,"dSE"),"dC":avg(proj,"dC")},"antisymmetry":{"dH":avg(anti,"dH"),"dLV":avg(anti,"dLV"),"dSE":avg(anti,"dSE"),"dC":avg(anti,"dC")}}

H1_compression_without_entropy_loss=bool(summary["projection"]["dC"]<0 and abs(summary["projection"]["dH"])<0.05)
H2_local_variation_growth=bool(summary["projection"]["dLV"]>0)
H3_flow_lowrank=bool(pc1>0.90)

RESULTS={"summary":summary,"tau_information_axis":tau.tolist(),"flow_pc1":pc1,"checks":{"H1_compression_without_entropy_loss":H1_compression_without_entropy_loss,"H2_local_variation_growth":H2_local_variation_growth,"H3_flow_lowrank":H3_flow_lowrank}}

with open(os.path.join(ROOT,"T038_RESULTS.json"),"w") as f: json.dump(RESULTS,f,indent=2)
sha=hashlib.sha256(json.dumps(RESULTS,sort_keys=True).encode()).hexdigest()
with open(os.path.join(ROOT,"T038.sha256"),"w") as f: f.write(sha)

print(f"\n=== T038 ENTROPY FLOW GEOMETRY ===\n{json.dumps(RESULTS,indent=2)}\nSHA256: {sha}")