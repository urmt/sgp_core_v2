"""
RD-10B.J5: Dependency Topology Audit

QUESTION:
> What is the structure of the dependency among the four junctions?

DESIGN:
Treat the four junctions as nodes.
Measure:
- dependency edges
- symmetry
- cycles
- reducibility
- strongly connected components

Possible outcomes:
A. Linear chain: A → B → C → D
B. Tree: one junction is more central
C. Cycle: none are primitive, the cycle is primitive
D. Complete graph: decomposition may be artificial

Standing Rule 15: The true junction may be the structure itself.
"""

import json

# ============================================================
# DEPENDENCY MATRIX
# ============================================================

def build_dependency_matrix():
    """
    Build a dependency matrix for the four junctions.
    
    matrix[i][j] = True if junction i depends on junction j.
    """
    junctions = ['distinction', 'constraint', 'preservation', 'recursion']
    
    # Initialize matrix
    matrix = {j1: {j2: False for j2 in junctions} for j1 in junctions}
    
    # From J4 analysis:
    # Constraint depends on distinction
    matrix['constraint']['distinction'] = True
    
    # Preservation depends on distinction
    matrix['preservation']['distinction'] = True
    
    # Preservation depends on constraint (partially)
    matrix['preservation']['constraint'] = True
    
    # Recursion depends on distinction
    matrix['recursion']['distinction'] = True
    
    # Recursion depends on constraint
    matrix['recursion']['constraint'] = True
    
    # Recursion depends on preservation
    matrix['recursion']['preservation'] = True
    
    return junctions, matrix

