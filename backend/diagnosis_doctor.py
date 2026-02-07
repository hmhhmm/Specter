# diagnosis_doctor.py (Rules-Based Edition)
import json
import os
from dotenv import load_dotenv
import anthropic

load_dotenv(os.path.join("backend", ".env"))
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

def diagnose_failure(handoff_packet):
    print("🧠 Specter (Claude Haiku) is diagnosing...")
    
    # Get the deterministic severity we calculated
    calc_severity = handoff_packet['outcome'].get('calculated_severity', 'P3')

    user_message = f"""
    You are Specter.AI. Analyze this failure.
    
    STRICT RULES:
    1. Respect the Calculated Severity: {calc_severity}. Do not override it unless logs contradict.
    2. Team Assignment Logic:
       - 500/502 Errors -> "Backend"
       - 400/404 Errors -> "Frontend"
       - Visual Alignment/CSS -> "Design"
    
    CONTEXT:
    - Persona: "{handoff_packet['persona']}"
    - Action: "{handoff_packet['action_taken']}"
    - Device: "{handoff_packet.get('meta_data', {}).get('device_type')}" (Mobile Test)
    - Network: "{handoff_packet.get('meta_data', {}).get('network_type')}"
    
    EVIDENCE:
    - Logs: {json.dumps(handoff_packet['evidence']['network_logs'])}
    
    TASK:
    Return valid JSON (no markdown):
    - diagnosis: Short technical summary (Max 10 words).
    - severity: "{calc_severity}" (Confirm this).
    - responsible_team: "Backend", "Frontend", or "Design".
    """

    try:
        message = client.messages.create(
            model="claude-3-haiku-20240307", 
            max_tokens=1024,
            messages=[{"role": "user", "content": user_message}]
        )
        ai_analysis = json.loads(message.content[0].text)
        handoff_packet['outcome'].update(ai_analysis)
        
    except Exception as e:
        print(f"❌ Claude Error: {e}")
        handoff_packet['outcome'].update({
            "diagnosis": "Analysis Failed",
            "severity": calc_severity,
            "responsible_team": "Manual Review"
        })
    
    return handoff_packet