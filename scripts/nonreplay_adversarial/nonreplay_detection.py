"""
SGP-CORE V2 Non-Replay Adversarial Detection

Detect adversarial systems that are NOT simple replay attacks.
Focus: temporal camouflage, delayed coherence, phase-shift spoofing
"""

import numpy as np
from typing import Dict


def temporal_transition_variance(sequence):
    """Measures variability of transitions."""
    transitions = []
    
    for i in range(len(sequence) - 1):
        delta = sequence[i + 1] - sequence[i]
        transitions.append(np.std(delta))
    
    return np.std(transitions) if transitions else 0


def phase_shift_instability(sequence):
    """Detects rotating or cyclic spoof patterns."""
    instabilities = []
    
    for i in range(len(sequence) - 2):
        a = sequence[i].flatten()
        b = sequence[i + 1].flatten()
        c = sequence[i + 2].flatten()
        
        ab = np.corrcoef(a, b)[0, 1]
        bc = np.corrcoef(b, c)[0, 1]
        
        if not np.isnan(ab) and not np.isnan(bc):
            instabilities.append(abs(ab - bc))
    
    return np.mean(instabilities) if instabilities else 0


def coherence_collapse(sequence):
    """Real systems maintain structured coherence; fake systems collapse."""
    corrs = []
    
    for i in range(len(sequence) - 1):
        a = sequence[i].flatten()
        b = sequence[i + 1].flatten()
        
        c = np.corrcoef(a, b)[0, 1]
        if not np.isnan(c):
            corrs.append(c)
    
    if len(corrs) < 2:
        return 0
    
    corrs = np.array(corrs)
    return np.max(corrs) - np.min(corrs)


def state_entropy(sequence):
    """Measures entropy of state transitions."""
    states = []
    
    for i in range(len(sequence)):
        # Use mean of state as simple representation
        states.append(np.mean(sequence[i]))
    
    if len(states) < 2:
        return 0
    
    hist, _ = np.histogram(states, bins=10, density=True)
    hist = hist + 1e-12
    
    return -np.sum(hist * np.log(hist))


def structural_stability(sequence):
    """Measures how stable the structure is across time."""
    # For each timestep, compute within-state variance
    within_vars = []
    
    for t in range(len(sequence)):
        within_vars.append(np.var(sequence[t]))
    
    # Real systems should have moderate, varying within-var
    # Fake systems often have unnatural patterns
    
    mean_var = np.mean(within_vars)
    std_var = np.std(within_vars)
    
    # Coefficient of variation
    cv = std_var / (mean_var + 1e-10)
    
    return cv


def anti_camouflage_score(sequence, seed: int = 42) -> Dict:
    """Compute anti-camouflage score."""
    transition_var = temporal_transition_variance(sequence)
    phase_instability = phase_shift_instability(sequence)
    collapse = coherence_collapse(sequence)
    ent = state_entropy(sequence)
    struct_stab = structural_stability(sequence)
    
    # Score: higher = more likely legitimate
    # Real systems have moderate transition variance
    # Fake systems have unnatural patterns
    
    score = (
        transition_var * 0.3 +
        phase_instability * 0.25 +
        collapse * 0.2 +
        min(ent / 2, 1) * 0.15 +
        min(struct_stab, 1) * 0.1
    )
    
    return {
        "transition_variance": float(transition_var),
        "phase_instability": float(phase_instability),
        "coherence_collapse": float(collapse),
        "state_entropy": float(ent),
        "structural_stability": float(struct_stab),
        "anti_camouflage_score": float(score),
        "is_adversarial": bool(score < 0.15)
    }


if __name__ == "__main__":
    SEED = 42
    rng = np.random.RandomState(SEED)
    
    # Test example systems
    def generate_legit_system():
        seq = []
        base = rng.randn(20, 20)
        for i in range(20):
            noise = rng.randn(20, 20) * 0.1
            seq.append(base + noise + i * 0.01)
        return seq
    
    def generate_temporal_camouflage():
        seq = []
        base = rng.randn(20, 20)
        for i in range(20):
            if i % 2 == 0:
                seq.append(base + rng.randn(20, 20) * 0.01)
            else:
                seq.append(rng.randn(20, 20))
        return seq
    
    legit = generate_legit_system()
    spoof = generate_temporal_camouflage()
    
    legit_result = anti_camouflage_score(legit)
    spoof_result = anti_camouflage_score(spoof)
    
    print("\nLEGIT SYSTEM")
    for k, v in legit_result.items():
        print(f"{k}: {v:.4f}")
    
    print("\nCAMOUFLAGE SPOOF")
    for k, v in spoof_result.items():
        print(f"{k}: {v:.4f}")
    
    print(f"\nDetection: {'PASS' if spoof_result['is_adversarial'] else 'FAIL'}")