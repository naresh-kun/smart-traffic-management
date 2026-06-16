"""
tests/test_helpers.py
---------------------
Unit tests for ``utils.helpers``.
"""

import time
import re
import uuid
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest
import yaml

from utils.helpers import (
    load_config,
    get_config_value,
    utc_now_iso,
    elapsed_seconds,
    generate_session_id,
    ensure_dir,
    resolve_video_source,
    clamp,
    moving_average,
)
from utils.constants import DB_DATETIME_FORMAT


# ---------------------------------------------------------------------------
# Configuration Tests
# ---------------------------------------------------------------------------

def test_load_config_success():
    """Test successful loading of a YAML config file."""
    yaml_content = "video:\n  source: 0\n"
    with patch("builtins.open", mock_open(read_data=yaml_content)):
        config = load_config("dummy_config.yaml")
        assert isinstance(config, dict)
        assert config["video"]["source"] == 0


def test_load_config_empty_file():
    """Test loading an empty YAML config file returns an empty dictionary."""
    with patch("builtins.open", mock_open(read_data="")):
        config = load_config("dummy_config.yaml")
        assert config == {}


def test_load_config_file_not_found():
    """Test FileNotFoundError is raised for non-existent config files."""
    with pytest.raises(FileNotFoundError):
        load_config("nonexistent_config.yaml")


def test_load_config_invalid_yaml():
    """Test yaml.YAMLError is raised for malformed YAML files."""
    invalid_yaml_content = "video: [unbalanced brackets"
    with patch("builtins.open", mock_open(read_data=invalid_yaml_content)):
        with pytest.raises(yaml.YAMLError):
            load_config("invalid_config.yaml")


def test_get_config_value():
    """Test nested value retrieval."""
    config = {
        "video": {
            "source": 0,
            "fps_target": 30
        },
        "detection": {
            "confidence_threshold": 0.45
        }
    }
    
    assert get_config_value(config, "video", "source") == 0
    assert get_config_value(config, "video", "fps_target") == 30
    assert get_config_value(config, "detection", "confidence_threshold") == 0.45


def test_get_config_value_missing_keys():
    """Test default values are returned for missing keys."""
    config = {"video": {"source": 0}}
    
    # Missing top-level key
    assert get_config_value(config, "nonexistent", default=42) == 42
    # Missing nested key
    assert get_config_value(config, "video", "fps_target", default=30) == 30
    # Not a dict path
    assert get_config_value(config, "video", "source", "nested", default="def") == "def"


# ---------------------------------------------------------------------------
# Time helper Tests
# ---------------------------------------------------------------------------

def test_utc_now_iso():
    """Test ISO timestamp generation matches DB_DATETIME_FORMAT pattern."""
    iso_str = utc_now_iso()
    assert isinstance(iso_str, str)
    # E.g. 2026-06-17T00:00:00.000000Z
    pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z$"
    assert re.match(pattern, iso_str)


def test_elapsed_seconds():
    """Test elapsed time calculation."""
    start = time.monotonic()
    time.sleep(0.05)
    elapsed = elapsed_seconds(start)
    assert elapsed > 0.0
    assert elapsed < 1.0


# ---------------------------------------------------------------------------
# Session / UUID Tests
# ---------------------------------------------------------------------------

def test_generate_session_id():
    """Test generation of valid UUID4 hex strings."""
    session_id = generate_session_id()
    assert isinstance(session_id, str)
    # Verify it can be parsed as a UUID
    uuid_obj = uuid.UUID(session_id)
    assert str(uuid_obj) == session_id


# ---------------------------------------------------------------------------
# Path helper Tests
# ---------------------------------------------------------------------------

@patch("pathlib.Path.mkdir")
def test_ensure_dir(mock_mkdir):
    """Test ensure_dir calls mkdir with parents=True, exist_ok=True."""
    result = ensure_dir("test/dir/path")
    assert isinstance(result, Path)
    assert str(result) == str(Path("test/dir/path"))
    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


def test_resolve_video_source():
    """Test normalisation of video source values."""
    assert resolve_video_source(0) == 0
    assert resolve_video_source("1") == 1
    assert resolve_video_source("data/video.mp4") == "data/video.mp4"
    assert resolve_video_source(None) == "None"


# ---------------------------------------------------------------------------
# Numeric helper Tests
# ---------------------------------------------------------------------------

def test_clamp():
    """Test value clamping."""
    assert clamp(5.0, 0.0, 10.0) == 5.0
    assert clamp(-5.0, 0.0, 10.0) == 0.0
    assert clamp(15.0, 0.0, 10.0) == 10.0
    assert clamp(10.0, 0.0, 10.0) == 10.0


def test_moving_average():
    """Test moving average calculation."""
    history = [1.0, 2.0, 3.0, 4.0, 5.0]
    
    # Normal cases
    assert moving_average(history, 3) == 4.0  # (3+4+5)/3
    assert moving_average(history, 5) == 3.0  # (1+2+3+4+5)/5
    
    # Window larger than history
    assert moving_average(history, 10) == 3.0
    
    # Edge cases
    assert moving_average([], 3) == 0.0
    assert moving_average(history, 0) == 0.0
    assert moving_average(history, -1) == 0.0
