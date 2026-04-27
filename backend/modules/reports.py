"""
Report Generation Module - PDF security audit report using ReportLab
"""
from flask import Blueprint, send_file, jsonify
from modules.db import vulnerabilities_col, logs_col, transactions_col
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from datetime import datetime
import io

reports_bp = Blueprint("reports", __name__)

def build_pdf():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle("title", parent=styles["Title"], fontSize=18,
                                  textColor=colors.HexColor("#1a237e"), spaceAfter=6)
    heading_style = ParagraphStyle("heading", parent=styles["Heading2"], fontSize=13,
                                    textColor=colors.HexColor("#283593"), spaceAfter=4)
    normal_style = styles["Normal"]

    # Title
    story.append(Paragraph("ATM Network Security Audit Report", title_style))
    story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", normal_style))
    story.append(Spacer(1, 0.2*inch))

    # Executive Summary
    story.append(Paragraph("1. Executive Summary", heading_style))
    vulns = list(vulnerabilities_col.find({}, {"_id": 0}))
    high = sum(1 for v in vulns if v.get("risk") == "High")
    med  = sum(1 for v in vulns if v.get("risk") == "Medium")
    low  = sum(1 for v in vulns if v.get("risk") == "Low")
    story.append(Paragraph(
        f"This report presents findings from an automated security audit of the ATM network. "
        f"Total vulnerabilities found: {len(vulns)} — High: {high}, Medium: {med}, Low: {low}.",
        normal_style
    ))
    story.append(Spacer(1, 0.15*inch))

    # Vulnerability Table
    story.append(Paragraph("2. Vulnerability Findings", heading_style))
    if vulns:
        table_data = [["Port", "Service", "Threat", "STRIDE", "Risk", "Mitigation"]]
        for v in vulns:
            table_data.append([
                v.get("port", "-"),
                v.get("service", "-"),
                v.get("threat", "-"),
                v.get("stride", "-"),
                v.get("risk", "-"),
                Paragraph(v.get("mitigation", "-"), ParagraphStyle("small", fontSize=7))
            ])

        col_widths = [0.5*inch, 0.8*inch, 1.5*inch, 0.6*inch, 0.7*inch, 2.5*inch]
        t = Table(table_data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a237e")),
            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
            ("FONTSIZE",   (0, 0), (-1, 0), 9),
            ("FONTSIZE",   (0, 1), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#e8eaf6")]),
            ("GRID",       (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN",     (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(t)
    else:
        story.append(Paragraph("No vulnerabilities recorded. Run a scan first.", normal_style))
    story.append(Spacer(1, 0.15*inch))

    # STRIDE Analysis
    story.append(Paragraph("3. STRIDE Threat Model Analysis", heading_style))
    stride_map = {"S": "Spoofing", "T": "Tampering", "R": "Repudiation",
                  "I": "Info Disclosure", "D": "DoS", "E": "Privilege Escalation"}
    stride_counts = {k: 0 for k in stride_map}
    for v in vulns:
        key = v.get("stride", "I")
        if key in stride_counts:
            stride_counts[key] += 1

    stride_data = [["STRIDE Category", "Count", "Description"]]
    for k, name in stride_map.items():
        stride_data.append([name, str(stride_counts[k]),
                             "Detected" if stride_counts[k] > 0 else "Not detected"])
    st = Table(stride_data, colWidths=[2*inch, 1*inch, 3.5*inch])
    st.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#283593")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTSIZE",   (0, 0), (-1, -1), 9),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#e8eaf6")]),
    ]))
    story.append(st)
    story.append(Spacer(1, 0.15*inch))

    # Recent Audit Logs
    story.append(Paragraph("4. Recent Audit Logs", heading_style))
    logs = list(logs_col.find({}, {"_id": 0}).sort("timestamp", -1).limit(10))
    if logs:
        log_data = [["Timestamp", "Event", "User", "Details"]]
        for log in logs:
            log_data.append([
                log.get("timestamp", "-")[:19],
                log.get("event_type", "-"),
                str(log.get("user_id", "-"))[:12],
                Paragraph(str(log.get("details", "-")), ParagraphStyle("small", fontSize=7))
            ])
        lt = Table(log_data, colWidths=[1.5*inch, 1.3*inch, 1.2*inch, 2.6*inch])
        lt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a237e")),
            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
            ("FONTSIZE",   (0, 0), (-1, -1), 8),
            ("GRID",       (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#e8eaf6")]),
        ]))
        story.append(lt)
    else:
        story.append(Paragraph("No audit logs available.", normal_style))

    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph("5. Recommendations", heading_style))
    recs = [
        "• Enforce TLS 1.3 on all ATM-to-server communications",
        "• Implement HSM for PIN encryption key management",
        "• Deploy network segmentation: ATM VLAN isolated from corporate",
        "• Enable rate limiting on authentication endpoints",
        "• Conduct quarterly penetration testing",
        "• Maintain PCI-DSS compliance with annual QSA audit"
    ]
    for r in recs:
        story.append(Paragraph(r, normal_style))

    doc.build(story)
    buffer.seek(0)
    return buffer

@reports_bp.route("/generate-pdf", methods=["GET"])
def generate_pdf():
    try:
        pdf_buffer = build_pdf()
        return send_file(
            pdf_buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"atm_security_audit_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.pdf"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
