"""
ReAct Graph - Full Autonomous Loop with Escalating Internet Strategies
=====================================================================
On each retry, the agent:
  1. Searches the internet and Reddit for alternative approaches
  2. Escalates its method (basic -> deep scrape -> Reddit research -> visual browsing -> multi-source)
  3. Learns from each failure before trying again
Max retries: 5
"""

import asyncio
import logging
from typing import TypedDict, Optional
import nest_asyncio
nest_asyncio.apply()  # Allows nested async calls inside LangGraph's sync nodes
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama

logger = logging.getLogger("Nexus.ReActGraph")

# ---------------------------------------------------------------------------- #
# State Definition
# ---------------------------------------------------------------------------- #
class AgentState(TypedDict):
    input_query:     str
    plan:            str
    strategy:        str          # current escalation strategy name
    current_strategy_index: int   # Added for dynamic routing
    gathered_data:   str
    evaluation:      str
    retry_count:     int
    failure_log:     str          # accumulates what failed and why
    internet_advice: str          # advice pulled from web/reddit on each retry
    final_output:    str

# ---------------------------------------------------------------------------- #
# Escalation Strategy Table (max 5 retries → 5 strategies)
# ---------------------------------------------------------------------------- #
ESCALATION_STRATEGIES = [
    {
        "name": "Local LLM Knowledge",
        "description": "Answer directly using internal training data without going to the internet.",
        "source": "local_llm"
    },
    {
        "name": "Basic Crawl",
        "description": "Use Crawl4AI to scrape the most relevant public web pages for the query.",
        "source": "crawl"
    },
    {
        "name": "Deep Crawl",
        "description": "Use Crawl4AI in deep mode, following sub-links one level down to gather richer data.",
        "source": "crawl_deep"
    },
    {
        "name": "Reddit Research",
        "description": "Search Reddit via web scraping for community discussion and expert opinions on the topic.",
        "source": "reddit"
    },
    {
        "name": "Visual Browser Navigation",
        "description": "Use browser-use or playwright to visually navigate a search engine and interact with websites.",
        "source": "browser"
    },
    {
        "name": "Gmail Operations",
        "description": "Read, search, or send emails using the local Gmail agent (Himalaya CLI).",
        "source": "gmail"
    },
    {
        "name": "Multi-Source Comparison",
        "description": "Combine all previous gathered data and use LLM to cross-reference and pick the best answer.",
        "source": "compare"
    },
]


