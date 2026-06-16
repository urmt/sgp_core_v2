#!/usr/bin/env python3
"""RD-MATH.2B.R2: Metric Unit Tests

Test whether TE and Empowerment recover known answers in toy systems.
"""

import numpy as np
import sys, time, json
sys.path.insert(0, "coherence-benchmark")
from metrics import compute_transfer_entropy_matrix, compute_predictive_information

# === TE UNIT TESTS ===

def te_system_a_independent(n_steps=1000):
    """X independent of Y. Expected TE = 0."""
    rng = np.random.default_rng(42)
    X = rng.random((1, n_steps))
    Y = rng.random((1, n_steps))
    return np.vstack([X, Y])

def te_system_b_causal(n_steps=1000):
    """Y(t+1) = X(t). Expected TE > 0."""
    rng = np.random.default_rng(42)
    X = np.zeros((1, n_steps))
    X[0, 0] = rng.random()
    for t in range(1, n_steps):
        X[0, t] = rng.random()
    
    Y = np.zeros((1, n_steps))
    for t in range(1, n_steps):
        Y[0, t] = X[0, t-1]
    
    return np.vstack([X, Y])

def te_system_c_random(n_steps=1000):
    """Y(t+1) = random. Expected TE ≈ 0."""
    rng = np.random.default_rng(42)
    X = rng.random((1, n_steps))
    Y = rng.random((1, n_steps))
    return np.vstack([X, Y])

# === EMPOWERMENT UNIT TESTS ===

def empowerment_system_a_low(n_steps=1000):
    """1 action → 1 outcome. Low empowerment."""
    rng = np.random.default_rng(42)
    # Single dimension, deterministic transitions
    X = np.zeros((1, n_steps))
    X[0, 0] = 0.5
    for t in range(1, n_steps):
        X[0, t] = 0.5 + 0.1 * np.sin(2 * np.pi * t / 100)
    return X

def empowerment_system_b_high(n_steps=1000):
    """4 actions → 4 distinct outcomes. High empowerment."""
    rng = np.random.default_rng(42)
    # 4 dimensions, each independent
    X = np.zeros((4, n_steps))
    for i in range(4):
        X[i, :] = rng.random(n_steps)
    return X

def empowerment_system_c_low(n_steps=1000):
    """Many actions → same outcome. Low empowerment."""
    rng = np.random.default_rng(42)
    # Many dimensions, all correlated
    base = rng.random(n_steps)
    X = np.zeros((4, n_steps))
    for i in range(4):
        X[i, :] = base + rng.normal(0, 0.01, n_steps)
    return X

# === MAIN ===

print("=== RD-MATH.2B.R2: Metric Unit Tests ===")
print()

# TE Tests
print("=== TE UNIT TESTS ===")
print()

te_tests = [
    ("A: X independent of Y", te_system_a_independent, 0),
    ("B: Y(t+1) = X(t)", te_system_b_causal, "positive"),
    ("C: Y(t+1) = random", te_system_c_random, 0),
]

for name, func, expected in te_tests:
    print(f"Test {name}:")
    data = func()
    print(f"  Shape: {data.shape}")
    
    te_matrix = compute_transfer_entropy_matrix(data, tau=1, k=1)
    TE = np.mean(te_matrix)
    
    print(f"  TE = {TE:.6f}")
    print(f"  Expected: {expected}")
    
    if expected == 0:
        passed = abs(TE) < 0.01
    elif expected == "positive":
        passed = TE > 0.01
    else:
        passed = False
    
    print(f"  PASS: {passed}")
    print()

# Empowerment Tests
print("=== EMPOWERMENT UNIT TESTS ===")
print()

emp_tests = [
    ("A: 1 action → 1 outcome", empowerment_system_a_low, "low"),
    ("B: 4 actions → 4 outcomes", empowerment_system_b_high, "high"),
    ("C: many actions → same outcome", empowerment_system_c_low, "low"),
]

emp_values = []
for name, func, expected in emp_tests:
    print(f"Test {name}:")
    data = func()
    print(f"  Shape: {data.shape}")
    
    I_pred = compute_predictive_information(data, tau=1, k=1)
    emp_values.append(I_pred)
    
    print(f"  Empowerment = {I_pred:.4f}")
    print(f"  Expected: {expected}")
    print()

# Check ordering
print("=== EMPOWERMENT ORDERING ===")
print()

a_val, b_val, c_val = emp_values
print(f"A (low): {a_val:.4f}")
print(f"B (high): {b_val:.4f}")
print(f"C (low): {c_val:.4f}")
print()

correct_ordering = (b_val > a_val) and (b_val > c_val)
print(f"B > A and B > C: {correct_ordering}")
print()

# Summary
print("=== SUMMARY ===")
print()

te_passed = all([
    abs(np.mean(compute_transfer_entropy_matrix(te_system_a_independent(), tau=1, k=1))) < 0.01,
    np.mean(compute_transfer_entropy_matrix(te_system_b_causal(), tau=1, k=1)) > 0.01,
    abs(np.mean(compute_transfer_entropy_matrix(te_system_c_random(), tau=1, k=1))) < 0.01,
])

print(f"TE unit tests: {'PASS' if te_passed else 'FAIL'}")
print(f"Empowerment ordering: {'PASS' if correct_ordering else 'FAIL'}")
print()

if te_passed and correct_ordering:
    print("VERDICT: Metrics recover known answers. Ready for scientific use.")
else:
    print("VERDICT: Metrics do not recover known answers. Need repair before use.")

# Save results
with open("audits/RD_MATH_2B_R2/unit_test_results.json", "w") as f:
    json.dump({
        "TE_tests": [
            {"name": name, "TE": float(np.mean(compute_transfer_entropy_matrix(func(), tau=1, k=1))), "expected": expected}
            for name, func, expected in te_tests
        ],
        "Empowerment_tests": [
            {"name": name, "value": float(val), "expected": expected}
            for (name, _, expected), val in zip(emp_tests, emp_values)
        ],
        "te_passed": bool(te_passed),
        "emp_ordering_passed": bool(correct_ordering)
    }, f, indent=2)
