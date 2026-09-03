"""
HistoryPage — Halaman Riwayat & Laporan Pengujian (Shortcut: F4).
Acuan: DESIGN.md & Mockup Laporan Pengujian.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from database.repository import DatabaseRepository
from ui.components.history.history_detail_dialog import HistoryDetailDialog
from ui.components.history.history_filter_panel import HistoryFilterPanel
from ui.components.history.history_table_panel import HistoryTablePanel
from ui.styles import Spacing


def _lbl(text: str, obj_name: str) -> QLabel:
    l = QLabel(text)
    l.setObjectName(obj_name)
    return l


class HistoryPage(QWidget):
    """Halaman Dashboard Riwayat & Laporan Pengujian."""

    def __init__(self, repository: DatabaseRepository, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("appRoot")
        self._repo = repository

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

        content = QWidget()
        content.setObjectName("appRoot")

        root = QVBoxLayout(content)
        root.setContentsMargins(Spacing.XXL, Spacing.XL, Spacing.XXL, Spacing.LG)
        root.setSpacing(Spacing.MD)

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
        col.addWidget(_lbl("Laporan Pengujian", "pageTitle"))
        col.addWidget(_lbl("Lihat, tinjau, dan ekspor hasil pengujian kendaraan.", "pageSubtitle"))
        row.addLayout(col)
        row.addStretch(1)

        pdf_btn = QPushButton("📄  Export PDF  [F11]")
        pdf_btn.setObjectName("secondaryButton")
        pdf_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        pdf_btn.clicked.connect(self._on_export_pdf)

        excel_btn = QPushButton("📊  Export Excel  [F10]")
        excel_btn.setObjectName("saveButton")
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
        """Placeholder — shortcut F12 print thermal receipt."""
        print(f"[HistoryPage] Cetak struk untuk sesi #{session_id}")

    def _on_export_pdf(self) -> None:
        """Placeholder — shortcut F11 export PDF."""
        print("[HistoryPage] Trigger Export PDF")

    def _on_export_excel(self) -> None:
        """Placeholder — shortcut F10 export Excel."""
        print("[HistoryPage] Trigger Export Excel")

    def _setup_shortcuts(self) -> None:
        QShortcut(QKeySequence("F10"), self).activated.connect(self._on_export_excel)
        QShortcut(QKeySequence("F11"), self).activated.connect(self._on_export_pdf)
        QShortcut(QKeySequence("F5"),  self).activated.connect(self.reload_data)
