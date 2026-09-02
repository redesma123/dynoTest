# PRD: DynoTest & BrakeTest Desktop Application

> Last updated: 2026-08-31  
> Status: Approved  
> Author: System Architect & Engineering Team  
> Platform: Desktop Application (Windows / Python PyQt6)

---

## 1. Overview
Aplikasi Desktop **DynoTest & BrakeTest** adalah sistem akuisisi data dan instrumen pengujian kendaraan bermotor (uji performa mesin dyno dan uji kelaikan rem & lampu/lux) yang terhubung ke PLC (Programmable Logic Controller) via protokol Modbus TCP/RTU. Aplikasi ini berfungsi mencatat data pengujian secara *real-time*, menyimpannya ke database lokal SQLite, serta mencetak struk thermal (58mm/80mm) dan mengekspor laporan resmi berformat PDF A4 dan Excel (.xlsx).

---

## 2. Goals & Objectives
- **Primary Goal:** Menyediakan antarmuka desktop presisi tinggi untuk membaca nilai sensor dari PLC secara realtime, mengevaluasi performa dan kelaikan kendaraan, serta mencetak bukti pengujian secara instan.
- **Secondary Goals:**
  - Menghilangkan pencatatan manual hasil uji dyno dan brake test.
  - Memberikan visualisasi live dual-dial gauge (RPM & Speed) dan kurva performa (Power & Torque).
  - Memastikan data pengujian tersimpan aman secara offline dan dapat dicari kembali sewaktu-waktu.
  - Memudahkan audit dan rekapitulasi data pengujian melalui export Excel dan PDF.

---

## 3. Non-Goals (Out of Scope)
> Fitur yang TIDAK dikerjakan pada rilis versi 1.0.0 agar tidak terjadi scope creep:
- ❌ **Cloud Sync / Multi-branch Sync**: Versi awal difokuskan 100% offline-first pada satu workstation pengujian.
- ❌ **ECU Tuning / Remapping Direct Flashing**: Aplikasi hanya bertindak sebagai instrumen uji (Dyno/Brake measurement), bukan software remapping ECU.
- ❌ **Integrasi Kamera CCTV Plat Otomatis (ANPR/OCR)**: Nomor plat dan nomor uji diinput oleh operator atau dicari dari riwayat database lokal.

---

## 4. Target Users & Personas
| Persona | Deskripsi | Kebutuhan Utama |
|---|---|---|
| **Operator / Penguji KIR** | Petugas teknis balai uji kendaraan bermotor | Input identitas cepat, visualisasi status Lulus/Tidak Lulus otomatis, cetak struk instan. |
| **Mekanik / Tuner Dyno** | Teknisi bengkel performa / modifikasi mesin | Membaca grafik realtime HP vs Torsi, mencari titik puncak (Peak Power), membandingkan run. |
| **Auditor / Manajer Pengujian** | Pengawas operasional dan data teknis | Rekapitulasi laporan berkala dalam format PDF resmi dan spreadsheet Excel. |

---

## 5. MVP Features Matrix
| # | Fitur | Prioritas | Status |
|---|---|---|---|
| 1 | **Form Registrasi & Login Sesi Uji** (No Uji, No Rangka, Penguji, No Polisi, Bobot) | 🔴 Must Have | ⬜ Ready to Build |
| 2 | **Modul Dyno Test Realtime** (RPM, Torsi, Daya HP, Top Speed, Peak Detection) | 🔴 Must Have | ⬜ Ready to Build |
| 3 | **Modul Brake Test & Lux Meter** (RPM Roller, Gaya Rem, Braking Time, Lux, Evaluasi) | 🔴 Must Have | ⬜ Ready to Build |
| 4 | **Penyimpanan Database Lokal SQLite** (Master Kendaraan, Sesi, Time-series) | 🔴 Must Have | ⬜ Ready to Build |
| 5 | **Cetak Struk Thermal & Export Laporan** (ESC/POS 58/80mm, PDF A4, Excel .xlsx) | 🔴 Must Have | ⬜ Ready to Build |
| 6 | **Driver Komunikasi Modbus TCP Worker** (Auto-reconnect, Watchdog) | 🔴 Must Have | ⬜ Ready to Build |

