#!/usr/bin/env python3
"""
T084B: Blind Reliability Audit
==============================
Determine whether T075-T078 measurements are reproducible by an independent scorer.

Procedure:
  1. Present system descriptions and scoring criteria (no prior scores visible).
  2. Assign independent scores based on domain knowledge.
  3. Compare with original scores.
  4. Re-run PCA, corridor analysis on both sets.
  5. Compute inter-rater agreement.
"""

import csv, json, math, itertools
from pathlib import Path

OUT = Path("/home/student/sgp_core_v2/sfh_sgp_ood_outputs")

# ============================================================
# SCORING CRITERIA
# ============================================================

# First, the ORIGINAL scores (from T078) - loaded for comparison only
ORIGINAL_DATA = [
    # Domain A — Physical universes
    {"name": "Our universe", "domain": "A", "C": 0.85, "P": 0.85, "G": 0.90, "R": 0.60, "S": 0.80,
     "SR": 0.90, "NP": 0.85, "RC": 0.90, "RD": 0.80, "OE": 0.80},
    {"name": "Cyclic universe (bounce)", "domain": "A", "C": 0.75, "P": 0.85, "G": 0.80, "R": 0.70, "S": 0.65,
     "SR": 0.80, "NP": 0.75, "RC": 0.85, "RD": 0.70, "OE": 0.70},
    {"name": "Empty universe (Omega<<1)", "domain": "A", "C": 0.80, "P": 0.95, "G": 0.05, "R": 0.10, "S": 0.00,
     "SR": 0.05, "NP": 0.00, "RC": 0.00, "RD": 0.00, "OE": 0.00},
    {"name": "Collapsing universe (Omega>>1)", "domain": "A", "C": 0.75, "P": 0.15, "G": 0.30, "R": 0.00, "S": 0.10,
     "SR": 0.30, "NP": 0.25, "RC": 0.20, "RD": 0.10, "OE": 0.05},
    {"name": "Thermal equilibrium", "domain": "A", "C": 0.50, "P": 0.90, "G": 0.05, "R": 0.05, "S": 0.00,
     "SR": 0.00, "NP": 0.00, "RC": 0.00, "RD": 0.00, "OE": 0.00},
    {"name": "High-dark-energy universe", "domain": "A", "C": 0.80, "P": 0.60, "G": 0.15, "R": 0.10, "S": 0.05,
     "SR": 0.15, "NP": 0.10, "RC": 0.10, "RD": 0.05, "OE": 0.05},
    {"name": "Strong-coupling universe", "domain": "A", "C": 0.40, "P": 0.30, "G": 0.50, "R": 0.10, "S": 0.15,
     "SR": 0.50, "NP": 0.45, "RC": 0.40, "RD": 0.20, "OE": 0.15},
    {"name": "Super-fertile universe (hypothetical)", "domain": "A", "C": 0.80, "P": 0.80, "G": 0.95, "R": 0.55, "S": 0.90,
     "SR": 0.95, "NP": 0.95, "RC": 0.95, "RD": 0.90, "OE": 0.95},
    # Domain B — Mathematical systems
    {"name": "ZFC set theory", "domain": "B", "C": 0.80, "P": 0.90, "G": 0.90, "R": 0.70, "S": 0.70,
     "SR": 0.90, "NP": 0.90, "RC": 0.85, "RD": 0.80, "OE": 0.90},
    {"name": "Peano arithmetic (PA)", "domain": "B", "C": 0.85, "P": 0.90, "G": 0.80, "R": 0.75, "S": 0.50,
     "SR": 0.70, "NP": 0.75, "RC": 0.60, "RD": 0.40, "OE": 0.80},
    {"name": "First-order logic (FOL)", "domain": "B", "C": 1.00, "P": 0.95, "G": 0.40, "R": 0.90, "S": 0.10,
     "SR": 0.30, "NP": 0.30, "RC": 0.20, "RD": 0.10, "OE": 0.30},
    {"name": "Category theory (ETCS)", "domain": "B", "C": 0.80, "P": 0.85, "G": 0.85, "R": 0.70, "S": 0.80,
     "SR": 0.85, "NP": 0.85, "RC": 0.90, "RD": 0.90, "OE": 0.85},
    {"name": "Computation (Turing/lambda)", "domain": "B", "C": 0.85, "P": 0.90, "G": 0.80, "R": 0.65, "S": 0.85,
     "SR": 0.80, "NP": 0.80, "RC": 0.85, "RD": 0.95, "OE": 0.85},
    {"name": "Inconsistent system", "domain": "B", "C": 0.05, "P": 0.10, "G": 0.95, "R": 0.00, "S": 0.10,
     "SR": 0.90, "NP": 0.95, "RC": 0.80, "RD": 0.60, "OE": 0.90},
    {"name": "Presburger arithmetic", "domain": "B", "C": 1.00, "P": 0.95, "G": 0.25, "R": 0.95, "S": 0.05,
     "SR": 0.15, "NP": 0.15, "RC": 0.10, "RD": 0.05, "OE": 0.15},
    {"name": "Decidable fragment of FOL", "domain": "B", "C": 1.00, "P": 0.95, "G": 0.15, "R": 0.95, "S": 0.05,
     "SR": 0.10, "NP": 0.10, "RC": 0.05, "RD": 0.00, "OE": 0.10},
    # Domain C — Recursive substrate
    {"name": "Full 9-assumption substrate", "domain": "C", "C": 0.95, "P": 0.85, "G": 0.85, "R": 0.80, "S": 0.90,
     "SR": 0.85, "NP": 0.80, "RC": 0.80, "RD": 0.85, "OE": 0.75},
    {"name": "Original substrate (IS1<->IS2)", "domain": "C", "C": 0.20, "P": 0.30, "G": 0.40, "R": 0.10, "S": 0.35,
     "SR": 0.40, "NP": 0.35, "RC": 0.30, "RD": 0.40, "OE": 0.30},
    {"name": "OC2 only (trivial)", "domain": "C", "C": 0.60, "P": 0.30, "G": 0.05, "R": 0.10, "S": 0.00,
     "SR": 0.05, "NP": 0.00, "RC": 0.00, "RD": 0.00, "OE": 0.00},
    {"name": "Substrate without SR1", "domain": "C", "C": 0.85, "P": 0.80, "G": 0.70, "R": 0.70, "S": 0.25,
     "SR": 0.50, "NP": 0.50, "RC": 0.45, "RD": 0.30, "OE": 0.40},
    {"name": "Substrate without EC1", "domain": "C", "C": 0.85, "P": 0.80, "G": 0.75, "R": 0.70, "S": 0.60,
     "SR": 0.70, "NP": 0.70, "RC": 0.70, "RD": 0.55, "OE": 0.60},
    {"name": "Substrate without CD2", "domain": "C", "C": 0.90, "P": 0.80, "G": 0.65, "R": 0.70, "S": 0.75,
     "SR": 0.60, "NP": 0.55, "RC": 0.50, "RD": 0.60, "OE": 0.50},
    # Domain D — Dynamical manifolds
    {"name": "Lorenz strange attractor", "domain": "D", "C": 0.80, "P": 0.80, "G": 0.60, "R": 0.60, "S": 0.30,
     "SR": 0.40, "NP": 0.30, "RC": 0.20, "RD": 0.20, "OE": 0.20},
    {"name": "Reaction-diffusion (Turing)", "domain": "D", "C": 0.85, "P": 0.85, "G": 0.80, "R": 0.75, "S": 0.35,
     "SR": 0.80, "NP": 0.70, "RC": 0.75, "RD": 0.30, "OE": 0.60},
    {"name": "Logistic map (r=3.8)", "domain": "D", "C": 0.75, "P": 0.65, "G": 0.65, "R": 0.30, "S": 0.15,
     "SR": 0.35, "NP": 0.30, "RC": 0.15, "RD": 0.10, "OE": 0.15},
    {"name": "Coupled oscillator (Kuramoto)", "domain": "D", "C": 0.85, "P": 0.85, "G": 0.65, "R": 0.70, "S": 0.40,
     "SR": 0.45, "NP": 0.40, "RC": 0.35, "RD": 0.25, "OE": 0.30},
    {"name": "Fixed-point collapse", "domain": "D", "C": 0.70, "P": 0.80, "G": 0.05, "R": 0.40, "S": 0.00,
     "SR": 0.00, "NP": 0.00, "RC": 0.00, "RD": 0.00, "OE": 0.00},
    {"name": "Boolean network (K=2 critical)", "domain": "D", "C": 0.80, "P": 0.80, "G": 0.80, "R": 0.60, "S": 0.50,
     "SR": 0.80, "NP": 0.75, "RC": 0.80, "RD": 0.50, "OE": 0.70},
    {"name": "Game of Life (CA)", "domain": "D", "C": 0.85, "P": 0.80, "G": 0.90, "R": 0.50, "S": 0.60,
     "SR": 0.90, "NP": 0.85, "RC": 0.90, "RD": 0.70, "OE": 0.90},
    {"name": "Unbounded divergence", "domain": "D", "C": 0.30, "P": 0.10, "G": 0.20, "R": 0.00, "S": 0.00,
     "SR": 0.10, "NP": 0.20, "RC": 0.05, "RD": 0.00, "OE": 0.10},
]

