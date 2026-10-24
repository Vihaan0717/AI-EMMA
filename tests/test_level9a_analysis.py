import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import hashlib
import json
import sqlite3
from scripts.analyze_repository import analyze_repository
from core.code_analyzer import RepositoryAnalyzer

def get_filesystem_manifest(root_dir="."):
    """Computes a deterministic manifest of all tracked files in the repo."""
    manifest = {}
    
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", "logs", "venv", ".venv", ".pytest_cache", ".system_generated"}]
        for f in files:
            filepath = os.path.join(root, f)
            try:
                stat = os.stat(filepath)
                hasher = hashlib.sha256()
                with open(filepath, "rb") as file_obj:
                    for chunk in iter(lambda: file_obj.read(4096), b""):
                        hasher.update(chunk)
                manifest[os.path.relpath(filepath, root_dir)] = {
                    "sha256": hasher.hexdigest(),
                    "size": stat.st_size
                }
            except Exception:
                pass
                
    return manifest

def test_repository_immutability():
    """
    Level 9A Core Constraint:
    JARVIS can analyze the repo without modifying it.
    """
    # 1. Snapshot repo
    initial_manifest = get_filesystem_manifest()
    
    # 2. Run analysis 2 times to simulate usage
    for _ in range(2):
        analyze_repository()
        
    # 3. Verify manifest was generated
    assert os.path.exists("logs/analysis_manifest.json")
    with open("logs/analysis_manifest.json", "r") as f:
        manifest = json.load(f)
        assert manifest["files_analyzed"] > 0
        assert manifest["files_cached"] >= 0
        
    # 4. Check DB
    assert os.path.exists("logs/code_analysis.db")
    conn = sqlite3.connect("logs/code_analysis.db")
    c = conn.cursor()
    c.execute("SELECT count(*) FROM files")
    assert c.fetchone()[0] > 0
    conn.close()
    
    # 5. Verify immutability
    final_manifest = get_filesystem_manifest()
    
    # Check for added/deleted files
    assert set(initial_manifest.keys()) == set(final_manifest.keys()), "Files were added or deleted!"
    
    # Check for modifications
    for filepath, init_data in initial_manifest.items():
        assert init_data["sha256"] == final_manifest[filepath]["sha256"], f"File {filepath} was modified!"
        assert init_data["size"] == final_manifest[filepath]["size"], f"File {filepath} size changed!"

def test_code_analyzer_api():
    """Test the read-only LLM-facing API wrapper."""
    analyzer = RepositoryAnalyzer()
    
    # Test reading
    files = analyzer.list_files()
    assert len(files) > 0
    assert any("core/goal_manager.py" in f for f in files)
    
    # Test AST
    ast_meta = analyzer.parse_ast(files[0])
    assert "classes" in ast_meta
    assert "functions" in ast_meta
    
    # Test blast radius
    # We must ensure the DB is populated first
    analyze_repository()
    
    # Pick a file that should be in the DB
    target_file = next(f for f in files if "goal_manager.py" in f)
    
    blast = analyzer.get_blast_radius(target_file)
    assert blast["target"] == target_file
    assert "risk" in blast
    assert "plane" in blast
    assert "CONTROL PLANE" in blast["plane"]
    assert "CRITICAL" in blast["risk"]
    
    # Dependents should be captured
    assert "direct_dependents" in blast
    assert "indirect_dependents" in blast
    assert "test_coverage" in blast
    
    # Verify no write methods exist
    assert not hasattr(analyzer, "write_file")
    assert not hasattr(analyzer, "delete_file")
    assert not hasattr(analyzer, "git_commit")
