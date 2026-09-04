"""
Main Window & Router aplikasi.
"""

from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout, QWidget

from core.models import TestMode
from database.repository import DatabaseRepository
from ui.navigation import NAV_TABS, TopNavBar
from ui.pages import BrakeTestPage, DynoTestPage, HistoryPage, SessionEntryPage
from ui.styles import build_stylesheet

IMPLEMENTED_TABS = {"registrasi", "test", "riwayat"}
TABS_WITHOUT_NAV_BAR = set()
TAB_DISPLAY_NAMES = {key: label for key, label, _shortcut in NAV_TABS}


class MainWindow(QMainWindow):
    """Jendela utama aplikasi DynoTest & BrakeTest."""

    def __init__(self, repository: DatabaseRepository) -> None:
        super().__init__()
        self.setWindowTitle("DynoTest & BrakeTest \u2014 AUTO-TECH SYSTEMS")
        self.resize(1440, 960)
        self.showMaximized()
        self.setStyleSheet(build_stylesheet())

        self._repository = repository
        self._current_test_submode = "dyno"

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
        self.dyno_test_page.mode_switch_requested.connect(self._on_switch_test_submode)
        self.stack.addWidget(self.dyno_test_page)

        self.brake_test_page = BrakeTestPage(self._repository)
        self.brake_test_page.mode_switch_requested.connect(self._on_switch_test_submode)
        self.stack.addWidget(self.brake_test_page)

        self.history_page = HistoryPage(self._repository)
        self.stack.addWidget(self.history_page)

        self.top_nav.setVisible("registrasi" not in TABS_WITHOUT_NAV_BAR)
        self.statusBar().showMessage("Siap.", 3000)
        self._setup_shortcuts()

    def _setup_shortcuts(self) -> None:
        for key, _label, shortcut_key in NAV_TABS:
            shortcut = QShortcut(QKeySequence(shortcut_key), self)
            shortcut.activated.connect(lambda k=key: self._on_tab_requested(k))

        cancel_shortcut = QShortcut(QKeySequence("Esc"), self)
        cancel_shortcut.activated.connect(self._on_cancel_shortcut)

    def _on_switch_test_submode(self, mode: str) -> None:
        """Beralih antara sub-mode pengujian (Dyno atau Brake) melalui tombol di header."""
        if mode == self._current_test_submode:
            return

        current_page = self.dyno_test_page if self._current_test_submode == "dyno" else self.brake_test_page
        if getattr(current_page, "_state", None) and current_page._state.name == "RUNNING":
            self.statusBar().showMessage(
                "Pengujian sedang berjalan. Hentikan pengujian terlebih dahulu.", 3000
            )
            return

        # Sinkronkan data sesi aktif antar halaman jika ada
        if mode == "brake" and self.dyno_test_page._session_id is not None:
            self.brake_test_page.load_session(self.dyno_test_page._session_id)
        elif mode == "dyno" and self.brake_test_page._session_id is not None:
            self.dyno_test_page.load_session(self.brake_test_page._session_id)

        self._current_test_submode = mode
        self._on_tab_requested("test")
        label = "Dyno Test" if mode == "dyno" else "Brake Test"
        self.statusBar().showMessage(f"Mode pengujian dialihkan ke {label}.", 2500)

    def _on_tab_requested(self, key: str) -> None:
        # Dukung key "test" serta backwards-compatibility jika dipanggil "dyno" atau "brake"
        if key in ("test", "dyno", "brake"):
            if key in ("dyno", "brake"):
                self._current_test_submode = key
            self.top_nav.set_active_tab("test")
            self.top_nav.setVisible("test" not in TABS_WITHOUT_NAV_BAR)
            if self._current_test_submode == "brake":
                self.stack.setCurrentWidget(self.brake_test_page)
            else:
                self.stack.setCurrentWidget(self.dyno_test_page)
            return

        if key not in IMPLEMENTED_TABS:
            label = TAB_DISPLAY_NAMES.get(key, key)
            self.statusBar().showMessage(f"Halaman '{label}' belum tersedia.", 3000)
            return

        self.top_nav.set_active_tab(key)
        self.top_nav.setVisible(key not in TABS_WITHOUT_NAV_BAR)

        if key == "registrasi":
            self.stack.setCurrentWidget(self.session_entry_page)
        elif key == "riwayat":
            self.history_page.reload_data()
            self.stack.setCurrentWidget(self.history_page)

    def _on_cancel_shortcut(self) -> None:
        if self.stack.currentWidget() is self.session_entry_page:
            self.session_entry_page.cancel_entry()
            self.statusBar().showMessage("Input dibatalkan.", 2000)

    def _on_session_started(self, session_id: int) -> None:
        """Routing ke halaman pengujian berdasarkan test_mode sesi yang baru dibuat."""
        session = self._repository.get_test_session(session_id)
        if session and session.test_mode == TestMode.BRAKE:
            self.brake_test_page.load_session(session_id)
            self._current_test_submode = "brake"
        else:
            self.dyno_test_page.load_session(session_id)
            self._current_test_submode = "dyno"

        self._on_tab_requested("test")
        self.statusBar().showMessage(
            f"Sesi #{session_id} dibuat. Tekan START untuk memulai pengujian.", 5000
        )