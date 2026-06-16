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
    # TODO: Open and parse the YAML file.
    # TODO: Log success and return the dict.
    raise NotImplementedError("TODO: implement load_config()")


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
    # TODO: Traverse config dict with the key sequence; return default on KeyError.
    raise NotImplementedError("TODO: implement get_config_value()")


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
    # TODO: Return datetime.now(timezone.utc).strftime(DB_DATETIME_FORMAT)
    raise NotImplementedError("TODO: implement utc_now_iso()")


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
    # TODO: return time.monotonic() - start_time
    raise NotImplementedError("TODO: implement elapsed_seconds()")


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
    # TODO: return str(uuid.uuid4())
    raise NotImplementedError("TODO: implement generate_session_id()")


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
    # TODO: p = Path(path); p.mkdir(parents=True, exist_ok=True); return p
    raise NotImplementedError("TODO: implement ensure_dir()")


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
    # TODO: Try casting source to int; if it succeeds return int, else return str.
    raise NotImplementedError("TODO: implement resolve_video_source()")


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
    # TODO: return max(min_val, min(value, max_val))
    raise NotImplementedError("TODO: implement clamp()")


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
    # TODO: Slice last `window` values and compute mean.
    raise NotImplementedError("TODO: implement moving_average()")
