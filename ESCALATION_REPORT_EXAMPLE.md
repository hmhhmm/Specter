# 📊 Specter Escalation Report - Complete Example

## ✅ All Escalation Features Achieved

### 1. **Dedicated Channel/Thread** ✅
- **Smart Channel Routing**: Each team has their own dedicated channel
  - Backend issues → `#backend-alerts`
  - Frontend issues → `#frontend-alerts`
  - Design issues → `#design-alerts`
  - QA issues → `#qa-alerts`
- Creates threaded conversation with evidence upload + detailed analysis
- **Only the responsible team sees the alert** - no spam to other teams!

### 2. **Evidence Upload** ✅ 
- **Screenshots**: Before/after action comparison
- **Screen Recordings**: GIF replay of failure sequence  
- **Network Logs**: HTTP requests with status codes
- **Console Logs**: JavaScript errors and warnings

### 3. **Smart Team Tagging** ✅
- **Smart Channel Routing**: Routes to team-specific channels, not shared channel
- Tags specific team based on diagnosis:
  - `@backend-team` in #backend-alerts for 500/502 errors
  - `@frontend-team` in #frontend-alerts for 400/404 errors  
  - `@design-team` in #design-alerts for CSS/visual issues
  - `@qa-team` in #qa-alerts for unclear failures
- **No more spamming everyone!** Other teams don't even see the alert.

### 4. **Severity Assessment** ✅
- **P0** 🚨 Critical (F-Score 80+): Blocks core flow
- **P1** ⚠️  High (F-Score 60-79): Major friction
- **P2** ⚡ Medium (F-Score 40-59): Moderate issue
- **P3** ℹ️  Low (F-Score 0-39): Minor annoyance

### 5. **Reproduction Steps** ✅
- Persona used (Elderly, Power User, etc.)
- Device and network conditions
- Step-by-step action sequence
- Expected vs actual outcome

### 6. **Root Cause Intelligence** ✅
- "This error is similar to Issue #test_2026-02-07_21-34-25 (87.3% match) from 2026-02-07 21:34:25 - possibly related"
- Pattern detection: "5 total similar incidents detected - pattern confirmed"
- Links to historical issues for context

---

## 📝 Sample Slack Alert Message

**In #backend-alerts channel (only Backend team sees this):**

```
🚨 P0 Alert - @backend-team
[Screenshot/GIF uploaded as attachment]

━━━━━━━━━━━━━━━━━━━━━━━━━━

Diagnosis: Network timeout on country selector API endpoint

F-Score (Frustration): 85/100
User Confusion: 8/10 🔴 Critical
Responsible Team: Backend

Reproduction Steps:
1. Navigate to target page as Elderly User (65+)
2. Action: Clicked on country dropdown selector
3. Expected: Dropdown opens with country list within 2 seconds
4. Result: Failure detected

Network Logs:
• GET https://api.example.com/countries → 500
• POST https://api.example.com/validate → timeout
• GET https://cdn.example.com/assets/flags.png → 200

Console Logs:
• [error] Failed to fetch countries: Network timeout after 30000ms
• [warning] Retry attempt 3 failed
• [error] TypeError: Cannot read property 'data' of undefined

Recommendations:
• Add retry logic with exponential backoff for country API
• Implement local fallback cache for country list
• Display loading state with timeout warning after 3 seconds

🔗 Root Cause Intelligence:
This error is similar to test_2026-02-07_21-34-25_217317 (93.2% match) from 2026-02-07 21:34:25 - possibly related.
5 total similar incidents detected - pattern confirmed.
```

**In #frontend-alerts channel:** Empty ✅  
**In #design-alerts channel:** Empty ✅  
**In #qa-alerts channel:** Empty ✅

👉 **Only the Backend team saw this alert!**

---

## 🧠 Behind the Scenes: How Diagnosis Works

### Step 1: Expectation Engine
**File**: `backend/expectation_engine.py`
- Calculates F-Score (frustration): dwell time + confusion + retries
- Generates severity based on impact
- Creates GIF replay and heatmap visualization

### Step 2: AI Vision Diagnosis  
**File**: `backend/diagnosis_doctor.py`
- Claude 3.5 Sonnet analyzes before/after screenshots
- Compares visual changes vs expected outcome
- Assigns responsible team based on error patterns
- Provides actionable recommendations

### Step 3: Root Cause Intelligence
**File**: `backend/root_cause_intelligence.py`
- Extracts issue signature (error type + component + diagnosis)
- Calculates similarity with historical incidents (0-100 score)
- Detects recurring patterns across test runs
- Links to similar issues with 70%+ match threshold

