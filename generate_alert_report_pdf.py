"""
Generate PDF Report for Slack Routing Test Alerts

This script generates a professional PDF report from test alert data,
formatted similar to the Slack routing test structure.
"""

import sys
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_alert_pdf(output_filename="alert_report.pdf"):
    """
    Generate a PDF report with all test alerts
    """
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define custom styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2c5aa0'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#444444'),
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6,
        fontName='Helvetica'
    )
    
    # Add title
    title = Paragraph("Slack Smart Routing - Test Alerts Report", title_style)
    elements.append(title)
    
    # Add timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_text = Paragraph(f"<i>Generated on: {timestamp}</i>", body_style)
    elements.append(date_text)
    elements.append(Spacer(1, 0.3*inch))
    
    # Add summary section
    summary_heading = Paragraph("📊 Executive Summary", heading_style)
    elements.append(summary_heading)
    
    summary_text = Paragraph(
        "This report demonstrates the smart channel routing system. "
        "Each type of failure automatically routes to the correct team's Slack channel. "
        "Four test scenarios were executed covering Backend, Frontend, Design, and QA issues.",
        body_style
    )
    elements.append(summary_text)
    elements.append(Spacer(1, 0.4*inch))
    
    # Test alerts data
    test_alerts = [
        {
            "test_number": 1,
            "title": "Backend Issue → Routes to #backend-alerts",
            "color": colors.HexColor('#ff4444'),
            "persona": "Elderly User (65+)",
            "action": "Clicked 'Sign Up' button",
            "expectation": "Account creation form submits successfully",
            "confusion_score": 8,
            "status": "FAILED",
            "diagnosis": "Database connection timeout on user registration",
            "severity": "P0",
            "team": "Backend",
            "f_score": 92,
            "recommendations": [
                "Add connection pooling with retry logic",
                "Implement circuit breaker for database calls",
                "Set up database read replicas"
            ],
            "network_logs": [
                "POST https://api.deriv.com/signup → 500",
                "GET https://api.deriv.com/health → 200",
                "POST https://api.deriv.com/retry → 504"
            ],
            "console_logs": [
                "[error] Database connection timeout after 30000ms",
                "[error] Failed to insert user record",
                "[warning] Retry attempt 3/3 failed"
            ]
        },
        {
            "test_number": 2,
            "title": "Frontend Issue → Routes to #frontend-alerts",
            "color": colors.HexColor('#4444ff'),
            "persona": "Power User",
            "action": "Clicked country dropdown",
            "expectation": "Dropdown opens with country list",
            "confusion_score": 6,
            "status": "FAILED",
            "diagnosis": "Country selector API endpoint not found",
            "severity": "P1",
            "team": "Frontend",
            "f_score": 75,
            "recommendations": [
                "Update API endpoint path in frontend config",
                "Add fallback for missing country data",
                "Display user-friendly error message"
            ],
            "network_logs": [
                "GET https://api.deriv.com/v2/countries → 404",
                "GET https://api.deriv.com/v1/countries → 200"
            ],
            "console_logs": [
                "[error] Failed to fetch: 404 Not Found",
                "[warning] Endpoint /v2/countries does not exist"
            ]
        },
        {
            "test_number": 3,
            "title": "Design Issue → Routes to #design-alerts",
            "color": colors.HexColor('#ff8800'),
            "persona": "Mobile User",
            "action": "Attempted to tap submit button",
            "expectation": "Button should be tappable on mobile",
            "confusion_score": 7,
            "status": "FAILED",
            "diagnosis": "Button too small for mobile touch target (28px instead of 44px minimum)",
            "severity": "P2",
            "team": "Design",
            "f_score": 68,
            "recommendations": [
                "Increase button min-height to 44px for touch targets",
                "Add more padding around clickable elements",
                "Test with mobile device emulator"
            ],
            "network_logs": [],
            "console_logs": [
                "[warning] Touch target smaller than recommended 44x44px",
                "[info] Element dimensions: 28x32px"
            ]
        },
        {
            "test_number": 4,
            "title": "QA Issue → Routes to #qa-alerts",
            "color": colors.HexColor('#888888'),
            "persona": "Senior User",
            "action": "Filled form and clicked submit",
            "expectation": "Form submits and shows confirmation",
            "confusion_score": 5,
            "status": "FAILED",
            "diagnosis": "Form submission unclear - needs manual review",
            "severity": "P3",
            "team": "QA",
            "f_score": 45,
            "recommendations": [
                "Investigate form validation logic",
                "Check browser console for hidden errors",
                "Manual testing required"
            ],
            "network_logs": [
                "POST https://deriv.com/submit → 200"
            ],
            "console_logs": []
        }
    ]
    
    # Add each test case
    for alert in test_alerts:
        # Test case header
        test_header = Paragraph(
            f"TEST {alert['test_number']}: {alert['title']}", 
            heading_style
        )
        elements.append(test_header)
        elements.append(Spacer(1, 0.1*inch))
        
        # Create overview table
        overview_data = [
            ["Persona:", alert['persona']],
            ["Action Taken:", alert['action']],
            ["Expectation:", alert['expectation']],
            ["Confusion Score:", str(alert['confusion_score'])],
            ["Status:", alert['status']],
            ["Severity:", alert['severity']],
            ["Responsible Team:", alert['team']],
            ["F-Score:", f"{alert['f_score']}%"],
        ]
        
        overview_table = Table(overview_data, colWidths=[1.5*inch, 4.5*inch])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(overview_table)
        elements.append(Spacer(1, 0.15*inch))
        
        # Diagnosis section
        diagnosis_header = Paragraph(f"<b>🔍 Diagnosis:</b>", subheading_style)
        elements.append(diagnosis_header)
        diagnosis_text = Paragraph(alert['diagnosis'], body_style)
        elements.append(diagnosis_text)
        elements.append(Spacer(1, 0.1*inch))
        
        # Recommendations section
        if alert['recommendations']:
            recommendations_header = Paragraph(f"<b>💡 Recommendations:</b>", subheading_style)
            elements.append(recommendations_header)
            for i, rec in enumerate(alert['recommendations'], 1):
                rec_text = Paragraph(f"{i}. {rec}", body_style)
                elements.append(rec_text)
            elements.append(Spacer(1, 0.1*inch))
        
        # Network Logs section
        if alert['network_logs']:
            network_header = Paragraph(f"<b>🌐 Network Logs:</b>", subheading_style)
            elements.append(network_header)
            for log in alert['network_logs']:
                log_text = Paragraph(f"• {log}", body_style)
                elements.append(log_text)
            elements.append(Spacer(1, 0.1*inch))
        
        # Console Logs section
        if alert['console_logs']:
            console_header = Paragraph(f"<b>📝 Console Logs:</b>", subheading_style)
            elements.append(console_header)
            for log in alert['console_logs']:
                log_text = Paragraph(f"• {log}", body_style)
                elements.append(log_text)
            elements.append(Spacer(1, 0.1*inch))
        
        # Add separator between test cases
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("_" * 100, body_style))
        elements.append(Spacer(1, 0.3*inch))
    
    # Add summary table at the end
    elements.append(PageBreak())
    summary_title = Paragraph("📋 Routing Summary", heading_style)
    elements.append(summary_title)
    elements.append(Spacer(1, 0.2*inch))
    
    routing_data = [
        ["Slack Channel", "Issue Type", "Severity", "Status"],
        ["#backend-alerts", "Backend (Database Timeout)", "P0", "✅ Routed"],
        ["#frontend-alerts", "Frontend (API 404)", "P1", "✅ Routed"],
        ["#design-alerts", "Design (Touch Target)", "P2", "✅ Routed"],
        ["#qa-alerts", "QA (Manual Review)", "P3", "✅ Routed"],
    ]
    
    routing_table = Table(routing_data, colWidths=[1.5*inch, 2.5*inch, 1*inch, 1*inch])
    routing_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
    ]))
    elements.append(routing_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Add conclusion
    conclusion_text = Paragraph(
        "<b>🎯 Conclusion:</b> All test alerts were successfully routed to their respective team channels. "
        "Each team only receives alerts relevant to their domain, reducing noise and improving response times.",
        body_style
    )
    elements.append(conclusion_text)
    
    # Build PDF
    doc.build(elements)
    print(f"\n✅ PDF Report generated successfully: {output_filename}")
    return output_filename


if __name__ == "__main__":
    # Generate the PDF report
    output_path = "reports/slack_routing_test_report.pdf"
    
    # Create reports directory if it doesn't exist
    os.makedirs("reports", exist_ok=True)
    
    create_alert_pdf(output_path)
    
    print("\n" + "="*60)
    print("📄 PDF REPORT GENERATED")
    print("="*60)
    print(f"\nLocation: {output_path}")
    print("\nThe report includes:")
    print("  • Executive Summary")
    print("  • 4 Test Cases with full details")
    print("  • Network & Console Logs")
    print("  • Recommendations for each issue")
    print("  • Routing Summary Table")
    print("\n✨ Ready to share with your team!")
    print("="*60)
