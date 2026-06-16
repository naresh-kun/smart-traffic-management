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
from pathlib import Path
from typing import Any, Optional

import cv2
import numpy as np
from ultralytics import YOLO

from utils.logger import get_logger
from utils.constants import (
    VehicleType,
    COCO_CLASS_ID_TO_VEHICLE_TYPE,
    BOUNDING_BOX_COLORS,
)

logger = get_logger(__name__)

# Thickness and font settings for annotation rendering (not user-facing
# thresholds — purely cosmetic, so they live here rather than config.yaml).
_BBOX_THICKNESS: int = 2
_LABEL_FONT_SCALE: float = 0.55
_LABEL_FONT: int = cv2.FONT_HERSHEY_SIMPLEX
_LABEL_THICKNESS: int = 2
_LABEL_BG_ALPHA: float = 0.6  # opacity of the label background rectangle


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

        Returns a structure that matches the ``DetectedVehicle`` data
        structure defined in ``API_CONTRACT.md``.

        Returns
        -------
        dict
            JSON-serialisable representation with keys:
            ``vehicle_type``, ``confidence``, ``position``,
            ``frame_id``, ``timestamp``.
        """
        return {
            "vehicle_type": str(self.vehicle_type.value),
            "confidence": round(self.confidence, 4),
            "position": {
                "x1": self.x1,
                "y1": self.y1,
                "x2": self.x2,
                "y2": self.y2,
            },
            "frame_id": self.frame_id,
            "timestamp": self.timestamp,
        }


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------

class VehicleDetector:
    """Handles video capture and YOLOv8-based vehicle detection.

    Parameters
    ----------
    config : dict
        The full application configuration dictionary (or at least the
        ``detection`` and ``video`` sections of ``config.yaml``).

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
        self._model: Optional[YOLO] = None
        self._cap: Optional[cv2.VideoCapture] = None
        self._frame_id: int = 0

        # Pull detection settings from config with safe defaults
        det_cfg = config.get("detection", {})
        self._model_path: str = det_cfg.get(
            "model_path", "models/yolov8/yolov8n.pt"
        )
        self._confidence_threshold: float = det_cfg.get(
            "confidence_threshold", 0.45
        )
        self._iou_threshold: float = det_cfg.get("iou_threshold", 0.5)
        self._device: str = det_cfg.get("device", "cpu")
        self._target_class_ids: set[int] = set(
            det_cfg.get("target_classes", [2, 3, 5, 7])
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
        try:
            logger.info(f"Loading YOLOv8 model from '{self._model_path}' ...")
            self._model = YOLO(self._model_path)
            logger.info(
                f"YOLOv8 model loaded successfully "
                f"(device={self._device}, "
                f"conf_threshold={self._confidence_threshold}, "
                f"iou_threshold={self._iou_threshold})."
            )
            return True
        except Exception as exc:
            logger.error(f"Failed to load YOLOv8 model: {exc}")
            self._model = None
            return False

    # ------------------------------------------------------------------
    # Video source management
    # ------------------------------------------------------------------

    def open_source(self, source: int | str) -> bool:
        """Open a webcam or video file for frame capture.

        If a previous source was open, it is released first.

        Parameters
        ----------
        source : int | str
            Integer webcam index (e.g. ``0``) or path to a ``.mp4`` file.

        Returns
        -------
        bool
            ``True`` if the source opened successfully.
        """
        # Release any previous capture handle
        if self._cap is not None:
            self._cap.release()
            logger.debug("Previous video source released.")

        # Normalise: if source looks like an integer string, cast it
        resolved_source = self._resolve_source(source)

        logger.info(f"Opening video source: {resolved_source}")
        self._cap = cv2.VideoCapture(resolved_source)

        if not self._cap.isOpened():
            logger.error(
                f"Failed to open video source '{resolved_source}'. "
                "Check that the path exists or the camera is connected."
            )
            self._cap = None
            return False

        width, height = self.get_frame_dimensions()
        fps = self._cap.get(cv2.CAP_PROP_FPS) or 0.0
        logger.info(
            f"Video source opened: {width}x{height} @ {fps:.1f} FPS."
        )
        self._frame_id = 0
        return True

    def read_frame(self) -> tuple[bool, Optional[np.ndarray]]:
        """Read the next frame from the video source.

        Returns
        -------
        tuple[bool, Optional[np.ndarray]]
            ``(success, frame)`` where ``frame`` is a BGR numpy array or
            ``None`` if reading failed.
        """
        if self._cap is None or not self._cap.isOpened():
            logger.warning("read_frame() called but no video source is open.")
            return False, None

        ret, frame = self._cap.read()
        if ret:
            self._frame_id += 1
        else:
            logger.debug(
                f"read_frame() returned empty at frame_id={self._frame_id}. "
                "End of stream or camera error."
            )
        return ret, frame if ret else None

    def get_frame_dimensions(self) -> tuple[int, int]:
        """Return ``(width, height)`` of the video source frames.

        Returns
        -------
        tuple[int, int]
            Frame dimensions in pixels. ``(0, 0)`` if no source is open.
        """
        if self._cap is None:
            return (0, 0)
        width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return (width, height)

    def release(self) -> None:
        """Release the video capture resource.

        Must be called when the processing loop ends to free the camera or
        file handle. Safe to call multiple times.
        """
        if self._cap is not None:
            self._cap.release()
            logger.info(
                f"Video source released after {self._frame_id} frames."
            )
            self._cap = None

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
        if self._model is None:
            logger.error("detect_frame() called but model is not loaded.")
            return []

        # Run YOLOv8 inference – verbose=False suppresses the built-in
        # Ultralytics progress prints that clutter production logs.
        results = self._model(
            frame,
            conf=self._confidence_threshold,
            iou=self._iou_threshold,
            device=self._device,
            verbose=False,
        )

        detections: list[DetectedVehicle] = []
        current_time = time.time()

        for result in results:
            if result.boxes is None:
                continue
            for box in result.boxes:
                vehicle = self._parse_detection(box, self._frame_id, current_time)
                if vehicle is not None:
                    detections.append(vehicle)

        if detections:
            logger.debug(
                f"Frame {self._frame_id}: detected {len(detections)} vehicle(s)."
            )
        return detections

    def _parse_detection(
        self,
        box: Any,
        frame_id: int,
        timestamp: float,
    ) -> Optional[DetectedVehicle]:
        """Convert a single YOLO result box to a ``DetectedVehicle``.

        Parameters
        ----------
        box : ultralytics Boxes element
            A single detection box from a YOLO result.
        frame_id : int
            Current frame counter.
        timestamp : float
            Unix epoch seconds shared across all detections in this frame.

        Returns
        -------
        Optional[DetectedVehicle]
            Parsed vehicle, or ``None`` if the class is not a target vehicle
            type.
        """
        # Extract scalar values from single-element tensors
        class_id = int(box.cls.item())

        # Skip classes not in our target set
        if class_id not in self._target_class_ids:
            return None

        vehicle_type = COCO_CLASS_ID_TO_VEHICLE_TYPE.get(class_id)
        if vehicle_type is None:
            return None

        confidence = float(box.conf.item())

        # xyxy returns shape (1, 4) – squeeze to 1-D then cast to int
        coords = box.xyxy.squeeze().tolist()
        x1, y1, x2, y2 = int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])

        return DetectedVehicle(
            vehicle_type=vehicle_type,
            confidence=confidence,
            x1=x1,
            y1=y1,
            x2=x2,
            y2=y2,
            frame_id=frame_id,
            timestamp=timestamp,
        )

    # ------------------------------------------------------------------
    # Annotation
    # ------------------------------------------------------------------

    def annotate_frame(
        self, frame: np.ndarray, detections: list[DetectedVehicle]
    ) -> np.ndarray:
        """Draw bounding boxes and labels on a copy of ``frame``.

        The original frame is never modified.

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
        annotated = frame.copy()

        for det in detections:
            colour = BOUNDING_BOX_COLORS.get(det.vehicle_type, (255, 255, 255))

            # Draw bounding box
            cv2.rectangle(
                annotated,
                (det.x1, det.y1),
                (det.x2, det.y2),
                colour,
                _BBOX_THICKNESS,
            )

            # Prepare label text
            label = f"{det.vehicle_type.value} {det.confidence:.0%}"
            (text_w, text_h), baseline = cv2.getTextSize(
                label, _LABEL_FONT, _LABEL_FONT_SCALE, _LABEL_THICKNESS
            )

            # Draw a semi-transparent background rectangle for readability
            label_y1 = max(det.y1 - text_h - baseline - 4, 0)
            label_y2 = max(det.y1, text_h + baseline + 4)
            overlay = annotated.copy()
            cv2.rectangle(
                overlay,
                (det.x1, label_y1),
                (det.x1 + text_w + 4, label_y2),
                colour,
                cv2.FILLED,
            )
            cv2.addWeighted(
                overlay, _LABEL_BG_ALPHA,
                annotated, 1 - _LABEL_BG_ALPHA,
                0,
                annotated,
            )

            # Draw label text
            cv2.putText(
                annotated,
                label,
                (det.x1 + 2, label_y2 - baseline - 2),
                _LABEL_FONT,
                _LABEL_FONT_SCALE,
                (255, 255, 255),
                _LABEL_THICKNESS,
                lineType=cv2.LINE_AA,
            )

        return annotated

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
        return self._cap is not None and self._cap.isOpened()

    @property
    def model_loaded(self) -> bool:
        """Return ``True`` if the YOLO model has been loaded."""
        return self._model is not None

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_source(source: int | str) -> int | str:
        """Normalise the video source value for OpenCV.

        Parameters
        ----------
        source : int | str
            Either an integer camera index, a string file path, or a
            string that looks like an integer (e.g. ``"0"``).

        Returns
        -------
        int | str
            Integer if the source is a camera index, string path otherwise.
        """
        if isinstance(source, int):
            return source
        # A string that is purely numeric is a camera index
        try:
            return int(source)
        except (ValueError, TypeError):
            return str(source)
