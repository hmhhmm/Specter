"""
Test Slack Smart Routing - Send Test Alerts

This script sends test alerts to demonstrate the smart channel routing.
Each type of failure routes to the correct team's channel.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.escalation_webhook import send_alert

# Test Case 1: Backend Issue (500 Error)
print("\n" + "="*60)
print("TEST 1: Backend Issue → Routes to #backend-alerts")
print("="*60)

backend_packet = {
    "persona": "Elderly User (65+)",
    "action_taken": "Clicked 'Sign Up' button",
    "agent_expectation": "Account creation form submits successfully",
    "confusion_score": 8,
    "outcome": {
        "status": "FAILED",
        "diagnosis": "Database connection timeout on user registration",
        "severity": "P0",
        "responsible_team": "Backend",
        "f_score": 92,
        "gif_path": None,
        "recommendations": [
            "Add connection pooling with retry logic",
            "Implement circuit breaker for database calls",
            "Set up database read replicas"
        ]
    },
    "evidence": {
        "screenshot_before_path": "reports/test_2026-02-07_22-09-34_057167/screenshots/220935_091905_6gjx_autonomous_step_01_observe.png",
        "screenshot_after_path": "reports/test_2026-02-07_22-09-34_057167/screenshots/220943_930959_dr3y_autonomous_step_01_after.png",
        "network_logs": [
            {"method": "POST", "url": "https://api.deriv.com/signup", "status": 500},
            {"method": "GET", "url": "https://api.deriv.com/health", "status": 200},
            {"method": "POST", "url": "https://api.deriv.com/retry", "status": 504}
        ],
        "console_logs": [
            "[error] Database connection timeout after 30000ms",
            "[error] Failed to insert user record",
            "[warning] Retry attempt 3/3 failed"
        ]
    }
}

try:
    send_alert(backend_packet)
    print("✅ Backend alert sent successfully!")
    print("   → Check #backend-alerts channel in Slack")
except Exception as e:
    print(f"❌ Error: {e}")


# Test Case 2: Frontend Issue (404 Error)
print("\n" + "="*60)
print("TEST 2: Frontend Issue → Routes to #frontend-alerts")
print("="*60)

frontend_packet = {
    "persona": "Power User",
    "action_taken": "Clicked country dropdown",
    "agent_expectation": "Dropdown opens with country list",
    "confusion_score": 6,
    "outcome": {
        "status": "FAILED",
        "diagnosis": "Country selector API endpoint not found",
        "severity": "P1",
        "responsible_team": "Frontend",
        "f_score": 75,
        "gif_path": None,
        "recommendations": [
            "Update API endpoint path in frontend config",
            "Add fallback for missing country data",
            "Display user-friendly error message"
        ]
    },
    "evidence": {
        "screenshot_before_path": "reports/test_2026-02-07_22-09-34_057167/screenshots/220935_091905_6gjx_autonomous_step_01_observe.png",
        "screenshot_after_path": "reports/test_2026-02-07_22-09-34_057167/screenshots/220943_930959_dr3y_autonomous_step_01_after.png",
        "network_logs": [
            {"method": "GET", "url": "https://api.deriv.com/v2/countries", "status": 404},
            {"method": "GET", "url": "https://api.deriv.com/v1/countries", "status": 200}
        ],
        "console_logs": [
            "[error] Failed to fetch: 404 Not Found",
            "[warning] Endpoint /v2/countries does not exist"
        ]
    }
}

try:
    send_alert(frontend_packet)
    print("✅ Frontend alert sent successfully!")
    print("   → Check #frontend-alerts channel in Slack")
except Exception as e:
    print(f"❌ Error: {e}")


# Test Case 3: Design Issue (CSS/Visual)
print("\n" + "="*60)
print("TEST 3: Design Issue → Routes to #design-alerts")
print("="*60)

design_packet = {
    "persona": "Mobile User",
    "action_taken": "Attempted to tap submit button",
    "agent_expectation": "Button should be tappable on mobile",
    "confusion_score": 7,
    "outcome": {
        "status": "FAILED",
        "diagnosis": "Button too small for mobile touch target (28px instead of 44px minimum)",
        "severity": "P2",
        "responsible_team": "Design",
        "f_score": 68,
        "gif_path": None,
        "recommendations": [
            "Increase button min-height to 44px for touch targets",
            "Add more padding around clickable elements",
            "Test with mobile device emulator"
        ]
    },
    "evidence": {
        "screenshot_before_path": "reports/test_2026-02-07_22-09-34_057167/screenshots/220935_091905_6gjx_autonomous_step_01_observe.png",
        "screenshot_after_path": "reports/test_2026-02-07_22-09-34_057167/screenshots/220943_930959_dr3y_autonomous_step_01_after.png",
        "network_logs": [],
        "console_logs": [
            "[warning] Touch target smaller than recommended 44x44px",
            "[info] Element dimensions: 28x32px"
        ]
    }
}

try:
    send_alert(design_packet)
    print("✅ Design alert sent successfully!")
    print("   → Check #design-alerts channel in Slack")
except Exception as e:
    print(f"❌ Error: {e}")


# Test Case 4: QA Issue (Unclear)
print("\n" + "="*60)
print("TEST 4: QA Issue → Routes to #qa-alerts")
print("="*60)

qa_packet = {
    "persona": "Senior User",
    "action_taken": "Filled form and clicked submit",
    "agent_expectation": "Form submits and shows confirmation",
    "confusion_score": 5,
    "outcome": {
        "status": "FAILED",
        "diagnosis": "Form submission unclear - needs manual review",
        "severity": "P3",
        "responsible_team": "QA",
        "f_score": 45,
        "gif_path": None,
        "recommendations": [
            "Investigate form validation logic",
            "Check browser console for hidden errors",
            "Manual testing required"
        ]
    },
    "evidence": {
        "screenshot_before_path": "reports/test_2026-02-07_22-09-34_057167/screenshots/220935_091905_6gjx_autonomous_step_01_observe.png",
        "screenshot_after_path": "reports/test_2026-02-07_22-09-34_057167/screenshots/220943_930959_dr3y_autonomous_step_01_after.png",
        "network_logs": [
            {"method": "POST", "url": "https://deriv.com/submit", "status": 200}
        ],
        "console_logs": []
    }
}

try:
    send_alert(qa_packet)
    print("✅ QA alert sent successfully!")
    print("   → Check #qa-alerts channel in Slack")
except Exception as e:
    print(f"❌ Error: {e}")


print("\n" + "="*60)
print("✅ ALL TEST ALERTS SENT!")
print("="*60)
print("\nCheck your Slack workspace:")
print("  • #backend-alerts   → Should have Backend issue (P0)")
print("  • #frontend-alerts  → Should have Frontend issue (P1)")
print("  • #design-alerts    → Should have Design issue (P2)")
print("  • #qa-alerts        → Should have QA issue (P3)")
print("\n🎯 Each team only sees their relevant alerts!")
print("="*60)