### Step 4: Slack Escalation
**File**: `backend/escalation_webhook.py`
- **Smart Channel Routing**: Routes to team-specific channels
  ```python
  TEAM_CHANNELS = {
      "Backend": "C01ABC12DEF",    # #backend-alerts
      "Frontend": "C02XYZ34GHI",   # #frontend-alerts
      "Design": "C03PQR56JKL",     # #design-alerts
      "QA": "C04MNO78RST"          # #qa-alerts
  }
  target_channel = TEAM_CHANNELS[responsible_team]
  client.files_upload_v2(channel=target_channel, ...)
  ```
- Tags correct team within their channel (optional)
- Uploads evidence (screenshot/GIF) to the right channel only
- Posts diagnostic analysis in thread
- Includes reproduction steps + root cause links
- **Result**: Only Backend team sees Backend issues - no spam to others!

---

## 🔧 Configuration

Set these in `backend/.env`:

```env
# Slack Bot
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token

# SMART CHANNEL ROUTING - Each team gets their own channel
SLACK_BACKEND_CHANNEL=C01ABC12DEF    # #backend-alerts
SLACK_FRONTEND_CHANNEL=C02XYZ34GHI   # #frontend-alerts
SLACK_DESIGN_CHANNEL=C03PQR56JKL     # #design-alerts
SLACK_QA_CHANNEL=C04MNO78RST         # #qa-alerts

# Fallback channel (if team channel not configured)
SLACK_CHANNEL_ID=C00SHARED99

# Team Mentions (optional - tags within their channel)
SLACK_BACKEND_TEAM=@backend-team
SLACK_FRONTEND_TEAM=@frontend-team  
SLACK_DESIGN_TEAM=@design-team
SLACK_QA_TEAM=@qa-team

# Claude API for diagnosis
CLAUDE_API_KEY=sk-ant-your-api-key
```

**📖 See [SLACK_SETUP_GUIDE.md](SLACK_SETUP_GUIDE.md) for detailed setup instructions.**

---

## 📊 Report Data Structure

Each test generates a JSON report in `reports/test_YYYY-MM-DD_HH-MM-SS/`:

```json
{
  "step_id": 3,
  "timestamp": "2026-02-07T22:09:43.965941",
  "persona": "Elderly User (65+)",
  "device": "iPhone 13 Pro",
  "network": "Slow 3G",
  "action": "Tap country dropdown",
  "confusion_score": 8,
  "ux_issues": [
    "Button too small for touch target (28px instead of 44px minimum)",
    "Insufficient loading feedback - no spinner visible"
  ],
  "outcome": {
    "status": "FAILED",
    "diagnosis": "Network timeout on country selector API endpoint",
    "severity": "P0",
    "responsible_team": "Backend",
    "f_score": 85,
    "calculated_severity": "P0",
    "recommendations": [
      "Add retry logic with exponential backoff",
      "Implement local fallback cache",
      "Display loading state with timeout warning"
    ]
  },
  "evidence": {
    "screenshot_before_path": "screenshots/step_03_before.png",
    "screenshot_after_path": "screenshots/step_03_after.png",
    "network_logs": [
      {"method": "GET", "url": "https://api.example.com/countries", "status": 500}
    ],
    "console_logs": [
      "[error] Failed to fetch countries: Network timeout after 30000ms"
    ]
  }
}
```

---

## ✅ Checklist - All Features Implemented

- [x] Creates dedicated Slack thread for each issue
- [x] Uploads screenshots (before/after)
- [x] Uploads GIF screen recordings when available
- [x] Includes network logs with HTTP status codes
- [x] Includes console logs (errors/warnings)
- [x] Tags specific team (@backend/@frontend/@design)
- [x] Severity assessment (P0-P3) with emoji indicators
- [x] F-Score (frustration metric 0-100)
- [x] User confusion score (0-10) with color coding
- [x] Reproduction steps with persona/device/network
- [x] AI-generated recommendations (2-3 actionable fixes)
- [x] Root cause intelligence linking similar historical issues
- [x] Pattern detection ("5 similar incidents detected")

---

## 🚀 Test It Now

```bash
# Start API server
python api_server.py

# Run autonomous test (will trigger alert on failure)
python main.py

# Or test specific scenario
python main.py https://deriv.com/signup --persona elderly --device iphone13
```

**Expected Console Output:**
```
  Diagnosing with Claude + Vision...
  AI determined: Backend team responsible (500 error detected)

📤 Smart Routing: Backend team → #C01ABC12DEF
   Uploading GIF...
✅ Alert sent successfully to Backend team in #backend-alerts
```

**Expected Slack Result:**
- ✅ #backend-alerts receives the alert
- ✅ #frontend-alerts - Empty (no spam)
- ✅ #design-alerts - Empty (no spam)
- ✅ #qa-alerts - Empty (no spam)

**Alert includes:** Team mention, evidence uploads, confusion score, diagnosis, network logs, console logs, reproduction steps, and root cause intelligence linking to similar historical issues.
