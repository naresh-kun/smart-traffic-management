"""
tests/test_vehicle_detector.py
--------------------------------
Unit tests for ``modules.vehicle_detector``.

Scope
-----
* Instantiation of ``VehicleDetector``.
* ``DetectedVehicle`` dataclass behaviour (bbox, centre, to_dict).
* Model loading (success and failure paths).
* Source opening (webcam index, video file, invalid paths).
* Frame reading and frame_id increment.
* Detection parsing from YOLO results (including class filtering).
* Annotation does not modify the original frame.
* Release and is_open lifecycle.

Notes
-----
* YOLO model is mocked so tests run without GPU or large weights files.
* OpenCV video capture is mocked so tests run without a physical camera.
* All tests are self-contained and do not require external resources.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, PropertyMock, patch, call

import numpy as np
import pytest

from utils.constants import VehicleType, COCO_CLASS_ID_TO_VEHICLE_TYPE
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
        timestamp=1700000000.0,
    )


@pytest.fixture
def blank_frame() -> np.ndarray:
    """Return a blank BGR frame of standard size."""
    return np.zeros((720, 1280, 3), dtype=np.uint8)


def _make_mock_box(class_id: int, confidence: float,
                   x1: int, y1: int, x2: int, y2: int) -> MagicMock:
    """Create a mock YOLO detection box with the given attributes.

    Returns an object that mimics ``ultralytics.engine.results.Boxes``
    for a single detection.
    """
    box = MagicMock()
    box.cls = MagicMock()
    box.cls.item.return_value = class_id
    box.conf = MagicMock()
    box.conf.item.return_value = confidence
    # xyxy is a tensor of shape (1, 4) – squeeze() returns 1-D
    coords = MagicMock()
    coords.squeeze.return_value = MagicMock()
    coords.squeeze.return_value.tolist.return_value = [
        float(x1), float(y1), float(x2), float(y2)
    ]
    box.xyxy = coords
    return box


def _make_mock_result(boxes: list[MagicMock]) -> MagicMock:
    """Wrap a list of mock boxes into a mock YOLO result object."""
    result = MagicMock()
    result.boxes = boxes
    return result


# ---------------------------------------------------------------------------
# DetectedVehicle dataclass tests
# ---------------------------------------------------------------------------

class TestDetectedVehicle:
    """Tests for the ``DetectedVehicle`` dataclass."""

    def test_bbox_property(self, sample_detection: DetectedVehicle) -> None:
        """bbox property should return (x1, y1, x2, y2)."""
        assert sample_detection.bbox == (100, 150, 200, 250)

    def test_centre_property(self, sample_detection: DetectedVehicle) -> None:
        """centre property should return the midpoint of the bounding box."""
        assert sample_detection.centre == (150, 200)

    def test_centre_with_odd_dimensions(self) -> None:
        """Centre uses integer division, so odd-sized boxes round down."""
        det = DetectedVehicle(
            vehicle_type=VehicleType.TRUCK,
            confidence=0.5,
            x1=0, y1=0, x2=9, y2=9,
        )
        # (0+9)//2 = 4, (0+9)//2 = 4
        assert det.centre == (4, 4)

    def test_to_dict_keys(self, sample_detection: DetectedVehicle) -> None:
        """to_dict() should include all required API contract keys."""
        d = sample_detection.to_dict()
        required_keys = {"vehicle_type", "confidence", "position", "frame_id", "timestamp"}
        assert required_keys <= set(d.keys())

    def test_to_dict_position_keys(self, sample_detection: DetectedVehicle) -> None:
        """to_dict() position sub-dict should contain x1, y1, x2, y2."""
        position = sample_detection.to_dict()["position"]
        assert {"x1", "y1", "x2", "y2"} <= set(position.keys())

    def test_to_dict_position_values(self, sample_detection: DetectedVehicle) -> None:
        """to_dict() position values should match the detection coordinates."""
        pos = sample_detection.to_dict()["position"]
        assert pos == {"x1": 100, "y1": 150, "x2": 200, "y2": 250}

    def test_to_dict_vehicle_type_is_string(self, sample_detection: DetectedVehicle) -> None:
        """to_dict() vehicle_type must be a plain string, not an Enum."""
        d = sample_detection.to_dict()
        assert isinstance(d["vehicle_type"], str)
        assert d["vehicle_type"] == "car"

    def test_to_dict_confidence_rounded(self) -> None:
        """to_dict() should round confidence to 4 decimal places."""
        det = DetectedVehicle(
            vehicle_type=VehicleType.BUS,
            confidence=0.876543219,
            x1=0, y1=0, x2=1, y2=1,
        )
        assert det.to_dict()["confidence"] == 0.8765

    def test_to_dict_frame_id_preserved(self, sample_detection: DetectedVehicle) -> None:
        """to_dict() should include the correct frame_id."""
        assert sample_detection.to_dict()["frame_id"] == 1

    def test_to_dict_timestamp_is_float(self, sample_detection: DetectedVehicle) -> None:
        """to_dict() timestamp must be a float."""
        assert isinstance(sample_detection.to_dict()["timestamp"], float)

    def test_default_frame_id_is_zero(self) -> None:
        """Default frame_id should be 0."""
        det = DetectedVehicle(
            vehicle_type=VehicleType.MOTORCYCLE,
            confidence=0.9,
            x1=0, y1=0, x2=10, y2=10,
        )
        assert det.frame_id == 0

    def test_timestamp_auto_populated(self) -> None:
        """When timestamp is not provided, it should default to current time."""
        det = DetectedVehicle(
            vehicle_type=VehicleType.CAR,
            confidence=0.5,
            x1=0, y1=0, x2=1, y2=1,
        )
        import time
        # Should be within the last 2 seconds
        assert abs(det.timestamp - time.time()) < 2.0


# ---------------------------------------------------------------------------
# VehicleDetector instantiation tests
# ---------------------------------------------------------------------------

class TestVehicleDetectorInit:
    """Tests for ``VehicleDetector`` construction."""

    def test_instantiation(self, minimal_config: dict) -> None:
        """VehicleDetector should instantiate without raising."""
        detector = VehicleDetector(minimal_config)
        assert detector is not None

    def test_default_config_values(self) -> None:
        """Missing config keys should fall back to safe defaults."""
        detector = VehicleDetector({})
        assert detector._confidence_threshold == 0.45
        assert detector._iou_threshold == 0.5
        assert detector._device == "cpu"
        assert 2 in detector._target_class_ids

    def test_custom_config_values(self) -> None:
        """Custom config values should override defaults."""
        config = {
            "detection": {
                "confidence_threshold": 0.7,
                "iou_threshold": 0.3,
                "device": "cuda",
                "target_classes": [2, 7],
            }
        }
        detector = VehicleDetector(config)
        assert detector._confidence_threshold == 0.7
        assert detector._iou_threshold == 0.3
        assert detector._device == "cuda"
        assert detector._target_class_ids == {2, 7}

    def test_initial_state(self, minimal_config: dict) -> None:
        """Freshly created detector should have no model and no source."""
        detector = VehicleDetector(minimal_config)
        assert detector.frame_id == 0
        assert detector.is_open is False
        assert detector.model_loaded is False


# ---------------------------------------------------------------------------
# Model loading tests
# ---------------------------------------------------------------------------

class TestLoadModel:
    """Tests for ``VehicleDetector.load_model()``."""

    @patch("modules.vehicle_detector.YOLO")
    def test_load_model_success(
        self, mock_yolo_cls: MagicMock, minimal_config: dict
    ) -> None:
        """load_model() should return True on success and store the model."""
        mock_model = MagicMock()
        mock_yolo_cls.return_value = mock_model

        detector = VehicleDetector(minimal_config)
        result = detector.load_model()

        assert result is True
        assert detector.model_loaded is True
        mock_yolo_cls.assert_called_once_with(minimal_config["detection"]["model_path"])

    @patch("modules.vehicle_detector.YOLO", side_effect=Exception("Weights not found"))
    def test_load_model_failure(
        self, mock_yolo_cls: MagicMock, minimal_config: dict
    ) -> None:
        """load_model() should return False on failure and leave model as None."""
        detector = VehicleDetector(minimal_config)
        result = detector.load_model()

        assert result is False
        assert detector.model_loaded is False

    @patch("modules.vehicle_detector.YOLO")
    def test_load_model_uses_config_path(
        self, mock_yolo_cls: MagicMock
    ) -> None:
        """load_model() should use model_path from config."""
        config = {"detection": {"model_path": "custom/path/yolov8s.pt"}}
        detector = VehicleDetector(config)
        detector.load_model()
        mock_yolo_cls.assert_called_once_with("custom/path/yolov8s.pt")


# ---------------------------------------------------------------------------
# Video source management tests
# ---------------------------------------------------------------------------

class TestOpenSource:
    """Tests for ``VehicleDetector.open_source()``."""

    @patch("modules.vehicle_detector.cv2")
    def test_open_source_webcam(
        self, mock_cv2: MagicMock, minimal_config: dict
    ) -> None:
        """open_source(0) should call VideoCapture with int 0 and return True."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 1280.0  # used by get_frame_dimensions / FPS log
        mock_cv2.VideoCapture.return_value = mock_cap
        mock_cv2.CAP_PROP_FRAME_WIDTH = 3
        mock_cv2.CAP_PROP_FRAME_HEIGHT = 4
        mock_cv2.CAP_PROP_FPS = 5

        detector = VehicleDetector(minimal_config)
        result = detector.open_source(0)

        assert result is True
        assert detector.is_open is True
        mock_cv2.VideoCapture.assert_called_once_with(0)

    @patch("modules.vehicle_detector.cv2")
    def test_open_source_video_file(
        self, mock_cv2: MagicMock, minimal_config: dict
    ) -> None:
        """open_source('video.mp4') should call VideoCapture with the path."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 720.0
        mock_cv2.VideoCapture.return_value = mock_cap
        mock_cv2.CAP_PROP_FRAME_WIDTH = 3
        mock_cv2.CAP_PROP_FRAME_HEIGHT = 4
        mock_cv2.CAP_PROP_FPS = 5

        detector = VehicleDetector(minimal_config)
        result = detector.open_source("data/videos/traffic.mp4")

        assert result is True
        mock_cv2.VideoCapture.assert_called_once_with("data/videos/traffic.mp4")

    @patch("modules.vehicle_detector.cv2")
    def test_open_source_string_index(
        self, mock_cv2: MagicMock, minimal_config: dict
    ) -> None:
        """open_source('0') should resolve '0' to int 0."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 640.0
        mock_cv2.VideoCapture.return_value = mock_cap
        mock_cv2.CAP_PROP_FRAME_WIDTH = 3
        mock_cv2.CAP_PROP_FRAME_HEIGHT = 4
        mock_cv2.CAP_PROP_FPS = 5

        detector = VehicleDetector(minimal_config)
        detector.open_source("0")

        mock_cv2.VideoCapture.assert_called_once_with(0)

    @patch("modules.vehicle_detector.cv2")
    def test_open_source_failure(
        self, mock_cv2: MagicMock, minimal_config: dict
    ) -> None:
        """open_source() should return False when VideoCapture fails."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_cv2.VideoCapture.return_value = mock_cap

        detector = VehicleDetector(minimal_config)
        result = detector.open_source("nonexistent.mp4")

        assert result is False
        assert detector.is_open is False

    @patch("modules.vehicle_detector.cv2")
    def test_open_source_releases_previous(
        self, mock_cv2: MagicMock, minimal_config: dict
    ) -> None:
        """Opening a new source should release the previous one first."""
        mock_cap_1 = MagicMock()
        mock_cap_1.isOpened.return_value = True
        mock_cap_1.get.return_value = 640.0

        mock_cap_2 = MagicMock()
        mock_cap_2.isOpened.return_value = True
        mock_cap_2.get.return_value = 640.0

        mock_cv2.VideoCapture.side_effect = [mock_cap_1, mock_cap_2]
        mock_cv2.CAP_PROP_FRAME_WIDTH = 3
        mock_cv2.CAP_PROP_FRAME_HEIGHT = 4
        mock_cv2.CAP_PROP_FPS = 5

        detector = VehicleDetector(minimal_config)
        detector.open_source(0)
        detector.open_source(1)

        mock_cap_1.release.assert_called_once()

    @patch("modules.vehicle_detector.cv2")
    def test_open_source_resets_frame_id(
        self, mock_cv2: MagicMock, minimal_config: dict
    ) -> None:
        """Opening a new source should reset frame_id to 0."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 1280.0
        mock_cap.read.return_value = (True, np.zeros((720, 1280, 3), dtype=np.uint8))
        mock_cv2.VideoCapture.return_value = mock_cap
        mock_cv2.CAP_PROP_FRAME_WIDTH = 3
        mock_cv2.CAP_PROP_FRAME_HEIGHT = 4
        mock_cv2.CAP_PROP_FPS = 5

        detector = VehicleDetector(minimal_config)
        detector.open_source(0)
        detector.read_frame()
        detector.read_frame()
        assert detector.frame_id == 2

        # Re-open should reset
        detector.open_source(0)
        assert detector.frame_id == 0


