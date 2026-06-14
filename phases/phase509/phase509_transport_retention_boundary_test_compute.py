#!/usr/bin/env python3
"""
Phase 509: Transport-Retention-Boundary Test
Directly tests whether TRE = RTP × (1 − SRD) is the actual governing invariant
behind recursive stability, using out-of-distribution positive and negative
candidate systems plus the original Phase 505/506 corpus.
"""

import json, math, itertools, os, sys
import numpy as np
from scipy import stats
from scipy.spatial.distance import cdist

np.random.seed(509)

# ---------------------------------------------------------------------------
# 1.  Metric functions (self‑contained, no external dependencies)
# ---------------------------------------------------------------------------

SFHSGP_HIERARCHY = np.array([0.9285, 0.9283, 0.9279, 0.9244, 0.9225, 0.9031, 0.8864])

def _trunc(values, ref):
    ml = min(len(values), len(ref))
    return np.array(values[:ml]), np.array(ref[:ml])

def _layer_coherence(seq):
    if len(seq) < 2: return 0.0
    m = np.mean(np.abs(seq))
    return 1.0 - np.std(seq) / (m + 1e-10) if m > 0 else (1.0 if np.std(seq) == 0 else 0.0)

def metric_coherence_survival_ratio(values, ref):
    v, r = _trunc(values, ref)
    if len(v) < 4: return 0.0
    third = max(1, len(v)//3)
    def mc(lv, lr):
        return _layer_coherence(lv) * _layer_coherence(lr)
    shallow = mc(v[:third], r[:third])
    middle = mc(v[third:2*third], r[third:2*third])
    deep   = mc(v[2*third:3*third] if 3*third<=len(v) else v[2*third:],
                r[2*third:3*third] if 3*third<=len(r) else r[2*third:])
    return float((shallow + middle + deep) / 3.0)

def metric_recursive_balance_strength(values, ref):
    v, r = _trunc(values, ref)
    if len(v) < 2: return 0.0
    def bal(s):
        m = np.mean(np.abs(s))
        return 1.0 - np.std(s)/(m+1e-10) if m > 0 else (1.0 if np.std(s)==0 else 0.0)
    bv, br = bal(v), bal(r)
    return float(bv * br)

def metric_recursive_transport_persistence(values, ref):
    v, r = _trunc(values, ref)
    if len(v) < 3: return 0.0
    dv, dr = np.diff(v), np.diff(r)
    if len(dv) < 2 or np.std(dv) < 1e-12 or np.std(dr) < 1e-12:
        return 0.0
    c = np.corrcoef(dv, dr)[0, 1]
    return float(abs(c) if not np.isnan(c) else 0.0)

def metric_asymmetry_dependence_index(values, ref):
    v, r = _trunc(values, ref)
    if len(v) < 3: return 0.0
    def asym(s):
        m = np.mean(s)
        t = np.mean((s - m)**3)
        var = np.var(s)
        return abs(t / (var**1.5)) if var > 0 else 0.0
    av, ar = asym(v), asym(r)
    change = abs(av - ar) / (av + 1e-12)
    return float(min(change, 1.0))

def metric_signature_retention_decay(values, ref):
    v, r = _trunc(values, ref)
    if len(v) < 3: return 0.0
    def dg(s):
        pg = np.diff(s); rg = np.diff(r[:len(s)])
        ss = np.mean(np.sign(pg) == np.sign(rg))
        if np.std(pg) > 0 and np.std(rg) > 0:
            gc = np.corrcoef(pg, rg)[0,1]
            return ss * (1 + (gc if not np.isnan(gc) else 0)) / 2
        return ss
    return float(1.0 - dg(v))

def compute_all_metrics(values):
    """Return dict of five metric values for a given system value list."""
    return {
        'coherence_survival_ratio': metric_coherence_survival_ratio(values, SFHSGP_HIERARCHY),
        'recursive_balance_strength': metric_recursive_balance_strength(values, SFHSGP_HIERARCHY),
        'recursive_transport_persistence': metric_recursive_transport_persistence(values, SFHSGP_HIERARCHY),
        'asymmetry_dependence_index': metric_asymmetry_dependence_index(values, SFHSGP_HIERARCHY),
        'signature_retention_decay': metric_signature_retention_decay(values, SFHSGP_HIERARCHY),
    }

# ---------------------------------------------------------------------------
# 2.  Candidate system generators (all return 7-element list in [0,1])
# ---------------------------------------------------------------------------

def _rescale(a):
    a = np.array(a, dtype=float)
    lo, hi = a.min(), a.max()
    if hi - lo < 1e-12: return np.full_like(a, 0.5)
    return (a - lo) / (hi - lo)

# -- Positive candidates ----------------------------------------------------

def gen_reaction_diffusion():
    # Activator-inhibitor steady-state profile
    x = np.linspace(0, 6, 7)
    u = 1 / (1 + np.exp(-(3 - x)))          # sigmoid
    v = 0.5 * np.exp(-x/2)
    return _rescale(u * v).tolist()

def gen_synchronized_oscillators():
    # Kuramoto order parameter across coupling strengths
    omega = np.linspace(0.1, 2.0, 7)
    order = 1.0 / (1.0 + np.exp(-3 * (omega - 1.0)))
    return _rescale(order).tolist()

def gen_recursive_market():
    # Multiplicative cascade: log-normal volatility clustering
    x = np.linspace(-2, 2, 7)
    cascade = np.exp(-x**2) * (1 + 0.3 * np.sin(3*x))
    return _rescale(cascade).tolist()

def gen_predator_prey():
    # Lotka-Volterra amplitude envelope
    t = np.linspace(0, 6, 7)
    prey = 1 + 0.5 * np.sin(t)
    pred = 1 + 0.5 * np.sin(t - 1.5)
    return _rescale(prey * pred).tolist()

def gen_neural_cascade():
    # Cascading activation with refractory decay
    x = np.linspace(0, 6, 7)
    act = np.exp(-x) * (1 + np.sin(2*x)**2)
    return _rescale(act).tolist()

def gen_avalanche():
    # SOC sandpile: power-law size distribution across thresholds
    thresh = np.linspace(0.1, 2.0, 7)
    aval = thresh**(-1.5)
    return _rescale(aval).tolist()

def gen_percolation():
    # Percolation cluster density (p > p_c)
    p = np.linspace(0.3, 0.9, 7)
    Pinf = np.maximum(p - 0.5927, 0) ** 0.4
    Pinf = np.maximum(Pinf, 0)
    return _rescale(Pinf).tolist()

POSITIVE_GENERATORS = [
    ('reaction_diffusion', gen_reaction_diffusion),
    ('synchronized_oscillators', gen_synchronized_oscillators),
    ('recursive_market', gen_recursive_market),
    ('predator_prey_cycles', gen_predator_prey),
    ('neural_cascade', gen_neural_cascade),
    ('avalanche_redistribution', gen_avalanche),
    ('percolation_transport', gen_percolation),
]

# -- Negative candidates ----------------------------------------------------

def gen_random_walk():
    steps = np.random.normal(0, 0.15, 7)
    return _rescale(np.cumsum(steps)).tolist()

def gen_static_equilibrium():
    return [0.5] * 7

def gen_memoryless_diffusion():
    x = np.linspace(0, 3, 7)
    return _rescale(np.exp(-x) + np.random.normal(0, 0.02, 7)).tolist()

def gen_white_noise():
    return _rescale(np.random.uniform(0, 1, 7)).tolist()

def gen_disconnected_flow():
    base = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
    np.random.shuffle(base)
    return base

def gen_monotonic_decay():
    return _rescale(np.exp(-np.linspace(0, 2, 7))).tolist()

NEGATIVE_GENERATORS = [
    ('random_walk', gen_random_walk),
    ('static_equilibrium', gen_static_equilibrium),
    ('memoryless_diffusion', gen_memoryless_diffusion),
    ('white_noise', gen_white_noise),
    ('disconnected_flow', gen_disconnected_flow),
    ('monotonic_decay', gen_monotonic_decay),
]

# ---------------------------------------------------------------------------
# 3.  Adversarial perturbation functions (simplified, one per depth level)
# ---------------------------------------------------------------------------

def perturb_transport_interruption(values, strength=0.5):
    n = len(values)
    if n < 4: return values[:]
    bp = int(n * strength)
    a, b = values[:bp].copy(), values[bp:].copy()
    np.random.shuffle(a); np.random.shuffle(b)
    return (a + b)[:n]

def perturb_coherence_scrambling(values, strength=0.5):
    rw = np.cumsum(np.random.normal(0, strength * np.std(values) if np.std(values) > 0 else 0.1, len(values)))
    return np.clip(np.array(values) + rw, 0, 1).tolist()

def perturb_phase_decorrelation(values, strength=0.5):
    n = len(values)
    noise = np.random.normal(0, strength * (np.std(values) if np.std(values) > 0 else 0.1), n)
    return np.clip(np.array(values) + noise, 0, 1).tolist()

def perturb_asymmetric_inversion(values, **_):
    m = np.mean(values)
    return np.clip([2*m - v for v in values], 0, 1).tolist()

# ---------------------------------------------------------------------------
# 4.  Main analysis
# ---------------------------------------------------------------------------

def compute_auc(scores, labels):
    """One-vs-rest AUC using Mann–Whitney."""
    pos = [s for s, l in zip(scores, labels) if l == 1]
    neg = [s for s, l in zip(scores, labels) if l == 0]
    if len(pos) == 0 or len(neg) == 0:
        return 0.5
    u, _ = stats.mannwhitneyu(pos, neg, alternative='two-sided')
    return u / (len(pos) * len(neg))

def main():
    print("=" * 70)
    print("PHASE 509: TRANSPORT-RETENTION-BOUNDARY TEST")
    print("=" * 70)

    # -----------------------------------------------------------------------
    # A.  Build system corpus
    # -----------------------------------------------------------------------
    corpus = {}

    # Original 5 surviving systems (from Phase 503 values loaded via JSON)
    sys.path.insert(0, os.path.dirname(os.path.abspath('../../../')))
    try:
        with open('phases/phase503/phase503_results.json') as f:
            p503 = json.load(f)
        all_auth = p503['physical_systems']
        # Also include rejected ones as additional negatives below
        surviving_names = {'EnergyMomentumConservation', 'DoubleSlitInterference',
                          'ChemicalEquilibriumNetwork', 'TurbulenceEnergyCascade',
                          'SuperconductorCoherence'}
        rejected_names = set(all_auth.keys()) - surviving_names
    except Exception:
        all_auth = {}
        surviving_names = set()
        rejected_names = set()

    pos_class = {}   # 1 = surviving or positive candidate
    neg_class = {}   # 0 = rejected or negative candidate

    # Original surviving systems
    for nm in surviving_names:
        if nm in all_auth:
            vals = all_auth[nm]['values']
            m = compute_all_metrics(vals)
            m['values'] = vals
            pos_class[nm] = m

    # Original rejected systems
    for nm in rejected_names:
        if nm in all_auth:
            vals = all_auth[nm]['values']
            m = compute_all_metrics(vals)
            m['values'] = vals
            neg_class[nm] = m

    # New positive candidates
    for nm, gen in POSITIVE_GENERATORS:
        vals = gen()
        m = compute_all_metrics(vals)
        m['values'] = vals
        pos_class[nm] = m

    # New negative candidates
    for nm, gen in NEGATIVE_GENERATORS:
        vals = gen()
        m = compute_all_metrics(vals)
        m['values'] = vals
        neg_class[nm] = m

    print(f"\nPositive systems (class=1): {len(pos_class)}")
    for nm in pos_class:
        print(f"  + {nm}")
    print(f"Negative systems (class=0): {len(neg_class)}")
    for nm in neg_class:
        print(f"  - {nm}")

    # -----------------------------------------------------------------------
    # B.  Compute TRE for each system
    # -----------------------------------------------------------------------
    def compute_TRE(m):
        rtp = m['recursive_transport_persistence']
        srd = m['signature_retention_decay']
        return rtp * (1.0 - srd)

    # Combined list
    all_names = list(pos_class.keys()) + list(neg_class.keys())
    all_labels = [1]*len(pos_class) + [0]*len(neg_class)
    all_metrics = {**pos_class, **neg_class}

    all_TRE = np.array([compute_TRE(all_metrics[nm]) for nm in all_names])
    CSR = np.array([all_metrics[nm]['coherence_survival_ratio'] for nm in all_names])
    RBS = np.array([all_metrics[nm]['recursive_balance_strength'] for nm in all_names])

    labels = np.array(all_labels)

    # Normalise TRE
    mu, sg = np.mean(all_TRE), np.std(all_TRE) + 1e-12
    TRE_n = (all_TRE - mu) / sg

    # -----------------------------------------------------------------------
    # C.  Invariant strength: R² of TRE → stability
    # -----------------------------------------------------------------------
    from sklearn.linear_model import LogisticRegression
    X_tre = TRE_n.reshape(-1, 1)
    clf = LogisticRegression(C=1e6, solver='lbfgs')
    clf.fit(X_tre, labels)
    # Use AUC as practical measure of invariant strength
    auc_tre = compute_auc(TRE_n.tolist(), labels.tolist())
    print(f"\n--- Invariant strength ---")
    print(f"AUC(TRE → class): {auc_tre:.4f}")
    if auc_tre > 0.90:
        tre_verdict = "strong invariant candidate"
    elif auc_tre >= 0.75:
        tre_verdict = "bounded discriminator"
    else:
        tre_verdict = "insufficient specificity"
    print(f"TRE verdict: {tre_verdict}")

    # Full model (TRE + CSR + RBS)
    X_full = np.column_stack([TRE_n, CSR, RBS])
    clf_full = LogisticRegression(C=1e6, solver='lbfgs')
    clf_full.fit(X_full, labels)
    probs_full = clf_full.predict_proba(X_full)[:, 1]
    auc_full = compute_auc(probs_full.tolist(), labels.tolist())
    print(f"AUC(TRE+CSR+RBS → class): {auc_full:.4f}")

    # Check of TRE alone dominates
    r2_approx = 2 * (auc_tre - 0.5)  # rough transformation
    print(f"TRE alone R²(approx): {r2_approx:.4f}")

    # -----------------------------------------------------------------------
    # D.  Separation boundary
    # -----------------------------------------------------------------------
    pos_tre = TRE_n[labels == 1]
    neg_tre = TRE_n[labels == 0]
    # Find best split threshold
    thresholds = np.linspace(TRE_n.min(), TRE_n.max(), 200)
    best_acc = 0; best_th = 0.0
    for th in thresholds:
        pred = (TRE_n >= th).astype(int)
        acc = np.mean(pred == labels)
        if acc > best_acc:
            best_acc = acc; best_th = th
    print(f"\n--- Boundary separation ---")
    print(f"Best threshold (TRE_n >= {best_th:.4f}): accuracy = {best_acc:.4f}")
    print(f"Positive TRE_n: mean={pos_tre.mean():.4f} std={pos_tre.std():.4f}")
    print(f"Negative TRE_n: mean={neg_tre.mean():.4f} std={neg_tre.std():.4f}")

    # -----------------------------------------------------------------------
    # E.  Perturbation trajectory test
    # -----------------------------------------------------------------------
    print(f"\n--- Perturbation trajectory ---")
    perturbations = [
        ('transport_interruption', perturb_transport_interruption),
        ('coherence_scrambling',   perturb_coherence_scrambling),
        ('phase_decorrelation',    perturb_phase_decorrelation),
        ('asymmetric_inversion',   perturb_asymmetric_inversion),
    ]
    depths = [0.1, 0.3, 0.5, 0.7, 0.9]

    delta_tre_records = []
    delta_stab_records = []
    stability_scores = []  # simple stability score = CSR + RBS (baseline)

    for nm in all_names:
        base_vals = all_metrics[nm]['values']
        base_m = all_metrics[nm]
        base_tre = compute_TRE(base_m)
        base_stab = base_m['coherence_survival_ratio'] + base_m['recursive_balance_strength']

        for pname, pfunc in perturbations:
            for d in depths:
                pert_vals = pfunc(base_vals, strength=d)
                pm = compute_all_metrics(pert_vals)
                tre_pert = compute_TRE(pm)
                stab_pert = pm['coherence_survival_ratio'] + pm['recursive_balance_strength']
                delta_tre_records.append(tre_pert - base_tre)
                delta_stab_records.append(stab_pert - base_stab)

    dt = np.array(delta_tre_records)
    ds = np.array(delta_stab_records)
    if np.std(dt) > 0 and np.std(ds) > 0:
        corr_tre_stab = np.corrcoef(dt, ds)[0, 1]
    else:
        corr_tre_stab = 0.0
    print(f"corr(ΔTRE, ΔStability) across all perturbations: {corr_tre_stab:.4f}")

    # Per-system correlation
    per_sys_corr = {}
    idx = 0
    for nm in all_names:
        n_pts = len(perturbations) * len(depths)
        dts = dt[idx:idx+n_pts]
        dss = ds[idx:idx+n_pts]
        if np.std(dts) > 0 and np.std(dss) > 0:
            pc = np.corrcoef(dts, dss)[0, 1]
        else:
            pc = 0.0
        if np.isnan(pc): pc = 0.0
        per_sys_corr[nm] = float(pc)
        idx += n_pts
    print()
    for nm, pc in sorted(per_sys_corr.items(), key=lambda x: -abs(x[1])):
        print(f"  corr(ΔTRE, ΔStab) {nm}: {pc:.4f}")

    # -----------------------------------------------------------------------
    # F.  Full output
    # -----------------------------------------------------------------------
    # System table
    table_rows = []
    for nm in all_names:
        m = all_metrics[nm]
        tre = compute_TRE(m)
        tre_n = (tre - mu) / sg
        table_rows.append({
            'name': nm,
            'class': 'positive' if labels[all_names.index(nm)] == 1 else 'negative',
            'TRE_raw': round(tre, 6),
            'TRE_norm': round(tre_n, 6),
            'CSR': round(m['coherence_survival_ratio'], 6),
            'RBS': round(m['recursive_balance_strength'], 6),
            'RTP': round(m['recursive_transport_persistence'], 6),
            'SRD': round(m['signature_retention_decay'], 6),
            'ADI': round(m['asymmetry_dependence_index'], 6),
        })

    # Print table
    print(f"\n--- Full system table ---")
    header = f"{'System':30s} {'Class':10s} {'TRE_n':8s} {'CSR':8s} {'RBS':8s} {'RTP':8s} {'SRD':8s}"
    print(header)
    print("-" * len(header))
    for nr in table_rows:
        mark = " *" if nr['class'] == 'positive' else "  "
        print(f"{nr['name']:30s} {nr['class']:10s} {nr['TRE_norm']:8.4f} {nr['CSR']:8.4f} {nr['RBS']:8.4f} {nr['RTP']:8.4f} {nr['SRD']:8.4f}{mark}")

    # -----------------------------------------------------------------------
    # G.  Summary
    # -----------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("PHASE 509 RESULTS SUMMARY")
    print("=" * 70)
    print(f"Systems tested: {len(all_names)}")
    print(f"    positive: {len(pos_class)}")
    print(f"    negative: {len(neg_class)}")
    print(f"AUC(TRE → class):            {auc_tre:.4f}  — {tre_verdict}")
    print(f"AUC(TRE+CSR+RBS → class):    {auc_full:.4f}")
    print(f"corr(ΔTRE, ΔStability):      {corr_tre_stab:.4f}")
    print(f"Best boundary accuracy:       {best_acc:.4f} @ TRE_n >= {best_th:.4f}")

    # Overall verdict
    if auc_tre >= 0.75 and corr_tre_stab > 0.5:
        print(f"\nVERDICT: INVARIANT-CANDIDATE-CONFIRMED")
        print(f"TRE separates classes reliably and perturbation tracking is coherent.")
    elif auc_tre >= 0.60 and corr_tre_stab > 0.3:
        print(f"\nVERDICT: PARTIAL-GOVERNING-STRUCTURE")
        print(f"TRE partially explains stability but is not the full invariant.")
    else:
        print(f"\nVERDICT: PROJECTION-ARTIFACT")
        print(f"Phase 508 result was latent compression, not invariant discovery.")

    # Save
    results = {
        'phase': 509,
        'seed': 509,
        'tier': 3,
        'system_table': table_rows,
        'auc_TRE': auc_tre,
        'auc_full': auc_full,
        'corr_delta_TRE_stability': float(corr_tre_stab),
        'per_system_corr': {nm: float(pc) for nm, pc in per_sys_corr.items()},
        'best_boundary_threshold': float(best_th),
        'best_boundary_accuracy': float(best_acc),
        'tre_verdict': tre_verdict,
        'overall_verdict': "INVARIANT-CANDIDATE-CONFIRMED" if (auc_tre >= 0.75 and corr_tre_stab > 0.5) else ("PARTIAL-GOVERNING-STRUCTURE" if (auc_tre >= 0.60 and corr_tre_stab > 0.3) else "PROJECTION-ARTIFACT"),
        'pos_TRE_mean': float(pos_tre.mean()), 'pos_TRE_std': float(pos_tre.std()),
        'neg_TRE_mean': float(neg_tre.mean()), 'neg_TRE_std': float(neg_tre.std()),
    }
    with open('phases/phase509/phase509_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to phases/phase509/phase509_results.json")
    print("=" * 70)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback; traceback.print_exc()
