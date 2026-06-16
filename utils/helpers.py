"""
utils/helpers.py
----------------
Shared utility functions used across multiple modules.

Rules
-----
* Keep functions pure (no side-effects) where possible.
* Do NOT perform vehicle detection, signal control, or UI rendering here.
* Functions here may be used by any module without creating circular imports.
"""

import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import yaml

from utils.logger import get_logger
from utils.constants import DB_DATETIME_FORMAT

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def load_config(path: str = "config/config.yaml") -> dict:
    """Load and return the YAML configuration file as a dictionary.

    Parameters
    ----------
    path : str
        Relative or absolute path to the YAML config file.

    Returns
    -------
    dict
        Parsed configuration dictionary.

    Raises
    ------
    FileNotFoundError
        If the config file does not exist at ``path``.
    yaml.YAMLError
        If the file contains invalid YAML.

    Example
    -------
    >>> config = load_config("config/config.yaml")
    >>> config["video"]["source"]
    0
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        if not isinstance(config, dict):
            config = {}
            
        logger.info(f"Loaded configuration from '{path}'")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {path}")
        raise
    except yaml.YAMLError as exc:
        logger.error(f"Error parsing YAML file '{path}': {exc}")
        raise


def get_config_value(config: dict, *keys: str, default: Any = None) -> Any:
    """Safely retrieve a nested value from the config dictionary.

    Parameters
    ----------
    config : dict
        The root configuration dictionary.
    *keys : str
        Sequence of nested keys, e.g. ``"video", "source"``.
    default : Any
        Value returned when the key path does not exist.

    Returns
    -------
    Any
        The value at the key path, or ``default`` if not found.

    Example
    -------
    >>> get_config_value(config, "detection", "confidence_threshold", default=0.5)
    0.45
    """
    curr = config
    for key in keys:
        if isinstance(curr, dict) and key in curr:
            curr = curr[key]
        else:
            return default
    return curr


# ---------------------------------------------------------------------------
# Time helpers
# ---------------------------------------------------------------------------

def utc_now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string.

    Returns
    -------
    str
        Example: ``"2026-06-17T00:00:00.000000Z"``
    """
    return datetime.now(timezone.utc).strftime(DB_DATETIME_FORMAT)


def elapsed_seconds(start_time: float) -> float:
    """Return elapsed seconds since ``start_time`` (from ``time.monotonic()``).

    Parameters
    ----------
    start_time : float
        A reference timestamp obtained via ``time.monotonic()``.

    Returns
    -------
    float
        Number of seconds elapsed.
    """
    return time.monotonic() - start_time


# ---------------------------------------------------------------------------
# Session / UUID helpers
# ---------------------------------------------------------------------------

def generate_session_id() -> str:
    """Generate a unique session identifier for a single application run.

    Returns
    -------
    str
        A UUID4 hex string.
    """
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

def ensure_dir(path: str) -> Path:
    """Create a directory (and all parents) if it does not already exist.

    Parameters
    ----------
    path : str
        Directory path to create.

    Returns
    -------
    Path
        Resolved ``pathlib.Path`` object.
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def resolve_video_source(source: Any) -> Any:
    """Normalise the video source value for OpenCV.

    Parameters
    ----------
    source : Any
        Either a string (file path or ``"0"`` / ``"1"`` camera index)
        or an integer camera index.

    Returns
    -------
    int | str
        Integer if the source is a camera index, string path otherwise.
    """
    if isinstance(source, int):
        return source
    try:
        return int(source)
    except (ValueError, TypeError):
        return str(source)


# ---------------------------------------------------------------------------
# Numeric helpers
# ---------------------------------------------------------------------------

def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp ``value`` to the inclusive range [``min_val``, ``max_val``].

    Parameters
    ----------
    value : float
        The number to clamp.
    min_val : float
        Lower bound.
    max_val : float
        Upper bound.

    Returns
    -------
    float
        The clamped value.
    """
    return max(min_val, min(value, max_val))


def moving_average(history: list[float], window: int) -> float:
    """Compute the moving average over the last ``window`` values.

    Parameters
    ----------
    history : list[float]
        List of numerical observations (newest last).
    window : int
        Number of recent values to average.

    Returns
    -------
    float
        The average, or 0.0 if ``history`` is empty.
    """
    if not history or window <= 0:
        return 0.0
    recent = history[-window:]
    return sum(recent) / len(recent)
