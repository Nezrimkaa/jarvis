import pytest
from jarvis.utils.logger import setup_logger, get_logger


def test_setup_logger_returns_logger():
    logger = setup_logger("test", level="DEBUG")
    assert logger is not None


def test_setup_logger_default_level():
    logger = setup_logger("test_default")
    assert logger is not None


def test_get_logger_returns_same_instance():
    setup_logger("test_singleton")
    logger1 = get_logger("test_singleton")
    logger2 = get_logger("test_singleton")
    assert logger1 is logger2


def test_get_logger_creates_new_if_not_exists():
    logger = get_logger("nonexistent")
    assert logger is not None
