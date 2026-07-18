import asyncio
from telegram import Bot

# Your Secured Credentials
TELEGRAM_TOKEN = '8708453921:AAGYu-CU3AdgfTu3x1brLDiI2sifV8wIGF0'
USER_ID = '8708453921' # Your Registered ID

async def send_morning_briefing(briefing_data):
    """
    Broadcasts the A15 Executive Summary to your mobile device.
    """
    bot = Bot(token=TELEGRAM_TOKEN)
    
    header = "🌅 *NEXUS-X Morning Briefing* [03:35 AM]\n"
    status = "Status: 24h Reset Complete. War Room Cleared.\n\n"
    
    # Building the body from your A15 logic
    body = (
        f"🧠 *Intelligence:* {briefing_data.get('knowledge', 'No new logic mapped.')}\n"
        f"🗣️ *Linguistics:* {briefing_data.get('slang', 'No new T7 DNA patterns.')}\n"
        f"📁 *Ingestion:* {briefing_data.get('files', 'Cleanup successful.')}\n\n"
        f"💬 *Agent Opinions:*\n"
        f"Arion: \"{briefing_data.get('arion_note', 'Standing by.')}\"\n"
        f"Hank: \"{briefing_data.get('hank_note', 'Logic stable.')}\""
    )

    full_message = header + status + body
    
    try:
        await bot.send_message(chat_id=USER_ID, text=full_message, parse_mode='Markdown')
        print("✅ Telegram Briefing Sent to Vihaan0717.")
    except Exception as e:
        print(f"❌ Telegram Error: {e}")

if __name__ == "__main__":
    # For testing manually:
    asyncio.run(send_morning_briefing({
        "knowledge": "Java Concurrency", 
        "slang": "Em septhiri",
        "files": "Cleanup successful.",
        "arion_note": "Kirrak energy!",
        "hank_note": "Logic verified."
    }))
