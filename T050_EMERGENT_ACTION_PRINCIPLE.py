#!/usr/bin/env python3
import numpy as np
from sklearn.decomposition import PCA
from scipy.stats import pearsonr
import json

np.random.seed(2025)

def random_signal(n=512):
    return np.random.randn(n)

def replay(x):
    h=len(x)//2
    return np.concatenate([x[:h],x[:h]])

def reverse(x):
    return x[::-1]

def swap(x):
    h=len(x)//2
    return np.concatenate([x[h:],x[:h]])

def stitch(x):
    h=len(x)//2
    return np.concatenate([x[:h],x[::-1][:h]])

OPS={"R":replay,"V":reverse,"W":swap,"S":stitch}

def embed(x):
    h=len(x)//2; a,b=x[:h],x[h:]
    m1=np.mean(np.diff(x>np.median(x)))
    m2=np.corrcoef(a,b)[0,1]
    if np.isnan(m2): m2=0.0
    fft=np.abs(np.fft.rfft(x)); p=fft/(fft.sum()+1e-9)
    m3=-np.sum(p*np.log(p+1e-9))
    m4=np.std(np.diff(x))
    return np.array([m1,m2,m3,m4])

def apply_chain(x,chain):
    y=x.copy(); traj=[embed(y)]
    for c in chain:
        y=OPS[c](y); traj.append(embed(y))
    return np.array(traj)

def path_length(traj):
    return np.sum([np.linalg.norm(traj[i+1]-traj[i]) for i in range(len(traj)-1)])

def curvature_action(traj):
    if len(traj)<3: return 0.0
    angles=[]
    for i in range(1,len(traj)-1):
        a,b=traj[i]-traj[i-1],traj[i+1]-traj[i]
        na,nb=np.linalg.norm(a),np.linalg.norm(b)
        if na<1e-9 or nb<1e-9: continue
        angles.append(np.arccos(np.clip(np.dot(a,b)/(na*nb),-1,1)))
    return np.sum(angles)

def terminal_distance(traj):
    return np.linalg.norm(traj[-1]-np.array([0,1,0,0]))

def total_action(traj):
    return 0.5*path_length(traj)+0.3*curvature_action(traj)+0.2*terminal_distance(traj)

actions,terminals,lengths,curvatures=[],[],[],[]
for i in range(1000):
    x=random_signal()
    traj=apply_chain(x,[np.random.choice(list(OPS.keys())) for _ in range(np.random.randint(1,8))])
    A=total_action(traj); T=terminal_distance(traj); L=path_length(traj); C=curvature_action(traj)
    actions.append(A); terminals.append(T); lengths.append(L); curvatures.append(C)

actions,terminals,lengths,curvatures=np.array(actions),np.array(terminals),np.array(lengths),np.array(curvatures)

action_terminal_corr=pearsonr(actions,terminals)[0]
length_terminal_corr=pearsonr(lengths,terminals)[0]
curvature_terminal_corr=pearsonr(curvatures,terminals)[0]

low_idx=np.argsort(actions)[:100]
high_idx=np.argsort(actions)[-100:]
low_terminal=np.mean(terminals[low_idx])
high_terminal=np.mean(terminals[high_idx])

results={"action_terminal_corr":float(action_terminal_corr),"length_terminal_corr":float(length_terminal_corr),"curvature_terminal_corr":float(curvature_terminal_corr),"low_action_terminal":float(low_terminal),"high_action_terminal":float(high_terminal),"H1_action_predicts_terminal":bool(action_terminal_corr>0.7),"H2_low_action_near_attractor":bool(low_terminal<high_terminal),"H3_geodesic_bias":bool(length_terminal_corr>0.5),"H4_curvature_penalty":bool(curvature_terminal_corr>0.3)}
print(json.dumps(results,indent=2))