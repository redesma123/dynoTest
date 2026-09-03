"""
DynoWeatherPanel — Panel Kiri untuk DynoTestPage (Kondisi Lingkungan & Tare).
Extracted to respect RULES.md §2 (max ~300 lines per file).
"""

from PyQt6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout
from ui.styles import Spacing


def _lbl(text: str, obj_name: str) -> QLabel:
    l = QLabel(text)
    l.setObjectName(obj_name)
    return l


def _divider() -> QFrame:
    f = QFrame()
    f.setObjectName("divider")
    return f


def _weather_row(label: str, value: str) -> QLabel:
    lbl = QLabel(f"{label}  <b>{value}</b>")
    lbl.setObjectName("weatherRow")
    return lbl


class DynoWeatherPanel(QFrame):
    """Panel Kondisi Lingkungan dan tombol Zero/Tare."""

    def __init__(self, on_tare_slot, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("sidePanel")
        self.setFixedWidth(175)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        lay.setSpacing(Spacing.SM)

        lay.addWidget(_lbl("KONDISI LINGKUNGAN", "sectionTitle"))
        lay.addWidget(_divider())
        lay.addWidget(_weather_row("🌡 Suhu", "28 °C"))
        lay.addWidget(_weather_row("⊿ Tekanan", "1013 mbar"))
        lay.addWidget(_weather_row("💧 Kelembaban", "65 %"))
        lay.addWidget(_weather_row("∂ Faktor DIN", "0.998"))
        lay.addStretch(1)

        tare = QPushButton("Zero / Tare  (F9)")
        tare.setObjectName("secondaryButton")
        tare.clicked.connect(on_tare_slot)
        lay.addWidget(tare)
