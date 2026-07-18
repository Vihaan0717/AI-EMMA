import logging
import asyncio
from typing import Optional
from brain.agents.vision_hand_agent import VisionHandAgent

logger = logging.getLogger("Nexus.FoodOrderAgent")

class FoodOrderAgent:
    """
    Orchestrates the food ordering process (e.g., Swiggy, Zomato).
    """
    def __init__(self, vision_hand: Optional[VisionHandAgent] = None):
        self.hand = vision_hand or VisionHandAgent()

    async def order_food(self, item: str, restaurant: Optional[str] = None) -> str:
        """
        Main loop for ordering food.
        """
        logger.info(f"Starting food order: {item} from {restaurant or 'anywhere'}")
        
        # 1. Search for restaurant/item
        search_query = f"{item} {restaurant if restaurant else ''}"
        logger.info(f"Searching for: {search_query}")
        
        # Example steps:
        # a. Click search bar
        res = await self.hand.type_in_element("the search bar or search icon", search_query + "\n")
        if "Successfully" not in res: return res
        
        await asyncio.sleep(2) # Wait for results
        
        # b. Click the first restaurant/item
        res = await self.hand.find_and_click("the first food item or restaurant in the list")
        if "Successfully" not in res: return res
        
        await asyncio.sleep(1)
        
        # c. Click 'Add' button
        res = await self.hand.find_and_click("the 'Add' or 'Add to Cart' button")
        if "Successfully" not in res: return res
        
        # d. Click 'View Cart'
        res = await self.hand.find_and_click("the 'View Cart' or 'Checkout' button")
        if "Successfully" not in res: return res
        
        return f"Food order for {item} initiated. JARVIS is waiting for your final confirmation at checkout."

async def test_order():
    agent = FoodOrderAgent()
    # Note: This will fail until Moondream is installed and a food app is open.
    result = await agent.order_food("Biryani")
    print(result)

if __name__ == "__main__":
    # asyncio.run(test_order())
    print("FoodOrderAgent ready. Waiting for VLM stack to complete.")
