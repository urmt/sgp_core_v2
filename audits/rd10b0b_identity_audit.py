"""
RD-10B.0B: Identity Audit (Corrected)

QUESTION:
> What observations would justify saying that two descriptions refer
> to the same underlying process?

DESIGN:
Take TWO DIFFERENT worlds.
Represent each in MULTIPLE representations.
Ask: do the identity criteria agree on which pairs are "the same"?

If criteria disagree → "same world" is itself representation-dependent.

STANDING RULE:
> Whenever something looks fundamental, ask what makes it possible.
"""

import numpy as np
import json
from collections import defaultdict
import sys

sys.path.insert(0, '/home/student/sgp_core_v2/audits')
from rd10b0_representation_audit import (
    run_world, representation_graph, representation_timeseries,
    representation_state_transition, representation_correlation,
    representation_phasespace
)

# ============================================================
# IDENTITY CRITERIA (between two trajectories)
# ============================================================

def predictive_identity(traj_a, traj_b):
    """
    Do two trajectories predict the same futures?
    Compare prediction errors when each is used to predict the other.
    """
    T = min(traj_a.shape[0], traj_b.shape[0])
    if T < 40:
        return {'score': 0.0}
    
    train_end = T // 2
    mean_a = traj_a.mean(axis=(1, 2))
    mean_b = traj_b.mean(axis=(1, 2))
    
    # Predict using A's history, compare to B's future
    errors_ab = []
    errors_ba = []
    errors_aa = []
    errors_bb = []
    
    for t in range(train_end, T - 10):
        pred_a = mean_a[max(0, t-20):t].mean()
        pred_b = mean_b[max(0, t-20):t].mean()
        
        future_a = mean_a[t+10]
        future_b = mean_b[t+10]
        
        errors_ab.append((pred_a - future_b)**2)
        errors_ba.append((pred_b - future_a)**2)
        errors_aa.append((pred_a - future_a)**2)
        errors_bb.append((pred_b - future_b)**2)
    
    if len(errors_ab) < 5:
        return {'score': 0.0}
    
    errors_ab = np.mean(errors_ab)
    errors_ba = np.mean(errors_ba)
    errors_aa = np.mean(errors_aa)
    errors_bb = np.mean(errors_bb)
    
    # Cross-prediction error vs self-prediction error
    self_error = (errors_aa + errors_bb) / 2
    cross_error = (errors_ab + errors_ba) / 2
    
    if self_error + cross_error == 0:
        score = 1.0
    else:
        score = 1.0 - cross_error / (self_error + cross_error)
    
    return {'score': float(max(0, score))}

def intervention_identity(traj_a, traj_b):
    """
    Do two trajectories have similar response patterns?
    Compare variance profiles.
    """
    # Variance over time
    var_a = traj_a.var(axis=(1, 2))
    var_b = traj_b.var(axis=(1, 2))
    
    T = min(len(var_a), len(var_b))
    var_a = var_a[:T]
    var_b = var_b[:T]
    
    if T < 10:
        return {'score': 0.0}
    
    # Correlation of variance profiles
    if np.std(var_a) == 0 or np.std(var_b) == 0:
        score = 1.0 if np.std(var_a) == np.std(var_b) else 0.0
    else:
        score = abs(np.corrcoef(var_a, var_b)[0, 1])
    
    return {'score': float(score)}

def counterfactual_identity(traj_a, traj_b):
    """
    Do two trajectories have similar divergence patterns?
    """
    T = min(traj_a.shape[0], traj_b.shape[0])
    if T < 30:
        return {'score': 0.0}
    
    mean_a = traj_a.mean(axis=(1, 2))
    mean_b = traj_b.mean(axis=(1, 2))
    
    # Divergence from local mean
    div_a = []
    div_b = []
    
    for t in range(10, T - 10):
        local_a = mean_a[t-5:t].mean()
        local_b = mean_b[t-5:t].mean()
        
        future_a = mean_a[t+5]
        future_b = mean_b[t+5]
        
        div_a.append((future_a - local_a)**2)
        div_b.append((future_b - local_b)**2)
    
    if len(div_a) < 5:
        return {'score': 0.0}
    
    div_a = np.array(div_a)
    div_b = np.array(div_b)
    
    if np.std(div_a) == 0 or np.std(div_b) == 0:
        score = 1.0 if np.std(div_a) == np.std(div_b) else 0.0
    else:
        score = abs(np.corrcoef(div_a, div_b)[0, 1])
    
    return {'score': float(score)}

