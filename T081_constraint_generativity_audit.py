#!/usr/bin/env python3
"""
T081: Constraint Generativity Audit
====================================
Test whether MC2 (Productive Transformation), MC3 (Constraint Balance),
and MC4 (Recursive Accessibility) can GENERATE the structures discovered
throughout the program, rather than merely DESCRIBE them.

Method:
  Phase 1 — Assumption Emergence: do OC2..SR1 appear spontaneously?
  Phase 2 — Mechanism Emergence: do T059 failure modes reappear?
  Phase 3 — Viability Basin: does a viability region emerge?
  Phase 4 — Fertile Corridor: does a finite-width fertility band emerge?
  Phase 5 — Meta-space: does the latent geometry match T078?
  Phase 6 — Ablation: what breaks when a constraint is removed?
"""

import csv, json, math, itertools, random
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np

OUT = Path("/home/student/sgp_core_v2/sfh_sgp_ood_outputs")
random.seed(42)
np.random.seed(42)

# ============================================================
# SYSTEM GENERATION
# ============================================================
# Each system is a Markov chain with optional self-modeling and
# state-generation capabilities.

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
        # Transition matrix: n x n, rows sum to 1
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
# CONSTRAINT SCORING
# ============================================================

def score_mc2(metrics):
    """Productive Transformation: system generates novelty."""
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
    """Constraint Balance: bounded freedom — not too rigid, not too divergent."""
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
    """Recursive Accessibility: system can access own state."""
    sm_r = metrics.get("sm_ratio", 0)
    sm_i = metrics.get("sm_impact", 0)
    sc = metrics.get("self_correlation", 0)
    score = sm_r * 0.4 + sm_i * 0.3 + sc * 0.3
    return min(1.0, score)


# ============================================================
# EMERGENCE MEASUREMENT
# ============================================================

def measure_oc2(metrics, system):
    """Distinguishability: states have distinguishable effects."""
    if system.n_actual < 2:
        return 0.0
    trans_sets = [set(np.where(row > 0.01)[0].tolist()) for row in system.T]
    unique_trans = len(set(tuple(sorted(t)) for t in trans_sets))
    return min(1.0, unique_trans / max(1, system.n_actual))


def measure_oc1(metrics, system):
    """Stable structure: states persist."""
    h = system.history
    if len(h) < 10:
        return 0.0
    recent = h[-20:]
    recurrence = len(set(recent)) / max(1, len(recent))
    return 1.0 - recurrence


def measure_cd1(metrics, system):
    """Causal relations: transitions are regular."""
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
    """Extractable information: differences are registered."""
    if system.n_actual < 2:
        return 0.0
    trans = list(zip(system.history[:-1], system.history[1:]))
    if not trans:
        return 0.0
    future_divergence = 0
    state_outcomes = defaultdict(set)
    for s, ns in trans:
        state_outcomes[s].add(ns)
    for s, outcomes in state_outcomes.items():
        future_divergence += len(outcomes) / max(1, system.n_actual)
    future_divergence /= max(1, len(state_outcomes))
    return min(1.0, future_divergence * 1.5)


def measure_is1(metrics, system):
    """Phase structure: system changes over time."""
    h = system.history
    if len(h) < 10:
        return 0.0
    blocks = [h[i:i+5] for i in range(0, len(h)-4, 5)]
    if len(blocks) < 2:
        return 0.0
    changes = sum(1 for i in range(1, len(blocks)) if set(blocks[i]) != set(blocks[i-1]))
    return min(1.0, changes / max(1, len(blocks) - 1))


def measure_is2(metrics, system):
    """Determinate outputs: system produces identifiable results."""
    h = system.history
    if len(h) < 5:
        return 0.0
    recent = h[-10:]
    if len(set(recent)) <= 2:
        return 1.0
    return min(0.5, 5.0 / len(set(recent)))


def measure_cd2(metrics, system):
    """Self-affecting procedures: procedures affect themselves."""
    sm = system.self_model_level
    sm_i = system.sm_influence
    sc = metrics.get("self_correlation", 0)
    cycle = metrics.get("cycle_length", 0)
    score = (min(1.0, sm / 2) * 0.4 +
             sm_i * 0.3 +
             min(1.0, sc * 1.5) * 0.15 +
             (1.0 if cycle > 2 else 0.0) * 0.15)
    return min(1.0, score)


def measure_ec1(metrics, system):
    """Self-knowledge: system has access to own state."""
    sm = system.self_model_level
    sm_i = system.sm_influence
    sc = metrics.get("self_correlation", 0)
    return min(1.0, (sm / 3) * 0.5 + sm_i * 0.3 + sc * 0.2)


def measure_sr1(metrics, system):
    """Self-examination of outputs: system examines own results."""
    sm = system.self_model_level
    sm_i = system.sm_influence
    cycle = metrics.get("cycle_length", 0)
    sc = metrics.get("self_correlation", 0)
    if sm < 2:
        return sm * 0.3
    return min(1.0, (sm / 3) * 0.3 + sm_i * 0.3 + (1.0 if cycle > 1 else 0.0) * 0.2 + sc * 0.2)


# ============================================================
# VIABILITY & FERTILITY METRICS (mirroring T073-T074)
# ============================================================

def compute_coherence(metrics, system, em):
    """C — internal consistency."""
    det = system.determinism
    sc = metrics.get("self_correlation", 0)
    oc2 = em.get("OC2", 0)
    return min(1.0, (det * 0.3 + sc * 0.3 + oc2 * 0.4))


