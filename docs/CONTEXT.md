# CONTEXT.md: Project Anchor & AI Skills Mapping

Dokumen ini berfungsi sebagai **Single Source of Truth (SSOT)** agar pengembangan aplikasi desktop **DynoTest & BrakeTest** tetap terarah, konsisten, dan tidak mengalami *cognitive drift*.

---

## 1. Ubiquitous Language (Glosarium & Naming Convention)

Semua variabel, field database, endpoint/register, dan kode UI wajib mengikuti konvensi penamaan standar berikut:

| Istilah Domain | Nama Teknis / Variabel | Tipe Data | Definisi |
|---|---|---|---|
| **Nomor Uji** | `test_number` | `String` | Nomor identitas pengujian resmi kendaraan (KIR/Reg). |
| **Nomor Rangka** | `vin` | `String` | Vehicle Identification Number / Nomor Rangka kendaraan. |
| **Nomor Polisi** | `license_plate` | `String` | Plat nomor registrasi kendaraan bermotor. |
| **Nama Penguji** | `inspector_name` | `String` | Nama teknisi/operator yang melakukan pengujian. |
| **Sesi Pengujian** | `test_session` | `Object/Model` | Satu rangkaian pengujian untuk 1 kendaraan pada waktu tertentu. |
| **Mode Uji** | `test_mode` | `Enum('DYNO', 'BRAKE', 'COMBINED')` | Jenis pengujian yang sedang aktif. |
| **RPM Mesin/Roller** | `engine_rpm` / `roller_rpm` | `Float/Int` | Kecepatan putar dalam Revolution Per Minute. |
| **Torsi Dyno** | `dyno_torque_nm` | `Float` | Torsi hasil pengukuran dyno (Newton-meter). |
| **Tenaga Kuda** | `power_hp` | `Float` | Daya mesin yang dikalkulasi (\(\text{HP} = \frac{T \times \text{RPM}}{7127}\)). |
| **Kecepatan Uji** | `speed_kmh` | `Float` | Kecepatan linier roller/kendaraan dalam km/jam. |
| **Torsi Pengereman** | `braking_torque_nm` / `braking_force_n` | `Float` | Gaya/torsi tahanan rem yang dihasilkan saat pedal ditekan. |
| **Waktu Pengereman**| `braking_time_s` | `Float` | Durasi dari rem aktif hingga roller berhenti (detik). |
| **Waktu Uji Rem** | `running_time_s` | `Float` | Total durasi pengujian rem berjalan (detik). |
| **Intensitas Cahaya**| `lux_intensity` | `Float` | Pengukuran intensitas berkas cahaya lampu (Lux). |
| **Efisiensi Rem** | `braking_efficiency_pct` | `Float` | Persentase gaya rem total terhadap berat kendaraan. |
| **Status Kelulusan** | `pass_fail_status` | `Enum('PASS', 'FAIL')` | Status kelulusan berdasarkan ambang batas standar teknis. |

---

## 2. Pemetaan AI Skills & SOP Lifecycle (Tahap 1 - 5)

Berikut adalah panduan eksekusi dan skills yang wajib diaktifkan pada setiap tahapan:

```
[Tahap 1: Ideasi & Validasi] ──> [Tahap 2: PRD & SRS] ──> [Tahap 3: Arsitektur & Blueprint]
                                                                        │
┌───────────────────────────────────────────────────────────────────────┘
│
▼
[Tahap 4: Build (TDD & Ponytail)] <───┐ (Iterative Sprint Loop)
  │                                   │
  └───> [Tahap 5: QA & Verification] ─┘ (Jika ada bug / cacat)
          │
          └───> [PRODUCTION READY]
```

### 🔹 Tahap 1: Ideasi & Validasi Konsep
- **Skill**: `brainstorming`, `gstack` (`/office-hours`), `grilling`.
- **Tujuan**: Memastikan kebutuhan pengguna (Dyno + Brake Test + Struk + PDF + Excel) tervalidasi tanpa asumsi liar.
- **Status**: **LULUS & TERVALIDASI** (Kebutuhan: Login Sesi $\rightarrow$ Dyno $\rightarrow$ Brake Test $\rightarrow$ DB $\rightarrow$ Export/Cetak).

### 🔹 Tahap 2: Penentuan Scope & Spesifikasi Produk (PRD / SRS)
- **Skill**: `prd`, `domain-modeling`, `doc-coauthoring`.
- **Artefak**: `docs/PRD.md` (Berisi functional & non-functional requirements, atomic user stories, edge cases).
- **Status**: **AKTIF (Dokumen Disiapkan)**.

### 🔹 Tahap 3: Pemilihan Stack, Arsitektur & Desain Visual
- **Skill**: `context7-docs`, `excalidraw-diagram`, `ui-ux-pro-max`, `theme-factory`.
- **Artefak**: `docs/ARCHITECTURE.md` (System Architecture, Modbus Register Map, Database Schema, Data Flow).
- **Status**: **AKTIF (Dokumen Disiapkan)**.

### 🔹 Tahap 4: Eksekusi Kode & Pengerjaan (Build)
- **Skill**: `writing-plans`, `executing-plans`, `karpathy-guidelines`, `ponytail`, `test-driven-development` (`tdd`), `codegraph`.
- **Prinsip**:
  - *Ponytail*: Solusi paling minimal & tangguh, hindari boilerplate berlebih.
  - *TDD*: Red-Green-Refactor untuk logika kalkulasi HP, efisiensi rem, dan parser data Modbus.
  - *Surgical Diffs*: Perubahan modular per layer (`core/`, `database/`, `ui/`, `exporters/`).

### 🔹 Tahap 5: Pengujian, Keamanan & Quality Assurance (QA & Security)
- **Skill**: `verification-before-completion`, `diagnosing-bugs`, `application-security-testing`, `code-review`.
- **Cakupan**:
  - Validasi koneksi putus-nyambung PLC (Auto-reconnect & packet loss handling).
  - Validasi akurasi perhitungan matematika (Dyno & Brake Test).
  - Validasi layout cetak struk 58mm/80mm, PDF A4, dan export Excel.

---

## 3. Boundary & Guardrails (Batasan Proyek)

1. **Komunikasi Hardware**: Menggunakan protokol **Modbus TCP / RTU** terstandarisasi. Tidak ada binding low-level proprietary di luar pustaka Modbus.
2. **Kemandirian Aplikasi**: Dapat berjalan secara offline (Local SQLite) tanpa ketergantungan koneksi internet.
3. **Penyimpanan**: Format database SQLite terenkapsulasi di dalam direktori aplikasi.
4. **Performa UI**: UI desktop tidak boleh lag/freeze saat polling Modbus 10-50 Hz (Wajib Worker Thread / QThread terpisah dari Main UI Thread).