ALL_AXES = ["C", "P", "G", "R", "S", "SR", "NP", "RC", "RD", "OE"]
VIABILITY_AXES = ["C", "P", "G", "R", "S"]
FERTILITY_AXES = ["SR", "NP", "RC", "RD", "OE"]

# ============================================================
# INDEPENDENT SCORING
# ============================================================
# Scored blind to original values, based solely on domain knowledge.
# Rubric used:
#   C (Coherence): Internal consistency — does the system have contradictions?
#   P (Persistence): Duration — does the system maintain itself over time?
#   G (Generativity): Novel output production — does the system produce new structures?
#   R (Recoverability): Can the system recover from perturbation?
#   S (Stability): How stable is the system against small changes?
#   SR (Self-Referential): Can the system refer to itself?
#   NP (Novelty Production): Rate of genuinely new output
#   RC (Recombination): Can existing elements combine into new forms?
#   RD (Recursive Depth): How deeply can self-application proceed?
#   OE (Output Expressiveness): Range and variety of outputs
#
# All scores 0.00–1.00

INDEPENDENT_DATA = [
    # Domain A — Physical universes
    # Our universe: highly structured, long-lived, productive. Self-referential via conscious observers.
    # High coherence, persistence, generativity. Moderate recoverability (some catastrophes are final).
    {"name": "Our universe", "domain": "A", "C": 0.85, "P": 0.85, "G": 0.90, "R": 0.55, "S": 0.75,
     "SR": 0.85, "NP": 0.85, "RC": 0.90, "RD": 0.75, "OE": 0.85},
    # Cyclic universe: periodic bounce, sustained generativity across cycles.
    {"name": "Cyclic universe (bounce)", "domain": "A", "C": 0.75, "P": 0.90, "G": 0.80, "R": 0.75, "S": 0.70,
     "SR": 0.75, "NP": 0.70, "RC": 0.80, "RD": 0.65, "OE": 0.70},
    # Empty universe: almost no structure, no complexity growth.
    {"name": "Empty universe (Omega<<1)", "domain": "A", "C": 0.85, "P": 0.95, "G": 0.05, "R": 0.05, "S": 0.00,
     "SR": 0.00, "NP": 0.00, "RC": 0.00, "RD": 0.00, "OE": 0.00},
    # Collapsing universe: structures form but are crushed. Short-lived generativity.
    {"name": "Collapsing universe (Omega>>1)", "domain": "A", "C": 0.70, "P": 0.20, "G": 0.35, "R": 0.00, "S": 0.05,
     "SR": 0.25, "NP": 0.30, "RC": 0.20, "RD": 0.05, "OE": 0.10},
    # Thermal equilibrium: no gradients, no structure, no change.
    {"name": "Thermal equilibrium", "domain": "A", "C": 0.60, "P": 0.95, "G": 0.00, "R": 0.00, "S": 0.00,
     "SR": 0.00, "NP": 0.00, "RC": 0.00, "RD": 0.00, "OE": 0.00},
    # High-dark-energy: rapid expansion dilutes structure, limited complexity.
    {"name": "High-dark-energy universe", "domain": "A", "C": 0.80, "P": 0.65, "G": 0.15, "R": 0.10, "S": 0.05,
     "SR": 0.10, "NP": 0.10, "RC": 0.10, "RD": 0.05, "OE": 0.05},
    # Strong-coupling: intense interactions, rich structure but chaotic.
    {"name": "Strong-coupling universe", "domain": "A", "C": 0.35, "P": 0.25, "G": 0.55, "R": 0.10, "S": 0.10,
     "SR": 0.50, "NP": 0.50, "RC": 0.40, "RD": 0.25, "OE": 0.20},
    # Super-fertile: hypothetical maximum generativity.
    {"name": "Super-fertile universe (hypothetical)", "domain": "A", "C": 0.80, "P": 0.80, "G": 0.95, "R": 0.55, "S": 0.85,
     "SR": 0.95, "NP": 0.95, "RC": 0.95, "RD": 0.90, "OE": 0.95},
    # Domain B — Mathematical systems
    # ZFC: extremely productive foundations, high self-reference via set theory.
    {"name": "ZFC set theory", "domain": "B", "C": 0.85, "P": 0.90, "G": 0.90, "R": 0.75, "S": 0.70,
     "SR": 0.90, "NP": 0.90, "RC": 0.85, "RD": 0.80, "OE": 0.90},
    # PA: productive but less self-referential than ZFC.
    {"name": "Peano arithmetic (PA)", "domain": "B", "C": 0.90, "P": 0.90, "G": 0.80, "R": 0.80, "S": 0.55,
     "SR": 0.65, "NP": 0.75, "RC": 0.60, "RD": 0.40, "OE": 0.80},
    # FOL: complete, decidable fragments are very coherent but not very generative.
    {"name": "First-order logic (FOL)", "domain": "B", "C": 1.00, "P": 0.95, "G": 0.40, "R": 0.90, "S": 0.10,
     "SR": 0.25, "NP": 0.25, "RC": 0.20, "RD": 0.10, "OE": 0.30},
    # ETCS: categorical foundations, highly expressive.
    {"name": "Category theory (ETCS)", "domain": "B", "C": 0.80, "P": 0.85, "G": 0.85, "R": 0.70, "S": 0.80,
     "SR": 0.85, "NP": 0.85, "RC": 0.90, "RD": 0.90, "OE": 0.85},
    # Computation theory: extremely high recursive depth, very generative.
    {"name": "Computation (Turing/lambda)", "domain": "B", "C": 0.85, "P": 0.90, "G": 0.85, "R": 0.70, "S": 0.85,
     "SR": 0.85, "NP": 0.85, "RC": 0.85, "RD": 0.95, "OE": 0.85},
    # Inconsistent: explodes to prove everything — maximum generativity, zero coherence.
    {"name": "Inconsistent system", "domain": "B", "C": 0.00, "P": 0.05, "G": 1.00, "R": 0.00, "S": 0.05,
     "SR": 0.95, "NP": 1.00, "RC": 0.85, "RD": 0.60, "OE": 0.95},
    # Presburger: decidable, complete, but very limited expressiveness.
    {"name": "Presburger arithmetic", "domain": "B", "C": 1.00, "P": 0.95, "G": 0.25, "R": 0.95, "S": 0.05,
     "SR": 0.10, "NP": 0.10, "RC": 0.10, "RD": 0.05, "OE": 0.15},
    # Decidable FOL: very limited expressiveness.
    {"name": "Decidable fragment of FOL", "domain": "B", "C": 1.00, "P": 0.95, "G": 0.10, "R": 0.95, "S": 0.05,
     "SR": 0.05, "NP": 0.05, "RC": 0.05, "RD": 0.00, "OE": 0.10},
    # Domain C — Recursive substrate
    # Full substrate: balanced coherence and generativity.
    {"name": "Full 9-assumption substrate", "domain": "C", "C": 0.95, "P": 0.85, "G": 0.85, "R": 0.80, "S": 0.85,
     "SR": 0.85, "NP": 0.80, "RC": 0.80, "RD": 0.85, "OE": 0.80},
    # Original (with deadlock): bootstrap deadlock reduces viability.
    {"name": "Original substrate (IS1<->IS2)", "domain": "C", "C": 0.25, "P": 0.30, "G": 0.35, "R": 0.10, "S": 0.30,
     "SR": 0.35, "NP": 0.30, "RC": 0.25, "RD": 0.35, "OE": 0.25},
    # OC2 only: maximally minimal, no fertility.
    {"name": "OC2 only (trivial)", "domain": "C", "C": 0.65, "P": 0.35, "G": 0.00, "R": 0.10, "S": 0.00,
     "SR": 0.00, "NP": 0.00, "RC": 0.00, "RD": 0.00, "OE": 0.00},
    # Without SR1: structurally coherent but lacks self-examination.
    {"name": "Substrate without SR1", "domain": "C", "C": 0.85, "P": 0.80, "G": 0.70, "R": 0.70, "S": 0.30,
     "SR": 0.45, "NP": 0.50, "RC": 0.45, "RD": 0.30, "OE": 0.40},
    # Without EC1: still fertile per T074 result.
    {"name": "Substrate without EC1", "domain": "C", "C": 0.85, "P": 0.80, "G": 0.75, "R": 0.70, "S": 0.60,
     "SR": 0.70, "NP": 0.70, "RC": 0.70, "RD": 0.55, "OE": 0.60},
    # Without CD2: reduced self-affecting capacity.
    {"name": "Substrate without CD2", "domain": "C", "C": 0.90, "P": 0.80, "G": 0.65, "R": 0.70, "S": 0.75,
     "SR": 0.55, "NP": 0.55, "RC": 0.50, "RD": 0.55, "OE": 0.50},
    # Domain D — Dynamical manifolds
    # Lorenz: deterministic chaos, structured but limited generativity.
    {"name": "Lorenz strange attractor", "domain": "D", "C": 0.85, "P": 0.85, "G": 0.55, "R": 0.60, "S": 0.25,
     "SR": 0.30, "NP": 0.25, "RC": 0.15, "RD": 0.15, "OE": 0.20},
    # RD: pattern formation, moderate generativity, good self-organization.
    {"name": "Reaction-diffusion (Turing)", "domain": "D", "C": 0.85, "P": 0.85, "G": 0.80, "R": 0.75, "S": 0.35,
     "SR": 0.75, "NP": 0.70, "RC": 0.75, "RD": 0.25, "OE": 0.60},
    # Logistic map (r=3.8): chaotic but pattern is restricted.
    {"name": "Logistic map (r=3.8)", "domain": "D", "C": 0.75, "P": 0.70, "G": 0.60, "R": 0.25, "S": 0.10,
     "SR": 0.20, "NP": 0.25, "RC": 0.10, "RD": 0.05, "OE": 0.10},
    # Kuramoto: synchronized dynamics, low generativity.
    {"name": "Coupled oscillator (Kuramoto)", "domain": "D", "C": 0.85, "P": 0.85, "G": 0.60, "R": 0.70, "S": 0.40,
     "SR": 0.35, "NP": 0.30, "RC": 0.30, "RD": 0.20, "OE": 0.25},
    # Fixed-point: no dynamics, no generativity.
    {"name": "Fixed-point collapse", "domain": "D", "C": 0.75, "P": 0.85, "G": 0.00, "R": 0.35, "S": 0.00,
     "SR": 0.00, "NP": 0.00, "RC": 0.00, "RD": 0.00, "OE": 0.00},
    # Boolean network K=2: critical dynamics, balanced generativity.
    {"name": "Boolean network (K=2 critical)", "domain": "D", "C": 0.80, "P": 0.80, "G": 0.80, "R": 0.60, "S": 0.50,
     "SR": 0.80, "NP": 0.75, "RC": 0.80, "RD": 0.50, "OE": 0.75},
    # Game of Life: highly generative, Turing-complete.
    {"name": "Game of Life (CA)", "domain": "D", "C": 0.85, "P": 0.80, "G": 0.90, "R": 0.50, "S": 0.60,
     "SR": 0.90, "NP": 0.90, "RC": 0.90, "RD": 0.70, "OE": 0.90},
    # Unbounded divergence: no structure at all.
    {"name": "Unbounded divergence", "domain": "D", "C": 0.20, "P": 0.05, "G": 0.15, "R": 0.00, "S": 0.00,
     "SR": 0.05, "NP": 0.15, "RC": 0.05, "RD": 0.00, "OE": 0.05},
]

