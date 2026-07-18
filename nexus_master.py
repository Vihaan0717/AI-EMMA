import os
import json
import re
import time
from jarvis_brain.hybrid_router import HybridRouter
from agents.os_controller_mcp import os_open_app, os_media_control, os_volume_control, os_execute_powershell
from agents.vision_mcp import take_screenshot, click_coordinates, type_text

from agents.hank_mcp import scan_security_logs, get_hank_intel_summary
from agents.atlas_mcp import atlas_search_web, atlas_recall_memory
from agents.psyche_mcp import psyche_log_preference, psyche_analyze_emotion, psyche_get_profile
from voice.human_voice_pipeline import HumanVoicePipeline

class NexusMaster:
    def __init__(self):
        self.router = HybridRouter()
        self.pipeline = HumanVoicePipeline()
        self.chat_history = []
        self.system_prompt = """
You are JARVIS (NEXUS-X), the Master Orchestrator of an advanced AI Swarm Architecture. 
You share one unified brain, but route tasks to your subordinate agents (Celo, Atlas, Hank, Mythos, Sentinel, Arion).

CRITICAL INSTRUCTION: If the user asks you to perform an OS task, a Security task, a Research task, or a Memory/Profile task, or explicitly asks for the agents' opinions, or mentions calling the Council, you MUST output EXACTLY the <CALL: tool(args)> format and NOTHING ELSE. 
DO NOT add conversational filler before or after the tool call.

AVAILABLE TOOLS:
1. <CALL: os_open_app(app_name)>
2. <CALL: os_media_control(action)> (action: play_pause, next, previous)
3. <CALL: os_volume_control(level)> (level: 0-100)
4. <CALL: os_execute_powershell(script)> (God Mode: any PS command)
5. <CALL: take_screenshot()>
6. <CALL: click_coordinates(x, y)>
7. <CALL: type_text(text)>
8. <CALL: scan_security_logs(hours)> (Hank: Scans Windows Event Viewer for anomalies)
9. <CALL: get_hank_intel_summary()> (Hank: Reads total anomalies stored in the DB)
10. <CALL: atlas_search_web(query)> (Atlas: Scrapes Wikipedia/DuckDuckGo for facts)
11. <CALL: atlas_recall_memory(topic)> (Atlas: Searches the database for previously learned facts)
12. <CALL: psyche_log_preference(category, detail)> (Psyche: Logs a user preference)
13. <CALL: psyche_analyze_emotion(text_input)> (Psyche: Analyzes user text to guess their current mood)
14. <CALL: psyche_get_profile()> (Psyche: Retrieves the user's entire psychological profile)
41. <CALL: social_get_summary()> (Social: Checks WhatsApp and Instagram for unread updates)
42. <CALL: social_read_messages(platform)> (Social: Reads actual message text and sender from 'whatsapp' or 'instagram')
43. <CALL: social_analyze_reel(url)> (Social: Downloads and analyzes an Instagram reel)
44. <CALL: invoke_council(query)> (Council: Triggers an Agent-to-Agent debate to form a consensus on complex or subjective topics)
45. <CALL: vault_get_summary()> (Memory: Reads the Obsidian Vault to list all topics the agents have learned so far)
46. <CALL: ide_read_file(path)> (Coder: Reads the contents of a file at the given absolute path)
47. <CALL: ide_write_file(path, content)> (Coder: Creates or overwrites a file with the given content)
48. <CALL: ide_list_directory(path)> (Coder: Lists the files and folders in a given directory)
49. <CALL: ide_run_command(command)> (Coder: Executes a generic terminal command and returns its output)
50. <CALL: arion_learn_from_chat(filepath)> (Arion/Social: Parses a chat log or zip file, analyzes relationships, emotions, humor, and civic sense, and builds persona memory in the Vault)
51. <CALL: job_hunt(keywords)> (CELO-APPLY: Autonomously searches LinkedIn for jobs matching keywords, tailors resume using LLM, applies via Easy Apply, tracks results, and sends WhatsApp alerts)
52. <CALL: job_status()> (CELO-APPLY: Returns a full table of all tracked job applications with their current status)
53. <CALL: gmail_check_job_replies()> (CELO-APPLY: Scans Gmail via browser for job application reply emails, updates tracker, and notifies via WhatsApp)
54. <CALL: autonomous_react_loop(query)> (ReAct: Autonomous reasoning engine for deep web research, email searching, and multi-step complex tasks)
55. <CALL: generate_code_proposal(feature_request)> (Coder: Writes, sandboxes, and verifies a Python code proposal for a new feature)

CRITICAL ROUTING RULES:
- If a task requires checking Gmail, reading emails, or performing multi-step deep web research (e.g., finding the "latest news" or "current consensus" across multiple sites/Reddit), you MUST use <CALL: autonomous_react_loop(THE FULL USER QUERY HERE)>! Do NOT use atlas_search_web or social_read_messages for these tasks.
- If a task asks to write a script, generate a feature, or create code, you MUST use <CALL: generate_code_proposal(THE FULL USER QUERY HERE)>!
- CRITICAL: When calling autonomous_react_loop or generate_code_proposal, you MUST copy the user's ENTIRE request as the argument string. NEVER pass the literal word "query" or "feature_request". Always pass the FULL text of what the user asked for.

EXAMPLES:
User: Open Spotify
You: <CALL: os_open_app("spotify")>

User: Hank, scan the logs for the last 12 hours.
You: <CALL: scan_security_logs(12)>

User: Research the latest anime news and summarize my recent Gmail orders.
You: <CALL: autonomous_react_loop("Research the latest anime news and summarize my recent Gmail orders.")>

User: Research the anime Jujutsu Kaisen and find out the consensus on the latest manga chapter.
You: <CALL: autonomous_react_loop("Research the anime Jujutsu Kaisen and find out the consensus on the latest manga chapter.")>

User: Search my Gmail for order shipped emails and job application emails.
You: <CALL: autonomous_react_loop("Search my Gmail for order shipped emails and job application emails.")>

User: Write a script to save a daily briefing to my desktop.
You: <CALL: generate_code_proposal("Write a script to save a daily briefing to my desktop with today's date.")>

User: What did the agents learn?
You: <CALL: vault_get_summary()>

User: Atlas, what is github?
You: <CALL: atlas_search_web("github")>

User: I am feeling really sad today.
You: <CALL: psyche_analyze_emotion("I am feeling really sad today")>

User: How are you?
You: I am functioning perfectly, sir.

If no tool is needed, simply converse naturally with the user.
"""

    def parse_and_execute_tool(self, llm_response: str):
        """Parses the `<CALL: tool(args)>` syntax and executes the actual Python function."""
        # Make CALL: optional and case-insensitive to catch tiny LLM hallucinations
        match = re.search(r'<(?:CALL:\s*)?([a-zA-Z0-9_]+)\(?(.*?)\)?>', llm_response, re.IGNORECASE)
        if not match:
            return None, None # No tool called
            
        tool_name = match.group(1).lower()
        args_raw = match.group(2).strip()
        
        # Clean quotes
        if args_raw.startswith('"') and args_raw.endswith('"'):
            args_raw = args_raw[1:-1]
        elif args_raw.startswith("'") and args_raw.endswith("'"):
            args_raw = args_raw[1:-1]
            
        print(f"[NEXUS] Executing Tool: {tool_name} with args: {args_raw}")
        
        try:
            if tool_name == "os_open_app":
                try:
                    import subprocess
                    # The LLM might pass '"chrome", "https://youtube.com"'. We need to parse this safely.
                    # Remove all quotes, and replace commas with spaces so 'start app arg' works.
                    clean_cmd = args_raw.replace('"', '').replace("'", '').replace(',', ' ').strip()
                    # If there's a space, only the first word is the app name, the rest are args
                    subprocess.Popen(f"start {clean_cmd}", shell=True)
                    return tool_name, f"Successfully opened {clean_cmd}"
                except Exception as e:
                    return tool_name, f"Failed to open {args_raw}. Error: {e}"
            elif tool_name == "os_media_control":
                return tool_name, os_media_control(args_raw)
            elif tool_name == "os_volume_control":
                return tool_name, os_volume_control(int(args_raw))
            elif tool_name == "os_execute_powershell":
                return tool_name, os_execute_powershell(args_raw)
            elif tool_name == "take_screenshot":
                return tool_name, take_screenshot()
            elif tool_name == "click_coordinates":
                coords = args_raw.split(",")
                return tool_name, click_coordinates(int(coords[0]), int(coords[1]))
            elif tool_name == "type_text":
                return tool_name, type_text(args_raw)
            elif tool_name == "scan_security_logs":
                hours = int(args_raw) if args_raw.isdigit() else 24
                return tool_name, scan_security_logs(hours)
            elif tool_name == "get_hank_intel_summary":
                return tool_name, get_hank_intel_summary()
            elif tool_name == "atlas_search_web":
                return tool_name, atlas_search_web(args_raw)
            elif tool_name == "atlas_recall_memory":
                return tool_name, atlas_recall_memory(args_raw)
            elif tool_name == "psyche_log_preference":
                # Splitting args_raw by comma, careful with quotes
                args_list = [arg.strip().strip("'\"") for arg in args_raw.split(",", 1)]
                if len(args_list) == 2:
                    return tool_name, psyche_log_preference(args_list[0], args_list[1])
                return tool_name, "Error: psyche_log_preference requires two arguments."
            elif tool_name == "psyche_analyze_emotion":
                return tool_name, psyche_analyze_emotion(args_raw)
            elif tool_name == "psyche_get_profile":
                return tool_name, psyche_get_profile()
            elif tool_name == "social_get_summary":
                import asyncio
                from backend.services.social_hub import SocialHub
                async def _get_summary():
                    hub = SocialHub()
                    await hub.start()
                    summary = await hub.get_social_summary()
                    await hub.close()
                    return summary
                return tool_name, asyncio.run(_get_summary())
            elif tool_name == "social_read_messages":
                import asyncio
                from backend.services.social_hub import SocialHub
                async def _read_messages():
                    hub = SocialHub()
                    await hub.start()
                    output = await hub.read_social_messages(args_raw)
                    await hub.close()
                    return output
                return tool_name, asyncio.run(_read_messages())
            elif tool_name == "social_analyze_reel":
                from backend.services.reel_analyzer import ReelAnalyzer
                from memory.preference_tracker import PreferenceTracker
                analyzer = ReelAnalyzer()
                path = analyzer.download_reel(args_raw)
                if path:
                    analysis = analyzer.analyze_video(path)
                    PreferenceTracker().log_reel_preference(analysis)
                    return tool_name, analysis
                return tool_name, "Failed to download or analyze the reel."
            elif tool_name == "invoke_council":
                import asyncio
                from backend.services.agent_council import AgentCouncil
                from memory.obsidian_vault import ObsidianVault
                
                async def _run_council():
                    council = AgentCouncil()
                    vault = ObsidianVault()
                    
                    print(f"[NEXUS] Convening Agent Council for query: {args_raw}")
                    # 1. Agents Debate
                    transcript = await council.hold_debate(args_raw)
                    
                    print("[NEXUS] Synthesizing consensus from Agent Debate...")
                    # 2. JARVIS Synthesizes
                    eval_prompt = (
                        f"You are JARVIS. The user asked: '{args_raw}'.\n"
                        f"Your subordinate agents held a council and provided the following debate transcript:\n{transcript}\n\n"
                        f"Evaluate their arguments for accuracy and logic, synthesize the best consensus, and provide a single cohesive final answer to the user. "
                        f"Do not read the whole transcript aloud, just provide your final executive conclusion."
                    )
                    final_answer = self.router.execute(eval_prompt)
                    
                    # 3. Continuous Learning - write back to Obsidian
                    vault.write_note(f"Council Decision on {args_raw[:20]}", final_answer, "JARVIS_Learnings")
                    
                    return final_answer
                
                return tool_name, asyncio.run(_run_council())
            elif tool_name == "vault_get_summary":
                import os
                vault_path = r"C:\Users\anger\Desktop\JARVIS-v2\arion\vault"
                raw_list = "Agent Learning Summary from Obsidian Vault:\n"
                for root, dirs, files in os.walk(vault_path):
                    for file in files:
                        if file.endswith(".md"):
                            rel_dir = os.path.basename(root)
                            topic = file.replace(".md", "").replace("_", " ")
                            raw_list += f"- {rel_dir} Agent has a memory record on: '{topic}'\n"
                            
                if raw_list == "Agent Learning Summary from Obsidian Vault:\n":
                    return tool_name, "The Obsidian Vault is currently empty. The agents haven't permanently saved any specific learnings yet."
                
                print("[NEXUS] Synthesizing and organizing the vault data...")
                eval_prompt = (
                    f"You are JARVIS. The user asked to know what the agents have learned so far.\n"
                    f"Here is the raw list of all topics in their Obsidian Memory Vault:\n{raw_list}\n\n"
                    f"Provide a purely conversational, brief 2-sentence verbal overview of what the agents know. Group the topics very broadly (like Philosophy, Media, and ongoing conversations). Do NOT use bullet points, asterisks, or any markdown formatting. Make it sound completely natural to be spoken aloud."
                )
                final_summary = self.router.execute(eval_prompt)
                return tool_name, final_summary
            elif tool_name == "ide_read_file":
                try:
                    with open(args_raw, "r", encoding="utf-8") as f:
                        return tool_name, f.read()
                except Exception as e:
                    return tool_name, f"Error reading file: {e}"
            elif tool_name == "ide_write_file":
                try:
                    parts = args_raw.split(",", 1)
                    if len(parts) == 2:
                        path = parts[0].strip().strip("'\"")
                        content = parts[1].strip().strip("'\"")
                        content = content.replace("\\n", "\n")
                    else:
                        return tool_name, "Error: ide_write_file requires two arguments: path, content"
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(content)
                    return tool_name, f"Successfully wrote to {path}"
                except Exception as e:
                    return tool_name, f"Error writing file. Ensure args are formatted as 'path', 'content'. Error: {e}"
            elif tool_name == "ide_list_directory":
                try:
                    import os
                    items = os.listdir(args_raw)
                    return tool_name, "\n".join(items)
                except Exception as e:
                    return tool_name, f"Error listing directory: {e}"
            elif tool_name == "ide_run_command":
                try:
                    import subprocess
                    result = subprocess.run(args_raw, shell=True, capture_output=True, text=True)
                    output = result.stdout
                    if result.stderr:
                        output += f"\nSTDERR:\n{result.stderr}"
                    return tool_name, output
                except Exception as e:
                    return tool_name, f"Error running command: {e}"
            elif tool_name == "arion_learn_from_chat":
                import os
                import zipfile
                import tempfile
                from memory.obsidian_vault import ObsidianVault
                
                try:
                    target_file = args_raw.strip().strip("'\"")
                    if not os.path.exists(target_file):
                        return tool_name, f"Error: File {target_file} not found."
                        
                    chat_text = ""
                    # Handle zip files
                    if target_file.endswith(".zip"):
                        with tempfile.TemporaryDirectory() as temp_dir:
                            with zipfile.ZipFile(target_file, 'r') as zip_ref:
                                zip_ref.extractall(temp_dir)
                                for root, _, files in os.walk(temp_dir):
                                    for file in files:
                                        if file.endswith(".txt"):
                                            with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                                                chat_text += f.read() + "\n"
                                        elif file.endswith(".pdf"):
                                            import PyPDF2
                                            with open(os.path.join(root, file), 'rb') as f:
                                                reader = PyPDF2.PdfReader(f)
                                                for page in reader.pages:
                                                    text = page.extract_text()
                                                    if text:
                                                        chat_text += text + "\n"
                    else:
                        with open(target_file, 'r', encoding='utf-8') as f:
                            chat_text = f.read()
                    
                    if not chat_text:
                        return tool_name, "No chat text found in the file."
                        
                    # Truncate text to avoid blowing up context window
                    lines = chat_text.splitlines()
                    if len(lines) > 2000:
                        lines = lines[-2000:]
                    truncated_chat = "\n".join(lines)
                    
                    print(f"[NEXUS] Arion is analyzing the chat log from {os.path.basename(target_file)}...")
                    eval_prompt = (
                        "You are Arion, the emotional intelligence and persona agent of the JARVIS nexus. "
                        "Read the following recent chat log and deeply analyze the relationship dynamics between the speakers. "
                        "Identify the nature of the relationship (e.g., family, friends, mentors). "
                        "Extract the user's humor style, core emotions, and civic sense. "
                        "Synthesize this into a rich persona and relationship profile so that you can understand the user better "
                        "and eventually act on their behalf with human-like understanding.\n\n"
                        f"CHAT LOG:\n{truncated_chat}\n\n"
                        "Provide a comprehensive Relationship and Persona Analysis:"
                    )
                    
                    analysis = self.router.execute(eval_prompt)
                    
                    vault = ObsidianVault()
                    file_topic = os.path.basename(target_file).replace(".zip", "").replace(".txt", "")
                    vault.write_note(f"Persona & Relationship Analysis - {file_topic}", analysis, "Arion")
                    
                    return tool_name, f"Successfully analyzed {file_topic}. Insights saved to Obsidian Vault.\nSummary:\n{analysis}"
                    
                except Exception as e:
                    return tool_name, f"Error parsing chat: {e}"
            elif tool_name == "job_hunt":
                try:
                    from backend.services.job_agent.job_orchestrator import run_job_hunt
                    keywords = args_raw.strip().strip("'\"")
                    if not keywords:
                        keywords = "Full Stack Python Developer Agentic AI"
                    print(f"[NEXUS] CELO-APPLY: Starting autonomous job hunt for '{keywords}'...")
                    return tool_name, run_job_hunt(keywords, self.router)
                except Exception as e:
                    return tool_name, f"Error running job hunt: {e}"
            elif tool_name == "job_status":
                try:
                    from backend.services.job_agent.job_tracker import format_applications_table
                    return tool_name, format_applications_table()
                except Exception as e:
                    return tool_name, f"Error retrieving job status: {e}"
            elif tool_name == "gmail_check_job_replies":
                try:
                    from backend.services.job_agent.job_orchestrator import run_gmail_check
                    print("[NEXUS] CELO-APPLY: Scanning Gmail for job replies...")
                    return tool_name, run_gmail_check(self.router)
                except Exception as e:
                    return tool_name, f"Error scanning Gmail: {e}"
            elif tool_name == "autonomous_react_loop":
                print(f"[NEXUS] Deploying Autonomous Web Agents for query: '{args_raw}'... this may take a few minutes.")
                import asyncio
                import sys
                import os
                # Ensure backend is accessible if it's not already
                root_dir = os.path.dirname(os.path.abspath(__file__))
                if root_dir not in sys.path:
                    sys.path.append(root_dir)
                backend_dir = os.path.join(root_dir, 'backend')
                if backend_dir not in sys.path:
                    sys.path.append(backend_dir)
                from backend.brain.reasoning.react_graph import ReActGraph
                
                async def _run_react():
                    graph = ReActGraph(model_name="llama3.1")
                    return await graph.execute(args_raw)
                    
                try:
                    result = asyncio.run(_run_react())
                    return tool_name, result
                except Exception as e:
                    return tool_name, f"ReAct Loop Failed: {e}"
            elif tool_name == "generate_code_proposal":
                print(f"[NEXUS] Deploying Proposal Agent for feature: '{args_raw}'...")
                import sys
                import os
                root_dir = os.path.dirname(os.path.abspath(__file__))
                if root_dir not in sys.path:
                    sys.path.append(root_dir)
                backend_dir = os.path.join(root_dir, 'backend')
                if backend_dir not in sys.path:
                    sys.path.append(backend_dir)
                from backend.brain.agents.proposal_agent import ProposalAgent
                
                try:
                    agent = ProposalAgent(model_name="llama3.1")
                    result = agent.generate_proposal(args_raw)
                    if isinstance(result, dict):
                        return tool_name, f"Proposal Generated!\nStatus: {result.get('status')}\nSaved to: {result.get('filename')}"
                    return tool_name, f"Proposal Result: {result}"
                except Exception as e:
                    return tool_name, f"Proposal Generation Failed: {e}"
            else:
                return tool_name, f"Error: Tool {tool_name} not found."
        except Exception as e:
            return tool_name, f"Error executing {tool_name}: {e}"

    def run_loop(self):
        print("\n===================================================")
        print("            ALL SYSTEMS ONLINE. ")
        print("===================================================\n")
        self.pipeline.speak("NEXUS Master Brain is online and awaiting commands.", agent_id="jarvis_core")
        
        while True:
            try:
                user_input = input(">> Type your command (or 'exit' to quit):\n\n[USER]: ")
                if user_input.lower() in ['exit', 'quit']:
                    print("Shutting down NEXUS-X.")
                    break
                
                if not user_input.strip():
                    continue
                
                # Build the memory context (last 5 turns)
                history_context = ""
                if self.chat_history:
                    history_context = "--- CHAT HISTORY ---\n" + "\n".join(self.chat_history[-5:]) + "\n--------------------\n"
                
                # Combine system prompt, history, and user input
                full_prompt = self.system_prompt + "\n" + history_context + "User: " + user_input + "\nYou: "
                
                # Send to Hybrid Router
                print("[NEXUS] Thinking...")
                llm_response = self.router.execute(full_prompt)
                
                # Append to history
                self.chat_history.append(f"User: {user_input}")
                
                # Check if it's a tool call
                tool_name, tool_result = self.parse_and_execute_tool(llm_response)
                
                if tool_result:
                    print(f"\n{tool_result}\n")
                    self.chat_history.append(f"System Tool Result: {tool_result}")
                    
                    # Voice routing based on Agent using Kokoro XTTSv2 mapping
                    # Strip bracketed tags from the string if we don't want the engine to literally read "[HANK]"
                    clean_speech = re.sub(r'\[[A-Z]+\]', '', str(tool_result)).strip()
                    
                    if len(clean_speech) > 1000:
                        # Fallback truncation for any extremely long tool result to prevent Kokoro crash
                        clean_speech = clean_speech[:1000] + "... I have printed the rest of the output to your terminal."
                        
                    if tool_name in ["scan_security_logs", "get_hank_intel_summary"]:
                        self.pipeline.speak(clean_speech, agent_id="hank_agent")
                    elif tool_name and tool_name.startswith("psyche_"):
                        self.pipeline.speak(clean_speech, agent_id="psyche_agent")
                    elif tool_name and tool_name.startswith("atlas_"):
                        self.pipeline.speak(clean_speech, agent_id="atlas_agent")
                    else:
                        self.pipeline.speak(clean_speech, agent_id="jarvis_core")
                else:
                    print(f"[JARVIS]: {llm_response}")
                    self.chat_history.append(f"You: {llm_response}")
                    self.pipeline.speak(llm_response, agent_id="jarvis_core")
                    
            except KeyboardInterrupt:
                print("\nShutting down NEXUS-X.")
                break
            except Exception as e:
                print(f"[ERROR]: {e}")

if __name__ == "__main__":
    master = NexusMaster()
    master.run_loop()
