#!/usr/bin/env python3
"""
T082: Structural Realization Audit
===================================
Question: What minimal additional principle, when combined with MC2+MC3+MC4,
causes the substrate, mechanism classes, fertile corridor, and meta-space
geometry to reappear?

Design:
  Phase 0 — Baseline: replicate T081 with corrected MC4 grouping
  Phase 1 — SP: Add Structural Persistence constraint
  Phase 2 — MC5: Add Recoverable Perturbation constraint
  Phase 3 — MC1: Add Information Preservation constraint
  Phase 4 — Higher thresholds: MC2/MC3/MC4 >= 0.7 instead of 0.5
  Phase 5 — Interaction: MC2 x MC3 x MC4 product term
  Phase 6 — SP + MC5: Best combination
  Phase 7 — Ablation: remove each added principle

For each phase, measure:
  - Assumption emergence (9 substrate assumptions, delta >= 0.2)
  - Mechanism emergence (8 mechanism classes, delta >= 0.15)
  - Viability basin (viable fraction in "all" vs "none" group)
  - Fertile corridor (finite width fertility band across stability)
  - Meta-space PCA structure (PC1 dominance near 75%)
  - Ablation sensitivity of new principle
"""

import csv, json, math, itertools, random
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np

OUT = Path("/home/student/sgp_core_v2/sfh_sgp_ood_outputs")
random.seed(42)
np.random.seed(42)


# ============================================================
# SYSTEM GENERATION (same as T081)
# ============================================================