class ReActGraph:
    """
    Full autonomous ReAct loop with escalating internet research strategies.
    The agent learns from each failure by querying the web for alternative methods.
    """

    def __init__(self, model_name="llama3.1", ollama_url="http://localhost:11434"):
        self.llm = ChatOllama(model=model_name, base_url=ollama_url)
        self.max_retries = 5
        self._harvester = None
        self._vision_hand = None
        self.graph = self._build_graph()

    def _run_async(self, coro):
        """Safely run an async coroutine from a sync context, even inside a running loop."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)

    # ------------------------------------------------------------------ #
    # Lazy-load real agents to avoid heavy imports on startup
    # ------------------------------------------------------------------ #
    def _get_harvester(self):
        if self._harvester is None:
            from brain.agents.harvester_agent import HarvesterAgent
            self._harvester = HarvesterAgent()
        return self._harvester

    def _get_vision_hand(self):
        if self._vision_hand is None:
            from brain.agents.vision_hand_agent import VisionHandAgent
            self._vision_hand = VisionHandAgent()
        return self._vision_hand

    # ------------------------------------------------------------------ #
    # Graph Construction
    # ------------------------------------------------------------------ #
    def _build_graph(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("analyze_and_plan",    self.analyze_and_plan)
        workflow.add_node("fetch_internet_advice", self.fetch_internet_advice)
        workflow.add_node("act_web",             self.act_web)
        workflow.add_node("observe_and_evaluate",self.observe_and_evaluate)
        workflow.add_node("finalize_output",     self.finalize_output)

        workflow.set_entry_point("analyze_and_plan")
        workflow.add_edge("analyze_and_plan",    "fetch_internet_advice")
        workflow.add_edge("fetch_internet_advice","act_web")
        workflow.add_edge("act_web",             "observe_and_evaluate")

        workflow.add_conditional_edges(
            "observe_and_evaluate",
            self.should_continue,
            {
                "retry":  "analyze_and_plan",
                "finish": "finalize_output",
            },
        )
        workflow.add_edge("finalize_output", END)

        return workflow.compile()

    # ------------------------------------------------------------------ #
    # Node: analyze_and_plan
    # ------------------------------------------------------------------ #
    def analyze_and_plan(self, state: AgentState) -> dict:
        retry  = state.get("retry_count", 0)
        
        if retry == 0:
            q_lower = state['input_query'].lower()
            if any(k in q_lower for k in ["gmail", "email", "inbox"]):
                chosen_strategy = next((s for s in ESCALATION_STRATEGIES if s["source"] == "gmail"), ESCALATION_STRATEGIES[-1])
            elif any(k in q_lower for k in ["login", "navigate", "click", "browser", "website"]):
                chosen_strategy = next((s for s in ESCALATION_STRATEGIES if s["source"] == "browser"), ESCALATION_STRATEGIES[-1])
            else:
                strategy_descriptions = "\n".join([f"- {s['name']}: {s['description']}" for s in ESCALATION_STRATEGIES])
                selection_prompt = (
                    f"User Goal: {state['input_query']}\n\n"
                    f"Available Strategies:\n{strategy_descriptions}\n\n"
                    f"Which strategy is the MOST appropriate starting point for this goal? "
                    f"Respond with EXACTLY the strategy name and nothing else."
                )
                selection_response = self.llm.invoke(selection_prompt).content.strip()
                # Default to Local LLM Knowledge if not found
                chosen_strategy = next((s for s in ESCALATION_STRATEGIES if s["name"].lower() in selection_response.lower()), ESCALATION_STRATEGIES[0])
            current_idx = ESCALATION_STRATEGIES.index(chosen_strategy)
        else:
            current_idx = state.get("current_strategy_index", 0)
            current_idx = min(current_idx + 1, len(ESCALATION_STRATEGIES) - 1)
            
        strategy = ESCALATION_STRATEGIES[current_idx]

        logger.info(f"[{retry+1}/{self.max_retries}] PLAN — Strategy: {strategy['name']}")

        prompt = (
            f"User Goal: {state['input_query']}\n"
            f"Current Strategy: {strategy['description']}\n"
            f"Previous Failures: {state.get('failure_log', 'None')}\n"
            f"Internet Advice from last retry: {state.get('internet_advice', 'None')}\n\n"
            f"Given the above context, write a concise action plan for this strategy. "
            f"What exact URLs, search terms, or actions should the agent take?"
        )

        response = self.llm.invoke(prompt)
        return {
            "plan":     response.content.strip(),
            "strategy": strategy["name"],
            "current_strategy_index": current_idx
        }

    # ------------------------------------------------------------------ #
    # Node: fetch_internet_advice
    # Searches the web/Reddit for "how to solve this if previous method failed"
    # ------------------------------------------------------------------ #
    def fetch_internet_advice(self, state: AgentState) -> dict:
        retry = state.get("retry_count", 0)
        if retry == 0:
            # No failure yet on first pass
            return {"internet_advice": ""}

        logger.info(f"[LEARN] Fetching new internet advice after failure #{retry}...")

        advice_query = (
            f"Best methods and tools for: {state['input_query']}. "
            f"Previous approach that failed: {state.get('strategy', '')}. "
            f"site:reddit.com OR developer blogs"
        )

        try:
            harvester = self._get_harvester()
            search_url = f"https://www.google.com/search?q={advice_query.replace(' ', '+')}"
            # Run the async harvester synchronously inside the sync LangGraph node
            raw_md = self._run_async(harvester.harvest_article(search_url))
            # Summarize the raw advice with the LLM
            summary_prompt = (
                f"Here is raw web content:\n{raw_md[:3000]}\n\n"
                f"Summarize the top 3 alternative methods/tools mentioned that could help achieve: "
                f"{state['input_query']}. Be concise."
            )
            advice_response = self.llm.invoke(summary_prompt)
            return {"internet_advice": advice_response.content.strip()}
        except Exception as e:
            logger.warning(f"Could not fetch internet advice: {e}")
            return {"internet_advice": f"Could not fetch advice: {e}"}

    # ------------------------------------------------------------------ #
    # Node: act_web  — routes to the correct real agent
    # ------------------------------------------------------------------ #
    def act_web(self, state: AgentState) -> dict:
        current_idx = state.get("current_strategy_index", 0)
        strategy = ESCALATION_STRATEGIES[current_idx]
        source   = strategy["source"]
        plan     = state["plan"]

        logger.info(f"[ACT] Executing '{strategy['name']}' strategy...")

        try:
            if source == "local_llm":
                prompt = f"Answer the user's goal directly without browsing:\nGoal: {state['input_query']}"
                response = self.llm.invoke(prompt)
                data = response.content.strip()

            elif source == "crawl":
                harvester = self._get_harvester()
                # Extract clean URLs from the plan — strip trailing punctuation the LLM may add
                import re
                raw_urls = re.findall(r'https?://[^\s<>"\']+', plan)
                # Strip trailing punctuation like ), . ,
                urls = [u.rstrip(".,);'\"") for u in raw_urls]
                target = urls[0] if urls else f"https://www.google.com/search?q={state['input_query'].replace(' ', '+')}"
                data = self._run_async(harvester.harvest_article(target))

            elif source == "crawl_deep":
                harvester = self._get_harvester()
                target = f"https://www.google.com/search?q={state['input_query'].replace(' ', '+')}"
                data = self._run_async(harvester.harvest_article(target))

            elif source == "reddit":
                harvester = self._get_harvester()
                reddit_url = f"https://www.reddit.com/search/?q={state['input_query'].replace(' ', '+')}&sort=relevance"
                data = self._run_async(harvester.harvest_article(reddit_url))

            elif source == "browser":
                from brain.agents.browser_agent import BrowserAgent
                try:
                    with BrowserAgent(headless=True) as browser:
                        # Basic integration: navigate to google with the query and return page text
                        browser.go_to(f"https://www.google.com/search?q={state['input_query'].replace(' ', '+')}")
                        data = browser.get_page_content()[:2000]
                except Exception as e:
                    data = f"Browser interaction failed: {e}"

            elif source == "gmail":
                from brain.agents.gmail_agent import GmailAgent
                agent = GmailAgent()
                q_lower = state['input_query'].lower()
                if "send" in q_lower or "write" in q_lower:
                    data = "Gmail send requested. Need specific 'to', 'subject', 'body' extraction logic."
                else:
                    data = agent.list_emails()

            elif source == "compare":
                # Multi-source: LLM synthesizes all data gathered so far
                compare_prompt = (
                    f"Goal: {state['input_query']}\n"
                    f"All data gathered so far:\n{state.get('gathered_data', '')}\n\n"
                    "Cross-reference this data from multiple sources and produce a final, accurate answer."
                )
                response = self.llm.invoke(compare_prompt)
                data = response.content.strip()

            else:
                data = "Unknown strategy source."

            return {"gathered_data": (state.get("gathered_data", "") + f"\n\n[{strategy['name']}]:\n{data}").strip()}

        except Exception as e:
            logger.error(f"act_web failed with strategy '{strategy['name']}': {e}")
            failure = state.get("failure_log", "")
            return {
                "gathered_data": state.get("gathered_data", ""),
                "failure_log": failure + f"\n- Strategy '{strategy['name']}' failed: {e}",
            }

    # ------------------------------------------------------------------ #
    # Node: observe_and_evaluate
    # ------------------------------------------------------------------ #
    def observe_and_evaluate(self, state: AgentState) -> dict:
        retry = state.get("retry_count", 0)
        logger.info(f"[EVALUATE] Checking if goal is satisfied (attempt {retry + 1})...")

        eval_prompt = (
            f"Goal: {state['input_query']}\n"
            f"Data Gathered:\n{state.get('gathered_data', '')[-3000:]}\n\n"
            "Is this data sufficient and accurate enough to fully answer the user's goal? "
            "Reply with EXACTLY 'YES' or 'NO', then a one-sentence reason."
        )
        response = self.llm.invoke(eval_prompt)
        evaluation = response.content.strip()

        failure_log = state.get("failure_log", "")
        if "NO" in evaluation.upper()[:5]:
            failure_log += f"\n- Attempt {retry + 1} insufficient: {evaluation}"

        return {
            "evaluation":  evaluation,
            "retry_count": retry + 1,
            "failure_log": failure_log,
        }

    def should_continue(self, state: AgentState) -> str:
        evaluation = state.get("evaluation", "")
        retry      = state.get("retry_count", 0)

        if "YES" in evaluation.upper()[:5]:
            logger.info("[DONE] Goal satisfied.")
            return "finish"
        if retry >= self.max_retries:
            logger.warning(f"[GIVE UP] Max retries ({self.max_retries}) reached. Escalating to user.")
            return "finish"

        logger.info(f"[RETRY] Goal not met. Escalating to strategy {retry + 1}...")
        return "retry"

    # ------------------------------------------------------------------ #
    # Node: finalize_output
    # ------------------------------------------------------------------ #
    def finalize_output(self, state: AgentState) -> dict:
        logger.info("[FINALIZE] Formatting final output...")
        finalize_prompt = (
            f"User Goal: {state['input_query']}\n"
            f"All Data Gathered:\n{state.get('gathered_data', '')[-4000:]}\n\n"
            "Write a clear, well-structured, final answer for the user. "
            "If you had to try multiple methods, note which one worked."
        )
        response = self.llm.invoke(finalize_prompt)
        return {"final_output": response.content.strip()}

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    async def execute(self, query: str) -> str:
        initial_state: AgentState = {
            "input_query":      query,
            "plan":             "",
            "strategy":         "",
            "gathered_data":    "",
            "evaluation":       "",
            "retry_count":      0,
            "failure_log":      "",
            "internet_advice":  "",
            "final_output":     "",
        }
        result = self.graph.invoke(initial_state)
        return result["final_output"]
