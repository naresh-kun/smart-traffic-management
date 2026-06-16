"""
modules/vehicle_counter.py
---------------------------
Responsibility
--------------
* Count detected vehicles received from ``VehicleDetector``.
* Maintain running totals by vehicle type.
* Maintain per-lane counts when lane detection is enabled.
* Expose a snapshot ``VehicleCount`` on demand.

This module must NOT:
* Perform object detection.
* Calculate congestion or density.
* Control traffic signals.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from utils.logger import get_logger
from utils.constants import VehicleType
from modules.vehicle_detector import DetectedVehicle

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Data structure
# ---------------------------------------------------------------------------

@dataclass
class VehicleCount:
    """Snapshot of vehicle counts at a point in time.

    Attributes
    ----------
    total_vehicles : int
        Total number of vehicles detected in the current frame/window.
    cars : int
        Count of cars.
    buses : int
        Count of buses.
    trucks : int
        Count of trucks.
    motorcycles : int
        Count of motorcycles.
    lane_counts : dict
        Per-lane vehicle counts, keyed by lane identifier string.
    """

    total_vehicles: int = 0
    cars: int = 0
    buses: int = 0
    trucks: int = 0
    motorcycles: int = 0
    lane_counts: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Return the count snapshot as a plain dictionary.

        Returns
        -------
        dict
            JSON-serialisable representation matching the API contract.
        """
        # TODO: Return all fields as a dict.
        raise NotImplementedError("TODO: implement to_dict()")

    def __add__(self, other: "VehicleCount") -> "VehicleCount":
        """Support aggregation of two snapshots with the ``+`` operator.

        Parameters
        ----------
        other : VehicleCount
            Another count snapshot to add to this one.

        Returns
        -------
        VehicleCount
            New snapshot with summed fields.
        """
        # TODO: Sum corresponding fields; merge lane_counts dicts.
        raise NotImplementedError("TODO: implement __add__()")


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------

class VehicleCounter:
    """Maintains running vehicle counts across frames.

    Receives detection lists from ``VehicleDetector`` and produces
    ``VehicleCount`` snapshots consumed by ``TrafficAnalyzer``.

    Parameters
    ----------
    config : dict
        The ``counting`` section of ``config.yaml``.
    """

    def __init__(self, config: dict) -> None:
        self._config = config
        self._enable_lane_counting: bool = config.get(
            "counting", {}
        ).get("enable_lane_counting", False)
        self._lane_count: int = config.get("counting", {}).get("lane_count", 4)
        self._counting_line_y: float = config.get("counting", {}).get(
            "counting_line_position", 0.6
        )

        # Per-frame counts (reset on each update call)
        self._current_count: VehicleCount = VehicleCount()

        # Cumulative session counters
        self._session_total: int = 0

        logger.info("VehicleCounter initialised.")

    # ------------------------------------------------------------------
    # Core methods
    # ------------------------------------------------------------------

    def update(self, detections: list[DetectedVehicle]) -> VehicleCount:
        """Process a list of detections and return the current frame count.

        Parameters
        ----------
        detections : list[DetectedVehicle]
            Detections produced by ``VehicleDetector.detect_frame()``.

        Returns
        -------
        VehicleCount
            Count snapshot for the current frame.
        """
        # TODO: Reset per-frame counters.
        # TODO: Increment type-specific counts based on detection.vehicle_type.
        # TODO: Optionally call _assign_lane() for each detection.
        # TODO: Update self._current_count; increment self._session_total.
        # TODO: Log count if debug level.
        raise NotImplementedError("TODO: implement update()")

    def get_counts(self) -> VehicleCount:
        """Return the most recent frame's vehicle count snapshot.

        Returns
        -------
        VehicleCount
            Latest count snapshot.
        """
        # TODO: return a copy of self._current_count
        raise NotImplementedError("TODO: implement get_counts()")

    def get_lane_counts(self) -> dict[str, int]:
        """Return per-lane vehicle counts.

        Returns
        -------
        dict[str, int]
            Mapping of lane identifier to vehicle count.
            Empty dict when lane counting is disabled.
        """
        # TODO: return self._current_count.lane_counts.copy()
        raise NotImplementedError("TODO: implement get_lane_counts()")

    def reset(self) -> None:
        """Reset all per-frame and session counters to zero.

        Typically called at the start of a new session or when the video
        source changes.
        """
        # TODO: Re-initialise self._current_count and self._session_total.
        raise NotImplementedError("TODO: implement reset()")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _assign_lane(
        self, detection: DetectedVehicle, frame_width: int
    ) -> str:
        """Determine which lane a detection belongs to.

        Divides the frame width equally into ``self._lane_count`` lanes
        and maps the detection centre-x to a lane identifier.

        Parameters
        ----------
        detection : DetectedVehicle
            The vehicle detection to classify.
        frame_width : int
            Width of the current video frame in pixels.

        Returns
        -------
        str
            Lane identifier string, e.g. ``"lane_1"``.
        """
        # TODO: lane_width = frame_width / self._lane_count
        # TODO: lane_index = int(detection.centre[0] / lane_width) + 1
        # TODO: return f"lane_{min(lane_index, self._lane_count)}"
        raise NotImplementedError("TODO: implement _assign_lane()")

    @property
    def session_total(self) -> int:
        """Total vehicles counted since the last ``reset()`` call."""
        return self._session_total
