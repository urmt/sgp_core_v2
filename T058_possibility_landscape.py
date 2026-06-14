#!/usr/bin/env python3
"""
T058: Possibility Landscape Survey
====================================
Build a structured inventory of candidate explanations for why
the investigation repeatedly encounters recursive dependency structures.

Do NOT evaluate. Do NOT rank. Do NOT destroy. Just collect.
"""

import csv, json
from pathlib import Path

OUT = Path("/home/student/sgp_core_v2/sfh_sgp_ood_outputs")

# ============================================================
# CANDIDATE EXPLANATION FAMILIES
# ============================================================

CANDIDATES = [
    # ---- 1. COMPUTATIONAL ----
    {
        "id": "C001",
        "family": "computational",
        "short_description": "Bounded state space forces recurrence",
        "core_mechanism": "Any finite computational system will eventually revisit states. The audit procedure investigates a finite space; recursion is inevitable.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "partial",
        "predicts_collapse": "yes",
        "confidence": "high",
    },
    {
        "id": "C002",
        "family": "computational",
        "short_description": "Halting problem analogy",
        "core_mechanism": "The question 'does this statement have a foundation?' is analogous to the halting problem — undecidable for arbitrary statements.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },
    {
        "id": "C003",
        "family": "computational",
        "short_description": "Gödel incompleteness",
        "core_mechanism": "The investigation's formal system contains statements that cannot be proven or disproven within the system. The search for foundation hits a Gödel sentence.",
        "predicts_recursion": "partial",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "medium",
    },
    {
        "id": "C004",
        "family": "computational",
        "short_description": "Complexity-class barrier",
        "core_mechanism": "The recursion-detection problem belongs to a complexity class (e.g., PSPACE-complete, EXPTIME) that makes exhaustive search intractable.",
        "predicts_recursion": "no",
        "predicts_self_audit": "no",
        "predicts_collapse": "partial",
        "confidence": "low",
    },
    {
        "id": "C005",
        "family": "computational",
        "short_description": "Fixed-point combinator structure",
        "core_mechanism": "The audit procedure Y = λf.(λx.f(xx))(λx.f(xx)) is structurally a fixed-point combinator. It finds fixed points of its own operation because it IS a fixed-point combinator.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },
    {
        "id": "C006",
        "family": "computational",
        "short_description": "Turing completeness of the audit language",
        "core_mechanism": "The language used to describe and audit statements is Turing-complete, which guarantees the existence of non-terminating computations and self-referential statements.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },

    # ---- 2. INFORMATION-THEORETIC ----
    {
        "id": "C007",
        "family": "information_theoretic",
        "short_description": "Kolmogorov complexity minimum is uncomputable",
        "core_mechanism": "The 'first primitive' corresponds to the shortest description of the observed data. But Kolmogorov complexity is uncomputable — we can never be sure we've found the minimum.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },
    {
        "id": "C008",
        "family": "information_theoretic",
        "short_description": "Mutual information saturation",
        "core_mechanism": "All candidates share approximately the same mutual information with the observed data. No candidate is more informative than any other, making selection impossible.",
        "predicts_recursion": "partial",
        "predicts_self_audit": "no",
        "predicts_collapse": "yes",
        "confidence": "medium",
    },
    {
        "id": "C009",
        "family": "information_theoretic",
        "short_description": "Data-processing inequality cascade",
        "core_mechanism": "Each audit step loses information about the original phenomenon. After enough steps, the investigation is auditing its own artifacts, not the phenomenon.",
        "predicts_recursion": "no",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "medium",
    },
    {
        "id": "C010",
        "family": "information_theoretic",
        "short_description": "Maximum entropy of the hypothesis space",
        "core_mechanism": "The space of possible explanations is so large that the prior probability of any specific candidate is negligible. No candidate can be preferred on information grounds.",
        "predicts_recursion": "no",
        "predicts_self_audit": "no",
        "predicts_collapse": "yes",
        "confidence": "low",
    },
    {
        "id": "C011",
        "family": "information_theoretic",
        "short_description": "Fisher information singularity",
        "core_mechanism": "The investigation's question may be at a point where the Fisher information matrix is singular — parameters cannot be distinguished, producing apparent circularity.",
        "predicts_recursion": "partial",
        "predicts_self_audit": "no",
        "predicts_collapse": "partial",
        "confidence": "low",
    },
    {
        "id": "C012",
        "family": "information_theoretic",
        "short_description": "Rate-distortion ceiling",
        "core_mechanism": "There is a maximum rate at which information about 'foundations' can be extracted from the system. The investigation has reached this ceiling.",
        "predicts_recursion": "no",
        "predicts_self_audit": "no",
        "predicts_collapse": "yes",
        "confidence": "low",
    },

    # ---- 3. SELF-REFERENCE ----
    {
        "id": "C013",
        "family": "self_reference",
        "short_description": "Hofstadter strange loop",
        "core_mechanism": "The investigation is a strange loop — a hierarchical system that curls back on itself. Each level of audit reveals a higher level that is isomorphic to the previous.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },
    {
        "id": "C014",
        "family": "self_reference",
        "short_description": "Impredicative self-definition",
        "core_mechanism": "The 'first primitive' is defined in terms of a totality that includes it. Every attempt to define it from below fails because it is already presupposed.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },
    {
        "id": "C015",
        "family": "self_reference",
        "short_description": "Reflexive closure of the procedure",
        "core_mechanism": "The investigation has reached the reflexive closure of its own operation — the operation applied to itself produces the same operation. No escape is possible because there is no outside.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },
    {
        "id": "C016",
        "family": "self_reference",
        "short_description": "Autopoiesis of the audit system",
        "core_mechanism": "The audit system is autopoietic — it produces the components that produce it. It is organizationally closed and self-maintaining.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "no",
        "confidence": "medium",
    },
    {
        "id": "C017",
        "family": "self_reference",
        "short_description": "Quine-like self-generation",
        "core_mechanism": "Each phase is a Quine — it produces a description of itself that can be parsed by the next phase. The chain is self-sustaining like a Quine chain.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "partial",
        "confidence": "medium",
    },

    # ---- 4. OBSERVER-MODEL ----
    {
        "id": "C018",
        "family": "observer_model",
        "short_description": "Von Neumann regress",
        "core_mechanism": "Every observation requires an observer. Every observer requires another observation to verify. This regress is infinite — the investigation cannot find a first observer.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },
    {
        "id": "C019",
        "family": "observer_model",
        "short_description": "Measurement apparatus cannot be separated",
        "core_mechanism": "The investigation's detectors are entangled with what they detect. You cannot factor the measurement from the system in a unique way.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },
    {
        "id": "C020",
        "family": "observer_model",
        "short_description": "Bayesian prior dominates",
        "core_mechanism": "The recursive dependency structure reflects the prior implicit in the investigation's methodology, not anything about the world. Bayesian updating cannot converge without a non-zero prior on non-recursive structures.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },
    {
        "id": "C021",
        "family": "observer_model",
        "short_description": "Embedded observer",
        "core_mechanism": "The investigators are themselves part of the system they study. They cannot take an external view. All observations are self-observations.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },
    {
        "id": "C022",
        "family": "observer_model",
        "short_description": "Wigner's friend hierarchy",
        "core_mechanism": "Each audit level is a 'Wigner's friend' — what is a measurement at one level is a system at the next. The hierarchy of observers is unbounded.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "medium",
    },
    {
        "id": "C023",
        "family": "observer_model",
        "short_description": "Dark room problem",
        "core_mechanism": "If the only evidence available is the structure of the investigation itself, the optimal Bayesian explanation is 'nothing exists outside the investigation.' The recursion is a consequence of sensory deprivation.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "medium",
    },

    # ---- 5. LANGUAGE-STRUCTURE ----
    {
        "id": "C024",
        "family": "language_structure",
        "short_description": "Linguistic relativity (Whorfian)",
        "core_mechanism": "The language of the investigation (mathematics, formal logic) imposes a structure that appears as 'recursive dependency' but is actually just the grammar of the language. Different languages would find different structures.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "no",
        "predicts_collapse": "partial",
        "confidence": "medium",
    },
    {
        "id": "C025",
        "family": "language_structure",
        "short_description": "Definitional circularity is grammatical",
        "core_mechanism": "Every term is defined in terms of other terms. There is no bottom level of definition. The recursion is not a discovery — it is a property of definitional systems.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "no",
        "predicts_collapse": "yes",
        "confidence": "high",
    },
    {
        "id": "C026",
        "family": "language_structure",
        "short_description": "Semantic grounding problem",
        "core_mechanism": "Symbols cannot be grounded without reference to other symbols. The investigation's terms are ungrounded — they refer to each other in a closed loop.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },
    {
        "id": "C027",
        "family": "language_structure",
        "short_description": "Categorical grammar constraint",
        "core_mechanism": "The grammatical categories available to the investigation (noun, verb, relation, property) force certain patterns. The search for 'first' requires a noun, but the phenomenon may not be a noun.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "partial",
        "predicts_collapse": "yes",
        "confidence": "medium",
    },
    {
        "id": "C028",
        "family": "language_structure",
        "short_description": "Performative-constative collapse",
        "core_mechanism": "The investigation's statements are both descriptions (constative) and acts (performative). The collapse happens because the description changes what it describes.",
        "predicts_recursion": "no",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "medium",
    },
    {
        "id": "C029",
        "family": "language_structure",
        "short_description": "Tarski's undefinability of truth",
        "core_mechanism": "Truth cannot be defined within the language. The investigation's search for 'true primitives' is an attempt to define truth within the system, which Tarski proved impossible.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },

    # ---- 6. MATHEMATICAL FIXED-POINT ----
    {
        "id": "C030",
        "family": "mathematical_fixed_point",
        "short_description": "Kleene fixed-point theorem",
        "core_mechanism": "The audit procedure is a continuous function on a complete partial order. Its least fixed point is the recursive dependency structure — the minimal solution to the equation F(x)=x.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },
    {
        "id": "C031",
        "family": "mathematical_fixed_point",
        "short_description": "Lawvere's fixed-point theorem",
        "core_mechanism": "In any Cartesian closed category with a universal property, every endomorphism has a fixed point. The investigation is operating in such a category.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },
    {
        "id": "C032",
        "family": "mathematical_fixed_point",
        "short_description": "Cantor diagonalization",
        "core_mechanism": "The investigation constructs a diagonal argument: 'all explanations are in this list, but this one is not.' The collapse is the diagonal element that cannot be in the list.",
        "predicts_recursion": "no",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },
    {
        "id": "C033",
        "family": "mathematical_fixed_point",
        "short_description": "Initial algebra / terminal coalgebra misfit",
        "core_mechanism": "The investigation searches for an initial object (simplest foundation) but the system only has terminal objects (infinite regress). The direction of search is wrong.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },
    {
        "id": "C034",
        "family": "mathematical_fixed_point",
        "short_description": "Banach fixed-point theorem",
        "core_mechanism": "The audit procedure is a contraction mapping on the space of statements. Its fixed point is unique and can be found by iteration — which is exactly what the investigation does.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "medium",
    },
    {
        "id": "C035",
        "family": "mathematical_fixed_point",
        "short_description": "Löb's theorem",
        "core_mechanism": "Provability of a statement from within the system requires the system to already contain it. The search for foundations within the system can only find what the system already assumes.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },

    # ---- 7. CATEGORY-THEORETIC ----
    {
        "id": "C036",
        "family": "category_theoretic",
        "short_description": "No initial object in the category",
        "core_mechanism": "The category of statements and dependencies has no initial object — no statement from which all others uniquely derive. The search for a first statement fails categorically.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },
    {
        "id": "C037",
        "family": "category_theoretic",
        "short_description": "Yoneda insight: objects are relations",
        "core_mechanism": "The Yoneda lemma shows that objects in a category are determined by their relationships, not by intrinsic properties. 'What a thing is' IS its web of relations — the recursion IS the object.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "no",
        "confidence": "high",
    },
    {
        "id": "C038",
        "family": "category_theoretic",
        "short_description": "Free-forgetful adjunction failure",
        "core_mechanism": "The free-forgetful adjunction between 'unstructured' and 'structured' categories has a unit that is not injective. Not every structure can be forgotten to a unique unstructured base.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "partial",
        "confidence": "medium",
    },
    {
        "id": "C039",
        "family": "category_theoretic",
        "short_description": "Recursive coalgebra as minimal invariant",
        "core_mechanism": "The audit procedure forms a recursive coalgebra. The minimal invariant is the terminal coalgebra — the infinite regress itself. The investigation has found the minimal invariant.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },
    {
        "id": "C040",
        "family": "category_theoretic",
        "short_description": "Monad structure of the audit",
        "core_mechanism": "The audit procedure is a monad: it has a unit (wrapping a statement for audit) and a multiplication (flattening nested audits). The recursion is the monad's Kleisli composition.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "no",
        "confidence": "medium",
    },

    # ---- 8. DYNAMICAL-SYSTEM ----
    {
        "id": "C041",
        "family": "dynamical_system",
        "short_description": "Strange attractor in statement space",
        "core_mechanism": "The investigation's trajectory through statement space converges to a strange attractor — the recursive dependency structure. Different starting points all end up at the same attractor.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },
    {
        "id": "C042",
        "family": "dynamical_system",
        "short_description": "Bifurcation cascade",
        "core_mechanism": "The investigation has crossed a bifurcation point. Before the bifurcation, different phases gave different results. After, all phases converge to the same behavior.",
        "predicts_recursion": "no",
        "predicts_self_audit": "no",
        "predicts_collapse": "yes",
        "confidence": "medium",
    },
    {
        "id": "C043",
        "family": "dynamical_system",
        "short_description": "Limit cycle of the audit operator",
        "core_mechanism": "The investigation has entered a limit cycle. The sequence select→separate→examine→report→select→separate→... is a periodic orbit in the state space of the investigation.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },
    {
        "id": "C044",
        "family": "dynamical_system",
        "short_description": "Lyapunov exponent sign change",
        "core_mechanism": "The Lyapunov exponent of the investigation's dynamics changed sign, indicating a transition from exploration to entrapment. The system is now trapped in a basin of attraction.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "no",
        "predicts_collapse": "yes",
        "confidence": "low",
    },
    {
        "id": "C045",
        "family": "dynamical_system",
        "short_description": "Conservative vs dissipative transition",
        "core_mechanism": "The investigation transitioned from a conservative regime (preserving information across phases) to a dissipative regime (losing information). The collapse is energy dissipation.",
        "predicts_recursion": "no",
        "predicts_self_audit": "no",
        "predicts_collapse": "yes",
        "confidence": "low",
    },
    {
        "id": "C046",
        "family": "dynamical_system",
        "short_description": "Homoclinic tangle",
        "core_mechanism": "The stable and unstable manifolds of the investigation's fixed points intersect chaotically, producing a homoclinic tangle. The recursive structure is the tangle.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "low",
    },

    # ---- 9. EVOLUTIONARY ----
    {
        "id": "C047",
        "family": "evolutionary",
        "short_description": "Single-peaked fitness landscape",
        "core_mechanism": "The explanation space has a single fitness peak (self-reference). All evolutionary trajectories converge to this peak. There is no escaping it — it is the global optimum.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },
    {
        "id": "C048",
        "family": "evolutionary",
        "short_description": "Evolutionary trap / fitness valley",
        "core_mechanism": "The investigation is in an evolutionary trap. Local optimization leads to recursive dependency, and escaping would require crossing a fitness valley (accepting a worse explanation temporarily).",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },
    {
        "id": "C049",
        "family": "evolutionary",
        "short_description": "Neutral network drift",
        "core_mechanism": "Many candidates are equally fit. The investigation drifts along a neutral network of explanations. The apparent recursion is just drift without selection pressure.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "no",
        "predicts_collapse": "partial",
        "confidence": "medium",
    },
    {
        "id": "C050",
        "family": "evolutionary",
        "short_description": "Punctuated equilibrium",
        "core_mechanism": "Long periods of methodological stability (one family dominating) punctuated by rapid transitions. The phase structure IS the punctuation. Self-audit is a mass extinction event.",
        "predicts_recursion": "no",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "medium",
    },
    {
        "id": "C051",
        "family": "evolutionary",
        "short_description": "Red Queen effect",
        "core_mechanism": "The investigation must keep running just to stay in the same place. Each new candidate invalidates the previous, but the overall level of understanding does not increase. Running in place.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "medium",
    },
    {
        "id": "C052",
        "family": "evolutionary",
        "short_description": "Exaptation of audit machinery",
        "core_mechanism": "The audit machinery evolved for one purpose (checking detectors) and was exapted for another (auditing itself). The recursive behavior is a spandrel — a byproduct of exaptation.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "partial",
        "confidence": "medium",
    },

    # ---- 10. COGNITIVE ----
    {
        "id": "C053",
        "family": "cognitive",
        "short_description": "Methodological confirmation bias",
        "core_mechanism": "The investigation's methodology (decompose→audit→report) biases it toward finding recursive dependency. A methodology that looked for emergent simplicity would find that instead.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },
    {
        "id": "C054",
        "family": "cognitive",
        "short_description": "Framing dictates answer type",
        "core_mechanism": "The question 'what is first?' can only be answered with an object. If the answer is not an object (but a process, relation, or field), the question forces an infinite search.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },
    {
        "id": "C055",
        "family": "cognitive",
        "short_description": "Cognitive closure on non-recursive modes",
        "core_mechanism": "The investigators (human or AI) may be unable to conceive of alternatives to recursive dependency. The search space is bounded by cognitive architecture, not by the phenomenon.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },
    {
        "id": "C056",
        "family": "cognitive",
        "short_description": "Problem-solution isomorphism",
        "core_mechanism": "The problem IS the solution. The recursive dependency structure of the investigation's results is isomorphic to the recursive dependency structure of the problem. The investigation discovers itself.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "medium",
    },
    {
        "id": "C057",
        "family": "cognitive",
        "short_description": "Telic recursion",
        "core_mechanism": "The investigation's goal (finding a foundation) is itself recursive — each foundation requires a deeper foundation. The goal structure guarantees infinite regress regardless of the domain.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },

    # ---- 11. MEASUREMENT-FRAMEWORK ----
    {
        "id": "C058",
        "family": "measurement_framework",
        "short_description": "Observer effect in statement space",
        "core_mechanism": "The act of auditing a statement changes its dependency structure. The investigation cannot observe the 'true' dependencies because observation alters them.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },
    {
        "id": "C059",
        "family": "measurement_framework",
        "short_description": "Instrument resolution limit",
        "core_mechanism": "The investigation's instruments (detectors, audits, classifiers) have a finite resolution. Below this resolution, all structures appear identical — which is the collapse.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },
    {
        "id": "C060",
        "family": "measurement_framework",
        "short_description": "Operational closure",
        "core_mechanism": "The set of operations available to the investigation is closed — no new operations can be generated. Every audit uses the same operations on different targets, producing the same kind of result.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },
    {
        "id": "C061",
        "family": "measurement_framework",
        "short_description": "Heisenberg uncertainty for structure",
        "core_mechanism": "There is an uncertainty principle: the more precisely you know a statement's dependencies, the less precisely you know its content, and vice versa. The investigation optimizes one at the expense of the other.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "low",
    },
    {
        "id": "C062",
        "family": "measurement_framework",
        "short_description": "Measurement-induced state collapse",
        "core_mechanism": "The investigation's measurement of a statement's dependencies collapses the statement's state. The 'collapse' is not a property of the statement — it is a consequence of the measurement.",
        "predicts_recursion": "no",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },
    {
        "id": "C063",
        "family": "measurement_framework",
        "short_description": "Unbiased estimator does not exist",
        "core_mechanism": "No unbiased estimator exists for the quantity 'foundationality.' Every measurement method is biased, and the bias produces apparent recursion. The bias cannot be corrected because the true value is unknown.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "medium",
    },

    # ---- 12. UNKNOWN / UNCLASSIFIED ----
    {
        "id": "C064",
        "family": "unknown",
        "short_description": "Unknown unknown — blind spot",
        "core_mechanism": "There may be a category of explanation that the investigation cannot formulate because it lacks the necessary conceptual vocabulary. The recursion is a symptom of this blind spot.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "low",
    },
    {
        "id": "C065",
        "family": "unknown",
        "short_description": "Transcendent explanation",
        "core_mechanism": "The explanation may require concepts or mathematics not yet available. The current framework is inadequate, not because the question is unanswerable, but because the tools are insufficient.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "low",
    },
    {
        "id": "C066",
        "family": "unknown",
        "short_description": "Genuine mystery",
        "core_mechanism": "The phenomenon may be genuinely inexplicable within any possible framework. There are limits to explanation, and the investigation has reached one.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "low",
    },
    {
        "id": "C067",
        "family": "unknown",
        "short_description": "Meta-language hierarchy",
        "core_mechanism": "The investigation may need to ascend a hierarchy of meta-languages (object→meta→meta-meta→...) and the recursion is the trace of this ascent. Each level is expressible only in the next.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "high",
    },
    {
        "id": "C068",
        "family": "unknown",
        "short_description": "Non-Archimedean structure",
        "core_mechanism": "The dependence structure may be non-Archimedean: there exist statements that are infinitely close but not identical, with no finite chain connecting them. Standard audit fails on such structures.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "low",
    },
    {
        "id": "C069",
        "family": "unknown",
        "short_description": "Paraconsistent resolution",
        "core_mechanism": "The investigation may have hit a true contradiction — a dialetheia. The recursive dependency structure is a true paradox that cannot be resolved, only accepted.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "low",
    },
    {
        "id": "C070",
        "family": "unknown",
        "short_description": "Recursive structure is fundamental",
        "core_mechanism": "Recursive dependency is not an artifact, a limitation, or a discovery — it IS the phenomenon. The investigation has found what it was looking for but failed to recognize it.",
        "predicts_recursion": "yes",
        "predicts_self_audit": "yes",
        "predicts_collapse": "yes",
        "confidence": "medium",
    },
]

# ============================================================
# EXPLANATION CLUSTERS
# ============================================================

CLUSTERS = [
    {
        "cluster_id": "CLU01",
        "name": "Fixed-point mechanisms",
        "members": ["C005", "C030", "C031", "C033", "C034", "C035"],
        "core_theme": "The audit procedure is mathematically forced to find fixed points because it IS a fixed-point-finding operation.",
        "families_represented": ["computational", "mathematical_fixed_point", "self_reference"],
    },
    {
        "cluster_id": "CLU02",
        "name": "Limits of formal systems",
        "members": ["C002", "C003", "C029", "C032"],
        "core_theme": "The investigation has encountered fundamental limits of formal systems (incompleteness, undecidability, undefinability).",
        "families_represented": ["computational", "mathematical_fixed_point", "language_structure"],
    },
    {
        "cluster_id": "CLU03",
        "name": "Self-reference as structure",
        "members": ["C013", "C014", "C015", "C016", "C017"],
        "core_theme": "The investigation is a self-referential system; the recursion is what self-reference looks like from inside.",
        "families_represented": ["self_reference"],
    },
    {
        "cluster_id": "CLU04",
        "name": "Observer entanglement",
        "members": ["C018", "C019", "C021", "C022", "C023"],
        "core_theme": "The observer and observed cannot be separated; every result is about the joint system, not the phenomenon.",
        "families_represented": ["observer_model", "measurement_framework"],
    },
    {
        "cluster_id": "CLU05",
        "name": "Methodological prior dominance",
        "members": ["C020", "C053", "C054", "C055", "C057"],
        "core_theme": "The investigation's methodology rigidly determines its findings; the recursion reflects method, not world.",
        "families_represented": ["observer_model", "cognitive"],
    },
    {
        "cluster_id": "CLU06",
        "name": "Language as cage",
        "members": ["C024", "C025", "C026", "C027", "C028", "C029"],
        "core_theme": "The investigation's descriptive language imposes the recursive structure it seeks to explain.",
        "families_represented": ["language_structure"],
    },
    {
        "cluster_id": "CLU07",
        "name": "Information degradation",
        "members": ["C007", "C008", "C009", "C010", "C011", "C012"],
        "core_theme": "The investigation has exhausted the available information and is now processing its own noise.",
        "families_represented": ["information_theoretic"],
    },
    {
        "cluster_id": "CLU08",
        "name": "Attractor dynamics",
        "members": ["C001", "C041", "C042", "C043", "C044", "C045", "C046"],
        "core_theme": "The investigation's trajectory through explanation space converges to a basin of attraction from which it cannot escape.",
        "families_represented": ["computational", "dynamical_system"],
    },
    {
        "cluster_id": "CLU09",
        "name": "Evolutionary dead ends",
        "members": ["C047", "C048", "C049", "C050", "C051", "C052"],
        "core_theme": "The investigation has been trapped by its own optimization dynamics into a local optimum or evolutionary dead end.",
        "families_represented": ["evolutionary"],
    },
    {
        "cluster_id": "CLU10",
        "name": "Category mismatch",
        "members": ["C036", "C037", "C038", "C039", "C040"],
        "core_theme": "The investigation is looking in the wrong categorical direction (initial vs terminal, object vs relation).",
        "families_represented": ["category_theoretic"],
    },
    {
        "cluster_id": "CLU11",
        "name": "Measurement artifact",
        "members": ["C058", "C059", "C060", "C061", "C062", "C063"],
        "core_theme": "The recursion is an artifact of the measurement instruments, not a property of the measured system.",
        "families_represented": ["measurement_framework"],
    },
    {
        "cluster_id": "CLU12",
        "name": "Genuine unknowns",
        "members": ["C064", "C065", "C066", "C067", "C068", "C069", "C070"],
        "core_theme": "The recursion may point to something genuinely outside the current framework's capacity to formulate.",
        "families_represented": ["unknown"],
    },
    {
        "cluster_id": "CLU13",
        "name": "Emergent complexity from simplicity",
        "members": ["C001", "C030", "C041", "C047", "C070"],
        "core_theme": "The recursion is the simplest possible behavior of a wide class of systems; it is what emerges when nothing else is forced.",
        "families_represented": ["computational", "mathematical_fixed_point", "dynamical_system", "evolutionary", "unknown"],
    },
    {
        "cluster_id": "CLU14",
        "name": "Infinite regress variants",
        "members": ["C018", "C022", "C057", "C067", "C069"],
        "core_theme": "The investigation has entered an infinite regress that is structurally necessary for certain types of questions.",
        "families_represented": ["observer_model", "cognitive", "unknown"],
    },
    {
        "cluster_id": "CLU15",
        "name": "Question-reformulation needed",
        "members": ["C027", "C054", "C056", "C064", "C065"],
        "core_theme": "The question itself may be malformed; the recursion is what happens when you ask a question that has no answer in the form requested.",
        "families_represented": ["language_structure", "cognitive", "unknown"],
    },
]

# ============================================================
# OPEN QUESTIONS
# ============================================================

QUESTIONS = [
    # About the phenomenon itself (01-10)
    "Q01: Is recursive dependency a property of the world or a property of the investigation's methodology?",
    "Q02: Could a different investigation (different detectors, different audit procedure) reach a non-recursive result?",
    "Q03: Is the recursion convergent (approaching a limit) or divergent (exploding in complexity)?",
    "Q04: Does the recursive structure have a characteristic signature that distinguishes it from genuine discovery?",
    "Q05: Is there a level of analysis at which the recursion stops — a 'ground' that the current procedure cannot reach?",
    "Q06: Is the collapse at T055 a real collapse or a phase transition to a new regime?",
    "Q07: Could the recursion be broken by changing the goal (e.g., from 'find first' to 'find useful')?",
    "Q08: Is the recursive dependency structure invariant under changes to the investigation's starting assumptions?",
    "Q09: Would non-human investigators (e.g., purely formal, non-neural) produce the same recursive structure?",
    "Q10: Is the recursion a single phenomenon or multiple phenomena collapsed by the description?",

    # About family-specific predictions (11-25)
    "Q11: Which explanation families predict the specific collapse depth observed at T055?",
    "Q12: Does the fixed-point combinator explanation (C005) predict the exact phase structure from T037-T055?",
    "Q13: Under the Yoneda interpretation (C037), what would a non-recursive alternative look like?",
    "Q14: If the observer effect explanation (C058) is correct, what changes if the investigation stops observing?",
    "Q15: Does the Kolmogorov complexity explanation (C007) predict that a different formal language would find a shorter description?",
    "Q16: Under the Bayesian prior explanation (C020), what prior would produce non-recursive results?",
    "Q17: Does the limit-cycle explanation (C043) predict the exact periodicity of T037-T055?",
    "Q18: Under the evolutionary trap explanation (C048), what is the fitness function?",
    "Q19: Does the categorical grammar explanation (C027) predict that changing the grammar changes the recursion?",
    "Q20: Can the information-theoretic and self-reference families be distinguished experimentally?",
    "Q21: Which family explains the transition from computational phases (T037-T046) to meta-phases (T047-T055)?",
    "Q22: Does any family predict the specific numerical values observed (98.3%, 0.69, 85.8%)?",
    "Q23: Which families predict that the audit becomes destructive (T055) rather than productive?",
    "Q24: Can the fixed-point families predict which statements survive and which collapse at each phase?",
    "Q25: Under the autopoiesis explanation (C016), is the audit system alive?",

    # About discriminating between families (26-40)
    "Q26: If the investigation switched from text-based to geometric representations, would the recursion change?",
    "Q27: What experiment would distinguish the computational from the self-reference families?",
    "Q28: What experiment would distinguish the observer-model from the language-structure families?",
    "Q29: Can the information-theoretic collapse be distinguished from the mathematical fixed-point collapse by measurement?",
    "Q30: Is there a signature in the phase data that distinguishes evolutionary from dynamical explanations?",
    "Q31: Can we design a detector that does NOT produce recursive results, and if so, what would it measure?",
    "Q32: If the investigation asked 'what is the most useful' instead of 'what is first,' would the recursion persist?",
    "Q33: Can the cognitive closure hypothesis (C055) be distinguished from genuine mystery (C066)?",
    "Q34: Under the Whorfian explanation (C024), would a formal logic with different primitives find different results?",
    "Q35: Does the rate-distortion explanation (C012) predict a specific bit rate for the recursive structure?",
    "Q36: Can we construct a category where the investigation HAS an initial object, and compare?",
    "Q37: Would a quantum computation version of the investigation produce different phase results?",
    "Q38: What does each family predict about the NEXT phase (T057 and beyond)?",
    "Q39: Which families predict that the recursive structure has been present since T001 (not just T037)?",
    "Q40: Can any family explain the phase transition from 'finding structures' to 'auditing audits'?",

    # About the limits of the current approach (41-50)
    "Q41: Is the investigation trapped by its own success — the recursion IS the answer but cannot be accepted as one?",
    "Q42: Would an investigation that DID NOT audit itself produce more informative results?",
    "Q43: Is the 12-family taxonomy itself a recursive decomposition of the explanation space?",
    "Q44: Does the taxonomy of families contain the same circular dependency structure as the original investigation?",
    "Q45: Are the families genuinely distinct, or are they the same explanation viewed through different languages?",
    "Q46: Could the investigation benefit from not having a fixed procedure (non-methodological exploration)?",
    "Q47: What is the simplest possible explanation that fits ALL the phase data from T037-T055?",
    "Q48: If the simplest explanation is 'the procedure produces recursion,' is that acceptable?",
    "Q49: What new data (outside T037-T055) would be needed to distinguish between the families?",
    "Q50: Is the investigation's demand for unique explanations itself the source of recursion?",

    # About unknown unknowns and meta-questions (51-65)
    "Q51: What is the investigator's relationship to the recursion — are they part of it or outside it?",
    "Q52: Is there a version of this investigation that DOES terminate, and if so, what does it look like?",
    "Q53: Could the recursion be not a problem to solve but a structure to inhabit productively?",
    "Q54: What would it mean if the BEST explanation is 'there is no unified explanation'?",
    "Q55: Is the concept of 'first' coherent at all, or is it a grammatical illusion?",
    "Q56: Does the investigation presuppose that explanations are hierarchically ordered, and if so, is that assumption valid?",
    "Q57: Could the recursion be resolved by switching from hierarchical to network models of explanation?",
    "Q58: What would a non-foundational investigation look like — one that does not search for ground?",
    "Q59: Is the investigation's demand for non-circularity itself a cultural/historical artifact?",
    "Q60: Are there investigative traditions (Buddhist logic, dialectical materialism, etc.) where recursive dependency is not seen as a problem?",
    "Q61: If the recursion is inherent, what is the ethical/investigative response — acceptance, transformation, or transcendence?",
    "Q62: Does the phase structure T037-T055 encode information about the investigator as well as the investigated?",
    "Q63: Can the recursion be modeled as a game between two players (generator and auditor) with different objectives?",
    "Q64: Under the game model, what payoff structure produces the T055 collapse?",
    "Q65: What does it mean to *decide* that one explanation family is correct? Is such a decision possible from within the recursion?",
]

# ============================================================
# WRITE OUTPUTS
# ============================================================

# 1. Candidate landscape CSV
with open(OUT / "t058_candidate_landscape.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id", "family", "short_description", "core_mechanism",
                 "predicts_recursion", "predicts_self_audit", "predicts_collapse", "confidence"])
    for c in CANDIDATES:
        w.writerow([c["id"], c["family"], c["short_description"], c["core_mechanism"],
                     c["predicts_recursion"], c["predicts_self_audit"],
                     c["predicts_collapse"], c["confidence"]])

print(f"Wrote {len(CANDIDATES)} candidates to t058_candidate_landscape.csv")

# 2. Explanation clusters CSV
with open(OUT / "t058_explanation_clusters.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cluster_id", "name", "member_ids", "n_members",
                 "core_theme", "families_represented"])
    for cl in CLUSTERS:
        w.writerow([cl["cluster_id"], cl["name"], ";".join(cl["members"]),
                     len(cl["members"]), cl["core_theme"],
                     ";".join(cl["families_represented"])])

print(f"Wrote {len(CLUSTERS)} clusters to t058_explanation_clusters.csv")

# 3. Open questions CSV
with open(OUT / "t058_open_questions.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id", "question"])
    for q in QUESTIONS:
        w.writerow([q[:3], q[5:]])

print(f"Wrote {len(QUESTIONS)} questions to t058_open_questions.csv")

# ============================================================
# SUMMARY
# ============================================================

family_counts = {}
for c in CANDIDATES:
    f = c["family"]
    family_counts[f] = family_counts.get(f, 0) + 1

print("\nCandidate distribution by family:")
for fam, n in sorted(family_counts.items()):
    print(f"  {fam:30s} {n:2d} candidates")
print(f"\nTotal candidates: {len(CANDIDATES)}")
print(f"Total clusters:  {len(CLUSTERS)}")
print(f"Total questions: {len(QUESTIONS)}")
print("\nT058 complete. No candidates eliminated. No winners declared.")
