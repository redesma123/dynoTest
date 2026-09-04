"""
HistoryPage — Halaman Riwayat & Laporan Pengujian (Shortcut: F4).
Acuan: DESIGN.md & Mockup Laporan Pengujian.
"""

from datetime import datetime
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from database.repository import DatabaseRepository
from exporters.export_service import ExportService
from ui.components.common.factory import create_label
from ui.components.history.history_detail_dialog import HistoryDetailDialog
from ui.components.history.history_filter_panel import HistoryFilterPanel
from ui.components.history.history_table_panel import HistoryTablePanel
from ui.styles import Spacing


class HistoryPage(QWidget):
    """Halaman Dashboard Riwayat & Laporan Pengujian."""

    def __init__(self, repository: DatabaseRepository, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("appRoot")
        self._repo = repository
        self._export_service = ExportService(self._repo)

        self._build_ui()
        self._setup_shortcuts()

    def reload_data(self) -> None:
        """Refresh data dari DB (dipanggil saat switch tab atau filter)."""
        rows = self._repo.get_recent_sessions(limit=100)
        self._all_rows = rows
        self._table_panel.set_data(rows)

    def _build_ui(self) -> None:
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        content = QWidget()
        content.setObjectName("appRoot")

        root = QVBoxLayout(content)
        root.setContentsMargins(Spacing.LG, Spacing.MD, Spacing.LG, Spacing.LG)
        root.setSpacing(Spacing.MD)
        root.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinimumSize)

        # 1. Header Row (Judul + Export buttons)
        root.addLayout(self._build_header())

        # 2. Filter Card
        self._filter_panel = HistoryFilterPanel()
        self._filter_panel.filter_changed.connect(self._on_filter_changed)
        root.addWidget(self._filter_panel)

        # 3. Table Card
        self._table_panel = HistoryTablePanel()
        self._table_panel.detail_requested.connect(self._on_show_detail)
        self._table_panel.print_requested.connect(self._on_print_receipt)
        root.addWidget(self._table_panel, 1)

        scroll.setWidget(content)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        self.reload_data()

    def _build_header(self) -> QHBoxLayout:
        row = QHBoxLayout()
        col = QVBoxLayout()
        col.setSpacing(2)
        col.addWidget(create_label("Laporan Pengujian", "pageTitle"))
        col.addWidget(create_label("Lihat, tinjau, dan ekspor hasil pengujian kendaraan.", "pageSubtitle"))
        row.addLayout(col)
        row.addStretch(1)

        pdf_btn = QPushButton("📄  Export PDF  [F11]")
        pdf_btn.setObjectName("secondaryButton")
        pdf_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        pdf_btn.clicked.connect(self._on_export_pdf)

        excel_btn = QPushButton("📊  Export Excel  [F10]")
        excel_btn.setObjectName("secondaryButton")
        excel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        excel_btn.clicked.connect(self._on_export_excel)

        row.addWidget(pdf_btn)
        row.addWidget(excel_btn)
        return row

    def _on_filter_changed(self, filters: dict) -> None:
        q_no = filters.get("test_number", "").lower()
        q_mode = filters.get("mode", "").lower()
        q_date = filters.get("date", "").lower()

        filtered = []
        for r in self._all_rows:
            match_no = not q_no or q_no in str(r.get("test_number", "")).lower()
            mode_val = str(r.get("test_mode", "")).lower()
            match_mode = not q_mode or q_mode in mode_val
            date_val = str(r.get("tested_at", "")).lower()
            match_date = not q_date or q_date in date_val

            if match_no and match_mode and match_date:
                filtered.append(r)

        self._table_panel.set_data(filtered)

    def _on_show_detail(self, session_id: int) -> None:
        dlg = HistoryDetailDialog(self._repo, session_id, parent=self)
        dlg.exec()

    def _on_print_receipt(self, session_id: int) -> None:
        session = self._repo.get_test_session(session_id)
        vehicle = self._repo.get_vehicle_by_vin(session.vin) if session else None
        dyno_res = self._repo.get_dyno_result_by_session(session_id)
        brake_res = self._repo.get_brake_result_by_session(session_id)

        txt = self._export_service.format_thermal_receipt_text(session, vehicle, dyno_res, brake_res)
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            f"Simpan Struk Pengujian #{session_id}",
            f"Struk_Uji_{session_id}.txt",
            "Text Files (*.txt);;All Files (*)",
        )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(txt)
            QMessageBox.information(self, "Cetak Struk", f"Struk berhasil diekspor ke:\n{file_path}")

    def _on_export_pdf(self) -> None:
        rows = getattr(self._table_panel, "_all_rows", [])
        if not rows:
            QMessageBox.warning(self, "Export PDF", "Tidak ada data riwayat untuk diekspor.")
            return

        default_name = f"Laporan_Riwayat_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Riwayat ke PDF", default_name, "PDF Files (*.pdf)"
        )
        if file_path:
            ok = self._export_service.export_history_pdf(file_path, rows)
            if ok:
                QMessageBox.information(self, "Export Berhasil", f"Laporan PDF berhasil disimpan ke:\n{file_path}")
            else:
                QMessageBox.critical(self, "Export Gagal", "Gagal mengekspor laporan PDF.")

    def _on_export_excel(self) -> None:
        rows = getattr(self._table_panel, "_all_rows", [])
        if not rows:
            QMessageBox.warning(self, "Export Excel", "Tidak ada data riwayat untuk diekspor.")
            return

        default_name = f"Laporan_Riwayat_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Riwayat ke Excel", default_name, "Excel Files (*.xlsx)"
        )
        if file_path:
            ok = self._export_service.export_history_excel(file_path, rows)
            if ok:
                QMessageBox.information(self, "Export Berhasil", f"Laporan Excel berhasil disimpan ke:\n{file_path}")
            else:
                QMessageBox.critical(self, "Export Gagal", "Gagal mengekspor laporan Excel.")

    def _setup_shortcuts(self) -> None:
        QShortcut(QKeySequence("F10"), self).activated.connect(self._on_export_excel)
        QShortcut(QKeySequence("F11"), self).activated.connect(self._on_export_pdf)
        QShortcut(QKeySequence("F5"),  self).activated.connect(self.reload_data)
