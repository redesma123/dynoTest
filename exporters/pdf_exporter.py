"""
PDF Exporter untuk DynoTest & BrakeTest.
Menghasilkan dokumen PDF laporan pengujian berformat A4 resmi menggunakan ReportLab.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from core.models import BrakeResult, DynoResult, EvaluationStatus, TestSession, Vehicle


def _get_styles():
    base_styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocTitle",
        parent=base_styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#0F172A"),
        alignment=1,  # Center
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#475569"),
        alignment=1,
    )
    section_style = ParagraphStyle(
        "SectionHead",
        parent=base_styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#0284C7"),
    )
    cell_style = ParagraphStyle(
        "TableCell",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#0E1726"),
    )
    cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=base_styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#0E1726"),
    )
    cell_center_bold = ParagraphStyle(
        "TableCellCenterBold",
        parent=base_styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        alignment=1,
        textColor=colors.HexColor("#0E1726"),
    )
    return {
        "title": title_style,
        "subtitle": subtitle_style,
        "section": section_style,
        "cell": cell_style,
        "cell_bold": cell_bold,
        "cell_center_bold": cell_center_bold,
    }


def export_dyno_to_pdf(
    filepath: str,
    session: Optional[TestSession],
    vehicle: Optional[Vehicle],
    result: DynoResult,
) -> bool:
    """Export lembar hasil uji Dyno Test ke file PDF A4."""
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
    )
    styles = _get_styles()
    story = []

    # 1. Header Instansi
    story.append(Paragraph("AUTO-TECH SYSTEMS", styles["title"]))
    story.append(Paragraph("LEMBAR HASIL PENGUJIAN PERFORMA KENDARAAN (DYNO TEST)", styles["subtitle"]))
    story.append(Spacer(1, 0.4 * cm))

    # Divider bar
    divider_data = [[""]]
    divider_table = Table(divider_data, colWidths=[17.4 * cm], rowHeights=[2])
    divider_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0284C7"))]))
    story.append(divider_table)
    story.append(Spacer(1, 0.4 * cm))

    # 2. Identitas Kendaraan & Pengujian Table
    story.append(Paragraph("IDENTITAS KENDARAAN & PENGUJI", styles["section"]))
    story.append(Spacer(1, 0.2 * cm))

    id_data = [
        [
            Paragraph("Nomor Uji (KIR)", styles["cell"]),
            Paragraph(vehicle.test_number if vehicle else "—", styles["cell_bold"]),
            Paragraph("ID Sesi", styles["cell"]),
            Paragraph(f"#{result.session_id}", styles["cell_bold"]),
        ],
        [
            Paragraph("Nomor Rangka (VIN)", styles["cell"]),
            Paragraph(vehicle.vin if vehicle else "—", styles["cell_bold"]),
            Paragraph("Nama Penguji", styles["cell"]),
            Paragraph(session.inspector_name if session else "—", styles["cell_bold"]),
        ],
        [
            Paragraph("Nomor Polisi", styles["cell"]),
            Paragraph(vehicle.license_plate if vehicle else "—", styles["cell_bold"]),
            Paragraph("Waktu Pengujian", styles["cell"]),
            Paragraph(str(session.tested_at) if session and session.tested_at else datetime.now().strftime("%Y-%m-%d %H:%M"), styles["cell_bold"]),
        ],
        [
            Paragraph("Merk & Tipe", styles["cell"]),
            Paragraph(vehicle.brand_model if vehicle else "—", styles["cell_bold"]),
            Paragraph("Bobot Kendaraan", styles["cell"]),
            Paragraph(f"{vehicle.vehicle_weight_kg:.1f} kg" if vehicle else "150.0 kg", styles["cell_bold"]),
        ],
    ]

    id_table = Table(id_data, colWidths=[4.2 * cm, 4.5 * cm, 4.2 * cm, 4.5 * cm])
    id_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(id_table)
    story.append(Spacer(1, 0.5 * cm))

    # 3. Hasil Peak Telemetri
    story.append(Paragraph("HASIL PENGUKURAN PUNCAK (PEAK PERFORMANCE)", styles["section"]))
    story.append(Spacer(1, 0.2 * cm))

    peak_headers = [
        Paragraph("<b>Parameter Uji</b>", styles["cell_center_bold"]),
        Paragraph("<b>Nilai Maksimal</b>", styles["cell_center_bold"]),
        Paragraph("<b>Satuan</b>", styles["cell_center_bold"]),
        Paragraph("<b>RPM Saat Puncak</b>", styles["cell_center_bold"]),
    ]

    peak_rows = [
        peak_headers,
        [Paragraph("Daya Mesin (Power)", styles["cell"]), Paragraph(f"{result.max_power_hp:.2f}", styles["cell_center_bold"]), Paragraph("HP", styles["cell"]), Paragraph(f"{result.rpm_at_peak_power:.0f} RPM", styles["cell_center_bold"])],
        [Paragraph("Torsi Mesin (Torque)", styles["cell"]), Paragraph(f"{result.max_torque_nm:.1f}", styles["cell_center_bold"]), Paragraph("Nm", styles["cell"]), Paragraph(f"{result.rpm_at_peak_torque:.0f} RPM", styles["cell_center_bold"])],
        [Paragraph("Kecepatan Puncak (Top Speed)", styles["cell"]), Paragraph(f"{result.max_speed_kmh:.1f}", styles["cell_center_bold"]), Paragraph("km/h", styles["cell"]), Paragraph("—", styles["cell_center_bold"])],
        [Paragraph("RPM Maksimal Mesin", styles["cell"]), Paragraph(f"{result.max_rpm:.0f}", styles["cell_center_bold"]), Paragraph("RPM", styles["cell"]), Paragraph("—", styles["cell_center_bold"])],
    ]

    peak_table = Table(peak_rows, colWidths=[6.4 * cm, 3.8 * cm, 3.2 * cm, 4.0 * cm])
    peak_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(peak_table)
    story.append(Spacer(1, 0.8 * cm))

    # 4. Tanda Tangan Penguji & Catatan
    sign_data = [
        [Paragraph("Catatan Khusus:", styles["cell_bold"]), Paragraph("Petugas Penguji,", styles["cell_center_bold"])],
        [Paragraph(session.notes if session and session.notes else "Kondisi mesin normal saat pengujian berlangsung.", styles["cell"]), Paragraph("<br/><br/><br/>( " + (session.inspector_name if session else "....................") + " )", styles["cell_center_bold"])],
    ]
    sign_table = Table(sign_data, colWidths=[10.4 * cm, 7.0 * cm])
    sign_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(sign_table)

    doc.build(story)
    return True


def export_brake_to_pdf(
    filepath: str,
    session: Optional[TestSession],
    vehicle: Optional[Vehicle],
    result: BrakeResult,
) -> bool:
    """Export lembar hasil uji Brake Test ke file PDF A4."""
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
    )
    styles = _get_styles()
    story = []

    story.append(Paragraph("AUTO-TECH SYSTEMS", styles["title"]))
    story.append(Paragraph("LEMBAR HASIL PENGUJIAN REM & INTENSITAS LAMPU (BRAKE TEST)", styles["subtitle"]))
    story.append(Spacer(1, 0.4 * cm))

    divider_data = [[""]]
    divider_table = Table(divider_data, colWidths=[17.4 * cm], rowHeights=[2])
    divider_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0284C7"))]))
    story.append(divider_table)
    story.append(Spacer(1, 0.4 * cm))

    # Identitas
    story.append(Paragraph("IDENTITAS KENDARAAN & PENGUJI", styles["section"]))
    story.append(Spacer(1, 0.2 * cm))

    id_data = [
        [
            Paragraph("Nomor Uji (KIR)", styles["cell"]),
            Paragraph(vehicle.test_number if vehicle else "—", styles["cell_bold"]),
            Paragraph("ID Sesi", styles["cell"]),
            Paragraph(f"#{result.session_id}", styles["cell_bold"]),
        ],
        [
            Paragraph("Nomor Rangka (VIN)", styles["cell"]),
            Paragraph(vehicle.vin if vehicle else "—", styles["cell_bold"]),
            Paragraph("Nama Penguji", styles["cell"]),
            Paragraph(session.inspector_name if session else "—", styles["cell_bold"]),
        ],
        [
            Paragraph("Nomor Polisi", styles["cell"]),
            Paragraph(vehicle.license_plate if vehicle else "—", styles["cell_bold"]),
            Paragraph("Waktu Pengujian", styles["cell"]),
            Paragraph(str(session.tested_at) if session and session.tested_at else datetime.now().strftime("%Y-%m-%d %H:%M"), styles["cell_bold"]),
        ],
        [
            Paragraph("Bobot Uji", styles["cell"]),
            Paragraph(f"{vehicle.vehicle_weight_kg:.1f} kg" if vehicle else "150.0 kg", styles["cell_bold"]),
            Paragraph("Mode Uji", styles["cell"]),
            Paragraph("BRAKE TEST", styles["cell_bold"]),
        ],
    ]

    id_table = Table(id_data, colWidths=[4.2 * cm, 4.5 * cm, 4.2 * cm, 4.5 * cm])
    id_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(id_table)
    story.append(Spacer(1, 0.5 * cm))

    # Evaluasi Hasil
    story.append(Paragraph("EVALUASI KELAYAKAN REM & LAMPU UTAMA", styles["section"]))
    story.append(Spacer(1, 0.2 * cm))

    b_pass = result.brake_pass_status == EvaluationStatus.PASS
    l_pass = result.lux_pass_status == EvaluationStatus.PASS
    o_pass = result.overall_status == EvaluationStatus.PASS

    eval_headers = [
        Paragraph("<b>Parameter Pengujian</b>", styles["cell_center_bold"]),
        Paragraph("<b>Hasil Ukur</b>", styles["cell_center_bold"]),
        Paragraph("<b>Standar Ambang Batas</b>", styles["cell_center_bold"]),
        Paragraph("<b>Status Evaluasi</b>", styles["cell_center_bold"]),
    ]

    eval_rows = [
        eval_headers,
        [Paragraph("Efisiensi Pengereman", styles["cell"]), Paragraph(f"{result.braking_efficiency_pct:.1f} %", styles["cell_center_bold"]), Paragraph("≥ 50.0 %", styles["cell_center_bold"]), Paragraph("<b>LULUS</b>" if b_pass else "<b>TIDAK LULUS</b>", styles["cell_center_bold"])],
        [Paragraph("Gaya Pengereman Puncak", styles["cell"]), Paragraph(f"{result.peak_braking_force_n:,.0f} N", styles["cell_center_bold"]), Paragraph("—", styles["cell_center_bold"]), Paragraph("TERCATAT", styles["cell_center_bold"])],
        [Paragraph("Waktu Pengereman", styles["cell"]), Paragraph(f"{result.braking_time_s:.2f} s", styles["cell_center_bold"]), Paragraph("≤ 4.00 s", styles["cell_center_bold"]), Paragraph("LULUS" if result.braking_time_s <= 4.0 else "TIDAK LULUS", styles["cell_center_bold"])],
        [Paragraph("Intensitas Lampu Utama", styles["cell"]), Paragraph(f"{result.lux_intensity:,.0f} Lux", styles["cell_center_bold"]), Paragraph("≥ 12,000 Lux", styles["cell_center_bold"]), Paragraph("<b>LULUS</b>" if l_pass else "<b>TIDAK LULUS</b>", styles["cell_center_bold"])],
        [Paragraph("<b>KESIMPULAN AKHIR</b>", styles["cell_bold"]), Paragraph("<b>LULUS UJI</b>" if o_pass else "<b>TIDAK LULUS</b>", styles["cell_center_bold"]), Paragraph("Semua Uji Lulus", styles["cell_center_bold"]), Paragraph("<b>PASS</b>" if o_pass else "<b>FAIL</b>", styles["cell_center_bold"])],
    ]

    eval_table = Table(eval_rows, colWidths=[6.0 * cm, 3.8 * cm, 4.0 * cm, 3.6 * cm])
    eval_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("BACKGROUND", (3, 1), (3, 1), colors.HexColor("#DCFCE7") if b_pass else colors.HexColor("#FEE2E2")),
        ("BACKGROUND", (3, 4), (3, 4), colors.HexColor("#DCFCE7") if l_pass else colors.HexColor("#FEE2E2")),
        ("BACKGROUND", (0, 5), (-1, 5), colors.HexColor("#DCFCE7") if o_pass else colors.HexColor("#FEE2E2")),
    ]))
    story.append(eval_table)
    story.append(Spacer(1, 0.8 * cm))

    # Tanda Tangan
    sign_data = [
        [Paragraph("Catatan Petugas:", styles["cell_bold"]), Paragraph("Petugas Penguji,", styles["cell_center_bold"])],
        [Paragraph(session.notes if session and session.notes else "Pengujian rem dan intensitas cahaya lampu telah diverifikasi.", styles["cell"]), Paragraph("<br/><br/><br/>( " + (session.inspector_name if session else "....................") + " )", styles["cell_center_bold"])],
    ]
    sign_table = Table(sign_data, colWidths=[10.4 * cm, 7.0 * cm])
    sign_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(sign_table)

    doc.build(story)
    return True


def export_history_to_pdf(filepath: str, rows: List[Dict[str, Any]]) -> bool:
    """Export daftar riwayat pengujian ke file PDF."""
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )
    styles = _get_styles()
    story = []

    story.append(Paragraph("AUTO-TECH SYSTEMS", styles["title"]))
    story.append(Paragraph("REKAPITULASI LAPORAN RIWAYAT PENGUJIAN KENDARAAN", styles["subtitle"]))
    story.append(Spacer(1, 0.4 * cm))

    headers = [
        Paragraph("<b>Tanggal & Waktu</b>", styles["cell_center_bold"]),
        Paragraph("<b>No. Uji (KIR)</b>", styles["cell_center_bold"]),
        Paragraph("<b>No. Rangka</b>", styles["cell_center_bold"]),
        Paragraph("<b>Penguji</b>", styles["cell_center_bold"]),
        Paragraph("<b>Mode</b>", styles["cell_center_bold"]),
    ]
    table_data = [headers]

    for r in rows:
        mode_val = r.get("test_mode", "—")
        if hasattr(mode_val, "value"):
            mode_val = mode_val.value
        table_data.append([
            Paragraph(str(r.get("tested_at", "—")), styles["cell"]),
            Paragraph(str(r.get("test_number", "—")), styles["cell_bold"]),
            Paragraph(str(r.get("vin", "—")), styles["cell"]),
            Paragraph(str(r.get("inspector_name", "—")), styles["cell"]),
            Paragraph(str(mode_val), styles["cell_center_bold"]),
        ])

    table = Table(table_data, colWidths=[4.0 * cm, 3.5 * cm, 4.5 * cm, 3.5 * cm, 2.5 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(table)

    doc.build(story)
    return True
