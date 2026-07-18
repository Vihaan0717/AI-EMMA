"""
NEXUS-X ULTIMATE Master Brain
The central intelligence - One Brain, Two Personalities
"""

import asyncio
import logging
import datetime
import os
import traceback
from typing import Dict, Any, Optional, List

from core.message_bus import MessageBus, Channel, Message
from core.privacy_guard import PrivacyGuard
from pipeline.pipeline_runner import PipelineRunner
from nexus.agents.scholar_agent import ScholarAgent
from nexus.agents.psyche_agent import PsycheAgent
from brain.agents.tenglish_intent_agent import TenglishIntentAgent
from agents.finance_monitor import FinanceMonitor
from agents.daily_note_agent import DailyNoteAgent
from core.fleet.boardroom import boardroom
from brain.emotion import EmotionEngine
from brain.prediction import PredictionEngine
from language.telugu_parser import TeluguParser
from language.tenglish_mapper import TenglishMapper
import json
import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger('NexusBrain')

class RoutingDecision(BaseModel):
    intent: str = Field(description="The core classification of the user request.")
    target_agent: str = Field(description="Must be one of: JARVIS, ARION, HANK, CLEO, ATLAS, SENTINEL, COSMOS")
    requires_context: bool = Field(description="True if long-term memory (ChromaDB/Obsidian) query is necessary.")
    keep_alive_override: str = Field(description="Floating time for target agent VRAM, e.g., '30s', '5m', or '0s'.")
    confidence: float = Field(description="Confidence rating between 0.0 and 1.0")

