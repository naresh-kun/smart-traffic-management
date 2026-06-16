"""
tests/test_congestion_predictor.py
------------------------------------
Unit tests for ``modules.congestion_predictor``.

Scope
-----
* ``PredictionResult`` serialisation and defaults.
* ``build_features()`` output shape and dtype.
* ``is_ready()`` returns False before training.
* ``train()`` sets is_ready() to True.
* ``predict()`` returns a ``PredictionResult`` after training.
* ``accumulate()`` collects samples and triggers retraining.
"""

from __future__ import annotations

import numpy as np
import pytest

from utils.constants import CongestionLevel
from modules.vehicle_counter import VehicleCount
from modules.traffic_analyzer import TrafficMetrics
from modules.congestion_predictor import CongestionPredictor, PredictionResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def predictor_config() -> dict:
    """Minimal config dict for CongestionPredictor."""
    return {
        "predictor": {
            "model_type": "decision_tree",   # faster for unit tests
            "retrain_interval_frames": 20,
            "min_samples_to_train": 10,
            "n_estimators": 10,
            "max_depth": 3,
        }
    }


@pytest.fixture
def sample_count() -> VehicleCount:
    """A typical vehicle count snapshot."""
    return VehicleCount(total_vehicles=25, cars=15, buses=3, trucks=4, motorcycles=3)


@pytest.fixture
def sample_metrics() -> TrafficMetrics:
    """A typical traffic metrics snapshot."""
    return TrafficMetrics(
        density_percentage=45.0,
        congestion_level=CongestionLevel.MEDIUM,
        queue_length_estimate=10,
        avg_vehicle_count=22.0,
    )


def generate_training_data(
    predictor: CongestionPredictor,
    count: VehicleCount,
    metrics: TrafficMetrics,
    n: int = 15,
) -> None:
    """Helper: push ``n`` samples into the predictor's accumulator."""
    for _ in range(n):
        features = predictor.build_features(count, metrics)
        predictor.accumulate(features, CongestionLevel.MEDIUM)


# ---------------------------------------------------------------------------
# PredictionResult tests
# ---------------------------------------------------------------------------

class TestPredictionResult:
    """Tests for the ``PredictionResult`` dataclass."""

    def test_defaults(self) -> None:
        """PredictionResult should have safe default values."""
        # TODO: pr = PredictionResult()
        # TODO: assert pr.predicted_congestion_level == CongestionLevel.LOW
        # TODO: assert pr.confidence == 0.0
        raise NotImplementedError("TODO: implement test_defaults")

    def test_to_dict_keys(self) -> None:
        """to_dict() must include all API contract keys."""
        # TODO: d = PredictionResult().to_dict()
        # TODO: assert {"predicted_congestion_level","confidence","model_type"} <= d.keys()
        raise NotImplementedError("TODO: implement test_to_dict_keys")

    def test_level_serialised_as_string(self) -> None:
        """to_dict() predicted_congestion_level must be a plain string."""
        # TODO: pr = PredictionResult(predicted_congestion_level=CongestionLevel.HIGH)
        # TODO: assert pr.to_dict()["predicted_congestion_level"] == "high"
        raise NotImplementedError("TODO: implement test_level_serialised_as_string")


# ---------------------------------------------------------------------------
# CongestionPredictor tests
# ---------------------------------------------------------------------------

class TestCongestionPredictor:
    """Tests for ``CongestionPredictor``."""

    def test_instantiation(self, predictor_config: dict) -> None:
        """CongestionPredictor should instantiate without raising."""
        # TODO: cp = CongestionPredictor(predictor_config); assert cp is not None
        raise NotImplementedError("TODO: implement test_instantiation")

    def test_not_ready_before_training(self, predictor_config: dict) -> None:
        """is_ready() must return False before any training."""
        # TODO: cp = CongestionPredictor(predictor_config)
        # TODO: assert cp.is_ready() is False
        raise NotImplementedError("TODO: implement test_not_ready_before_training")

    def test_build_features_shape(
        self, predictor_config: dict, sample_count: VehicleCount, sample_metrics: TrafficMetrics
    ) -> None:
        """build_features() should return a 1-D array of shape (8,)."""
        # TODO: cp = CongestionPredictor(predictor_config)
        # TODO: features = cp.build_features(sample_count, sample_metrics)
        # TODO: assert features.shape == (8,)
        raise NotImplementedError("TODO: implement test_build_features_shape")

    def test_build_features_dtype(
        self, predictor_config: dict, sample_count: VehicleCount, sample_metrics: TrafficMetrics
    ) -> None:
        """build_features() should return a float32 array."""
        # TODO: assert features.dtype == np.float32
        raise NotImplementedError("TODO: implement test_build_features_dtype")

    def test_train_sets_ready(
        self, predictor_config: dict, sample_count: VehicleCount, sample_metrics: TrafficMetrics
    ) -> None:
        """After train() with enough samples, is_ready() must return True."""
        # TODO: cp = CongestionPredictor(predictor_config)
        # TODO: generate_training_data(cp, sample_count, sample_metrics, n=15)
        # TODO: cp.train(); assert cp.is_ready() is True
        raise NotImplementedError("TODO: implement test_train_sets_ready")

    def test_predict_before_training_returns_default(
        self, predictor_config: dict, sample_count: VehicleCount, sample_metrics: TrafficMetrics
    ) -> None:
        """predict() should return a safe default PredictionResult before training."""
        # TODO: cp = CongestionPredictor(predictor_config)
        # TODO: features = cp.build_features(sample_count, sample_metrics)
        # TODO: result = cp.predict(features); assert isinstance(result, PredictionResult)
        raise NotImplementedError("TODO: implement test_predict_before_training_returns_default")

    def test_predict_after_training_returns_valid_level(
        self, predictor_config: dict, sample_count: VehicleCount, sample_metrics: TrafficMetrics
    ) -> None:
        """After training, predict() must return a valid CongestionLevel."""
        # TODO: generate_training_data(cp, sample_count, sample_metrics)
        # TODO: cp.train(); features = cp.build_features(sample_count, sample_metrics)
        # TODO: result = cp.predict(features)
        # TODO: assert result.predicted_congestion_level in list(CongestionLevel)
        raise NotImplementedError("TODO: implement test_predict_after_training_returns_valid_level")

    def test_accumulate_triggers_retrain(
        self, predictor_config: dict, sample_count: VehicleCount, sample_metrics: TrafficMetrics
    ) -> None:
        """accumulate() should auto-retrain after retrain_interval samples."""
        # TODO: config retrain_interval = 20, min_samples = 10
        # TODO: Push 20 samples; assert cp.is_ready() is True (auto-retrain fired)
        raise NotImplementedError("TODO: implement test_accumulate_triggers_retrain")
