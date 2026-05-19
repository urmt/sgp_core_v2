#!/usr/bin/env python3
import os, json, hashlib, itertools, numpy as np
from sklearn.decomposition import PCA

ROOT="T036_SECTOR_DYNAMICS"
os.makedirs(ROOT, exist_ok=True)
SEED=79
rng=np.random.default_rng(SEED)

def m1(x): d=np.diff(x); return np.mean(np.sign(d[:-1])*np.sign(d[1:])) if len(d)>1 else 0.0
def m2(x): n=len(x)//2; a,b=x[:n],x[n:2*n]; return np.corrcoef(a,b)[0,1] if np.std(a)>0 and np.std(b)>0 else 0.0
def m3(x): q=np.round((x-np.mean(x))/(np.std(x)+1e-8),2); return -np.mean(np.abs(np.diff(q)))
def m4(x): return np.mean(np.abs(np.diff(x)))
def E(x): return np.array([m1(x),m2(x),m3(x),m4(x)])

def R(x): h=len(x)//2; return np.concatenate([x[:h],x[:h]])
def S(x): q=len(x)//4; return np.concatenate([x[:q],x[2*q:3*q],x[q:2*q],x[3*q:]])
def W(x): h=len(x)//2; return np.concatenate([x[h:],x[:h]])
def V(x): return x[::-1]
OPS={"R":R,"S":S,"W":W,"V":V}

N=512; t=np.linspace(0,1,N)
signals={"chirp":np.sin(2*np.pi*(3*t+10*t*t)),"rw":np.cumsum(rng.normal(size=N)),"telegraph":np.sign(np.sin(2*np.pi*7*t)),"pink":np.cumsum(rng.normal(size=N))}

replay_disp=np.stack([E(R(sig))-E(sig) for sig in signals.values()])
tau=PCA(n_components=4).fit(replay_disp).components_[0]

def sector(vec):
    n=np.linalg.norm(vec)
    if n<1e-8: return "neutral"
    a=np.dot(vec,tau)/n
    if abs(a)>0.8: return "projection"
    if abs(a)<0.2: return "antisymmetry"
    return "mixed"

chains=[seq for L in [1,2,3,4] for seq in itertools.product(OPS.keys(),repeat=L)]

results=[]
for name,sig in signals.items():
    base=E(sig)
    for seq in chains:
        x=sig.copy()
        for s in seq: x=OPS[s](x)
        disp=E(x)-base
        results.append({"signal":name,"chain":"".join(seq),"sector":sector(disp),"norm":float(np.linalg.norm(disp))})

counts={"projection":0,"antisymmetry":0,"mixed":0,"neutral":0}
for r in results: counts[r["sector"]]+=1

terminal_projection=sum(1 for r in results if "R" in r["chain"] and r["sector"]=="projection")
terminal_antisymmetry=sum(1 for r in results if all(c in ["W","V"] for c in r["chain"]) and r["sector"]=="antisymmetry")

total_R=sum(1 for r in results if "R" in r["chain"])
total_WV=sum(1 for r in results if all(c in ["W","V"] for c in r["chain"]))

H1_replay_terminal=bool(terminal_projection>0.9*total_R) if total_R>0 else False
H2_antisymmetry_closed=bool(terminal_antisymmetry>0.9*total_WV) if total_WV>0 else False
H3_sectorization=bool((counts["projection"]+counts["antisymmetry"])/len(results)>0.8)

RESULTS={"sector_counts":counts,"terminal_projection":terminal_projection,"terminal_antisymmetry":terminal_antisymmetry,"checks":{"H1_replay_terminal":H1_replay_terminal,"H2_antisymmetry_closed":H2_antisymmetry_closed,"H3_sectorization":H3_sectorization}}

with open(os.path.join(ROOT,"T036_RESULTS.json"),"w") as f: json.dump(RESULTS,f,indent=2)
sha=hashlib.sha256(json.dumps(RESULTS,sort_keys=True).encode()).hexdigest()
with open(os.path.join(ROOT,"T036.sha256"),"w") as f: f.write(sha)

print(f"\n=== T036 SECTOR DYNAMICS ===\nsector counts: {counts}\nChecks: H1={H1_replay_terminal}, H2={H2_antisymmetry_closed}, H3={H3_sectorization}\nSHA256: {sha}")