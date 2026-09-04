"""
BrakeTestPage — Dashboard pengujian Brake Test realtime (3-panel layout).
RULES.md: maks ~300 baris per file.
"""

from enum import Enum, auto

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.physics import BrakePeakTracker, calculate_braking_torque
from database.repository import DatabaseRepository
from exporters.export_service import ExportService
from ui.components.brake.brake_center_panel import BrakeCenterPanel
from ui.components.brake.brake_eval_panel import BrakeEvalPanel
from ui.components.brake.brake_vehicle_panel import BrakeVehiclePanel
from ui.components.common.factory import create_label
from ui.components.common.live_plot import BrakeChartWidget
from ui.styles import Spacing

_TICK_MS   = 100
_LUX_CONST = 18_450.0

_PHASE1_END  = 5.0
_PHASE2_END  = 8.0
_PHASE3_END  = 11.0
_PHASE4_HOLD = 1.0


class _State(Enum):
    IDLE    = auto()
    RUNNING = auto()
    STOPPED = auto()


class BrakeTestPage(QWidget):
    """Halaman dashboard Brake Test."""

    mode_switch_requested = pyqtSignal(str)

    def __init__(
        self,
        repository: DatabaseRepository,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("appRoot")
        self._repo = repository
        self._session_id: int | None = None
        self._vehicle_weight_kg: float = 150.0
        self._state = _State.IDLE
        self._peak: BrakePeakTracker | None = None
        self._sim_t: float = 0.0
        self._phase4_start: float | None = None

        self._timer = QTimer(self)
        self._timer.setInterval(_TICK_MS)
        self._timer.timeout.connect(self._on_tick)

        self._build_ui()
        self._apply_state(_State.IDLE)
        self._setup_shortcuts()

    def load_session(self, session_id: int) -> None:
        if self._state == _State.RUNNING:
            return
        self._session_id = session_id

        session = self._repo.get_test_session(session_id)
        if session:
            vehicle = self._repo.get_vehicle_by_vin(session.vin)
            if vehicle:
                self._vehicle_weight_kg = vehicle.vehicle_weight_kg
                self._vehicle_panel.update_vehicle_info(
                    vehicle.test_number, vehicle.vin, vehicle.vehicle_weight_kg
                )

        self._apply_state(_State.IDLE)

    def _build_ui(self) -> None:
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        content = QWidget()
        content.setObjectName("appRoot")
        root = QVBoxLayout(content)
        root.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinimumSize)
        root.setContentsMargins(Spacing.LG, Spacing.MD, Spacing.LG, Spacing.MD)
        root.setSpacing(Spacing.SM)

        root.addLayout(self._build_header())
        root.addLayout(self._build_main_row(), 1)
        root.addWidget(self._build_chart_card())

        scroll.setWidget(content)
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)

    def _build_header(self) -> QHBoxLayout:
        row = QHBoxLayout()
        col = QVBoxLayout()
        col.setSpacing(2)
        col.addWidget(create_label("Modul Brake Test", "pageTitle"))
        col.addWidget(create_label("Pengujian Gaya Rem & Lampu Kendaraan", "pageSubtitle"))
        row.addLayout(col)
        row.addStretch(1)

        self._status_badge = QLabel("● IDLE")
        self._status_badge.setObjectName("statusIdle")
        row.addWidget(self._status_badge)
        return row

    def _build_main_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(Spacing.MD)
        self._vehicle_panel = BrakeVehiclePanel()
        self._center_panel  = BrakeCenterPanel(
            on_start_slot=self._on_start,
            on_reset_slot=self._on_reset,
            on_save_slot=self._on_save,
            on_excel_slot=self._on_export_excel,
            on_pdf_slot=self._on_export_pdf,
            on_receipt_slot=self._on_print_receipt,
        )
        self._eval_panel = BrakeEvalPanel()
        self._eval_panel.lux_start_requested.connect(self._on_start_lux_test)

        row.addWidget(self._vehicle_panel)
        row.addLayout(self._center_panel, 2)
        row.addWidget(self._eval_panel)
        return row

    def _build_chart_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("tableCard")
        card.setFixedHeight(272)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(Spacing.SM, Spacing.SM, Spacing.SM, Spacing.SM)
        lay.setSpacing(Spacing.XS)
        lay.addWidget(create_label("Gaya Pengereman vs Waktu (Real-time)", "historyHeader"))
        self._chart = BrakeChartWidget()
        self._chart.setFixedHeight(230)
        lay.addWidget(self._chart)
        return card

    def _apply_state(self, state: _State) -> None:
        self._state = state
        is_idle    = state == _State.IDLE
        is_running = state == _State.RUNNING
        is_stopped = state == _State.STOPPED

        self._center_panel.start_btn.setEnabled(is_idle or is_stopped)
        self._center_panel.reset_btn.setEnabled(is_running or is_stopped)
        has_result = is_stopped and (self._peak is not None)
        self._center_panel.save_btn.setEnabled(has_result and self._session_id is not None)
        self._center_panel.excel_btn.setEnabled(has_result)
        self._center_panel.pdf_btn.setEnabled(has_result)
        self._center_panel.receipt_btn.setEnabled(has_result)

        if is_running:
            self._status_badge.setText("● RUNNING")
            self._status_badge.setObjectName("statusRunning")
        else:
            self._status_badge.setText("● IDLE" if is_idle else "● SELESAI")
            self._status_badge.setObjectName("statusIdle")

        self._status_badge.style().unpolish(self._status_badge)
        self._status_badge.style().polish(self._status_badge)

        if is_idle:
            self._vehicle_panel.reset_cycle_display()
            self._eval_panel.reset_eval_panel()

    def _on_start(self) -> None:
        if self._state == _State.STOPPED:
            self._chart.clear_data()
            self._center_panel.reset_displays()
        self._sim_t = 0.0
        self._phase4_start = None
        target_spd = self._eval_panel.get_target_speed()
        self._peak = BrakePeakTracker(
            session_id=self._session_id or 0,
            vehicle_weight_kg=self._vehicle_weight_kg,
            target_speed_kmh=target_spd,
        )
        self._timer.start()
        self._apply_state(_State.RUNNING)

    def _on_start_lux_test(self) -> None:
        """Picu pengujian intensitas lampu mandiri."""
        if self._peak is not None:
            res = self._peak.get_result()
            self._eval_panel.refresh_eval_panel(res)
        else:
            QMessageBox.information(
                self,
                "Uji Lampu",
                f"Pengujian intensitas cahaya lampu aktif.\nHasil terdeteksi: {_LUX_CONST:,.0f} Lux (LULUS).",
            )

    def _on_reset(self) -> None:
        self._timer.stop()
        self._chart.clear_data()
        self._chart.set_frozen(False)
        self._center_panel.reset_displays()
        self._apply_state(_State.IDLE)

    def _auto_stop(self) -> None:
        self._timer.stop()
        self._chart.set_frozen(True)
        if self._peak is not None:
            result = self._peak.get_result()
            self._eval_panel.refresh_eval_panel(result)
        self._apply_state(_State.STOPPED)

    def _on_save(self) -> None:
        if self._peak is None or self._session_id is None:
            return
        try:
            self._repo.save_brake_result(self._peak.get_result())
            QMessageBox.information(self, "Simpan Data", "Data Brake Test berhasil disimpan.")
        except Exception as exc:  # noqa: BLE001
            print(f"[BrakeTestPage] Gagal simpan: {exc}")
            QMessageBox.critical(self, "Simpan Data", f"Gagal menyimpan data: {exc}")

    def _on_export_excel(self) -> None:
        if self._peak is None:
            QMessageBox.warning(self, "Export Excel", "Belum ada hasil uji untuk diekspor.")
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Brake Test ke Excel",
            f"Brake_Test_{self._session_id or 'Result'}.xlsx",
            "Excel Files (*.xlsx)",
        )
        if file_path:
            exporter = ExportService(self._repo)
            ok = exporter.export_brake_excel(file_path, self._peak.get_result())
            if ok:
                QMessageBox.information(self, "Export Berhasil", f"Data berhasil diekspor ke:\n{file_path}")
            else:
                QMessageBox.critical(self, "Export Gagal", "Gagal mengekspor data ke Excel.")

    def _on_export_pdf(self) -> None:
        if self._peak is None:
            QMessageBox.warning(self, "Export PDF", "Belum ada hasil uji untuk diekspor.")
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Brake Test ke PDF",
            f"Brake_Test_{self._session_id or 'Result'}.pdf",
            "PDF Files (*.pdf)",
        )
        if file_path:
            exporter = ExportService(self._repo)
            ok = exporter.export_brake_pdf(file_path, self._peak.get_result())
            if ok:
                QMessageBox.information(self, "Export Berhasil", f"Laporan PDF berhasil disimpan ke:\n{file_path}")
            else:
                QMessageBox.critical(self, "Export Gagal", "Gagal mengekspor laporan ke PDF.")

    def _on_print_receipt(self) -> None:
        if self._peak is None:
            QMessageBox.warning(self, "Cetak Struk", "Belum ada hasil uji untuk dicetak.")
            return
        session = self._repo.get_test_session(self._session_id) if self._session_id else None
        vehicle = self._repo.get_vehicle_by_vin(session.vin) if session else None
        exporter = ExportService(self._repo)
        txt = exporter.format_thermal_receipt_text(
            session=session,
            vehicle=vehicle,
            brake_result=self._peak.get_result(),
        )
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            f"Simpan Struk Pengujian Rem #{self._session_id or 'Result'}",
            f"Struk_Brake_{self._session_id or 'Result'}.txt",
            "Text Files (*.txt);;All Files (*)",
        )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(txt)
            QMessageBox.information(self, "Cetak Struk", f"Struk berhasil diekspor ke:\n{file_path}")

    def _setup_shortcuts(self) -> None:
        QShortcut(QKeySequence("F9"),    self).activated.connect(self._on_tare)
        QShortcut(QKeySequence("F10"),   self).activated.connect(self._on_export_excel)
        QShortcut(QKeySequence("F11"),   self).activated.connect(self._on_export_pdf)
        QShortcut(QKeySequence("F12"),   self).activated.connect(self._on_print_receipt)
        QShortcut(QKeySequence("Space"), self).activated.connect(self._on_space)

    def _on_space(self) -> None:
        if self._state == _State.RUNNING:
            self._on_reset()
        else:
            self._on_start()

    def _on_tare(self) -> None:
        """Placeholder — kirim coil ke Modbus saat ModbusWorker tersedia."""

    def _on_tick(self) -> None:
        self._sim_t += _TICK_MS / 1000.0
        t = self._sim_t

        target_spd = self._eval_panel.get_target_speed()
        max_rpm    = int(target_spd * 40.0)

        roller_rpm:      int   = 0
        speed_kmh:       float = 0.0
        braking_force_n: float = 0.0
        braking_time_s:  float = 0.0
        is_pedal:        bool  = False

        if t <= _PHASE1_END:
            ratio       = t / _PHASE1_END
            speed_kmh   = target_spd * ratio
            roller_rpm  = int(max_rpm * ratio)
            self._vehicle_panel.set_cycle_step(0)
        elif t <= _PHASE2_END:
            speed_kmh  = target_spd
            roller_rpm = max_rpm
            self._vehicle_panel.set_cycle_step(1)
        elif t <= _PHASE3_END:
            ratio           = (t - _PHASE2_END) / (_PHASE3_END - _PHASE2_END)
            speed_kmh       = target_spd * (1.0 - ratio)
            roller_rpm      = int(max_rpm * (1.0 - ratio))
            braking_force_n = 2800.0 * ratio
            braking_time_s  = 3.0 * ratio
            is_pedal        = True
            self._vehicle_panel.set_cycle_step(2)
        else:
            speed_kmh       = 0.0
            roller_rpm      = 0
            braking_force_n = 2800.0
            braking_time_s  = 3.0
            is_pedal        = True
            self._vehicle_panel.set_cycle_step(3)

            if self._phase4_start is None:
                self._phase4_start = t
            elif t - self._phase4_start >= _PHASE4_HOLD:
                braking_torque_nm = calculate_braking_torque(braking_force_n)
                if self._peak is not None:
                    self._peak.update(
                        roller_rpm=roller_rpm,
                        braking_force_n=braking_force_n,
                        braking_time_s=braking_time_s,
                        lux_intensity=_LUX_CONST,
                        running_time_s=t,
                        speed_kmh=speed_kmh,
                        is_pedal_pressed=is_pedal,
                    )
                self._center_panel.update_displays(
                    speed_kmh, roller_rpm, braking_force_n, braking_torque_nm, braking_time_s, _LUX_CONST, t
                )
                self._auto_stop()
                return

        braking_torque_nm = calculate_braking_torque(braking_force_n)
        if self._peak is not None:
            self._peak.update(
                roller_rpm=roller_rpm,
                braking_force_n=braking_force_n,
                braking_time_s=braking_time_s,
                lux_intensity=_LUX_CONST,
                running_time_s=t,
                speed_kmh=speed_kmh,
                is_pedal_pressed=is_pedal,
            )
        self._chart.append_data(t, braking_force_n)
        self._center_panel.update_displays(
            speed_kmh, roller_rpm, braking_force_n, braking_torque_nm, braking_time_s, _LUX_CONST, t
        )
