"""
FormCardPanel — Card Registrasi 2 Kolom (DESIGN_SYSTEM.md §4.D).
- Kolom Kiri : Identitas Kendaraan (No. Uji, VIN, No. Polisi, Jenis, Merk/Tipe)
- Kolom Kanan: Data Pengujian (Penguji, Waktu Otomatis, Mode Uji, Bobot, Catatan)
"""

from datetime import datetime
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from core.models import TestMode
from ui.styles import Colors, Spacing


def _text_icon(char: str, color: str = Colors.TEXT_SECONDARY, size: int = 16) -> QIcon:
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


def _field_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("fieldLabel")
    return lbl


def _field_input(icon_char: str, placeholder: str) -> QLineEdit:
    field = QLineEdit()
    field.setObjectName("fieldInput")
    field.setPlaceholderText(placeholder)
    field.addAction(_text_icon(icon_char), QLineEdit.ActionPosition.LeadingPosition)
    return field


class FormCardPanel(QFrame):
    """Panel Form Registrasi 2 Kolom Sejajar."""

    submit_requested = pyqtSignal(dict)    # dict data registrasi lengkap
    history_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("card")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.MD)

        title = QLabel("IDENTITAS KENDARAAN & DATA PENGUJIAN")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        divider = QFrame()
        divider.setObjectName("divider")
        layout.addWidget(divider)

        # Main 2-Column Grid Layout
        cols_row = QHBoxLayout()
        cols_row.setSpacing(Spacing.XL)

        # ── KOLOM KIRI: Identitas Kendaraan ────────────────────────────────────
        col_left = QVBoxLayout()
        col_left.setSpacing(Spacing.SM)

        self.no_uji_input = _field_input("#", "e.g. UJI-2026-0891")
        col_left.addWidget(_field_label("NOMOR UJI (KIR)"))
        col_left.addWidget(self.no_uji_input)

        self.no_rangka_input = _field_input("🔑", "e.g. MH3JF5110NK123456")
        col_left.addWidget(_field_label("NOMOR RANGKA (VIN)"))
        col_left.addWidget(self.no_rangka_input)

        self.no_polisi_input = _field_input("🚘", "e.g. B 1234 ABC")
        col_left.addWidget(_field_label("NOMOR POLISI"))
        col_left.addWidget(self.no_polisi_input)

        col_left.addWidget(_field_label("JENIS KENDARAAN"))
        self.jenis_combo = QComboBox()
        self.jenis_combo.setObjectName("filterCombo")
        self.jenis_combo.addItems(["Roda 2", "Roda 4", "Bus", "Truk"])
        col_left.addWidget(self.jenis_combo)

        self.merk_tipe_input = _field_input("🏍", "e.g. Honda Vario 150")
        col_left.addWidget(_field_label("MERK & TIPE"))
        col_left.addWidget(self.merk_tipe_input)

        cols_row.addLayout(col_left, 1)

        # ── KOLOM KANAN: Data Pengujian ───────────────────────────────────────
        col_right = QVBoxLayout()
        col_right.setSpacing(Spacing.SM)

        self.nama_penguji_input = _field_input("👤", "Nama penguji aktif")
        col_right.addWidget(_field_label("NAMA PENGUJI"))
        col_right.addWidget(self.nama_penguji_input)

        col_right.addWidget(_field_label("TANGGAL & JAM"))
        self.timestamp_lbl = QLabel(datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.timestamp_lbl.setObjectName("weatherRow")
        self.timestamp_lbl.setStyleSheet("padding: 8px 12px; background-color: #F1F5F9; border-radius: 8px; font-weight: 600;")
        col_right.addWidget(self.timestamp_lbl)

        col_right.addWidget(_field_label("MODE UJI"))
        mode_box = QHBoxLayout()
        mode_box.setSpacing(Spacing.MD)
        self.mode_group = QButtonGroup(self)

        self.rb_dyno = QRadioButton("Dyno Test")
        self.rb_dyno.setChecked(True)
        self.rb_brake = QRadioButton("Brake Test")
        self.rb_combined = QRadioButton("Lengkap (Combined)")

        self.mode_group.addButton(self.rb_dyno, 1)
        self.mode_group.addButton(self.rb_brake, 2)
        self.mode_group.addButton(self.rb_combined, 3)

        mode_box.addWidget(self.rb_dyno)
        mode_box.addWidget(self.rb_brake)
        mode_box.addWidget(self.rb_combined)
        col_right.addLayout(mode_box)

        self.bobot_input = _field_input("⚖", "150.0")
        self.bobot_input.setText("150.0")
        col_right.addWidget(_field_label("BOBOT UJI (kg)"))
        col_right.addWidget(self.bobot_input)

        self.catatan_input = _field_input("📝", "Catatan khusus pengujian (opsional)")
        col_right.addWidget(_field_label("CATATAN KHUSUS"))
        col_right.addWidget(self.catatan_input)

        cols_row.addLayout(col_right, 1)
        layout.addLayout(cols_row)

        # Error Label
        self.error_label = QLabel()
        self.error_label.setObjectName("errorLabel")
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)

        # Action Buttons Row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(Spacing.MD)

        start_btn = QPushButton("▶  MULAI PENGUJIAN")
        start_btn.setObjectName("primaryButton")
        start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        start_btn.clicked.connect(self._on_submit)
        btn_row.addWidget(start_btn)

        link_btn = QPushButton("🔍 Cari / Lihat Semua Riwayat Uji →")
        link_btn.setObjectName("linkButton")
        link_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        link_btn.clicked.connect(self.history_requested.emit)
        btn_row.addWidget(link_btn)
        btn_row.addStretch(1)

        layout.addLayout(btn_row)

    def _on_submit(self) -> None:
        no_uji = self.no_uji_input.text().strip()
        no_rangka = self.no_rangka_input.text().strip()
        penguji = self.nama_penguji_input.text().strip()

        has_error = False
        for field, value in (
            (self.no_uji_input, no_uji),
            (self.no_rangka_input, no_rangka),
            (self.nama_penguji_input, penguji),
        ):
            if not value:
                field.setProperty("error", True)
                has_error = True
            else:
                field.setProperty("error", False)
            field.style().unpolish(field)
            field.style().polish(field)

        if has_error:
            self.error_label.setText("Mohon lengkapi field wajib: No. Uji, No. Rangka, dan Nama Penguji.")
            self.error_label.setVisible(True)
            return

        try:
            bobot_val = float(self.bobot_input.text().strip() or "150.0")
        except ValueError:
            bobot_val = 150.0

        if self.rb_brake.isChecked():
            test_mode = TestMode.BRAKE
        elif self.rb_combined.isChecked():
            test_mode = TestMode.COMBINED
        else:
            test_mode = TestMode.DYNO

        data = {
            "test_number": no_uji,
            "vin": no_rangka,
            "license_plate": self.no_polisi_input.text().strip(),
            "vehicle_category": self.jenis_combo.currentText(),
            "brand_model": self.merk_tipe_input.text().strip(),
            "inspector_name": penguji,
            "test_mode": test_mode,
            "vehicle_weight_kg": bobot_val,
            "notes": self.catatan_input.text().strip(),
        }

        self.error_label.setVisible(False)
        self.submit_requested.emit(data)

    def clear_form(self) -> None:
        self.no_uji_input.clear()
        self.no_rangka_input.clear()
        self.no_polisi_input.clear()
        self.merk_tipe_input.clear()
        self.nama_penguji_input.clear()
        self.bobot_input.setText("150.0")
        self.catatan_input.clear()
        self.error_label.setVisible(False)
        self.rb_dyno.setChecked(True)