# ---------------------------------------------------------------------------
# Frame reading tests
# ---------------------------------------------------------------------------

class TestReadFrame:
    """Tests for ``VehicleDetector.read_frame()``."""

    @patch("modules.vehicle_detector.cv2")
    def test_read_frame_success(
        self, mock_cv2: MagicMock, minimal_config: dict
    ) -> None:
        """read_frame() should return (True, frame) on success."""
        frame_data = np.ones((720, 1280, 3), dtype=np.uint8) * 128
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, frame_data)
        mock_cap.get.return_value = 1280.0
        mock_cv2.VideoCapture.return_value = mock_cap
        mock_cv2.CAP_PROP_FRAME_WIDTH = 3
        mock_cv2.CAP_PROP_FRAME_HEIGHT = 4
        mock_cv2.CAP_PROP_FPS = 5

        detector = VehicleDetector(minimal_config)
        detector.open_source(0)
        success, frame = detector.read_frame()

        assert success is True
        assert frame is not None
        assert np.array_equal(frame, frame_data)

    def test_read_frame_no_source(self, minimal_config: dict) -> None:
        """read_frame() without open source should return (False, None)."""
        detector = VehicleDetector(minimal_config)
        success, frame = detector.read_frame()

        assert success is False
        assert frame is None

    @patch("modules.vehicle_detector.cv2")
    def test_frame_id_increments(
        self, mock_cv2: MagicMock, minimal_config: dict
    ) -> None:
        """frame_id should increment with each successful read_frame() call."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, np.zeros((100, 100, 3), dtype=np.uint8))
        mock_cap.get.return_value = 100.0
        mock_cv2.VideoCapture.return_value = mock_cap
        mock_cv2.CAP_PROP_FRAME_WIDTH = 3
        mock_cv2.CAP_PROP_FRAME_HEIGHT = 4
        mock_cv2.CAP_PROP_FPS = 5

        detector = VehicleDetector(minimal_config)
        detector.open_source(0)
        assert detector.frame_id == 0

        for i in range(5):
            detector.read_frame()
        assert detector.frame_id == 5

    @patch("modules.vehicle_detector.cv2")
    def test_frame_id_no_increment_on_failure(
        self, mock_cv2: MagicMock, minimal_config: dict
    ) -> None:
        """frame_id should NOT increment when read_frame() returns False."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (False, None)
        mock_cap.get.return_value = 100.0
        mock_cv2.VideoCapture.return_value = mock_cap
        mock_cv2.CAP_PROP_FRAME_WIDTH = 3
        mock_cv2.CAP_PROP_FRAME_HEIGHT = 4
        mock_cv2.CAP_PROP_FPS = 5

        detector = VehicleDetector(minimal_config)
        detector.open_source(0)
        detector.read_frame()

        assert detector.frame_id == 0