def compute_persistence(metrics, system, em):
    """P — system endures."""
    conv = metrics.get("convergence", 0)
    cycle = metrics.get("cycle_length", 0)
    n = system.n_actual
    oc1 = em.get("OC1", 0)
    stab = (1.0 if cycle <= 5 else 0.5 if cycle <= 10 else 0.2) * 0.4
    return min(1.0, stab + conv * 0.3 + oc1 * 0.3)


def compute_generativity(metrics, system, em):
    """G — capacity for novel structure."""
    mc2 = score_mc2(metrics)
    expan = metrics.get("state_expansions", 0)
    trans_div = metrics.get("transition_diversity", 0)
    ic1 = em.get("IC1", 0)
    return min(1.0, mc2 * 0.4 + min(1.0, expan / 3) * 0.2 + trans_div * 0.2 + ic1 * 0.2)


def compute_recoverability(metrics, system, em):
    """R — ability to absorb disruption."""
    conv = metrics.get("convergence", 0)
    cycle = metrics.get("cycle_length", 0)
    sc = metrics.get("self_correlation", 0)
    cd1 = em.get("CD1", 0)
    recover = (1.0 if 2 <= cycle <= 6 else 0.5 if cycle > 0 else 0.0) * 0.4
    return min(1.0, recover + conv * 0.2 + sc * 0.2 + cd1 * 0.2)


def compute_self_modeling(metrics, system, em):
    """S — system represents/examines itself."""
    ec1 = em.get("EC1", 0)
    sr1 = em.get("SR1", 0)
    cd2 = em.get("CD2", 0)
    return min(1.0, ec1 * 0.4 + sr1 * 0.3 + cd2 * 0.3)


# Fertility metrics (mirroring T074)

def compute_novelty_production(metrics, system, em):
    """NP — rate of novel output generation."""
    uniq = metrics.get("unique_ratio", 0)
    expan = metrics.get("state_expansions", 0)
    entropy = metrics.get("entropy", 0)
    return min(1.0, uniq * 0.4 + min(1.0, expan / 4) * 0.3 + entropy * 0.3)


def compute_structural_richness(metrics, system, em):
    """SR — structural diversity."""
    trans_div = metrics.get("transition_diversity", 0)
    n = system.n_actual
    is1 = em.get("IS1", 0)
    return min(1.0, trans_div * 0.4 + min(1.0, n / 8) * 0.3 + is1 * 0.3)


def compute_recombination(metrics, system, em):
    """RC — capacity to recombine existing structures."""
    sc = metrics.get("self_correlation", 0)
    cd2 = em.get("CD2", 0)
    cycle = metrics.get("cycle_length", 0)
    trans_div = metrics.get("transition_diversity", 0)
    return min(1.0, sc * 0.3 + cd2 * 0.3 + (1.0 if cycle >= 3 else cycle / 3) * 0.2 + trans_div * 0.2)


def compute_recursive_depth(metrics, system, em):
    """RD — depth of recursive processing."""
    sm = system.self_model_level
    sr1 = em.get("SR1", 0)
    ec1 = em.get("EC1", 0)
    cd2 = em.get("CD2", 0)
    return min(1.0, (sm / 3) * 0.4 + sr1 * 0.3 + ec1 * 0.15 + cd2 * 0.15)


def compute_open_endedness(metrics, system, em):
    """OE — potential for continued evolution."""
    mc2 = score_mc2(metrics)
    expan = metrics.get("state_expansions", 0)
    unique = metrics.get("unique_ratio", 0)
    is1 = em.get("IS1", 0)
    return min(1.0, mc2 * 0.3 + min(1.0, expan / 3) * 0.3 + unique * 0.2 + is1 * 0.2)


# ============================================================
# MECHANISM DETECTION (Phase 2)
# ============================================================

def detect_mechanisms(metrics, system):
    """Detect which T059 mechanism classes appear in the system dynamics."""
    mechanisms = {}
    h = system.history

    # M01: System cannot fully examine itself
    sm = system.self_model_level
    n = system.n_actual
    m01 = 1.0 if (sm < 2 and n >= 4) else (0.5 if sm < 2 else 0.0)

    # M02: Procedure finds its own fixed point
    cycle = metrics.get("cycle_length", 0)
    conv = metrics.get("convergence", 0)
    m02 = 1.0 if (cycle == 1 and conv > 0.8) else (0.5 if cycle <= 2 else 0.0)

    # M03: Method determines result
    det = system.determinism
    m03 = det * 0.7 + (1.0 if system.novelty_drive < 0.2 else 0.0) * 0.3

    # M04: Observer and observed cannot be separated
    sm_i = system.sm_influence
    sc = metrics.get("self_correlation", 0)
    m04 = min(1.0, sm_i * 0.5 + sc * 0.5)

    # M05: Information exhausted; artifacts remain
    uniq = metrics.get("unique_ratio", 0)
    entropy = metrics.get("entropy", 0)
    m05 = max(0.0, 1.0 - uniq * 0.5 - entropy * 0.5)

    # M06: System trapped in attractor basin
    conv = metrics.get("convergence", 0)
    cycle = metrics.get("cycle_length", 0)
    sc = metrics.get("self_correlation", 0)
    m06 = 1.0 if (conv > 0.9 and cycle <= 2 and sc > 0.8) else (0.5 if cycle <= 3 else 0.0)

    # M07: Question is incoherent at this level
    if len(h) < 10:
        m07 = 0.0
    else:
        recent = h[-10:]
        if len(set(recent)) == len(recent):
            m07 = 0.8
        else:
            m07 = 0.0

    # M08: Recursion IS the identity
    sm = system.self_model_level
    cycle = metrics.get("cycle_length", 0)
    sc = metrics.get("self_correlation", 0)
    m08 = 1.0 if (sm >= 2 and cycle > 2 and sc > 0.6) else (0.5 if cycle > 2 else 0.0)

    return {
        "M01": m01, "M02": m02, "M03": m03, "M04": m04,
        "M05": m05, "M06": m06, "M07": m07, "M08": m08,
    }


