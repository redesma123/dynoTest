import os
import tempfile
import pytest
from core.models import (
    Vehicle,
    TestSession,
    TestMode,
    DynoResult,
    BrakeResult,
    EvaluationStatus
)
from database.connection import DatabaseManager
from database.repository import DatabaseRepository


import gc


@pytest.fixture
def temp_repo():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db_mgr = DatabaseManager(path)
    repo = DatabaseRepository(db_mgr)
    yield repo
    gc.collect()
    if os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass


def test_vehicle_crud(temp_repo):
    veh = Vehicle(
        vin="MH1JF5123PK009988",
        test_number="KIR-2026-08-001",
        license_plate="B 1234 XYZ",
        vehicle_category="Roda 2",
        brand_model="Honda Vario 160",
        engine_capacity_cc=160,
        vehicle_weight_kg=118.0
    )
    assert temp_repo.save_vehicle(veh) is True

    fetched = temp_repo.get_vehicle_by_vin("MH1JF5123PK009988")
    assert fetched is not None
    assert fetched.test_number == "KIR-2026-08-001"
    assert fetched.brand_model == "Honda Vario 160"

    # Search
    search_res = temp_repo.search_vehicles("Vario")
    assert len(search_res) == 1
    assert search_res[0].vin == "MH1JF5123PK009988"


def test_test_session_and_results(temp_repo):
    # Setup vehicle
    veh = Vehicle(
        vin="MH1JF5123PK001122",
        test_number="KIR-2026-08-002",
        license_plate="D 5678 ABC",
        brand_model="Yamaha NMAX 155",
        vehicle_weight_kg=130.0
    )
    temp_repo.save_vehicle(veh)

    # Create session
    session = TestSession(
        vin=veh.vin,
        inspector_name="Budi Santoso",
        test_mode=TestMode.COMBINED,
        notes="Pengujian berkala 6 bulanan"
    )
    session_id = temp_repo.create_test_session(session)
    assert session_id > 0

    # Save Dyno result
    dyno_res = DynoResult(
        session_id=session_id,
        max_rpm=9500.0,
        max_torque_nm=14.5,
        max_power_hp=15.2,
        max_speed_kmh=115.0,
        rpm_at_peak_power=8000.0,
        rpm_at_peak_torque=6500.0,
        raw_time_series=[{"t": 1.0, "rpm": 3000, "hp": 5.0}]
    )
    temp_repo.save_dyno_result(dyno_res)

    # Save Brake result
    brake_res = BrakeResult(
        session_id=session_id,
        initial_speed_kmh=50.0,
        peak_braking_force_n=950.0,
        braking_time_s=1.2,
        total_running_time_s=10.0,
        lux_intensity=14800.0,
        braking_efficiency_pct=74.5,
        lux_pass_status=EvaluationStatus.PASS,
        brake_pass_status=EvaluationStatus.PASS,
        overall_status=EvaluationStatus.PASS,
        raw_time_series=[{"t": 1.0, "force_n": 950.0}]
    )
    temp_repo.save_brake_result(brake_res)

    # Retrieve full session with attached results
    full_session = temp_repo.get_test_session(session_id)
    assert full_session is not None
    assert full_session.dyno_result is not None
    assert full_session.dyno_result.max_power_hp == 15.2
    assert full_session.brake_result is not None
    assert full_session.brake_result.overall_status == EvaluationStatus.PASS
