"""
DynoTestPage — Dashboard pengujian Dyno Test realtime (3-panel layout).

Acuan:
- Layout   : DESIGN_SYSTEM.md §4.B (Panel Kiri/Tengah/Kanan + Bottom chart)
- Widgets  : DESIGN_SYSTEM.md §5.1 CircularGaugeWidget, §5.2 DigitalMetricBox,
             §5.3 LiveChartWidget
- Keyboard : DESIGN_SYSTEM.md §6 (F9=Zero/Tare, Spasi=Start/Stop)
- Data     : core/models.py DynoTelemetry, core/physics.py DynoPeakTracker
- DB       : database/repository.py save_dyno_result()

RULES.md: maks ~300 baris per file.
"""
import math
from enum import Enum, auto

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.physics import DynoPeakTracker
from database.repository import DatabaseRepository
from ui.components.common.gauge_widget import CircularGaugeWidget
from ui.components.common.live_plot import LiveChartWidget
from ui.components.dyno.dyno_peak_panel import DynoPeakPanel
from ui.components.dyno.dyno_weather_panel import DynoWeatherPanel
from ui.styles import Spacing

_TICK_MS = 100  # 10 Hz polling rate


class _State(Enum):
    IDLE    = auto()
    RUNNING = auto()
    STOPPED = auto()


def _lbl(text: str, obj_name: str) -> QLabel:
    l = QLabel(text)
    l.setObjectName(obj_name)
    return l


def _action_btn(text: str, obj_name: str, slot) -> QPushButton:
    btn = QPushButton(text)
    btn.setObjectName(obj_name)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.clicked.connect(slot)
    return btn


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


