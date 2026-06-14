#!/usr/bin/env python3
"""
T060: Class Discrimination Matrix
=================================
Given 8 mechanism classes from T059, derive:
1. Distinctive predictions per class
2. Pairwise separation between classes
3. Logical constraints per class

No ranking. No elimination. No argument for any class.
Only consequences.
"""

import csv
from pathlib import Path

OUT = Path("/home/student/sgp_core_v2/sfh_sgp_ood_outputs")

# ============================================================
# CLASS PREDICTIONS
# ============================================================

PREDICTIONS = {
    "M01": {
        "name": "System cannot fully examine itself",
        "predictions": [
            "Any self-investigation with sufficient expressive power will eventually encounter unresolvable circularity, regardless of specific domain or methodology.",
            "The circularity is domain-independent; it appears across formal, computational, cognitive, and linguistic systems alike.",
            "Breaking the circularity requires introducing an external reference framework not itself subject to the same self-referential dynamic.",
            "Richer expressive resources produce more complex circularity, not less (expressive power and circularity depth are correlated).",
        ],
        "would_contradict": "A self-investigation of a sufficiently expressive system that terminates in a unique, non-circular, non-self-referential foundation.",
        "minimum_test": "Construct a maximally expressive system (capable of self-representation) and attempt a self-investigation; check whether any non-circular foundation can be established from within.",
    },
    "M02": {
        "name": "Procedure finds its own fixed point",
        "predictions": [
            "The result of the investigation is independent of starting point; different initial assumptions converge to the same recursive structure.",
            "The convergence is mathematically guaranteed given the operation's formal properties (monotonicity, continuity on a complete partial order).",
            "Changing the operation changes the fixed point; the convergence reveals properties of the operation, not properties of the target.",
            "The fixed point is reached in a finite number of steps for any finitely bounded analysis space.",
        ],
        "would_contradict": "Starting-point sensitivity (different initial assumptions producing structurally different results) or operation-independent convergence.",
        "minimum_test": "Systematically vary starting assumptions while holding the procedure fixed; measure whether results converge to a single structure.",
    },
    "M03": {
        "name": "Method determines result",
        "predictions": [
            "Changing the methodological approach (decomposition strategy, success criterion, stopping condition, audit rule) produces a different result.",
            "The recursion is absent or takes a structurally different form under a differently designed method.",
            "The phenomenon exhibits no intrinsic structure independent of method choice; all observed structure is method-imposed.",
            "Methodological pluralism yields multiple incompatible but internally consistent accounts of the same phenomenon.",
        ],
        "would_contradict": "A single method-independent result that persists across substantially different methodological approaches.",
        "minimum_test": "Redesign the core audit procedure with different success criteria or decomposition rules and compare results.",
    },
    "M04": {
        "name": "Observer and target inseparable",
        "predictions": [
            "The observed recursion changes when the observer's epistemic relationship to the target changes (distance, involvement, stance).",
            "No measurement result can be attributed solely to the target; every result describes the joint observer-observed system.",
            "Attempting to isolate the target from the observer by methodological refinement changes both; there is no isolation procedure that leaves the target undisturbed.",
            "The recursion is a property of the relational configuration, not of the target in isolation.",
        ],
        "would_contradict": "Observational invariance across substantially different observer stances, or a measurement that can be attributed solely to the target.",
        "minimum_test": "Hold the method fixed but vary the observer's relationship to the target (insider/outsider, participant/detached); check whether recursion structure changes.",
    },
    "M05": {
        "name": "Information exhausted",
        "predictions": [
            "All candidate classes will eventually become empirically indistinguishable; further processing produces more descriptions but no new discriminating constraints.",
            "The number of distinguishable states of the investigation decreases monotonically as processing continues beyond the information bound.",
            "Different starting investigative strategies converge to the same undifferentiated state once all discriminating information is consumed.",
            "New sources of genuine information about the target will break the recursion and produce new discriminating structure.",
        ],
        "would_contradict": "New discriminating constraints emerging from continued processing without new information sources, or persistent distinguishability beyond the information bound.",
        "minimum_test": "Compute the information-theoretic upper bound on discriminations obtainable from the available data; check whether the investigation has approached this bound.",
    },
    "M06": {
        "name": "Attractor/trap dynamics",
        "predictions": [
            "The same cyclic behavior repeats indefinitely without external intervention; the investigation cannot escape under its own动力.",
            "Small perturbations produce transient effects, but the dynamics return to the same attractor; the basin is locally stable.",
            "Only a sufficiently large qualitative perturbation — changing the procedure or introducing new operations — could produce escape from the attractor.",
            "All starting states within the basin of attraction converge to the same dynamic regime (same sequence of phases).",
        ],
        "would_contradict": "Spontaneous escape from the cyclic behavior without external intervention, or trajectory divergence from similar starting states within the basin.",
        "minimum_test": "Introduce a large qualitative perturbation to the investigative procedure and compare the post-perturbation trajectory to the pre-perturbation trajectory over an extended sequence.",
    },
    "M07": {
        "name": "Inquiry malformed at current level",
        "predictions": [
            "The recursion disappears or fundamentally changes when the guiding question is reformulated at a different conceptual level or in a different vocabulary.",
            "The same phenomenon exhibits no recursive dependency when examined by a discipline or framework with a sufficiently different conceptual architecture.",
            "The recursion is specific to the framing of the question, not the phenomenon; it is a symptom of a category error in the inquiry.",
            "No amount of methodological refinement within the current framework will resolve the recursion because the framework itself is the issue.",
        ],
        "would_contradict": "Framework-independent recursive structure that persists across fundamentally different conceptual vocabularies and question formulations.",
        "minimum_test": "Reformulate the core question in a different discipline's vocabulary (e.g., reframe as a biological, economic, or physical question) and observe whether recursion persists.",
    },
    "M08": {
        "name": "Recursion IS the phenomenon",
        "predictions": [
            "The recursion is stable and does not generate new information over time; it is the invariant structure the investigation was seeking.",
            "The recursion appears at every level of analysis equally; it is scale-invariant and not a transient feature of a particular depth of investigation.",
            "Attempting to 'solve' or 'escape' the recursion is a misunderstanding — the recursion is the answer, not an obstacle.",
            "Any non-recursive description of the phenomenon is less complete or less informative than the recursive one.",
        ],
        "would_contradict": "A non-recursive, non-circular description that is strictly more informative or more complete than the recursive description.",
        "minimum_test": "Check scale-invariance: analyze the recursion at multiple levels of analysis and verify it maintains the same structure. Attempt to construct a more informative non-recursive description.",
    },
}