def information_identity(traj_a, traj_b):
    """
    Do two trajectories have similar information content?
    Compare entropy of state distributions.
    """
    flat_a = traj_a.flatten()
    flat_b = traj_b.flatten()
    
    n_bins = 20
    hist_a, _ = np.histogram(flat_a, bins=n_bins, density=True)
    hist_b, _ = np.histogram(flat_b, bins=n_bins, density=True)
    
    hist_a = hist_a + 1e-10
    hist_b = hist_b + 1e-10
    
    hist_a = hist_a / hist_a.sum()
    hist_b = hist_b / hist_b.sum()
    
    entropy_a = -np.sum(hist_a * np.log(hist_a))
    entropy_b = -np.sum(hist_b * np.log(hist_b))
    
    max_ent = max(entropy_a, entropy_b)
    if max_ent == 0:
        score = 1.0
    else:
        score = 1.0 - abs(entropy_a - entropy_b) / max_ent
    
    return {'score': float(score)}

def causal_identity(traj_a, traj_b):
    """
    Do two trajectories have similar causal structure?
    Compare autocorrelation patterns.
    """
    T = min(traj_a.shape[0], traj_b.shape[0])
    if T < 30:
        return {'score': 0.0}
    
    mean_a = traj_a.mean(axis=(1, 2))
    mean_b = traj_b.mean(axis=(1, 2))
    
    lags = [1, 2, 5, 10, 20]
    autocorrs_a = []
    autocorrs_b = []
    
    for lag in lags:
        if T > lag + 10:
            corr_a = np.corrcoef(mean_a[:-lag], mean_a[lag:])[0, 1]
            corr_b = np.corrcoef(mean_b[:-lag], mean_b[lag:])[0, 1]
            autocorrs_a.append(corr_a)
            autocorrs_b.append(corr_b)
    
    if len(autocorrs_a) < 3:
        return {'score': 0.0}
    
    autocorrs_a = np.array(autocorrs_a)
    autocorrs_b = np.array(autocorrs_b)
    
    if np.std(autocorrs_a) == 0 or np.std(autocorrs_b) == 0:
        score = 1.0 if np.std(autocorrs_a) == np.std(autocorrs_b) else 0.0
    else:
        score = abs(np.corrcoef(autocorrs_a, autocorrs_b)[0, 1])
    
    return {'score': float(score)}

# ============================================================
# MAIN EXPERIMENT
# ============================================================

