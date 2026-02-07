"""AI-powered failure diagnosis module with intelligent team routing."""

import json
import os
import base64
from dotenv import load_dotenv
import anthropic

load_dotenv(os.path.join("backend", ".env"))
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)


def determine_responsible_team(handoff_packet):
    """
    Intelligently determine responsible team based on evidence analysis.
    
    Decision Logic:
    1. Backend  → 5xx errors, database issues, server timeouts
    2. Frontend → 4xx errors, JavaScript errors, API client issues
    3. Design   → UX/accessibility issues with no network errors
    4. QA       → Unclear root cause or multiple suspects
    
    Args:
        handoff_packet: Failure context with evidence
        
    Returns:
        str: One of "Backend", "Frontend", "Design", or "QA"
    """
    evidence = handoff_packet.get('evidence', {})
    network_logs = evidence.get('network_logs', [])
    console_logs = evidence.get('console_logs', [])
    
    # Analyze network logs for HTTP errors
    has_5xx_error = any(log.get('status', 0) >= 500 for log in network_logs)
    has_4xx_error = any(400 <= log.get('status', 0) < 500 for log in network_logs)
    has_network_errors = len(network_logs) > 0 and any(log.get('status', 200) >= 400 for log in network_logs)
    
    # Analyze console logs for specific patterns
    console_text = ' '.join(console_logs).lower()
    
    # Backend indicators
    backend_keywords = [
        'database', 'timeout', 'connection', 'server error', 
        '500', '502', '503', '504', 'internal server',
        'sql', 'query', 'service unavailable', 'gateway'
    ]
    has_backend_indicators = any(keyword in console_text for keyword in backend_keywords)
    
    # Frontend indicators
    frontend_keywords = [
        'undefined', 'null', 'javascript', 'typeerror', 'referenceerror',
        '404', '400', '401', '403', 'not found', 'endpoint',
        'fetch failed', 'cors', 'api', 'xhr', 'ajax'
    ]
    has_frontend_indicators = any(keyword in console_text for keyword in frontend_keywords)
    
    # Design/UX indicators
    design_keywords = [
        'touch target', 'button', 'click', 'tap', 'size', 'contrast',
        'accessibility', 'wcag', 'mobile', 'responsive', 'layout',
        'css', 'style', 'visual', 'spacing'
    ]
    has_design_indicators = any(keyword in console_text for keyword in design_keywords)
    
    # Check UI analysis for design issues
    ui_analysis = evidence.get('ui_analysis', {})
    ux_issues = ui_analysis.get('ux_issues', [])
    has_ux_issues = len(ux_issues) > 0
    
    # Decision tree
    if has_5xx_error or has_backend_indicators:
        return "Backend"
    elif has_4xx_error or has_frontend_indicators:
        return "Frontend"
    elif (has_ux_issues or has_design_indicators) and not has_network_errors:
        return "Design"
    else:
        # Unclear root cause - needs QA investigation
        return "QA"

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
    
    # INTELLIGENT TEAM ASSIGNMENT - Determine team BEFORE asking Claude
    suggested_team = determine_responsible_team(handoff_packet)
    print(f"📊 Smart Routing: Evidence suggests → {suggested_team} team")

    # Build text prompt with pre-determined team
    text_prompt = f"""
You are Specter.AI. Analyze this UX failure.

SEVERITY DEFINITIONS:
- P0 - Critical: Signup completely blocked (500 errors, no progress possible)
- P1 - Major: High friction/drop-off risk (400 errors, severe usability issues)
- P2 - Minor: Degraded experience (moderate issues, workarounds exist)
- P3 - Cosmetic: Minor UI issues (low impact, cosmetic only)

TEAM ASSIGNMENT (Pre-analyzed):
Our intelligent analysis suggests: {suggested_team}
- Backend:  5xx errors, database, server timeouts
- Frontend: 4xx errors, JavaScript, API client issues
- Design:   UX/accessibility issues without network errors
- QA:       Unclear root cause

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
{{
  "diagnosis": "Short technical summary (15 words max)",
  "severity": "{calc_severity}",
  "responsible_team": "{suggested_team}",
  "recommendations": ["Action 1", "Action 2", "Action 3"]
}}

IMPORTANT: 
- Keep diagnosis concise and technical
- Use the suggested team unless evidence clearly contradicts it
- responsible_team MUST be exactly one of: "Backend", "Frontend", "Design", "QA"
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
        
        # VALIDATE: Ensure responsible_team is one of the 4 valid teams
        valid_teams = ["Backend", "Frontend", "Design", "QA"]
        if ai_analysis.get('responsible_team') not in valid_teams:
            print(f"⚠️  Invalid team '{ai_analysis.get('responsible_team')}' - using pre-analyzed team: {suggested_team}")
            ai_analysis['responsible_team'] = suggested_team
        
        handoff_packet['outcome'].update(ai_analysis)
        
        if use_vision and 'visual_issues' in ai_analysis:
            print(f"Visual Analysis: {len(ai_analysis.get('visual_issues', []))} issues found")
        
        print(f"✅ Final routing: {ai_analysis.get('responsible_team')} team")
        
    except json.JSONDecodeError as e:
        print(f"Error: Claude JSON parse failed: {e}")
        print(f"Raw response: {response_text if 'response_text' in locals() else 'N/A'}")
        handoff_packet['outcome'].update({
            "diagnosis": "Analysis completed - see evidence for details",
            "severity": calc_severity,
            "responsible_team": suggested_team,  # Use intelligent team determination
            "recommendations": ["Review network logs", "Check console errors", "Analyze screenshots"]
        })
    except Exception as e:
        print(f"Error: Claude API failed: {e}")
        handoff_packet['outcome'].update({
            "diagnosis": "Analysis completed - see evidence for details",
            "severity": calc_severity,
            "responsible_team": suggested_team,  # Use intelligent team determination
            "recommendations": ["Review network logs", "Check console errors", "Analyze screenshots"]
        })
    
    return handoff_packet