import os
import json
import uuid
import sqlite3
from typing import List, Dict, Optional
from datetime import datetime, timezone

from core.agent_message import AgentMessage
from core.capability_registry import AGENT_CAPABILITIES
from core.context_compressor import ContextCompressor

class AgentBus:
    def __init__(self, db_path: str = "logs/agent_events.db", jsonl_path: str = "logs/agent_events.jsonl"):
        self.db_path = db_path
        self.jsonl_path = jsonl_path
        self.max_messages_per_conversation = 20
        self.max_rounds = 5
        
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
        
        # Track processed messages for idempotency
        self.processed_message_ids = set()
        # In-memory tracking for active rounds, max counts
        self.conversations: Dict[str, List[AgentMessage]] = {}
        self.compressor = ContextCompressor()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS agent_events (
                event_id TEXT PRIMARY KEY,
                conversation_id TEXT,
                message_id TEXT,
                timestamp TEXT,
                sender TEXT,
                recipient TEXT,
                event_type TEXT,
                topic TEXT,
                content TEXT,
                confidence REAL,
                outcome TEXT,
                metadata TEXT,
                execution_mode TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def _log_event(self, event_type: str, message: AgentMessage, outcome: str = "success", execution_mode: str = "mock"):
        event_id = str(uuid.uuid4())
        
        # 1. SQLite authoritative store
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO agent_events (event_id, conversation_id, message_id, timestamp, sender, recipient, event_type, topic, content, confidence, outcome, metadata, execution_mode)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event_id,
            message.conversation_id,
            message.message_id,
            datetime.now(timezone.utc).isoformat(),
            message.sender,
            message.recipient,
            event_type,
            message.topic,
            message.content,
            message.confidence,
            outcome,
            json.dumps(message.metadata),
            execution_mode
        ))
        conn.commit()
        conn.close()

        # 2. JSONL Debug/Export log
        event_dict = {
            "event_id": event_id,
            "event_type": event_type,
            "conversation_id": message.conversation_id,
            "message_id": message.message_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sender": message.sender,
            "recipient": message.recipient,
            "topic": message.topic,
            "outcome": outcome,
            "metadata": message.metadata,
            "execution_mode": execution_mode
        }
        with open(self.jsonl_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event_dict) + "\n")

    def _store_message(self, message: AgentMessage):
        if message.conversation_id not in self.conversations:
            self.conversations[message.conversation_id] = []
        
        conv = self.conversations[message.conversation_id]
        
        # Calculate rounds properly based on round_id explicitly given
        rounds = set(m.round_id for m in conv)
        rounds.add(message.round_id)
        
        # Infinite debate protection
        if len(rounds) > self.max_rounds or len(conv) >= self.max_messages_per_conversation:
            self._log_event("debate_timeout", message, outcome="MAX_ROUNDS_REACHED")
            raise ValueError("MAX_ROUNDS_REACHED")
            
        conv.append(message)
        self.processed_message_ids.add(message.message_id)

    def send(self, message: AgentMessage):
        # Check idempotency
        if message.message_id in self.processed_message_ids:
            return  # Ignore duplicate message

        # Validate sender identity
        if message.sender not in AGENT_CAPABILITIES and message.sender != "nexus_master":
            raise ValueError(f"REJECT: Unauthorized sender '{message.sender}'")

        # Validate recipient identity
        if message.recipient != "ALL" and message.recipient not in AGENT_CAPABILITIES and message.recipient != "nexus_master":
            raise ValueError(f"REJECT: Unknown recipient '{message.recipient}'")
        
        # Store full raw message in Audit Storage
        self._store_message(message)
        
        # Determine risk profile (mock logic: could be dynamic based on message content/topic)
        risk_profile = message.metadata.get("risk_profile", "NORMAL")
        
        # Extract the compact MessageContract to send to the recipient
        contract = self.compressor.compress(message, risk_profile)
        
        # (In a real system, the recipient agent is fed `contract`, not `message`)
        
        # Log basic message event with contract metadata
        message.metadata["contract_payload"] = contract.model_dump()
        self._log_event("message_sent", message, outcome="delivered")

    def request(self, sender: str, recipient: str, message_type: str, content: str, topic: str = "", evidence: List[str] = None, conversation_id: str = None, round_id: int = 1, priority: str = "normal") -> AgentMessage:
        if evidence is None:
            evidence = []
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            
        msg = AgentMessage(
            conversation_id=conversation_id,
            sender=sender,
            recipient=recipient,
            message_type=message_type,
            content=content,
            topic=topic,
            evidence=evidence,
            requires_response=True,
            round_id=round_id,
            priority=priority
        )
        self.send(msg)
        return msg

    def broadcast(self, sender: str, message_type: str, content: str, topic: str = "", conversation_id: str = None, round_id: int = 1, priority: str = "normal") -> List[AgentMessage]:
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            
        msgs = []
        for agent in AGENT_CAPABILITIES.keys():
            if agent != sender:
                msg = AgentMessage(
                    conversation_id=conversation_id,
                    sender=sender,
                    recipient=agent,
                    message_type=message_type,
                    content=content,
                    topic=topic,
                    round_id=round_id,
                    priority=priority
                )
                self.send(msg)
                msgs.append(msg)
        return msgs

    def get_conversation(self, conversation_id: str) -> List[AgentMessage]:
        return self.conversations.get(conversation_id, [])
