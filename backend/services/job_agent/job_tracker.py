"""
Job Tracker - Persistent SQLite store for all applications.
Tracks: title, company, site, URL, date, status, notes.
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "job_applications.db")

STATUSES = ["applied", "interview_invite", "assessment", "offer", "rejected", "pending", "withdrawn"]

def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create the jobs table if it doesn't exist."""
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS job_applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                site TEXT NOT NULL,
                job_url TEXT,
                date_applied TEXT NOT NULL,
                status TEXT DEFAULT 'applied',
                last_updated TEXT,
                notes TEXT
            )
        """)
        conn.commit()

def log_application(title: str, company: str, site: str, job_url: str = "", notes: str = "") -> int:
    """Log a new job application. Returns the new row id."""
    init_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with _get_conn() as conn:
        cursor = conn.execute("""
            INSERT INTO job_applications (title, company, site, job_url, date_applied, status, last_updated, notes)
            VALUES (?, ?, ?, ?, ?, 'applied', ?, ?)
        """, (title, company, site, job_url, now, now, notes))
        conn.commit()
        return cursor.lastrowid

def update_status(job_id: int, status: str, notes: str = ""):
    """Update the status of an existing application."""
    init_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with _get_conn() as conn:
        conn.execute("""
            UPDATE job_applications
            SET status = ?, last_updated = ?, notes = COALESCE(NULLIF(?, ''), notes)
            WHERE id = ?
        """, (status, now, notes, job_id))
        conn.commit()

def get_all_applications() -> list:
    """Return all tracked applications as a list of dicts."""
    init_db()
    with _get_conn() as conn:
        rows = conn.execute("SELECT * FROM job_applications ORDER BY date_applied DESC").fetchall()
        return [dict(row) for row in rows]

def get_by_status(status: str) -> list:
    """Return applications filtered by status."""
    init_db()
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM job_applications WHERE status = ? ORDER BY date_applied DESC", (status,)
        ).fetchall()
        return [dict(row) for row in rows]

def format_applications_table() -> str:
    """Return all applications as a formatted text table for JARVIS to read."""
    apps = get_all_applications()
    if not apps:
        return "No job applications tracked yet, sir."
    
    lines = [f"{'ID':<5} {'Title':<35} {'Company':<25} {'Site':<15} {'Status':<18} {'Date':<20}"]
    lines.append("-" * 120)
    for a in apps:
        lines.append(
            f"{a['id']:<5} {a['title'][:34]:<35} {a['company'][:24]:<25} {a['site'][:14]:<15} {a['status']:<18} {a['date_applied']:<20}"
        )
    return "\n".join(lines)
