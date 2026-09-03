"""
Top Navigation Bar — header persisten di semua halaman.

Acuan: docs/DESIGN_SYSTEM.md Bagian 4.A "Top Navigation Bar (Header)".
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton

from ui.styles import Spacing

NAV_TABS = [
    ("registrasi", "Registrasi", "F1"),
    ("dyno", "Dyno Test", "F2"),
    ("brake", "Brake Test", "F3"),
    ("riwayat", "Riwayat", "F4"),
    ("setting", "Setting", "F5"),
]


class TopNavBar(QFrame):
    """Header navigasi. Emit `tab_requested(key)` saat sebuah tab diklik/ditekan."""

    tab_requested = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("topNavBar")
        self._tab_buttons: dict[str, QPushButton] = {}

        layout = QHBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, Spacing.SM, Spacing.LG, Spacing.SM)
        layout.setSpacing(Spacing.MD)

        logo = QLabel("DYNOTEST & BRAKE PRO")
        logo.setObjectName("navLogo")
        layout.addWidget(logo)

        layout.addSpacing(Spacing.LG)

        for key, label, _shortcut in NAV_TABS:
            button = QPushButton(label)
            button.setObjectName("navTab")
            button.setProperty("active", key == "registrasi")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda _checked=False, k=key: self.tab_requested.emit(k))
            self._tab_buttons[key] = button
            layout.addWidget(button)

        layout.addStretch(1)

        self.plc_badge = QLabel()
        self.plc_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.plc_badge)

        self.set_active_tab("registrasi")
        self.set_plc_status(connected=False)

    def set_active_tab(self, active_key: str) -> None:
        """Set state visual tab aktif (tidak mengubah widget yang ditampilkan)."""
        for key, button in self._tab_buttons.items():
            button.setProperty("active", key == active_key)
            button.style().unpolish(button)
            button.style().polish(button)

    def set_plc_status(self, connected: bool, address: str = "127.0.0.1:502") -> None:
        """Perbarui badge status koneksi PLC di kanan atas."""
        if connected:
            self.plc_badge.setText(f"CONNECTED {address}")
            self.plc_badge.setObjectName("plcBadgeConnected")
        else:
            self.plc_badge.setText("DISCONNECTED")
            self.plc_badge.setObjectName("plcBadgeDisconnected")
        self.plc_badge.style().unpolish(self.plc_badge)
        self.plc_badge.style().polish(self.plc_badge)
