import sqlite3
import os
from datetime import datetime
from core.logger import get_logger

logger = get_logger("LocalFleetDB")

class LocalFleetDB:
    """
    SQLite Database for tracking Local Fleet metrics and experience.
    Tracks 'Growth' of agents via EP (Experience Points) and ENT (Entity Knowledge).
    """
    def __init__(self, db_path="memory/fleet.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Agent Stats: EP, ENT, Success Rate
        c.execute('''CREATE TABLE IF NOT EXISTS agent_stats
                     (agent_id TEXT PRIMARY KEY, 
                      ep INTEGER DEFAULT 0, 
                      ent INTEGER DEFAULT 0, 
                      success_rate REAL DEFAULT 100.0,
                      last_active DATETIME)''')
        
        # Interaction Logs: Tracking performance of each "thought"
        c.execute('''CREATE TABLE IF NOT EXISTS interaction_logs
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      agent_id TEXT, 
                      task TEXT, 
                      tokens INTEGER, 
                      latency_ms REAL, 
                      score INTEGER, 
                      critic_feedback TEXT,
                      timestamp DATETIME)''')
        
        # Correction Notes: The "Lessons Learned" for agents
        c.execute('''CREATE TABLE IF NOT EXISTS correction_notes
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      agent_id TEXT, 
                      topic TEXT, 
                      correction TEXT, 
                      applied BOOLEAN DEFAULT 0,
                      timestamp DATETIME)''')
        
        # Initialize default agents if not present
        agents = [("atlas", 100, 50, 95.0), ("hank", 120, 80, 98.5), ("critic", 500, 200, 99.9)]
        for agent in agents:
            c.execute("INSERT OR IGNORE INTO agent_stats (agent_id, ep, ent, success_rate, last_active) VALUES (?, ?, ?, ?, ?)",
                      (agent[0], agent[1], agent[2], agent[3], datetime.now()))
            
        conn.commit()
        conn.close()
        logger.info(f"LocalFleetDB: Initialized at {self.db_path}")

    def log_interaction(self, agent_id, task, tokens, latency_ms, score, feedback=""):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""INSERT INTO interaction_logs 
                     (agent_id, task, tokens, latency_ms, score, critic_feedback, timestamp) 
                     VALUES (?, ?, ?, ?, ?, ?, ?)""",
                  (agent_id, task, tokens, latency_ms, score, str(feedback), datetime.now()))
        
        # Update agent stats
        ep_gain = 5 if score >= 80 else 1
        ent_gain = 2 if score >= 90 else 0
        
        c.execute("""UPDATE agent_stats 
                     SET ep = ep + ?, ent = ent + ?, 
                         success_rate = (success_rate * 0.9) + (? * 0.1),
                         last_active = ?
                     WHERE agent_id = ?""",
                  (ep_gain, ent_gain, score, datetime.now(), agent_id))
        
        conn.commit()
        conn.close()

    def add_correction_note(self, agent_id, topic, correction):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO correction_notes (agent_id, topic, correction, timestamp) VALUES (?, ?, ?, ?)",
                  (agent_id, topic, correction, datetime.now()))
        conn.commit()
        conn.close()

    def get_agent_stats(self, agent_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT ep, ent, success_rate FROM agent_stats WHERE agent_id = ?", (agent_id,))
        res = c.fetchone()
        conn.close()
        return res if res else (0, 0, 0.0)

    def get_recent_corrections(self, agent_id, limit=5):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT topic, correction FROM correction_notes WHERE agent_id = ? ORDER BY timestamp DESC LIMIT ?", 
                  (agent_id, limit))
        res = c.fetchall()
        conn.close()
        return res

# Global instance
fleet_db = LocalFleetDB()