class DynoTestPage(QWidget):
    """Halaman dashboard Dyno Test."""

    def __init__(
        self,
        repository: DatabaseRepository,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("appRoot")
        self._repo = repository
        self._session_id: int | None = None
        self._state = _State.IDLE
        self._peak: DynoPeakTracker | None = None
        self._sim_t: float = 0.0

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
        self._apply_state(_State.IDLE)

    def _build_ui(self) -> None:
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("appRoot")
        root = QVBoxLayout(content)
        root.setContentsMargins(Spacing.LG, Spacing.MD, Spacing.LG, Spacing.MD)
        root.setSpacing(Spacing.SM)

        root.addLayout(self._build_header())
        root.addLayout(self._build_main_row(), 1)
        root.addWidget(self._build_chart_card())

        scroll.setWidget(content)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _build_header(self) -> QHBoxLayout:
        row = QHBoxLayout()
        col = QVBoxLayout()
        col.setSpacing(2)
        col.addWidget(_lbl("Modul Dyno Test", "pageTitle"))
        col.addWidget(_lbl("Live Telemetry & Diagnostics Monitoring", "pageSubtitle"))
        row.addLayout(col)
        row.addStretch(1)

        dyno_btn = QPushButton("DYNO TEST")
        dyno_btn.setObjectName("modeActive")
        dyno_btn.setEnabled(False)
        brake_btn = QPushButton("BRAKE TEST")
        brake_btn.setObjectName("modeInactive")
        brake_btn.setEnabled(False)
        row.addWidget(dyno_btn)
        row.addWidget(brake_btn)
        row.addSpacing(Spacing.MD)

        self._status_badge = QLabel("● IDLE")
        self._status_badge.setObjectName("statusIdle")
        row.addWidget(self._status_badge)
        return row

    def _build_main_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(Spacing.MD)
        self._weather_panel = DynoWeatherPanel(on_tare_slot=self._on_tare)
        self._peak_panel = DynoPeakPanel()

        row.addWidget(self._weather_panel)
        row.addLayout(self._build_center_panel(), 2)
        row.addWidget(self._peak_panel)
        return row

    def _build_center_panel(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(Spacing.SM)

        g_row = QHBoxLayout()
        g_row.setSpacing(Spacing.MD)
        self._rpm_gauge   = CircularGaugeWidget("RPM",       "RPM",  0, 15000, 0.70, 0.90)
        self._speed_gauge = CircularGaugeWidget("KECEPATAN", "KM/H", 0, 200,   0.70, 0.90)
        g_row.addWidget(self._rpm_gauge)
        g_row.addWidget(self._speed_gauge)
        col.addLayout(g_row)

        b_row = QHBoxLayout()
        b_row.setSpacing(Spacing.SM)
        self._hp_box, self._hp_val = _metric_box("DAYA MESIN", "HP")
        self._nm_box, self._nm_val = _metric_box("TORSI",      "Nm")
        self._fw_box, self._fw_val = _metric_box("GAYA RODA",  "N")
        b_row.addWidget(self._hp_box)
        b_row.addWidget(self._nm_box)
        b_row.addWidget(self._fw_box)
        col.addLayout(b_row)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(Spacing.MD)
        self._start_btn = _action_btn("▶  START",        "startButton", self._on_start)
        self._stop_btn  = _action_btn("■  STOP",         "stopButton",  self._on_stop)
        self._save_btn  = _action_btn("💾  SIMPAN DATA", "saveButton",  self._on_save)
        btn_row.addWidget(self._start_btn)
        btn_row.addWidget(self._stop_btn)
        btn_row.addWidget(self._save_btn)
        btn_row.addStretch(1)
        col.addLayout(btn_row)
        return col

    def _build_chart_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("tableCard")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(Spacing.SM, Spacing.SM, Spacing.SM, Spacing.SM)
        lay.setSpacing(Spacing.XS)
        lay.addWidget(_lbl("Power / Torque Curve (Real-time)", "historyHeader"))
        self._chart = LiveChartWidget()
        self._chart.setMinimumHeight(210)
        lay.addWidget(self._chart)
        return card

    def _apply_state(self, state: _State) -> None:
        self._state = state
        is_idle    = state == _State.IDLE
        is_running = state == _State.RUNNING
        is_stopped = state == _State.STOPPED

        self._start_btn.setEnabled(is_idle or is_stopped)
        self._stop_btn.setEnabled(is_running)
        self._save_btn.setEnabled(is_stopped and self._session_id is not None)

        if is_running:
            self._status_badge.setText("● RUNNING")
            self._status_badge.setObjectName("statusRunning")
        else:
            self._status_badge.setText("● IDLE" if is_idle else "● SELESAI")
            self._status_badge.setObjectName("statusIdle")
        self._status_badge.style().unpolish(self._status_badge)
        self._status_badge.style().polish(self._status_badge)

    def _on_start(self) -> None:
        if self._state == _State.STOPPED:
            self._chart.clear_data()
            self._reset_displays()
        self._sim_t = 0.0
        self._peak = DynoPeakTracker(session_id=self._session_id or 0)
        self._timer.start()
        self._apply_state(_State.RUNNING)

    def _on_stop(self) -> None:
        self._timer.stop()
        self._chart.set_frozen(True)
        self._apply_state(_State.STOPPED)
        self._refresh_peak_panel()

    def _on_save(self) -> None:
        if self._peak is None or self._session_id is None:
            return
        try:
            self._repo.save_dyno_result(self._peak.get_result())
        except Exception as exc:  # noqa: BLE001
            print(f"[DynoTestPage] Gagal simpan: {exc}")

    def _on_tare(self) -> None:
        """Placeholder — kirim coil M2 ke Modbus saat ModbusWorker tersedia."""

    def _setup_shortcuts(self) -> None:
        QShortcut(QKeySequence("F9"), self).activated.connect(self._on_tare)
        QShortcut(QKeySequence("Space"), self).activated.connect(
            lambda: self._on_stop() if self._state == _State.RUNNING else self._on_start()
        )

    def _on_tick(self) -> None:
        self._sim_t += _TICK_MS / 1000.0
        t = self._sim_t

        rpm_ratio = min(t / 25.0, 1.0)
        rpm       = 1000 + 9000 * rpm_ratio * (1 + 0.015 * math.sin(t * 7))
        torque_nm = max(0.0, 80 * (1 - 0.6 * (rpm_ratio - 0.40) ** 2) + 3 * math.sin(t * 4))
        speed_kmh = rpm * 0.013

        power_hp, _ = self._peak.update(
            rpm=int(rpm), torque_nm=torque_nm,
            speed_kmh=speed_kmh, running_time_s=t,
        )
        wheel_force_n = torque_nm * 7.5

        self._rpm_gauge.set_value(rpm)
        self._speed_gauge.set_value(speed_kmh)
        self._hp_val.setText(f"{power_hp:.2f}")
        self._nm_val.setText(f"{torque_nm:.1f}")
        self._fw_val.setText(f"{wheel_force_n:.0f}")
        self._chart.append_data(t, power_hp, torque_nm)

    def _refresh_peak_panel(self) -> None:
        if self._peak is None:
            return
        r = self._peak
        self._peak_panel.update_peaks(r.max_power_hp, r.max_torque_nm, r.max_speed_kmh)

    def _reset_displays(self) -> None:
        self._rpm_gauge.set_value(0)
        self._speed_gauge.set_value(0)
        for lbl in (self._hp_val, self._nm_val):
            lbl.setText("0.00")
        self._fw_val.setText("0")
        self._peak_panel.reset_displays()
