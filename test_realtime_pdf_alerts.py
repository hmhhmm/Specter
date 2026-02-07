"""
Test Real-time PDF Alerts to Slack

This script demonstrates the real-time PDF report generation and delivery.
When an alert is triggered, a PDF is automatically generated and sent to 
the corresponding team's Slack channel.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.escalation_webhook import send_alert

print("\n" + "="*70)
print("🚀 REAL-TIME PDF ALERT SYSTEM TEST")
print("="*70)
print("\nThis will send alerts WITH PDF reports to each team's Slack channel")
print("Each team receives:")
print("  1. Screenshot/GIF evidence")
print("  2. Detailed Slack message with logs")
print("  3. 📄 PDF report document")
print("\n" + "="*70 + "\n")

# Test Case 1: Backend P0 Alert
print("🔴 TEST 1: Backend P0 Critical Alert")
print("-" * 70)

backend_packet = {
    "persona": "Elderly User (65+)",
    "action_taken": "Clicked 'Sign Up' button",
    "agent_expectation": "Account creation form submits successfully",
    "confusion_score": 9,
    "outcome": {
        "status": "FAILED",
        "diagnosis": "Database connection timeout on user registration - critical system failure",
        "severity": "P0",
        "responsible_team": "Backend",
        "f_score": 95,
        "gif_path": None,
        "recommendations": [
            "Immediately rollback recent database configuration changes",
            "Add connection pooling with exponential backoff retry logic",
            "Implement circuit breaker pattern for database calls",
            "Set up database read replicas for load distribution",
            "Add monitoring alerts for connection pool exhaustion"
        ]
    },
    "evidence": {
        "screenshot_before_path": "reports/test_2026-02-07_22-09-34_057167/screenshots/220935_091905_6gjx_autonomous_step_01_observe.png",
        "screenshot_after_path": "reports/test_2026-02-07_22-09-34_057167/screenshots/220943_930959_dr3y_autonomous_step_01_after.png",
        "network_logs": [
            {"method": "POST", "url": "https://api.deriv.com/signup", "status": 500},
            {"method": "GET", "url": "https://api.deriv.com/health", "status": 200},
            {"method": "POST", "url": "https://api.deriv.com/retry", "status": 504},
            {"method": "POST", "url": "https://api.deriv.com/fallback", "status": 503}
        ],
        "console_logs": [
            "[error] Database connection timeout after 30000ms",
            "[error] Failed to insert user record into users table",
            "[error] Connection pool exhausted: 0/50 available",
            "[warning] Retry attempt 3/3 failed - escalating",
            "[critical] Transaction rolled back"
        ]
    }
}

try:
    send_alert(backend_packet)
    print("✅ Backend alert + PDF sent!")
    print("   → Check #backend-alerts for screenshot + PDF report\n")
except Exception as e:
    print(f"❌ Error: {e}\n")


# Test Case 2: Frontend P1 Alert
print("\n🟠 TEST 2: Frontend P1 High Priority Alert")
print("-" * 70)

frontend_packet = {
    "persona": "Power User",
    "action_taken": "Clicked country dropdown",
    "agent_expectation": "Dropdown opens with country list",
    "confusion_score": 7,
    "outcome": {
        "status": "FAILED",
        "diagnosis": "Country selector API endpoint returns 404 - missing v2 endpoint",
        "severity": "P1",
        "responsible_team": "Frontend",
        "f_score": 78,
        "gif_path": None,
        "recommendations": [
            "Update API endpoint path from /v2/countries to /v1/countries",
            "Add fallback mechanism for missing country data",
            "Display user-friendly error message instead of blank dropdown",
            "Implement client-side country list caching",
            "Add error boundary for dropdown component"
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
            "[warning] Endpoint /v2/countries does not exist",
            "[error] Dropdown component failed to render list"
        ]
    }
}

try:
    send_alert(frontend_packet)
    print("✅ Frontend alert + PDF sent!")
    print("   → Check #frontend-alerts for screenshot + PDF report\n")
except Exception as e:
    print(f"❌ Error: {e}\n")


# Test Case 3: Design P2 Alert
print("\n🟡 TEST 3: Design P2 Medium Priority Alert")
print("-" * 70)

design_packet = {
    "persona": "Mobile User",
    "action_taken": "Attempted to tap submit button on mobile device",
    "agent_expectation": "Button should be easily tappable on mobile screen",
    "confusion_score": 6,
    "outcome": {
        "status": "FAILED",
        "diagnosis": "Button touch target too small (28px) - violates WCAG 2.1 minimum of 44px",
        "severity": "P2",
        "responsible_team": "Design",
        "f_score": 72,
        "gif_path": None,
        "recommendations": [
            "Increase button min-height to 44px for WCAG 2.1 compliance",
            "Add more padding (16px) around clickable elements",
            "Test with mobile device emulator and real devices",
            "Implement responsive button sizing for different screen sizes",
            "Review all interactive elements for touch target sizes"
        ]
    },
    "evidence": {
        "screenshot_before_path": "reports/test_2026-02-07_22-09-34_057167/screenshots/220935_091905_6gjx_autonomous_step_01_observe.png",
        "screenshot_after_path": "reports/test_2026-02-07_22-09-34_057167/screenshots/220943_930959_dr3y_autonomous_step_01_after.png",
        "network_logs": [],
        "console_logs": [
            "[warning] Touch target smaller than recommended 44x44px",
            "[info] Element dimensions: 28x32px",
            "[warning] WCAG 2.1 Level AAA guideline violation"
        ]
    }
}

try:
    send_alert(design_packet)
    print("✅ Design alert + PDF sent!")
    print("   → Check #design-alerts for screenshot + PDF report\n")
except Exception as e:
    print(f"❌ Error: {e}\n")


print("\n" + "="*70)
print("✅ ALL REAL-TIME PDF ALERTS SENT!")
print("="*70)
print("\n📱 Check your Slack workspace - each team should have:")
print("\n  #backend-alerts  → 🚨 P0 Backend alert with PDF")
print("  #frontend-alerts → ⚠️  P1 Frontend alert with PDF")
print("  #design-alerts   → ⚡ P2 Design alert with PDF")
print("\n🎯 Benefits of PDF Reports:")
print("  • Professional documentation for stakeholders")
print("  • Easy to forward and share outside Slack")
print("  • Archivable for compliance and auditing")
print("  • Contains complete diagnostic data")
print("  • Can be attached to JIRA tickets")
print("\n" + "="*70 + "\n")
