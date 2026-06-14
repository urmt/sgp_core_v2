#!/usr/bin/env python3
"""
T091: Construct Validity Audit
===============================
Objective: For each of the 9 substrate assumptions, compare the original
theoretical definition against the operational measurement, identify
threats to construct validity, and classify validity level.

For each assumption:
  1. Original SFH-SGP theoretical definition
  2. Operational definition used in T082/T089/T090
  3. Exact measurement formula
  4. Dependence on simulator architecture
  5. Dependence on scoring choices
  6. Construct validity assessment
  7. Specific threats to validity

Output: t091_validity_matrix.csv, t091_report.md
"""

import csv, json
from pathlib import Path
from collections import OrderedDict

OUT = Path("/home/student/sgp_core_v2/sfh_sgp_ood_outputs")

# ============================================================
# COMPLETE SPECIFICATION FOR EACH ASSUMPTION
# ============================================================

assumptions = OrderedDict()

# ── OC2: Distinguishability ──────────────────────────────
assumptions["OC2"] = {
    "name": "Distinguishability",

    "theoretical_definition": (
        "Things can be told apart — difference exists prior to any investigation. "
        "The phenomenon and the investigation of it are distinguishable "
        "(even if inseparable in practice)."
    ),
    "theoretical_source": "T061 (line 69), T080 (line 36)",

    "operational_definition": (
        "Ratio of distinct transition-pattern types to total number of states. "
        "Each state's outgoing transitions (T[row] > 0.01) form a pattern; "
        "unique patterns are counted and divided by n_actual."
    ),
    "operational_source": "T082 measure_oc2() (lines 324-329)",
    "formula": "OC2 = min(1.0, len(unique({set(T[i] > 0.01) for i in range(n)})) / n)",

    "params_used": ["T_matrix", "n_actual"],
    "simulator_dependence": (
        "HIGH — depends on T_matrix (explicit probabilistic transition matrix per state). "
        "Requires row-stochastic matrix with rows per state. In CA/RBN/CML, T_matrix is "
        "reconstructed from observed transitions, which compresses the full dynamics into "
        "a finite matrix. The 0.01 threshold assumes probabilistic (not deterministic) "
        "transitions."
    ),
    "scoring_dependence": (
        "MODERATE — the 0.01 epsilon cutoff determines whether near-zero probabilities "
        "are counted as transitions. Normalization by n_actual penalizes larger state "
        "spaces. The set-based pattern comparison loses information about transition "
        "probabilities (two rows with different probability distributions but same support "
        "are treated as identical)."
    ),

    "construct_validity": "LOW-MODERATE",
    "validity_assessment": (
        "The theoretical concept is broad and philosophical: difference exists prior to "
        "investigation, observer and observed are distinguishable. The operational measure "
        "captures a narrow technical version: states have distinguishable successor sets. "
        "While this IS one form of distinguishability, it does not capture the intended "
        "meaning of observer-observed distinction or transcendental difference. "
        "The 'phenomenon vs investigation' distinction is not measured at all — the "
        "operational metric only distinguishes states from each other within the system."
    ),
    "threats": [
        "Category error: distinguishes states, not observer from phenomenon",
        "T_matrix must be pre-computed (circular for non-Markov substrates)",
        "0.01 threshold is arbitrary — changes pattern classification",
        "Set comparison discards probability information"
    ],

    "t090_verdict": "Primitive (99-100% in all substrates)",
    "remediation": (
        "If OC2 is to remain a theoretical primitive, it should be acknowledged as a "
        "pre-empirical axiom, not an empirically measured property. The operational "
        "metric should either be abandoned or re-labeled as 'state distinguishability' "
        "to avoid conflating measurement with ontology."
    ),
}

