#!/usr/bin/env python3
import os, json, numpy as np
from itertools import product

ROOT = os.getcwd()
OUTDIR = os.path.join(ROOT, "STRICT_GROUP_STRUCTURE"); os.makedirs(OUTDIR, exist_ok=True)

def identity(x): return x.copy()
def reverse(x): return x[::-1]
def swap(x): n=len(x); return np.concatenate([x[n//2:],x[:n//2]])
def replay(x): n=len(x); return np.concatenate([x[:n//2],x[:n//2]])
def stitch(x): ts=np.array_split(x,3); return np.concatenate([ts[2],ts[0],ts[1]])

OPS={"identity":identity,"reverse":reverse,"swap":swap,"replay":replay,"stitch":stitch}; TRANSFORMS=list(OPS.keys())
np.random.seed(79); N=1024; t=np.linspace(0,1,N); x=np.sin(2*np.pi*5*t)+0.4*np.sin(2*np.pi*17*t)+0.05*np.random.randn(N)

def mse(a,b): return float(np.mean((a-b)**2))
def compose(a,b,x_): return OPS[a](OPS[b](x_))

INVERTIBILITY={}
for a in TRANSFORMS:
    invertible,inverse=False,None
    for b in TRANSFORMS:
        if mse(compose(a,b,x),x)<1e-10: invertible,inverse=True,b; break
    INVERTIBILITY[a]={"invertible":bool(invertible),"inverse":inverse}

IDEMPOTENT={}
for a in TRANSFORMS:
    y1,y2=OPS[a](x),OPS[a](OPS[a](x))
    IDEMPOTENT[a]={"idempotent":bool(mse(y1,y2)<1e-10),"mse":mse(y1,y2)}

invertible_ops=[k for k,v in INVERTIBILITY.items() if v["invertible"]]
SUBGROUP_CLOSURE={}
for a,b in product(invertible_ops,invertible_ops):
    y=compose(a,b,x); found,matched=False,None
    for c in invertible_ops:
        if mse(OPS[c](x),y)<1e-10: found,matched=True,c; break
    SUBGROUP_CLOSURE[f"{a}∘{b}"]={"closed":bool(found),"maps_to":matched}

r1,r2=replay(x),replay(replay(x)); REPLAY_PROJECTION={"projection_like":bool(mse(r1,r2)<1e-10),"mse":mse(r1,r2)}

EQUIVALENCE={}
for a,b in product(TRANSFORMS,TRANSFORMS): EQUIVALENCE[f"{a},{b}"]={"distance":mse(OPS[a](x),OPS[b](x))}

BASE={"variance":float(np.var(x)),"energy":float(np.sum(x**2)),"mean":float(np.mean(x))}
CONSERVATION={}
for a in TRANSFORMS:
    y=OPS[a](x)
    CONSERVATION[a]={"variance_ratio":float(np.var(y)/BASE["variance"]),"energy_ratio":float(np.sum(y**2)/BASE["energy"]),"mean_shift":float(np.mean(y)-BASE["mean"])}

CLASSIFICATION={"identity":"identity_element","reverse":"invertible_involution","swap":"invertible_permutation","stitch":"invertible_localized_permutation","replay":"noninvertible_projection_like_operator"}

RESULTS={"invertibility":INVERTIBILITY,"idempotency":IDEMPOTENT,"subgroup_closure":SUBGROUP_CLOSURE,"replay_projection":REPLAY_PROJECTION,"equivalence":EQUIVALENCE,"conservation":CONSERVATION,"classification":CLASSIFICATION}
with open(os.path.join(OUTDIR,"group_structure_analysis.json"),"w") as f: json.dump(RESULTS,f,indent=2)

print("="*60); print("STRICT GROUP STRUCTURE ANALYSIS COMPLETE"); print("="*60)
num_inv=sum(int(v["invertible"]) for v in INVERTIBILITY.values())
num_idem=sum(int(v["idempotent"]) for v in IDEMPOTENT.values())
print(f"\nInvertible operators: {num_inv}/{len(TRANSFORMS)}")
print(f"Idempotent operators: {num_idem}/{len(TRANSFORMS)}")
print(f"\nReplay projection-like: {REPLAY_PROJECTION['projection_like']}")
print("\nOperator classes:")
for k,v in CLASSIFICATION.items(): print(f"  {k}: {v}")
print(f"\nSaved: {OUTDIR}/group_structure_analysis.json")
print("="*60)