"""
Phase A1–A4: Generate independent simulated systems across multiple domains.
Compute structural descriptors AND behavioral outcomes INDEPENDENTLY.
"""
import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp, odeint
from scipy.spatial.distance import pdist, squareform
from scipy.stats import entropy
import warnings
warnings.filterwarnings('ignore')

SEED = 1000
rng = np.random.default_rng(SEED)

# ============ DOMAIN 1: CELLULAR AUTOMATA ============
def generate_ca_systems(n_systems=300):
    """Generate random 1D elementary cellular automata systems."""
    results = []
    for sid in range(n_systems):
        rule = rng.integers(0, 256)
        L = rng.integers(20, 60)                    # lattice size
        T = 150                                       # simulation steps
        pert_step = 80                                # perturbation at step 80

        # Random initial condition
        state = rng.integers(0, 2, L)
        traj = [state.copy()]
        for t in range(T):
            state = apply_ca_rule(state, rule)
            traj.append(state.copy())
        traj = np.array(traj)  # shape (T+1, L)

        # Unperturbed trajectory (first pert_step steps only)
        unpert = traj[:pert_step+1]

        # Perturbation: flip some bits
        pert_state = traj[pert_step].copy()
        n_flip = max(1, L // 10)
        flip_idx = rng.choice(L, n_flip, replace=False)
        pert_state[flip_idx] = 1 - pert_state[flip_idx]

        # Perturbed trajectory
        pert_traj = [pert_state.copy()]
        for t_step in range(pert_step, T):
            pert_traj.append(apply_ca_rule(pert_traj[-1], rule))
        pert_traj = np.array(pert_traj)  # shape (T - pert_step + 1, L)

        # Also: generate trajectory for computing structural descriptors
        state2 = rng.integers(0, 2, L)
        ref_traj = [state2.copy()]
        for t in range(T):
            ref_traj.append(apply_ca_rule(ref_traj[-1], rule))
        ref_traj = np.array(ref_traj)

        results.append({
            'sys_id': f'CA_{sid}',
            'domain': 'cellular_automata',
            'rule': rule,
            'L': L,
            'traj': traj,
            'pert_traj': pert_traj,
            'pert_step': pert_step,
            'ref_traj': ref_traj,
            'parameters': {'rule': rule, 'L': L},
        })
    return results

def apply_ca_rule(state, rule):
    """Apply elementary CA rule to 1D binary state."""
    L = len(state)
    new = np.zeros(L, dtype=int)
    for i in range(L):
        left = state[(i-1) % L]
        center = state[i]
        right = state[(i+1) % L]
        idx = 4*left + 2*center + right
        new[i] = (rule >> idx) & 1
    return new

# ============ DOMAIN 2: NONLINEAR OSCILLATORS (Duffing) ============
def generate_oscillator_systems(n_systems=300):
    """Generate random Duffing oscillator systems."""
    results = []
    sid = 0
    attempts = 0
    while len(results) < n_systems and attempts < n_systems * 5:
        attempts += 1
        delta = rng.uniform(0.01, 0.5)     # damping
        alpha = rng.uniform(-1.0, 1.0)     # linear stiffness
        beta = rng.uniform(-0.5, 0.5)      # nonlinear stiffness
        gamma = rng.uniform(0.0, 0.5)      # drive amplitude
        omega = rng.uniform(0.5, 2.0)      # drive frequency

        def duffing(t, state):
            x, v = state
            dx = v
            dv = -delta*v - alpha*x - beta*x**3 + gamma*np.cos(omega*t)
            return [dx, dv]

        T = 200
        n_pts = 500
        t_eval = np.linspace(0, T, n_pts)
        x0 = rng.uniform(-2, 2, 2)
        try:
            sol = solve_ivp(duffing, (0, T), x0, t_eval=t_eval, method='RK45', rtol=1e-6, atol=1e-8)
            if not sol.success or sol.y.shape[1] < 10:
                continue
            traj = sol.y.T
            # Perturbation at midpoint
            pert_idx = min(len(t_eval) // 2, sol.y.shape[1] - 1)
            x_pert = sol.y[:, pert_idx].copy() + rng.normal(0, 0.5, 2)
            t_pert = t_eval[pert_idx:]
            sol_pert = solve_ivp(duffing, (t_eval[pert_idx], T), x_pert,
                                 t_eval=t_pert, method='RK45', rtol=1e-6, atol=1e-8)
            if not sol_pert.success or sol_pert.y.shape[1] < 5:
                continue
            pert_traj = sol_pert.y.T
            # Reference trajectory
            x0_ref = rng.uniform(-2, 2, 2)
            sol_ref = solve_ivp(duffing, (0, T), x0_ref, t_eval=t_eval, method='RK45', rtol=1e-6, atol=1e-8)
            if not sol_ref.success:
                continue
            ref_traj = sol_ref.y.T
        except Exception:
            continue

        results.append({
            'sys_id': f'OSC_{sid}',
            'domain': 'nonlinear_oscillator',
            'params': {'delta': delta, 'alpha': alpha, 'beta': beta, 'gamma': gamma, 'omega': omega},
            'traj': traj,
            't_eval': t_eval[:traj.shape[0]],
            'pert_traj': pert_traj,
            'pert_idx': pert_idx,
            'ref_traj': ref_traj,
            'parameters': {'delta': delta, 'alpha': alpha, 'beta': beta, 'gamma': gamma, 'omega': omega},
        })
        sid += 1
    return results


# ============ DOMAIN 3: RANDOM GRAPH DIFFUSION ============
def generate_graph_systems(n_systems=300):
    """Generate random graph diffusion systems."""
    results = []
    for sid in range(n_systems):
        n_nodes = rng.integers(10, 40)
        p_edge = rng.uniform(0.1, 0.6)
        D = rng.uniform(0.01, 0.5)  # diffusion rate

        # Erdos-Renyi graph
        adj = np.zeros((n_nodes, n_nodes), dtype=float)
        for i in range(n_nodes):
            for j in range(i+1, n_nodes):
                if rng.random() < p_edge:
                    adj[i,j] = adj[j,i] = 1.0

        # Laplacian
        deg = adj.sum(axis=1)
        L_mat = np.diag(deg) - adj

        T = 200
        dt = 0.1
        n_steps = int(T / dt)

        # Initial concentration
        conc = rng.uniform(0, 1, n_nodes)
        conc = conc / conc.sum()

        traj = [conc.copy()]
        for t in range(n_steps):
            conc = conc - dt * D * L_mat @ conc
            conc = np.maximum(conc, 0)
            conc = conc / conc.sum()
            traj.append(conc.copy())
        traj = np.array(traj)

        # Perturbation at midpoint
        pert_idx = n_steps // 2
        conc_pert = traj[pert_idx].copy()
        pert_idx_conc = rng.integers(n_nodes)
        conc_pert[pert_idx_conc] += 0.5
        conc_pert = np.maximum(conc_pert, 0)
        conc_pert = conc_pert / conc_pert.sum()

        pert_traj = [conc_pert.copy()]
        for t in range(pert_idx, n_steps):
            conc_pert = conc_pert - dt * D * L_mat @ conc_pert
            conc_pert = np.maximum(conc_pert, 0)
            conc_pert = conc_pert / conc_pert.sum()
            pert_traj.append(conc_pert.copy())
        pert_traj = np.array(pert_traj)

        # Reference
        conc_ref = rng.uniform(0, 1, n_nodes)
        conc_ref = conc_ref / conc_ref.sum()
        ref_traj = [conc_ref.copy()]
        for t in range(n_steps):
            conc_ref = conc_ref - dt * D * L_mat @ conc_ref
            conc_ref = np.maximum(conc_ref, 0)
            conc_ref = conc_ref / conc_ref.sum()
            ref_traj.append(conc_ref.copy())
        ref_traj = np.array(ref_traj)

        results.append({
            'sys_id': f'GRAPH_{sid}',
            'domain': 'graph_diffusion',
            'adj': adj,
            'n_nodes': n_nodes,
            'p_edge': p_edge,
            'D': D,
            'traj': traj,
            'pert_traj': pert_traj,
            'pert_idx': pert_idx,
            'ref_traj': ref_traj,
            'parameters': {'n_nodes': n_nodes, 'p_edge': round(p_edge, 4), 'D': round(D, 4)},
        })
    return results

# ============ DOMAIN 4: EVOLUTIONARY POPULATION (Logistic Map Variants) ============
def generate_population_systems(n_systems=300):
    """Generate logistic map / population dynamics systems."""
    results = []
    for sid in range(n_systems):
        r = rng.uniform(0.5, 4.0)  # growth rate (covers all regimes)
        init_pop = rng.uniform(0.01, 0.99)

        T = 300
        traj = np.zeros(T+1)
        traj[0] = init_pop
        for t in range(T):
            traj[t+1] = r * traj[t] * (1 - traj[t])

        # Perturbation at midpoint
        pert_idx = T // 2
        pop_pert = traj[pert_idx] + rng.uniform(-0.2, 0.2)
        pop_pert = np.clip(pop_pert, 0.001, 0.999)

        pert_traj = np.zeros(T - pert_idx + 1)
        pert_traj[0] = pop_pert
        for t in range(pert_idx, T):
            pert_traj[t - pert_idx + 1] = r * pert_traj[t - pert_idx] * (1 - pert_traj[t - pert_idx])

        results.append({
            'sys_id': f'POP_{sid}',
            'domain': 'population',
            'r': r,
            'traj': traj,
            'pert_traj': pert_traj,
            'pert_idx': pert_idx,
            'ref_traj': traj.copy(),  # same dynamics
            'parameters': {'r': round(r, 4)},
        })
    return results

# ============ GENERATE ALL SYSTEMS ============
print('Generating CA systems...')
ca_systems = generate_ca_systems(200)
print(f'  {len(ca_systems)} generated')

print('Generating oscillator systems...')
osc_systems = generate_oscillator_systems(200)
print(f'  {len(osc_systems)} generated')

print('Generating graph systems...')
graph_systems = generate_graph_systems(200)
print(f'  {len(graph_systems)} generated')

print('Generating population systems...')
pop_systems = generate_population_systems(200)
print(f'  {len(pop_systems)} generated')

all_systems = ca_systems + osc_systems + graph_systems + pop_systems

# Save
import pickle
with open('/home/student/sgp_core_v2/phases/phaseA/phaseA_systems.pkl', 'wb') as f:
    pickle.dump(all_systems, f)

print(f'\nTotal systems generated: {len(all_systems)}')
print('Saved to phaseA_systems.pkl')