# ============================================================
# ANALYSIS FUNCTIONS
# ============================================================

def build_matrix(data):
    """Extract N x M data matrix from scored configs."""
    return [[c[ax] for ax in ALL_AXES] for c in data]

def transpose(m):
    return list(map(list, zip(*m)))

def mean_vec(matrix):
    n = len(matrix)
    if n == 0: return []
    m = len(matrix[0])
    return [sum(row[j] for row in matrix) / n for j in range(m)]

def vec_norm(v):
    return math.sqrt(sum(x*x for x in v))

def dot(v1, v2):
    return sum(a*b for a, b in zip(v1, v2))

def pearson_r(x, y):
    n = len(x)
    mx = sum(x)/n
    my = sum(y)/n
    dx = [xi - mx for xi in x]
    dy = [yi - my for yi in y]
    num = sum(dx[i]*dy[i] for i in range(n))
    den = math.sqrt(sum(d* d for d in dx)) * math.sqrt(sum(d*d for d in dy))
    return num/den if den != 0 else 0.0

def rank_correlation(x, y):
    """Spearman rank correlation."""
    n = len(x)
    def rank(v):
        sorted_v = sorted((val, i) for i, val in enumerate(v))
        ranks = [0]*n
        for pos, (val, idx) in enumerate(sorted_v):
            ranks[idx] = pos + 1
        return ranks
    rx = rank(x)
    ry = rank(y)
    d2 = sum((rx[i] - ry[i])**2 for i in range(n))
    return 1 - (6 * d2) / (n * (n*n - 1))

