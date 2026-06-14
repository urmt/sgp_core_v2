"""
RD-OBSERVER.2 — Observer Comparison Framework

Compares reports from six independent observers.
Produces convergence matrices and identifies cross-observer survivors.
"""

import json
import os
from collections import defaultdict

BASE = "/home/student/sgp_core_v2"


def load_observer_reports(out_dir):
    """Load all observer reports from disk."""
    reports = {}
    for obs_id in ["A", "B", "C", "D", "E", "F"]:
        path = f"{out_dir}/report_observer_{obs_id}.json"
        if os.path.exists(path):
            with open(path) as f:
                reports[obs_id] = json.load(f)
    return reports


def extract_finding_signatures(reports):
    """
    Extract finding signatures from each observer.
    A signature is: (dataset, frozenset(variables_involved), significant_structure_keywords).
    """
    signatures = {}
    for obs_id, report in reports.items():
        sigs = set()
        for finding in report.get("findings", []):
            dataset = finding.get("dataset", "")
            variables = tuple(sorted(finding.get("variables_involved", [])))
            structure = finding.get("significant_structure", "")
            # Use first 50 chars of structure as signature
            sig_key = (dataset, variables, structure[:50])
            sigs.add(sig_key)
        signatures[obs_id] = sigs
    return signatures


def compute_pairwise_overlap(signatures):
    """
    Compute pairwise overlap between observers.
    Returns dict: (obs_i, obs_j) -> overlap_fraction.
    """
    obs_ids = sorted(signatures.keys())
    overlap = {}
    for i in range(len(obs_ids)):
        for j in range(i + 1, len(obs_ids)):
            oi, oj = obs_ids[i], obs_ids[j]
            si, sj = signatures[oi], signatures[oj]
            if len(si) == 0 or len(sj) == 0:
                overlap[(oi, oj)] = 0.0
            else:
                intersection = len(si & sj)
                union = len(si | sj)
                overlap[(oi, oj)] = intersection / union if union > 0 else 0.0
    return overlap


def compute_convergence_matrix(reports):
    """
    Compute full convergence matrix.
    Returns matrix as dict of dicts, plus summary statistics.
    """
    signatures = extract_finding_signatures(reports)
    obs_ids = sorted(reports.keys())

    # Pairwise Jaccard similarity
    pairwise = compute_pairwise_overlap(signatures)

    # Matrix form
    matrix = {}
    for oi in obs_ids:
        matrix[oi] = {}
        for oj in obs_ids:
            if oi == oj:
                matrix[oi][oj] = 1.0
            elif (oi, oj) in pairwise:
                matrix[oi][oj] = pairwise[(oi, oj)]
            else:
                matrix[oi][oj] = pairwise[(oj, oi)]

    # Summary statistics
    pair_values = list(pairwise.values())
    mean_overlap = sum(pair_values) / len(pair_values) if pair_values else 0
    max_overlap = max(pair_values) if pair_values else 0
    min_overlap = min(pair_values) if pair_values else 0

    # Find most overlapping pair
    if pairwise:
        most_similar = max(pairwise, key=pairwise.get)
        least_similar = min(pairwise, key=pairwise.get)
    else:
        most_similar = ("?", "?")
        least_similar = ("?", "?")

    # Find findings that appear in ALL observers (if any)
    all_findings = set()
    first = True
    for obs_id in obs_ids:
        sigs = signatures[obs_id]
        if first:
            all_findings = sigs
            first = False
        else:
            all_findings = all_findings & sigs

    # Find findings that appear in at least 3 observers
    finding_counts = defaultdict(int)
    for obs_id in obs_ids:
        for sig in signatures[obs_id]:
            finding_counts[sig] += 1
    common_findings = {k: v for k, v in finding_counts.items() if v >= 3}

    return {
        "matrix": matrix,
        "pairwise": pairwise,
        "summary": {
            "mean_pairwise_overlap": round(mean_overlap, 4),
            "max_pairwise_overlap": round(max_overlap, 4),
            "min_pairwise_overlap": round(min_overlap, 4),
        "most_similar_pair": list(most_similar),
        "least_similar_pair": list(least_similar),
            "total_unique_findings": sum(len(s) for s in signatures.values()),
            "findings_in_all_observers": len(all_findings),
            "findings_in_3plus_observers": len(common_findings),
        },
        "common_findings": [
            {"finding": f[2], "dataset": f[0], "variables": list(f[1]), "observers": count}
            for f, count in sorted(common_findings.items(), key=lambda x: -x[1])
        ],
        "all_observer_findings": all_findings,
    }


