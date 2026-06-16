"""
utils/constants.py
------------------
System-wide enumerations and named constants.

Rules
-----
* Every "magic value" used in more than one place must be defined here.
* Numeric thresholds belong in ``config/config.yaml``; only symbolic names
  (enums, string literals) live here.
* Do NOT import from other project modules to avoid circular dependencies.
"""

from enum import Enum, unique


# ---------------------------------------------------------------------------
# Congestion levels
# ---------------------------------------------------------------------------

@unique
class CongestionLevel(str, Enum):
    """Enumeration of possible traffic congestion states.

    Inherits from ``str`` so instances can be used directly as strings
    (e.g. in database writes and JSON serialisation) without calling
    ``.value``.

    Example
    -------
    >>> CongestionLevel.LOW == "low"
    True
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ---------------------------------------------------------------------------
# Signal phases
# ---------------------------------------------------------------------------

@unique
class SignalPhase(str, Enum):
    """Enumeration of traffic signal phases."""

    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


# ---------------------------------------------------------------------------
# Vehicle types (COCO class names used by YOLOv8)
# ---------------------------------------------------------------------------

@unique
class VehicleType(str, Enum):
    """Vehicle categories detected by the object detection model."""

    CAR = "car"
    BUS = "bus"
    TRUCK = "truck"
    MOTORCYCLE = "motorcycle"


# ---------------------------------------------------------------------------
# COCO class-ID → VehicleType mapping
# ---------------------------------------------------------------------------

COCO_CLASS_ID_TO_VEHICLE_TYPE: dict[int, VehicleType] = {
    2: VehicleType.CAR,
    3: VehicleType.MOTORCYCLE,
    5: VehicleType.BUS,
    7: VehicleType.TRUCK,
}
"""Maps YOLOv8 COCO class IDs to ``VehicleType`` enum members."""

VEHICLE_TYPE_TO_COCO_CLASS_ID: dict[VehicleType, int] = {
    v: k for k, v in COCO_CLASS_ID_TO_VEHICLE_TYPE.items()
}
"""Reverse mapping from ``VehicleType`` to COCO class ID."""


# ---------------------------------------------------------------------------
# Default display colours (BGR for OpenCV)
# ---------------------------------------------------------------------------

BOUNDING_BOX_COLORS: dict[VehicleType, tuple[int, int, int]] = {
    VehicleType.CAR: (0, 255, 0),          # Green
    VehicleType.BUS: (255, 165, 0),        # Orange
    VehicleType.TRUCK: (0, 0, 255),        # Red
    VehicleType.MOTORCYCLE: (255, 0, 255), # Magenta
}
"""BGR colour tuples for drawing bounding boxes per vehicle type."""


# ---------------------------------------------------------------------------
# Congestion level display colours (RGB for Streamlit / Plotly)
# ---------------------------------------------------------------------------

CONGESTION_COLORS_RGB: dict[CongestionLevel, str] = {
    CongestionLevel.LOW: "#22c55e",       # Green
    CongestionLevel.MEDIUM: "#f59e0b",    # Amber
    CongestionLevel.HIGH: "#ef4444",      # Red
    CongestionLevel.CRITICAL: "#7c3aed",  # Purple
}
"""Hex RGB colours for rendering congestion levels in the dashboard."""


# ---------------------------------------------------------------------------
# Miscellaneous
# ---------------------------------------------------------------------------

CONFIG_PATH_DEFAULT: str = "config/config.yaml"
DB_DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%S.%fZ"
LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
