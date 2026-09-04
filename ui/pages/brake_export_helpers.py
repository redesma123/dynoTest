"""
Helper fungsi ekspor PDF, Excel, & Struk thermal untuk BrakeTestPage.
Menjaga brake_test_page.py tetap di bawah 300 baris (RULES.md).
"""

from PyQt6.QtWidgets import QFileDialog, QMessageBox, QWidget

from database.repository import DatabaseRepository
from services import ExportService


def export_brake_pdf(parent: QWidget, repo: DatabaseRepository, session_id: int | None) -> None:
    """Ekspor laporan pengujian ke format PDF."""
    if not session_id:
        QMessageBox.warning(parent, "Peringatan", "Belum ada sesi pengujian yang aktif untuk diekspor.")
        return
    session = repo.get_test_session(session_id)
    if not session:
        QMessageBox.warning(parent, "Peringatan", "Data sesi tidak ditemukan di database.")
        return
    vehicle = repo.get_vehicle_by_vin(session.vin)
    file_path, _ = QFileDialog.getSaveFileName(
        parent, "Export Laporan PDF", f"Laporan_Sesi_{session_id}.pdf", "PDF Files (*.pdf)"
    )
    if file_path:
        if ExportService.export_to_pdf(session, vehicle, file_path):
            QMessageBox.information(parent, "Sukses Ekspor", f"Laporan PDF berhasil disimpan ke:\n{file_path}")


def export_brake_excel(parent: QWidget, repo: DatabaseRepository, session_id: int | None) -> None:
    """Ekspor data pengujian ke format CSV/Excel."""
    if not session_id:
        QMessageBox.warning(parent, "Peringatan", "Belum ada sesi pengujian yang aktif untuk diekspor.")
        return
    session = repo.get_test_session(session_id)
    if not session:
        QMessageBox.warning(parent, "Peringatan", "Data sesi tidak ditemukan di database.")
        return
    vehicle = repo.get_vehicle_by_vin(session.vin)
    file_path, _ = QFileDialog.getSaveFileName(
        parent, "Export Data Excel", f"Data_Sesi_{session_id}.csv", "CSV Files (*.csv)"
    )
    if file_path:
        rows = [{
            "id": session.id,
            "tested_at": session.tested_at,
            "test_number": vehicle.test_number if vehicle else "—",
            "vin": session.vin,
            "license_plate": vehicle.license_plate if vehicle else "—",
            "brand_model": vehicle.brand_model if vehicle else "—",
            "inspector_name": session.inspector_name,
            "test_mode": session.test_mode,
        }]
        if ExportService.export_to_excel(rows, file_path):
            QMessageBox.information(parent, "Sukses Ekspor", f"Data Excel/CSV berhasil disimpan ke:\n{file_path}")


def print_brake_receipt(parent: QWidget, repo: DatabaseRepository, session_id: int | None) -> None:
    """Cetak struk thermal hasil pengujian."""
    if not session_id:
        QMessageBox.warning(parent, "Peringatan", "Belum ada sesi pengujian yang aktif untuk dicetak.")
        return
    session = repo.get_test_session(session_id)
    if not session:
        QMessageBox.warning(parent, "Peringatan", "Data sesi tidak ditemukan di database.")
        return
    vehicle = repo.get_vehicle_by_vin(session.vin)
    out_file = f"Struk_Sesi_{session_id}.txt"
    if ExportService.print_thermal_receipt(session, vehicle, out_file):
        QMessageBox.information(parent, "Cetak Struk", f"Struk thermal berhasil dicetak/disimpan ke:\n{out_file}")
