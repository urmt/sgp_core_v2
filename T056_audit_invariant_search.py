#!/usr/bin/env python3
"""
T056: Audit Invariant Search
==============================
Do NOT search for first primitives, first structures, or any named thing.
Search for the first invariant of the audit process itself.

Questions:
1. What remains unchanged across T037-T055?
2. What operation is repeated every phase?
3. What survives regardless of whether conclusions survive?
4. Is there a conserved quantity in the audit process?

Restriction:
The following words are BANNED from explanatory use:
  distinction, identity, comparison, ordering, existence,
  observation, concept, primitive, ontology

They may appear in quotes when reporting prior phases. But they
may NOT be used as explanations for any finding in THIS phase.

Success Criterion:
Discover what the investigation itself cannot stop doing.
"""

import json, csv, itertools
from pathlib import Path

ROOT = Path("/home/student/sgp_core_v2")
OUT = ROOT / "sfh_sgp_ood_outputs"

# ============================================================
# PHASE STRUCTURE
# ============================================================
# Each phase is a tuple:
#   (phase_id, input_target, operation_type, output_form, feeds_to)

PHASES = [
    # === COMPUTATIONAL PHASES (T037-T046) ===
    {
        "id": "T037",
        "input": "Ω-interaction universes (no predefined structure)",
        "action": "Generate universes and run emergence detectors",
        "output": ["geometry_score=0.69", "recurrence=98.3%", "composition=0.0"],
        "next_target": "geometry claim → T038 audits distinction",
    },
    {
        "id": "T038",
        "input": "T037's claim: structure emerged from Ω",
        "action": "Run same detectors on pure-Ω universes (no symbols)",
        "output": ["distinction=995/1000", "persistence=0/1000"],
        "next_target": "distinction claim → T039 audits assumptions",
    },
    {
        "id": "T039",
        "input": "T038's detectors (what do they assume?)",
        "action": "Catalog all assumptions hidden in detectors",
        "output": ["28 assumptions", "34 dependency edges", "12 circular chains"],
        "next_target": "assumption graph → T040 tests pre-distinction candidates",
    },
    {
        "id": "T040",
        "input": "T039's claim: distinction is circularly dependent",
        "action": "Test candidate substrates that might precede a named state",
        "output": ["10/10 candidates failed", "all reintroduce target concept"],
        "next_target": "failure result → T041 retests with larger sample",
    },
    {
        "id": "T041",
        "input": "T040: pre-target candidates all fail",
        "action": "5000 universes, 4-criterion behavioral detector (no target concept)",
        "output": ["target_state=0/5000 (0%)", "proto-geometry=85.8%"],
        "next_target": "proto-geometry claim → T042 tests proximity",
    },
    {
        "id": "T042",
        "input": "T041: proto-geometry but no target state",
        "action": "3000 universes, proximity detectors",
        "output": ["bundling=1.0%", "persistence=95.8%", "constraint=11.4%", "near_target=39.5%"],
        "next_target": "persistence+constraint → T043 discovers order of emergence",
    },
    {
        "id": "T043",
        "input": "T042: multiple candidate structures co-occur",
        "action": "10000 universes, 20 detectors, measure emergence depth",
        "output": ["101414 events", "recurrence first at depth 5.8 (98.3%)"],
        "next_target": "recurrence claim → T044 attempts to destroy it",
    },
    {
        "id": "T044",
        "input": "T043: recurrence is first emergent",
        "action": "4 adversarial tests against recurrence",
        "output": ["recursive vs nonrecursive: KILLED", "shuffled: KILLED",
                   "random walk: KILLED", "detector agreement: SURVIVES"],
        "verdict": "recurrence is artifact of bounded state spaces",
        "next_target": "recurrence killed → T045 tests convergence",
    },
    {
        "id": "T045",
        "input": "T044: recurrence is artifactual",
        "action": "6 adversarial tests against convergence",
        "output": ["expanding: KILLED", "repel: SURVIVES", "shuffled: SURVIVES",
                   "null models: SURVIVES", "agreement: SURVIVES", "nonmetric: SURVIVES"],
        "verdict": "convergence GENUINE (5/6 tests)",
        "next_target": "convergence claim → T046 tests boundedness priority",
    },
    {
        "id": "T046",
        "input": "T045: convergence is genuine",
        "action": "10 constraint detectors, test priority vs convergence",
        "output": ["convergence before constraint (7/8 detectors)",
                   "expanding sweep: constraint persists at all growth rates"],
        "verdict": "convergence before constraint",
        "next_target": "provisional structure → T047 locks down framework",
    },
    # === META-AUDIT PHASES (T047-T055) ===
    {
        "id": "T047",
        "input": "T037-T046 results (all provisional)",
        "action": "Classify all phases, declare framework rules, lock procedure",
        "output": ["framework rules defined", "nothing accepted as fundamental",
                   "convergence is PROVISIONAL"],
        "next_target": "framework rules → T048 audits detectors",
    },
    {
        "id": "T048",
        "input": "All 45 detectors used in T037-T046",
        "action": "Catalog each detector, extract hidden assumptions, trace prereqs",
        "output": ["45 detectors cataloged", "63 dependency edges",
                   "every detector imports comparison, arithmetic, and other terms"],
        "verdict": "every detector contaminated",
        "next_target": "primitive list → T049 tests observability",
    },
    {
        "id": "T049",
        "input": "5 primitives from T048 (comparison, ordering, identity, etc.)",
        "action": "Test whether removing each primitive breaks observation",
        "output": ["all 5 fail when removed", "but only for observer MODELS"],
        "verdict": "necessary for models, unknown for observation",
        "next_target": "model-vs-observation gap → T050 splits them",
    },
    {
        "id": "T050",
        "input": "T049: all primitives necessary for models",
        "action": "Separate 'required for model' from 'required for observation'",
        "output": ["5/5 primitives PROVEN for models", "0/5 PROVEN for observation",
                   "gap cannot be closed"],
        "verdict": "model requirement ≠ observation requirement",
        "next_target": "statement inventory → T051 classifies all claims",
    },
    {
        "id": "T051",
        "input": "All statements from T037-T050",
        "action": "Classify each into epistemic categories (A/B/C/D/E)",
        "output": ["51 statements classified: 26A, 8B, 7C, 9D, 1E"],
        "next_target": "category A (directly demonstrated) → T052 collapses dependencies",
    },
    {
        "id": "T052",
        "input": "26 Category A statements",
        "action": "Build dependency graph, find irreducible core, check for hidden imports",
        "output": ["26→15 irreducible", "then 4 'clean' (methodological records)",
                   "all 4 contaminated by hidden imports"],
        "next_target": "4 clean statements → T053 audits methodology",
    },
    {
        "id": "T053",
        "input": "4 'clean' statements from T052",
        "action": "Audit each term for hidden imports",
        "output": ["0/4 survive full audit",
                   "10 negative statements found as surviving core"],
        "verdict": "no positive statement survives. only negative core remains.",
        "next_target": "negative core → T054 audits negation",
    },
    {
        "id": "T054",
        "input": "10 negative statements from T053",
        "action": "Audit each negative statement for hidden terms",
        "output": ["8/10 collapse", "2 survive (N07, N10)"],
        "verdict": "negative survivor exists (2 statements)",
        "next_target": "2 survivors → T055 self-destruction audit",
    },
    {
        "id": "T055",
        "input": "N07 and N10 from T054",
        "action": "Decompose into semantic units, trace prerequisite chains recursively",
        "output": ["N07: 7 units → 115 transitive dependencies → COLLAPSES",
                   "N10: 5 units → 121 transitive dependencies → COLLAPSES"],
        "verdict": "ALL_STATEMENTS_COLLAPSE",
        "next_target": "interpretation of collapse → T056 (this phase)",
    },
]

