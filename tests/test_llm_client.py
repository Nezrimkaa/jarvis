import pytest
from jarvis.nlu.llm_client import LLMClient, LLMError


def test_llm_client_init():
    client = LLMClient(api_key="test-key")
    assert client.api_key.get_secret_value() == "test-key"
    assert client.provider == "github"


def test_llm_client_default_endpoint():
    client = LLMClient(api_key="test-key")
    assert "models.inference.ai.azure.com" in client.endpoint


def test_llm_client_missing_key():
    with pytest.raises(LLMError):
        LLMClient(api_key="")


@pytest.mark.asyncio
async def test_llm_client_chat():
    client = LLMClient(api_key="test-key", endpoint="https://httpbin.org/post")
    with pytest.raises(LLMError):
        await client.chat("hello")


@pytest.mark.asyncio
async def test_llm_client_chat_with_system():
    client = LLMClient(api_key="test-key", endpoint="https://httpbin.org/post")
    with pytest.raises(LLMError):
        await client.chat("hello", system="You are a test bot")
