"""
Phase C1 — System Generation.
5000+ systems across 10 dynamical families.
"""
import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
from scipy.stats import entropy, linregress
from scipy.spatial.distance import pdist, squareform
from sklearn.neighbors import NearestNeighbors
import pickle, os, warnings
warnings.filterwarnings('ignore')

SEED = 2000
rng = np.random.default_rng(SEED)
OUT = '/home/student/sgp_core_v2/phases/phaseC'

# ===================================================================
# DOMAIN 1: CELLULAR AUTOMATA (reuse from Phase A, expanded)
# ===================================================================
def apply_ca_rule(state, rule):
    L = len(state); new = np.zeros(L, dtype=int)
    for i in range(L):
        idx = 4*state[(i-1)%L] + 2*state[i] + state[(i+1)%L]
        new[i] = (rule >> idx) & 1
    return new

def generate_ca(n):
    results = []
    for sid in range(n):
        rule = rng.integers(0, 256)
        L = rng.integers(20, 60)
        T, pert_step = 150, 80
        state = rng.integers(0, 2, L)
        traj = [state.copy()]
        for t in range(T):
            traj.append(apply_ca_rule(traj[-1], rule))
        traj = np.array(traj)
        pert_state = traj[pert_step].copy()
        flip_idx = rng.choice(L, max(1, L//10), replace=False)
        pert_state[flip_idx] = 1 - pert_state[flip_idx]
        pert_traj = [pert_state.copy()]
        for t in range(pert_step, T):
            pert_traj.append(apply_ca_rule(pert_traj[-1], rule))
        pert_traj = np.array(pert_traj)
        state2 = rng.integers(0, 2, L)
        ref_traj = [state2.copy()]
        for t in range(T):
            ref_traj.append(apply_ca_rule(ref_traj[-1], rule))
        ref_traj = np.array(ref_traj)
        results.append({
            'sys_id': f'CA_{sid}', 'domain': 'cellular_automata',
            'traj': traj, 'pert_traj': pert_traj, 'ref_traj': ref_traj,
            'pert_step': pert_step, 'pert_idx': pert_step,
            'params': {'rule': int(rule), 'L': int(L)},
            'gen_params': {'rule': int(rule), 'L': int(L)},
        })
    return results

# ===================================================================
# DOMAIN 2: NONLINEAR OSCILLATOR (Duffing, expanded)
# ===================================================================
def generate_oscillator(n):
    results = []; sid = 0; attempts = 0
    while len(results) < n and attempts < n * 5:
        attempts += 1
        delta = rng.uniform(0.01, 0.5)
        alpha = rng.uniform(-1.0, 1.0)
        beta = rng.uniform(-0.5, 0.5)
        gamma = rng.uniform(0.0, 0.5)
        omega = rng.uniform(0.5, 2.0)
        def rhs(t, s):
            x, v = s; return [v, -delta*v - alpha*x - beta*x**3 + gamma*np.cos(omega*t)]
        T, n_pts = 200, 500
        t_eval = np.linspace(0, T, n_pts)
        try:
            sol = solve_ivp(rhs, (0,T), rng.uniform(-2,2,2), t_eval=t_eval,
                            method='RK45', rtol=1e-6, atol=1e-8)
            if not sol.success or sol.y.shape[1] < 10: continue
            traj = sol.y.T; pert_idx = min(len(t_eval)//2, sol.y.shape[1]-1)
            xp = sol.y[:, pert_idx].copy() + rng.normal(0, 0.5, 2)
            sol_p = solve_ivp(rhs, (t_eval[pert_idx], T), xp, t_eval=t_eval[pert_idx:],
                              method='RK45', rtol=1e-6, atol=1e-8)
            if not sol_p.success or sol_p.y.shape[1] < 5: continue
            sol_r = solve_ivp(rhs, (0,T), rng.uniform(-2,2,2), t_eval=t_eval,
                              method='RK45', rtol=1e-6, atol=1e-8)
            if not sol_r.success: continue
        except Exception: continue
        results.append({
            'sys_id': f'OSC_{sid}', 'domain': 'nonlinear_oscillator',
            'traj': traj, 't_eval': t_eval[:traj.shape[0]],
            'pert_traj': sol_p.y.T, 'pert_idx': pert_idx,
            'ref_traj': sol_r.y.T,
            'params': {'delta':delta,'alpha':alpha,'beta':beta,'gamma':gamma,'omega':omega},
            'gen_params': {'delta':delta,'alpha':alpha,'beta':beta,'gamma':gamma,'omega':omega},
        }); sid += 1
    return results

# ===================================================================
# DOMAIN 3: RANDOM GRAPH DIFFUSION (expanded)
# ===================================================================
def generate_graph(n):
    results = []
    for sid in range(n):
        nn = rng.integers(10, 40); pe = rng.uniform(0.1, 0.6); D = rng.uniform(0.01, 0.5)
        adj = np.zeros((nn,nn))
        for i in range(nn):
            for j in range(i+1, nn):
                if rng.random() < pe: adj[i,j] = adj[j,i] = 1.0
        deg = adj.sum(axis=1); Lm = np.diag(deg) - adj
        T, dt, n_steps = 200, 0.1, 2000
        conc = rng.uniform(0,1,nn); conc /= conc.sum()
        traj = [conc.copy()]
        for t in range(n_steps):
            conc = conc - dt*D*Lm@conc; conc = np.maximum(conc,0); conc /= conc.sum()
            traj.append(conc.copy())
        traj = np.array(traj)
        pert_idx = n_steps//2
        cp = traj[pert_idx].copy(); cp[rng.integers(nn)] += 0.5
        cp = np.maximum(cp,0); cp /= cp.sum()
        pert_traj = [cp.copy()]
        for t in range(pert_idx, n_steps):
            cp = cp - dt*D*Lm@cp; cp = np.maximum(cp,0); cp /= cp.sum()
            pert_traj.append(cp.copy())
        pert_traj = np.array(pert_traj)
        cr = rng.uniform(0,1,nn); cr /= cr.sum()
        ref_traj = [cr.copy()]
        for t in range(n_steps):
            cr = cr - dt*D*Lm@cr; cr = np.maximum(cr,0); cr /= cr.sum()
            ref_traj.append(cr.copy())
        ref_traj = np.array(ref_traj)
        results.append({
            'sys_id': f'GRAPH_{sid}', 'domain': 'graph_diffusion',
            'adj': adj, 'traj': traj, 'pert_traj': pert_traj, 'ref_traj': ref_traj,
            'pert_idx': pert_idx,
            'params': {'n_nodes':int(nn),'p_edge':round(pe,4),'D':round(D,4)},
            'gen_params': {'n_nodes':int(nn),'p_edge':round(pe,4),'D':round(D,4)},
        })
    return results

# ===================================================================
# DOMAIN 4: LOGISTIC POPULATION (expanded)
# ===================================================================
def generate_population(n):
    results = []
    for sid in range(n):
        r = rng.uniform(0.5, 4.0); init = rng.uniform(0.01, 0.99)
        T = 300; traj = np.zeros(T+1); traj[0] = init
        for t in range(T): traj[t+1] = r*traj[t]*(1-traj[t])
        pert_idx = T//2
        pp = traj[pert_idx] + rng.uniform(-0.2, 0.2); pp = np.clip(pp, 0.001, 0.999)
        pert_traj = np.zeros(T-pert_idx+1); pert_traj[0] = pp
        for t in range(pert_idx, T): pert_traj[t-pert_idx+1] = r*pert_traj[t-pert_idx]*(1-pert_traj[t-pert_idx])
        results.append({
            'sys_id': f'POP_{sid}', 'domain': 'population',
            'traj': traj, 'pert_traj': pert_traj, 'ref_traj': traj.copy(),
            'pert_idx': pert_idx,
            'params': {'r': round(r,4)},
            'gen_params': {'r': round(r,4)},
        })
    return results

# ===================================================================
# DOMAIN 5: GRAY-SCOTT REACTION-DIFFUSION
# ===================================================================
def generate_gray_scott(n):
    results = []; sid = 0; attempts = 0
    while len(results) < n and attempts < n * 3:
        attempts += 1
        Du = rng.uniform(0.01, 0.2); Dv = rng.uniform(0.005, 0.1)
        F = rng.uniform(0.01, 0.06); k = rng.uniform(0.04, 0.08)
        L = rng.integers(20, 40); T = 500; dt = 1.0; n_steps = int(T/dt)
        n_report = 200
        u = np.ones((L,L)); v = np.zeros((L,L))
        # Seed
        cx, cy = L//2, L//2; sz = 5
        u[cx-sz:cx+sz, cy-sz:cy+sz] = 0.5
        v[cx-sz:cx+sz, cy-sz:cy+sz] = 0.25
        report_interval = max(1, n_steps // n_report)
        traj_u, traj_v = [], []
        for step in range(1, n_steps+1):
            lap_u = (np.roll(u,1,0)+np.roll(u,-1,0)+np.roll(u,1,1)+np.roll(u,-1,1)-4*u)/4
            lap_v = (np.roll(v,1,0)+np.roll(v,-1,0)+np.roll(v,1,1)+np.roll(v,-1,1)-4*v)/4
            uvv = u*v*v
            u += dt*(Du*lap_u - uvv + F*(1-u))
            v += dt*(Dv*lap_v + uvv - (F+k)*v)
            u = np.clip(u, 0, 1); v = np.clip(v, 0, 1)
            if step % report_interval == 0:
                traj_u.append(u.copy()); traj_v.append(v.copy())
        traj_u = np.array(traj_u); traj_v = np.array(traj_v)
        if traj_u.shape[0] < 10: continue
        # Assemble trajectory as mean u + pattern entropy per step
        mean_u = traj_u.mean(axis=(1,2))
        flat_hist = np.array([np.histogram(traj_u[i].ravel(), bins=10, range=(0,1))[0] for i in range(len(traj_u))])
        pat_ent = np.array([entropy(h/h.sum()) if h.sum()>0 else 0 for h in flat_hist])
        traj = np.column_stack([mean_u, pat_ent])
        # Perturbation at midpoint: inject u at center
        pert_idx = len(traj)//2
        # Find current state
        u_pert = traj_u[pert_idx].copy(); v_pert = traj_v[pert_idx].copy()
        u_pert[L//2, L//2] += 0.3; u_pert = np.clip(u_pert, 0, 1)
        # Run perturbed evolution
        tu2, tv2 = [u_pert.copy()], [v_pert.copy()]
        for step in range(1, n_steps+1):
            lap_u = (np.roll(u_pert,1,0)+np.roll(u_pert,-1,0)+np.roll(u_pert,1,1)+np.roll(u_pert,-1,1)-4*u_pert)/4
            lap_v = (np.roll(v_pert,1,0)+np.roll(v_pert,-1,0)+np.roll(v_pert,1,1)+np.roll(v_pert,-1,1)-4*v_pert)/4
            uvv = u_pert*v_pert*v_pert
            u_pert += dt*(Du*lap_u - uvv + F*(1-u_pert))
            v_pert += dt*(Dv*lap_v + uvv - (F+k)*v_pert)
            u_pert = np.clip(u_pert,0,1); v_pert = np.clip(v_pert,0,1)
            if step % report_interval == 0:
                tu2.append(u_pert.copy())
        tu2 = np.array(tu2)
        mean_u2 = tu2.mean(axis=(1,2))
        flat_hist2 = np.array([np.histogram(tu2[i].ravel(), bins=10, range=(0,1))[0] for i in range(len(tu2))])
        pat_ent2 = np.array([entropy(h/h.sum()) if h.sum()>0 else 0 for h in flat_hist2])
        pert_traj = np.column_stack([mean_u2, pat_ent2])
        # Reference from different IC
        u_ref = np.ones((L,L)); v_ref = np.zeros((L,L))
        sz = max(3, L // 4)
        cx, cy = L//2, L//2
        u_ref[cx-sz:cx+sz, cy-sz:cy+sz] = rng.uniform(0, 1, (2*sz, 2*sz))
        v_ref[cx-sz:cx+sz, cy-sz:cy+sz] = rng.uniform(0, 0.5, (2*sz, 2*sz))
        tu_r, tv_r = [u_ref.copy()], [v_ref.copy()]
        for step in range(1, n_steps+1):
            lap_u = (np.roll(u_ref,1,0)+np.roll(u_ref,-1,0)+np.roll(u_ref,1,1)+np.roll(u_ref,-1,1)-4*u_ref)/4
            lap_v = (np.roll(v_ref,1,0)+np.roll(v_ref,-1,0)+np.roll(v_ref,1,1)+np.roll(v_ref,-1,1)-4*v_ref)/4
            uvv = u_ref*v_ref*v_ref
            u_ref += dt*(Du*lap_u - uvv + F*(1-u_ref))
            v_ref += dt*(Dv*lap_v + uvv - (F+k)*v_ref)
            u_ref = np.clip(u_ref,0,1); v_ref = np.clip(v_ref,0,1)
            if step % report_interval == 0:
                tu_r.append(u_ref.copy())
        tu_r = np.array(tu_r)
        mu_r = tu_r.mean(axis=(1,2))
        fh_r = np.array([np.histogram(tu_r[i].ravel(), bins=10, range=(0,1))[0] for i in range(len(tu_r))])
        pe_r = np.array([entropy(h/h.sum()) if h.sum()>0 else 0 for h in fh_r])
        ref_traj = np.column_stack([mu_r, pe_r])
        results.append({
            'sys_id': f'GS_{sid}', 'domain': 'gray_scott',
            'traj': traj, 'pert_traj': pert_traj, 'ref_traj': ref_traj,
            'pert_idx': min(pert_idx, len(pert_traj)-1),
            'params': {'Du':Du,'Dv':Dv,'F':F,'k':k,'L':int(L)},
            'gen_params': {'Du':Du,'Dv':Dv,'F':F,'k':k,'L':int(L)},
        }); sid += 1
    return results

# ===================================================================
# DOMAIN 6: KURAMOTO NETWORK SYNCHRONIZATION
# ===================================================================
def generate_kuramoto(n):
    results = []; sid = 0; attempts = 0
    while len(results) < n and attempts < n * 3:
        attempts += 1
        N = rng.integers(10, 50); K = rng.uniform(0, 3.0)
        w_width = rng.uniform(0.1, 2.0)
        omegas = rng.normal(0, w_width, N)
        T, dt, n_steps = 100, 0.05, 2000
        report_interval = max(1, n_steps // 200)
        theta = rng.uniform(0, 2*np.pi, N)
        traj_r = []
        for step in range(n_steps):
            phases = theta
            sin_sum = np.sin(theta - phases[:,None]).sum(axis=0)/N
            theta = theta + dt*(omegas + K*sin_sum)
            r_ord = abs(np.exp(1j*theta).mean())
            if step % report_interval == 0: traj_r.append(r_ord)
        traj = np.array(traj_r).reshape(-1,1)
        if len(traj) < 10: continue
        pert_idx = len(traj)//2
        theta_p = theta.copy(); theta_p[rng.integers(N)] += np.pi
        theta = theta_p; pert_r = []
        for step in range(pert_idx*report_interval, n_steps):
            sin_sum = np.sin(theta - theta[:,None]).sum(axis=0)/N
            theta = theta + dt*(omegas + K*sin_sum)
            r_ord = abs(np.exp(1j*theta).mean())
            pert_r.append(r_ord)
        pert_traj = np.array(pert_r).reshape(-1,1)
        # Reference from different IC
        theta_r = rng.uniform(0, 2*np.pi, N); ref_r = []
        for step in range(n_steps):
            sin_sum = np.sin(theta_r - theta_r[:,None]).sum(axis=0)/N
            theta_r = theta_r + dt*(omegas + K*sin_sum)
            r_ord = abs(np.exp(1j*theta_r).mean())
            if step % report_interval == 0: ref_r.append(r_ord)
        ref_traj = np.array(ref_r).reshape(-1,1)
        results.append({
            'sys_id': f'KUR_{sid}', 'domain': 'kuramoto',
            'traj': traj, 'pert_traj': pert_traj, 'ref_traj': ref_traj,
            'pert_idx': min(pert_idx, len(pert_traj)-1),
            'params': {'N':int(N),'K':round(K,4),'w_width':round(w_width,4)},
            'gen_params': {'N':int(N),'K':round(K,4),'w_width':round(w_width,4)},
        }); sid += 1
    return results

# ===================================================================
# DOMAIN 7: LOTKA-VOLTERRA (predator-prey)
# ===================================================================
def generate_lotka_volterra(n):
    results = []; sid = 0; attempts = 0
    while len(results) < n and attempts < n * 3:
        attempts += 1
        alpha = rng.uniform(0.5, 2.0); beta = rng.uniform(0.01, 0.05)
        delta = rng.uniform(0.01, 0.05); gamma = rng.uniform(0.5, 2.0)
        def rhs(t, s):
            x, y = s; return [alpha*x - beta*x*y, delta*x*y - gamma*y]
        T, n_pts = 200, 500
        t_eval = np.linspace(0, T, n_pts)
        try:
            sol = solve_ivp(rhs, (0,T), rng.uniform(1,10,2), t_eval=t_eval,
                            method='RK45', rtol=1e-6, atol=1e-8)
            if not sol.success or sol.y.shape[1] < 10: continue
            traj = sol.y.T
            pert_idx = min(len(t_eval)//2, sol.y.shape[1]-1)
            xp = sol.y[:, pert_idx].copy() * rng.uniform(1.5, 3.0)
            sol_p = solve_ivp(rhs, (t_eval[pert_idx], T), xp, t_eval=t_eval[pert_idx:],
                              method='RK45', rtol=1e-6, atol=1e-8)
            if not sol_p.success or sol_p.y.shape[1] < 5: continue
            sol_r = solve_ivp(rhs, (0,T), rng.uniform(1,10,2), t_eval=t_eval,
                              method='RK45', rtol=1e-6, atol=1e-8)
            if not sol_r.success: continue
        except Exception: continue
        results.append({
            'sys_id': f'LV_{sid}', 'domain': 'lotka_volterra',
            'traj': traj, 't_eval': t_eval[:traj.shape[0]],
            'pert_traj': sol_p.y.T, 'pert_idx': pert_idx,
            'ref_traj': sol_r.y.T,
            'params': {'alpha':alpha,'beta':beta,'delta':delta,'gamma':gamma},
            'gen_params': {'alpha':alpha,'beta':beta,'delta':delta,'gamma':gamma},
        }); sid += 1
    return results

# ===================================================================
# DOMAIN 8: COUPLED MAP LATTICE (CML - logistic)
# ===================================================================
def generate_cml(n):
    results = []
    for sid in range(n):
        L = rng.integers(10, 40); r = rng.uniform(2.5, 4.0)
        eps = rng.uniform(0.05, 0.5)
        T, n_steps = 100, 1000
        report_interval = 5
        def logistic(x): return r*x*(1-x)
        x = rng.uniform(0, 1, L)
        traj = []
        for step in range(n_steps):
            x_new = (1-eps)*logistic(x) + (eps/2)*(np.roll(logistic(x),1)+np.roll(logistic(x),-1))
            x = x_new
            if step % report_interval == 0:
                traj.append(x.copy())
        traj = np.array(traj)
        if len(traj) < 10: continue
        pert_idx = len(traj)//2
        xp = traj[pert_idx].copy(); xp[rng.integers(L)] = rng.uniform(0,1)
        x = xp; pert_traj = [xp.copy()]
        for step in range(1, n_steps - pert_idx*report_interval):
            x_new = (1-eps)*logistic(x) + (eps/2)*(np.roll(logistic(x),1)+np.roll(logistic(x),-1))
            x = x_new
            if step % report_interval == 0:
                pert_traj.append(x.copy())
        pert_traj = np.array(pert_traj)
        xr = rng.uniform(0, 1, L); ref_traj = [xr.copy()]
        for step in range(1, n_steps):
            x_new = (1-eps)*logistic(xr) + (eps/2)*(np.roll(logistic(xr),1)+np.roll(logistic(xr),-1))
            xr = x_new
            if step % report_interval == 0:
                ref_traj.append(xr.copy())
        ref_traj = np.array(ref_traj)
        results.append({
            'sys_id': f'CML_{sid}', 'domain': 'coupled_map_lattice',
            'traj': traj, 'pert_traj': pert_traj, 'ref_traj': ref_traj,
            'pert_idx': min(pert_idx, len(pert_traj)-1),
            'params': {'L':int(L),'r':round(r,4),'eps':round(eps,4)},
            'gen_params': {'L':int(L),'r':round(r,4),'eps':round(eps,4)},
        })
    return results

# ===================================================================
# DOMAIN 9: REPLICATOR DYNAMICS (evolutionary game theory)
# ===================================================================
def generate_replicator(n):
    results = []; sid = 0; attempts = 0
    while len(results) < n and attempts < n * 3:
        attempts += 1
        n_strat = rng.integers(3, 6)
        A = rng.uniform(-1, 2, (n_strat, n_strat))
        A = (A + A.T) / 2  # symmetric games
        T, n_pts = 100, 500
        t_eval = np.linspace(0, T, n_pts)
        x0 = rng.dirichlet(np.ones(n_strat))
        def rhs(t, s):
            x = np.maximum(s, 0); x = x / x.sum()
            Ax = A @ x; return x * (Ax - x@Ax)
        try:
            sol = solve_ivp(rhs, (0,T), x0, t_eval=t_eval, method='RK45', rtol=1e-6, atol=1e-8)
            if not sol.success or sol.y.shape[1] < 10: continue
            traj = sol.y.T; traj = np.clip(traj, 0, 1)
            pert_idx = min(len(t_eval)//2, sol.y.shape[1]-1)
            xp = sol.y[:, pert_idx].copy()
            xp += rng.normal(0, 0.1, n_strat); xp = np.clip(xp, 0.001, None); xp /= xp.sum()
            sol_p = solve_ivp(rhs, (t_eval[pert_idx], T), xp, t_eval=t_eval[pert_idx:],
                              method='RK45', rtol=1e-6, atol=1e-8)
            if not sol_p.success or sol_p.y.shape[1] < 5: continue
            sol_r = solve_ivp(rhs, (0,T), rng.dirichlet(np.ones(n_strat)), t_eval=t_eval,
                              method='RK45', rtol=1e-6, atol=1e-8)
            if not sol_r.success: continue
        except Exception: continue
        results.append({
            'sys_id': f'REP_{sid}', 'domain': 'replicator',
            'traj': traj, 't_eval': t_eval[:traj.shape[0]],
            'pert_traj': sol_p.y.T, 'pert_idx': pert_idx,
            'ref_traj': sol_r.y.T, 'A': A,
            'params': {'n_strat':int(n_strat)},
            'gen_params': {'n_strat':int(n_strat)},
        }); sid += 1
    return results

# ===================================================================
# DOMAIN 10: BRANCHING PROCESS (Galton-Watson)
# ===================================================================
def generate_branching(n):
    results = []
    for sid in range(n):
        lam = rng.uniform(0.1, 2.5)  # mean offspring
        dist_type = rng.choice(['poisson', 'geometric'])
        T = 30
        def run_process(Z0, T):
            Z = np.zeros(T+1, dtype=float); Z[0] = Z0
            for t in range(T):
                if Z[t] < 1: break
                if dist_type == 'poisson':
                    Z[t+1] = rng.poisson(lam, int(max(1, Z[t]))).sum()
                else:
                    Z[t+1] = rng.geometric(1/(1+lam), int(max(1, Z[t]))).sum()
            return Z
        Z0 = rng.integers(5, 50)
        traj = run_process(Z0, T)
        # Perturbation: add extra individuals at midpoint
        pert_idx = T//2
        Z_pert = traj[pert_idx] + rng.poisson(max(1, traj[pert_idx]))
        pert_traj = run_process(max(1, Z_pert), T-pert_idx)
        # Reference trajectory
        ref_traj = run_process(rng.integers(5, 50), T)
        results.append({
            'sys_id': f'BR_{sid}', 'domain': 'branching',
            'traj': traj.reshape(-1,1), 'pert_traj': pert_traj.reshape(-1,1),
            'ref_traj': ref_traj.reshape(-1,1),
            'pert_idx': min(pert_idx, len(pert_traj)-1),
            'params': {'lambda':round(lam,4),'dist':dist_type,'Z0':int(Z0)},
            'gen_params': {'lambda':round(lam,4),'dist':dist_type,'Z0':int(Z0)},
        })
    return results

# ===================================================================
# GENERATOR REGISTRY
# ===================================================================
GENERATORS = {
    'cellular_automata':     (generate_ca, 500),
    'nonlinear_oscillator':  (generate_oscillator, 500),
    'graph_diffusion':       (generate_graph, 500),
    'population':            (generate_population, 500),
    'gray_scott':            (generate_gray_scott, 500),
    'kuramoto':              (generate_kuramoto, 500),
    'lotka_volterra':        (generate_lotka_volterra, 500),
    'coupled_map_lattice':   (generate_cml, 500),
    'replicator':            (generate_replicator, 500),
    'branching':             (generate_branching, 500),
}

def generate_all():
    all_systems = []
    for name, (gen_fn, n) in GENERATORS.items():
        print(f'Generating {name} ({n} systems)...')
        sys = gen_fn(n)
        print(f'  {len(sys)} generated')
        all_systems.extend(sys)
    # Save raw systems
    pkl_path = os.path.join(OUT, 'phaseC_systems.pkl')
    with open(pkl_path, 'wb') as f:
        pickle.dump(all_systems, f)
    print(f'\nTotal: {len(all_systems)} systems -> {pkl_path}')
    return all_systems

if __name__ == '__main__':
    generate_all()
