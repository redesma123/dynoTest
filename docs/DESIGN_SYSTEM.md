# Spesifikasi Desain UI/UX & Design System (DynoTest & BrakeTest)
## Versi: 2.0.0 — Modern Light Industrial Theme

Dokumen ini adalah acuan resmi desain antarmuka (*Design System & UI Guidelines*) untuk memastikan setiap coding agent membangun tampilan yang **konsisten, profesional, presisi berstandar industri otomotif**, menggunakan **Tema Terang (Light Theme)** dengan dominasi warna putih lembut/off-white, dan **tanpa menggunakan kode warna netral murni (`#FFFFFF` atau `#000000`)**.

---

## 1. Filosofi & Karakter Visual

- **Theme Style**: *Modern Precision Light Cockpit* (Instrumen laboratorium uji modern, bersih, kontras tinggi, dan elegan).
- **Nuansa**: Bersih, tajam (*crisp*), mudah dibaca dalam kondisi ruangan terang/siang hari, tanpa silau berlebih.
- **Aturan Warna Baku**:
  - ❌ **DILARANG MENGGUNAKAN**: Pure `#FFFFFF` (putih 100%) dan Pure `#000000` (hitam pekat 100%).
  - ✔️ **WAJIB MENGGUNAKAN**: Nuansa *Porcelain White, Cool Ice, Deep Slate Navy, dan High-Contrast Inks*.
  - Angka metrik penting (RPM, HP, Torsi, Braking Force, Lux) berukuran **Extra Large (Hero Typography)** dengan kontras tajam rasio $\ge 7:1$ (memenuhi standar WCAG AAA).

---

## 2. Palet Warna Resmi (Color Palette & Tokens)

```
[Background App Base: #F1F5F9] ─> [Card / Surface: #FAFCFE] ─> [Border: #CBD5E1]
     │
     ├── Accent Primary (Speed / RPM Gauge)   : #0284C7 (Cobalt Azure)
     ├── Accent Secondary (Power / Active)    : #E11D48 (Vivid Crimson)
     ├── Accent Success / Pass (Status Lulus) : #059669 (Emerald Green)
     ├── Accent Warning / Needle (Jarum Dial) : #D97706 (Amber Orange)
     ├── Accent Danger / Stop / Fail          : #DC2626 (Ruby Red)
     └── Metric Background Display Box        : #0F172A (Deep Slate Ink)
```

### Tabel Token Warna Lengkap

| Token Warna | Nilai HEX | Definisi & Penggunaan |
|---|---|---|
| `--bg-app` | `#F1F5F9` | Latar belakang dasar jendela aplikasi (*Cool Porcelain White*). |
| `--bg-surface` | `#FAFCFE` | Latar belakang card panel, form input, dan sidebar (*Crisp Off-White*). |
| `--bg-surface-elevated` | `#E2E8F0` | Latar belakang header tabel, tombol sekunder, dan area dinonaktifkan. |
| `--bg-metric-box` | `#0F172A` | Latar belakang box nilai digital hero (Deep Slate Navy berkontras tinggi). |
| `--border-subtle` | `#CBD5E1` | Garis pembatas panel, grid chart, dan divider tab (*Crisp Slate Border*). |
| `--border-focus` | `#0284C7` | Highlight border saat elemen/input aktif atau fokus. |
| `--text-primary` | `#0E1726` | Teks utama pada latar terang (*Deep Obsidian Ink*). |
| `--text-secondary` | `#475569` | Label satuan metrik, deskripsi kolom, sub-header (*Cool Slate*). |
| `--text-on-dark` | `#F8FAFC` | Teks nilai digital di dalam `--bg-metric-box` (*Bright Ice White*). |
| `--text-unit-on-dark` | `#94A3B8` | Label satuan `[rpm]`, `[km/h]` di dalam box gelap (*Muted Ice*). |
| `--accent-primary` | `#0284C7` | Arc gauge aktif, tombol aksi utama, tab aktif (*Cobalt Azure*). |
| `--accent-magenta` | `#E11D48` | Banner status `TEST AKTIF`, badge pengujian berjalan (*Vivid Crimson*). |
| `--accent-needle` | `#D97706` | Jarum penunjuk (Needle) pada dial RPM & Speedometer (*Amber Orange*). |
| `--accent-success` | `#059669` | Status kelulusan `LULUS / PASS`, tombol `START PENGUJIAN`. |
| `--accent-danger` | `#DC2626` | Tombol `EMERGENCY STOP`, batas Redline, status `TIDAK LULUS / FAIL`. |

