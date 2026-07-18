import logging
import asyncio
from typing import Optional, List, Dict
from brain.agents.vision_hand_agent import VisionHandAgent
from core.ai_engine import AIEngine
from services.hand_service import HandService
from config.system_config import JarvisConfig

logger = logging.getLogger("Nexus.AutonomousOrderAgent")

class AutonomousOrderAgent:
    """
    Advanced agent for autonomous commerce (Comparison -> Approval -> Ordering -> Tracking).
    """
    def __init__(self, vision_hand: Optional[VisionHandAgent] = None):
        self.hand = vision_hand or VisionHandAgent()
        self.ai = self.hand.ai
        self.hands = self.hand.hands

    async def run_market_analysis(self, item: str) -> str:
        """
        Scans the screen, scrolls, and compares options.
        """
        logger.info(f"Analyzing market for {item}...")
        
        # 1. Initial Scan
        data1 = await self.hand.extract_screen_data("List the options with their prices and ratings.")
        
        # 2. Scroll and Scan again
        self.hands.scroll(-500) # Scroll down
        await asyncio.sleep(1)
        data2 = await self.hand.extract_screen_data("List any additional options visible after scrolling.")
        
        # 3. Use Reasoning Model to compare with Budget and Location constraints
        comparison_prompt = f"""
        Based on these two data sets from the screen:
        Set 1: {data1}
        Set 2: {data2}
        
        USER CONSTRAINTS:
        - Current Location: {JarvisConfig.USER_LOCATION}
        - Maximum Budget: {JarvisConfig.ORDER_BUDGET} INR
        
        Identify the best option for '{item}' based on:
        1. Must be WITHIN the budget of {JarvisConfig.ORDER_BUDGET} INR.
        2. Proximity to {JarvisConfig.USER_LOCATION} (favor local results if possible).
        3. Highest rating among budget-friendly options.
        
        Return a summary of the top 3 options that FIT the budget and your recommendation.
        """
        analysis = await self.ai.generate(comparison_prompt)
        return analysis

    async def request_order_approval(self, recommendation: str, target_jid: str):
        """
        Sends the recommendation to WhatsApp and waits for approval.
        """
        # Note: In a real system, this would use the WhatsAppBridge
        message = f"🤖 JARVIS Order Proposal:\n\n{recommendation}\n\nShall I proceed with the recommended order? (Reply with 'Yes' or 'No')"
        
        # Mocking the send (would use WhatsAppBridge in production)
        print(f"--- WHATSAPP TO {target_jid} ---")
        print(message)
        print("-------------------------------")
        
        # In a real agent loop, this would wait for an event from the MessageBus
        return "Waiting for approval..."

    async def track_order(self) -> str:
        """
        Periodically checks the screen for order status updates.
        """
        logger.info("Tracking order status...")
        status = await self.hand.extract_screen_data("What is the current status of the order? (e.g., Prepared, Out for delivery)")
        return status

async def demo_autonomous_flow():
    agent = AutonomousOrderAgent()
    
    # 1. Compare
    analysis = await agent.run_market_analysis("Biryani")
    print(f"Analysis:\n{analysis}")
    
    # 2. Ask Permission
    await agent.request_order_approval(analysis, "919154716156@c.us")
    
    # 3. If approved (mocked)
    print("Approval received! Proceeding to order...")
    # await agent.hand.find_and_click("the 'Order Now' or 'Confirm' button")

if __name__ == "__main__":
    # asyncio.run(demo_autonomous_flow())
    print("AutonomousOrderAgent initialized.")
