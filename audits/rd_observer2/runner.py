"""
RD-OBSERVER.2 — Main Runner

Generates blinded data, creates observer prompts, and documents the procedure.
Actual observer execution happens via parallel Task agents.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from blinded_data import create_blinded_datasets
from observers import get_all_observers, format_observer_prompt
from comparison import generate_report

BASE = "/home/student/sgp_core_v2"


def generate_prompts():
    """Generate prompts for all six observers."""
    out_dir = f"{BASE}/audits/rd_observer2/blinded"
    prompt_dir = f"{BASE}/audits/rd_observer2/prompts"
    os.makedirs(prompt_dir, exist_ok=True)

    # Load blinded data
    with open(f"{out_dir}/dataset_granular_ensemble.json") as f:
        t901 = json.load(f)
    with open(f"{out_dir}/dataset_system_results.json") as f:
        t081 = json.load(f)
    with open(f"{out_dir}/dataset_historical_summary.txt") as f:
        hist = f.read()

    data_text = f"""=== DATASET 1: Granular Simulation Ensemble ===
60 runs of a particle simulation with 11 measured variables per run.
Each run has a run_id, a condition parameter, and 10 metric variables (A through K).
Variables A-K are anonymized. condition ranges from 0.05 to 0.8.

First 5 runs:
{json.dumps(t901[:5], indent=2)}

Summary statistics:
- Number of runs: {len(t901)}
- Variables per run: {len(t901[0]) - 2}
- Conditions: {sorted(set(r['condition'] for r in t901))}

Full dataset: {json.dumps(t901, indent=2)}

=== DATASET 2: System Evaluation Results ===
240 systems evaluated across 37 measured variables.
Each system has a system_id, boolean flags, and numeric variables.
Variables are anonymized as var_N.

First 3 systems:
{json.dumps(t081[:3], indent=2)}

Summary statistics:
- Number of systems: {len(t081)}
- Variables per system: {len(t081[0]) - 1}

Full dataset (first 20 systems for tractability):
{json.dumps(t081[:20], indent=2)}

=== DATASET 3: Historical Study Summary ===
Summary of 236 studies investigating complex system behavior.
Terminology has been anonymized.

{hist}
"""

    observers = get_all_observers()
    prompts = {}
    for obs_id, obs_def in observers.items():
        prompt = format_observer_prompt(obs_id, data_text)
        prompts[obs_id] = prompt
        with open(f"{prompt_dir}/prompt_observer_{obs_id}.txt", "w") as f:
            f.write(prompt)

    print(f"Prompts generated for {len(prompts)} observers in {prompt_dir}")
    return prompts


def load_reports_and_compare():
    """Load observer reports and run comparison."""
    report_dir = f"{BASE}/audits/rd_observer2/reports"
    result = generate_report({}, report_dir)  # Will load from disk
    return result


if __name__ == "__main__":
    print("=" * 60)
    print("RD-OBSERVER.2 — Independent Observer Experiment")
    print("=" * 60)

    # Step 1: Create blinded datasets
    print("\nStep 1: Creating blinded datasets...")
    create_blinded_datasets()

    # Step 2: Generate observer prompts
    print("\nStep 2: Generating observer prompts...")
    prompts = generate_prompts()

    # Step 3: Document procedure
    print("\nStep 3: Procedure documented.")
    print("  Next: Run each observer prompt via Task agents.")
    print("  Then: Run comparison.")

    print("\n" + "=" * 60)
    print("READY FOR OBSERVER EXECUTION")
    print("=" * 60)
