import pytest
from jarvis.ui.overlay import OverlayWindow


def test_overlay_init():
    ol = OverlayWindow()
    assert ol is not None
    assert ol.width == 400
    assert ol.height == 300


def test_overlay_update_status():
    ol = OverlayWindow()
    ol.update_status("Listening...")
    ol.add_to_history("user command")
    ol.close()
