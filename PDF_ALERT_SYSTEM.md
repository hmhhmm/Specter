# 📄 Real-Time PDF Alert System

## Overview

The Specter system now automatically generates and sends PDF reports to the corresponding team's Slack channel whenever a failure is detected. Each team receives professional PDF documentation alongside the standard Slack alerts.

## Features

### ✨ Automatic PDF Generation
- **Real-time**: PDFs are generated instantly when failures are detected
- **Team-specific**: Each team receives only their relevant alerts
- **Professional formatting**: Clean, readable reports with tables and charts
- **Complete data**: Includes all diagnostic information, logs, and recommendations

### 🎯 Smart Routing
- **Backend Team** → `#backend-alerts` (P0/P1 issues)
- **Frontend Team** → `#frontend-alerts` (API/UI issues)
- **Design Team** → `#design-alerts` (UX/accessibility issues)
- **QA Team** → `#qa-alerts` (unclear issues)

## What Gets Sent

When a failure is detected, each team receives:

1. **Screenshot/GIF** - Visual evidence of the failure
2. **Slack Message** - Detailed alert with network/console logs
3. **📄 PDF Report** - Professional document with:
   - Alert overview (persona, action, severity)
   - Diagnosis and root cause
   - Recommendations with action items
   - Network logs
   - Console logs
   - Timestamp and metadata

## Usage

### Automatic (Production)

The PDF system is integrated into the alert pipeline. No action needed - PDFs are sent automatically when failures occur.

### Manual Testing

Test the PDF alert system with sample data:

```bash
python test_realtime_pdf_alerts.py
```

This will send 3 test alerts to different team channels, each with a PDF report.

### Send Custom Alert

```python
from backend.escalation_webhook import send_alert

alert_packet = {
    "persona": "Mobile User",
    "action_taken": "Clicked login button",
    "agent_expectation": "Login form should submit",
    "confusion_score": 8,
    "outcome": {
        "status": "FAILED",
        "diagnosis": "Login API endpoint timeout",
        "severity": "P0",
        "responsible_team": "Backend",
        "f_score": 90,
        "recommendations": [
            "Check database connection pool",
            "Review API gateway logs",
            "Scale backend servers"
        ]
    },
    "evidence": {
        "screenshot_after_path": "path/to/screenshot.png",
        "network_logs": [
            {"method": "POST", "url": "https://api.example.com/login", "status": 504}
        ],
        "console_logs": [
            "[error] Request timeout after 30000ms"
        ]
    }
}

send_alert(alert_packet)  # Automatically generates and sends PDF too!
```

## File Structure

```
backend/
├── escalation_webhook.py        # Main alert sender (includes PDF integration)
├── pdf_alert_generator.py       # PDF generation and Slack delivery
└── .env                          # Slack credentials

reports/
└── pdf_alerts/                   # Generated PDFs are saved here
    ├── Backend_P0_20260208_143522.pdf
    ├── Frontend_P1_20260208_143530.pdf
    └── Design_P2_20260208_143540.pdf
```

## Benefits of PDF Reports

✅ **Professional Documentation**
   - Share with stakeholders outside Slack
   - Attach to project management tools (JIRA, Asana)
   - Include in status reports and presentations

✅ **Archival & Compliance**
   - Long-term storage outside Slack
   - Audit trail for security reviews
   - Historical analysis of issues

✅ **Complete Context**
   - All diagnostic data in one place
   - Easy to reference during debugging
   - No dependency on Slack retention policies

✅ **Shareable**
   - Email to external teams or vendors
   - Print for meetings
   - Universal format (opens anywhere)

## Configuration

### Environment Variables

Set these in `backend/.env`:

```env
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token

# Team Channel IDs
SLACK_BACKEND_CHANNEL=C01234ABCDE
SLACK_FRONTEND_CHANNEL=C01234FGHIJ
SLACK_DESIGN_CHANNEL=C01234KLMNO
SLACK_QA_CHANNEL=C01234PQRST
```

### Customization

**Change PDF Directory:**
```python
# In backend/pdf_alert_generator.py
generate_team_alert_pdf(packet, output_dir="custom/path")
```

**Disable PDF Generation (keep Slack alerts only):**
```python
# In backend/escalation_webhook.py
# Comment out these lines:
# try:
#     generate_and_send_alert_pdf(final_packet)
# except Exception as pdf_error:
#     print(f"⚠️  PDF generation failed: {pdf_error}")
```

## Troubleshooting

### PDF Not Generated
- Check if `reportlab` is installed: `pip install reportlab`
- Verify output directory exists and is writable
- Check console for error messages

### PDF Not Sent to Slack
- Verify Slack bot token is valid
- Ensure bot has permission to upload files
- Check channel IDs are correct
- Look for API errors in console

### Missing Data in PDF
- Ensure `final_packet` contains all required fields
- Check `evidence` dictionary is properly formatted
- Verify `outcome` contains diagnosis and recommendations

## Live Demo

Watch the system in action:

1. Start the API server:
```bash
python api_server.py
```

2. Open the lab UI:
```bash
npm run dev
# Visit http://localhost:3000/lab
```

3. Run a test and watch for failures
4. Check Slack channels for PDF reports

## UI Improvements

### Fixed: Neural Link Scrolling

The neural link panel in `/lab` now properly scrolls when diagnostic data is long, keeping the phone emulator at a consistent size.

**Before:** Neural link expanded to bottom, pushing phone off-screen  
**After:** Neural link scrolls internally, phone stays fixed size

This ensures a better experience when monitoring long-running tests with extensive logs.

---

**Questions or issues?** Check the console output for detailed error messages or contact the dev team.
