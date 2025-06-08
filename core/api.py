import httpx
import asyncio


class API:
    """This class is responsible for the actual communication between the edge device and the cloud"""
    def __init__(self, config, intent_queue:asyncio.Queue):
        self.config = config.get("server")
        self.API_ROOT = f"http://{self.config.get('HOST')}:{self.config.get('PORT')}/api"
        self.intent_queue = intent_queue  # Shared queue


    async def get_user_intent(self, data:str) -> str:
        try:
            payload = {"query":data}
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.API_ROOT}/get_intent", json=payload)

            if response.status_code == 200:
                intent = response.json().get("predicted_intent")
                print(f"[API] ➜ Intent detected: {intent}")
                await self.intent_queue.put(intent)
            else:
                print(f"[API] Error: {response.status_code}")
            
        except Exception as e:
            print(f"[API] Exception: {e}")