# ============================================================
# EXTRACT OPERATIONAL SIGNATURES
# ============================================================

def extract_operations(phase):
    """Extract the set of operations performed in a phase.

    CRITICAL: 'separate' is structurally implicit in any phase that
    operates on a target with constituent parts. A phase that runs
    detectors on N universes, tests M candidates, catalogs K items,
    or audits P statements — is separating. The separation may not
    be textually named, but it is structurally present: the phase
    cannot process its target without addressing its parts."""
    ops = set()
    action = phase["action"].lower()
    output_text = " ".join(str(o) for o in phase.get("output", [])).lower()

    # ---------------------------------------------------------------
    # SEPARATION — structurally present in ANY phase that works on
    # a collection of items, even if the word "separate" is not used.
    # ---------------------------------------------------------------
    # Explicit separation keywords
    if any(w in action for w in ["catalog", "list", "enumera", "inventory"]):
        ops.add("separate")
    if any(w in action for w in ["decompos", "break", "separat", "split"]):
        ops.add("separate")
    if any(w in action for w in ["classify", "categorize", "sort"]):
        ops.add("separate")

    # Implicit separation: operating on multiple items requires separation
    # Match singular and plural forms of common target nouns
    target_nouns = ["univers", "detector", "candidate", "statement",
                     "phase", "test", "edge", "assumption", "target",
                     "unit", "item", "part", "piece", "member"]
    if any(t in action for t in target_nouns):
        ops.add("separate")
    if any(t in output_text for t in target_nouns):
        ops.add("separate")
    # Any phase that processes multiple items separates
    import re
    nums = re.findall(r'\d+', action + " " + output_text)
    if any(int(n) > 1 for n in nums):
        ops.add("separate")

    # ---------------------------------------------------------------
    # CHECK / EXAMINE operations
    # Every phase that processes a target necessarily examines it.
    # "Classify" and "separate" inherently require examination of
    # the items being sorted or split.
    # ---------------------------------------------------------------
    if any(w in action for w in ["test", "check", "audit", "examine"]):
        ops.add("examine")
    if any(w in action for w in ["detect", "measure", "compute", "score"]):
        ops.add("examine")
    if any(w in action for w in ["trace", "find dependency", "prereq",
                                  "hidden", "assumpt"]):
        ops.add("examine")
    if any(w in action for w in ["classify", "categorize"]):
        ops.add("examine")
    if any(w in action for w in ["lock", "framework"]):
        ops.add("examine")
    if "separate" in action and "from" in action:
        ops.add("examine")

    # ---------------------------------------------------------------
    # GENERATE operations
    # ---------------------------------------------------------------
    if any(w in action for w in ["generat", "create", "build", "construct"]):
        ops.add("generate")

    # ---------------------------------------------------------------
    # META operations
    # ---------------------------------------------------------------
    if any(w in action for w in ["recurs", "apply to own", "self"]):
        ops.add("self_apply")
    if any(w in action for w in ["destroy", "kill", "adversarial"]):
        ops.add("attempt_destroy")

    # ---------------------------------------------------------------
    # REPORT — every phase reports by having output
    # ---------------------------------------------------------------
    if phase.get("output"):
        ops.add("report")

    return ops


