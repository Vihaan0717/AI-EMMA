import asyncio
import sys
import os

# Configure stdout/stderr to use UTF-8
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add root and backend to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))

# Load dotenv to get IG credentials
from dotenv import load_dotenv
load_dotenv()

from backend.services.instagram_monitor import InstagramMonitor

async def main():
    print("Testing Instagram Monitor Authentication via Session ID...")
    monitor = InstagramMonitor()
    
    session_id = "23108518666%3Aa1OwlHqpHFR4rO%3A13%3AAYhox_Fm9olPttHQHfbc8aUASBPrwgBi-b7oX6X_Zw"
    
    try:
        from instagrapi import Client
        client = Client()
        
        print("Logging in via Session ID...")
        # Run login_by_sessionid in an executor
        await asyncio.to_thread(client.login_by_sessionid, session_id)
        
        print("Login SUCCESSFUL!")
        
        # Dump settings to session file so the main monitor service can reuse it automatically!
        os.makedirs(os.path.dirname(monitor.session_file), exist_ok=True)
        client.dump_settings(monitor.session_file)
        print(f"Session successfully saved to {monitor.session_file}")
        
        # Retrieve user info to verify it works
        user_info = client.user_info(client.user_id)
        print(f"Account Username: {user_info.username}")
        print(f"Account Full Name: {user_info.full_name}")
        
    except Exception as e:
        print(f"Instagram Session ID Login Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
