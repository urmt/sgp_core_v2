#!/usr/bin/env python3
"""
RD-WELL.5D.R3A — Descriptor Ladder Audit

Audit all descriptors used in RD-WELL.5D.R3 according to the descriptor ladder:
- Layer 0 — Raw: mean, variance, entropy, power spectrum, component count, frame difference
- Layer 1 — Derived: stabilization, boundary formation, periodicity, drift, repetition
- Layer 2 — Interpretive: organization, coherence, adaptation, information (FORBIDDEN for metrics)

Metrics may only consume Layer 0 or Layer 1. Layer 2 is forbidden.
"""

import numpy as np
import os
import json


def classify_descriptor(descriptor_name):
    """Classify a descriptor according to the descriptor ladder."""
    layer_0_descriptors = [
        'mean', 'variance', 'entropy', 'power_spectrum', 'component_count',
        'frame_difference', 'spatial_autocorrelation', 'mean_intensity',
        'variance_over_time', 'frame_to_frame_difference'
    ]

    layer_1_descriptors = [
        'stabilization', 'boundary_formation', 'periodicity', 'drift',
        'repetition', 'movement', 'disappearance', 'appearance'
    ]

    layer_2_descriptors = [
        'organization', 'coherence', 'adaptation', 'information',
        'boundary_symmetry', 'appearance_trend', 'stabilization_pattern'
    ]

    if descriptor_name in layer_0_descriptors:
        return 'Layer_0'
    elif descriptor_name in layer_1_descriptors:
        return 'Layer_1'
    elif descriptor_name in layer_2_descriptors:
        return 'Layer_2'
    else:
        return 'Unknown'


def audit_descriptors(phenomena):
    """Audit all descriptors in the phenomena dictionary."""
    audit_results = {
        'layer_0': [],
        'layer_1': [],
        'layer_2': [],
        'unknown': []
    }

    for phenomenon_name, phenomenon_data in phenomena.items():
        layer = classify_descriptor(phenomenon_name)

        if layer == 'Layer_0':
            audit_results['layer_0'].append(phenomenon_name)
        elif layer == 'Layer_1':
            audit_results['layer_1'].append(phenomenon_name)
        elif layer == 'Layer_2':
            audit_results['layer_2'].append(phenomenon_name)
        else:
            audit_results['unknown'].append(phenomenon_name)

    return audit_results


def reclassify_layer_2_to_layer_1(descriptor_name):
    """Reclassify Layer 2 descriptors to Layer 1 where possible."""
    reclassification_map = {
        'boundary_symmetry': 'boundary_formation',
        'appearance_trend': 'mean_intensity_over_time',
        'stabilization_pattern': 'frame_difference_trend'
    }

    return reclassification_map.get(descriptor_name, descriptor_name)


def main():
    print("RD-WELL.5D.R3A — Descriptor Ladder Audit")
    print("=" * 60)
    print("Descriptor Ladder:")
    print("  Layer 0 — Raw: mean, variance, entropy, power spectrum, component count, frame difference")
    print("  Layer 1 — Derived: stabilization, boundary formation, periodicity, drift, repetition")
    print("  Layer 2 — Interpretive: organization, coherence, adaptation, information (FORBIDDEN)")
    print("=" * 60)

    output_dir = "/home/student/sgp_core_v2/audits/rd_well5d_r3a"
    os.makedirs(output_dir, exist_ok=True)

    # Load cross-domain comparison results
    comparison_file = "/home/student/sgp_core_v2/audits/rd_well5d_r3/cross_domain_comparison.json"
    with open(comparison_file, 'r') as f:
        comparison_data = json.load(f)

    # Audit descriptors for each field
    print("\n" + "=" * 60)
    print("DESCRIPTOR AUDIT")
    print("=" * 60)

    all_audit_results = {}

    for field_id, phenomena in comparison_data['phenomena'].items():
        print(f"\n{'#'*60}")
        print(f"FIELD: {field_id}")
        print(f"{'#'*60}")

        audit_results = audit_descriptors(phenomena)
        all_audit_results[field_id] = audit_results

        print(f"  Layer 0 (Raw): {audit_results['layer_0']}")
        print(f"  Layer 1 (Derived): {audit_results['layer_1']}")
        print(f"  Layer 2 (Interpretive): {audit_results['layer_2']}")
        print(f"  Unknown: {audit_results['unknown']}")

    # Audit comparison descriptors
    print("\n" + "=" * 60)
    print("COMPARISON DESCRIPTOR AUDIT")
    print("=" * 60)

    comparison_audit = []
    for comparison in comparison_data['comparisons']:
        print(f"\n{comparison['domain1']} vs {comparison['domain2']}")

        for similarity in comparison['similarities']:
            descriptor = similarity['phenomenon']
            layer = classify_descriptor(descriptor)
            print(f"  {descriptor}: {layer}")

            comparison_audit.append({
                'descriptor': descriptor,
                'layer': layer,
                'domains': f"{comparison['domain1']} vs {comparison['domain2']}"
            })

        for difference in comparison['differences']:
            descriptor = difference['phenomenon']
            layer = classify_descriptor(descriptor)
            print(f"  {descriptor}: {layer}")

            comparison_audit.append({
                'descriptor': descriptor,
                'layer': layer,
                'domains': f"{comparison['domain1']} vs {comparison['domain2']}"
            })

    # Reclassification recommendations
    print("\n" + "=" * 60)
    print("RECLASSIFICATION RECOMMENDATIONS")
    print("=" * 60)

    for item in comparison_audit:
        if item['layer'] == 'Layer_2':
            reclassified = reclassify_layer_2_to_layer_1(item['descriptor'])
            print(f"  {item['descriptor']} → {reclassified}")

    # Save audit results
    output_file = os.path.join(output_dir, "descriptor_ladder_audit.json")
    with open(output_file, 'w') as f:
        json.dump({
            'field_audits': all_audit_results,
            'comparison_audit': comparison_audit,
            'reclassification_recommendations': {
                item['descriptor']: reclassify_layer_2_to_layer_1(item['descriptor'])
                for item in comparison_audit if item['layer'] == 'Layer_2'
            }
        }, f, indent=2)

    print(f"\nAudit results saved to: {output_file}")

    print("\n" + "=" * 60)
    print("Status: Descriptor ladder audit complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
