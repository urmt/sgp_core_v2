"""
Phase R5 — RECONSTRUCTION THRESHOLDS (lightweight)
"""
import sys, numpy as np, pandas as pd, os, json, warnings
sys.path.insert(0, '/home/student/sgp_core_v2')
warnings.filterwarnings('ignore')
BASE = '/home/student/sgp_core_v2/phases/phaseR_minimal_mechanisms'
N_SIMS = 40; STEPS = 150; DT = 0.05; N = 5

def run(K, alpha, beta):
    survivals=[]; final_cs=[]
    for _ in range(N_SIMS):
        theta=np.random.uniform(0,2*np.pi,N); c=np.random.uniform(0,1,N)
        omega=np.random.uniform(0.5,2.0,N)
        for t in range(STEPS):
            for i in range(N):
                dtheta=omega[i]
                for j in range(N):
                    if j!=i: dtheta+=(K/N)*np.sin(theta[j]-theta[i])
                theta[i]+=DT*dtheta
            theta=np.mod(theta,2*np.pi)
            r=np.abs(np.mean(np.exp(1j*theta)))
            psi=np.angle(np.mean(np.exp(1j*theta)))
            for i in range(N):
                align=np.cos(theta[i]-psi)
                dc=alpha*(align*r-c[i])
                for j in range(N):
                    if j!=i: dc+=(beta/N)*(c[j]-c[i])
                c[i]+=DT*dc;c[i]=np.clip(c[i],0,1)
        final_cs.append(float(np.mean(c[-50:])))
        survivals.append(int(np.mean(c[-50:])>0.3))
    return float(np.mean(final_cs)), float(np.mean(survivals))

records=[]

print('K scan:')
for K in np.linspace(0,1.0,11):
    c,s=run(K,0.2,0.3); records.append({'param':'K','value':float(K),'mean_closure':c,'survival_rate':s})
    print(f'  K={K:.2f} closure={c:.4f} surv={s*100:.1f}%')

print('alpha scan:')
for a in np.linspace(0,0.5,11):
    c,s=run(0.8,a,0.3); records.append({'param':'alpha','value':float(a),'mean_closure':c,'survival_rate':s})
    print(f'  a={a:.3f} closure={c:.4f} surv={s*100:.1f}%')

print('beta scan:')
for b in np.linspace(0,0.5,11):
    c,s=run(0.8,0.2,b); records.append({'param':'beta','value':float(b),'mean_closure':c,'survival_rate':s})
    print(f'  b={b:.3f} closure={c:.4f} surv={s*100:.1f}%')

# 2D grid (coarse)
print('2D phase diagram (K x a):')
for K in np.linspace(0,1.0,6):
    row=[]
    for a in np.linspace(0,0.5,6):
        c,s=run(K,a,0.3); records.append({'K':float(K),'alpha':float(a),'survival_rate':s,'mean_closure':c})
        row.append(f'{s*100:4.0f}%')
    print(f'  K={K:.2f}: '+'|'.join(row))

pd.DataFrame(records).to_csv(f'{BASE}/outputs/R5_reconstruction_thresholds.csv',index=False)
print('R5 done')
