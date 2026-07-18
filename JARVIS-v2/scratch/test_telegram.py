
import asyncio
import aiohttp
import json

async def test_telegram():
    token = "8662332284:AAFjrx-KSS4aAgrLemDO1kFoMnSw8EC5MAo"
    chat_id = "5500095565"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": "🚀 ARION Integration Test: If you see this, my credentials are correct ra!",
        "parse_mode": "Markdown"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            data = await resp.json()
            if data.get("ok"):
                print("✅ Telegram credentials verified! Message sent.")
            else:
                print(f"❌ Telegram Error: {data}")

if __name__ == "__main__":
    asyncio.run(test_telegram())