def compute_pca(data_matrix):
    """PCA via power iteration (same method as T078)."""
    N = len(data_matrix)
    M = len(data_matrix[0])
    data_T = transpose(data_matrix)
    means = [sum(col)/len(col) for col in data_T]
    centered = [[data_matrix[i][j] - means[j] for j in range(M)] for i in range(N)]

    cov = [[0.0]*M for _ in range(M)]
    for i in range(M):
        for j in range(M):
            cov[i][j] = sum(centered[k][i] * centered[k][j] for k in range(N)) / (N-1)

    def power_iteration(mat, n_iter=1000):
        M_ = len(mat)
        v = [1.0/M_] * M_
        for _ in range(n_iter):
            w = [sum(mat[i][j] * v[j] for j in range(M_)) for i in range(M_)]
            norm = math.sqrt(sum(x*x for x in w))
            v = [x / norm for x in w]
        eigenvalue = sum(v[i] * sum(mat[i][j] * v[j] for j in range(M_)) for i in range(M_))
        return eigenvalue, v

    def deflate(mat, eigenvalue, eigenvector):
        M_ = len(mat)
        result = [[mat[i][j] for j in range(M_)] for i in range(M_)]
        for i in range(M_):
            for j in range(M_):
                result[i][j] -= eigenvalue * eigenvector[i] * eigenvector[j]
        return result

    eigenvalues = []
    eigenvectors = []
    working_cov = [row[:] for row in cov]
    for k in range(M):
        ev, ev_vec = power_iteration(working_cov)
        eigenvalues.append(ev)
        eigenvectors.append(ev_vec)
        working_cov = deflate(working_cov, ev, ev_vec)

    total_var = sum(eigenvalues)
    explained = [ev / total_var * 100 for ev in eigenvalues]
    cumulative = []
    s = 0.0
    for v in explained:
        s += v
        cumulative.append(s)

    def project(mat, eigvecs, n_comp, means_v):
        proj = []
        for row in mat:
            centered_row = [row[j] - means_v[j] for j in range(len(row))]
            p = [sum(centered_row[j] * eigvecs[k][j] for j in range(len(row))) for k in range(n_comp)]
            proj.append(p)
        return proj

    n_kaiser = sum(1 for ev in eigenvalues if ev > 1.0)
    elbow = sum(1 for v in explained if v > 100/M)
    latent_3d = project(data_matrix, eigenvectors, 3, means)

    return {
        "eigenvalues": eigenvalues,
        "eigenvectors": eigenvectors,
        "explained": explained,
        "cumulative": cumulative,
        "n_kaiser": n_kaiser,
        "elbow": elbow,
        "means": means,
        "latent_3d": latent_3d,
        "project": lambda d, n: project(d, eigenvectors, n, means)
    }

