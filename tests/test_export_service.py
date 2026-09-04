"""
Unit tests for ExportService (PDF, Excel/CSV, Thermal receipt).
"""

import os
import tempfile
import sys
from PyQt6.QtWidgets import QApplication

from core.models import (
    BrakeResult,
    DynoResult,
    EvaluationStatus,
    TestMode,
    TestSession,
    Vehicle,
)
from services import ExportService

_app = QApplication.instance() or QApplication(sys.argv)


def test_export_pdf_and_receipt():
    veh = Vehicle(
        vin="MH1JF5123PK009988",
        test_number="KIR-2026-08-001",
        license_plate="B 1234 XYZ",
        vehicle_category="Roda 2",
        brand_model="Honda Vario 160",
        engine_capacity_cc=160,
        vehicle_weight_kg=118.0,
    )

    session = TestSession(
        id=1,
        vin=veh.vin,
        inspector_name="Budi Santoso",
        test_mode=TestMode.COMBINED,
        notes="Pengujian KIR Berkala",
    )

    session.dyno_result = DynoResult(
        session_id=1,
        max_power_hp=15.2,
        max_torque_nm=14.5,
        max_speed_kmh=115.0,
        max_rpm=9500.0,
    )

    session.brake_result = BrakeResult(
        session_id=1,
        peak_braking_force_n=950.0,
        braking_time_s=1.2,
        lux_intensity=14800.0,
        braking_efficiency_pct=74.5,
        brake_pass_status=EvaluationStatus.PASS,
        lux_pass_status=EvaluationStatus.PASS,
        overall_status=EvaluationStatus.PASS,
    )

    # Test PDF export
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        pdf_path = f.name

    try:
        success_pdf = ExportService.export_to_pdf(session, veh, pdf_path)
        assert success_pdf is True
        assert os.path.exists(pdf_path)
        assert os.path.getsize(pdf_path) > 0
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    # Test Receipt export
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        receipt_path = f.name

    try:
        success_receipt = ExportService.print_thermal_receipt(session, veh, receipt_path)
        assert success_receipt is True
        assert os.path.exists(receipt_path)
        assert os.path.getsize(receipt_path) > 0
    finally:
        if os.path.exists(receipt_path):
            os.remove(receipt_path)


def test_export_excel_csv():
    rows = [
        {
            "id": 1,
            "test_number": "KIR-2026-08-001",
            "vin": "MH1JF5123PK009988",
            "license_plate": "B 1234 XYZ",
            "brand_model": "Honda Vario 160",
            "inspector_name": "Budi Santoso",
            "test_mode": "DYNO",
            "tested_at": "2026-09-04 10:00:00",
        }
    ]

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        csv_path = f.name

    try:
        success_csv = ExportService.export_to_excel(rows, csv_path)
        assert success_csv is True
        assert os.path.exists(csv_path)
        assert os.path.getsize(csv_path) > 0
    finally:
        if os.path.exists(csv_path):
            os.remove(csv_path)
