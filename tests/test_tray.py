import pytest
from jarvis.ui.tray import TrayIcon


def test_tray_icon_init():
    tray = TrayIcon()
    assert tray is not None
    assert tray.tooltip == "Jarvis Assistant"


def test_tray_icon_custom():
    tray = TrayIcon(tooltip="My Bot")
    assert tray.tooltip == "My Bot"


def test_tray_icon_start_stop():
    tray = TrayIcon()
    # Just test that these don't crash
    tray.start()
    tray.stop()