---

## 3. Tipografi (Typography System)

- **Font UI / Label**: `Segoe UI`, `Inter`, atau `Roboto` (modern, legible, anti-aliased).
- **Font Angka / Metrik**: `Consolas`, `Roboto Mono`, atau font digital tabular berbobot tegas.

| Hierarchy | Ukuran | Weight | Warna Teks | Penggunaan |
|---|---|---|---|---|
| **Display Hero** | `48px – 56px` | Bold (`700`) | `#F8FAFC` (on dark) | Nilai digital di dalam dial & box bawah (HP/Torque/Force). |
| **Heading 1** | `22px – 26px` | Bold (`700`) | `#0E1726` | Judul Modul dan Header Halaman Utama. |
| **Heading 2** | `15px – 17px` | SemiBold (`600`)| `#0E1726` | Header Card Panel Samping (`DATA SENSOR`, `KONDISI CUACA`). |
| **Body Primary** | `13px – 14px` | Regular (`400`)| `#0E1726` | Form input, data tabel riwayat, teks tombol. |
| **Metric Label** | `11px – 12px` | Medium (`500`) | `#475569` | Satuan metrik (`[RPM]`, `[KM/H]`, `[NM]`, `[LUX]`). |

---

## 4. Anatomi Layout Antarmuka (Tema Terang)

### A. Top Navigation Bar (Header)
- **Background**: `#FAFCFE` dengan bottom border 1px solid `#CBD5E1`.
- **Kiri**: Logo Sistem (`DYNOTEST & BRAKE PRO`) dengan aksen warna `#0284C7`.
- **Tengah**: Tab Navigasi Aktif:
  - Tab Aktif: Latar `#0284C7`, teks `#F8FAFC`, border-radius 6px.
  - Tab Tidak Aktif: Latar transparan, teks `#475569`, hover `#E2E8F0`.
- **Kanan**: Badge Status Koneksi PLC:
  - Terhubung: Latar `#DCFCE7`, teks `#059669`, border `#86EFAC` (`CONNECTED 127.0.0.1:502`).
  - Terputus: Latar `#FEE2E2`, teks `#DC2626`, border `#FCA5A5` (`DISCONNECTED`).

---

### B. Layout Halaman: Modul Dyno Test

