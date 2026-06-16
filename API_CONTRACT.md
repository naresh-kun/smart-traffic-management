# API Contract – Smart Traffic Management System

> **Version**: 1.0.0  
> **Status**: Draft  
> **Last Updated**: 2026-06-17

This document defines the public interfaces (class contracts) for every module.  
All inter-module communication must respect these contracts.  
Changes to any method signature require updating this document.

---

## Data Structures

### `DetectedVehicle`

```python
{
    "vehicle_type": str,       # "car" | "bus" | "truck" | "motorcycle"
    "confidence": float,       # 0.0 – 1.0
    "position": {
        "x1": int,
        "y1": int,
        "x2": int,
        "y2": int
    },
    "frame_id": int,
    "timestamp": float         # Unix epoch seconds
}
```

### `VehicleCount`

```python
{
    "total_vehicles": int,
    "cars": int,
    "buses": int,
    "trucks": int,
    "motorcycles": int,
    "lane_counts": dict        # {"lane_1": int, "lane_2": int, ...}
}
```

### `TrafficMetrics`

```python
{
    "density_percentage": float,   # 0.0 – 100.0
    "congestion_level": str,       # "low" | "medium" | "high" | "critical"
    "queue_length_estimate": int,  # estimated vehicles in queue
    "avg_vehicle_count": float,
    "timestamp": float
}
```

### `SignalTimings`

```python
{
    "green_duration": int,    # seconds
    "yellow_duration": int,   # seconds
    "red_duration": int,      # seconds
    "current_phase": str,     # "green" | "yellow" | "red"
    "time_remaining": int     # seconds until phase change
}
```

### `PredictionResult`

```python
{
    "predicted_congestion_level": str,   # "low" | "medium" | "high" | "critical"
    "confidence": float,
    "model_type": str
}
```

---

## Module Contracts

### `VehicleDetector` — `modules/vehicle_detector.py`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `config: dict` | — | Initialises model and video source |
| `load_model` | — | `bool` | Loads YOLOv8 weights; returns success flag |
| `open_source` | `source: str \| int` | `bool` | Opens webcam or video file |
| `detect_frame` | `frame: np.ndarray` | `list[DetectedVehicle]` | Runs inference on a single frame |
| `annotate_frame` | `frame: np.ndarray`, `detections: list` | `np.ndarray` | Draws bounding boxes on frame |
| `read_frame` | — | `tuple[bool, np.ndarray]` | Reads next frame from source |
| `release` | — | `None` | Releases video capture resource |

---

### `VehicleCounter` — `modules/vehicle_counter.py`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `config: dict` | — | Initialises counters |
| `update` | `detections: list[DetectedVehicle]` | `VehicleCount` | Updates count from new detections |
| `get_counts` | — | `VehicleCount` | Returns current count snapshot |
| `get_lane_counts` | — | `dict` | Returns per-lane vehicle counts |
| `reset` | — | `None` | Resets all counters to zero |

---

### `TrafficAnalyzer` — `modules/traffic_analyzer.py`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `config: dict` | — | Initialises analysis parameters |
| `calculate_density` | `count: VehicleCount` | `float` | Returns density as a percentage |
| `classify_congestion` | `density: float` | `str` | Maps density to congestion level |
| `estimate_queue_length` | `count: VehicleCount` | `int` | Estimates vehicles queued |
| `generate_metrics` | `count: VehicleCount` | `TrafficMetrics` | Produces full metrics snapshot |

---

### `SignalController` — `modules/signal_controller.py`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `config: dict` | — | Initialises signal parameters |
| `calculate_timings` | `metrics: TrafficMetrics` | `SignalTimings` | Computes green/yellow/red durations |
| `get_current_phase` | — | `str` | Returns current signal phase |
| `tick` | `elapsed_seconds: float` | `SignalTimings` | Advances signal state by elapsed time |
| `set_strategy` | `strategy: BaseSignalStrategy` | `None` | Swaps timing strategy (extension point) |

---

### `CongestionPredictor` — `modules/congestion_predictor.py`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `config: dict` | — | Initialises ML model |
| `train` | `X: np.ndarray`, `y: np.ndarray` | `None` | Trains the predictor |
| `predict` | `features: np.ndarray` | `PredictionResult` | Predicts next congestion level |
| `build_features` | `count: VehicleCount`, `metrics: TrafficMetrics`, `prev_count: VehicleCount` | `np.ndarray` | Builds feature vector |
| `is_ready` | — | `bool` | Returns True when model is trained |

---

### `DashboardData` — `modules/dashboard_data.py`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | — | — | Creates thread-safe data store |
| `update` | `count: VehicleCount`, `metrics: TrafficMetrics`, `signal: SignalTimings`, `prediction: PredictionResult` | `None` | Stores latest snapshot |
| `get_snapshot` | — | `dict` | Returns latest system state |
| `get_history` | `minutes: int` | `list[dict]` | Returns historical records |
| `append_history` | `record: dict` | `None` | Appends a time-stamped record |

---

## Extension Points

### `BaseSignalStrategy` — Abstract base for signal timing strategies

Future RL or rule-based strategies must implement:
```python
def calculate_timings(self, metrics: TrafficMetrics) -> SignalTimings: ...
```

### `BaseSensorAdapter` — Abstract base for sensor/IoT data ingestion

Future IoT adapters must implement:
```python
def read_detections(self) -> list[DetectedVehicle]: ...
```

---

*Changes to this document must be reviewed and committed alongside the corresponding code change.*
