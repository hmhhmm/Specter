# escalation_webhook.py (Crash-Proof Version)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
from dotenv import load_dotenv

load_dotenv(os.path.join("backend", ".env"))

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")

client = WebClient(token=SLACK_BOT_TOKEN)

def send_alert(final_packet):
    outcome = final_packet['outcome']
   
    evidence_path = final_packet['evidence']['screenshot_after_path']
    
    print(f"Uploading evidence to Slack...")

    try:
        # 1. Upload the Screenshot
        # We explicitly set 'initial_comment' to ensure the main alert is seen immediately
        file_response = client.files_upload_v2(
            channel=CHANNEL_ID,
            file=evidence_path,
            title=f"Evidence: {outcome.get('visual_observation', 'Failure')}",
            initial_comment=f"*Specter Alert: {outcome['severity']}* detected by {outcome['responsible_team']}"
        )
        
        print("Image Uploaded Successfully.")

        # 2. Try to Thread the Technical Details (Safely)
        thread_ts = None
        try:
            # Try to grab the timestamp from the file share
            # This is the line that was crashing before
            file_shares = file_response.get('file', {}).get('shares', {})
            if 'public' in file_shares and CHANNEL_ID in file_shares['public']:
                thread_ts = file_shares['public'][CHANNEL_ID][0]['ts']
        except Exception as e:
            print(f"Could not thread message (Minor API issue): {e}")

        # 3. Post the Diagnosis (Threaded if possible, otherwise normal)
        client.chat_postMessage(
            channel=CHANNEL_ID,
            thread_ts=thread_ts, # If None, it just posts a normal message (No Crash!)
            text=f"📋 *Diagnosis:* {outcome.get('diagnosis', 'N/A')}\n🔍 *Logs:* `{final_packet['evidence']['network_logs'][0]}`"
        )
        print("Diagnosis Sent!")
        
    except SlackApiError as e:
        print(f"Slack API Error: {e.response['error']}")
    except FileNotFoundError:
        print(f"Image File Not Found at: {evidence_path}")