# ============================================================
# LOGICAL CONSTRAINTS
# ============================================================

CONSTRAINTS = {
    "M01": {
        "must_be_true": "The system under investigation has sufficient expressive power to represent and examine itself. Self-reference is a meaningful operation in the investigative context.",
        "cannot_be_true": "A fully self-transparent system exists (one that can completely characterize itself). The investigation can achieve an external vantage point from within.",
        "unknown": "Whether the expressive power of the actual system under study (the audit process itself) exceeds the threshold for self-referential undecidability. Whether a suitable external reference framework exists and can be accessed.",
    },
    "M02": {
        "must_be_true": "The investigative procedure defines a monotonic/continuous operation on a partially ordered space. The space has a least element or bottom.",
        "cannot_be_true": "The operation is discontinuous or non-monotonic. The space lacks sufficient structure to guarantee fixed-point existence.",
        "unknown": "The exact mathematical structure of the operation space. Whether the procedure as implemented actually meets the formal criteria for guaranteed convergence to a least fixed point.",
    },
    "M03": {
        "must_be_true": "The methodological choices made in designing the investigation are contingent (could have been otherwise). There exists at least one alternative methodology that produces a different result.",
        "cannot_be_true": "The method is forced by the nature of the phenomenon (only one valid way to investigate). There is only one possible result regardless of method.",
        "unknown": "The full space of alternative methodologies. Whether any alternative method produces a non-recursive result. Whether method-independence is achievable in principle.",
    },
    "M04": {
        "must_be_true": "The observer is part of the same system as the target. There is a bidirectional causal or constitutive relationship between observer and observed at the relevant level.",
        "cannot_be_true": "The observer can achieve a fully external, non-interactive relationship to the target. Measurements can be unambiguously attributed to the target alone.",
        "unknown": "The exact nature and strength of the observer-observed coupling. Whether a different observer stance (more distant, more involved) would break or change the recursion.",
    },
    "M05": {
        "must_be_true": "There is a finite upper bound on the information extractable from the available data about the target. The investigation has extracted information approaching this bound.",
        "cannot_be_true": "The investigation can generate new information about the target from purely internal processing (without new data). Distinguishability is unbounded given the available data.",
        "unknown": "The exact information bound for this investigation. Whether genuinely new information about the target is obtainable from external sources. Whether the bound has been reached or is merely approached.",
    },
    "M06": {
        "must_be_true": "The investigation's dynamics are governed by an attractor in state space. The attractor has a basin that contains the investigation's current trajectory.",
        "cannot_be_true": "The investigation's dynamics are ergodic or exhibit sensitive dependence on initial conditions across the relevant state region. Spontaneous escape from the cyclic regime is possible.",
        "unknown": "The exact geometry and dimensionality of the attractor. The size and boundaries of its basin. The minimum perturbation required for escape. Whether escape is possible at all.",
    },
    "M07": {
        "must_be_true": "The question as formulated makes an implicit category error or operates at a level that cannot support the desired answer type. An alternative formulation exists.",
        "cannot_be_true": "The recursion is a direct property of the phenomenon itself, independent of how the inquiry is framed. The recursion is framework-independent.",
        "unknown": "Whether a suitable alternative formulation exists. Whether the alternative formulation produces a non-recursive result. Whether the category error is correctable or intrinsic to the question domain.",
    },
    "M08": {
        "must_be_true": "The recursion is stable, scale-invariant, and informative. There exists no non-recursive description that captures the same information without loss.",
        "cannot_be_true": "The recursion is a transient artifact of method choice or incomplete analysis. A non-recursive description with equal or greater informativeness exists.",
        "unknown": "Whether the recursion is genuinely scale-invariant. Whether the recursive description is the maximally informative description. Whether 'informativeness' is a well-defined measure here.",
    },
}

