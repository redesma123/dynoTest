from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QDoubleSpinBox, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout
from core.models import EvaluationStatus
from ui.components.common.factory import create_divider, create_label
from ui.styles import Spacing


class BrakeEvalPanel(QFrame):
    """Panel Evaluasi Hasil dan Pengaturan Pengujian."""

    lux_start_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("sidePanel")
        self.setFixedWidth(240)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        lay.setSpacing(Spacing.SM)

        lay.addWidget(create_label("EVALUASI HASIL", "sectionTitle"))
        lay.addWidget(create_divider())

        # TARGET SPEED SETTING
        lay.addWidget(create_label("KEC. TARGET REM (KM/H)", "fieldLabel"))
        speed_row = QHBoxLayout()
        speed_row.setSpacing(Spacing.XS)
        self.target_speed_spin = QDoubleSpinBox()
        self.target_speed_spin.setRange(10.0, 120.0)
        self.target_speed_spin.setSingleStep(5.0)
        self.target_speed_spin.setValue(60.0)
        self.target_speed_spin.setSuffix(" km/h")
        self.target_speed_spin.setObjectName("fieldInput")
        speed_row.addWidget(self.target_speed_spin)
        lay.addLayout(speed_row)

        lay.addSpacing(Spacing.XS)

        # STATUS REM
        lay.addWidget(create_label("STATUS PENGEREMAN", "fieldLabel"))
        self.brake_status_lbl = QLabel("● MENUNGGU PENGUJIAN")
        self.brake_status_lbl.setObjectName("pendingLabelHero")
        self.brake_status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.brake_status_lbl.setWordWrap(True)
        lay.addWidget(self.brake_status_lbl)

        self.brake_detail_lbl = QLabel("Efisiensi: — %\nWaktu Rem: — s  (thres ≤ 4.0 s)")
        self.brake_detail_lbl.setObjectName("weatherRow")
        self.brake_detail_lbl.setWordWrap(True)
        lay.addWidget(self.brake_detail_lbl)

        lay.addSpacing(Spacing.SM)

        # STATUS LAMPU
        lay.addWidget(create_label("STATUS INTENSITAS LAMPU", "fieldLabel"))
        self.lux_status_lbl = QLabel("● MENUNGGU PENGUJIAN")
        self.lux_status_lbl.setObjectName("pendingLabelHero")
        self.lux_status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lux_status_lbl.setWordWrap(True)
        lay.addWidget(self.lux_status_lbl)

        self.lux_detail_lbl = QLabel("Intensitas: — Lx (thres ≥ 12,000 Lx)")
        self.lux_detail_lbl.setObjectName("weatherRow")
        self.lux_detail_lbl.setWordWrap(True)
        lay.addWidget(self.lux_detail_lbl)

        lay.addSpacing(Spacing.XS)
        self.lux_start_btn = QPushButton("▶  MULAI UJI LAMPU")
        self.lux_start_btn.setObjectName("luxButton")
        self.lux_start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lux_start_btn.clicked.connect(self.lux_start_requested.emit)
        lay.addWidget(self.lux_start_btn)

        lay.addStretch(1)

    def get_target_speed(self) -> float:
        return self.target_speed_spin.value()

    def refresh_eval_panel(self, result) -> None:
        eff    = result.braking_efficiency_pct
        b_pass = result.brake_pass_status == EvaluationStatus.PASS
        self.brake_status_lbl.setText(
            f"✓ LULUS ({eff:.1f}%)" if b_pass else f"✕ TIDAK LULUS ({eff:.1f}%)"
        )
        self.brake_status_lbl.setObjectName("passLabelHero" if b_pass else "failLabelHero")
        self.brake_status_lbl.style().unpolish(self.brake_status_lbl)
        self.brake_status_lbl.style().polish(self.brake_status_lbl)

        wkt = result.braking_time_s
        self.brake_detail_lbl.setText(
            f"Efisiensi: {eff:.1f} %\nWaktu Rem: {wkt:.2f} s  (thres ≤ 4.0 s)"
        )

        lux    = result.lux_intensity
        l_pass = result.lux_pass_status == EvaluationStatus.PASS
        self.lux_status_lbl.setText(
            f"✓ LULUS ({lux:,.0f} Lx)" if l_pass else f"✕ TIDAK LULUS ({lux:,.0f} Lx)"
        )
        self.lux_status_lbl.setObjectName("passLabelHero" if l_pass else "failLabelHero")
        self.lux_status_lbl.style().unpolish(self.lux_status_lbl)
        self.lux_status_lbl.style().polish(self.lux_status_lbl)
        self.lux_detail_lbl.setText(f"Intensitas: {lux:,.0f} Lx (thres ≥ 12,000 Lx)")

    def reset_eval_panel(self) -> None:
        for lbl in (self.brake_status_lbl, self.lux_status_lbl):
            lbl.setText("● MENUNGGU PENGUJIAN")
            lbl.setObjectName("pendingLabelHero")
            lbl.style().unpolish(lbl)
            lbl.style().polish(lbl)
        self.brake_detail_lbl.setText(
            "Efisiensi: — %\nWaktu Rem: — s  (thres ≤ 4.0 s)"
        )
        self.lux_detail_lbl.setText("Intensitas: — Lx (thres ≥ 12,000 Lx)")
