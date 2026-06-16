"""
tests/test_vehicle_detector.py
--------------------------------
Unit tests for ``modules.vehicle_detector``.

Scope
-----
* Instantiation of ``VehicleDetector``.
* ``DetectedVehicle`` dataclass behaviour.
* Frame detection output shape and types.
* Annotation does not modify the original frame.

Notes
-----
* YOLO model is mocked so tests run without GPU or large weights files.
* OpenCV video capture is mocked so tests run without a physical camera.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from utils.constants import VehicleType
from modules.vehicle_detector import DetectedVehicle, VehicleDetector


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def minimal_config() -> dict:
    """Return a minimal config dict sufficient for VehicleDetector."""
    return {
        "detection": {
            "model_path": "models/yolov8/yolov8n.pt",
            "confidence_threshold": 0.45,
            "iou_threshold": 0.5,
            "target_classes": [2, 3, 5, 7],
            "device": "cpu",
        },
        "video": {
            "source": 0,
        },
    }


@pytest.fixture
def sample_detection() -> DetectedVehicle:
    """Return a sample DetectedVehicle for use in multiple tests."""
    return DetectedVehicle(
        vehicle_type=VehicleType.CAR,
        confidence=0.87,
        x1=100, y1=150, x2=200, y2=250,
        frame_id=1,
    )


@pytest.fixture
def blank_frame() -> np.ndarray:
    """Return a blank BGR frame of standard size."""
    return np.zeros((720, 1280, 3), dtype=np.uint8)


# ---------------------------------------------------------------------------
# DetectedVehicle tests
# ---------------------------------------------------------------------------

class TestDetectedVehicle:
    """Tests for the ``DetectedVehicle`` dataclass."""

    def test_bbox_property(self, sample_detection: DetectedVehicle) -> None:
        """bbox property should return (x1, y1, x2, y2)."""
        # TODO: assert sample_detection.bbox == (100, 150, 200, 250)
        raise NotImplementedError("TODO: implement test_bbox_property")

    def test_centre_property(self, sample_detection: DetectedVehicle) -> None:
        """centre property should return the midpoint of the bounding box."""
        # TODO: assert sample_detection.centre == (150, 200)
        raise NotImplementedError("TODO: implement test_centre_property")

    def test_to_dict_keys(self, sample_detection: DetectedVehicle) -> None:
        """to_dict() should include all required API contract keys."""
        # TODO: d = sample_detection.to_dict()
        # TODO: assert {"vehicle_type", "confidence", "position", "frame_id", "timestamp"} <= d.keys()
        raise NotImplementedError("TODO: implement test_to_dict_keys")

    def test_to_dict_position_keys(self, sample_detection: DetectedVehicle) -> None:
        """to_dict() position sub-dict should contain x1, y1, x2, y2."""
        # TODO: assert {"x1","y1","x2","y2"} <= sample_detection.to_dict()["position"].keys()
        raise NotImplementedError("TODO: implement test_to_dict_position_keys")


# ---------------------------------------------------------------------------
# VehicleDetector tests
# ---------------------------------------------------------------------------

class TestVehicleDetector:
    """Tests for the ``VehicleDetector`` class."""

    def test_instantiation(self, minimal_config: dict) -> None:
        """VehicleDetector should instantiate without raising."""
        # TODO: detector = VehicleDetector(minimal_config); assert detector is not None
        raise NotImplementedError("TODO: implement test_instantiation")

    @patch("modules.vehicle_detector.YOLO", create=True)
    def test_load_model_success(
        self, mock_yolo: MagicMock, minimal_config: dict
    ) -> None:
        """load_model() should return True on success."""
        # TODO: detector = VehicleDetector(minimal_config)
        # TODO: mock_yolo.return_value = MagicMock()
        # TODO: assert detector.load_model() is True
        raise NotImplementedError("TODO: implement test_load_model_success")

    @patch("modules.vehicle_detector.cv2", create=True)
    def test_open_source_webcam(
        self, mock_cv2: MagicMock, minimal_config: dict
    ) -> None:
        """open_source() should call VideoCapture and return True."""
        # TODO: mock_cv2.VideoCapture.return_value.isOpened.return_value = True
        # TODO: assert detector.open_source(0) is True
        raise NotImplementedError("TODO: implement test_open_source_webcam")

    def test_detect_frame_returns_list(
        self, minimal_config: dict, blank_frame: np.ndarray
    ) -> None:
        """detect_frame() should always return a list."""
        # TODO: Mock self._model; call detect_frame(blank_frame); assert isinstance(result, list)
        raise NotImplementedError("TODO: implement test_detect_frame_returns_list")

    def test_annotate_does_not_mutate_original(
        self, minimal_config: dict, blank_frame: np.ndarray, sample_detection: DetectedVehicle
    ) -> None:
        """annotate_frame() must not modify the original frame in-place."""
        # TODO: original = blank_frame.copy(); annotated = detector.annotate_frame(blank_frame, [...])
        # TODO: assert np.array_equal(blank_frame, original)
        raise NotImplementedError("TODO: implement test_annotate_does_not_mutate_original")

    def test_frame_id_increments(
        self, minimal_config: dict
    ) -> None:
        """frame_id should increment with each read_frame() call."""
        # TODO: Mock VideoCapture to return valid frames.
        # TODO: Call read_frame() N times; assert detector.frame_id == N
        raise NotImplementedError("TODO: implement test_frame_id_increments")
