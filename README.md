# 🔮 Specter - Autonomous AI Agent for Signup Testing

**100% autonomous signup testing with vision-based navigation and cognitive UX analysis**

Specter combines AI-powered navigation (Feature 1) with mathematical friction analysis (Feature 2) to automatically detect UX issues, accessibility problems, and network latency in signup flows.

---

## ✨ Features

### Feature 1: Multimodal Human-Persona Navigator (100%)
- ✅ Vision-based navigation using Claude Vision
- ✅ Autonomous decision-making (no hardcoded selectors)
- ✅ User persona simulation (normal, cautious, confused, elderly, mobile_novice)
- ✅ Device emulation (iPhone, Android, Desktop)
- ✅ Network throttling (3G, 4G, WiFi, Slow)
- ✅ Accessibility detection (button size, contrast, elderly-friendly)

### Feature 2: Cognitive UX Analyst & Diagnosis (100%)
- ✅ Mathematical F-Score calculation (friction metric)
- ✅ Dynamic AI Uncertainty Heatmap generation
- ✅ Ghost Replay GIF (animated failure replay)
- ✅ P0-P3 severity classification (impact-based)
- ✅ Smart team routing (Backend, Frontend, Design, QA)
- ✅ Claude Vision diagnosis with root cause analysis
- ✅ Slack escalation + PDF reports to team channels

📖 **[Understanding Severity & Team Assignment →](SEVERITY_LOGIC.md)**

---

## 🚀 Quick Start

### 1. Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright (for autonomous mode)
pip install playwright
playwright install chromium
```

### 2. Configuration

Create `.env` file in `backend/` folder:

```bash
# backend/.env
CLAUDE_API_KEY=your_claude_api_key_here
SLACK_WEBHOOK_URL=your_slack_webhook_url_here
```

---

## 🛠 Development setup (full-stack app)

For working on the Next.js dashboard (Lab, Vault, Command Center, Healer) with the FastAPI backend.

### Prerequisites

- **Node.js** 20+ (LTS or current). [nvm](https://github.com/nvm-sh/nvm) or [fnm](https://github.com/Schniz/fnm) recommended.
- **Python** 3.10+ and `pip`.
- **Git** (for Healer PRs; token required only if you use "Open GitHub Pull Request").

### 1. Install dependencies

```bash
# Frontend
npm install

# Backend
pip install -r requirements.txt

# Playwright (only if you run E2E or autonomous agent)
pip install playwright
playwright install chromium
# Optional for Next.js E2E: npx playwright install
```

### 2. Environment variables

**Backend** — create `backend/.env`:

```bash
CLAUDE_API_KEY=your_anthropic_api_key_here
SLACK_WEBHOOK_URL=your_slack_webhook_url_here   # optional
NVIDIA_API_KEY=your_nvidia_api_key_here         # optional; used by diagnosis/Healer
GEMINI_API_KEY=your_gemini_api_key_here         # optional; fallback
```

**Frontend** — create `.env.local` in the **project root** (next to `package.json`):

```bash
# GitHub (required for Specter Healer "Open GitHub Pull Request")
# Create a classic Personal Access Token with 'repo' scope: https://github.com/settings/tokens
GITHUB_TOKEN=your_github_pat_here
GITHUB_OWNER=your_github_username_or_org
GITHUB_REPO=Specter

# NVIDIA NIM (for Healer AI-generated fixes; can copy from backend/.env)
NVIDIA_API_KEY=your_nvidia_api_key_here
```

If `GITHUB_TOKEN` / `GITHUB_OWNER` are missing, the Healer still runs but will return a mocked PR (no real branch or PR created). Do **not** commit `.env` or `.env.local`; they are gitignored.

### 3. Run the app

```bash
# Terminal 1 — FastAPI backend (port 8000)
python run_dev.py

# Terminal 2 — Next.js (port 3000)
npm run dev
```

Then open [http://localhost:3000](http://localhost:3000). The Command Center (Page 4) talks to the backend at `http://localhost:8000`.

**Note:** On Windows, `run_dev.py` disables auto-reload to avoid socket errors; restart it manually after backend code changes.

### Line endings (Windows ↔ macOS/Linux)

