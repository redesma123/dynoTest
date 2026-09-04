"""
Tests for UI navigation and sub-mode switching between Dyno Test and Brake Test.
"""
import tempfile
import os
import pytest
from PyQt6.QtWidgets import QApplication

from database.connection import DatabaseManager
from database.repository import DatabaseRepository
from ui.navigation import NAV_TABS
from ui.main_window import MainWindow
from ui.pages import DynoTestPage, BrakeTestPage, SessionEntryPage, HistoryPage
from core.models import TestMode, TestSession, Vehicle


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def temp_repo():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = DatabaseManager(path)
    repo = DatabaseRepository(db)
    yield repo
    if os.path.exists(path):
        os.unlink(path)


def test_nav_tabs_structure():
    """Memastikan tab navigasi hanya berisi Registrasi, Test, dan Riwayat."""
    keys = [key for key, _, _ in NAV_TABS]
    assert keys == ["registrasi", "test", "riwayat"]
    assert "setting" not in keys
    assert "dyno" not in keys
    assert "brake" not in keys


def test_main_window_navigation_and_switching(qapp, temp_repo):
    """Pengujian alur navigasi MainWindow, sub-mode switching, dan pencegahan switch saat running."""
    win = MainWindow(temp_repo)

    # 1. Pastikan tab navigasi top bar sinkron
    nav_keys = list(win.top_nav._tab_buttons.keys())
    assert nav_keys == ["registrasi", "test", "riwayat"]

    win.show()

    # 2. Pindah ke tab Test -> secara default menampilkan DynoTestPage
    win.top_nav.tab_requested.emit("test")
    assert isinstance(win.stack.currentWidget(), DynoTestPage)
    assert not win.top_nav.isHidden()

    # 3. Klik tombol switch ke Brake Test dari header
    win.dyno_test_page.mode_switch_requested.emit("brake")
    assert isinstance(win.stack.currentWidget(), BrakeTestPage)
    assert win._current_test_submode == "brake"

    # 4. Klik tombol switch kembali ke Dyno Test dari header
    win.brake_test_page.mode_switch_requested.emit("dyno")
    assert isinstance(win.stack.currentWidget(), DynoTestPage)
    assert win._current_test_submode == "dyno"

    # 5. Uji pencegahan switch saat pengujian sedang RUNNING
    from ui.pages.dyno_test_page import _State
    win.dyno_test_page._state = _State.RUNNING
    win.dyno_test_page.mode_switch_requested.emit("brake")
    # Tetap di DynoTestPage karena sedang RUNNING
    assert isinstance(win.stack.currentWidget(), DynoTestPage)
    assert win._current_test_submode == "dyno"

    # Hentikan state running
    win.dyno_test_page._state = _State.IDLE
    win.close()


def test_session_started_routing(qapp, temp_repo):
    """Memastikan session baru diarahkan ke sub-mode yang sesuai dengan TestMode."""
    win = MainWindow(temp_repo)

    # Buat data kendaraan dan session
    temp_repo.save_vehicle(Vehicle(vin="VIN123", test_number="UJI001"))
    dyno_sess_id = temp_repo.create_test_session(
        TestSession(vin="VIN123", inspector_name="Budi", test_mode=TestMode.DYNO)
    )
    brake_sess_id = temp_repo.create_test_session(
        TestSession(vin="VIN123", inspector_name="Budi", test_mode=TestMode.BRAKE)
    )

    # Jalankan session dyno
    win._on_session_started(dyno_sess_id)
    assert isinstance(win.stack.currentWidget(), DynoTestPage)
    assert win._current_test_submode == "dyno"
    assert win.dyno_test_page._session_id == dyno_sess_id

    # Jalankan session brake
    win._on_session_started(brake_sess_id)
    assert isinstance(win.stack.currentWidget(), BrakeTestPage)
    assert win._current_test_submode == "brake"
    assert win.brake_test_page._session_id == brake_sess_id

    win.close()
