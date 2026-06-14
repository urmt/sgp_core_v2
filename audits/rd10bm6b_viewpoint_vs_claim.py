"""
RD-10B.M6b: Viewpoint vs Claim Comparison

HYPOTHESIS:
Viewpoint comparison (different perspectives on same thing) preserves tension.
Claim comparison (competing answers to same question) causes collapse.

TEST:
Classify each comparison as viewpoint or claim.
Check if this predicts collapse.
"""

import json

def classify_comparisons():
    comparisons = [
        # Viewpoint comparisons (different perspectives)
        ('RD-5', 'metric', 'viewpoint', False),
        ('RD-10B.0', 'representation', 'viewpoint', False),
        ('RD-10B.0A', 'representation', 'viewpoint', False),
        ('RD-10B.X', 'path', 'viewpoint', False),
        ('RD-10B.J2', 'path', 'viewpoint', False),
        ('RD-10B.J3', 'vocabulary', 'viewpoint', False),
        ('RD-10B.J7', 'decomposition', 'viewpoint', False),
        ('RD-10B.J8', 'decomposition', 'viewpoint', False),
        # Claim comparisons (competing answers)
        ('RD-9E', 'method-artifact', 'claim', True),
        ('RD-10B.3', 'detector', 'claim', True),
        ('RD-10B.0B', 'criterion', 'claim', True),
        ('RD-10B.0C', 'criterion', 'claim', True),
        ('RD-10B.0D', 'criterion', 'claim', True),
        ('RD-10B.0F', 'world', 'claim', True),
        ('RD-10B.J4', 'dependency', 'claim', True),
        ('RD-10B.J6', 'decomposition', 'claim', True),
        ('RD-10B.M1', 'methodology', 'claim', True),
        # Ambiguous
        ('RD-10B.0E', 'world', 'viewpoint', False),
        ('RD-10B.M2', 'meta', 'viewpoint', False),
    ]
    return comparisons

def analyze():
    comparisons = classify_comparisons()
    
    viewpoints = [c for c in comparisons if c[2] == 'viewpoint']
    claims = [c for c in comparisons if c[2] == 'claim']
    
    vp_collapsed = sum(1 for c in viewpoints if c[3])
    cl_collapsed = sum(1 for c in claims if c[3])
    
    print("VIEWPOINT COMPARISON:")
    print(f"  Total: {len(viewpoints)}")
    print(f"  Collapsed: {vp_collapsed}")
    print(f"  Collapse rate: {vp_collapsed/len(viewpoints):.2%}")
    
    print()
    print("CLAIM COMPARISON:")
    print(f"  Total: {len(claims)}")
    print(f"  Collapsed: {cl_collapsed}")
    print(f"  Collapse rate: {cl_collapsed/len(claims):.2%}")
    
    print()
    print("VERDICT:")
    if vp_collapsed/len(viewpoints) < cl_collapsed/len(claims):
        print("  Viewpoint comparison preserves tension.")
        print("  Claim comparison causes collapse.")
        print("  The distinction is predictive.")
    else:
        print("  The distinction is not predictive.")
    
    # Decomposition stability
    print()
    print("DECOMPOSITION STABILITY:")
    decomp_viewpoint = [c for c in comparisons if c[1] == 'decomposition' and c[2] == 'viewpoint']
    decomp_claim = [c for c in comparisons if c[1] == 'decomposition' and c[2] == 'claim']
    
    print(f"  Viewpoint decompositions: {len(decomp_viewpoint)}")
    for c in decomp_viewpoint:
        print(f"    {c[0]}: collapsed={c[3]}")
    
    print(f"  Claim decompositions: {len(decomp_claim)}")
    for c in decomp_claim:
        print(f"    {c[0]}: collapsed={c[3]}")

if __name__ == '__main__':
    analyze()
