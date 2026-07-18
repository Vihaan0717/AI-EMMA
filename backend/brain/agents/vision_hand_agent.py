import logging
from browser_use.browser.profile import BrowserProfile
from browser_use.browser.session import BrowserSession
from browser_use.agent.service import Agent
from langchain_ollama import ChatOllama


# browser-use Agent internally reads llm.provider to identify the LLM backend.
# ChatOllama is a strict Pydantic model so we cannot set arbitrary attributes.
# Solution: subclass it and declare 'provider' as a proper Pydantic field.
class OllamaWithProvider(ChatOllama):
    provider: str = "ollama"


logger = logging.getLogger("Nexus.VisionHandAgent")


class VisionHandAgent:
    """
    The 'Hands' of JARVIS using Agentic Computer Use.
    Uses browser-use (modern API v0.2.x+) and an LLM via Ollama to navigate
    the web via Accessibility Trees instead of raw coordinates.

    Key API note: BrowserSession uses .start()/.stop(), NOT async-with.
    """

    def __init__(self, model_name="llama3.1", ollama_url="http://localhost:11434"):
        # Use our Pydantic-safe subclass that includes the 'provider' field
        self.llm = OllamaWithProvider(model=model_name, base_url=ollama_url)

        # BrowserProfile replaces the old BrowserConfig.
        # Pointing to Chrome + user's existing profile so no login is needed.
        self.profile = BrowserProfile(
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            profile_directory="Default",  # Change to "Profile 1" etc. if needed
            headless=False,               # Show the browser window
            keep_alive=False,             # Let the session manage its own lifecycle
        )

    async def execute_web_task(self, task_description: str) -> str:
        """
        Executes an autonomous web task using browser-use.
        Opens a live Chrome window using the user's existing profile/login session.
        """
        import re
        # Strip markdown links [text](url) → just url, to prevent IPv6 parse errors
        # caused by the square brackets being mistaken for IPv6 address notation.
        clean_task = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\2', task_description)
        logger.info(f"Executing web task: {clean_task[:120]}...")
        session = BrowserSession(browser_profile=self.profile)
        try:
            # BrowserSession uses .start() / .stop(), NOT async-with
            await session.start()
            agent = Agent(
                task=clean_task,
                llm=self.llm,
                browser_session=session,
            )
            result = await agent.run()
            return f"Task Result:\n{result}"
        except Exception as e:
            logger.error(f"VisionHandAgent error: {e}")
            return f"Action failed: {e}"
        finally:
            try:
                await session.stop()
            except Exception:
                pass