# ── OC1: Stable Structure / Boundedness ──────────────────
assumptions["OC1"] = {
    "name": "Stable Structure (Boundedness)",

    "theoretical_definition": (
        "Things persist enough to be recognized across moments. "
        "The phenomenon under study has some stable structure — "
        "it is not pure randomness or noise."
    ),
    "theoretical_source": "T061 (line 63), T080 (line 41)",

    "operational_definition": (
        "Inverted recurrence rate over the last 20 history steps. "
        "High OC1 means few distinct states appear recently (high repeat rate)."
    ),
    "operational_source": "T082 measure_oc1() (lines 331-337)",
    "formula": "OC1 = 1.0 - (len(set(history[-20:])) / 20)",

    "params_used": ["history"],
    "simulator_dependence": (
        "LOW — only depends on history sequence. Compatible with any substrate "
        "that produces a discrete-state trajectory."
    ),
    "scoring_dependence": (
        "HIGH — the window size (20) is arbitrary. A system with period-21 behavior "
        "would show different OC1 depending on which 20-step segment is sampled. "
        "The inversion means OC1 is HIGH when the system is REPETITIVE (few distinct "
        "states), whereas the theoretical concept is about having ANY structure at all. "
        "A system with 20 unique states and a clear periodic pattern (objectively "
        "structured) gets OC1=0, conflating 'no structure' with 'many states.'"
    ),

    "construct_validity": "LOW",
    "validity_assessment": (
        "CRITICAL MISMATCH. The theoretical OC1 is about the EXISTENCE of stable "
        "structure — that the phenomenon is not pure noise. The operational measure "
        "captures REPETITIVENESS (few distinct states in recent window). These are "
        "different constructs. A system with rich structured dynamics (e.g., a "
        "deterministic CA rule 30 with period-127 behavior across 50 cells) has "
        "extremely high structure but low OC1 by this metric because it produces "
        "many distinct states. Conversely, a trivial 2-state oscillator gets OC1≈0.9. "
        "The operational measure rewards triviality and penalizes complexity."
    ),
    "threats": [
        "Inversion error: structure ≠ repetitiveness",
        "Window size (20) is arbitrary and underspecified",
        "Rewards trivial fixed points over complex structured dynamics",
        "Doesn't distinguish between structure and stagnation"
    ],

    "t090_verdict": "Implementation-dependent (41.8-94.8%)",
    "remediation": (
        "Replace with a genuine structure measure: permutation entropy, "
        "Lempel-Ziv complexity, or autocorrelation structure. "
        "The operational measure should assess 'non-randomness,' not 'repetitiveness.'"
    ),
}

# ── CD1: Causal Relations Exist ───────────────────────────
assumptions["CD1"] = {
    "name": "Causal Relations Exist",

    "theoretical_definition": (
        "Changes have causes — events are not arbitrary. "
        "Causal, dependency, or explanatory relationships exist between "
        "elements of the phenomenon."
    ),
    "theoretical_source": "T061 (line 151), T080 (line 46)",

    "operational_definition": (
        "Weighted sum of the determinism parameter (40%) and empirical "
        "transition consistency (60%). Consistency = for each state visited "
        "at least twice, fraction of transitions to its most common successor."
    ),
    "operational_source": "T082 measure_cd1() (lines 339-355)",
    "formula": "CD1 = determinism * 0.4 + mean(most_common_ratio_per_state) * 0.6",

    "params_used": ["determinism (parameter)", "history"],
    "simulator_dependence": (
        "HIGH — uses the determinism parameter directly, which is an input "
        "to the simulator. This parameter is not a measured property of the "
        "system. Non-Markov substrates (CA, CML) don't have a determinism "
        "parameter, so only the empirical consistency component is available."
    ),
    "scoring_dependence": (
        "HIGH — the 40/60 weight split is arbitrary with no theoretical "
        "justification. The 'most common successor' metric ignores multi-modal "
        "causality (a state might have two equally likely outcomes). "
        "The guard (len(history) < 5 → 0) creates a hard cutoff. "
        "States visited only once contribute zero to consistency even if "
        "they would have deterministic behavior."
    ),

    "construct_validity": "MODERATE",
    "validity_assessment": (
        "The operational measure partially captures the theoretical construct. "
        "Causal relations mean that state transitions are not arbitrary, and "
        "the consistency metric does measure whether states have predictable "
        "outcomes. However, the 40% weight on a simulator parameter (not an "
        "observed property) contaminates the measurement with input assumptions. "
        "In non-Markov substrates, the parameter component is unavailable, "
        "making the measurement inconsistent across substrates."
    ),
    "threats": [
        "40% weight is a simulator configuration, not an observation",
        "40/60 weight split is arbitrary",
        "Most-common-ratio misses multi-modal causality",
        "Rarely-visited states are underweighted",
        "Measurement is inconsistent across substrates"
    ],

    "t090_verdict": "Implementation-dependent (10.2-100%)",
    "remediation": (
        "Remove the parameter component entirely; use only empirical "
        "transition consistency. Replace 'most common successor' with "
        "conditional entropy or transfer entropy for richer causal assessment."
    ),
}

