#!/usr/bin/env python3
"""
P19 — Predictive Failure Cartography

Purpose: Where do minimal invariant reconstructions fail first?
Core question: Predictive breakdown under progressive perturbation.

Architecture:
  Layer A: Reconstruction Stress Tests (progressive perturbation)
  Layer B: Breakdown Frontiers (phase boundaries)
  Layer C: Irreducible Observer Sensitivity (domains where no prediction survives)
  Layer D: Non-Reconstructible Regions (dead zones)
  Layer E: Warning Failure Ecology (which warnings fail first)

Allowed: failure mapping, breakdown regions, instability frontiers, dead zones
Forbidden: strengthening claims, extending prediction, rebuilding structure
"""

import numpy as np
import json
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

DOMAINS = {
    "GS": {"trajectories": 50, "max_N": 10},
    "RB": {"trajectories": 25, "max_N": 10},
    "CML": {"trajectories": 12, "max_N": 10},
    "AM": {"trajectories": 2, "max_N": 2},
}

PERTURBATION_LEVELS = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

OUTPUT_DIR = Path("audits/rd_p19_failure_cartography")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# P18 BASELINE PREDICTIONS
# ============================================================================


def get_p18_predictions(domain, max_N):
    """Return P18 predictions for a domain."""
    return {
        "convergence_envelope": {
            "cv_lower": 0.05,
            "cv_upper": lambda n: 3.0 / np.sqrt(n) if n > 0 else 3.0,
            "convergence_direction": "decreasing" if domain in ["GS", "RB", "CML"] else "unknown",
            "confidence": "high" if domain in ["GS", "RB", "CML"] else "low",
        },
        "admissibility_boundary": {
            "warning_probability": lambda n: 0.8 if n < 5 else 0.4,
            "disagreement_probability": 0.5,
        },
        "perturbation_envelope": {
            "sensitivity_lower": 0.05,
            "sensitivity_upper": lambda n: 2.0 / np.sqrt(n) if n > 0 else 2.0,
        },
        "observer_divergence": {
            "divergence_probability": lambda n: 0.9 if n < 3 else 0.7,
            "instability_probability": lambda n: 0.8 if n < 5 else 0.5,
        },
    }


# ============================================================================
# SIMULATION: Domain Data Generation
# ============================================================================


def generate_gs_data(n_trajectories=50, n_steps=100, grid_size=64, seed=42):
    """Generate Gray-Scott-like reaction-diffusion data."""
    rng = np.random.RandomState(seed)
    trajectories = []
    for t in range(n_trajectories):
        np.random.seed(seed + t)
        A = np.ones((grid_size, grid_size)) * 0.5
        B = np.zeros((grid_size, grid_size))
        cx, cy = grid_size // 2, grid_size // 2
        r = grid_size // 4
        A[cx-r:cx+r, cy-r:cy+r] = 0.5
        B[cx-r:cx+r, cy-r:cy+r] = 0.25
        
        F, k = 0.029 + rng.uniform(-0.005, 0.005), 0.057 + rng.uniform(-0.005, 0.005)
        dt = 1.0
        
        frames = []
        for step in range(n_steps):
            lap_A = np.roll(A, 1, axis=0) + np.roll(A, -1, axis=0) + np.roll(A, 1, axis=1) + np.roll(A, -1, axis=1) - 4 * A
            lap_B = np.roll(B, 1, axis=0) + np.roll(B, -1, axis=0) + np.roll(B, 1, axis=1) + np.roll(B, -1, axis=1) - 4 * B
            A += dt * (0.2 * lap_A - A * B**2 + F * (1 - A))
            B += dt * (0.1 * lap_B + A * B**2 - (F + k) * B)
            frames.append(np.mean(B))
        trajectories.append(np.array(frames))
    return np.array(trajectories)


