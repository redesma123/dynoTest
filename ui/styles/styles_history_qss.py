"""
QSS Stylesheet generator khusus untuk Halaman Riwayat (HistoryPage).
Extracted to respect RULES.md §2 (max ~300 lines per file).
"""


def get_history_qss(c, spacing, font_mono: str, min_touch_target: int) -> str:
    """Return QSS styles khusus filter bar, pagination, dialog detail, dan tabel riwayat."""
    return f"""
    /* ── History Page: Filter Bar Input & Combobox ── */
    QComboBox#filterCombo {{
        background-color: {c.BG_APP};
        border: 1px solid {c.BORDER_SUBTLE};
        border-radius: 8px;
        padding: 6px 12px;
        font-size: 13px;
        color: {c.TEXT_PRIMARY};
        min-height: {min_touch_target - 16}px;
    }}
    QComboBox#filterCombo:focus {{
        border: 1.5px solid {c.BORDER_FOCUS};
    }}
    QComboBox#filterCombo::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 24px;
        border-left: none;
    }}

    /* ── History Page: Pagination Buttons ── */
    QPushButton#pageBtn {{
        background-color: {c.BG_SURFACE};
        color: {c.TEXT_PRIMARY};
        font-size: 13px;
        font-weight: 600;
        border: 1px solid {c.BORDER_SUBTLE};
        border-radius: 6px;
        min-width: 36px;
        max-width: 44px;
        min-height: 36px;
    }}
    QPushButton#pageBtn:hover {{
        background-color: {c.BG_SURFACE_ELEVATED};
        border-color: {c.BORDER_FOCUS};
    }}
    QPushButton#pageBtn[active="true"] {{
        background-color: {c.ACCENT_PRIMARY};
        color: {c.TEXT_ON_DARK};
        border: none;
        font-weight: 700;
    }}
    QPushButton#pageBtn:disabled {{
        background-color: {c.BG_SURFACE_ELEVATED};
        color: {c.TEXT_UNIT_ON_DARK};
        border-color: {c.BORDER_SUBTLE};
    }}

    /* ── History Page: Table Action Buttons (Eye Detail & Print) ── */
    QPushButton#actionIconBtn {{
        background-color: transparent;
        color: {c.TEXT_SECONDARY};
        border: 1px solid {c.BORDER_SUBTLE};
        border-radius: 6px;
        font-size: 14px;
        min-width: 32px;
        min-height: 32px;
    }}
    QPushButton#actionIconBtn:hover {{
        background-color: {c.BG_SURFACE_ELEVATED};
        color: {c.ACCENT_PRIMARY};
        border-color: {c.ACCENT_PRIMARY};
    }}

    /* ── History Detail Dialog ── */
    QDialog#detailDialog {{
        background-color: {c.BG_APP};
    }}
    QFrame#dialogCard {{
        background-color: {c.BG_SURFACE};
        border: 1px solid {c.BORDER_SUBTLE};
        border-radius: 12px;
    }}
    """
