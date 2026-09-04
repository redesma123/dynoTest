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
from ui.pages import BrakeTestPage, SessionEntryPage, HistoryPage
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
        try:
            os.unlink(path)
        except OSError:
            pass


def test_nav_tabs_structure():
    """Memastikan tab navigasi hanya berisi Registrasi, Test, dan Riwayat."""
    keys = [key for key, _, _ in NAV_TABS]
    assert keys == ["registrasi", "test", "riwayat"]
    assert "setting" not in keys
    assert "dyno" not in keys
    assert "brake" not in keys


def test_main_window_navigation_and_switching(qapp, temp_repo):
    """Pengujian alur navigasi MainWindow langsung mengarah ke BrakeTestPage."""
    win = MainWindow(temp_repo)

    # 1. Pastikan tab navigasi top bar sinkron
    nav_keys = list(win.top_nav._tab_buttons.keys())
    assert nav_keys == ["registrasi", "test", "riwayat"]

    win.show()

    # 2. Pindah ke tab Test -> secara default menampilkan BrakeTestPage
    win.top_nav.tab_requested.emit("test")
    assert isinstance(win.stack.currentWidget(), BrakeTestPage)
    assert not win.top_nav.isHidden()
    win.close()


def test_session_started_routing(qapp, temp_repo):
    """Memastikan session baru diarahkan langsung ke BrakeTestPage."""
    win = MainWindow(temp_repo)

    # Buat data kendaraan dan session
    temp_repo.save_vehicle(Vehicle(vin="VIN123", test_number="UJI001"))
    brake_sess_id = temp_repo.create_test_session(
        TestSession(vin="VIN123", inspector_name="Budi", test_mode=TestMode.BRAKE)
    )

    # Jalankan session brake
    win._on_session_started(brake_sess_id)
    assert isinstance(win.stack.currentWidget(), BrakeTestPage)
    assert win.brake_test_page._session_id == brake_sess_id

    win.close()