print("=" * 72)
print("T084B: BLIND RELIABILITY AUDIT")
print("=" * 72)

N = len(ORIGINAL_DATA)
M = len(ALL_AXES)

# ============================================================
# 1. RAW SCORE COMPARISON
# ============================================================
print(f"\n{'='*60}")
print("1. RAW SCORE COMPARISON")
print(f"{'='*60}")

per_axis_correlations = {}
per_axis_rank_corrs = {}
per_axis_mean_abs_diff = {}
per_axis_mean_diff = {}

for ax in ALL_AXES:
    orig = [c[ax] for c in ORIGINAL_DATA]
    indep = [c[ax] for c in INDEPENDENT_DATA]
    r = pearson_r(orig, indep)
    rho = rank_correlation(orig, indep)
    abs_diff = [abs(orig[i] - indep[i]) for i in range(N)]
    diff = [orig[i] - indep[i] for i in range(N)]
    per_axis_correlations[ax] = r
    per_axis_rank_corrs[ax] = rho
    per_axis_mean_abs_diff[ax] = sum(abs_diff)/N
    per_axis_mean_diff[ax] = sum(diff)/N

print(f"\n  Per-Axis Agreement:")
print(f"  {'Axis':<6}{'Pearson r':<12}{'Spearman rho':<15}{'Mean |Diff|':<15}{'Mean Diff':<12}")
print(f"  {'-'*60}")
for ax in ALL_AXES:
    print(f"  {ax:<6}{per_axis_correlations[ax]:<12.4f}{per_axis_rank_corrs[ax]:<15.4f}"
          f"{per_axis_mean_abs_diff[ax]:<15.4f}{per_axis_mean_diff[ax]:<12.4f}")

