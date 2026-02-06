import json
import anthropic
import os
from dotenv import load_dotenv

dotenv_path = os.path.join("backend", ".env")
load_dotenv(dotenv_path)

CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

if not CLAUDE_API_KEY:
    raise ValueError(f"API Key not found! Checked path: {os.path.abspath(dotenv_path)}")
    
client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

def diagnose_failure(handoff_packet):
    print("Specter (Claude 3.5) is diagnosing...")
    
    # Construct the context for Claude
    user_message = f"""
    You are Specter.AI. Analyze this failure.
    
    CONTEXT:
    - Persona: "{handoff_packet['persona']}"
    - Action: "{handoff_packet['action_taken']}"
    - Expectation: "{handoff_packet['agent_expectation']}"
    - Observation: "{handoff_packet['outcome'].get('visual_observation', 'Unknown')}"
    
    EVIDENCE:
    - Network Logs: {json.dumps(handoff_packet['evidence']['network_logs'])}
    - Console Logs: {json.dumps(handoff_packet['evidence']['console_logs'])}
    
    TASK:
    Return valid JSON (no markdown formatting) with these fields:
    - diagnosis: Short technical summary.
    - severity: "P0", "P1", or "P2".
    - responsible_team: "Backend", "Frontend", or "Design".
    """

    try:
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            messages=[
            {"role": "user", "content": user_message}
            ]
        )
        
        # Claude returns text. We parse it into JSON.
        ai_text = message.content[0].text
        ai_analysis = json.loads(ai_text)
        
        # Update the packet
        handoff_packet['outcome'].update(ai_analysis)
        
    except Exception as e:
        print(f"Claude Error: {e}")
        # Fallback just in case
        handoff_packet['outcome'].update({
            "diagnosis": "AI Analysis Failed",
            "severity": "P1",
            "responsible_team": "Manual Review"
        })
    
    return handoff_packet

