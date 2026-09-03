"""
BrakeCenterPanel — Panel Tengah untuk BrakeTestPage (Dual Gauge + Metric Boxes + Control Buttons).
Extracted to respect RULES.md §2 (max ~300 lines per file).
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout
from ui.components.common.gauge_widget import CircularGaugeWidget
from ui.styles import Spacing


def _metric_box(label_text: str, unit: str) -> tuple[QFrame, QLabel]:
    frame = QFrame()
    frame.setObjectName("metricBox")
    lay = QVBoxLayout(frame)
    lay.setContentsMargins(Spacing.MD, Spacing.SM, Spacing.MD, Spacing.SM)
    lay.setSpacing(2)
    top = QLabel(f"{label_text}  [{unit}]")
    top.setObjectName("metricBoxLabel")
    top.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lay.addWidget(top)
    val = QLabel("0.00")
    val.setObjectName("metricBoxValue")
    val.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lay.addWidget(val)
    return frame, val


def _action_btn(text: str, obj_name: str, slot) -> QPushButton:
    btn = QPushButton(text)
    btn.setObjectName(obj_name)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.clicked.connect(slot)
    return btn


class BrakeCenterPanel(QVBoxLayout):
    """Panel Tengah pengujian rem."""

    def __init__(self, on_start_slot, on_reset_slot, parent=None) -> None:
        super().__init__(parent)
        self.setSpacing(Spacing.SM)

        g_row = QHBoxLayout()
        g_row.setSpacing(Spacing.MD)
        self.speed_gauge = CircularGaugeWidget("ROLLER KECEPATAN", "KM/H", 0, 80, 0.70, 0.90)
        self.force_gauge = CircularGaugeWidget("GAYA REM", "N", 0, 10_000, 0.50, 0.85)
        g_row.addWidget(self.speed_gauge)
        g_row.addWidget(self.force_gauge)
        self.addLayout(g_row)

        b_row = QHBoxLayout()
        b_row.setSpacing(Spacing.SM)
        self.wkt_box, self.wkt_val = _metric_box("WAKTU REM",  "Detik")
        self.lux_box, self.lux_val = _metric_box("LUX METER",  "Lux")
        self.run_box, self.run_val = _metric_box("RUN TIME",   "s")
        b_row.addWidget(self.wkt_box)
        b_row.addWidget(self.lux_box)
        b_row.addWidget(self.run_box)
        self.addLayout(b_row)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(Spacing.MD)
        self.start_btn = _action_btn("▶  START UJI REM", "startButton", on_start_slot)
        self.reset_btn = _action_btn("↺  RESET CYCLE",   "secondaryButton", on_reset_slot)
        btn_row.addWidget(self.start_btn)
        btn_row.addWidget(self.reset_btn)
        btn_row.addStretch(1)
        self.addLayout(btn_row)

    def update_displays(
        self, speed_kmh: float, braking_force_n: float, braking_time_s: float, lux: float, run_time: float
    ) -> None:
        self.speed_gauge.set_value(speed_kmh)
        self.force_gauge.set_value(braking_force_n)
        self.wkt_val.setText(f"{braking_time_s:.2f}")
        self.lux_val.setText(f"{lux:,.0f}")
        self.run_val.setText(f"{run_time:.1f}")

    def reset_displays(self) -> None:
        self.speed_gauge.set_value(0)
        self.force_gauge.set_value(0)
        self.wkt_val.setText("0.00")
        self.lux_val.setText("0")
        self.run_val.setText("0.0")