# ── IC1: Extractable Information ──────────────────────────
assumptions["IC1"] = {
    "name": "Extractable Information",

    "theoretical_definition": (
        "Differences can be registered — structure is detectable. "
        "There is information about the phenomenon that the investigation "
        "can extract and process."
    ),
    "theoretical_source": "T061 (line 132), T080 (line 53)",

    "operational_definition": (
        "Amplified average branching factor: for each state, the number "
        "of distinct successor states observed, normalized by n_actual, "
        "averaged across all states, then amplified by 1.5x."
    ),
    "operational_source": "T082 measure_ic1() (lines 357-370)",
    "formula": "IC1 = min(1.0, mean(len(distinct_successors(s)) / n_actual for s in states) * 1.5)",

    "params_used": ["history", "n_actual"],
    "simulator_dependence": (
        "EXTREME — requires probabilistic branching (multiple distinct "
        "successor states). In deterministic substrates (CA, CML), each "
        "state has exactly one successor, giving IC1 ≈ 0 regardless of "
        "how much information is extractable. This is the root cause of "
        "the T090 finding that IC1 is a Markov artifact."
    ),
    "scoring_dependence": (
        "HIGH — the 1.5x amplification factor has no theoretical basis. "
        "Normalization by n_actual creates an inverse relationship with "
        "system size (larger state spaces produce lower IC1 for the same "
        "branching structure). The set-based successor counting treats "
        "all distinct successors equally regardless of probability."
    ),

    "construct_validity": "LOW",
    "validity_assessment": (
        "FUNDAMENTAL MISMATCH. The theoretical concept is about information "
        "being extractable — an observer can register differences. The "
        "operational measure captures branching diversity — how many "
        "different outcomes a state can lead to. These are inversely related: "
        "a deterministic system (one successor per state) has maximally "
        "extractable information (outcome is perfectly predictable) but "
        "minimal IC1. A maximally random system (all outcomes equally "
        "likely from every state) has maximal IC1 but minimal extractable "
        "information (nothing is predictable). The metric inverts the "
        "theoretical construct."
    ),
    "threats": [
        "Inversion: branching diversity ≠ extractable information",
        "1.5x amplification is arbitrary",
        "Deterministic systems score near zero despite high extractability",
        "Normalization by n_actual conflates information with state space size",
        "Set-based counting loses probability information"
    ],

    "t090_verdict": "Markov artifact (0-100%)",
    "remediation": (
        "Replace with an actual information-theoretic measure: mutual "
        "information between consecutive states, or Shannon entropy of "
        "the transition distribution. If the theoretical construct is "
        "'information can be extracted,' then the metric should measure "
        "how much information is available, not how many branches exist."
    ),
}

