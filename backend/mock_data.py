# mock_data.py (Telemetry Edition)

"""
CURSOR DETECTION INSTRUCTIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Cursor position is NOT detected from screenshots (most screenshot tools
don't capture it). Instead, get coordinates from your automation tool:

METHOD 1: Selenium WebDriver (Recommended)
    from backend.cursor_detector import get_cursor_from_selenium_action
    
    element = driver.find_element(By.ID, "signup-btn")
    coords = get_cursor_from_selenium_action(element, driver)
    
    # Add to meta_data:
    # 'touch_x': 0.65, 'touch_y': 0.45

METHOD 2: Playwright (Recommended)
    from backend.cursor_detector import get_cursor_from_playwright_action
    
    locator = page.locator("#signup-btn")
    coords = get_cursor_from_playwright_action(locator, page)

METHOD 3: Manual Coordinates
    - touch_x: Horizontal position (0.0 = left, 1.0 = right)
    - touch_y: Vertical position (0.0 = top, 1.0 = bottom)
    - Example: Center of screen = (0.5, 0.5)

See cursor_detector.py for full integration examples.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

def get_mock_handoff():
    return {
        "step_id": 1,
        "persona": "Rushed Commuter (Low Connectivity)", 
        "action_taken": "Clicked 'Sign Up' button",
        "agent_expectation": "I expect the loading spinner to appear or a success message.",
        "outcome": {}, 
        
        # NEW: Real Telemetry Data (No more guessing)
        "meta_data": {
            "device_type": "Mobile (Pixel 7)",  # Satisfies "Mobile Testing"
            "network_type": "3G (High Latency)", # Satisfies "Network Conditions"
            "locale": "en-US",                   # Satisfies "Localized Flow"
            
            # The exact point where frustration occurred
            "touch_x": 0.65, 
            "touch_y": 0.45,
            
            # Real metrics for the Formula
            "dwell_time_ms": 4200,    # User waited 4.2s (Frustrating!)
            "previous_entropy": 5.2,  # Complexity of screen BEFORE click
            "current_entropy": 5.2    # Complexity AFTER (Same = Frozen)
        },

        "evidence": { 
            "screenshot_before_path": "backend/assets/mock_before.jpg", 
            "screenshot_after_path": "backend/assets/mock_after.jpg",
            "network_logs": [
                {"status": 200, "url": "/api/config"},
                {"status": 500, "url": "/api/register", "error": "Internal Server Error"} 
            ],
            "console_logs": [
                "Warning: Viewport mismatch for mobile device", # Mobile specific log
                "Error: POST /api/register 500 (Internal Server Error)"
            ]
        }
    }