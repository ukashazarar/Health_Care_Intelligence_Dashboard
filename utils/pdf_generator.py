import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_pdf_report(metrics_data=None):
    buffer = io.BytesIO()
    
    # Page setup with 0.5 inch margins for professional layout
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    story = []
    styles = getSampleStyleSheet()

    # --- Executive Color Palette ---
    NAVY_PRIMARY = colors.HexColor("#0F172A")    # Deep Slate / Navy Header
    BLUE_ACCENT  = colors.HexColor("#0B5FFF")    # Brand Accent
    TEXT_DARK    = colors.HexColor("#1E293B")    # High contrast body text
    TEXT_MUTED   = colors.HexColor("#64748B")    # Subtitle / Captions
    BG_LIGHT     = colors.HexColor("#F8FAFC")    # Alternate Row Background
    BORDER_COLOR = colors.HexColor("#CBD5E1")    # Subtle Grid Borders
    CRITICAL_RED = colors.HexColor("#991B1B")    # Risk Highlight
    GOOD_GREEN   = colors.HexColor("#166534")    # Healthy Metric

    # --- Professional Typography Styles ---
    doc_title_style = ParagraphStyle(
        'DocTitle', parent=styles['Heading1'],
        fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=NAVY_PRIMARY, spaceAfter=2
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=9, textColor=BLUE_ACCENT, spaceAfter=10
    )

    meta_style = ParagraphStyle(
        'MetaText', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, textColor=TEXT_MUTED, alignment=2
    )

    section_heading = ParagraphStyle(
        'SectionHeading', parent=styles['Heading2'],
        fontName='Helvetica-Bold', fontSize=12, leading=15, textColor=NAVY_PRIMARY,
        spaceBefore=12, spaceAfter=6
    )

    body_text = ParagraphStyle(
        'BodyTextCustom', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=12, textColor=TEXT_DARK
    )

    tbl_header = ParagraphStyle(
        'TblHeader', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.white
    )

    tbl_cell = ParagraphStyle(
        'TblCell', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=11, textColor=TEXT_DARK
    )

    tbl_cell_bold = ParagraphStyle(
        'TblCellBold', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8, leading=11, textColor=TEXT_DARK
    )

    alert_text = ParagraphStyle(
        'AlertText', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8, leading=11, textColor=CRITICAL_RED
    )

    # --- Header Banner Section ---
    header_data = [
        [
            Paragraph("Healthcare Operations & Intelligence Report", doc_title_style),
            Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%d %b %Y, %I:%M %p')}<br/><b>Scope:</b> Hospital-Wide Operations", meta_style)
        ],
        [
            Paragraph("EXECUTIVE PERFORMANCE ANALYSIS & DECISION SUPPORT DRAFT", subtitle_style),
            Paragraph("", meta_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[380, 160])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BLUE_ACCENT, spaceAfter=10))

    # --- Section 1: Executive Summary & Critical Insights ---
    story.append(Paragraph("1. Executive Summary & Operational Risk Assessment", section_heading))
    exec_summary = (
        "This enterprise intelligence report consolidates real-time performance indicators across hospital departments "
        "including Clinical Operations, Emergency Services, Operating Theatres (OT), Pharmacy, Laboratory, and Ambulance Services. "
        "Current metrics indicate operational bottlenecks in <b>ER Avg Wait Time (47.9 mins)</b> and <b>Readmission Rates (52.1%)</b>, "
        "requiring immediate clinical workflow and discharge planning optimization."
    )
    story.append(Paragraph(exec_summary, body_text))
    story.append(Spacer(1, 8))

    # --- Section 2: Core Hospital Executive KPIs ---
    story.append(Paragraph("2. Executive Level Key Performance Indicators (KPIs)", section_heading))
    
    kpi_table_data = [
        [Paragraph("Core Indicator", tbl_header), Paragraph("Current Value", tbl_header), Paragraph("Target / Benchmark", tbl_header), Paragraph("Operational Impact", tbl_header)],
        [Paragraph("Total Hospital Revenue", tbl_cell_bold), Paragraph("₹ 30.52 Cr", tbl_cell), Paragraph("₹ 28.00 Cr Target", tbl_cell), Paragraph("11,000 Total Patients Served", tbl_cell)],
        [Paragraph("Bed Occupancy Rate", tbl_cell_bold), Paragraph("50.9%", tbl_cell), Paragraph("75.0% Optimal", tbl_cell), Paragraph("Healthy capacity margin available", tbl_cell)],
        [Paragraph("ER Avg Wait Time", tbl_cell_bold), Paragraph("47.9 min", alert_text), Paragraph("< 15.0 min Target", tbl_cell), Paragraph("Critical overload; patient triage delay", alert_text)],
        [Paragraph("Readmission Rate", tbl_cell_bold), Paragraph("52.1%", alert_text), Paragraph("< 10.0% Standard", tbl_cell), Paragraph("Requires discharge review & followup", alert_text)],
        [Paragraph("Avg Patient Satisfaction", tbl_cell_bold), Paragraph("3.0 / 5.0", tbl_cell), Paragraph("> 4.2 / 5.0 Target", tbl_cell), Paragraph("Moderate satisfaction level", tbl_cell)],
        [Paragraph("Avg Length of Stay (ALOS)", tbl_cell_bold), Paragraph("7.4 days", tbl_cell), Paragraph("5.0 - 7.0 days", tbl_cell), Paragraph("Standard operational turnover", tbl_cell)],
        [Paragraph("OT Operating Cases", tbl_cell_bold), Paragraph("3,000", tbl_cell), Paragraph("2,500 Baseline", tbl_cell), Paragraph("High volume case management", tbl_cell)],
    ]

    kpi_table = Table(kpi_table_data, colWidths=[130, 85, 115, 210])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY_PRIMARY),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('BACKGROUND', (0,1), (-1,-1), BG_LIGHT),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 10))

    # --- Section 3: Department-Wise Operational Deep-Dive ---
    story.append(Paragraph("3. Multi-Department Intelligence & Metrics Breakdown", section_heading))

    dept_table_data = [
        [Paragraph("Department", tbl_header), Paragraph("Key Metric / Volume", tbl_header), Paragraph("Performance Benchmark", tbl_header), Paragraph("Actionable Insight", tbl_header)],
        
        # Emergency
        [Paragraph("Emergency (ER)", tbl_cell_bold), Paragraph("47.9 min Wait Time", alert_text), Paragraph("< 15 min Target", tbl_cell), Paragraph("Deploy additional triage staff during peak hours.", tbl_cell)],
        
        # Ambulance
        [Paragraph("Ambulance Fleet", tbl_cell_bold), Paragraph("3,734 Total Trips<br/>23.4 min Response", tbl_cell), Paragraph("15 min Target<br/>₹ 20.1 L Fuel Cost", tbl_cell), Paragraph("High response time; optimize fleet deployment & routing.", tbl_cell)],
        
        # Operating Theatre
        [Paragraph("OT Operations", tbl_cell_bold), Paragraph("3,000 Procedures", tbl_cell), Paragraph("5.2% Cancellation Rate", tbl_cell), Paragraph("Schedule utilization is stable; maintain pre-op prep.", tbl_cell)],
        
        # Pharmacy
        [Paragraph("Pharmacy", tbl_cell_bold), Paragraph("₹ 4.82 Cr Revenue", tbl_cell), Paragraph("98.4% Fulfillment", tbl_cell), Paragraph("Stock levels healthy; low stockouts reported.", tbl_cell)],
        
        # Laboratory
        [Paragraph("Laboratory", tbl_cell_bold), Paragraph("14,250 Tests", tbl_cell), Paragraph("3.2 hrs Avg Turnaround", tbl_cell), Paragraph("Turnaround within limits; pathology workload balanced.", tbl_cell)],
        
        # Staff Scheduling
        [Paragraph("Staffing & Shifts", tbl_cell_bold), Paragraph("84.2% Attendance", tbl_cell), Paragraph("92.0% Target", tbl_cell), Paragraph("Night shift shortages identified in ICU & Emergency.", alert_text)],
    ]

    dept_table = Table(dept_table_data, colWidths=[110, 120, 130, 180])
    dept_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BLUE_ACCENT),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
    ]))
    story.append(dept_table)
    story.append(Spacer(1, 10))

    # --- Section 4: Strategic Recommendations for Executive Management ---
    story.append(Paragraph("4. Strategic Decision-Making Recommendations", section_heading))
    
    rec_data = [
        [Paragraph("1", tbl_cell_bold), Paragraph("<b>Triage & Emergency Optimization:</b> Restructure ER admission protocols and deploy fast-track beds to reduce average response and waiting times from 47.9 mins to under 20 mins.", body_text)],
        [Paragraph("2", tbl_cell_bold), Paragraph("<b>Discharge & Readmission Protocol:</b> Implement mandatory post-discharge patient follow-up within 48 hours to curb high readmission rates (52.1%).", body_text)],
        [Paragraph("3", tbl_cell_bold), Paragraph("<b>Ambulance Fleet Dispatch:</b> Integrate GPS-based dynamic routing to bring average fleet arrival time down from 23.4 mins closer to the 15-min target.", body_text)],
    ]
    
    rec_table = Table(rec_data, colWidths=[20, 520])
    rec_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(rec_table)

    # --- Document Footer Divider ---
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.5, color=TEXT_MUTED, spaceAfter=8))
    story.append(Paragraph("<b>Confidential Document</b> — Internal Healthcare Operations Intelligence & Decision Support Report.", ParagraphStyle('Footer', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=7.5, textColor=TEXT_MUTED, alignment=1)))

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer