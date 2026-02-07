"""
Send Slack Alerts from Real Test Reports

This reads your actual test reports and sends them to Slack
using the smart channel routing.
"""

import sys
import os
import json
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.escalation_webhook import send_alert

def find_latest_test_reports(reports_dir="reports", limit=5):
    """Find the most recent test reports with failures."""
    if not os.path.exists(reports_dir):
        print(f"❌ No reports directory found at: {reports_dir}")
        return []
    
    # Get all test folders sorted by date (newest first)
    test_folders = sorted(
        [f for f in os.listdir(reports_dir) if os.path.isdir(os.path.join(reports_dir, f))],
        reverse=True
    )
    
    failed_reports = []
    
    for folder in test_folders[:20]:  # Check last 20 test runs
        folder_path = os.path.join(reports_dir, folder)
        
        # Look for step report JSONs
        for file in os.listdir(folder_path):
            if file.endswith('_report.json'):
                report_path = os.path.join(folder_path, file)
                
                try:
                    with open(report_path, 'r', encoding='utf-8') as f:
                        report_data = json.load(f)
                    
                    # Only include failed steps
                    if report_data.get('outcome', {}).get('status') == 'FAILED':
                        failed_reports.append({
                            'folder': folder,
                            'file': file,
                            'path': report_path,
                            'data': report_data
                        })
                        
                        if len(failed_reports) >= limit:
                            return failed_reports
                            
                except Exception as e:
                    print(f"Error reading {report_path}: {e}")
                    continue
    
    return failed_reports


def send_real_alerts(limit=3):
    """Send alerts from real test reports."""
    print("\n" + "="*60)
    print("📊 LOADING REAL TEST REPORTS")
    print("="*60)
    
    reports = find_latest_test_reports(limit=limit)
    
    if not reports:
        print("\n❌ No failed test reports found!")
        print("   Run some tests first: python main.py <url>")
        return
    
    print(f"\n✅ Found {len(reports)} failed test reports\n")
    
    for i, report in enumerate(reports, 1):
        print("="*60)
        print(f"ALERT {i}/{len(reports)}: {report['folder']} - {report['file']}")
        print("="*60)
        
        data = report['data']
        
        # Build the packet in the format send_alert expects
        packet = {
            "persona": data.get("persona", "Unknown User"),
            "action_taken": data.get("action", "Unknown action"),
            "agent_expectation": data.get("evidence", {}).get("expected_outcome", "Expected outcome"),
            "confusion_score": data.get("confusion_score", 0),
            "outcome": data.get("outcome", {}),
            "evidence": data.get("evidence", {})
        }
        
        # Display what we're sending
        outcome = packet['outcome']
        print(f"   Issue: {outcome.get('diagnosis', 'N/A')}")
        print(f"   Severity: {outcome.get('severity', 'N/A')}")
        print(f"   Team: {outcome.get('responsible_team', 'N/A')}")
        print(f"   F-Score: {outcome.get('f_score', 'N/A')}/100")
        print(f"   Confusion: {packet['confusion_score']}/10")
        
        try:
            send_alert(packet)
            print(f"   ✅ Alert sent successfully!")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    print("="*60)
    print("✅ DONE! Check your Slack channels:")
    print("="*60)
    
    # Show which teams should have received alerts
    teams_alerted = set()
    for report in reports:
        team = report['data'].get('outcome', {}).get('responsible_team')
        if team:
            teams_alerted.add(team)
    
    channel_map = {
        "Backend": "#backend-alerts",
        "Frontend": "#frontend-alerts",
        "Design": "#design-alerts",
        "QA": "#qa-alerts"
    }
    
    for team in teams_alerted:
        channel = channel_map.get(team, "#unknown")
        print(f"  • {channel} → Should have {team} team alerts")
    
    print("="*60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Send Slack alerts from real test reports")
    parser.add_argument("--limit", type=int, default=3, help="Number of failed reports to send (default: 3)")
    args = parser.parse_args()
    
    send_real_alerts(limit=args.limit)
