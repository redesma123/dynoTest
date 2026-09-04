"""
DynoPeakPanel — Panel Kanan untuk DynoTestPage (Peak Monitor).
Extracted to respect RULES.md §2 (max ~300 lines per file).
"""

from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout
from ui.components.common.factory import create_divider, create_label
from ui.styles import Spacing


def _peak_row(layout: QVBoxLayout, label: str) -> QLabel:
    layout.addWidget(create_label(label, "weatherRow"))
    val = QLabel("—")
    val.setObjectName("peakValue")
    layout.addWidget(val)
    layout.addSpacing(Spacing.XS)
    return val


class DynoPeakPanel(QFrame):
    """Panel Peak Monitor (Peak HP, Peak Torsi, Top Speed)."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("sidePanel")
        self.setFixedWidth(220)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        lay.setSpacing(Spacing.SM)

        lay.addWidget(create_label("PEAK MONITOR", "sectionTitle"))
        lay.addWidget(create_divider())
        self.peak_hp = _peak_row(lay, "Peak HP")
        self.peak_nm = _peak_row(lay, "Peak Torsi")
        self.peak_spd = _peak_row(lay, "Top Speed")
        lay.addStretch(1)

    def update_peaks(self, max_power_hp: float, max_torque_nm: float, max_speed_kmh: float) -> None:
        self.peak_hp.setText(f"{max_power_hp:.2f} HP")
        self.peak_nm.setText(f"{max_torque_nm:.1f} Nm")
        self.peak_spd.setText(f"{max_speed_kmh:.1f} km/h")

    def reset_displays(self) -> None:
        for lbl in (self.peak_hp, self.peak_nm, self.peak_spd):
            lbl.setText("—")