# ── IS1: Phase Structure / Investigative Change ────────────
assumptions["IS1"] = {
    "name": "Phase Structure (Investigative Change)",

    "theoretical_definition": (
        "The investigation changes what it investigates over time. "
        "The investigation is a process with identifiable stages, "
        "phases, or states."
    ),
    "theoretical_source": "T061 (line 44), T080 (line 59)",

    "operational_definition": (
        "Fraction of adjacent 5-step blocks whose state sets differ. "
        "History is split into contiguous 5-step blocks; each block is "
        "compared to the previous block as a set; the fraction of "
        "block-boundaries with composition change is the IS1 score."
    ),
    "operational_source": "T082 measure_is1() (lines 372-380)",
    "formula": "IS1 = min(1.0, count(set(block_i) != set(block_{i-1})) / (num_blocks - 1))",

    "params_used": ["history"],
    "simulator_dependence": (
        "LOW — only depends on history sequence. Compatible with any "
        "discrete-state trajectory substrate."
    ),
    "scoring_dependence": (
        "HIGH — block size (5) and stride (5) are arbitrary. A system "
        "with period-6 dynamics would show different IS1 than period-4 "
        "dynamics due to block alignment. Set comparison (rather than "
        "sequence comparison) loses ordering information within blocks. "
        "Two blocks with the same states in different orders are treated "
        "as identical, even though the order change might indicate a "
        "phase transition."
    ),

    "construct_validity": "MODERATE",
    "validity_assessment": (
        "The operational measure partially captures the construct. "
        "'Phase structure' = the trajectory has identifiable stages, "
        "and block-composition change is one reasonable proxy for "
        "stage boundaries. However, the specific choice of block size "
        "(5) imposes a particular timescale on what counts as a 'phase.' "
        "A better measure would allow the timescale to emerge from the data. "
        "The set comparison loses the sequence-level structure within each "
        "phase (e.g., whether phase-internal dynamics are stable or chaotic)."
    ),
    "threats": [
        "Block size (5) is arbitrary — determines what counts as a phase",
        "Set comparison loses sequential structure within blocks",
        "Stride=5 means overlapping shifts are ignored",
        "Doesn't detect hierarchical or nested phase structures"
    ],

    "t090_verdict": "Implementation-dependent (23.2-100%)",
    "remediation": (
        "Use recurrence quantification analysis or change-point detection "
        "to identify phase boundaries from data rather than imposing them. "
        "Alternatively, make block size a parameter and test robustness."
    ),
}

# ── IS2: Determinate Outputs / Coincidence ────────────────
assumptions["IS2"] = {
    "name": "Determinate Outputs (Coincidence)",

    "theoretical_definition": (
        "The investigation produces determinate results — outputs that "
        "can be compared across phases. If results were random or "
        "incomparable, no pattern could be detected."
    ),
    "theoretical_source": "T061 (line 50), T080 (line 65)",

    "operational_definition": (
        "If the last 10 history steps contain <= 2 unique states → 1.0. "
        "Otherwise → min(0.5, 5.0 / len(unique(recent))). "
        "This creates a floor at 0.5 for any system with >2 unique states."
    ),
    "operational_source": "T082 measure_is2() (lines 382-389)",
    "formula": "IS2 = 1.0 if len(unique(history[-10:])) <= 2 else min(0.5, 5.0/len(unique(history[-10:])))",

    "params_used": ["history"],
    "simulator_dependence": (
        "LOW — only depends on history. Compatible with any discrete-state substrate."
    ),
    "scoring_dependence": (
        "EXTREME — the 0.5 floor ensures no system with >2 states in the "
        "last 10 steps scores below 0.5. The shortcut (<=2 states → 1.0) "
        "is reachable only by nearly-converged systems. The min(0.5, ...) "
        "clamp means most systems get exactly 0.5 regardless of their "
        "actual diversity. IS2 is primarily a measurement floor artifact."
    ),

    "construct_validity": "VERY LOW",
    "validity_assessment": (
        "CRITICAL MISMATCH. The theoretical concept is about outputs being "
        "determinate (non-random, stable enough for comparison across phases). "
        "The operational measure captures recent state diversity with a "
        "floor at 0.5. This floor means the metric is almost entirely "
        "uninformative — it cannot distinguish between a highly diverse "
        "system and a moderately diverse one. The 'determinate outputs' "
        "construct is about COMPARABILITY across phases, not about the "
        "number of distinct states in a recent window. The operational "
        "measure doesn't address comparability at all."
    ),
    "threats": [
        "0.5 measurement floor makes the metric uninformative for most systems",
        "Window size (10) is arbitrary",
        "Doesn't measure comparability or determinateness",
        "Shortcut (≤2 states) conflates convergence with determinacy",
        "T090 confirmed this is a floor artifact (100% everywhere)"
    ],

    "t090_verdict": "Primitive (100% everywhere — floor artifact)",
    "remediation": (
        "Redesign from scratch: 'determinate outputs' should be measured as "
        "test-retest reliability, output variance under repeated identical "
        "conditions, or inter-annotator agreement. The current operational "
        "measure should be discarded."
    ),
}

