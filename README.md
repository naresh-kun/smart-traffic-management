# Smart Traffic Management System

> **A Python-based prototype for AI-assisted urban traffic management using computer vision and dynamic signal control.**

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Prerequisites](#prerequisites)
5. [Installation](#installation)
6. [Configuration](#configuration)
7. [Running the Application](#running-the-application)
8. [Running the Dashboard](#running-the-dashboard)
9. [Running Tests](#running-tests)
10. [Module Reference](#module-reference)
11. [Data Flow](#data-flow)
12. [Future Expansion](#future-expansion)
13. [Troubleshooting](#troubleshooting)

---

## Project Overview

The Smart Traffic Management System detects vehicles from a live webcam or recorded video, counts them per lane, analyses traffic density, and dynamically adjusts traffic signal timings to reduce urban congestion.

It is designed as a college-level AI prototype that runs fully on a standard laptop (8 GB RAM, Windows/Linux/macOS) without requiring paid services, custom GPU training, or IoT hardware.

---

## Features

| Feature | Status |
|---|---|
| Real-time vehicle detection (YOLOv8) | ✅ |
| Multi-class vehicle counting | ✅ |
| Traffic density & congestion analysis | ✅ |
| Dynamic signal timing adjustment | ✅ |
| Congestion prediction (Random Forest / Decision Tree) | ✅ |
| Streamlit monitoring dashboard | ✅ |
| SQLite data logging | ✅ |
| Webcam & video file support | ✅ |
| Fully configurable via YAML | ✅ |

---

## Architecture

```
smart_traffic_management/
├── main.py                         # Application entry point
├── config/
│   └── config.yaml                 # Central configuration
├── data/
│   ├── videos/                     # Input video files
│   ├── logs/                       # Log files & SQLite DB
│   └── results/                    # Output frames / reports
├── models/
│   └── yolov8/                     # Pretrained YOLO weights
├── modules/
│   ├── vehicle_detector.py         # Video input + YOLO detection
│   ├── vehicle_counter.py          # Counting & statistics
│   ├── traffic_analyzer.py         # Density & congestion analysis
│   ├── signal_controller.py        # Signal timing logic
│   ├── congestion_predictor.py     # ML-based prediction
│   └── dashboard_data.py           # Data bridge to dashboard
├── dashboard/
│   └── streamlit_dashboard.py      # Streamlit UI
├── utils/
│   ├── logger.py                   # Centralised logging
│   ├── constants.py                # System-wide constants
│   └── helpers.py                  # Shared utility functions
└── tests/
    ├── test_vehicle_detector.py
    ├── test_vehicle_counter.py
    ├── test_traffic_analyzer.py
    ├── test_signal_controller.py
    └── test_congestion_predictor.py
```

---

## Prerequisites

- Python 3.10 or higher
- pip
- Webcam (optional – video file can be used instead)
- ~2 GB free disk space (YOLOv8 weights download)

---

## Installation

```bash
# 1. Clone the repository
git clone <repo-url>
cd smart_traffic_management

# 2. Create a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS

# 3. Install dependencies
pip install -r requirements.txt
```

YOLOv8 weights (`yolov8n.pt`) are downloaded automatically on first run via the `ultralytics` library.

---

## Configuration

All tunable parameters live in `config/config.yaml`.

| Parameter | Description |
|---|---|
| `video.source` | `0` for webcam or path to a `.mp4` file |
| `detection.confidence_threshold` | Minimum YOLO confidence (0–1) |
| `signal.timing_map` | Green duration per congestion level |
| `database.path` | SQLite database location |
| `dashboard.refresh_interval_seconds` | Dashboard polling rate |

---

## Running the Application

```bash
# Run with webcam (default)
python main.py

# Run with a video file
python main.py --source data/videos/traffic.mp4

# Run headless (no video window)
python main.py --headless
```

---

## Running the Dashboard

```bash
streamlit run dashboard/streamlit_dashboard.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Running Tests

```bash
python -m pytest tests/ -v
```

---

## Module Reference

| Module | Class | Responsibility |
|---|---|---|
| `vehicle_detector.py` | `VehicleDetector` | Video capture + YOLOv8 inference |
| `vehicle_counter.py` | `VehicleCounter` | Counting by type and lane |
| `traffic_analyzer.py` | `TrafficAnalyzer` | Density & congestion scoring |
| `signal_controller.py` | `SignalController` | Signal state & timing decisions |
| `congestion_predictor.py` | `CongestionPredictor` | ML-based congestion forecast |
| `dashboard_data.py` | `DashboardData` | Thread-safe data bridge to UI |

---

## Data Flow

```
Video Source
    ↓
VehicleDetector   →  raw detections (type, confidence, bbox)
    ↓
VehicleCounter    →  counts per type / lane
    ↓
TrafficAnalyzer   →  density %, congestion level, queue length
    ↓
CongestionPredictor → predicted next congestion level
    ↓
SignalController  →  green / yellow / red durations
    ↓
DashboardData     →  shared state consumed by Streamlit
```

---

## Future Expansion

The architecture provides the following extension points:

- **IoT sensors**: Replace or supplement `VehicleDetector` with sensor adapters.
- **Multi-intersection**: Wrap the pipeline in an intersection manager class.
- **Reinforcement learning**: Swap `SignalController.calculate_timings()` with an RL agent.
- **Cloud deployment**: `DashboardData` can be backed by Redis or a cloud database.
- **Hardware controllers**: Add a `HardwareSignalAdapter` that implements the same interface as `SignalController`.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| Webcam not detected | Set `video.source` to a valid device index or video path |
| Low FPS | Use `yolov8n.pt` (nano) and lower frame resolution |
| YOLO weights not found | Delete `models/yolov8/` and restart – auto-downloaded |
| Dashboard shows no data | Ensure `main.py` is running before opening the dashboard |

---

*Built with Python · OpenCV · YOLOv8 · Streamlit · SQLite*

Current Status

Completed:
- Configuration system
- Utility layer
- Vehicle Detector
- YOLO integration

In Progress:
- Vehicle Counter
- Traffic Analysis
- Signal Control
- Dashboard