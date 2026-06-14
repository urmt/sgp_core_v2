"""
Phase C1 — Streaming Generation + Metrics Pipeline.
Generates 5000+ systems across 10 families, writing directly to CSV.
One row at a time, no trajectory accumulation.
"""
import numpy as np, pandas as pd, os, warnings, signal, sys
from scipy.integrate import solve_ivp
from scipy.stats import entropy, linregress, pearsonr
warnings.filterwarnings('ignore')

SEED = 2000; rng = np.random.default_rng(SEED)
OUT = '/home/student/sgp_core_v2/phases/phaseC'
CSV = os.path.join(OUT, 'phaseC_metrics.csv')

# Helper: write header if first write
def write_row(row, first=False):
    df = pd.DataFrame([row])
    df.to_csv(CSV, mode='w' if first else 'a', header=first, index=False)

# ==============================================================
# CA (fastest — no ODE solver)
# ==============================================================
def apply_ca(state, rule):
    L = len(state); n = np.zeros(L, dtype=int)
    for i in range(L):
        idx = 4*state[(i-1)%L] + 2*state[i] + state[(i+1)%L]
        n[i] = (rule >> idx) & 1
    return n

def gen_ca_rows(prefix='CA'):
    for sid in range(500):
        rule = int(rng.integers(0, 256)); L = int(rng.integers(20, 60))
        T, ps = 150, 80
        s = rng.integers(0, 2, L)
        traj = [s.copy()]
        for t in range(T): traj.append(apply_ca(traj[-1], rule))
        traj = np.array(traj)
        # Perturb
        ps2 = traj[ps].copy()
        fi = rng.choice(L, max(1, L//10), replace=False)
        ps2[fi] = 1 - ps2[fi]
        pt = [ps2.copy()]
        for t in range(ps, T): pt.append(apply_ca(pt[-1], rule))
        pt = np.array(pt)
        # Ref
        s2 = rng.integers(0, 2, L)
        rt = [s2.copy()]
        for t in range(T): rt.append(apply_ca(rt[-1], rule))
        rt = np.array(rt)
        # Stability
        up = traj[ps:]; n2 = min(len(pt), len(up)); p2=pt[:n2]; u2=up[:n2]
        ham = np.mean(p2 != u2, axis=1)
        rtm = np.argmax(ham < 0.1) if np.any(ham < 0.1) else len(ham)
        if len(ham) > 3 and ham[0] > 0:
            sl = linregress(np.arange(len(ham)), np.log(np.clip(ham, 1e-10, None))).slope; rr = -sl
        else: rr = 0.0
        # Fertility
        sb = [r.tobytes() for r in rt]
        uq = len(set(sb)); n3 = len(sb)
        seen = set(); fs = [0]
        for b in sb:
            if b not in seen: seen.add(b); fs.append(1)
            else: fs.append(0)
        trans = [(sb[i], sb[i+1]) for i in range(len(sb)-1)]
        _, ct = np.unique(trans, axis=0, return_counts=True) if len(trans) > 0 else ([], np.array([1]))
        te = entropy(ct/ct.sum()) if len(ct) > 1 else 0.0
        # Descriptors
        bits = [(rule>>i)&1 for i in range(8)]
        p1 = sum(bits)/8; csr = entropy([p1, 1-p1]) if 0 < p1 < 1 else 0.0
        rbs = sum(bits)/8.0
        st = traj[:,0]
        adi = float(abs(np.corrcoef(st[:-1], st[1:])[0,1])) if len(st)>5 and np.std(st[:-1])>0 and np.std(st[1:])>0 else 0.0
        trans2 = [(sb[i], sb[i+1]) for i in range(min(len(sb)-1, 50))]
        _, ct2 = np.unique(trans2, return_counts=True) if len(set(trans2)) > 1 else ([], np.array([1]))
        rtp = entropy(ct2/ct2.sum()) if len(ct2) > 1 else 0.0
        srd = float(2**L)
        yield dict(stability_return_time=float(rtm), stability_recovery_rate=float(rr),
                   stability_final_dev=float(ham[-1]), stability_max_dev=float(np.max(ham)),
                   fertility_state_diversity=float(uq/n3), fertility_novelty_rate=float(np.mean(fs[1:])),
                   fertility_state_coverage=float(uq/max(1,2**L)),
                   fertility_transition_entropy=float(te),
                   CSR=float(csr), RBS=float(rbs), ADI=float(adi), RTP=float(rtp), SRD=float(srd))

# ==============================================================
# POPULATION (fast — discrete map)
# ==============================================================
def gen_pop_rows(prefix='POP'):
    for sid in range(500):
        r = rng.uniform(0.5, 4.0); init = rng.uniform(0.01, 0.99)
        T = 300; traj = np.zeros(T+1); traj[0] = init
        for t in range(T): traj[t+1] = r*traj[t]*(1-traj[t])
        pi = T//2
        pp = traj[pi] + rng.uniform(-0.2, 0.2); pp = np.clip(pp, 0.001, 0.999)
        pt = np.zeros(T-pi+1); pt[0] = pp
        for t in range(pi, T): pt[t-pi+1] = r*pt[t-pi]*(1-pt[t-pi])
        # Stability
        up = traj[pi:]; n2 = min(len(pt), len(up)); p2=pt[:n2]; u2=up[:n2]
        dists = np.abs(p2 - u2)
        rtm = np.argmax(dists < 0.01) if np.any(dists < 0.01) else len(dists)
        if len(dists) > 3 and dists[0] > 1e-8:
            sl = linregress(np.arange(len(dists)), np.log(np.clip(dists, 1e-10, None))).slope; rr = -sl
        else: rr = 0.0
        # Fertility
        rf = ref = traj.copy(); rf = rf.flatten()
        bins = np.linspace(rf.min(), rf.max(), 20) if np.ptp(rf) > 0 else np.arange(20)
        disc = np.digitize(rf, bins); uq = len(set(disc))
        seen = set(); fs = [0]
        for s in disc:
            if s not in seen: seen.add(s); fs.append(1)
            else: fs.append(0)
        trans = [(disc[i], disc[i+1]) for i in range(len(disc)-1)]
        _, ct = np.unique(trans, axis=0, return_counts=True) if len(trans) > 0 else ([], np.array([1]))
        te = entropy(ct/ct.sum()) if len(ct) > 1 else 0.0
        # Descriptors
        nb2 = 20; bins2 = np.linspace(0, 1, nb2)
        disc2 = np.digitize(traj, bins2).flatten()
        counts = np.bincount(disc2, minlength=nb2+1)[:nb2]
        fracs = counts / (counts.sum() + 1e-10)
        csr = entropy(fracs) / np.log(nb2); rbs = abs(r - 2.5)
        x = traj.flatten()
        adi = float(abs(np.corrcoef(x[:-1], x[1:])[0,1])) if len(x)>10 and np.std(x[:-1])>1e-10 and np.std(x[1:])>1e-10 else 0.0
        if len(x) > 10 and np.std(x) > 1e-10:
            fn = np.abs(np.fft.fft(x - x.mean())); fn /= fn.sum() + 1e-10; rtp = entropy(fn) / np.log(len(fn))
        else: rtp = 0.0
        yield dict(stability_return_time=float(rtm), stability_recovery_rate=float(rr),
                   stability_final_dev=float(dists[-1]), stability_max_dev=float(np.max(dists)),
                   fertility_state_diversity=float(uq/20), fertility_novelty_rate=float(np.mean(fs[1:])),
                   fertility_state_coverage=float(uq/20), fertility_transition_entropy=float(te),
                   CSR=float(csr), RBS=float(rbs), ADI=float(adi), RTP=float(rtp), SRD=float(r))

# ==============================================================
# GRAPH DIFFUSION (moderate)
# ==============================================================
def gen_graph_rows(prefix='GRAPH'):
    for sid in range(500):
        nn = int(rng.integers(10, 40)); pe = rng.uniform(0.1, 0.6); D = rng.uniform(0.01, 0.5)
        adj = np.zeros((nn,nn))
        for i in range(nn):
            for j in range(i+1, nn):
                if rng.random() < pe: adj[i,j] = adj[j,i] = 1.0
        deg = adj.sum(axis=1); Lm = np.diag(deg) - adj
        T, dt, ns2 = 200, 0.1, 2000
        conc = rng.uniform(0,1,nn); conc /= conc.sum()
        traj = [conc.copy()]
        for t in range(ns2):
            conc = conc - dt*D*Lm@conc; conc = np.maximum(conc,0); conc /= conc.sum()
            traj.append(conc.copy())
        traj = np.array(traj); pi = ns2//2
        cp = traj[pi].copy(); cp[rng.integers(nn)] += 0.5
        cp = np.maximum(cp,0); cp /= cp.sum()
        pt = [cp.copy()]
        for t in range(pi, ns2):
            cp = cp - dt*D*Lm@cp; cp = np.maximum(cp,0); cp /= cp.sum()
            pt.append(cp.copy())
        pt = np.array(pt)
        cr = rng.uniform(0,1,nn); cr /= cr.sum()
        ref = [cr.copy()]
        for t in range(ns2):
            cr = cr - dt*D*Lm@cr; cr = np.maximum(cr,0); cr /= cr.sum()
            ref.append(cr.copy())
        ref = np.array(ref)
        # Stability
        up = traj[pi:]; n2 = min(len(pt), len(up)); p2=pt[:n2]; u2=up[:n2]
        dists = np.sum(np.abs(p2-u2), axis=1)
        rtm = np.argmax(dists < 0.01) if np.any(dists < 0.01) else len(dists)
        if len(dists) > 3 and dists[0] > 1e-8:
            sl = linregress(np.arange(len(dists)), np.log(np.clip(dists, 1e-10, None))).slope; rr = -sl
        else: rr = 0.0
        # Fertility
        nb = 10
        keys = [tuple(np.digitize(r, np.linspace(0,1,nb))) for r in ref]
        uq = len(set(keys)); n3 = len(keys)
        seen = set(); fs = [0]
        for s in keys:
            if s not in seen: seen.add(s); fs.append(1)
            else: fs.append(0)
        trans = [(keys[i], keys[i+1]) for i in range(len(keys)-1)]
        _, ct = np.unique(trans, axis=0, return_counts=True) if len(trans) > 0 else ([], np.array([1]))
        te = entropy(ct/ct.sum()) if len(ct) > 1 else 0.0
        # Descriptors
        dg = deg / max(1, deg.sum()); csr = entropy(dg) if deg.sum() > 0 else 0.0
        degb = (adj>0).astype(float)
        num = degb @ degb @ degb; den = np.diag(degb @ degb) * (np.diag(degb @ degb) - 1) + 1e-10
        rbs = float(np.mean(np.diag(num)/den))
        levs = np.sort(np.linalg.eigvalsh(Lm)); adi = float(levs[1]) if len(levs) > 1 else 0.0
        rtp = csr / np.log(nn) if nn > 1 else 0.0; srd = float(nn)
        yield dict(stability_return_time=float(rtm), stability_recovery_rate=float(rr),
                   stability_final_dev=float(dists[-1]), stability_max_dev=float(np.max(dists)),
                   fertility_state_diversity=float(uq/min(nb**min(nn,5), n3)),
                   fertility_novelty_rate=float(np.mean(fs[1:])),
                   fertility_state_coverage=float(uq/min(nb**min(nn,5), n3)),
                   fertility_transition_entropy=float(te),
                   CSR=float(csr), RBS=float(rbs), ADI=float(adi), RTP=float(rtp), SRD=float(srd))

# ==============================================================
# BRANCHING (fast)
# ==============================================================
def gen_branch_rows(prefix='BR'):
    for sid in range(500):
        lam = rng.uniform(0.1, 2.5); dt2 = rng.choice(['poisson','geometric']); Z0 = int(rng.integers(5,50))
        T2 = 30
        def runp(Z0, T2):
            Z = np.zeros(T2+1, dtype=float); Z[0] = Z0
            for t in range(T2):
                if Z[t] < 1 or Z[t] > 1e5: break
                n = int(min(max(1, Z[t]), 10000))
                if dt2 == 'poisson': Z[t+1] = rng.poisson(lam, n).sum()
                else:
                    # Geometric sum: process in chunks to avoid large allocation
                    total = 0
                    for _ in range(n):
                        total += rng.geometric(1/(1+lam), 1)[0]
                    Z[t+1] = total
            return Z
        traj = runp(Z0, T2); pi = T2//2
        Zp = traj[pi] + rng.poisson(max(1, traj[pi]))
        pt = runp(max(1, Zp), T2-pi); ref = runp(int(rng.integers(5,50)), T2)
        # Stability
        up = traj[pi:]; n2 = min(len(pt), len(up)); p2=pt[:n2]; u2=up[:n2]
        dists = np.abs(p2 - u2)
        rtm = np.argmax(dists < 1.0) if np.any(dists < 1.0) else len(dists)
        if len(dists) > 3 and dists[0] > 1e-8:
            sl = linregress(np.arange(len(dists)), np.log(np.clip(dists, 1e-10, None))).slope; rr = -sl
        else: rr = 0.0
        # Fertility
        rf = ref.flatten()
        bins = np.linspace(rf.min(), rf.max(), 15) if np.ptp(rf) > 0 else np.arange(15)
        disc = np.digitize(rf, bins); uq = len(set(disc))
        seen = set(); fs = [0]
        for s in disc:
            if s not in seen: seen.add(s); fs.append(1)
            else: fs.append(0)
        trans = [(disc[i], disc[i+1]) for i in range(len(disc)-1)]
        _, ct = np.unique(trans, axis=0, return_counts=True) if len(trans) > 0 else ([], np.array([1]))
        te = entropy(ct/ct.sum()) if len(ct) > 1 else 0.0
        # Descriptors
        csr = float(lam/2.5); rbs = float(max(0, lam-1.0))
        tj = traj.flatten()
        adi = float(abs(np.corrcoef(tj[:-1], tj[1:])[0,1])) if len(tj)>5 and np.std(tj[:-1])>0 and np.std(tj[1:])>0 else 0.0
        rtp = 0.0; srd = 1.0
        yield dict(stability_return_time=float(rtm), stability_recovery_rate=float(rr),
                   stability_final_dev=float(dists[-1]), stability_max_dev=float(np.max(dists)),
                   fertility_state_diversity=float(uq/15), fertility_novelty_rate=float(np.mean(fs[1:])),
                   fertility_state_coverage=float(uq/15), fertility_transition_entropy=float(te),
                   CSR=float(csr), RBS=float(rbs), ADI=float(adi), RTP=float(rtp), SRD=float(srd))

# ==============================================================
# NONLINEAR OSCILLATOR (solve_ivp — robust timeout)
# ==============================================================
def gen_osc_rows(prefix='OSC'):
    def rhs_factory(p):
        d, a, b, g, w = p['delta'],p['alpha'],p['beta'],p['gamma'],p['omega']
        def rhs(t,s): x,v=s; return [v, -d*v - a*x - b*x**3 + g*np.cos(w*t)]
        return rhs
    T,np2=200,500; te=np.linspace(0,T,np2)
    sid=0; attempts=0
    while sid < 500 and attempts < 2500:
        attempts+=1
        try:
            p = dict(delta=rng.uniform(0.01,0.5), alpha=rng.uniform(-1,1),
                     beta=rng.uniform(-0.5,0.5), gamma=rng.uniform(0,0.5),
                     omega=rng.uniform(0.5,2.0))
            so = solve_ivp(rhs_factory(p), (0,T), rng.uniform(-2,2,2), t_eval=te,
                           method='RK45', rtol=1e-6, atol=1e-8)
            if not so.success or so.y.shape[1] < 10: continue
            traj = so.y.T; pi = min(len(te)//2, so.y.shape[1]-1)
            xp = so.y[:,pi].copy() + rng.normal(0,0.5,2)
            sp = solve_ivp(rhs_factory(p), (te[pi],T), xp, t_eval=te[pi:],
                           method='RK45', rtol=1e-6, atol=1e-8)
            if not sp.success or sp.y.shape[1] < 5: continue
            sr = solve_ivp(rhs_factory(p), (0,T), rng.uniform(-2,2,2), t_eval=te,
                           method='RK45', rtol=1e-6, atol=1e-8)
            if not sr.success: continue
            ref = sr.y.T
        except: continue
        # Stability
        up = traj[pi:]; n2 = min(len(sp.y.T), len(up)); pt2=sp.y.T[:n2]; up2=up[:n2]
        dists = np.sqrt(np.sum((pt2-up2)**2, axis=1))
        rtm = np.argmax(dists < 0.1) if np.any(dists < 0.1) else len(dists)
        if len(dists) > 3 and dists[0] > 1e-8:
            sl = linregress(np.arange(len(dists)), np.log(np.clip(dists, 1e-10, None))).slope; rr = -sl
        else: rr = 0.0
        # Fertility
        nb=20; xd=np.digitize(ref[:,0],np.linspace(ref[:,0].min(),ref[:,0].max(),nb))
        yd=np.digitize(ref[:,1],np.linspace(ref[:,1].min(),ref[:,1].max(),nb))
        pairs=list(zip(xd,yd)); uq=len(set(pairs)); n3=len(pairs)
        seen=set(); fs=[0]
        for s in pairs:
            if s not in seen: seen.add(s); fs.append(1)
            else: fs.append(0)
        trans=[(xd[i],yd[i],xd[i+1],yd[i+1]) for i in range(len(xd)-1)]
        _,ct=np.unique(trans,axis=0,return_counts=True) if len(trans)>0 else ([],np.array([1]))
        te2=entropy(ct/ct.sum()) if len(ct)>1 else 0.0
        # Descriptors
        csr=abs(p['beta'])/(p['delta']+1e-10); rbs=abs(p['beta'])*abs(p['gamma'])
        x=traj[:100,0] if len(traj)>100 else traj[:,0]
        adi=float(abs(np.corrcoef(x[:-1],x[1:])[0,1])) if len(x)>10 and np.std(x[:-1])>1e-10 and np.std(x[1:])>1e-10 else 0.0
        x2=traj[:200,0] if len(traj)>200 else traj[:,0]
        if len(x2)>10 and np.std(x2)>1e-10:
            fn=np.abs(np.fft.fft(x2-x2.mean())); fn/=fn.sum()+1e-10; rtp2=entropy(fn)/np.log(len(fn))
        else: rtp2=0.0
        srd=2.0
        yield dict(stability_return_time=float(rtm), stability_recovery_rate=float(rr),
                   stability_final_dev=float(dists[-1]), stability_max_dev=float(np.max(dists)),
                   fertility_state_diversity=float(uq/min(nb**2,n3)),
                   fertility_novelty_rate=float(np.mean(fs[1:])),
                   fertility_state_coverage=float(uq/(nb**2)),
                   fertility_transition_entropy=float(te2),
                   CSR=float(csr), RBS=float(rbs), ADI=float(adi), RTP=float(rtp2), SRD=float(srd))
        sid+=1
        if sid%100==0: print(f'  Oscillator: {sid}/500', flush=True)

# ==============================================================
# LOTKA-VOLTERRA (solve_ivp)
# ==============================================================
def gen_lv_rows(prefix='LV'):
    def rhs_factory(p):
        a,b,d,g=p['alpha'],p['beta'],p['delta'],p['gamma']
        return lambda t,s: [a*s[0]-b*s[0]*s[1], d*s[0]*s[1]-g*s[1]]
    T,mp=200,500; te=np.linspace(0,T,mp)
    sid=0; attempts=0
    while sid < 500 and attempts < 2500:
        attempts+=1
        try:
            p = dict(alpha=rng.uniform(0.5,2), beta=rng.uniform(0.01,0.05),
                     delta=rng.uniform(0.01,0.05), gamma=rng.uniform(0.5,2))
            so = solve_ivp(rhs_factory(p), (0,T), rng.uniform(1,10,2), t_eval=te,
                           method='RK45', rtol=1e-6, atol=1e-8)
            if not so.success or so.y.shape[1] < 10: continue
            traj = so.y.T; pi = min(len(te)//2, so.y.shape[1]-1)
            xp = so.y[:,pi].copy() * rng.uniform(1.5,3.0)
            sp = solve_ivp(rhs_factory(p), (te[pi],T), xp, t_eval=te[pi:],
                           method='RK45', rtol=1e-6, atol=1e-8)
            if not sp.success or sp.y.shape[1] < 5: continue
            sr = solve_ivp(rhs_factory(p), (0,T), rng.uniform(1,10,2), t_eval=te,
                           method='RK45', rtol=1e-6, atol=1e-8)
            if not sr.success: continue
            ref = sr.y.T
        except: continue
        up = traj[pi:]; n2 = min(len(sp.y.T), len(up)); p2=sp.y.T[:n2]; u2=up[:n2]
        dists = np.sqrt(np.sum((p2-u2)**2, axis=1))
        rtm = np.argmax(dists < 0.5) if np.any(dists < 0.5) else len(dists)
        if len(dists) > 3 and dists[0] > 1e-8:
            sl = linregress(np.arange(len(dists)), np.log(np.clip(dists, 1e-10, None))).slope; rr = -sl
        else: rr = 0.0
        nb=20; xd=np.digitize(ref[:,0],np.linspace(ref[:,0].min(),ref[:,0].max(),nb))
        yd=np.digitize(ref[:,1],np.linspace(ref[:,1].min(),ref[:,1].max(),nb))
        pairs=list(zip(xd,yd)); uq=len(set(pairs)); n3=len(pairs)
        seen=set(); fs=[0]
        for s in pairs:
            if s not in seen: seen.add(s); fs.append(1)
            else: fs.append(0)
        trans=[(xd[i],yd[i],xd[i+1],yd[i+1]) for i in range(len(xd)-1)]
        _,ct=np.unique(trans,axis=0,return_counts=True) if len(trans)>0 else ([],np.array([1]))
        te2=entropy(ct/ct.sum()) if len(ct)>1 else 0.0
        a,b2,d2,g2=p['alpha'],p['beta'],p['delta'],p['gamma']
        csr=a/(g2+1e-10); rbs=b2*d2
        x=traj[:,0]
        adi=float(abs(np.corrcoef(x[:-1],x[1:])[0,1])) if len(x)>10 and np.std(x[:-1])>1e-10 and np.std(x[1:])>1e-10 else 0.0
        x2=traj[:,1]
        if len(x2)>10 and np.std(x2)>1e-10:
            fn=np.abs(np.fft.fft(x2-x2.mean())); fn/=fn.sum()+1e-10; rtp2=entropy(fn)/np.log(len(fn))
        else: rtp2=0.0
        srd=2.0
        yield dict(stability_return_time=float(rtm), stability_recovery_rate=float(rr),
                   stability_final_dev=float(dists[-1]), stability_max_dev=float(np.max(dists)),
                   fertility_state_diversity=float(uq/min(nb**2,n3)),
                   fertility_novelty_rate=float(np.mean(fs[1:])),
                   fertility_state_coverage=float(uq/(nb**2)),
                   fertility_transition_entropy=float(te2),
                   CSR=float(csr), RBS=float(rbs), ADI=float(adi), RTP=float(rtp2), SRD=float(srd))
        sid+=1
        if sid%100==0: print(f'  Lotka-Volterra: {sid}/500', flush=True)

# ==============================================================
# REPLICATOR (solve_ivp)
# ==============================================================
def gen_rep_rows(prefix='REP'):
    sid=0; attempts=0
    while sid < 500 and attempts < 2500:
        attempts+=1
        try:
            ns=int(rng.integers(3,6)); A=rng.uniform(-1,2,(ns,ns)); A=(A+A.T)/2
            T,mp=100,500; te=np.linspace(0,T,mp)
            x0=rng.dirichlet(np.ones(ns))
            def rhs(t,s):
                x=np.maximum(s,0); x=x/x.sum(); Ax=A@x; return x*(Ax - x@Ax)
            so=solve_ivp(rhs,(0,T),x0,t_eval=te,method='RK45',rtol=1e-6,atol=1e-8)
            if not so.success or so.y.shape[1] < 10: continue
            traj=so.y.T; traj=np.clip(traj,0,1); pi=min(len(te)//2,so.y.shape[1]-1)
            xp=so.y[:,pi].copy()+rng.normal(0,0.1,ns); xp=np.clip(xp,0.001,None); xp/=xp.sum()
            sp=solve_ivp(rhs,(te[pi],T),xp,t_eval=te[pi:],method='RK45',rtol=1e-6,atol=1e-8)
            if not sp.success or sp.y.shape[1] < 5: continue
            sr=solve_ivp(rhs,(0,T),rng.dirichlet(np.ones(ns)),t_eval=te,method='RK45',rtol=1e-6,atol=1e-8)
            if not sr.success: continue
            ref=sr.y.T; ref=np.clip(ref,0,1)
        except: continue
        up=traj[pi:]; n2=min(len(sp.y.T),len(up)); p2=sp.y.T[:n2]; u2=up[:n2]
        dists=np.sum(np.abs(p2-u2),axis=1)
        rtm=np.argmax(dists<0.05) if np.any(dists<0.05) else len(dists)
        if len(dists) > 3 and dists[0] > 1e-8:
            sl=linregress(np.arange(len(dists)),np.log(np.clip(dists,1e-10,None))).slope; rr=-sl
        else: rr=0.0
        nb=10; keys=[tuple(np.digitize(r,np.linspace(0,1,nb))) for r in ref]
        uq=len(set(keys)); n3=len(keys)
        seen=set(); fs=[0]
        for s in keys:
            if s not in seen: seen.add(s); fs.append(1)
            else: fs.append(0)
        trans=[(keys[i],keys[i+1]) for i in range(len(keys)-1)]
        _,ct=np.unique(trans,axis=0,return_counts=True) if len(trans)>0 else ([],np.array([1]))
        te2=entropy(ct/ct.sum()) if len(ct)>1 else 0.0
        csr=float(ns/3.0)
        tclip=np.clip(traj,1e-10,1-1e-10)
        ent_r=np.array([entropy(r) for r in tclip]); rbs=float(np.mean(ent_r))
        mf=tclip.mean(axis=1)
        adi=float(abs(np.corrcoef(mf[:-1],mf[1:])[0,1])) if len(mf)>10 and np.std(mf[:-1])>1e-10 and np.std(mf[1:])>1e-10 else 0.0
        if len(mf)>10 and np.std(mf)>1e-10:
            fn=np.abs(np.fft.fft(mf-mf.mean())); fn/=fn.sum()+1e-10; rtp2=entropy(fn)/np.log(len(fn))
        else: rtp2=0.0
        srd=float(ns)
        yield dict(stability_return_time=float(rtm), stability_recovery_rate=float(rr),
                   stability_final_dev=float(dists[-1]), stability_max_dev=float(np.max(dists)),
                   fertility_state_diversity=float(uq/min(nb**ns,n3)),
                   fertility_novelty_rate=float(np.mean(fs[1:])),
                   fertility_state_coverage=float(uq/min(nb**min(ns,4),n3)),
                   fertility_transition_entropy=float(te2),
                   CSR=float(csr), RBS=float(rbs), ADI=float(adi), RTP=float(rtp2), SRD=float(srd))
        sid+=1
        if sid%100==0: print(f'  Replicator: {sid}/500', flush=True)

# ==============================================================
# COUPLED MAP LATTICE (moderate — no ODE)
# ==============================================================
def gen_cml_rows(prefix='CML'):
    for sid in range(500):
        L=int(rng.integers(10,40)); r=rng.uniform(2.5,4.0); eps=rng.uniform(0.05,0.5)
        T,ns=100,1000; ri=5
        def lmap(x): return r*x*(1-x)
        x=rng.uniform(0,1,L); traj=[]
        for step in range(ns):
            lx=lmap(x); x=(1-eps)*lx+(eps/2)*(np.roll(lx,1)+np.roll(lx,-1))
            if step%ri==0: traj.append(x.copy())
        traj=np.array(traj)
        if len(traj)<10: continue
        pi=len(traj)//2
        xp=traj[pi].copy(); xp[rng.integers(L)]=rng.uniform(0,1); x=xp; ptraj=[xp.copy()]
        for step in range(1,ns-pi*ri):
            lx=lmap(x); x=(1-eps)*lx+(eps/2)*(np.roll(lx,1)+np.roll(lx,-1))
            if step%ri==0: ptraj.append(x.copy())
        pt=np.array(ptraj)
        xr=rng.uniform(0,1,L); rtraj=[xr.copy()]
        for step in range(1,ns):
            lx=lmap(xr); xr=(1-eps)*lx+(eps/2)*(np.roll(lx,1)+np.roll(lx,-1))
            if step%ri==0: rtraj.append(xr.copy())
        ref=np.array(rtraj)
        # Stability
        up=traj[pi:]; n2=min(len(pt),len(up)); p2=pt[:n2]; u2=up[:n2]
        mp=p2.mean(axis=1); mu=u2.mean(axis=1); dists=np.abs(mp-mu)
        rtm=np.argmax(dists<0.1) if np.any(dists<0.1) else len(dists)
        if len(dists)>3 and dists[0]>1e-8:
            sl=linregress(np.arange(len(dists)),np.log(np.clip(dists,1e-10,None))).slope; rr=-sl
        else: rr=0.0
        # Fertility
        keys=[tuple(np.digitize(rv,np.linspace(rv.min(),rv.max(),10))) for rv in ref]
        uq=len(set(keys)); n3=len(keys)
        seen=set(); fs=[0]
        for s in keys:
            if s not in seen: seen.add(s); fs.append(1)
            else: fs.append(0)
        trans=[(keys[i],keys[i+1]) for i in range(len(keys)-1)]
        _,ct=np.unique(trans,axis=0,return_counts=True) if len(trans)>0 else ([],np.array([1]))
        te2=entropy(ct/ct.sum()) if len(ct)>1 else 0.0
        # Descriptors
        csr=r/(eps+1e-10); rbs=float(r)
        mf=traj.mean(axis=1)
        adi=float(abs(np.corrcoef(mf[:-1],mf[1:])[0,1])) if len(mf)>10 and np.std(mf[:-1])>1e-10 and np.std(mf[1:])>1e-10 else 0.0
        if len(mf)>10 and np.std(mf)>1e-10:
            fn=np.abs(np.fft.fft(mf-mf.mean())); fn/=fn.sum()+1e-10; rtp2=entropy(fn)/np.log(len(fn))
        else: rtp2=0.0
        srd=float(L)
        yield dict(stability_return_time=float(rtm), stability_recovery_rate=float(rr),
                   stability_final_dev=float(dists[-1]), stability_max_dev=float(np.max(dists)),
                   fertility_state_diversity=float(uq/n3), fertility_novelty_rate=float(np.mean(fs[1:])),
                   fertility_state_coverage=float(uq/n3), fertility_transition_entropy=float(te2),
                   CSR=float(csr), RBS=float(rbs), ADI=float(adi), RTP=float(rtp2), SRD=float(srd))

# ==============================================================
# GRAY-SCOTT (reaction-diffusion)
# ==============================================================
def gen_gs_rows(prefix='GS'):
    for sid in range(500):
        Du=rng.uniform(0.01,0.2); Dv=rng.uniform(0.005,0.1); F=rng.uniform(0.01,0.06)
        k=rng.uniform(0.04,0.08); L=int(rng.integers(20,40))
        T,dt,ns2=500,1.0,500; n_rep=200; ri=max(1,ns2//n_rep)
        u=np.ones((L,L)); v=np.zeros((L,L))
        u[L//2-5:L//2+5, L//2-5:L//2+5]=0.5; v[L//2-5:L//2+5, L//2-5:L//2+5]=0.25
        tu=[]
        for step in range(1,ns2+1):
            la=(np.roll(u,1,0)+np.roll(u,-1,0)+np.roll(u,1,1)+np.roll(u,-1,1)-4*u)/4
            lv=(np.roll(v,1,0)+np.roll(v,-1,0)+np.roll(v,1,1)+np.roll(v,-1,1)-4*v)/4
            uvv=u*v*v; u+=dt*(Du*la-uvv+F*(1-u)); v+=dt*(Dv*lv+uvv-(F+k)*v)
            u=np.clip(u,0,1); v=np.clip(v,0,1)
            if step%ri==0: tu.append(u.copy())
        tu=np.array(tu)
        if len(tu)<10: continue
        mu=tu.mean(axis=(1,2))
        fh=np.array([np.histogram(tu[i].ravel(),bins=10,range=(0,1))[0] for i in range(len(tu))])
        pe=np.array([entropy(h/h.sum()) if h.sum()>0 else 0 for h in fh])
        traj=np.column_stack([mu,pe])
        # Perturb
        up=tu[len(tu)//2].copy(); up[L//2,L//2]+=0.3; up=np.clip(up,0,1)
        tu2=[up.copy()]
        for step in range(1,ns2+1):
            la=(np.roll(up,1,0)+np.roll(up,-1,0)+np.roll(up,1,1)+np.roll(up,-1,1)-4*up)/4
            lv=(np.roll(v,1,0)+np.roll(v,-1,0)+np.roll(v,1,1)+np.roll(v,-1,1)-4*v)/4
            uvv=up*v*v; up+=dt*(Du*la-uvv+F*(1-up)); v+=dt*(Dv*lv+uvv-(F+k)*v)
            up=np.clip(up,0,1); v=np.clip(v,0,1)
            if step%ri==0: tu2.append(up.copy())
        tu2=np.array(tu2)
        mu2=tu2.mean(axis=(1,2))
        fh2=np.array([np.histogram(tu2[i].ravel(),bins=10,range=(0,1))[0] for i in range(len(tu2))])
        pe2=np.array([entropy(h/h.sum()) if h.sum()>0 else 0 for h in fh2])
        pt=np.column_stack([mu2,pe2])
        # Ref IC
        u_ref=np.ones((L,L)); v_ref=np.zeros((L,L))
        sz=max(3,L//4); cx,cy=L//2,L//2
        u_ref[cx-sz:cx+sz,cy-sz:cy+sz]=rng.uniform(0,1,(2*sz,2*sz))
        v_ref[cx-sz:cx+sz,cy-sz:cy+sz]=rng.uniform(0,0.5,(2*sz,2*sz))
        tu_r=[u_ref.copy()]
        for step in range(1,ns2+1):
            la=(np.roll(u_ref,1,0)+np.roll(u_ref,-1,0)+np.roll(u_ref,1,1)+np.roll(u_ref,-1,1)-4*u_ref)/4
            lv=(np.roll(v_ref,1,0)+np.roll(v_ref,-1,0)+np.roll(v_ref,1,1)+np.roll(v_ref,-1,1)-4*v_ref)/4
            uvv=u_ref*v_ref*v_ref
            u_ref+=dt*(Du*la-uvv+F*(1-u_ref)); v_ref+=dt*(Dv*lv+uvv-(F+k)*v_ref)
            u_ref=np.clip(u_ref,0,1); v_ref=np.clip(v_ref,0,1)
            if step%ri==0: tu_r.append(u_ref.copy())
        tu_r=np.array(tu_r)
        mu_r=tu_r.mean(axis=(1,2))
        fh_r=np.array([np.histogram(tu_r[i].ravel(),bins=10,range=(0,1))[0] for i in range(len(tu_r))])
        pe_r=np.array([entropy(h/h.sum()) if h.sum()>0 else 0 for h in fh_r])
        ref=np.column_stack([mu_r,pe_r])
        # Stability
        pi=min(len(traj)//2,len(pt)-1); up2=traj[pi:]; n2=min(len(pt),len(up2)); p2=pt[:n2]; u2=up2[:n2]
        dists=np.sqrt(np.sum((p2-u2)**2,axis=1))
        rtm=np.argmax(dists<0.05) if np.any(dists<0.05) else len(dists)
        if len(dists)>3 and dists[0]>1e-8:
            sl=linregress(np.arange(len(dists)),np.log(np.clip(dists,1e-10,None))).slope; rr=-sl
        else: rr=0.0
        # Fertility
        m=ref[:,0]
        md=np.digitize(m,np.linspace(m.min(),m.max(),20)) if np.std(m)>0 else np.zeros(len(m),dtype=int)
        uq=len(set(md)); div=uq/20
        seen=set(); fs=[0]
        for s_ in md:
            if s_ not in seen: seen.add(s_); fs.append(1)
            else: fs.append(0)
        trans=[(md[i],md[i+1]) for i in range(len(md)-1)]
        _,ct=np.unique(trans,axis=0,return_counts=True) if len(trans)>0 else ([],np.array([1]))
        te2=entropy(ct/ct.sum()) if len(ct)>1 else 0.0
        # Descriptors
        csr=F/(k+1e-10); rbs=Du/(Dv+1e-10)
        adi=float(abs(np.corrcoef(traj[:,0][:-1],traj[:,0][1:])[0,1])) if len(traj)>5 and np.std(traj[:,0][:-1])>0 and np.std(traj[:,0][1:])>0 else 0.0
        if len(traj)>10 and np.std(traj[:,1])>1e-10:
            fn=np.abs(np.fft.fft(traj[:,1]-traj[:,1].mean())); fn/=fn.sum()+1e-10; rtp2=entropy(fn)/np.log(len(fn))
        else: rtp2=0.0
        srd=float(L**2)
        yield dict(stability_return_time=float(rtm), stability_recovery_rate=float(rr),
                   stability_final_dev=float(dists[-1]), stability_max_dev=float(np.max(dists)),
                   fertility_state_diversity=float(div), fertility_novelty_rate=float(np.mean(fs[1:])),
                   fertility_state_coverage=float(uq/20), fertility_transition_entropy=float(te2),
                   CSR=float(csr), RBS=float(rbs), ADI=float(adi), RTP=float(rtp2), SRD=float(srd))

# ==============================================================
# KURAMOTO (moderate)
# ==============================================================
def gen_kur_rows(prefix='KUR'):
    for sid in range(500):
        N=int(rng.integers(10,50)); K=rng.uniform(0,3.0); ww=rng.uniform(0.1,2.0)
        omegas=rng.normal(0,ww,N)
        T,dt,ns2=100,0.05,2000; ri=max(1,ns2//200)
        theta=rng.uniform(0,2*np.pi,N); tr=[]
        for step in range(ns2):
            ss=np.sin(theta-theta[:,None]).sum(axis=0)/N
            theta=theta+dt*(omegas+K*ss)
            if step%ri==0: tr.append(abs(np.exp(1j*theta).mean()))
        traj=np.array(tr).reshape(-1,1)
        if len(traj)<10: continue
        pi=len(traj)//2
        theta_p=theta.copy(); theta_p[rng.integers(N)]+=np.pi; theta=theta_p; pr=[]
        for step in range(pi*ri,ns2):
            ss=np.sin(theta-theta[:,None]).sum(axis=0)/N
            theta=theta+dt*(omegas+K*ss); pr.append(abs(np.exp(1j*theta).mean()))
        pt=np.array(pr).reshape(-1,1)
        theta_r=rng.uniform(0,2*np.pi,N); rr2=[]
        for step in range(ns2):
            ss=np.sin(theta_r-theta_r[:,None]).sum(axis=0)/N
            theta_r=theta_r+dt*(omegas+K*ss)
            if step%ri==0: rr2.append(abs(np.exp(1j*theta_r).mean()))
        ref=np.array(rr2).reshape(-1,1)
        # Stability
        up=traj[pi:]; n2=min(len(pt),len(up)); p2=pt[:n2]; u2=up[:n2]
        dists=np.abs(p2.flatten()-u2.flatten())
        rtm=np.argmax(dists<0.02) if np.any(dists<0.02) else len(dists)
        if len(dists)>3 and dists[0]>1e-8:
            sl=linregress(np.arange(len(dists)),np.log(np.clip(dists,1e-10,None))).slope; rr=-sl
        else: rr=0.0
        # Fertility
        rf=ref.flatten()
        bins=np.linspace(rf.min(),rf.max(),20) if np.ptp(rf)>0 else np.arange(20)
        disc=np.digitize(rf,bins); uq=len(set(disc))
        seen=set(); fs=[0]
        for s in disc:
            if s not in seen: seen.add(s); fs.append(1)
            else: fs.append(0)
        trans=[(disc[i],disc[i+1]) for i in range(len(disc)-1)]
        _,ct=np.unique(trans,axis=0,return_counts=True) if len(trans)>0 else ([],np.array([1]))
        te2=entropy(ct/ct.sum()) if len(ct)>1 else 0.0
        # Descriptors
        csr=K/(ww+1e-10); rbs=float(K)
        tj=traj.flatten()
        adi=float(abs(np.corrcoef(tj[:-1],tj[1:])[0,1])) if len(tj)>5 and np.std(tj[:-1])>0 and np.std(tj[1:])>0 else 0.0
        rtp2=0.0; srd=float(N)
        yield dict(stability_return_time=float(rtm), stability_recovery_rate=float(rr),
                   stability_final_dev=float(dists[-1]), stability_max_dev=float(np.max(dists)),
                   fertility_state_diversity=float(uq/20), fertility_novelty_rate=float(np.mean(fs[1:])),
                   fertility_state_coverage=float(uq/20), fertility_transition_entropy=float(te2),
                   CSR=float(csr), RBS=float(rbs), ADI=float(adi), RTP=float(rtp2), SRD=float(srd))

# ===================================================================
# RUN
# ===================================================================
GENERATORS = [
    ('cellular_automata', gen_ca_rows),
    ('population', gen_pop_rows),
    ('graph_diffusion', gen_graph_rows),
    ('branching', gen_branch_rows),
    ('coupled_map_lattice', gen_cml_rows),
    ('kuramoto', gen_kur_rows),
    ('gray_scott', gen_gs_rows),
    ('nonlinear_oscillator', gen_osc_rows),
    ('lotka_volterra', gen_lv_rows),
    ('replicator', gen_rep_rows),
]

def main():
    first = True
    total = sum(500 for _ in GENERATORS)
    done = 0
    for name, gen in GENERATORS:
        print(f'Generating {name}...', flush=True)
        for i, row in enumerate(gen()):
            row['domain'] = name
            write_row(row, first=first)
            if first: first = False
            done += 1
        print(f'  {name} done (total: {done}/{total})', flush=True)
    # Verify
    df = pd.read_csv(CSV)
    print(f'\n=== PHASE C1 COMPLETE ===')
    print(f'{len(df)} systems in phaseC_metrics.csv')
    print(f'Domains: {df["domain"].value_counts().to_dict()}')
    # Leakage audit
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import LeaveOneOut
    from sklearn.preprocessing import StandardScaler
    loo = LeaveOneOut()
    print(f'\nLEAKAGE AUDIT:')
    for t in [c for c in df.columns if c.startswith('stability_') or c.startswith('fertility_')]:
        comb = df['CSR'].values + df['RBS'].values
        r, p = pearsonr(comb, df[t].values)
        print(f'  CSR+RBS vs {t}: r={r:.4f}, p={p:.4g}')
        X = df[['CSR','RBS','ADI','RTP','SRD']].values; y = df[t].values
        if len(y) < 10: continue
        preds = np.empty(len(y))
        try:
            for tr, te in loo.split(X):
                X_tr=StandardScaler().fit_transform(X[tr]); X_te=StandardScaler().fit_transform(X[te])
                preds[te[0]] = LinearRegression().fit(X_tr,y[tr]).predict(X_te)[0]
            r2 = np.corrcoef(y,preds)[0,1]**2
            print(f'  5-desc LOOCV vs {t}: R²={r2:.4f}{" *** HIGH-RISK" if r2>0.9 else ""}')
        except: pass

if __name__ == '__main__':
    main()
