import os
import sys
from typing import Dict, Any
from core.code_analyzer import RepositoryAnalyzer

def analyze_repository(root_dir: str = ".") -> Dict[str, Any]:
    """
    Analyzes the entire repository and generates AST metadata, dependency graphs,
    and blast radius metrics without modifying any files.
    """
    analyzer = RepositoryAnalyzer(root_dir=root_dir)
    files = analyzer.list_files(".py")
    results = {}
    
    for f in files:
        try:
            results[f] = {
                "symbols": analyzer.get_symbols(f),
                "risk": analyzer.get_risk(f),
                "blast_radius": analyzer.get_blast_radius(f)
            }
        except Exception as e:
            results[f] = {"error": str(e)}
            
    return {
        "total_files": len(files),
        "dependencies": analyzer.get_dependencies(),
        "files": results
    }

if __name__ == "__main__":
    res = analyze_repository()
    print(f"Repository analysis complete. Tracked {res['total_files']} Python modules.")
