"""
Phase R6 — ORGANIZATIONAL COMPRESSION (PCA)
"""
import sys,numpy as np,pandas as pd,os,json,warnings
sys.path.insert(0,'/home/student/sgp_core_v2')
warnings.filterwarnings('ignore')
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
BASE='/home/student/sgp_core_v2/phases/phaseR_minimal_mechanisms'
os.makedirs(f'{BASE}/outputs',exist_ok=True)
N=5;STEPS=200;DT=0.05;N_TRAJ=150

print('Generating trajectories...')
trajs=[];final_cs=[]
for _ in range(N_TRAJ):
    theta=np.random.uniform(0,2*np.pi,N);c=np.random.uniform(0,1,N)
    omega=np.random.uniform(0.5,2.0,N);traj=np.zeros((STEPS,N))
    for t in range(STEPS):
        for i in range(N):
            dtheta=omega[i]
            for j in range(N):
                if j!=i:dtheta+=(0.8/N)*np.sin(theta[j]-theta[i])
            theta[i]+=DT*dtheta
        theta=np.mod(theta,2*np.pi)
        r=np.abs(np.mean(np.exp(1j*theta)))
        psi=np.angle(np.mean(np.exp(1j*theta)))
        for i in range(N):
            align=np.cos(theta[i]-psi)
            dc=0.2*(align*r-c[i])
            for j in range(N):
                if j!=i:dc+=(0.3/N)*(c[j]-c[i])
            c[i]+=DT*dc;c[i]=np.clip(c[i],0,1)
        traj[t]=c
    trajs.append(traj.flatten())
    final_cs.append(np.mean(c[-50:]))

X=np.array(trajs);y=np.array(final_cs)
scaler=StandardScaler();X_scaled=scaler.fit_transform(X)
pca=PCA();X_pca=pca.fit_transform(X_scaled)
vr=pca.explained_variance_ratio_;cv=np.cumsum(vr)

print(f'\nPCA on {X.shape[1]}D data:')
for i in range(min(10,len(vr))):
    print(f'  PC{i+1}: var={vr[i]:.4f} cum={cv[i]:.4f}')

n90=int(np.argmax(cv>=0.90)+1)if np.any(cv>=0.90)else len(vr)
n95=int(np.argmax(cv>=0.95)+1)if np.any(cv>=0.95)else len(vr)
print(f'\nComponents for 90% var: {n90} (compression: {X.shape[1]/n90:.1f}x)')
print(f'Components for 95% var: {n95} (compression: {X.shape[1]/n95:.1f}x)')

print('\nFinal closure prediction from reduced representation:')
for nc in [1,2,3,5,10,20]:
    if nc>X.shape[0]:continue
    pr=PCA(n_components=nc);xr=pr.fit_transform(X_scaled)
    lr=LinearRegression().fit(xr,y)
    print(f'  {nc} PCs: R²={r2_score(y,lr.predict(xr)):.4f}')

print('\nTemporal compression (last N timesteps):')
for nt in [1,5,10,20,50]:
    xt=np.array([t[-nt:] for t in trajs]);xs=StandardScaler().fit_transform(xt)
    lr=LinearRegression().fit(xs,y)
    print(f'  last {nt:3d} steps: R²={r2_score(y,lr.predict(xs)):.4f} (dim={nt*N})')

pd.DataFrame([{'pc':i+1,'var_ratio':vr[i],'cum_var':cv[i]} for i in range(min(20,len(vr)))]
    ).to_csv(f'{BASE}/outputs/R6_organizational_compression.csv',index=False)
print('R6 done')
