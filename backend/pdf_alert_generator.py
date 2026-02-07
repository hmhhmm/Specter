"""
Real-time PDF Report Generator for Slack Alerts

This module generates PDF reports in real-time when failures are detected
and automatically sends them to the corresponding team's Slack channel.
"""

from datetime import datetime
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv(os.path.join("backend", ".env"))
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

TEAM_CHANNELS = {
    "Backend": os.getenv("SLACK_BACKEND_CHANNEL", os.getenv("SLACK_CHANNEL_ID")),
    "Frontend": os.getenv("SLACK_FRONTEND_CHANNEL", os.getenv("SLACK_CHANNEL_ID")),
    "Design": os.getenv("SLACK_DESIGN_CHANNEL", os.getenv("SLACK_CHANNEL_ID")),
    "QA": os.getenv("SLACK_QA_CHANNEL", os.getenv("SLACK_CHANNEL_ID"))
}

client = WebClient(token=SLACK_BOT_TOKEN)


def generate_team_alert_pdf(final_packet, output_dir="reports/pdf_alerts"):
    """
    Generate a PDF report for a single alert
    
    Args:
        final_packet: Alert data packet
        output_dir: Directory to save PDFs
        
    Returns:
        Path to generated PDF or None if failed
    """
    try:
        outcome = final_packet['outcome']
        evidence = final_packet.get('evidence', {})
        responsible_team = outcome.get('responsible_team', 'QA')
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        severity = outcome.get('severity', 'P3')
        pdf_filename = os.path.join(
            output_dir, 
            f"{responsible_team}_{severity}_{timestamp}.pdf"
        )
        
        # Create PDF document
        doc = SimpleDocTemplate(
            pdf_filename,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=50,
        )
        
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=11,
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
        
        # Add title with severity
        severity_text = outcome.get('severity', 'P3')
        title = Paragraph(f"{severity_text} Alert - {responsible_team} Team", title_style)
        elements.append(title)
        
        # Add timestamp
        timestamp_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_para = Paragraph(f"<i>Generated: {timestamp_text}</i>", body_style)
        elements.append(date_para)
        elements.append(Spacer(1, 0.3*inch))
        
        # Alert Overview
        overview_heading = Paragraph("🚨 Alert Overview", heading_style)
        elements.append(overview_heading)
        
        overview_data = [
            ["Persona:", final_packet.get('persona', 'N/A')],
            ["Action Taken:", final_packet.get('action_taken', 'N/A')],
            ["Expectation:", final_packet.get('agent_expectation', 'N/A')],
            ["Confusion Score:", f"{final_packet.get('confusion_score', 0)}/10"],
            ["Status:", outcome.get('status', 'FAILED')],
            ["Severity:", severity_text],
            ["F-Score:", f"{outcome.get('f_score', 0)}%"],
            ["Responsible Team:", responsible_team],
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
        elements.append(Spacer(1, 0.2*inch))
        
        # Diagnosis
        diagnosis_heading = Paragraph("🔍 Diagnosis", subheading_style)
        elements.append(diagnosis_heading)
        diagnosis_text = Paragraph(outcome.get('diagnosis', 'No diagnosis available'), body_style)
        elements.append(diagnosis_text)
        elements.append(Spacer(1, 0.15*inch))
        
        # Recommendations
        recommendations = outcome.get('recommendations', [])
        if recommendations:
            rec_heading = Paragraph("💡 Recommendations", subheading_style)
            elements.append(rec_heading)
            for i, rec in enumerate(recommendations, 1):
                rec_text = Paragraph(f"{i}. {rec}", body_style)
                elements.append(rec_text)
            elements.append(Spacer(1, 0.15*inch))
        
        # Network Logs
        network_logs = evidence.get('network_logs', [])
        if network_logs:
            network_heading = Paragraph("🌐 Network Logs", subheading_style)
            elements.append(network_heading)
            for log in network_logs[:5]:  # Limit to 5 logs
                log_text = f"{log.get('method', 'GET')} {log.get('url', '')} → {log.get('status', '?')}"
                log_para = Paragraph(f"• {log_text}", body_style)
                elements.append(log_para)
            elements.append(Spacer(1, 0.15*inch))
        
        # Console Logs
        console_logs = evidence.get('console_logs', [])
        if console_logs:
            console_heading = Paragraph("📝 Console Logs", subheading_style)
            elements.append(console_heading)
            for log in console_logs[:5]:  # Limit to 5 logs
                log_para = Paragraph(f"• {log}", body_style)
                elements.append(log_para)
            elements.append(Spacer(1, 0.15*inch))
        
        # Build PDF
        doc.build(elements)
        print(f"✅ PDF generated: {pdf_filename}")
        return pdf_filename
        
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        return None


def send_pdf_to_team_slack(pdf_path, team_name, severity, diagnosis):
    """
    Send PDF report to the team's Slack channel
    
    Args:
        pdf_path: Path to the PDF file
        team_name: Name of the team (Backend, Frontend, Design, QA)
        severity: Severity level (P0, P1, P2, P3)
        diagnosis: Brief diagnosis text
        
    Returns:
        bool: True if successful, False otherwise
    """
    channel = TEAM_CHANNELS.get(team_name)
    
    if not channel:
        print(f"❌ No Slack channel configured for {team_name} team")
        return False
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return False
    
    try:
        severity_emoji = {
            "P0": "🚨",
            "P1": "⚠️",
            "P2": "⚡",
            "P3": "ℹ️"
        }.get(severity, "🔍")
        
        # Upload PDF to team channel
        response = client.files_upload_v2(
            channel=channel,
            file=pdf_path,
            title=f"{severity} Alert Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            initial_comment=f"{severity_emoji} *{severity} Alert for {team_name} Team*\n\n"
                          f"*Diagnosis:* {diagnosis[:200]}...\n\n"
                          f"📄 Detailed report attached. Please review and take action."
        )
        
        print(f"✅ PDF sent to {team_name} team in #{channel}")
        return True
        
    except SlackApiError as e:
        print(f"❌ Slack API Error for {team_name}: {e.response['error']}")
        return False
    except Exception as e:
        print(f"❌ Error sending PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_and_send_alert_pdf(final_packet):
    """
    Generate PDF report and send to corresponding team's Slack channel
    
    This is called automatically when an alert is triggered
    
    Args:
        final_packet: Complete failure analysis data
        
    Returns:
        bool: True if PDF was generated and sent successfully
    """
    try:
        outcome = final_packet['outcome']
        responsible_team = outcome.get('responsible_team', 'QA')
        severity = outcome.get('severity', 'P3')
        diagnosis = outcome.get('diagnosis', 'Issue detected')
        
        print(f"\n📄 Generating PDF report for {responsible_team} team...")
        
        # Generate PDF
        pdf_path = generate_team_alert_pdf(final_packet)
        
        if not pdf_path:
            print("❌ Failed to generate PDF")
            return False
        
        # Send to Slack
        print(f"📤 Sending PDF to {responsible_team} team Slack channel...")
        success = send_pdf_to_team_slack(pdf_path, responsible_team, severity, diagnosis)
        
        if success:
            print(f"✅ PDF report delivered to {responsible_team} team!")
            return True
        else:
            print(f"❌ Failed to send PDF to Slack")
            return False
            
    except Exception as e:
        print(f"❌ Error in generate_and_send_alert_pdf: {e}")
        import traceback
        traceback.print_exc()
        return False
