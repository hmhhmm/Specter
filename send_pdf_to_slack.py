"""
Send PDF Reports to Slack - Smart Team Routing

This script generates PDF reports and sends them to the correct Slack team channels.
Each team receives a PDF containing only their relevant alerts.
"""

import sys
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv(os.path.join("backend", ".env"))
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

# Team channel mapping
TEAM_CHANNELS = {
    "Backend": os.getenv("SLACK_BACKEND_CHANNEL", os.getenv("SLACK_CHANNEL_ID")),
    "Frontend": os.getenv("SLACK_FRONTEND_CHANNEL", os.getenv("SLACK_CHANNEL_ID")),
    "Design": os.getenv("SLACK_DESIGN_CHANNEL", os.getenv("SLACK_CHANNEL_ID")),
    "QA": os.getenv("SLACK_QA_CHANNEL", os.getenv("SLACK_CHANNEL_ID"))
}

client = WebClient(token=SLACK_BOT_TOKEN)


def create_team_pdf(team_name, alerts, output_filename):
    """
    Generate a PDF report for a specific team with only their alerts
    
    Args:
        team_name: Name of the team (Backend, Frontend, Design, QA)
        alerts: List of alert dictionaries for this team
        output_filename: Path to save the PDF
    """
    # Filter alerts for this team
    team_alerts = [alert for alert in alerts if alert.get('team') == team_name]
    
    if not team_alerts:
        print(f"⚠️  No alerts for {team_name} team")
        return None
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )
    
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
    title = Paragraph(f"{team_name} Team - Alert Report", title_style)
    elements.append(title)
    
    # Add timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_text = Paragraph(f"<i>Generated on: {timestamp}</i>", body_style)
    elements.append(date_text)
    elements.append(Spacer(1, 0.3*inch))
    
    # Add summary
    summary_heading = Paragraph(f"📊 {team_name} Team Summary", heading_style)
    elements.append(summary_heading)
    
    summary_text = Paragraph(
        f"This report contains {len(team_alerts)} alert(s) assigned to the {team_name} team. "
        f"All issues require immediate attention and have been routed to your team channel.",
        body_style
    )
    elements.append(summary_text)
    elements.append(Spacer(1, 0.4*inch))
    
    # Add each alert for this team
    for i, alert in enumerate(team_alerts, 1):
        # Alert header
        alert_header = Paragraph(
            f"ALERT {i}: {alert['diagnosis']}", 
            heading_style
        )
        elements.append(alert_header)
        elements.append(Spacer(1, 0.1*inch))
        
        # Create overview table
        overview_data = [
            ["Persona:", alert['persona']],
            ["Action Taken:", alert['action']],
            ["Expectation:", alert['expectation']],
            ["Confusion Score:", f"{alert['confusion_score']}/10"],
            ["Status:", alert['status']],
            ["Severity:", alert['severity']],
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
            for j, rec in enumerate(alert['recommendations'], 1):
                rec_text = Paragraph(f"{j}. {rec}", body_style)
                elements.append(rec_text)
            elements.append(Spacer(1, 0.1*inch))
        
        # Network Logs section
        if alert.get('network_logs'):
            network_header = Paragraph(f"<b>🌐 Network Logs:</b>", subheading_style)
            elements.append(network_header)
            for log in alert['network_logs']:
                log_text = Paragraph(f"• {log}", body_style)
                elements.append(log_text)
            elements.append(Spacer(1, 0.1*inch))
        
        # Console Logs section
        if alert.get('console_logs'):
            console_header = Paragraph(f"<b>📝 Console Logs:</b>", subheading_style)
            elements.append(console_header)
            for log in alert['console_logs']:
                log_text = Paragraph(f"• {log}", body_style)
                elements.append(log_text)
            elements.append(Spacer(1, 0.1*inch))
        
        # Add separator between alerts
        if i < len(team_alerts):
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph("_" * 100, body_style))
            elements.append(Spacer(1, 0.3*inch))
    
    # Build PDF
    doc.build(elements)
    print(f"✅ {team_name} team PDF generated: {output_filename}")
    return output_filename