def generate_rb_data(n_trajectories=25, n_steps=100, grid_size=64, seed=42):
    """Generate Rayleigh-Benard-like convection data."""
    rng = np.random.RandomState(seed)
    trajectories = []
    for t in range(n_trajectories):
        np.random.seed(seed + t)
        x = np.linspace(0, 2*np.pi, grid_size)
        y = np.linspace(0, np.pi, grid_size)
        X, Y = np.meshgrid(x, y)
        
        Ra = 1708 + rng.uniform(-100, 500)
        frames = []
        for step in range(n_steps):
            A1 = rng.uniform(0.1, 0.5)
            T = A1 * np.sin(np.pi * X / (2*np.pi)) * np.sin(np.pi * Y / np.pi) * np.exp(-0.01 * step)
            T += 0.01 * rng.randn(grid_size, grid_size)
            frames.append(np.mean(T**2))
        trajectories.append(np.array(frames))
    return np.array(trajectories)


def generate_cml_data(n_trajectories=12, n_steps=100, grid_size=64, epsilon=0.5, r=3.8, seed=42):
    """Generate Coupled Map Lattice data."""
    rng = np.random.RandomState(seed)
    trajectories = []
    for t in range(n_trajectories):
        np.random.seed(seed + t)
        x = rng.uniform(0, 1, (grid_size, grid_size))
        frames = []
        for step in range(n_steps):
            f_x = r * x * (1 - x)
            lap = np.roll(f_x, 1, axis=0) + np.roll(f_x, -1, axis=0) + np.roll(f_x, 1, axis=1) + np.roll(f_x, -1, axis=1) - 4 * f_x
            x = (1 - epsilon) * f_x + (epsilon / 4) * lap
            frames.append(np.mean(x))
        trajectories.append(np.array(frames))
    return np.array(trajectories)


def generate_am_data(n_trajectories=2, n_steps=81, grid_size=64, seed=42):
    """Generate Active Matter-like data."""
    rng = np.random.RandomState(seed)
    trajectories = []
    for t in range(n_trajectories):
        np.random.seed(seed + t)
        n_particles = 200
        pos = rng.uniform(0, grid_size, (n_particles, 2))
        vel = rng.randn(n_particles, 2)
        frames = []
        for step in range(n_steps):
            noise = rng.randn(n_particles, 2) * 0.5
            vel += noise
            vel /= (np.linalg.norm(vel, axis=1, keepdims=True) + 1e-8)
            pos += vel
            pos %= grid_size
            density = np.zeros((grid_size, grid_size))
            for p in range(n_particles):
                ix, iy = int(pos[p, 0]) % grid_size, int(pos[p, 1]) % grid_size
                density[ix, iy] += 1
            frames.append(np.mean(density))
        trajectories.append(np.array(frames))
    return np.array(trajectories)


# ============================================================================
# PERTURBATION OPERATORS
# ============================================================================


def apply_noise_perturbation(data, level):
    """Add Gaussian noise proportional to signal variance."""
    noise = np.random.randn(*data.shape) * level * np.std(data)
    return data + noise


def apply_subsampling_perturbation(data, level):
    """Subsample temporal dimension."""
    n_samples = max(2, int(data.shape[-1] * (1 - level)))
    indices = np.linspace(0, data.shape[-1] - 1, n_samples, dtype=int)
    return data[..., indices]


def apply_scale_perturbation(data, level):
    """Multiply by random scale factor."""
    scale = 1.0 + level * (np.random.rand() - 0.5)
    return data * scale


def apply_offset_perturbation(data, level):
    """Add random offset."""
    offset = level * np.random.randn() * np.std(data)
    return data + offset


PERTURBATION_OPERATORS = [
    ("noise", apply_noise_perturbation),
    ("subsampling", apply_subsampling_perturbation),
    ("scale", apply_scale_perturbation),
    ("offset", apply_offset_perturbation),
]


# ============================================================================
# LAYER A: RECONSTRUCTION STRESS TESTS
# ============================================================================


def measure_cv(data):
    """Compute coefficient of variation of temporal means across trajectories."""
    means = np.mean(data, axis=-1)
    if np.mean(means) == 0:
        return 0.0
    return np.std(means) / np.mean(means)


def compute_convergence_cv(data, n_subsets):
    """Compute CV for a given number of trajectories (subsets)."""
    n_traj = data.shape[0]
    if n_subsets > n_traj:
        n_subsets = n_traj
    subset = data[:n_subsets]
    return measure_cv(subset)


