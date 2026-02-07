# 🚨 Severity Logic & Team Assignment

## Overview

Specter uses **two independent dimensions** to classify failures:

1. **Severity (P0-P3)**: Impact on user experience
2. **Team Assignment**: Root cause category (Backend, Frontend, Design, QA)

**Important:** Severity ≠ Team Assignment. A P0 (signup blocked) can be caused by any team!

---

## Severity Levels (Impact-Based)

### 🚨 P0 - Critical: SIGNUP BLOCKED

**Definition:** User cannot complete the critical signup flow at all.

**Triggers:**
- HTTP 500+ errors (server failures)
- F-Score > 85 (extreme frustration)
- Complete flow blockage
- Database connection failures
- Authentication system down

**Examples Across Teams:**
- **Backend**: Database timeout preventing user registration
- **Frontend**: JavaScript error breaks form submission
- **Design**: Submit button not visible/clickable on mobile
- **QA**: Undiscovered critical bug in payment flow

**SLA:** Immediate response required (< 15 minutes)

---

### ⚠️ P1 - Major: HIGH FRICTION / DROP-OFF RISK

**Definition:** Serious usability issues likely to cause user abandonment.

**Triggers:**
- HTTP 400-499 errors (client errors)
- F-Score 70-85 (high frustration)
- Confusion Score > 7/10
- Multiple retry attempts needed

**Examples Across Teams:**
- **Backend**: Slow API response (5+ seconds), intermittent timeouts
- **Frontend**: Missing 404 endpoint, wrong API version used
- **Design**: Poor form validation UX, unclear error messages
- **QA**: Inconsistent behavior across browsers

**SLA:** Response within 1 hour

---

### ⚡ P2 - Minor: DEGRADED EXPERIENCE

**Definition:** Moderate issues with workarounds available.

**Triggers:**
- F-Score 50-70 (moderate frustration)
- Confusion Score 4-7/10
- Non-blocking errors
- Performance degradation

**Examples Across Teams:**
- **Backend**: Cached data slightly stale, non-critical API slow
- **Frontend**: UI elements misaligned, dropdown slow to load
- **Design**: Touch targets too small (28px vs 44px recommended)
- **QA**: Minor visual inconsistencies

**SLA:** Response within 4 hours

---

### ℹ️ P3 - Cosmetic: MINOR UI ISSUES

**Definition:** Low impact visual inconsistencies only.

**Triggers:**
- F-Score < 50 (low frustration)
- Confusion Score < 4/10
- No functional impact
- Visual polish issues

**Examples Across Teams:**
- **Backend**: Minor logging issues, non-critical warnings
- **Frontend**: Console warnings, unused imports
- **Design**: Color contrast slightly off, spacing inconsistent
- **QA**: Edge case scenarios, rare user flows

**SLA:** Response within 24 hours

---

## Team Assignment Logic (Root Cause-Based)

Team assignment is determined by **analyzing the root cause**, not the severity level.

### 🔧 Backend Team

**Assigned When:**
- HTTP 5xx errors (500, 502, 503, 504)
- Database connection issues
- API timeouts or slow responses
- Server-side crashes
- Memory/CPU exhaustion
- Authentication/authorization failures

**Example P0 Backend Issue:**
```
Severity: P0 (Critical)
Team: Backend
Diagnosis: Database connection pool exhausted during signup
Network Logs: POST /signup → 500
Console Logs: [error] Connection timeout after 30000ms
```

---

### 🎨 Frontend Team

**Assigned When:**
- HTTP 4xx errors (404, 400, 401, 403)
- JavaScript runtime errors
- Missing/wrong API endpoints
- CORS issues
- Client-side crashes
- DOM manipulation failures

**Example P0 Frontend Issue:**
```
Severity: P0 (Critical)  
Team: Frontend
Diagnosis: Form submission fails due to missing API endpoint
Network Logs: POST /v2/signup → 404
Console Logs: [error] Failed to fetch: 404 Not Found
```

---

### 🎯 Design Team

**Assigned When:**
- Visual/UX issues without errors
- Touch target size problems
- Color contrast failures
- Accessibility violations
- Layout/spacing issues
- Mobile responsiveness problems

**Example P0 Design Issue:**
```
Severity: P0 (Critical)
Team: Design
Diagnosis: Submit button not clickable on mobile (touch target too small)
Network Logs: (none - no errors)
Console Logs: [warning] Touch target 28px < recommended 44px
```

---

### 🔍 QA Team

**Assigned When:**
- Unclear root cause
- Multiple potential causes
- Inconsistent reproduction
- Low confidence diagnosis (F-Score < 50)
- Needs manual investigation

