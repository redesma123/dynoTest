"""
Halaman Registrasi Sesi Uji (Shortcut: F1).

Acuan:
- Layout & copy    : desain UI yang dikirim user (form "Vehicle Identity"
                      + tabel "Uji Terakhir").
- Token warna/style: ui/styles.py -> docs/DESIGN.md & docs/DESIGN_SYSTEM.md.
- Data layer       : database/repository.py (DatabaseRepository) & core/models.py
                      (Vehicle, TestSession, TestMode) -> docs/SCHEMA.md.
- RULES.md         : parameterized queries sudah ditangani DatabaseRepository,
                      tombol aksi minimal 44x44 px, tanpa pure #FFFFFF/#000000.

Halaman ini TIDAK membuat koneksi/skema DB sendiri. `DatabaseRepository`
diinjeksikan dari luar (lihat ui/main_window.py) supaya satu koneksi/skema
dipakai bersama oleh semua halaman (Dyno/Brake/Riwayat) nantinya.
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
    """Render glyph unicode jadi QIcon kecil (placeholder ikon leading input).

    Placeholder tanpa dependency aset SVG baru. Untuk produksi sebaiknya
    diganti ikon vektor resmi (mis. Lucide) yang konsisten dengan style guide.
    """
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

    session_started = pyqtSignal(int)  # membawa session_id (test_sessions.id)
    view_all_requested = pyqtSignal()

    def __init__(self, repository: DatabaseRepository, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("appRoot")
        self._repository = repository

        self._build_ui()
        self._load_recent_sessions()

    # ------------------------------------------------------------------ UI
    def _build_ui(self) -> None:
        # QScrollArea sebagai root agar konten tidak overlap saat window diperkecil.
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Widget konten di dalam scroll area.
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
        root.addWidget(self._build_footer())

        scroll.setWidget(content)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _build_form_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.MD)

        section_title = QLabel("VEHICLE IDENTITY")
        section_title.setObjectName("sectionTitle")
        layout.addWidget(section_title)

        divider = QFrame()
        divider.setObjectName("divider")
        layout.addWidget(divider)

        row = QHBoxLayout()
        row.setSpacing(Spacing.LG)
        self.no_uji_input = self._make_field(row, "NO. UJI", "Masukkan Nomor Uji", "#")
        self.no_rangka_input = self._make_field(row, "NO. RANGKA", "Masukkan Nomor Rangka", "▦")
        layout.addLayout(row)

        name_row = QHBoxLayout()
        self.nama_penguji_input = self._make_field(name_row, "NAMA PENGUJI", "Masukkan Nama Penguji", "☺")
        layout.addLayout(name_row)

        self.error_label = QLabel("")
        self.error_label.setObjectName("errorLabel")
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)

        action_row = QHBoxLayout()
        action_row.addStretch(1)
        self.mulai_button = QPushButton("MULAI  \u2192")
        self.mulai_button.setObjectName("primaryButton")
        self.mulai_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mulai_button.clicked.connect(self._on_mulai_clicked)
        action_row.addWidget(self.mulai_button)
        layout.addLayout(action_row)

        return card

    def _make_field(self, row_layout: QHBoxLayout, label_text: str, placeholder: str, icon_char: str) -> QLineEdit:
        container = QVBoxLayout()
        container.setSpacing(Spacing.XS + 2)

        label = QLabel(label_text)
        label.setObjectName("fieldLabel")
        container.addWidget(label)

        field = QLineEdit()
        field.setObjectName("fieldInput")
        field.setPlaceholderText(placeholder)
        field.addAction(_text_icon(icon_char, Colors.TEXT_SECONDARY), QLineEdit.ActionPosition.LeadingPosition)
        field.returnPressed.connect(self._on_mulai_clicked)
        container.addWidget(field)

        row_layout.addLayout(container, 1)
        return field

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

        header_label = QLabel("Uji Terakhir")
        header_label.setObjectName("historyHeader")
        header_layout.addWidget(header_label)
        header_layout.addStretch(1)

        view_all_button = QPushButton("Lihat Semua")
        view_all_button.setObjectName("linkButton")
        view_all_button.setCursor(Qt.CursorShape.PointingHandCursor)
        view_all_button.clicked.connect(self.view_all_requested.emit)
        header_layout.addWidget(view_all_button)

        layout.addWidget(header_bar)

        self.history_table = QTableWidget(0, len(HISTORY_COLUMNS))
        self.history_table.setObjectName("historyTable")
        self.history_table.setHorizontalHeaderLabels(HISTORY_COLUMNS)
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.history_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.history_table.setShowGrid(False)
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.history_table.setMinimumHeight(180)
        layout.addWidget(self.history_table)

        return card

    def _build_footer(self) -> QLabel:
        footer = QLabel("AUTO-TECH SYSTEMS V4.2.1")
        footer.setObjectName("footerLabel")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return footer

    # -------------------------------------------------------------- Logic
    def _on_mulai_clicked(self) -> None:
        no_uji = self.no_uji_input.text().strip()
        no_rangka = self.no_rangka_input.text().strip()
        nama_penguji = self.nama_penguji_input.text().strip()

        missing = [
            field
            for field, value in (
                (self.no_uji_input, no_uji),
                (self.no_rangka_input, no_rangka),
                (self.nama_penguji_input, nama_penguji),
            )
            if not value
        ]
        for field in (self.no_uji_input, self.no_rangka_input, self.nama_penguji_input):
            field.setProperty("error", field in missing)
            field.style().unpolish(field)
            field.style().polish(field)

        if missing:
            self._show_error("Semua field wajib diisi sebelum memulai pengujian.")
            return

        # vehicles.test_number bersifat UNIQUE tapi tidak termasuk kunci ON
        # CONFLICT di save_vehicle() (yang konfliknya di kolom vin) -> cek
        # manual dulu supaya tidak menabrak UNIQUE constraint di database.
        existing_vehicle = self._repository.get_vehicle_by_test_number(no_uji)
        if existing_vehicle and existing_vehicle.vin != no_rangka:
            self._show_error(f"No. Uji '{no_uji}' sudah digunakan kendaraan lain (VIN {existing_vehicle.vin}).")
            return

        try:
            vehicle = Vehicle(vin=no_rangka, test_number=no_uji)
            self._repository.save_vehicle(vehicle)

            session = TestSession(
                vin=no_rangka,
                inspector_name=nama_penguji,
                test_mode=TestMode.DYNO,
            )
            session_id = self._repository.create_test_session(session)
        except Exception as exc:  # noqa: BLE001 - tampilkan pesan apa adanya ke UI
            self._show_error(f"Gagal menyimpan sesi: {exc}")
            return

        self.error_label.setVisible(False)
        self._clear_form()
        self._load_recent_sessions()
        self.session_started.emit(session_id)

    def cancel_entry(self) -> None:
        """Batalkan input yang sedang diketik (dipanggil oleh shortcut `Esc`).

        Acuan: docs/DESIGN_SYSTEM.md Bagian 6 -- `Esc`: Emergency Stop /
        Batalkan Sesi Uji. Di halaman ini belum ada pengujian yang berjalan,
        jadi maknanya dipersempit ke "batalkan input form".
        """
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