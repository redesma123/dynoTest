"""
Widget-specific QSS styles for DynoTestPage & BrakeTestPage.
Extracted to respect RULES.md §2 (max ~300 lines per file).
"""


def get_widget_qss(c, spacing, font_mono: str, min_touch_target: int) -> str:
    """QSS tambahan untuk modul Dyno dan Brake test."""
    return f"""
    /* ── DynoTestPage: action buttons ── */
    QPushButton#startButton {{
        background-color: {c.ACCENT_SUCCESS};
        color: {c.TEXT_ON_DARK};
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.5px;
        border: none;
        border-radius: 8px;
        padding: 0 {spacing.LG}px;
        min-height: {min_touch_target}px;
        min-width: 110px;
    }}
    QPushButton#startButton:hover   {{ background-color: #047857; }}
    QPushButton#startButton:pressed {{ background-color: #065F46; }}
    QPushButton#startButton:disabled {{ background-color: {c.BG_SURFACE_ELEVATED}; color: {c.TEXT_SECONDARY}; }}

    QPushButton#stopButton {{
        background-color: {c.ACCENT_DANGER};
        color: {c.TEXT_ON_DARK};
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.5px;
        border: none;
        border-radius: 8px;
        padding: 0 {spacing.LG}px;
        min-height: {min_touch_target}px;
        min-width: 110px;
    }}
    QPushButton#stopButton:hover   {{ background-color: #B91C1C; }}
    QPushButton#stopButton:pressed {{ background-color: #991B1B; }}
    QPushButton#stopButton:disabled {{ background-color: {c.BG_SURFACE_ELEVATED}; color: {c.TEXT_SECONDARY}; }}

    QPushButton#saveButton {{
        background-color: {c.ACCENT_PRIMARY};
        color: {c.TEXT_ON_DARK};
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.5px;
        border: none;
        border-radius: 8px;
        padding: 0 {spacing.LG}px;
        min-height: {min_touch_target}px;
        min-width: 140px;
    }}
    QPushButton#saveButton:hover   {{ background-color: {c.ACCENT_PRIMARY_HOVER}; }}
    QPushButton#saveButton:pressed {{ background-color: {c.ACCENT_PRIMARY_PRESSED}; }}
    QPushButton#saveButton:disabled {{ background-color: {c.BG_SURFACE_ELEVATED}; color: {c.TEXT_SECONDARY}; }}

    QPushButton#secondaryButton {{
        background-color: {c.BG_SURFACE_ELEVATED};
        color: {c.TEXT_PRIMARY};
        font-size: 12px;
        font-weight: 600;
        border: 1px solid {c.BORDER_SUBTLE};
        border-radius: 8px;
        padding: 0 {spacing.MD}px;
        min-height: {min_touch_target}px;
    }}
    QPushButton#secondaryButton:hover {{ background-color: {c.BORDER_SUBTLE}; }}

    /* ── Mode toggle badges ── */
    QPushButton#modeActive {{
        background-color: {c.ACCENT_PRIMARY};
        color: {c.TEXT_ON_DARK};
        font-size: 12px;
        font-weight: 700;
        border: none;
        border-radius: 6px;
        padding: 0 {spacing.MD}px;
        min-height: 32px;
    }}
    QPushButton#modeInactive {{
        background-color: transparent;
        color: {c.TEXT_SECONDARY};
        font-size: 12px;
        font-weight: 600;
        border: 1px solid {c.BORDER_SUBTLE};
        border-radius: 6px;
        padding: 0 {spacing.MD}px;
        min-height: 32px;
    }}
    QPushButton#modeInactive:hover {{
        background-color: {c.BG_SURFACE_ELEVATED};
        color: {c.TEXT_PRIMARY};
        border-color: {c.ACCENT_PRIMARY};
    }}
    QPushButton#modeInactive:pressed {{
        background-color: {c.BORDER_SUBTLE};
    }}

    /* ── Status badges ── */
    QLabel#statusRunning {{
        background-color: {c.ACCENT_MAGENTA};
        color: {c.TEXT_ON_DARK};
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
        border-radius: 6px;
        padding: {spacing.XS}px {spacing.SM}px;
        min-height: {min_touch_target - 16}px;
    }}
    QLabel#statusIdle {{
        background-color: {c.BG_SURFACE_ELEVATED};
        color: {c.TEXT_SECONDARY};
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
        border: 1px solid {c.BORDER_SUBTLE};
        border-radius: 6px;
        padding: {spacing.XS}px {spacing.SM}px;
        min-height: {min_touch_target - 16}px;
    }}

    /* ── Side panels ── */
    QFrame#sidePanel {{
        background-color: {c.BG_SURFACE};
        border: 1px solid {c.BORDER_SUBTLE};
        border-radius: 10px;
    }}

    /* ── DigitalMetricBox (DESIGN_SYSTEM.md §5.2) ── */
    QFrame#metricBox {{
        background-color: {c.BG_METRIC_BOX};
        border: 1px solid #1E293B;
        border-radius: 8px;
    }}
    QLabel#metricBoxLabel {{
        font-size: 11px;
        font-weight: 500;
        color: {c.TEXT_UNIT_ON_DARK};
        letter-spacing: 0.5px;
    }}
    QLabel#metricBoxValue {{
        font-family: {font_mono};
        font-size: 22px;
        font-weight: 700;
        color: {c.TEXT_ON_DARK};
    }}

    /* ── Peak monitor panel ── */
    QLabel#peakValue {{
        font-family: {font_mono};
        font-size: 14px;
        font-weight: 700;
        color: {c.ACCENT_PRIMARY};
    }}
    QLabel#weatherRow {{
        font-size: 13px;
        color: {c.TEXT_SECONDARY};
    }}

    /* ── BrakeTestPage: evaluasi PASS / FAIL / PENDING badges ── */
    QLabel#passLabel {{
        background-color: {c.SUCCESS_BG};
        color: {c.ACCENT_SUCCESS};
        border: 1px solid {c.SUCCESS_BORDER};
        font-size: 13px;
        font-weight: 700;
        border-radius: 6px;
        padding: {spacing.XS}px {spacing.SM}px;
        min-height: {min_touch_target - 16}px;
    }}
    QLabel#failLabel {{
        background-color: {c.DANGER_BG};
        color: {c.ACCENT_DANGER};
        border: 1px solid {c.DANGER_BORDER};
        font-size: 13px;
        font-weight: 700;
        border-radius: 6px;
        padding: {spacing.XS}px {spacing.SM}px;
        min-height: {min_touch_target - 16}px;
    }}
    QLabel#pendingLabel {{
        background-color: {c.BG_SURFACE_ELEVATED};
        color: {c.TEXT_SECONDARY};
        border: 1px solid {c.BORDER_SUBTLE};
        font-size: 13px;
        font-weight: 700;
        border-radius: 6px;
        padding: {spacing.XS}px {spacing.SM}px;
        min-height: {min_touch_target - 16}px;
    }}

    /* ── BrakeTestPage: siklus indicator labels ── */
    QLabel#cycleActive {{
        font-size: 13px;
        font-weight: 700;
        color: {c.ACCENT_PRIMARY};
    }}
    QLabel#cycleInactive {{
        font-size: 13px;
        font-weight: 400;
        color: {c.TEXT_UNIT_ON_DARK};
    }}
    QLabel#cycleDone {{
        font-size: 13px;
        font-weight: 600;
        color: {c.ACCENT_SUCCESS};
    }}

    /* ── BrakeTestPage: export action buttons ── */
    QPushButton#exportButton {{
        background-color: {c.ACCENT_PRIMARY};
        color: {c.TEXT_ON_DARK};
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.5px;
        border: none;
        border-radius: 8px;
        padding: 0 {spacing.MD}px;
        min-height: {min_touch_target}px;
    }}
    QPushButton#exportButton:hover {{
        background-color: {c.ACCENT_PRIMARY_HOVER};
    }}
    QPushButton#exportButton:pressed {{
        background-color: {c.ACCENT_PRIMARY_PRESSED};
    }}
    QPushButton#exportButton:disabled {{
        background-color: {c.BG_SURFACE_ELEVATED};
        color: {c.TEXT_UNIT_ON_DARK};
        border: 1px solid {c.BORDER_SUBTLE};
    }}
    """
