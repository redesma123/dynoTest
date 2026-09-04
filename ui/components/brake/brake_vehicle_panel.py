"""
BrakeVehiclePanel — Panel Kiri untuk BrakeTestPage (Data Kendaraan & Indikator Siklus).
Extracted to respect RULES.md §2 (max ~300 lines per file).
"""

from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout
from ui.components.common.factory import create_divider, create_label
from ui.styles import Spacing


class BrakeVehiclePanel(QFrame):
    """Panel Data Kendaraan dan Indikator 4-Fase Siklus Pengereman."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("sidePanel")
        self.setFixedWidth(220)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        lay.setSpacing(Spacing.SM)

        lay.addWidget(create_label("DATA KENDARAAN", "sectionTitle"))
        lay.addWidget(create_divider())

        def _info_row(label: str, default: str) -> QLabel:
            lay.addWidget(create_label(label, "fieldLabel"))
            val = QLabel(default)
            val.setObjectName("weatherRow")
            lay.addWidget(val)
            return val

        self.lbl_test_number = _info_row("No. Uji", "—")
        self.lbl_vin         = _info_row("No. Rangka", "—")
        self.lbl_weight      = _info_row("Bobot Uji", "—")

        lay.addSpacing(Spacing.SM)
        lay.addWidget(create_label("SIKLUS", "sectionTitle"))
        lay.addWidget(create_divider())

        self.cycle_labels: list[QLabel] = []
        cycle_names = ["Akselerasi", "Kec. Stabil", "Pengereman", "Berhenti"]
        for name in cycle_names:
            lbl_cycle = QLabel(f"○  {name}")
            lbl_cycle.setObjectName("cycleInactive")
            lay.addWidget(lbl_cycle)
            self.cycle_labels.append(lbl_cycle)

        lay.addStretch(1)

    def update_vehicle_info(self, test_number: str, vin: str, weight_kg: float) -> None:
        self.lbl_test_number.setText(test_number or "—")
        self.lbl_vin.setText(vin or "—")
        self.lbl_weight.setText(f"{weight_kg:.0f} kg")

    def set_cycle_step(self, active_idx: int) -> None:
        icons     = ["○", "○", "○", "○"]
        names     = ["Akselerasi", "Kec. Stabil", "Pengereman", "Berhenti"]
        obj_names = ["cycleInactive"] * 4

        for i in range(active_idx):
            icons[i]     = "✓"
            obj_names[i] = "cycleDone"
        icons[active_idx]     = "●"
        obj_names[active_idx] = "cycleActive"

        for i, lbl in enumerate(self.cycle_labels):
            lbl.setText(f"{icons[i]}  {names[i]}")
            lbl.setObjectName(obj_names[i])
            lbl.style().unpolish(lbl)
            lbl.style().polish(lbl)

    def reset_cycle_display(self) -> None:
        names = ["Akselerasi", "Kec. Stabil", "Pengereman", "Berhenti"]
        for i, lbl in enumerate(self.cycle_labels):
            lbl.setText(f"○  {names[i]}")
            lbl.setObjectName("cycleInactive")
            lbl.style().unpolish(lbl)
            lbl.style().polish(lbl)
