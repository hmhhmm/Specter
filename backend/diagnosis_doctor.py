# diagnosis_doctor.py (Vision-Enhanced Edition)
import json
import os
import base64
from dotenv import load_dotenv
import anthropic

load_dotenv(os.path.join("backend", ".env"))
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

def diagnose_failure(handoff_packet, use_vision=True):
    """
    AI-powered failure diagnosis with optional vision analysis.
    
    Args:
        handoff_packet: Failure context and evidence
        use_vision: If True, sends screenshots to Claude for visual analysis
    """
    
    if use_vision:
        print("🧠 Specter (Claude Sonnet + Vision) is diagnosing...")
    else:
        print("🧠 Specter (Claude Haiku) is diagnosing...")
    
    # Get the deterministic severity we calculated
    calc_severity = handoff_packet['outcome'].get('calculated_severity', 'P3')

    # Build text prompt
    text_prompt = f"""
You are Specter.AI. Analyze this UX failure.

STRICT RULES:
1. Respect the Calculated Severity: {calc_severity}. Do not override it unless logs contradict.
2. Team Assignment Logic:
   - 500/502 Errors -> "Backend"
   - 400/404 Errors -> "Frontend"
   - Visual Alignment/CSS -> "Design"

CONTEXT:
- Persona: "{handoff_packet['persona']}"
- Action: "{handoff_packet['action_taken']}"
- Expectation: "{handoff_packet['agent_expectation']}"
- Device: "{handoff_packet.get('meta_data', {}).get('device_type')}"
- Network: "{handoff_packet.get('meta_data', {}).get('network_type')}"

EVIDENCE:
- Network Logs: {json.dumps(handoff_packet['evidence']['network_logs'])}
- Console Logs: {json.dumps(handoff_packet['evidence'].get('console_logs', []))}
- F-Score: {handoff_packet['outcome'].get('f_score', 'N/A')}/100

TASK:
Return valid JSON (no markdown):
- diagnosis: Short technical summary (Max 15 words).
- severity: "{calc_severity}" (Confirm this).
- responsible_team: "Backend", "Frontend", or "Design".
- visual_issues: List of UI problems observed (if using vision).
- recommendations: Array of 2-3 actionable fixes.
"""

    # Prepare message content
    message_content = []
    
    # Add text prompt
    message_content.append({
        "type": "text",
        "text": text_prompt
    })
    
    # Add screenshots if vision is enabled
    if use_vision:
        try:
            # Get screenshot paths
            before_path = handoff_packet['evidence'].get('screenshot_before_path')
            after_path = handoff_packet['evidence'].get('screenshot_after_path')
            
            # Add before screenshot
            if before_path and os.path.exists(before_path):
                with open(before_path, 'rb') as f:
                    before_b64 = base64.b64encode(f.read()).decode('utf-8')
                message_content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": before_b64
                    }
                })
                message_content.append({
                    "type": "text",
                    "text": "↑ BEFORE: Screenshot taken before user action"
                })
            
            # Add after screenshot
            if after_path and os.path.exists(after_path):
                with open(after_path, 'rb') as f:
                    after_b64 = base64.b64encode(f.read()).decode('utf-8')
                message_content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": after_b64
                    }
                })
                message_content.append({
                    "type": "text",
                    "text": "↑ AFTER: Screenshot taken after user action. Compare with BEFORE to identify what changed (or didn't change when expected)."
                })
        except Exception as e:
            print(f"⚠️  Vision analysis failed, falling back to text-only: {e}")
            use_vision = False

    try:
        # Choose model based on vision usage
        model = "claude-3-haiku-20240307" if use_vision else "claude-3-haiku-20240307"
        
        message = client.messages.create(
            model=model,
            max_tokens=2048,
            messages=[{"role": "user", "content": message_content}]
        )
        ai_analysis = json.loads(message.content[0].text)
        handoff_packet['outcome'].update(ai_analysis)
        
        # Log vision insights if available
        if use_vision and 'visual_issues' in ai_analysis:
            print(f"👁️  Visual Analysis: {len(ai_analysis.get('visual_issues', []))} issues found")
        
    except Exception as e:
        print(f"❌ Claude Error: {e}")
        handoff_packet['outcome'].update({
            "diagnosis": "Analysis Failed",
            "severity": calc_severity,
            "responsible_team": "Manual Review",
            "recommendations": ["Review logs manually", "Check screenshot evidence"]
        })
    
    return handoff_packet