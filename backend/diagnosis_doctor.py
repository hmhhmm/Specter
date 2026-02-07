"""AI-powered failure diagnosis module."""

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
    Analyze failure using AI with optional vision analysis.
    
    Args:
        handoff_packet: Failure context and evidence
        use_vision: Enable screenshot analysis
        
    Returns:
        Updated handoff_packet with diagnosis
    """
    print("Diagnosing with Claude{}...".format(" + Vision" if use_vision else ""))
    
    # Get the deterministic severity we calculated
    calc_severity = handoff_packet['outcome'].get('calculated_severity', 'P3 - Cosmetic')

    # Build text prompt
    text_prompt = f"""
You are Specter.AI. Analyze this UX failure.

SEVERITY DEFINITIONS (Read carefully):
- P0 - Critical: Signup completely blocked (500 errors, no progress possible)
- P1 - Major: High friction/drop-off risk (400 errors, severe usability issues)
- P2 - Minor: Degraded experience (moderate issues, workarounds exist)
- P3 - Cosmetic: Minor UI issues (low impact, cosmetic only)

STRICT RULES:
1. Respect the Calculated Severity: {calc_severity}. Do not override unless evidence contradicts.
2. Team Assignment Logic:
   - 500/502 Errors -> "Backend"
   - 400/404 Errors -> "Frontend"
   - Visual Alignment/CSS/UX -> "Design"
   - Unclear/Multiple Teams -> "QA"

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
- Confusion Score: {handoff_packet['evidence'].get('ui_analysis', {}).get('confusion_score', 'N/A')}/10

TASK:
Return valid JSON (no markdown):
- diagnosis: Short technical summary (Max 15 words).
- severity: "{calc_severity}" (Confirm this exact string).
- responsible_team: "Backend", "Frontend", "Design", or "QA".
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
            print(f"Warning: Vision analysis failed, falling back to text-only: {e}")
            use_vision = False

    try:
        # Choose model based on vision usage - use Claude 3.5 Sonnet for vision
        model = "claude-3-5-sonnet-20240620" if use_vision else "claude-3-haiku-20240307"
        
        message = client.messages.create(
            model=model,
            max_tokens=2048,
            messages=[{"role": "user", "content": message_content}]
        )
        
        # Extract response text
        response_text = message.content[0].text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            # Remove ```json and ``` markers
            response_text = response_text.split('\n', 1)[1] if '\n' in response_text else response_text
            if response_text.endswith("```"):
                response_text = response_text.rsplit("```", 1)[0]
            response_text = response_text.strip()
        
        # Parse JSON
        ai_analysis = json.loads(response_text)
        handoff_packet['outcome'].update(ai_analysis)
        
        if use_vision and 'visual_issues' in ai_analysis:
            print(f"Visual Analysis: {len(ai_analysis.get('visual_issues', []))} issues found")
        
    except json.JSONDecodeError as e:
        print(f"Error: Claude JSON parse failed: {e}")
        print(f"Raw response: {response_text if 'response_text' in locals() else 'N/A'}")
        handoff_packet['outcome'].update({
            "diagnosis": "Analysis Failed - Invalid JSON",
            "severity": calc_severity,
            "responsible_team": "Manual Review",
            "recommendations": ["Review logs manually", "Check screenshot evidence"]
        })
    except Exception as e:
        print(f"Error: Claude API failed: {e}")
        handoff_packet['outcome'].update({
            "diagnosis": "Analysis Failed",
            "severity": calc_severity,
            "responsible_team": "Manual Review",
            "recommendations": ["Review logs manually", "Check screenshot evidence"]
        })
    
    return handoff_packet