# ============================================================
# PAIRWISE SEPARATION
# ============================================================

def pairwise_separations():
    classes = sorted(PREDICTIONS.keys())
    rows = []
    for i, a in enumerate(classes):
        for b in classes[i+1:]:
            preds_a = set(PREDICTIONS[a]["predictions"])
            preds_b = set(PREDICTIONS[b]["predictions"])
            shared = preds_a & preds_b
            different = (preds_a - preds_b) | (preds_b - preds_a)

            # Determine possible discriminator
            discriminator = _discriminator(a, b)

            rows.append({
                "class_A": a,
                "class_B": b,
                "shared_predictions": len(shared),
                "different_predictions": len(different),
                "possible_discriminator": discriminator,
                "notes": _separation_notes(a, b),
            })
    return rows


def _discriminator(a, b):
    dm = {
        ("M01", "M02"): "Vary system expressive power: M01 predicts circularity depth correlates with expressiveness; M02 predicts same convergence regardless.",
        ("M01", "M03"): "Change method: M01 predicts any method within the system hits the same wall; M03 predicts different methods give different results.",
        ("M01", "M04"): "Vary observer stance: M01 predicts all stances within the system hit circularity; M04 predicts different stances produce different recursion.",
        ("M01", "M05"): "Introduce new information source: M05 predicts this breaks the recursion; M01 predicts the limitation is inherent regardless.",
        ("M01", "M06"): "Apply large perturbation: M06 predicts possible escape; M01 predicts escape requires external reference (not same as perturbation).",
        ("M01", "M07"): "Reformulate question at different level: M07 predicts recursion disappears; M01 predicts recursion reappears at new level if system remains self-referential.",
        ("M01", "M08"): "Evaluate whether the recursion produces new information (M01: yes, generative frustration) vs is stable and complete (M08). Scale-invariance test.",
        ("M02", "M03"): "Change method while holding operation properties fixed: M03 predicts different result; M02 predicts new fixed point for new operation.",
        ("M02", "M04"): "Vary observer relationship: M02 predicts convergence independent of observer; M04 predicts result changes with observer.",
        ("M02", "M05"): "Introduce new information sources: M05 predicts new structure; M02 predicts same fixed point regardless.",
        ("M02", "M06"): "Check trajectory behavior after convergence: M02 predicts stable rest; M06 predicts ongoing cycling around attractor.",
        ("M02", "M07"): "Reformulate question: M07 predicts recursion disappears; M02 predicts procedure finds a fixed point of the new operation.",
        ("M02", "M08"): "Check informativeness of result: M02 sees recursion as convergent limit (procedure exhausted its utility); M08 sees it as complete discovery.",
        ("M03", "M04"): "Hold method fixed, vary observer stance: M03 predicts same result (method determines); M04 predicts different result (observer matters).",
        ("M03", "M05"): "Introduce new information without changing method: M05 predicts new structure; M03 predicts same method-dependent result.",
        ("M03", "M06"): "Apply small perturbations: M03 predicts method still determines result; M06 predicts return to same attractor. Vary method: M03 predicts different results; M06 predicts same attractor.",
        ("M03", "M07"): "Change method within same framework vs change framework: M07 requires framework change; M03 predicts method change within framework suffices.",
        ("M03", "M08"): "Method-independence test: M03 predicts result depends on method choice; M08 predicts recursion is method-independent (it IS the phenomenon).",
        ("M04", "M05"): "Introduce new information sources: M05 predicts new structure; M04 predicts observer relation still colors any new information.",
        ("M04", "M06"): "Change observer stance vs perturb dynamics: M04 predicts stance change (even small) changes result; M06 predicts small perturbations are absorbed by attractor.",
        ("M04", "M07"): "Change observer stance vs reformulate question: M04 predicts stance change suffices; M07 predicts deeper category-level change needed.",
        ("M04", "M08"): "Vary observer: M04 predicts recursion changes with observer; M08 predicts recursion is invariant (it IS the phenomenon).",
        ("M05", "M06"): "Introduce new information: M05 predicts this changes result; M06 predicts new info within basin is absorbed by attractor.",
        ("M05", "M07"): "Introduce new information vs new framework: M05 predicts new info from any source suffices; M07 predicts framework change needed (new info within same framework insufficient).",
        ("M05", "M08"): "New information test: M05 predicts recursion is artifact of depletion; M08 predicts recursion persists even with new information.",
        ("M06", "M07"): "Perturb dynamics vs reformulate question: M06 predicts large dynamic perturbation escapes; M07 predicts framework change escapes (dynamic perturbation may not suffice).",
        ("M06", "M08"): "Check whether recursion is stable and informative (M08) vs a trap preventing progress (M06). Scale-invariance test.",
        ("M07", "M08"): "Reformulate question: M07 predicts recursion disappears with correct framing; M08 predicts recursion persists as it IS the phenomenon.",
    }
    key = (a, b) if (a, b) in dm else (b, a) if (b, a) in dm else None
    return dm.get(key, "No obvious discriminator identified")


