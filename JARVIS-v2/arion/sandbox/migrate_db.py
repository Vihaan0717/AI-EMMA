import sqlite3
import os

db_path = "arion/data/memory.db"
if not os.path.exists(db_path):
    db_path = "data/memory.db"

print(f"Migrating {db_path}...")

conn = sqlite3.connect(db_path)
c = conn.cursor()

# Get existing columns
c.execute("PRAGMA table_info(conversations)")
cols = [col[1] for col in c.fetchall()]

migrations = [
    ("tier", "INTEGER DEFAULT 1"),
    ("emotion", "TEXT DEFAULT ''"),
    ("promoted", "INTEGER DEFAULT 0")
]

for col_name, col_def in migrations:
    if col_name not in cols:
        print(f"Adding column '{col_name}' to conversations...")
        c.execute(f"ALTER TABLE conversations ADD COLUMN {col_name} {col_def}")

# Check people_metadata too
c.execute("PRAGMA table_info(people_metadata)")
cols = [col[1] for col in c.fetchall()]
people_migrations = [
    ("relationship", "TEXT DEFAULT 'stranger'"),
    ("bio", "TEXT DEFAULT ''"),
    ("style_notes", "TEXT DEFAULT ''"),
    ("media_count", "INTEGER DEFAULT 0"),
    ("intent_avg", "REAL DEFAULT 2.0")
]

for col_name, col_def in people_migrations:
    if col_name not in cols:
        print(f"Adding column '{col_name}' to people_metadata...")
        c.execute(f"ALTER TABLE people_metadata ADD COLUMN {col_name} {col_def}")

conn.commit()
conn.close()
print("Migration complete.")
