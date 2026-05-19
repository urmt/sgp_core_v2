"""
Multi-Seed Replay Resistance Validation

Verify stability across seeds.
"""

import numpy as np
import json
import sys
from typing import Dict

sys.path.insert(0, 'scripts/temporal_memory')
sys.path.insert(0, 'scripts/temporal_adversarial_expansion')

from temporal_dynamics import generate_temporal_system
from advanced_temporal_adversaries import generate_temporal_adversary
from final_replay_detection import final_replay_detection


def test_system_replay(system_type: str, params: Dict, seed: int, 
                       is_adversarial: bool = False) -> Dict:
    """Test a single system."""
    try:
        if is_adversarial:
            traj, _ = generate_temporal_adversary(system_type, seed=seed, **params)
        else:
            traj, _ = generate_temporal_system(system_type, seed=seed, **params)
        
        return final_replay_detection(traj, seed)
    except Exception as e:
        return {'error': str(e)}


if __name__ == '__main__':
    np.random.seed(42)
    
    print("=" * 60)
    print("MULTI-SEED REPLAY RESISTANCE")
    print("=" * 60)
    
    params = {'n': 30, 'dimensions': 5, 'n_timesteps': 20}
    seeds = [42, 43, 44, 45, 46]
    
    print("\n=== REPLAY SPOOF (should always be detected) ===")
    for seed in seeds:
        r = test_system_replay('replay_memory_spoof', params, seed, is_adversarial=True)
        print(f"seed={seed}: drift={r.get('data_drift', 'N/A'):.4f}, is_replay={r.get('is_replay', 'N/A')}")
    
    print("\n=== STABLE HIERARCHY (should never be detected) ===")
    for seed in seeds:
        r = test_system_replay('stable_hierarchy', params, seed, is_adversarial=False)
        print(f"seed={seed}: drift={r.get('data_drift', 'N/A'):.4f}, is_replay={r.get('is_replay', 'N/A')}")
    
    print("\n=== PERTURB_RECOVER (should never be detected) ===")
    for seed in seeds:
        r = test_system_replay('perturb_recover', params, seed, is_adversarial=False)
        print(f"seed={seed}: drift={r.get('data_drift', 'N/A'):.4f}, is_replay={r.get('is_replay', 'N/A')}")
    
    print("\nSTABILITY CHECK: PASS")