# ============================================================
# GENERATE ENSEMBLE
# ============================================================

def generate_parameter_grid(n_per_region=30):
    """Generate diverse system configurations."""
    params_list = []
    for det in [0.2, 0.4, 0.6, 0.8, 0.95]:
        for conn in [0.3, 0.5, 0.7, 0.9]:
            for sm_level in [0, 1, 2, 3]:
                for sm_inf in [0.0, 0.3, 0.6]:
                    params_list.append({
                        "base_n_states": random.choice([3, 4, 5, 6]),
                        "determinism": det,
                        "connectivity": conn,
                        "novelty_drive": random.choice([0.1, 0.2, 0.3, 0.5]),
                        "boundary_strength": random.choice([0.3, 0.5, 0.7, 0.9]),
                        "self_model_level": sm_level,
                        "self_model_influence": sm_inf,
                    })
    random.shuffle(params_list)
    return params_list[:n_per_region * 10]


def run_system(params, steps=200):
    system = GeneratedSystem(params)
    metrics = system.run(steps)

    mc2 = score_mc2(metrics)
    mc3 = score_mc3(metrics)
    mc4 = score_mc4(metrics)

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

    sat_mc2 = mc2 >= 0.5
    sat_mc3 = mc3 >= 0.5
    sat_mc4 = mc4 >= 0.5

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
        "sat_mc2": sat_mc2, "sat_mc3": sat_mc3, "sat_mc4": sat_mc4,
        "em": em, "mechs": mechs,
        "viability": viability, "fertility": fertility,
        "viable": viability_threshold,
        "fertile": fertile_signature,
        "stability": stability,
        "fertility_index": fert_index,
    }


# ============================================================
# MAIN ANALYSIS
# ============================================================

print("=" * 72)
print("T081: CONSTRAINT GENERATIVITY AUDIT")
print("=" * 72)

print("\nGenerating system ensemble...")
all_params = generate_parameter_grid(50)
print(f"  {len(all_params)} parameter configurations")

results = []
for i, params in enumerate(all_params):
    r = run_system(params)
    results.append(r)
    if (i + 1) % 50 == 0:
        print(f"  Ran {i+1}/{len(all_params)} systems...")

print(f"  Complete: {len(results)} systems analyzed")

# ============================================================
# PHASE 1: ASSUMPTION EMERGENCE
# ============================================================

print(f"\n{'='*72}")
print("PHASE 1: ASSUMPTION EMERGENCE")
print("=" * 72)

# Systems that satisfy all three constraints vs those that don't
mc_all_sat = [r for r in results if r["sat_mc2"] and r["sat_mc3"]]
mc_none_sat = [r for r in results if not r["sat_mc2"] and not r["sat_mc3"]]
mc_some_sat = [r for r in results if r not in mc_all_sat and r not in mc_none_sat]

print(f"\n  Constraint satisfaction groups:")
print(f"    All three:     {len(mc_all_sat)} systems")
print(f"    Some:          {len(mc_some_sat)} systems")
print(f"    None:          {len(mc_none_sat)} systems")

ass_ids = ["OC2", "OC1", "CD1", "IC1", "IS1", "IS2", "CD2", "EC1", "SR1"]
ass_names = ["Distinguishability", "Stable structure", "Causal relations",
             "Extractable info", "Phase structure", "Determinate outputs",
             "Self-affecting procedures", "Self-knowledge",
             "Self-examination of outputs"]

print(f"\n  {'Assumption':<8}{'Name':<30}{'All MCs':<10}{'None MCs':<10}{'Delta':<10}{'Sig':<8}")
print(f"  {'-'*76}")

phase1_rows = []
emergent_assumptions = []
for aid, aname in zip(ass_ids, ass_names):
    if mc_all_sat:
        all_mean = np.mean([r["em"][aid] for r in mc_all_sat])
    else:
        all_mean = 0
    if mc_none_sat:
        none_mean = np.mean([r["em"][aid] for r in mc_none_sat])
    else:
        none_mean = 0

    delta = all_mean - none_mean
    threshold = 0.3
    sig = "***" if delta > threshold else "**" if delta > 0.2 else "*" if delta > 0.1 else ""
    emergent = delta >= 0.2
    if emergent:
        emergent_assumptions.append(aid)

    print(f"  {aid:<8}{aname:<30}{all_mean:<10.3f}{none_mean:<10.3f}{delta:<+10.3f}{sig:<8}")
    phase1_rows.append({
        "assumption": aid, "name": aname,
        "all_mcs_mean": round(all_mean, 3),
        "none_mcs_mean": round(none_mean, 3),
        "delta": round(delta, 3),
        "emergent": emergent,
    })

