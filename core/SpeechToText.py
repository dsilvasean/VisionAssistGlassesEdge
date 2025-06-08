from vosk import Model, KaldiRecognizer
import numpy as np
from scipy.signal import resample_poly
import sounddevice as sd
import functools
import asyncio
import json
import re


class SpeechToTextManager:
    def __init__(self, config, result_queue: asyncio.Queue):
        config = config.get("speechToText")
        self.SAMPLE_RATE = config.get("SAMPLE_RATE", 44100)
        self.TARGET_RATE = config.get("TARGET_RATE", 16000)
        self.BLOCK_SIZE = config.get("BLOCK_SIZE", 8192)
        self.INPUT_DEVICE_ID = config.get("INPUT_DEVICE_ID", None)
        self.TIMEOUT = config.get("TIMEOUT", 1.5)
        self.CHANNELS = config.get("CHANNELS", 1)
        self.MODEL_PATH = config.get("MODEL_PATH")
        
        self.audio_queue = asyncio.Queue()
        self.result_queue = result_queue  # Queue where transcribed text is pushed
        self.recognizer = KaldiRecognizer(Model(self.MODEL_PATH), self.TARGET_RATE)
        self.running = True

    def _resample_audio(self, audio_data, original_rate, target_rate):
        if original_rate == target_rate:
            return audio_data
        gcd = np.gcd(original_rate, target_rate)
        up = target_rate // gcd
        down = original_rate // gcd
        audio_data = audio_data.astype(np.float32) / 32767.0
        resampled_data = resample_poly(audio_data, up, down)
        return np.clip(resampled_data * 32767, -32768, 32767).astype(np.int16)

    def _audio_callback(self, indata, frames, time_, status):
        if status:
            print("Audio callback status:", status)
        audio_data = indata[:, 0] if indata.ndim > 1 else indata
        resampled_data = self._resample_audio(audio_data, self.SAMPLE_RATE, self.TARGET_RATE)
        self.audio_queue.put_nowait(resampled_data.tobytes())

    async def listen_to_microphone(self):
        with sd.InputStream(
            device=self.INPUT_DEVICE_ID,
            samplerate=self.SAMPLE_RATE,
            channels=self.CHANNELS,
            dtype="int16",
            blocksize=self.BLOCK_SIZE,
            callback=self._audio_callback,
        ):
            print("Listening to mic...")
            while self.running:
                await asyncio.sleep(0.1)  # Just keep the context alive

    async def process_audio(self):
        buffer = ""
        last_time = asyncio.get_event_loop().time()

        while self.running:
            try:
                data = await asyncio.wait_for(self.audio_queue.get(), timeout=1)
                if self.recognizer.AcceptWaveform(data):
                    result = self.recognizer.Result()
                    text = self._extract_text(result)
                    if text:
                        await self.result_queue.put(text)
                else:
                    partial = self.recognizer.PartialResult()
                
                # Check for silence timeout
                if buffer and asyncio.get_event_loop().time() - last_time > self.TIMEOUT:
                    await self.result_queue.put(buffer.strip())
                    buffer = ""
            except asyncio.TimeoutError:
                continue

    def _extract_text(self, result_json):
        try:
            result = json.loads(result_json)
            return result.get("text", "").strip()
        except Exception:
            return ""
