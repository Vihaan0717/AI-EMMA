"""
NEXUS-X ReAct Engine — Reasoning + Acting Execution Loop
==========================================================
Implements the ReAct (Reasoning + Acting) paradigm for all fleet agents.

Flow per agent turn:
  1. Agent receives task + context
  2. Agent MUST output [THOUGHT] block (Chain-of-Thought reasoning)
  3. Agent optionally outputs [TOOL_CALL] block
  4. System executes tool → returns [TOOL_RESULT]
  5. Loop repeats until agent outputs [FINAL_ANSWER] or max steps reached
  6. Self-evaluation: agent rates its own confidence

This replaces the old linear generate-once pipeline.
"""

import re
import json
import time
import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger("ReActEngine")

# ── Constants ────────────────────────────────────────────────────
MAX_REACT_STEPS = 6              # Maximum reasoning loops before forced output
THOUGHT_WEIGHT = 0.3             # Bonus to quality score for explicit reasoning
COT_REQUIRED_AGENTS = ["*"]      # All agents must reason


@dataclass
class ReActTrace:
    """Full trace of an agent's ReAct execution."""
    agent_id: str
    task: str
    steps: List[Dict[str, Any]] = field(default_factory=list)
    final_answer: str = ""
    total_thoughts: int = 0
    total_tool_calls: int = 0
    self_confidence: float = 0.0
    elapsed_ms: float = 0.0


