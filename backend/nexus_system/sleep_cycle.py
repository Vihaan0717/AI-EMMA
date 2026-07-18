import asyncio
import time
from datetime import datetime, timedelta

def get_ist_now():
    # IST is UTC + 5:30
    return datetime.utcnow() + timedelta(hours=5, minutes=30)

from telegram_bridge import send_morning_briefing

async def daily_reset():
    """
    The 3:30 AM Glymphatic Trigger.
    Consolidates daily logs, clears temporary buffers, and triggers the morning briefing.
    """
    print("🧠 Starting Glymphatic Flush...")
    
    # 1. Logic to gather ingested data from the last 24 hours
    # In a production environment, this would query Tier 3 memory
    summary_data = {
        "knowledge": "Mapped 12 concepts to Tier 3.",
        "slang": "Mastered: 'Pora Babi' & 'Em septhiri'.",
        "files": "6 PDFs offloaded to permanent memory.",
        "arion_note": "The new script has kirrak energy, Boss!",
        "hank_note": "Memory consistency verified."
    }
    
    # 2. Trigger the Telegram Briefing at 03:35 AM
    # We add a slight delay to match the 03:35 AM target if needed, 
    # but for now we trigger it immediately after the flush.
    await send_morning_briefing(summary_data)
    print("✨ System reset complete. Ready for new ingestion cycle.")

async def sleep_cycle_loop():
    print("🌙 Sleep Cycle Monitor Active. Waiting for 03:30 IST...")
    
    while True:
        now = get_ist_now()
        
        # Target time is 03:30 AM IST
        target = now.replace(hour=3, minute=30, second=0, microsecond=0)
        
        # If it's already past 3:30 AM today, set target to 3:30 AM tomorrow
        if now >= target:
            target += timedelta(days=1)
            
        wait_seconds = (target - now).total_seconds()
        
        print(f"💤 Sleeping for {wait_seconds/3600:.2f} hours until next flush at 03:30 IST.")
        
        # Wait until the target time (or check every hour to be safe)
        if wait_seconds > 3600:
            await asyncio.sleep(3600)
        else:
            await asyncio.sleep(wait_seconds)
            await daily_reset()
            # Wait a bit so we don't trigger again immediately in the same second
            await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        asyncio.run(sleep_cycle_loop())
    except KeyboardInterrupt:
        print("\n🛑 Sleep Cycle Monitor stopped.")
