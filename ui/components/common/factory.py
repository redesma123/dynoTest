"""
Factory Helper Terpusat untuk Komponen UI Sederhana (DRY Principle).
Acuan: docs/DESIGN_SYSTEM.md & docs/RULES.md
"""

from typing import Callable, Optional, Tuple
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout
from ui.styles import Spacing


def create_label(text: str, obj_name: str = "") -> QLabel:
    """Factory pembuat QLabel standar dengan objectName terkonfigurasi."""
    lbl = QLabel(text)
    if obj_name:
        lbl.setObjectName(obj_name)
    return lbl


def create_action_button(text: str, obj_name: str, slot: Optional[Callable] = None) -> QPushButton:
    """Factory pembuat QPushButton dengan kursor hand pointer & koneksi slot."""
    btn = QPushButton(text)
    btn.setObjectName(obj_name)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    if slot is not None:
        btn.clicked.connect(slot)
    return btn


def create_metric_box(label_text: str, unit: str) -> Tuple[QFrame, QLabel]:
    """Factory pembuat Kotak Metric Box Digital (QFrame & Value QLabel)."""
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


def create_divider() -> QFrame:
    """Factory pembuat QFrame garis pemisah horizontal standar."""
    f = QFrame()
    f.setObjectName("divider")
    return f