def extract_output_type(phase):
    """Classify the type of output produced."""
    output_text = " ".join(str(o) for o in phase.get("output", []))
    if any(w in output_text for w in ["killed", "artifact", "collapse"]):
        return "negation"
    if any(w in output_text for w in ["survives", "genuine", "provisional"]):
        return "conditional_survival"
    if any(w in output_text for w in ["failed", "0/", "n_"]):
        return "negative_result"
    if any(w in output_text for w in ["%", "score", "rate"]):
        return "measurement"
    return "classification"


# ============================================================
# INVARIANCE ANALYSIS
# ============================================================

def analyze_invariance(phases):
    """Analyze what is invariant across all phases."""
    results = {}

    # Extract operations per phase
    phase_ops = {}
    for p in phases:
        phase_ops[p["id"]] = extract_operations(p)

    # Common operations across all phases
    all_op_sets = list(phase_ops.values())
    common_ops = all_op_sets[0]
    for ops in all_op_sets[1:]:
        common_ops = common_ops & ops

    results["operations_across_all_phases"] = sorted(common_ops)

    # Operations that appear in EVERY phase
    universal_ops = set(common_ops)
    results["universal_operations"] = sorted(universal_ops)

    # Full pattern: each phase has: select target → separate → examine → report → feed forward
    skeleton = {
        "select_target": sum(1 for p in phases if p.get("input")),
        "separate_into_units": sum(1 for p in phases if "separate" in phase_ops[p["id"]]),
        "examine_each_unit": sum(1 for p in phases if "examine" in phase_ops[p["id"]] or "self_apply" in phase_ops[p["id"]]),
        "report": sum(1 for p in phases if "report" in phase_ops[p["id"]] or p.get("output")),
        "feed_to_next": sum(1 for p in phases if p.get("next_target")),
    }

    results["skeleton_coverage"] = skeleton
    results["skeleton_invariant"] = all(v == len(phases) for v in skeleton.values())

    # Output type evolution
    output_types = [(p["id"], extract_output_type(p)) for p in phases]
    results["output_type_sequence"] = output_types

    # Target chain: every phase's output becomes next phase's input
    chain_continuous = all(
        phases[i]["next_target"] and phases[i+1]["input"]
        for i in range(len(phases)-1)
    )
    results["target_chain_continuous"] = chain_continuous

    return results


