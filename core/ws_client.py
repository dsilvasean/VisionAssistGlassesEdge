import socketio
import asyncio
import datetime


class WebSocketClient:
    def __init__(self, config, general_queue:asyncio.Queue):
        self.config = config
        self.sio = socketio.AsyncClient()
        self.WEBSOCKET_ENDPOINT = f"ws://{self.config.get('HOST')}:{self.config.get('PORT')}"
        self.ws_url = self.WEBSOCKET_ENDPOINT
        self.result_queue = general_queue
        self._register_callbacks()
    
    async def connect(self):
        await self.sio.connect(self.ws_url, transports=["websocket"])
        print("[WebSocket] Connected to server.")

    async def emit(self, event:str, data):
        try:
            await self.sio.emit(event, {"uid" : datetime.datetime.now().timestamp(), "frame":data.tobytes(), "distance_info":[0, 0]})
            print("event sent")
            print(f"[WebSocket] Sent event: {event} with data: {data}")
        except Exception as e:
            print(f"[WebSocket] Emit failed: {e}")


    def _register_callbacks(self):
        @self.sio.event
        async def connect():
            print("[WebSocket] Connection successful.")
        
        @self.sio.event
        async def message(data):
            try:
                # Remove the old value if present
                self.result_queue.get_nowait()
            except asyncio.QueueEmpty:
                pass
            await self.result_queue.put((True, "intent_scene_description", str(data).strip()))
    
    async def wait_forever(self):
        await self.sio.wait()


