"""
Database connection manager and schema initializer for SQLite.
Ensures Foreign Keys and WAL Mode are active.
"""
import os
import sqlite3
from typing import Optional

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dyno_database.db")

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS vehicles (
    vin TEXT PRIMARY KEY,
    test_number TEXT UNIQUE NOT NULL,
    license_plate TEXT,
    vehicle_category TEXT DEFAULT 'Roda 2',
    brand_model TEXT,
    engine_capacity_cc INTEGER,
    vehicle_weight_kg REAL NOT NULL DEFAULT 150.0,
    created_at DATETIME DEFAULT (DATETIME('now', 'localtime'))
);

CREATE INDEX IF NOT EXISTS idx_vehicles_test_number ON vehicles(test_number);
CREATE INDEX IF NOT EXISTS idx_vehicles_license_plate ON vehicles(license_plate);

CREATE TABLE IF NOT EXISTS test_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vin TEXT NOT NULL,
    inspector_name TEXT NOT NULL,
    test_mode TEXT NOT NULL CHECK(test_mode IN ('DYNO', 'BRAKE', 'COMBINED')),
    tested_at DATETIME DEFAULT (DATETIME('now', 'localtime')),
    notes TEXT,
    FOREIGN KEY(vin) REFERENCES vehicles(vin) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_test_sessions_vin ON test_sessions(vin);
CREATE INDEX IF NOT EXISTS idx_test_sessions_tested_at ON test_sessions(tested_at);

CREATE TABLE IF NOT EXISTS dyno_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL UNIQUE,
    max_rpm REAL NOT NULL,
    max_torque_nm REAL NOT NULL,
    max_power_hp REAL NOT NULL,
    max_speed_kmh REAL NOT NULL,
    rpm_at_peak_power REAL,
    rpm_at_peak_torque REAL,
    raw_time_series_json TEXT,
    FOREIGN KEY(session_id) REFERENCES test_sessions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS brake_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL UNIQUE,
    initial_speed_kmh REAL NOT NULL,
    peak_braking_force_n REAL NOT NULL,
    braking_time_s REAL NOT NULL,
    total_running_time_s REAL NOT NULL,
    lux_intensity REAL NOT NULL,
    braking_efficiency_pct REAL NOT NULL,
    lux_pass_status TEXT NOT NULL CHECK(lux_pass_status IN ('PASS', 'FAIL')),
    brake_pass_status TEXT NOT NULL CHECK(brake_pass_status IN ('PASS', 'FAIL')),
    overall_status TEXT NOT NULL CHECK(overall_status IN ('PASS', 'FAIL')),
    raw_time_series_json TEXT,
    FOREIGN KEY(session_id) REFERENCES test_sessions(id) ON DELETE CASCADE
);
"""


class DatabaseManager:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DEFAULT_DB_PATH

    def get_connection(self) -> sqlite3.Connection:
        """Returns SQLite connection with row factory and foreign keys enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_database(self) -> None:
        """Executes table creation DDL."""
        with self.get_connection() as conn:
            conn.executescript(SCHEMA_SQL)
