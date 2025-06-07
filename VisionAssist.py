import asyncio
import json
from core.SpeechToText import SpeechToTextManager
from utils.api import API


def load_config(path="config.json"):
    with open(path, "r") as f:
        return json.load(f)


class VisionAssist:
    def __init__(self):
        self.config = load_config()
        self.api = API(host=self.config.get("server_url"))
        self.result_queue = asyncio.Queue()
        self.STT = SpeechToTextManager(self.config, self.result_queue)

    async def mic_task(self):
        await asyncio.gather(
            self.STT.listen_to_microphone(),
            self.STT.process_audio()
        )

    async def handle_transcriptions(self):
        while True:
            text = await self.result_queue.get()
            print(f"📝 Transcribed: {text}")
            # await self.api.send_text(text)  # Replace with your actual method

    async def run(self):
        print("👓 Vision Assist Smart Glasses Booting Up...")
        await asyncio.gather(
            self.mic_task(),
            self.handle_transcriptions()
        )
