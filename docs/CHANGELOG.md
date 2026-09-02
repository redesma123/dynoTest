# Changelog: DynoTest & BrakeTest

Seluruh perubahan penting pada proyek ini dicatat secara kronologis di dokumen ini.
Format ini mengikuti prinsip [Keep a Changelog](https://keepachangelog.com/id/1.0.0/) dan [Semantic Versioning](https://semver.org/).

---

## [Unreleased] - 2026-08-31

### 🔹 Milestone 1: Inisialisasi Arsitektur & Dokumentasi SSOT
*Fase perencanaan, penentuan spesifikasi hardware Modbus, desain skema database, dan aturan sistem.*

- **Dokumentasi Utama (`docs/`)**:
  - Inisialisasi `PRD.md` (Product Requirements Document & MVP scope).
  - Inisialisasi `SRS.md` (Software Requirements Specification).
  - Inisialisasi `ARCHITECTURE.md` (Arsitektur sistem, modul, thread safety).
  - Inisialisasi `SCHEMA.md` (Skema SQLite, tabel `vehicles`, `test_sessions`, `dyno_results`, `brake_results`).
  - Inisialisasi `API.md` (Modbus TCP Register Map V0–V10 & Coils M0–M3).
  - Inisialisasi `DESIGN.md` & `DESIGN_SYSTEM.md` (Modern Light Industrial Theme).
  - Inisialisasi `SECURITY.md`, `RULES.md`, dan `CONTEXT.md` (Ubiquitous Language SSOT).

---

### 🔹 Milestone 2: Core Physics Engine & Domain Models
*Fase pembuatan entitas data dan mesin kalkulasi matematis.*

- **Domain Entities ([`core/models.py`](file:///d:/Redesma/Project/Desktop/DynoTest/core/models.py))**:
  - Model data untuk `Vehicle`, `TestSession`, `TestMode`, `DynoResult`, `BrakeResult`, dan `EvaluationStatus`.
- **Physics Engine ([`core/physics.py`](file:///d:/Redesma/Project/Desktop/DynoTest/core/physics.py))**:
  - Rumus Tenaga Mesin: $HP = \frac{\text{Torque} \times \text{RPM}}{7127}$.
  - Rumus Efisiensi Pengereman: $\% = \frac{\sum F_{\text{rem}}}{\text{Bobot} \times g} \times 100\%$.
  - Evaluasi batas kelulusan uji rem ($\ge 50\%$) dan intensitas lampu ($\ge 12.000\text{ Lux}$).
  - `DynoPeakTracker` & `BrakePeakTracker` untuk pelacakan nilai puncak secara realtime.

---

### 🔹 Milestone 3: Database Storage Layer (SQLite)
*Fase pembuatan lapisan persistensi data lokal.*

- **Connection Manager ([`database/connection.py`](file:///d:/Redesma/Project/Desktop/DynoTest/database/connection.py))**:
  - Pengaturan koneksi SQLite dengan Write-Ahead Logging (WAL) dan Foreign Keys aktif.
- **Repository Pattern ([`database/repository.py`](file:///d:/Redesma/Project/Desktop/DynoTest/database/repository.py))**:
  - Operasi CRUD lengkap untuk registrasi master kendaraan.
  - Penyimpanan sesi pengujian dan serialisasi time-series data mentah ke format JSON.
  - Fitur pencarian cepat riwayat kendaraan berdasarkan VIN, Nomor Uji, Plat Nomor, atau Model.

---

### 🔹 Milestone 4: Modbus TCP Driver & Digital Twin Simulator
*Fase komunikasi hardware dan simulator pengujian virtual.*

- **Client Driver ([`drivers/modbus_driver.py`](file:///d:/Redesma/Project/Desktop/DynoTest/drivers/modbus_driver.py))**:
  - Klien Modbus TCP socket native untuk membaca V-Registers dan menulis M-Coils dengan scaling otomatis ($V_1/10$, $V_4/100$, $V_7/10$).
- **Digital Twin PLC ([`simulator/digital_twin_plc.py`](file:///d:/Redesma/Project/Desktop/DynoTest/simulator/digital_twin_plc.py))**:
  - Server Modbus TCP lokal dengan simulasi kurva akselerasi gas motor (1.500 $\rightarrow$ 10.500 RPM) dan deselerasi rem realistis.

---

### 🔹 Milestone 5: Testing & Interactive Simulation CLI
*Fase verifikasi otomatis dan demonstrasi interaktif.*

- **Automated Test Suite ([`tests/`](file:///d:/Redesma/Project/Desktop/DynoTest/tests/))**:
  - `test_physics.py`: Unit test rumus fisika dan peak detection.
  - `test_database.py`: Test CRUD database dan relasi antar tabel.
  - `test_modbus.py`: Integration test driver Modbus dengan simulator digital twin.
  - Seluruh 9 test lulus 100% green via `pytest`.
- **Console Runner ([`run_simulation_cli.py`](file:///d:/Redesma/Project/Desktop/DynoTest/run_simulation_cli.py))**:
  - Aplikasi terminal interaktif dengan live ASCII gauge untuk menjalankan 1 siklus pengujian Dyno & Brake test penuh.
- **Project Hygiene**:
  - Penambahan file [`.gitignore`](file:///d:/Redesma/Project/Desktop/DynoTest/.gitignore) standar dan ringkas.
