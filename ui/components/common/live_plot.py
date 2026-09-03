"""
LiveChartWidget & BrakeChartWidget — Realtime curve plot berbasis pyqtgraph.

Acuan:
- DESIGN_SYSTEM.md §5.3 (LiveChartWidget)
- DESIGN_SYSTEM.md §4.C (BrakeChartWidget)
"""

from collections import deque
import pyqtgraph as pg
from ui.styles import Colors

_MAX_POINTS = 300


class LiveChartWidget(pg.PlotWidget):
    """Dual-line rolling plot: HP (Crimson) & Torque (Azure) vs Time (s)."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._t:      deque[float] = deque(maxlen=_MAX_POINTS)
        self._hp:     deque[float] = deque(maxlen=_MAX_POINTS)
        self._torque: deque[float] = deque(maxlen=_MAX_POINTS)
        self._frozen = False
        self._setup()

    def _setup(self) -> None:
        self.setBackground(Colors.BG_SURFACE)
        self.setLabel("left",   "Power (HP) / Torque (Nm)", color=Colors.TEXT_SECONDARY, size="10pt")
        self.setLabel("bottom", "Time (s)",                 color=Colors.TEXT_SECONDARY, size="10pt")
        self.showGrid(x=True, y=True, alpha=0.25)
        for axis in ("left", "bottom"):
            self.getAxis(axis).setPen(pg.mkPen(Colors.BORDER_SUBTLE))
            self.getAxis(axis).setTextPen(pg.mkPen(Colors.TEXT_SECONDARY))

        legend = self.addLegend(offset=(10, 10))
        legend.setLabelTextColor(Colors.TEXT_PRIMARY)

        self._hp_curve = self.plot(
            [], [],
            pen=pg.mkPen(color=Colors.ACCENT_MAGENTA, width=2.5),
            name="Horsepower (HP)",
        )
        self._nm_curve = self.plot(
            [], [],
            pen=pg.mkPen(color=Colors.ACCENT_PRIMARY, width=2.5),
            name="Torque (Nm)",
        )

    def append_data(self, time_s: float, hp: float, torque_nm: float) -> None:
        if self._frozen:
            return
        self._t.append(time_s)
        self._hp.append(hp)
        self._torque.append(torque_nm)
        t_list = list(self._t)
        self._hp_curve.setData(t_list, list(self._hp))
        self._nm_curve.setData(t_list, list(self._torque))

    def clear_data(self) -> None:
        self._t.clear(); self._hp.clear(); self._torque.clear()
        self._frozen = False
        self._hp_curve.setData([], [])
        self._nm_curve.setData([], [])

    def set_frozen(self, frozen: bool) -> None:
        self._frozen = frozen


class BrakeChartWidget(pg.PlotWidget):
    """Single-line rolling chart: Gaya Pengereman (N) vs Waktu (s)."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._t:     deque[float] = deque(maxlen=_MAX_POINTS)
        self._force: deque[float] = deque(maxlen=_MAX_POINTS)
        self._frozen = False
        self._setup()

    def _setup(self) -> None:
        self.setBackground(Colors.BG_SURFACE)
        self.setLabel("left",   "Gaya Rem (N)", color=Colors.TEXT_SECONDARY, size="10pt")
        self.setLabel("bottom", "Waktu (s)",    color=Colors.TEXT_SECONDARY, size="10pt")
        self.showGrid(x=True, y=True, alpha=0.25)
        for axis in ("left", "bottom"):
            self.getAxis(axis).setPen(pg.mkPen(Colors.BORDER_SUBTLE))
            self.getAxis(axis).setTextPen(pg.mkPen(Colors.TEXT_SECONDARY))
        legend = self.addLegend(offset=(10, 10))
        legend.setLabelTextColor(Colors.TEXT_PRIMARY)
        self._force_curve = self.plot(
            [], [],
            pen=pg.mkPen(color=Colors.ACCENT_PRIMARY, width=2.5),
            name="Gaya Rem (N)",
        )

    def append_data(self, time_s: float, force_n: float) -> None:
        if self._frozen:
            return
        self._t.append(time_s)
        self._force.append(force_n)
        self._force_curve.setData(list(self._t), list(self._force))

    def clear_data(self) -> None:
        self._t.clear(); self._force.clear()
        self._frozen = False
        self._force_curve.setData([], [])

    def set_frozen(self, frozen: bool) -> None:
        self._frozen = frozen