# ---------------------------------------------------------------------------
# Detection tests
# ---------------------------------------------------------------------------

class TestDetectFrame:
    """Tests for ``VehicleDetector.detect_frame()``."""

    def test_detect_no_model(self, minimal_config: dict, blank_frame: np.ndarray) -> None:
        """detect_frame() without a loaded model should return []."""
        detector = VehicleDetector(minimal_config)
        result = detector.detect_frame(blank_frame)
        assert result == []

    @patch("modules.vehicle_detector.YOLO")
    def test_detect_returns_list(
        self, mock_yolo_cls: MagicMock, minimal_config: dict, blank_frame: np.ndarray
    ) -> None:
        """detect_frame() should always return a list."""
        mock_model = MagicMock()
        mock_model.return_value = []  # YOLO inference returns empty results
        mock_yolo_cls.return_value = mock_model

        detector = VehicleDetector(minimal_config)
        detector.load_model()
        result = detector.detect_frame(blank_frame)

        assert isinstance(result, list)

    @patch("modules.vehicle_detector.YOLO")
    def test_detect_parses_vehicles(
        self, mock_yolo_cls: MagicMock, minimal_config: dict, blank_frame: np.ndarray
    ) -> None:
        """detect_frame() should return DetectedVehicle objects from YOLO results."""
        box_car = _make_mock_box(2, 0.92, 10, 20, 110, 120)
        box_bus = _make_mock_box(5, 0.78, 200, 300, 400, 500)
        result_obj = _make_mock_result([box_car, box_bus])

        mock_model = MagicMock()
        mock_model.return_value = [result_obj]
        mock_yolo_cls.return_value = mock_model

        detector = VehicleDetector(minimal_config)
        detector.load_model()
        detections = detector.detect_frame(blank_frame)

        assert len(detections) == 2
        assert all(isinstance(d, DetectedVehicle) for d in detections)

        types = {d.vehicle_type for d in detections}
        assert VehicleType.CAR in types
        assert VehicleType.BUS in types

    @patch("modules.vehicle_detector.YOLO")
    def test_detect_filters_non_vehicle_classes(
        self, mock_yolo_cls: MagicMock, minimal_config: dict, blank_frame: np.ndarray
    ) -> None:
        """detect_frame() should exclude classes not in target_classes."""
        box_car = _make_mock_box(2, 0.9, 0, 0, 50, 50)       # car → keep
        box_person = _make_mock_box(0, 0.95, 100, 100, 200, 200)  # person → skip
        box_dog = _make_mock_box(16, 0.88, 300, 300, 400, 400)    # dog → skip
        result_obj = _make_mock_result([box_car, box_person, box_dog])

        mock_model = MagicMock()
        mock_model.return_value = [result_obj]
        mock_yolo_cls.return_value = mock_model

        detector = VehicleDetector(minimal_config)
        detector.load_model()
        detections = detector.detect_frame(blank_frame)

        assert len(detections) == 1
        assert detections[0].vehicle_type == VehicleType.CAR

    @patch("modules.vehicle_detector.YOLO")
    def test_detect_passes_config_thresholds(
        self, mock_yolo_cls: MagicMock, blank_frame: np.ndarray
    ) -> None:
        """detect_frame() should pass conf and iou from config to the model."""
        config = {
            "detection": {
                "confidence_threshold": 0.7,
                "iou_threshold": 0.3,
                "device": "cpu",
                "target_classes": [2],
            }
        }
        mock_model = MagicMock()
        mock_model.return_value = []
        mock_yolo_cls.return_value = mock_model

        detector = VehicleDetector(config)
        detector.load_model()
        detector.detect_frame(blank_frame)

        mock_model.assert_called_once()
        call_kwargs = mock_model.call_args
        assert call_kwargs.kwargs["conf"] == 0.7
        assert call_kwargs.kwargs["iou"] == 0.3
        assert call_kwargs.kwargs["device"] == "cpu"

    @patch("modules.vehicle_detector.YOLO")
    def test_detect_all_four_vehicle_types(
        self, mock_yolo_cls: MagicMock, minimal_config: dict, blank_frame: np.ndarray
    ) -> None:
        """detect_frame() should recognise all four vehicle types."""
        boxes = [
            _make_mock_box(2, 0.9, 0, 0, 10, 10),    # car
            _make_mock_box(3, 0.8, 20, 20, 30, 30),   # motorcycle
            _make_mock_box(5, 0.7, 40, 40, 50, 50),   # bus
            _make_mock_box(7, 0.6, 60, 60, 70, 70),   # truck
        ]
        result_obj = _make_mock_result(boxes)

        mock_model = MagicMock()
        mock_model.return_value = [result_obj]
        mock_yolo_cls.return_value = mock_model

        detector = VehicleDetector(minimal_config)
        detector.load_model()
        detections = detector.detect_frame(blank_frame)

        detected_types = {d.vehicle_type for d in detections}
        assert detected_types == {
            VehicleType.CAR,
            VehicleType.MOTORCYCLE,
            VehicleType.BUS,
            VehicleType.TRUCK,
        }

    @patch("modules.vehicle_detector.YOLO")
    def test_detect_preserves_coordinates(
        self, mock_yolo_cls: MagicMock, minimal_config: dict, blank_frame: np.ndarray
    ) -> None:
        """Detected bounding box coordinates should match YOLO output."""
        box = _make_mock_box(2, 0.9, 55, 66, 155, 266)
        result_obj = _make_mock_result([box])

        mock_model = MagicMock()
        mock_model.return_value = [result_obj]
        mock_yolo_cls.return_value = mock_model

        detector = VehicleDetector(minimal_config)
        detector.load_model()
        detections = detector.detect_frame(blank_frame)

        assert len(detections) == 1
        d = detections[0]
        assert d.bbox == (55, 66, 155, 266)

    @patch("modules.vehicle_detector.YOLO")
    def test_detect_empty_results(
        self, mock_yolo_cls: MagicMock, minimal_config: dict, blank_frame: np.ndarray
    ) -> None:
        """detect_frame() should return [] when YOLO has no detections."""
        result_obj = MagicMock()
        result_obj.boxes = None

        mock_model = MagicMock()
        mock_model.return_value = [result_obj]
        mock_yolo_cls.return_value = mock_model

        detector = VehicleDetector(minimal_config)
        detector.load_model()
        detections = detector.detect_frame(blank_frame)

        assert detections == []


