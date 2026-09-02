"""
Database repository implementation for DynoTest & BrakeTest.
Provides atomic transactions and clean entity mapping.
"""
import json
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from core.models import (
    Vehicle,
    TestSession,
    TestMode,
    DynoResult,
    BrakeResult,
    EvaluationStatus
)
from database.connection import DatabaseManager


class DatabaseRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.db_manager.init_database()

    # ==================== VEHICLE CRUD ====================

    def save_vehicle(self, vehicle: Vehicle) -> bool:
        """Upsert vehicle data."""
        sql = """
        INSERT INTO vehicles (
            vin, test_number, license_plate, vehicle_category,
            brand_model, engine_capacity_cc, vehicle_weight_kg, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, COALESCE(?, DATETIME('now', 'localtime')))
        ON CONFLICT(vin) DO UPDATE SET
            test_number=excluded.test_number,
            license_plate=excluded.license_plate,
            vehicle_category=excluded.vehicle_category,
            brand_model=excluded.brand_model,
            engine_capacity_cc=excluded.engine_capacity_cc,
            vehicle_weight_kg=excluded.vehicle_weight_kg;
        """
        with self.db_manager.get_connection() as conn:
            conn.execute(sql, (
                vehicle.vin,
                vehicle.test_number,
                vehicle.license_plate,
                vehicle.vehicle_category,
                vehicle.brand_model,
                vehicle.engine_capacity_cc,
                vehicle.vehicle_weight_kg,
                vehicle.created_at
            ))
            conn.commit()
            return True

    def get_vehicle_by_vin(self, vin: str) -> Optional[Vehicle]:
        sql = "SELECT * FROM vehicles WHERE vin = ?;"
        with self.db_manager.get_connection() as conn:
            row = conn.execute(sql, (vin,)).fetchone()
            if not row:
                return None
            return self._row_to_vehicle(row)

    def get_vehicle_by_test_number(self, test_number: str) -> Optional[Vehicle]:
        sql = "SELECT * FROM vehicles WHERE test_number = ?;"
        with self.db_manager.get_connection() as conn:
            row = conn.execute(sql, (test_number,)).fetchone()
            if not row:
                return None
            return self._row_to_vehicle(row)

    def search_vehicles(self, query: str, limit: int = 10) -> List[Vehicle]:
        sql = """
        SELECT * FROM vehicles
        WHERE vin LIKE ? OR test_number LIKE ? OR license_plate LIKE ? OR brand_model LIKE ?
        ORDER BY created_at DESC LIMIT ?;
        """
        wildcard = f"%{query}%"
        with self.db_manager.get_connection() as conn:
            rows = conn.execute(sql, (wildcard, wildcard, wildcard, wildcard, limit)).fetchall()
            return [self._row_to_vehicle(r) for r in rows]

    # ==================== TEST SESSION CRUD ====================

    def create_test_session(self, session: TestSession) -> int:
        """Create new test session record and return inserted ID."""
        sql = """
        INSERT INTO test_sessions (vin, inspector_name, test_mode, notes, tested_at)
        VALUES (?, ?, ?, ?, COALESCE(?, DATETIME('now', 'localtime')));
        """
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute(sql, (
                session.vin,
                session.inspector_name,
                session.test_mode.value if isinstance(session.test_mode, TestMode) else session.test_mode,
                session.notes,
                session.tested_at
            ))
            conn.commit()
            session.id = cursor.lastrowid
            return cursor.lastrowid

    def get_test_session(self, session_id: int) -> Optional[TestSession]:
        sql = "SELECT * FROM test_sessions WHERE id = ?;"
        with self.db_manager.get_connection() as conn:
            row = conn.execute(sql, (session_id,)).fetchone()
            if not row:
                return None

            session = TestSession(
                id=row["id"],
                vin=row["vin"],
                inspector_name=row["inspector_name"],
                test_mode=TestMode(row["test_mode"]),
                notes=row["notes"] or "",
                tested_at=row["tested_at"]
            )
            session.dyno_result = self.get_dyno_result_by_session(session_id)
            session.brake_result = self.get_brake_result_by_session(session_id)
            return session

    def get_recent_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        sql = """
        SELECT s.id, s.vin, v.test_number, v.license_plate, v.brand_model,
               s.inspector_name, s.test_mode, s.tested_at
        FROM test_sessions s
        JOIN vehicles v ON s.vin = v.vin
        ORDER BY s.tested_at DESC LIMIT ?;
        """
        with self.db_manager.get_connection() as conn:
            rows = conn.execute(sql, (limit,)).fetchall()
            return [dict(r) for r in rows]

    # ==================== RESULTS CRUD ====================

    def save_dyno_result(self, result: DynoResult) -> int:
        sql = """
        INSERT INTO dyno_results (
            session_id, max_rpm, max_torque_nm, max_power_hp,
            max_speed_kmh, rpm_at_peak_power, rpm_at_peak_torque, raw_time_series_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(session_id) DO UPDATE SET
            max_rpm=excluded.max_rpm,
            max_torque_nm=excluded.max_torque_nm,
            max_power_hp=excluded.max_power_hp,
            max_speed_kmh=excluded.max_speed_kmh,
            rpm_at_peak_power=excluded.rpm_at_peak_power,
            rpm_at_peak_torque=excluded.rpm_at_peak_torque,
            raw_time_series_json=excluded.raw_time_series_json;
        """
        time_series_json = json.dumps(result.raw_time_series) if result.raw_time_series else None
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute(sql, (
                result.session_id,
                result.max_rpm,
                result.max_torque_nm,
                result.max_power_hp,
                result.max_speed_kmh,
                result.rpm_at_peak_power,
                result.rpm_at_peak_torque,
                time_series_json
            ))
            conn.commit()
            result.id = cursor.lastrowid
            return cursor.lastrowid

    def get_dyno_result_by_session(self, session_id: int) -> Optional[DynoResult]:
        sql = "SELECT * FROM dyno_results WHERE session_id = ?;"
        with self.db_manager.get_connection() as conn:
            row = conn.execute(sql, (session_id,)).fetchone()
            if not row:
                return None
            raw_ts = json.loads(row["raw_time_series_json"]) if row["raw_time_series_json"] else []
            return DynoResult(
                id=row["id"],
                session_id=row["session_id"],
                max_rpm=row["max_rpm"],
                max_torque_nm=row["max_torque_nm"],
                max_power_hp=row["max_power_hp"],
                max_speed_kmh=row["max_speed_kmh"],
                rpm_at_peak_power=row["rpm_at_peak_power"] or 0.0,
                rpm_at_peak_torque=row["rpm_at_peak_torque"] or 0.0,
                raw_time_series=raw_ts
            )

    def save_brake_result(self, result: BrakeResult) -> int:
        sql = """
        INSERT INTO brake_results (
            session_id, initial_speed_kmh, peak_braking_force_n, braking_time_s,
            total_running_time_s, lux_intensity, braking_efficiency_pct,
            lux_pass_status, brake_pass_status, overall_status, raw_time_series_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(session_id) DO UPDATE SET
            initial_speed_kmh=excluded.initial_speed_kmh,
            peak_braking_force_n=excluded.peak_braking_force_n,
            braking_time_s=excluded.braking_time_s,
            total_running_time_s=excluded.total_running_time_s,
            lux_intensity=excluded.lux_intensity,
            braking_efficiency_pct=excluded.braking_efficiency_pct,
            lux_pass_status=excluded.lux_pass_status,
            brake_pass_status=excluded.brake_pass_status,
            overall_status=excluded.overall_status,
            raw_time_series_json=excluded.raw_time_series_json;
        """
        time_series_json = json.dumps(result.raw_time_series) if result.raw_time_series else None
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute(sql, (
                result.session_id,
                result.initial_speed_kmh,
                result.peak_braking_force_n,
                result.braking_time_s,
                result.total_running_time_s,
                result.lux_intensity,
                result.braking_efficiency_pct,
                result.lux_pass_status.value if isinstance(result.lux_pass_status, EvaluationStatus) else result.lux_pass_status,
                result.brake_pass_status.value if isinstance(result.brake_pass_status, EvaluationStatus) else result.brake_pass_status,
                result.overall_status.value if isinstance(result.overall_status, EvaluationStatus) else result.overall_status,
                time_series_json
            ))
            conn.commit()
            result.id = cursor.lastrowid
            return cursor.lastrowid

    def get_brake_result_by_session(self, session_id: int) -> Optional[BrakeResult]:
        sql = "SELECT * FROM brake_results WHERE session_id = ?;"
        with self.db_manager.get_connection() as conn:
            row = conn.execute(sql, (session_id,)).fetchone()
            if not row:
                return None
            raw_ts = json.loads(row["raw_time_series_json"]) if row["raw_time_series_json"] else []
            return BrakeResult(
                id=row["id"],
                session_id=row["session_id"],
                initial_speed_kmh=row["initial_speed_kmh"],
                peak_braking_force_n=row["peak_braking_force_n"],
                braking_time_s=row["braking_time_s"],
                total_running_time_s=row["total_running_time_s"],
                lux_intensity=row["lux_intensity"],
                braking_efficiency_pct=row["braking_efficiency_pct"],
                lux_pass_status=EvaluationStatus(row["lux_pass_status"]),
                brake_pass_status=EvaluationStatus(row["brake_pass_status"]),
                overall_status=EvaluationStatus(row["overall_status"]),
                raw_time_series=raw_ts
            )

    def _row_to_vehicle(self, row: sqlite3.Row) -> Vehicle:
        return Vehicle(
            vin=row["vin"],
            test_number=row["test_number"],
            license_plate=row["license_plate"] or "",
            vehicle_category=row["vehicle_category"] or "Roda 2",
            brand_model=row["brand_model"] or "",
            engine_capacity_cc=row["engine_capacity_cc"] or 150,
            vehicle_weight_kg=row["vehicle_weight_kg"] or 150.0,
            created_at=row["created_at"]
        )
