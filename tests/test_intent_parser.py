import pytest
from jarvis.nlu.intent_parser import IntentParser, NLUResponse


@pytest.fixture
def parser():
    return IntentParser()


def test_nlu_response_text_only():
    r = NLUResponse(text="Привет! Чем помочь?")
    assert r.text == "Привет! Чем помочь?"
    assert r.actions == []
    assert r.is_action is False


def test_nlu_response_with_actions():
    r = NLUResponse(
        text="✅ Создаю файл",
        actions=[{"name": "file.create", "params": {"filename": "test.txt"}}],
        is_action=True,
    )
    assert r.actions[0]["name"] == "file.create"
    assert r.actions[0]["params"]["filename"] == "test.txt"


def test_parse_single_action(parser):
    raw = "[ACTION: file.create] filename=test.txt, path=Desktop"
    r = parser.parse_response(raw)
    assert r.is_action is True
    assert len(r.actions) == 1
    assert r.actions[0]["name"] == "file.create"
    assert r.actions[0]["params"]["filename"] == "test.txt"


def test_parse_multiple_actions(parser):
    raw = (
        "[ACTION: folder.create] foldername=project, path=Desktop\n"
        "[ACTION: file.create] filename=main.py, path=Desktop/project"
    )
    r = parser.parse_response(raw)
    assert len(r.actions) == 2
    assert r.actions[0]["name"] == "folder.create"
    assert r.actions[1]["name"] == "file.create"


def test_parse_text_only(parser):
    raw = "Привет! Я Jarvis. Чем могу помочь?"
    r = parser.parse_response(raw)
    assert r.is_action is False
    assert r.actions == []
    assert "Jarvis" in r.text


def test_parse_mixed_text_and_actions(parser):
    raw = "Creating folder...\n[ACTION: folder.create] foldername=test\nDone!"
    r = parser.parse_response(raw)
    assert r.is_action is True
    assert len(r.actions) == 1
    assert r.actions[0]["name"] == "folder.create"
    assert r.actions[0]["params"]["foldername"] == "test"
    assert "Creating" in r.text
    assert "Done" in r.text


def test_build_prompt_includes_context(parser):
    prompt = parser.build_prompt(
        user_message="hello",
        session_context="desktop: C:\\Users\\test\\Desktop",
        dialog_history="user: hi\nassistant: hello",
    )
    assert "hello" in prompt
    assert "desktop" in prompt
    assert "hi" in prompt