# ── CD2: Self-Affecting Procedures ────────────────────────
assumptions["CD2"] = {
    "name": "Self-Affecting Procedures",

    "theoretical_definition": (
        "Procedures can affect themselves — feedback is possible. "
        "The investigation's procedures produce effects on the "
        "investigation itself or its object."
    ),
    "theoretical_source": "T061 (line 157), T080 (line 71)",

    "operational_definition": (
        "4-component weighted sum: self_model_level (capped at 2, ×0.4), "
        "self_model_influence (×0.3), self_correlation amplified 1.5x (×0.15), "
        "and a binary indicator for cycle > 2 (×0.15)."
    ),
    "operational_source": "T082 measure_cd2() (lines 391-399)",
    "formula": (
        "CD2 = min(1.0, min(1, sm/2)*0.4 + sm_i*0.3 + "
        "min(1, sc*1.5)*0.15 + (1 if cycle > 2 else 0)*0.15)"
    ),

    "params_used": ["self_model_level (parameter)", "self_model_influence (parameter)",
                    "self_correlation (metric)", "cycle_length (metric)"],
    "simulator_dependence": (
        "EXTREME — 70% of the weight comes from simulator parameters "
        "(self_model_level, self_model_influence) that are direct inputs "
        "to T082's simulator. These parameters have no equivalent in "
        "non-Markov substrates (CA, RBN, CML). The remaining 30% comes "
        "from history-derived metrics (self_correlation, cycle_length)."
    ),
    "scoring_dependence": (
        "HIGH — all weight values are arbitrary with no theoretical "
        "justification. self_model_level is saturated at 2 (levels 0,1 "
        "map to 0,0.5; levels 2,3 both map to 1.0). Self_correlation "
        "is amplified 1.5x. The cycle > 2 indicator is a binary threshold "
        "with no rationale for the choice of 2."
    ),

    "construct_validity": "LOW",
    "validity_assessment": (
        "FUNDAMENTAL CONTAMINATION. The theoretical concept is about "
        "procedural self-affection — that the methods of investigation "
        "affect the investigation itself. The operational measure is "
        "primarily a reading of simulator configuration parameters. "
        "This is a measurement of the model, not of the phenomenon. "
        "A system with high self_model_level and self_model_influence "
        "scores high on CD2 because it was DESIGNED to have self-affecting "
        "procedures, not because self-affection was observed to emerge."
    ),
    "threats": [
        "70% weight is simulator configuration, not observation",
        "Self_model_level is an input parameter, not an emergent property",
        "Weights are entirely arbitrary",
        "Binary threshold (cycle > 2) is unmotivated",
        "No non-Markov substrate can score high (T090 confirmed)"
    ],

    "t090_verdict": "Markov artifact (0-84.6%)",
    "remediation": (
        "Abandon the parametric approach entirely. Self-affecting procedures "
        "should be measured behaviorally: detect whether system state at time "
        "t+1 depends on system state at time t in a way that creates feedback "
        "loops (e.g., autocorrelation in transition patterns, or detection of "
        "second-order dynamics). The current measure conflates configuration "
        "with observation."
    ),
}

