import os
from piper.voice import PiperVoice
import sounddevice as sd
import asyncio
import tempfile
import wave
import soundfile as sf



class TextToSpeechManager:
    """This class handles the text to speech """
    def __init__(self, config):
        self.config = config.get("textToSpeech")
        print(self.config)
        self.PIPER_VOICEDIR = os.path.expanduser(self.config.get("PIPER_VOICE_DIR"))  
        self.PIPER_MODEL = os.path.join(self.PIPER_VOICEDIR, self.config.get("PIPER_MODEL")) 
        self.voice = PiperVoice.load(self.PIPER_MODEL)  
        self.LENGTH_SCALE = config.get("LENGTH_SCALE")
        self.PLAYBACK_DEVICE = sd.default.device[self.config.get("PLAYBACK_DEVICE_ID")]

        self.queue = asyncio.PriorityQueue()
        self.processing_task = None
    
    async def setup(self):
        self.processing_task = asyncio.create_task(self._process_queue())
        print("TTSManager Initialized")

        
    async def speak(self, text:str, priority: int = 5):
        future = asyncio.get_running_loop().create_future()
        await self.queue.put((priority, text, future))
        await future

    async def _synthesize(self, text:str,) -> str:
        """Generate wav file from text"""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            with wave.open(temp_filename, 'wb') as wav_file:
                wav_file.setnchannels(self.config.get("WAV_CHANNEL"))
                wav_file.setsampwidth(self.config.get("WAV_SAMPLE_WIDTH"))
                wav_file.setframerate(self.config.get("WAV_FRAMERATE"))
                self.voice.synthesize(text, wav_file, length_scale=self.LENGTH_SCALE)
                return temp_filename
        except Exception as e:
            print(f"[TTS Error] synthesis failed : {e}")
            return None
        
    async def _play_audio(self, filename:str):
        try:
            data, fs = sf.read(filename, dtype='float32')
            sd.play(data, samplerate=fs, device=self.PLAYBACK_DEVICE)

            while sd.get_stream().active:
                await asyncio.sleep(0.1)
        except Exception as e:
            print(f"TTS ERROR Playback Failed: {e}")
        finally:
            if os.path.exists(filename):
                os.remove(filename)

    async def _process_queue(self):
        """Main async loop to process TTS queue by priority"""
        while True:
            priority, text, future = await self.queue.get()
            print(f"[TTS] (Priority {priority}) Speaking: {text}")

            wav_file = await self._synthesize(text)
            print(wav_file)
            if wav_file:
                await self._play_audio(wav_file)
            
            if not future.done():
                future.set_result(True)
            self.queue.task_done()
    
    async def play_notification_sound(self,):
        path = self.config.get("NOTIFICATION_SOUND")
        if not os.path.exists(path):
            print(f"[TTS Warning] Notification file not found: {path}")
            return

        try:
            data, fs = sf.read(path, dtype="float32")
            sd.play(data, samplerate=fs, device=self.PLAYBACK_DEVICE)

            while sd.get_stream().active:
                await asyncio.sleep(0.1)
        
        except Exception as e:
            print(f"[TTS Error] Notification playback failed: {e}")









        