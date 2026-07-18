import asyncio
import websockets
import json
import math

class DummyServer:
    def __init__(self, port=8001):
        self.port = port
        self.clients = set()
        self.is_running = True

    async def register(self, websocket):
        self.clients.add(websocket)
        try:
            await websocket.wait_closed()
        finally:
            self.clients.remove(websocket)

    async def broadcast(self, data):
        if not self.clients:
            return
        message = json.dumps(data)
        await asyncio.gather(*[client.send(message) for client in self.clients], return_exceptions=True)

    async def start_server(self):
        async with websockets.serve(self.register, "localhost", self.port):
            print(f"Dummy Server running on ws://localhost:{self.port}")
            await self.test_dummy_motion()

    async def test_dummy_motion(self):
        t = 0
        while self.is_running:
            head_angle = math.sin(t) * 0.5
            arm_angle = math.cos(t) * 0.5
            
            payload = {
                "bones": {
                    "head": {"x": 0, "y": math.sin(head_angle/2), "z": 0, "w": math.cos(head_angle/2)},
                    "leftUpperArm": {"x": 0, "y": 0, "z": math.sin(arm_angle/2), "w": math.cos(arm_angle/2)},
                    "rightUpperArm": {"x": 0, "y": 0, "z": -math.sin(arm_angle/2), "w": math.cos(arm_angle/2)}
                },
                "blendshapes": {
                    "A": (math.sin(t*2) + 1) / 2
                }
            }
            await self.broadcast(payload)
            t += 0.1
            await asyncio.sleep(0.05)

if __name__ == "__main__":
    server = DummyServer()
    asyncio.run(server.start_server())
