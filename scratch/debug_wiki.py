import asyncio
import httpx
import json

async def check_wiki():
    query = "Alan_Turing"
    headers = {'User-Agent': 'JARVIS-Project/1.0 (vanger.vihaan@gmail.com)'}
    async with httpx.AsyncClient(headers=headers) as c:
        r = await c.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
        )
        print(f"Status: {r.status_code}")
        print(f"Body: {r.text[:500]}")

if __name__ == "__main__":
    asyncio.run(check_wiki())
