
"""
Integration Bridge: webqa_agent → Specter

Converts webqa_agent test results and browser data into Specter's handoff packet format.
This allows Specter to analyze UX issues detected by webqa_agent.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import os
import glob
from pathlib import Path


def _resolve_screenshot_path(screenshot_path: str) -> str:
    """
    Convert relative screenshot paths from webqa_agent to absolute paths.
    
    webqa_agent returns relative paths like "screenshots/135529_752063_ahv1_test_element_0_before_click.png"
    which are relative to the reports directory (e.g., "reports/test_2026-02-07_13-55-13_046376/").
    
    This function finds the most recent reports directory and converts relative paths to absolute.
    
    Args:
        screenshot_path: Path from webqa_agent (relative or absolute)
        
    Returns:
        Absolute path to the screenshot file
    """
    if not screenshot_path:
        return screenshot_path
    
    # If already absolute and exists, return as-is
    if os.path.isabs(screenshot_path):
        return screenshot_path
    
    # If path exists relative to current directory, return absolute path
    if os.path.exists(screenshot_path):
        return os.path.abspath(screenshot_path)
    
    # Handle webqa_agent relative paths (screenshots/filename.png)
    # These are relative to the reports directory
    if screenshot_path.startswith("screenshots/"):
        # Find the most recent report directory
        reports_dir = "reports"
        if os.path.exists(reports_dir):
            # Get all test_* directories
            test_dirs = glob.glob(os.path.join(reports_dir, "test_*"))
            if test_dirs:
                # Sort by modification time (most recent first)
                most_recent = max(test_dirs, key=os.path.getmtime)
                absolute_path = os.path.join(most_recent, screenshot_path)
                
                # Return absolute path even if file doesn't exist yet
                # (file might be created shortly after this function is called)
                return os.path.abspath(absolute_path)
    
    # Fallback: try to make it absolute relative to current directory
    return os.path.abspath(screenshot_path)


def convert_click_result_to_handoff(
    click_result: Dict[str, Any],
    step_id: int = 1,
    persona: str = "Automated Test Agent",
    action_description: str = None,
    expectation: str = None
) -> Dict[str, Any]:
    """
    Convert webqa_agent click_handler result to Specter handoff packet.
    
    Args:
        click_result: Result from ClickHandler.click_and_screenshot()
        step_id: Test step number
        persona: User persona for context
        action_description: Human-readable action description
        expectation: Expected outcome
        
    Returns:
        Specter handoff packet ready for check_expectation()
        
    Example:
        from webqa_agent.actions.click_handler import ClickHandler
        
        click_handler = ClickHandler()
        result = await click_handler.click_and_screenshot(page, element_info)
        
        # Convert to Specter format
        handoff = convert_click_result_to_handoff(result, step_id=1)
        
        # Run through Specter
        from backend.main import run_specter_pipeline
        run_specter_pipeline(handoff)
    """
    
    element = click_result.get('element', {})
    click_coords = click_result.get('click_coordinates')
    
    # Extract click coordinates (absolute pixels)
    if click_coords:
        # webqa_agent returns {'x': px, 'y': px}
        viewport_width = click_result.get('viewport_width', 1920)
        viewport_height = click_result.get('viewport_height', 1080)
        
        touch_x = click_coords['x'] / viewport_width if viewport_width > 0 else 0.5
        touch_y = click_coords['y'] / viewport_height if viewport_height > 0 else 0.5
    else:
        # Fallback to center
        touch_x, touch_y = 0.5, 0.5
    
    # Build action description
    if not action_description:
        element_text = element.get('text', element.get('aria_label', 'element'))
        element_type = element.get('tag_name', 'button')
        action_description = f"Clicked {element_type}: '{element_text}'"
    
    # Build expectation
    if not expectation:
        if click_result.get('has_new_page'):
            expectation = "I expect a new page or tab to open with relevant content."
        else:
            expectation = "I expect the page to respond with visual feedback or navigation."
    
    # Calculate dwell time (time between before/after screenshots)
    dwell_time_ms = 2000  # Default assumption
    if click_result.get('timing'):
        dwell_time_ms = click_result['timing'].get('total_ms', 2000)
    
    # Build network logs from webqa_agent errors
    network_logs = []
    for error in click_result.get('network_errors', []):
        network_logs.append({
            'status': 0,
            'url': error.get('url', ''),
            'error': error.get('failure', 'Network Error')
        })
    
    for error in click_result.get('response_errors', []):
        network_logs.append({
            'status': error.get('status', 500),
            'url': error.get('url', ''),
            'error': error.get('status_text', 'HTTP Error')
        })
    
    # Add success log if no errors
    if not network_logs:
        network_logs.append({
            'status': 200,
            'url': click_result.get('element', {}).get('href', '/'),
        })
    
    # Build console logs
    console_logs = []
    for error in click_result.get('console_errors', []):
        console_logs.append(f"{error.get('type', 'error').upper()}: {error.get('text', '')}")
    
    # Get screenshot paths
    screenshot_before_path = click_result.get('screenshot_before_path')
    screenshot_after_path = click_result.get('screenshot_after_path') or click_result.get('new_page_screenshot_path')
    
    # If base64 data is provided but no path, save to file
    if not screenshot_before_path and click_result.get('screenshot_before'):
        screenshot_before_b64 = click_result.get('screenshot_before')
        if isinstance(screenshot_before_b64, str) and screenshot_before_b64.startswith('data:'):
            screenshot_before_path = _save_base64_screenshot(screenshot_before_b64, f"step_{step_id}_before.png")
    
    if not screenshot_after_path and click_result.get('screenshot_after'):
        screenshot_after_b64 = click_result.get('screenshot_after')
        if isinstance(screenshot_after_b64, str) and screenshot_after_b64.startswith('data:'):
            screenshot_after_path = _save_base64_screenshot(screenshot_after_b64, f"step_{step_id}_after.png")
    
    # Convert relative paths to absolute paths
    screenshot_before_path = _resolve_screenshot_path(screenshot_before_path)
    screenshot_after_path = _resolve_screenshot_path(screenshot_after_path)
    
    # Fallback to mock images if screenshots are still missing
    if not screenshot_before_path or not os.path.exists(screenshot_before_path):
        screenshot_before_path = "backend/assets/mock_before.jpg"
    if not screenshot_after_path or not os.path.exists(screenshot_after_path):
        screenshot_after_path = "backend/assets/mock_after.jpg"
    
    # Build the Specter handoff packet
    handoff_packet = {
        "step_id": step_id,
        "persona": persona,
        "action_taken": action_description,
        "agent_expectation": expectation,
        "outcome": {},
        
        "meta_data": {
            # REQUIRED for dynamic heatmap positioning
            "touch_x": touch_x,
            "touch_y": touch_y,
            
            # Telemetry for F-Score calculation
            "dwell_time_ms": dwell_time_ms,
            "device_type": click_result.get('device_type', 'Desktop (Playwright)'),
            "network_type": "Stable",  # webqa_agent runs in controlled environment
            "locale": click_result.get('locale', 'en-US'),
            
            # Additional context
            "click_method": click_result.get('click_method', 'unknown'),
            "has_new_page": click_result.get('has_new_page', False),
            "element_info": {
                "tag": element.get('tag_name'),
                "text": element.get('text'),
                "selector": element.get('selector'),
                "xpath": element.get('xpath'),
            }
        },
        
        "evidence": {
            "screenshot_before_path": screenshot_before_path,
            "screenshot_after_path": screenshot_after_path,
            "network_logs": network_logs,
            "console_logs": console_logs,
            
            # For cursor detection
            "click_coords": (int(click_coords['x']), int(click_coords['y'])) if click_coords else None,
            
            # Additional metadata
            "expected_outcome": expectation,
            "actual_outcome": "NEW_PAGE" if click_result.get('has_new_page') else "SAME_PAGE",
        }
    }
    
    return handoff_packet


def convert_ux_test_to_handoffs(
    ux_test_result,  # SubTestResult from webqa_agent
    base_step_id: int = 1000
) -> List[Dict[str, Any]]:
    """
    Convert webqa_agent UX test results to Specter handoff packets.
    
    Args:
        ux_test_result: SubTestResult from UX tester
        base_step_id: Starting step ID for generated packets
        
    Returns:
        List of Specter handoff packets (one per issue found)
        
    Example:
        from webqa_agent.testers.ux_tester import PageTextTest
        
        ux_tester = PageTextTest(llm_config, user_cases)
        result = await ux_tester.run(page)
        
        # Convert to Specter format
        handoffs = convert_ux_test_to_handoffs(result)
        
        # Run each through Specter
        for handoff in handoffs:
            run_specter_pipeline(handoff)
    """
    
    handoffs = []
    
    # If UX test failed, create handoff packets for each issue
    if ux_test_result.status == "failed":
        messages = ux_test_result.messages or {}
        
        for idx, (category, issue) in enumerate(messages.items()):
            handoff = {
                "step_id": base_step_id + idx,
                "persona": "UX Auditor (AI)",
                "action_taken": f"Analyzed page for UX issue: {category}",
                "agent_expectation": "I expect the page to follow UX best practices and be user-friendly.",
                "outcome": {},
                
                "meta_data": {
                    "touch_x": 0.5,  # Center of page for UX issues
                    "touch_y": 0.5,
                    "dwell_time_ms": 5000,  # UX analysis takes time
                    "device_type": "Desktop (UX Analysis)",
                    "network_type": "Stable",
                    "locale": ux_test_result.language if hasattr(ux_test_result, 'language') else 'en-US',
                    
                    "ux_category": category,
                    "test_type": "UX_AUDIT",
                    "sub_test_id": ux_test_result.sub_test_id,
                },
                
                "evidence": {
                    "screenshot_before_path": "backend/assets/mock_before.jpg",  # Placeholder
                    "screenshot_after_path": "backend/assets/mock_after.jpg",    # Placeholder
                    "network_logs": [{"status": 200, "url": "/"}],
                    "console_logs": [f"UX Issue ({category}): {issue}"],
                    
                    "expected_outcome": "Clean, accessible, user-friendly UI",
                    "actual_outcome": issue,
                }
            }
            
            # Try to get screenshot if available
            if hasattr(ux_test_result, 'screenshots') and ux_test_result.screenshots:
                screenshot = ux_test_result.screenshots[0]
                if hasattr(screenshot, 'path') and screenshot.path:
                    handoff["evidence"]["screenshot_before_path"] = screenshot.path
                    handoff["evidence"]["screenshot_after_path"] = screenshot.path
            
            handoffs.append(handoff)
    
    return handoffs


def _save_base64_screenshot(base64_data: str, filename: str) -> str:
    """
    Save base64-encoded screenshot to file.
    
    Args:
        base64_data: Base64 data URL (e.g., "data:image/png;base64,...")
        filename: Output filename
        
    Returns:
        Path to saved file
    """
    import base64
    
    # Extract base64 data (remove data:image/png;base64, prefix)
    if ',' in base64_data:
        base64_data = base64_data.split(',')[1]
    
    # Ensure assets directory exists
    assets_dir = "backend/assets"
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
    
    # Save to file
    output_path = os.path.join(assets_dir, filename)
    with open(output_path, 'wb') as f:
        f.write(base64.b64decode(base64_data))
    
    return output_path


def enrich_playwright_handoff(
    handoff_packet: Dict[str, Any],
    page,  # playwright.async_api.Page
    element = None  # playwright.async_api.ElementHandle
) -> Dict[str, Any]:
    """
    Enrich a Specter handoff packet with Playwright page/element data.
    
    This is a synchronous helper that extracts coordinates from Playwright objects.
    
    Args:
        handoff_packet: Existing Specter handoff packet
        page: Playwright Page object
        element: Playwright ElementHandle (optional)
        
    Returns:
        Updated handoff packet with click coordinates
        
    Example:
        # In an async Playwright context
        element = await page.query_selector("#signup-button")
        
        packet = get_mock_handoff()
        packet = await enrich_playwright_handoff_async(packet, page, element)
    """
    # Note: This needs to be called in async context
    # For sync usage, use the async version below
    return handoff_packet


async def enrich_playwright_handoff_async(
    handoff_packet: Dict[str, Any],
    page,  # playwright.async_api.Page
    element = None  # playwright.async_api.ElementHandle
) -> Dict[str, Any]:
    """
    Async version: Enrich handoff packet with Playwright data.
    
    Args:
        handoff_packet: Existing Specter handoff packet
        page: Playwright Page object
        element: Playwright ElementHandle (optional)
        
    Returns:
        Updated handoff packet
    """
    # Get viewport size
    viewport = page.viewport_size
    viewport_width = viewport['width'] if viewport else 1920
    viewport_height = viewport['height'] if viewport else 1080
    
    # Get element coordinates if provided
    if element:
        box = await element.bounding_box()
        if box:
            # Calculate center of element
            click_x = box['x'] + (box['width'] / 2)
            click_y = box['y'] + (box['height'] / 2)
            
            # Convert to ratios
            touch_x = click_x / viewport_width
            touch_y = click_y / viewport_height
            
            # Update packet
            if 'meta_data' not in handoff_packet:
                handoff_packet['meta_data'] = {}
            
            handoff_packet['meta_data']['touch_x'] = touch_x
            handoff_packet['meta_data']['touch_y'] = touch_y
            
            if 'evidence' not in handoff_packet:
                handoff_packet['evidence'] = {}
            
            handoff_packet['evidence']['click_coords'] = (int(click_x), int(click_y))
    
    return handoff_packet


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  USAGE EXAMPLES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
EXAMPLE 1: Basic Integration with ClickHandler

```python
from playwright.async_api import async_playwright
from webqa_agent.actions.click_handler import ClickHandler
from backend.webqa_bridge import convert_click_result_to_handoff
from backend.main import run_specter_pipeline

async def test_with_specter():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://example.com")
        
        # Use webqa_agent to test a button
        click_handler = ClickHandler()
        await click_handler.setup_listeners(page)
        
        element_info = {
            'selector': '#signup-button',
            'text': 'Sign Up',
            'tag_name': 'button'
        }
        
        result = await click_handler.click_and_screenshot(page, element_info)
        
        # Convert to Specter format
        handoff = convert_click_result_to_handoff(
            result,
            step_id=1,
            persona="New User Signup Flow",
            action_description="Clicked signup button",
            expectation="Signup form should appear"
        )
        
        # Run through Specter analysis
        run_specter_pipeline(handoff)
        
        await browser.close()
```

EXAMPLE 2: UX Test Integration

```python
from webqa_agent.testers.ux_tester import PageTextTest
from backend.webqa_bridge import convert_ux_test_to_handoffs

async def test_ux_with_specter():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://example.com")
        
        # Run webqa_agent UX test
        llm_config = {"provider": "claude", "api_key": "..."}
        ux_tester = PageTextTest(llm_config)
        ux_result = await ux_tester.run(page)
        
        # Convert to Specter format
        handoffs = convert_ux_test_to_handoffs(ux_result)
        
        # Run each issue through Specter
        for handoff in handoffs:
            run_specter_pipeline(handoff)
        
        await browser.close()
```

EXAMPLE 3: Full Integration Agent

```python
from webqa_agent.browser.session import BrowserSessionPool
from webqa_agent.testers.function_tester import FunctionTester
from backend.webqa_bridge import convert_click_result_to_handoff

async def full_integration_test():
    pool = BrowserSessionPool()
    
    async with pool.create_session() as session:
        page = session.page
        await page.goto("https://myapp.com")
        
        # Run webqa_agent functional tests
        function_tester = FunctionTester(llm_config={...})
        test_results = await function_tester.run(page)
        
        # For each test result, run through Specter
        for idx, test_result in enumerate(test_results):
            if test_result.click_result:
                handoff = convert_click_result_to_handoff(
                    test_result.click_result,
                    step_id=idx + 1
                )
                run_specter_pipeline(handoff)
```
"""
