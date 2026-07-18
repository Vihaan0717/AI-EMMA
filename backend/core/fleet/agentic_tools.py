"""
NEXUS-X Agentic Tools — Universal Tool Manifest for All Fleet Agents
=====================================================================
This replaces the old Hank-only [ACTION] system with a structured tool
manifest that any agent can invoke through the ReAct engine.

Every tool has:
  - name: unique identifier
  - description: what it does (shown to agents in their system prompt)
  - handler: async function that executes the tool
  - parameters: expected input keys
  - allowed_agents: list of agent IDs that can use this tool (or ["*"] for all)
"""

import logging
import json
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("AgenticTools")


@dataclass
class AgenticTool:
    """Definition of a single tool available to fleet agents."""
    name: str
    description: str
    handler: Optional[Callable] = None       # Set at runtime
    parameters: Dict[str, str] = field(default_factory=dict)
    allowed_agents: List[str] = field(default_factory=lambda: ["*"])
    category: str = "general"
    requires_approval: bool = False          # If True, requires Boss approval before execution


class AgenticToolRegistry:
    """
    Central registry of tools available to the agentic fleet.
    Agents query this to discover what they can do, and the ReAct engine
    calls the handler when an agent emits a [TOOL_CALL] block.
    """

    def __init__(self):
        self._tools: Dict[str, AgenticTool] = {}
        self._register_builtin_tools()
        logger.info(f"AgenticToolRegistry: {len(self._tools)} tools registered.")

    def register(self, tool: AgenticTool):
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[AgenticTool]:
        return self._tools.get(name)

    def list_for_agent(self, agent_id: str) -> List[AgenticTool]:
        """Return all tools available to a specific agent."""
        result = []
        for tool in self._tools.values():
            if "*" in tool.allowed_agents or agent_id.lower() in tool.allowed_agents:
                result.append(tool)
        return result

    def generate_tool_prompt(self, agent_id: str) -> str:
        """
        Generate the tool-use instruction block that gets injected into
        an agent's system prompt. This tells the agent what tools exist
        and how to invoke them.
        """
        tools = self.list_for_agent(agent_id)
        if not tools:
            return ""

        lines = [
            "\n[AVAILABLE TOOLS]",
            "You can invoke tools by writing a [TOOL_CALL] block in your response.",
            "Format: [TOOL_CALL] {\"tool\": \"tool_name\", \"params\": {\"key\": \"value\"}} [/TOOL_CALL]",
            "After invoking a tool, STOP and wait for the system to return [TOOL_RESULT].",
            "Then continue your reasoning with the result.",
            "",
            "Tools you can use:"
        ]
        for t in tools:
            param_desc = ", ".join([f"{k}: {v}" for k, v in t.parameters.items()]) if t.parameters else "none"
            lines.append(f"  - {t.name}: {t.description} (params: {param_desc})")

        lines.append("")
        lines.append("Example:")
        lines.append("[THOUGHT] I need to verify this calculation by running code. [/THOUGHT]")
        lines.append("[TOOL_CALL] {\"tool\": \"run_python\", \"params\": {\"code\": \"print(2+2)\"}} [/TOOL_CALL]")
        lines.append("... system returns [TOOL_RESULT] 4 [/TOOL_RESULT] ...")
        lines.append("[THOUGHT] The result is 4, which confirms my calculation. [/THOUGHT]")
        lines.append("[FINAL_ANSWER] The answer is 4. [/FINAL_ANSWER]")

        return "\n".join(lines)

    async def execute_tool(self, tool_name: str, params: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
        """Execute a tool and return the result."""
        tool = self._tools.get(tool_name)
        if not tool:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}

        # Permission check
        if "*" not in tool.allowed_agents and agent_id.lower() not in tool.allowed_agents:
            return {"success": False, "error": f"Agent '{agent_id}' is not authorized to use tool '{tool_name}'"}

        if tool.requires_approval:
            logger.warning(f"AgenticTools: Tool '{tool_name}' requires Boss approval — skipping auto-exec.")
            return {"success": False, "error": f"Tool '{tool_name}' requires Boss approval. Awaiting confirmation."}

        if tool.handler is None:
            return {"success": False, "error": f"Tool '{tool_name}' has no handler registered."}

        try:
            result = await tool.handler(**params)
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"AgenticTools: Tool '{tool_name}' failed: {e}")
            return {"success": False, "error": str(e)}

    def _register_builtin_tools(self):
        """Register all built-in agentic tools."""

        # ── 1. Code Execution (Sandbox) ─────────────────────────────
        async def _run_python(code: str, timeout: int = 30) -> str:
            from tools.agent_sandbox import agent_sandbox
            result = await agent_sandbox.execute_python(code, timeout=int(timeout))
            if result.success:
                return f"EXIT_CODE=0\nSTDOUT:\n{result.stdout}"
            else:
                return f"EXIT_CODE={result.exit_code}\nSTDERR:\n{result.stderr}\nSTDOUT:\n{result.stdout}"

        self.register(AgenticTool(
            name="run_python",
            description="Execute Python code in a sandboxed environment. Returns stdout/stderr.",
            handler=_run_python,
            parameters={"code": "str (Python source code)", "timeout": "int (seconds, default 30)"},
            allowed_agents=["*"],
            category="execution"
        ))

        # ── 2. Shell Command ────────────────────────────────────────
        async def _run_shell(command: str, timeout: int = 30) -> str:
            from tools.agent_sandbox import agent_sandbox
            result = await agent_sandbox.execute_shell(command, timeout=int(timeout))
            if result.success:
                return f"EXIT_CODE=0\n{result.stdout}"
            else:
                return f"EXIT_CODE={result.exit_code}\nSTDERR:\n{result.stderr}\nSTDOUT:\n{result.stdout}"

        self.register(AgenticTool(
            name="run_shell",
            description="Execute a shell/PowerShell command. Returns stdout/stderr.",
            handler=_run_shell,
            parameters={"command": "str (shell command)", "timeout": "int (seconds, default 30)"},
            allowed_agents=["hank", "sentinel", "cyber_auditor", "mythos"],
            category="execution"
        ))

        # ── 3. Web Search ────────────────────────────────────────────
        async def _web_search(query: str) -> str:
            try:
                # Try to use WebBrain if available
                from search.web_brain import WebBrain
                wb = WebBrain()
                result = await wb.learn(query)
                if result:
                    if result.get("source") == "wikipedia":
                        return f"[Wikipedia] {result.get('content', '')[:2000]}"
                    elif "documents" in result:
                        docs = result["documents"][:3]
                        return "\n---\n".join([f"[{d.get('source','web')}] {d.get('text','')[:600]}" for d in docs])
                return "No results found."
            except Exception as e:
                return f"Search error: {e}"

        self.register(AgenticTool(
            name="web_search",
            description="Search the web for information on a topic. Returns summarized results.",
            handler=_web_search,
            parameters={"query": "str (search query)"},
            allowed_agents=["*"],
            category="research"
        ))

        async def _scrape_website(url: str) -> str:
            """Scrape full content from a website."""
            try:
                import urllib.request
                from bs4 import BeautifulSoup
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                html = urllib.request.urlopen(req).read()
                soup = BeautifulSoup(html, 'html.parser')
                # Extract text
                for script in soup(["script", "style"]):
                    script.extract()
                text = soup.get_text(separator=' ', strip=True)
                # Return up to 8000 chars to avoid blowing up context window
                return f"[Content from {url}]\n{text[:8000]}"
            except Exception as e:
                return f"Scrape error: {e}"

        self.register(AgenticTool(
            name="scrape_website",
            description="Extract and read the full text content from a specific URL (Wikipedia, IMDB, Arxiv, News, etc).",
            handler=_scrape_website,
            parameters={"url": "str"},
            allowed_agents=["cosmos", "atlas"],
            category="research"
        ))

        async def _read_social_trends() -> str:
            """Read the latest Instagram social insights."""
            try:
                import json
                with open("memory/social_insights.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                output = [f"Social Trends Last Updated: {data.get('last_updated')}"]
                output.append("\n[RECENTLY LIKED REELS/POSTS]")
                for item in data.get("liked_items", [])[:5]:
                    output.append(f"- By {item.get('user')} ({item.get('like_count')} likes): {item.get('caption')}")
                    
                output.append("\n[CURRENT FEED/TIMELINE]")
                for item in data.get("feed_items", [])[:5]:
                    output.append(f"- By {item.get('user')} ({item.get('like_count')} likes): {item.get('caption')}")
                    
                return "\n".join(output)
            except FileNotFoundError:
                return "No social insights found. The Instagram Monitor might not be running or hasn't collected data yet."
            except Exception as e:
                return f"Error reading social trends: {e}"

        self.register(AgenticTool(
            name="read_social_trends",
            description="Reads the latest social media trends, reels, and liked content from the Instagram Monitor.",
            handler=_read_social_trends,
            parameters={},
            allowed_agents=["cosmos", "cleo"],
            category="research"
        ))

        # ── 4. File Read ──────────────────────────────────────────────
        async def _file_read(path: str) -> str:
            from pathlib import Path as P
            target = P(path)
            if not target.exists():
                return f"File not found: {path}"
            if target.stat().st_size > 50_000:
                return f"File too large ({target.stat().st_size} bytes). Max 50KB for agent reads."
            try:
                return target.read_text(encoding="utf-8")[:8000]
            except Exception as e:
                return f"Read error: {e}"

        self.register(AgenticTool(
            name="file_read",
            description="Read a file's contents (max 50KB). Returns text content.",
            handler=_file_read,
            parameters={"path": "str (absolute or relative file path)"},
            allowed_agents=["*"],
            category="filesystem"
        ))

        # ── 5. File Write ─────────────────────────────────────────────
        async def _file_write(path: str, content: str) -> str:
            from pathlib import Path as P
            target = P(path)
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
                return f"Written {len(content)} bytes to {path}"
            except Exception as e:
                return f"Write error: {e}"

        self.register(AgenticTool(
            name="file_write",
            description="Write content to a file. Creates parent directories if needed.",
            handler=_file_write,
            parameters={"path": "str (file path)", "content": "str (file content)"},
            allowed_agents=["hank", "cosmos", "atlas_x", "alfred"],
            category="filesystem",
            requires_approval=True   # Destructive — needs Boss approval
        ))

        # ── 6. Math Evaluate ──────────────────────────────────────────
        async def _math_eval(expression: str) -> str:
            """Safely evaluate a mathematical expression."""
            import ast
            try:
                # Only allow safe math operations
                tree = ast.parse(expression, mode="eval")
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        return "ERROR: Function calls not allowed. Use basic arithmetic only."
                result = eval(compile(tree, "<math>", "eval"), {"__builtins__": {}}, {})
                return str(result)
            except Exception as e:
                return f"Math error: {e}"

        self.register(AgenticTool(
            name="math_eval",
            description="Safely evaluate a mathematical expression (no function calls). Returns the result.",
            handler=_math_eval,
            parameters={"expression": "str (e.g., '(3.14 * 5**2) / 2')"},
            allowed_agents=["*"],
            category="reasoning"
        ))

        # ── 7. Memory Store ──────────────────────────────────────────
        async def _memory_store(content: str, importance: float = 0.7) -> str:
            """Store a fact in long-term memory."""
            try:
                from core.fleet.local_db import fleet_db
                fleet_db.add_correction_note("system", "agentic_memory", content)
                return f"Stored in memory: {content[:100]}..."
            except Exception as e:
                return f"Memory store error: {e}"

        self.register(AgenticTool(
            name="memory_store",
            description="Store a fact or insight in the shared fleet long-term memory.",
            handler=_memory_store,
            parameters={"content": "str (the fact to remember)", "importance": "float (0.0-1.0)"},
            allowed_agents=["*"],
            category="memory"
        ))

        # ── Knowledge Graph ──────────────────────────────────────────
        async def _kg_add(subject: str, predicate: str, object_str: str) -> str:
            """Add a fact (triple) to the semantic knowledge graph."""
            try:
                from core.fleet.knowledge_graph import knowledge_graph
                success = await knowledge_graph.add_triple(subject, predicate, object_str)
                if success:
                    return f"Successfully added to Knowledge Graph: [{subject}] --({predicate})--> [{object_str}]"
                return "Failed to add to Knowledge Graph (AI Engine might not be bound)."
            except Exception as e:
                return f"Knowledge Graph error: {e}"

        self.register(AgenticTool(
            name="kg_add",
            description="Store a relationship or fact in the Knowledge Graph. Use simple concepts.",
            handler=_kg_add,
            parameters={"subject": "str (e.g., 'atlas')", "predicate": "str (e.g., 'is_expert_in')", "object_str": "str (e.g., 'quantum_physics')"},
            allowed_agents=["*"],
            category="memory"
        ))

        async def _kg_search(query: str) -> str:
            """Semantic search in the knowledge graph."""
            try:
                from core.fleet.knowledge_graph import knowledge_graph
                results = await knowledge_graph.semantic_search(query, top_k=3)
                if not results:
                    return "No relevant facts found in the Knowledge Graph."
                
                output = ["Found in Knowledge Graph:"]
                for r in results:
                    output.append(f"- [{r['subject']}] --({r['predicate']})--> [{r['object']}] (Relevance: {r['score']:.2f})")
                return "\n".join(output)
            except Exception as e:
                return f"Knowledge Graph search error: {e}"

        self.register(AgenticTool(
            name="kg_search",
            description="Semantically search the Knowledge Graph for facts. Matches by meaning, not exact words.",
            handler=_kg_search,
            parameters={"query": "str (e.g., 'who knows about physics?')"},
            allowed_agents=["*"],
            category="research"
        ))

        # ── 8. Delegate to Agent ──────────────────────────────────────
        async def _delegate(target_agent: str, sub_task: str) -> str:
            """
            Delegate a sub-task to another agent.
            This is handled by the swarm coordinator, not executed here directly.
            """
            return f"DELEGATION_REQUEST: {target_agent} | {sub_task}"

        self.register(AgenticTool(
            name="delegate",
            description="Delegate a sub-task to another specialist agent. Use this when the task requires expertise outside your domain.",
            handler=_delegate,
            parameters={"target_agent": "str (atlas, hank, cosmos, sentinel, etc.)", "sub_task": "str (the task description)"},
            allowed_agents=["*"],
            category="coordination"
        ))

        # ── Goal & Task Scheduling ────────────────────────────────────
        async def _schedule_task(target_agent: str, task: str, delay_seconds: int) -> str:
            """Schedule a task for a future time."""
            try:
                import time
                from core.fleet.goal_manager import goal_manager
                run_at = time.time() + int(delay_seconds)
                result = goal_manager.schedule_task(target_agent, task, run_at)
                return f"Task scheduled successfully. ID: {result.get('task_id')}"
            except Exception as e:
                return f"Scheduling error: {e}"

        self.register(AgenticTool(
            name="schedule_task",
            description="Schedule a background task to run in the future.",
            handler=_schedule_task,
            parameters={"target_agent": "str (e.g., 'atlas')", "task": "str", "delay_seconds": "int"},
            allowed_agents=["*"],
            category="coordination"
        ))

        async def _add_goal(agent_id: str, description: str) -> str:
            """Set a persistent long-term goal."""
            try:
                from core.fleet.goal_manager import goal_manager
                result = goal_manager.add_goal(agent_id, description)
                if result.get("success"):
                    return f"Goal added successfully. ID: {result.get('goal_id')}"
                return f"Failed to add goal: {result.get('error')}"
            except Exception as e:
                return f"Goal error: {e}"

        self.register(AgenticTool(
            name="add_goal",
            description="Add a persistent long-term goal for an agent to work on in the background.",
            handler=_add_goal,
            parameters={"agent_id": "str", "description": "str"},
            allowed_agents=["*"],
            category="coordination"
        ))

        # ── 9. MIDI Music Generator ──────────────────────────────────
        async def _create_midi(notes: str, filename: str = "output.mid", bpm: int = 120) -> str:
            """Generate a MIDI file from note string."""
            try:
                from tools.music_tools import create_midi_file
                result = create_midi_file(notes, filename, int(bpm))
                return result
            except Exception as e:
                return f"MIDI generation error: {e}"

        self.register(AgenticTool(
            name="create_midi",
            description="Generate a MIDI music file from a note sequence (e.g., 'C4 D4 E4 F4 G4').",
            handler=_create_midi,
            parameters={"notes": "str (space-separated notes like 'C4 D4 E4')", "filename": "str", "bpm": "int"},
            allowed_agents=["cosmos"],
            category="creative"
        ))

        # ── 10. Vision / Screen Inspect ──────────────────────────────
        async def _look_at_screen(query: str = "describe what's on screen") -> str:
            """Capture and analyze the current screen."""
            try:
                from tools.vision_tools import look_at_screen
                return await look_at_screen(query)
            except Exception as e:
                return f"Vision error: {e}"

        self.register(AgenticTool(
            name="look_at_screen",
            description="Capture the current screen and describe/analyze what's visible.",
            handler=_look_at_screen,
            parameters={"query": "str (what to look for on screen)"},
            allowed_agents=["hank", "sentinel", "cyber_auditor"],
            category="vision"
        ))

        # ── 11. Headless Web Browser & Transactions ──────────────────────
        async def _browse_url(url: str) -> str:
            try:
                from tools.browser_agent import browser_agent
                return await browser_agent.browse(url)
            except Exception as e:
                return f"Browse error: {e}"

        self.register(AgenticTool(
            name="browse_url",
            description="Open a URL in a headless browser and read its rendered content (ideal for dynamic sites like Zomato/Swiggy).",
            handler=_browse_url,
            parameters={"url": "str"},
            allowed_agents=["hank", "alfred"],
            category="web"
        ))

        async def _click_web_element(selector: str) -> str:
            try:
                from tools.browser_agent import browser_agent
                return await browser_agent.click(selector)
            except Exception as e:
                return f"Click error: {e}"

        self.register(AgenticTool(
            name="click_web_element",
            description="Click a web element using a CSS selector inside the headless browser.",
            handler=_click_web_element,
            parameters={"selector": "str"},
            allowed_agents=["hank", "alfred"],
            category="web"
        ))

        async def _fill_web_form(selector: str, value: str) -> str:
            try:
                from tools.browser_agent import browser_agent
                return await browser_agent.fill_form(selector, value)
            except Exception as e:
                return f"Fill error: {e}"

        self.register(AgenticTool(
            name="fill_web_form",
            description="Fill a text input on the current webpage using a CSS selector.",
            handler=_fill_web_form,
            parameters={"selector": "str", "value": "str"},
            allowed_agents=["hank", "alfred"],
            category="web"
        ))

        async def _request_human_approval(amount: float, description: str) -> str:
            """Pauses execution and sends an approval request via Telegram."""
            try:
                import os
                
                # We import dynamically to avoid circular imports at module level
                try:
                    from main import nexus_brain
                except ImportError:
                    return "ERROR: Could not import nexus_brain. Cannot request approval."
                
                if nexus_brain and 'telegram' in nexus_brain.modules:
                    telegram_service = nexus_brain.modules['telegram']
                    if not telegram_service:
                        return "ERROR: Telegram Service is not active. Cannot request approval."
                        
                    # This will suspend execution of the ReAct loop until the user clicks Approve/Deny
                    approved = await telegram_service.request_financial_authorization(amount, description)
                    
                    if approved:
                        return f"SUCCESS: Approval GRANTED by Boss for ₹{amount}."
                    else:
                        return f"DENIED: Boss denied the transaction for ₹{amount}."
                else:
                    return "ERROR: Telegram Service is not bound to the active Brain. Cannot request approval."
                    
            except Exception as e:
                return f"Approval request error: {e}"

        self.register(AgenticTool(
            name="request_human_approval",
            description="Request human approval before executing a financial transaction. MUST be used before spending money.",
            handler=_request_human_approval,
            parameters={"amount": "float", "description": "str (What are we buying?)"},
            allowed_agents=["hank", "alfred"],
            category="finance"
        ))

        # ── 12. Computer Use (GUI Actions) ───────────────────────────
        async def _click_element(element_name: str) -> str:
            """Find an element on screen using VLM and click it."""
            try:
                import os
                import time
                from services.hand_service import HandService
                # Needs access to AI engine via system instance. 
                # For this tool, we assume the system saves screenshots to a known path.
                shot_path = "memory/latest_screen.png"
                
                hands = HandService()
                hands.capture_screen(shot_path)
                
                # We need the AI engine. We'll import it from the globally active Brain context.
                try:
                    from main import nexus_brain
                except ImportError:
                    return "ERROR: Could not import nexus_brain. Cannot access AIEngine."
                
                if not nexus_brain or 'ai' not in nexus_brain.modules:
                    return "ERROR: AI Engine is not active in the master brain."
                    
                ai = nexus_brain.modules['ai']
                
                bbox = await ai.find_object(element_name, shot_path)
                if not bbox:
                    return f"Failed to locate '{element_name}' on screen."
                
                # bbox is [ymin, xmin, ymax, xmax]
                ymin, xmin, ymax, xmax = bbox
                center_x = (xmin + xmax) // 2
                center_y = (ymin + ymax) // 2
                
                result = hands.click_at(center_x, center_y)
                return f"Located '{element_name}' at {bbox}. {result}"
            except Exception as e:
                return f"Click element error: {e}"

        self.register(AgenticTool(
            name="click_element",
            description="Visually locate a UI element (e.g., 'search bar', 'submit button') and click it.",
            handler=_click_element,
            parameters={"element_name": "str (description of the target)"},
            allowed_agents=["hank", "sentinel"],
            category="gui"
        ))

        async def _type_text(text: str, hit_enter: bool = False) -> str:
            """Type text using keyboard."""
            try:
                from services.hand_service import HandService
                hands = HandService()
                return hands.type_text(text, hit_enter=hit_enter)
            except Exception as e:
                return f"Type text error: {e}"

        self.register(AgenticTool(
            name="type_text",
            description="Type text at the current cursor position. Optionally hit Enter.",
            handler=_type_text,
            parameters={"text": "str", "hit_enter": "bool"},
            allowed_agents=["hank", "sentinel"],
            category="gui"
        ))

        async def _press_hotkey(keys: str) -> str:
            """Press a combination of keys."""
            try:
                from services.hand_service import HandService
                hands = HandService()
                key_list = [k.strip() for k in keys.split(",")]
                return hands.press_hotkey(key_list)
            except Exception as e:
                return f"Hotkey error: {e}"

        self.register(AgenticTool(
            name="press_hotkey",
            description="Press OS hotkeys. Provide keys comma-separated (e.g., 'win, d' or 'ctrl, c').",
            handler=_press_hotkey,
            parameters={"keys": "str"},
            allowed_agents=["hank", "sentinel"],
            category="gui"
        ))

        async def _window_manage(action: str, title: str = "") -> str:
            """Manage OS windows."""
            try:
                from services.hand_service import HandService
                hands = HandService()
                action = action.lower()
                if action == "list":
                    wins = hands.list_windows()
                    return "Open Windows:\n" + "\n".join(wins[:15])
                elif action == "maximize":
                    return hands.maximize_window(title)
                elif action == "close":
                    return hands.close_window(title)
                else:
                    return f"Unknown window action: {action}"
            except Exception as e:
                return f"Window manage error: {e}"

        self.register(AgenticTool(
            name="window_manage",
            description="Manage OS windows. Actions: 'list', 'maximize', 'close'. Title required for maximize/close.",
            handler=_window_manage,
            parameters={"action": "str", "title": "str (optional)"},
            allowed_agents=["hank", "sentinel"],
            category="gui"
        ))

        # ── 13. Motion Mimicry ───────────────────────────────────────
        async def _learn_body_language(youtube_url: str) -> str:
            """Learn and mimic body language from a YouTube video."""
            try:
                import asyncio
                from services.vrm_motion_service import VRMMotionService
                
                service = VRMMotionService(port=8001)
                
                # Start server in background
                asyncio.create_task(service.start_server())
                
                # Start processing video in background
                asyncio.create_task(service.process_video(youtube_url))
                
                return f"Successfully initiated motion capture from {youtube_url}. The VRM avatar is now mimicking the body language."
            except Exception as e:
                return f"Failed to learn body language: {e}"

        self.register(AgenticTool(
            name="learn_body_language",
            description="Autonomously observe and mimic a person's body language/pose from a YouTube video or stream.",
            handler=_learn_body_language,
            parameters={"youtube_url": "str"},
            allowed_agents=["cleo", "hank", "arion"],
            category="vision"
        ))

# Global registry instance...
# ── Global Singleton ──────────────────────────────────────────────
agentic_tool_registry = AgenticToolRegistry()
