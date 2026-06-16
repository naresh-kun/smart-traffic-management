"""
tests/test_signal_controller.py
---------------------------------
Unit tests for ``modules.signal_controller``.

Scope
-----
* ``SignalTimings`` serialisation and defaults.
* ``RuleBasedStrategy.calculate_timings()`` maps congestion → green duration.
* ``SignalController.tick()`` advances phases correctly.
* ``SignalController.set_strategy()`` replaces the active strategy.
* Phase cycling: GREEN → YELLOW → RED → GREEN.
"""

from __future__ import annotations

import pytest

from utils.constants import CongestionLevel, SignalPhase
from modules.traffic_analyzer import TrafficMetrics
from modules.signal_controller import (
    SignalTimings,
    RuleBasedStrategy,
    SignalController,
    BaseSignalStrategy,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def signal_config() -> dict:
    """Config dict for SignalController."""
    return {
        "signal": {
            "min_green_seconds": 10,
            "max_green_seconds": 120,
            "yellow_duration_seconds": 3,
            "red_min_seconds": 10,
            "timing_map": {
                "low": 20,
                "medium": 40,
                "high": 60,
                "critical": 90,
            },
        }
    }


def make_metrics(level: CongestionLevel, density: float = 10.0) -> TrafficMetrics:
    """Helper: create a TrafficMetrics with the given congestion level."""
    return TrafficMetrics(
        density_percentage=density,
        congestion_level=level,
        queue_length_estimate=0,
        avg_vehicle_count=5.0,
    )


# ---------------------------------------------------------------------------
# SignalTimings tests
# ---------------------------------------------------------------------------

class TestSignalTimings:
    """Tests for the ``SignalTimings`` dataclass."""

    def test_defaults(self) -> None:
        """SignalTimings should initialise with safe defaults."""
        # TODO: st = SignalTimings()
        # TODO: assert st.current_phase == SignalPhase.RED
        # TODO: assert st.green_duration > 0
        raise NotImplementedError("TODO: implement test_defaults")

    def test_to_dict_keys(self) -> None:
        """to_dict() must expose all API contract keys."""
        # TODO: d = SignalTimings().to_dict()
        # TODO: required = {"green_duration","yellow_duration","red_duration","current_phase","time_remaining"}
        # TODO: assert required <= d.keys()
        raise NotImplementedError("TODO: implement test_to_dict_keys")

    def test_phase_serialised_as_string(self) -> None:
        """to_dict() current_phase must be a plain string."""
        # TODO: d = SignalTimings(current_phase=SignalPhase.GREEN).to_dict()
        # TODO: assert d["current_phase"] == "green"
        raise NotImplementedError("TODO: implement test_phase_serialised_as_string")


# ---------------------------------------------------------------------------
# RuleBasedStrategy tests
# ---------------------------------------------------------------------------

class TestRuleBasedStrategy:
    """Tests for ``RuleBasedStrategy``."""

    def test_low_traffic_green_20s(self, signal_config: dict) -> None:
        """Low congestion should yield 20s green per config."""
        # TODO: strategy = RuleBasedStrategy(signal_config)
        # TODO: timings = strategy.calculate_timings(make_metrics(CongestionLevel.LOW))
        # TODO: assert timings.green_duration == 20
        raise NotImplementedError("TODO: implement test_low_traffic_green_20s")

    def test_critical_traffic_green_90s(self, signal_config: dict) -> None:
        """Critical congestion should yield 90s green per config."""
        # TODO: timings = strategy.calculate_timings(make_metrics(CongestionLevel.CRITICAL))
        # TODO: assert timings.green_duration == 90
        raise NotImplementedError("TODO: implement test_critical_traffic_green_90s")

    def test_green_within_bounds(self, signal_config: dict) -> None:
        """Green duration must always be within [min_green, max_green]."""
        # TODO: for level in CongestionLevel:
        # TODO:     timings = strategy.calculate_timings(make_metrics(level))
        # TODO:     assert 10 <= timings.green_duration <= 120
        raise NotImplementedError("TODO: implement test_green_within_bounds")


# ---------------------------------------------------------------------------
# SignalController tests
# ---------------------------------------------------------------------------

class TestSignalController:
    """Tests for ``SignalController``."""

    def test_instantiation(self, signal_config: dict) -> None:
        """SignalController should instantiate without raising."""
        # TODO: sc = SignalController(signal_config); assert sc is not None
        raise NotImplementedError("TODO: implement test_instantiation")

    def test_calculate_timings_returns_signal_timings(self, signal_config: dict) -> None:
        """calculate_timings() must return a SignalTimings instance."""
        # TODO: sc = SignalController(signal_config)
        # TODO: result = sc.calculate_timings(make_metrics(CongestionLevel.MEDIUM))
        # TODO: assert isinstance(result, SignalTimings)
        raise NotImplementedError("TODO: implement test_calculate_timings_returns_signal_timings")

    def test_tick_advances_time_remaining(self, signal_config: dict) -> None:
        """tick() should decrease time_remaining by the elapsed amount."""
        # TODO: sc.calculate_timings(make_metrics(CongestionLevel.LOW))
        # TODO: before = sc.get_timings().time_remaining
        # TODO: sc.tick(5.0)
        # TODO: assert sc.get_timings().time_remaining == before - 5
        raise NotImplementedError("TODO: implement test_tick_advances_time_remaining")

    def test_phase_transition_on_timeout(self, signal_config: dict) -> None:
        """When time_remaining reaches 0 the phase should advance."""
        # TODO: sc.calculate_timings(make_metrics(CongestionLevel.LOW))
        # TODO: sc.tick(1000.0)  # Exhaust the phase
        # TODO: assert sc.get_current_phase() != SignalPhase.GREEN (was initially GREEN)
        raise NotImplementedError("TODO: implement test_phase_transition_on_timeout")

    def test_set_strategy_replaces_strategy(self, signal_config: dict) -> None:
        """set_strategy() should replace the active timing strategy."""
        # TODO: class DummyStrategy(BaseSignalStrategy):
        # TODO:     def calculate_timings(self, metrics): return SignalTimings(green_duration=999)
        # TODO: sc.set_strategy(DummyStrategy())
        # TODO: timings = sc.calculate_timings(make_metrics(CongestionLevel.LOW))
        # TODO: assert timings.green_duration == 999
        raise NotImplementedError("TODO: implement test_set_strategy_replaces_strategy")