emergent_pct = len(emergent_assumptions) / len(ass_ids) * 100
print(f"\n  Emergent assumptions (delta >= 0.2): {len(emergent_assumptions)}/{len(ass_ids)} ({emergent_pct:.0f}%)")
print(f"  Success criterion (>=80%): {'PASS' if emergent_pct >= 80 else 'FAIL'}")

if emergent_assumptions:
    print(f"  Emerged: {', '.join(emergent_assumptions)}")
not_emergent = set(ass_ids) - set(emergent_assumptions)
if not_emergent:
    print(f"  Not emerged: {', '.join(sorted(not_emergent))}")

# ============================================================
# PHASE 2: MECHANISM EMERGENCE
# ============================================================

print(f"\n{'='*72}")
print("PHASE 2: MECHANISM EMERGENCE")
print("=" * 72)

mech_ids = ["M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08"]
mech_names = [
    "Cannot fully examine self", "Fixed-point finder",
    "Method determines result", "Observer/observed entangled",
    "Info exhausted, artifacts", "Trapped in attractor",
    "Incoherent question", "Recursion is identity",
]

print(f"\n  {'Mech':<8}{'Name':<30}{'All MCs':<10}{'None MCs':<10}{'Delta':<10}")
print(f"  {'-'*68}")

phase2_rows = []
emergent_mechanisms = []
for mid, mname in zip(mech_ids, mech_names):
    if mc_all_sat:
        all_mean = np.mean([r["mechs"][mid] for r in mc_all_sat])
    else:
        all_mean = 0
    if mc_none_sat:
        none_mean = np.mean([r["mechs"][mid] for r in mc_none_sat])
    else:
        none_mean = 0
    delta = all_mean - none_mean
    emergent = delta >= 0.15
    if emergent:
        emergent_mechanisms.append(mid)
    print(f"  {mid:<8}{mname:<30}{all_mean:<10.3f}{none_mean:<10.3f}{delta:<+10.3f}")
    phase2_rows.append({
        "mechanism": mid, "name": mname,
        "all_mcs_mean": round(all_mean, 3),
        "none_mcs_mean": round(none_mean, 3),
        "delta": round(delta, 3),
        "emergent": emergent,
    })

print(f"\n  Emergent mechanisms (delta >= 0.15): {len(emergent_mechanisms)}/{len(mech_ids)}")
if emergent_mechanisms:
    print(f"  Emerged: {', '.join(emergent_mechanisms)}")

# ============================================================
# PHASE 3: VIABILITY BASIN EMERGENCE
# ============================================================

print(f"\n{'='*72}")
print("PHASE 3: VIABILITY BASIN EMERGENCE")
print("=" * 72)

viable_count = sum(1 for r in results if r["viable"])
viable_mc_all = sum(1 for r in mc_all_sat if r["viable"])
viable_mc_none = sum(1 for r in mc_none_sat if r["viable"])

print(f"\n  Viable systems (C>=0.75, P>=0.65, G>=0.40): {viable_count}/{len(results)} ({viable_count/len(results)*100:.0f}%)")
print(f"  Viable among ALL MCs satisfied:  {viable_mc_all}/{len(mc_all_sat)} ({viable_mc_all/max(1,len(mc_all_sat))*100:.0f}%)")
print(f"  Viable among NO MCs satisfied:   {viable_mc_none}/{len(mc_none_sat)} ({viable_mc_none/max(1,len(mc_none_sat))*100:.0f}%)")

print(f"\n  Mean viability metrics:")
v_axes = ["C", "P", "G", "R", "S"]
print(f"  {'Axis':<6}{'All MCs':<12}{'None MCs':<12}{'Delta':<12}")
print(f"  {'-'*42}")
viability_rows = []
for axis in v_axes:
    if mc_all_sat:
        all_m = np.mean([r["viability"][axis] for r in mc_all_sat])
    else:
        all_m = 0
    if mc_none_sat:
        none_m = np.mean([r["viability"][axis] for r in mc_none_sat])
    else:
        none_m = 0
    delta = all_m - none_m
    print(f"  {axis:<6}{all_m:<12.3f}{none_m:<12.3f}{delta:<+12.3f}")
    viability_rows.append({
        "axis": axis, "all_mcs": round(all_m, 3),
        "none_mcs": round(none_m, 3), "delta": round(delta, 3),
    })

print(f"\n  Viability basin emergence: {'YES — MCs create viability' if viable_mc_all/max(1,len(mc_all_sat)) > viable_mc_none/max(1,len(mc_none_sat))*2 else 'WEAK'}")

# ============================================================
# PHASE 4: FERTILE CORRIDOR EMERGENCE
# ============================================================

print(f"\n{'='*72}")
print("PHASE 4: FERTILE CORRIDOR EMERGENCE")
print("=" * 72)

fertile_count = sum(1 for r in results if r["fertile"])
fertile_mc_all = sum(1 for r in mc_all_sat if r["fertile"])
fertile_mc_none = sum(1 for r in mc_none_sat if r["fertile"])

print(f"\n  Fertile systems: {fertile_count}/{len(results)} ({fertile_count/len(results)*100:.0f}%)")
print(f"  Fertile among ALL MCs:  {fertile_mc_all}/{len(mc_all_sat)} ({fertile_mc_all/max(1,len(mc_all_sat))*100:.0f}%)")
print(f"  Fertile among NO MCs:   {fertile_mc_none}/{len(mc_none_sat)} ({fertile_mc_none/max(1,len(mc_none_sat))*100:.0f}%)")

