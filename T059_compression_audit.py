#!/usr/bin/env python3
"""
T059: Compression Audit
========================
Determine whether the 70 T058 candidates represent
70 distinct explanations, ~20 in different languages,
or only a handful of underlying mechanisms.

Do NOT evaluate truth. Do NOT evaluate evidence.
Do NOT eliminate classes. Only determine structural equivalence.
"""

import csv, json
from pathlib import Path
from collections import defaultdict

OUT = Path("/home/student/sgp_core_v2/sfh_sgp_ood_outputs")

# ============================================================
# READ T058 CANDIDATES
# ============================================================

candidates = []
with open(OUT / "t058_candidate_landscape.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        candidates.append(row)

print(f"Loaded {len(candidates)} candidates from T058")

# ============================================================
# NORMALIZATION MAP
# ============================================================
# Each candidate gets a neutral mechanism — domain-specific terms
# stripped, core pattern expressed in a shared vocabulary.

NORMALIZED = {
    "C001": "A system with finite degrees of freedom will eventually occupy a previously occupied state, producing apparent structure from mere boundedness.",
    "C002": "A system cannot determine whether an arbitrary property holds of its own behavior using only its own resources; the question is undecidable from within.",
    "C003": "A system of sufficient expressiveness contains statements that cannot be proved or disproved using the system's own rules; these statements appear as unresolvable recursion.",
    "C004": "The computational resources required to analyze the system exceed what is available; the search terminates in resource exhaustion, not in a finding.",
    "C005": "The procedure is structurally a fixed-point finder; when applied to itself it finds itself as its own fixed point.",
    "C006": "A language capable of expressing arbitrary computation guarantees the existence of non-terminating self-referential expressions; the recursion is a consequence of expressiveness.",
    "C007": "The minimum description length of a system is uncomputable; the search for a shortest explanation cannot terminate with certainty.",
    "C008": "All candidates carry approximately the same information about the target; no structural basis exists for selecting among them.",
    "C009": "Each processing step irreversibly loses information about the original target; after sufficient steps the investigation operates on its own artifacts, not the phenomenon.",
    "C010": "The space of possible explanations is so large that every candidate has negligible prior probability; no candidate can be preferred on probabilistic grounds.",
    "C011": "The system's parameters are locally indistinguishable at the point of investigation; apparent structure arises from a singularity in the distinguishability metric.",
    "C012": "There is an upper bound on the information extractable from the system; the investigation has reached this bound and cannot obtain further discriminating information.",
    "C013": "The system's hierarchical levels curl back on themselves; each level when examined fully reveals the structure of the level above, which is isomorphic to itself.",
    "C014": "The target is defined in terms of the totality it belongs to; every attempt to reach it from below fails because it is presupposed by the reach.",
    "C015": "The operation applied to its own output yields the same operation; no outside of the operation exists from which to observe or modify it.",
    "C016": "The system produces the components that produce it; it is organizationally closed and self-sustaining, not derivable from external foundations.",
    "C017": "Each phase of the investigation produces a description that serves as the input for the next phase; the chain is self-sustaining without external reference.",
    "C018": "Every determination requires a determiner; every determiner requires a prior determination; this regress has no first term accessible from within the regress.",
    "C019": "The instrument of determination cannot be separated from what is determined; any attempt to isolate one changes the other.",
    "C020": "The result of the investigation reflects the assumptions built into the method, not properties of the target; changing the assumptions would change the result.",
    "C021": "The investigator is part of the investigated system; every determination is a self-determination and cannot achieve external reference.",
    "C022": "What counts as determiner at one level counts as determined at the next; the levels are unbounded and no ground level can be reached.",
    "C023": "When the only available data is the structure of the investigation itself, the optimal inference is that nothing outside the investigation exists; the recursion is self-confirmation.",
    "C024": "The descriptive framework imposes structural patterns that appear as properties of the described; a different framework would find different patterns.",
    "C025": "Every term is defined through other terms; there is no bottom layer of primitive definitions from which all others derive.",
    "C026": "Symbolic representations cannot be grounded in non-symbolic reference; every grounding attempt produces another symbol requiring grounding.",
    "C027": "The grammatical categories available (object, relation, property) force the investigation to find results that fit these categories; a phenomenon that is not an object cannot be found as one.",
    "C028": "The act of describing changes what is described; the description captures the joint state of describer-and-described, not the described in isolation.",
    "C029": "A language cannot define its own truth predicate; the search for true foundations within the language cannot succeed because the language cannot refer to its own truth.",
    "C030": "The procedure is a continuous function on an ordered space; its least fixed point is the recursive structure, found by repeated application starting from nothing.",
    "C031": "In a system with sufficient structure (Cartesian closure, universal property), every sufficiently regular operation has a fixed point; the recursion is mathematically guaranteed.",
    "C032": "The investigation constructs a diagonal argument: any enumerable list of explanations excludes at least one that is defined by its exclusion; the recursion is the diagonal element.",
    "C033": "The search direction (simplest → complex) is opposite to the direction in which structure exists (complex → simplest). The recursion is a search-direction error.",
    "C034": "The procedure is a contraction mapping on the space of statements; iteration converges to its unique fixed point, which is the recursive dependency structure.",
    "C035": "A system can only prove statements whose prerequisites the system already contains; the search for external foundations cannot terminate because every proof presupposes its conclusion.",
    "C036": "The category of statements has no initial object; no statement exists from which all others uniquely derive without circularity.",
    "C037": "What a thing IS is determined entirely by its relationships to other things, not by intrinsic properties; the relational web IS the identity, and recursion is what a closed relational web looks like.",
    "C038": "Not every structured system can be 'forgotten' to a unique unstructured base; the mapping from structured to unstructured is many-to-one, so no unique foundation exists.",
    "C039": "The minimal invariant of the recursive procedure is the terminal coalgebra — the infinite trajectory itself. The recursion IS what is conserved; there is no simpler conserved quantity.",
    "C040": "The audit procedure forms a monad: wrapping (unit) and flattening (multiplication) are associative and unital; the recursion is the Kleisli composition structure.",
    "C041": "The investigation's trajectory through explanation space converges to an attractor; once inside the attractor's basin, all trajectories end in the same structure regardless of starting point.",
    "C042": "The system crossed a bifurcation point where the qualitative dynamics changed; post-bifurcation behavior converges to a single regime regardless of prior state.",
    "C043": "The phase sequence has entered a periodic orbit; the same pattern repeats because the procedure maps its own output back to a previous output.",
    "C044": "The dynamics of the investigation changed from exploration (sensitivity to starting conditions) to entrapment (convergence regardless of starting point); a Lyapunov exponent crossed zero.",
    "C045": "The investigation transitioned from an information-preserving regime (where processing added information) to a dissipative regime (where processing lost information).",
    "C046": "Stable and unstable manifolds of the investigation's fixed points intersect chaotically; the recursive structure is the geometric structure of this intersection.",
    "C047": "All trajectories in the explanation space converge to a single optimum; no alternative stable states exist, so the investigation cannot escape the recursive attractor.",
    "C048": "Local optimization leads to a dead end from which escape requires accepting a worse intermediate state; no such acceptance is possible within the investigation's method.",
    "C049": "Multiple candidates are approximately equally fit; the investigation drifts among them without selection pressure, producing the appearance of recursion through indecision.",
    "C050": "Long periods of stability in one explanation family are punctuated by rapid transitions to another; the phase structure is the punctuation pattern.",
    "C051": "Each new explanation invalidates the previous without advancing overall understanding; the investigation must keep producing explanations to stay in the same place.",
    "C052": "A mechanism developed for one purpose (detector auditing) was repurposed for another (self-audit); the recursive behavior is a byproduct of this repurposing, not an intended function.",
    "C053": "The investigation's procedure (decompose → audit → report) is biased toward finding recursive dependency; a procedure with different bias would find different structure.",
    "C054": "The form of the question ('what is first?') demands an answer in the form of an object; if the true answer is not an object, the search for one produces infinite regress.",
    "C055": "The investigator cannot conceive of alternatives to recursive dependency; the search space is bounded by cognitive architecture, not by the phenomenon.",
    "C056": "The problem's structure and the solution's structure are isomorphic; the investigation discovers itself as the solution to its own question.",
    "C057": "The goal of finding a foundation is itself recursive; each candidate foundation requires a deeper foundation, so the goal structure guarantees infinite regress regardless of domain.",
    "C058": "The act of examining a statement changes its dependency structure; the investigation cannot observe 'true' dependencies because observation alters them.",
    "C059": "The investigation's instruments have finite resolution; below a threshold, all structures appear identical, producing the appearance of collapse.",
    "C060": "The set of available operations is closed under composition; no new operation type can be generated, so every phase produces the same kind of result as every other.",
    "C061": "There is a tradeoff: knowing dependencies precisely sacrifices knowledge of content, and vice versa. The investigation has optimized one at the expense of the other, producing apparent emptiness.",
    "C062": "The 'collapse' of structure is a consequence of the measurement act, not a property of the measured system; different measurement would produce different apparent structure.",
    "C063": "No unbiased estimator exists for the quantity being investigated; every measurement method is biased, and the bias pattern produces the appearance of recursion.",
    "C064": "The investigation has a blind spot: there exist explanation categories it cannot formulate because it lacks the necessary conceptual vocabulary. The recursion is a symptom of this absence.",
    "C065": "The concepts or mathematics required to formulate the correct explanation are not yet available; the framework is inadequate, not the question unanswerable.",
    "C066": "The phenomenon may be genuinely inexplicable within any possible framework; there are limits to explanation and the investigation has reached one.",
    "C067": "Each explanatory level is expressible only in the next higher level; explanation requires infinite ascent. The recursion is the trace of this ascent.",
    "C068": "The dependency structure is non-Archimedean: there exist statements infinitely close but not identical, with no finite connecting chain. Standard audit fails on such structures.",
    "C069": "The investigation has reached a true contradiction; the recursive dependency IS a dialetheia that cannot be resolved, only accepted.",
    "C070": "Recursive dependency is not a symptom, artifact, or problem to be solved; it IS the phenomenon the investigation was seeking. The investigation succeeded but failed to recognize success.",
}

# ============================================================
# EQUIVALENCE CLASSES
# ============================================================
# Each class contains candidates that share a core structural
# pattern after domain-specific language is stripped.

EQUIVALENCE_CLASSES = [
    {
        "class_id": "M01",
        "name": "System cannot fully examine itself",
        "shared_structure": "A system cannot fully characterize itself using only its own resources; self-examination encounters undecidability, incompleteness, or unresolvable circularity.",
        "members": ["C002", "C003", "C006", "C014", "C015", "C025", "C026", "C029", "C033", "C035", "C060", "C067"],
        "exemplar": "C002",
        "origin_families": ["computational", "self_reference", "language_structure", "mathematical_fixed_point", "category_theoretic", "measurement_framework", "unknown"],
        "n_members": 12,
    },
    {
        "class_id": "M02",
        "name": "Procedure finds its own fixed point",
        "shared_structure": "The operation applied to its own output converges to a fixed point that is the operation itself; recursion is mathematically guaranteed.",
        "members": ["C001", "C005", "C013", "C016", "C017", "C030", "C031", "C034", "C039", "C040", "C043"],
        "exemplar": "C005",
        "origin_families": ["computational", "self_reference", "mathematical_fixed_point", "category_theoretic", "dynamical_system"],
        "n_members": 11,
    },
    {
        "class_id": "M03",
        "name": "Method determines result",
        "shared_structure": "The investigation's choice of method, prior, language, or framing forces the recursive result; a different method would find different structure.",
        "members": ["C020", "C024", "C027", "C053", "C054", "C055", "C056", "C057"],
        "exemplar": "C020",
        "origin_families": ["observer_model", "language_structure", "cognitive"],
        "n_members": 8,
    },
    {
        "class_id": "M04",
        "name": "Observer and observed cannot be separated",
        "shared_structure": "The act of investigation cannot be separated from the investigated; results describe the joint observer-observed system, making the recursion a relational property.",
        "members": ["C018", "C019", "C021", "C022", "C023", "C028", "C058", "C062"],
        "exemplar": "C019",
        "origin_families": ["observer_model", "language_structure", "measurement_framework"],
        "n_members": 8,
    },
    {
        "class_id": "M05",
        "name": "Information exhausted; processing artifacts remain",
        "shared_structure": "The investigation has extracted all available discriminating information from the target; further processing operates on its own artifacts, producing apparent recursion.",
        "members": ["C007", "C008", "C009", "C010", "C011", "C012", "C045", "C049", "C063"],
        "exemplar": "C009",
        "origin_families": ["information_theoretic", "dynamical_system", "evolutionary", "measurement_framework"],
        "n_members": 9,
    },
    {
        "class_id": "M06",
        "name": "System trapped in attractor basin",
        "shared_structure": "The investigation's dynamics are governed by an attractor with a basin that traps all trajectories; escape would require external intervention or a qualitative regime change.",
        "members": ["C004", "C041", "C042", "C044", "C046", "C047", "C048", "C050", "C051", "C052", "C059"],
        "exemplar": "C041",
        "origin_families": ["computational", "dynamical_system", "evolutionary", "measurement_framework"],
        "n_members": 11,
    },
    {
        "class_id": "M07",
        "name": "Question is incoherent at this level",
        "shared_structure": "The question being asked cannot be answered within the current framework; the recursion is a symptom of a malformed or misdirected inquiry.",
        "members": ["C061", "C064", "C065", "C066", "C068", "C069"],
        "exemplar": "C064",
        "origin_families": ["measurement_framework", "unknown"],
        "n_members": 6,
    },
    {
        "class_id": "M08",
        "name": "Recursion IS the identity",
        "shared_structure": "What a thing IS is constituted by its relationships, not by intrinsic essence; the recursive relational web is not a defect but the phenomenon itself.",
        "members": ["C032", "C036", "C037", "C038", "C070"],
        "exemplar": "C037",
        "origin_families": ["mathematical_fixed_point", "category_theoretic", "unknown"],
        "n_members": 5,
    },
]

# Validate: every candidate appears in exactly one class
all_classified = set()
for cl in EQUIVALENCE_CLASSES:
    for m in cl["members"]:
        all_classified.add(m)

assert all_classified == set(NORMALIZED.keys()), (
    f"Classification mismatch: "
    f"{set(NORMALIZED.keys()) - all_classified} unclassified, "
    f"{all_classified - set(NORMALIZED.keys())} unknown"
)

# ============================================================
# COMPRESSION REPORT
# ============================================================

class_sizes = [cl["n_members"] for cl in EQUIVALENCE_CLASSES]
largest = max(EQUIVALENCE_CLASSES, key=lambda x: x["n_members"])
smallest = min(EQUIVALENCE_CLASSES, key=lambda x: x["n_members"])

# Count irreducible families: classes where all members come from
# the same original family (no cross-family compression)
irreducible_classes = []
for cl in EQUIVALENCE_CLASSES:
    families = set()
    for m in cl["members"]:
        c = next(c for c in candidates if c["id"] == m)
        families.add(c["family"])
    cl["origin_family_set"] = sorted(families)
    if len(families) == 1:
        irreducible_classes.append(cl["class_id"])

compression_report = {
    "starting_candidates": len(candidates),
    "ending_classes": len(EQUIVALENCE_CLASSES),
    "compression_ratio": round(len(candidates) / len(EQUIVALENCE_CLASSES), 2),
    "largest_class": largest["class_id"],
    "largest_class_name": largest["name"],
    "largest_class_size": largest["n_members"],
    "smallest_class": smallest["class_id"],
    "smallest_class_name": smallest["name"],
    "smallest_class_size": smallest["n_members"],
    "irreducible_classes": irreducible_classes,
    "n_irreducible": len(irreducible_classes),
    "class_sizes": class_sizes,
    "interpretation": (
        f"{len(candidates)} candidates compressed to {len(EQUIVALENCE_CLASSES)} "
        f"mechanism classes (ratio {len(candidates)/len(EQUIVALENCE_CLASSES):.1f}:1). "
        f"The largest class ({largest['name']}) absorbs {largest['n_members']} candidates. "
        f"{len(irreducible_classes)} classes are irreducible (single-family origin). "
        f"The landscape's apparent breadth is largely a vocabulary effect: "
        f"{len(EQUIVALENCE_CLASSES)} independent mechanism structures exist."
    ),
}

# ============================================================
# WRITE OUTPUTS
# ============================================================

# 1. Normalized mechanisms
with open(OUT / "t059_mechanism_normalization.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["candidate", "original_family", "original_mechanism", "normalized_mechanism"])
    for c in candidates:
        cid = c["id"]
        w.writerow([cid, c["family"], c["core_mechanism"], NORMALIZED.get(cid, "MISSING")])

print(f"Wrote {len(candidates)} normalizations to t059_mechanism_normalization.csv")

# 2. Equivalence classes
with open(OUT / "t059_equivalence_classes.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["class_id", "name", "n_members", "members", "shared_structure", "exemplar",
                 "origin_families", "same_family_only"])
    for cl in EQUIVALENCE_CLASSES:
        w.writerow([cl["class_id"], cl["name"], cl["n_members"],
                     ";".join(cl["members"]), cl["shared_structure"],
                     cl["exemplar"], ";".join(cl["origin_family_set"]),
                     cl["class_id"] in irreducible_classes])

print(f"Wrote {len(EQUIVALENCE_CLASSES)} classes to t059_equivalence_classes.csv")

# 3. Compression report
with open(OUT / "t059_compression_report.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["metric", "value"])
    for k, v in compression_report.items():
        if isinstance(v, list):
            w.writerow([k, ";".join(str(x) for x in v)])
        else:
            w.writerow([k, str(v)])

print(f"Wrote compression report to t059_compression_report.csv")

# 4. JSON version of report for analysis
with open(OUT / "t059_summary.json", "w") as f:
    json.dump(compression_report, f, indent=2)

# ============================================================
# SUMMARY
# ============================================================

print(f"\n{'='*60}")
print("COMPRESSION AUDIT RESULTS")
print(f"{'='*60}")
print(f"Starting candidates:  {compression_report['starting_candidates']}")
print(f"Ending classes:       {compression_report['ending_classes']}")
print(f"Compression ratio:    {compression_report['compression_ratio']}:1")
print(f"Largest class:        {compression_report['largest_class_name']} "
      f"({compression_report['largest_class_size']} members)")
print(f"Smallest class:       {compression_report['smallest_class_name']} "
      f"({compression_report['smallest_class_size']} members)")
print(f"Irreducible classes:  {compression_report['n_irreducible']} "
      f"({', '.join(compression_report['irreducible_classes'])})\n")

print("Class distribution:")
for cl in sorted(EQUIVALENCE_CLASSES, key=lambda x: -x["n_members"]):
    pct = 100 * cl["n_members"] / len(candidates)
    bar = "#" * cl["n_members"]
    print(f"  {cl['class_id']} {cl['name']:40s} {cl['n_members']:2d}/{len(candidates):2d} ({pct:4.0f}%) {bar}")

print(f"\nInterpretation: {compression_report['interpretation']}")
print("\nT059 complete. No truth evaluated. No evidence evaluated. No classes eliminated.")
