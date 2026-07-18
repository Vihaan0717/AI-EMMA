"""
NEXUS-X OMEGA Message Bus
Async pub/sub backbone connecting all agents
"""

import asyncio
import logging
import uuid
from typing import Dict, Callable, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

logger = logging.getLogger('MessageBus')


class Channel(Enum):
    ORCHESTRATOR  = "orchestrator"
    LANGUAGE      = "language"
    MEMORY        = "memory"
    INTENT        = "intent"
    COMPREHENSION = "comprehension"
    VOICE         = "voice"
    VISION        = "vision"
    WHATSAPP      = "whatsapp"
    TELEGRAM      = "telegram"
    TOOLS         = "tools"
    HEALER        = "healer"
    BACKGROUND    = "background"
    LEARNING      = "learning"
    EMOTION       = "emotion"
    PLANNING      = "planning"
    BROADCAST     = "broadcast"


@dataclass
class Message:
    channel: str
    event: str
    data: Any
    sender: str = "system"
    correlation_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )
    priority: int = 5  # 1=highest, 10=lowest
    reply_to: Optional[str] = None


class MessageBus:
    """
    Central nervous system message router
    High-performance async pub/sub
    """

    def __init__(self):
        self.subscribers: Dict[str, list] = defaultdict(list)
        self.pending_replies: Dict[str, asyncio.Future] = {}
        self.message_queue: asyncio.PriorityQueue = None
        self.is_running = False
        self.stats = {
            "total_messages": 0,
            "messages_per_channel": defaultdict(int)
        }

    async def start(self):
        """Start the message bus"""
        self.message_queue = asyncio.PriorityQueue()
        self.is_running = True
        asyncio.create_task(self._process_loop())
        logger.info("📡 Message Bus started")

    async def publish(
        self,
        channel: str,
        event: str,
        data: Any,
        sender: str = "system",
        priority: int = 5
    ):
        """Publish message to a channel"""
        msg = Message(
            channel=channel,
            event=event,
            data=data,
            sender=sender,
            priority=priority
        )
        await self.message_queue.put((priority, msg))
        self.stats["total_messages"] += 1
        self.stats["messages_per_channel"][channel] += 1

    async def request(
        self,
        channel: str,
        event: str,
        data: Any,
        sender: str = "system",
        timeout: float = 30.0
    ) -> Any:
        """Request-response pattern"""
        correlation_id = str(uuid.uuid4())
        future = asyncio.get_event_loop().create_future()
        self.pending_replies[correlation_id] = future

        msg = Message(
            channel=channel,
            event=event,
            data=data,
            sender=sender,
            correlation_id=correlation_id,
            reply_to=correlation_id
        )

        await self.message_queue.put((5, msg))

        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            self.pending_replies.pop(correlation_id, None)
            raise TimeoutError(
                f"Request to {channel}/{event} timed out"
            )

    def subscribe(
        self,
        channel: str,
        handler: Callable,
        event_filter: str = None
    ):
        """Subscribe to a channel"""
        self.subscribers[channel].append({
            "handler": handler,
            "event_filter": event_filter
        })

    async def reply(self, correlation_id: str, data: Any):
        """Reply to a request"""
        if correlation_id in self.pending_replies:
            future = self.pending_replies.pop(correlation_id)
            if not future.done():
                future.set_result(data)

    async def _process_loop(self):
        """Main message processing loop"""
        while self.is_running:
            try:
                priority, msg = await asyncio.wait_for(
                    self.message_queue.get(), timeout=1.0
                )
                await self._dispatch(msg)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Bus error: {e}")

    async def _dispatch(self, msg: Message):
        """Dispatch message to subscribers"""
        channels_to_check = [msg.channel, Channel.BROADCAST.value]

        for channel in channels_to_check:
            for sub in self.subscribers.get(channel, []):
                ef = sub.get("event_filter")
                if ef is None or ef == msg.event:
                    try:
                        await sub["handler"](msg)
                    except Exception as e:
                        logger.error(
                            f"Handler error [{channel}]: {e}"
                        )

    def stop(self):
        self.is_running = False
