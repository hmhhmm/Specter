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
        
        # Extract confusion_score from nested evidence structure
        ui_analysis = final_packet.get('evidence', {}).get('ui_analysis', {})
        confusion = ui_analysis.get('confusion_score', 0)
        
        # Format visual change score with context
        f_score = outcome.get('f_score', 0)
        if f_score < 20:
            f_score_text = f"{f_score}% ⚠️ No response detected"
        elif f_score < 40:
            f_score_text = f"{f_score}% ⚠️ Minimal change"
        elif f_score < 60:
            f_score_text = f"{f_score}% Moderate change"
        else:
            f_score_text = f"{f_score}% Expected change"
        
        overview_data = [
            ["Persona:", final_packet.get('persona', 'N/A')],
            ["Action Taken:", final_packet.get('action_taken', 'N/A')],
            ["Expectation:", final_packet.get('agent_expectation', 'N/A')],
            ["Confusion Score:", f"{confusion}/10"],
            ["Status:", outcome.get('status', 'FAILED')],
            ["Severity:", severity_text],
            ["Visual Change Score:", f_score_text],
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
        
        # Add explanatory note for Visual Change Score
        note_style = ParagraphStyle(
            'Note',
            parent=body_style,
            fontSize=8,
            textColor=colors.HexColor('#666666'),
            leftIndent=10,
            rightIndent=10
        )
        note_text = "<i>Note: Visual Change Score measures how much the page changed after the action. " \
                   "Low scores (0-40%) indicate the page barely responded, suggesting broken functionality or stuck flows. " \
                   "High scores (60-100%) indicate expected navigation/changes.</i>"
        note_para = Paragraph(note_text, note_style)
        elements.append(note_para)
        
        elements.append(Spacer(1, 0.2*inch))
        
        # ============ ALL ISSUES FOUND (COMPREHENSIVE SECTION) ============
        all_issues = final_packet.get('all_issues', [])
        if all_issues and len(all_issues) > 1:
            all_issues_heading = Paragraph("📋 All Issues Found Across Test", heading_style)
            elements.append(all_issues_heading)
            
            for idx, issue_report in enumerate(all_issues, 1):
                issue_outcome = issue_report.get('outcome', {})
                issue_evidence = issue_report.get('evidence', {})
                
                # Step header
                step_num = issue_report.get('step_id', idx)
                step_severity = issue_outcome.get('severity', 'P3')
                step_title = Paragraph(f"<b>Step {step_num} - {step_severity}</b>", subheading_style)
                elements.append(step_title)
                
                # Diagnosis
                diagnosis = issue_outcome.get('diagnosis', 'No diagnosis available')
                diagnosis_para = Paragraph(f"<i>Diagnosis:</i> {diagnosis}", body_style)
                elements.append(diagnosis_para)
                
                # UX Issues from this step
                ui_analysis = issue_evidence.get('ui_analysis', {})
                step_ux_issues = ui_analysis.get('issues', [])
                if step_ux_issues:
                    ux_label = Paragraph("<i>UX Observations:</i>", body_style)
                    elements.append(ux_label)
                    for ux_issue in step_ux_issues:
                        ux_para = Paragraph(f"  • {ux_issue}", body_style)
                        elements.append(ux_para)
                
                # Recommendations from this step
                step_recommendations = issue_outcome.get('recommendations', [])
                if step_recommendations:
                    rec_label = Paragraph("<i>Recommendations:</i>", body_style)
                    elements.append(rec_label)
                    for rec in step_recommendations[:3]:  # Show top 3
                        rec_para = Paragraph(f"  • {rec}", body_style)
                        elements.append(rec_para)
                
                # Visual change score and metrics with context
                f_score = issue_outcome.get('f_score', 0)
                confusion = ui_analysis.get('confusion_score', 0)
                dwell_time = issue_report.get('dwell_time_ms', 0) / 1000
                
                # Add context to visual change score
                if f_score < 20:
                    f_score_display = f"{f_score}/100 ⚠️ No response"
                elif f_score < 40:
                    f_score_display = f"{f_score}/100 ⚠️ Minimal"
                else:
                    f_score_display = f"{f_score}/100"
                
                metrics_text = f"<i>Metrics:</i> Visual Change: {f_score_display}, Confusion: {confusion}/10, Dwell Time: {dwell_time:.1f}s"
                metrics_para = Paragraph(metrics_text, body_style)
                elements.append(metrics_para)
                
                elements.append(Spacer(1, 0.1*inch))
            
            elements.append(Spacer(1, 0.1*inch))
        
        # Diagnosis
        diagnosis_heading = Paragraph("🔍 Primary Diagnosis (Most Severe)", heading_style)
        elements.append(diagnosis_heading)
        diagnosis_text = Paragraph(outcome.get('diagnosis', 'Analysis completed - see evidence for details'), body_style)
        elements.append(diagnosis_text)
        elements.append(Spacer(1, 0.15*inch))
        
        # UX Observations (CONSOLIDATED FROM ALL STEPS)
        all_ux_issues = []
        
        # Collect UX issues from all steps
        all_issue_reports = final_packet.get('all_issues', [final_packet])
        for report in all_issue_reports:
            report_evidence = report.get('evidence', {})
            report_ui_analysis = report_evidence.get('ui_analysis', {})
            report_ux_issues = report_ui_analysis.get('issues', [])
            all_ux_issues.extend(report_ux_issues)
        
        # Deduplicate while preserving order
        seen = set()
        unique_ux_issues = []
        for issue in all_ux_issues:
            if issue.lower() not in seen:
                seen.add(issue.lower())
                unique_ux_issues.append(issue)
        
        if unique_ux_issues:
            ux_heading = Paragraph("👁️ All UX Observations", heading_style)
            elements.append(ux_heading)
            for i, issue in enumerate(unique_ux_issues, 1):
                issue_para = Paragraph(f"{i}. {issue}", body_style)
                elements.append(issue_para)
            elements.append(Spacer(1, 0.15*inch))
        
        # Network Logs (ENHANCED - Show even when empty)
        network_heading = Paragraph("🌐 Network Logs", heading_style)
        elements.append(network_heading)
        network_logs = evidence.get('network_logs', [])
        if network_logs:
            for log in network_logs[:8]:  # Show up to 8 logs
                method = log.get('method', 'GET')
                url = log.get('url', '')[:80]  # Truncate long URLs
                status = log.get('status', '?')
                duration = log.get('duration', 0)
                
                # Color code by status
                status_color = 'green' if status < 400 else 'red'
                log_text = f"<b>{method}</b> {url} → <font color='{status_color}'>{status}</font>"
                if duration > 0:
                    log_text += f" ({duration}ms)"
                
                log_para = Paragraph(f"• {log_text}", body_style)
                elements.append(log_para)
        else:
            no_logs_para = Paragraph("✓ No network errors detected", body_style)
            elements.append(no_logs_para)
        elements.append(Spacer(1, 0.15*inch))
        
        # Console Logs (ENHANCED - Show errors prominently)
        console_logs = evidence.get('console_logs', [])
        if console_logs:
            console_heading = Paragraph("📝 Console Errors", heading_style)
            elements.append(console_heading)
            for log in console_logs[:8]:  # Show up to 8 logs
                log_text = str(log)[:150]  # Truncate long logs
                log_para = Paragraph(f"• {log_text}", body_style)
                elements.append(log_para)
            elements.append(Spacer(1, 0.15*inch))
        
        # Recommendations (COMPREHENSIVE - From ALL steps)
        recommendations_heading = Paragraph("💡 How to Fix It - All Recommendations", heading_style)
        elements.append(recommendations_heading)
        
        # Collect ALL recommendations from all steps
        all_recommendations = []
        all_issue_reports = final_packet.get('all_issues', [final_packet])
        for report in all_issue_reports:
            report_outcome = report.get('outcome', {})
            report_recs = report_outcome.get('recommendations', [])
            all_recommendations.extend(report_recs)
        
        # Also get from primary outcome
        recommendations = outcome.get('recommendations', [])
        all_recommendations.extend(recommendations)
        
        # Deduplicate while preserving order
        seen = set()
        unique_recommendations = []
        for rec in all_recommendations:
            if rec.lower() not in seen:
                seen.add(rec.lower())
                unique_recommendations.append(rec)
        
        # Add all unique recommendations
        if unique_recommendations:
            for i, rec in enumerate(unique_recommendations, 1):
                rec_text = Paragraph(f"{i}. {rec}", body_style)
                elements.append(rec_text)
        else:
            # If no AI recommendations, add generic ones
            generic_recs = [
                "Review the network logs and console errors above",
                "Check for API endpoint issues or backend errors",
                "Verify the expected user flow completes successfully"
            ]
            for i, rec in enumerate(generic_recs, 1):
                rec_text = Paragraph(f"{i}. {rec}", body_style)
                elements.append(rec_text)
        
        # Add UX-specific recommendations based on ALL UX issues
        if unique_ux_issues:
            elements.append(Spacer(1, 0.1*inch))
            ux_rec_para = Paragraph("<b>UX Improvements Based on Observations:</b>", subheading_style)
            elements.append(ux_rec_para)
            
            # Generate UX-specific recommendations based on ALL issues detected
            added_recs = set()
            for issue in unique_ux_issues:
                rec = None
                if 'search' in issue.lower() and ('no' in issue.lower() or 'missing' in issue.lower()):
                    rec = "Add search/filter functionality to help users quickly find options in long lists"
                elif 'long' in issue.lower() or 'scrollable' in issue.lower() or 'overwhelming' in issue.lower():
                    rec = "Implement pagination, virtualized scrolling, or group items by category to reduce cognitive load"
                elif 'small' in issue.lower() or 'touch target' in issue.lower():
                    rec = "Increase touch target size to minimum 44x44px (WCAG 2.1 standard)"
                elif 'contrast' in issue.lower():
                    rec = "Improve color contrast ratio to meet WCAG AA standards (minimum 4.5:1 for text)"
                elif 'loading' in issue.lower() or 'indicator' in issue.lower():
                    rec = "Add loading indicators, progress bars, or skeleton screens for better user feedback"
                elif 'button' in issue.lower() and 'size' in issue.lower():
                    rec = "Enlarge button size for better accessibility (recommended minimum 44x44px)"
                elif 'text' in issue.lower() and ('size' in issue.lower() or 'small' in issue.lower()):
                    rec = "Increase font size to at least 16px for better readability"
                elif 'elderly' in issue.lower() or 'senior' in issue.lower():
                    rec = "Optimize for elderly users: larger text, higher contrast, simpler navigation"
                elif 'scroll' in issue.lower() or 'form' in issue.lower():
                    rec = "Improve form layout: place form fields above the fold, reduce scrolling required"
                elif 'visible' in issue.lower() or 'hidden' in issue.lower():
                    rec = "Ensure critical form elements are immediately visible without requiring user interaction"
                else:
                    rec = f"Address UX concern: {issue[:80]}"
                
                if rec and rec not in added_recs:
                    added_recs.add(rec)
                    rec_para = Paragraph(f"• {rec}", body_style)
                    elements.append(rec_para)
        
        elements.append(Spacer(1, 0.15*inch))
        
        # Reproduction Steps (NEW SECTION)
        repro_heading = Paragraph("Reproduction Steps", heading_style)
        elements.append(repro_heading)
        
        repro_steps = [
            f"1. Navigate to target page as {final_packet.get('persona', 'Normal User')}",
            f"2. Action: {final_packet.get('action_taken', 'N/A')}",
            f"3. Expected: {final_packet.get('agent_expectation', 'Complete signup flow')}",
            f"4. Result: {outcome.get('status', 'Failure')} detected"
        ]
        
        for step in repro_steps:
            step_para = Paragraph(step, body_style)
            elements.append(step_para)
        
        elements.append(Spacer(1, 0.2*inch))
        
        # Build PDF
        doc.build(elements)
        print(f"PDF generated: {pdf_filename}")
        return pdf_filename
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
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
        print(f"No Slack channel configured for {team_name} team")
        return False
    
    if not os.path.exists(pdf_path):
        print(f"PDF file not found: {pdf_path}")
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
                          f"*Diagnosis:* {diagnosis}\n\n"
                          f"Detailed PDF report attached with network logs, UX observations, and actionable recommendations."
        )
        
        print(f"PDF sent to {team_name} team in #{channel}")
        return True
        
    except SlackApiError as e:
        print(f"Slack API Error for {team_name}: {e.response['error']}")
        return False
    except Exception as e:
        print(f"Error sending PDF: {e}")
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
        
        print(f"\nGenerating PDF report for {responsible_team} team...")
        
        # Generate PDF
        pdf_path = generate_team_alert_pdf(final_packet)
        
        if not pdf_path:
            print("Failed to generate PDF")
            return False
        
        # Send to Slack
        print(f"Sending PDF to {responsible_team} team Slack channel...")
        success = send_pdf_to_team_slack(pdf_path, responsible_team, severity, diagnosis)
        
        if success:
            print(f"PDF report delivered to {responsible_team} team!")
            return True
        else:
            print(f"Failed to send PDF to Slack")
            return False
            
    except Exception as e:
        print(f"Error in generate_and_send_alert_pdf: {e}")
        import traceback
        traceback.print_exc()
        return False
