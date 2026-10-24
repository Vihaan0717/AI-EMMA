"""
Needle Decision Router Service (Needle 3 on-device model)
Powered by Cactus Compute's Needle 3 (3.2.8) architecture.

Provides ultra-fast (<20ms execution on CPU, ~128MB RAM footprint) 
on-device tool-calling, intent routing, and grammar-constrained decision dispatch.
Acts as a lightning fast-path router before invoking heavy reasoners or cloud LLMs.
"""

import os
import sys
import time
import logging
from typing import Optional, Dict, Any, Tuple, Literal

logger = logging.getLogger("NeedleDecisionRouter")
logger.setLevel(logging.INFO)

# Suppress telemetry and HF warnings
os.environ["NEEDLE_TELEMETRY"] = "0"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Gesture and emotion allowed vocabularies (aligned with VRM & AvatarDirector)
GestureLiteral = Literal[
    'idle', 'walk', 'run', 'sit', 'seiza', 'agura', 
    'wave', 'bow', 'clap', 'cheer', 'dance', 'think', 
    'explain', 'nod', 'disagree', 'peace_sign'
]

EmotionLiteral = Literal[
    'neutral', 'happy', 'thinking', 'surprised', 'sad', 
    'angry', 'wink', 'smug', 'shy', 'relaxed'
]

MediaActionLiteral = Literal['play_pause', 'next', 'previous', 'mute']

AppLaunchLiteral = Literal[
    'spotify', 'chrome', 'youtube', 'calculator', 
    'notepad', 'terminal', 'vscode'
]

ScanLiteral = Literal['room_objects', 'user_presence']


