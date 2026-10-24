import os
from typing import Dict, Any, List
from pathlib import Path
from core.ast_extractor import extract_ast_metadata
from core.dependency_graph import get_file_metadata, build_file_dependency_graph, get_symbol_call_graph
from core.blast_radius import compute_blast_radius
from core.code_risk import determine_module_risk

class RepositoryAnalyzer:
    """
    Read-only API for Level 9A Code Analysis.
    Strictly forbids modifications, file writes, deletes, and pip installs.
    """
    
    def __init__(self, root_dir: str = "."):
        # Make root_dir explicit and immutable for the lifetime of this run
        self._root_dir = os.path.abspath(root_dir)
        
    @property
    def root_dir(self):
        return self._root_dir
        
    def _enforce_bounds(self, filepath: str) -> str:
        """Ensures the filepath doesn't escape the repository root."""
        full_path = Path(self._root_dir) / filepath
        resolved_path = full_path.resolve()
        resolved_root = Path(self._root_dir).resolve()
        
        # is_relative_to is Python 3.9+
        if not resolved_path.is_relative_to(resolved_root):
            raise PermissionError(f"Path traversal blocked: {filepath} escapes repository root.")
            
        return str(resolved_path)
        
    def list_files(self, extension: str = ".py") -> List[str]:
        """Returns a list of tracked files matching the extension."""
        result = []
        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", "logs", "venv", ".venv", ".pytest_cache", ".system_generated"}]
            for f in files:
                if f.endswith(extension):
                    path = os.path.relpath(os.path.join(root, f), self.root_dir)
                    # Normalize slashes for consistency
                    result.append(path.replace("\\", "/"))
        return result
        
    def read_file(self, filepath: str) -> str:
        """Reads a file strictly in read-only mode."""
        full_path = self._enforce_bounds(filepath)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found: {filepath}")
            
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
            
    def parse_ast(self, filepath: str) -> Dict[str, Any]:
        """Parses AST metadata for a given file (reads from cache if unchanged)."""
        full_path = self._enforce_bounds(filepath)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found: {filepath}")
            
        return extract_ast_metadata(full_path)
        
    def get_symbols(self, filepath: str) -> Dict[str, Any]:
        """Retrieves symbols (classes, functions) for a file."""
        metadata = self.parse_ast(filepath)
        return {
            "classes": metadata.get("classes", []),
            "functions": metadata.get("functions", [])
        }
        
    def get_dependencies(self) -> Dict[str, List[str]]:
        """Returns the file dependency graph (Graph A)."""
        return build_file_dependency_graph()
        
    def get_call_graph(self, filepath: str) -> Dict[str, List[str]]:
        """Returns the symbol dependency graph (Graph B) for a specific file."""
        return get_symbol_call_graph(filepath)
        
    def get_blast_radius(self, filepath: str) -> Dict[str, Any]:
        """Computes the impact of modifying a specific file."""
        # Normalize slashes for db lookup
        normalized_path = filepath.replace("/", "\\") if os.name == 'nt' else filepath
        # But wait, our DB might store them with forward slashes or backwards slashes depending on how it was inserted.
        # Let's try both to be safe.
        res = compute_blast_radius(filepath)
        if not res["direct_dependents"] and "\\" in filepath:
             res = compute_blast_radius(filepath.replace("\\", "/"))
        return res
        
    def get_risk(self, filepath: str) -> Dict[str, str]:
        """Retrieves the risk level and plane (Control vs Data)."""
        return determine_module_risk(filepath)
