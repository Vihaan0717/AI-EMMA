import ast
import hashlib
import os
from typing import Dict, Any, List

def calculate_file_hash(filepath: str) -> str:
    """Calculate the SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

class ASTMetadataVisitor(ast.NodeVisitor):
    def __init__(self):
        self.classes = []
        self.functions = []
        self.imports = []
        self.calls = []
        self.current_class = None
        
    def visit_ClassDef(self, node):
        class_info = {
            "name": node.name,
            "lineno": node.lineno,
            "docstring": ast.get_docstring(node),
            "bases": [b.id for b in node.bases if isinstance(b, ast.Name)],
            "methods": []
        }
        
        previous_class = self.current_class
        self.current_class = class_info
        
        self.generic_visit(node)
        
        self.classes.append(class_info)
        self.current_class = previous_class
        
    def visit_FunctionDef(self, node):
        func_info = {
            "name": node.name,
            "lineno": node.lineno,
            "docstring": ast.get_docstring(node),
            "decorators": [d.id for d in node.decorator_list if isinstance(d, ast.Name)],
        }
        
        if self.current_class is not None:
            self.current_class["methods"].append(func_info)
        else:
            self.functions.append(func_info)
            
        self.generic_visit(node)
        
    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)
        
    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append({"module": alias.name, "name": alias.name, "lineno": node.lineno})
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node):
        module = node.module or ""
        for alias in node.names:
            self.imports.append({"module": module, "name": alias.name, "lineno": node.lineno})
        self.generic_visit(node)
        
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.calls.append({"name": node.func.id, "lineno": node.lineno})
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                self.calls.append({"name": f"{node.func.value.id}.{node.func.attr}", "lineno": node.lineno})
        self.generic_visit(node)

def extract_ast_metadata(filepath: str) -> Dict[str, Any]:
    """
    Reads a Python file, parses its AST, and extracts structured metadata.
    """
    if not filepath.endswith(".py") or not os.path.exists(filepath):
        return {}
        
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()
        
    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:
        return {}
        
    visitor = ASTMetadataVisitor()
    visitor.visit(tree)
    
    # Extract module docstring
    module_docstring = ast.get_docstring(tree)
    
    stat = os.stat(filepath)
    
    return {
        "path": filepath,
        "sha256": calculate_file_hash(filepath),
        "language": "python",
        "size": stat.st_size,
        "modified_time": stat.st_mtime,
        "analysis_version": 1,
        "symbols": len(visitor.classes) + len(visitor.functions),
        "imports": visitor.imports,
        "classes": visitor.classes,
        "functions": visitor.functions,
        "calls": visitor.calls,
        "docstring": module_docstring
    }
