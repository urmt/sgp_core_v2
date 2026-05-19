#!/usr/bin/env python3
import os, json, hashlib, numpy as np
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression

ROOT="T034_FLOW_GENERATOR"
os.makedirs(ROOT, exist_ok=True)
SEED=79
rng=np.random.default_rng(SEED)

def signed_ordinal_flow(x): d=np.diff(x); return np.mean(np.sign(d[:-1])*np.sign(d[1:])) if len(d)>1 else 0.0
def half_corr(x): n=len(x)//2; a,b=x[:n],x[n:2*n]; return np.corrcoef(a,b)[0,1] if np.std(a)>0 and np.std(b)>0 else 0.0
def signed_compress(x): q=np.round((x-np.mean(x))/(np.std(x)+1e-8),2); return -np.mean(np.abs(np.diff(q)))
def amp_transition(x): return np.mean(np.abs(np.diff(x)))
def embed(x): return np.array([signed_ordinal_flow(x),half_corr(x),signed_compress(x),amp_transition(x)])

def replay(x): h=len(x)//2; return np.concatenate([x[:h],x[:h]])
def stitch(x): q=len(x)//4; return np.concatenate([x[:q],x[2*q:3*q],x[q:2*q],x[3*q:]])
def swap(x): h=len(x)//2; return np.concatenate([x[h:],x[:h]])
def reverse(x): return x[::-1]
OPS={"R":replay,"S":stitch,"W":swap,"V":reverse}

N=512; t=np.linspace(0,1,N)
signals={"chirp":np.sin(2*np.pi*(3*t+12*t*t)),"rw_trend":np.cumsum(rng.normal(size=N)),"telegraph":np.sign(np.sin(2*np.pi*8*t)),"square":np.sign(np.sin(2*np.pi*5*t)),"pink_noise":np.cumsum(rng.normal(size=N))}

MAX_STEPS=10
positions,velocities=[],[]
for op_name,op in OPS.items():
    for sig_name,sig in signals.items():
        x=sig.copy(); traj=[]
        for k in range(MAX_STEPS):
            traj.append(embed(x)); x=op(x)
        traj=np.array(traj)
        positions.append(traj[:-1]); velocities.append(traj[1:]-traj[:-1])

positions=np.concatenate(positions,axis=0)
velocities=np.concatenate(velocities,axis=0)

flow_pca=PCA(n_components=4); flow_pca.fit(velocities)
tau=flow_pca.components_[0]
flow_pc1=float(flow_pca.explained_variance_ratio_[0])

alignments=[abs(np.dot(v,tau)/np.linalg.norm(v)) for v in velocities if np.linalg.norm(v)>1e-8]
mean_alignment=float(np.mean(alignments))

reg=LinearRegression(); reg.fit(positions,velocities)
u,s,vh=np.linalg.svd(reg.coef_)
rank1_ratio=float(s[0]/np.sum(s))

pred=reg.predict(positions)
resid=np.mean(np.linalg.norm(velocities-pred,axis=1))
vel_mag=np.mean(np.linalg.norm(velocities,axis=1))
continuous_ratio=float(1-resid/(vel_mag+1e-8))

H1_tau_alignment=bool(mean_alignment>0.90)
H2_rank1_generator=bool(rank1_ratio>0.85)
H3_replay_terminal=bool(np.linalg.norm(embed(replay(signals["chirp"]))-embed(replay(replay(signals["chirp"]))))<0.05)
H4_transient_nonreplay=bool(np.mean(np.linalg.norm(velocities,axis=1))>0.05)
H5_continuous_flow=bool(continuous_ratio>0.80)

RESULTS={"flow_pc1":flow_pc1,"mean_alignment":mean_alignment,"generator_singular_values":s.tolist(),"rank1_ratio":rank1_ratio,"continuous_ratio":continuous_ratio,"checks":{"H1_tau_alignment":H1_tau_alignment,"H2_rank1_generator":H2_rank1_generator,"H3_replay_terminal":H3_replay_terminal,"H4_transient_nonreplay":H4_transient_nonreplay,"H5_continuous_flow":H5_continuous_flow}}

with open(os.path.join(ROOT,"T034_RESULTS.json"),"w") as f: json.dump(RESULTS,f,indent=2)
sha=hashlib.sha256(json.dumps(RESULTS,sort_keys=True).encode()).hexdigest()
with open(os.path.join(ROOT,"T034.sha256"),"w") as f: f.write(sha)

print(f"\n=== T034 FLOW GENERATOR ===\nflow_pc1: {round(flow_pc1,6)}\nmean_alignment: {round(mean_alignment,6)}\nrank1_ratio: {round(rank1_ratio,6)}\ncontinuous_ratio: {round(continuous_ratio,6)}\nChecks: H1={H1_tau_alignment}, H2={H2_rank1_generator}, H3={H3_replay_terminal}, H4={H4_transient_nonreplay}, H5={H5_continuous_flow}\nSHA256: {sha}")