# ---------------------------------------------------------------------------
# _parse_detection tests
# ---------------------------------------------------------------------------

class TestParseDetection:
    """Tests for ``VehicleDetector._parse_detection()``."""

    def test_parse_valid_car(self, minimal_config: dict) -> None:
        """_parse_detection() should return a DetectedVehicle for a car."""
        detector = VehicleDetector(minimal_config)
        box = _make_mock_box(2, 0.95, 10, 20, 100, 200)
        result = detector._parse_detection(box, frame_id=5, timestamp=1234.0)

        assert result is not None
        assert result.vehicle_type == VehicleType.CAR
        assert result.confidence == 0.95
        assert result.frame_id == 5
        assert result.timestamp == 1234.0

    def test_parse_non_vehicle_class(self, minimal_config: dict) -> None:
        """_parse_detection() should return None for non-vehicle COCO classes."""
        detector = VehicleDetector(minimal_config)
        box = _make_mock_box(0, 0.99, 0, 0, 50, 50)  # person
        result = detector._parse_detection(box, frame_id=1, timestamp=0.0)

        assert result is None

    def test_parse_motorcycle(self, minimal_config: dict) -> None:
        """_parse_detection() should correctly map COCO class 3 to MOTORCYCLE."""
        detector = VehicleDetector(minimal_config)
        box = _make_mock_box(3, 0.8, 0, 0, 30, 30)
        result = detector._parse_detection(box, frame_id=1, timestamp=0.0)

        assert result is not None
        assert result.vehicle_type == VehicleType.MOTORCYCLE


