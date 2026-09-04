"""
ExportService — Layanan terpusat untuk ekspor laporan PDF, Excel, dan struk termal.
Acuan: docs/API.md §C "ExportService Contract".
"""

import os
from typing import Any, Dict, List, Optional

from core.models import BrakeResult, DynoResult, TestSession, Vehicle
from database.repository import DatabaseRepository
from exporters.excel_exporter import (
    export_brake_to_excel,
    export_dyno_to_excel,
    export_history_to_excel,
)
from exporters.pdf_exporter import (
    export_brake_to_pdf,
    export_dyno_to_pdf,
    export_history_to_pdf,
)


class ExportService:
    """Service facade untuk operasi ekspor dokumen laporan pengujian."""

    def __init__(self, repository: Optional[DatabaseRepository] = None):
        self._repo = repository

    def export_dyno_excel(
        self,
        filepath: str,
        result: DynoResult,
        session: Optional[TestSession] = None,
        vehicle: Optional[Vehicle] = None,
    ) -> bool:
        if self._repo and session is None and result.session_id:
            session = self._repo.get_test_session(result.session_id)
        if self._repo and vehicle is None and session and session.vin:
            vehicle = self._repo.get_vehicle_by_vin(session.vin)
        return export_dyno_to_excel(filepath, session, vehicle, result)

    def export_dyno_pdf(
        self,
        filepath: str,
        result: DynoResult,
        session: Optional[TestSession] = None,
        vehicle: Optional[Vehicle] = None,
    ) -> bool:
        if self._repo and session is None and result.session_id:
            session = self._repo.get_test_session(result.session_id)
        if self._repo and vehicle is None and session and session.vin:
            vehicle = self._repo.get_vehicle_by_vin(session.vin)
        return export_dyno_to_pdf(filepath, session, vehicle, result)

    def export_brake_excel(
        self,
        filepath: str,
        result: BrakeResult,
        session: Optional[TestSession] = None,
        vehicle: Optional[Vehicle] = None,
    ) -> bool:
        if self._repo and session is None and result.session_id:
            session = self._repo.get_test_session(result.session_id)
        if self._repo and vehicle is None and session and session.vin:
            vehicle = self._repo.get_vehicle_by_vin(session.vin)
        return export_brake_to_excel(filepath, session, vehicle, result)

    def export_brake_pdf(
        self,
        filepath: str,
        result: BrakeResult,
        session: Optional[TestSession] = None,
        vehicle: Optional[Vehicle] = None,
    ) -> bool:
        if self._repo and session is None and result.session_id:
            session = self._repo.get_test_session(result.session_id)
        if self._repo and vehicle is None and session and session.vin:
            vehicle = self._repo.get_vehicle_by_vin(session.vin)
        return export_brake_to_pdf(filepath, session, vehicle, result)

    def export_history_excel(self, filepath: str, rows: List[Dict[str, Any]]) -> bool:
        return export_history_to_excel(filepath, rows)

    def export_history_pdf(self, filepath: str, rows: List[Dict[str, Any]]) -> bool:
        return export_history_to_pdf(filepath, rows)

    def format_thermal_receipt_text(
        self,
        session: Optional[TestSession],
        vehicle: Optional[Vehicle],
        dyno_result: Optional[DynoResult] = None,
        brake_result: Optional[BrakeResult] = None,
    ) -> str:
        """Menghasilkan teks format struk pengujian 58mm/80mm."""
        w = 32
        lines = [
            "=" * w,
            "AUTO-TECH SYSTEMS".center(w),
            "BUKTI HASIL PENGUJIAN".center(w),
            "=" * w,
            f"No. Uji : {vehicle.test_number if vehicle else '—'}",
            f"VIN     : {vehicle.vin if vehicle else '—'}",
            f"No. Pol : {vehicle.license_plate if vehicle else '—'}",
            f"Penguji : {session.inspector_name if session else '—'}",
            f"Waktu   : {str(session.tested_at)[:16] if session and session.tested_at else '—'}",
            "-" * w,
        ]

        if dyno_result:
            lines.extend([
                "HASIL UJI DYNO:".center(w),
                f"Peak HP    : {dyno_result.max_power_hp:.2f} HP",
                f"Peak Torsi : {dyno_result.max_torque_nm:.1f} Nm",
                f"Top Speed  : {dyno_result.max_speed_kmh:.1f} km/h",
                "-" * w,
            ])

        if brake_result:
            eff = brake_result.braking_efficiency_pct
            b_ok = "LULUS" if eff >= 50.0 else "GAGAL"
            l_ok = "LULUS" if brake_result.lux_intensity >= 12000.0 else "GAGAL"
            lines.extend([
                "HASIL UJI REM & LAMPU:".center(w),
                f"Efisiensi  : {eff:.1f}% [{b_ok}]",
                f"Gaya Rem   : {brake_result.peak_braking_force_n:.0f} N",
                f"Lampu Utama: {brake_result.lux_intensity:,.0f} Lx [{l_ok}]",
                f"Status Akhir: {brake_result.overall_status.value}",
                "-" * w,
            ])

        lines.extend([
            "Terima kasih atas kunjungan Anda".center(w),
            "=" * w,
        ])
        return "\n".join(lines)
