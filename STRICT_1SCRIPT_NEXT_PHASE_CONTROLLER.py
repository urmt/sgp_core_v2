#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime

REGISTRY_PATH = Path("STRICT_RESEARCH_REGISTRY/CANONICAL_REGISTRY.json")
RUNLOG_PATH = Path("STRICT_RESEARCH_REGISTRY/RUN_HISTORY.json")

if not REGISTRY_PATH.exists(): raise RuntimeError("CANONICAL REGISTRY NOT FOUND")
with open(REGISTRY_PATH, "r") as f: REGISTRY = json.load(f)

APPROVED_ACTIONS = {
    "A01": {"name": "Replace scalar gate with LDA readout", "status": "APPROVED", "goal": "recover separable information already present"},
    "A02": {"name": "Train domain-specific classifiers", "status": "APPROVED", "goal": "improve rw_trend and regime_switch"},
    "A03": {"name": "Calibrated probabilistic detector", "status": "APPROVED", "goal": "replace brittle threshold gate"},
    "A04": {"name": "Transform confusion analysis", "status": "APPROVED", "goal": "identify transform overlaps"},
    "A05": {"name": "Benchmark suite generation", "status": "APPROVED", "goal": "fully reproducible evaluation"},
    "A06": {"name": "Manuscript-quality outputs", "status": "APPROVED", "goal": "publishable summaries/figures/tables"}
}

FORBIDDEN_ACTIONS = ["modify V2_079 metrics", "modify V2_079 transforms", "modify V2_079 signals", "reuse invalidated runs", "mix canonical and invalid embeddings"]

def load_history():
    if not RUNLOG_PATH.exists(): return []
    with open(RUNLOG_PATH, "r") as f: return json.load(f)
def save_history(history):
    with open(RUNLOG_PATH, "w") as f: json.dump(history, f, indent=2)
def log_action(action_id):
    history = load_history()
    action = APPROVED_ACTIONS[action_id]
    history.append({"timestamp": datetime.utcnow().isoformat()+"Z", "action_id": action_id, "action": action["name"], "goal": action["goal"], "status": "AUTHORIZED"})
    save_history(history)
    print(f"[LOGGED] {action_id}: {action['name']}")

def display_status():
    print("="*70)
    print("STRICT 1SCRIPT NEXT PHASE CONTROLLER")
    print("="*70)
    print("\nCANONICAL ARCHITECTURE")
    print("-"*70)
    arch = REGISTRY["canonical_architecture"]
    print(f"NAME   : {arch['name']}")
    print(f"STATUS : {arch['status']}")
    print("\nVALIDATED FINDINGS")
    print("-"*70)
    for item in REGISTRY["validated_findings"]: print(f"{item['id']}  {item['finding']}")
    print("\nAPPROVED NEXT ACTIONS")
    print("-"*70)
    for k,v in APPROVED_ACTIONS.items(): print(f"{k}  {v['name']}")
    print("\nFORBIDDEN ACTIONS")
    print("-"*70)
    for x in FORBIDDEN_ACTIONS: print(f"- {x}")
    print("\nSYSTEM STATUS")
    print("-"*70)
    print("VALID LINEAGE : ACTIVE")
    print("INVALID RUNS  : QUARANTINED")
    print("PROTOCOL      : STRICT 1SCRIPT")
    print("="*70)

if __name__ == "__main__":
    display_status()
    # Log A01 as selected next step
    log_action("A01")
    print("\n[A01] Replace scalar gate with LDA readout - APPROVED FOR EXECUTION")