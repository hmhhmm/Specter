# 🎯 Cursor Detection & Enhanced GIF Generation

## Problem Solved

### 1. **Cursor Detection from Screenshots**
Screenshots typically **DON'T capture the cursor**. We solve this by extracting coordinates from your automation framework.

### 2. **Better "Ghost Replay" GIFs**
The enhanced GIF now includes:
- ✅ **Click location indicator** (animated yellow circle)
- ✅ **Smooth 8-frame animation** (not just 2 frames)
- ✅ **Difference highlighting** (shows what changed in green)
- ✅ **3.2-second loop** for Slack visibility

---

## 🔧 How to Get Cursor Coordinates

### Option 1: Selenium WebDriver (Python)

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from backend.cursor_detector import enrich_handoff_with_cursor

driver = webdriver.Chrome()
driver.get("https://myapp.com/signup")

# User clicks button
button = driver.find_element(By.ID, "signup-btn")
button.click()

# Take screenshots
driver.save_screenshot("before.png")
# ... action happens ...
driver.save_screenshot("after.png")

# Create handoff packet
packet = {
    "step_id": 1,
    "persona": "New User",
    "action_taken": "Clicked signup button",
    "evidence": {
        "screenshot_before_path": "before.png",
        "screenshot_after_path": "after.png",
        ...
    },
    "meta_data": {}
}

# AUTO-DETECT cursor position
enrich_handoff_with_cursor(packet, "selenium", element=button, driver=driver)

# Packet now has: meta_data.touch_x, meta_data.touch_y
```

---

### Option 2: Playwright (Python)

```python
from playwright.sync_api import sync_playwright
from backend.cursor_detector import enrich_handoff_with_cursor

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://myapp.com/signup")
    
    # User clicks button
    locator = page.locator("#signup-btn")
    
    # Take screenshots
    page.screenshot(path="before.png")
    locator.click()
    page.screenshot(path="after.png")
    
    # Create packet
    packet = {...}
    
    # AUTO-DETECT cursor position
    enrich_handoff_with_cursor(packet, "playwright", locator=locator, page=page)
```

---

### Option 3: Puppeteer (Node.js) → Python

**JavaScript (Puppeteer):**
```javascript
const puppeteer = require('puppeteer');

const browser = await puppeteer.launch();
const page = await browser.newPage();
await page.goto('https://myapp.com/signup');

// Get element position
const button = await page.$('#signup-btn');
const box = await button.boundingBox();

// Calculate click coordinates
const clickX = box.x + (box.width / 2);
const clickY = box.y + (box.height / 2);

const viewport = page.viewport();

// Send to Python via JSON
const coords = {
    click_x: clickX,
    click_y: clickY,
    viewport_width: viewport.width,
    viewport_height: viewport.height
};

// POST to Python API or save to file
await fs.writeFile('cursor_coords.json', JSON.stringify(coords));
```

**Python:**
```python
import json
from backend.cursor_detector import parse_puppeteer_coords

with open('cursor_coords.json') as f:
    coords = json.load(f)

parsed = parse_puppeteer_coords(coords)
packet['meta_data'].update(parsed)
```

---

### Option 4: Manual Coordinates (Quick Test)

```python
packet = {
    "meta_data": {
        "touch_x": 0.65,  # 65% from left edge
        "touch_y": 0.45,  # 45% from top edge
        "device_type": "Desktop",
        "network_type": "4G",
        ...
    }
}

# touch_x: 0.0 = left edge, 0.5 = center, 1.0 = right edge
# touch_y: 0.0 = top edge, 0.5 = middle, 1.0 = bottom edge
```

---

## 🎬 Understanding the Enhanced GIF

The new `generate_ghost_replay()` creates an 8-frame animation:

| Frame | Duration | Content |
|-------|----------|---------|
| 1 | 400ms | **Before state** + click indicator starts |
| 2-4 | 400ms each | Click animation expands (yellow circle) |
| 5 | 400ms | **After state** + click indicator fades |
| 6 | 400ms | After state with **difference highlighting** (green overlay) |
| 7 | 400ms | Plain after state |
| 8 | 400ms | Back to before (loop continuity) |

**Total loop time:** 3.2 seconds

### Visual Indicators:
- 🟡 **Yellow expanding circle** = where user clicked
- 🔴 **Red center dot** = exact click point
- 🟢 **Green overlay** = areas that changed between before/after

---

## 📊 Example Output

### Before Enhancement:
```
GIF: [Before] → [After] → [Before] → [After] ...
Duration: 1 second loop
Issues: Hard to see what changed, no click indication
```

### After Enhancement:
```
GIF: [Before + Click Animation] → [After + Highlights] → [Before]
Duration: 3.2 second loop
Features:
  ✅ Shows exact click location
  ✅ Highlights visual differences
  ✅ Smooth animation (8 frames)
  ✅ Better Slack visibility
```

---

## 🔍 How It Works

### 1. **Click Indicator** (`add_click_indicator()`)
- Draws animated yellow circle at cursor position
- Expands from 15px → 40px over 6 frames
- Fades out as it expands
- Red dot marks exact center

### 2. **Difference Highlighting** (`create_difference_overlay()`)
- Compares grayscale images
- Detects pixel changes > 30 threshold
- Overlays green on changed areas
- 70/30 blend ratio for visibility

### 3. **Dynamic Positioning**
- Uses `meta_data.touch_x` and `touch_y` from automation tool
- Converts ratios to pixels: `x = width * touch_x`
- Fallback to center (0.5, 0.5) if not provided

---

## 🚀 Quick Start

**1. Install dependencies** (if not already done):
```bash
pip install opencv-python-headless imageio scikit-image
```

**2. Update your test agent**:
```python
from backend.cursor_detector import enrich_handoff_with_cursor

# After taking screenshots and before sending to Specter:
enrich_handoff_with_cursor(packet, "selenium", element=button, driver=driver)
```

**3. Run Specter:**
```bash
python main.py
```

**4. Check the outputs:**
- `backend/assets/ghost_replay.gif` - Enhanced 8-frame GIF with click indicators
- `backend/assets/evidence_heatmap.jpg` - Heatmap with dynamic positioning

---

## ❓ FAQ

**Q: Why doesn't my screenshot show the cursor?**  
A: Most screenshot tools (Selenium, Playwright, etc.) don't capture the cursor by default. Use automation framework coordinates instead.

**Q: Can I use visual cursor detection?**  
A: Yes, but it's unreliable. See `detect_cursor_visual()` in `cursor_detector.py`. You'll need cursor template images for each OS.

**Q: What if I don't provide cursor coordinates?**  
A: The system falls back to center position (0.5, 0.5). The GIF will still work but may not show the exact click location.

**Q: How do I verify the GIF is better?**  
A: Open `backend/assets/ghost_replay.gif` and look for:
1. Yellow circle showing where the click happened
2. Green overlay showing what changed
3. Smooth 8-frame animation

**Q: Can I disable difference highlighting?**  
A: Yes, set `show_diff=False` when calling `generate_ghost_replay()`.

---

## 📝 See Also

- [`cursor_detector.py`](backend/cursor_detector.py) - Full cursor detection utilities
- [`expectation_engine.py`](backend/expectation_engine.py) - GIF generation implementation
- [`mock_data.py`](backend/mock_data.py) - Example usage with coordinates
