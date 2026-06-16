"""
modules/dashboard_data.py
--------------------------
Responsibility
--------------
* Provide a thread-safe bridge between the main processing loop and the
  Streamlit dashboard process.
* Store the latest system snapshot (counts, metrics, signal, prediction).
* Maintain a time-windowed history for chart rendering.
* Persist snapshots to SQLite via the data access layer.

This module must NOT:
* Contain traffic analysis calculations.
* Contain ML training logic.
* Render any UI components.
"""

from __future__ import annotations

import sqlite3
import threading
import time
from collections import deque
from pathlib import Path
from typing import Deque, Optional

from utils.logger import get_logger
from utils.helpers import utc_now_iso, generate_session_id, ensure_dir
from modules.vehicle_counter import VehicleCount
from modules.traffic_analyzer import TrafficMetrics
from modules.signal_controller import SignalTimings
from modules.congestion_predictor import PredictionResult

logger = get_logger(__name__)

# Maximum number of historical records kept in memory for the dashboard
_MAX_HISTORY_RECORDS = 1000


# ---------------------------------------------------------------------------
# Data access layer
# ---------------------------------------------------------------------------

class TrafficDatabase:
    """Isolated SQLite data access layer for traffic log persistence.

    All raw SQL is confined to this class. Future migration to PostgreSQL
    requires changes only here.

    Parameters
    ----------
    db_path : str
        File path to the SQLite database (created if absent).
    session_id : str
        UUID string identifying the current application session.
    """

    def __init__(self, db_path: str, session_id: str) -> None:
        self._db_path = db_path
        self._session_id = session_id
        self._conn: Optional[sqlite3.Connection] = None
        logger.info(f"TrafficDatabase target: {db_path}")

    def connect(self) -> None:
        """Open the SQLite connection and initialise the schema.

        Creates tables if they do not already exist.
        """
        # TODO: ensure_dir(Path(self._db_path).parent)
        # TODO: self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        # TODO: Call self._create_schema()
        raise NotImplementedError("TODO: implement connect()")

    def _create_schema(self) -> None:
        """Execute CREATE TABLE IF NOT EXISTS statements from DATABASE_SCHEMA.md."""
        # TODO: Execute SQL for traffic_log, sessions, signal_events tables.
        # TODO: Execute index creation statements.
        # TODO: conn.commit()
        raise NotImplementedError("TODO: implement _create_schema()")

    def insert_session(self, source: str) -> None:
        """Write a new session record to the ``sessions`` table.

        Parameters
        ----------
        source : str
            Video source description (``"webcam"`` or filename).
        """
        # TODO: INSERT INTO sessions (id, started_at, source) VALUES (...)
        raise NotImplementedError("TODO: implement insert_session()")

    def close_session(self) -> None:
        """Mark the current session as ended in the ``sessions`` table."""
        # TODO: UPDATE sessions SET ended_at = utc_now_iso() WHERE id = self._session_id
        raise NotImplementedError("TODO: implement close_session()")

    def insert_traffic_log(self, record: dict) -> None:
        """Persist one traffic snapshot to the ``traffic_log`` table.

        Parameters
        ----------
        record : dict
            Flat dictionary matching the ``traffic_log`` column schema.
        """
        # TODO: INSERT INTO traffic_log (...) VALUES (...)
        raise NotImplementedError("TODO: implement insert_traffic_log()")

    def insert_signal_event(self, phase: str, duration: int, level: str, density: float) -> None:
        """Record a signal phase change in the ``signal_events`` table.

        Parameters
        ----------
        phase : str
            New signal phase name.
        duration : int
            Duration of the new phase in seconds.
        level : str
            Congestion level that triggered the change.
        density : float
            Density percentage at the time of change.
        """
        # TODO: INSERT INTO signal_events (...) VALUES (...)
        raise NotImplementedError("TODO: implement insert_signal_event()")

    def query_recent_logs(self, minutes: int) -> list[dict]:
        """Retrieve traffic_log records from the last ``minutes`` minutes.

        Parameters
        ----------
        minutes : int
            Lookback window.

        Returns
        -------
        list[dict]
            List of row dictionaries ordered by timestamp ascending.
        """
        # TODO: SELECT * FROM traffic_log WHERE timestamp >= cutoff ORDER BY timestamp
        # TODO: Return list of dicts via cursor.fetchall() + column names.
        raise NotImplementedError("TODO: implement query_recent_logs()")

    def close(self) -> None:
        """Close the SQLite connection."""
        # TODO: if self._conn: self._conn.close()
        raise NotImplementedError("TODO: implement close()")