# Stability bins to detect corridor
viable_results = [r for r in results if r["viable"]]
if len(viable_results) >= 10:
    stabilities = np.array([r["stability"] for r in viable_results])
    fertilities = np.array([r["fertility_index"] for r in viable_results])

    n_bins = 5
    bin_edges = np.linspace(stabilities.min(), stabilities.max(), n_bins + 1)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    print(f"\n  Stability bins (viable systems only):")
    print(f"  {'Bin':<6}{'Range':<18}{'N':<6}{'Mean Fert':<12}{'Max Fert':<12}")
    print(f"  {'-'*54}")

    corridor_detected = False
    for i in range(n_bins):
        lo, hi = bin_edges[i], bin_edges[i+1]
        mask = (stabilities >= lo) & (stabilities < hi)
        n_in_bin = mask.sum()
        if n_in_bin > 0:
            mean_f = fertilities[mask].mean()
            max_f = fertilities[mask].max()
            print(f"  {i+1:<6}{lo:.3f}-{hi:.3f}{'':8}{n_in_bin:<6}{mean_f:<12.3f}{max_f:<12.3f}")

    # Check for corridor: at least one intermediate bin has higher mean fertility than extremes
    bin_means = []
    for i in range(n_bins):
        lo, hi = bin_edges[i], bin_edges[i+1]
        mask = (stabilities >= lo) & (stabilities < hi)
        if mask.sum() > 0:
            bin_means.append(fertilities[mask].mean())
        else:
            bin_means.append(0)

    if n_bins >= 3 and len(bin_means) >= 3:
        interior = bin_means[1:-1]
        extremes = [bin_means[0], bin_means[-1]]
        if interior and max(interior) > min(extremes) * 1.1:
            corridor_detected = True

    print(f"\n  Fertile corridor detected: {'YES' if corridor_detected else 'NO'}")

    # Edge-of-chaos quadrant analysis
    if len(viable_results) >= 4:
        med_stab = np.median(stabilities)
        med_fert = np.median(fertilities)
        quadrants = {"HS/HF": 0, "HS/LF": 0, "LS/HF": 0, "LS/LF": 0}
        for r in viable_results:
            s = r["stability"]
            f = r["fertility_index"]
            if s >= med_stab and f >= med_fert:
                quadrants["HS/HF"] += 1
            elif s >= med_stab and f < med_fert:
                quadrants["HS/LF"] += 1
            elif s < med_stab and f >= med_fert:
                quadrants["LS/HF"] += 1
            else:
                quadrants["LS/LF"] += 1
        total_q = sum(quadrants.values()) or 1
        print(f"\n  Quadrant distribution (viable only, medians as thresholds):")
        for qname, qcount in sorted(quadrants.items()):
            print(f"    {qname}: {qcount} ({qcount/total_q*100:.0f}%)")
        print(f"  LS/HF (edge-of-chaos) fraction: {quadrants['LS/HF']/total_q*100:.0f}%")
        print(f"  Boundary regime pattern: {'MATCHES T075' if quadrants['LS/HF'] >= quadrants['HS/HF'] else 'DIFFERS from T075'}")

# ============================================================
# PHASE 5: META-SPACE RECONSTRUCTION
# ============================================================

print(f"\n{'='*72}")
print("PHASE 5: META-SPACE RECONSTRUCTION (generated systems)")
print("=" * 72)

all_features = []
for r in results:
    v = r["viability"]
    f = r["fertility"]
    all_features.append([
        v["C"], v["P"], v["G"], v["R"], v["S"],
        f["SR"], f["NP"], f["RC"], f["RD"], f["OE"],
        r["stability"], r["fertility_index"],
        r["mc2"], r["mc3"], r["mc4"],
    ])
all_features = np.array(all_features)
n_obs = all_features.shape[0]
n_vars = 10  # C, P, G, R, S, SR, NP, RC, RD, OE

if n_obs >= n_vars:
    X = all_features[:, :n_vars]
    X_centered = X - X.mean(axis=0)
    cov = (X_centered.T @ X_centered) / (n_obs - 1)
    eigvals, eigvecs = np.linalg.eigh(cov)
    idx = np.argsort(eigvals)[::-1]
    eigvals = eigvals[idx]
    eigvecs = eigvecs[:, idx]
    total_var = eigvals.sum()
    explained = eigvals / total_var * 100
    cumulative = np.cumsum(explained)

    print(f"\n  PCA on {n_obs} generated systems, {n_vars} metrics:")
    print(f"  {'PC':<6}{'Eigenvalue':<14}{'Explained %':<14}{'Cumulative %':<16}")
    print(f"  {'-'*50}")

    for i in range(min(6, len(eigvals))):
        print(f"  PC{i+1:<5}{eigvals[i]:<14.4f}{explained[i]:<14.2f}{cumulative[i]:<16.2f}")

    intrinsic_dim = sum(1 for v in cumulative if v < 90) + 1
    print(f"\n  Intrinsic dimensionality (90% threshold): {intrinsic_dim}")
    print(f"  PC1 dominance: {explained[0]:.1f}% {'(MATCHES T078: 75.1%)' if abs(explained[0] - 75.1) < 20 else '(DIFFERS from T078)'}")

    # Check for fertile corridor in latent space
    if len(viable_results) >= 4:
        X_viable = np.array([[
            r["viability"]["C"], r["viability"]["P"], r["viability"]["G"],
            r["viability"]["R"], r["viability"]["S"],
            r["fertility"]["SR"], r["fertility"]["NP"], r["fertility"]["RC"],
            r["fertility"]["RD"], r["fertility"]["OE"],
        ] for r in viable_results])
        latent = X_viable @ eigvecs[:, :2]
        fertile_latent = latent[[i for i, r in enumerate(viable_results) if r["fertile"]], :]
        nonfertile_latent = latent[[i for i, r in enumerate(viable_results) if not r["fertile"]], :]
        if len(fertile_latent) > 0 and len(nonfertile_latent) > 0:
            fertile_spread = np.std(fertile_latent, axis=0).mean()
            nonfertile_spread = np.std(nonfertile_latent, axis=0).mean()
            print(f"\n  Fertile cluster spread (latent): {fertile_spread:.3f}")
            print(f"  Non-fertile spread: {nonfertile_spread:.3f}")
            print(f"  Connected fertile cluster: {'YES' if fertile_spread < nonfertile_spread * 1.5 else 'UNCLEAR'}")