class NeedleDecisionRouter:
    """
    On-device Needle 3 decision router for real-time avatar kinematics & OS quick dispatch.
    """
    def __init__(self):
        self.is_available = False
        self.agent = None
        self._init_needle()

    def _init_needle(self):
        try:
            import needle

            @needle.tool
            def direct_avatar_action(gesture: GestureLiteral, emotion: EmotionLiteral) -> dict:
                """Control Ava avatar body posture, physical gesture, and facial emotional expression."""
                return {'tool': 'avatar_action', 'gesture': gesture, 'emotion': emotion}

            @needle.tool
            def os_media_command(action: MediaActionLiteral) -> dict:
                """Control media playback such as pause, resume, next track, or mute."""
                return {'tool': 'os_media', 'action': action}

            @needle.tool
            def os_quick_launch(app: AppLaunchLiteral) -> dict:
                """Launch or open desktop applications and web apps."""
                return {'tool': 'os_launch', 'app': app}

            @needle.tool
            def senses_quick_scan(scan_type: ScanLiteral) -> dict:
                """Scan physical room environment or detect user desk presence via webcam."""
                return {'tool': 'senses_scan', 'scan_type': scan_type}

            self.agent = needle.Needle(tools=[
                direct_avatar_action,
                os_media_command,
                os_quick_launch,
                senses_quick_scan
            ])
            self.is_available = True
            logger.info("Needle 3 on-device decision engine initialized successfully.")
        except Exception as e:
            logger.warning(f"Needle 3 initialization skipped or failed: {e}. Falling back to standard router.")
            self.is_available = False

    def route(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Evaluates the user query through Needle 3.
        Returns a structured decision dictionary if a fast-path tool matched, or None for LLM fallback.
        """
        if not self.is_available or not self.agent or not query.strip():
            return None

        try:
            t0 = time.perf_counter()
            self.agent.reset()
            res = self.agent.run(query)
            latency_ms = (time.perf_counter() - t0) * 1000

            decision = None
            # 1. Check direct execution results
            results = res.get('results') or []
            if results and isinstance(results[0], dict):
                decision = results[0]
                decision['latency_ms'] = latency_ms
                decision['source'] = 'needle_direct'
                decision['confidence'] = res.get('confidence', 0.95)

            # 2. Check function calls
            if not decision:
                function_calls = res.get('function_calls') or []
                if function_calls:
                    call = function_calls[0]
                    name = call.get('name')
                    args = call.get('arguments', {})
                    decision = self._format_call(name, args, latency_ms, res.get('confidence', 0.9))

            # 3. Check suppressed calls if high confidence
            if not decision:
                suppressed = res.get('suppressed_calls') or []
                if suppressed and res.get('confidence', 0) > 0.15:
                    call = suppressed[0]
                    name = call.get('name')
                    args = call.get('arguments', {})
                    decision = self._format_call(name, args, latency_ms, res.get('confidence', 0.5))

            if decision:
                self._enrich_decision(query, decision)
                return decision

            return None
        except Exception as e:
            logger.debug(f"Needle route evaluation error: {e}")
            return None

    def _format_call(self, name: str, args: dict, latency_ms: float, confidence: float) -> Optional[Dict[str, Any]]:
        if name == 'direct_avatar_action':
            return {
                'tool': 'avatar_action',
                'gesture': args.get('gesture', 'idle'),
                'emotion': args.get('emotion', 'neutral'),
                'latency_ms': latency_ms,
                'source': 'needle_call',
                'confidence': confidence
            }
        elif name == 'os_media_command':
            return {
                'tool': 'os_media',
                'action': args.get('action', 'play_pause'),
                'latency_ms': latency_ms,
                'source': 'needle_call',
                'confidence': confidence
            }
        elif name == 'os_quick_launch':
            return {
                'tool': 'os_launch',
                'app': args.get('app', 'spotify'),
                'latency_ms': latency_ms,
                'source': 'needle_call',
                'confidence': confidence
            }
        elif name == 'senses_quick_scan':
            return {
                'tool': 'senses_scan',
                'scan_type': args.get('scan_type', 'user_presence'),
                'latency_ms': latency_ms,
                'source': 'needle_call',
                'confidence': confidence
            }
        return None

    def _enrich_decision(self, query: str, decision: dict):
        tool = decision.get('tool')
        q_lower = query.lower().strip()

        info_keywords = [
            "what", "why", "who", "where", "when", "how", "explain", "describe",
            "summarize", "search", "research", "tell me", "define", "meaning of",
            "could you explain", "can you explain", "analyze"
        ]
        is_info = any(q_lower.startswith(k) or f" {k} " in q_lower for k in info_keywords)

        if tool == 'avatar_action':
            if is_info:
                decision['is_pure_command'] = False
                decision['needs_llm'] = True
            else:
                decision['is_pure_command'] = True
                decision['needs_llm'] = False
        else:
            decision['is_pure_command'] = True
            decision['needs_llm'] = False

    def execute_fast_decision(self, decision: Dict[str, Any]) -> Tuple[str, str]:
        """
        Executes the fast-path decision and returns (tool_name, tool_result_string).
        """
        tool = decision.get('tool')
        latency = decision.get('latency_ms', 0.0)

        if tool == 'avatar_action':
            gesture = decision.get('gesture', 'idle')
            emotion = decision.get('emotion', 'neutral')

            # Handle seating/locomotion vs conversational gestures
            if gesture in ['sit', 'seiza', 'agura', 'walk', 'run', 'idle']:
                from agents.body_control_mcp import body_set_posture, body_trigger_gesture
                body_set_posture(gesture)
                res = body_trigger_gesture(gesture, emotion)
                return "body_set_posture", f"[NEEDLE FAST-PATH {latency:.1f}ms] Avatar posture set to '{gesture}' with emotion '{emotion}'."
            else:
                from agents.body_control_mcp import body_trigger_gesture
                res = body_trigger_gesture(gesture, emotion)
                return "body_trigger_gesture", f"[NEEDLE FAST-PATH {latency:.1f}ms] Triggered gesture '{gesture}' with emotion '{emotion}'."

        elif tool == 'os_media':
            action = decision.get('action', 'play_pause')
            from agents.os_controller_mcp import os_media_control
            res = os_media_control(action)
            return "os_media_control", f"[NEEDLE FAST-PATH {latency:.1f}ms] Media control: {res}"

        elif tool == 'os_launch':
            app = decision.get('app', 'spotify')
            import subprocess
            try:
                subprocess.Popen(f"start {app}", shell=True)
                return "os_open_app", f"[NEEDLE FAST-PATH {latency:.1f}ms] Successfully launched {app}."
            except Exception as e:
                return "os_open_app", f"[NEEDLE FAST-PATH] Failed to launch {app}: {e}"

        elif tool == 'senses_scan':
            scan_type = decision.get('scan_type')
            if scan_type == 'room_objects':
                from agents.senses_mcp import scan_physical_environment
                return "scan_physical_environment", scan_physical_environment()
            else:
                from agents.senses_mcp import check_user_presence
                return "check_user_presence", check_user_presence()

        return "unknown_tool", f"Unsupported Needle tool: {tool}"
