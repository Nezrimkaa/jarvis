"""Integration tests for Jarvis assistant pipeline."""
import pytest
from unittest.mock import AsyncMock
from jarvis.core.session import Session
from jarvis.actions.dispatcher import ActionDispatcher
from jarvis.actions.file_ops import FileOperator
from jarvis.actions.system_cmd import SystemCmd


@pytest.fixture
def session():
    return Session()


@pytest.fixture
def dispatcher():
    d = ActionDispatcher()
    d.register("file.create", lambda i, e, s: f"✅ Файл {e.get('filename', '')} создан")
    d.register("folder.create", lambda i, e, s: f"✅ Папка {e.get('foldername', '')} создана")
    d.register("shell.run", lambda i, e, s: SystemCmd().run(e.get("command", ""))["stdout"])
    d.register("assistant.help", lambda i, e, s: "Справка...")
    return d


class TestNluEngine:
    """Test the NLU engine with mock LLM."""

    @pytest.fixture
    def mock_parser(self):
        """Mock parser that returns predefined responses."""
        class MockParser:
            async def parse(self, text, session_context="", dialog_history=""):
                from jarvis.nlu.intent_parser import NLUResponse
                if "создай" in text.lower() and "файл" in text.lower():
                    return NLUResponse(
                        text="✅ Создаю файл",
                        actions=[{"name": "file.create", "params": {"filename": "test.txt"}}],
                        is_action=True,
                    )
                if "создай" in text.lower() and "папк" in text.lower():
                    return NLUResponse(
                        text="✅ Создаю папку",
                        actions=[{"name": "folder.create", "params": {"foldername": "test_folder"}}],
                        is_action=True,
                    )
                if "echo" in text.lower():
                    return NLUResponse(
                        text="",
                        actions=[{"name": "shell.run", "params": {"command": "echo hello"}}],
                        is_action=True,
                    )
                if "проект" in text.lower():
                    return NLUResponse(
                        text="✅ Создаю проект",
                        actions=[
                            {"name": "folder.create", "params": {"foldername": "my_project", "path": "."}},
                            {"name": "file.create", "params": {"filename": "main.py", "path": "./my_project"}},
                        ],
                        is_action=True,
                    )
                if "помощ" in text.lower() or "help" in text.lower():
                    return NLUResponse(text="Справка...")
                return NLUResponse(text="Не понял", raw=text)

        return MockParser()

    @pytest.mark.asyncio
    async def test_simple_file_create(self, mock_parser):
        r = await mock_parser.parse("создай файл test.txt")
        assert r.is_action is True
        assert r.actions[0]["name"] == "file.create"

    @pytest.mark.asyncio
    async def test_multi_step_project(self, mock_parser):
        r = await mock_parser.parse("создай проект на десктопе")
        assert len(r.actions) == 2
        assert r.actions[0]["name"] == "folder.create"
        assert r.actions[1]["name"] == "file.create"

    @pytest.mark.asyncio
    async def test_help_returns_text(self, mock_parser):
        r = await mock_parser.parse("помощь")
        assert r.is_action is False
        assert "Справка" in r.text

    def test_execute_plan(self, dispatcher, session):
        actions = [
            {"name": "folder.create", "params": {"foldername": "p"}},
            {"name": "file.create", "params": {"filename": "f.txt"}},
        ]
        results = dispatcher.execute_plan(actions, session)
        assert len(results) == 2
        assert "Папка" in results[0]
        assert "Файл" in results[1]

    def test_session_dialog(self, session):
        session.add_message("user", "создай файл")
        session.add_message("assistant", "✅ Файл создан")
        assert len(session.dialog) == 2
        assert "создай файл" in session.get_dialog_prompt()
