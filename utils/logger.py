"""
utils/logger.py
---------------
Centralised logging configuration for the Smart Traffic Management System.

All modules must obtain their logger from this module via ``get_logger()``.
Direct use of ``print()`` for diagnostics is forbidden in production code.

Uses Loguru for structured, rotating file logs alongside console output.
"""

import sys
from pathlib import Path
from typing import Optional

from loguru import logger as _loguru_logger

# Track whether setup_logging() has been called so we can apply a sensible
# default configuration on first ``get_logger()`` call.
_is_configured: bool = False

# Default console format – includes timestamp, level, bound module name, and message
_CONSOLE_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{extra[module]}</cyan> | "
    "<level>{message}</level>"
)

# File format – same content, no ANSI colour codes
_FILE_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
    "{level: <8} | "
    "{extra[module]} | "
    "{message}"
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def setup_logging(
    level: str = "INFO",
    log_dir: str = "data/logs",
    log_file: str = "traffic_system.log",
    rotation: str = "10 MB",
    retention: str = "7 days",
) -> None:
    """Configure global Loguru logging sinks.

    Must be called once at application startup before any module creates a
    logger. Subsequent calls will reconfigure the sinks.

    Parameters
    ----------
    level : str
        Minimum log level: ``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``.
    log_dir : str
        Directory where log files are written. Created if it does not exist.
    log_file : str
        Base filename for the rotating log file.
    rotation : str
        Loguru rotation trigger, e.g. ``"10 MB"`` or ``"1 day"``.
    retention : str
        How long completed log files are kept, e.g. ``"7 days"``.
    """
    global _is_configured

    # Remove all existing sinks (including the default stderr sink)
    _loguru_logger.remove()

    # Console sink – colourised
    _loguru_logger.add(
        sys.stderr,
        format=_CONSOLE_FORMAT,
        level=level.upper(),
        colorize=True,
    )

    # File sink – rotating, no colours
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    _loguru_logger.add(
        str(log_path / log_file),
        format=_FILE_FORMAT,
        level=level.upper(),
        rotation=rotation,
        retention=retention,
        encoding="utf-8",
    )

    _is_configured = True
    _loguru_logger.bind(module="logger").info(
        f"Logging configured: level={level}, dir={log_dir}, file={log_file}"
    )


def _ensure_default_config() -> None:
    """Apply a minimal default configuration if ``setup_logging()`` has not
    been called yet.

    This avoids ``KeyError`` on the ``module`` extra key when a module calls
    ``get_logger()`` before the application entry point invokes
    ``setup_logging()``.
    """
    global _is_configured
    if not _is_configured:
        # Remove the default Loguru sink and add one with our format
        _loguru_logger.remove()
        _loguru_logger.add(
            sys.stderr,
            format=_CONSOLE_FORMAT,
            level="DEBUG",
            colorize=True,
        )
        _is_configured = True


def get_logger(name: str) -> "_loguru_logger.__class__":  # type: ignore[name-defined]
    """Return a Loguru logger bound with the caller's module name.

    Parameters
    ----------
    name : str
        Typically ``__name__`` of the calling module.

    Returns
    -------
    loguru.Logger
        A logger instance with the ``name`` context bound.

    Example
    -------
    >>> from utils.logger import get_logger
    >>> logger = get_logger(__name__)
    >>> logger.info("Module started")
    """
    _ensure_default_config()
    return _loguru_logger.bind(module=name)


def log_section_header(title: str) -> None:
    """Emit a prominent section-divider log message.

    Useful for clearly marking the start of major lifecycle events
    (session start, model load, teardown, etc.) in log files.

    Parameters
    ----------
    title : str
        Human-readable label for the section.
    """
    _ensure_default_config()
    divider = "=" * 60
    _loguru_logger.bind(module="system").info(divider)
    _loguru_logger.bind(module="system").info(f"  {title}")
    _loguru_logger.bind(module="system").info(divider)
