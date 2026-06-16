"""
modules/congestion_predictor.py
---------------------------------
Responsibility
--------------
* Build feature vectors from vehicle counts and traffic metrics.
* Train a lightweight scikit-learn model (Random Forest or Decision Tree).
* Predict the next congestion level from current features.
* Accumulate training data incrementally and retrain periodically.

This module must NOT:
* Perform vehicle detection.
* Control signal timings directly.
* Access the dashboard UI.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from utils.logger import get_logger
from utils.constants import CongestionLevel
from modules.vehicle_counter import VehicleCount
from modules.traffic_analyzer import TrafficMetrics

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Data structure
# ---------------------------------------------------------------------------

@dataclass
class PredictionResult:
    """Result of a single congestion prediction.

    Attributes
    ----------
    predicted_congestion_level : CongestionLevel
        The model's predicted next congestion state.
    confidence : float
        Probability of the predicted class (where available).
    model_type : str
        Name of the model used (``"random_forest"`` or ``"decision_tree"``).
    """

    predicted_congestion_level: CongestionLevel = CongestionLevel.LOW
    confidence: float = 0.0
    model_type: str = "unknown"

    def to_dict(self) -> dict:
        """Serialise to a plain dictionary.

        Returns
        -------
        dict
            JSON-serialisable representation matching the API contract.
        """
        # TODO: Return all fields as dict; convert CongestionLevel to str.
        raise NotImplementedError("TODO: implement to_dict()")


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------

class CongestionPredictor:
    """Lightweight ML-based congestion forecasting.

    Uses a scikit-learn Random Forest (default) or Decision Tree trained
    incrementally on live data captured during the current session.

    The model is intentionally simple – the goal is to demonstrate ML
    integration, not to achieve high absolute accuracy on small datasets.

    Parameters
    ----------
    config : dict
        The ``predictor`` section of ``config.yaml``.
    """

    def __init__(self, config: dict) -> None:
        predictor_cfg = config.get("predictor", {})
        self._model_type: str = predictor_cfg.get("model_type", "random_forest")
        self._retrain_interval: int = predictor_cfg.get("retrain_interval_frames", 500)
        self._min_samples: int = predictor_cfg.get("min_samples_to_train", 50)
        self._n_estimators: int = predictor_cfg.get("n_estimators", 50)
        self._max_depth: Optional[int] = predictor_cfg.get("max_depth", 5)

        self._model = None          # scikit-learn estimator
        self._X_train: list[list[float]] = []
        self._y_train: list[str] = []
        self._frame_counter: int = 0
        self._is_trained: bool = False

        logger.info(
            f"CongestionPredictor initialised (model_type={self._model_type})."
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build_features(
        self,
        count: VehicleCount,
        metrics: TrafficMetrics,
        prev_count: Optional[VehicleCount] = None,
    ) -> np.ndarray:
        """Construct the feature vector for model input.

        Feature set
        -----------
        0: total_vehicles
        1: cars
        2: buses
        3: trucks
        4: motorcycles
        5: density_percentage
        6: queue_length_estimate
        7: delta_total (current - previous total, 0 if no prev_count)

        Parameters
        ----------
        count : VehicleCount
            Current frame count.
        metrics : TrafficMetrics
            Current traffic metrics.
        prev_count : Optional[VehicleCount]
            Previous frame count for computing delta. May be ``None``.

        Returns
        -------
        np.ndarray
            1-D feature array of shape ``(8,)``.
        """
        # TODO: Extract features from count and metrics.
        # TODO: Compute delta_total = count.total_vehicles - prev_count.total_vehicles (or 0).
        # TODO: Return np.array([...], dtype=np.float32).
        raise NotImplementedError("TODO: implement build_features()")

    def accumulate(
        self,
        features: np.ndarray,
        label: CongestionLevel,
    ) -> None:
        """Store a labelled sample for future training.

        Parameters
        ----------
        features : np.ndarray
            Feature vector from ``build_features()``.
        label : CongestionLevel
            Ground-truth congestion level for this sample.
        """
        # TODO: Append features.tolist() to self._X_train.
        # TODO: Append label.value to self._y_train.
        # TODO: Increment self._frame_counter.
        # TODO: If frame_counter % retrain_interval == 0 and samples >= min, call train().
        raise NotImplementedError("TODO: implement accumulate()")

    def train(
        self,
        X: Optional[np.ndarray] = None,
        y: Optional[np.ndarray] = None,
    ) -> None:
        """Fit the classifier on accumulated (or provided) training data.

        Parameters
        ----------
        X : Optional[np.ndarray]
            Feature matrix. When ``None``, uses ``self._X_train``.
        y : Optional[np.ndarray]
            Label array. When ``None``, uses ``self._y_train``.
        """
        # TODO: Use provided X, y or fall back to self._X_train / self._y_train.
        # TODO: Instantiate the model via self._build_model().
        # TODO: Fit model on X, y.
        # TODO: Set self._is_trained = True; log sample count and model type.
        raise NotImplementedError("TODO: implement train()")

    def predict(self, features: np.ndarray) -> PredictionResult:
        """Predict the next congestion level from a feature vector.

        Parameters
        ----------
        features : np.ndarray
            1-D feature array from ``build_features()``.

        Returns
        -------
        PredictionResult
            Prediction with congestion level and confidence.
        """
        # TODO: If not self._is_trained, return a default PredictionResult.
        # TODO: predicted_label = self._model.predict(features.reshape(1, -1))[0]
        # TODO: confidence = max(self._model.predict_proba(...))[0] if RF.
        # TODO: Return PredictionResult with parsed CongestionLevel.
        raise NotImplementedError("TODO: implement predict()")

    def is_ready(self) -> bool:
        """Return ``True`` when the model has been trained at least once.

        Returns
        -------
        bool
            Training status.
        """
        return self._is_trained

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_model(self):
        """Instantiate the scikit-learn estimator from config.

        Returns
        -------
        sklearn estimator
            A ``RandomForestClassifier`` or ``DecisionTreeClassifier``
            depending on ``self._model_type``.
        """
        # TODO: from sklearn.ensemble import RandomForestClassifier
        # TODO: from sklearn.tree import DecisionTreeClassifier
        # TODO: Build and return the appropriate model.
        raise NotImplementedError("TODO: implement _build_model()")
