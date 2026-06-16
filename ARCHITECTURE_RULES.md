# Architecture Rules

## Purpose

This document defines the architectural rules for the Smart Traffic Management System.

All developers and AI agents must follow these rules unless explicitly instructed otherwise.

The goal is to ensure consistency, maintainability, scalability, and easy collaboration.

---

# General Principles

1. Use Python only.
2. Prioritize readability over clever implementations.
3. Keep the project modular.
4. Follow the Single Responsibility Principle.
5. Avoid tightly coupled components.
6. Design for future expansion.
7. Business logic must be independent from UI logic.
8. Avoid duplicate code.
9. All functionality must be configurable where appropriate.
10. The application must run on a standard laptop without requiring specialized hardware.

---

# Project Structure

The project structure must remain:

smart_traffic_management/

├── main.py

├── config/

├── data/

├── models/

├── modules/

├── dashboard/

├── utils/

├── tests/

└── requirements.txt

New directories should only be added when absolutely necessary.

---

# Module Responsibilities

## vehicle_detector.py

Responsible only for:

* Video input handling
* Vehicle detection
* Vehicle classification
* Bounding box generation

Must NOT:

* Calculate traffic density
* Calculate signal timings
* Update dashboards
* Access databases directly

---

## vehicle_counter.py

Responsible only for:

* Counting detected vehicles
* Vehicle type statistics
* Lane-wise counting

Must NOT:

* Perform object detection
* Calculate congestion
* Control traffic signals

---

## traffic_analyzer.py

Responsible only for:

* Density calculation
* Congestion analysis
* Queue length estimation
* Traffic metrics generation

Must NOT:

* Perform vehicle detection
* Render dashboards
* Control traffic signals directly

---

## signal_controller.py

Responsible only for:

* Signal timing calculations
* Signal state management
* Traffic optimization decisions

Must NOT:

* Detect vehicles
* Render dashboards
* Access video feeds

---

## congestion_predictor.py

Responsible only for:

* Congestion forecasting
* Machine learning predictions

Must NOT:

* Perform detection
* Control signals directly
* Access dashboard UI

---

## dashboard/

Responsible only for:

* Data visualization
* User interaction
* Monitoring views

Must NOT:

* Contain business logic
* Contain traffic analysis calculations
* Contain ML training logic

---

# Data Flow Rules

The application must follow this flow:

Video Source
↓
Vehicle Detector
↓
Vehicle Counter
↓
Traffic Analyzer
↓
Congestion Predictor
↓
Signal Controller
↓
Dashboard

Modules should not bypass this flow unless justified.

---

# Naming Conventions

Use snake_case for:

* Variables
* Functions
* File names

Examples:

vehicle_count

traffic_density

signal_duration

Avoid camelCase.

---

# Class Naming

Use PascalCase.

Examples:

VehicleDetector

TrafficAnalyzer

SignalController

CongestionPredictor

---

# Database Rules

Use SQLite.

All database interactions must be isolated.

Future migration to PostgreSQL should require minimal code changes.

Do not hardcode SQL queries throughout the project.

Use a dedicated database access layer if database complexity grows.

---

# Configuration Rules

All configurable values must be stored in:

config/config.yaml

Examples:

* Detection confidence threshold
* Signal timing values
* Dashboard refresh rate
* Video source settings

Avoid hardcoded constants.

---

# Machine Learning Rules

Use pretrained models whenever possible.

Preferred object detection:

* YOLOv8 pretrained weights

Do not train custom object detection models unless explicitly required.

Keep machine learning lightweight.

Use:

* Scikit-learn
* Random Forest
* Decision Tree

for congestion prediction.

---

# Logging Rules

All major events must be logged.

Examples:

* Vehicle counts
* Density calculations
* Signal changes
* Prediction outputs
* Errors

Use centralized logging utilities.

---

# Testing Rules

Every major module should have corresponding tests.

Tests should remain independent from the dashboard.

Business logic must be testable without launching the UI.

---

# Dashboard Rules

Dashboard must consume processed data only.

Dashboard must never calculate:

* Density
* Congestion
* Signal timings

Dashboard is a visualization layer only.

---

# Future Expansion Requirements

The architecture must support future integration of:

* IoT sensors
* Multiple intersections
* Cloud deployment
* Reinforcement learning
* Hardware traffic controllers

Current implementation should provide extension points but should not implement these features.

---

# AI Agent Instructions

Before modifying any code:

1. Read PROJECT_SPEC.md
2. Read ARCHITECTURE_RULES.md
3. Preserve existing architecture
4. Avoid unnecessary refactoring
5. Do not rename modules without strong justification
6. Do not change API contracts without updating documentation

Maintain consistency over novelty.

The architecture is the source of truth.
