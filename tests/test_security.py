import pytest
from jarvis.utils.security import get_api_key, mask_key


def test_mask_key():
    key = "sk-1234567890abcdef"
    masked = mask_key(key)
    assert masked == "sk-...cdef"
    assert "1234567890" not in masked


def test_mask_short_key():
    assert mask_key("ab") == "ab"


def test_get_api_key_nonexistent():
    key = get_api_key("NONEXISTENT_VAR")
    assert key is None
