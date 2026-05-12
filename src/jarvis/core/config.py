from pathlib import Path
from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    name: str = "Jarvis"
    version: str = "0.1.0"
    hotkey: str = "ctrl+win+z"


class AudioSTTConfig(BaseSettings):
    engine: str = "vosk"
    model_path: str = "models/vosk-model-small-ru-0.22"
    sample_rate: int = 16000


class AudioTTSConfig(BaseSettings):
    engine: str = "piper"
    model_path: str = "models/piper-voices"
    voice: str = "ru_RU-irina-medium"


class AudioConfig(BaseSettings):
    stt: AudioSTTConfig = AudioSTTConfig()
    tts: AudioTTSConfig = AudioTTSConfig()


class LLMConfig(BaseSettings):
    provider: str = "github"  # "deepseek" or "github"
    model: str = "gpt-4o-mini"  # deepseek-coder / deepseek-chat / gpt-4o-mini
    temperature: float = 0.3
    max_tokens: int = 4096
    endpoint: str = "https://models.inference.ai.azure.com"
    # DeepSeek
    deepseek_key: SecretStr = Field(default=SecretStr(""), alias="DEEPSEEK_API_KEY")
    deepseek_endpoint: str = "https://api.deepseek.com/v1"
    deepseek_model: str = "deepseek-coder"
    # GitHub Models
    github_key: SecretStr = Field(default=SecretStr(""), alias="GITHUB_TOKEN")
    github_endpoint: str = "https://models.inference.ai.azure.com"
    github_model: str = "gpt-4o-mini"


class GitHubConfig(BaseSettings):
    token_env: str = "GITHUB_TOKEN"
    default_repo: str = ""


class UIConfig(BaseSettings):
    tray_tooltip: str = "Jarvis Assistant"
    overlay_width: int = 400
    overlay_height: int = 300
    overlay_opacity: float = 0.9


class LoggingConfig(BaseSettings):
    level: str = "DEBUG"
    file: str = "logs/jarvis.log"
    max_size_mb: int = 10
    retention_days: int = 7


class SessionConfig(BaseSettings):
    history_size: int = 50
    context_timeout_minutes: int = 30


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    app: AppConfig = AppConfig()
    audio: AudioConfig = AudioConfig()
    llm: LLMConfig = LLMConfig()
    github: GitHubConfig = GitHubConfig()
    ui: UIConfig = UIConfig()
    logging: LoggingConfig = LoggingConfig()
    session: SessionConfig = SessionConfig()


_settings_instance: Settings | None = None


def load_config(path: str | None = None) -> Settings:
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance


def get_config() -> Settings:
    if _settings_instance is None:
        return load_config()
    return _settings_instance
