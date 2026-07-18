import sys
import os
import json
import asyncio

# Set PYTHONPATH to project root
sys.path.append(os.getcwd())

from core.social_filter import apply_social_filter, how_should_i_talk_to

def test_filter():
    print("--- Testing Social Filter ---")
    
    # Test 1: Annaya (Elder Brother)
    raw_response = "The system failed because of a logic error in the fleet manager."
    context = "Explaining why something went wrong"
    
    print(f"\n[Test 1] Adapting for Annaya (Elder Brother)...")
    result = apply_social_filter(raw_response, "Annaya", context)
    print(f"Adapted Response: {result.get('adapted_response')}")
    print(f"Respect Score: {result.get('respect_score')}")
    
    # Test 2: Ammamma (Grandparent)
    print(f"\n[Test 2] Adapting for Ammamma (Grandparent)...")
    result = apply_social_filter(raw_response, "Ammamma", context)
    print(f"Adapted Response: {result.get('adapted_response')}")
    print(f"Respect Score: {result.get('respect_score')}")
    
    # Test 3: BestFriend (Peer)
    print(f"\n[Test 3] Adapting for BestFriend (Close Friend)...")
    result = apply_social_filter(raw_response, "BestFriend", context)
    print(f"Adapted Response: {result.get('adapted_response')}")
    print(f"Respect Score: {result.get('respect_score')}")

def test_advisor():
    print("\n--- Testing Relationship Advisor ---")
    result = how_should_i_talk_to("Annaya")
    print(f"How to talk to Annaya: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    test_filter()
    test_advisor()
