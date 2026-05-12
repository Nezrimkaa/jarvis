import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def get_api_key(var_name: str) -> str | None:
    return os.getenv(var_name)


def get_github_token() -> str | None:
    return get_api_key("GITHUB_TOKEN")


def get_deepseek_key() -> str | None:
    return get_api_key("DEEPSEEK_API_KEY")


def mask_key(key: str, visible_chars: int = 4) -> str:
    if len(key) <= visible_chars + 4:
        return key
    return f"{key[:3]}...{key[-visible_chars:]}"