def send_pdf_to_slack(team_name, pdf_path, alert_count):
    """
    Send PDF report to the team's Slack channel
    
    Args:
        team_name: Name of the team
        pdf_path: Path to the PDF file
        alert_count: Number of alerts in the report
    """
    channel = TEAM_CHANNELS.get(team_name)
    
    if not channel:
        print(f"❌ No Slack channel configured for {team_name} team")
        return False
    
    try:
        # Upload PDF to team channel
        response = client.files_upload_v2(
            channel=channel,
            file=pdf_path,
            title=f"{team_name} Team Alert Report - {datetime.now().strftime('%Y-%m-%d')}",
            initial_comment=f"📋 *{team_name} Team Alert Report*\n\n"
                          f"This report contains *{alert_count} alert(s)* that require your team's attention.\n"
                          f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                          f"Please review and take appropriate action. 🚀"
        )
        
        print(f"✅ PDF sent successfully to {team_name} team in #{channel}")
        return True
        
    except SlackApiError as e:
        print(f"❌ Slack API Error for {team_name}: {e.response['error']}")
        return False


def main():
    """
    Main function to generate PDFs and send to Slack
    """
    # Test alerts data (same as test_slack_routing.py)
    test_alerts = [
        {
            "team": "Backend",
            "persona": "Elderly User (65+)",
            "action": "Clicked 'Sign Up' button",
            "expectation": "Account creation form submits successfully",
            "confusion_score": 8,
            "status": "FAILED",
            "diagnosis": "Database connection timeout on user registration",
            "severity": "P0",
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
            "team": "Frontend",
            "persona": "Power User",
            "action": "Clicked country dropdown",
            "expectation": "Dropdown opens with country list",
            "confusion_score": 6,
            "status": "FAILED",
            "diagnosis": "Country selector API endpoint not found",
            "severity": "P1",
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
            "team": "Design",
            "persona": "Mobile User",
            "action": "Attempted to tap submit button",
            "expectation": "Button should be tappable on mobile",
            "confusion_score": 7,
            "status": "FAILED",
            "diagnosis": "Button too small for mobile touch target (28px instead of 44px minimum)",
            "severity": "P2",
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
            "team": "QA",
            "persona": "Senior User",
            "action": "Filled form and clicked submit",
            "expectation": "Form submits and shows confirmation",
            "confusion_score": 5,
            "status": "FAILED",
            "diagnosis": "Form submission unclear - needs manual review",
            "severity": "P3",
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
    
    # Create reports directory if it doesn't exist
    os.makedirs("reports/pdf_slack", exist_ok=True)
    
    print("\n" + "="*60)
    print("📄 GENERATING AND SENDING PDF REPORTS TO SLACK")
    print("="*60 + "\n")
    
    teams = ["Backend", "Frontend", "Design", "QA"]
    success_count = 0
    
    for team in teams:
        print(f"\n🔄 Processing {team} Team...")
        
        # Generate team-specific PDF
        pdf_filename = f"reports/pdf_slack/{team.lower()}_alert_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = create_team_pdf(team, test_alerts, pdf_filename)
        
        if pdf_path and os.path.exists(pdf_path):
            # Send to Slack
            team_alerts = [a for a in test_alerts if a.get('team') == team]
            if send_pdf_to_slack(team, pdf_path, len(team_alerts)):
                success_count += 1
        
        print()
    
    print("\n" + "="*60)
    print(f"✅ COMPLETE: {success_count}/{len(teams)} PDFs sent to Slack")
    print("="*60)
    print("\nCheck your Slack workspace:")
    print("  • #backend-alerts   → Backend team PDF")
    print("  • #frontend-alerts  → Frontend team PDF")
    print("  • #design-alerts    → Design team PDF")
    print("  • #qa-alerts        → QA team PDF")
    print("\n🎯 Each team received their personalized report!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