# ---------------------------------------------------------------------------
# Annotation tests
# ---------------------------------------------------------------------------

class TestAnnotateFrame:
    """Tests for ``VehicleDetector.annotate_frame()``."""

    def test_annotate_does_not_mutate_original(
        self, minimal_config: dict, blank_frame: np.ndarray, sample_detection: DetectedVehicle
    ) -> None:
        """annotate_frame() must not modify the original frame in-place."""
        original = blank_frame.copy()
        detector = VehicleDetector(minimal_config)
        annotated = detector.annotate_frame(blank_frame, [sample_detection])

        assert np.array_equal(blank_frame, original), "Original frame was mutated!"

    def test_annotate_returns_ndarray(
        self, minimal_config: dict, blank_frame: np.ndarray, sample_detection: DetectedVehicle
    ) -> None:
        """annotate_frame() should return an np.ndarray."""
        detector = VehicleDetector(minimal_config)
        result = detector.annotate_frame(blank_frame, [sample_detection])
        assert isinstance(result, np.ndarray)

    def test_annotate_same_shape(
        self, minimal_config: dict, blank_frame: np.ndarray, sample_detection: DetectedVehicle
    ) -> None:
        """Annotated frame should have the same shape as the original."""
        detector = VehicleDetector(minimal_config)
        result = detector.annotate_frame(blank_frame, [sample_detection])
        assert result.shape == blank_frame.shape

    def test_annotate_empty_detections(
        self, minimal_config: dict, blank_frame: np.ndarray
    ) -> None:
        """annotate_frame([]) should return a clean copy of the frame."""
        detector = VehicleDetector(minimal_config)
        result = detector.annotate_frame(blank_frame, [])
        assert np.array_equal(result, blank_frame)

    def test_annotate_modifies_pixels(
        self, minimal_config: dict, blank_frame: np.ndarray, sample_detection: DetectedVehicle
    ) -> None:
        """annotate_frame() with detections should produce different pixel values."""
        detector = VehicleDetector(minimal_config)
        annotated = detector.annotate_frame(blank_frame, [sample_detection])
        assert not np.array_equal(annotated, blank_frame), (
            "Annotated frame should differ from the original when detections are present."
        )

    def test_annotate_multiple_detections(
        self, minimal_config: dict, blank_frame: np.ndarray
    ) -> None:
        """annotate_frame() should handle multiple detections without error."""
        dets = [
            DetectedVehicle(VehicleType.CAR, 0.9, 10, 10, 100, 100),
            DetectedVehicle(VehicleType.BUS, 0.8, 200, 200, 400, 400),
            DetectedVehicle(VehicleType.TRUCK, 0.7, 500, 300, 700, 500),
        ]
        detector = VehicleDetector(minimal_config)
        result = detector.annotate_frame(blank_frame, dets)
        assert result.shape == blank_frame.shape