def analyze_topology(junctions, matrix):
    print("="*70)
    print("DEPENDENCY TOPOLOGY AUDIT")
    print("="*70)
    
    # Show dependency matrix
    print("\n--- DEPENDENCY MATRIX ---")
    print()
    print("  matrix[i][j] = True if i depends on j")
    print()
    
    # Header
    header = "  " + " ".join(f"{j[:8]:>9}" for j in junctions)
    print(header)
    
    for j1 in junctions:
        row = f"  {j1[:8]:>9}"
        for j2 in junctions:
            if matrix[j1][j2]:
                row += "      YES"
            else:
                row += "       --"
        print(row)
    
    # Count dependencies
    print("\n--- DEPENDENCY COUNTS ---")
    print()
    for j1 in junctions:
        depends_on = [j2 for j2 in junctions if matrix[j1][j2]]
        depended_by = [j2 for j2 in junctions if matrix[j2][j1]]
        print(f"  {j1}:")
        print(f"    depends on: {depends_on if depends_on else 'nothing'}")
        print(f"    depended by: {depended_by if depended_by else 'nothing'}")
    
    # Check for cycles
    print("\n--- CYCLE DETECTION ---")
    print()
    
    has_cycle = False
    for j1 in junctions:
        for j2 in junctions:
            if matrix[j1][j2] and matrix[j2][j1]:
                print(f"  CYCLE: {j1} ↔ {j2}")
                has_cycle = True
    
    if not has_cycle:
        print("  No cycles detected.")
    
    # Check for symmetry
    print("\n--- SYMMETRY ANALYSIS ---")
    print()
    
    symmetric_pairs = []
    asymmetric_pairs = []
    
    for i, j1 in enumerate(junctions):
        for j2 in junctions[i+1:]:
            if matrix[j1][j2] and matrix[j2][j1]:
                symmetric_pairs.append((j1, j2))
            elif matrix[j1][j2] or matrix[j2][j1]:
                asymmetric_pairs.append((j1, j2))
    
    print(f"  Symmetric pairs: {symmetric_pairs if symmetric_pairs else 'none'}")
    print(f"  Asymmetric pairs: {asymmetric_pairs if asymmetric_pairs else 'none'}")
    
    # Find strongly connected components
    print("\n--- STRONGLY CONNECTED COMPONENTS ---")
    print()
    
    # Simple SCC detection (for 4 nodes, we can do this manually)
    sccs = []
    visited = set()
    
    for j in junctions:
        if j not in visited:
            # DFS to find reachable nodes
            reachable = set()
            stack = [j]
            while stack:
                node = stack.pop()
                if node not in reachable:
                    reachable.add(node)
                    for j2 in junctions:
                        if matrix[node][j2] and j2 not in reachable:
                            stack.append(j2)
            
            # Check if any reachable node can reach back
            for j2 in reachable:
                if matrix[j2][j]:
                    sccs.append((j, j2))
                    visited.add(j)
                    visited.add(j2)
    
    if sccs:
        print(f"  Strongly connected pairs: {sccs}")
    else:
        print("  No strongly connected components (no cycles).")
    
    # Find roots (no incoming edges)
    print("\n--- ROOT ANALYSIS ---")
    print()
    
    roots = []
    for j1 in junctions:
        has_incoming = any(matrix[j1][j2] for j2 in junctions)
        if not has_incoming:
            roots.append(j1)
    
    print(f"  Roots (no dependencies): {roots if roots else 'none'}")
    
    # Find leaves (no outgoing edges)
    print("\n--- LEAF ANALYSIS ---")
    print()
    
    leaves = []
    for j1 in junctions:
        has_outgoing = any(matrix[j2][j1] for j2 in junctions)
        if not has_outgoing:
            leaves.append(j1)
    
    print(f"  Leaves (depended on by nothing): {leaves if leaves else 'none'}")
    
    # Topological sort (if acyclic)
    print("\n--- TOPOLOGICAL ORDER ---")
    print()
    
    if has_cycle:
        print("  Cannot determine topological order (cycle exists).")
    else:
        # Simple topological sort
        # in_degree[j] = number of nodes that depend on j (incoming edges)
        in_degree = {j: 0 for j in junctions}
        for j1 in junctions:
            for j2 in junctions:
                if matrix[j1][j2]:  # j1 depends on j2
                    in_degree[j2] += 1  # j2 has an incoming edge from j1
        
        print(f"  In-degrees: {in_degree}")
        
        order = []
        remaining = list(junctions)
        while remaining:
            # Find all nodes with in-degree 0
            candidates = [j for j in remaining if in_degree[j] == 0]
            if not candidates:
                print("  ERROR: No node with in-degree 0. Cycle may exist.")
                break
            # Process all candidates at this level
            for node in candidates:
                order.append(node)
                remaining.remove(node)
                # Update in-degrees for remaining nodes
                for j2 in remaining:
                    if matrix[j2][node]:  # j2 depends on node
                        in_degree[j2] -= 1
        
        if len(order) == len(junctions):
            print(f"  Topological order: {' → '.join(order)}")
        else:
            print(f"  Partial order: {' → '.join(order)}")
            print(f"  Remaining: {remaining}")
    
    # Verdict
    print("\n--- VERDICT ---")
    print()
    
    if has_cycle:
        print("Outcome C: Cycle detected.")
        print("None of the junctions are primitive.")
        print("The cycle itself is the primitive structure.")
        verdict = 'cycle'
    elif len(roots) == 1 and len(leaves) == 1:
        print("Outcome A: Linear chain structure.")
        print(f"  Root: {roots[0]}")
        print(f"  Leaf: {leaves[0]}")
        print("The compression hypothesis gains support.")
        verdict = 'chain'
    elif len(roots) > 1:
        print("Outcome B: Multiple roots.")
        print("The structure is not a simple chain.")
        verdict = 'multiple_roots'
    else:
        print("Outcome D: Complex structure.")
        verdict = 'complex'
    
    return {
        'junctions': junctions,
        'has_cycle': has_cycle,
        'roots': roots,
        'leaves': leaves,
        'symmetric_pairs': symmetric_pairs,
        'verdict': verdict,
    }

if __name__ == '__main__':
    junctions, matrix = build_dependency_matrix()
    result = analyze_topology(junctions, matrix)
    
    with open('/home/student/sgp_core_v2/audits/rd10bj5_results.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("\nSaved to audits/rd10bj5_results.json")
