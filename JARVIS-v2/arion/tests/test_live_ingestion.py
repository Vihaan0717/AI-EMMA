
import asyncio
import json
import os
import sys
from pathlib import Path

# Add arion to path
sys.path.append(os.path.join(os.getcwd(), 'arion'))

from core.message_bus import Channel, Message, MessageBus
from agents.learning_scheduler import LearningScheduler
from agents.orchestrator import Orchestrator

async def test_immediate_ingestion():
    print("Starting Live Ingestion Test...")
    bus = MessageBus()
    
    # Mock config
    config = {
        "ollama_url": "http://localhost:11434",
        "model_name": "llama3.1",
        "db_paths": {
            "learning_queue": "arion/data/test_queue.json",
            "obsidian_vault": "arion/vault",
            "chroma": "arion/data/chromadb"
        }
    }
    
    # Init Scheduler
    scheduler = LearningScheduler(config)
    
    # Init Orchestrator (minimal for this test)
    # Orchestrator needs many files, so we'll just mock the message sending part
    
    print("Simulating message: 'learn movie Hi Nanna: [Script Content]'")
    
    # The Orchestrator's logic we want to test is:
    # 1. Parsing text
    # 2. Sending add_to_queue with priority 9
    
    # Since Orchestrator is heavy, let's just test the scheduler's immediate reaction first.
    test_content = "This is a test script for Hi Nanna. Viraj is a photographer."
    
    payload = {
        "title": "Hi Nanna Test",
        "domain": "movies_series",
        "content": test_content,
        "source_type": "manual_content",
        "priority": 9
    }
    
    # Trigger scheduler
    await scheduler.start()
    
    print("Adding to queue via bus...")
    msg = Message(from_agent="Test", to_channel=Channel.SCHEDULER, action="add_to_queue", payload=payload)
    await bus.publish(msg)
    
    # scheduler.start() runs a loop, and the handle_message handles the bus.
    # However, for handle_message to work, we need to let the loop run.
    # LearningScheduler.run_loop is where it gets messages.
    
    print("Waiting for immediate processing (10s)...")
    await asyncio.sleep(10) 
    
    # Check queue status
    queue = await scheduler._get_queue()
    if queue:
        for item in queue:
            if item["title"] == "Hi Nanna Test":
                print(f"Item found in queue. Status: {item['status']}")
                break
    else:
        print("Queue is empty!")
    
    await scheduler.stop()
    print("Test complete.")

if __name__ == "__main__":
    asyncio.run(test_immediate_ingestion())