# ── EC1: Self-Knowledge ────────────────────────────────────
assumptions["EC1"] = {
    "name": "Self-Knowledge",

    "theoretical_definition": (
        "The investigation has access to its own state. "
        "The investigation can have knowledge about its own state and outputs."
    ),
    "theoretical_source": "T061 (line 88), T080 (line 77)",

    "operational_definition": (
        "3-component weighted sum: self_model_level/3 (×0.5), "
        "self_model_influence (×0.3), self_correlation (×0.2)."
    ),
    "operational_source": "T082 measure_ec1() (lines 401-405)",
    "formula": "EC1 = min(1.0, (sm/3)*0.5 + sm_i*0.3 + sc*0.2)",

    "params_used": ["self_model_level (parameter)", "self_model_influence (parameter)",
                    "self_correlation (metric)"],
    "simulator_dependence": (
        "EXTREME — 80% of the weight comes from simulator parameters. "
        "Same root problem as CD2: the measure reads the model configuration, "
        "not the phenomenon. The self_model parameters are specific to T082."
    ),
    "scoring_dependence": (
        "HIGH — weights are arbitrary. self_model_level/3 is a linear "
        "scaling with no theoretical basis. Self_correlation is used raw "
        "(not amplified like in CD2), creating inconsistency across the "
        "two measures that share the same theoretical grounding."
    ),

    "construct_validity": "LOW",
    "validity_assessment": (
        "FUNDAMENTAL CONTAMINATION. Same problem as CD2. The theoretical "
        "concept is epistemic — the system has knowledge of its own state. "
        "The operational measure is parametric — the simulator has a "
        "self_model_level parameter. These are categorically different "
        "things. 'Knowledge' is not measured by the simulator's internal "
        "configuration. The operational measure cannot distinguish between "
        "a system that genuinely monitors its own state and a system that "
        "simply has parameters that affect its behavior."
    ),
    "threats": [
        "80% weight is simulator configuration, not observed self-knowledge",
        "Self_model parameters are input assumptions",
        "Weights are arbitrary",
        "Cannot distinguish genuine self-monitoring from parameter effects",
        "T090 confirmed Markov-only (79.8% Markov, <1% elsewhere)"
    ],

    "t090_verdict": "Markov artifact (<1-79.8%)",
    "remediation": (
        "Replace with a behavioral measure of self-monitoring: detect whether "
        "the system's transition behavior changes as a function of its own "
        "recent history in a way that indicates state-awareness (e.g., "
        "state-dependent modulation of transition probabilities based on "
        "visit frequency). The current measure is uninterpretable as "
        "'self-knowledge.'"
    ),
}

# ── SR1: Self-Examination of Outputs ───────────────────────
assumptions["SR1"] = {
    "name": "Self-Examination of Outputs",

    "theoretical_definition": (
        "The investigation examines its own results, closing the loop. "
        "The investigation can examine its own outputs as objects of analysis."
    ),
    "theoretical_source": "T061 (line 25), T080 (line 83)",

    "operational_definition": (
        "Bifurcated by self_model_level: if sm < 2 → return sm * 0.3. "
        "If sm >= 2 → 4-component sum: sm/3 (×0.3), sm_influence (×0.3), "
        "binary cycle > 1 (×0.2), self_correlation (×0.2)."
    ),
    "operational_source": "T082 measure_sr1() (lines 407-414)",
    "formula": (
        "SR1 = sm*0.3 if sm < 2 else "
        "min(1.0, (sm/3)*0.3 + sm_i*0.3 + (1 if cycle>1 else 0)*0.2 + sc*0.2)"
    ),

    "params_used": ["self_model_level (parameter)", "self_model_influence (parameter)",
                    "cycle_length (metric)", "self_correlation (metric)"],
    "simulator_dependence": (
        "EXTREME — primary driver is self_model_level parameter. "
        "The bifurcation at sm=2 means the formula changes structurally "
        "based on a simulator configuration input."
    ),
    "scoring_dependence": (
        "EXTREME — the sm < 2 branch completely ignores all other metrics "
        "(self_correlation, cycle_length, sm_influence), returning a flat "
        "sm*0.3. This means a system with sm=1 and excellent self-examining "
        "behavior gets SR1=0.3 while a system with sm=2 and no actual "
        "self-examination gets SR1 potentially much higher. All weights "
        "in the full formula are arbitrary."
    ),

    "construct_validity": "VERY LOW",
    "validity_assessment": (
        "CRITICAL FAILURE. The theoretical concept is the capstone of the "
        "entire substrate: the investigation examines its own outputs, "
        "closing the recursive loop. The operational measure is entirely "
        "driven by a simulator parameter. The bifurcation at sm < 2 means "
        "the measure has a built-in threshold below which self-examination "
        "is declared impossible regardless of actual system behavior. This "
        "pre-judges the phenomenon. The theoretical concept of 'examination "
        "of outputs' — a recursive epistemic loop — is nowhere captured "
        "by the parametric formula."
    ),
    "threats": [
        "Entirely driven by simulator configuration, not observation",
        "sm < 2 bifurcation pre-judges self-examination as impossible",
        "Low-sm systems ignore all behavioral metrics",
        " 'Examination of outputs' is not measured at all",
        "Weights are arbitrary",
        "T090 confirmed Markov-only (0-76%)"
    ],

    "t090_verdict": "Markov artifact (0-76%)",
    "remediation": (
        "Requires a fundamentally different approach. Self-examination of "
        "outputs should be measured by detecting whether the system's "
        "behavior at time t+k reflects analysis of its own output at time t — "
        "i.e., whether outputs become inputs to subsequent behavior. This "
        "would require tracking information flow from outputs back into "
        "the system's state, not reading simulator parameters."
    ),
}


