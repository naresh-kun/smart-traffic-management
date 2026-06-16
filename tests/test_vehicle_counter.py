"""
tests/test_vehicle_counter.py
-------------------------------
Unit tests for ``modules.vehicle_counter``.

Scope
-----
* ``VehicleCount`` dataclass arithmetic and serialisation.
* ``VehicleCounter.update()`` correctly tallies detections by type.
* ``VehicleCounter.reset()`` zeroes all counters.
* Lane assignment logic (when enabled).
* Session total accumulation across frames.
"""

from __future__ import annotations

import pytest

from utils.constants import VehicleType
from modules.vehicle_detector import DetectedVehicle
from modules.vehicle_counter import VehicleCount, VehicleCounter


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def minimal_config() -> dict:
    """Minimal config dict for VehicleCounter."""
    return {
        "counting": {
            "enable_lane_counting": False,
            "lane_count": 4,
            "counting_line_position": 0.6,
        }
    }


@pytest.fixture
def lane_config() -> dict:
    """Config with lane counting enabled."""
    return {
        "counting": {
            "enable_lane_counting": True,
            "lane_count": 4,
            "counting_line_position": 0.6,
        }
    }


def make_detection(vehicle_type: VehicleType, x1: int = 0, x2: int = 100) -> DetectedVehicle:
    """Helper: create a DetectedVehicle with given type and x-coordinates."""
    return DetectedVehicle(
        vehicle_type=vehicle_type,
        confidence=0.9,
        x1=x1, y1=0, x2=x2, y2=100,
    )


# ---------------------------------------------------------------------------
# VehicleCount tests
# ---------------------------------------------------------------------------

class TestVehicleCount:
    """Tests for the ``VehicleCount`` dataclass."""

    def test_default_zero(self) -> None:
        """All fields should default to 0."""
        # TODO: vc = VehicleCount(); assert vc.total_vehicles == 0; etc.
        raise NotImplementedError("TODO: implement test_default_zero")

    def test_to_dict_has_required_keys(self) -> None:
        """to_dict() should include all API contract keys."""
        # TODO: vc = VehicleCount(total_vehicles=5, cars=3, buses=1, trucks=1, motorcycles=0)
        # TODO: assert {"total_vehicles","cars","buses","trucks","motorcycles","lane_counts"} <= vc.to_dict().keys()
        raise NotImplementedError("TODO: implement test_to_dict_has_required_keys")

    def test_addition(self) -> None:
        """Two VehicleCount objects added together should sum their fields."""
        # TODO: a = VehicleCount(total_vehicles=3, cars=2, buses=1)
        # TODO: b = VehicleCount(total_vehicles=2, cars=1, trucks=1)
        # TODO: c = a + b; assert c.total_vehicles == 5; assert c.cars == 3
        raise NotImplementedError("TODO: implement test_addition")


# ---------------------------------------------------------------------------
# VehicleCounter tests
# ---------------------------------------------------------------------------

class TestVehicleCounter:
    """Tests for ``VehicleCounter``."""

    def test_instantiation(self, minimal_config: dict) -> None:
        """VehicleCounter should instantiate without raising."""
        # TODO: counter = VehicleCounter(minimal_config); assert counter is not None
        raise NotImplementedError("TODO: implement test_instantiation")

    def test_update_empty_detections(self, minimal_config: dict) -> None:
        """update([]) should return a VehicleCount with all zeros."""
        # TODO: counter = VehicleCounter(minimal_config)
        # TODO: result = counter.update([]); assert result.total_vehicles == 0
        raise NotImplementedError("TODO: implement test_update_empty_detections")

    def test_update_counts_by_type(self, minimal_config: dict) -> None:
        """update() should correctly count each vehicle type."""
        # TODO: detections = [make_detection(VehicleType.CAR)] * 3 + [make_detection(VehicleType.BUS)]
        # TODO: result = counter.update(detections)
        # TODO: assert result.cars == 3; assert result.buses == 1; assert result.total_vehicles == 4
        raise NotImplementedError("TODO: implement test_update_counts_by_type")

    def test_reset_zeroes_counters(self, minimal_config: dict) -> None:
        """reset() should zero all counters."""
        # TODO: counter.update([make_detection(VehicleType.TRUCK)])
        # TODO: counter.reset()
        # TODO: assert counter.get_counts().total_vehicles == 0
        raise NotImplementedError("TODO: implement test_reset_zeroes_counters")

    def test_session_total_accumulates(self, minimal_config: dict) -> None:
        """session_total should accumulate across multiple update() calls."""
        # TODO: Call update() twice with 3 detections each.
        # TODO: assert counter.session_total == 6
        raise NotImplementedError("TODO: implement test_session_total_accumulates")

    def test_reset_clears_session_total(self, minimal_config: dict) -> None:
        """reset() must also zero session_total."""
        # TODO: counter.update([...]); counter.reset(); assert counter.session_total == 0
        raise NotImplementedError("TODO: implement test_reset_clears_session_total")

    def test_lane_assignment_returns_valid_lane(self, lane_config: dict) -> None:
        """_assign_lane() should return a lane identifier within bounds."""
        # TODO: counter = VehicleCounter(lane_config)
        # TODO: detection = make_detection(VehicleType.CAR, x1=0, x2=50)
        # TODO: lane = counter._assign_lane(detection, frame_width=1280)
        # TODO: assert lane.startswith("lane_"); lane_num = int(lane.split("_")[1]); assert 1 <= lane_num <= 4
        raise NotImplementedError("TODO: implement test_lane_assignment_returns_valid_lane")