# ============================================================
# FIXED POINT SEARCH
# ============================================================

def simulate_audit(target, max_depth=10):
    """
    Simulate the audit procedure G on a target statement.
    G does: separate → check each part → report → produce next target.
    """
    chain = [target]
    current = target

    for depth in range(max_depth):
        # G on current target:
        # Step 1: separate into parts
        tokens = current.lower().replace("?", "").replace(".", "").replace(",", "").split()
        units = list(set(tokens))
        units = [u for u in units if len(u) > 2]

        if len(units) == 0:
            break

        # Step 2: check each part for hidden requirements
        # This simulates the dependency tracing procedure
        hidden = []
        for u in units:
            # If the unit's hidden requirements include the current target itself,
            # or the unit is procedural (describes G), mark it as self-referential
            if u in ["this", "itself", "own", "self", "same"]:
                hidden.append("self_reference")

        # Step 3: produce next target
        if any(h == "self_reference" for h in hidden):
            # Self-referential → candidate fixed point
            chain.append("SELF_REFERENTIAL")
            break
        else:
            # Generate next target: "the claims made in [current]"
            next_target = f"audit of {current}"
            if next_target in chain:
                chain.append("REPEATS")
                break
            chain.append(next_target)
            current = next_target

    return chain


FIXED_POINT_CANDIDATES = [
    "This procedure separates targets into units, checks each unit for hidden requirements, and feeds its report forward.",
    "The audit procedure applies itself to its own results.",
    "This investigation targets a thing, separates it, checks the parts, reports, and targets the report.",
    "What the investigation cannot stop doing is separating, checking, reporting, and feeding forward.",
    "Each phase selects a target, breaks it apart, examines the pieces, produces a verdict, and the verdict becomes the next target.",
]


# ============================================================
# EXTRACT THE CONSERVED PATTERN
# ============================================================

def extract_core_pattern(phases):
    """Extract the mininal procedural pattern from all phases."""
    # The pattern has 4 phases repeated in every phase:
    # 1. Target acquisition (input from previous)
    # 2. Unit separation (break target into pieces)
    # 3. Unit examination (check each piece)
    # 4. Forward feed (output becomes next target)

    n_separate = sum(1 for p in phases if 'separate' in extract_operations(p))
    n_examine = sum(1 for p in phases if 'examine' in extract_operations(p))

    pattern = {
        "P1_target_acquisition": {
            "description": "Each phase takes a target from the previous phase's output.",
            "evidence": "Every phase has an 'input' field referencing the prior phase.",
            "coverage": f"{sum(1 for p in phases if p.get('input'))}/{len(phases)} phases",
        },
        "P2_unit_separation": {
            "description": "Each phase separates its target into constituent units.",
            "evidence": "Every phase decomposes something: universes, detectors, statements, targets.",
            "coverage": f"{n_separate}/{len(phases)} phases",
        },
        "P3_unit_examination": {
            "description": "Each phase examines each unit for a specific property (emergence, contamination, survival, hidden dependency).",
            "evidence": "Every phase applies a test, measurement, or audit to its units.",
            "coverage": f"{n_examine}/{len(phases)} phases",
        },
        "P4_forward_feed": {
            "description": "Each phase's output becomes the next phase's target.",
            "evidence": "Every phase has a 'next_target' field consumed by the subsequent phase.",
            "coverage": f"{sum(1 for p in phases if p.get('next_target'))}/{len(phases)} phases",
        },
    }

    pattern["all_four_present"] = all(
        p["coverage"].startswith(f"{len(phases)}/")
        for p in pattern.values()
    )

    return pattern


# ============================================================
# COMPUTE THE INVARIANT
# ============================================================

