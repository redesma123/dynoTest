# Database Schema & Data Dictionary (DynoTest & BrakeTest)

> Last updated: 2026-08-31  
> Database Engine: SQLite 3  
> Storage File: `dyno_database.db`  
> Strategy: Embedded Offline-First dengan Transactional Integrity (WAL Mode)

---

## 1. Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    VEHICLES ||--o{ TEST_SESSIONS : "memiliki riwayat"
    TEST_SESSIONS ||--o| DYNO_RESULTS : "memiliki hasil (opsional)"
    TEST_SESSIONS ||--o| BRAKE_RESULTS : "memiliki hasil (opsional)"

    VEHICLES {
        string vin PK "Nomor Rangka"
        string test_number UK "Nomor Uji KIR"
        string license_plate "Nomor Polisi"
        string vehicle_category "Roda 2 / Roda 4"
        string brand_model "Merk dan Model"
        int engine_capacity_cc "Kapasitas Silinder"
        float vehicle_weight_kg "Bobot Kendaraan (kg)"
        datetime created_at "Waktu Terdaftar"
    }

    TEST_SESSIONS {
        int id PK "Auto Increment"
        string vin FK "Relasi ke Vehicles"
        string inspector_name "Nama Petugas Uji"
        string test_mode "DYNO / BRAKE / COMBINED"
        datetime tested_at "Waktu Mulai Pengujian"
        string notes "Catatan Hasil Inspeksi"
    }

    DYNO_RESULTS {
        int id PK "Auto Increment"
        int session_id FK "Relasi ke Test Sessions"
        float max_rpm "RPM Maksimum"
        float max_torque_nm "Torsi Maksimum (Nm)"
        float max_power_hp "Daya Kuda Maksimum (HP)"
        float max_speed_kmh "Top Speed (km/h)"
        float rpm_at_peak_power "RPM saat Peak HP"
        float rpm_at_peak_torque "RPM saat Peak Torsi"
        text raw_time_series_json "Array Time-Series Sampling"
    }

    BRAKE_RESULTS {
        int id PK "Auto Increment"
        int session_id FK "Relasi ke Test Sessions"
        float initial_speed_kmh "Kecepatan Sebelum Rem"
        float peak_braking_force_n "Gaya Rem Maksimum (N)"
        float braking_time_s "Durasi Pengereman (detik)"
        float total_running_time_s "Total Durasi Uji (detik)"
        float lux_intensity "Intensitas Cahaya (Lux)"
        float braking_efficiency_pct "Efisiensi Rem (%)"
        string lux_pass_status "PASS / FAIL"
        string brake_pass_status "PASS / FAIL"
        string overall_status "PASS / FAIL"
        text raw_time_series_json "Array Time-Series Sampling"
    }
```

---

## 2. Definisi Skema Tabel (SQL DDL)

```sql
-- Aktifkan Foreign Key dan Write-Ahead Logging untuk performa & integritas
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- 1. Master Kendaraan
CREATE TABLE IF NOT EXISTS vehicles (
    vin TEXT PRIMARY KEY,
    test_number TEXT UNIQUE NOT NULL,
    license_plate TEXT,
    vehicle_category TEXT DEFAULT 'Roda 2',
    brand_model TEXT,
    engine_capacity_cc INTEGER,
    vehicle_weight_kg REAL NOT NULL DEFAULT 150.0,
    created_at DATETIME DEFAULT (DATETIME('now', 'localtime'))
);

CREATE INDEX IF NOT EXISTS idx_vehicles_test_number ON vehicles(test_number);
CREATE INDEX IF NOT EXISTS idx_vehicles_license_plate ON vehicles(license_plate);

-- 2. Sesi Pengujian
CREATE TABLE IF NOT EXISTS test_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vin TEXT NOT NULL,
    inspector_name TEXT NOT NULL,
    test_mode TEXT NOT NULL CHECK(test_mode IN ('DYNO', 'BRAKE', 'COMBINED')),
    tested_at DATETIME DEFAULT (DATETIME('now', 'localtime')),
    notes TEXT,
    FOREIGN KEY(vin) REFERENCES vehicles(vin) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sessions_vin ON test_sessions(vin);
CREATE INDEX IF NOT EXISTS idx_sessions_tested_at ON test_sessions(tested_at);

-- 3. Hasil Pengujian Dyno Test
CREATE TABLE IF NOT EXISTS dyno_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL UNIQUE,
    max_rpm REAL NOT NULL,
    max_torque_nm REAL NOT NULL,
    max_power_hp REAL NOT NULL,
    max_speed_kmh REAL NOT NULL,
    rpm_at_peak_power REAL,
    rpm_at_peak_torque REAL,
    raw_time_series_json TEXT,
    FOREIGN KEY(session_id) REFERENCES test_sessions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_dyno_session ON dyno_results(session_id);

-- 4. Hasil Pengujian Brake Test & Lux
CREATE TABLE IF NOT EXISTS brake_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL UNIQUE,
    initial_speed_kmh REAL NOT NULL,
    peak_braking_force_n REAL NOT NULL,
    braking_time_s REAL NOT NULL,
    total_running_time_s REAL NOT NULL,
    lux_intensity REAL NOT NULL,
    braking_efficiency_pct REAL NOT NULL,
    lux_pass_status TEXT NOT NULL CHECK(lux_pass_status IN ('PASS', 'FAIL')),
    brake_pass_status TEXT NOT NULL CHECK(brake_pass_status IN ('PASS', 'FAIL')),
    overall_status TEXT NOT NULL CHECK(overall_status IN ('PASS', 'FAIL')),
    raw_time_series_json TEXT,
    FOREIGN KEY(session_id) REFERENCES test_sessions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_brake_session ON brake_results(session_id);

-- 5. Pengaturan Aplikasi
CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT
);
```

---

## 3. Format Payload JSON Time-Series (`raw_time_series_json`)

### Payload Dyno Time-Series
```json
[
  { "t_sec": 0.05, "rpm": 2100.0, "torque_nm": 12.4, "power_hp": 3.65, "speed_kmh": 22.5 },
  { "t_sec": 0.10, "rpm": 2350.0, "torque_nm": 13.8, "power_hp": 4.54, "speed_kmh": 25.1 }
]
```

### Payload Brake Time-Series
```json
[
  { "t_sec": 0.05, "speed_kmh": 41.5, "force_n": 120.0, "brake_pedal": 0 },
  { "t_sec": 0.10, "speed_kmh": 39.8, "force_n": 2450.0, "brake_pedal": 1 }
]
```

---

## 4. Default Seed & Settings Data

```sql
INSERT OR IGNORE INTO app_settings (key, value, description) VALUES
('plc_ip', '127.0.0.1', 'Alamat IP PLC Modbus TCP'),
('plc_port', '502', 'Port Modbus TCP PLC'),
('min_brake_efficiency_pct', '50.0', 'Ambang batas minimum efisiensi rem lulus (%)'),
('max_braking_time_s', '4.0', 'Ambang batas waktu pengereman maksimum (detik)'),
('min_lux_intensity', '12000.0', 'Ambang batas intensitas cahaya lampu utama (Lux)'),
('workshop_name', 'BALAI UJI KENDARAAN & PERFORMA DYNO', 'Nama institusi / bengkel di kop struk dan laporan'),
('workshop_address', 'Jl. Industri Otomotif No. 88, Indonesia', 'Alamat institusi');
```
