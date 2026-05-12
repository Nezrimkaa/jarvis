import pytest
from jarvis.actions.os_control import OSController


@pytest.fixture
def os_ctrl():
    return OSController()


def test_os_controller_init(os_ctrl):
    assert os_ctrl is not None


def test_get_volume(os_ctrl):
    # Should return current volume level (0-100)
    level = os_ctrl.get_volume()
    assert 0 <= level <= 100


def test_open_app_not_found(os_ctrl):
    result = os_ctrl.close_app("nonexistent_app_xyz_123")
    assert result is False


def test_screenshot(os_ctrl):
    result = os_ctrl.take_screenshot()
    assert result is not None
    import os
    if os.path.exists(result):
        os.remove(result)
