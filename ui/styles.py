"""
Design tokens & QSS stylesheet aplikasi DynoTest & BrakeTest.

Acuan:
- docs/DESIGN.md            (Design Tokens & Typography)
- docs/DESIGN_SYSTEM.md     (Palet Warna Resmi & Anatomi Layout)
- docs/RULES.md             (Anti pure #FFFFFF/#000000, 8dp spacing, min touch 44x44)

JANGAN hardcode hex baru di file page lain — semua warna WAJIB lewat
`Colors` di modul ini agar konsisten satu sumber kebenaran (single source
of truth) sesuai Golden Rule di RULES.md.
"""


class Colors:
    """Token warna resmi. Nilai HEX identik dengan tabel di DESIGN.md."""

    # Backgrounds
    BG_APP = "#F1F5F9"
    BG_SURFACE = "#FAFCFE"
    BG_SURFACE_ELEVATED = "#E2E8F0"
    BG_METRIC_BOX = "#0F172A"

    # Borders
    BORDER_SUBTLE = "#CBD5E1"
    BORDER_FOCUS = "#0284C7"

    # Text
    TEXT_PRIMARY = "#0E1726"
    TEXT_SECONDARY = "#475569"
    TEXT_ON_DARK = "#F8FAFC"
    TEXT_UNIT_ON_DARK = "#94A3B8"

    # Accents
    ACCENT_PRIMARY = "#0284C7"
    ACCENT_PRIMARY_HOVER = "#0369A1"
    ACCENT_PRIMARY_PRESSED = "#075985"
    ACCENT_MAGENTA = "#E11D48"
    ACCENT_NEEDLE = "#D97706"
    ACCENT_SUCCESS = "#059669"
    ACCENT_DANGER = "#DC2626"

    # Status chip (badge koneksi PLC / status lulus-tidak lulus)
    SUCCESS_BG = "#DCFCE7"
    SUCCESS_BORDER = "#86EFAC"
    DANGER_BG = "#FEE2E2"
    DANGER_BORDER = "#FCA5A5"


class Spacing:
    """8dp Spacing Grid — DESIGN.md Bagian 3."""

    XS = 4
    SM = 8
    MD = 16
    LG = 24
    XL = 32
    XXL = 48


FONT_UI = "'Inter', 'Segoe UI', 'Roboto'"
FONT_MONO = "'Roboto Mono', 'Consolas', monospace"

# RULES.md: seluruh elemen tombol klik minimal 44x44 px.
MIN_TOUCH_TARGET = 44


def build_stylesheet() -> str:
    """Kembalikan QSS global untuk diterapkan pada QApplication/QMainWindow."""
    c = Colors
    return f"""
    QWidget#appRoot {{
        background-color: {c.BG_APP};
        font-family: {FONT_UI};
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
        font-size: 16px;
        font-weight: 600;
        color: {c.TEXT_PRIMARY};
        letter-spacing: 1px;
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

    QLineEdit#fieldInput {{
        background-color: {c.BG_APP};
        border: 1px solid {c.BORDER_SUBTLE};
        border-radius: 8px;
        padding: 10px 12px;
        font-size: 14px;
        color: {c.TEXT_PRIMARY};
        min-height: {MIN_TOUCH_TARGET - 20}px;
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
        padding: 0 {Spacing.LG}px;
        min-height: {MIN_TOUCH_TARGET}px;
        min-width: {MIN_TOUCH_TARGET * 2}px;
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
        padding: 0 {Spacing.SM}px;
        min-height: {MIN_TOUCH_TARGET}px;
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
        padding: 0 {Spacing.MD}px;
        min-height: {MIN_TOUCH_TARGET}px;
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
        padding: {Spacing.XS}px {Spacing.SM}px;
        min-height: {MIN_TOUCH_TARGET - 16}px;
    }}

    QLabel#plcBadgeDisconnected {{
        background-color: {c.DANGER_BG};
        color: {c.ACCENT_DANGER};
        border: 1px solid {c.DANGER_BORDER};
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        padding: {Spacing.XS}px {Spacing.SM}px;
        min-height: {MIN_TOUCH_TARGET - 16}px;
    }}

    QLabel#footerLabel {{
        font-family: {FONT_MONO};
        font-size: 11px;
        color: {c.TEXT_SECONDARY};
        letter-spacing: 1px;
    }}

    QLabel#emptyStateLabel {{
        font-size: 13px;
        color: {c.TEXT_SECONDARY};
        padding: {Spacing.LG}px;
    }}
    """