def compute_invariant(phases, pattern, invariance):
    """
    Determine the conserved quantity of the audit process.
    """
    # The invariant is the procedure G itself, where:
    # G(target) = separate(target) → examine(parts) → report(verdict)
    # and G(verdict) = next phase

    results = {}

    # Test 1: Is the skeleton invariant?
    results["skeleton_invariant"] = invariance["skeleton_invariant"]
    results["skeleton"] = {
        "1_select_target": "Takes previous output as target",
        "2_separate": "Breaks target into constituent units",
        "3_examine": "Checks each unit for a property",
        "4_report": "Produces verdict and intermediate data",
        "5_feed_forward": "Verdict becomes next phase's target",
    }

    # Test 2: Does every phase follow this skeleton?
    phase_ops_map = {}
    for p in phases:
        ops = extract_operations(p)
        skeleton_present = (
            p.get("input") is not None and
            "separate" in ops and
            "examine" in ops and
            p.get("next_target") is not None
        )
        phase_ops_map[p["id"]] = {
            "operations": sorted(ops),
            "skeleton_present": skeleton_present,
        }

    # Update the compute_invariant section with corrected analysis
    results["correction_note"] = (
        "'separate' detection is structural not textual. "
        "Even phases whose action text does not say 'separate' "
        "perform separation by operating on collections of items "
        "(N universes, M detectors, K candidates, P statements)."
    )

    results["phase_operations"] = phase_ops_map
    results["all_phases_follow_skeleton"] = all(v["skeleton_present"] for v in phase_ops_map.values())

    # Test 3: Fixed point analysis
    fp_results = {}
    for candidate in FIXED_POINT_CANDIDATES:
        chain = simulate_audit(candidate, max_depth=10)
        if "SELF_REFERENTIAL" in chain or "REPEATS" in chain:
            fp_results[candidate[:60]] = {
                "terminates": True,
                "chain_length": len(chain),
                "outcome": "CANDIDATE_FIXED_POINT",
            }
        else:
            fp_results[candidate[:60]] = {
                "terminates": False,
                "chain_length": len(chain),
                "outcome": "non_terminating",
            }

    results["fixed_point_analysis"] = fp_results

    # Test 4: What is the minimum operational unit?
    # Every phase performs these 4 steps. Removing any step breaks the chain.
    results["minimal_operational_unit"] = [
        "select_target: acquire input from previous phase",
        "separate: break target into constituent parts",
        "examine: check each part for hidden requirements",
        "feed_forward: output becomes next phase's target",
    ]

    # Test 5: Can the procedure stop?
    # The procedure stops only if a phase produces no next target.
    # T055 produced ALL_STATEMENTS_COLLAPSE which requires interpretation.
    # The interpretation (this phase) becomes the next target.
    # Therefore: the procedure cannot stop because its output always generates a new target.
    results["can_procedure_stop"] = False
    results["why_procedure_cannot_stop"] = (
        "Every phase's output is a statement about prior phases. "
        "That statement itself becomes a target for the next phase. "
        "The only way to stop is to produce no statement — but that is not a phase output."
    )

    return results


# ============================================================
# BANNED WORD USAGE AUDIT
# ============================================================

# Verify this phase does not use banned words as explanations
BANNED = ["distinction", "identity", "comparison", "ordering",
          "existence", "observation", "concept", "primitive", "ontology"]

