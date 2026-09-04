"""
BrakeEvalPanel — Panel Kanan untuk BrakeTestPage (Evaluasi Hasil & Export).
Extracted to respect RULES.md §2 (max ~300 lines per file).
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout
from core.models import EvaluationStatus
from ui.components.common.factory import create_divider, create_label
from ui.styles import Spacing


class BrakeEvalPanel(QFrame):
    """Panel Evaluasi Hasil dan Tombol Export Laporan."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("sidePanel")
        self.setFixedWidth(210)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        lay.setSpacing(Spacing.SM)

        lay.addWidget(create_label("EVALUASI HASIL", "sectionTitle"))
        lay.addWidget(create_divider())

        # STATUS REM
        lay.addWidget(create_label("STATUS REM", "fieldLabel"))
        self.brake_status_lbl = QLabel("● MENUNGGU")
        self.brake_status_lbl.setObjectName("pendingLabel")
        self.brake_status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.brake_status_lbl.setWordWrap(True)
        lay.addWidget(self.brake_status_lbl)

        self.brake_detail_lbl = QLabel("Efisiensi: — %\nWaktu Rem: — s  (thres ≤ 4.0 s)")
        self.brake_detail_lbl.setObjectName("weatherRow")
        self.brake_detail_lbl.setWordWrap(True)
        lay.addWidget(self.brake_detail_lbl)

        lay.addSpacing(Spacing.XS)

        # STATUS LAMPU
        lay.addWidget(create_label("STATUS LAMPU", "fieldLabel"))
        self.lux_status_lbl = QLabel("● MENUNGGU")
        self.lux_status_lbl.setObjectName("pendingLabel")
        self.lux_status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.lux_status_lbl)

        self.lux_detail_lbl = QLabel("Intensitas: — Lx")
        self.lux_detail_lbl.setObjectName("weatherRow")
        lay.addWidget(self.lux_detail_lbl)

        lay.addStretch(1)
        lay.addWidget(create_divider())

        # Export buttons (disabled -- ExportService belum diimplementasi)
        for label in [
            "CETAK STRUK  [F12]",
            "EXPORT PDF   [F11]",
            "EXPORT EXCEL [F10]",
        ]:
            btn = QPushButton(label)
            btn.setObjectName("exportButton")
            btn.setEnabled(False)
            btn.setCursor(Qt.CursorShape.ForbiddenCursor)
            lay.addWidget(btn)

    def refresh_eval_panel(self, result) -> None:
        eff    = result.braking_efficiency_pct
        b_pass = result.brake_pass_status == EvaluationStatus.PASS
        self.brake_status_lbl.setText(
            f"● LULUS ({eff:.1f}%)" if b_pass else f"● TIDAK LULUS ({eff:.1f}%)"
        )
        self.brake_status_lbl.setObjectName("passLabel" if b_pass else "failLabel")
        self.brake_status_lbl.style().unpolish(self.brake_status_lbl)
        self.brake_status_lbl.style().polish(self.brake_status_lbl)

        wkt = result.braking_time_s
        self.brake_detail_lbl.setText(
            f"Efisiensi: {eff:.1f} %\nWaktu Rem: {wkt:.2f} s  (thres ≤ 4.0 s)"
        )

        lux    = result.lux_intensity
        l_pass = result.lux_pass_status == EvaluationStatus.PASS
        self.lux_status_lbl.setText(
            f"● LULUS ({lux:,.0f} Lx)" if l_pass else f"● TIDAK LULUS ({lux:,.0f} Lx)"
        )
        self.lux_status_lbl.setObjectName("passLabel" if l_pass else "failLabel")
        self.lux_status_lbl.style().unpolish(self.lux_status_lbl)
        self.lux_status_lbl.style().polish(self.lux_status_lbl)
        self.lux_detail_lbl.setText(f"Intensitas: {lux:,.0f} Lx")

    def reset_eval_panel(self) -> None:
        for lbl in (self.brake_status_lbl, self.lux_status_lbl):
            lbl.setText("● MENUNGGU")
            lbl.setObjectName("pendingLabel")
            lbl.style().unpolish(lbl)
            lbl.style().polish(lbl)
        self.brake_detail_lbl.setText(
            "Efisiensi: — %\nWaktu Rem: — s  (thres ≤ 4.0 s)"
        )
        self.lux_detail_lbl.setText("Intensitas: — Lx")
