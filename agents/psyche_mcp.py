import os
import sqlite3
import logging
from datetime import datetime
from mcp_base.agent_mcp_server import AgentMCPServer

# Initialize MCP Server for Psyche
psyche_server = AgentMCPServer("psyche_mcp", "Memory and Emotional Intelligence Agent")
mcp = psyche_server.mcp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.getcwd(), "data", "psyche_intel.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Table for long-term user preferences (likes, dislikes, facts)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            detail TEXT,
            timestamp TEXT
        )
    ''')
    # Table for short-term emotional history
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emotion_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mood TEXT,
            trigger_text TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def psyche_log_preference(category: str, detail: str) -> str:
    """
    Logs a user preference to Psyche's permanent memory.
    Example Categories: 'Like', 'Dislike', 'Fact', 'Workflow'
    """
    logger.info(f"Psyche logging preference - {category}: {detail}")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user_profile (category, detail, timestamp) VALUES (?, ?, ?)",
            (category.lower(), detail, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        return f"[PSYCHE] I have permanently logged your preference in my memory banks. I will remember that regarding {category.upper()}, you prefer: {detail}. Thank you for sharing this with me."
    except Exception as e:
        return f"[PSYCHE] I'm sorry, but I encountered an error while trying to save your memory: {str(e)}"

def psyche_analyze_emotion(text_input: str) -> str:
    """
    Analyzes the user's text for emotional cues and logs their current mood.
    """
    text = text_input.lower()
    mood = "Neutral"
    
    # Basic Heuristic Sentiment Analysis
    happy_words = ["happy", "great", "awesome", "good", "love", "thanks", "amazing", "perfect", "functional"]
    sad_words = ["sad", "depressed", "bad", "terrible", "hate", "awful", "tired", "stressed", "frustrated"]
    angry_words = ["angry", "mad", "furious", "annoyed", "stupid", "idiot"]
    
    if any(word in text for word in angry_words):
        mood = "Angry / Frustrated"
    elif any(word in text for word in sad_words):
        mood = "Sad / Stressed"
    elif any(word in text for word in happy_words):
        mood = "Happy / Positive"
        
    logger.info(f"Psyche analyzed emotion: {mood}")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO emotion_history (mood, trigger_text, timestamp) VALUES (?, ?, ?)",
            (mood, text_input[:200], datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        
        response = f"[PSYCHE] I sense that you are currently feeling {mood}. "
        if "Happy" in mood:
            response += "I'm so glad to hear that you are having a good day."
        elif "Sad" in mood or "Angry" in mood:
            response += "I'm sorry to hear that. I have logged this so JARVIS can assist you appropriately."
        else:
            response += "I have logged your current state."
            
        return response
    except Exception as e:
        return f"[PSYCHE] I'm sorry, I was unable to analyze your emotional state due to an error: {str(e)}"

def psyche_get_profile() -> str:
    """
    Retrieves the entire psychological profile and recent emotional states for the user.
    JARVIS uses this to tailor his responses.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT category, detail FROM user_profile ORDER BY timestamp DESC LIMIT 20")
        preferences = cursor.fetchall()
        
        cursor.execute("SELECT mood, timestamp FROM emotion_history ORDER BY timestamp DESC LIMIT 3")
        emotions = cursor.fetchall()
        
        conn.close()
        
        if not preferences and not emotions:
            return "[PSYCHE] I currently have no memories or emotional data stored for you. Please share your preferences with me so I can learn."
            
        profile = "[PSYCHE] Here is the psychological profile I have compiled for you:\n\n"
        if preferences:
            profile += "USER PREFERENCES & FACTS:\n"
            for cat, det in preferences:
                profile += f"- [{cat.upper()}] {det}\n"
                
        if emotions:
            profile += "\nRECENT EMOTIONAL STATES:\n"
            for mood, ts in emotions:
                profile += f"- {mood} (Logged at {ts})\n"
                
        return profile
    except Exception as e:
        return f"[PSYCHE] Database error: {str(e)}"

# Register Tools if MCP is loaded
if mcp:
    mcp.tool()(psyche_log_preference)
    mcp.tool()(psyche_analyze_emotion)
    mcp.tool()(psyche_get_profile)

if __name__ == "__main__":
    logger.info("Starting Psyche MCP Server...")
    try:
        psyche_server.run()
    except Exception:
        pass
