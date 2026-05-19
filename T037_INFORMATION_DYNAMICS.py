#!/usr/bin/env python3
import os, json, hashlib, numpy as np
from scipy.stats import entropy

ROOT="T037_INFORMATION_DYNAMICS"
os.makedirs(ROOT, exist_ok=True)
SEED=79
rng=np.random.default_rng(SEED)

N=512; t=np.linspace(0,1,N)
signals={"chirp":np.sin(2*np.pi*(3*t+10*t*t)),"rw":np.cumsum(rng.normal(size=N)),"telegraph":np.sign(np.sin(2*np.pi*7*t)),"pink":np.cumsum(rng.normal(size=N)),"square":np.sign(np.sin(2*np.pi*5*t))}

def R(x): h=len(x)//2; return np.concatenate([x[:h],x[:h]])
def S(x): q=len(x)//4; return np.concatenate([x[:q],x[2*q:3*q],x[q:2*q],x[3*q:]])
def W(x): h=len(x)//2; return np.concatenate([x[h:],x[:h]])
def V(x): return x[::-1]
OPS={"R":R,"S":S,"W":W,"V":V}

def signal_entropy(x,bins=64): hist,_=np.histogram(x,bins=bins,density=True); hist+=1e-12; return entropy(hist)
def diversity(x): return np.std(np.diff(x))
def compressibility(x): q=np.round((x-np.mean(x))/(np.std(x)+1e-8),2); return len(np.unique(q))/len(q)

results=[]
for name,sig in signals.items():
    base={"entropy":signal_entropy(sig),"diversity":diversity(sig),"compressibility":compressibility(sig)}
    for op_name,op in OPS.items():
        y=op(sig)
        after={"entropy":signal_entropy(y),"diversity":diversity(y),"compressibility":compressibility(y)}
        results.append({"signal":name,"operator":op_name,"entropy_change":float(after["entropy"]-base["entropy"]),"diversity_change":float(after["diversity"]-base["diversity"]),"compressibility_change":float(after["compressibility"]-base["compressibility"])})

projection=[r for r in results if r["operator"] in ["R","S"]]
antisymmetry=[r for r in results if r["operator"] in ["W","V"]]

def avg(key,rows): return float(np.mean([r[key] for r in rows]))
summary={"projection":{"entropy_change":avg("entropy_change",projection),"diversity_change":avg("diversity_change",projection),"compressibility_change":avg("compressibility_change",projection)},"antisymmetry":{"entropy_change":avg("entropy_change",antisymmetry),"diversity_change":avg("diversity_change",antisymmetry),"compressibility_change":avg("compressibility_change",antisymmetry)}}

H1_projection_compresses=bool(summary["projection"]["compressibility_change"]<0)
H2_projection_reduces_diversity=bool(summary["projection"]["diversity_change"]<0)
H3_antisymmetry_preserves=bool(abs(summary["antisymmetry"]["entropy_change"])<0.05)

RESULTS={"summary":summary,"checks":{"H1_projection_compresses":H1_projection_compresses,"H2_projection_reduces_diversity":H2_projection_reduces_diversity,"H3_antisymmetry_preserves":H3_antisymmetry_preserves}}

with open(os.path.join(ROOT,"T037_RESULTS.json"),"w") as f: json.dump(RESULTS,f,indent=2)
sha=hashlib.sha256(json.dumps(RESULTS,sort_keys=True).encode()).hexdigest()
with open(os.path.join(ROOT,"T037.sha256"),"w") as f: f.write(sha)

print(f"\n=== T037 INFORMATION DYNAMICS ===\n{json.dumps(RESULTS,indent=2)}\nSHA256: {sha}")