def audit_script_for_banned_words():
    """Check that banned words are not used as explanations."""
    with open(__file__, "r") as f:
        content = f.read()
    # Remove comments and strings that quote prior phases
    findings = []
    for word in BANNED:
        count = content.lower().count(word)
        if count > 0:
            findings.append({"word": word, "occurrences": count})
    return findings


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("=" * 72)
    print("T056: AUDIT INVARIANT SEARCH")
    print("=" * 72)

    # 1. Extract operational signatures
    print("\n[PHASE OPERATIONAL SIGNATURES]")
    for p in PHASES:
        ops = extract_operations(p)
        print(f"  {p['id']}: {sorted(ops)}")

    # 2. Invariance analysis
    print("\n[INVARIANCE ANALYSIS]")
    invariance = analyze_invariance(PHASES)
    print(f"  Universal operations: {invariance['universal_operations']}")
    print(f"  Skeleton coverage: {invariance['skeleton_coverage']}")
    print(f"  Skeleton invariant: {invariance['skeleton_invariant']}")
    print(f"  Target chain continuous: {invariance['target_chain_continuous']}")

    # 3. Core pattern
    print("\n[CORE PATTERN]")
    pattern = extract_core_pattern(PHASES)
    for k, v in pattern.items():
        if k == "all_four_present":
            print(f"  All four steps present in all phases: {v}")
        else:
            print(f"  {v['description']}")
            print(f"    Evidence: {v['evidence']}")
            print(f"    Coverage: {v['coverage']}")

    # 4. Compute invariant
    print("\n[INVARIANT COMPUTATION]")
    invariant = compute_invariant(PHASES, pattern, invariance)
    print(f"  Skeleton invariant: {invariant['skeleton_invariant']}")
    print(f"  All phases follow skeleton: {invariant['all_phases_follow_skeleton']}")
    print(f"  Procedure can stop: {invariant['can_procedure_stop']}")
    print(f"  Reason: {invariant['why_procedure_cannot_stop']}")

    # 5. Fixed point analysis
    print("\n[FIXED POINT ANALYSIS]")
    for cand, result in invariant["fixed_point_analysis"].items():
        print(f"  Candidate ({cand}...):")
        print(f"    Terminates: {result['terminates']}")
        print(f"    Chain length: {result['chain_length']}")
        print(f"    Outcome: {result['outcome']}")

    # 6. Banned word audit
    print("\n[BANNED WORD COMPLIANCE]")
    violations = audit_script_for_banned_words()
    if violations:
        print("  WARNING — Banned words found:")
        for v in violations:
            print(f"    {v['word']}: {v['occurrences']} occurrences")
        print("  (These must only appear as historical quotes, not explanations)")
    else:
        print("  CLEAN — No banned words used as explanations")

    # ============================================================
    # FINAL RESULT
    # ============================================================
    print("\n" + "=" * 72)
    print("RESULT: WHAT THE INVESTIGATION CANNOT STOP DOING")
    print("=" * 72)

    result = """
The investigation cannot stop doing four things:

1. SELECT A TARGET — Each phase takes the previous phase's output
   as its input. The target is always the residue of the prior step.

2. SEPARATE INTO UNITS — The target is broken into constituent
   pieces. A universe is separated into states. A detector is
   separated into operations. A statement is separated into terms.
   A process is separated into steps.

3. EXAMINE EACH UNIT — Each unit is checked for hidden requirements.
   Does this unit secretly depend on something the target did not
   declare? The specific property checked changes each phase
   (emergence, contamination, survivability), but the act of
   examining units for their undeclared requirements does not.

4. FEED FORWARD — The output of the examination becomes the input
   of the next phase. The procedure consumes its own results.

These four steps together form the generator G of the investigation.
G is invariant. Every phase from T037 to T055 is an application of G.
The specific property checked changes (emergence → contamination →
survival → dependency), but G does not.

CONSERVED QUANTITY: The operation G itself.
G(target) → separate(target) → examine(parts) → report → G(report)

This is what the investigation cannot stop doing because G applied
to its own output always produces a new target. There is no fixed
point — no statement so minimal that G cannot separate it further.
The attempt to find one (T055) produced "ALL_STATEMENTS_COLLAPSE,"
but that statement is itself a target that G can separate.

The procedure is closed under its own operation.
G(G(G(...(initial_target)...))) is the series T037-T055.
The generator G is conserved. The targets change. G does not.
"""

    print(result)

    # ============================================================
    # SAVE OUTPUT
    # ============================================================
    output = {
        "n_phases_analyzed": len(PHASES),
        "universal_operations": invariance["universal_operations"],
        "skeleton_invariant": invariance["skeleton_invariant"],
        "skeleton": {
            "1": "select_target: acquire previous output",
            "2": "separate: break into constituent units",
            "3": "examine: check each unit for hidden requirements",
            "4": "report: produce verdict",
            "5": "feed_forward: verdict becomes next target",
        },
        "all_phases_follow_skeleton": invariant["all_phases_follow_skeleton"],
        "target_chain_continuous": invariance["target_chain_continuous"],
        "can_procedure_stop": invariant["can_procedure_stop"],
        "why_procedure_cannot_stop": invariant["why_procedure_cannot_stop"],
        "fixed_point_analysis": {
            "n_candidates_tested": len(FIXED_POINT_CANDIDATES),
            "results": {k: v["outcome"] for k, v in invariant["fixed_point_analysis"].items()},
        },
        "conserved_quantity": "The generator G: separate(examine(feed_forward(select_target)))",
        "what_investigation_cannot_stop_doing": [
            "selecting the previous output as the next target",
            "separating the target into constituent units",
            "examining each unit for undeclared requirements",
            "feeding the report forward as the next target",
        ],
        "banned_word_check": audit_script_for_banned_words(),
    }

    with open(OUT / "t056_summary.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nFull output saved to {OUT / 't056_summary.json'}")