def layer_a_stress_test(domain_name, data):
    """Progressively perturb data and measure when P18 predictions fail."""
    results = []
    n_traj = data.shape[0]
    
    for level in PERTURBATION_LEVELS:
        for p_name, p_func in PERTURBATION_OPERATORS:
            if p_name == PERTURBATION_OPERATORS[0][0]:
                pass  # continue
            
        level_results = {"perturbation_level": level, "perturbations": {}}
        
        for p_name, p_func in PERTURBATION_OPERATORS:
            perturbed = p_func(data, level)
            
            # Measure convergence behavior
            cv_values = []
            for n in range(1, min(n_traj + 1, 11)):
                cv = compute_convergence_cv(perturbed, n)
                cv_values.append(cv)
            
            # Test P18 predictions
            p18_pass = True
            failure_point = None
            
            for n_idx, n in enumerate(range(1, len(cv_values) + 1)):
                cv = cv_values[n_idx]
                
                # P18 prediction: cv > 0.05 (convergence floor)
                if cv < 0.05:
                    p18_pass = False
                    failure_point = n
                    break
                
                # P18 prediction: cv decreasing for GS/RB/CML
                if domain_name in ["GS", "RB", "CML"] and n > 1:
                    if cv_values[n_idx] > cv_values[n_idx - 1] * 1.1:  # 10% tolerance
                        p18_pass = False
                        failure_point = n
                        break
            
            level_results["perturbations"][p_name] = {
                "cv_values": cv_values,
                "p18_prediction_passes": p18_pass,
                "failure_point": failure_point,
            }
        
        results.append(level_results)
    
    return results


# ============================================================================
# LAYER B: BREAKDOWN FRONTIERS
# ============================================================================


def layer_b_breakdown_frontiers(domain_name, layer_a_results):
    """Identify perturbation levels where predictions first fail."""
    frontiers = {}
    
    for p_name in ["noise", "subsampling", "scale", "offset"]:
        failure_level = None
        for result in layer_a_results:
            level = result["perturbation_level"]
            p_data = result["perturbations"][p_name]
            
            if not p_data["p18_prediction_passes"]:
                failure_level = level
                break
        
        frontiers[p_name] = {
            "failure_level": failure_level,
            "survives_all": failure_level is None,
        }
    
    return frontiers


# ============================================================================
# LAYER C: IRREDUCIBLE OBSERVER SENSITIVITY
# ============================================================================


def layer_c_observer_sensitivity(domain_name, data):
    """Test whether ANY observer-independent prediction survives."""
    n_traj = data.shape[0]
    
    # Compute C for different observer perspectives
    # Perspective 1: temporal mean
    means = np.mean(data, axis=-1)
    cv_mean = np.std(means) / np.mean(means) if np.mean(means) > 0 else 0
    
    # Perspective 2: temporal variance
    variances = np.var(data, axis=-1)
    cv_var = np.std(variances) / np.mean(variances) if np.mean(variances) > 0 else 0
    
    # Perspective 3: spatial mean (if spatial data)
    spatial_means = np.mean(data, axis=tuple(range(len(data.shape) - 1)))
    cv_spatial = np.std(spatial_means) / np.mean(spatial_means) if np.mean(spatial_means) > 0 else 0
    
    # Test: are these observers consistent?
    observer_values = [cv_mean, cv_var, cv_spatial]
    observer_agreement = np.std(observer_values) / np.mean(observer_values) if np.mean(observer_values) > 0 else 0
    
    irreducible_sensitivity = observer_agreement > 0.5  # threshold
    
    return {
        "cv_mean": float(cv_mean),
        "cv_var": float(cv_var),
        "cv_spatial": float(cv_spatial),
        "observer_agreement": float(observer_agreement),
        "irreducible_sensitivity": bool(irreducible_sensitivity),
    }


# ============================================================================
# LAYER D: NON-RECONSTRUCTIBLE REGIONS
# ============================================================================