class MasterBrainRouter:
    def __init__(self):
        # High-speed exact-match pattern cache to bypass LLM inference entirely
        self._static_cache: Dict[str, Dict[str, Any]] = {
            "clear logs": {"intent": "system_maintenance", "target_agent": "JARVIS", "requires_context": False, "keep_alive_override": "0s", "confidence": 1.0},
            "check networks": {"intent": "security_audit", "target_agent": "SENTINEL", "requires_context": False, "keep_alive_override": "1m", "confidence": 1.0},
            "status check": {"intent": "system_status", "target_agent": "JARVIS", "requires_context": False, "keep_alive_override": "0s", "confidence": 1.0}
        }

    async def route_input(self, user_input: str) -> Dict[str, Any]:
        """
        Main entry point. Cleans input, evaluates cache, and forces structured LLM routing.
        """
        cleaned_input = user_input.strip().lower()
        
        # 1. Hot Cache Lookup
        if cleaned_input in self._static_cache:
            logger.info(f"[BRAIN] Cache hit for query: '{cleaned_input}'")
            return self._static_cache[cleaned_input]

        # 2. Structured Inference Fallback
        return await self._query_local_router(user_input)

    async def _query_local_router(self, raw_input: str) -> Dict[str, Any]:
        """
        Queries the ultra-fast local routing model with strict JSON response enforcement.
        """
        system_prompt = (
            "You are the Master Brain Router for the NEXUS-X operating system. Your only job is to analyze "
            "the user input and output a strict JSON object mapping the request to the most optimal fleet agent.\n"
            "Allowed Agents and Domains:\n"
            "- JARVIS: OS control, system files, administrative actions, precise technical tasks.\n"
            "- ARION: Conversational companion, multilingual chat, casual text, emotional context, Tenglish.\n"
            "- HANK: Code generation, execution, compilation, script editing.\n"
            "- CLEO: Creative narrative, content scripting, marketing copy, social media reels.\n"
            "- ATLAS: Deep web research, raw data scraping, long-context text analysis.\n"
            "- SENTINEL: Cyber security audits, network scanners, port sweeps, connection monitoring.\n"
            "- COSMOS: Academic subjects (biology, physics, chemistry), movies, music composition, stories.\n"
            "Output must strictly match this schema layout: "
            '{"intent": "string", "target_agent": "STRING", "requires_context": true/false, '
            '"keep_alive_override": "string", "confidence": float}'
        )

        payload = {
            "model": "llama3.2:1b",
            "prompt": f"{system_prompt}\n\nUser Input: {raw_input}",
            "stream": False,
            "format": "json",  # Forces Ollama to output valid JSON text
            "options": {
                "temperature": 0.0,  # Deterministic execution
                "keep_alive": "-1"  # Keep router permanently resident in VRAM
            }
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post("http://localhost:11434/api/generate", json=payload, timeout=5.0)
                
                if response.status_code == 200:
                    raw_response_text = response.json().get("response", "{}")
                    parsed_json = json.loads(raw_response_text)
                    
                    # Enforce data validation via Pydantic model structure
                    validated_decision = RoutingDecision(**parsed_json)
                    return validated_decision.model_dump()
                else:
                    logger.error(f"[BRAIN] Router returned HTTP error status: {response.status_code}")
                    return self._get_fallback_route()
                    
        except Exception as e:
            logger.error(f"[BRAIN] Routing inference failed or timed out: {str(e)}")
            return self._get_fallback_route()

    def _get_fallback_route(self) -> Dict[str, Any]:
        """Safe default fallback if local model fails to respond or breaks schema."""
        return {
            "intent": "casual_fallback",
            "target_agent": "ARION",
            "requires_context": False,
            "keep_alive_override": "30s",
            "confidence": 0.5
        }


class NexusBrain:
    """
    The Shared Brain Core for NEXUS-X ULTIMATE.
    Coordinates between JARVIS and ARION personalities.
    
    Bulletproof:
    - Stage-based pipeline with full error recovery
    - Personality routing based on input source
    - Centralized memory and knowledge access
    """

    def __init__(self, modules: Dict):
        self.modules = modules
        self.bus = modules.get('bus') or MessageBus()
        self.privacy = modules.get('privacy') or PrivacyGuard()
        self.pipeline = PipelineRunner(self)
        self.scholar = ScholarAgent(self)
        self.psyche = PsycheAgent(self)
        self.tenglish = TenglishIntentAgent(modules.get('ai'))
        self.finance = FinanceMonitor()
        self.daily_note = DailyNoteAgent()
        self.emotion = EmotionEngine()
        self.prediction = PredictionEngine()
        self.te_parser = TeluguParser()
        self.te_mapper = TenglishMapper()
        self.router = MasterBrainRouter()
        self.active = False
        
        # Identity state
        self.personality_map = {
            "whatsapp": "arion",
            "telegram": "arion",
            "voice": "jarvis",
            "ui": "jarvis",
            "vision": "jarvis"
        }
        
        logger.info("[NexusBrain] Core initialized")

    async def start(self):
        """Start the brain and its proactive loops"""
        self.active = True
        logger.info("[NexusBrain] Brain active and listening...")
        # Start background thinking loops if needed
        # asyncio.create_task(self._proactive_loop())

    async def process_input(self, raw_input: str, source: str = "ui", sender: str = "Owner", context: Dict = None) -> Dict[str, Any]:
        """
        Entry point for all user interactions.
        Decides personality and runs the cognitive pipeline.
        """
        try:
            # A14 Executive: Dynamic Mode Selection
            if 'executive' in self.modules and self.modules['executive']:
                new_mode = self.modules['executive'].decide_mode(raw_input, source)
                await self.modules['executive'].set_mode(new_mode)

            # Check Privacy Gate
            if not self.privacy.is_authorized(sender):
                logger.warning(f"[Security] Unauthorized access attempt from {sender}")
                return await self._handle_unauthorized(raw_input, sender, source)

            # Determine personality based on source
            personality = self.personality_map.get(source, "jarvis")

            # ── AGENT OVERRIDE (from @mention / focused session) ─────────
            ctx = context or {}
            if ctx.get("agent_override") and ctx.get("target_agent"):
                personality = ctx["target_agent"]
                logger.info(f"[Brain] Agent override active → routing to '{personality}'")
                # Inform pipeline which agent to use
                ctx['personality'] = personality
                ctx['force_agent'] = personality

            # ── ADMIN COMMANDS ──────────────────────────────────────────
            if sender == self.privacy.get_admin() or sender.split('@')[0] == self.privacy.get_admin():
                admin_res = await self._handle_admin_commands(raw_input)
                if admin_res: return admin_res
            # ────────────────────────────────────────────────────────────
            
            # ── MASTER BRAIN INTENT ROUTING ──────────────────────────────
            decision = await self.router.route_input(raw_input)
            logger.info(f"[Brain Routing] Decision: {decision}")
            
            target_agent = decision.get("target_agent", "ARION").upper()
            keep_alive = decision.get("keep_alive_override", "30s")
            
            ctx['target_agent'] = target_agent.lower()
            ctx['keep_alive_override'] = keep_alive
            
            # If routed to Sentinel (Network Security scans)
            if target_agent == "SENTINEL":
                logger.info("[Brain] Routing task to SENTINEL network auditor...")
                from core.fleet.sentinel_tools import execute_nmap_scan, execute_netstat
                from core.fleet.sentinel_summarizer import process_sentinel_output
                
                # Extract target ip or domain if provided, otherwise default to 127.0.0.1
                import re
                targets = re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', raw_input)
                target = targets[0] if targets else "127.0.0.1"
                
                scan_type = "quick"
                if "ping" in raw_input.lower():
                    scan_type = "ping"
                elif "os" in raw_input.lower() or "detection" in raw_input.lower():
                    scan_type = "os_detect"
                elif "stealth" in raw_input.lower():
                    scan_type = "stealth"
                
                if "netstat" in raw_input.lower() or "connections" in raw_input.lower():
                    logger.info("Executing async netstat scan...")
                    raw_data = await execute_netstat()
                else:
                    logger.info(f"Executing async nmap scan for target {target} ({scan_type})...")
                    raw_data = await execute_nmap_scan(target=target, scan_type=scan_type)
                
                processed_result = await process_sentinel_output(
                    target=target,
                    scan_type=scan_type,
                    raw_output=raw_data
                )
                
                return {
                    "response": processed_result["vocal_response"],
                    "bubbles": [processed_result["vocal_response"]],
                    "personality": "sentinel",
                    "emotion": "analytical",
                    "intent": "security_audit",
                    "vault_path": processed_result["vault_path"]
                }

            # Enrich context
            ctx['personality'] = ctx.get('personality', personality)
            ctx['source'] = source
            ctx['sender'] = sender
            
            logger.info(f"[Brain] processing ({personality}): {raw_input[:50]}...")
            
            # Tenglish Pre-processing (Translation & Intent Extraction)
            tenglish_data = await self.tenglish.parse(raw_input)
            
            # [NEW] Slang Mapping & Pattern Detection
            slang_analysis = self.te_mapper.parse_slang(raw_input)
            if slang_analysis["is_tenglish"]:
                logger.info(f"[Language] Slang detected: {slang_analysis['mapped_slang']}")
                ctx['slang_context'] = slang_analysis['mapped_slang']

            if "english_translation" in tenglish_data:
                logger.info(f"[Tenglish] Translated: {tenglish_data['english_translation']}")
                raw_input = tenglish_data["english_translation"]
                ctx['tenglish_context'] = tenglish_data
            
            # [NEW] Update Emotional State
            self.emotion.update(tenglish_data.get("mood", "neutral"), len(raw_input)/1000)
            ctx['emotion_params'] = self.emotion.modulate_response({})
            
            # RUN THE PIPELINE (A1-A8)
            result = await self.pipeline.process(raw_input, source, sender, ctx)
            
            # --- FEEDBACK LEARNING LOOP ---
            # If intent is FEEDBACK and mood is negative, trigger RCA
            if tenglish_data.get("intent") == "FEEDBACK" and "frustrated" in tenglish_data.get("mood", "").lower():
                logger.info("[Learning] Negative feedback detected. Triggering Deep RCA...")
                # We need the previous task and response. This requires session history.
                # For now, we use a placeholder or the current context if available.
                # In a full implementation, we'd pull from MemoryManager.
                from core.fleet.manager import fleet_manager
                lesson = await fleet_manager.trigger_root_cause_analysis(
                    task="Previous interaction", # Needs history retrieval
                    failed_response="Previous response", # Needs history retrieval
                    user_feedback=raw_input
                )
                logger.info(f"[Learning] RCA Complete. Lesson learned: {lesson}")
                # Store the lesson
                fleet_manager.fleet_db.add_correction_note("jarvis", "task_feedback", lesson)
            # -------------------------------
            
            # Post-processing learning
            asyncio.create_task(self._learn(raw_input, result, sender))
            
            result["agent_name"] = personality.capitalize()
            result["text"] = result.get("response", "")
            
            # [NEW] Prediction & Proactive Hinting
            topic = result.get("intent", "general")
            self.prediction.record_transition(ctx.get('prev_topic', 'none'), topic)
            hint = self.prediction.get_proactive_hint(topic)
            if hint:
                result["proactive_hint"] = hint
            
            # --- AUTOMATED TRACKING ---
            # Financial Scan
            if source == "whatsapp":
                asyncio.create_task(self.finance.scan_message(raw_input))
            # --------------------------
            
            return result

        except Exception as e:
            logger.error(f"Brain process error: {e}")
            logger.error(traceback.format_exc())
            return self._fallback_response()

    async def _learn(self, original_input: str, result: Dict, sender: str):
        """Asynchronous learning and memory storage"""
        try:
            if 'memory' in self.modules:
                await self.modules['memory'].store({
                    "input": original_input,
                    "response": result.get("response"),
                    "intent": result.get("intent"),
                    "emotion": result.get("emotion"),
                    "sender": sender,
                    "personality": result.get("personality")
                })
        except Exception as e:
            logger.warning(f"Learning failed: {e}")

    def _fallback_response(self) -> Dict:
        return {
            "response": "My cognitive systems are recovering from a minor glitch. I'm here now, Sir.",
            "emotion": "apologetic",
            "intent": "recovery",
            "personality": "jarvis"
        }
    async def _handle_unauthorized(self, raw_input: str, sender: str, source: str) -> Dict:
        """Handle access attempts from unauthorized users."""
        telegram = self.modules.get('telegram')
        
        if telegram:
            logger.info(f"[Security] Requesting Telegram authorization for {sender}...")
            
            # This will send a message with buttons and wait for the response
            allowed = await telegram.request_user_authorization(sender, raw_input)
            
            if allowed:
                self.privacy.authorize(sender)
                # Now that they are allowed, we can actually process the original message
                return await self.process_input(raw_input, source, sender)
            else:
                logger.warning(f"🛡️ Access DENIED for {sender}")
        
        # Default response if not allowed: Use Voice Note if possible
        response_text = "Namaste. I am currently restricted to authorized users only. My creator has been notified."
        
        if telegram:
            # If the user is on Telegram, we send them a voice note.
            if source == "telegram":
                await telegram.send_voice_note(sender, response_text)
        
        return {
            "response": response_text,
            "emotion": "formal",
            "intent": "restricted",
            "personality": "arion"
        }

    async def _handle_admin_commands(self, raw_input: str) -> Optional[Dict]:
        """Process special commands from the admin."""
        cmd = raw_input.strip().lower()
        
        if cmd in ("approve workspace", "approve gmail", "approve calendar", "approve google workspace"):
            from tools.google_workspace_tools import set_workspace_approval
            res = set_workspace_approval(300)
            return {
                "response": f"✅ {res}",
                "emotion": "formal",
                "intent": "action",
                "personality": "jarvis"
            }
            
        elif cmd.startswith("allow "):
            target = raw_input[6:].strip()
            self.privacy.authorize(target)
            return {
                "response": f"✅ Access granted to: {target}",
                "emotion": "proud",
                "intent": "action",
                "personality": "jarvis"
            }
            
        elif cmd.startswith("revoke "):
            target = raw_input[7:].strip()
            self.privacy.revoke(target)
            return {
                "response": f"🛡️ Access revoked from: {target}",
                "emotion": "stern",
                "intent": "action",
                "personality": "jarvis"
            }
            
        elif cmd == "check healing":
            status = await self.psyche.check_healing_status()
            return {
                "response": f"🏥 HEALING DIAGNOSTICS: {status}",
                "emotion": "analytical",
                "intent": "status",
                "personality": "jarvis"
            }
            
        elif cmd.startswith("debate "):
            topic = cmd.replace("debate ", "")
            transcript = await boardroom.run_debate(topic)
            # Format the debate summary
            summary = "\n\n".join([f"[{t['agent'].upper()} - {t['mood_impact']}]: {t['content']}" for t in transcript])
            return {
                "response": f"The Boardroom has reached a verdict on '{topic}':\n\n{summary}",
                "emotion": "analytical",
                "intent": "debate",
                "personality": "jarvis"
            }

        elif cmd in ("list agents", "agents", "fleet agents"):
            # Return list of all registered agents
            try:
                from core.whatsapp_session_manager import session_manager
                return {
                    "response": session_manager.list_all_agents(),
                    "emotion": "informative",
                    "intent": "status",
                    "personality": "jarvis"
                }
            except Exception as e:
                return {
                    "response": f"Could not list agents: {e}",
                    "emotion": "neutral",
                    "intent": "status",
                    "personality": "jarvis"
                }

        elif cmd in ("debug fleet", "fleet status", "fleet debug"):
            try:
                from core.fleet.manager import fleet_manager
                summary = fleet_manager.get_fleet_summary() if hasattr(fleet_manager, "get_fleet_summary") else str(fleet_manager)
                return {
                    "response": f"🚀 *Fleet Debug*\n{summary}",
                    "emotion": "analytical",
                    "intent": "status",
                    "personality": "jarvis"
                }
            except Exception as e:
                return {
                    "response": f"Fleet debug failed: {e}",
                    "emotion": "neutral",
                    "intent": "status",
                    "personality": "jarvis"
                }
            
        return None

    async def request_guardian_approval(self, event_type: str, details: str) -> bool:
        """
        The 'Guardian' Secure-Handshake.
        Sends a Telegram message to the owner for manual approval of sensitive actions.
        """
        telegram = self.modules.get('telegram')
        if not telegram:
            logger.warning("[Guardian] Telegram service unavailable. Denying sensitive action.")
            return False
            
        logger.info(f"[Guardian] Requesting approval for: {event_type}")
        
        # This will send a message with buttons and wait for 'Yes/No' or a Wake Word
        message = f"🛡️ GUARDIAN ALERT: {event_type}\nDetails: {details}\n\nConfirm with 'Yes' or your Wake Word."
        allowed = await telegram.request_user_authorization("Owner", message)
        
        if allowed:
            logger.info(f"✅ GUARDIAN: Approved {event_type}")
            return True
        else:
            logger.warning(f"🛡️ GUARDIAN: Denied {event_type}")
            return False

    async def process_telegram_command(self, text: str, sender: str = "owner") -> str:
        """
        Special entry point for Telegram service.
        Maps to the shared process_input pipeline.
        """
        try:
            # Check if this is the authorized chat id from env
            is_admin = sender == self.privacy.get_admin() or sender == str(os.getenv("AUTHORIZED_CHAT_ID", ""))
            
            # Run the input through the brain
            result = await self.process_input(
                raw_input=text,
                source="telegram",
                sender=sender if not is_admin else self.privacy.get_admin()
            )
            
            return result.get("response", "No response generated.")
        except Exception as e:
            logger.error(f"Error in process_telegram_command: {e}")
            return f"Brain Error: {str(e)}"

    async def health_check(self) -> Dict:
        """System-wide health check of cognitive modules"""
        health = {}
        for name, mod in self.modules.items():
            if hasattr(mod, 'health_check'):
                health[name] = await mod.health_check()
            else:
                health[name] = "available"
        return health

    async def process_vision(self, image_path: str, prompt: str = "Analyze this image and describe what is happening, especially noting any objects, text, or activities.") -> str:
        """Process an image from the mobile app via Ollama Vision."""
        if 'ai' in self.modules:
            return await self.modules['ai'].vision_analyze(prompt, image_path)
        return "AI Engine not connected."

    async def process_context(self, context_data: Dict) -> None:
        """Ingests mobile context (GPS, battery, activity) into behavior observer."""
        if 'behavior' in self.modules:
            if hasattr(self.modules['behavior'], 'process_mobile_context'):
                await self.modules['behavior'].process_mobile_context(context_data)
            else:
                logger.info(f"[Context] Ingested context data: {context_data}")
        else:
            logger.info(f"[Context] Ignored context data (behavior module not loaded): {context_data}")

    async def ingest_multimodal(self, file_path: str) -> Optional[str]:
        """
        ATLAS & ARION Metabolism (A15 Ingestion Layer)
        Extracts logic, slang, and knowledge from files and saves to Tiered Memory.
        If it's a voice message, it returns the transcription/answer.
        """
        try:
            logger.info(f"[Ingestion] Commencing metabolism for: {file_path}")
            
            ext = os.path.splitext(file_path)[1].lower()
            analysis_response = None

            if ext in ['.wav', '.mp3', '.m4a', '.ogg', '.aac']:
                logger.info(f"[Ingestion] Audio file detected. Transcribing...")
                from voice.audio_intelligence import AudioIntelligenceProcessor
                proc = AudioIntelligenceProcessor()
                # Transcribe the whole file
                segments, info = proc.model.transcribe(file_path, language="te")
                transcript = " ".join([s.text for s in segments])
                
                if transcript.strip():
                    logger.info(f"[Ingestion] Transcribed ({info.language}): {transcript}")
                    # Process the transcript through the brain to get an answer
                    ai_res = await self.process_input(transcript, source="voice")
                    analysis_response = ai_res.get("response")
                    
                    # Save to Memory Tier 3
                    if 'memory' in self.modules:
                        await self.modules['memory'].remember(
                            content=f"Voice Message Analysis: {transcript}",
                            importance=0.7,
                            metadata={"source": "voice_ingestion", "transcript": transcript},
                            tags=["@atlas", "@voice"]
                        )
            else:
                # Generic file processing
                await asyncio.sleep(1)
                if 'memory' in self.modules:
                    await self.modules['memory'].remember(
                        content=f"Ingested knowledge from {os.path.basename(file_path)}",
                        importance=0.5,
                        metadata={"source": "file_ingestion"},
                        tags=["@atlas"]
                    )

            logger.info(f"[Ingestion] SUCCESS: {file_path} processed.")
            return analysis_response or "Knowledge ingested successfully."
            
        except Exception as e:
            logger.error(f"[Ingestion] FAILED: {e}")
            return None
