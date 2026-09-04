"""
QSS Stylesheet Generator untuk DynoTest & BrakeTest.
Extracted from styles.py to respect RULES.md §2 (max ~300 lines per file).
"""

from ui.styles.styles_history_qss import get_history_qss
from ui.styles.styles_widgets_qss import get_widget_qss


def get_qss_styles(c, spacing, font_ui: str, font_mono: str, min_touch_target: int) -> str:
    """Kembalikan string QSS global."""
    base_qss = f"""
    QWidget#appRoot {{
        background-color: {c.BG_APP};
        font-family: {font_ui};
        color: {c.TEXT_PRIMARY};
    }}

    QLabel#pageTitle {{
        font-size: 26px;
        font-weight: 700;
        color: {c.TEXT_PRIMARY};
    }}

    QLabel#pageSubtitle {{
        font-size: 14px;
        font-weight: 400;
        color: {c.TEXT_SECONDARY};
    }}

    QFrame#card {{
        background-color: {c.BG_SURFACE};
        border: 1px solid {c.BORDER_SUBTLE};
        border-top: 3px solid {c.ACCENT_PRIMARY};
        border-radius: 10px;
    }}

    QFrame#tableCard {{
        background-color: {c.BG_SURFACE};
        border: 1px solid {c.BORDER_SUBTLE};
        border-radius: 10px;
    }}

    QLabel#sectionTitle {{
        font-size: 14px;
        font-weight: 700;
        color: {c.TEXT_PRIMARY};
        letter-spacing: 0.5px;
    }}

    QFrame#divider {{
        background-color: {c.BORDER_SUBTLE};
        max-height: 1px;
        min-height: 1px;
        border: none;
    }}

    QLabel#fieldLabel {{
        font-size: 12px;
        font-weight: 500;
        color: {c.TEXT_SECONDARY};
        letter-spacing: 0.5px;
    }}

    QRadioButton {{
        color: {c.TEXT_PRIMARY};
        font-size: 13px;
        font-weight: 500;
        spacing: 8px;
    }}

    QRadioButton::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 9px;
        border: 1.5px solid {c.BORDER_SUBTLE};
        background-color: {c.BG_APP};
    }}

    QRadioButton::indicator:checked {{
        border: 4px solid {c.BG_SURFACE};
        background-color: {c.ACCENT_PRIMARY};
    }}

    QRadioButton::indicator:hover {{
        border-color: {c.ACCENT_PRIMARY};
    }}

    QLineEdit#fieldInput {{
        background-color: {c.BG_APP};
        border: 1px solid {c.BORDER_SUBTLE};
        border-radius: 8px;
        padding: 10px 12px;
        font-size: 14px;
        color: {c.TEXT_PRIMARY};
        min-height: {min_touch_target - 20}px;
    }}

    QLineEdit#fieldInput:focus {{
        border: 1.5px solid {c.BORDER_FOCUS};
    }}

    QLineEdit#fieldInput[error="true"] {{
        border: 1.5px solid {c.ACCENT_DANGER};
    }}

    QPushButton#primaryButton {{
        background-color: {c.ACCENT_PRIMARY};
        color: {c.TEXT_ON_DARK};
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 0.5px;
        border: none;
        border-radius: 8px;
        padding: 0 {spacing.LG}px;
        min-height: {min_touch_target}px;
        min-width: {min_touch_target * 2}px;
    }}

    QPushButton#primaryButton:hover {{
        background-color: {c.ACCENT_PRIMARY_HOVER};
    }}

    QPushButton#primaryButton:pressed {{
        background-color: {c.ACCENT_PRIMARY_PRESSED};
    }}

    QPushButton#linkButton {{
        background-color: transparent;
        border: none;
        color: {c.ACCENT_PRIMARY};
        font-size: 13px;
        font-weight: 600;
        padding: 0 {spacing.SM}px;
        min-height: {min_touch_target}px;
    }}

    QPushButton#linkButton:hover {{
        color: {c.ACCENT_PRIMARY_HOVER};
        text-decoration: underline;
    }}

    QLabel#errorLabel {{
        font-size: 12px;
        font-weight: 600;
        color: {c.ACCENT_DANGER};
    }}

    QFrame#historyHeaderBar {{
        background-color: {c.BG_SURFACE_ELEVATED};
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
    }}

    QLabel#historyHeader {{
        font-size: 15px;
        font-weight: 700;
        color: {c.TEXT_PRIMARY};
    }}

    QTableWidget#historyTable {{
        background-color: {c.BG_SURFACE};
        alternate-background-color: {c.BG_APP};
        gridline-color: transparent;
        border: none;
        font-size: 13px;
        color: {c.TEXT_PRIMARY};
    }}

    QTableWidget#historyTable::item {{
        padding: 10px 6px;
    }}

    QHeaderView::section {{
        background-color: {c.BG_SURFACE};
        color: {c.TEXT_SECONDARY};
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.5px;
        border: none;
        border-bottom: 1px solid {c.BORDER_SUBTLE};
        padding: 10px 6px;
    }}

    QTableCornerButton::section {{
        background-color: {c.BG_SURFACE};
        border: none;
        border-bottom: 1px solid {c.BORDER_SUBTLE};
    }}

    QFrame#topNavBar {{
        background-color: {c.BG_SURFACE};
        border-bottom: 1px solid {c.BORDER_SUBTLE};
    }}

    QLabel#navLogo {{
        font-size: 15px;
        font-weight: 700;
        color: {c.ACCENT_PRIMARY};
        letter-spacing: 0.5px;
    }}

    QPushButton#navTab {{
        background-color: transparent;
        color: {c.TEXT_SECONDARY};
        font-size: 13px;
        font-weight: 600;
        border: none;
        border-radius: 6px;
        padding: 0 {spacing.MD}px;
        min-height: {min_touch_target}px;
    }}

    QPushButton#navTab:hover {{
        background-color: {c.BG_SURFACE_ELEVATED};
    }}

    QPushButton#navTab[active="true"] {{
        background-color: {c.ACCENT_PRIMARY};
        color: {c.TEXT_ON_DARK};
    }}

    QPushButton#navTab[active="true"]:hover {{
        background-color: {c.ACCENT_PRIMARY};
    }}

    QLabel#plcBadgeConnected {{
        background-color: {c.SUCCESS_BG};
        color: {c.ACCENT_SUCCESS};
        border: 1px solid {c.SUCCESS_BORDER};
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        padding: {spacing.XS}px {spacing.SM}px;
        min-height: {min_touch_target - 16}px;
    }}

    QLabel#plcBadgeDisconnected {{
        background-color: {c.DANGER_BG};
        color: {c.ACCENT_DANGER};
        border: 1px solid {c.DANGER_BORDER};
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        padding: {spacing.XS}px {spacing.SM}px;
        min-height: {min_touch_target - 16}px;
    }}

    QLabel#footerLabel {{
        font-family: {font_mono};
        font-size: 11px;
        color: {c.TEXT_SECONDARY};
        letter-spacing: 1px;
    }}

    QLabel#emptyStateLabel {{
        font-size: 13px;
        color: {c.TEXT_SECONDARY};
        padding: {spacing.LG}px;
    }}

    QScrollBar:vertical {{
        background-color: transparent;
        width: 8px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background-color: {c.BORDER_SUBTLE};
        min-height: 24px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical:hover {{
        background-color: {c.ACCENT_PRIMARY};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background-color: transparent;
    }}
    """
    widgets_qss = get_widget_qss(c, spacing, font_mono, min_touch_target)
    history_qss = get_history_qss(c, spacing, font_mono, min_touch_target)
    return base_qss + widgets_qss + history_qss
