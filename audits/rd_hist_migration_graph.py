"""
RD-HIST.1 Phase 6: Migration Graph

Build graph:
Claimed explanation → Later explanation → Later explanation → Later explanation

Measure:
- recurring transitions
- cycles
- attractors
- dead ends
"""

import json
from pathlib import Path

ROOT = Path("/home/student/sgp_core_v2")

def build_migration_edges():
    """
    Build edges showing how explanations migrated.
    """
    edges = [
        # T-series → Phase-series
        ('T037_primitive_interaction_genesis', 'phase398_interaction_framework', 'interaction persistence'),
        
        # Phase-series → RD-series
        ('phase398_interaction_framework', 'RD-019', 'new research direction'),
        
        # RD-019-022 causal interventions
        ('RD-019', 'RD-020', 'density failed, try structure'),
        ('RD-020', 'RD-021', 'structure failed, try velocity'),
        ('RD-021', 'RD-022', 'velocity failed, measure C robustness'),
        
        # RD-022 → RD-5
        ('RD-022', 'RD-5', 'C robustness → metric comparison'),
        
        # RD-5 → RD-9E
        ('RD-5', 'RD-9E', 'metrics compared → SP tested'),
        
        # RD-9E → RD-10A
        ('RD-9E', 'RD-10A.1', 'SP falsified → constraint framework'),
        
        # RD-10A chain
        ('RD-10A.1', 'RD-10A.8', 'taxonomy → topology'),
        ('RD-10A.8', 'RD-10A.9', 'topology → distinctions'),
        ('RD-10A.9', 'RD-10A.10', 'distinctions → preservation'),
        ('RD-10A.10', 'RD-10A.12', 'preservation → lenses'),
        
        # RD-10A → RD-10B
        ('RD-10A.12', 'RD-10B.0', 'lenses → representation audit'),
        
        # RD-10B.0 series
        ('RD-10B.0', 'RD-10B.0A', 'representation → correspondence'),
        ('RD-10B.0A', 'RD-10B.0B', 'correspondence → identity'),
        ('RD-10B.0B', 'RD-10B.0C', 'identity → purpose'),
        ('RD-10B.0C', 'RD-10B.0D', 'purpose → failure modes'),
        ('RD-10B.0D', 'RD-10B.0E', 'failure modes → domains'),
        ('RD-10B.0E', 'RD-10B.0F', 'domains → world assumptions'),
        
        # RD-10B.0F → Junction search
        ('RD-10B.0F', 'RD-10B.X', 'world assumptions → junction search'),
        
        # Junction chain
        ('RD-10B.X', 'RD-10B.Y', 'recursion → constraint'),
        ('RD-10B.Y', 'RD-10B.Z', 'constraint → preservation'),
        ('RD-10B.Z', 'RD-10B.W', 'preservation → distinction'),
        
        # Junction → Independence testing
        ('RD-10B.W', 'RD-10B.J2', 'distinction → path independence'),
        ('RD-10B.J2', 'RD-10B.J3', 'path → vocabulary'),
        ('RD-10B.J3', 'RD-10B.J4', 'vocabulary → dependency'),
        ('RD-10B.J4', 'RD-10B.J5', 'dependency → topology'),
        ('RD-10B.J5', 'RD-10B.J6', 'topology → compression'),
        ('RD-10B.J6', 'RD-10B.J7', 'compression → isomorphism'),
        ('RD-10B.J7', 'RD-10B.J8', 'isomorphism → translation'),
        
        # Translation → Migration
        ('RD-10B.J8', 'RD-10B.M1', 'translation → migration'),
        
        # Migration chain
        ('RD-10B.M1', 'RD-10B.M2', 'migration → oscillation'),
        ('RD-10B.M2', 'RD-10B.M3', 'oscillation → comparison'),
        ('RD-10B.M3', 'RD-10B.M5', 'comparison → tension'),
        ('RD-10B.M5', 'RD-10B.M6b', 'tension → viewpoint'),
        
        # Viewpoint → Interaction
        ('RD-10B.M6b', 'RD-10B.R1', 'viewpoint → interaction'),
        
        # Interaction chain
        ('RD-10B.R1', 'RD-10B.R3', 'interaction → fertile interaction'),
        ('RD-10B.R3', 'RD-10B.R4', 'fertile → experience'),
        ('RD-10B.R4', 'RD-10B.R0R', 'experience → persistence ladder'),
    ]
    return edges

def analyze_migration():
    print("="*70)
    print("RD-HIST.1 PHASE 6: MIGRATION GRAPH")
    print("="*70)
    
    edges = build_migration_edges()
    
    # Build node list
    nodes = set()
    for src, dst, label in edges:
        nodes.add(src)
        nodes.add(dst)
    
    print(f"\nNodes: {len(nodes)}")
    print(f"Edges: {len(edges)}")
    
    # Find cycles
    print("\n--- CYCLES ---\n")
    
    # Build adjacency list
    adj = {}
    for src, dst, label in edges:
        if src not in adj:
            adj[src] = []
        adj[src].append(dst)
    
    # Simple cycle detection (DFS)
    def find_cycles(node, visited, stack, cycles):
        visited.add(node)
        stack.add(node)
        
        for neighbor in adj.get(node, []):
            if neighbor not in visited:
                find_cycles(neighbor, visited, stack, cycles)
            elif neighbor in stack:
                cycles.append((node, neighbor))
        
        stack.remove(node)
    
    visited = set()
    stack = set()
    cycles = []
    for node in nodes:
        if node not in visited:
            find_cycles(node, visited, stack, cycles)
    
    if cycles:
        print("Cycles found:")
        for src, dst in cycles:
            print(f"  {src} → {dst}")
    else:
        print("No cycles found.")
    
    # Find attractors (nodes with high in-degree)
    print("\n--- ATTRACTORS (high in-degree) ---\n")
    
    in_degree = {}
    for src, dst, label in edges:
        if dst not in in_degree:
            in_degree[dst] = 0
        in_degree[dst] += 1
    
    for node, degree in sorted(in_degree.items(), key=lambda x: -x[1])[:5]:
        print(f"  {node}: {degree} incoming edges")
    
    # Find dead ends (nodes with no outgoing edges)
    print("\n--- DEAD ENDS (no outgoing edges) ---\n")
    
    out_degree = {}
    for src, dst, label in edges:
        if src not in out_degree:
            out_degree[src] = 0
        out_degree[src] += 1
    
    dead_ends = [n for n in nodes if n not in out_degree]
    for node in dead_ends:
        print(f"  {node}")
    
    # Find sources (nodes with no incoming edges)
    print("\n--- SOURCES (no incoming edges) ---\n")
    
    sources = [n for n in nodes if n not in in_degree]
    for node in sources:
        print(f"  {node}")
    
    # Save
    output = {
        'nodes': list(nodes),
        'edges': [{'src': src, 'dst': dst, 'label': label} for src, dst, label in edges],
        'cycles': cycles,
        'attractors': {n: d for n, d in sorted(in_degree.items(), key=lambda x: -x[1])[:5]},
        'dead_ends': dead_ends,
        'sources': sources,
    }
    
    with open(ROOT / 'audits' / 'RD_HIST_MIGRATION_GRAPH.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("\nSaved to audits/RD_HIST_MIGRATION_GRAPH.json")

if __name__ == '__main__':
    analyze_migration()