def identify_cross_observer_survivors(reports):
    """
    Identify findings that survive across multiple observers.
    These are the strongest candidates for observer-independent structure.
    """
    convergence = compute_convergence_matrix(reports)
    return convergence


def generate_report(reports, out_dir):
    """Generate full comparison report."""
    result = identify_cross_observer_survivors(reports)

    report_lines = [
        "# RD-OBSERVER.2 — Observer Comparison Report",
        "",
        "## Status: COMPLETE",
        "",
        "---",
        "",
        "## Convergence Matrix (Pairwise Jaccard Similarity)",
        "",
    ]

    # Matrix display
    obs_ids = sorted(reports.keys())
    header = "| Observer | " + " | ".join(obs_ids) + " |"
    sep = "|----------|" + "|".join(["------" for _ in obs_ids]) + "|"
    report_lines.append(header)
    report_lines.append(sep)
    for oi in obs_ids:
        row = f"| {oi} | "
        vals = []
        for oj in obs_ids:
            vals.append(f"{result['matrix'][oi][oj]:.3f}")
        row += " | ".join(vals) + " |"
        report_lines.append(row)

    report_lines.extend([
        "",
        "## Summary Statistics",
        "",
        f"- **Mean pairwise overlap:** {result['summary']['mean_pairwise_overlap']}",
        f"- **Max pairwise overlap:** {result['summary']['max_pairwise_overlap']} ({result['summary']['most_similar_pair']})",
        f"- **Min pairwise overlap:** {result['summary']['min_pairwise_overlap']} ({result['summary']['least_similar_pair']})",
        f"- **Total unique findings:** {result['summary']['total_unique_findings']}",
        f"- **Findings in ALL observers:** {result['summary']['findings_in_all_observers']}",
        f"- **Findings in 3+ observers:** {result['summary']['findings_in_3plus_observers']}",
        "",
        "## Common Findings (3+ observers)",
        "",
    ])

    if result["common_findings"]:
        for cf in result["common_findings"]:
            report_lines.append(
                f"- **{cf['observers']}/{len(obs_ids)} observers**: {cf['finding']} "
                f"(dataset: {cf['dataset']}, variables: {cf['variables']})"
            )
    else:
        report_lines.append("*No findings shared by 3 or more observers.*")

    report_lines.extend([
        "",
        "## Cross-Observer Survivors",
        "",
        "Findings that appear in ALL observers are the strongest candidates for observer-independent structure.",
        "",
    ])

    if result["all_observer_findings"]:
        for f in result["all_observer_findings"]:
            report_lines.append(f"- {f[2]} (dataset: {f[0]}, variables: {list(f[1])})")
    else:
        report_lines.append("*No findings appear in all observers.*")

    report_lines.extend([
        "",
        "## Interpretation",
        "",
        "Per SR-32: Evidence Strength ∝ Observer Invariance.",
        "",
        "If all observers find the same structure despite different priors,",
        "that structure is likely a property of the data, not the observer.",
        "",
        "If observers disagree, the disagreement itself is informative:",
        "it reveals observer-dependent structure.",
        "",
        "**Critical caveat:** All observers are generated by the same LLM.",
        "This is pseudo-independence (SR-32). True independence requires",
        "genuinely different research groups.",
        "",
        "---",
        "",
        "## Artifact",
        "",
        f"`{out_dir}/RD_OBSERVER_2_COMPARISON_REPORT.md`",
    ])

    report_text = "\n".join(report_lines)

    with open(f"{out_dir}/RD_OBSERVER_2_COMPARISON_REPORT.md", "w") as f:
        f.write(report_text)

    # Convert tuple keys to strings for JSON serialization
    result_json = dict(result)
    result_json["pairwise"] = {f"{k[0]}_{k[1]}": v for k, v in result["pairwise"].items()}
    result_json["matrix"] = result["matrix"]
    with open(f"{out_dir}/convergence_data.json", "w") as f:
        json.dump(result_json, f, indent=2, default=str)

    print(f"Comparison report written to {out_dir}/RD_OBSERVER_2_COMPARISON_REPORT.md")
    print(f"Convergence data written to {out_dir}/convergence_data.json")

    return result
