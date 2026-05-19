"""
Temporal Adversarial Visualizations
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
import sys
sys.path.insert(0, 'scripts/temporal_memory')

from temporal_dynamics import generate_temporal_system
from memory_metrics import InteractionMemoryScore, StructuralPersistence, TemporalConsensusScore
sys.path.insert(0, 'scripts/temporal_adversarial_expansion')
from advanced_temporal_adversaries import generate_temporal_adversary


def generate_visualizations():
    """Generate all visualization plots."""
    
    np.random.seed(42)
    params = {'n': 30, 'dimensions': 5, 'n_timesteps': 20}
    
    # 1. Persistence distributions
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    
    systems = ['stable_hierarchy', 'random_temporal', 'perturb_recover']
    persistences = []
    
    for idx, system in enumerate(systems):
        traj, _ = generate_temporal_system(system, seed=42, **params)
        persist = StructuralPersistence(42).compute(traj)
        persistences.append(persist['persistence_mean'])
        axes[idx].bar(idx, persist['persistence_mean'], yerr=persist['persistence_std'], alpha=0.7)
        axes[idx].set_title(system)
        axes[idx].set_ylabel('Persistence Mean')
    
    plt.suptitle('Temporal Persistence Distributions')
    plt.tight_layout()
    plt.savefig('/home/student/sgp_core_v2/outputs/temporal_adversarial_expansion/figures/persistence_distributions.png', dpi=100)
    plt.close()
    
    # 2. Adversarial comparison
    fig, ax = plt.subplots(figsize=(8, 5))
    
    labels = ['stable_hierarchy', 'random_temporal', 'perturb_recover', 
              'replay_spoof', 'delayed_coherence', 'temporal_camo']
    consensus_scores = []
    
    for label in labels:
        if 'spoof' in label or 'coherence' in label or 'camo' in label:
            # Adversarial
            adv_map = {
                'replay_spoof': 'replay_memory_spoof',
                'delayed_coherence': 'delayed_random_coherence',
                'temporal_camo': 'temporal_camouflage'
            }
            traj, _ = generate_temporal_adversary(adv_map[label], seed=42, **params)
        else:
            traj, _ = generate_temporal_system(label, seed=42, **params)
        
        consensus = TemporalConsensusScore(42).compute(traj)
        consensus_scores.append(consensus['consensus_mean'])
    
    colors = ['green', 'red', 'green', 'red', 'red', 'red']
    ax.bar(range(len(labels)), consensus_scores, color=colors, alpha=0.7)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.set_ylabel('Consensus Score')
    ax.set_title('Adversarial vs Legitimate Systems')
    
    plt.tight_layout()
    plt.savefig('/home/student/sgp_core_v2/outputs/temporal_adversarial_expansion/figures/adversarial_comparison.png', dpi=100)
    plt.close()
    
    # 3. Scale robustness curves
    with open('/home/student/sgp_core_v2/outputs/temporal_adversarial_expansion/scale_results.json', 'r') as f:
        scale_data = json.load(f)
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    scales = sorted(scale_data.keys())
    for system in ['stable_hierarchy', 'random_temporal']:
        values = [scale_data[s][system]['consensus'] for s in scales]
        ax.plot(scales, values, marker='o', label=system)
    
    ax.set_xlabel('N (graph size)')
    ax.set_ylabel('Consensus Score')
    ax.set_title('Scale Robustness')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/student/sgp_core_v2/outputs/temporal_adversarial_expansion/figures/scale_robustness.png', dpi=100)
    plt.close()
    
    # 4. Classifier confusion matrix visualization
    with open('/home/student/sgp_core_v2/outputs/temporal_adversarial_expansion/classifier_results.json', 'r') as f:
        clf_data = json.load(f)
    
    cm = clf_data['confusion_matrix']
    fig, ax = plt.subplots(figsize=(6, 5))
    
    cmatrix = [[cm['tn'], cm['fp']], [cm['fn'], cm['tp']]]
    im = ax.imshow(cmatrix, cmap='Blues')
    
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(['Adversarial', 'Organized'])
    ax.set_yticklabels(['Adversarial', 'Organized'])
    
    for i in range(2):
        for j in range(2):
            ax.text(j, i, cmatrix[i][j], ha='center', va='center', fontsize=14)
    
    ax.set_title(f'Classifier Confusion Matrix\nAccuracy: {clf_data["accuracy"]:.1%}')
    
    plt.tight_layout()
    plt.savefig('/home/student/sgp_core_v2/outputs/temporal_adversarial_expansion/figures/confusion_matrix.png', dpi=100)
    plt.close()
    
    print("Visualizations saved to figures/")


if __name__ == '__main__':
    generate_visualizations()