class ReActEngine:
    """
    Core engine that orchestrates the ReAct loop for any fleet agent.
    It parses agent output for [THOUGHT], [TOOL_CALL], and [FINAL_ANSWER]
    blocks, executes tools, and feeds results back.
    """

    def __init__(self, agentic_tools=None):
        """
        Args:
            agentic_tools: AgenticToolRegistry instance for tool execution
        """
        if agentic_tools is None:
            from core.fleet.agentic_tools import agentic_tool_registry
            agentic_tools = agentic_tool_registry
        self.tools = agentic_tools

    def build_react_system_prompt(self, base_prompt: str, agent_id: str) -> str:
        """
        Wrap an agent's base system prompt with ReAct protocol instructions
        and available tool descriptions.
        """
        tool_prompt = self.tools.generate_tool_prompt(agent_id)

        react_instructions = """
[MANDATORY REASONING PROTOCOL]
You MUST follow the ReAct (Reasoning + Acting) protocol for EVERY response:

1. ALWAYS start with a [THOUGHT] block that explains your reasoning step-by-step.
   - Break down the problem into sub-problems
   - Identify what information you have vs. what you need
   - Plan your approach before acting

2. If you need external data or computation, use a [TOOL_CALL] block.
   - Only ONE tool call per step
   - Wait for the [TOOL_RESULT] before continuing

3. After receiving results, write another [THOUGHT] block analyzing them.

4. When you have the final answer, wrap it in [FINAL_ANSWER] ... [/FINAL_ANSWER].

5. After your final answer, rate your confidence: [CONFIDENCE: 0.XX]

CRITICAL RULES:
- NEVER skip the [THOUGHT] block. Every response must start with reasoning.
- If a task seems simple, still reason through it — explain WHY it's simple.
- If you're unsure, say so in your [THOUGHT] and lower your [CONFIDENCE].
- If you detect an error in your own reasoning, correct it immediately.

FORMAT EXAMPLE:
[THOUGHT]
The user asks about X. Let me break this down:
1. First, I need to understand Y
2. Then I should check Z
3. Finally, I can synthesize the answer
[/THOUGHT]

[TOOL_CALL] {"tool": "web_search", "params": {"query": "topic X"}} [/TOOL_CALL]

... [TOOL_RESULT] ... result data ... [/TOOL_RESULT] ...

[THOUGHT]
The search returned useful data. Key findings:
- Finding A supports my hypothesis
- Finding B contradicts it
Let me reconcile these...
[/THOUGHT]

[FINAL_ANSWER]
Based on my analysis...
[/FINAL_ANSWER]

[CONFIDENCE: 0.85]
"""
        return base_prompt + react_instructions + tool_prompt

    async def execute(
        self,
        agent_id: str,
        task: str,
        system_prompt: str,
        ai_engine,
        temperature: float = 0.7,
        context: str = "",
        max_steps: int = MAX_REACT_STEPS
    ) -> ReActTrace:
        """
        Run the full ReAct loop for an agent.

        Args:
            agent_id: Agent identifier
            task: The user task or sub-task
            system_prompt: Full system prompt (should already include ReAct instructions)
            ai_engine: The AI engine to generate responses
            temperature: Base temperature for first generation
            context: Additional context (previous agent output, web data, etc.)
            max_steps: Maximum ReAct loop iterations

        Returns:
            ReActTrace with full execution history
        """
        start_time = time.perf_counter()
        trace = ReActTrace(agent_id=agent_id, task=task)

        current_prompt = task
        if context:
            current_prompt = f"{task}\n\n[CONTEXT]\n{context}\n[/CONTEXT]"

        step = 0
        while step < max_steps:
            step += 1
            logger.info(f"ReAct [{agent_id}] Step {step}/{max_steps}")

            # Generate agent response
            try:
                response = await ai_engine.generate(
                    prompt=current_prompt,
                    system=system_prompt,
                    temperature=temperature if step == 1 else 0.2  # Lower temp for correction steps
                )
            except Exception as e:
                logger.error(f"ReAct [{agent_id}]: Generation failed: {e}")
                trace.steps.append({"step": step, "type": "error", "content": str(e)})
                break

            # Parse the response for structured blocks
            thoughts = self._extract_blocks(response, "THOUGHT")
            tool_calls = self._extract_tool_calls(response)
            final_answer = self._extract_blocks(response, "FINAL_ANSWER")
            confidence = self._extract_confidence(response)

            # Record this step
            step_record = {
                "step": step,
                "thoughts": thoughts,
                "tool_calls": [tc[0] for tc in tool_calls],  # tool name only
                "has_final_answer": bool(final_answer),
                "raw_length": len(response)
            }
            trace.steps.append(step_record)
            trace.total_thoughts += len(thoughts)

            # If agent produced final answer, we're done
            if final_answer:
                trace.final_answer = final_answer[0]
                trace.self_confidence = confidence
                logger.info(f"ReAct [{agent_id}]: Final answer at step {step} (confidence={confidence})")
                break

            # If agent called a tool, execute it
            if tool_calls:
                tool_results = []
                for tool_name, tool_params in tool_calls:
                    trace.total_tool_calls += 1
                    logger.info(f"ReAct [{agent_id}]: Tool call -> {tool_name}({list(tool_params.keys())})")

                    # Check for delegation requests
                    if tool_name == "delegate":
                        tool_result = await self._handle_delegation(tool_params, agent_id)
                    else:
                        tool_result = await self.tools.execute_tool(tool_name, tool_params, agent_id)

                    result_str = json.dumps(tool_result, default=str) if isinstance(tool_result, dict) else str(tool_result)
                    tool_results.append(f"[TOOL_RESULT: {tool_name}]\n{result_str}\n[/TOOL_RESULT]")

                # Feed results back to agent
                current_prompt = (
                    f"Previous reasoning and tool calls:\n{response}\n\n"
                    + "\n".join(tool_results)
                    + "\n\nContinue your reasoning. If you have the answer, write [FINAL_ANSWER]...[/FINAL_ANSWER]."
                )
                continue

            # No tool call and no final answer — agent gave a raw response
            # Treat the entire response as the final answer
            if not thoughts and not tool_calls and not final_answer:
                # Agent didn't follow ReAct format — use raw response
                trace.final_answer = response
                trace.self_confidence = 0.5  # Lower confidence for unstructured output
                logger.warning(f"ReAct [{agent_id}]: Raw response (no ReAct format) at step {step}")
                break
            elif thoughts and not tool_calls and not final_answer:
                # Agent thought but didn't act or conclude — prompt for conclusion
                current_prompt = (
                    f"Your previous reasoning:\n{response}\n\n"
                    "You've analyzed the problem but haven't provided a final answer. "
                    "Please write your [FINAL_ANSWER]...[/FINAL_ANSWER] now."
                )
                continue

        # If we exhausted max steps, use last response
        if not trace.final_answer and step >= max_steps:
            trace.final_answer = response if 'response' in dir() else "ERROR: No response generated."
            trace.self_confidence = 0.3
            logger.warning(f"ReAct [{agent_id}]: Max steps exhausted. Forcing output.")

        trace.elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.info(
            f"ReAct [{agent_id}]: Complete — "
            f"steps={len(trace.steps)}, thoughts={trace.total_thoughts}, "
            f"tools={trace.total_tool_calls}, confidence={trace.self_confidence}, "
            f"elapsed={trace.elapsed_ms}ms"
        )
        return trace

    async def execute_voice_stream(
        self,
        agent_id: str,
        task: str,
        system_prompt: str,
        ai_engine,
        voice_service,
        voice_id: int = 0
    ) -> ReActTrace:
        """
        Runs the ReAct loop but streams the FINAL_ANSWER to the voice service.
        Suppresses [THOUGHT] and [TOOL_CALL] blocks from being spoken aloud.
        Handles dynamic interruption.
        """
        start_time = time.perf_counter()
        trace = ReActTrace(agent_id=agent_id, task=task)
        
        current_prompt = task
        step = 1 # Force single step for now, or loop it
        
        # Buffer for TTS chunking
        full_response = ""
        spoken_cursor = 0
        
        try:
            logger.info(f"ReAct Voice [{agent_id}] Streaming started...")
            
            async for token in ai_engine.generate_stream(
                prompt=current_prompt,
                system=system_prompt,
                temperature=0.7
            ):
                if voice_service.interrupted.is_set():
                    logger.warning(f"ReAct Voice [{agent_id}] Interrupted by user mid-sentence!")
                    trace.final_answer = full_response + "... [INTERRUPTED]"
                    return trace
                    
                full_response += token
                
                # Robustly isolate FINAL_ANSWER using regex
                import re
                match = re.search(r"\[FINAL_ANSWER\](.*)", full_response, re.DOTALL)
                if match:
                    current_final = match.group(1).replace("[/FINAL_ANSWER]", "")
                    
                    # Get the new text since our last spoken cursor
                    new_text = current_final[spoken_cursor:]
                    
                    # If we have a sentence boundary
                    if any(p in new_text for p in ['. ', '? ', '! ', '\n']):
                        # Find the last punctuation mark
                        last_punc = max([new_text.rfind(p) for p in ['. ', '? ', '! ', '\n']])
                        chunk_to_speak = new_text[:last_punc+1].strip()
                        
                        if chunk_to_speak:
                            voice_service.speak(chunk_to_speak, voice_id)
                        
                        # Advance cursor
                        spoken_cursor += last_punc + 1
            
            # Flush remaining buffer at the end
            match = re.search(r"\[FINAL_ANSWER\](.*)", full_response, re.DOTALL)
            if match:
                current_final = match.group(1).replace("[/FINAL_ANSWER]", "")
                new_text = current_final[spoken_cursor:].strip()
                if new_text:
                    voice_service.speak(new_text, voice_id)
                
            trace.final_answer = full_response
            trace.elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            
        except Exception as e:
            logger.error(f"ReAct Voice [{agent_id}] Error: {e}")
            trace.final_answer = "Error: Voice stream failed."
            
        return trace

    async def _handle_delegation(self, params: Dict, requesting_agent: str) -> Dict:
        """
        Handle an agent's delegation request.
        This creates a sub-task for another agent through the swarm coordinator.
        """
        target = params.get("target_agent", "")
        sub_task = params.get("sub_task", "")

        if not target or not sub_task:
            return {"success": False, "error": "Missing target_agent or sub_task"}

        try:
            from core.fleet.swarm_coordinator import swarm_coordinator
            result = await swarm_coordinator.delegate(
                from_agent=requesting_agent,
                to_agent=target,
                task=sub_task
            )
            return {"success": True, "result": result}
        except ImportError:
            return {"success": False, "error": "Swarm coordinator not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ── Parsing Helpers ──────────────────────────────────────────────

    def _extract_blocks(self, text: str, block_type: str) -> List[str]:
        """Extract content from [BLOCK_TYPE]...[/BLOCK_TYPE] tags."""
        pattern = rf"\[{block_type}\](.*?)\[/{block_type}\]"
        matches = re.findall(pattern, text, re.DOTALL)
        return [m.strip() for m in matches]

    def _extract_tool_calls(self, text: str) -> List[Tuple[str, Dict]]:
        """
        Extract [TOOL_CALL] {"tool": "name", "params": {...}} [/TOOL_CALL] blocks.
        Returns list of (tool_name, params_dict) tuples.
        """
        pattern = r"\[TOOL_CALL\]\s*(.*?)\s*\[/TOOL_CALL\]"
        matches = re.findall(pattern, text, re.DOTALL)

        results = []
        for match in matches:
            try:
                data = json.loads(match.strip())
                tool_name = data.get("tool", "")
                params = data.get("params", {})
                if tool_name:
                    results.append((tool_name, params))
            except json.JSONDecodeError:
                logger.warning(f"ReAct: Failed to parse TOOL_CALL JSON: {match[:100]}")
                continue

        return results

    def _extract_confidence(self, text: str) -> float:
        """Extract [CONFIDENCE: 0.XX] from text."""
        pattern = r"\[CONFIDENCE:\s*([\d.]+)\]"
        match = re.search(pattern, text)
        if match:
            try:
                return min(1.0, max(0.0, float(match.group(1))))
            except ValueError:
                pass
        return 0.0

    def compute_quality_score(self, trace: ReActTrace, critic_score: float) -> float:
        """
        Compute a final quality score that rewards reasoning depth.

        Quality = critic_score + thought_bonus + confidence_adjustment
        """
        # Bonus for explicit reasoning (up to +10 points)
        thought_bonus = min(10.0, trace.total_thoughts * 3.0)

        # Confidence alignment: if agent's self-confidence matches critic, bonus; if divergent, penalty
        if trace.self_confidence > 0:
            confidence_diff = abs(trace.self_confidence * 100 - critic_score)
            confidence_adj = max(-5.0, 5.0 - confidence_diff * 0.1)
        else:
            confidence_adj = 0.0

        final = min(100.0, critic_score + thought_bonus + confidence_adj)
        return round(final, 1)


# ── Global Singleton ──────────────────────────────────────────────
react_engine = ReActEngine()