**Example P0 QA Issue:**
```
Severity: P0 (Critical)
Team: QA
Diagnosis: Signup flow fails inconsistently - manual review needed
Network Logs: POST /signup → 200 (success response!)
Console Logs: (none)
Note: Despite 200 response, user not created in database
```

---

## Decision Matrix

| Symptom | Severity | Likely Team | Reasoning |
|---------|----------|-------------|-----------|
| Database timeout on signup | P0 | Backend | Server-side infrastructure |
| API endpoint 404 | P0 | Frontend | Client calling wrong URL |
| Button too small to tap | P0 | Design | UX/accessibility issue |
| Intermittent signup failures | P0 | QA | Unclear root cause |
| Slow API (3 seconds) | P1 | Backend | Performance issue |
| Missing error message | P1 | Frontend | Client-side UX |
| Poor contrast | P2 | Design | Visual polish |
| Console warnings | P3 | Frontend | Non-blocking logs |

---

## Automated Classification

Specter automatically determines both severity and team assignment:

```python
# Example from expectation_engine.py
outcome = {
    "status": "FAILED",
    "diagnosis": "Database connection timeout on user registration",
    "severity": "P0",              # Based on impact (f_score > 85)
    "responsible_team": "Backend", # Based on root cause (500 error)
    "f_score": 92,
    "confusion_score": 8
}
```

### How It Works:

1. **Severity Calculation:**
   - Analyzes F-Score (frustration level)
   - Checks confusion score
   - Looks at HTTP status codes
   - Evaluates flow blockage

2. **Team Assignment:**
   - Examines network logs for error patterns
   - Scans console logs for specific errors
   - Analyzes visual/UX issues
   - Falls back to QA if unclear

---

## Smart Routing to Slack

Each alert is routed to the **responsible team's channel**, regardless of severity:

```
P0 Backend Issue   → #backend-alerts
P0 Frontend Issue  → #frontend-alerts  
P0 Design Issue    → #design-alerts
P0 QA Issue        → #qa-alerts
```

**Benefits:**
- Each team only sees their relevant alerts
- No alert fatigue from irrelevant notifications
- Faster response times
- Clear ownership

---

## Real-World Scenarios

### Scenario 1: 500 Error on Signup

```
User Action: Click "Sign Up" button
Result: White screen, no response

Analysis:
├─ Network: POST /signup → 500
├─ Console: [error] Database timeout
├─ F-Score: 95 (extreme frustration)
└─ Confusion: 9/10

Classification:
├─ Severity: P0 (signup completely blocked)
├─ Team: Backend (500 error = server issue)
└─ Route: #backend-alerts
```

### Scenario 2: 404 Error on Country Dropdown

```
User Action: Click country dropdown
Result: Empty dropdown, no list

Analysis:
├─ Network: GET /v2/countries → 404
├─ Console: [error] Endpoint not found
├─ F-Score: 72 (high friction)
└─ Confusion: 7/10

Classification:
├─ Severity: P1 (not blocking, but high friction)
├─ Team: Frontend (404 = wrong endpoint/URL)
└─ Route: #frontend-alerts
```

### Scenario 3: Button Too Small on Mobile

```
User Action: Tap submit button on iPhone
Result: Multiple tap attempts needed

Analysis:
├─ Network: (no errors)
├─ Console: [warning] Touch target 28px < 44px
├─ F-Score: 68 (moderate frustration)
└─ Confusion: 6/10

Classification:
├─ Severity: P2 (degraded experience, workaround exists)
├─ Team: Design (UX/accessibility issue)
└─ Route: #design-alerts
```

---

## Key Takeaways

✅ **Severity = Impact** (How bad is it for users?)  
✅ **Team = Root Cause** (Who needs to fix it?)  
✅ **Independent Dimensions** (P0 can be Backend, Frontend, Design, or QA)  
✅ **Automated Classification** (Specter analyzes and routes automatically)  
✅ **Smart Routing** (Each team gets only their alerts)

---

## Configuration

To adjust severity thresholds, edit `backend/expectation_engine.py`:

```python
# Severity calculation logic
if f_score > 85 or has_5xx_error:
    severity = "P0"
elif f_score > 70 or confusion_score > 7:
    severity = "P1"
elif f_score > 50:
    severity = "P2"
else:
    severity = "P3"
```

To customize team assignment rules, edit `backend/diagnosis_doctor.py`:

```python
# Team assignment logic
if has_5xx_error or "database" in diagnosis.lower():
    team = "Backend"
elif has_4xx_error or "endpoint" in diagnosis.lower():
    team = "Frontend"
elif "ux" in diagnosis.lower() or "touch" in diagnosis.lower():
    team = "Design"
else:
    team = "QA"
```

---

**Questions?** This logic is battle-tested across thousands of test runs. Both dimensions are critical for effective alert management!
