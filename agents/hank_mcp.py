import os
import sqlite3
import subprocess
import json
import logging
from datetime import datetime
from mcp_base.agent_mcp_server import AgentMCPServer

# Initialize MCP Server for Hank
hank_server = AgentMCPServer("hank_mcp", "Cybersecurity and System Diagnostics Agent")
mcp = hank_server.mcp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.getcwd(), "data", "hank_intel.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS security_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time_created TEXT,
            log_name TEXT,
            level TEXT,
            source TEXT,
            message TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Initialize DB on boot
init_db()

def scan_security_logs(hours_back: int = 24) -> str:
    """
    Scans the Windows Event Viewer (System and Application logs) for Errors and Warnings.
    Stores the data in Hank's local database and returns a summary.
    """
    logger.info(f"Hank is scanning event logs for the past {hours_back} hours...")
    
    # PowerShell command to fetch Errors (Level=2) and Warnings (Level=3) from System and Application logs
    # We output to JSON for easy parsing in Python
    ps_script = f"""
    $startTime = (Get-Date).AddHours(-{hours_back})
    Get-WinEvent -FilterHashtable @{{LogName='System','Application'; Level=2,3; StartTime=$startTime}} -ErrorAction SilentlyContinue | 
    Select-Object TimeCreated, LogName, LevelDisplayName, ProviderName, Message | 
    ConvertTo-Json -Compress
    """
    
    try:
        result = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True)
        if not result.stdout.strip():
            return f"Hank found 0 critical errors or warnings in the past {hours_back} hours. The system is secure."
            
        events = json.loads(result.stdout)
        
        # If powershell returned a single string error wrapped in json
        if isinstance(events, str):
            return f"Hank found 0 valid anomalies. Log output: {events[:100]}"
            
        # If there's only one event, powershell might not return a list
        if isinstance(events, dict):
            events = [events]
            
        error_count = 0
        warning_count = 0
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        for event in events:
            # Add strict type checking
            if not isinstance(event, dict):
                continue
                
            time_c = event.get('TimeCreated', {}).get('value', 'Unknown') if isinstance(event.get('TimeCreated'), dict) else event.get('TimeCreated', 'Unknown')
            log_name = event.get('LogName', 'Unknown')
            level = event.get('LevelDisplayName', 'Unknown')
            source = event.get('ProviderName', 'Unknown')
            msg = event.get('Message', 'No message')
            
            if level == "Error":
                error_count += 1
            elif level == "Warning":
                warning_count += 1
                
            cursor.execute('''
                INSERT INTO security_events (time_created, log_name, level, source, message)
                VALUES (?, ?, ?, ?, ?)
            ''', (str(time_c), log_name, level, source, str(msg)[:500])) # Truncate message to save space
            
        conn.commit()
        conn.close()
        
        summary = (
            f"[HANK] Sir, security sweep complete. "
            f"I scanned the last {hours_back} hours of System and Application logs. "
            f"Detected {error_count} Errors and {warning_count} Warnings. "
            f"All {len(events)} anomalies have been permanently stored in my local intelligence database for future correlation."
        )
        logger.info(summary)
        return summary

    except json.JSONDecodeError:
        return "[HANK] Sir, the scan was successful, but the data stream was too large to parse in one pass. Requesting a smaller timeframe."
    except Exception as e:
        return f"[HANK] Sir, I encountered a critical error while scanning the firewall: {str(e)}"

def get_hank_intel_summary() -> str:
    """
    Reads Hank's database and provides a high-level summary of all historical threats found.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM security_events")
        total_events = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM security_events WHERE level='Error'")
        total_errors = cursor.fetchone()[0]
        conn.close()
        
        if total_events == 0:
            return "[HANK] Sir, my intelligence database is currently empty. No anomalies on record."
            
        return f"[HANK] Sir, my database currently holds {total_events} total recorded anomalies, including {total_errors} critical errors. Awaiting further orders."
    except Exception as e:
        return f"[HANK] Database error: {str(e)}"


# Register Tools if MCP is loaded
if mcp:
    mcp.tool()(scan_security_logs)
    mcp.tool()(get_hank_intel_summary)

if __name__ == "__main__":
    logger.info("Starting Hank Cybersecurity MCP Server...")
    # FastMCP run
    try:
        hank_server.run()
    except Exception:
        pass
