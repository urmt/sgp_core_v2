#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime

ROOT = Path("STRICT_RESEARCH_REGISTRY")
ROOT.mkdir(exist_ok=True)
REGISTRY_PATH = ROOT / "CANONICAL_REGISTRY.json"

REGISTRY = {
    "project": "V2 Temporal Transform Detection",
    "last_updated_utc": datetime.utcnow().isoformat() + "Z",
    "canonical_architecture": {
        "name": "V2_079",
        "status": "FROZEN",
        "rules": ["DO NOT MODIFY METRICS", "DO NOT MODIFY SIGNALS", "DO NOT MODIFY TRANSFORMS", "ONLY CHANGE READOUT/GATE", "EMBEDDINGS ARE CANONICAL"]
    },
    "validated_findings": [
        {"id": "F001", "finding": "V2_079 embeddings are separable", "evidence": "1NN accuracy = 0.80 (chance = 0.20)", "status": "VALID"},
        {"id": "F002", "finding": "LDA recovers substantially more information than scalar gate", "evidence": "LDA AUC = 0.905 vs gate pass ~0.76", "status": "VALID"},
        {"id": "F003", "finding": "Gate geometry destroys separable information", "evidence": "regime_switch gate=3/10 while LDA=0.64", "status": "VALID"},
        {"id": "F004", "finding": "M4 dead metric for oscillatory domains", "evidence": "chirp/coupled_osc M4 std = 0 across all seeds", "status": "VALID"},
        {"id": "F005", "finding": "Cross-version comparisons before audit were contaminated", "evidence": "different versions used different random signal realizations", "status": "VALID"}
    ],
    "invalidated_runs": [
        {"name": "STRICT_1SCRIPT_RECOVERY_PROTOCOL.py", "reason": "metrics diverged from canonical V2_079", "status": "INVALIDATED"},
        {"name": "Early V2_082 standardized version", "reason": "signals standardized to unit variance", "status": "INVALIDATED"},
        {"name": "Modified stitch transform variants", "reason": "transform definitions diverged from V2_079", "status": "INVALIDATED"}
    ],
    "forensic_findings": [
        {"id": "B001", "bug": "V2_076 embedding dimension alignment bug", "severity": "CRITICAL"},
        {"id": "B002", "bug": "V2_079/V2_080 eigvalsh singular correlation crash", "severity": "CRITICAL"},
        {"id": "B003", "bug": "V2_080 jitter bins violate monotonicity", "severity": "CRITICAL"},
        {"id": "B004", "bug": "V2_081 global correlation accumulator bug", "severity": "HIGH"}
    ],
    "approved_next_steps": [
        "replace scalar gate with discriminative classifier",
        "train domain-specific readouts",
        "evaluate calibrated probabilistic detectors",
        "perform transform confusion analysis",
        "write manuscript-quality summary",
        "produce reproducible benchmark suite"
    ]
}

with open(REGISTRY_PATH, "w") as f:
    json.dump(REGISTRY, f, indent=2)

print("="*70)
print("STRICT RESEARCH REGISTRY WRITTEN")
print("="*70)
print(REGISTRY_PATH)
print("="*70)
print(f"Validated findings: {len(REGISTRY['validated_findings'])}")
print(f"Invalidated runs: {len(REGISTRY['invalidated_runs'])}")
print(f"Approved next steps: {len(REGISTRY['approved_next_steps'])}")