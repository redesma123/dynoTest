# Security Architecture & Policies: DynoTest & BrakeTest

> Last updated: 2026-08-31  
> Security Classification: Industrial Instrumentation / Offline Desktop  
> Standards: OWASP Top 10 Safeguards & Industrial Hardware Safety

---

## 1. Threat Model & Asset Protection

### 1.1 Aset Kritis
| Aset | Deskripsi | Lokasi / Penyimpanan | Dampak jika Terkompromi |
|---|---|---|---|
| **Data Hasil Pengujian** | Rekam historis kelaikan kendaraan (KIR) | `dyno_database.db` (SQLite) | **High** (Manipulasi hasil uji laik jalan) |
| **PLC Control State** | Sinyal Coil `M0` (Start/Stop) & `M2` (Tare) | Socket Modbus TCP (Port 502) | **Critical** (Kecelakaan kerja / mesin menyala tanpa kontrol) |
| **Konfigurasi Ambang Batas** | Nilai standar lulus efisiensi rem & lux | Tabel `app_settings` | **High** (Standar uji diturunkan sepihak) |

### 1.2 Identifikasi Vektor Ancaman & Mitigasi
| Vektor Ancaman | Dampak | Layer | Strategi Mitigasi |
|---|---|---|---|
| **SQL Injection** | Akses/modifikasi tabel database ilegal | Persistence | Wajib menggunakan parameterized queries (`?` placeholder) pada seluruh query SQLite. Dilarang konkatenasi string SQL. |
| **Modbus Packet Injection / Malformed Data** | Crash background worker / buffer issue | Hardware / Core | Validasi tipe data (Type-checking), length validation, dan try-catch pada setiap parsing frame Modbus. |
| **Data Tampering (Pengubahan Hasil Uji)** | Pemalsuan status kelulusan kendaraan | Service / DB | Record hasil uji yang telah berstatus `SAVED` dikunci (Read-Only) dan dicatat timestamp pembuatannya. |
| **Hardware Hang / Loss of Communication** | Roller terus berputar tanpa kontrol software | Hardware Driver | Implementasi software Watchdog (Heartbeat) & auto-command `M0=0` jika koneksi terputus tiba-tiba. |
| **Unbounded Memory Growth (Memory Leak)** | UI Desktop crash saat sampling berjam-jam | Core / UI | Pembatasan buffer live chart maksimum 10.000 titik sampling dengan strategi downsampling/decimation. |

---

## 2. Hardware Safety & Emergency Interlock

1. **Tombol Fisik & Software Emergency Stop (`Esc`):**
   - Menekan tombol `Esc` atau tombol `EMERGENCY STOP` pada UI akan seketika mengirim sinyal pemutusan `Coil M0 = False` ke PLC dalam waktu < 20ms.
2. **Koneksi Loss Fail-Safe:**
   - Jika socket Modbus TCP terputus saat pengujian berjalan, sistem secara otomatis menghentikan status sesi dan memunculkan status `DISCONNECTED (STOPPED FOR SAFETY)`.

---

## 3. Data Integrity & Database Security

- **Parameterized Statements Mandated:**
  ```python
  # WAJIB (Aman dari SQL Injection):
  cursor.execute("SELECT * FROM vehicles WHERE vin = ?", (vin,))
  
  # DILARANG KERAS (Vulnerable):
  cursor.execute(f"SELECT * FROM vehicles WHERE vin = '{vin}'")
  ```
- **Integrity Check:**
  - Database SQLite menjalankan `PRAGMA integrity_check` saat inisialisasi aplikasi untuk mendeteksi kerusakan file database akibat pemadaman listrik mendadak.