def run_identity_audit(n_worlds=6, n_steps=200):
    """
    Run identity audit.
    
    Take multiple worlds.
    For each pair of worlds, apply all identity criteria.
    Ask: do criteria agree on which pairs are "the same"?
    """
    print("RD-10B.0B: Identity Audit")
    print("="*60)
    
    # 1. Generate multiple worlds
    print(f"\n1. Generating {n_worlds} worlds...")
    trajectories = []
    worlds = []
    
    for i in range(n_worlds):
        traj, world = run_world(n_steps=n_steps, seed=i * 100)
        trajectories.append(traj)
        worlds.append(world)
        print(f"   World {i}: N={world['N']}, D={world['D']}, coupling={world['coupling']:.2f}")
    
    # 2. Run identity criteria for all world pairs
    print("\n2. Running identity criteria for all world pairs...")
    
    results = {}
    all_pairs = []
    
    for i in range(n_worlds):
        for j in range(i+1, n_worlds):
            pair = f"world_{i} ↔ world_{j}"
            all_pairs.append(pair)
            
            traj_i = trajectories[i]
            traj_j = trajectories[j]
            
            # Apply all criteria
            scores = {
                'predictive': predictive_identity(traj_i, traj_j)['score'],
                'intervention': intervention_identity(traj_i, traj_j)['score'],
                'counterfactual': counterfactual_identity(traj_i, traj_j)['score'],
                'information': information_identity(traj_i, traj_j)['score'],
                'causal': causal_identity(traj_i, traj_j)['score'],
            }
            
            results[pair] = scores
            
            # Quick summary
            values = list(scores.values())
            mean_score = np.mean(values)
            print(f"   {pair}: mean={mean_score:.3f}, min={min(values):.3f}, max={max(values):.3f}")
    
    # 3. Analysis: do criteria agree?
    print("\n" + "="*60)
    print("CRITERION AGREEMENT ANALYSIS")
    print("="*60)
    
    # Collect scores by criterion
    criterion_scores = defaultdict(list)
    for pair, scores in results.items():
        for criterion, score in scores.items():
            criterion_scores[criterion].append(score)
    
    print("\nMean score per criterion:")
    for criterion, scores in criterion_scores.items():
        print(f"   {criterion}: {np.mean(scores):.3f} (std={np.std(scores):.3f})")
    
    # Criterion correlations
    print("\nCriterion correlations:")
    criteria = list(criterion_scores.keys())
    corr_matrix = []
    
    for i, c1 in enumerate(criteria):
        for j, c2 in enumerate(criteria):
            if i >= j:
                continue
            scores1 = criterion_scores[c1]
            scores2 = criterion_scores[c2]
            min_len = min(len(scores1), len(scores2))
            if min_len >= 3:
                corr = np.corrcoef(scores1[:min_len], scores2[:min_len])[0, 1]
                print(f"   {c1} ↔ {c2}: {corr:.3f}")
                corr_matrix.append(corr)
    
    # 4. Classification agreement
    print("\n" + "="*60)
    print("CLASSIFICATION AGREEMENT")
    print("="*60)
    
    # For each pair, classify as "same" or "different" using each criterion
    threshold = 0.5
    
    for criterion in criteria:
        same_pairs = []
        diff_pairs = []
        
        for pair, scores in results.items():
            if scores[criterion] > threshold:
                same_pairs.append(pair)
            else:
                diff_pairs.append(pair)
        
        print(f"\n{ criterion} (threshold={threshold}):")
        print(f"   Same: {len(same_pairs)} pairs")
        print(f"   Different: {len(diff_pairs)} pairs")
    
    # Do criteria agree on classification?
    print("\nCross-criterion classification agreement:")
    
    for i, c1 in enumerate(criteria):
        for j, c2 in enumerate(criteria):
            if i >= j:
                continue
            
            agree = 0
            total = 0
            
            for pair, scores in results.items():
                class_c1 = scores[c1] > threshold
                class_c2 = scores[c2] > threshold
                
                if class_c1 == class_c2:
                    agree += 1
                total += 1
            
            if total > 0:
                agreement = agree / total
                print(f"   {c1} ↔ {c2}: {agreement:.3f}")
    
    # 5. Interpretation
    print("\n" + "="*60)
    print("INTERPRETATION")
    print("="*60)
    
    if corr_matrix:
        mean_corr = np.mean(corr_matrix)
        print(f"\nMean criterion correlation: {mean_corr:.3f}")
        
        if mean_corr > 0.8:
            print("Criteria strongly agree on what 'same world' means.")
            print("'Same world' has a unified meaning.")
        elif mean_corr > 0.5:
            print("Criteria moderately agree.")
            print("'Same world' has a partial meaning.")
        else:
            print("Criteria weakly agree or disagree.")
            print("'Same world' itself becomes representation-dependent.")
            print("This is a deeper finding than any specific motif result.")
    
    return results

# ============================================================
# RUN
# ============================================================

if __name__ == '__main__':
    n_worlds = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    
    results = run_identity_audit(n_worlds=n_worlds)
    
    with open('/home/student/sgp_core_v2/audits/rd10b0b_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nSaved to audits/rd10b0b_results.json")
