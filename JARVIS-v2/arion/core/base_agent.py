import asyncio
import traceback
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from .message_bus import MessageBus, Channel, Message, Priority

class BaseAgent(ABC):
    def __init__(self, name: str, channels: List[Channel], heartbeat_interval: int = 10):
        self.name = name
        self.channels = channels
        self.channels.append(Channel.BROADCAST) # Auto subscribe to broadcast
        self.heartbeat_interval = heartbeat_interval
        self.bus = MessageBus()
        self.queues: List[asyncio.Queue] = []
        self.running = False
        self._loop_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the agent and subscribe to channels."""
        self.running = True
        for channel in set(self.channels):
            queue = await self.bus.subscribe(channel)
            self.queues.append(queue)
            
        self._loop_task = asyncio.create_task(self._safe_run_loop())
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        print(f"[{self.name}] Started.")

    async def stop(self):
        """Stop the agent and unsubscribe."""
        self.running = False
        if self._loop_task:
            self._loop_task.cancel()
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            
        for queue, channel in zip(self.queues, set(self.channels)):
            await self.bus.unsubscribe(channel, queue)
        self.queues.clear()
        print(f"[{self.name}] Stopped.")

    async def _safe_run_loop(self):
        """Wraps run_loop with try/except and reports errors."""
        try:
            await self.run_loop()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            error_trace = traceback.format_exc()
            print(f"[{self.name}] Crashed! {e}")
            await self.send(
                to_channel=Channel.AGENT_HEALTH,
                action="agent_crash",
                payload={"agent": self.name, "error": str(e), "traceback": error_trace},
                priority=Priority.CRITICAL
            )

    async def _heartbeat_loop(self):
        """Sends periodic heartbeats to AGENT_HEALTH channel."""
        while self.running:
            try:
                await self.send(
                    to_channel=Channel.AGENT_HEALTH,
                    action="heartbeat",
                    payload={"agent": self.name, "timestamp": time.time()}
                )
            except Exception:
                pass
            await asyncio.sleep(self.heartbeat_interval)

    async def send(self, to_channel: Channel, action: str, payload: Dict[str, Any], priority: Priority = Priority.NORMAL, requires_response: bool = False) -> str:
        """Helper to send a message."""
        msg = Message(
            from_agent=self.name,
            to_channel=to_channel,
            action=action,
            payload=payload,
            priority_level=priority,
            requires_response=requires_response
        )
        await self.bus.publish(msg)
        return msg.id

    async def respond_to(self, original_msg: Message, action: str, payload: Dict[str, Any], priority: Priority = Priority.NORMAL):
        """Helper to send a response to a specific message."""
        if not original_msg.requires_response:
            return
        
        msg = Message(
            from_agent=self.name,
            to_channel=Channel.BROADCAST,
            action=action,
            payload=payload,
            priority_level=priority,
            response_to=original_msg.id
        )
        await self.bus.publish(msg)

    async def get_next_message(self, timeout: Optional[float] = None) -> Optional[Message]:
        """Gets next message from any of the subscribed queues."""
        if not self.queues:
            return None
            
        # Create tasks to wait on all queues
        tasks = [asyncio.create_task(q.get()) for q in self.queues]
        
        try:
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED, timeout=timeout)
            
            # Cancel pending tasks to prevent memory leaks
            for task in pending:
                task.cancel()
                
            if not done:
                return None
                
            return done.pop().result()
        except Exception:
            for task in tasks:
                if not task.done():
                    task.cancel()
            return None

    @abstractmethod
    async def handle_message(self, message: Message):
        """Handle an incoming message."""
        pass

    @abstractmethod
    async def run_loop(self):
        """The main loop of the agent."""
        pass
