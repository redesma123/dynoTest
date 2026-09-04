"""
HistoryTablePanel — Tabel data riwayat & pagination footer bar.
Acuan mockup Laporan Pengujian.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ui.components.common.factory import create_label
from ui.styles import Colors, FONT_MONO, Spacing

COLUMNS = ["TANGGAL & WAKTU", "NO. UJI", "NO. RANGKA", "NAMA PENGUJI", "MODE", "HASIL", "AKSI"]


class HistoryTablePanel(QFrame):
    """Panel Tabel Riwayat dan Navigasi Halaman."""

    detail_requested = pyqtSignal(int)
    print_requested  = pyqtSignal(int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("tableCard")
        self._current_page = 1
        self._page_size = 5
        self._total_entries = 0
        self._all_rows: list[dict] = []

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 1. Tabel Utama
        self.table = QTableWidget()
        self.table.setObjectName("historyTable")
        self.table.setColumnCount(len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.setMinimumHeight(160)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(48)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(5, 120)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(6, 110)

        layout.addWidget(self.table, 1)

        # 2. Footer Bar (Pagination & Info)
        footer_bar = QFrame()
        footer_bar.setObjectName("historyHeaderBar")
        foot_lay = QHBoxLayout(footer_bar)
        foot_lay.setContentsMargins(Spacing.LG, Spacing.SM, Spacing.LG, Spacing.SM)

        self.info_lbl = create_label("Showing 0 of 0 entries", "weatherRow")
        foot_lay.addWidget(self.info_lbl)
        foot_lay.addStretch(1)

        self.pag_layout = QHBoxLayout()
        self.pag_layout.setSpacing(Spacing.XS)
        foot_lay.addLayout(self.pag_layout)

        layout.addWidget(footer_bar)

    def set_data(self, rows: list[dict]) -> None:
        self._all_rows = rows
        self._total_entries = len(rows)
        self._current_page = 1
        self._render_page()

    def _render_page(self) -> None:
        self.table.setRowCount(0)
        if not self._all_rows:
            self.table.setRowCount(1)
            empty = QTableWidgetItem("Belum ada data pengujian yang tersimpan.")
            empty.setForeground(QColor(Colors.TEXT_SECONDARY))
            self.table.setItem(0, 0, empty)
            self.table.setSpan(0, 0, 1, len(COLUMNS))
            self.info_lbl.setText("Showing 0 to 0 of 0 entries")
            self._update_pagination_buttons(1)
            return

        total_pages = max(1, (self._total_entries + self._page_size - 1) // self._page_size)
        self._current_page = min(self._current_page, total_pages)

        start_idx = (self._current_page - 1) * self._page_size
        end_idx   = min(start_idx + self._page_size, self._total_entries)
        page_rows = self._all_rows[start_idx:end_idx]

        self.table.setRowCount(len(page_rows))
        for row_idx, r in enumerate(page_rows):
            session_id = r["id"]

            # Tanggal & Waktu
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(r.get("tested_at", "—"))))

            # No. Uji (Monospace Bold Azure)
            no_uji_item = QTableWidgetItem(r.get("test_number", "—"))
            no_uji_item.setForeground(QColor(Colors.ACCENT_PRIMARY))
            mono_font = QFont(FONT_MONO)
            mono_font.setBold(True)
            no_uji_item.setFont(mono_font)
            self.table.setItem(row_idx, 1, no_uji_item)

            # No. Rangka
            self.table.setItem(row_idx, 2, QTableWidgetItem(r.get("vin", "—")))

            # Penguji
            self.table.setItem(row_idx, 3, QTableWidgetItem(r.get("inspector_name", "—")))

            # Mode
            mode_text = r.get("test_mode", "Dyno Test")
            if hasattr(mode_text, "value"):
                mode_text = mode_text.value
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(mode_text)))

            # Hasil Badge
            status_widget = QWidget()
            status_lay = QHBoxLayout(status_widget)
            status_lay.setContentsMargins(4, 4, 4, 4)
            status_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
            status_lbl = QLabel("Selesai")
            status_lbl.setObjectName("passLabel")
            status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            status_lay.addWidget(status_lbl)
            self.table.setCellWidget(row_idx, 5, status_widget)

            # Action buttons (Detail 👁 & Print 🖨)
            act_widget = QWidget()
            act_lay = QHBoxLayout(act_widget)
            act_lay.setContentsMargins(4, 4, 4, 4)
            act_lay.setSpacing(6)
            act_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

            eye_btn = QPushButton("👁")
            eye_btn.setObjectName("actionIconBtn")
            eye_btn.setFixedSize(32, 32)
            eye_btn.setToolTip("Lihat Detail")
            eye_btn.clicked.connect(lambda _, s=session_id: self.detail_requested.emit(s))

            print_btn = QPushButton("🖨")
            print_btn.setObjectName("actionIconBtn")
            print_btn.setFixedSize(32, 32)
            print_btn.setToolTip("Cetak Struk [F12]")
            print_btn.clicked.connect(lambda _, s=session_id: self.print_requested.emit(s))

            act_lay.addWidget(eye_btn)
            act_lay.addWidget(print_btn)
            self.table.setCellWidget(row_idx, 6, act_widget)

        self.info_lbl.setText(f"Showing {start_idx + 1} to {end_idx} of {self._total_entries} entries")
        self._update_pagination_buttons(total_pages)

    def _update_pagination_buttons(self, total_pages: int) -> None:
        while self.pag_layout.count():
            item = self.pag_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

        prev_btn = QPushButton("<")
        prev_btn.setObjectName("pageBtn")
        prev_btn.setEnabled(self._current_page > 1)
        prev_btn.clicked.connect(self._prev_page)
        self.pag_layout.addWidget(prev_btn)

        for p in range(1, total_pages + 1):
            p_btn = QPushButton(str(p))
            p_btn.setObjectName("pageBtn")
            p_btn.setProperty("active", p == self._current_page)
            p_btn.clicked.connect(lambda _, page=p: self._go_page(page))
            self.pag_layout.addWidget(p_btn)

        next_btn = QPushButton(">")
        next_btn.setObjectName("pageBtn")
        next_btn.setEnabled(self._current_page < total_pages)
        next_btn.clicked.connect(self._next_page)
        self.pag_layout.addWidget(next_btn)

    def _prev_page(self) -> None:
        if self._current_page > 1:
            self._current_page -= 1
            self._render_page()

    def _next_page(self) -> None:
        total_pages = (self._total_entries + self._page_size - 1) // self._page_size
        if self._current_page < total_pages:
            self._current_page += 1
            self._render_page()

    def _go_page(self, page: int) -> None:
        self._current_page = page
        self._render_page()
