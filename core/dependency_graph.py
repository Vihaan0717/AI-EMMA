import sqlite3
import os
import json
from typing import Dict, Any, List

DB_PATH = "logs/code_analysis.db"

def init_db():
    if not os.path.exists("logs"):
        os.makedirs("logs")
        
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS files (
            path TEXT PRIMARY KEY,
            sha256 TEXT,
            language TEXT,
            size INTEGER,
            modified_time REAL,
            analysis_version INTEGER,
            symbols INTEGER,
            docstring TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS imports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT,
            module TEXT,
            name TEXT,
            lineno INTEGER,
            FOREIGN KEY (file_path) REFERENCES files (path)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS symbols (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT,
            type TEXT, -- "class" or "function" or "method"
            name TEXT,
            lineno INTEGER,
            parent_class TEXT,
            docstring TEXT,
            FOREIGN KEY (file_path) REFERENCES files (path)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT,
            name TEXT,
            lineno INTEGER,
            FOREIGN KEY (file_path) REFERENCES files (path)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_file_metadata(filepath: str) -> Dict[str, Any]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM files WHERE path = ?", (filepath,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def save_ast_metadata(metadata: Dict[str, Any]):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    filepath = metadata["path"]
    
    # Delete old data for this file
    c.execute("DELETE FROM imports WHERE file_path = ?", (filepath,))
    c.execute("DELETE FROM symbols WHERE file_path = ?", (filepath,))
    c.execute("DELETE FROM calls WHERE file_path = ?", (filepath,))
    c.execute("DELETE FROM files WHERE path = ?", (filepath,))
    
    # Insert new data
    c.execute('''
        INSERT INTO files (path, sha256, language, size, modified_time, analysis_version, symbols, docstring)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        filepath, metadata["sha256"], metadata["language"], metadata["size"],
        metadata["modified_time"], metadata["analysis_version"], metadata["symbols"], metadata["docstring"]
    ))
    
    for imp in metadata["imports"]:
        c.execute('''
            INSERT INTO imports (file_path, module, name, lineno)
            VALUES (?, ?, ?, ?)
        ''', (filepath, imp["module"], imp["name"], imp["lineno"]))
        
    for cls in metadata["classes"]:
        c.execute('''
            INSERT INTO symbols (file_path, type, name, lineno, parent_class, docstring)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (filepath, "class", cls["name"], cls["lineno"], None, cls["docstring"]))
        
        for method in cls["methods"]:
            c.execute('''
                INSERT INTO symbols (file_path, type, name, lineno, parent_class, docstring)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (filepath, "method", method["name"], method["lineno"], cls["name"], method["docstring"]))
            
    for func in metadata["functions"]:
        c.execute('''
            INSERT INTO symbols (file_path, type, name, lineno, parent_class, docstring)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (filepath, "function", func["name"], func["lineno"], None, func["docstring"]))
        
    for call in metadata["calls"]:
        c.execute('''
            INSERT INTO calls (file_path, name, lineno)
            VALUES (?, ?, ?)
        ''', (filepath, call["name"], call["lineno"]))
        
    conn.commit()
    conn.close()

def build_file_dependency_graph() -> Dict[str, List[str]]:
    """Builds Graph A: File dependencies based on imports."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("SELECT path FROM files")
    files = [row["path"] for row in c.fetchall()]
    
    graph = {f: [] for f in files}
    
    for f in files:
        c.execute("SELECT module, name FROM imports WHERE file_path = ?", (f,))
        imports = c.fetchall()
        
        # Heuristic to map python import to internal file
        for imp in imports:
            module_name = imp["module"]
            if module_name:
                # e.g. "core.goal_manager" -> "core/goal_manager.py"
                possible_path = module_name.replace(".", "/") + ".py"
                # If they imported a name directly from a module
                # like "from core.models import Goal", the module is core.models
                if possible_path in graph and possible_path not in graph[f]:
                    graph[f].append(possible_path)
            
            # e.g. "import core"
            imp_name_path = imp["name"].replace(".", "/") + ".py"
            if imp_name_path in graph and imp_name_path not in graph[f]:
                graph[f].append(imp_name_path)
                
    conn.close()
    return graph

def get_symbol_call_graph(target_file: str) -> Dict[str, List[str]]:
    """Builds Graph B: Symbol dependencies (what calls what)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("SELECT name, lineno FROM calls WHERE file_path = ?", (target_file,))
    calls = [dict(row) for row in c.fetchall()]
    conn.close()
    return {"calls": calls}
