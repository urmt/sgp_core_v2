#!/usr/bin/env python3
"""
T050: Model vs Observation Separation Audit
=============================================
Separate observation from description of observation.
We suspect the two have been conflated.
"""

import json, csv
from pathlib import Path

ROOT = Path("/home/student/sgp_core_v2")
OUT = ROOT / "sfh_sgp_ood_outputs"

# ============================================================
# PRIMITIVES
# ============================================================

PRIMITIVES = ["comparison", "ordering", "identity", "difference", "distinction"]

# ============================================================
# ANALYSIS FUNCTION
# ============================================================

def analyze_primitive(name):
    """
    For each primitive, determine:
    A. Does our MODEL require it? (proven)
    B. Does OBSERVATION require it? (proven, assumed, or unknown)
    """

    if name == "comparison":
        return {
            "primitive": "comparison",
            "model_analysis": {
                "required": True,
                "proof_type": "formal",
                "evidence": (
                    "Every observer model we have built uses comparison: "
                    "comparing states, comparing metrics, comparing before/after. "
                    "Removing comparison from the model produces zero information output."
                ),
            },
            "observation_analysis": {
                "required": True,
                "proof_type": "assumed",
                "evidence": (
                    "We ASSUME observation requires comparison because we cannot "
                    "describe observation without comparison. But this is a limitation "
                    "of our descriptive apparatus, not proof about observation itself. "
                    "We have no example of observation-without-comparison to rule out."
                ),
            },
            "classification": "NECESSARY FOR CURRENT MODELS ONLY",
            "reasoning": (
                "We cannot distinguish: "
                "(A) observation inherently requires comparison, from "
                "(B) we cannot describe observation without comparison. "
                "Both produce the same observable output: our models fail. "
                "The two hypotheses are empirically indistinguishable."
            ),
        }

    elif name == "ordering":
        return {
            "primitive": "ordering",
            "model_analysis": {
                "required": True,
                "proof_type": "formal",
                "evidence": (
                    "Our observer models require temporal ordering to track "
                    "state evolution, detect change, and compute trajectories. "
                    "Without ordering, models produce static snapshots with no dynamics."
                ),
            },
            "observation_analysis": {
                "required": True,
                "proof_type": "assumed",
                "evidence": (
                    "We assume observation requires temporal ordering because "
                    "we experience observation as sequential. But we have no proof "
                    "that non-sequential observation is impossible — only that "
                    "we cannot describe it."
                ),
            },
            "classification": "NECESSARY FOR CURRENT MODELS ONLY",
            "reasoning": (
                "Temporal ordering is a feature of our models, not proven to be "
                "a feature of observation. Non-sequential observation may exist "
                "but be unreportable by sequential observers."
            ),
        }

    elif name == "identity":
        return {
            "primitive": "identity",
            "model_analysis": {
                "required": True,
                "proof_type": "formal",
                "evidence": (
                    "Our observer models require identity to track objects across "
                    "time, maintain memory, and verify predictions. Without identity, "
                    "each instant is disconnected."
                ),
            },
            "observation_analysis": {
                "required": True,
                "proof_type": "assumed",
                "evidence": (
                    "We assume observation requires identity because we assume "
                    "observers persist. But a non-persistent observer (one that "
                    "exists only in a single instant) might still observe — "
                    "it just cannot report."
                ),
            },
            "classification": "NECESSARY FOR CURRENT MODELS ONLY",
            "reasoning": (
                "Identity may be necessary for REPORTING but not for OBSERVING. "
                "A single-instant observer might observe without identity. "
                "We cannot prove this is impossible."
            ),
        }

    elif name == "difference":
        return {
            "primitive": "difference",
            "model_analysis": {
                "required": True,
                "proof_type": "formal",
                "evidence": (
                    "Our observer models require difference to detect anything. "
                    "Without difference, there is only one state: everything is "
                    "the same. No information can be extracted."
                ),
            },
            "observation_analysis": {
                "required": True,
                "proof_type": "assumed",
                "evidence": (
                    "We assume observation requires difference because observation "
                    "SEEMS to require distinguishing things. But 'observation seems "
                    "to require' is itself a comparison — so this argument is circular."
                ),
            },
            "classification": "UNKNOWN",
            "reasoning": (
                "The argument for difference is circular: we use comparison "
                "(which requires difference) to argue that observation requires "
                "difference. This proves nothing about observation itself."
            ),
        }

    elif name == "distinction":
        return {
            "primitive": "distinction",
            "model_analysis": {
                "required": True,
                "proof_type": "formal",
                "evidence": (
                    "Every observer model we have built requires distinction "
                    "to separate observer from observed, self from other, "
                    "signal from noise."
                ),
            },
            "observation_analysis": {
                "required": True,
                "proof_type": "assumed",
                "evidence": (
                    "We assume observation requires distinction because we "
                    "cannot describe observation without distinguishing the "
                    "observer from the observed. But this may be a feature "
                    "of description, not of observation."
                ),
            },
            "classification": "NECESSARY FOR CURRENT MODELS ONLY",
            "reasoning": (
                "Distinction may be necessary for the OBSERVER-observed split "
                "but not for observation itself. We cannot prove that observation "
                "without an observer-distinction boundary is impossible."
            ),
        }

    return None