The repo uses **LF** line endings (enforced via `.gitattributes`). That way Mac/Linux teammates don’t see CRLF-related diffs or script issues after pulling. On Windows, Git will still handle your working copy according to `core.autocrlf`; commits stay LF. If the repo had CRLF files before, a one-time renormalize (e.g. `git add --renormalize .` then commit) will fix them; after that, everyone gets LF.

---

### 3. Run Tests

**Demo Mode** (uses mock data, shows Feature 2):
```bash
python main.py
```

**Autonomous Mode** (full end-to-end testing):
```bash
# Basic test
python main.py autonomous https://example.com/signup

# With specific persona and device
python main.py autonomous https://spotify.com/signup --persona cautious --device iphone13

# Test with network throttling
python main.py autonomous https://app.com/signup --network 3g --device android

# Elderly accessibility test
python main.py autonomous https://yourapp.com/signup --persona elderly --device desktop

# All options
python main.py autonomous https://app.com/signup \
  --persona confused \
  --device iphone13 \
  --network slow \
  --locale es-ES
```

**Pre-built Demos**:
```bash
# Robust QA demo (tests all personas)
python demo_robust_qa.py

# Local test (3 scenarios with test_signup.html)
python test_autonomous_demo.py

# Integration verification (20/20 checks)
python verify_integration.py
```

---

## 📋 Available Options

### Personas (User Behavior)
| Persona | Description | Use Case |
|---------|-------------|----------|
| `normal` | Typical first-time user | General testing |
| `cautious` | Reads everything carefully | Detailed UI testing |
| `confused` | Struggles with UI | Error handling |
| `elderly` | 65+, needs large text/buttons | Accessibility testing |
| `mobile_novice` | First-time smartphone user | Mobile usability |

### Devices (Emulation)
| Device | Resolution | Use Case |
|--------|-----------|----------|
| `iphone13` | 390x844 | iOS mobile testing |
| `android` | 393x851 | Android testing |
| `desktop` | 1920x1080 | Desktop testing |

### Networks (Throttling)
| Network | Speed | Latency | Use Case |
|---------|-------|---------|----------|
| `wifi` | 30 Mbps | 2ms | Optimal conditions |
| `4g` | 4 Mbps | 20ms | Good mobile |
| `3g` | 400 Kbps | 400ms | Poor connection |
| `slow` | 50 Kbps | 800ms | Worst case |

---

## 📁 Project Structure

```
Specter/
├── main.py                    # Main autonomous agent
├── backend/
│   ├── expectation_engine.py  # F-Score calculation + heatmap/GIF
│   ├── diagnosis_doctor.py    # Claude Vision diagnosis
│   ├── escalation_webhook.py  # Slack alerts
│   ├── mock_data.py           # Demo data
│   └── webqa_bridge.py        # Integration layer
├── reports/                   # Generated test reports
│   └── test_TIMESTAMP/
│       ├── screenshots/       # Before/after images
│       ├── heatmap.png       # AI uncertainty heatmap
│       └── ghost_replay.gif  # Animated failure replay
├── demo_robust_qa.py         # Robust QA demonstration
├── test_autonomous_demo.py   # 3-scenario test suite
├── verify_integration.py     # Integration verification
└── test_signup.html          # Local test page
```

---

## 🎯 What Gets Detected

Specter's vision-based LLM analysis detects:

### 🔘 Button Size Issues
- Mobile touch targets < 44px (Apple HIG)
- Desktop buttons < 32px
- F-Score penalty: +3pts per undersized button

### 👴 Elderly Accessibility (WCAG AAA)
- Text size < 16px
- Contrast ratios < 7:1
- Complex language
- Unclear affordances
- F-Score penalty: +5pts if elderly_unfriendly + 3pts per issue

### 🌐 Network Latency
- Slow requests (>3s duration)
- Timeout errors in console
- Missing loading indicators
- F-Score penalty: +3pts per slow request, +5pts per timeout

### 🎯 Vision-Based Navigation
- Predicts exact click coordinates (x, y from screenshot)
- No hardcoded selectors needed
- Adapts to dynamic UIs

### 🧩 Confusion Risks
- Multiple similar buttons
- Form fields without labels
- Unclear error messages
- F-Score penalty: +3pts per issue

---

## 📊 Generated Artifacts

After each test, check:

