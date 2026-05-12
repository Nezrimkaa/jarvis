import pytest
from jarvis.core.session import Session


def test_session_initial_state():
    s = Session()
    assert s.context["state"] == "idle"
    assert s.dialog == []


def test_add_message():
    s = Session()
    s.add_message("user", "hello")
    assert len(s.dialog) == 1
    assert s.dialog[0]["role"] == "user"
    assert s.dialog[0]["text"] == "hello"


def test_multiple_messages():
    s = Session()
    s.add_message("user", "hi")
    s.add_message("assistant", "hello there")
    assert len(s.dialog) == 2
    assert s.dialog[1]["role"] == "assistant"


def test_context_update():
    s = Session()
    s.update_context("last_file", "/test/file.txt")
    assert s.context["last_file"] == "/test/file.txt"


def test_context_prompt_contains_info():
    s = Session()
    prompt = s.get_context_prompt()
    assert "Рабочий стол" in prompt
    assert "Текущая директория" in prompt


def test_dialog_prompt():
    s = Session()
    s.add_message("user", "create a file")
    s.add_message("assistant", "done")
    prompt = s.get_dialog_prompt()
    assert "create a file" in prompt
    assert "done" in prompt


def test_dialog_prompt_empty():
    s = Session()
    assert "пуста" in s.get_dialog_prompt()


def test_reset():
    s = Session()
    s.add_message("user", "test")
    s.update_context("last_command", "test")
    s.reset()
    assert s.dialog == []
    assert s.context["last_command"] is None


def test_to_dict():
    s = Session()
    s.add_message("user", "hello")
    d = s.to_dict()
    assert "session_id" in d
    assert d["dialog"][0]["text"] == "hello"
