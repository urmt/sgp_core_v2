"""
Hysteresis Expansion Tests

Measure forward/backward perturbation to detect path memory.
"""

import numpy as np
import sys
from typing import Dict
sys.path.insert(0, 'scripts/temporal_memory')

from temporal_dynamics import generate_temporal_system
from memory_metrics import HysteresisLoopArea


def test_hysteresis(system: str, params: Dict, seed: int = 42) -> Dict:
    """Test hysteresis metrics for a system."""
    try:
        traj, _ = generate_temporal_system(system, seed=seed, **params)
        
        hyst = HysteresisLoopArea(seed).compute(traj)
        
        return {
            'hysteresis_area': hyst.get('hysteresis_area', 0)
        }
    except Exception as e:
        return {'error': str(e)}


if __name__ == '__main__':
    np.random.seed(42)
    print("=" * 60)
    print("HYSTERESIS EXPANSION")
    print("=" * 60)
    
    params = {'n': 30, 'dimensions': 5, 'n_timesteps': 20}
    systems = ['stable_hierarchy', 'random_temporal', 'perturb_recover']
    
    results = {}
    for system in systems:
        r = test_hysteresis(system, params)
        results[system] = r
        hyst_val = r.get('hysteresis_area', 0)
        if isinstance(hyst_val, (int, float)):
            print(f"{system}: hysteresis={hyst_val:.3f}")
        else:
            print(f"{system}: hysteresis={hyst_val}")
    
    # Compare
    print("\n=== DISCRIMINATION ===")
    stable_hyst = results['stable_hierarchy'].get('hysteresis_area', 0)
    random_hyst = results['random_temporal'].get('hysteresis_area', 0)
    print(f"Stable vs Random hysteresis: {stable_hyst:.3f} vs {random_hyst:.3f}")
    
    # Save
    import json
    output = '/home/student/sgp_core_v2/outputs/temporal_adversarial_expansion/hysteresis_results.json'
    with open(output, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Saved: {output}")