class GeneratedSystem:
    def __init__(self, params):
        self.params = params
        self.base_n = params.get("base_n_states", 4)
        self.determinism = params.get("determinism", 0.7)
        self.connectivity = params.get("connectivity", 0.5)
        self.novelty_drive = params.get("novelty_drive", 0.3)
        self.boundary_strength = params.get("boundary_strength", 0.7)
        self.self_model_level = params.get("self_model_level", 0)
        self.sm_influence = params.get("self_model_influence", 0.0)
        self.states = list(range(self.base_n))
        self.n_actual = self.base_n
        self.T = self._build_transition_matrix()
        self.history = []
        self.visit_counts = Counter()
        self.state_ages = {}
        self.fixed_point_reached = False

    def _build_transition_matrix(self):
        n = self.base_n
        T = np.zeros((n, n))
        mask = np.random.random((n, n)) < self.connectivity
        np.fill_diagonal(mask, True)
        raw = np.random.random((n, n)) * mask
        if self.determinism > 0.8:
            for i in range(n):
                if np.random.random() < self.determinism:
                    raw[i] = 0
                    raw[i, np.random.randint(n)] = 1
        row_sums = raw.sum(axis=1)
        row_sums[row_sums == 0] = 1
        T = raw / row_sums[:, np.newaxis]
        return T

    def step(self):
        if not self.history:
            self.history.append(0)
            self.visit_counts[0] += 1
            self.state_ages[0] = 0
            return 0
        current = self.history[-1]
        if self.self_model_level > 0 and np.random.random() < self.sm_influence:
            current = self._self_model_modulated(current)
        if np.random.random() < self.novelty_drive:
            new_state = self._generate_new_state()
            if new_state is not None:
                self.history.append(new_state)
                self.visit_counts[new_state] += 1
                return new_state
        next_state = np.random.choice(self.n_actual, p=self.T[current])
        self.history.append(next_state)
        self.visit_counts[next_state] += 1
        return next_state

    def _self_model_modulated(self, current):
        if self.self_model_level == 1:
            recent = self.history[-min(3, len(self.history)):]
            if len(set(recent)) == 1:
                return random.choice(range(self.n_actual))
        elif self.self_model_level == 2:
            if self.visit_counts[current] > max(self.n_actual, 3):
                candidates = [s for s in range(self.n_actual) if self.visit_counts[s] < self.visit_counts[current]]
                if candidates:
                    return random.choice(candidates)
        elif self.self_model_level >= 3:
            if self._detect_cycle():
                candidates = [s for s in range(self.n_actual) if self.visit_counts.get(s, 0) < 2]
                if candidates:
                    return random.choice(candidates)
        return current

    def _detect_cycle(self):
        if len(self.history) < 6:
            return False
        recent = self.history[-6:]
        return len(recent) == 6 and len(set(recent)) <= 3

    def _generate_new_state(self):
        if self.boundary_strength > 0.9:
            return None
        expansion_ok = np.random.random() < (1.0 - self.boundary_strength) * 0.3
        if not expansion_ok:
            return None
        new_id = self.n_actual
        self.n_actual += 1
        self.states.append(new_id)
        old_T = self.T
        new_T = np.zeros((self.n_actual, self.n_actual))
        new_T[:old_T.shape[0], :old_T.shape[0]] = old_T
        for i in range(self.n_actual):
            conn = np.random.random(self.n_actual) < self.connectivity
            conn[i] = True
            raw = np.random.random(self.n_actual) * conn
            if raw.sum() == 0:
                raw[i] = 1
            new_T[i] = raw / raw.sum()
        self.T = new_T
        self.visit_counts[new_id] = 0
        self.state_ages[new_id] = 0
        return new_id

    def run(self, steps=200):
        for _ in range(steps):
            self.step()
        return self._compute_metrics()

    def _compute_metrics(self):
        h = self.history
        n = len(h)
        if n == 0:
            return defaultdict(float)
        unique_ratio = len(set(h)) / max(1, self.n_actual)
        cycle_length = self._find_cycle_length()
        convergence = 1.0 if cycle_length <= 1 else (1.0 / cycle_length if cycle_length > 0 else 0)
        entropy = self._compute_entropy()
        self_correlation = self._compute_self_correlation()
        trans_div = self._compute_transition_diversity()
        sm_ratio = self.self_model_level / 3.0
        sm_impact = self.sm_influence
        return {
            "unique_ratio": unique_ratio,
            "cycle_length": cycle_length,
            "convergence": convergence,
            "entropy": entropy,
            "self_correlation": self_correlation,
            "transition_diversity": trans_div,
            "sm_ratio": sm_ratio,
            "sm_impact": sm_impact,
            "n_states_actual": self.n_actual,
            "total_steps": n,
            "state_expansions": self.n_actual - self.base_n,
        }

    def _find_cycle_length(self):
        h = self.history
        if len(h) < 4:
            return len(set(h))
        recent = h[-20:]
        seen = {}
        for i, s in enumerate(recent):
            if s in seen:
                return i - seen[s]
            seen[s] = i
        return len(set(h))

    def _compute_entropy(self):
        if not self.history:
            return 0
        counts = Counter(self.history)
        total = len(self.history)
        ent = 0
        for c in counts.values():
            p = c / total
            if p > 0:
                ent -= p * math.log2(p)
        return ent / max(1, math.log2(len(counts)))

    def _compute_self_correlation(self):
        h = self.history
        if len(h) < 4:
            return 0
        lag = min(3, len(h) // 2)
        matches = sum(1 for i in range(len(h) - lag) if h[i] == h[i + lag])
        return matches / (len(h) - lag)

    def _compute_transition_diversity(self):
        trans = list(zip(self.history[:-1], self.history[1:]))
        if not trans:
            return 0
        return len(set(trans)) / max(1, len(trans))


# ============================================================
# CONSTRAINT SCORING (MCs + candidate additions)
# ============================================================

def score_mc2(metrics):
    """Productive Transformation."""
    uniq = metrics.get("unique_ratio", 0)
    expan = metrics.get("state_expansions", 0)
    entropy = metrics.get("entropy", 0)
    trans_div = metrics.get("transition_diversity", 0)
    score = (uniq * 0.3 +
             min(1.0, expan / 5) * 0.25 +
             entropy * 0.25 +
             trans_div * 0.2)
    return min(1.0, score)


def score_mc3(metrics):
    """Constraint Balance."""
    cycle = metrics.get("cycle_length", 0)
    convergence = metrics.get("convergence", 0)
    sm = metrics.get("sm_ratio", 0)
    sc = metrics.get("self_correlation", 0)
    if cycle == 0:
        freedom = 0.0
    elif cycle == 1:
        freedom = 0.0
    elif cycle <= 3:
        freedom = 0.3
    elif cycle <= 6:
        freedom = 0.7
    elif cycle <= 10:
        freedom = 0.5
    else:
        freedom = 0.2
    rigidity = convergence
    balance = 1.0 - abs(freedom - rigidity)
    balance_weighted = balance * 0.5 + (1.0 - abs(convergence - 0.5)) * 0.3 + sm * 0.2
    return min(1.0, balance_weighted)


def score_mc4(metrics):
    """Recursive Accessibility."""
    sm_r = metrics.get("sm_ratio", 0)
    sm_i = metrics.get("sm_impact", 0)
    sc = metrics.get("self_correlation", 0)
    score = sm_r * 0.4 + sm_i * 0.3 + sc * 0.3
    return min(1.0, score)


def score_mc5(metrics):
    """Recoverable Perturbation — ability to absorb shocks and return to baseline."""
    convergence = metrics.get("convergence", 0)
    cycle = metrics.get("cycle_length", 0)
    sc = metrics.get("self_correlation", 0)
    trans_div = metrics.get("transition_diversity", 0)
    if cycle == 0:
        recovery = 0.0
    elif cycle <= 2:
        recovery = 1.0
    elif cycle <= 5:
        recovery = 0.7
    elif cycle <= 10:
        recovery = 0.3
    else:
        recovery = 0.1
    score = recovery * 0.4 + convergence * 0.3 + sc * 0.2 + (1.0 - trans_div) * 0.1
    return min(1.0, score)


def score_mc1(metrics):
    """Information Preservation — info is not lost through transitions."""
    uniq = metrics.get("unique_ratio", 0)
    entropy = metrics.get("entropy", 0)
    sc = metrics.get("self_correlation", 0)
    cycle = metrics.get("cycle_length", 0)
    determinism = (1.0 if cycle <= 3 else 0.5 if cycle <= 8 else 0.2)
    score = uniq * 0.3 + entropy * 0.3 + sc * 0.2 + determinism * 0.2
    return min(1.0, score)


def score_sp(metrics):
    """Structural Persistence — counterpressure to novelty drive.
    System revisits states, maintaining bounded structure."""
    uniq = metrics.get("unique_ratio", 0)
    sc = metrics.get("self_correlation", 0)
    cycle = metrics.get("cycle_length", 0)
    convergence = metrics.get("convergence", 0)
    # Prefer moderate uniqueness (not too many new states), high self-correlation,
    # short cycles (structure), moderate convergence
    uniq_score = 1.0 - abs(uniq - 0.5) * 1.5
    if cycle == 0:
        cycle_score = 0.0
    elif cycle <= 3:
        cycle_score = 0.8
    elif cycle <= 6:
        cycle_score = 1.0
    elif cycle <= 10:
        cycle_score = 0.5
    else:
        cycle_score = 0.2
    score = uniq_score * 0.3 + sc * 0.3 + cycle_score * 0.2 + (1.0 - abs(convergence - 0.6)) * 0.2
    return min(1.0, max(0.0, score))


# ============================================================
# SUBSTRATE ASSUMPTION MEASUREMENT (same as T081)
# ============================================================

def measure_oc2(metrics, system):
    if system.n_actual < 2:
        return 0.0
    trans_sets = [set(np.where(row > 0.01)[0].tolist()) for row in system.T]
    unique_trans = len(set(tuple(sorted(t)) for t in trans_sets))
    return min(1.0, unique_trans / max(1, system.n_actual))

def measure_oc1(metrics, system):
    h = system.history
    if len(h) < 10:
        return 0.0
    recent = h[-20:]
    recurrence = len(set(recent)) / max(1, len(recent))
    return 1.0 - recurrence

def measure_cd1(metrics, system):
    if len(system.history) < 5:
        return 0.0
    raw_determinism = system.determinism
    trans = list(zip(system.history[:-1], system.history[1:]))
    if not trans:
        return 0.0
    state_outcomes = defaultdict(list)
    for s, ns in trans:
        state_outcomes[s].append(ns)
    consistency = 0
    for s, outs in state_outcomes.items():
        if len(outs) >= 2:
            most_common = Counter(outs).most_common(1)[0][1]
            consistency += most_common / len(outs)
    consistency /= max(1, len(state_outcomes))
    return raw_determinism * 0.4 + consistency * 0.6

def measure_ic1(metrics, system):
    if system.n_actual < 2:
        return 0.0
    trans = list(zip(system.history[:-1], system.history[1:]))
    if not trans:
        return 0.0
    state_outcomes = defaultdict(set)
    for s, ns in trans:
        state_outcomes[s].add(ns)
    future_divergence = 0
    for s, outcomes in state_outcomes.items():
        future_divergence += len(outcomes) / max(1, system.n_actual)
    future_divergence /= max(1, len(state_outcomes))
    return min(1.0, future_divergence * 1.5)

def measure_is1(metrics, system):
    h = system.history
    if len(h) < 10:
        return 0.0
    blocks = [h[i:i+5] for i in range(0, len(h)-4, 5)]
    if len(blocks) < 2:
        return 0.0
    changes = sum(1 for i in range(1, len(blocks)) if set(blocks[i]) != set(blocks[i-1]))
    return min(1.0, changes / max(1, len(blocks) - 1))

def measure_is2(metrics, system):
    h = system.history
    if len(h) < 5:
        return 0.0
    recent = h[-10:]
    if len(set(recent)) <= 2:
        return 1.0
    return min(0.5, 5.0 / len(set(recent)))

def measure_cd2(metrics, system):
    sm = system.self_model_level
    sm_i = system.sm_influence
    sc = metrics.get("self_correlation", 0)
    cycle = metrics.get("cycle_length", 0)
    score = (min(1.0, sm / 2) * 0.4 + sm_i * 0.3 +
             min(1.0, sc * 1.5) * 0.15 +
             (1.0 if cycle > 2 else 0.0) * 0.15)
    return min(1.0, score)

def measure_ec1(metrics, system):
    sm = system.self_model_level
    sm_i = system.sm_influence
    sc = metrics.get("self_correlation", 0)
    return min(1.0, (sm / 3) * 0.5 + sm_i * 0.3 + sc * 0.2)

def measure_sr1(metrics, system):
    sm = system.self_model_level
    sm_i = system.sm_influence
    cycle = metrics.get("cycle_length", 0)
    sc = metrics.get("self_correlation", 0)
    if sm < 2:
        return sm * 0.3
    return min(1.0, (sm / 3) * 0.3 + sm_i * 0.3 + (1.0 if cycle > 1 else 0.0) * 0.2 + sc * 0.2)


# ============================================================
# VIABILITY & FERTILITY METRICS
# ============================================================

def compute_coherence(metrics, system, em):
    det = system.determinism
    sc = metrics.get("self_correlation", 0)
    oc2 = em.get("OC2", 0)
    return min(1.0, (det * 0.3 + sc * 0.3 + oc2 * 0.4))

def compute_persistence(metrics, system, em):
    conv = metrics.get("convergence", 0)
    cycle = metrics.get("cycle_length", 0)
    oc1 = em.get("OC1", 0)
    stab = (1.0 if cycle <= 5 else 0.5 if cycle <= 10 else 0.2) * 0.4
    return min(1.0, stab + conv * 0.3 + oc1 * 0.3)

def compute_generativity(metrics, system, em):
    mc2 = score_mc2(metrics)
    expan = metrics.get("state_expansions", 0)
    trans_div = metrics.get("transition_diversity", 0)
    ic1 = em.get("IC1", 0)
    return min(1.0, mc2 * 0.4 + min(1.0, expan / 3) * 0.2 + trans_div * 0.2 + ic1 * 0.2)

def compute_recoverability(metrics, system, em):
    conv = metrics.get("convergence", 0)
    cycle = metrics.get("cycle_length", 0)
    sc = metrics.get("self_correlation", 0)
    cd1 = em.get("CD1", 0)
    recover = (1.0 if 2 <= cycle <= 6 else 0.5 if cycle > 0 else 0.0) * 0.4
    return min(1.0, recover + conv * 0.2 + sc * 0.2 + cd1 * 0.2)

def compute_self_modeling(metrics, system, em):
    ec1 = em.get("EC1", 0)
    sr1 = em.get("SR1", 0)
    cd2 = em.get("CD2", 0)
    return min(1.0, ec1 * 0.4 + sr1 * 0.3 + cd2 * 0.3)

def compute_novelty_production(metrics, system, em):
    uniq = metrics.get("unique_ratio", 0)
    expan = metrics.get("state_expansions", 0)
    entropy = metrics.get("entropy", 0)
    return min(1.0, uniq * 0.4 + min(1.0, expan / 4) * 0.3 + entropy * 0.3)

def compute_structural_richness(metrics, system, em):
    trans_div = metrics.get("transition_diversity", 0)
    n = system.n_actual
    is1 = em.get("IS1", 0)
    return min(1.0, trans_div * 0.4 + min(1.0, n / 8) * 0.3 + is1 * 0.3)

def compute_recombination(metrics, system, em):
    sc = metrics.get("self_correlation", 0)
    cd2 = em.get("CD2", 0)
    cycle = metrics.get("cycle_length", 0)
    trans_div = metrics.get("transition_diversity", 0)
    return min(1.0, sc * 0.3 + cd2 * 0.3 + (1.0 if cycle >= 3 else cycle / 3) * 0.2 + trans_div * 0.2)

def compute_recursive_depth(metrics, system, em):
    sm = system.self_model_level
    sr1 = em.get("SR1", 0)
    ec1 = em.get("EC1", 0)
    cd2 = em.get("CD2", 0)
    return min(1.0, (sm / 3) * 0.4 + sr1 * 0.3 + ec1 * 0.15 + cd2 * 0.15)

def compute_open_endedness(metrics, system, em):
    mc2 = score_mc2(metrics)
    expan = metrics.get("state_expansions", 0)
    unique = metrics.get("unique_ratio", 0)
    is1 = em.get("IS1", 0)
    return min(1.0, mc2 * 0.3 + min(1.0, expan / 3) * 0.3 + unique * 0.2 + is1 * 0.2)


# ============================================================
# MECHANISM DETECTION (same as T081)
# ============================================================

def detect_mechanisms(metrics, system):
    mechanisms = {}
    h = system.history
    sm = system.self_model_level
    n = system.n_actual
    cycle = metrics.get("cycle_length", 0)
    conv = metrics.get("convergence", 0)
    det = system.determinism
    sm_i = system.sm_influence
    sc = metrics.get("self_correlation", 0)
    uniq = metrics.get("unique_ratio", 0)
    entropy = metrics.get("entropy", 0)

    m01 = 1.0 if (sm < 2 and n >= 4) else (0.5 if sm < 2 else 0.0)
    m02 = 1.0 if (cycle == 1 and conv > 0.8) else (0.5 if cycle <= 2 else 0.0)
    m03 = det * 0.7 + (1.0 if system.novelty_drive < 0.2 else 0.0) * 0.3
    m04 = min(1.0, sm_i * 0.5 + sc * 0.5)
    m05 = max(0.0, 1.0 - uniq * 0.5 - entropy * 0.5)
    m06 = 1.0 if (conv > 0.9 and cycle <= 2 and sc > 0.8) else (0.5 if cycle <= 3 else 0.0)
    if len(h) < 10:
        m07 = 0.0
    else:
        recent = h[-10:]
        m07 = 0.8 if len(set(recent)) == len(recent) else 0.0
    m08 = 1.0 if (sm >= 2 and cycle > 2 and sc > 0.6) else (0.5 if cycle > 2 else 0.0)

    return {"M01": m01, "M02": m02, "M03": m03, "M04": m04,
            "M05": m05, "M06": m06, "M07": m07, "M08": m08}


# ============================================================
# CONSTELLATION ENCODING — each "phase" defines which constraints
# define the "all-satisfied" and "none-satisfied" groups
# ============================================================

PHASE_DEFS = [
    {
        "name": "baseline",
        "label": "Baseline (MC2+MC3+MC4, threshold 0.5)",
        "constraints": [
            ("MC2", lambda r: r["mc2"] >= 0.5),
            ("MC3", lambda r: r["mc3"] >= 0.5),
            ("MC4", lambda r: r["mc4"] >= 0.5),
        ],
    },
    {
        "name": "sp",
        "label": "SP (Structural Persistence) added",
        "constraints": [
            ("MC2", lambda r: r["mc2"] >= 0.5),
            ("MC3", lambda r: r["mc3"] >= 0.5),
            ("MC4", lambda r: r["mc4"] >= 0.5),
            ("SP", lambda r: r["sp"] >= 0.5),
        ],
    },
    {
        "name": "mc5",
        "label": "MC5 (Recoverable Perturbation) added",
        "constraints": [
            ("MC2", lambda r: r["mc2"] >= 0.5),
            ("MC3", lambda r: r["mc3"] >= 0.5),
            ("MC4", lambda r: r["mc4"] >= 0.5),
            ("MC5", lambda r: r["mc5"] >= 0.5),
        ],
    },
    {
        "name": "mc1",
        "label": "MC1 (Information Preservation) added",
        "constraints": [
            ("MC2", lambda r: r["mc2"] >= 0.5),
            ("MC3", lambda r: r["mc3"] >= 0.5),
            ("MC4", lambda r: r["mc4"] >= 0.5),
            ("MC1", lambda r: r["mc1"] >= 0.5),
        ],
    },
    {
        "name": "higher_threshold",
        "label": "Higher thresholds (MC2/MC3/MC4 >= 0.7)",
        "constraints": [
            ("MC2_hi", lambda r: r["mc2"] >= 0.7),
            ("MC3_hi", lambda r: r["mc3"] >= 0.7),
            ("MC4_hi", lambda r: r["mc4"] >= 0.7),
        ],
    },
    {
        "name": "interaction",
        "label": "Interaction (MC2 x MC3 x MC4 >= 0.216)",
        "constraints": [
            ("MC2x3x4", lambda r: (r["mc2"] * r["mc3"] * r["mc4"]) >= 0.216),
        ],
    },
    {
        "name": "sp_mc5",
        "label": "SP + MC5 combined",
        "constraints": [
            ("MC2", lambda r: r["mc2"] >= 0.5),
            ("MC3", lambda r: r["mc3"] >= 0.5),
            ("MC4", lambda r: r["mc4"] >= 0.5),
            ("SP", lambda r: r["sp"] >= 0.5),
            ("MC5", lambda r: r["mc5"] >= 0.5),
        ],
    },
]


# ============================================================
# ASSAY: compute all metrics for one configuration
# ============================================================

ASS_IDS = ["OC2", "OC1", "CD1", "IC1", "IS1", "IS2", "CD2", "EC1", "SR1"]
MECH_IDS = ["M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08"]


def assay_system(params):
    system = GeneratedSystem(params)
    metrics = system.run(200)

    mc2 = score_mc2(metrics)
    mc3 = score_mc3(metrics)
    mc4 = score_mc4(metrics)
    mc5 = score_mc5(metrics)
    mc1 = score_mc1(metrics)
    sp = score_sp(metrics)

    em = {
        "OC2": measure_oc2(metrics, system),
        "OC1": measure_oc1(metrics, system),
        "CD1": measure_cd1(metrics, system),
        "IC1": measure_ic1(metrics, system),
        "IS1": measure_is1(metrics, system),
        "IS2": measure_is2(metrics, system),
        "CD2": measure_cd2(metrics, system),
        "EC1": measure_ec1(metrics, system),
        "SR1": measure_sr1(metrics, system),
    }
    mechs = detect_mechanisms(metrics, system)
    viability = {
        "C": compute_coherence(metrics, system, em),
        "P": compute_persistence(metrics, system, em),
        "G": compute_generativity(metrics, system, em),
        "R": compute_recoverability(metrics, system, em),
        "S": compute_self_modeling(metrics, system, em),
    }
    fertility = {
        "SR": compute_structural_richness(metrics, system, em),
        "NP": compute_novelty_production(metrics, system, em),
        "RC": compute_recombination(metrics, system, em),
        "RD": compute_recursive_depth(metrics, system, em),
        "OE": compute_open_endedness(metrics, system, em),
    }
    viability_threshold = (
        viability["C"] >= 0.75 and
        viability["P"] >= 0.65 and
        viability["G"] >= 0.40
    )
    fertile_signature = (
        viability_threshold and
        fertility["SR"] >= 0.5 and
        fertility["NP"] >= 0.5 and
        fertility["RC"] >= 0.5
    )
    stability = (viability["C"] + viability["P"] + viability["R"]) / 3
    fert_index = (fertility["SR"] + fertility["NP"] + fertility["RC"] +
                  fertility["RD"] + fertility["OE"]) / 5

    return {
        "params": params,
        "metrics": metrics,
        "mc2": mc2, "mc3": mc3, "mc4": mc4,
        "mc5": mc5, "mc1": mc1, "sp": sp,
        "em": em, "mechs": mechs,
        "viability": viability, "fertility": fertility,
        "viable": viability_threshold,
        "fertile": fertile_signature,
        "stability": stability,
        "fertility_index": fert_index,
    }


# ============================================================
# PHASE ANALYSIS FUNCTIONS
# ============================================================

def run_assay(results, constraints, label):
    """Given a constraint set, compute grouped assays."""
    def sat_all(r):
        return all(pred(r) for _, pred in constraints)
    def sat_none(r):
        return all(not pred(r) for _, pred in constraints)

    all_sat = [r for r in results if sat_all(r)]
    none_sat = [r for r in results if sat_none(r)]
    some_sat = [r for r in results if r not in all_sat and r not in none_sat]

    # --- Assumption emergence ---
    ass_rows = []
    emergent = []
    for aid in ASS_IDS:
        all_m = np.mean([r["em"][aid] for r in all_sat]) if all_sat else 0
        none_m = np.mean([r["em"][aid] for r in none_sat]) if none_sat else 0
        delta = all_m - none_m
        emerged = delta >= 0.2
        if emerged:
            emergent.append(aid)
        ass_rows.append({"assumption": aid, "all_mean": round(all_m, 3),
                         "none_mean": round(none_m, 3), "delta": round(delta, 3),
                         "emerged": emerged})
    em_pct = len(emergent) / len(ASS_IDS) * 100

    # --- Mechanism emergence ---
    mech_rows = []
    emergent_m = []
    for mid in MECH_IDS:
        all_m = np.mean([r["mechs"][mid] for r in all_sat]) if all_sat else 0
        none_m = np.mean([r["mechs"][mid] for r in none_sat]) if none_sat else 0
        delta = all_m - none_m
        emerged = delta >= 0.15
        if emerged:
            emergent_m.append(mid)
        mech_rows.append({"mechanism": mid, "all_mean": round(all_m, 3),
                          "none_mean": round(none_m, 3), "delta": round(delta, 3),
                          "emerged": emerged})
    mech_pct = len(emergent_m) / len(MECH_IDS) * 100

    # --- Viability basin ---
    viable_all = sum(1 for r in all_sat if r["viable"])
    viable_none = sum(1 for r in none_sat if r["viable"])
    basin_yes = (viable_all / max(1, len(all_sat))) > (viable_none / max(1, len(none_sat))) * 2 if none_sat else None

    # --- Fertile corridor ---
    viable_results = [r for r in results if r["viable"]]
    corridor_detected = False
    edge_of_chaos_pct = None
    if len(viable_results) >= 10:
        stabilities = np.array([r["stability"] for r in viable_results])
        fertilities = np.array([r["fertility_index"] for r in viable_results])
        n_bins = 5
        bin_edges = np.linspace(stabilities.min(), stabilities.max(), n_bins + 1)
        bin_centers = []
        bin_mean_fert = []
        bin_max_fert = []
        bin_counts = []
        for i in range(n_bins):
            mask = (stabilities >= bin_edges[i]) & (stabilities < bin_edges[i + 1])
            if i == n_bins - 1:
                mask = (stabilities >= bin_edges[i]) & (stabilities <= bin_edges[i + 1])
            bin_counts.append(int(mask.sum()))
            if mask.sum() > 0:
                bin_centers.append((bin_edges[i] + bin_edges[i + 1]) / 2)
                bin_mean_fert.append(float(np.mean(fertilities[mask])))
                bin_max_fert.append(float(np.max(fertilities[mask])))
            else:
                bin_centers.append((bin_edges[i] + bin_edges[i + 1]) / 2)
                bin_mean_fert.append(0.0)
                bin_max_fert.append(0.0)
        mid_idx = n_bins // 2
        if len(bin_max_fert) > mid_idx and bin_max_fert[mid_idx] >= 0.7:
            corridor_detected = True

        # Quadrant analysis
        med_stab = np.median(stabilities)
        med_fert = np.median(fertilities)
        quads = {"HS/HF": 0, "HS/LF": 0, "LS/HF": 0, "LS/LF": 0}
        for s, f in zip(stabilities, fertilities):
            if s >= med_stab and f >= med_fert:
                quads["HS/HF"] += 1
            elif s >= med_stab:
                quads["HS/LF"] += 1
            elif f >= med_fert:
                quads["LS/HF"] += 1
            else:
                quads["LS/LF"] += 1
        total_q = sum(quads.values())
        edge_of_chaos_pct = round(quads["LS/HF"] / total_q * 100, 1) if total_q else None

    # --- Meta-space PCA ---
    pc1_pct = None
    intrinsic_dim = None
    if len(results) >= 10:
        metric_names = ["C", "P", "G", "R", "S", "SR", "NP", "RC", "RD", "OE"]
        X = np.array([[r["viability"].get(m, r["fertility"].get(m, 0)) for m in metric_names] for r in results])
        X_centered = X - X.mean(axis=0)
        _, eigvals, _ = np.linalg.svd(X_centered, full_matrices=False)
        eigvals = eigvals ** 2
        explained = eigvals / eigvals.sum() * 100
        pc1_pct = round(float(explained[0]), 1)
        cum = 0
        for i, ev in enumerate(explained):
            cum += ev
            if cum >= 90:
                intrinsic_dim = i + 1
                break

    # --- Fertile cluster analysis ---
    fertile_spread = None
    nonfertile_spread = None
    if len(results) >= 10 and pc1_pct is not None:
        metric_names = ["C", "P", "G", "R", "S", "SR", "NP", "RC", "RD", "OE"]
        X = np.array([[r["viability"].get(m, r["fertility"].get(m, 0)) for m in metric_names] for r in results])
        X_centered = X - X.mean(axis=0)
        U, _, _ = np.linalg.svd(X_centered, full_matrices=False)
        scores = X_centered @ U.T
        fertile_pts = scores[[i for i, r in enumerate(results) if r["fertile"]], :2]
        nonfertile_pts = scores[[i for i, r in enumerate(results) if not r["fertile"]], :2]
        if len(fertile_pts) >= 2:
            fertile_spread = round(float(np.mean(np.std(fertile_pts, axis=0))), 3)
        if len(nonfertile_pts) >= 2:
            nonfertile_spread = round(float(np.mean(np.std(nonfertile_pts, axis=0))), 3)

    return {
        "label": label,
        "n_all": len(all_sat),
        "n_none": len(none_sat),
        "n_some": len(some_sat),
        "assumption_emergence": {
            "n_emergent": len(emergent),
            "n_total": len(ASS_IDS),
            "pct": round(em_pct, 1),
            "emergent_list": emergent,
            "rows": ass_rows,
        },
        "mechanism_emergence": {
            "n_emergent": len(emergent_m),
            "n_total": len(MECH_IDS),
            "pct": round(mech_pct, 1),
            "emergent_list": emergent_m,
            "rows": mech_rows,
        },
        "viability_basin": {
            "viable_all": int(viable_all),
            "viable_none": int(viable_none),
            "basin_present": bool(basin_yes) if basin_yes is not None else None,
        },
        "fertile_corridor": {
            "corridor_detected": corridor_detected,
            "edge_of_chaos_pct": edge_of_chaos_pct,
        },
        "meta_space": {
            "pc1_pct": pc1_pct,
            "intrinsic_dim": intrinsic_dim,
            "fertile_spread": fertile_spread,
            "nonfertile_spread": nonfertile_spread,
        },
    }


# ============================================================
# MAIN
# ============================================================

print("=" * 72)
print("T082: STRUCTURAL REALIZATION AUDIT")
print("=" * 72)

# Generate ensemble (same as T081)
print("\nGenerating system ensemble...")
all_params = []
for det in [0.2, 0.4, 0.6, 0.8, 0.95]:
    for conn in [0.3, 0.5, 0.7, 0.9]:
        for sm_level in [0, 1, 2, 3]:
            for sm_inf in [0.0, 0.3, 0.6]:
                all_params.append({
                    "base_n_states": random.choice([3, 4, 5, 6]),
                    "determinism": det,
                    "connectivity": conn,
                    "novelty_drive": random.choice([0.1, 0.2, 0.3, 0.5]),
                    "boundary_strength": random.choice([0.3, 0.5, 0.7, 0.9]),
                    "self_model_level": sm_level,
                    "self_model_influence": sm_inf,
                })
random.shuffle(all_params)
all_params = all_params[:240]
print(f"  {len(all_params)} parameter configurations")

results = []
for i, params in enumerate(all_params):
    r = assay_system(params)
    results.append(r)
    if (i + 1) % 50 == 0:
        print(f"  Ran {i+1}/{len(all_params)} systems...")
print(f"  Complete: {len(results)} systems analyzed")


# ============================================================
# Run all phases
# ============================================================

print(f"\n{'='*72}")
print("RUNNING ALL CONSTELLATION PHASES")
print("=" * 72)

all_phase_results = []
for pdef in PHASE_DEFS:
    print(f"\n--- {pdef['label']} ---")
    pa = run_assay(results, pdef["constraints"], pdef["label"])
    all_phase_results.append(pa)
    ae = pa["assumption_emergence"]
    me = pa["mechanism_emergence"]
    vb = pa["viability_basin"]
    fc = pa["fertile_corridor"]
    ms = pa["meta_space"]
    print(f"  All-sat: {pa['n_all']}, None-sat: {pa['n_none']}")
    print(f"  Assumptions emerged: {ae['n_emergent']}/{ae['n_total']} ({ae['pct']}%) — {ae['emergent_list']}")
    print(f"  Mechanisms emerged:  {me['n_emergent']}/{me['n_total']} ({me['pct']}%) — {me['emergent_list']}")
    print(f"  Viability basin:     {'YES' if vb['basin_present'] else 'NO'}")
    print(f"  Fertile corridor:    {'YES' if fc['corridor_detected'] else 'NO'} (EoC: {fc['edge_of_chaos_pct']}%)")
    print(f"  PC1%: {ms['pc1_pct']}, Intrinsic dim: {ms['intrinsic_dim']}")


# ============================================================
# ABLATION: remove each candidate from the best constellation
# ============================================================

print(f"\n{'='*72}")
print("ABLATION ON BEST CONSTELLATION")
print("=" * 72)

# Identify best phase (most assumptions + mechanisms emerged)
best_idx = max(range(len(all_phase_results)),
               key=lambda i: (all_phase_results[i]["assumption_emergence"]["n_emergent"] +
                               all_phase_results[i]["mechanism_emergence"]["n_emergent"]))
best_pdef = PHASE_DEFS[best_idx]
best_result = all_phase_results[best_idx]
print(f"\nBest constellation: {best_pdef['label']}")
print(f"  ({best_result['assumption_emergence']['n_emergent']} assumptions, "
      f"{best_result['mechanism_emergence']['n_emergent']} mechanisms)")

# Ablate each constraint from the best set
constraint_names = [c[0] for c in best_pdef["constraints"]]
ablation_results = []
for skip_idx in range(len(best_pdef["constraints"])):
    ablated_constraints = [c for i, c in enumerate(best_pdef["constraints"]) if i != skip_idx]
    removed_name = constraint_names[skip_idx]
    pa = run_assay(results, ablated_constraints, f"Remove {removed_name}")
    ablation_results.append({
        "removed": removed_name,
        "n_all": pa["n_all"],
        "n_none": pa["n_none"],
        "assumptions_emerged": pa["assumption_emergence"]["n_emergent"],
        "mechanisms_emerged": pa["mechanism_emergence"]["n_emergent"],
        "viability_basin": pa["viability_basin"]["basin_present"],
        "fertile_corridor": pa["fertile_corridor"]["corridor_detected"],
    })
    print(f"  Remove {removed_name}: assumptions={pa['assumption_emergence']['n_emergent']}, "
          f"mechanisms={pa['mechanism_emergence']['n_emergent']}, "
          f"basin={'Y' if pa['viability_basin']['basin_present'] else 'N'}, "
          f"corridor={'Y' if pa['fertile_corridor']['corridor_detected'] else 'N'}")

# Also test full ablation (remove ALL constraints)
pa_none = run_assay(results, [], "No constraints (empty set)")
print(f"  No constraints: assumptions={pa_none['assumption_emergence']['n_emergent']}, "
      f"mechanisms={pa_none['mechanism_emergence']['n_emergent']}, "
      f"basin={'Y' if pa_none['viability_basin']['basin_present'] else 'N'}, "
      f"corridor={'Y' if pa_none['fertile_corridor']['corridor_detected'] else 'N'}")


# ============================================================
# DETAILED DELTA TABLE FOR BEST CONSTELLATION
# ============================================================

print(f"\n{'='*72}")
print(f"DETAILED DELTAS — BEST CONSTELLATION: {best_pdef['label']}")
print("=" * 72)

print(f"\n  {'Assumption':<8} {'Delta':<8} {'Emerged?':<10}")
print(f"  {'-'*26}")
for row in best_result["assumption_emergence"]["rows"]:
    marker = "***" if row["delta"] >= 0.3 else "**" if row["delta"] >= 0.2 else "*" if row["delta"] >= 0.1 else ""
    print(f"  {row['assumption']:<8} {row['delta']:<+8.3f} {str(row['emerged']):<10} {marker}")

print(f"\n  {'Mechanism':<8} {'Delta':<8} {'Emerged?':<10}")
print(f"  {'-'*26}")
for row in best_result["mechanism_emergence"]["rows"]:
    print(f"  {row['mechanism']:<8} {row['delta']:<+8.3f} {str(row['emerged']):<10}")


# ============================================================
# SUMMARY TABLE
# ============================================================

print(f"\n{'='*72}")
print("SUMMARY: ALL CONSTELLATIONS")
print("=" * 72)
print(f"\n  {'Phase':<20} {'N_all':<7} {'Assumptions':<14} {'Mechanisms':<14} {'Basin':<8} {'Corridor':<8} {'PC1%':<8}")
print(f"  {'-'*79}")
for pa in all_phase_results:
    ae = pa["assumption_emergence"]
    me = pa["mechanism_emergence"]
    vb = pa["viability_basin"]
    fc = pa["fertile_corridor"]
    ms = pa["meta_space"]
    label_short = pa["label"].split("(")[0].strip()[:18]
    basin_s = "YES" if vb["basin_present"] else ("NO" if vb["basin_present"] is False else "?")
    corr_s = "YES" if fc["corridor_detected"] else "NO"
    pc1_s = str(ms["pc1_pct"]) if ms["pc1_pct"] else "?"
    print(f"  {label_short:<20} {pa['n_all']:<7} {ae['n_emergent']}/{ae['n_total']:<10} {me['n_emergent']}/{me['n_total']:<10} {basin_s:<8} {corr_s:<8} {pc1_s:<8}")

# Ablation summary
print(f"\n  {'-'*79}")
print(f"\n  Ablation (from best = {best_pdef['label']}):")
print(f"  {'Removed':<15} {'Assumptions':<14} {'Mechanisms':<14} {'Basin':<8} {'Corridor':<8}")
print(f"  {'-'*59}")
for ar in ablation_results:
    print(f"  {ar['removed']:<15} {ar['assumptions_emerged']:<14} {ar['mechanisms_emerged']:<14} "
          f"{'Y' if ar['viability_basin'] else 'N':<8} {'Y' if ar['fertile_corridor'] else 'N':<8}")
print(f"  {'None':<15} {pa_none['assumption_emergence']['n_emergent']:<14} "
      f"{pa_none['mechanism_emergence']['n_emergent']:<14} "
      f"{'Y' if pa_none['viability_basin']['basin_present'] else 'N':<8} "
      f"{'Y' if pa_none['fertile_corridor']['corridor_detected'] else 'N':<8}")


# ============================================================
# WRITE OUTPUTS
# ============================================================

# Phase comparison table
with open(OUT / "t082_phase_comparison.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["phase", "label", "n_all", "n_none", "assumptions_emerged", "assumptions_total",
                 "mechanisms_emerged", "mechanisms_total", "viability_basin", "fertile_corridor",
                 "pc1_pct", "intrinsic_dim"])
    for pa in all_phase_results:
        ae = pa["assumption_emergence"]
        me = pa["mechanism_emergence"]
        vb = pa["viability_basin"]
        fc = pa["fertile_corridor"]
        ms = pa["meta_space"]
        w.writerow([pa["label"], ae["pct"], pa["n_all"], pa["n_none"],
                     ae["n_emergent"], ae["n_total"],
                     me["n_emergent"], me["n_total"],
                     vb["basin_present"], fc["corridor_detected"],
                     ms["pc1_pct"], ms["intrinsic_dim"]])

