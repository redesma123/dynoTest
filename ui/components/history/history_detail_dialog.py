"""
HistoryDetailDialog — Modal dialog ringkasan & detail pengujian sesi.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from database.repository import DatabaseRepository
from ui.styles import Colors, Spacing


def _lbl(text: str, obj_name: str) -> QLabel:
    l = QLabel(text)
    l.setObjectName(obj_name)
    return l


def _row(label: str, val: str) -> QHBoxLayout:
    lay = QHBoxLayout()
    lbl1 = QLabel(label)
    lbl1.setObjectName("fieldLabel")
    lbl2 = QLabel(val)
    lbl2.setObjectName("weatherRow")
    lbl2.setAlignment(Qt.AlignmentFlag.AlignRight)
    lay.addWidget(lbl1)
    lay.addWidget(lbl2)
    return lay


class HistoryDetailDialog(QDialog):
    """Dialog detail pengujian kendaraan."""

    def __init__(self, repository: DatabaseRepository, session_id: int, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("detailDialog")
        self.setWindowTitle(f"Detail Pengujian Sesi #{session_id}")
        self.resize(480, 520)

        self._repo = repository
        self._session_id = session_id

        self._build_ui()
        self._load_data()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        root.setSpacing(Spacing.MD)

        title = QLabel(f"Detail Sesi #{self._session_id}")
        title.setObjectName("sectionTitle")
        root.addWidget(title)

        card = QFrame()
        card.setObjectName("sidePanel")
        self.card_lay = QVBoxLayout(card)
        self.card_lay.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        self.card_lay.setSpacing(Spacing.SM)
        root.addWidget(card, 1)

        close_btn = QPushButton("Tutup")
        close_btn.setObjectName("secondaryButton")
        close_btn.clicked.connect(self.accept)
        root.addWidget(close_btn, 0, Qt.AlignmentFlag.AlignRight)

    def _load_data(self) -> None:
        session = self._repo.get_test_session(self._session_id)
        if not session:
            self.card_lay.addWidget(_lbl("Sesi tidak ditemukan.", "errorLabel"))
            return

        vehicle = self._repo.get_vehicle_by_vin(session.vin)
        no_uji = vehicle.test_number if vehicle else "—"
        weight = f"{vehicle.vehicle_weight_kg:.0f} kg" if vehicle else "—"

        self.card_lay.addLayout(_row("No. Uji", no_uji))
        self.card_lay.addLayout(_row("No. Rangka", session.vin))
        self.card_lay.addLayout(_row("Nama Penguji", session.inspector_name))
        self.card_lay.addLayout(_row("Bobot Uji", weight))
        self.card_lay.addLayout(_row("Mode", session.test_mode.value if session.test_mode else "—"))
        self.card_lay.addLayout(_row("Waktu Uji", str(session.tested_at)))

        # Results summary
        if session.dyno_result:
            dr = session.dyno_result
            self.card_lay.addSpacing(Spacing.SM)
            self.card_lay.addWidget(_lbl("HASIL DYNO TEST", "sectionTitle"))
            self.card_lay.addLayout(_row("Peak Power", f"{dr.max_power_hp:.2f} HP"))
            self.card_lay.addLayout(_row("Peak Torque", f"{dr.max_torque_nm:.1f} Nm"))
            self.card_lay.addLayout(_row("Top Speed", f"{dr.max_speed_kmh:.1f} km/h"))

        if session.brake_result:
            br = session.brake_result
            self.card_lay.addSpacing(Spacing.SM)
            self.card_lay.addWidget(_lbl("HASIL BRAKE TEST", "sectionTitle"))
            self.card_lay.addLayout(_row("Gaya Rem Puncak", f"{br.peak_braking_force_n:.0f} N"))
            self.card_lay.addLayout(_row("Waktu Rem", f"{br.braking_time_s:.2f} s"))
            self.card_lay.addLayout(_row("Efisiensi Rem", f"{br.braking_efficiency_pct:.1f} %"))
            self.card_lay.addLayout(_row("Intensitas Lampu", f"{br.lux_intensity:,.0f} Lx"))
            self.card_lay.addLayout(_row("Status", br.overall_status.value if br.overall_status else "—"))

        self.card_lay.addStretch(1)
