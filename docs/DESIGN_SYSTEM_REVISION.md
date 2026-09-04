# Spesifikasi Desain UI/UX & Design System (BrakeTest)
## Versi: 2.1.0 — Dedicated Brake Test Cockpit Theme

Dokumen ini adalah spesifikasi acuan resmi revisi antarmuka UI/UX untuk aplikasi **Brake Test**, melengkapi `docs/DESIGN_SYSTEM.md`. Dokumen ini mendefinisikan layout 3-panel terintegrasi, tampilan telemetry roller (Kecepatan & RPM), indikator evaluasi hero ber-kontras tinggi, setting target kecepatan, dan pengujian lampu independen.

---

## 1. Filosofi Visual & Aturan Warna Utama

- **Theme**: *Modern Precision Light Industrial Cockpit*.
- **Aturan Warna Anti-Slop (Wajib Dipatuhi)**:
  - ❌ **DILARANG MENGGUNAKAN**: Pure `#FFFFFF` (Putih 100%) dan Pure `#000000` (Hitam 100%).
  - ✔️ **BG App Base**: `#F1F5F9` (Cool Porcelain White).
  - ✔️ **Card / Surface**: `#FAFCFE` (Crisp Off-White).
  - ✔️ **Border**: `#CBD5E1` (Crisp Slate Border).
  - ✔️ **Metric Box**: `#0F172A` (Deep Slate Navy).

---

## 2. Layout 3-Panel Modul Brake Test

```
+-------------------------------------------------------------------------------------------------------+
| TOP NAV BAR: [LOGO: DYNOTEST & BRAKE PRO]   [Registrasi (F1)] [Test (F2)] [Riwayat (F3)]  [PLC BADGE] |
+-------------------------------------------------------------------------------------------------------+
| HEADER PAGE: Modul Brake Test - Pengujian Gaya Rem & Lampu Kendaraan                [● STATUS IDLE]   |
+-------------------------------------------------------------------------------------------------------+
| [PANEL KIRI: KENDARAAN & SIKLUS] |       [PANEL TENGAH: TELEMETRI & KONTROL]    | [PANEL KANAN: EVALUASI] |
| Surface: #FAFCFE                |  +-------------------+  +-------------------+ | Surface: #FAFCFE        |
|                                 |  | GAUGE: KEC ROLLER |  | GAUGE: ROLLER RPM | |                         |
| • No. Uji    : TEST-2026-001    |  |     (0-80 km/h)   |  |    (0-3000 RPM)   | | [SETTING KEC TARGET]  |
| • No. Rangka : MH1J...          |  +-------------------+  +-------------------+ | SpinBox: [60] km/h      |
| • Bobot Uji  : 150 kg           |                                               |                         |
|                                 |  [Metric: WAKTU REM] [Metric: TORSI REM (Nm)] | [HERO BADGE STATUS REM] |
| SIKLUS PENGEREMAN:              |  [Metric: LUX METER] [Metric: RUN TIME (s)]   | ✓ LULUS (Efisiensi 68%) |
|  ✓ Akselerasi                   |                                               |                         |
|  ✓ Kec. Stabil                  |  [▶ START] [■ STOP] [💾 SIMPAN] [EXCEL] [PDF] | [HERO BADGE STATUS LUX] |
|  ● Pengereman                   |                                               | ● MENUNGGU (18,450 Lx)  |
|  ○ Berhenti                     |                                               | [▶ MULAI UJI LAMPU]     |
+-------------------------------------------------------------------------------------------------------+
| [CARD BAWAH: REALTIME CHART GAYA PENGEREMAN (N) VS WAKTU (s)]                                         |
+-------------------------------------------------------------------------------------------------------+
```

---

## 3. Spesifikasi Prominent Hero Status Badges (Evaluasi Hasil)

Panel Evaluasi Hasil (`BrakeEvalPanel`) menggunakan **Hero Badges** dengan kontras tinggi untuk visibilitas maksimal operator:

| Status Evaluasi | Background Token | Teks / Border | Styling & Ikon |
|---|---|---|---|
| **LULUS / PASS** | `#059669` (Emerald) | Teks `#FFFFFF` (Bold) | `✓ LULUS (Efisiensi XX.X%)` dengan card glow hijau. |
| **TIDAK LULUS** | `#DC2626` (Ruby Red) | Teks `#FFFFFF` (Bold) | `✕ TIDAK LULUS` dengan card glow merah. |
| **MENUNGGU** | `#475569` (Cool Slate) | Teks `#F8FAFC` (Medium) | `● MENUNGGU PENGUJIAN` |

---

## 4. Parameter Telemetri Pengujian Rem

1. **Roller Speed (km/h)**: Ditampilkan pada Circular Gauge utama (range 0 - 80 km/h).
2. **Roller RPM**: Ditampilkan pada Circular Gauge sekunder (range 0 - 3000 RPM).
3. **Braking Force (N)**: Gaya tahanan rem pada roller (0 - 10,000 N).
4. **Braking Torque (Nm)**: Torsi tahanan rem ($T = F_{\text{rem}} \times r_{\text{roller}}$, $r = 0.15\text{ m}$).
5. **Waktu Rem (s)**: Durasi pengereman dari Kecepatan Target (misal 60 km/h) hingga roller berhenti ($0\text{ km/h}$).
6. **Intensitas Lampu (Lux)**: Pengukuran intensitas cahaya sorot utama headlamp (Threshold $\ge 12,000\text{ Lux}$).