def _separation_notes(a, b):
    notes = {
        ("M01", "M02"): "Both predict circularity, but M01 attributes it to self-reference limits and M02 to mathematical convergence. M01 is domain-independent; M02 is procedure-dependent.",
        ("M01", "M03"): "Fundamentally different: M01 says the system cannot avoid recursion; M03 says the method imposes it. Clear experimental separation possible.",
        ("M01", "M04"): "Related: both involve the relationship between investigator and investigated. M01 emphasizes system limits; M04 emphasizes inseparability.",
        ("M01", "M05"): "Different causal mechanisms: M01 = self-reference bound; M05 = information bound. May produce similar surface behavior.",
        ("M01", "M06"): "Different emphasis: M01 = structural limit; M06 = dynamical trap. Potentially compatible descriptions of same situation at different levels.",
        ("M01", "M07"): "M01 and M07 share the idea that recursion is a symptom, not the phenomenon. M01 says the system is limited; M07 says the question is wrong.",
        ("M01", "M08"): "Directly opposed: M01 says recursion is failure; M08 says it is success. Cannot both be correct in same sense.",
        ("M02", "M03"): "Close cousins: M02 emphasizes mathematical necessity of convergence; M03 emphasizes contingency of method choice. Could collapse if method choice is shown to be forced.",
        ("M02", "M04"): "Potentially compatible: M02 describes procedure behavior; M04 describes observer relation. M04 predicts M02's operation is observer-dependent.",
        ("M02", "M05"): "Different mechanisms: M02 = guaranteed convergence; M05 = information depletion. Same surface (all candidates collapse) but different cause.",
        ("M02", "M06"): "Different dynamic predictions: M02 converges to rest; M06 cycles. Distinguishable by trajectory shape over extended phases.",
        ("M02", "M07"): "M02 says the procedure does what procedures do (find fixed points); M07 says the procedure shouldn't be doing this at all.",
        ("M02", "M08"): "Different evaluation of same formal fact: M02 says procedure exhausted; M08 says procedure succeeded.",
        ("M03", "M04"): "Strong overlap: both say the result depends on how you approach the target. M03 emphasizes method design; M04 emphasizes observer position.",
        ("M03", "M05"): "Different intervention predictions: M03 says change method; M05 says find new data. Could be distinguished by which intervention changes the result.",
        ("M03", "M06"): "M03 predicts method change changes everything; M06 predicts small method changes are absorbed. Distinguishable by perturbation size effect.",
        ("M03", "M07"): "M03 allows escape by method refinement within framework; M07 requires framework change. Distinguishable by depth of change needed.",
        ("M03", "M08"): "M03 sees recursion as contingent on method; M08 sees it as necessary. Directly opposed.",
        ("M04", "M05"): "Compatible in principle: observer relation determines what counts as information. Distinguishable by what intervention resolves recursion.",
        ("M04", "M06"): "M04 predicts observer stance change (potentially small) changes result; M06 predicts small changes are absorbed. Directly testable.",
        ("M04", "M07"): "Both involve 'changing perspective' but at different levels: observer stance vs conceptual framework. Potentially nested.",
        ("M04", "M08"): "Opposed: M04 says recursion is observer-relative; M08 says it is invariant. Directly testable by varying observer.",
        ("M05", "M06"): "Different mechanisms: information depletion vs dynamical entrapment. Same surface (all look same). Distinguishable by whether new info changes result.",
        ("M05", "M07"): "Different: M05 says new info (any source) suffices; M07 says framework change needed. New info within same framework distinguishes them.",
        ("M05", "M08"): "Opposed on whether recursion is artifact or essence. Test: does new information produce non-recursive structure?",
        ("M06", "M07"): "Both predict escape is possible but via different routes (dynamic perturbation vs framework change). Distinguishable by which works.",
        ("M06", "M08"): "Opposed: M06 says recursion is a trap to escape; M08 says it is the found phenomenon. Normative tension.",
        ("M07", "M08"): "Directly opposed on whether recursion is a symptom of error (M07) or the correct answer (M08). Most fundamental split in the landscape.",
    }
    return notes.get((a, b), notes.get((b, a), ""))