---

## 6. User Stories & Acceptance Criteria

### US-001: Registrasi Sesi Pengujian
**As an** Operator Penguji, **I want** memasukkan Nomor Uji, Nomor Rangka (VIN), Nama Penguji, dan data kendaraan, **so that** data pengujian memiliki identitas yang valid.
- [ ] Field `test_number`, `vin`, dan `inspector_name` wajib diisi sebelum masuk ke pengujian.
- [ ] Tersedia fitur pencarian cepat riwayat kendaraan berdasarkan No. Uji atau No. Rangka.
- [ ] Pilihan mode pengujian (*Dyno*, *Brake*, atau *Lengkap*).

### US-002: Pengujian Dyno Test Realtime
**As a** Tuner/Penguji, **I want** melihat pembacaan RPM, Torsi, dan HP secara realtime di gauge dan grafik, **so that** saya dapat mengetahui performa puncak mesin.
- [ ] Gauge tachometer dan speedometer merespons perubahan nilai dari PLC dengan lancar (60 FPS).
- [ ] Kotak angka metrik (Hero Display) menampilkan nilai HP, Torsi (Nm), dan Gaya Roda secara jelas.
- [ ] Menekan tombol *Stop* secara otomatis mengunci nilai puncak (*Peak HP @ RPM* & *Peak Torque @ RPM*).

### US-003: Pengujian Brake Test & Evaluasi Kelaikan
**As an** Operator Uji Kelaikan, **I want** menguji gaya rem, waktu pengereman, dan intensitas cahaya lampu (Lux), **so that** sistem dapat menentukan kelulusan kendaraan.
- [ ] Sistem menghitung efisiensi pengereman secara otomatis berdasarkan bobot kendaraan.
- [ ] Sistem menampilkan indikator visual kelulusan (*LULUS* warna hijau `#059669` / *TIDAK LULUS* warna merah `#DC2626`).
- [ ] Waktu pengereman (*braking time*) dan intensitas lampu (*lux*) terekam dengan akurat.

### US-004: Pencetakan Struk dan Export Laporan
**As an** Operator, **I want** mencetak struk thermal serta mengekspor PDF/Excel, **so that** hasil uji dapat diserahkan ke pelanggan atau diarsipkan.
- [ ] Shortcut keyboard `F12` langsung mengirim data ke thermal printer via ESC/POS.
- [ ] Shortcut `F11` menghasilkan file PDF A4 resmi berisi kop, tabel hasil, dan kurva grafik.
- [ ] Shortcut `F10` menghasilkan file Excel (.xlsx) lengkap dengan log data mentah per 100ms.

---

## 7. Technical & Performance Requirements
- **Platform:** Windows Desktop Application (Python 3.10+ / PyQt6).
- **Protokol Hardware:** Modbus TCP (Ethernet / LAN / Localhost) & Modbus RTU (RS485 Serial).
- **Polling Rate:** 10 Hz – 50 Hz pada background thread terisolasi.
- **Latency / Response Time:** UI update latency < 50ms, tidak ada freeze saat I/O PLC atau database.
- **Database:** SQLite3 embedded local storage.

---

## 8. Success Metrics
| Metrik | Target | Metode Pengukuran |
|---|---|---|
| **Stabilitas Komunikasi PLC** | 0 Crash pada sampling continuous 1 jam | Stress test background worker |
| **Akurasi Hitung HP & Efisiensi** | 100% presisi sesuai formula matematis | Unit test suite |
| **Kecepatan Cetak Struk** | < 1.5 detik setelah tombol ditekan | Benchmark thermal printing |
| **Kecepatan Generate PDF/Excel** | < 2.0 detik | Benchmark ReportLab & OpenPyXL |