# ============================================================
# VALIDITY CLASSIFICATION
# ============================================================

VALIDITY_LEVELS = ["VERY LOW", "LOW", "LOW-MODERATE", "MODERATE", "HIGH", "VERY HIGH"]

def main():
    print("=" * 72)
    print("T091: CONSTRUCT VALIDITY AUDIT")
    print("=" * 72)

    # ── Build validity matrix ──
    rows = []
    for aid, a in assumptions.items():
        v = a["construct_validity"]
        dep_sim = a["simulator_dependence"].split("—")[0].strip()
        dep_score = a["scoring_dependence"].split("—")[0].strip()
        t090 = a["t090_verdict"]
        rows.append({
            "assumption": aid,
            "name": a["name"],
            "construct_validity": v,
            "simulator_dependence": dep_sim,
            "scoring_dependence": dep_score,
            "t090_verdict": t090,
            "primary_threat": a["threats"][0],
        })

    # Write CSV
    with open(OUT / "t091_validity_matrix.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "assumption", "name", "construct_validity",
            "simulator_dependence", "scoring_dependence",
            "t090_verdict", "primary_threat"
        ])
        w.writeheader()
        w.writerows(rows)

    # ── Print summary ──
    print(f"\n{'─'*72}")
    print("VALIDITY MATRIX")
    print(f"{'─'*72}")
    print(f"{'ID':<6} {'Construct Validity':<20} {'Sim Dep':<12} {'Score Dep':<12} {'T090 Verdict':<22}")
    print(f"{'─'*72}")
    for r in rows:
        v = r["construct_validity"]
        print(f"{r['assumption']:<6} {v:<20} {r['simulator_dependence']:<12} "
              f"{r['scoring_dependence']:<12} {r['t090_verdict']:<22}")

    # ── Aggregate statistics ──
    print(f"\n{'─'*72}")
    print("AGGREGATE")
    print(f"{'─'*72}")
    levels = {}
    for r in rows:
        levels[r["construct_validity"]] = levels.get(r["construct_validity"], 0) + 1
    for level in VALIDITY_LEVELS:
        if level in levels:
            print(f"  {level}: {levels[level]}/9 assumptions")

    # ── Key findings ──
    print(f"\n{'─'*72}")
    print("KEY FINDINGS")
    print(f"{'─'*72}")

    findings = [
        ("Inversion errors (2/9)", "OC1, IC1", (
            "OC1 operationalizes 'structure' as 'repetitiveness' — a system with "
            "rich structured dynamics scores low. IC1 operationalizes 'extractable "
            "information' as 'branching diversity' — deterministic systems score near "
            "zero despite maximal extractability. Both metrics invert their construct."
        )),
        ("Parametric contamination (3/9)", "CD2, EC1, SR1", (
            "These three assumptions are primarily measured via simulator configuration "
            "parameters (self_model_level, self_model_influence). 70-80% of their "
            "score comes from how the simulator was configured, not from observed "
            "system behavior. They are measurements of the MODEL, not the PHENOMENON."
        )),
        ("Measurement floor artifact (1/9)", "IS2", (
            "IS2 has a built-in floor at 0.5, making it uninformative for the vast "
            "majority of systems. The floor ensures universal prevalence but measures "
            "almost nothing."
        )),
        ("Parameter leakage (1/9)", "CD1", (
            "40% of CD1's score comes from the determinism parameter — a simulator "
            "input, not an empirically observed property of causal structure."
        )),
        ("Moderately valid (2/9)", "CD1 (60% component), IS1", (
            "CD1's empirical consistency component (60%) captures transition "
            "regularity, a reasonable proxy for causal structure. IS1's block-change "
            "metric captures phase structure, though with arbitrary timescale choices."
        )),
        ("Narrow but aligned (1/9)", "OC2", (
            "OC2's metric (distinct transition patterns) is a valid measure of state "
            "distinguishability, but this is much narrower than the theoretical "
            "concept of 'observer-phenomenon distinction.' The label overclaims."
        )),
    ]

    for title, ids, desc in findings:
        print(f"\n  {title} ({ids}):")
        print(f"    {desc}")

    # ── Cross-reference with T090 ──
    print(f"\n{'─'*72}")
    print("CROSS-REFERENCE: T090 CLASSIFICATION vs CONSTRUCT VALIDITY")
    print(f"{'─'*72}")
    print(f"\n{'ID':<6} {'T090 Verdict':<22} {'Construct Validity':<20} {'Alignment':<12}")
    print(f"{'─'*60}")
    alignment_map = {
        "Primitive": "Weak — label overclaims",
        "Primitive (floor artifact)": "Weak — floor artifact",
        "Markov artifact": "Strong — explains artifact status",
        "Implementation-dependent": "Strong — partial validity explains variance",
    }
    for aid, a in assumptions.items():
        tv = a["t090_verdict"]
        # Determine alignment category
        if "Markov" in tv:
            align = "Strong — metric is simulator-bound"
        elif "Implementation" in tv:
            align = "Strong — partial validity"
        elif "Primitive" in tv and "artifact" in tv:
            align = "Weak — floor artifact, not construct"
        elif "Primitive" in tv:
            align = "Weak — label overclaims"
        else:
            align = "Unknown"
        print(f"{aid:<6} {tv:<22} {a['construct_validity']:<20} {align:<12}")

    # ── Recommendations ──
    print(f"\n{'─'*72}")
    print("RECOMMENDATIONS")
    print(f"{'─'*72}")

    print("""
  IMMEDIATE (label corrections):
    1. OC1: Re-label as 'State Repetitiveness' — not 'Stable Structure.'
       The current measure does not capture structural persistence.
    2. IC1: Re-label as 'Transition Branching' — not 'Extractable Information.'
       The current measure inverts the theoretical construct.
    3. IS2: Re-label as 'Recent State Diversity (Floored)' — not 'Determinate Outputs.'
       The current measure is a floor artifact, not a determinate-output metric.
    4. CD2/EC1/SR1: Re-label as 'Self-Model Configuration Level' — not their
       current theoretical labels. These measure simulator parameters, not phenomena.
    5. OC2: Accept as 'State Distinguishability' — a valid but narrow measure.

  STRUCTURAL (metric redesigns):
    6. OC1: Replace with permutation entropy or Lempel-Ziv complexity.
    7. IC1: Replace with mutual information or Shannon entropy of transitions.
    8. IS2: Replace with test-retest reliability or output variance measure.
    9. CD2/EC1/SR1: Replace with behavioral/observational measures of feedback,
       self-monitoring, and output-reincorporation respectively.

  PROGRAMMATIC:
    10. Distinguish between theoretical constructs (philosophical) and operational
        metrics (empirical). The current assumption labels span both levels
        without acknowledging the gap.
    11. Before running future simulations, audit the measurement for construct
        validity. If the metric cannot logically capture the construct, no
        amount of simulation will fix it.
    12. For the SFH-SGP program: the substrate assumptions are valid as
        DESIGN COMMITMENTS of the T082 simulator, but should not be treated
        as discovered universal properties until construct-valid metrics
        confirm them on non-Markov substrates.
""")

    # ── Write full JSON summary ──
    summary = {
        "audit": "T091 — Construct Validity Audit",
        "objective": "Compare theoretical definitions against operational measurements "
                     "for all 9 substrate assumptions",
        "validity_counts": {k: levels.get(k, 0) for k in VALIDITY_LEVELS},
        "assumptions": {},
    }

    for aid, a in assumptions.items():
        summary["assumptions"][aid] = {
            "name": a["name"],
            "construct_validity": a["construct_validity"],
            "t090_verdict": a["t090_verdict"],
            "simulator_dependence": a["simulator_dependence"][:200],
            "primary_threat": a["threats"][0],
            "remediation": a["remediation"],
        }

    with open(OUT / "t091_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"Wrote t091_validity_matrix.csv")
    print(f"Wrote t091_summary.json")
    print(f"\nT091 complete.")


if __name__ == "__main__":
    main()
