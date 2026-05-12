import pytest
from jarvis.audio.tts import TTSEngine


def test_tts_init_no_voice():
    tts = TTSEngine(voice_path="nonexistent")
    assert tts.is_available is False


def test_tts_init():
    tts = TTSEngine()
    assert tts is not None


@pytest.mark.skip(reason="Requires actual voice model")
def test_tts_speak():
    tts = TTSEngine()
    result = tts.speak("тест")
    assert result is True
