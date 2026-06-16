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
    # TODO: Remove default Loguru sink.
    # TODO: Add a console sink with colourised format.
    # TODO: Create log_dir if it does not exist.
    # TODO: Add a rotating file sink writing to log_dir/log_file.
    # TODO: Set the minimum level on both sinks from the `level` parameter.
    raise NotImplementedError("TODO: implement setup_logging()")


def get_logger(name: str) -> "loguru.Logger":  # type: ignore[name-defined]
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
    # TODO: Return _loguru_logger.bind(module=name)
    raise NotImplementedError("TODO: implement get_logger()")


def log_section_header(title: str) -> None:
    """Emit a prominent section-divider log message.

    Useful for clearly marking the start of major lifecycle events
    (session start, model load, teardown, etc.) in log files.

    Parameters
    ----------
    title : str
        Human-readable label for the section.
    """
    # TODO: Log a formatted divider line at INFO level.
    raise NotImplementedError("TODO: implement log_section_header()")
