import asyncio
from playwright.async_api import async_playwright
import traceback

async def login():
    print("Launching browser...")
    try:
        async with async_playwright() as p:
            ctx = await p.chromium.launch_persistent_context(
                './social_browser_data',
                headless=False,
                args=['--disable-blink-features=AutomationControlled', '--start-maximized']
            )
            page = await ctx.new_page()
            await page.goto('https://www.linkedin.com/login')
            print("Browser opened. Log in now.")
            print("")
            input(">>> Press ENTER here after you have logged into LinkedIn...")
            await ctx.close()
        print("")
        print("SUCCESS! LinkedIn session saved permanently.")
        print("You can close this window now.")
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(login())