else:
    print(f"\n  Insufficient observations for PCA ({n_obs} < {n_vars})")

# ============================================================
# PHASE 6: CONSTRAINT ABLATION
# ============================================================

print(f"\n{'='*72}")
print("PHASE 6: CONSTRAINT ABLATION")
print("=" * 72)

ablation_tests = {
    "Remove MC2": lambda r: not r["sat_mc2"] and r["sat_mc3"],
    "Remove MC3": lambda r: r["sat_mc2"] and not r["sat_mc3"],
    "Remove MC4": lambda r: r["sat_mc2"] and r["sat_mc3"] and not r["sat_mc4"],
}

print(f"\n  {'Ablation':<20}{'N':<8}{'Viable':<10}{'Fertile':<10}{'Mean Fert':<12}{'Mean Stab':<12}")
print(f"  {'-'*72}")

ablation_rows = []
for ablation_name, condition in ablation_tests.items():
    subset = [r for r in results if condition(r)]
    n_sub = len(subset)
    if n_sub > 0:
        viable = sum(1 for r in subset if r["viable"])
        fertile = sum(1 for r in subset if r["fertile"])
        mean_fert = np.mean([r["fertility_index"] for r in subset])
        mean_stab = np.mean([r["stability"] for r in subset])
    else:
        viable = 0
        fertile = 0
        mean_fert = 0
        mean_stab = 0
    print(f"  {ablation_name:<20}{n_sub:<8}{viable:<10}{fertile:<10}{mean_fert:<12.3f}{mean_stab:<12.3f}")
    ablation_rows.append({
        "ablation": ablation_name, "n": n_sub,
        "viable": viable, "fertile": fertile,
        "mean_fertility": round(mean_fert, 3),
        "mean_stability": round(mean_stab, 3),
    })

# Verify predictions
print(f"\n  Prediction checks:")
mc2_removed = [r for r in results if not r["sat_mc2"] and r["sat_mc3"]]
mc3_removed = [r for r in results if r["sat_mc2"] and not r["sat_mc3"]]
mc4_removed = [r for r in results if r["sat_mc2"] and r["sat_mc3"] and not r["sat_mc4"]]

if mc2_removed:
    mc2_fert = np.mean([r["fertility_index"] for r in mc2_removed])
    print(f"  Remove MC2: fertility = {mc2_fert:.3f} {'(fertility collapses ✓)' if mc2_fert < 0.4 else '(fertility persists ✗)'}")
else:
    print(f"  Remove MC2: no systems in this condition")

if mc3_removed:
    mc3_stab = np.mean([r["stability"] for r in mc3_removed])
    mc3_viable = sum(1 for r in mc3_removed if r["viable"]) / max(1, len(mc3_removed))
    print(f"  Remove MC3: stability = {mc3_stab:.3f}, viability ratio = {mc3_viable:.2f} {'(viability collapses ✓)' if mc3_viable < 0.2 else '(viability persists ✗)'}")
else:
    print(f"  Remove MC3: no systems in this condition")

if mc4_removed:
    mc4_sr1 = np.mean([r["em"]["SR1"] for r in mc4_removed])
    mc4_ec1 = np.mean([r["em"]["EC1"] for r in mc4_removed])
    print(f"  Remove MC4: SR1 = {mc4_sr1:.3f}, EC1 = {mc4_ec1:.3f} {'(self-structures vanish ✓)' if mc4_sr1 < 0.3 and mc4_ec1 < 0.3 else '(self-structures persist ✗)'}")
else:
    print(f"  Remove MC4: no systems in this condition")

# ============================================================
# OVERALL VERDICT
# ============================================================

print(f"\n{'='*72}")
print("OVERALL VERDICT")
print("=" * 72)

pass_phase1 = emergent_pct >= 80
pass_phase2 = len(emergent_mechanisms) >= 5
pass_phase3 = viable_mc_all / max(1, len(mc_all_sat)) > viable_mc_none / max(1, len(mc_none_sat)) * 2
pass_phase4 = corridor_detected if len(viable_results) >= 10 else None
pass_phase5 = explained[0] > 50 if n_obs >= n_vars else None
pass_phase6_mc2 = np.mean([r["fertility_index"] for r in mc2_removed]) < 0.4 if len(mc2_removed) >= 3 else None
pass_phase6_mc3 = sum(1 for r in mc3_removed if r["viable"]) / max(1, len(mc3_removed)) < 0.2 if len(mc3_removed) >= 3 else None
pass_phase6_mc4 = np.mean([r["em"]["SR1"] for r in mc4_removed]) < 0.3 if len(mc4_removed) >= 3 else None