# Overall agreement
all_orig = [c[ax] for c in ORIGINAL_DATA for ax in ALL_AXES]
all_indep = [c[ax] for c in INDEPENDENT_DATA for ax in ALL_AXES]
overall_r = pearson_r(all_orig, all_indep)
overall_rho = rank_correlation(all_orig, all_indep)
overall_mean_abs = sum(abs(all_orig[i] - all_indep[i]) for i in range(len(all_orig))) / len(all_orig)

print(f"\n  OVERALL AGREEMENT:")
print(f"    Pearson r:       {overall_r:.4f}")
print(f"    Spearman rho:    {overall_rho:.4f}")
print(f"    Mean |diff|:     {overall_mean_abs:.4f}")

# Per-system agreement
print(f"\n  Per-System Mean |Diff|:")
sys_diffs = []
for i in range(N):
    diffs = [abs(ORIGINAL_DATA[i][ax] - INDEPENDENT_DATA[i][ax]) for ax in ALL_AXES]
    mean_d = sum(diffs)/M
    sys_diffs.append((mean_d, ORIGINAL_DATA[i]["name"], ORIGINAL_DATA[i]["domain"]))
    print(f"    {ORIGINAL_DATA[i]['name']:<40} mean |diff| = {mean_d:.4f}")

sys_diffs.sort(reverse=True)
print(f"\n  Most Disagreed Systems:")
for md, name, dom in sys_diffs[:5]:
    print(f"    {name} ({dom}): mean |diff| = {md:.4f}")
print(f"\n  Least Disagreed Systems:")
for md, name, dom in sys_diffs[-5:]:
    print(f"    {name} ({dom}): mean |diff| = {md:.4f}")

# ============================================================
# 2. VIABILITY / FERTILITY CLASSIFICATION AGREEMENT
# ============================================================
print(f"\n{'='*60}")
print("2. VIABILITY / FERTILITY CLASSIFICATION")
print(f"{'='*60}")

# Use T073-derived thresholds
VIABLE_THRESH = {"C": 0.75, "P": 0.65, "G": 0.40, "R": 0.30, "S": 0.10}
FERTILE_THRESH = {"SR": 0.70, "NP": 0.70, "RC": 0.60, "RD": 0.30, "OE": 0.60}

def classify_viable(config):
    return all(config[ax] >= VIABLE_THRESH[ax] for ax in VIABILITY_AXES)

def classify_fertile(config):
    return all(config[ax] >= FERTILE_THRESH[ax] for ax in FERTILITY_AXES)

orig_viable = [classify_viable(c) for c in ORIGINAL_DATA]
indep_viable = [classify_viable(c) for c in INDEPENDENT_DATA]
orig_fertile = [classify_fertile(c) for c in ORIGINAL_DATA]
indep_fertile = [classify_fertile(c) for c in INDEPENDENT_DATA]

viable_agree = sum(1 for i in range(N) if orig_viable[i] == indep_viable[i])
fertile_agree = sum(1 for i in range(N) if orig_fertile[i] == indep_fertile[i])
region_agree = sum(1 for i in range(N) if (orig_viable[i], orig_fertile[i]) == (indep_viable[i], indep_fertile[i]))

print(f"\n  Viability classification agreement: {viable_agree}/{N} ({100*viable_agree/N:.1f}%)")
print(f"  Fertility classification agreement: {fertile_agree}/{N} ({100*fertile_agree/N:.1f}%)")
print(f"  Full region (collapse/fortress/fertile) agreement: {region_agree}/{N} ({100*region_agree/N:.1f}%)")

# Show mismatches
print(f"\n  Classification mismatches:")
for i in range(N):
    o_reg = ("viable" if orig_viable[i] else "non-viable", "fertile" if orig_fertile[i] else "non-fertile")
    i_reg = ("viable" if indep_viable[i] else "non-viable", "fertile" if indep_fertile[i] else "non-fertile")
    o_label = f"V:{1 if orig_viable[i] else 0}/F:{1 if orig_fertile[i] else 0}"
    i_label = f"V:{1 if indep_viable[i] else 0}/F:{1 if indep_fertile[i] else 0}"
    if o_label != i_label:
        print(f"    {ORIGINAL_DATA[i]['name']:<40} Original: {o_label}  Independent: {i_label}")

# ============================================================
# 3. PCA COMPARISON
# ============================================================
print(f"\n{'='*60}")
print("3. PCA STRUCTURE COMPARISON")
print(f"{'='*60}")

orig_mat = build_matrix(ORIGINAL_DATA)
indep_mat = build_matrix(INDEPENDENT_DATA)

orig_pca = compute_pca(orig_mat)
indep_pca = compute_pca(indep_mat)

print(f"\n  Original PCA:")
print(f"  {'PC':<6}{'Eigenvalue':<15}{'Explained %':<15}{'Cumulative %':<15}")
for i in range(M):
    print(f"  PC{i+1:<4}{orig_pca['eigenvalues'][i]:<15.4f}{orig_pca['explained'][i]:<15.2f}{orig_pca['cumulative'][i]:<15.2f}")
print(f"  Kaiser criterion: {orig_pca['n_kaiser']}, Elbow: {orig_pca['elbow']}")

print(f"\n  Independent PCA:")
print(f"  {'PC':<6}{'Eigenvalue':<15}{'Explained %':<15}{'Cumulative %':<15}")
for i in range(M):
    print(f"  PC{i+1:<4}{indep_pca['eigenvalues'][i]:<15.4f}{indep_pca['explained'][i]:<15.2f}{indep_pca['cumulative'][i]:<15.2f}")
