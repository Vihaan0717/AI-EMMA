import asyncio
import uuid
import time
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

class Channel(Enum):
    INTENT = auto()
    EMOTION = auto()
    LANGUAGE = auto()
    MEMORY = auto()
    PERSONA = auto()
    WHATSAPP = auto()
    TELEGRAM = auto()
    VOICE = auto()
    CODING = auto()
    PREDICTION = auto()
    COMPREHENSION = auto()
    LIFE = auto()
    SYSTEM_HEALTH = auto()
    AGENT_HEALTH = auto()
    ORCHESTRATOR = auto()
    PRIVACY = auto()
    KNOWLEDGE = auto()
    SCHEDULER = auto()
    MONITOR = auto()
    INTAKE = auto()
    # ── ARION 3.0 — Cognitive channels ─────────────────────────────────────
    DEEP_LANGUAGE = auto()   # DeepLanguageEngine — phonetic + pragmatics (A0)
    COGNITION     = auto()   # CognitionEngine    — prefrontal cortex     (A5)
    REFLECTION    = auto()   # ReflectionEngine   — post-response learner  (A8)
    GOAL          = auto()   # GoalEngine         — 24h proactive goals    (A9)

    BROADCAST = auto()

class Priority(Enum):
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5

@dataclass(order=True)
class Message:
    # Priority for queue ordering
    priority: int = field(init=False)
    
    # Message fields
    id: str = field(default_factory=lambda: str(uuid.uuid4()), compare=False)
    from_agent: str = field(default="unknown", compare=False)
    to_channel: Channel = field(default=Channel.BROADCAST, compare=False)
    action: str = field(default="none", compare=False)
    payload: Dict[str, Any] = field(default_factory=dict, compare=False)
    priority_level: Priority = field(default=Priority.NORMAL, compare=False)
    timestamp: float = field(default_factory=time.time, compare=False)
    requires_response: bool = field(default=False, compare=False)
    response_to: Optional[str] = field(default=None, compare=False)
    ttl: float = field(default=60.0, compare=False) # Time to live in seconds
    
    def __post_init__(self):
        # lower integer = higher priority in PriorityQueue
        self.priority = self.priority_level.value

class MessageBus:
    _instance = None
    _bus_lock: Optional[asyncio.Lock] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MessageBus, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    @property
    def _lock(self) -> asyncio.Lock:
        """Lazy-initialize the lock within the active event loop context."""
        if self._bus_lock is None:
            self._bus_lock = asyncio.Lock()
        return self._bus_lock

    def __init__(self):
        if hasattr(self, 'initialized') and self.initialized:
            return
        self.subscribers: Dict[Channel, List[asyncio.Queue]] = {channel: [] for channel in Channel}
        self.pending_responses: Dict[str, asyncio.Future] = {}
        self.initialized = True
        
    async def subscribe(self, channel: Channel) -> asyncio.Queue:
        """Subscribe to a specific channel."""
        queue = asyncio.PriorityQueue()
        async with self._lock:
            self.subscribers[channel].append(queue)
        return queue

    async def unsubscribe(self, channel: Channel, queue: asyncio.Queue):
        """Unsubscribe from a specific channel."""
        async with self._lock:
            if queue in self.subscribers[channel]:
                self.subscribers[channel].remove(queue)

    async def publish(self, message: Message):
        """Publish a message to its target channel and BROADCAST."""
        # Handle responses to previous requests
        if message.response_to and message.response_to in self.pending_responses:
            future = self.pending_responses.pop(message.response_to)
            if not future.done():
                future.set_result(message)
            return

        target_queues = []
        async with self._lock:
            if message.to_channel == Channel.BROADCAST:
                for queues in self.subscribers.values():
                    target_queues.extend(queues)
            else:
                target_queues.extend(self.subscribers[message.to_channel])

            for queue in target_queues:
                await queue.put(message)

    async def request(self, message: Message, timeout: float = 30.0) -> Optional[Message]:
        """Publish a message and wait for a response."""
        message.requires_response = True
        future = asyncio.get_running_loop().create_future()
        self.pending_responses[message.id] = future
        
        await self.publish(message)
        
        try:
            # FIX: Internal timeout to manage the future
            return await asyncio.wait_for(future, timeout=timeout)
        except (asyncio.TimeoutError, asyncio.CancelledError):
            # FIX: Ensure cleanup on cancellation (e.g., from Orchestrator's wait_for)
            if message.id in self.pending_responses:
                del self.pending_responses[message.id]
            return None
        finally:
            # Final safety check
            if message.id in self.pending_responses:
                del self.pending_responses[message.id]
