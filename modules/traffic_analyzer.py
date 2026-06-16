"""
modules/traffic_analyzer.py
----------------------------
Responsibility
--------------
* Calculate traffic density as a percentage.
* Classify density into a congestion level (Low / Medium / High / Critical).
* Estimate queue length.
* Maintain a rolling history for average vehicle counts.
* Produce a ``TrafficMetrics`` snapshot consumed by downstream modules.

This module must NOT:
* Perform vehicle detection.
* Render dashboard components.
* Control traffic signals directly.
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Deque

from utils.logger import get_logger
from utils.constants import CongestionLevel
from modules.vehicle_counter import VehicleCount

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Data structure
# ---------------------------------------------------------------------------

@dataclass
class TrafficMetrics:
    """Full traffic-state snapshot for a single point in time.

    Attributes
    ----------
    density_percentage : float
        Road occupancy as a percentage (0–100).
    congestion_level : CongestionLevel
        Classified congestion state.
    queue_length_estimate : int
        Estimated number of vehicles waiting in the queue.
    avg_vehicle_count : float
        Smoothed average vehicle count over the history window.
    timestamp : float
        Unix epoch seconds when the snapshot was taken.
    """

    density_percentage: float = 0.0
    congestion_level: CongestionLevel = CongestionLevel.LOW
    queue_length_estimate: int = 0
    avg_vehicle_count: float = 0.0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        """Serialise this snapshot to a plain dictionary.

        Returns
        -------
        dict
            JSON-serialisable representation matching the API contract.
        """
        # TODO: Return dict with all fields; convert CongestionLevel to str.
        raise NotImplementedError("TODO: implement to_dict()")


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------

class TrafficAnalyzer:
    """Analyses vehicle counts to produce traffic metrics.

    Parameters
    ----------
    config : dict
        The ``analysis`` section of ``config.yaml``.
    """

    def __init__(self, config: dict) -> None:
        self._config = config
        self._density_area_sqm: float = config.get("analysis", {}).get(
            "density_area_sqm", 500.0
        )
        self._history_window: int = config.get("analysis", {}).get(
            "history_window", 10
        )
        thresholds = config.get("analysis", {}).get("congestion_thresholds", {})
        self._threshold_low: int = thresholds.get("low", 20)
        self._threshold_medium: int = thresholds.get("medium", 40)
        self._threshold_high: int = thresholds.get("high", 60)

        # Rolling history of recent vehicle counts (newest last)
        self._count_history: Deque[int] = deque(maxlen=self._history_window)

        logger.info("TrafficAnalyzer initialised.")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_metrics(self, count: VehicleCount) -> TrafficMetrics:
        """Produce a complete ``TrafficMetrics`` snapshot from a count.

        This is the primary method called by the main loop. It
        internally calls ``calculate_density``, ``classify_congestion``,
        and ``estimate_queue_length``.

        Parameters
        ----------
        count : VehicleCount
            Current frame vehicle count from ``VehicleCounter``.

        Returns
        -------
        TrafficMetrics
            Full traffic-state snapshot.
        """
        # TODO: Append count.total_vehicles to self._count_history.
        # TODO: density = self.calculate_density(count)
        # TODO: level = self.classify_congestion(density)
        # TODO: queue = self.estimate_queue_length(count)
        # TODO: avg = moving average of self._count_history
        # TODO: Construct and return TrafficMetrics.
        raise NotImplementedError("TODO: implement generate_metrics()")

    def calculate_density(self, count: VehicleCount) -> float:
        """Calculate traffic density as a percentage.

        Density is computed as the ratio of the current vehicle count to
        the theoretical maximum capacity of the monitored road area.

        Parameters
        ----------
        count : VehicleCount
            Current vehicle count snapshot.

        Returns
        -------
        float
            Density percentage in [0.0, 100.0].
        """
        # TODO: Estimate capacity from self._density_area_sqm (e.g. area / avg vehicle size).
        # TODO: density = (count.total_vehicles / capacity) * 100.0
        # TODO: return clamp(density, 0.0, 100.0)
        raise NotImplementedError("TODO: implement calculate_density()")

    def classify_congestion(self, density: float) -> CongestionLevel:
        """Map a density percentage to a ``CongestionLevel``.

        Thresholds are read from ``config.yaml`` (not hardcoded).

        Parameters
        ----------
        density : float
            Density percentage from ``calculate_density()``.

        Returns
        -------
        CongestionLevel
            One of: ``LOW``, ``MEDIUM``, ``HIGH``, ``CRITICAL``.
        """
        # TODO: Compare density against self._threshold_* values.
        # TODO: Note: thresholds are in vehicle counts; convert or use vehicle count directly.
        raise NotImplementedError("TODO: implement classify_congestion()")

    def estimate_queue_length(self, count: VehicleCount) -> int:
        """Estimate the number of vehicles currently queued.

        Uses a heuristic based on total vehicle count and configurable
        density thresholds.

        Parameters
        ----------
        count : VehicleCount
            Current vehicle count snapshot.

        Returns
        -------
        int
            Estimated queue length (0 or more).
        """
        # TODO: Apply a simple heuristic (e.g. proportion of heavy vehicles).
        raise NotImplementedError("TODO: implement estimate_queue_length()")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _vehicle_capacity(self) -> float:
        """Estimate the maximum vehicle capacity of the monitored area.

        Uses average vehicle footprint (approx. 4.5 m × 2 m) relative to
        ``self._density_area_sqm``.

        Returns
        -------
        float
            Theoretical maximum vehicle count for the road area.
        """
        # TODO: avg_vehicle_sqm = 9.0; return self._density_area_sqm / avg_vehicle_sqm
        raise NotImplementedError("TODO: implement _vehicle_capacity()")

    @property
    def count_history(self) -> list[int]:
        """Return the raw count history window as a list."""
        return list(self._count_history)