# ---------------------------------------------------------------------------
# Thread-safe dashboard bridge
# ---------------------------------------------------------------------------

class DashboardData:
    """Thread-safe shared data store consumed by the Streamlit dashboard.

    The main processing loop calls ``update()`` while Streamlit runs in a
    separate thread and calls ``get_snapshot()`` and ``get_history()``.
    A ``threading.Lock`` guards all shared state.

    Parameters
    ----------
    config : dict
        The ``database`` and ``dashboard`` sections of ``config.yaml``.
    """

    def __init__(self, config: dict) -> None:
        self._config = config
        self._lock = threading.Lock()
        self._session_id: str = generate_session_id()

        db_path: str = config.get("database", {}).get(
            "path", "data/logs/traffic_data.db"
        )
        self._db = TrafficDatabase(db_path, self._session_id)

        # Latest system snapshot
        self._snapshot: dict = {}

        # Rolling in-memory history
        self._history: Deque[dict] = deque(maxlen=_MAX_HISTORY_RECORDS)

        self._last_db_write: float = 0.0
        self._db_write_interval: float = config.get("database", {}).get(
            "log_interval_seconds", 5.0
        )

        logger.info(f"DashboardData initialised (session={self._session_id}).")

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self, source: str) -> None:
        """Open the database connection and create a session record.

        Parameters
        ----------
        source : str
            Description of the video source for session logging.
        """
        # TODO: self._db.connect()
        # TODO: self._db.insert_session(source)
        raise NotImplementedError("TODO: implement start()")

    def stop(self) -> None:
        """Close the session and release the database connection."""
        # TODO: self._db.close_session()
        # TODO: self._db.close()
        raise NotImplementedError("TODO: implement stop()")

    # ------------------------------------------------------------------
    # Write (called by main processing loop)
    # ------------------------------------------------------------------

    def update(
        self,
        count: VehicleCount,
        metrics: TrafficMetrics,
        signal: SignalTimings,
        prediction: Optional[PredictionResult] = None,
    ) -> None:
        """Store the latest pipeline snapshot and optionally persist to DB.

        Parameters
        ----------
        count : VehicleCount
            Current vehicle count.
        metrics : TrafficMetrics
            Current traffic metrics.
        signal : SignalTimings
            Current signal timings.
        prediction : Optional[PredictionResult]
            ML prediction, or ``None`` if the model isn't trained yet.
        """
        # TODO: Build flat record dict from all inputs.
        # TODO: Acquire self._lock; update self._snapshot; call self.append_history(record).
        # TODO: If elapsed since last db write >= interval, call self._db.insert_traffic_log(record).
        raise NotImplementedError("TODO: implement update()")

    def append_history(self, record: dict) -> None:
        """Append a time-stamped record to the in-memory history.

        Parameters
        ----------
        record : dict
            Flat snapshot dictionary.
        """
        # TODO: Acquire lock; self._history.append(record)
        raise NotImplementedError("TODO: implement append_history()")

    # ------------------------------------------------------------------
    # Read (called by Streamlit dashboard)
    # ------------------------------------------------------------------

    def get_snapshot(self) -> dict:
        """Return the most recent system state snapshot.

        Returns
        -------
        dict
            Copy of the latest snapshot dictionary.
        """
        # TODO: Acquire lock; return dict(self._snapshot)
        raise NotImplementedError("TODO: implement get_snapshot()")

    def get_history(self, minutes: int = 30) -> list[dict]:
        """Return historical records from the last ``minutes`` minutes.

        Queries the in-memory deque for speed; falls back to SQLite for
        longer lookback windows.

        Parameters
        ----------
        minutes : int
            Lookback window in minutes.

        Returns
        -------
        list[dict]
            Chronologically ordered list of snapshots.
        """
        # TODO: Acquire lock; filter self._history by timestamp cutoff.
        # TODO: If window exceeds in-memory range, query self._db.query_recent_logs(minutes).
        raise NotImplementedError("TODO: implement get_history()")

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def session_id(self) -> str:
        """Return the unique session identifier for this run."""
        return self._session_id
