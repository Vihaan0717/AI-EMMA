from typing import Dict, Any, List, Set
from core.dependency_graph import build_file_dependency_graph
from core.code_risk import determine_module_risk

def compute_blast_radius(target_file: str) -> Dict[str, Any]:
    """
    Computes the blast radius if target_file is modified.
    It finds direct dependents, indirect dependents, and affected test coverage.
    """
    graph = build_file_dependency_graph()
    
    # Invert the graph: map A -> B means B depends on A
    reverse_graph = {node: [] for node in graph}
    for node, edges in graph.items():
        for edge in edges:
            if edge not in reverse_graph:
                reverse_graph[edge] = []
            reverse_graph[edge].append(node)
            
    direct_dependents = reverse_graph.get(target_file, [])
    
    # Find indirect dependents via BFS
    visited = set(direct_dependents)
    queue = list(direct_dependents)
    indirect_dependents = set()
    
    while queue:
        current = queue.pop(0)
        for neighbor in reverse_graph.get(current, []):
            if neighbor not in visited and neighbor != target_file:
                visited.add(neighbor)
                queue.append(neighbor)
                indirect_dependents.add(neighbor)
                
    # Find test coverage
    tests = [f for f in direct_dependents + list(indirect_dependents) if "test_" in f]
    
    # Calculate risk
    risk_info = determine_module_risk(target_file)
    
    return {
        "target": target_file,
        "risk": risk_info["risk"],
        "plane": risk_info["plane"],
        "direct_dependents": direct_dependents,
        "indirect_dependents": list(indirect_dependents),
        "test_coverage": tests
    }