print(f"  Kaiser criterion: {indep_pca['n_kaiser']}, Elbow: {indep_pca['elbow']}")

# Compare PC1 % and PC loadings
pc1_diff = abs(orig_pca['explained'][0] - indep_pca['explained'][0])
print(f"\n  PC1% Original: {orig_pca['explained'][0]:.1f}%  Independent: {indep_pca['explained'][0]:.1f}%  |diff| = {pc1_diff:.1f}%")
pc2_diff = abs(orig_pca['explained'][1] - indep_pca['explained'][1])
print(f"  PC2% Original: {orig_pca['explained'][1]:.1f}%  Independent: {indep_pca['explained'][1]:.1f}%  |diff| = {pc2_diff:.1f}%")

# Compare loading patterns
print(f"\n  PC1 Loading Comparison:")
print(f"  {'Axis':<6}{'Original Loading':<18}{'Independent Loading':<20}{'Sign Agree?':<15}")
loading_agreements = 0
for j in range(M):
    o_loading = orig_pca['eigenvectors'][0][j]
    i_loading = indep_pca['eigenvectors'][0][j]
    sign_agree = (o_loading > 0) == (i_loading > 0)
    if sign_agree: loading_agreements += 1
    print(f"  {ALL_AXES[j]:<6}{o_loading:<18.4f}{i_loading:<20.4f}{'YES' if sign_agree else 'NO':<15}")
print(f"  PC1 sign agreement: {loading_agreements}/{M}")

# Compare PC2 loadings
print(f"\n  PC2 Loading Comparison:")
pc2_agree = 0
for j in range(M):
    o_loading = orig_pca['eigenvectors'][1][j]
    i_loading = indep_pca['eigenvectors'][1][j]
    sign_agree = (o_loading > 0) == (i_loading > 0)
    if sign_agree: pc2_agree += 1
    print(f"  {ALL_AXES[j]:<6}{o_loading:<18.4f}{i_loading:<20.4f}{'YES' if sign_agree else 'NO':<15}")
print(f"  PC2 sign agreement: {pc2_agree}/{M}")

# Interpretive labels comparison
print(f"\n  PC1 Interpretation:")
for label, pca in [("Original", orig_pca), ("Independent", indep_pca)]:
    loadings = [(ALL_AXES[j], pca['eigenvectors'][0][j]) for j in range(M)]
    loadings.sort(key=lambda x: abs(x[1]), reverse=True)
    strong = [l for l in loadings if abs(l[1]) > 0.3]
    pos = [l for l in strong if l[1] > 0]
    neg = [l for l in strong if l[1] < 0]
    print(f"    {label}:")
    if pos: print(f"      Positive: {', '.join(f'{a}(+{v:.2f})' for a,v in pos)}")
    if neg: print(f"      Negative: {', '.join(f'{a}({v:.2f})' for a,v in neg)}")

print(f"\n  PC2 Interpretation:")
for label, pca in [("Original", orig_pca), ("Independent", indep_pca)]:
    loadings = [(ALL_AXES[j], pca['eigenvectors'][1][j]) for j in range(M)]
    loadings.sort(key=lambda x: abs(x[1]), reverse=True)
    strong = [l for l in loadings if abs(l[1]) > 0.3]
    pos = [l for l in strong if l[1] > 0]
    neg = [l for l in strong if l[1] < 0]
    print(f"    {label}:")
    if pos: print(f"      Positive: {', '.join(f'{a}(+{v:.2f})' for a,v in pos)}")
    if neg: print(f"      Negative: {', '.join(f'{a}({v:.2f})' for a,v in neg)}")

# Projection comparison: check if fertile systems cluster similarly
print(f"\n{'='*60}")
print("4. FERTILE CORRIDOR COMPARISON")
print(f"{'='*60}")

orig_latent = orig_pca['latent_3d']
indep_latent = indep_pca['latent_3d']

def compute_fertile_cluster(latent, data, label):
    fertile_idx = [i for i, c in enumerate(data) if classify_viable(c) and classify_fertile(c)]
    if len(fertile_idx) < 2:
        print(f"  {label}: {len(fertile_idx)} fertile systems — insufficient for cluster analysis")
        return None
    coords = [latent[i] for i in fertile_idx]
    centroid = [sum(c[k] for c in coords)/len(coords) for k in range(3)]
    spread = math.sqrt(sum(sum((c[k]-centroid[k])**2 for k in range(3)) for c in coords) / len(coords))
    max_dev = max(math.sqrt(sum((c[k]-centroid[k])**2 for k in range(3))) for c in coords)
    return {
        "n_fertile": len(fertile_idx),
        "centroid": centroid,
        "spread": spread,
        "max_dev": max_dev,
        "fertile_names": [data[i]["name"] for i in fertile_idx]
    }

orig_fc = compute_fertile_cluster(orig_latent, ORIGINAL_DATA, "Original")
indep_fc = compute_fertile_cluster(indep_latent, INDEPENDENT_DATA, "Independent")

if orig_fc:
    print(f"\n  Original fertile corridor:")
    print(f"    N fertile: {orig_fc['n_fertile']}")
    print(f"    Spread: {orig_fc['spread']:.4f}")
    print(f"    Max deviation: {orig_fc['max_dev']:.4f}")
    print(f"    Systems: {', '.join(orig_fc['fertile_names'])}")
