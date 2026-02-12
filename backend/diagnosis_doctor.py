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
    2. Frontend → 4xx errors, JavaScript errors, broken functionality (buttons not working)
    3. Design   → Visual/UX issues WITHOUT functional failures
    4. QA       → Unclear root cause or multiple suspects
    
    Args:
        handoff_packet: Failure context with evidence
        
    Returns:
        str: One of "Backend", "Frontend", "Design", or "QA"
    """
    evidence = handoff_packet.get('evidence', {})
    network_logs = evidence.get('network_logs', [])
    console_logs = evidence.get('console_logs', [])
    outcome = handoff_packet.get('outcome', {})
    
    # Analyze network logs for HTTP errors
    has_5xx_error = any(log.get('status', 0) >= 500 for log in network_logs)
    has_4xx_error = any(400 <= log.get('status', 0) < 500 for log in network_logs)
    has_network_errors = len(network_logs) > 0 and any(log.get('status', 200) >= 400 for log in network_logs)
    
    # Analyze console logs for specific patterns
    console_text = ' '.join(str(log) for log in console_logs).lower()
    
    # Backend indicators
    backend_keywords = [
        'database', 'timeout', 'connection', 'server error', 
        '500', '502', '503', '504', 'internal server',
        'sql', 'query', 'service unavailable', 'gateway'
    ]
    has_backend_indicators = any(keyword in console_text for keyword in backend_keywords)
    
    # Frontend indicators (EXPANDED - detect broken interactions)
    frontend_keywords = [
        'undefined', 'null', 'javascript', 'typeerror', 'referenceerror',
        '404', '400', '401', '403', 'not found', 'endpoint',
        'fetch failed', 'cors', 'api', 'xhr', 'ajax',
        'event', 'handler', 'listener', 'function'
    ]
    has_frontend_indicators = any(keyword in console_text for keyword in frontend_keywords)
    
    # Functional failure indicators (NEW - detect broken buttons/interactions)
    action_taken = handoff_packet.get('action_taken', '').lower()
    visual_observation = outcome.get('visual_observation', '').lower()
    f_score = outcome.get('f_score', 100)
    
    # If user clicked/tapped something but page barely changed (low visual change)
    # AND there's no network activity, it's likely a broken button → Frontend
    is_click_action = any(word in action_taken for word in ['click', 'tap', 'press', 'button'])
    nothing_happened = f_score < 20  # Very low f_score means nothing happened
    no_network_activity = len(network_logs) == 0 or not has_network_errors
    
    functional_failure = is_click_action and nothing_happened and no_network_activity
    
    # Design/UX indicators (visual/layout only, not functional)
    design_keywords = [
        'contrast', 'accessibility', 'wcag', 'responsive', 'layout',
        'css', 'style', 'visual', 'spacing', 'font', 'color'
    ]
    has_design_indicators = any(keyword in console_text for keyword in design_keywords)
    
    # Check UI analysis for design vs functional issues
    ui_analysis = evidence.get('ui_analysis', {})
    ux_issues = ui_analysis.get('ux_issues', [])
    ux_issues_text = ' '.join(ux_issues).lower() if ux_issues else ''
    
    # Detect functional issues in UX observations
    functional_issue_keywords = [
        'not working', 'doesn\'t work', 'broken', 'not responding',
        'no response', 'no feedback', 'no action', 'fails to',
        'unable to', 'cannot', "can't", 'stuck', 'frozen'
    ]
    has_functional_ux_issues = any(keyword in ux_issues_text for keyword in functional_issue_keywords)
    
    # Detect viewport/scrolling/placement issues (NEW)
    viewport_issue_keywords = [
        'below fold', 'not visible', 'scroll', 'hidden', 'off screen',
        'not in view', 'viewport', 'above the fold', 'form placement',
        'requires scroll', 'auto-scroll'
    ]
    has_viewport_issues = any(keyword in ux_issues_text for keyword in viewport_issue_keywords) or \
                         any(keyword in visual_observation for keyword in viewport_issue_keywords)
    
    has_ux_issues = len(ux_issues) > 0
    
    # IMPROVED Decision tree
    if has_5xx_error or has_backend_indicators:
        print(f"  Routing: Backend (5xx errors or backend indicators)")
        return "Backend"
    elif has_4xx_error or has_frontend_indicators:
        print(f"  Routing: Frontend (4xx errors or frontend indicators)")
        return "Frontend"
    elif functional_failure or has_functional_ux_issues:
        # Button/interaction broken but no errors → Frontend JavaScript issue
        print(f"  Routing: Frontend (functional failure detected: click={is_click_action}, no_change={nothing_happened}, functional_keywords={has_functional_ux_issues})")
        return "Frontend"
    elif has_viewport_issues:
        # Viewport/scrolling/placement issues → UX/Design team
        print(f"  Routing: Design (viewport/scrolling/placement issue detected)")
        return "Design"
    elif (has_ux_issues or has_design_indicators) and not has_network_errors:
        # Pure visual/UX issues without functional problems
        print(f"  Routing: Design (UX issues without functional failures)")
        return "Design"
    else:
        # Unclear root cause - needs QA investigation
        print(f"  Routing: QA (unclear root cause)")
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
    print(f"Smart Routing: Evidence suggests → {suggested_team} team")

    # Build comprehensive analysis prompt
    ux_issues = handoff_packet['evidence'].get('ui_analysis', {}).get('issues', [])
    ux_issues_text = "\n".join([f"  • {issue}" for issue in ux_issues]) if ux_issues else "  None detected"
    
    f_score = handoff_packet['outcome'].get('f_score', 0)
    action_taken = handoff_packet['action_taken']
    
    text_prompt = f"""
