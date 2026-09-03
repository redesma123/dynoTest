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

from ui.styles.styles_qss import get_qss_styles


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
    return get_qss_styles(
        c=Colors,
        spacing=Spacing,
        font_ui=FONT_UI,
        font_mono=FONT_MONO,
        min_touch_target=MIN_TOUCH_TARGET,
    )
