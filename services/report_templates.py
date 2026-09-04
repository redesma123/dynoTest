"""
HTML & Text Report Templates for ExportService.
Extracted to comply with docs/RULES.md §2 (max ~300 lines per file).
"""

from typing import Optional
from core.models import BrakeResult, DynoResult, TestSession, Vehicle


def build_pdf_html(session: TestSession, vehicle: Optional[Vehicle]) -> str:
    """Merender HTML string Laporan Resmi A4 untuk dikonversi ke PDF."""
    no_uji = vehicle.test_number if vehicle else "—"
    vin = session.vin
    nopol = vehicle.license_plate if vehicle else "—"
    kategori = vehicle.vehicle_category if vehicle else "Roda 2"
    merk_tipe = vehicle.brand_model if vehicle else "—"
    bobot = f"{vehicle.vehicle_weight_kg:.0f} kg" if vehicle else "150 kg"
    penguji = session.inspector_name
    waktu_uji = str(session.tested_at or "—")
    mode = session.test_mode.value if hasattr(session.test_mode, "value") else str(session.test_mode)
    catatan = session.notes or "—"

    # Dyno section
    dyno_html = ""
    if session.dyno_result:
        dr: DynoResult = session.dyno_result
        dyno_html = f"""
        <h3 style="color: #0F172A; border-bottom: 2px solid #0284C7; padding-bottom: 4px; margin-top: 20px;">
            HASIL PENGUJIAN DYNO TEST (PERFORMA MESIN)
        </h3>
        <table style="width: 100%; border-collapse: collapse; margin-top: 8px;">
            <tr style="background-color: #E2E8F0; font-weight: bold; text-align: left;">
                <th style="padding: 8px; border: 1px solid #CBD5E1;">Parameter Metrik</th>
                <th style="padding: 8px; border: 1px solid #CBD5E1;">Nilai Puncak</th>
                <th style="padding: 8px; border: 1px solid #CBD5E1;">Satuan</th>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E1;">Daya Maksimal (Peak Power)</td>
                <td style="padding: 8px; border: 1px solid #CBD5E1; font-weight: bold; color: #E11D48;">{dr.max_power_hp:.2f}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E1;">HP</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E1;">Torsi Maksimal (Peak Torque)</td>
                <td style="padding: 8px; border: 1px solid #CBD5E1; font-weight: bold; color: #0284C7;">{dr.max_torque_nm:.1f}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E1;">Nm</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E1;">Kecepatan Maksimal (Top Speed)</td>
                <td style="padding: 8px; border: 1px solid #CBD5E1; font-weight: bold;">{dr.max_speed_kmh:.1f}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E1;">km/h</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E1;">Putaran Mesin Maksimal (Max RPM)</td>
                <td style="padding: 8px; border: 1px solid #CBD5E1;">{int(dr.max_rpm):,}</td>
                <td style="padding: 8px; border: 1px solid #CBD5E1;">RPM</td>
            </tr>
        </table>
        """

    # Brake section
    brake_html = ""
    if session.brake_result:
        br: BrakeResult = session.brake_result
        b_pass = br.brake_pass_status.value == "PASS" if hasattr(br.brake_pass_status, "value") else str(br.brake_pass_status) == "PASS"
        l_pass = br.lux_pass_status.value == "PASS" if hasattr(br.lux_pass_status, "value") else str(br.lux_pass_status) == "PASS"
        o_pass = br.overall_status.value == "PASS" if hasattr(br.overall_status, "value") else str(br.overall_status) == "PASS"

        b_badge = "<span style='color: #059669; font-weight: bold;'>● LULUS (PASS)</span>" if b_pass else "<span style='color: #DC2626; font-weight: bold;'>● TIDAK LULUS (FAIL)</span>"
        l_badge = "<span style='color: #059669; font-weight: bold;'>● LULUS (PASS)</span>" if l_pass else "<span style='color: #DC2626; font-weight: bold;'>● TIDAK LULUS (FAIL)</span>"
        o_badge = "<span style='background-color: #DCFCE7; color: #059669; padding: 4px 8px; border-radius: 4px; font-weight: bold;'>LULUS (PASS)</span>" if o_pass else "<span style='background-color: #FEE2E2; color: #DC2626; padding: 4px 8px; border-radius: 4px; font-weight: bold;'>TIDAK LULUS (FAIL)</span>"

        brake_html = f"""
        <h3 style="color: #0F172A; border-bottom: 2px solid #0284C7; padding-bottom: 4px; margin-top: 20px;">
            HASIL PENGUJIAN BRAKE TEST & LUX METER
        </h3>
        <table style="width: 100%; border-collapse: collapse; margin-top: 8px;">
            <tr style="background-color: #E2E8F0; font-weight: bold; text-align: left;">
                <th style="padding: 8px; border: 1px solid #CBD5E1;">Item Pengujian</th>
                <th style="padding: 8px; border: 1px solid #CBD5E1;">Hasil Ukur</th>
                <th style="padding: 8px; border: 1px solid #CBD5E1;">Ambang Batas / Syarat</th>
                <th style="padding: 8px; border: 1px solid #CBD5E1;">Status Evaluasi</th>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E1;">Efisiensi Pengereman</td>
                <td style="padding: 8px; border: 1px solid #CBD5E1; font-weight: bold;">{br.braking_efficiency_pct:.1f} %</td>
                <td style="padding: 8px; border: 1px solid #CBD5E1;">Min 50.0 %</td>
                <td style="padding: 8px; border: 1px solid #CBD5E1;">{b_badge}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E1;">Waktu Pengereman</td>
                <td style="padding: 8px; border: 1px solid #CBD5E1;">{br.braking_time_s:.2f} s</td>
                <td style="padding: 8px; border: 1px solid #CBD5E1;">Maks 4.00 s</td>
                <td style="padding: 8px; border: 1px solid #CBD5E1;">—</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E1;">Gaya Pengereman Puncak</td>
                <td style="padding: 8px; border: 1px solid #CBD5E1; font-weight: bold;">{br.peak_braking_force_n:,.0f} N</td>
                <td style="padding: 8px; border: 1px solid #CBD5E1;">—</td>
                <td style="padding: 8px; border: 1px solid #CBD5E1;">—</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #CBD5E1;">Intensitas Cahaya Lampu</td>
                <td style="padding: 8px; border: 1px solid #CBD5E1; font-weight: bold;">{br.lux_intensity:,.0f} Lux</td>
                <td style="padding: 8px; border: 1px solid #CBD5E1;">Min 12,000 Lux</td>
                <td style="padding: 8px; border: 1px solid #CBD5E1;">{l_badge}</td>
            </tr>
            <tr style="background-color: #FAFCFE; font-weight: bold;">
                <td colspan="3" style="padding: 8px; border: 1px solid #CBD5E1; text-align: right;">STATUS KELULUSAN AKHIR:</td>
                <td style="padding: 8px; border: 1px solid #CBD5E1;">{o_badge}</td>
            </tr>
        </table>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8"/>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #0E1726; margin: 20px; line-height: 1.4; }}
            .header-table {{ width: 100%; border-bottom: 3px double #0284C7; padding-bottom: 12px; margin-bottom: 20px; }}
            .title {{ font-size: 20px; font-weight: bold; color: #0284C7; text-transform: uppercase; }}
            .subtitle {{ font-size: 12px; color: #475569; }}
            .info-table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
            .info-table td {{ padding: 6px 10px; border: 1px solid #E2E8F0; font-size: 13px; }}
            .info-table td.label {{ background-color: #F1F5F9; font-weight: 600; width: 22%; color: #475569; }}
            .sign-table {{ width: 100%; margin-top: 40px; text-align: center; font-size: 12px; }}
        </style>
    </head>
    <body>
        <table class="header-table">
            <tr>
                <td style="width: 70%;">
                    <div class="title">DYNOTEST & BRAKE PRO</div>
                    <div class="subtitle">AUTO-TECH SYSTEMS — UJI BERKALA KENDARAAN BERMOTOR</div>
                </td>
                <td style="width: 30%; text-align: right; font-size: 11px; color: #475569;">
                    <b>DOKUMEN RESMI</b><br/>
                    Sesi ID: #{session.id}<br/>
                    Tanggal: {waktu_uji}
                </td>
            </tr>
        </table>

        <h3 style="color: #0F172A; border-bottom: 2px solid #0284C7; padding-bottom: 4px;">
            IDENTITAS KENDARAAN & DATA PENGUJI
        </h3>
        <table class="info-table">
            <tr>
                <td class="label">No. Uji KIR</td>
                <td style="font-weight: bold; color: #0284C7;">{no_uji}</td>
                <td class="label">Nama Penguji</td>
                <td style="font-weight: bold;">{penguji}</td>
            </tr>
            <tr>
                <td class="label">No. Rangka (VIN)</td>
                <td>{vin}</td>
                <td class="label">Mode Uji</td>
                <td>{mode}</td>
            </tr>
            <tr>
                <td class="label">No. Polisi</td>
                <td>{nopol}</td>
                <td class="label">Bobot Uji</td>
                <td>{bobot}</td>
            </tr>
            <tr>
                <td class="label">Kategori / Merk</td>
                <td>{kategori} — {merk_tipe}</td>
                <td class="label">Catatan Khusus</td>
                <td>{catatan}</td>
            </tr>
        </table>

        {dyno_html}
        {brake_html}

        <table class="sign-table">
            <tr>
                <td style="width: 50%;">
                    Mengetahui,<br/>
                    <b>Kepala Penguji KIR</b><br/><br/><br/><br/>
                    ( ____________________ )
                </td>
                <td style="width: 50%;">
                    Petugas Operator Uji,<br/>
                    <b>AUTO-TECH SYSTEMS</b><br/><br/><br/><br/>
                    ( <b>{penguji}</b> )
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


def build_receipt_text(session: TestSession, vehicle: Optional[Vehicle]) -> str:
    """Merender format teks ringkas untuk struk thermal (58mm/80mm)."""
    no_uji = vehicle.test_number if vehicle else "—"
    vin = session.vin
    penguji = session.inspector_name
    waktu = str(session.tested_at or "—")

    lines = [
        "========================================",
        "        DYNOTEST & BRAKE PRO            ",
        "       AUTO-TECH SYSTEMS KIR            ",
        "========================================",
        f"Sesi ID   : #{session.id}",
        f"Waktu     : {waktu}",
        f"No. Uji   : {no_uji}",
        f"VIN       : {vin}",
        f"Penguji   : {penguji}",
        "----------------------------------------",
    ]

    if session.dyno_result:
        dr = session.dyno_result
        lines.extend([
            "[HASIL DYNO TEST]",
            f"Peak Power  : {dr.max_power_hp:.2f} HP",
            f"Peak Torque : {dr.max_torque_nm:.1f} Nm",
            f"Top Speed   : {dr.max_speed_kmh:.1f} km/h",
            "----------------------------------------",
        ])

    if session.brake_result:
        br = session.brake_result
        o_pass = br.overall_status.value == "PASS" if hasattr(br.overall_status, "value") else str(br.overall_status) == "PASS"
        status_str = "LULUS (PASS)" if o_pass else "TIDAK LULUS (FAIL)"

        lines.extend([
            "[HASIL BRAKE TEST & LUX]",
            f"Gaya Rem    : {br.peak_braking_force_n:,.0f} N",
            f"Efisiensi   : {br.braking_efficiency_pct:.1f} %",
            f"Waktu Rem   : {br.braking_time_s:.2f} s",
            f"Lampu Lux   : {br.lux_intensity:,.0f} Lux",
            f"STATUS      : {status_str}",
            "----------------------------------------",
        ])

    lines.extend([
        "   Terima Kasih atas Kunjungan Anda!   ",
        "========================================",
    ])

    return "\n".join(lines)