# ---------------------------------------------------------------------------
# Release / lifecycle tests
# ---------------------------------------------------------------------------

class TestRelease:
    """Tests for ``VehicleDetector.release()``."""

    @patch("modules.vehicle_detector.cv2")
    def test_release_calls_cap_release(
        self, mock_cv2: MagicMock, minimal_config: dict
    ) -> None:
        """release() should call release() on the VideoCapture object."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 640.0
        mock_cv2.VideoCapture.return_value = mock_cap
        mock_cv2.CAP_PROP_FRAME_WIDTH = 3
        mock_cv2.CAP_PROP_FRAME_HEIGHT = 4
        mock_cv2.CAP_PROP_FPS = 5

        detector = VehicleDetector(minimal_config)
        detector.open_source(0)
        detector.release()

        mock_cap.release.assert_called()
        assert detector.is_open is False

    def test_release_without_source(self, minimal_config: dict) -> None:
        """release() should be safe to call when no source is open."""
        detector = VehicleDetector(minimal_config)
        detector.release()  # Should not raise

    @patch("modules.vehicle_detector.cv2")
    def test_release_idempotent(
        self, mock_cv2: MagicMock, minimal_config: dict
    ) -> None:
        """Calling release() twice should not raise."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 640.0
        mock_cv2.VideoCapture.return_value = mock_cap
        mock_cv2.CAP_PROP_FRAME_WIDTH = 3
        mock_cv2.CAP_PROP_FRAME_HEIGHT = 4
        mock_cv2.CAP_PROP_FPS = 5

        detector = VehicleDetector(minimal_config)
        detector.open_source(0)
        detector.release()
        detector.release()  # Second call should be harmless

    @patch("modules.vehicle_detector.cv2")
    def test_is_open_after_open_and_release(
        self, mock_cv2: MagicMock, minimal_config: dict
    ) -> None:
        """is_open should reflect the lifecycle: False → True → False."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 640.0
        mock_cv2.VideoCapture.return_value = mock_cap
        mock_cv2.CAP_PROP_FRAME_WIDTH = 3
        mock_cv2.CAP_PROP_FRAME_HEIGHT = 4
        mock_cv2.CAP_PROP_FPS = 5

        detector = VehicleDetector(minimal_config)
        assert detector.is_open is False

        detector.open_source(0)
        assert detector.is_open is True

        detector.release()
        assert detector.is_open is False


# ---------------------------------------------------------------------------
# _resolve_source tests
# ---------------------------------------------------------------------------

class TestResolveSource:
    """Tests for the static ``VehicleDetector._resolve_source()`` method."""

    def test_int_passthrough(self) -> None:
        """Integer sources should pass through unchanged."""
        assert VehicleDetector._resolve_source(0) == 0
        assert VehicleDetector._resolve_source(1) == 1

    def test_string_int_cast(self) -> None:
        """String representations of integers should be cast to int."""
        assert VehicleDetector._resolve_source("0") == 0
        assert VehicleDetector._resolve_source("2") == 2

    def test_string_path_passthrough(self) -> None:
        """Non-numeric string sources should remain as strings."""
        path = "data/videos/traffic.mp4"
        assert VehicleDetector._resolve_source(path) == path

    def test_complex_path(self) -> None:
        """Paths with special characters should remain as strings."""
        path = "C:\\Users\\test\\video (1).avi"
        assert VehicleDetector._resolve_source(path) == path


# ---------------------------------------------------------------------------
# get_frame_dimensions tests
# ---------------------------------------------------------------------------

class TestGetFrameDimensions:
    """Tests for ``VehicleDetector.get_frame_dimensions()``."""

    def test_no_source_returns_zero(self, minimal_config: dict) -> None:
        """get_frame_dimensions() with no source should return (0, 0)."""
        detector = VehicleDetector(minimal_config)
        assert detector.get_frame_dimensions() == (0, 0)

    @patch("modules.vehicle_detector.cv2")
    def test_returns_cap_dimensions(
        self, mock_cv2: MagicMock, minimal_config: dict
    ) -> None:
        """get_frame_dimensions() should return values from VideoCapture."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cv2.CAP_PROP_FRAME_WIDTH = 3
        mock_cv2.CAP_PROP_FRAME_HEIGHT = 4
        mock_cv2.CAP_PROP_FPS = 5

        def get_side_effect(prop_id):
            if prop_id == 3:
                return 1920.0
            elif prop_id == 4:
                return 1080.0
            return 0.0

        mock_cap.get.side_effect = get_side_effect
        mock_cv2.VideoCapture.return_value = mock_cap

        detector = VehicleDetector(minimal_config)
        detector.open_source(0)

        assert detector.get_frame_dimensions() == (1920, 1080)