def layer_d_non_reconstructible(domain_name, data):
    """Identify regimes where prediction is impossible."""
    n_traj = data.shape[0]
    
    dead_zones = []
    
    # Dead zone 1: too few trajectories
    if n_traj < 3:
        dead_zones.append({
            "type": "insufficient_replication",
            "threshold": 3,
            "actual": n_traj,
            "description": f"N={n_traj} trajectories insufficient for convergence measurement",
        })
    
    # Dead zone 2: signal too weak
    means = np.mean(data, axis=-1)
    if np.mean(means) < 1e-6:
        dead_zones.append({
            "type": "signal_insufficient",
            "threshold": 1e-6,
            "actual": float(np.mean(means)),
            "description": "Signal amplitude below measurement threshold",
        })
    
    # Dead zone 3: variance too low
    variances = np.var(data, axis=-1)
    if np.mean(variances) < 1e-10:
        dead_zones.append({
            "type": "variance_insufficient",
            "threshold": 1e-10,
            "actual": float(np.mean(variances)),
            "description": "Variance below convergence measurement threshold",
        })
    
    # Dead zone 4: non-stationarity
    if n_traj >= 4:
        half = n_traj // 2
        first_half_cv = np.std(np.mean(data[:half], axis=-1))
        second_half_cv = np.std(np.mean(data[half:], axis=-1))
        if first_half_cv > 0 and second_half_cv > 0:
            ratio = second_half_cv / first_half_cv
            if ratio > 2.0 or ratio < 0.5:
                dead_zones.append({
                    "type": "non_stationarity",
                    "ratio": float(ratio),
                    "description": "Temporal statistics non-stationary across trajectories",
                })
    
    return {
        "dead_zones": dead_zones,
        "n_dead_zones": len(dead_zones),
        "reconstructible": len(dead_zones) == 0,
    }


# ============================================================================
# LAYER E: WARNING FAILURE ECOLOGY
# ============================================================================


def layer_e_warning_failure(domain_name, layer_a_results, layer_b_frontiers, layer_c_sensitivity):
    """Map which warnings fail first and which become indispensable."""
    
    warnings = {
        "convergence_floor": {
            "fails": False,
            "failure_level": None,
            "indispensable": True,
        },
        "cv_decreasing": {
            "fails": False,
            "failure_level": None,
            "indispensable": domain_name in ["GS", "RB", "CML"],
        },
        "warning_coactivation": {
            "fails": False,
            "failure_level": None,
            "indispensable": True,
        },
        "structure_disagreement": {
            "fails": False,
            "failure_level": None,
            "indispensable": False,
        },
    }
    
    # Check convergence_floor
    for p_name in ["noise", "subsampling", "scale", "offset"]:
        frontier = layer_b_frontiers[p_name]
        if frontier["failure_level"] is not None:
            warnings["convergence_floor"]["fails"] = True
            warnings["convergence_floor"]["failure_level"] = frontier["failure_level"]
            break
    
    # Check cv_decreasing
    if domain_name in ["GS", "RB", "CML"]:
        for result in layer_a_results:
            for p_name in ["noise", "subsampling", "scale", "offset"]:
                p_data = result["perturbations"][p_name]
                if p_data["failure_point"] is not None:
                    warnings["cv_decreasing"]["fails"] = True
                    warnings["cv_decreasing"]["failure_level"] = result["perturbation_level"]
                    break
            if warnings["cv_decreasing"]["fails"]:
                break
    
    # Warning interaction effects
    warning_interaction = {
        "convergence_floor_and_cv_decreasing": (
            warnings["convergence_floor"]["fails"] and warnings["cv_decreasing"]["fails"]
        ),
        "any_warning_fails": any(w["fails"] for w in warnings.values()),
        "all_warnings_fail": all(w["fails"] for w in warnings.values()),
    }
    
    return {
        "warnings": warnings,
        "interaction": warning_interaction,
    }


# ============================================================================
# MAIN ANALYSIS
# ============================================================================


