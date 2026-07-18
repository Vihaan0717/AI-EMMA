import shutil
from pathlib import Path
import os

def migrate():
    # Make sure we are in the right directory
    base_dir = Path("c:/Users/anger/Desktop/JARVIS-v2")
    vault = base_dir / "arion" / "vault"
    old_conversations = vault / "Memories" / "conversations"
    archive_dest = vault / "Memory" / "_archive" / "conversations_old"
    
    print(f"[Migration] Checking {old_conversations}...")
    
    if old_conversations.exists():
        archive_dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.move(str(old_conversations), str(archive_dest))
            print(f"[SUCCESS] Archived old conversations -> {archive_dest}")
        except Exception as e:
            print(f"[ERROR] Migration failed: {e}")
    else:
        print("[INFO] No old conversations found to migrate.")
    
    # Remove old empty Memories folder if possible
    old_memories = vault / "Memories"
    if old_memories.exists():
        try:
            # Check if empty (ignoring hidden files)
            if not any(old_memories.iterdir()):
                old_memories.rmdir()
                print("[SUCCESS] Removed empty Memories folder.")
            else:
                print(f"[INFO] Memories folder not empty, keeping it. Contents: {list(old_memories.iterdir())}")
        except Exception as e:
            print(f"[INFO] Could not remove Memories folder: {e}")
    
    print("[INFO] Logic complete. Tiered system target folders established.")

if __name__ == "__main__":
    migrate()
