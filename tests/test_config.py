import pytest
from jarvis.core.config import Settings, load_config


def test_settings_default_values():
    s = Settings()
    assert s.app.name == "Jarvis"
    assert s.app.hotkey == "ctrl+win+z"
    assert s.llm.provider == "github"
    assert s.llm.github_model == "gpt-4o-mini"


def test_settings_custom_values():
    s = Settings(_env_file=None, app={"name": "TestBot", "hotkey": "ctrl+alt+k"})
    assert s.app.name == "TestBot"
    assert s.app.hotkey == "ctrl+alt+k"


def test_settings_deepseek_key():
    s = Settings(_env_file=None)
    assert s.llm.deepseek_key.get_secret_value() == ""


def test_settings_github_key():
    s = Settings(_env_file=None)
    assert s.llm.github_key.get_secret_value() == ""


def test_settings_github_token():
    s = Settings(_env_file=None, github={"token_env": "GITHUB_TOKEN"})
    assert s.github.token_env == "GITHUB_TOKEN"


def test_load_config_returns_settings():
    s = load_config()
    assert isinstance(s, Settings)