def run_p19_analysis():
    print("=" * 80)
    print("P19 — PREDICTIVE FAILURE CARTOGRAPHY")
    print("=" * 80)
    print()
    print("PURPOSE: Where do minimal invariant reconstructions fail first?")
    print("CORE QUESTION: Predictive breakdown under progressive perturbation")
    print()
    
    all_results = {}
    
    for domain_name, config in DOMAINS.items():
        print(f"{'='*80}")
        print(f"DOMAIN: {domain_name}")
        print(f"{'='*80}")
        print()
        
        # Generate domain data
        if domain_name == "GS":
            data = generate_gs_data(n_trajectories=config["trajectories"])
        elif domain_name == "RB":
            data = generate_rb_data(n_trajectories=config["trajectories"])
        elif domain_name == "CML":
            data = generate_cml_data(n_trajectories=config["trajectories"])
        elif domain_name == "AM":
            data = generate_am_data(n_trajectories=config["trajectories"])
        else:
            raise ValueError(f"Unknown domain: {domain_name}")
        
        print(f"  Data shape: {data.shape}")
        print()
        
        # Layer A: Reconstruction Stress Tests
        print("  LAYER A: Reconstruction Stress Tests")
        layer_a = layer_a_stress_test(domain_name, data)
        n_failures = sum(
            1 for r in layer_a
            for p in r["perturbations"].values()
            if not p["p18_prediction_passes"]
        )
        n_tests = len(layer_a) * len(PERTURBATION_OPERATORS)
        print(f"    Failures: {n_failures}/{n_tests}")
        print()
        
        # Layer B: Breakdown Frontiers
        print("  LAYER B: Breakdown Frontiers")
        layer_b = layer_b_breakdown_frontiers(domain_name, layer_a)
        for p_name, frontier in layer_b.items():
            if frontier["survives_all"]:
                print(f"    {p_name}: SURVIVES ALL PERTURBATIONS")
            else:
                print(f"    {p_name}: FAILS AT LEVEL {frontier['failure_level']}")
        print()
        
        # Layer C: Irreducible Observer Sensitivity
        print("  LAYER C: Irreducible Observer Sensitivity")
        layer_c = layer_c_observer_sensitivity(domain_name, data)
        print(f"    Observer agreement: {layer_c['observer_agreement']:.3f}")
        print(f"    Irreducible sensitivity: {layer_c['irreducible_sensitivity']}")
        print()
        
        # Layer D: Non-Reconstructible Regions
        print("  LAYER D: Non-Reconstructible Regions")
        layer_d = layer_d_non_reconstructible(domain_name, data)
        print(f"    Dead zones: {layer_d['n_dead_zones']}")
        print(f"    Reconstructible: {layer_d['reconstructible']}")
        for dz in layer_d["dead_zones"]:
            print(f"      - {dz['type']}: {dz['description']}")
        print()
        
        # Layer E: Warning Failure Ecology
        print("  LAYER E: Warning Failure Ecology")
        layer_e = layer_e_warning_failure(domain_name, layer_a, layer_b, layer_c)
        for w_name, w_data in layer_e["warnings"].items():
            status = "FAILS" if w_data["fails"] else "SURVIVES"
            if w_data["fails"]:
                print(f"    {w_name}: {status} at level {w_data['failure_level']}")
            else:
                print(f"    {w_name}: {status}")
        print(f"    Any warning fails: {layer_e['interaction']['any_warning_fails']}")
        print(f"    All warnings fail: {layer_e['interaction']['all_warnings_fail']}")
        print()
        
        all_results[domain_name] = {
            "data_shape": list(data.shape),
            "layer_a_stress_tests": layer_a,
            "layer_b_breakdown_frontiers": layer_b,
            "layer_c_observer_sensitivity": layer_c,
            "layer_d_non_reconstructible": layer_d,
            "layer_e_warning_failure": layer_e,
        }
    
    # Save results
    output_file = OUTPUT_DIR / "p19_results.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"Results saved to {output_file}")
    
    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    for domain_name, results in all_results.items():
        print(f"\n{domain_name}:")
        frontiers = results["layer_b_breakdown_frontiers"]
        surviving = [p for p, f in frontiers.items() if f["survives_all"]]
        failing = [p for p, f in frontiers.items() if not f["survives_all"]]
        print(f"  Survives all perturbations: {surviving}")
        print(f"  Fails under perturbation: {failing}")
        print(f"  Dead zones: {results['layer_d_non_reconstructible']['n_dead_zones']}")
        print(f"  Irreducible observer sensitivity: {results['layer_c_observer_sensitivity']['irreducible_sensitivity']}")
    
    return all_results


if __name__ == "__main__":
    run_p19_analysis()
