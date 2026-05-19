#!/usr/bin/env python3
import os, json, hashlib, numpy as np
from sklearn.decomposition import PCA

ROOT="T033_OPERATOR_FLOW"
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

def reverse(x): return x[::-1]
def replay(x): h=len(x)//2; return np.concatenate([x[:h],x[:h]])
def stitch(x): q=len(x)//4; return np.concatenate([x[:q],x[2*q:3*q],x[q:2*q],x[3*q:]])
def swap(x): h=len(x)//2; return np.concatenate([x[h:],x[:h]])
OPS={"R":replay,"S":stitch,"W":swap,"V":reverse}

MAX_STEPS=12
flow_results={}; all_trajectories=[]
for op_name,op in OPS.items():
    flow_results[op_name]={}
    for sig_name,sig in signals.items():
        x=sig.copy(); traj=[]
        for k in range(MAX_STEPS):
            traj.append(embed(x).tolist())
            x=op(x)
        traj=np.array(traj); all_trajectories.append(traj)
        step_dists=np.linalg.norm(traj[1:]-traj[:-1],axis=1)
        replay_target=embed(replay(sig))
        replay_dists=np.linalg.norm(traj-replay_target,axis=1)
        flow_results[op_name][sig_name]={"step_distances":step_dists.tolist(),"replay_distances":replay_dists.tolist(),"final_distance":float(replay_dists[-1])}

all_pts=np.concatenate(all_trajectories,axis=0)
pca=PCA(n_components=4); pca.fit(all_pts)
pc1=float(pca.explained_variance_ratio_[0])
dim95=int(np.searchsorted(np.cumsum(pca.explained_variance_ratio_),0.95))+1

trajectory_vectors=np.concatenate([traj[1:]-traj[:-1] for traj in all_trajectories],axis=0)
flow_pca=PCA(n_components=4); flow_pca.fit(trajectory_vectors)
flow_pc1=float(flow_pca.explained_variance_ratio_[0])
flow_dim95=int(np.searchsorted(np.cumsum(flow_pca.explained_variance_ratio_),0.95))+1

basin_summary={op_name:{"mean_final_distance":float(np.mean([flow_results[op_name][s]["final_distance"] for s in signals])),"std":float(np.std([flow_results[op_name][s]["final_distance"] for s in signals]))} for op_name in OPS}

replay_final=basin_summary["R"]["mean_final_distance"]
stitch_final=basin_summary["S"]["mean_final_distance"]
swap_final=basin_summary["W"]["mean_final_distance"]

H1_replay_attractor=bool(replay_final<0.05)
H2_stitch_flows_to_replay=bool(stitch_final<0.25)
H3_swap_metastable=bool(swap_final>stitch_final)
H4_lowrank_flow=bool(flow_pc1>0.90)
H5_phase_portrait=bool(dim95<=2)

RESULTS={"seed":SEED,"max_steps":MAX_STEPS,"global_geometry":{"pc1":pc1,"dim95":dim95},"flow_geometry":{"flow_pc1":flow_pc1,"flow_dim95":flow_dim95},"basin_summary":basin_summary,"checks":{"H1_replay_attractor":H1_replay_attractor,"H2_stitch_flows_to_replay":H2_stitch_flows_to_replay,"H3_swap_metastable":H3_swap_metastable,"H4_lowrank_flow":H4_lowrank_flow,"H5_phase_portrait":H5_phase_portrait}}

with open(os.path.join(ROOT,"T033_RESULTS.json"),"w") as f: json.dump(RESULTS,f,indent=2)
sha=hashlib.sha256(json.dumps(RESULTS,sort_keys=True).encode()).hexdigest()
with open(os.path.join(ROOT,"T033.sha256"),"w") as f: f.write(sha)

print(f"\n=== T033 OPERATOR FLOW ===\nGlobal PC1: {round(pc1,6)} | dim95: {dim95}\nFlow PC1: {round(flow_pc1,6)} | flow_dim95: {flow_dim95}\nBasin Summary:")
for k,v in basin_summary.items(): print(f"{k} | mean={v['mean_final_distance']:.6f} | std={v['std']:.6f}")
print(f"\nChecks: H1={H1_replay_attractor}, H2={H2_stitch_flows_to_replay}, H3={H3_swap_metastable}, H4={H4_lowrank_flow}, H5={H5_phase_portrait}\nSHA256: {sha}")