```text
+-------------------------------------------------------------------------------------------------------+
| [LOGO]  | [Registrasi]  [DYNO TEST (Aktif)]  [Brake Test]  [Riwayat]  [Setting] | PLC: CONNECTED [●]    |
+-------------------------------------------------------------------------------------------------------+
| [PANEL KIRI: CUACA & KONTROL] |          [CENTER: DUAL DIALS & CONTROLS]     | [PANEL KANAN: MONITOR] |
| Surface: #FAFCFE              |  [START (#059669)] [STOP (#DC2626)] [AKTIF]  | Surface: #FAFCFE       |
|                               |                                              |                        |
| • Suhu Udara : 28 °C          |      +-------------+    +-------------+      | • Peak HP : 14.8 HP    |
| • Tekanan    : 1013 mbar      |      |   DIAL 1    |    |   DIAL 2    |      | • Peak Nm : 12.1 Nm    |
| • Kelembaban : 65 %           |      |     RPM     |    |  KECEPATAN  |      | • Top Spd : 115 km/h   |
| • Faktor DIN : 0.998          |      |  (Ring Cyan)|    |  (Ring Cyan)|      |                        |
|                               |      |   [7,049]   |    |    [127]    |      | • AFR Status: [ 12.4 ] |
| • Pendingin  : [ 100% ]       |      +-------------+    +-------------+      | • Oil Temp  : 85 °C    |
| • [Zero / Tare Sensor]        |                                              | • Throttle  : 100 %    |
|                               |   [ BOX NILAI 1 ]   [ BOX NILAI 2 ]  [BOX 3] |                        |
|                               |     DAYA MESIN           TORSI      GAYA RODA|                        |
|                               |     58.05 [HP]         57.8 [Nm]    436 [N]  |                        |
+-------------------------------------------------------------------------------------------------------+
| [BOTTOM PANEL]: Live Curve Plot PyQtGraph (Latar: #FAFCFE, Grid: #CBD5E1, Line HP: #E11D48, Nm: #0284C7)
+-------------------------------------------------------------------------------------------------------+
```

---

### C. Layout Halaman: Modul Brake Test & Lux Meter

```text
+-------------------------------------------------------------------------------------------------------+
| [PANEL KIRI: DATA KENDARAAN]  |       [CENTER: DUAL BRAKE & LUX MONITOR]     | [PANEL KANAN: EVALUASI]|
| Surface: #FAFCFE              |  [START UJI REM (#059669)]  [RESET CYCLE]    | Surface: #FAFCFE       |
|                               |                                              |                        |
| • No. Uji    : UJI-2026-0891  |      +-------------+    +-------------+      | • STATUS REM:          |
| • No. Rangka : MH3JF...       |      |   ROLLER    |    |  GAYA REM   |      |   [ LULUS (58.4%) ]    |
| • Bobot Uji  : 1,150 kg       |      |  KECEPATAN  |    |  (TORQUE)   |      |   (Badge: #DCFCE7)     |
|                               |      |   [42 km/h] |    |   [2,850 N] |      |                        |
| • Status Siklus Pengereman:   |      +-------------+    +-------------+      | • STATUS LUX:          |
|   [1] Akselerasi Roller       |                                              |   [ LULUS (18,400 Lx)] |
|   [2] Kecepatan Stabil        |   [ BOX WAKTU REM ]   [ BOX LUX METER ] [RUN]|                        |
|   [3] Pengereman Aktif (M1)   |      2.14 [Detik]       18,450 [Lux]   15s   | • CETAK STRUK [F12]    |
|   [4] Roller Berhenti         |    (Box: #0F172A)     (Box: #0F172A)         | • EXPORT PDF [F11]     |
+-------------------------------------------------------------------------------------------------------+
| [BOTTOM GRAPH]: Profil Realtime Gaya Pengereman vs Waktu (Latar: #FAFCFE, Kurva: #0284C7)             |
+-------------------------------------------------------------------------------------------------------+
```

---

### D. Layout Halaman: Registrasi Sesi & Login