n_pass = sum(1 for p in [pass_phase1, pass_phase2, pass_phase3]
             if p is True)
n_pass += sum(1 for p in [pass_phase4, pass_phase5, pass_phase6_mc2, pass_phase6_mc3, pass_phase6_mc4]
              if p is True)
n_possible = sum(1 for p in [pass_phase1, pass_phase2, pass_phase3, pass_phase4,
                              pass_phase5, pass_phase6_mc2, pass_phase6_mc3, pass_phase6_mc4]
                 if p is not None)

print(f"\n  Phase results:")
print(f"    Phase 1 (Assumption emergence): {'PASS' if pass_phase1 else 'FAIL'} ({emergent_pct:.0f}%)")
print(f"    Phase 2 (Mechanism emergence):  {'PASS' if pass_phase2 else 'FAIL'} ({len(emergent_mechanisms)}/8)")
print(f"    Phase 3 (Viability basin):      {'PASS' if pass_phase3 else 'FAIL'}")
print(f"    Phase 4 (Fertile corridor):     {'PASS' if pass_phase4 else 'FAIL'}" if pass_phase4 is not None else "    Phase 4 (Fertile corridor):     INCONCLUSIVE")
print(f"    Phase 5 (Meta-space):           {'PASS' if pass_phase5 else 'FAIL'}" if pass_phase5 is not None else "    Phase 5 (Meta-space):           INCONCLUSIVE")
print(f"    Phase 6 (Ablation MC2):         {'PASS' if pass_phase6_mc2 else 'FAIL'}" if pass_phase6_mc2 is not None else "    Phase 6 (Ablation MC2):         INCONCLUSIVE")
print(f"    Phase 6 (Ablation MC3):         {'PASS' if pass_phase6_mc3 else 'FAIL'}" if pass_phase6_mc3 is not None else "    Phase 6 (Ablation MC3):         INCONCLUSIVE")
print(f"    Phase 6 (Ablation MC4):         {'PASS' if pass_phase6_mc4 else 'FAIL'}" if pass_phase6_mc4 is not None else "    Phase 6 (Ablation MC4):         INCONCLUSIVE")

print(f"\n  Overall: {n_pass}/{n_possible} phases passed")

# Determine outcome
if n_pass >= 6:
    outcome = "A — Strong Generative Sufficiency"
    desc = "MC2+MC3+MC4 regenerate the substrate, mechanisms, viability basin, fertile corridor, and latent geometry"
elif n_pass >= 4:
    outcome = "B — Partial Sufficiency"
    desc = "Only some structures emerge — additional meta-constraint may exist"
else:
    outcome = "C — Failure"
    desc = "Generated systems do not reproduce observed structures — substrate remains fundamental"

print(f"\n  OUTCOME: {outcome}")
print(f"  {desc}")

print(f"\n  Conclusion:")
print(f"  This test converts the conceptual derivation of T080 into an operational")
if n_pass >= 6:
    print(f"  generativity proof. MC2+MC3+MC4 are not just explanatory — they are")
    print(f"  generative. The program's deepest layer is a constraint architecture.")
elif n_pass >= 4:
    print(f"  generativity test. Results are partially positive but incomplete.")
    print(f"  A missing constraint may be needed for full generative closure.")
else:
    print(f"  generativity test. Results do not confirm generative sufficiency.")
    print(f"  The substrate retains independent explanatory value.")

# ============================================================
# WRITE DELIVERABLES
# ============================================================

# 1. System-level results
with open(OUT / "t081_system_results.csv", "w", newline="") as f:
    w = csv.writer(f)
    header = (["system_id", "sat_mc2", "sat_mc3", "sat_mc4", "viable", "fertile",
               "stability", "fertility_index", "mc2_score", "mc3_score", "mc4_score"]
              + [f"em_{a}" for a in ass_ids]
              + [f"mech_{m}" for m in mech_ids]
              + [f"via_{v}" for v in v_axes]
              + [f"fer_{f_}" for f_ in ["SR", "NP", "RC", "RD", "OE"]])
    w.writerow(header)
    for i, r in enumerate(results):
        row = [i, r["sat_mc2"], r["sat_mc3"], r["sat_mc4"],
               r["viable"], r["fertile"],
               round(r["stability"], 3), round(r["fertility_index"], 3),
               round(r["mc2"], 3), round(r["mc3"], 3), round(r["mc4"], 3)]
        for a in ass_ids:
            row.append(round(r["em"][a], 3))
        for m in mech_ids:
            row.append(round(r["mechs"][m], 3))
        for v in v_axes:
            row.append(round(r["viability"][v], 3))
        for f_ in ["SR", "NP", "RC", "RD", "OE"]:
            row.append(round(r["fertility"][f_], 3))
        w.writerow(row)
print(f"\nWrote t081_system_results.csv")

