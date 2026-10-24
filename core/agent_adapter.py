import abc
from typing import Optional

from core.agent_message import AgentMessage
from core.collaboration_session import CollaborationSession

class AgentAdapter(abc.ABC):
    """
    Abstract interface for bridging a Live LLM or Mock Agent 
    to the AgentBus during a Collaboration Session.
    """
    def __init__(self, agent_name: str, execution_mode: str = "mock"):
        self.agent_name = agent_name
        self.execution_mode = execution_mode

    @abc.abstractmethod
    async def handle_message(self, message: AgentMessage, session: CollaborationSession) -> Optional[AgentMessage]:
        """
        Takes an incoming AgentMessage from the bus and returns a response AgentMessage.
        Should construct the strict collaboration prompt and invoke the LLM.
        """
        pass
        
class MockCouncilAdapter(AgentAdapter):
    def __init__(self):
        super().__init__("council", execution_mode="mock")
        
    async def handle_message(self, message: AgentMessage, session: CollaborationSession) -> Optional[AgentMessage]:
        # Mock logic for testing
        import uuid
        
        if session.current_round == 1:
            return AgentMessage(
                conversation_id=session.conversation_id,
                sender="council",
                recipient=message.sender,
                message_type="CHALLENGE",
                content="CHALLENGE: Your evidence doesn't independently support this. Please provide a CORRECTION or more specific EVIDENCE.",
                claim_id=message.claim_id,
                parent_message_id=message.message_id,
                round_id=session.current_round + 1
            )
        elif session.current_round == 2:
            content_lower = message.content.lower()
            if "correction" in content_lower or "evidence" in content_lower or message.message_type in ["CORRECTION", "EVIDENCE"]:
                # Ensure it's not the exact fallback message from an LLM failure
                if "failed to parse my internal logic" in content_lower:
                    return AgentMessage(
                        conversation_id=session.conversation_id,
                        sender="council",
                        recipient=message.sender,
                        message_type="DISAGREEMENT",
                        content="You suffered an LLM backend failure and did not address the challenge.",
                        claim_id=message.claim_id,
                        parent_message_id=message.message_id,
                        round_id=session.current_round + 1
                    )
                    
                return AgentMessage(
                    conversation_id=session.conversation_id,
                    sender="council",
                    recipient=message.sender,
                    message_type="VERIFICATION_RESULT",
                    content="VERIFICATION_RESULT: CONSENSUS",
                    claim_id=message.claim_id,
                    parent_message_id=message.message_id,
                    round_id=session.current_round + 1
                )
            else:
                return AgentMessage(
                    conversation_id=session.conversation_id,
                    sender="council",
                    recipient=message.sender,
                    message_type="DISAGREEMENT",
                    content="You did not address the challenge properly.",
                    claim_id=message.claim_id,
                    parent_message_id=message.message_id,
                    round_id=session.current_round + 1
                )

class LiveAtlasAdapter(AgentAdapter):
    def __init__(self, llm_callable):
        super().__init__("atlas", execution_mode="live")
        self.llm_callable = llm_callable
        
    async def handle_message(self, message: AgentMessage, session: CollaborationSession) -> Optional[AgentMessage]:
        prompt = self._build_collaboration_prompt(message, session)
        
        # We instruct the LLM to output ONLY a JSON object
        prompt += "\nOutput ONLY valid JSON."
        
        # Parse the JSON response
        import json
        import re
        
        response_text = ""
        try:
            # Invoke the live LLM (using the router/llm_callable provided)
            response_text = self.llm_callable(prompt)
            
            # Clean markdown if present
            clean_json = re.sub(r'```json\n|\n```', '', response_text).strip()
            data = json.loads(clean_json)
            
            return AgentMessage(
                conversation_id=session.conversation_id,
                sender=self.agent_name,
                recipient=message.sender,
                message_type=data.get("message_type", "EVIDENCE"),
                content=data.get("content", ""),
                claim_id=data.get("claim_id", message.claim_id),
                evidence=data.get("evidence", []),
                confidence=float(data.get("confidence", 0.8)),
                parent_message_id=message.message_id,
                round_id=session.current_round + 1
            )
        except Exception as e:
            print(f"[{self.agent_name.upper()} ADAPTER ERROR]: {e}")
            # Fallback message
            return AgentMessage(
                conversation_id=session.conversation_id,
                sender=self.agent_name,
                recipient=message.sender,
                message_type="EVIDENCE",
                content=f"Failed to parse my internal logic. My raw thought was: {response_text[:200] if response_text else str(e)}",
                parent_message_id=message.message_id,
                round_id=session.current_round + 1
            )

    def _build_collaboration_prompt(self, message: AgentMessage, session: CollaborationSession) -> str:
        prompt = f"""ROLE
You are {self.agent_name.capitalize()}.

CURRENT TASK
Topic: {session.topic}
Round: {session.current_round} / {session.max_rounds}

CLAIM UNDER REVIEW
{message.claim_id if message.claim_id else 'None explicitly targeted'}

PREVIOUS AGENT MESSAGE
Sender: {message.sender}
Type: {message.message_type}
Content: {message.content}
Evidence: {', '.join(message.evidence)}

RULES
- Do not execute tools directly.
- Do not invent evidence.
- Clearly distinguish facts from hypotheses.
- Challenge unsupported claims.
- Return structured JSON matching the AgentMessage format (message_type, content, claim_id, etc.).
"""
        return prompt
