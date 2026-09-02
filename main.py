"""Entry point aplikasi desktop DynoTest & BrakeTest."""

import sys

from PyQt6.QtWidgets import QApplication

from database.connection import DatabaseManager
from database.repository import DatabaseRepository
from ui.main_window import MainWindow


def main() -> None:
    db_manager = DatabaseManager()
    repository = DatabaseRepository(db_manager)  # otomatis panggil init_database()

    app = QApplication(sys.argv)
    window = MainWindow(repository)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()