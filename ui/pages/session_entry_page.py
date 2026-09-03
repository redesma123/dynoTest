"""
Halaman Registrasi Sesi Uji (Shortcut: F1).
100% Presisi DESIGN_SYSTEM.md §4.D — Layout 2 Kolom Identitas & Data Pengujian.
RULES.md: maks ~300 baris per file.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.models import TestSession, Vehicle
from database.repository import DatabaseRepository
from ui.components.session_entry.form_card_panel import FormCardPanel
from ui.styles import Colors, FONT_MONO, Spacing

HISTORY_COLUMNS = ["NO. UJI", "NO. RANGKA", "NAMA PENGUJI", "WAKTU"]


class SessionEntryPage(QWidget):
    """Widget Halaman Registrasi Uji (DESIGN_SYSTEM.md §4.D)."""

    session_started = pyqtSignal(int)
    view_all_requested = pyqtSignal()

    def __init__(self, repository: DatabaseRepository, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("appRoot")
        self._repository = repository

        self._build_ui()
        self._load_recent_sessions()

    def _build_ui(self) -> None:
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("appRoot")

        root = QVBoxLayout(content)
        root.setContentsMargins(Spacing.XXL, Spacing.XL, Spacing.XXL, Spacing.LG)
        root.setSpacing(Spacing.LG)

        title = QLabel("Registrasi Pengujian Kendaraan (KIR / Dyno)")
        title.setObjectName("pageTitle")
        root.addWidget(title)

        subtitle = QLabel("Masukkan data identitas kendaraan, penguji, dan pilih mode pengujian untuk memulai.")
        subtitle.setObjectName("pageSubtitle")
        root.addWidget(subtitle)

        self.form_card = FormCardPanel()
        self.form_card.submit_requested.connect(self._on_submit_data)
        self.form_card.history_requested.connect(self.view_all_requested.emit)
        root.addWidget(self.form_card)

        root.addWidget(self._build_history_card())
        root.addStretch(1)

        scroll.setWidget(content)
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)

    def _build_history_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("tableCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header_bar = QFrame()
        header_bar.setObjectName("historyHeaderBar")
        header_layout = QHBoxLayout(header_bar)
        header_layout.setContentsMargins(Spacing.LG, Spacing.MD, Spacing.LG, Spacing.MD)

        header_title = QLabel("Uji Terakhir")
        header_title.setObjectName("historyHeader")
        header_layout.addWidget(header_title)

        layout.addWidget(header_bar)

        self.history_table = QTableWidget()
        self.history_table.setObjectName("historyTable")
        self.history_table.setColumnCount(len(HISTORY_COLUMNS))
        self.history_table.setHorizontalHeaderLabels(HISTORY_COLUMNS)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.history_table.setShowGrid(False)
        self.history_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.history_table.setFixedHeight(180)

        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.history_table)
        return card

    def _on_submit_data(self, data: dict) -> None:
        try:
            vehicle = Vehicle(
                vin=data["vin"],
                test_number=data["test_number"],
                license_plate=data.get("license_plate", ""),
                vehicle_category=data.get("vehicle_category", "Roda 2"),
                brand_model=data.get("brand_model", ""),
                engine_capacity_cc=150,
                vehicle_weight_kg=data.get("vehicle_weight_kg", 150.0),
            )
            self._repository.save_vehicle(vehicle)

            session = TestSession(
                vin=data["vin"],
                inspector_name=data["inspector_name"],
                test_mode=data["test_mode"],
                notes=data.get("notes", ""),
            )
            session_id = self._repository.create_test_session(session)
        except Exception as exc:  # noqa: BLE001
            self.form_card.error_label.setText(f"Gagal menyimpan sesi: {exc}")
            self.form_card.error_label.setVisible(True)
            return

        self.form_card.clear_form()
        self._load_recent_sessions()
        self.session_started.emit(session_id)

    def cancel_entry(self) -> None:
        self.form_card.clear_form()

    def _load_recent_sessions(self, limit: int = 5) -> None:
        rows = self._repository.get_recent_sessions(limit=limit)
        self.history_table.setRowCount(0)

        if not rows:
            self.history_table.setRowCount(1)
            empty_item = QTableWidgetItem("Belum ada riwayat pengujian.")
            empty_item.setForeground(QColor(Colors.TEXT_SECONDARY))
            self.history_table.setItem(0, 0, empty_item)
            self.history_table.setSpan(0, 0, 1, len(HISTORY_COLUMNS))
            return

        self.history_table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            no_uji_item = QTableWidgetItem(row["test_number"])
            no_uji_item.setForeground(QColor(Colors.ACCENT_PRIMARY))
            mono_font = QFont(FONT_MONO)
            mono_font.setBold(True)
            no_uji_item.setFont(mono_font)

            self.history_table.setItem(row_index, 0, no_uji_item)
            self.history_table.setItem(row_index, 1, QTableWidgetItem(row["vin"]))
            self.history_table.setItem(row_index, 2, QTableWidgetItem(row["inspector_name"]))
            self.history_table.setItem(row_index, 3, QTableWidgetItem(str(row["tested_at"])))
