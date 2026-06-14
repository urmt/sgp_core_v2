"""
RD-HIST.1 Phase 1: Archive Census

Enumerate every available study:
- T* (T-series)
- Phase* (Phase-series)
- RD* (RD-series)
- interaction_first*
- other experimental branches

For each file record:
- ID
- Date/Phase
- Purpose
- Inputs
- Outputs
- Status (success/failure/abandoned)
"""

import os
import json
from pathlib import Path
from datetime import datetime

ROOT = Path("/home/student/sgp_core_v2")

def find_all_studies():
    """Find all study files in the archive."""
    studies = []
    
    # T-series
    for f in sorted(ROOT.glob("T*.py")):
        studies.append({
            'id': f.stem,
            'series': 'T',
            'path': str(f),
            'size': f.stat().st_size,
            'modified': datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
        })
    
    # Phase-series
    phase_dir = ROOT / "phases"
    if phase_dir.exists():
        for f in sorted(phase_dir.glob("phase*")):
            if f.is_file():
                studies.append({
                    'id': f.stem,
                    'series': 'Phase',
                    'path': str(f),
                    'size': f.stat().st_size,
                    'modified': datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                })
    
    # RD-series
    for f in sorted(ROOT.glob("RD*.md")):
        studies.append({
            'id': f.stem,
            'series': 'RD',
            'path': str(f),
            'size': f.stat().st_size,
            'modified': datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
        })
    
    # RD audits
    audit_dir = ROOT / "audits"
    if audit_dir.exists():
        for f in sorted(audit_dir.glob("rd*.py")):
            studies.append({
                'id': f.stem,
                'series': 'RD-audit',
                'path': str(f),
                'size': f.stat().st_size,
                'modified': datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
            })
    
    # interaction_first
    if_dir = ROOT / "coherence-benchmark" / "interaction_first"
    if if_dir.exists():
        for f in sorted(if_dir.glob("*.py")):
            studies.append({
                'id': f.stem,
                'series': 'interaction_first',
                'path': str(f),
                'size': f.stat().st_size,
                'modified': datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
            })
    
    # Scripts
    scripts_dir = ROOT / "scripts"
    if scripts_dir.exists():
        for f in sorted(scripts_dir.glob("**/*.py")):
            if f.name != "__init__.py":
                studies.append({
                    'id': f.stem,
                    'series': 'scripts',
                    'path': str(f),
                    'size': f.stat().st_size,
                    'modified': datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                })
    
    return studies

def classify_status(study):
    """Classify study status based on size and content."""
    if study['size'] < 100:
        return 'abandoned'
    elif study['size'] < 500:
        return 'minimal'
    else:
        return 'substantive'

def run_census():
    print("="*70)
    print("RD-HIST.1 PHASE 1: ARCHIVE CENSUS")
    print("="*70)
    
    studies = find_all_studies()
    
    # Classify by series
    series_counts = {}
    for s in studies:
        series = s['series']
        if series not in series_counts:
            series_counts[series] = 0
        series_counts[series] += 1
    
    print("\n--- STUDIES BY SERIES ---\n")
    for series, count in sorted(series_counts.items()):
        print(f"{series}: {count} studies")
    
    print(f"\nTotal: {len(studies)} studies")
    
    # Classify by status
    status_counts = {}
    for s in studies:
        status = classify_status(s)
        s['status'] = status
        if status not in status_counts:
            status_counts[status] = 0
        status_counts[status] += 1
    
    print("\n--- STUDIES BY STATUS ---\n")
    for status, count in sorted(status_counts.items()):
        print(f"{status}: {count} studies")
    
    # Save index
    index = {
        'total_studies': len(studies),
        'series_counts': series_counts,
        'status_counts': status_counts,
        'studies': studies,
    }
    
    with open(ROOT / 'audits' / 'RD_HIST_ARCHIVE_INDEX.json', 'w') as f:
        json.dump(index, f, indent=2, default=str)
    
    print("\nSaved to audits/RD_HIST_ARCHIVE_INDEX.json")
    
    return studies

if __name__ == '__main__':
    run_census()
