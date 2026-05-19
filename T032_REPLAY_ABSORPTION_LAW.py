#!/usr/bin/env python3
import os, json, hashlib, itertools, numpy as np

ROOT="T032_REPLAY_ABSORPTION"
os.makedirs(ROOT, exist_ok=True)
SEED=79
rng=np.random.default_rng(SEED)

def signed_ordinal_flow(x): d=np.diff(x); return np.mean(np.sign(d[:-1])*np.sign(d[1:])) if len(d)>1 else 0.0
def half_corr(x): n=len(x)//2; a,b=x[:n],x[n:2*n]; return np.corrcoef(a,b)[0,1] if np.std(a)>0 and np.std(b)>0 else 0.0
def signed_compress(x): q=np.round((x-np.mean(x))/(np.std(x)+1e-8),2); return -np.mean(np.abs(np.diff(q)))
def amp_transition(x): return np.mean(np.abs(np.diff(x)))
def embed(x): return np.array([signed_ordinal_flow(x),half_corr(x),signed_compress(x),amp_transition(x)])

N=512; t=np.linspace(0,1,N)
x_logistic=np.zeros(N); x_logistic[0]=0.2
for i in range(N-1): x_logistic[i+1]=3.99*x_logistic[i]*(1-x_logistic[i])
signals={"chirp":np.sin(2*np.pi*(3*t+12*t*t)),"rw_trend":np.cumsum(rng.normal(size=N))+0.002*np.arange(N),"telegraph":np.sign(np.sin(2*np.pi*8*t)),"pink_noise":np.cumsum(rng.normal(size=N)),"square":np.sign(np.sin(2*np.pi*5*t)),"chaotic_logistic":x_logistic}

def identity(x): return x
def reverse(x): return x[::-1]
def replay(x): h=len(x)//2; return np.concatenate([x[:h],x[:h]])
def stitch(x): q=len(x)//4; return np.concatenate([x[:q],x[2*q:3*q],x[q:2*q],x[3*q:]])
def swap(x): h=len(x)//2; return np.concatenate([x[h:],x[:h]])
def jitter(x): return x+0.01*rng.normal(size=len(x))
OPS={"I":identity,"V":reverse,"R":replay,"S":stitch,"W":swap,"J":jitter}

def apply_chain(x, chain):
    y=x.copy()
    for op in chain: y=OPS[op](y)
    return y

structured_ops=["V","S","W"]
chains=[]
for depth in range(1,6):
    for combo in itertools.product(structured_ops,repeat=depth): chains.append(combo)
for _ in range(40):
    depth=rng.integers(2,7)
    combo=tuple(rng.choice(["V","S","W","J"],size=depth))
    chains.append(combo)

chain_results={}; all_errors=[]; depth_errors={}
for chain in chains:
    cname="".join(chain); errors=[]; depth=len(chain)
    if depth not in depth_errors: depth_errors[depth]=[]
    for sig in signals.values():
        base_replay=embed(replay(sig))
        transformed=apply_chain(sig,chain)
        replay_after=embed(replay(transformed))
        err=float(np.linalg.norm(replay_after-base_replay))
        errors.append(err); depth_errors[depth].append(err)
    mean_err=np.mean(errors)
    all_errors.append(mean_err)
    chain_results[cname]={"depth":depth,"mean_absorption_error":mean_err,"std":float(np.std(errors))}

depth_summary={d:{"mean":float(np.mean(v)),"std":float(np.std(v))} for d,v in depth_errors.items()}

terminal_errors=[]
for sig in signals.values():
    replay_states=[]
    for chain in chains[:50]:
        y=apply_chain(sig,chain)
        replay_states.append(embed(replay(y)))
    replay_states=np.array(replay_states)
    centroid=np.mean(replay_states,axis=0)
    dists=np.linalg.norm(replay_states-centroid,axis=1)
    terminal_errors.extend(dists)
terminal_mean=float(np.mean(terminal_errors))

mean_absorption=float(np.mean(all_errors))
depth_means=np.array([depth_summary[d]["mean"] for d in sorted(depth_summary)])
depth_slope=float(np.polyfit(np.arange(len(depth_means)),depth_means,1)[0])

H1_left_absorbing=bool(mean_absorption<0.25)
H2_depth_independent=bool(abs(depth_slope)<0.05)
H3_terminal_class=bool(terminal_mean<0.15)

RESULTS={"seed":SEED,"num_chains":len(chains),"mean_absorption_error":mean_absorption,"depth_slope":depth_slope,"terminal_class_radius":terminal_mean,"depth_summary":depth_summary,"sample_chains":dict(list(chain_results.items())[:20]),"checks":{"H1_left_absorbing":H1_left_absorbing,"H2_depth_independent":H2_depth_independent,"H3_terminal_class":H3_terminal_class}}

with open(os.path.join(ROOT,"T032_RESULTS.json"),"w") as f: json.dump(RESULTS,f,indent=2)
sha=hashlib.sha256(json.dumps(RESULTS,sort_keys=True).encode()).hexdigest()
with open(os.path.join(ROOT,"T032.sha256"),"w") as f: f.write(sha)

print(f"\n=== T032 REPLAY ABSORPTION LAW ===\nChains tested: {len(chains)}\nMean absorption error: {round(mean_absorption,6)}\nDepth slope: {round(depth_slope,6)}\nTerminal class radius: {round(terminal_mean,6)}\nDepth Summary:")
for d,v in depth_summary.items(): print(f"depth={d} | mean={v['mean']:.6f} | std={v['std']:.6f}")
print(f"\nChecks: H1={H1_left_absorbing}, H2={H2_depth_independent}, H3={H3_terminal_class}\nSHA256: {sha}")