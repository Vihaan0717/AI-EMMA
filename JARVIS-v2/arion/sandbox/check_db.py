import sqlite3
import os

db_path = "arion/data/memory.db"
if not os.path.exists(db_path):
    print("DB not found at arion/data/memory.db, trying data/memory.db")
    db_path = "data/memory.db"

try:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("PRAGMA table_info(conversations)")
    cols = [col[1] for col in c.fetchall()]
    print(f"Columns in 'conversations': {cols}")
    
    if "tier" in cols:
        print("SUCCESS: 'tier' column exists.")
    else:
        print("FAILURE: 'tier' column missing.")
        
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
