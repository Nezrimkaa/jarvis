import json
import httpx
from pydantic import SecretStr
from jarvis.utils.logger import get_logger

logger = get_logger("llm")


class LLMError(Exception):
    pass


PROVIDERS = {
    "deepseek": {
        "endpoint": "https://api.deepseek.com/v1",
        "model": "deepseek-coder",
        "env_key": "DEEPSEEK_API_KEY",
    },
    "github": {
        "endpoint": "https://models.inference.ai.azure.com",
        "model": "gpt-4o-mini",
        "env_key": "GITHUB_TOKEN",
    },
}


class LLMClient:
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        endpoint: str = "https://models.inference.ai.azure.com",
        provider: str = "github",
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ):
        if not api_key:
            raise LLMError(
                f"API key required for {provider}. "
                f"Set {PROVIDERS.get(provider, {}).get('env_key', 'LLM_API_KEY')} in .env"
            )
        self.api_key = SecretStr(api_key)
        self.model = model
        self.endpoint = endpoint.rstrip("/")
        self.provider = provider
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = httpx.AsyncClient(timeout=120.0)
        logger.info(f"LLM: {provider} | model: {model} | endpoint: {endpoint}")

    async def chat(
        self,
        message: str,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": message})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
        }

        try:
            response = await self._client.post(
                f"{self.endpoint}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key.get_secret_value()}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            msg = f"API error ({e.response.status_code}): {e.response.text[:200]}"
            raise LLMError(msg) from e
        except httpx.HTTPError as e:
            raise LLMError(f"API request failed: {e}") from e
        except (KeyError, json.JSONDecodeError) as e:
            raise LLMError(f"Invalid API response: {e}") from e

    async def close(self):
        await self._client.aclose()
