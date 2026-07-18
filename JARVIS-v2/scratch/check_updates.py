
import asyncio
import aiohttp

async def check_updates():
    token = "8662332284:AAFjrx-KSS4aAgrLemDO1kFoMnSw8EC5MAo"
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            print("Updates from Telegram:")
            print(data)

if __name__ == "__main__":
    asyncio.run(check_updates())
