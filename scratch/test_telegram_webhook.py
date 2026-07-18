import asyncio
import sys
import os

# Ensure project root is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, "backend"))

from services.telegram_service import TelegramService
from unittest.mock import AsyncMock, MagicMock

async def run_test():
    print("Testing TelegramService webhook fix...")
    
    # Instantiate service
    ts = TelegramService()
    ts.authorized_chat_id = "12345"
    
    # Mock application
    mock_app = MagicMock()
    mock_bot = AsyncMock()
    mock_app.bot = mock_bot
    ts.application = mock_app
    
    print("Simulating a financial authorization request...")
    
    # Start the request in the background
    auth_task = asyncio.create_task(ts.request_financial_authorization(1500.0, "Purchase new server hardware"))
    
    # Wait a tiny bit to ensure the message was sent
    await asyncio.sleep(0.1)
    
    # Verify the message was sent correctly
    mock_bot.send_message.assert_called_once()
    args, kwargs = mock_bot.send_message.call_args
    assert kwargs['chat_id'] == "12345"
    assert "₹1500.0" in kwargs['text']
    assert "Purchase new server hardware" in kwargs['text']
    
    print("Message sent successfully. Simulating user clicking 'Approve'...")
    
    # Simulate button click
    mock_update = MagicMock()
    mock_query = AsyncMock()
    mock_query.data = "fin_approve"
    mock_update.callback_query = mock_query
    
    await ts._button_callback(mock_update, None)
    
    # Verify button click handler updated caption
    mock_query.edit_message_text.assert_called_once_with(text="✅ Financial Transaction APPROVED by Boss.")
    
    # Await the original request
    result = await auth_task
    
    print(f"Final Result: {result} (Expected: True)")
    
    if result is True:
        print("✅ TEST PASSED: Webhook integration is bulletproof.")
    else:
        print("❌ TEST FAILED: Incorrect result.")

if __name__ == "__main__":
    asyncio.run(run_test())
