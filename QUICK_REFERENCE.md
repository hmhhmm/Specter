# Quick Reference: Severity ≠ Team Assignment

## The Two Dimensions

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║  DIMENSION 1: SEVERITY (Impact on User)                    ║
║  ────────────────────────────────────────                   ║
║  P0 🚨  Critical - Signup completely blocked               ║
║  P1 ⚠️   Major    - High friction, drop-off risk           ║
║  P2 ⚡  Minor    - Degraded experience                     ║
║  P3 ℹ️   Cosmetic - Low impact UI issues                  ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  DIMENSION 2: TEAM (Root Cause)                            ║
║  ───────────────────────────────                            ║
║  🔧 Backend   - Server, database, API infrastructure       ║
║  🎨 Frontend  - Client code, JavaScript, API calls         ║
║  🎯 Design    - UX, accessibility, visual                  ║
║  🔍 QA        - Unclear, needs investigation               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

## Example Matrix

| Severity | Team | Example Issue |
|----------|------|---------------|
| P0 🚨 | Backend | Database timeout blocks signup |
| P0 🚨 | Frontend | JavaScript error crashes form |
| P0 🚨 | Design | Submit button invisible on mobile |
| P0 🚨 | QA | Intermittent signup failure |
| P1 ⚠️ | Backend | Slow API response (5+ seconds) |
| P1 ⚠️ | Frontend | 404 missing API endpoint |
| P1 ⚠️ | Design | Poor error message UX |
| P2 ⚡ | Backend | Non-critical API slow |
| P2 ⚡ | Frontend | Console warnings |
| P2 ⚡ | Design | Touch target too small (28px) |
| P3 ℹ️ | Design | Minor spacing inconsistency |

## Decision Flow

```
┌─────────────────────────────────────┐
│  1. Analyze Impact → Set Severity  │
│  ─────────────────────────────────  │
│  • F-Score > 85?      → P0         │
│  • Confusion > 7?     → P1         │
│  • F-Score 50-70?     → P2         │
│  • F-Score < 50?      → P3         │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  2. Analyze Root Cause → Set Team  │
│  ─────────────────────────────────  │
│  • 5xx error?         → Backend    │
│  • 4xx error?         → Frontend   │
│  • No errors + UX?    → Design     │
│  • Unclear?           → QA         │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  3. Route to Team Channel          │
│  ─────────────────────────────────  │
│  Backend  → #backend-alerts        │
│  Frontend → #frontend-alerts       │
│  Design   → #design-alerts         │
│  QA       → #qa-alerts             │
└─────────────────────────────────────┘
```

## Real Examples from Tests

### ❌ WRONG Assumption
"P0 means Backend issue" ✗

### ✅ CORRECT Understanding
"P0 means signup is blocked, could be any team" ✓

---

### Example 1: Backend P0
```
Issue: Database connection timeout
├─ Severity: P0 (user cannot proceed)
├─ Team: Backend (500 error)
└─ Route: #backend-alerts
```

### Example 2: Frontend P0
```
Issue: API endpoint 404
├─ Severity: P0 (signup form doesn't submit)
├─ Team: Frontend (404 client error)
└─ Route: #frontend-alerts
```

### Example 3: Design P0
```
Issue: Button too small to tap on mobile
├─ Severity: P0 (user cannot click submit)
├─ Team: Design (UX/accessibility)
└─ Route: #design-alerts
```

### Example 4: Frontend P2
```
Issue: Console warnings about deprecated API
├─ Severity: P2 (no functional impact)
├─ Team: Frontend (client-side code quality)
└─ Route: #frontend-alerts
```

## Key Insight

**Same Symptom, Different Teams:**

"Signup button doesn't work" could be:
- Backend: API returns 500 error → **P0 Backend**
- Frontend: JavaScript error on click → **P0 Frontend**
- Design: Button too small to tap → **P0 Design**

All are P0 (critical impact), but route to different teams!

---

📖 For full details, see [SEVERITY_LOGIC.md](SEVERITY_LOGIC.md)
