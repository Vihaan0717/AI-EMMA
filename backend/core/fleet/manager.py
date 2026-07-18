import time
import json
import logging
from typing import Dict, Any, Tuple, List
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from core.fleet.personas import FleetPersonas
from core.fleet.local_db import fleet_db
from core.fleet.reward_model import reward_model
from core.fleet.react_engine import react_engine, ReActTrace
from core.fleet.swarm_coordinator import swarm_coordinator
from core.fleet.agentic_tools import agentic_tool_registry
from core.fleet.knowledge_graph import knowledge_graph
from config.system_config import JarvisConfig
from services.hand_service import HandService
import re

logger = logging.getLogger("FleetManager")

class FleetManager:
    """
    Orchestrates the Peer-Review Loop between local agents.
    Handles Doer generation, Critic review, and Learning updates.
    """
    
    def __init__(self):
        self.base_url = JarvisConfig.OLLAMA_BASE_URL
        self.personas = FleetPersonas()
        self.web = None
        self.hands = HandService()
        self.habit_cache = {} # Task Signature -> (Preferred Agent, Confidence)
        self.active_brief = None
        self.react_engine = react_engine
        self.swarm = swarm_coordinator

    def set_web_brain(self, web_brain):
        self.web = web_brain

    def set_ai_engine(self, ai_engine):
        """Set the AI engine and propagate to sub-systems."""
        self.ai_engine = ai_engine
        self.swarm.set_ai_engine(ai_engine)
        self.swarm.set_personas(self.personas)
        knowledge_graph.set_ai_engine(ai_engine)

    async def apply_mission_brief(self, brief):
        """Applies a new mission brief from the A14 Executive Layer."""
        self.active_brief = brief
        logger.info(f"Fleet: Acknowledged {brief.mode.value.upper()} Mission. Target Lead: {brief.lead_agent}")
        # Here we could proactively pre-load models if needed

    def _get_llm(self, agent_id: str):
        persona = self.personas.get_persona(agent_id)
        return ChatOllama(
            model=persona["model"],
            temperature=persona["temperature"],
            base_url=self.base_url
        )

    def _reduce_tokens(self, text: str) -> str:
        """Compresses content to achieve 90%+ token reduction using line filtration and sentence pruning."""
        if not text:
            return ""
        lines = text.split("\n")
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            # Skip short lines, generic markup, navigation headers
            if len(line) < 30 or any(word in line.lower() for word in ["navigation", "menu", "footer", "privacy policy", "copyright"]):
                continue
            cleaned_lines.append(line)
        
        # Take at most top 10% of lines or a capped number of key sentences to guarantee 90%+ reduction
        subset_len = max(1, len(cleaned_lines) // 10)
        reduced = "\n".join(cleaned_lines[:subset_len])
        return reduced

    async def _self_reflect_and_improve(self, agent_id: str, task: str, response: str, score: float, feedback: str):
        """Allows the agent to compare current output with history, find what they lack, and update skills/methods."""
        corrections = fleet_db.get_recent_corrections(agent_id, limit=5)
        reflection_prompt = f"""
Agent: {agent_id}
Current Task: {task}
Current Response: {response}
Current Score: {score}
Critic Feedback: {feedback}

Previous Correction Notes:
{chr(10).join([f'- {c[0]}: {c[1]}' for c in corrections])}

Compare your current response with the critic feedback and previous corrections. Identify what you lack (e.g. wrong tone, logic bugs, slang errors) and formulate a concrete improvement strategy/delta method to update your approach.
Return a single sentence instruction for your future self.
"""
        ai_engine = getattr(self, 'ai_engine', None)
        try:
            if ai_engine:
                reflection = await ai_engine.generate(prompt=reflection_prompt, system="You are an autonomous self-reflection system.", temperature=0.2)
            else:
                reflection = "Analyze task requirements more carefully and stick to specific persona guidelines."
            
            fleet_db.add_correction_note(agent_id, "Self-Reflection", reflection)
            logger.info(f"Fleet: Agent {agent_id} completed self-reflection. Strategy updated: {reflection}")
        except Exception as e:
            logger.warning(f"Self-reflection failed for {agent_id}: {e}")

    async def execute_task(self, task: str, doer_id: str = "hank", language: str = "english") -> Dict[str, Any]:
        """
        Executes a task using the Peer-Review Loop with sequential agent collaboration.
        """
        start_time = time.time()
        
        # 0. LINGUISTIC Phase (Constraints)
        lang_rules = {
            "telugu": "\n[STRICT RULE] Respond in TELUGU SCRIPT ONLY. NO ENGLISH.",
            "tenglish": "\n[STRICT RULE] Respond in TENGLISH (Mixed Telugu+English). NO TELUGU SCRIPT. NO TRANSLATIONS.",
            "english": "\n[STRICT RULE] Respond in ENGLISH ONLY."
        }.get(language, "")
        
        # 0. MISSION Phase (Executive Control)
        if not doer_id and self.active_brief:
            doer_id = self.active_brief.lead_agent
        
        # 0. HABIT Phase
        task_sig = self._generate_task_sig(task)
        if not doer_id: 
            doer_id = self._check_habits(task_sig) or "hank"
            logger.info(f"Fleet: Habit cache selected '{doer_id}' for '{task_sig}'")

        # 0.5 GREETING CHECK
        tech_keywords = ["code", "java", "python", "script", "how to", "debug", "math", "search", "who", "what"]
        has_tech_intent = any(tk in task.lower() for tk in tech_keywords)
        
        is_greeting = any(task.lower().strip() == g or task.lower().startswith(g + " ") for g in ["hi", "hello", "hey", "namaste", "namaskaram", "good morning", "good evening"])
        is_greeting = is_greeting and not has_tech_intent
        is_telugu_greeting = any(task.lower().strip() == g or task.lower().startswith(g + " ") for g in ["nuvvu ela", "ela unnav", "chasthunav", "em chesthunnav", "bagunnava"])
        is_telugu_greeting = is_telugu_greeting and not has_tech_intent
        
        chatter_phrases = [
            "how are you", "how r u", "how are u", "what's up", "wassup", "whats up",
            "you okay", "you ok", "u ok", "emo unnav", "em chesthunnav", "bagunnava"
        ]
        is_chatter = any(phrase in task.lower() for phrase in chatter_phrases) and not has_tech_intent
        is_skip_research = is_greeting or is_telugu_greeting or is_chatter
        
        # Define sequential agent chain: Primary Doer -> Researcher (Atlas) -> Stylist (Cleo)
        agent_chain = [doer_id]
        if not is_skip_research:
            if doer_id != "atlas":
                agent_chain.append("atlas")
            if doer_id != "cleo":
                agent_chain.append("cleo")

        logger.info(f"Fleet: Executing collaborative sequential pipeline: {agent_chain}")
        
        intermediate_output = ""
        ai_engine = getattr(self, 'ai_engine', None)
        ltm_recalled_data = []
        
        for idx, current_agent in enumerate(agent_chain):
            logger.info(f"Fleet: Agent '{current_agent}' (Stage {idx+1}/{len(agent_chain)}) is processing...")
            persona = self.personas.get_persona(current_agent)
            
            # Fetch and scrape from the internet using agent's skills POV (no API keys)
            web_context = ""
            if persona.get("can_research") and self.web and not is_skip_research:
                role = persona.get("role", "Specialist")
                pov_query = f"{role} POV on {task}"
                logger.info(f"Fleet: {current_agent} performing skills POV scraping for query: '{pov_query}'")
                research_data = await self.web.learn(pov_query)
                if research_data:
                    raw_content = ""
                    if research_data.get('source') == 'wikipedia':
                        raw_content = research_data.get('content', '')
                    elif 'documents' in research_data:
                        raw_content = "\n\n".join([d.get('text', '') for d in research_data['documents']])
                    
                    # 90% token reduction analysis
                    reduced_content = self._reduce_tokens(raw_content)
                    logger.info(f"Fleet: Token reduction completed. Compressed text length: {len(reduced_content)} characters.")
                    web_context = f"\n\n[WEB SCRAPING POV - {role}]:\n{reduced_content}"

            # Check LTM (Long Term Memory)
            ltm_context = ""
            try:
                # 1. Check Knowledge Graph for semantic matches
                kg_results = await knowledge_graph.semantic_search(task, top_k=3, threshold=0.5)
                if kg_results:
                    kg_text = "\n".join([f"[{r['subject']}] --({r['predicate']})--> [{r['object']}]" for r in kg_results])
                    ltm_context += f"\n\n[KNOWLEDGE GRAPH CONTEXT]:\n{kg_text}"

                # 2. Check traditional memory manager
                if hasattr(self, 'memory_manager') and self.memory_manager:
                    ltm_recalled = await self.memory_manager.recall(task, limit=3)
                    if ltm_recalled:
                        ltm_recalled_data.extend(ltm_recalled)
                        ltm_context += f"\n\n[LTM RECALL]: " + " | ".join([m.get("content", "") for m in ltm_recalled])
            except Exception as e:
                logger.warning(f"Failed to check LTM/KG: {e}")

            # Prepare inputs with previous agent's response passed on
            corrections = fleet_db.get_recent_corrections(current_agent)
            correction_context = "\n".join([f"- {c[0]}: {c[1]}" for c in corrections])
            
            system_prompt = persona["system_prompt"] + f"\n\nLessons Learned:\n{correction_context}" + web_context + ltm_context + lang_rules
            
            combined_prompt = task
            if intermediate_output:
                combined_prompt = f"Original Task: {task}\n\nPrevious Agent's Output: {intermediate_output}\n\nEnhance, correct, or format the previous output using your skill POV."

            # ══════════════════════════════════════════════════════════
            # ReAct Execution Loop (replaces old linear generation)
            # ══════════════════════════════════════════════════════════
            if ai_engine:
                logger.info(f"Fleet: {current_agent} entering ReAct loop (agentic mode)")
                react_trace = await self.react_engine.execute(
                    agent_id=current_agent,
                    task=combined_prompt,
                    system_prompt=system_prompt,
                    ai_engine=ai_engine,
                    temperature=persona.get("temperature", 0.7),
                    context=web_context + ltm_context
                )
                last_response = react_trace.final_answer
                logger.info(
                    f"Fleet: {current_agent} ReAct complete — "
                    f"thoughts={react_trace.total_thoughts}, "
                    f"tools={react_trace.total_tool_calls}, "
                    f"confidence={react_trace.self_confidence}"
                )
            else:
                # Fallback: legacy single-shot generation for local Ollama models
                logger.info(f"Fleet: {current_agent} using legacy single-shot (no AI engine)")
                llm = self._get_llm(current_agent)
                prompt_tpl = ChatPromptTemplate.from_messages([
                    ("system", system_prompt),
                    ("user", "{input}")
                ])
                chain = prompt_tpl | llm
                res = await chain.ainvoke({"input": combined_prompt})
                last_response = res.content
                react_trace = None
                
            # Execute any legacy [ACTION] blocks found in response
            action_results = self._execute_hand_actions(last_response)
            if action_results:
                last_response += f"\n\n[Hand Results]: {', '.join(action_results)}"

            intermediate_output = last_response

        response_text = intermediate_output

        # 2. OBJECTIVE Review (Reward Model)
        reward_score = reward_model.score(task, response_text)
        
        # 3. CRITIC Review (Subjective Feedback)
        if ai_engine:
            critic_persona = self.personas.get_persona("critic")
            critic_res = await ai_engine.generate(
                prompt=f"Task: {task}\n\nResponse to Review: {response_text}\n\nEvaluate and return JSON with 'score' (0-100) and 'feedback' (string).",
                system=critic_persona["system_prompt"],
                temperature=0.1
            )
            critic_content = critic_res
        else:
            critic_llm = self._get_llm("critic")
            critic_persona = self.personas.get_persona("critic")
            critic_prompt = ChatPromptTemplate.from_messages([
                ("system", critic_persona["system_prompt"]),
                ("user", "Task: {task_text}\n\nResponse to Review: {response_text}\n\nEvaluate and return JSON with 'score' (0-100) and 'feedback' (string).")
            ])
            critic_chain = critic_prompt | critic_llm
            critic_response = await critic_chain.ainvoke({"task_text": task, "response_text": response_text})
            critic_content = critic_response.content
        
        # Parse Critic feedback
        try:
            eval_data = self._parse_critic_json(critic_content)
            critic_score = eval_data.get("score", 80)
            feedback = eval_data.get("feedback", "No specific feedback.")
        except Exception as e:
            logger.warning(f"Failed to parse critic feedback: {e}")
            critic_score = 70
            feedback = critic_content
 
        final_score = (reward_score + critic_score) / 2

        # Apply ReAct quality bonus if we have a trace
        if 'react_trace' in dir() and react_trace:
            final_score = self.react_engine.compute_quality_score(react_trace, final_score)

        latency = (time.time() - start_time) * 1000
        tokens = len(response_text.split())
        
        # 4. GROWTH & REFLECTION LOGIC
        fleet_db.log_interaction(doer_id, task, tokens, latency, final_score, feedback)
        
        # Store in LTM if scored >= 80%
        if final_score >= 80:
            try:
                if hasattr(self, 'memory_manager') and self.memory_manager:
                    await self.memory_manager.remember(
                        content=response_text,
                        importance=final_score / 100.0,
                        metadata={"task": task, "agent": doer_id, "critic_score": final_score}
                    )
                    logger.info("NEXUS LTM: Ingested high scoring response (>=80%) to LTM.")
            except Exception as e:
                logger.warning(f"Failed to store in LTM: {e}")


        # Trigger self-reflection and update methods/approaches for the primary doer
        await self._self_reflect_and_improve(doer_id, task, response_text, final_score, feedback)
        
        if final_score < 80:
            fleet_db.add_correction_note(doer_id, task[:50], feedback)
            logger.info(f"Fleet: {doer_id} failed growth step (Score: {final_score:.1f}). Lesson recorded.")

        self._update_habits(task_sig, doer_id, final_score)


        # ── POST-GENERATION: Language Validation & Hindi Guard ──────────────
        HINDI_MARKERS = ["hai ", "kaa ", "mein ", "aur ", "yeh ", "ek ", "voh ", "toh ", "bhi ", "hain "]
        hindi_count = sum(1 for m in HINDI_MARKERS if m in response_text.lower())
        if hindi_count >= 2 and ai_engine:
            logger.warning(f"Fleet: Hindi detected in {doer_id} response! Re-generating...")
            # Language enforcement rules injected into system prompt
            lang_rules = ""
            if language == "tenglish":
                lang_rules = (
                    "\n\n[CRITICAL LANGUAGE RULE] RESPOND IN TENGLISH (Telugu+English mixed). "
                    "Example: 'Boss, adi chala famous book ra! APJ Abdul Kalam gurinchi...' "
                    "ABSOLUTELY NO HINDI. NO TRANSLATIONS IN BRACKETS. NO PRONUNCIATION GUIDES."
                )
            elif language == "telugu":
                lang_rules = (
                    "\n\n[CRITICAL LANGUAGE RULE] RESPOND IN TELUGU SCRIPT ONLY. "
                    "ABSOLUTELY NO HINDI. NO ENGLISH TRANSLATIONS IN BRACKETS."
                )
            elif language == "english":
                lang_rules = (
                    "\n\n[CRITICAL LANGUAGE RULE] RESPOND IN ENGLISH ONLY. "
                    "NO HINDI. NO TRANSLATIONS IN BRACKETS."
                )
            emergency_prompt = (
                f"RESPOND TO THIS IN {language.upper()} ONLY. NO HINDI WHATSOEVER.\n\n"
                f"Input: {task}\n\nYour previous response was in Hindi which is WRONG."
            )
            response_text = await ai_engine.generate(
                prompt=emergency_prompt,
                system=doer_persona["system_prompt"] + lang_rules,
                temperature=0.4
            )
        
        # 5. ACTION Phase (Executes 'Hand' commands if any)
        action_results = self._execute_hand_actions(response_text)
        if action_results:
            response_text += f"\n\n[Hand Results]: {', '.join(action_results)}"

        return {
            "agent": doer_id,
            "response": response_text,
            "score": final_score,
            "feedback": feedback,
            "latency_ms": latency
        }

    def _execute_hand_actions(self, text: str) -> List[str]:
        """Parses [ACTION] blocks and executes them via HandService and DOMEService."""
        # Regex to find [ACTION] ... [/ACTION]
        action_pattern = r"\[ACTION\](.*?)\[/ACTION\]"
        matches = re.findall(action_pattern, text, re.DOTALL)
        
        results = []
        for match in matches:
            try:
                # Basic parsing (we expect 'key: value' format)
                action_data = {}
                for line in match.split(','):
                    if ':' in line:
                        k, v = line.split(':', 1)
                        action_data[k.strip().lower()] = v.strip().strip("'").strip('"')
                
                a_type = action_data.get("type")
                target = action_data.get("target")
                content = action_data.get("content")
                
                logger.info(f"Fleet: HandAction detected -> {a_type} on {target}")
                
                if a_type == "maximize_window":
                    results.append(self.hands.maximize_window(target))
                elif a_type == "close_window":
                    results.append(self.hands.close_window(target))
                elif a_type == "open_app":
                    results.append(self.hands.open_app(target))
                elif a_type == "run_cmd":
                    results.append(self.hands.run_cmd(target))
                elif a_type == "uninstall_app":
                    results.append(self.hands.uninstall_app(target))
                elif a_type.startswith("file_"):
                    results.append(self.hands.perform_file_crud(a_type.split('_')[1], target, content))
                elif a_type == "type_text":
                    results.append(self.hands.type_text(target)) # In this case target is the text
                elif a_type == "inspect_ui":
                    from services.dome_service import DOMEService
                    dome = DOMEService()
                    hierarchy = dome.get_window_hierarchy()
                    results.append(f"DOME: Found {len(hierarchy)} top-level windows.")
                elif a_type == "click_element":
                    from services.dome_service import DOMEService
                    dome = DOMEService()
                    element = dome.find_element_by_title(target)
                    if element:
                        self.hands.maximize_window(element["title"])
                        rect = element["rect"]
                        cx = rect["left"] + rect["width"] // 2
                        cy = rect["top"] + rect["height"] // 2
                        if self.hands._validate_coordinates(cx, cy):
                            import pyautogui
                            pyautogui.click(cx, cy)
                            results.append(f"DOME: Clicked element '{target}' at ({cx}, {cy})")
                        else:
                            results.append(f"DOME: Element coordinates ({cx}, {cy}) out of bounds.")
                    else:
                        results.append(f"DOME: Element '{target}' not found.")
                else:
                    results.append(f"Unknown action type: {a_type}")
            except Exception as e:
                results.append(f"Action error: {e}")
                
        return results

    async def trigger_root_cause_analysis(self, task: str, failed_response: str, user_feedback: str) -> str:
        """
        Invokes a 'Master Critic' (Gemini) to perform a deep post-mortem on a failed task.
        Extracts the 'Correct Method' and saves it to the fleet database.
        """
        logger.info(f"Fleet: Commencing Deep Root Cause Analysis for task: '{task[:50]}...'")
        
        analysis_prompt = f"""
You are the NEXUS-X Master Critic. A task has failed to satisfy the user.
TASK: {task}
FAILED RESPONSE: {failed_response}
USER FEEDBACK: {user_feedback}

ANALYSIS REQUIRED:
1. What was the specific failure? (e.g., misunderstood intent, technical error, wrong tone, language mistake)
2. What would be the PERFECT response?
3. What is the GENERAL RULE or METHOD to follow for this type of task in the future?

OUTPUT FORMAT:
Return a concise 'Lesson Learned' that can be stored in the agent's memory.
Example: 'For Hyderabad slang requests, always include at least one "baigan" or "hau" to maintain authenticity.'
"""
        
        # Use Gemini (AIEngine fallback or direct) for high-level reasoning
        master_critic_response = await self.ai_engine.generate(
            prompt=analysis_prompt,
            system="You are an expert AI behavior analyst.",
            temperature=0.2
        )
        
        # Save the lesson to all relevant agents or the doer specifically
        # For now, we save it as a correction note in the fleet DB
        # Identify the doer (this information should be passed or inferred)
        # Assuming we know the doer_id from the context of the failure
        # For this implementation, we'll return the lesson to be handled by the caller
        
        return master_critic_response

    async def scholar_peer_review(self, phrase: str, meaning: str) -> Dict[str, Any]:
        """
        Special Collaborative Loop for Scholar Mode (A10-A11).
        Path: Cleo (Creative) -> Hank (Logic) -> Atlas (Verification) -> Critic (Audit)
        """
        logger.info(f"Scholar Loop: Peer-reviewing '{phrase}'...")
        
        # 1. Cleo: Generate Creative Context
        cleo_res = await self.execute_task(f"Create a casual Hyderabad-style sentence using '{phrase}' (meaning {meaning}).", doer_id="cleo")
        sentence = cleo_res["response"]
        
        # 2. Hank: Check Logic/Structure
        hank_res = await self.execute_task(f"Is this sentence grammatically and logically sound for Hyderabad slang? '{sentence}'", doer_id="hank")
        
        # 3. Atlas: Verify via Gemini (Mocked here as self.web + AI check)
        atlas_res = await self.execute_task(f"Verify if the slang '{phrase}' fits the cultural context of: '{sentence}'", doer_id="atlas")
        
        # 4. Critic: Final Verdict
        critic_res = await self.execute_task(
            f"Verdict for phrase '{phrase}' usage.\nSentence: {sentence}\nFeedback from Hank: {hank_res['response']}\nFeedback from Atlas: {atlas_res['response']}",
            doer_id="critic"
        )
        
        return {
            "phrase": phrase,
            "final_usage": sentence,
            "score": critic_res["score"],
            "feedback": critic_res["feedback"]
        }

    def _parse_critic_json(self, content: str) -> Dict:
        # Simple JSON extraction
        try:
            start = content.find("{")
            end = content.rfind("}") + 1
            if start != -1 and end != -1:
                return json.loads(content[start:end])
        except:
            pass
        return {}

    def _generate_task_sig(self, task: str) -> str:
        """Categorizes task into a signature for habit learning."""
        task_l = task.lower()
        # Simple rule-based categorization
        if any(w in task_l for w in ["music", "song", "note", "chord", "melody", "midi", "piano", "guitar"]): return "music"
        if any(w in task_l for w in ["movie", "film", "cinema", "director", "actor"]): return "movies"
        if any(w in task_l for w in ["biology", "physics", "chemistry", "science", "cell", "atom", "molecule", "study guide", "research paper"]): return "academic"
        if any(w in task_l for w in ["python", "code", "debug", "script", "java", "c++", "react", "html", "css", "programming"]): return "coding"
        if any(w in task_l for w in ["who", "what", "where", "latest", "news", "research", "verify"]): return "research"
        if any(w in task_l for w in ["write", "story", "poem", "essay", "script", "creative"]): return "creative"
        if any(w in task_l for w in ["math", "calculate", "solve", "equation"]): return "math"
        if any(w in task_l for w in ["data", "sales", "analytics", "roi", "trend", "chart", "graph", "statistics"]): return "analytics"
        if any(w in task_l for w in ["security", "vulnerability", "threat", "audit", "firewall", "breach", "malware", "phishing", "ssl", "encrypt", "cipher", "exploit", "cve", "stride", "owasp", "pentest", "hardening", "incident"]): return "security"
        return "general"

    def _check_habits(self, sig: str) -> str:
        if sig in self.habit_cache:
            agent, conf = self.habit_cache[sig]
            if conf > 0.7: return agent
        # Default routing if no habit established
        if sig in ["music", "movies", "academic"]: return "cosmos"
        if sig == "analytics": return "atlas_x"
        if sig == "security": return "mythos"
        return None

    def _update_habits(self, sig: str, agent: str, score: float):
        """Reinforce (LTP) or weaken (LTD) habits based on score."""
        current_agent, current_conf = self.habit_cache.get(sig, (agent, 0.5))
        
        if agent == current_agent:
            # LTP: Strengthen existing habit
            new_conf = min(1.0, current_conf + (score - 70) / 100.0)
        else:
            # Potential new habit competing
            if score > 85: # Significant improvement
                new_conf = 0.6
                current_agent = agent
            else:
                new_conf = current_conf * 0.9 # Weaken existing habit slightly
        
        self.habit_cache[sig] = (current_agent, new_conf)

# Global instance
fleet_manager = FleetManager()
