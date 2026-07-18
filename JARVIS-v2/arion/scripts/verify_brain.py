
import sys
from pathlib import Path

# Add arion to path
sys.path.append(str(Path.cwd() / "arion"))

try:
    from brain.vault_brain import VaultBrain
    from brain.rag_engine import RAGEngine
    from brain.reinforcement_engine import ReinforcementEngine
    
    print("Core Brain modules imported successfully.")
    
    # Test VaultBrain
    vb = VaultBrain(vault_path="arion/vault")
    vb.update_working_memory("TestUser", "assistant", "Verification test message", "happy", "testing")
    print("VaultBrain: update_working_memory test passed.")
    
    # Test RAGEngine
    rag = RAGEngine(chroma_path="arion/data/chromadb")
    print("RAGEngine: Initialization passed.")
    
    # Test ReinforcementEngine
    re_eng = ReinforcementEngine(profile_path="arion/data/brain/test_behavior.json")
    print("ReinforcementEngine: Initialization passed.")
    
    print("\nALL BRAIN COMPONENTS VERIFIED SUCCESSFULLY.")
except Exception as e:
    print(f"VERIFICATION FAILED: {e}")
    import traceback
    traceback.print_exc()
