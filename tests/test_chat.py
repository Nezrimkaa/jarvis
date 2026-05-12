import pytest
from unittest.mock import MagicMock, patch
from jarvis.ui.chat import ChatWindow


@pytest.fixture
def chat():
    return ChatWindow()


def test_chat_init(chat):
    assert chat is not None
    assert chat.root is not None
    assert chat.root.title() == "Jarvis Assistant"


def test_chat_add_message_user(chat):
    chat._add_message("user", "hello")
    content = chat.chat_display.get("1.0", "end-1c")
    assert "hello" in content


def test_chat_add_message_assistant(chat):
    chat._add_message("assistant", "response")
    content = chat.chat_display.get("1.0", "end-1c")
    assert "response" in content


def test_chat_no_crash_empty_message(chat):
    chat._add_message("user", "")


def test_chat_voice_button(chat):
    assert chat._voice_button is not None
    assert chat._voice_button.cget("text") in ["🎤", "🔴"]
