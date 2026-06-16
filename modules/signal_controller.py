"""
modules/signal_controller.py
------------------------------
Responsibility
--------------
* Compute green / yellow / red durations from traffic metrics.
* Manage the current signal phase and countdown.
* Expose a ``SignalTimings`` snapshot to downstream consumers.
* Allow the timing strategy to be swapped at runtime (extension point
  for future reinforcement learning integration).

This module must NOT:
* Detect vehicles.
* Render dashboard components.
* Access video feeds directly.
"""

from __future__ import annotations

import abc
import time
from dataclasses import dataclass

from utils.logger import get_logger
from utils.constants import CongestionLevel, SignalPhase
from modules.traffic_analyzer import TrafficMetrics

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Data structure
# ---------------------------------------------------------------------------

@dataclass
class SignalTimings:
    """Represents the current timing configuration for all signal phases.

    Attributes
    ----------
    green_duration : int
        Seconds of green phase.
    yellow_duration : int
        Seconds of yellow phase.
    red_duration : int
        Seconds of red phase.
    current_phase : SignalPhase
        The active signal colour right now.
    time_remaining : int
        Seconds until the current phase ends.
    """

    green_duration: int = 20
    yellow_duration: int = 3
    red_duration: int = 20
    current_phase: SignalPhase = SignalPhase.RED
    time_remaining: int = 20

    def to_dict(self) -> dict:
        """Serialise to a plain dictionary.

        Returns
        -------
        dict
            JSON-serialisable representation matching the API contract.
        """
        # TODO: Return all fields as dict; convert enums to str values.
        raise NotImplementedError("TODO: implement to_dict()")


# ---------------------------------------------------------------------------
# Strategy abstract base (extension point for RL / future algorithms)
# ---------------------------------------------------------------------------

class BaseSignalStrategy(abc.ABC):
    """Abstract base class for signal timing strategies.

    Future reinforcement learning agents or alternative rule-based
    strategies must subclass this and implement ``calculate_timings()``.
    """

    @abc.abstractmethod
    def calculate_timings(self, metrics: TrafficMetrics) -> SignalTimings:
        """Compute signal phase durations from traffic metrics.

        Parameters
        ----------
        metrics : TrafficMetrics
            Current traffic state snapshot.

        Returns
        -------
        SignalTimings
            Computed signal durations and current phase.
        """
        ...


# ---------------------------------------------------------------------------
# Default rule-based strategy
# ---------------------------------------------------------------------------

class RuleBasedStrategy(BaseSignalStrategy):
    """Default timing strategy: maps congestion level to fixed green durations.

    Timing values are sourced from ``config.yaml`` (``signal.timing_map``).

    Parameters
    ----------
    config : dict
        The ``signal`` section of ``config.yaml``.
    """

    def __init__(self, config: dict) -> None:
        signal_cfg = config.get("signal", {})
        self._min_green: int = signal_cfg.get("min_green_seconds", 10)
        self._max_green: int = signal_cfg.get("max_green_seconds", 120)
        self._yellow: int = signal_cfg.get("yellow_duration_seconds", 3)
        self._red_min: int = signal_cfg.get("red_min_seconds", 10)
        self._timing_map: dict[str, int] = signal_cfg.get(
            "timing_map",
            {"low": 20, "medium": 40, "high": 60, "critical": 90},
        )
        logger.info("RuleBasedStrategy initialised.")

    def calculate_timings(self, metrics: TrafficMetrics) -> SignalTimings:
        """Map congestion level to a green duration and return timings.

        Parameters
        ----------
        metrics : TrafficMetrics
            Current traffic state with ``congestion_level`` field.

        Returns
        -------
        SignalTimings
            Computed phase durations.
        """
        # TODO: Look up self._timing_map[metrics.congestion_level].
        # TODO: Clamp green to [self._min_green, self._max_green].
        # TODO: Compute red = max(self._red_min, green // 2).
        # TODO: Return SignalTimings with computed durations.
        raise NotImplementedError("TODO: implement calculate_timings()")


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------

class SignalController:
    """Manages traffic signal state and delegates timing to a strategy.

    The strategy can be swapped at runtime via ``set_strategy()``, enabling
    future plug-in of reinforcement learning algorithms without changing
    this class.

    Parameters
    ----------
    config : dict
        Full application config dict; the ``signal`` section is extracted.
    """

    def __init__(self, config: dict) -> None:
        self._config = config
        self._strategy: BaseSignalStrategy = RuleBasedStrategy(config)
        self._current_timings: SignalTimings = SignalTimings()
        self._phase_start_time: float = time.monotonic()
        logger.info("SignalController initialised with RuleBasedStrategy.")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def calculate_timings(self, metrics: TrafficMetrics) -> SignalTimings:
        """Delegate timing calculation to the active strategy.

        Stores the result internally and resets the phase timer.

        Parameters
        ----------
        metrics : TrafficMetrics
            Current traffic state.

        Returns
        -------
        SignalTimings
            Updated signal timings.
        """
        # TODO: self._current_timings = self._strategy.calculate_timings(metrics)
        # TODO: Log the new timings at INFO level.
        # TODO: return self._current_timings
        raise NotImplementedError("TODO: implement calculate_timings()")

    def tick(self, elapsed_seconds: float) -> SignalTimings:
        """Advance the signal state machine by ``elapsed_seconds``.

        Transitions between GREEN → YELLOW → RED → GREEN automatically
        based on the current phase durations.

        Parameters
        ----------
        elapsed_seconds : float
            Seconds elapsed since the last ``tick()`` call.

        Returns
        -------
        SignalTimings
            Updated snapshot with new ``current_phase`` and
            ``time_remaining``.
        """
        # TODO: Decrement time_remaining by elapsed_seconds.
        # TODO: When time_remaining <= 0 trigger _advance_phase().
        # TODO: Update self._current_timings.time_remaining.
        # TODO: Return snapshot.
        raise NotImplementedError("TODO: implement tick()")

    def get_current_phase(self) -> SignalPhase:
        """Return the currently active signal phase.

        Returns
        -------
        SignalPhase
            One of ``GREEN``, ``YELLOW``, ``RED``.
        """
        # TODO: return self._current_timings.current_phase
        raise NotImplementedError("TODO: implement get_current_phase()")

    def set_strategy(self, strategy: BaseSignalStrategy) -> None:
        """Replace the active timing strategy at runtime.

        This is the primary extension point for integrating reinforcement
        learning or other optimisation algorithms in future iterations.

        Parameters
        ----------
        strategy : BaseSignalStrategy
            A new strategy instance implementing ``calculate_timings()``.
        """
        # TODO: Validate type; set self._strategy = strategy; log change.
        raise NotImplementedError("TODO: implement set_strategy()")

    def get_timings(self) -> SignalTimings:
        """Return the most recently computed signal timings snapshot.

        Returns
        -------
        SignalTimings
            Current timings.
        """
        # TODO: return self._current_timings
        raise NotImplementedError("TODO: implement get_timings()")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _advance_phase(self) -> None:
        """Transition the signal to the next phase in the cycle.

        Cycle: GREEN → YELLOW → RED → GREEN.
        """
        # TODO: Determine next phase from current phase.
        # TODO: Set time_remaining to the corresponding duration.
        # TODO: Update current_phase; log the transition.
        raise NotImplementedError("TODO: implement _advance_phase()")
