import pytest
from jarvis.activation.hotkey import HotkeyListener


def test_hotkey_listener_init():
    hl = HotkeyListener("ctrl+win+z")
    assert hl is not None
    assert hl.hotkey == "ctrl+win+z"


def test_hotkey_default():
    hl = HotkeyListener()
    assert hl.hotkey == "ctrl+win+z"


def test_hotkey_register_unregister():
    hl = HotkeyListener("ctrl+alt+t")
    # Should not raise
    hl.register(lambda: None)
    hl.unregister()
