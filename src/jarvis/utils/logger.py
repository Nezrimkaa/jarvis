import sys
from pathlib import Path
from loguru import logger as _logger


_loggers: dict[str, "_logger.__class__"] = {}


def setup_logger(
    name: str = "jarvis",
    level: str = "INFO",
    file_path: str | None = None,
    rotation: str = "10 MB",
    retention: str = "7 days",
):
    logger = _logger.bind(name=name)
    logger.remove()

    logger.add(sys.stderr, level=level, format="<green>{time:HH:mm:ss}</green> | <level>{level:7}</level> | <cyan>{name}</cyan> | {message}")

    if file_path:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        logger.add(file_path, level=level, rotation=rotation, retention=retention)

    _loggers[name] = logger
    return logger


def get_logger(name: str = "jarvis"):
    if name in _loggers:
        return _loggers[name]
    return setup_logger(name)
