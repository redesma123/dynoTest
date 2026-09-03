"""
Main Window & Router aplikasi.
"""

from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout, QWidget

from core.models import TestMode
from database.repository import DatabaseRepository
from ui.navigation import NAV_TABS, TopNavBar
from ui.pages import BrakeTestPage, DynoTestPage, SessionEntryPage
from ui.styles import build_stylesheet

IMPLEMENTED_TABS = {"registrasi", "dyno", "brake"}
TABS_WITHOUT_NAV_BAR = {"registrasi"}
TAB_DISPLAY_NAMES = {key: label for key, label, _shortcut in NAV_TABS}


class MainWindow(QMainWindow):
    """Jendela utama aplikasi DynoTest & BrakeTest."""

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

        self.dyno_test_page = DynoTestPage(self._repository)
        self.stack.addWidget(self.dyno_test_page)

        self.brake_test_page = BrakeTestPage(self._repository)
        self.stack.addWidget(self.brake_test_page)

        self.top_nav.setVisible("registrasi" not in TABS_WITHOUT_NAV_BAR)
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
        self.top_nav.setVisible(key not in TABS_WITHOUT_NAV_BAR)

        if key == "registrasi":
            self.stack.setCurrentWidget(self.session_entry_page)
        elif key == "dyno":
            self.stack.setCurrentWidget(self.dyno_test_page)
        elif key == "brake":
            self.stack.setCurrentWidget(self.brake_test_page)

    def _on_cancel_shortcut(self) -> None:
        if self.stack.currentWidget() is self.session_entry_page:
            self.session_entry_page.cancel_entry()
            self.statusBar().showMessage("Input dibatalkan.", 2000)

    def _on_session_started(self, session_id: int) -> None:
        """Routing ke halaman yang sesuai berdasarkan test_mode sesi yang baru dibuat."""
        session = self._repository.get_test_session(session_id)
        if session and session.test_mode == TestMode.BRAKE:
            self.brake_test_page.load_session(session_id)
            self._on_tab_requested("brake")
        else:
            self.dyno_test_page.load_session(session_id)
            self._on_tab_requested("dyno")
        self.statusBar().showMessage(
            f"Sesi #{session_id} dibuat. Tekan START untuk memulai pengujian.", 5000
        )