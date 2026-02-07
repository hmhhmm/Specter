"""Slack alert notification module."""

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
from dotenv import load_dotenv

load_dotenv(os.path.join("backend", ".env"))
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")

client = WebClient(token=SLACK_BOT_TOKEN)

def send_alert(final_packet):
    """
    Send failure alert to Slack with evidence.
    
    Args:
        final_packet: Complete failure analysis data
    """
    outcome = final_packet['outcome']
    
    gif_path = outcome.get('gif_path')
    if gif_path and os.path.exists(gif_path):
        evidence_path = gif_path
    else:
        evidence_path = final_packet['evidence']['screenshot_after_path']
        if not os.path.exists(evidence_path):
            print(f"Warning: Screenshot not found at {evidence_path}")
            evidence_path = final_packet['evidence'].get('screenshot_before_path')
            if not evidence_path or not os.path.exists(evidence_path):
                print("Error: No valid evidence files found")
                return
    
    f_score = outcome.get('f_score', 'N/A')
    print(f"Uploading evidence ({'GIF' if gif_path and os.path.exists(gif_path) else 'Screenshot'}) to Slack...")

    try:
        file_response = client.files_upload_v2(
            channel=CHANNEL_ID,
            file=evidence_path,
            title=f"Failure Evidence: {outcome.get('visual_observation', 'Analysis')}",
            initial_comment=f"*Alert: {outcome['severity']}* | *F-Score: {f_score}/100*"
        )
        
        thread_ts = None
        try:
            file_shares = file_response.get('file', {}).get('shares', {})
            if 'public' in file_shares and CHANNEL_ID in file_shares['public']:
                thread_ts = file_shares['public'][CHANNEL_ID][0]['ts']
        except:
            pass

        client.chat_postMessage(
            channel=CHANNEL_ID,
            thread_ts=thread_ts,
            text=f"*Diagnosis:* {outcome.get('diagnosis', 'N/A')}\n*Heatmap:* Generated in reports\n*Logs:* {final_packet['evidence']['network_logs'][0]}"
        )
        print("Alert sent successfully")
        
    except SlackApiError as e:
        print(f"Slack API Error: {e.response['error']}")