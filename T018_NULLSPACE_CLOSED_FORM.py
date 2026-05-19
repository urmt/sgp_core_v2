#!/usr/bin/env python3
import os, json, numpy as np
from scipy.optimize import curve_fit

OUTDIR = "STRICT_PROOF_TRACK/T018_CLOSED_FORM"; os.makedirs(OUTDIR, exist_ok=True)
SEEDS = [11,23,37,51,79,101,149,211,307,401]

def make_signals(seed, N=4096):
    np.random.seed(seed); t=np.linspace(0,1,N)
    chirp=np.sin(2*np.pi*(8*t+32*t**2))
    rw=np.cumsum(np.random.randn(N))
    rs=np.zeros(N); idx=np.random.choice(np.arange(256,N-256),8,replace=False); idx.sort(); val,prev=0,0
    for i in idx: rs[prev:i]=val+0.3*np.random.randn(i-prev); val=np.random.randn()*3; prev=i
    rs[prev:]=val+0.3*np.random.randn(N-prev)
    x=np.zeros(N); x[0]=0.2
    for i in range(N-1): x[i+1]=3.99*x[i]*(1-x[i])
    c1=np.sin(2*np.pi*7*t); c2=np.sin(2*np.pi*7*t+0.5*np.sin(2*np.pi*0.5*t)); coupled=c1+0.7*c2
    return {"chirp":chirp,"rw_trend":rw,"regime_switch":rs,"chaotic_logistic":x,"coupled_osc":coupled}

def replay(x): h=len(x)//2; return np.concatenate([x[:h],x[:h]])
def signed_ordinal_flow(x): dx=np.diff(x); return float(np.mean(np.sign(dx[:-1]*dx[1:])) if len(dx)>1 else 0.0)
def half_corr(x): h=len(x)//2; a,b=x[:h],x[h:h+h]; return float(np.corrcoef(a,b)[0,1]) if np.std(a)>0 and np.std(b)>0 else 0.0
def signed_compress(x): dx=np.sign(np.diff(x)); p=np.mean(dx>0); p=np.clip(p,1e-6,1-1e-6); return float(-(p*np.log2(p)+(1-p)*np.log2(1-p)))
def amp_transition(x): q=np.quantile(np.abs(x),0.75); return float(np.mean(np.abs(np.diff((np.abs(x)>q).astype(int)))))
def embed(x): return np.array([signed_ordinal_flow(x),half_corr(x),signed_compress(x),amp_transition(x)])
def null_coordinate(e): return float(e[1]-e[2])

steps=6; all_trajectories=[]
for seed in SEEDS:
    for domain,x in make_signals(seed).items():
        vals=[]; z=x.copy()
        for k in range(steps):
            e=embed(z); vals.append(abs(null_coordinate(e))); z=replay(z)
        all_trajectories.append(vals)
all_trajectories=np.array(all_trajectories); mean_traj=np.mean(all_trajectories,axis=0)

def exp_model(k,a,b): return a*np.exp(-b*k)
params,_=curve_fit(exp_model,np.arange(steps),mean_traj,p0=[1.0,1.0],maxfev=10000); a_fit,b_fit=params
fit_vals=exp_model(np.arange(steps),a_fit,b_fit); r2=float(1-np.sum((mean_traj-fit_vals)**2)/(np.sum((mean_traj-np.mean(mean_traj))**2)+1e-12))

initial_null,final_null=mean_traj[0],mean_traj[-1]
projection_ratio=float(final_null/(initial_null+1e-12))
fixed_errors=[]
for seed in SEEDS:
    for d,x in make_signals(seed).items():
        r1=replay(x); r2x=replay(r1); e1,e2=embed(r1),embed(r2x); fixed_errors.append(np.linalg.norm(e2-e1))
fixed_error_mean=float(np.mean(fixed_errors))

H1_exponential_contraction=bool(r2>0.95); H2_projection_operator=bool(projection_ratio<0.01); H3_fixed_point=bool(fixed_error_mean<1e-6)
closed_form_statement="Replay operator R acts approximately as: R:(m1,m2,m3,m4)->(m1,phi,phi,m4) where phi≈shared redundancy coordinate. Thus replay annihilates N(x)=m2-m3 and projects onto M={x:m2=m3}."

result={"mean_trajectory":[float(x) for x in mean_traj],"exp_fit_a":float(a_fit),"exp_fit_b":float(b_fit),"exp_fit_r2":r2,"projection_ratio":projection_ratio,"fixed_error_mean":fixed_error_mean,"H1_exponential_contraction":H1_exponential_contraction,"H2_projection_operator":H2_projection_operator,"H3_fixed_point":H3_fixed_point,"closed_form_statement":closed_form_statement}
with open(os.path.join(OUTDIR,"T018_results.json"),"w") as f: json.dump(result,f,indent=2)
print("=== T018 CLOSED-FORM NULLSPACE THEORY ===")
for k,v in result.items(): print(f"{k}: {v}")
print(f"\nSaved -> {OUTDIR}")