```
reports/test_YYYY-MM-DD_HH-MM-SS_XXXXXX/
├── screenshots/
│   ├── step_1_before.png
│   ├── step_1_after.png
│   └── ...
├── heatmap.png          # Generated when F-Score > 50
└── ghost_replay.gif     # Generated when F-Score > 50
```

**Note**: Heatmaps and GIFs only generate on failures (F-Score > 50). Passing tests only save screenshots.

---

## 🧪 Testing Your Broken UI

If you have a broken UI for testing:

```bash
# Test with your broken UI
python main.py autonomous https://mocked-website.vercel.app/ --persona elderly

# Simulate high friction for full pipeline
python demo_high_friction.py
```

---

## 📈 F-Score Breakdown

Specter calculates a friction score (0-100) based on:

```
F-Score = Console Entropy (0-25)      # JS errors, warnings
        + Dwell Time (0-40)           # User waiting time
        + Semantic Distance (0-25)     # Expectation mismatch
        + Network Latency (0-20)       # Slow requests, timeouts
        + Accessibility (0-15)         # UI/UX issues
```

**Severity Classification**:
- **P0 (Critical)**: Signup completely blocked (F-Score > 85 OR 5xx errors)
- **P1 (Major)**: High friction, drop-off risk (F-Score > 70 OR confusion > 7)
- **P2 (Minor)**: Degraded experience (F-Score 50-70)
- **P3 (Cosmetic)**: Minor UI issues (F-Score < 50)

**Team Assignment** (independent of severity):
- **Backend**: 5xx errors, database issues, server timeouts
- **Frontend**: 4xx errors, JavaScript errors, API endpoint issues
- **Design**: UX/accessibility, touch targets, visual issues
- **QA**: Unclear root cause, needs investigation

**Important**: P0 ≠ Backend! A critical P0 signup block can be caused by Backend (DB timeout), Frontend (404 API), or Design (invisible button). See [SEVERITY_LOGIC.md](SEVERITY_LOGIC.md) for comprehensive examples.

---

## 🔧 Troubleshooting

**"Autonomous mode not available"**:
```bash
pip install playwright langchain langchain-anthropic
playwright install chromium
```

**"Claude API error"**:
- Check your `CLAUDE_API_KEY` in `backend/.env`
- Ensure you have Claude API credits

**"Vision analysis failed - invalid base64"**:
- This is a known issue being fixed
- Fallback to basic analysis still works
- Core functionality unaffected

**"No heatmap/GIF generated"**:
- These only generate when F-Score > 50 (failures)
- Check `backend/assets/` for demo mode artifacts
- Check `reports/test_*/` for autonomous mode artifacts

---

## 📚 Documentation

- **[AUTONOMOUS_DEMO.md](AUTONOMOUS_DEMO.md)** - Complete usage guide with examples
- **[ROBUST_QA.md](ROBUST_QA.md)** - Enhanced QA capabilities documentation
- **Backend Components**:
  - `expectation_engine.py` - F-Score algorithm details
  - `diagnosis_doctor.py` - AI diagnosis implementation
  
---

## 🎬 Example Output

```bash
$ python main.py autonomous https://app.com/signup --persona elderly

══════════════════════════════════════════════════════════════
🤖 SPECTER AUTONOMOUS AGENT - Initializing
══════════════════════════════════════════════════════════════
📍 URL: https://app.com/signup
📱 Device: Desktop 1920x1080
📡 Network: WiFi
👤 Persona: Elderly User (65+)

🔹 Step 1/4: Find and analyze the signup form
   ⚠️  UI Issues Detected:
      - Button too small - 28x28px, needs 44px+
      - Poor elderly access - text is 12px, needs 16px+
   🔎 Checking Step 1...
      + Accessibility Issues: 9.0pts (3 critical)
      + Elderly Unfriendly UI: +5.0pts
   📊 Final F-Score: 65.0/100 (P2)

🎬 AUTONOMOUS TEST COMPLETE
✅ Passed: 2/4
❌ Failed: 2/4
📊 Status: FAIL
══════════════════════════════════════════════════════════════
```

---

## 🤝 Contributing

This is a production-ready autonomous testing framework. All core features are implemented and functional.

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🔗 Quick Links

- Run basic test: `python main.py`
- Run autonomous: `python main.py autonomous <URL>`
- Verify integration: `python verify_integration.py`
- Robust QA demo: `python demo_robust_qa.py`