```text
+-------------------------------------------------------------------------------------------------------+
|                            REGISTRASI PENGUJIAN KENDARAAN (KIR / DYNO)                                |
+-------------------------------------------------------------------------------------------------------+
|  [Form Card Latar #FAFCFE, Border #CBD5E1]                                                           |
|                                                                                                       |
|  KOLOM KIRI (Identitas Kendaraan):           KOLOM KANAN (Data Pengujian):                            |
|  • Nomor Uji (KIR)   : [ Input Latar #F1F5F9] • Nama Penguji   : [ Input Latar #F1F5F9]               |
|  • Nomor Rangka (VIN): [ Input Latar #F1F5F9] • Tanggal & Jam  : [ Otomatis: 2026-08-31 09:30 ]       |
|  • Nomor Polisi      : [ Input Latar #F1F5F9] • Mode Uji       : (o) Dyno  ( ) Brake  ( ) Lengkap     |
|  • Jenis Kendaraan   : [ Roda 2 / Roda 4 ]    • Bobot Uji (kg) : [ 150.0 ]                            |
|  • Merk & Tipe       : [ Input Latar #F1F5F9] • Catatan Khusus : [ Input Latar #F1F5F9]               |
|                                                                                                       |
|  [ Tombol: CARI RIWAYAT (F2) ]               [ Tombol: LANJUT KE PENGUJIAN (F5) - Aksen #0284C7 ]     |
+-------------------------------------------------------------------------------------------------------+
|  [Tabel Bawah]: 5 Riwayat Pengujian Terakhir (Row genap: #FAFCFE, Row ganjil: #F1F5F9)                |
+-------------------------------------------------------------------------------------------------------+
```

---

## 5. Spesifikasi Komponen UI Kustom (Custom Widgets)

### 1. `CircularGaugeWidget` (Dual Light Cockpit Dials)
- **Komponen Render**: `QPainter` dengan antialiasing aktif.
- **Dial Background**: Lingkaran gradient halus dari `#E2E8F0` ke `#CBD5E1`.
- **Graduation Ticks**: Garis tick warna `#475569` dengan angka skala `#0E1726`.
- **Active Range Arc**: Busur warna dinamis Cobalt Azure (`#0284C7`), bertransisi ke Amber (`#D97706`), dan Redline (`#DC2626`).
- **Needle (Jarum)**: Jarum lancip presisi warna Amber Orange (`#D97706`) dengan drop shadow lembut.
- **Center Bezel**: Lingkaran tengah warna Deep Slate (`#0F172A`) dengan teks angka hero warna Ice White (`#F8FAFC`) dan satuan warna `#94A3B8`.

### 2. `DigitalMetricBox` (Kotak Angka Daya, Torsi & Gaya)
- **Tampilan**: Card persegi panjang berlatar Deep Slate (`#0F172A`), border 1px solid `#1E293B`, rounded-corner 8px.
- **Bagian Atas**: Label nama parameter (`DAYA MESIN [HP]`, `TORSI [Nm]`, `GAYA REM [N]`) dengan warna `#94A3B8`.
- **Bagian Tengah**: Angka besar monospaced tebal (`58.05`) warna `#F8FAFC`.
- **Active State**: Glow border tipis warna Azure (`#0284C7`) saat nilai aktif diperbarui.

### 3. `LiveChartWidget` (Kurva Realtime PyQtGraph)
- **Background**: `#FAFCFE` (Off-white bersih).
- **Axis & Grid**: Garis sumbu `#475569`, garis grid dashed tipis `#E2E8F0`.
- **Plot Line 1 (Horsepower)**: Garis tegas tebal 2.5px warna Crimson (`#E11D48`).
- **Plot Line 2 (Torque)**: Garis tegas tebal 2.5px warna Cobalt Azure (`#0284C7`).
- **Plot Line 3 (Brake Force)**: Garis tegas tebal 2.5px warna Emerald (`#059669`).

---

## 6. Standar Kontrol Keyboard & Ergonomi Penguji

- **`Spasi`** : Toggle Start / Stop Perekaman Data.
- **`F1`** : Pindah ke Tab Registrasi Sesi.
- **`F2`** : Pindah ke Tab Dyno Test.
- **`F3`** : Pindah ke Tab Brake Test.
- **`F4`** : Pindah ke Tab Riwayat & Laporan.
- **`F9`** : Zero / Tare Load Cell Sensor.
- **`F10`** : Export Data ke Excel (.xlsx).
- **`F11`** : Export Laporan ke PDF (A4).
- **`F12`** : Cetak Cepat Struk Thermal (ESC/POS).
- **`Esc`** : Emergency Stop / Batalkan Sesi Uji.
