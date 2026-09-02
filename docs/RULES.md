# Project Rules: DynoTest & BrakeTest

> Last updated: 2026-08-31  
> ⚠️ **WAJIB DIPATUHI** oleh setiap developer dan AI coding agent sebelum menulis atau memodifikasi kode.

---

## 1. Golden Rules (Prinsip Utama)

1. **BACA DULU, KODE KEMUDIAN:** Pahami dokumen di `docs/` (`PRD.md`, `ARCHITECTURE.md`, `DESIGN.md`, `SCHEMA.md`, `API.md`) sebelum menulis kode apapun.
2. **JANGAN MENAMBAHKAN FITUR TANPA IZIN:** Hanya implementasikan fitur yang tertera di `PRD.md` (YAGNI & Ponytail Principle).
3. **THREAD SAFETY WAJIB:** Komunikasi socket Modbus I/O dan operasi database berat **DILARANG KERAS** dijalankan di Main UI Thread. Gunakan `QThread` dan Qt Signals.
4. **ANTI-SLOP DESIGN RULES:**
   - Gunakan palet resmi di `docs/DESIGN.md`.
   - DILARANG menggunakan kode warna netral murni (`#FFFFFF` atau `#000000`).
   - Gunakan 8dp spacing system (4/8/16/24/32/48 px).
   - Seluruh elemen tombol klik minimal $44 \times 44\text{ px}$.
5. **ZERO HARDCODED SECRETS / SQL INJECTION:** Seluruh interaksi database SQLite wajib menggunakan parameterized queries (`?`).

---

## 2. File & Directory Conventions

- **Bahasa Pemrograman:** Python 3.10+ (PEP 8 standard).
- **Format Penamaan File:** `snake_case.py` (e.g. `modbus_worker.py`, `dyno_test_page.py`).
- **Format Penamaan Kelas:** `PascalCase` (e.g. `CircularGaugeWidget`, `DatabaseRepository`).
- **Format Penamaan Fungsi & Variabel:** `snake_case` (e.g. `calculate_horsepower()`, `braking_efficiency_pct`).
- **Ukuran File Maksimal:** ~300 baris per file. Jika melebihi batas, pisahkan ke dalam helper/sub-widget terpisah.

---

## 3. Layering & Co-Location

```text
DynoTest/
├── app/
│   ├── core/       # Pure Business logic & Modbus Worker (Bebas dari import PyQt6 widget UI)
│   ├── database/   # SQLite CRUD repository & models
│   ├── exporters/  # Thermal print, ReportLab PDF, OpenPyXL Excel
│   └── ui/         # PyQt6 Windows, Pages & Custom Widgets
├── docs/           # Mandatory System Documentation
├── tests/          # Unit & Integration Test Suite (PyTest)
└── server_plc_device_a.py # Simulator Modbus PLC
```

---

## 4. Test-Driven Development (TDD) Mandate

- Sebelum menulis logika baru di `app/core/` atau `app/database/`, buat unit test terlebih dahulu di folder `tests/`.
- Verifikasi siklus **RED $\rightarrow$ GREEN $\rightarrow$ REFACTOR**.
- Seluruh unit test wajib passing 100% sebelum integrasi ke UI.
