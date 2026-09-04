"""
ExportService — Service Layer for PDF, Excel, and Thermal Receipt Printing.
Follows docs/RULES.md, docs/DESIGN_SYSTEM.md, and docs/API.md.
"""

import csv
import os
import sys
from typing import Any, Dict, List, Optional
from PyQt6.QtGui import QPageLayout, QPageSize, QPdfWriter, QTextDocument
from PyQt6.QtWidgets import QApplication

from core.models import TestSession, Vehicle
from services.report_templates import build_pdf_html, build_receipt_text


def _ensure_qt_app() -> QApplication:
    """Memastikan instance QApplication aktif untuk operasi rendering Qt GUI/PDF."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


class ExportService:
    """Service terpusat untuk penanganan ekspor laporan dan pencetakan."""

    @staticmethod
    def export_to_pdf(
        session: TestSession,
        vehicle: Optional[Vehicle],
        output_pdf_path: str,
    ) -> bool:
        """
        Merender Laporan Resmi Pengujian A4 ke file PDF menggunakan HTML/CSS
        berstandar Modern Light Industrial Theme.
        """
        try:
            _ensure_qt_app()
            html_content = build_pdf_html(session, vehicle)
            doc = QTextDocument()
            doc.setHtml(html_content)

            writer = QPdfWriter(output_pdf_path)
            writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            doc.print(writer)
            return os.path.exists(output_pdf_path)
        except Exception as exc:  # noqa: BLE001
            print(f"[ExportService] Gagal ekspor PDF: {exc}")
            return False

    @staticmethod
    def export_to_excel(
        sessions_data: List[Dict[str, Any]],
        output_path: str,
    ) -> bool:
        """
        Mengoperasikan ekspor daftar sesi ke file CSV / Excel.
        """
        try:
            fieldnames = [
                "ID Sesi",
                "Tanggal & Waktu",
                "No. Uji KIR",
                "VIN (No. Rangka)",
                "No. Polisi",
                "Merk & Tipe",
                "Nama Penguji",
                "Mode Uji",
                "Status",
            ]

            with open(output_path, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for row in sessions_data:
                    mode_val = row.get("test_mode", "—")
                    if hasattr(mode_val, "value"):
                        mode_val = mode_val.value

                    writer.writerow({
                        "ID Sesi": row.get("id", "—"),
                        "Tanggal & Waktu": row.get("tested_at", "—"),
                        "No. Uji KIR": row.get("test_number", "—"),
                        "VIN (No. Rangka)": row.get("vin", "—"),
                        "No. Polisi": row.get("license_plate", "—"),
                        "Merk & Tipe": row.get("brand_model", "—"),
                        "Nama Penguji": row.get("inspector_name", "—"),
                        "Mode Uji": str(mode_val),
                        "Status": "Selesai",
                    })
            return os.path.exists(output_path)
        except Exception as exc:  # noqa: BLE001
            print(f"[ExportService] Gagal ekspor Excel/CSV: {exc}")
            return False

    @staticmethod
    def print_thermal_receipt(
        session: TestSession,
        vehicle: Optional[Vehicle],
        output_path: str = "",
    ) -> bool:
        """
        Mencetak atau merender Struk Thermal Ringkas (58mm/80mm).
        Jika output_path diisi, struk akan disimpan sebagai file teks / PDF.
        """
        try:
            _ensure_qt_app()
            receipt_text = build_receipt_text(session, vehicle)

            if not output_path:
                output_path = f"Struk_Sesi_{session.id}.txt"

            if output_path.endswith(".pdf"):
                html_receipt = f"<pre style='font-family: monospace; font-size: 11px;'>{receipt_text}</pre>"
                doc = QTextDocument()
                doc.setHtml(html_receipt)
                writer = QPdfWriter(output_path)
                writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
                doc.print(writer)
            else:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(receipt_text)

            return True
        except Exception as exc:  # noqa: BLE001
            print(f"[ExportService] Gagal cetak struk: {exc}")
            return False
