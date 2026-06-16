# Database Schema – Smart Traffic Management System

> **Engine**: SQLite  
> **File**: `data/logs/traffic_data.db`  
> **Version**: 1.0.0

All database access must go through the data access layer.  
Direct SQL queries scattered across modules are forbidden (per `ARCHITECTURE_RULES.md`).

---

## Design Goals

- Simple enough to run embedded with SQLite.
- Schema must survive a future migration to PostgreSQL with minimal changes.
- Every table has a surrogate integer primary key.
- Timestamps are stored as ISO-8601 strings (UTC).

---

## Tables

### `traffic_log`

Stores a snapshot of system state captured at regular intervals.

```sql
CREATE TABLE IF NOT EXISTS traffic_log (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp           TEXT    NOT NULL,          -- ISO-8601 UTC
    total_vehicles      INTEGER NOT NULL DEFAULT 0,
    cars                INTEGER NOT NULL DEFAULT 0,
    buses               INTEGER NOT NULL DEFAULT 0,
    trucks              INTEGER NOT NULL DEFAULT 0,
    motorcycles         INTEGER NOT NULL DEFAULT 0,
    density_percentage  REAL    NOT NULL DEFAULT 0.0,
    congestion_level    TEXT    NOT NULL,           -- low|medium|high|critical
    queue_length        INTEGER NOT NULL DEFAULT 0,
    green_duration      INTEGER NOT NULL DEFAULT 0, -- seconds
    yellow_duration     INTEGER NOT NULL DEFAULT 0,
    red_duration        INTEGER NOT NULL DEFAULT 0,
    signal_phase        TEXT    NOT NULL,           -- green|yellow|red
    predicted_level     TEXT,                       -- ML prediction (nullable)
    session_id          TEXT    NOT NULL            -- groups records per run
);
```

**Indexes**:
```sql
CREATE INDEX IF NOT EXISTS idx_traffic_log_timestamp   ON traffic_log (timestamp);
CREATE INDEX IF NOT EXISTS idx_traffic_log_session     ON traffic_log (session_id);
CREATE INDEX IF NOT EXISTS idx_traffic_log_congestion  ON traffic_log (congestion_level);
```

---

### `sessions`

Tracks individual application run sessions for historical comparison.

```sql
CREATE TABLE IF NOT EXISTS sessions (
    id          TEXT    PRIMARY KEY,   -- UUID
    started_at  TEXT    NOT NULL,      -- ISO-8601 UTC
    ended_at    TEXT,                  -- NULL while running
    source      TEXT    NOT NULL,      -- "webcam" | video filename
    notes       TEXT                   -- optional user comment
);
```

---

### `signal_events`

Records every signal phase change for audit and analysis.

```sql
CREATE TABLE IF NOT EXISTS signal_events (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      TEXT    NOT NULL REFERENCES sessions(id),
    timestamp       TEXT    NOT NULL,
    phase           TEXT    NOT NULL,     -- green|yellow|red
    duration_sec    INTEGER NOT NULL,
    trigger_level   TEXT    NOT NULL,     -- congestion level that triggered change
    congestion_at_change REAL NOT NULL    -- density % at time of change
);
```

**Indexes**:
```sql
CREATE INDEX IF NOT EXISTS idx_signal_events_session ON signal_events (session_id);
CREATE INDEX IF NOT EXISTS idx_signal_events_ts      ON signal_events (timestamp);
```

---

## Column Constraints

| Column | Allowed Values |
|--------|---------------|
| `congestion_level` | `low`, `medium`, `high`, `critical` |
| `signal_phase` | `green`, `yellow`, `red` |
| `density_percentage` | `0.0` – `100.0` |
| `predicted_level` | Same as `congestion_level` or `NULL` |

---

## Data Retention

- Log records older than 30 days may be purged automatically.
- Session records are kept indefinitely.
- Signal events are kept for the lifetime of their session.

---

## Migration Notes

When migrating to PostgreSQL:
1. Replace `INTEGER PRIMARY KEY AUTOINCREMENT` with `SERIAL PRIMARY KEY`.
2. Replace `TEXT` timestamps with `TIMESTAMPTZ`.
3. Add foreign key constraints (`REFERENCES`) with `ON DELETE CASCADE`.
4. Update connection string in `config/config.yaml`.

---

## Entity-Relationship Diagram

```
sessions (1) ──< traffic_log (N)
sessions (1) ──< signal_events (N)
```

---

*Schema version changes must be documented here and a migration script added to `utils/`.*
