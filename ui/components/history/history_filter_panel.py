"""
HistoryFilterPanel — Form Filter Card horizontal untuk Halaman Riwayat.
Acuan mockup & DESIGN_SYSTEM.md.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)
from ui.components.common.factory import create_label
from ui.styles import Colors, Spacing


class HistoryFilterPanel(QFrame):
    """Panel Filter Riwayat Pengujian."""

    filter_changed = pyqtSignal(dict)  # emit dict(test_number, mode, date_str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("sidePanel")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, Spacing.MD, Spacing.LG, Spacing.MD)
        layout.setSpacing(Spacing.MD)

        # 1. Field No. Uji
        col_uji = QVBoxLayout()
        col_uji.setSpacing(Spacing.XS)
        col_uji.addWidget(create_label("No. Uji", "fieldLabel"))
        self.search_input = QLineEdit()
        self.search_input.setObjectName("fieldInput")
        self.search_input.setPlaceholderText("🔍 Cari No. Uji...")
        self.search_input.returnPressed.connect(self._on_apply)
        col_uji.addWidget(self.search_input)
        layout.addLayout(col_uji, 2)

        # 2. Field Mode
        col_mode = QVBoxLayout()
        col_mode.setSpacing(Spacing.XS)
        col_mode.addWidget(create_label("Mode", "fieldLabel"))
        self.mode_combo = QComboBox()
        self.mode_combo.setObjectName("filterCombo")
        self.mode_combo.addItems(["All Modes", "Dyno Test", "Brake Test", "Combined"])
        self.mode_combo.currentIndexChanged.connect(lambda _: self._on_apply())
        col_mode.addWidget(self.mode_combo)
        layout.addLayout(col_mode, 1)

        # 3. Field Tanggal
        col_date = QVBoxLayout()
        col_date.setSpacing(Spacing.XS)
        col_date.addWidget(create_label("Tanggal", "fieldLabel"))
        self.date_input = QLineEdit()
        self.date_input.setObjectName("fieldInput")
        self.date_input.setPlaceholderText("📅 dd-mm-yyyy")
        self.date_input.returnPressed.connect(self._on_apply)
        col_date.addWidget(self.date_input)
        layout.addLayout(col_date, 1)

        # 4. Tombol Filter & Reset
        col_btn = QVBoxLayout()
        col_btn.setSpacing(Spacing.XS)
        col_btn.addWidget(create_label(" ", "fieldLabel"))  # spacer label

        btn_row = QHBoxLayout()
        btn_row.setSpacing(Spacing.SM)

        self.filter_btn = QPushButton("≡  Filter")
        self.filter_btn.setObjectName("secondaryButton")
        self.filter_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.filter_btn.clicked.connect(self._on_apply)
        btn_row.addWidget(self.filter_btn)

        self.reset_btn = QPushButton("↺  Reset")
        self.reset_btn.setObjectName("linkButton")
        self.reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reset_btn.clicked.connect(self._on_reset)
        btn_row.addWidget(self.reset_btn)

        col_btn.addLayout(btn_row)
        layout.addLayout(col_btn)

    def _on_apply(self) -> None:
        mode_val = self.mode_combo.currentText()
        filters = {
            "test_number": self.search_input.text().strip(),
            "mode": "" if mode_val == "All Modes" else mode_val,
            "date": self.date_input.text().strip(),
        }
        self.filter_changed.emit(filters)

    def _on_reset(self) -> None:
        self.search_input.clear()
        self.mode_combo.setCurrentIndex(0)
        self.date_input.clear()
        self._on_apply()
