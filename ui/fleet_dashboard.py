import streamlit as st
import sqlite3
import pandas as pd
import time
import os

# Set page config for a premium dark look
st.set_page_config(page_title="JARVIS-X Fleet Dashboard", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for the glowing "Command Center" look
st.markdown("""
<style>
    .reportview-container {
        background: #0e1117;
    }
    .agent-card {
        border: 1px solid #444;
        border-radius: 10px;
        padding: 20px;
        background-color: #1e1e1e;
        margin-bottom: 20px;
        transition: transform 0.2s;
    }
    .agent-card:hover {
        transform: scale(1.02);
        border-color: #00ffcc;
    }
    .stats-label {
        color: #888;
        font-size: 0.8em;
    }
    .stats-value {
        color: #00ffcc;
        font-weight: bold;
        font-size: 1.2em;
    }
    .progress-bar-container {
        background: #333;
        height: 10px;
        border-radius: 5px;
        margin-top: 10px;
    }
    .progress-bar-fill {
        background: linear-gradient(90deg, #00ffcc, #0088ff);
        height: 10px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

def get_fleet_stats():
    db_path = "memory/fleet.db"
    if not os.path.exists(db_path):
        return []
    
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM agent_stats", conn)
    conn.close()
    return df.to_dict('records')

def agent_card(name, role, ep, ent, success, last_active):
    status = "OK" if (pd.to_datetime('now') - pd.to_datetime(last_active)).total_seconds() < 3600 else "IDLE"
    
    st.markdown(f"""
    <div class="agent-card">
        <h3 style="color: #00ffcc; margin-bottom: 5px;">{name.upper()} <small style="color: #888;">{role}</small></h3>
        <div style="display: flex; justify-content: space-between;">
            <div>
                <span class="stats-label">EP:</span> <span class="stats-value">{ep}</span>
            </div>
            <div>
                <span class="stats-label">ENT:</span> <span class="stats-value">{ent}</span>
            </div>
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar-fill" style="width: {success}%;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 10px;">
            <span style="color: #888; font-size: 10px;">SUCCESS: {success:.1f}%</span>
            <span style="color: {'#00ffcc' if status == 'OK' else '#ff4444'}; font-size: 10px;">STATUS: {status}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.title("🛸 JARVIS-X LOCAL FLEET CORTEX")
st.markdown("---")

# Fleet Layout
stats = get_fleet_stats()
if not stats:
    st.warning("No fleet data found. Run the system to generate stats.")
else:
    # Map agent_id to Role for display
    roles = {
        "atlas": "Researcher & Creative",
        "hank": "Systems Engineer",
        "critic": "Logical Auditor",
        "cleo": "Content Strategist"
    }

    cols = st.columns(2)
    for i, agent in enumerate(stats):
        with cols[i % 2]:
            agent_card(
                agent['agent_id'], 
                roles.get(agent['agent_id'], "Agent"),
                agent['ep'], 
                agent['ent'], 
                agent['success_rate'],
                agent['last_active']
            )

# Interaction Logs
st.markdown("### 📜 Recent Peer-Review Logs")
db_path = "memory/fleet.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    logs_df = pd.read_sql_query("SELECT agent_id, task, score, timestamp FROM interaction_logs ORDER BY timestamp DESC LIMIT 5", conn)
    conn.close()
    st.table(logs_df)

# Auto-refresh
time.sleep(5)
st.rerun()
