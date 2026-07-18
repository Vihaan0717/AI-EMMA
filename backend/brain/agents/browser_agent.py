from playwright.sync_api import sync_playwright
import time

class BrowserAgent:
    """
    A wrapper around Playwright to control Chrome/Chromium.
    """

    def __init__(self, headless: bool = False):
        self.headless = headless
        self._playwright = None
        self._browser = None
        self._context = None
        self.page = None

    def start(self):
        """Start the Playwright browser session."""
        self._playwright = sync_playwright().start()
        # Launch Chromium (acts like Chrome)
        self._browser = self._playwright.chromium.launch(headless=self.headless)
        self._context = self._browser.new_context()
        self.page = self._context.new_page()

    def stop(self):
        """Stop the Playwright browser session."""
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()

    def go_to(self, url: str):
        """Navigate to a specific URL."""
        if not self.page:
            self.start()
        self.page.goto(url)

    def click(self, selector: str):
        """Click on an element by its CSS selector."""
        self.page.click(selector)

    def type_text(self, selector: str, text: str):
        """Type text into an input field."""
        self.page.fill(selector, text)

    def get_page_content(self) -> str:
        """Get the textual content of the current page (simplified)."""
        return self.page.locator("body").inner_text()

    def wait(self, seconds: int = 2):
        """Wait for a short period."""
        time.sleep(seconds)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
