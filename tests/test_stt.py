import pytest
from jarvis.audio.stt import SpeechRecognizer


def test_stt_init_no_model():
    sr = SpeechRecognizer(model_path="nonexistent_path")
    assert sr is not None
    assert sr.is_available is False


def test_stt_init_with_model():
    sr = SpeechRecognizer()
    assert sr is not None
