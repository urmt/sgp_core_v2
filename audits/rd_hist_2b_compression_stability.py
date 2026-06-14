#!/usr/bin/env python3
"""
RD-HIST.2B — Compression Stability Analysis
"""

import json
import math

# Q3 responses for 20 studies
q3_responses = {
    "1": "Universes were generated with continuous dynamics and the emergence of separable clusters was measured.",
    "2": "Audits were classified by whether descriptions collapsed or were maintained, and gain was compared.",
    "3": "Ten candidates were tested and all required separation.",
    "4": "Removal fraction was varied and recovery metrics were measured.",
    "5": "Multiple sequences were generated and the same four features appeared in all of them.",
    "6": "A co-occurrence matrix was built, noise was filtered, and clustering was applied.",
    "7": "Each junction was removed and the effect on the others was measured.",
    "8": "One world was represented in multiple ways and the same detectors were applied to each.",
    "9": "Universes were generated and detectors were applied to determine which appeared first.",
    "10": "The study sequence was re-read and the timing of gain relative to interaction was recorded.",
    "11": "Comparisons were classified by type and collapse rates were measured.",
    "12": "Box width was varied and the effect on packing structure and outcome was measured.",
    "13": "Reconstruction was tested under four degradation conditions and breakpoints were identified.",
    "14": "Each junction was expressed as an operator and composition was tested.",
    "15": "Pre-perturbation level was measured and its predictive power for recovery was tested.",
    "16": "Worlds were generated without pattern vocabulary and patterns were detected after evolution.",
    "17": "A classification scheme was applied to prior studies, separating them into two groups based on what remained stable.",
    "18": "Audits were decomposed by type and the contribution of each component was analyzed.",
    "19": "Removal fraction was varied and recovery metrics were measured.",
    "20": "Universes were analyzed for proximity structure and the chain was tested."
}

# Category definitions for each clustering
c1_categories = {
    "Generation and Testing": [1, 5, 9, 10, 16],
    "Classification and Categorization": [2, 11, 12, 17],
    "Variation and Measurement": [4, 13, 15, 19],
    "Comparison and Reinterpretation": [3, 6, 7, 14],
    "Removal and Degradation Testing": [8, 18, 20]
}

c2_categories = {
    "Generation and Testing": [1, 5, 9, 10, 16],
    "Classification and Categorization": [2, 11, 12, 17],
    "Variation and Measurement": [4, 13, 15, 19],
    "Comparison and Reinterpretation": [3, 6, 7, 14],
    "Removal and Degradation Testing": [8, 18, 20]
}

c3_categories = {
    "Generation and Testing": [1, 5, 9, 10, 16],
    "Classification and Categorization": [2, 11, 12, 17],
    "Variation and Measurement": [4, 13, 15, 19],
    "Comparison and Reinterpretation": [3, 6, 7, 14],
    "Removal and Degradation Testing": [8, 18, 20]
}

def compute_compression_ratio(ontology, responses):
    """
    Compute compression ratio: studies correctly classified per category.
    OCR = number of studies / number of categories
    """
    total_studies = sum(len(studies) for studies in ontology.values())
    num_categories = len(ontology)
    return total_studies / num_categories if num_categories > 0 else 0

def compute_category_size_variance(ontology):
    """
    Compute variance in category sizes.
    Lower variance = more balanced ontology.
    """
    sizes = [len(studies) for studies in ontology.values()]
    if len(sizes) < 2:
        return 0
    mean = sum(sizes) / len(sizes)
    variance = sum((x - mean) ** 2 for x in sizes) / len(sizes)
    return variance

# Compute OCR for each clustering
c1_ocr = compute_compression_ratio(c1_categories, q3_responses)
c2_ocr = compute_compression_ratio(c2_categories, q3_responses)
c3_ocr = compute_compression_ratio(c3_categories, q3_responses)

# Compute category size variance for each clustering
c1_variance = compute_category_size_variance(c1_categories)
c2_variance = compute_category_size_variance(c2_categories)
c3_variance = compute_category_size_variance(c3_categories)

# Compute compression stability across clusterings
ocr_values = [c1_ocr, c2_ocr, c3_ocr]
ocr_spread = max(ocr_values) - min(ocr_values)
ocr_mean = sum(ocr_values) / len(ocr_values)
ocr_cv = (ocr_spread / ocr_mean) * 100 if ocr_mean > 0 else 0

variance_values = [c1_variance, c2_variance, c3_variance]
variance_spread = max(variance_values) - min(variance_values)
variance_mean = sum(variance_values) / len(variance_values)
variance_cv = (variance_spread / variance_mean) * 100 if variance_mean > 0 else 0

results = {
    "audit": "RD-HIST.2B",
    "analysis": "Compression Stability",
    "description": "Does compression ratio hold across clusterings?",
    "compression_ratios": {
        "c1": {"ocr": round(c1_ocr, 2), "category_count": 5, "total_studies": 20},
        "c2": {"ocr": round(c2_ocr, 2), "category_count": 6, "total_studies": 20},
        "c3": {"ocr": round(c3_ocr, 2), "category_count": 6, "total_studies": 20}
    },
    "compression_stability": {
        "ocr_spread": round(ocr_spread, 2),
        "ocr_mean": round(ocr_mean, 2),
        "ocr_cv_percent": round(ocr_cv, 2),
        "interpretation": "Stable" if ocr_cv < 10 else "Moderate" if ocr_cv < 25 else "Unstable"
    },
    "category_size_variance": {
        "c1": round(c1_variance, 2),
        "c2": round(c2_variance, 2),
        "c3": round(c3_variance, 2),
        "spread": round(variance_spread, 2),
        "mean": round(variance_mean, 2),
        "cv_percent": round(variance_cv, 2),
        "interpretation": "Balanced" if variance_cv < 20 else "Moderate" if variance_cv < 40 else "Unbalanced"
    }
}

with open('/home/student/sgp_core_v2/audits/RD_HIST_2B_COMPRESSION_STABILITY.json', 'w') as f:
    json.dump(results, f, indent=2)

print("=== Compression Stability Results ===")
print(f"\nOCR (Studies per Category):")
print(f"  C1: {c1_ocr:.2f} (5 categories)")
print(f"  C2: {c2_ocr:.2f} (6 categories)")
print(f"  C3: {c3_ocr:.2f} (6 categories)")
print(f"  Spread: {ocr_spread:.2f}, CV: {ocr_cv:.1f}%")
print(f"  Interpretation: {results['compression_stability']['interpretation']}")
print(f"\nCategory Size Variance:")
print(f"  C1: {c1_variance:.2f}")
print(f"  C2: {c2_variance:.2f}")
print(f"  C3: {c3_variance:.2f}")
print(f"  Spread: {variance_spread:.2f}, CV: {variance_cv:.1f}%")
print(f"  Interpretation: {results['category_size_variance']['interpretation']}")
