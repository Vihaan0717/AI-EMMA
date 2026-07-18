import logging
import sqlite3
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger("Nexus.DailyNoteAgent")

class DailyNoteAgent:
    """
    Manages daily goals, reminders, and success/failure tracking.
    """
    def __init__(self, db_path: str = "memory/daily_notes.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # Goals and their status
        c.execute('''CREATE TABLE IF NOT EXISTS goals
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      goal TEXT,
                      category TEXT, -- 'education', 'health', 'work', etc.
                      status TEXT DEFAULT 'pending', -- 'pending', 'success', 'failure'
                      date DATE,
                      timestamp DATETIME)''')
        # Reminders / Test dates
        c.execute('''CREATE TABLE IF NOT EXISTS reminders
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      event TEXT,
                      event_date DATETIME,
                      type TEXT, -- 'test', 'meeting', 'reminder'
                      notified BOOLEAN DEFAULT 0)''')
        conn.commit()
        conn.close()

    def add_goal(self, goal: str, category: str = "general"):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO goals (goal, category, date, timestamp) VALUES (?, ?, date('now'), ?)",
                  (goal, category, datetime.now()))
        conn.commit()
        conn.close()
        logger.info(f"Goal added: {goal} ({category})")

    def update_goal_status(self, goal_id: int, status: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("UPDATE goals SET status = ? WHERE id = ?", (status, goal_id))
        conn.commit()
        conn.close()

    def add_reminder(self, event: str, event_date: str, event_type: str = "reminder"):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO reminders (event, event_date, type) VALUES (?, ?, ?)",
                  (event, event_date, event_type))
        conn.commit()
        conn.close()
        logger.info(f"Reminder added: {event} on {event_date}")

    def get_today_summary(self) -> Dict[str, Any]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("SELECT id, goal, status FROM goals WHERE date = date('now')")
        goals = [{"id": r[0], "goal": r[1], "status": r[2]} for r in c.fetchall()]
        
        c.execute("SELECT event, event_date FROM reminders WHERE date(event_date) = date('now')")
        reminders = [{"event": r[0], "time": r[1]} for r in c.fetchall()]
        
        # Calculate success rate
        total = len(goals)
        successes = sum(1 for g in goals if g["status"] == "success")
        rate = (successes / total * 100) if total > 0 else 0
        
        conn.close()
        return {
            "goals": goals,
            "reminders": reminders,
            "success_rate": rate,
            "total_goals": total
        }

    def get_upcoming_tests(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT event, event_date FROM reminders WHERE type='test' AND event_date >= datetime('now') ORDER BY event_date ASC")
        tests = [{"event": r[0], "date": r[1]} for r in c.fetchall()]
        conn.close()
        return tests