# ============================================================
# WRITE OUTPUTS
# ============================================================

# 1. Discrimination matrix
with open(OUT / "t060_discrimination_matrix.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["class_id", "class_name", "prediction_1", "prediction_2", "prediction_3",
                 "prediction_4", "would_contradict", "minimum_test"])
    for cid in sorted(PREDICTIONS.keys()):
        p = PREDICTIONS[cid]
        preds = p["predictions"]
        w.writerow([cid, p["name"],
                     preds[0] if len(preds) > 0 else "",
                     preds[1] if len(preds) > 1 else "",
                     preds[2] if len(preds) > 2 else "",
                     preds[3] if len(preds) > 3 else "",
                     p["would_contradict"],
                     p["minimum_test"]])

print("Wrote t060_discrimination_matrix.csv")

# 2. Pairwise separation
rows = pairwise_separations()
with open(OUT / "t060_pairwise_separation.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["class_A", "class_B", "shared_predictions", "different_predictions",
                 "possible_discriminator", "notes"])
    for r in rows:
        w.writerow([r["class_A"], r["class_B"], r["shared_predictions"],
                     r["different_predictions"], r["possible_discriminator"],
                     r["notes"]])

print(f"Wrote t060_pairwise_separation.csv ({len(rows)} pairs)")

# 3. Constraint table
with open(OUT / "t060_constraint_table.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["class_id", "must_be_true", "cannot_be_true", "unknown"])
    for cid in sorted(CONSTRAINTS.keys()):
        c = CONSTRAINTS[cid]
        w.writerow([cid, c["must_be_true"], c["cannot_be_true"], c["unknown"]])

print("Wrote t060_constraint_table.csv")

print("\nT060 complete. No classes ranked. No classes eliminated. No arguments for any class.")
