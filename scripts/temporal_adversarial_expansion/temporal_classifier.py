"""
Temporal Classifier

Simple classifier to distinguish organized from adversarial systems.
"""

import numpy as np
from typing import List, Tuple, Dict
import json
import sys
sys.path.insert(0, 'scripts/temporal_memory')

from temporal_dynamics import generate_temporal_system
from memory_metrics import (
    InteractionMemoryScore, StructuralPersistence,
    TemporalFragmentationVariance, TemporalConsensusScore,
    RecoveryLatency, HysteresisLoopArea
)
sys.path.insert(0, 'scripts/temporal_adversarial_expansion')
from advanced_temporal_adversaries import generate_temporal_adversary


def extract_features(traj: np.ndarray, seed: int) -> np.ndarray:
    """Extract temporal features as vector."""
    features = []
    
    memory = InteractionMemoryScore(seed).compute(traj)
    persist = StructuralPersistence(seed).compute(traj)
    frag = TemporalFragmentationVariance(seed).compute(traj)
    consensus = TemporalConsensusScore(seed).compute(traj)
    
    features = [
        memory['memory_score_mean'],
        memory['memory_score_std'],
        persist['persistence_mean'],
        persist['persistence_std'],
        frag['fragmentation_std'],
        consensus['consensus_mean'],
        consensus['consensus_std']
    ]
    
    # Try optional metrics
    try:
        recovery = RecoveryLatency(seed).compute(traj)
        features.append(recovery['recovery_latency'])
    except:
        features.append(0)
    
    try:
        hyst = HysteresisLoopArea(seed).compute(traj)
        features.append(hyst['hysteresis_area'])
    except:
        features.append(0)
    
    return np.array(features)


def load_dataset(n_per_class: int = 15) -> Tuple[np.ndarray, np.ndarray]:
    """Load training data."""
    X, y = [], []
    
    organized = ['stable_hierarchy', 'perturb_recover']
    adversarial = ['replay_memory_spoof', 'delayed_random_coherence', 'temporal_camouflage']
    
    # Organized systems
    for system in organized:
        for seed in range(42, 42 + n_per_class):
            try:
                traj, _ = generate_temporal_system(system, seed=seed, n=30, dimensions=5, n_timesteps=20)
                feat = extract_features(traj, seed)
                X.append(feat)
                y.append(1)  # organized
            except Exception as e:
                pass
    
    # Adversarial systems
    for system in adversarial:
        for seed in range(42, 42 + n_per_class):
            try:
                traj, _ = generate_temporal_adversary(system, seed=seed, n=30, dimensions=5, n_timesteps=20)
                feat = extract_features(traj, seed)
                X.append(feat)
                y.append(0)  # adversarial
            except Exception as e:
                pass
    
    return np.array(X), np.array(y)


def simple_classifier(X_train: np.ndarray, y_train: np.ndarray, 
                      X_test: np.ndarray) -> np.ndarray:
    """Simple nearest-centroid classifier."""
    # Compute centroids
    organized_mask = y_train == 1
    centroid_organ = X_train[organized_mask].mean(axis=0)
    centroid_adv = X_train[~organized_mask].mean(axis=0)
    
    # Classify by distance
    preds = []
    for x in X_test:
        dist_organ = np.linalg.norm(x - centroid_organ)
        dist_adv = np.linalg.norm(x - centroid_adv)
        preds.append(1 if dist_organ < dist_adv else 0)
    
    return np.array(preds)


def cross_validate(X: np.ndarray, y: np.ndarray, n_folds: int = 5) -> Dict:
    """K-fold cross validation."""
    n = len(X)
    fold_size = n // n_folds
    
    all_preds = np.zeros(n)
    all_true = np.zeros(n)
    
    indices = np.random.permutation(n)
    
    for fold in range(n_folds):
        test_indices = indices[fold * fold_size:(fold + 1) * fold_size]
        train_indices = np.concatenate([indices[:fold * fold_size], indices[(fold + 1) * fold_size:]])
        
        X_train, y_train = X[train_indices], y[train_indices]
        X_test, y_test = X[test_indices], y[test_indices]
        
        preds = simple_classifier(X_train, y_train, X_test)
        
        all_preds[test_indices] = preds
        all_true[test_indices] = y_test
    
    # Metrics
    accuracy = (all_preds == all_true).mean()
    true_positives = ((all_preds == 1) & (all_true == 1)).sum()
    false_positives = ((all_preds == 1) & (all_true == 0)).sum()
    precision = true_positives / (true_positives + false_positives + 1e-10)
    recall = true_positives / (all_true == 1).sum()
    fpr = false_positives / (all_true == 0).sum()
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'false_positive_rate': fpr,
        'confusion_matrix': {
            'tp': int(true_positives),
            'fp': int(false_positives),
            'tn': int(((all_preds == 0) & (all_true == 0)).sum()),
            'fn': int(((all_preds == 0) & (all_true == 1)).sum())
        }
    }


if __name__ == '__main__':
    np.random.seed(42)
    
    print("=" * 60)
    print("TEMPORAL CLASSIFIER")
    print("=" * 60)
    
    print("\nLoading dataset...")
    X, y = load_dataset(n_per_class=10)
    print(f"Dataset: {len(X)} samples, {y.sum()} organized, {len(y) - y.sum()} adversarial")
    
    print("\nRunning cross-validation...")
    metrics = cross_validate(X, y, n_folds=5)
    
    print(f"\n=== RESULTS ===")
    print(f"Accuracy: {metrics['accuracy']:.1%}")
    print(f"Precision: {metrics['precision']:.1%}")
    print(f"Recall: {metrics['recall']:.1%}")
    print(f"False Positive Rate: {metrics['false_positive_rate']:.1%}")
    print(f"Confusion: {metrics['confusion_matrix']}")
    
    target_met = metrics['accuracy'] > 0.80 and metrics['false_positive_rate'] < 0.15
    print(f"\nTarget (80% acc, <15% FPR): {'PASS' if target_met else 'FAIL'}")
    
    # Save
    output = '/home/student/sgp_core_v2/outputs/temporal_adversarial_expansion/classifier_results.json'
    with open(output, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved: {output}")