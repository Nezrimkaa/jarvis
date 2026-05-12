import os
from pathlib import Path
from jarvis.utils.logger import get_logger

logger = get_logger("tts")


class TTSEngine:
    def __init__(self, voice_path: str = "models/piper-voices", voice: str = "ru_RU-irina-medium"):
        self.model_dir = Path(voice_path)
        self.voice = voice
        self.is_available = self._check_models()

    def _check_models(self) -> bool:
        model_file = self.model_dir / f"{self.voice}.onnx"
        if model_file.exists():
            logger.info(f"Piper voice found: {model_file}")
            return True
        logger.warning(f"Piper voice not found at {model_file}")
        logger.info("Download with: python -m jarvis.utils.download_models")
        return False

    def speak(self, text: str) -> bool:
        if not text:
            return False

        if not self.is_available:
            return self._fallback_speak(text)

        try:
            self._piper_speak(text)
            return True
        except Exception as e:
            logger.error(f"Piper TTS failed: {e}, falling back to SAPI")
            return self._fallback_speak(text)

    def _piper_speak(self, text: str):
        import subprocess
        import tempfile
        import wave

        model_path = str(self.model_dir / f"{self.voice}.onnx")
        config_path = str(self.model_dir / f"{self.voice}.onnx.json")

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            subprocess.run(
                ["piper", "--model", model_path, "--output_file", tmp_path],
                input=text.encode("utf-8"), capture_output=True, timeout=30,
            )

            import winsound
            winsound.PlaySound(tmp_path, winsound.SND_FILENAME)
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    def _fallback_speak(self, text: str) -> bool:
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
            return True
        except Exception as e:
            logger.error(f"Fallback TTS failed: {e}")
            return False
