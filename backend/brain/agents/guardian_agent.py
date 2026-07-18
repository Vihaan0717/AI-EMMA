import logging
import asyncio
from typing import Dict, Any, Optional

logger = logging.getLogger("Nexus.GuardianAgent")

class GuardianAgent:
    """
    Handles secure handshakes and approvals for sensitive actions.
    Routes requests to Telegram or the mobile app for user confirmation.
    """
    def __init__(self, bus=None, telegram_bridge=None):
        self.bus = bus
        self.telegram = telegram_bridge
        self._pending_approvals = {}

    async def request_approval(self, action_type: str, details: str, timeout: int = 60) -> bool:
        """
        Sends an approval request to the user and waits for a response.
        """
        request_id = f"req_{int(asyncio.get_event_loop().time())}"
        logger.info(f"[Guardian] Requesting approval for {action_type}: {details}")
        
        # 1. Format the message
        msg = f"🛡️ GUARDIAN APPROVAL REQUIRED\n\nACTION: {action_type}\nDETAILS: {details}\n\nReply 'APPROVE' or 'DENY'."
        
        # 2. Send to Telegram (if available)
        if self.telegram:
            await self.telegram.send_admin_message(msg)
        
        # 3. Emit to MessageBus for the App
        if self.bus:
            self.bus.publish("guardian", "approval_request", {
                "id": request_id,
                "type": action_type,
                "details": details
            })

        # 4. Wait for response (poll pending_approvals)
        self._pending_approvals[request_id] = None
        
        try:
            for _ in range(timeout):
                if self._pending_approvals.get(request_id) is not None:
                    result = self._pending_approvals[request_id]
                    del self._pending_approvals[request_id]
                    return result
                await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Approval wait error: {e}")
        
        # Timeout = Denied by default
        logger.warning(f"[Guardian] Approval timeout for {request_id}")
        if request_id in self._pending_approvals:
            del self._pending_approvals[request_id]
        return False

    def handle_response(self, request_id: str, approved: bool):
        """Called by the bridge/bus when a user responds."""
        if request_id in self._pending_approvals:
            self._pending_approvals[request_id] = approved
            logger.info(f"[Guardian] Approval {request_id} received: {approved}")
