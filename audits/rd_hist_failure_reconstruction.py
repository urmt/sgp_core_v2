"""
RD-HIST.1 Phase 5: Failure Reconstruction

Most important phase.

Find:
- abandoned studies
- unfinished studies
- empty directories
- negative results
- dead branches
- unpublished experiments

The archive currently suffers from success bias.
This phase exists specifically to counter that.
"""

import os
import json
from pathlib import Path

ROOT = Path("/home/student/sgp_core_v2")

def find_failures():
    failures = []
    
    # Empty directories
    for d in ROOT.rglob("*"):
        if d.is_dir() and not any(d.iterdir()):
            failures.append({
                'id': str(d.relative_to(ROOT)),
                'type': 'empty_directory',
                'detail': 'Directory created but never populated',
            })
    
    # Small Python files (< 100 bytes)
    for f in ROOT.rglob("*.py"):
        if f.stat().st_size < 100 and f.name != "__init__.py":
            failures.append({
                'id': f.stem,
                'type': 'minimal_file',
                'detail': f'File only {f.stat().st_size} bytes',
                'path': str(f.relative_to(ROOT)),
            })
    
    # interaction_first (abandoned experiments)
    if_dir = ROOT / "coherence-benchmark" / "interaction_first"
    if if_dir.exists():
        for f in if_dir.glob("*.py"):
            failures.append({
                'id': f.stem,
                'type': 'abandoned_experiment',
                'detail': 'Interaction experiment coded but never completed',
                'path': str(f.relative_to(ROOT)),
            })
    
    # interaction_models (empty directory)
    im_dir = ROOT / "interaction_models"
    if im_dir.exists() and not any(im_dir.iterdir()):
        failures.append({
            'id': 'interaction_models',
            'type': 'empty_directory',
            'detail': 'Directory created for interaction models, never populated',
        })
    
    # Check for TODO/FIXME markers
    for f in ROOT.rglob("*.py"):
        try:
            content = f.read_text()
            if 'TODO' in content or 'FIXME' in content or 'BROKEN' in content:
                failures.append({
                    'id': f.stem,
                    'type': 'incomplete_marker',
                    'detail': f'Contains TODO/FIXME/BROKEN markers',
                    'path': str(f.relative_to(ROOT)),
                })
        except:
            pass
    
    return failures

def analyze_failures():
    print("="*70)
    print("RD-HIST.1 PHASE 5: FAILURE RECONSTRUCTION")
    print("="*70)
    
    failures = find_failures()
    
    # Count by type
    print("\n--- FAILURES BY TYPE ---\n")
    
    type_counts = {}
    for f in failures:
        t = f['type']
        if t not in type_counts:
            type_counts[t] = 0
        type_counts[t] += 1
    
    for t, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"{t}: {count}")
    
    print(f"\nTotal failures: {len(failures)}")
    
    # Show key failures
    print("\n--- KEY FAILURES ---\n")
    
    key_failures = [f for f in failures if f['type'] in ['empty_directory', 'abandoned_experiment']]
    for f in key_failures:
        print(f"  {f['id']}: {f['detail']}")
    
    # Save
    output = {
        'total_failures': len(failures),
        'type_counts': type_counts,
        'failures': failures,
    }
    
    with open(ROOT / 'audits' / 'RD_HIST_FAILURE_CATALOG.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("\nSaved to audits/RD_HIST_FAILURE_CATALOG.json")

if __name__ == '__main__':
    analyze_failures()
