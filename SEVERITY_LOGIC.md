# Specter AI - Severity Classification Logic

## Overview
Specter automatically classifies every detected issue into 4 severity levels (P0-P3) based on **impact to signup flow** and **user friction**.

## Severity Definitions

### 🔴 P0 - Critical: SIGNUP BLOCKED
**Complete blocker - user cannot proceed at all**

**Automatic Triggers:**
- ✓ HTTP 500/502/503 errors (backend crashed)
- ✓ F-Score > 85/100 (extreme friction)
- ✓ Complete workflow failure

**Impact:** User abandons immediately, zero conversion

**Alert Channel:** Routes to responsible team (#backend-alerts, #frontend-alerts, etc.)

**Example:**
```
❌ Backend API returned 500 error
❌ Form submission completely broken
❌ Page crashes on load
```

---

### 🟠 P1 - Major: HIGH FRICTION / DROP-OFF RISK
**Serious usability issues likely to cause abandonment**

**Automatic Triggers:**
- ✓ HTTP 400/404 errors (broken functionality)
- ✓ F-Score > 70/100 (high friction)
- ✓ Confusion Score > 7/10 (user very confused)
- ✓ Console errors + F-Score > 55

**Impact:** High probability of user drop-off, significant conversion loss

**Alert Channel:** Routes to responsible team

**Example:**
```
⚠️ Country dropdown not responding
⚠️ Validation errors unclear
⚠️ Button click does nothing
```

---

### 🟡 P2 - Minor: DEGRADED EXPERIENCE
**Moderate issues - workarounds exist but UX suffers**

**Automatic Triggers:**
- ✓ F-Score 50-70/100 (moderate friction)
- ✓ Confusion Score 4-7/10
- ✓ Minor errors with some friction (400 errors + F-Score 40-60)

**Impact:** User can complete signup but experiences frustration

**Alert Channel:** Routes to responsible team

**Example:**
```
⚠️ Form takes multiple attempts
⚠️ Unclear instructions
⚠️ Slow page transitions
```

---

### 🔵 P3 - Cosmetic: MINOR UI ISSUES
**Low impact visual inconsistencies**

**Automatic Triggers:**
- ✓ F-Score < 50/100 (low friction)
- ✓ Confusion Score < 4/10
- ✓ UI inconsistencies only

**Impact:** Minimal impact on conversion, polish issues

**Alert Channel:** Routes to responsible team

**Example:**
```
ℹ️ Button alignment off by 2px
ℹ️ Font size inconsistent
ℹ️ Color contrast could be better
```

---

## F-Score Components

The **F-Score (0-100)** measures total user friction:

| Factor | Weight | Impact |
|--------|--------|--------|
| Visual Change | 25% | Did page update as expected? |
| Network Errors | 30% | 400/500 status codes |
| Console Errors | 15% | JavaScript errors |
| Confusion Score | 20% | How confused is the user? (0-10) |
| Dwell Time | 10% | Time between actions |

**Formula:**
```
F-Score = (visual_delta × 0.25) + 
          (network_score × 0.30) + 
          (console_score × 0.15) + 
          (confusion × 0.20) + 
          (dwell_penalty × 0.10)
```

---

## Team Routing Logic

Each issue automatically routes to the **responsible team's Slack channel**:

| Condition | Team | Channel |
|-----------|------|---------|
| 500/502 errors | Backend | #backend-alerts |
| 400/404 errors | Frontend | #frontend-alerts |
| Visual/CSS/UX | Design | #design-alerts |
| Unclear/Multiple | QA | #qa-alerts |

**Smart Routing = Zero Spam**
- Backend team only sees backend issues
- Frontend team only sees frontend issues
- No @channel spam, no noise

---

## Alert Workflow

```
┌─────────────────┐
│  Test Running   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Issue Detected  │ ← AI observes friction
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Calculate       │ ← F-Score, confusion, errors
│ F-Score         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Classify        │ ← Automatic P0/P1/P2/P3
│ Severity        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Diagnose        │ ← Claude Vision analysis
│ Root Cause      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Assign Team     │ ← Backend/Frontend/Design/QA
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 🚨 SLACK ALERT  │ ← Sent to team's channel
│ Sent to Team    │    (ALL severities alert)
└─────────────────┘
```

**Real-time:** Alerts sent **immediately** when issue detected (not batch)

---

## Configuration

### Environment Variables (.env)
```env
# Slack Bot Token
SLACK_BOT_TOKEN=xoxb-your-token

# Team Channels (each team gets their own)
SLACK_BACKEND_CHANNEL=C0ADFC8LAQ3
SLACK_FRONTEND_CHANNEL=C0ADKMZQY8N
SLACK_DESIGN_CHANNEL=C0ADJB8J11B
SLACK_QA_CHANNEL=C0ADFCARY75
```

### Bot Setup
1. Invite bot to each team channel:
   ```
   /invite @Specter Bot
   ```

2. Verify in each channel:
   - #backend-alerts
   - #frontend-alerts
   - #design-alerts
   - #qa-alerts

---

## Examples

### Example 1: P0 Backend Blocker
```
Step 3: User clicks "Submit"
├─ Action: click_button("Submit")
├─ Result: ❌ FAILED
├─ Network: 500 Internal Server Error
├─ F-Score: 88/100
├─ Severity: P0 - Critical
├─ Team: Backend
├─ Diagnosis: "API endpoint crashed, user blocked"
└─ 🚨 Alert → #backend-alerts
```

### Example 2: P1 Frontend Issue
```
Step 5: User selects country
├─ Action: select_dropdown("Country")
├─ Result: ❌ FAILED
├─ Network: 200 OK
├─ F-Score: 72/100
├─ Confusion: 8/10
├─ Severity: P1 - Major
├─ Team: Frontend
├─ Diagnosis: "Dropdown not responding, high confusion"
└─ 🚨 Alert → #frontend-alerts
```

### Example 3: P2 Design Issue
```
Step 2: User views form
├─ Action: observe_page
├─ Result: ⚠️ DEGRADED
├─ F-Score: 58/100
├─ Confusion: 5/10
├─ UX Issues: ["Long form requires scrolling", "No password hints"]
├─ Severity: P2 - Minor
├─ Team: Design
├─ Diagnosis: "Form UX challenging for elderly users"
└─ 🚨 Alert → #design-alerts
```

---

## Tuning Severity Thresholds

Want to adjust sensitivity? Edit `backend/expectation_engine.py`:

```python
def determine_severity_rule(f_score, network_logs, console_logs, ui_analysis):
    # Adjust these thresholds:
    
    if has_500_error or f_score > 85:  # P0 threshold
        return "P0 - Critical"
    
    if f_score > 70 or confusion_score > 7:  # P1 threshold
        return "P1 - Major"
    
    if f_score > 50 or confusion_score > 4:  # P2 threshold
        return "P2 - Minor"
    
    return "P3 - Cosmetic"
```

---

## Monitoring

View live diagnostics in **/lab** frontend:
- Real-time confusion scores
- Network activity
- F-score calculation
- Slack alert status

All diagnostic data streams to the terminal as tests run.