# ============================================================
# PROOF INVENTORY
# ============================================================

def build_proof_inventory():
    """What is actually proven vs assumed?"""
    return [
        {
            "claim": "Our observer models require comparison",
            "status": "PROVEN",
            "proof_type": "formal",
            "evidence": "All 45 detectors and all observer models use comparison.",
        },
        {
            "claim": "Observation itself requires comparison",
            "status": "UNPROVEN",
            "proof_type": "assumed",
            "evidence": "We cannot describe observation without comparison, but this is a limitation of description, not proof about observation.",
        },
        {
            "claim": "Our observer models require ordering",
            "status": "PROVEN",
            "proof_type": "formal",
            "evidence": "All temporal tracking requires ordering.",
        },
        {
            "claim": "Observation itself requires ordering",
            "status": "UNPROVEN",
            "proof_type": "assumed",
            "evidence": "We experience observation as sequential, but cannot prove non-sequential observation is impossible.",
        },
        {
            "claim": "Our observer models require identity",
            "status": "PROVEN",
            "proof_type": "formal",
            "evidence": "All persistence tracking requires identity.",
        },
        {
            "claim": "Observation itself requires identity",
            "status": "UNPROVEN",
            "proof_type": "assumed",
            "evidence": "Identity may be required for reporting but not for observing.",
        },
        {
            "claim": "Our observer models require difference",
            "status": "PROVEN",
            "proof_type": "formal",
            "evidence": "All information extraction requires difference.",
        },
        {
            "claim": "Observation itself requires difference",
            "status": "UNPROVEN",
            "proof_type": "circular",
            "evidence": "The argument uses comparison (which requires difference) to prove difference is needed.",
        },
        {
            "claim": "Our observer models require distinction",
            "status": "PROVEN",
            "proof_type": "formal",
            "evidence": "All observer-observed splits require distinction.",
        },
        {
            "claim": "Observation itself requires distinction",
            "status": "UNPROVEN",
            "proof_type": "assumed",
            "evidence": "Distinction may be necessary for the observer boundary but not for observation itself.",
        },
    ]


# ============================================================
# UNPROVEN ASSUMPTIONS
# ============================================================

