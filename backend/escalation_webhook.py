# escalation_webhook.py (Rich Media Edition)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
from dotenv import load_dotenv

load_dotenv(os.path.join("backend", ".env"))
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
# CHECK YOUR CHANNEL ID!
CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")

client = WebClient(token=SLACK_BOT_TOKEN)

def send_alert(final_packet):
    outcome = final_packet['outcome']
    
    # 1. Grab the new Rich Media assets
    # Use GIF if available, otherwise use static image
    evidence_path = outcome.get('gif_path', final_packet['evidence']['screenshot_after_path'])
    f_score = outcome.get('f_score', 'N/A')
    
    print(f"Uploading Evidence (GIF) to Slack...")

    try:
        # 2. Upload the Evidence
        file_response = client.files_upload_v2(
            channel=CHANNEL_ID,
            file=evidence_path,
            title=f"Ghost Replay: {outcome.get('visual_observation', 'Failure')}",
            initial_comment=f"🚨 *Specter Alert: {outcome['severity']}* | 😡 *Frustration Score: {f_score}/100*"
        )
        
        # 3. Thread the Details + Heatmap Note
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
            text=f"*Diagnosis:* {outcome.get('diagnosis', 'N/A')}\n🔥 *Heatmap Analysis:* `Generated in backend/assets/evidence_heatmap.jpg`\n🔍 *Logs:* `{final_packet['evidence']['network_logs'][0]}`"
        )
        print("Alert Sent with GIF & Score!")
        
    except SlackApiError as e:
        print(f"Slack API Error: {e.response['error']}")