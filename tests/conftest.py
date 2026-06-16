"""
tests/conftest.py
------------------
Shared pytest fixtures and configuration for the test suite.

Any fixtures defined here are automatically available in all test files
without explicit imports.
"""

import pytest


@pytest.fixture(scope="session")
def base_config() -> dict:
    """Return the full default configuration dict for session-scoped tests.

    Mirrors the structure of ``config/config.yaml`` so tests don't
    need to read from disk.
    """
    return {
        "video": {"source": 0, "frame_width": 1280, "frame_height": 720},
        "detection": {
            "model_path": "models/yolov8/yolov8n.pt",
            "confidence_threshold": 0.45,
            "iou_threshold": 0.5,
            "target_classes": [2, 3, 5, 7],
            "device": "cpu",
        },
        "counting": {
            "enable_lane_counting": False,
            "lane_count": 4,
            "counting_line_position": 0.6,
        },
        "analysis": {
            "density_area_sqm": 500.0,
            "history_window": 10,
            "congestion_thresholds": {"low": 20, "medium": 40, "high": 60},
        },
        "signal": {
            "min_green_seconds": 10,
            "max_green_seconds": 120,
            "yellow_duration_seconds": 3,
            "red_min_seconds": 10,
            "timing_map": {"low": 20, "medium": 40, "high": 60, "critical": 90},
        },
        "predictor": {
            "model_type": "decision_tree",
            "retrain_interval_frames": 20,
            "min_samples_to_train": 10,
            "n_estimators": 10,
            "max_depth": 3,
        },
        "database": {"path": ":memory:", "log_interval_seconds": 5},
        "dashboard": {"refresh_interval_seconds": 2, "chart_history_minutes": 30},
        "logging": {"level": "DEBUG"},
    }