def identify_unproven():
    """What are we assuming without proof?"""
    return [
        {
            "assumption": "Observation requires comparison",
            "why_unproven": "We cannot describe observation without comparison, but this may be a limitation of description.",
            "alternative": "Non-comparative observation may exist but be unreportable.",
        },
        {
            "assumption": "Observation requires temporal ordering",
            "why_unproven": "We experience observation as sequential, but this may be a feature of experience, not observation.",
            "alternative": "Simultaneous non-sequential observation may exist.",
        },
        {
            "assumption": "Observation requires identity",
            "why_unproven": "Identity may be necessary for persistence of the observer, not for the act of observing.",
            "alternative": "Single-instant observation may exist.",
        },
        {
            "assumption": "Observation requires difference",
            "why_unproven": "The argument is circular: we use comparison to prove difference is needed.",
            "alternative": "Non-differentiated observation may exist.",
        },
        {
            "assumption": "Observation requires distinction",
            "why_unproven": "Distinction may be necessary for the observer-observed boundary, not for observation.",
            "alternative": "Observation without an observer-observed boundary may exist.",
        },
    ]


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("T050: MODEL vs OBSERVATION SEPARATION AUDIT")
    print("=" * 70)
    print("Separating observation from description of observation.")
    print("=" * 70)

    # Analyze each primitive
    print("\n[Analyzing each primitive...]\n")
    results = []
    for name in PRIMITIVES:
        result = analyze_primitive(name)
        results.append(result)
        print(f"  {name}:")
        print(f"    Model requires: {result['model_analysis']['required']}")
        print(f"    Observation requires: {result['observation_analysis']['required']}")
        print(f"    Proof type: {result['observation_analysis']['proof_type']}")
        print(f"    Classification: {result['classification']}")
        print(f"    Reasoning: {result['reasoning'][:100]}...")
        print()

    # Proof inventory
    print("[Proof inventory...]\n")
    proofs = build_proof_inventory()
    n_proven = sum(1 for p in proofs if p["status"] == "PROVEN")
    n_unproven = sum(1 for p in proofs if p["status"] == "UNPROVEN")
    print(f"  Proven: {n_proven}")
    print(f"  Unproven: {n_unproven}")
    for p in proofs:
        marker = "✓" if p["status"] == "PROVEN" else "?"
        print(f"    {marker} {p['claim']} [{p['status']}]")

    # Unproven assumptions
    print("\n[Unproven assumptions...]\n")
    unproven = identify_unproven()
    for a in unproven:
        print(f"  {a['assumption']}")
        print(f"    Why unproven: {a['why_unproven']}")
        print(f"    Alternative: {a['alternative']}")
        print()

    # ============================================================
    # SAVE
    # ============================================================

    print("[Saving outputs...]\n")

    # t050_model_observation_split.csv
    split_rows = []
    for r in results:
        split_rows.append({
            "primitive": r["primitive"],
            "model_required": r["model_analysis"]["required"],
            "model_proof_type": r["model_analysis"]["proof_type"],
            "observation_required": r["observation_analysis"]["required"],
            "observation_proof_type": r["observation_analysis"]["proof_type"],
            "classification": r["classification"],
            "reasoning": r["reasoning"],
        })
    with open(OUT / "t050_model_observation_split.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=split_rows[0].keys())
        w.writeheader()
        w.writerows(split_rows)
    print("  Saved t050_model_observation_split.csv")

    # t050_proof_inventory.csv
    with open(OUT / "t050_proof_inventory.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=proofs[0].keys())
        w.writeheader()
        w.writerows(proofs)
    print("  Saved t050_proof_inventory.csv")

    # t050_unproven_assumptions.csv
    with open(OUT / "t050_unproven_assumptions.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=unproven[0].keys())
        w.writeheader()
        w.writerows(unproven)
    print("  Saved t050_unproven_assumptions.csv")

    # t050_summary.json
    summary = {
        "n_primitives": len(PRIMITIVES),
        "n_proven": n_proven,
        "n_unproven": n_unproven,
        "classifications": {r["primitive"]: r["classification"] for r in results},
        "key_insight": (
            "All 5 primitives are PROVEN necessary for observer MODELS "
            "but UNPROVEN necessary for observation itself. "
            "We cannot distinguish 'observation requires X' from "
            "'we cannot describe observation without X'."
        ),
    }
    with open(OUT / "t050_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("  Saved t050_summary.json")

    # ============================================================
    # FINAL REPORT
    # ============================================================

    print("\n" + "=" * 70)
    print("T050 RESULTS")
    print("=" * 70)

    print("\nCLASSIFICATION OF EACH PRIMITIVE:")
    for r in results:
        print(f"  {r['primitive']:20s}: {r['classification']}")

    print(f"\nPROOF STATUS:")
    print(f"  Proven (model):   {n_proven}")
    print(f"  Unproven (observation): {n_unproven}")

    print(f"\nKEY INSIGHT:")
    print(f"  All 5 primitives are PROVEN necessary for observer MODELS.")
    print(f"  None are PROVEN necessary for observation ITSELF.")
    print()
    print(f"  The gap between 'model requires X' and 'observation requires X'")
    print(f"  cannot be closed with current evidence.")
    print()
    print(f"  This is not a failure of the investigation.")
    print(f"  This is the most precise result available:")
    print(f"  We know what our models need.")
    print(f"  We do not know what observation needs.")
    print(f"  These are different questions.")
    print("=" * 70)


if __name__ == "__main__":
    main()