You are Specter.AI, an expert at diagnosing signup flow failures.

CRITICAL: Distinguish between FUNCTIONAL issues (doesn't work) vs VISUAL issues (looks bad).

ANALYZE THIS FAILURE:

USER CONTEXT:
• Persona: {handoff_packet['persona']}
• Device: {handoff_packet.get('meta_data', {}).get('device_type')}
• Network: {handoff_packet.get('meta_data', {}).get('network_type')}

WHAT THE USER DID:
• Action: {action_taken}
• Expected: {handoff_packet['agent_expectation']}
• Actual Result: {handoff_packet['outcome'].get('visual_observation', 'See screenshots')}
• F-Score (Friction): {f_score}/100 (higher = worse UX, more frustration/issues)
• User Confusion: {handoff_packet['evidence'].get('ui_analysis', {}).get('confusion_score', 0)}/10

⚠️ KEY DIAGNOSTIC QUESTIONS:
1. Did the page change at all after the user's action? (Check visual similarity score)
2. If user clicked a button/link, did it DO anything? (New page, form submission, navigation)
3. Was there any visible response/feedback? (Loading state, error message, confirmation)
4. If F-Score is very low (<20) after a click → Button likely broken (Frontend issue)
5. Is the expected element/form rendered but NOT VISIBLE in viewport? (Scroll required) → Design issue

UX OBSERVATIONS:
{ux_issues_text}

TECHNICAL EVIDENCE:
• Network Logs: {json.dumps(handoff_packet['evidence']['network_logs'], indent=2) if handoff_packet['evidence']['network_logs'] else '[]'}
• Console Errors: {json.dumps(handoff_packet['evidence'].get('console_logs', []), indent=2) if handoff_packet['evidence'].get('console_logs') else '[]'}

TEAM ROUTING LOGIC:
• Backend → 5xx errors, server crashes, database failures, timeouts
• Frontend → Broken buttons/clicks, JavaScript errors, 4xx errors, forms not submitting, no response to user actions
• Design → Visual/layout issues, poor UX/accessibility, viewport/scrolling problems, form placement issues, elements below fold
• QA → Unclear root cause, multiple suspects, needs investigation

SMART ROUTING SUGGESTION: {suggested_team} team
(You can override if evidence clearly points elsewhere)

YOUR TASK:
1. Compare BEFORE and AFTER screenshots
2. Determine: Is this a FUNCTIONAL failure (doesn't work) or VISUAL failure (looks bad)?
3. If button was clicked but nothing happened → Frontend bug
4. If functionality works but experience is poor → Design issue
5. Provide clear diagnosis with specific root cause

Return ONLY valid JSON (no markdown):
{{
  "diagnosis": "Technical explanation: What failed? Why? Is it functional or visual? (2-3 sentences)",
  "severity": "P0|P1|P2|P3",
  "responsible_team": "Backend|Frontend|Design|QA",
  "recommendations": ["Specific action 1", "Specific action 2", "Specific action 3"]
}}

Focus on: What failed? Why? What team should fix it?
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
        # Using Claude Haiku for both vision and non-vision (faster and more reliable)
        model = "claude-3-haiku-20240307"
        
        message = client.messages.create(
            model=model,
            max_tokens=3000,  # Increased for comprehensive analysis
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
            print(f"Invalid team '{ai_analysis.get('responsible_team')}' - using pre-analyzed team: {suggested_team}")
            ai_analysis['responsible_team'] = suggested_team
        
        handoff_packet['outcome'].update(ai_analysis)
        
        if use_vision and 'visual_issues' in ai_analysis:
            print(f"Visual Analysis: {len(ai_analysis.get('visual_issues', []))} issues found")
        
        print(f"Final routing: {ai_analysis.get('responsible_team')} team")
        
    except json.JSONDecodeError as e:
        print(f"Error: Claude JSON parse failed: {e}")
        print(f"Raw response: {response_text if 'response_text' in locals() else 'N/A'}")
        handoff_packet['outcome'].update({
            "diagnosis": "Analyzing issue... (AI diagnosis pending)",
            "severity": calc_severity,
            "responsible_team": suggested_team,  # Use intelligent team determination
            "recommendations": ["Review network logs", "Check console errors", "Analyze screenshots"]
        })
    except Exception as e:
        print(f"Error: Claude API failed: {e}")
        handoff_packet['outcome'].update({
            "diagnosis": "Analyzing issue... (AI diagnosis pending)",
            "severity": calc_severity,
            "responsible_team": suggested_team,  # Use intelligent team determination
            "recommendations": ["Review network logs", "Check console errors", "Analyze screenshots"]
        })
    
    return handoff_packet