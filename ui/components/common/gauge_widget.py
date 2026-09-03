"""
CircularGaugeWidget — Custom dial instrument berbasis QPainter.
Acuan: DESIGN_SYSTEM.md §5.1 (Dual Light Cockpit Dials).
"""

import math
from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QColor,
    QConicalGradient,
    QFont,
    QPainter,
    QPainterPath,
    QPen,
)
from PyQt6.QtWidgets import QWidget
from ui.styles import Colors, FONT_MONO, FONT_UI


class CircularGaugeWidget(QWidget):
    """Circular gauge dial dengan QPainter antialiased."""

    def __init__(
        self,
        title: str,
        unit: str,
        min_val: float = 0.0,
        max_val: float = 100.0,
        warn_pct: float = 0.75,
        danger_pct: float = 0.90,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._title = title
        self._unit = unit
        self._min_val = min_val
        self._max_val = max_val
        self._warn_pct = warn_pct
        self._danger_pct = danger_pct
        self._value = min_val
        self.setMinimumSize(180, 180)

    def set_value(self, value: float) -> None:
        clamped = max(self._min_val, min(self._max_val, value))
        if abs(self._value - clamped) > 1e-4:
            self._value = clamped
            self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        side = min(w, h)
        cx, cy = w / 2.0, h / 2.0
        r = (side / 2.0) * 0.90

        start_angle = 225.0
        total_span = 270.0

        ratio = (self._value - self._min_val) / (self._max_val - self._min_val)
        val_angle = start_angle - ratio * total_span

        # 1. Bezel luar
        pen_bezel = QPen(QColor(Colors.BORDER_SUBTLE), r * 0.06)
        painter.setPen(pen_bezel)
        painter.drawEllipse(QPointF(cx, cy), r * 0.92, r * 0.92)

        # 2. Track busur latar
        pen_track = QPen(QColor(Colors.BG_SURFACE_ELEVATED), r * 0.10)
        pen_track.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_track)
        rect = QRectF(cx - r * 0.85, cy - r * 0.85, r * 1.70, r * 1.70)
        painter.drawArc(rect, int((start_angle - total_span) * 16), int(total_span * 16))

        # 3. Active Arc (Cobalt Azure -> Amber -> Redline)
        arc_color = QColor(Colors.ACCENT_PRIMARY)
        if ratio >= self._danger_pct:
            arc_color = QColor(Colors.ACCENT_DANGER)
        elif ratio >= self._warn_pct:
            arc_color = QColor(Colors.ACCENT_NEEDLE)

        pen_arc = QPen(arc_color, r * 0.10)
        pen_arc.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_arc)
        if ratio > 0.001:
            painter.drawArc(rect, int(start_angle * 16), int(-ratio * total_span * 16))

        # 4. Ticks
        num_ticks = 10
        for i in range(num_ticks + 1):
            t_ratio = i / float(num_ticks)
            deg = start_angle - t_ratio * total_span
            rad = math.radians(deg)
            is_major = i % 2 == 0
            len_tick = r * (0.10 if is_major else 0.05)
            r_outer = r * 0.78
            r_inner = r_outer - len_tick

            x1 = cx + r_outer * math.cos(rad)
            y1 = cy - r_outer * math.sin(rad)
            x2 = cx + r_inner * math.cos(rad)
            y2 = cy - r_inner * math.sin(rad)

            color = Colors.ACCENT_DANGER if t_ratio >= self._danger_pct else Colors.TEXT_SECONDARY
            painter.setPen(QPen(QColor(color), 1.5 if is_major else 1.0))
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # 5. Jarum (Needle)
        rad_n = math.radians(val_angle)
        needle_len = r * 0.72
        nx = cx + needle_len * math.cos(rad_n)
        ny = cy - needle_len * math.sin(rad_n)
        px1 = cx + (r * 0.08) * math.cos(rad_n + math.pi / 2.0)
        py1 = cy - (r * 0.08) * math.sin(rad_n + math.pi / 2.0)
        px2 = cx + (r * 0.08) * math.cos(rad_n - math.pi / 2.0)
        py2 = cy - (r * 0.08) * math.sin(rad_n - math.pi / 2.0)

        path = QPainterPath()
        path.moveTo(QPointF(px1, py1))
        path.lineTo(QPointF(nx, ny))
        path.lineTo(QPointF(px2, py2))
        path.closeSubpath()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(Colors.ACCENT_NEEDLE))
        painter.drawPath(path)

        # 6. Center Hub Bezel (Deep Slate Navy)
        hub_r = r * 0.38
        painter.setBrush(QColor(Colors.BG_METRIC_BOX))
        painter.setPen(QPen(QColor(Colors.BORDER_SUBTLE), 1.5))
        painter.drawEllipse(QPointF(cx, cy), hub_r, hub_r)

        # 7. Angka Hero Di Dalam Hub
        font_num = QFont(FONT_MONO)
        font_num.setPixelSize(int(hub_r * 0.65))
        font_num.setBold(True)
        painter.setFont(font_num)
        painter.setPen(QColor(Colors.TEXT_ON_DARK))

        val_str = f"{int(round(self._value)):,}" if self._max_val >= 1000 else f"{self._value:.1f}"
        painter.drawText(
            QRectF(cx - hub_r, cy - hub_r * 0.4, hub_r * 2, hub_r * 0.8),
            Qt.AlignmentFlag.AlignCenter,
            val_str,
        )

        font_unit = QFont(FONT_UI)
        font_unit.setPixelSize(int(hub_r * 0.32))
        painter.setFont(font_unit)
        painter.setPen(QColor(Colors.TEXT_UNIT_ON_DARK))
        painter.drawText(
            QRectF(cx - hub_r, cy + hub_r * 0.3, hub_r * 2, hub_r * 0.5),
            Qt.AlignmentFlag.AlignCenter,
            self._unit,
        )

        # 8. Judul di bagian bawah dial
        font_title = QFont(FONT_UI)
        font_title.setPixelSize(int(r * 0.12))
        font_title.setBold(True)
        painter.setFont(font_title)
        painter.setPen(QColor(Colors.TEXT_PRIMARY))
        painter.drawText(
            QRectF(cx - r, cy + r * 0.52, r * 2, r * 0.35),
            Qt.AlignmentFlag.AlignCenter,
            self._title,
        )
        painter.end()
