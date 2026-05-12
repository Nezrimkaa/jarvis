import json
from pathlib import Path
from jarvis.utils.logger import get_logger

logger = get_logger("stt")


class SpeechRecognizer:
    def __init__(self, model_path: str = "models/vosk-model-small-ru-0.22", sample_rate: int = 16000):
        self.model_path = model_path
        self.sample_rate = sample_rate
        self._model = None
        self.is_available = self._try_load()

    def _try_load(self) -> bool:
        try:
            import vosk
            model_dir = Path(self.model_path)
            if not model_dir.exists():
                logger.warning(f"Vosk model not found at {self.model_path}. Run: python -m jarvis.utils.download_models")
                return False
            self._model = vosk.Model(str(model_dir))
            logger.info("Vosk model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load Vosk model: {e}")
            return False

    def transcribe(self, audio_data: bytes | None = None, duration: float = 5.0) -> str:
        if not self.is_available:
            return ""

        if audio_data is None:
            return self._record_and_transcribe(duration)

        return self._transcribe_bytes(audio_data)

    def _record_and_transcribe(self, duration: float) -> str:
        import sounddevice as sd
        import numpy as np
        import queue

        q = queue.Queue()

        def callback(indata, frames, time, status):
            if status:
                logger.debug(f"Sounddevice status: {status}")
            q.put(bytes(indata))

        try:
            with sd.RawInputStream(
                samplerate=self.sample_rate, blocksize=8000, dtype="int16",
                channels=1, callback=callback,
            ):
                rec = vosk.KaldiRecognizer(self._model, self.sample_rate)
                for _ in range(int(duration * self.sample_rate / 8000)):
                    data = q.get()
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        if result.get("text"):
                            return result["text"]

                final = json.loads(rec.FinalResult())
                return final.get("text", "")
        except Exception as e:
            logger.error(f"Recording failed: {e}")
            return ""

    def _transcribe_bytes(self, audio_data: bytes) -> str:
        try:
            import vosk
            rec = vosk.KaldiRecognizer(self._model, self.sample_rate)
            rec.AcceptWaveform(audio_data)
            result = json.loads(rec.FinalResult())
            return result.get("text", "")
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return ""
