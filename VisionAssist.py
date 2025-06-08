import asyncio
import json
from core.SpeechToText import SpeechToTextManager
from core.TextToSpeech import TextToSpeechManager
from core.ImageProcessing import ImageProcssingManager
from core.api import API
from core import VisionAssistModes


def load_config(path="config.json"):
    with open(path, "r") as f:
        return json.load(f)


class VisionAssist:
    def __init__(self):
        self.config = load_config()
        self.result_queue = asyncio.Queue()
        self.intent_queue = asyncio.Queue()
        self.general_queue = asyncio.Queue()
        self.ImageProcessor_queue = asyncio.Queue(maxsize=1)
        self.api = API(self.config, self.intent_queue, self.ImageProcessor_queue)
        self.STT = SpeechToTextManager(self.config, self.result_queue)
        self.TTS = TextToSpeechManager(self.config)
        self.imageProcessor = ImageProcssingManager(self.config)
        self.current_mode = self.config.get("SYSTEM_STATES")[0]
        self.mode_lock = asyncio.Lock()
    
    async def switch_mode(self, new_mode:str):
        async with self.mode_lock:
            if self.current_mode != new_mode:
                print(f"switching to {new_mode}")
                await self.TTS.speak(f"Switching to {new_mode} mode")

                mode_func = getattr(VisionAssistModes, f"intent_{new_mode}", None)
                if callable(mode_func):
                    await mode_func(self)
                else:
                    await self.TTS.speak("unknown mode detetected")


    async def handle_intents(self):
        while True:
            intent = await self.intent_queue.get()
            await self.switch_mode(intent)
            print(f"Handling intent: {intent}")
    
    async def greet(self):
        await self.TTS.speak("Hello and welcome to vision assist")

    async def mic_task(self):
        await asyncio.gather(
            self.STT.listen_to_microphone(),
            self.STT.process_audio()
        )

    async def handle_transcriptions(self):
        while True:
            text = await self.result_queue.get()
            print(f"Transcribed: {text}")
            # await self.api.ws.emit("frame", "frame")
            await self.api.get_user_intent(text)

    async def run(self):
        await self.TTS.setup()
        print("Vision Assist Smart Glasses Booting Up...")
        await self.greet()
        await asyncio.gather(
            self.mic_task(),
            self.handle_transcriptions(),
            self.handle_intents()
        )
