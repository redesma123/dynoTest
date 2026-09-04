"""
Unit tests untuk modul exporters (Excel & PDF).
"""
import os
import tempfile
import pytest

from core.models import DynoResult, BrakeResult, EvaluationStatus, TestSession, Vehicle, TestMode
from exporters.export_service import ExportService


@pytest.fixture
def sample_data():
    veh = Vehicle(vin="MH1KF1118PK123456", test_number="KIR-2026-08-999", license_plate="B 1234 ABC")
    sess = TestSession(vin=veh.vin, inspector_name="Taufik Hidayat", test_mode=TestMode.DYNO, id=1)
    dyno = DynoResult(
        session_id=1,
        max_rpm=9500,
        max_torque_nm=78.5,
        max_power_hp=21.4,
        max_speed_kmh=124.0,
        rpm_at_peak_power=8500,
        rpm_at_peak_torque=6500,
        raw_time_series=[{"t": 0.1, "rpm": 1200, "torque": 20.0, "power": 5.0, "speed": 15.0}],
    )
    brake = BrakeResult(
        session_id=1,
        initial_speed_kmh=50.0,
        peak_braking_force_n=2800.0,
        braking_time_s=2.8,
        total_running_time_s=11.5,
        lux_intensity=18500.0,
        braking_efficiency_pct=62.5,
        lux_pass_status=EvaluationStatus.PASS,
        brake_pass_status=EvaluationStatus.PASS,
        overall_status=EvaluationStatus.PASS,
        raw_time_series=[{"t": 0.1, "speed": 50.0, "brake_force": 1200.0, "lux": 18500.0}],
    )
    return veh, sess, dyno, brake


def test_dyno_excel_and_pdf_export(sample_data):
    veh, sess, dyno, _ = sample_data
    service = ExportService()

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        excel_path = f.name
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        pdf_path = f.name

    try:
        ok_excel = service.export_dyno_excel(excel_path, dyno, sess, veh)
        assert ok_excel is True
        assert os.path.exists(excel_path)
        assert os.path.getsize(excel_path) > 1000

        ok_pdf = service.export_dyno_pdf(pdf_path, dyno, sess, veh)
        assert ok_pdf is True
        assert os.path.exists(pdf_path)
        assert os.path.getsize(pdf_path) > 1000
    finally:
        if os.path.exists(excel_path):
            os.unlink(excel_path)
        if os.path.exists(pdf_path):
            os.unlink(pdf_path)


def test_brake_excel_and_pdf_export(sample_data):
    veh, sess, _, brake = sample_data
    service = ExportService()

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        excel_path = f.name
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        pdf_path = f.name

    try:
        ok_excel = service.export_brake_excel(excel_path, brake, sess, veh)
        assert ok_excel is True
        assert os.path.exists(excel_path)
        assert os.path.getsize(excel_path) > 1000

        ok_pdf = service.export_brake_pdf(pdf_path, brake, sess, veh)
        assert ok_pdf is True
        assert os.path.exists(pdf_path)
        assert os.path.getsize(pdf_path) > 1000
    finally:
        if os.path.exists(excel_path):
            os.unlink(excel_path)
        if os.path.exists(pdf_path):
            os.unlink(pdf_path)


def test_history_export():
    service = ExportService()
    rows = [{"tested_at": "2026-09-04 11:00", "test_number": "UJI01", "vin": "VIN01", "inspector_name": "Budi", "test_mode": "DYNO"}]

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        excel_path = f.name
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        pdf_path = f.name

    try:
        assert service.export_history_excel(excel_path, rows) is True
        assert os.path.exists(excel_path)
        assert service.export_history_pdf(pdf_path, rows) is True
        assert os.path.exists(pdf_path)
    finally:
        if os.path.exists(excel_path):
            os.unlink(excel_path)
        if os.path.exists(pdf_path):
            os.unlink(pdf_path)
