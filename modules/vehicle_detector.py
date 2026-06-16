"""
modules/vehicle_detector.py
----------------------------
Responsibility
--------------
* Read frames from a webcam or video file.
* Run YOLOv8 inference to detect vehicles.
* Classify vehicles by type (car, bus, truck, motorcycle).
* Annotate frames with bounding boxes.
* Return structured ``DetectedVehicle`` objects.

This module must NOT:
* Calculate traffic density or congestion levels.
* Control signal timings.
* Update the dashboard.
* Access the database.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from utils.logger import get_logger
from utils.constants import VehicleType, COCO_CLASS_ID_TO_VEHICLE_TYPE, BOUNDING_BOX_COLORS

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Data structure
# ---------------------------------------------------------------------------

@dataclass
class DetectedVehicle:
    """Represents a single vehicle detection from one frame.

    Attributes
    ----------
    vehicle_type : VehicleType
        Classified vehicle category.
    confidence : float
        Detection confidence score in [0.0, 1.0].
    x1, y1, x2, y2 : int
        Bounding-box corner pixel coordinates.
    frame_id : int
        Sequential frame index within the current session.
    timestamp : float
        Unix epoch seconds at the time of detection.
    """

    vehicle_type: VehicleType
    confidence: float
    x1: int
    y1: int
    x2: int
    y2: int
    frame_id: int = 0
    timestamp: float = field(default_factory=time.time)

    @property
    def bbox(self) -> tuple[int, int, int, int]:
        """Return the bounding box as ``(x1, y1, x2, y2)``."""
        return (self.x1, self.y1, self.x2, self.y2)

    @property
    def centre(self) -> tuple[int, int]:
        """Return the centre pixel of the bounding box."""
        return ((self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2)

    def to_dict(self) -> dict:
        """Serialise the detection to a plain dictionary.

        Returns
        -------
        dict
            JSON-serialisable representation matching the API contract.
        """
        # TODO: Return dict with vehicle_type, confidence, position, frame_id, timestamp.
        raise NotImplementedError("TODO: implement to_dict()")


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------

class VehicleDetector:
    """Handles video capture and YOLOv8-based vehicle detection.

    Parameters
    ----------
    config : dict
        The ``detection`` and ``video`` sections of ``config.yaml``.

    Example
    -------
    >>> detector = VehicleDetector(config)
    >>> detector.load_model()
    True
    >>> detector.open_source(0)
    True
    >>> ok, frame = detector.read_frame()
    >>> if ok:
    ...     detections = detector.detect_frame(frame)
    """

    def __init__(self, config: dict) -> None:
        self._config = config
        self._model = None          # ultralytics YOLO instance
        self._cap = None            # cv2.VideoCapture instance
        self._frame_id: int = 0
        self._model_path: str = config.get("detection", {}).get(
            "model_path", "models/yolov8/yolov8n.pt"
        )
        self._confidence_threshold: float = config.get("detection", {}).get(
            "confidence_threshold", 0.45
        )
        self._iou_threshold: float = config.get("detection", {}).get(
            "iou_threshold", 0.5
        )
        self._device: str = config.get("detection", {}).get("device", "cpu")
        self._target_class_ids: list[int] = config.get("detection", {}).get(
            "target_classes", [2, 3, 5, 7]
        )
        logger.info("VehicleDetector initialised.")

    # ------------------------------------------------------------------
    # Model management
    # ------------------------------------------------------------------

    def load_model(self) -> bool:
        """Load pretrained YOLOv8 weights from ``self._model_path``.

        Downloads weights automatically from the Ultralytics hub if the
        file is absent locally.

        Returns
        -------
        bool
            ``True`` if the model loaded successfully, ``False`` otherwise.
        """
        # TODO: from ultralytics import YOLO
        # TODO: self._model = YOLO(self._model_path)
        # TODO: Log success or failure and return bool.
        raise NotImplementedError("TODO: implement load_model()")

    # ------------------------------------------------------------------
    # Video source management
    # ------------------------------------------------------------------

    def open_source(self, source: int | str) -> bool:
        """Open a webcam or video file for frame capture.

        Parameters
        ----------
        source : int | str
            Integer webcam index (e.g. ``0``) or path to a ``.mp4`` file.

        Returns
        -------
        bool
            ``True`` if the source opened successfully.
        """
        # TODO: import cv2; self._cap = cv2.VideoCapture(source)
        # TODO: Check cap.isOpened(); log and return result.
        raise NotImplementedError("TODO: implement open_source()")

    def read_frame(self) -> tuple[bool, Optional[np.ndarray]]:
        """Read the next frame from the video source.

        Returns
        -------
        tuple[bool, Optional[np.ndarray]]
            ``(success, frame)`` where ``frame`` is a BGR numpy array or
            ``None`` if reading failed.
        """
        # TODO: ret, frame = self._cap.read(); self._frame_id += 1; return ret, frame
        raise NotImplementedError("TODO: implement read_frame()")

    def get_frame_dimensions(self) -> tuple[int, int]:
        """Return ``(width, height)`` of the video source frames.

        Returns
        -------
        tuple[int, int]
            Frame dimensions in pixels.
        """
        # TODO: Query cap.get(cv2.CAP_PROP_FRAME_WIDTH/HEIGHT)
        raise NotImplementedError("TODO: implement get_frame_dimensions()")

    def release(self) -> None:
        """Release the video capture resource.

        Must be called when the processing loop ends to free the camera or
        file handle.
        """
        # TODO: if self._cap: self._cap.release(); log.
        raise NotImplementedError("TODO: implement release()")

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------

    def detect_frame(self, frame: np.ndarray) -> list[DetectedVehicle]:
        """Run YOLOv8 inference on a single frame.

        Parameters
        ----------
        frame : np.ndarray
            BGR image array as returned by ``read_frame()``.

        Returns
        -------
        list[DetectedVehicle]
            All detected vehicle objects for this frame, filtered to
            ``self._target_class_ids`` and confidence threshold.
        """
        # TODO: results = self._model(frame, conf=threshold, iou=iou, device=device)
        # TODO: Parse results.boxes; filter by target class IDs.
        # TODO: Build DetectedVehicle instances and return list.
        raise NotImplementedError("TODO: implement detect_frame()")

    def _parse_detection(
        self,
        box: "ultralytics.engine.results.Boxes",  # type: ignore[name-defined]
        frame_id: int,
    ) -> Optional[DetectedVehicle]:
        """Convert a single YOLO result box to a ``DetectedVehicle``.

        Parameters
        ----------
        box : ultralytics Boxes object
            A single detection box from a YOLO result.
        frame_id : int
            Current frame counter.

        Returns
        -------
        Optional[DetectedVehicle]
            Parsed vehicle, or ``None`` if the class is not a target vehicle.
        """
        # TODO: Extract class_id, confidence, xyxy coords.
        # TODO: Map class_id via COCO_CLASS_ID_TO_VEHICLE_TYPE; skip if absent.
        # TODO: Construct and return DetectedVehicle.
        raise NotImplementedError("TODO: implement _parse_detection()")

    # ------------------------------------------------------------------
    # Annotation
    # ------------------------------------------------------------------

    def annotate_frame(
        self, frame: np.ndarray, detections: list[DetectedVehicle]
    ) -> np.ndarray:
        """Draw bounding boxes and labels on a copy of ``frame``.

        Parameters
        ----------
        frame : np.ndarray
            Original BGR frame from the video source.
        detections : list[DetectedVehicle]
            Detections to render onto the frame.

        Returns
        -------
        np.ndarray
            Annotated BGR frame (copy of input with drawings applied).
        """
        # TODO: import cv2; annotated = frame.copy()
        # TODO: For each detection draw rectangle + label using BOUNDING_BOX_COLORS.
        # TODO: Return annotated frame.
        raise NotImplementedError("TODO: implement annotate_frame()")

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def frame_id(self) -> int:
        """Return the count of frames read so far."""
        return self._frame_id

    @property
    def is_open(self) -> bool:
        """Return ``True`` if the video source is currently open."""
        # TODO: return self._cap is not None and self._cap.isOpened()
        raise NotImplementedError("TODO: implement is_open property")
