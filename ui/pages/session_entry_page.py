"""
Halaman Registrasi Sesi Uji (Shortcut: F1).

Acuan:
- Layout & copy    : form "Vehicle Identity" + tabel "Uji Terakhir".
- Token warna/style: ui/styles -> docs/DESIGN.md & docs/DESIGN_SYSTEM.md.
- Data layer       : database/repository.py & core/models.py
- RULES.md         : maks ~300 baris per file.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.models import TestMode, TestSession, Vehicle
from database.repository import DatabaseRepository
from ui.styles import Colors, FONT_MONO, Spacing

HISTORY_COLUMNS = ["NO. UJI", "NO. RANGKA", "NAMA PENGUJI", "WAKTU"]


def _text_icon(char: str, color: str, size: int = 16) -> QIcon:
    """Render glyph unicode jadi QIcon kecil (placeholder ikon leading input)."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QColor(color))
    font = QFont()
    font.setPixelSize(size - 3)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, char)
    painter.end()
    return QIcon(pixmap)


class SessionEntryPage(QWidget):
    """Widget halaman Registrasi Uji. Emit `session_started` saat sesi dibuat."""

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

        title = QLabel("Registrasi Uji")
        title.setObjectName("pageTitle")
        root.addWidget(title)

        subtitle = QLabel("Masukkan data kendaraan dan penguji untuk memulai pengujian dynotest.")
        subtitle.setObjectName("pageSubtitle")
        root.addWidget(subtitle)

        root.addWidget(self._build_form_card())
        root.addWidget(self._build_history_card())
        root.addStretch(1)

        scroll.setWidget(content)
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)

    def _build_form_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.MD)

        header = QLabel("IDENTITAS KENDARAAN")
        header.setObjectName("sectionTitle")
        layout.addWidget(header)

        divider = QFrame()
        divider.setObjectName("divider")
        layout.addWidget(divider)

        self.no_uji_input = self._create_field_input("#", "e.g. UJI-2026-0891")
        layout.addLayout(self._create_field("NO. UJI", self.no_uji_input))

        self.no_rangka_input = self._create_field_input("🔑", "e.g. MH3JF5110NK123456")
        layout.addLayout(self._create_field("NO. RANGKA (VIN)", self.no_rangka_input))

        self.nama_penguji_input = self._create_field_input("👤", "Nama penguji aktif")
        layout.addLayout(self._create_field("NAMA PENGUJI", self.nama_penguji_input))

        self.error_label = QLabel()
        self.error_label.setObjectName("errorLabel")
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)

        action_layout = QHBoxLayout()
        action_layout.setSpacing(Spacing.MD)

        start_btn = QPushButton("MULAI PENGUJIAN")
        start_btn.setObjectName("primaryButton")
        start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        start_btn.clicked.connect(self._on_start_clicked)
        action_layout.addWidget(start_btn)

        link_btn = QPushButton("Lihat Semua Riwayat Uji →")
        link_btn.setObjectName("linkButton")
        link_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        link_btn.clicked.connect(self.view_all_requested.emit)
        action_layout.addWidget(link_btn)
        action_layout.addStretch(1)

        layout.addLayout(action_layout)
        return card

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

    def _create_field(self, label_text: str, input_widget: QLineEdit) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(Spacing.XS)
        lbl = QLabel(label_text)
        lbl.setObjectName("fieldLabel")
        layout.addWidget(lbl)
        layout.addWidget(input_widget)
        return layout

    def _create_field_input(self, icon_char: str, placeholder: str) -> QLineEdit:
        field = QLineEdit()
        field.setObjectName("fieldInput")
        field.setPlaceholderText(placeholder)
        icon = _text_icon(icon_char, Colors.TEXT_SECONDARY)
        field.addAction(icon, QLineEdit.ActionPosition.LeadingPosition)
        return field

    def _on_start_clicked(self) -> None:
        no_uji = self.no_uji_input.text().strip()
        no_rangka = self.no_rangka_input.text().strip()
        nama_penguji = self.nama_penguji_input.text().strip()

        has_error = False
        for field, value in (
            (self.no_uji_input, no_uji),
            (self.no_rangka_input, no_rangka),
            (self.nama_penguji_input, nama_penguji),
        ):
            if not value:
                field.setProperty("error", True)
                has_error = True
            else:
                field.setProperty("error", False)
            field.style().unpolish(field)
            field.style().polish(field)

        if has_error:
            self._show_error("Mohon lengkapi semua field yang ditandai merah.")
            return

        try:
            vehicle = Vehicle(
                vin=no_rangka,
                test_number=no_uji,
                license_plate="",
                vehicle_category="Roda 2",
                brand_model="",
                engine_capacity_cc=150,
                vehicle_weight_kg=150.0,
            )
            self._repository.save_vehicle(vehicle)

            session = TestSession(
                vin=no_rangka,
                inspector_name=nama_penguji,
                test_mode=TestMode.DYNO,
            )
            session_id = self._repository.create_test_session(session)
        except Exception as exc:  # noqa: BLE001
            self._show_error(f"Gagal menyimpan sesi: {exc}")
            return

        self.error_label.setVisible(False)
        self._clear_form()
        self._load_recent_sessions()
        self.session_started.emit(session_id)

    def cancel_entry(self) -> None:
        self.error_label.setVisible(False)
        self._clear_form()

    def _show_error(self, message: str) -> None:
        self.error_label.setText(message)
        self.error_label.setVisible(True)

    def _clear_form(self) -> None:
        for field in (self.no_uji_input, self.no_rangka_input, self.nama_penguji_input):
            field.clear()
            field.setProperty("error", False)
            field.style().unpolish(field)
            field.style().polish(field)

    def _load_recent_sessions(self, limit: int = 3) -> None:
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
