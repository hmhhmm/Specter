"""
Test Intelligent Team Routing

This script tests the smart team assignment logic that analyzes
evidence and automatically routes issues to the correct team.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.diagnosis_doctor import determine_responsible_team

print("\n" + "="*70)
print("🧪 TESTING INTELLIGENT TEAM ROUTING")
print("="*70)

# Test Case 1: Backend - 500 Error
print("\n📋 Test 1: Backend Issue (500 Error)")
print("-" * 70)
packet1 = {
    "evidence": {
        "network_logs": [
            {"method": "POST", "url": "/signup", "status": 500}
        ],
        "console_logs": [
            "[error] Database connection timeout after 30000ms"
        ]
    }
}
team1 = determine_responsible_team(packet1)
print(f"Network: 500 error")
print(f"Console: Database timeout")
print(f"✅ Routed to: {team1}")
assert team1 == "Backend", f"Expected Backend, got {team1}"

# Test Case 2: Frontend - 404 Error
print("\n📋 Test 2: Frontend Issue (404 Error)")
print("-" * 70)
packet2 = {
    "evidence": {
        "network_logs": [
            {"method": "GET", "url": "/v2/countries", "status": 404}
        ],
        "console_logs": [
            "[error] Failed to fetch: 404 Not Found",
            "[error] Endpoint /v2/countries does not exist"
        ]
    }
}
team2 = determine_responsible_team(packet2)
print(f"Network: 404 error")
print(f"Console: Endpoint not found")
print(f"✅ Routed to: {team2}")
assert team2 == "Frontend", f"Expected Frontend, got {team2}"

# Test Case 3: Design - Touch Target Issue
print("\n📋 Test 3: Design Issue (Touch Target)")
print("-" * 70)
packet3 = {
    "evidence": {
        "network_logs": [],
        "console_logs": [
            "[warning] Touch target smaller than recommended 44x44px",
            "[info] Element dimensions: 28x32px"
        ],
        "ui_analysis": {
            "ux_issues": ["Button too small for mobile touch"]
        }
    }
}
team3 = determine_responsible_team(packet3)
print(f"Network: No errors")
print(f"Console: Touch target warning")
print(f"UX Issues: Button too small")
print(f"✅ Routed to: {team3}")
assert team3 == "Design", f"Expected Design, got {team3}"

# Test Case 4: QA - Unclear Issue
print("\n📋 Test 4: QA Issue (Unclear Root Cause)")
print("-" * 70)
packet4 = {
    "evidence": {
        "network_logs": [
            {"method": "POST", "url": "/signup", "status": 200}
        ],
        "console_logs": []
    }
}
team4 = determine_responsible_team(packet4)
print(f"Network: 200 success (but user reports failure)")
print(f"Console: No errors")
print(f"✅ Routed to: {team4}")
assert team4 == "QA", f"Expected QA, got {team4}"

# Test Case 5: Backend - Database Keyword
print("\n📋 Test 5: Backend Issue (Database Keyword)")
print("-" * 70)
packet5 = {
    "evidence": {
        "network_logs": [],
        "console_logs": [
            "[error] SQL query timeout",
            "[error] Database connection pool exhausted"
        ]
    }
}
team5 = determine_responsible_team(packet5)
print(f"Console: SQL and database keywords")
print(f"✅ Routed to: {team5}")
assert team5 == "Backend", f"Expected Backend, got {team5}"

# Test Case 6: Frontend - JavaScript Error
print("\n📋 Test 6: Frontend Issue (JavaScript Error)")
print("-" * 70)
packet6 = {
    "evidence": {
        "network_logs": [],
        "console_logs": [
            "[error] Uncaught TypeError: Cannot read property 'submit' of null",
            "[error] ReferenceError: submitForm is not defined"
        ]
    }
}
team6 = determine_responsible_team(packet6)
print(f"Console: JavaScript errors")
print(f"✅ Routed to: {team6}")
assert team6 == "Frontend", f"Expected Frontend, got {team6}"

# Test Case 7: Design - Accessibility Issue
print("\n📋 Test 7: Design Issue (Accessibility)")
print("-" * 70)
packet7 = {
    "evidence": {
        "network_logs": [],
        "console_logs": [
            "[warning] WCAG 2.1 contrast ratio violation",
            "[warning] Button lacks accessible label"
        ],
        "ui_analysis": {
            "ux_issues": ["Low contrast text", "Missing ARIA labels"]
        }
    }
}
team7 = determine_responsible_team(packet7)
print(f"Console: WCAG violations")
print(f"UX Issues: Accessibility problems")
print(f"✅ Routed to: {team7}")
assert team7 == "Design", f"Expected Design, got {team7}"

# Test Case 8: Backend - 503 Service Unavailable
print("\n📋 Test 8: Backend Issue (503 Service Unavailable)")
print("-" * 70)
packet8 = {
    "evidence": {
        "network_logs": [
            {"method": "POST", "url": "/api/register", "status": 503}
        ],
        "console_logs": [
            "[error] Service temporarily unavailable"
        ]
    }
}
team8 = determine_responsible_team(packet8)
print(f"Network: 503 error")
print(f"✅ Routed to: {team8}")
assert team8 == "Backend", f"Expected Backend, got {team8}"

print("\n" + "="*70)
print("✅ ALL TESTS PASSED!")
print("="*70)
print("\n📊 Summary:")
print("  • Backend routing: ✅ (500 errors, database, timeouts)")
print("  • Frontend routing: ✅ (404 errors, JavaScript, API issues)")
print("  • Design routing: ✅ (UX, accessibility, no network errors)")
print("  • QA routing: ✅ (Unclear root cause)")
print("\n🎯 The intelligent team routing is working correctly!")
print("="*70 + "\n")