if indep_fc:
    print(f"\n  Independent fertile corridor:")
    print(f"    N fertile: {indep_fc['n_fertile']}")
    print(f"    Spread: {indep_fc['spread']:.4f}")
    print(f"    Max deviation: {indep_fc['max_dev']:.4f}")
    print(f"    Systems: {', '.join(indep_fc['fertile_names'])}")

# Intersection of fertile sets
if orig_fc and indep_fc:
    orig_set = set(orig_fc['fertile_names'])
    indep_set = set(indep_fc['fertile_names'])
    intersection = orig_set & indep_set
    only_orig = orig_set - indep_set
    only_indep = indep_set - orig_set
    print(f"\n  Fertile set comparison:")
    print(f"    Original fertile: {len(orig_set)}, Independent fertile: {len(indep_set)}")
    print(f"    Intersection: {len(intersection)} ({', '.join(sorted(intersection))})")
    if only_orig:
        print(f"    Only in original: {', '.join(sorted(only_orig))}")
    if only_indep:
        print(f"    Only in independent: {', '.join(sorted(only_indep))}")

# ============================================================
# 5. CORRIDOR WIDTH COMPARISON (replicating T076)
# ============================================================
print(f"\n{'='*60}")
print("5. STABILITY-FERTILITY RELATIONSHIP COMPARISON")
print(f"{'='*60}")

def compute_stability(config):
    return (config["C"] + config["P"] + config["R"]) / 3

def compute_fertility_score(config):
    return sum(config[ax] for ax in FERTILITY_AXES) / 5

V_THRESH = {"C": 0.75, "P": 0.65, "G": 0.40, "R": 0.30, "S": 0.10}

for label, data in [("Original", ORIGINAL_DATA), ("Independent", INDEPENDENT_DATA)]:
    viable = [c for c in data if all(c[ax] >= V_THRESH[ax] for ax in VIABILITY_AXES)]
    fertile = [c for c in viable if classify_fertile(c)]
    fortress = [c for c in viable if not classify_fertile(c)]

    if len(fertile) >= 2:
        stabilities = [compute_stability(c) for c in fertile]
        fertility_scores = [compute_fertility_score(c) for c in fertile]
        r_stab_fert = pearson_r(stabilities, fertility_scores)
        width = max(stabilities) - min(stabilities)
        print(f"\n  {label}:")
        print(f"    N viable: {len(viable)}, N fertile: {len(fertile)}, N fortress: {len(fortress)}")
        print(f"    Fertile stability range: {min(stabilities):.3f}–{max(stabilities):.3f} (width = {width:.3f})")
        print(f"    Fertile-fertility correlation: r = {r_stab_fert:.4f}")
        # Mean stability of fertile vs fortress
        if fortress:
            fert_mean_s = sum(stabilities)/len(stabilities)
            fort_s = [compute_stability(c) for c in fortress]
            fort_mean_s = sum(fort_s)/len(fort_s)
            print(f"    Mean stability: fertile = {fert_mean_s:.4f}, fortress = {fort_mean_s:.4f}")

# ============================================================
# 6. SUMMARY
# ============================================================
print(f"\n{'='*60}")
print("6. RELIABILITY SUMMARY")
print(f"{'='*60}")

print(f"""
  SCORE RELIABILITY:
    Overall Pearson r:          {overall_r:.3f}
    Overall Spearman rho:       {overall_rho:.3f}
    Overall mean |diff|:        {overall_mean_abs:.3f}
    Best axis (highest r):      {max(per_axis_correlations, key=per_axis_correlations.get)}
                                  (r = {max(per_axis_correlations.values()):.4f})
    Worst axis (lowest r):      {min(per_axis_correlations, key=per_axis_correlations.get)}
                                  (r = {min(per_axis_correlations.values()):.4f})

  CLASSIFICATION RELIABILITY:
    Viability agreement:        {viable_agree}/{N} ({100*viable_agree/N:.1f}%)
    Fertility agreement:        {fertile_agree}/{N} ({100*fertile_agree/N:.1f}%)
    Full region agreement:      {region_agree}/{N} ({100*region_agree/N:.1f}%)

  PCA STRUCTURE:
    Original PC1%:              {orig_pca['explained'][0]:.1f}%
    Independent PC1%:           {indep_pca['explained'][0]:.1f}%
    PC1 |diff|:                 {pc1_diff:.1f}% points
    Original Kaiser/Elbow:      {orig_pca['n_kaiser']}/{orig_pca['elbow']}
    Independent Kaiser/Elbow:   {indep_pca['n_kaiser']}/{indep_pca['elbow']}
    PC1 sign agreement:         {loading_agreements}/{M}
    PC2 sign agreement:         {pc2_agree}/{M}

  CRITICAL FAILURE THRESHOLDS:
    PASS if overall r > 0.80:     {'PASS' if overall_r > 0.80 else 'FAIL'} ({overall_r:.3f})
    PASS if PC1% |diff| < 10:     {'PASS' if pc1_diff < 10 else 'FAIL'} ({pc1_diff:.1f})
    PASS if viability agree > 80%: {'PASS' if viable_agree/N > 0.80 else 'FAIL'} ({100*viable_agree/N:.1f}%)
    PASS if fertility agree > 80%: {'PASS' if fertile_agree/N > 0.80 else 'FAIL'} ({100*fertile_agree/N:.1f}%)
""")
