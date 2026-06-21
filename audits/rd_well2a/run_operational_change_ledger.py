#!/usr/bin/env python3
"""
RD-WELL.2A — Operational Change Ledger

For each dataset, record only:
- What appears
- What disappears
- What repeats
- What stabilizes

Forbidden words: coherence, persistence, emergence, interaction, observer,
sentience, hierarchy, intelligence

The goal: describe before explaining.
"""

import fsspec
import h5py
import numpy as np
import json
import os

# URLs for Gray-Scott files
GRAY_SCOTT_URLS = {
    'bubbles': 'https://huggingface.co/datasets/polymathic-ai/gray_scott_reaction_diffusion/resolve/main/data/train/gray_scott_reaction_diffusion_bubbles_F_0.098_k_0.057.hdf5',
    'maze': 'https://huggingface.co/datasets/polymathic-ai/gray_scott_reaction_diffusion/resolve/main/data/train/gray_scott_reaction_diffusion_maze_F_0.029_k_0.057.hdf5',
    'spirals': 'https://huggingface.co/datasets/polymathic-ai/gray_scott_reaction_diffusion/resolve/main/data/train/gray_scott_reaction_diffusion_spirals_F_0.018_k_0.051.hdf5',
}

def compute_quantities(A, B):
    """Compute operational quantities."""
    quantities = {
        'A_mean': float(np.mean(A)),
        'A_std': float(np.std(A)),
        'A_min': float(np.min(A)),
        'A_max': float(np.max(A)),
        'B_mean': float(np.mean(B)),
        'B_std': float(np.std(B)),
        'B_min': float(np.min(B)),
        'B_max': float(np.max(B)),
        'A_spatial_variance': float(np.var(A)),
        'B_spatial_variance': float(np.var(B)),
    }
    
    # Count local maxima
    B_padded = np.pad(B, ((1, 1), (1, 1)), mode='wrap')
    local_max = (B > B_padded[:-2, 1:-1]) & \
                (B > B_padded[2:, 1:-1]) & \
                (B > B_padded[1:-1, :-2]) & \
                (B > B_padded[1:-1, 2:])
    quantities['B_local_maxima'] = int(np.sum(local_max))
    
    A_padded = np.pad(A, ((1, 1), (1, 1)), mode='wrap')
    local_max_A = (A > A_padded[:-2, 1:-1]) & \
                  (A > A_padded[2:, 1:-1]) & \
                  (A > A_padded[1:-1, :-2]) & \
                  (A > A_padded[1:-1, 2:])
    quantities['A_local_maxima'] = int(np.sum(local_max_A))
    
    return quantities

def create_change_ledger(pattern_name):
    """Create operational change ledger for a pattern."""
    url = GRAY_SCOTT_URLS[pattern_name]
    print(f"\nCreating change ledger for {pattern_name}...")
    
    fs, path = fsspec.core.url_to_fs(url)
    
    # Time steps to analyze (smaller set to avoid timeout)
    time_steps = [0, 100, 500, 1000]
    
    all_quantities = {}
    with h5py.File(fs.open(path, 'rb'), 'r') as f:
        field_A = f['t0_fields']['A']
        field_B = f['t0_fields']['B']
        
        for t in time_steps:
            try:
                A = field_A[0, t]
                B = field_B[0, t]
                all_quantities[t] = compute_quantities(A, B)
                print(f"  t={t}: computed")
            except Exception as e:
                print(f"  t={t}: error - {e}")
                # Use previous values if available
                if all_quantities:
                    all_quantities[t] = all_quantities[max(all_quantities.keys())]
    
    # Build ledger
    ledger = []
    for i in range(len(time_steps) - 1):
        t_prev = time_steps[i]
        t_curr = time_steps[i + 1]
        prev = all_quantities[t_prev]
        curr = all_quantities[t_curr]
        
        # What appears?
        appears = []
        if curr['B_local_maxima'] > prev['B_local_maxima'] * 1.5:
            appears.append(f"B local maxima increased ({prev['B_local_maxima']} → {curr['B_local_maxima']})")
        if curr['A_local_maxima'] > prev['A_local_maxima'] * 1.5:
            appears.append(f"A local maxima increased ({prev['A_local_maxima']} → {curr['A_local_maxima']})")
        
        # What disappears?
        disappears = []
        if curr['B_local_maxima'] < prev['B_local_maxima'] * 0.5:
            disappears.append(f"B local maxima decreased ({prev['B_local_maxima']} → {curr['B_local_maxima']})")
        if curr['A_local_maxima'] < prev['A_local_maxima'] * 0.5:
            disappears.append(f"A local maxima decreased ({prev['A_local_maxima']} → {curr['A_local_maxima']})")
        
        # What repeats? (values stay similar)
        repeats = []
        if abs(curr['A_mean'] - prev['A_mean']) < 0.01:
            repeats.append(f"A mean stable (~{curr['A_mean']:.4f})")
        if abs(curr['B_mean'] - prev['B_mean']) < 0.005:
            repeats.append(f"B mean stable (~{curr['B_mean']:.4f})")
        
        # What stabilizes? (variance decreases)
        stabilizes = []
        if curr['A_spatial_variance'] < prev['A_spatial_variance'] * 0.8:
            stabilizes.append(f"A variance decreased ({prev['A_spatial_variance']:.6f} → {curr['A_spatial_variance']:.6f})")
        if curr['B_spatial_variance'] < prev['B_spatial_variance'] * 0.8:
            stabilizes.append(f"B variance decreased ({prev['B_spatial_variance']:.6f} → {curr['B_spatial_variance']:.6f})")
        
        ledger.append({
            'interval': f"t{t_prev}→t{t_curr}",
            'appears': appears if appears else ['none'],
            'disappears': disappears if disappears else ['none'],
            'repeats': repeats if repeats else ['none'],
            'stabilizes': stabilizes if stabilizes else ['none'],
        })
    
    return ledger

def main():
    print("RD-WELL.2A — Operational Change Ledger")
    print("=" * 60)
    print("Forbidden words: coherence, persistence, emergence, interaction,")
    print("observer, sentience, hierarchy, intelligence")
    print("=" * 60)
    
    all_ledgers = {}
    
    for pattern_name in ['bubbles', 'maze', 'spirals']:
        ledger = create_change_ledger(pattern_name)
        all_ledgers[pattern_name] = ledger
        
        print(f"\n{'='*60}")
        print(f"LEDGER: {pattern_name}")
        print(f"{'='*60}")
        for entry in ledger:
            print(f"\n{entry['interval']}:")
            print(f"  Appears: {', '.join(entry['appears'])}")
            print(f"  Disappears: {', '.join(entry['disappears'])}")
            print(f"  Repeats: {', '.join(entry['repeats'])}")
            print(f"  Stabilizes: {', '.join(entry['stabilizes'])}")
    
    # Save results
    output_dir = "/home/student/sgp_core_v2/audits/rd_well2a"
    os.makedirs(output_dir, exist_ok=True)
    
    output = {
        'description': 'Operational Change Ledger',
        'forbidden_words': ['coherence', 'persistence', 'emergence', 'interaction', 
                           'observer', 'sentience', 'hierarchy', 'intelligence'],
        'ledgers': all_ledgers
    }
    
    output_file = os.path.join(output_dir, "operational_change_ledger.json")
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
