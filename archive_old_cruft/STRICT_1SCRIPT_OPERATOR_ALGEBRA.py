#!/usr/bin/env python3
import os, json, numpy as np
from itertools import product

ROOT = os.getcwd()
OUTDIR = os.path.join(ROOT, "STRICT_OPERATOR_ALGEBRA"); os.makedirs(OUTDIR, exist_ok=True)

TRANSFORMS = ["identity", "reverse", "swap", "replay", "stitch"]

def op_identity(x): return x.copy()
def op_reverse(x): return x[::-1]
def op_swap(x): n=len(x); return np.concatenate([x[n//2:], x[:n//2]])
def op_replay(x): n=len(x); return np.concatenate([x[:n//2], x[:n//2]])
def op_stitch(x): ts=np.array_split(x,3); return np.concatenate([ts[2],ts[0],ts[1]])

OPS = {"identity":op_identity,"reverse":op_reverse,"swap":op_swap,"replay":op_replay,"stitch":op_stitch}

np.random.seed(79); N=1024; t=np.linspace(0,1,N)
x = np.sin(2*np.pi*5*t) + 0.5*np.sin(2*np.pi*13*t) + 0.1*np.random.randn(N)

def compose(a,b,x_): return OPS[a](OPS[b](x_))
def closest_operator(y,x_):
    errs={name:float(np.mean((y-op(x_))**2)) for name,op in OPS.items()}
    return min(errs,key=errs.get), errs[min(errs,key=errs.get)]

COMPOSITION={}
for a,b in product(TRANSFORMS,TRANSFORMS):
    y=compose(a,b,x); best,err=closest_operator(y,x)
    COMPOSITION[f"{a}∘{b}"]={"closest":best,"mse":err}

COMMUTATIVITY={}
for a,b in product(TRANSFORMS,TRANSFORMS):
    y1,y2=compose(a,b,x),compose(b,a,x)
    COMMUTATIVITY[f"{a},{b}"]={"commutes":bool(np.mean((y1-y2)**2)<1e-9),"mse":float(np.mean((y1-y2)**2))}

def variance(x_): return float(np.var(x_))
def energy(x_): return float(np.sum(x_**2))
base_var,base_energy=variance(x),energy(x)
INVARIANTS={name:{"variance_ratio":variance(op(x))/base_var,"energy_ratio":energy(op(x))/base_energy} for name,op in OPS.items()}

base=op_identity(x)
GENERATOR_VECTORS={name:{"norm":float(np.linalg.norm(op(x)-base)),"mean":float(np.mean(op(x)-base)),"std":float(np.std(op(x)-base))} for name,op in OPS.items()}

INTERPRETATION={"identity":"neutral_element","reverse":"involution_candidate","swap":"permutation_operator","replay":"noninvertible_duplication_operator","stitch":"localized_permutation_operator"}

RESULTS={"composition":COMPOSITION,"commutativity":COMMUTATIVITY,"invariants":INVARIANTS,"generator_vectors":GENERATOR_VECTORS,"interpretation":INTERPRETATION}
with open(os.path.join(OUTDIR,"operator_algebra.json"),"w") as f: json.dump(RESULTS,f,indent=2)

num_commuting=sum(int(v["commutes"]) for v in COMMUTATIVITY.values())
print("="*60); print("STRICT OPERATOR ALGEBRA COMPLETE"); print("="*60)
print(f"\nCommuting pairs: {num_commuting}/{len(COMMUTATIVITY)}")
print("\nInvariant ratios:")
for k,v in INVARIANTS.items(): print(f"  {k}: var={v['variance_ratio']:.3f}, energy={v['energy_ratio']:.3f}")
print("\nInterpretation:")
for k,v in INTERPRETATION.items(): print(f"  {k}: {v}")
print(f"\nSaved: {OUTDIR}/operator_algebra.json")
print("="*60)