# Detailed phase data
for pa in all_phase_results:
    safe_name = pa["label"].replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")[:30]
    # Assumption details
    with open(OUT / f"t082_assumptions_{safe_name}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["assumption", "all_mean", "none_mean", "delta", "emerged"])
        for row in pa["assumption_emergence"]["rows"]:
            w.writerow([row["assumption"], row["all_mean"], row["none_mean"], row["delta"], row["emerged"]])
    # Mechanism details
    with open(OUT / f"t082_mechanisms_{safe_name}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["mechanism", "all_mean", "none_mean", "delta", "emerged"])
        for row in pa["mechanism_emergence"]["rows"]:
            w.writerow([row["mechanism"], row["all_mean"], row["none_mean"], row["delta"], row["emerged"]])

# Ablation results
with open(OUT / "t082_ablation.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["removed", "n_all", "n_none", "assumptions_emerged", "mechanisms_emerged",
                 "viability_basin", "fertile_corridor"])
    for ar in ablation_results:
        w.writerow([ar["removed"], ar["n_all"], ar["n_none"],
                     ar["assumptions_emerged"], ar["mechanisms_emerged"],
                     ar["viability_basin"], ar["fertile_corridor"]])
    w.writerow(["none_removed", pa_none["n_all"], pa_none["n_none"],
                 pa_none["assumption_emergence"]["n_emergent"],
                 pa_none["mechanism_emergence"]["n_emergent"],
                 pa_none["viability_basin"]["basin_present"],
                 pa_none["fertile_corridor"]["corridor_detected"]])

# Summary JSON
summary = {
    "audit": "T082 — Structural Realization Audit",
    "question": "What additional principle, combined with MC2+MC3+MC4, causes substrate/mechanisms/corridor to reappear?",
    "n_systems": int(len(results)),
    "phases": [],
    "best_phase": {
        "label": best_pdef["label"],
        "assumptions": int(best_result["assumption_emergence"]["n_emergent"]),
        "mechanisms": int(best_result["mechanism_emergence"]["n_emergent"]),
    },
    "ablation": [],
}
for pa in all_phase_results:
    ae = pa["assumption_emergence"]
    me = pa["mechanism_emergence"]
    vb = pa["viability_basin"]
    fc = pa["fertile_corridor"]
    ms = pa["meta_space"]
    summary["phases"].append({
        "label": pa["label"],
        "n_all": int(pa["n_all"]),
        "n_none": int(pa["n_none"]),
        "assumptions_emerged": int(ae["n_emergent"]),
        "assumptions_pct": ae["pct"],
        "emergent_assumptions": ae["emergent_list"],
        "mechanisms_emerged": int(me["n_emergent"]),
        "emergent_mechanisms": me["emergent_list"],
        "viability_basin": vb["basin_present"],
        "fertile_corridor": fc["corridor_detected"],
        "pc1_pct": ms["pc1_pct"],
        "intrinsic_dim": ms["intrinsic_dim"],
    })
for ar in ablation_results:
    summary["ablation"].append({
        "removed": ar["removed"],
        "assumptions_emerged": int(ar["assumptions_emerged"]),
        "mechanisms_emerged": int(ar["mechanisms_emerged"]),
        "viability_basin": ar["viability_basin"],
        "fertile_corridor": ar["fertile_corridor"],
    })

with open(OUT / "t082_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print(f"\nWrote t082_phase_comparison.csv")
print(f"Wrote t082_assumptions_*.csv (one per phase)")
print(f"Wrote t082_mechanisms_*.csv (one per phase)")
print(f"Wrote t082_ablation.csv")
print(f"Wrote t082_summary.json")
print(f"\nT082 complete.")
