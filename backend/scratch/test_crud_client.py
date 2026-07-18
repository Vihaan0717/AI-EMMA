import asyncio
import websockets
import json

async def run_client():
    uri = "ws://localhost:8000/crud"
    print(f"Connecting to CRUD stream at {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            # 1. Listen for initial state
            init_msg = await websocket.recv()
            print(f"\n[INIT STATE RECEIVE]\n{json.dumps(json.loads(init_msg), indent=2)}")

            # 2. Simulate CREATE action from UI
            create_cmd = {
                "action": "create",
                "title": "Learn Telugu startup terms",
                "importance": 0.85
            }
            print(f"\n[SENDING CREATE ACTION] -> {create_cmd['title']}")
            await websocket.send(json.dumps(create_cmd))

            # Listen for transition thinking state
            thinking_msg = await websocket.recv()
            print(f"[TRANSITION STATE RECEIVE] -> isThinking: {json.loads(thinking_msg).get('isThinking')}")

            # Listen for final updated broadcast
            update_msg = await websocket.recv()
            print(f"[UPDATED STATE RECEIVE]\n{json.dumps(json.loads(update_msg), indent=2)}")

            # 3. Simulate DELETE action
            last_state = json.loads(update_msg)
            added_id = last_state["dataList"][-1]["id"]
            
            delete_cmd = {
                "action": "delete",
                "id": added_id
            }
            print(f"\n[SENDING DELETE ACTION] -> ID: {added_id}")
            await websocket.send(json.dumps(delete_cmd))

            # Listen for state transitions
            await websocket.recv() # thinking state
            delete_finish_msg = await websocket.recv()
            print(f"[FINAL STATE RECEIVE]\n{json.dumps(json.loads(delete_finish_msg), indent=2)}")

    except Exception as e:
        print(f"Error: {e}. Make sure the backend server (python backend/main.py) is running on port 8000.")

if __name__ == "__main__":
    asyncio.run(run_client())
