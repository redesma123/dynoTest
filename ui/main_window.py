"""
Main Window & Router aplikasi.

"""

from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout, QWidget

from database.repository import DatabaseRepository
from ui.session_entry_page import SessionEntryPage
from ui.styles import build_stylesheet
from ui.top_nav_bar import NAV_TABS, TopNavBar

# Tab yang sudah punya halaman nyata. Sisanya ("dyno", "brake", "riwayat",
# "setting") baru placeholder sampai halamannya dibangun.
IMPLEMENTED_TABS = {"registrasi"}

TAB_DISPLAY_NAMES = {key: label for key, label, _shortcut in NAV_TABS}


class MainWindow(QMainWindow):
    def __init__(self, repository: DatabaseRepository) -> None:
        super().__init__()
        self.setWindowTitle("DynoTest & BrakeTest \u2014 AUTO-TECH SYSTEMS")
        self.resize(1440, 960)
        self.setStyleSheet(build_stylesheet())

        self._repository = repository

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        self.top_nav = TopNavBar()
        self.top_nav.tab_requested.connect(self._on_tab_requested)
        container_layout.addWidget(self.top_nav)

        self.stack = QStackedWidget()
        container_layout.addWidget(self.stack, 1)
        self.setCentralWidget(container)

        self.session_entry_page = SessionEntryPage(self._repository)
        self.session_entry_page.session_started.connect(self._on_session_started)
        self.session_entry_page.view_all_requested.connect(lambda: self._on_tab_requested("riwayat"))
        self.stack.addWidget(self.session_entry_page)

        self.statusBar().showMessage("Siap.", 3000)

        self._setup_shortcuts()

    def _setup_shortcuts(self) -> None:
        for key, _label, shortcut_key in NAV_TABS:
            shortcut = QShortcut(QKeySequence(shortcut_key), self)
            shortcut.activated.connect(lambda k=key: self._on_tab_requested(k))

        cancel_shortcut = QShortcut(QKeySequence("Esc"), self)
        cancel_shortcut.activated.connect(self._on_cancel_shortcut)

    def _on_tab_requested(self, key: str) -> None:
        if key not in IMPLEMENTED_TABS:
            label = TAB_DISPLAY_NAMES.get(key, key)
            self.statusBar().showMessage(f"Halaman '{label}' belum tersedia.", 3000)
            return

        self.top_nav.set_active_tab(key)
        if key == "registrasi":
            self.stack.setCurrentWidget(self.session_entry_page)

    def _on_cancel_shortcut(self) -> None:
        if self.stack.currentWidget() is self.session_entry_page:
            self.session_entry_page.cancel_entry()
            self.statusBar().showMessage("Input dibatalkan.", 2000)

    def _on_session_started(self, session_id: int) -> None:
        # TODO: navigasi otomatis ke Dyno Test / Brake Test page setelah
        # halaman tsb dibuat (mengikuti Page Map di docs/DESIGN.md).
        self.statusBar().showMessage(f"Sesi #{session_id} dibuat, siap lanjut ke pengujian.", 4000)