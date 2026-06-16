"""
dashboard/streamlit_dashboard.py
----------------------------------
Streamlit monitoring dashboard for the Smart Traffic Management System.

Responsibility
--------------
* Visualise live and historical traffic data.
* Display vehicle counts, density, congestion level, and signal status.
* Render charts and statistics for project demonstrations.

Rules (per ARCHITECTURE_RULES.md)
----------------------------------
* This file must NOT calculate density, congestion, or signal timings.
* This file must NOT contain ML training logic.
* All data is consumed via ``DashboardData`` (or a shared JSON/SQLite store).
* Business logic belongs in the ``modules/`` package.

Run with
--------
    streamlit run dashboard/streamlit_dashboard.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Ensure project root is on the path when run via streamlit CLI
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from utils.helpers import load_config
from utils.constants import CongestionLevel, SignalPhase, CONGESTION_COLORS_RGB


# ---------------------------------------------------------------------------
# Page configuration (must be first Streamlit call)
# ---------------------------------------------------------------------------

def configure_page() -> None:
    """Set Streamlit page metadata and layout.

    Must be called before any other ``st.*`` function.
    """
    # TODO: st.set_page_config(title, layout="wide", page_icon, initial_sidebar_state)
    raise NotImplementedError("TODO: implement configure_page()")


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_dashboard_data() -> dict:
    """Load the latest traffic snapshot from the shared data source.

    Returns
    -------
    dict
        Latest system snapshot, or an empty dict if no data is available.

    Notes
    -----
    The dashboard reads from a shared SQLite database or in-process shared
    object depending on deployment mode. For decoupled Streamlit usage the
    SQLite path from config is queried directly.
    """
    # TODO: Load config; connect to SQLite; query latest traffic_log row.
    # TODO: Return as dict; return {} on failure.
    raise NotImplementedError("TODO: implement load_dashboard_data()")


def load_history(minutes: int = 30) -> list[dict]:
    """Load historical traffic records for trend charts.

    Parameters
    ----------
    minutes : int
        Number of minutes of history to retrieve.

    Returns
    -------
    list[dict]
        Ordered list of snapshot dictionaries.
    """
    # TODO: Connect to SQLite; call equivalent of query_recent_logs(minutes).
    raise NotImplementedError("TODO: implement load_history()")


# ---------------------------------------------------------------------------
# UI component renderers
# ---------------------------------------------------------------------------

def render_header(config: dict) -> None:
    """Render the dashboard title and subtitle.

    Parameters
    ----------
    config : dict
        Application configuration (for page title from ``dashboard.page_title``).
    """
    # TODO: st.title(config["dashboard"]["page_title"])
    # TODO: st.markdown("Real-time traffic monitoring powered by YOLOv8 + Streamlit")
    raise NotImplementedError("TODO: implement render_header()")


def render_live_metrics(snapshot: dict) -> None:
    """Render the top KPI metric row with live values.

    Displays:
    - Total vehicles detected
    - Traffic density (%)
    - Congestion level badge
    - Current signal phase

    Parameters
    ----------
    snapshot : dict
        Latest system snapshot from ``load_dashboard_data()``.
    """
    # TODO: col1, col2, col3, col4 = st.columns(4)
    # TODO: col1.metric("Vehicles", snapshot.get("total_vehicles", 0))
    # TODO: col2.metric("Density", f'{snapshot.get("density_percentage", 0):.1f}%')
    # TODO: Render congestion level with colour via st.markdown / st.info / st.error.
    # TODO: Render signal phase with emoji indicator.
    raise NotImplementedError("TODO: implement render_live_metrics()")


def render_vehicle_breakdown(snapshot: dict) -> None:
    """Render a bar chart showing vehicle counts by type.

    Parameters
    ----------
    snapshot : dict
        Latest system snapshot.
    """
    # TODO: Extract cars, buses, trucks, motorcycles from snapshot.
    # TODO: Build Plotly bar chart and render with st.plotly_chart().
    raise NotImplementedError("TODO: implement render_vehicle_breakdown()")


def render_signal_status(snapshot: dict) -> None:
    """Render the current signal timing and phase with a visual indicator.

    Parameters
    ----------
    snapshot : dict
        Latest system snapshot with signal timing fields.
    """
    # TODO: Display green/yellow/red phase with colour-coded progress bar.
    # TODO: Show green_duration, yellow_duration, red_duration seconds.
    # TODO: Show time_remaining with st.progress().
    raise NotImplementedError("TODO: implement render_signal_status()")


def render_historical_charts(history: list[dict]) -> None:
    """Render line charts of vehicle count and density over time.

    Parameters
    ----------
    history : list[dict]
        Time-ordered list of traffic snapshots.
    """
    # TODO: Convert history to pandas DataFrame.
    # TODO: Plot "total_vehicles" over time with Plotly line chart.
    # TODO: Plot "density_percentage" over time with Plotly line chart.
    # TODO: Render both charts in two columns with st.plotly_chart().
    raise NotImplementedError("TODO: implement render_historical_charts()")


def render_congestion_gauge(snapshot: dict) -> None:
    """Render a gauge or indicator for the current congestion level.

    Parameters
    ----------
    snapshot : dict
        Latest system snapshot.
    """
    # TODO: Use plotly.graph_objects.Indicator or a custom gauge.
    # TODO: Colour the gauge using CONGESTION_COLORS_RGB.
    raise NotImplementedError("TODO: implement render_congestion_gauge()")


def render_prediction_panel(snapshot: dict) -> None:
    """Display the ML-predicted next congestion level.

    Parameters
    ----------
    snapshot : dict
        Latest system snapshot including ``predicted_level`` and
        ``prediction_confidence`` fields.
    """
    # TODO: Show predicted_level with confidence percentage.
    # TODO: Add a note that the model trains live during the session.
    raise NotImplementedError("TODO: implement render_prediction_panel()")


def render_statistics_summary(history: list[dict]) -> None:
    """Display summary statistics derived from the session history.

    Statistics
    ----------
    - Average vehicle count
    - Peak vehicle count
    - Most common congestion level
    - Total signal cycles

    Parameters
    ----------
    history : list[dict]
        Time-ordered list of traffic snapshots.
    """
    # TODO: Compute stats from history using pandas.
    # TODO: Display in an expander or a four-column metric row.
    raise NotImplementedError("TODO: implement render_statistics_summary()")


def render_sidebar(config: dict) -> dict:
    """Render the sidebar with user controls and configuration display.

    Parameters
    ----------
    config : dict
        Application configuration.

    Returns
    -------
    dict
        User selections from sidebar widgets (e.g. history_minutes).
    """
    # TODO: st.sidebar.header("Settings")
    # TODO: history_minutes slider (5–120 minutes).
    # TODO: Show current config values (source, model, thresholds) as info text.
    # TODO: Return dict of user selections.
    raise NotImplementedError("TODO: implement render_sidebar()")


# ---------------------------------------------------------------------------
# Main dashboard loop
# ---------------------------------------------------------------------------

def main() -> None:
    """Streamlit application entry point.

    Orchestrates page configuration, data loading, and component rendering.
    Auto-refreshes at the configured interval.
    """
    configure_page()
    config = load_config("config/config.yaml")

    refresh_interval: int = config.get("dashboard", {}).get(
        "refresh_interval_seconds", 2
    )

    user_settings = render_sidebar(config)
    render_header(config)

    snapshot = load_dashboard_data()
    history = load_history(minutes=user_settings.get("history_minutes", 30))

    # --- Live metrics row ---
    render_live_metrics(snapshot)

    # --- Signal and congestion gauges ---
    col_signal, col_gauge, col_pred = st.columns(3)
    with col_signal:
        render_signal_status(snapshot)
    with col_gauge:
        render_congestion_gauge(snapshot)
    with col_pred:
        render_prediction_panel(snapshot)

    # --- Vehicle breakdown chart ---
    render_vehicle_breakdown(snapshot)

    # --- Historical trend charts ---
    render_historical_charts(history)

    # --- Statistics summary ---
    render_statistics_summary(history)

    # Auto-refresh
    # TODO: time.sleep(refresh_interval); st.rerun()
    raise NotImplementedError("TODO: implement auto-refresh in main()")


if __name__ == "__main__":
    main()
