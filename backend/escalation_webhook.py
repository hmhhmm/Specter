"""Slack alert notification module with smart channel routing."""

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
import json
from dotenv import load_dotenv
from .root_cause_intelligence import RootCauseIntelligence
from .pdf_alert_generator import generate_and_send_alert_pdf

load_dotenv(os.path.join("backend", ".env"))
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

# SMART CHANNEL ROUTING - Each team gets their own channel
# Only the responsible team sees the alert - no spam!
TEAM_CHANNELS = {
    "Backend": os.getenv("SLACK_BACKEND_CHANNEL", os.getenv("SLACK_CHANNEL_ID")),
    "Frontend": os.getenv("SLACK_FRONTEND_CHANNEL", os.getenv("SLACK_CHANNEL_ID")),
    "Design": os.getenv("SLACK_DESIGN_CHANNEL", os.getenv("SLACK_CHANNEL_ID")),
    "QA": os.getenv("SLACK_QA_CHANNEL", os.getenv("SLACK_CHANNEL_ID"))
}

# Team mentions (optional - for tagging within their channel)
TEAM_MENTIONS = {
    "Backend": os.getenv("SLACK_BACKEND_TEAM", "@backend-team"),
    "Frontend": os.getenv("SLACK_FRONTEND_TEAM", "@frontend-team"),
    "Design": os.getenv("SLACK_DESIGN_TEAM", "@design-team"),
    "QA": os.getenv("SLACK_QA_TEAM", "@qa-team")
}

client = WebClient(token=SLACK_BOT_TOKEN)

def send_alert(final_packet):
    """
    Send failure alert to Slack with SMART CHANNEL ROUTING.
    Each team only sees alerts relevant to them - no spam!
    
    Args:
        final_packet: Complete failure analysis data
    """
    outcome = final_packet['outcome']
    evidence = final_packet['evidence']
    
    # Determine responsible team and route to their channel
    responsible_team = outcome.get('responsible_team', 'QA')
    target_channel = TEAM_CHANNELS.get(responsible_team)
    team_mention = TEAM_MENTIONS.get(responsible_team, "@channel")
    
    if not target_channel:
        print(f"Warning: No channel configured for {responsible_team} team. Skipping alert.")
        return
    
    # Get severity and f-score
    severity = outcome.get('severity', 'P3')
    f_score = outcome.get('f_score', 'N/A')
    confusion_score = final_packet.get('confusion_score', 0)
    diagnosis = outcome.get('diagnosis', 'Issue detected')
    
    # ROOT CAUSE INTELLIGENCE - Find similar historical issues
    rc_intel = RootCauseIntelligence()
    similar_issues_text = ""
    try:
        # Build minimal report structure for root cause analysis
        report_structure = {
            'outcome': outcome,
            'steps': [final_packet]  # Wrap in array for compatibility
        }
        analysis = rc_intel.analyze_with_root_cause(report_structure)
        
        if analysis['similar_issues']:
            top_match = analysis['similar_issues'][0]
            similar_issues_text = f"\n\n🔗 *Root Cause Intelligence:*\nThis error is similar to *{top_match['test_id']}* ({top_match['similarity']}% match) from {top_match['timestamp']} - possibly related.\n"
            
            if len(analysis['similar_issues']) > 1:
                similar_issues_text += f"_{len(analysis['similar_issues'])} total similar incidents detected - pattern confirmed._"
    except Exception as e:
        print(f"Root cause analysis warning: {e}")
    
    # Build severity emoji
    severity_emoji = {
        "P0": "🚨",
        "P1": "⚠️",
        "P2": "⚡",
        "P3": "ℹ️"
    }.get(severity, "🔍")
    
    gif_path = outcome.get('gif_path')
    if gif_path and os.path.exists(gif_path):
        evidence_path = gif_path
        evidence_type = "GIF"
    else:
        evidence_path = evidence.get('screenshot_after_path')
        evidence_type = "Screenshot"
        if not evidence_path or not os.path.exists(evidence_path):
            evidence_path = evidence.get('screenshot_before_path')
            if not evidence_path or not os.path.exists(evidence_path):
                print("Error: No valid evidence files found")
                return
    
    print(f"📤 Smart Routing: {responsible_team} team → #{target_channel}")
    print(f"   Uploading {evidence_type}...")

    try:
        # Build alert message with team mention (optional within their channel)
        alert_header = f"{severity_emoji} *{severity} Alert* - {team_mention}"
        
        # Build confusion indicator
        confusion_indicator = "🟢 Low" if confusion_score < 4 else "🟡 Moderate" if confusion_score < 7 else "🔴 Critical"
        
        # Build detailed message with network logs
        network_logs_text = "None" if not evidence.get('network_logs') else "\n".join([
            f"• {log.get('method', 'GET')} {log.get('url', '')} → {log.get('status', '?')}"
            for log in evidence['network_logs'][:3]
        ])
        
        console_logs_text = "None" if not evidence.get('console_logs') else "\n".join([
            f"• {log}" for log in evidence['console_logs'][:3]
        ])
        
        # Build reproduction steps
        action_taken = final_packet.get('action_taken', 'Unknown action')
        expectation = final_packet.get('agent_expectation', 'Expected outcome')
        
        reproduction_steps = f"""
*Reproduction Steps:*
1. Navigate to target page as {final_packet.get('persona', 'user')}
2. Action: {action_taken}
3. Expected: {expectation}
4. Result: Failure detected
"""
        
        detailed_message = f"""
*Diagnosis:* {diagnosis}
*F-Score (Frustration):* {f_score}/100
*User Confusion:* {confusion_score}/10 {confusion_indicator}
*Responsible Team:* {responsible_team}

{reproduction_steps}

*Network Logs:*
{network_logs_text}

*Console Logs:*
{console_logs_text}

*Recommendations:*
{chr(10).join([f"• {rec}" for rec in outcome.get('recommendations', ['Review and fix'])])}
{similar_issues_text}
"""
        
        # Upload evidence file to the TEAM'S CHANNEL
        file_response = client.files_upload_v2(
            channel=target_channel,
            file=evidence_path,
            title=f"{severity}: {diagnosis[:100]}",
            initial_comment=alert_header
        )
        
        # Get thread timestamp
        thread_ts = None
        try:
            file_shares = file_response.get('file', {}).get('shares', {})
            if 'public' in file_shares and target_channel in file_shares['public']:
                thread_ts = file_shares['public'][target_channel][0]['ts']
        except:
            pass

        # Post detailed info in thread
        client.chat_postMessage(
            channel=target_channel,
            thread_ts=thread_ts,
            text=detailed_message
        )
        
        print(f"✅ Alert sent successfully to {responsible_team} team in #{target_channel}")
        
        # Generate and send PDF report to the team
        try:
            print(f"\n📄 Generating PDF report for {responsible_team} team...")
            generate_and_send_alert_pdf(final_packet)
        except Exception as pdf_error:
            print(f"⚠️  PDF generation failed (non-critical): {pdf_error}")
        
    except SlackApiError as e:
        print(f"❌ Slack API Error: {e.response['error']}")