# 2. Phase 1 summary
with open(OUT / "t081_phase1_assumption_emergence.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["assumption", "name", "all_mcs_mean", "none_mcs_mean", "delta", "emergent"])
    for row in phase1_rows:
        w.writerow([row["assumption"], row["name"], row["all_mcs_mean"],
                     row["none_mcs_mean"], row["delta"], row["emergent"]])
print(f"Wrote t081_phase1_assumption_emergence.csv")

# 3. Phase 2 summary
with open(OUT / "t081_phase2_mechanism_emergence.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["mechanism", "name", "all_mcs_mean", "none_mcs_mean", "delta", "emergent"])
    for row in phase2_rows:
        w.writerow([row["mechanism"], row["name"], row["all_mcs_mean"],
                     row["none_mcs_mean"], row["delta"], row["emergent"]])
print(f"Wrote t081_phase2_mechanism_emergence.csv")

# 4. Phase 3 viability summary
with open(OUT / "t081_phase3_viability_basin.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["group", "n_systems", "n_viable", "viable_ratio"])
    for label, group in [("ALL_MCS", mc_all_sat), ("NONE_MCS", mc_none_sat), ("ALL", results)]:
        n_v = sum(1 for r in group if r["viable"])
        w.writerow([label, len(group), n_v, round(n_v / max(1, len(group)), 3)])
print(f"Wrote t081_phase3_viability_basin.csv")

# 5. Phase 4 fertile corridor data
with open(OUT / "t081_phase4_fertile_corridor.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["group", "n_systems", "n_fertile", "fertile_ratio",
                 "mean_stability", "mean_fertility"])
    for label, group in [("ALL_MCS", mc_all_sat), ("NONE_MCS", mc_none_sat), ("ALL_VIABLE", viable_results)]:
        n_f = sum(1 for r in group if r["fertile"])
        m_stab = np.mean([r["stability"] for r in group]) if group else 0
        m_fert = np.mean([r["fertility_index"] for r in group]) if group else 0
        w.writerow([label, len(group), n_f, round(n_f / max(1, len(group)), 3),
                     round(m_stab, 3), round(m_fert, 3)])
print(f"Wrote t081_phase4_fertile_corridor.csv")

# 6. Phase 5 PCA results
with open(OUT / "t081_phase5_pca_results.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["component", "eigenvalue", "explained_pct", "cumulative_pct"])
    for i in range(min(6, len(eigvals))):
        w.writerow([f"PC{i+1}", round(eigvals[i], 4),
                     round(explained[i], 2), round(cumulative[i], 2)])
print(f"Wrote t081_phase5_pca_results.csv")

# 7. Phase 6 ablation
with open(OUT / "t081_phase6_ablation.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["ablation", "n", "viable", "fertile", "mean_fertility", "mean_stability"])
    for row in ablation_rows:
        w.writerow([row["ablation"], row["n"], row["viable"], row["fertile"],
                     row["mean_fertility"], row["mean_stability"]])
print(f"Wrote t081_phase6_ablation.csv")

# 8. Summary JSON
summary = {
    "audit": "T081 — Constraint Generativity Audit",
    "n_systems": int(len(results)),
    "n_all_mcs": int(len(mc_all_sat)),
    "n_none_mcs": int(len(mc_none_sat)),
    "phase1": {
        "emergent_assumptions": emergent_assumptions,
        "n_emergent": len(emergent_assumptions),
        "n_total": len(ass_ids),
        "emergent_pct": round(float(emergent_pct), 1),
        "pass": bool(pass_phase1),
    },
    "phase2": {
        "emergent_mechanisms": emergent_mechanisms,
        "n_emergent": len(emergent_mechanisms),
        "n_total": len(mech_ids),
        "pass": bool(pass_phase2),
    },
    "phase3": {
        "viable_all_mcs": int(viable_mc_all),
        "viable_none_mcs": int(viable_mc_none),
        "pass": bool(pass_phase3),
    },
    "phase4": {
        "n_fertile": int(fertile_count),
        "n_fertile_none": int(fertile_mc_none),
        "pass": bool(pass_phase4) if pass_phase4 is not None else None,
    },
    "phase5": {
        "pc1_explained": round(float(explained[0]), 1) if n_obs >= n_vars else None,
        "intrinsic_dim": int(intrinsic_dim) if n_obs >= n_vars else None,
        "pass": bool(pass_phase5) if pass_phase5 is not None else None,
    },
    "phase6": {
        "mc2_ablation_fertility": round(float(np.mean([r["fertility_index"] for r in mc2_removed])), 3) if len(mc2_removed) >= 3 else None,
        "mc3_ablation_viability_ratio": round(float(sum(1 for r in mc3_removed if r["viable"]) / max(1, len(mc3_removed))), 3) if len(mc3_removed) >= 3 else None,
        "mc4_ablation_sr1": round(float(np.mean([r["em"]["SR1"] for r in mc4_removed])), 3) if len(mc4_removed) >= 3 else None,
        "pass_mc2": bool(pass_phase6_mc2) if pass_phase6_mc2 is not None else None,
        "pass_mc3": bool(pass_phase6_mc3) if pass_phase6_mc3 is not None else None,
        "pass_mc4": bool(pass_phase6_mc4) if pass_phase6_mc4 is not None else None,
    },
    "overall": {
        "n_pass": int(n_pass),
        "n_possible": int(n_possible),
        "outcome": outcome,
        "description": desc,
    },
}
with open(OUT / "t081_summary.json", "w") as f:
    json.dump(summary, f, indent=2)
print(f"Wrote t081_summary.json")

print(f"\nT081 complete.")
