import sys
from backend.brain.agents.browser_agent import BrowserAgent
from backend.brain.agents.gmail_agent import GmailAgent

def test_browser():
    print("Testing Browser Automation (Playwright)...")
    try:
        with BrowserAgent(headless=True) as browser:
            browser.go_to("https://example.com")
            content = browser.get_page_content()
            print(f"Success! Page Content Snippet: {content[:100].strip()}...")
    except Exception as e:
        print(f"Browser test failed: {e}")

def test_gmail():
    print("\nTesting Gmail Automation (Himalaya)...")
    agent = GmailAgent()
    try:
        # We just try to list the first email to see if Himalaya is configured
        output = agent.list_emails(limit=1)
        if "Error executing" in output or "failed" in output.lower():
            print(f"Gmail test failed or Himalaya not configured yet.\nOutput:\n{output}")
        else:
            print("Success! Himalaya connected and returned inbox data.")
            print(f"Snippet:\n{output[:200]}...")
    except Exception as e:
        print(f"Gmail test failed: {e}")

if __name__ == "__main__":
    test_browser()
    test_gmail()
