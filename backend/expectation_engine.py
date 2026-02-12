# expectation_engine.py (The "Pro" Logic)
"""
Specter Expectation Engine - F-Score Calculation & Severity Classification

IMPORTANT: Severity (P0-P3) and Team Assignment are INDEPENDENT dimensions!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SEVERITY LEVELS (Impact-Based):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
P0 - Critical: SIGNUP BLOCKED (any team can cause this!)
  └─ User cannot proceed at all
  └─ Triggers: 500 errors, f_score > 85
  └─ Examples: Backend DB timeout, Frontend API 404, Design button invisible

P1 - Major: HIGH FRICTION / DROP-OFF RISK
  └─ Serious usability issues likely to cause abandonment
  └─ Triggers: 400 errors + friction, f_score > 70, confusion > 7/10
  └─ Examples: Slow APIs, missing endpoints, poor UX

P2 - Minor: DEGRADED EXPERIENCE
  └─ Moderate issues, workarounds exist
  └─ Triggers: f_score 50-70, confusion 4-7/10, minor errors
  └─ Examples: Performance degradation, small touch targets

P3 - Cosmetic: MINOR UI ISSUES
  └─ Low impact, visual inconsistencies only
  └─ Triggers: f_score < 50, confusion < 4/10
  └─ Examples: Console warnings, spacing issues

TEAM ASSIGNMENT (Root Cause-Based):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Backend:  5xx errors, DB issues, server timeouts
- Frontend: 4xx errors, JS errors, API endpoint issues  
- Design:   UX/accessibility, touch targets, visual issues
- QA:       Unclear root cause, needs investigation

See SEVERITY_LOGIC.md for comprehensive examples and decision matrix
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ALL severity levels trigger Slack alerts for complete visibility.
"""
import cv2
import numpy as np
import imageio
from skimage.metrics import structural_similarity as ssim
import os

def generate_heatmap(img_path, output_path, x_ratio, y_ratio, intensity=0.5):
    """
    Professional Heatmap: Multiple friction zones with gradient falloff.
    Creates a more realistic "heat signature" effect.
    """
    img = cv2.imread(img_path)
    if img is None: return None
    
    overlay = img.copy()
    rows, cols, _ = img.shape
    
    # Convert ratio to pixels
    center_x = int(cols * x_ratio)
    center_y = int(rows * y_ratio)
    
    # Create gradient heatmap (not just solid circle)
    # Multiple concentric circles with decreasing intensity
    max_radius = int(50 + (intensity * 150))
    
    for i in range(5):
        radius = int(max_radius * (1 - i * 0.15))
        alpha_layer = 0.15 + (intensity * 0.15 * (5 - i))
        
        # Color gradient: Red (intense) → Orange → Yellow (less intense)
        if i == 0:
            color = (0, 0, 255)  # Pure red (BGR)
        elif i == 1:
            color = (0, 100, 255)  # Red-Orange
        elif i == 2:
            color = (0, 165, 255)  # Orange
        else:
            color = (0, 200, 255)  # Yellow-Orange
        
        layer = overlay.copy()
        cv2.circle(layer, (center_x, center_y), radius, color, -1)
        cv2.addWeighted(layer, alpha_layer, overlay, 1 - alpha_layer, 0, overlay)
    
    # Add outer glow effect
    glow_radius = max_radius + 30
    glow_layer = overlay.copy()
    cv2.circle(glow_layer, (center_x, center_y), glow_radius, (0, 50, 200), -1)
    cv2.addWeighted(glow_layer, 0.08, overlay, 0.92, 0, overlay)
    
    # Final blend with original
    alpha = 0.5 + (intensity * 0.2)
    heatmap_img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)
    
    # Add crosshair at exact click point
    line_color = (255, 255, 255)  # White
    line_length = 20
    cv2.line(heatmap_img, (center_x - line_length, center_y), (center_x + line_length, center_y), line_color, 2)
    cv2.line(heatmap_img, (center_x, center_y - line_length), (center_x, center_y + line_length), line_color, 2)
    cv2.circle(heatmap_img, (center_x, center_y), 3, (255, 255, 255), -1)
    
    cv2.imwrite(output_path, heatmap_img)
    return output_path

def add_click_indicator(img, x, y, frame_num=0, total_frames=12):
    """
    Professional click animation with ripple effect and shadow.
    """
    img_copy = img.copy()
    rows, cols = img.shape[:2]
    
    # Convert ratio to pixels
    center_x = int(cols * x) if x <= 1.0 else int(x)
    center_y = int(rows * y) if y <= 1.0 else int(y)
    
    # Animated ripple effect (2 expanding rings)
    progress = frame_num / max(total_frames - 1, 1)
    
    # Ring 1 (primary)
    radius1 = int(10 + (progress * 50))
    thickness1 = max(2, int(6 - (progress * 4)))
    alpha1 = max(0.0, 1.0 - (progress * 1.2))
    
    # Ring 2 (delayed secondary)
    ring2_start = 0.3
    if progress > ring2_start:
        progress2 = (progress - ring2_start) / (1.0 - ring2_start)
        radius2 = int(10 + (progress2 * 40))
        thickness2 = max(2, int(5 - (progress2 * 3)))
        alpha2 = max(0.0, 0.8 - (progress2 * 1.0))
    else:
        radius2, thickness2, alpha2 = 0, 0, 0
    
    overlay = img_copy.copy()
    
    # Draw shadow (black, slightly offset)
    if alpha1 > 0:
        cv2.circle(overlay, (center_x + 2, center_y + 2), radius1, (0, 0, 0), thickness1)
        cv2.addWeighted(overlay, alpha1 * 0.3, img_copy, 1 - (alpha1 * 0.3), 0, img_copy)
        
        overlay = img_copy.copy()
    
    # Draw primary ring (yellow)
    if alpha1 > 0:
        cv2.circle(overlay, (center_x, center_y), radius1, (0, 255, 255), thickness1)
        cv2.addWeighted(overlay, alpha1, img_copy, 1 - alpha1, 0, img_copy)
        
        overlay = img_copy.copy()
    
    # Draw secondary ring (cyan)
    if alpha2 > 0:
        cv2.circle(overlay, (center_x, center_y), radius2, (255, 255, 0), thickness2)
        cv2.addWeighted(overlay, alpha2, img_copy, 1 - alpha2, 0, img_copy)
        
        overlay = img_copy.copy()
    
    # Draw center target (always visible)
    cv2.circle(img_copy, (center_x, center_y), 5, (0, 0, 255), -1)  # Red center
    cv2.circle(img_copy, (center_x, center_y), 5, (255, 255, 255), 2)  # White outline
    
    return img_copy

def create_difference_overlay(img_before, img_after):
    """
    Professional difference visualization with contours and color-coded intensity.
    """
    # Convert to grayscale
    gray_before = cv2.cvtColor(img_before, cv2.COLOR_BGR2GRAY)
    gray_after = cv2.cvtColor(img_after, cv2.COLOR_BGR2GRAY)
    
    # Compute absolute difference
    diff = cv2.absdiff(gray_before, gray_after)
    
    # Apply blur to reduce noise
    diff = cv2.GaussianBlur(diff, (5, 5), 0)
    
    # Threshold to get significant changes
    _, thresh = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)
    
    # Find contours of changed regions
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Create colored overlay with intensity mapping
    img_overlay = img_after.copy()
    
    # Create heatmap from difference intensity
    diff_colored = cv2.applyColorMap(diff, cv2.COLORMAP_JET)
    
    # Blend only where changes occurred
    mask = thresh > 0
    img_overlay[mask] = cv2.addWeighted(img_after, 0.4, diff_colored, 0.6, 0)[mask]
    
    # Draw contours around changed regions
    cv2.drawContours(img_overlay, contours, -1, (0, 255, 0), 2)
    
    # Add change indicator text
    if len(contours) > 0:
        total_change_area = sum(cv2.contourArea(c) for c in contours)
        img_height, img_width = img_after.shape[:2]
        change_percent = (total_change_area / (img_width * img_height)) * 100
        
        # Add semi-transparent background for text
        text = f"Changed: {change_percent:.1f}%"
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, 0.7, 2)[0]
        
        # Background rectangle
        bg_x1, bg_y1 = 10, 10
        bg_x2, bg_y2 = bg_x1 + text_size[0] + 10, bg_y1 + text_size[1] + 10
        cv2.rectangle(img_overlay, (bg_x1, bg_y1), (bg_x2, bg_y2), (0, 0, 0), -1)
        cv2.rectangle(img_overlay, (bg_x1, bg_y1), (bg_x2, bg_y2), (0, 255, 0), 2)
        
        # Text
        cv2.putText(img_overlay, text, (15, 30), font, 0.7, (0, 255, 0), 2)
    
    return img_overlay, thresh

def add_diagnostic_overlay(img, frame_info, f_score=None, severity=None, error_msg=None):
    """
    Adds professional diagnostic information overlay to frame.
    """
    img_copy = img.copy()
    height, width = img.shape[:2]
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # Top banner with frame info
    banner_height = 40
    banner = np.zeros((banner_height, width, 3), dtype=np.uint8)
    banner[:] = (30, 30, 30)  # Dark gray
    
    # Frame timestamp
    cv2.putText(banner, frame_info, (10, 27), font, 0.6, (255, 255, 255), 1)
    
    # Add severity indicator
    if severity:
        severity_color = {
            'P0': (0, 0, 255),      # Red
            'P1': (0, 140, 255),    # Orange
            'P2': (0, 255, 255),    # Yellow
            'P3': (128, 128, 128)   # Gray
        }.get(severity, (255, 255, 255))
        
        cv2.putText(banner, f"[{severity}]", (width - 100, 27), font, 0.7, severity_color, 2)
    
    # F-Score indicator
    if f_score is not None:
        score_x = width - 250
        score_text = f"F-Score: {f_score:.1f}"
        
        # Color code based on score
        if f_score >= 80:
            score_color = (0, 0, 255)  # Red
        elif f_score >= 60:
            score_color = (0, 140, 255)  # Orange
        elif f_score >= 40:
            score_color = (0, 255, 255)  # Yellow
        else:
            score_color = (0, 255, 0)  # Green
        
        cv2.putText(banner, score_text, (score_x, 27), font, 0.6, score_color, 2)
    
    # Combine banner with image
    result = np.vstack([banner, img_copy])
    
    # Bottom error message banner (ALWAYS added for consistent frame size)
    error_banner_height = 50
    error_banner = np.zeros((error_banner_height, width, 3), dtype=np.uint8)
    
    if error_msg:
        error_banner[:] = (0, 0, 128)  # Dark red
        
        # Truncate long error messages
        max_chars = int(width / 8)
        if len(error_msg) > max_chars:
            error_msg = error_msg[:max_chars-3] + "..."
        
        cv2.putText(error_banner, f"Warning: {error_msg}", (10, 32), font, 0.5, (255, 255, 255), 1)
    else:
        error_banner[:] = (30, 30, 30)  # Dark gray (same as top, no error)
    
    result = np.vstack([result, error_banner])
    
    return result

def generate_ghost_replay(img_a_path, img_b_path, output_path, click_x=0.5, click_y=0.5, f_score=None, severity=None, error_msg=None, show_diff=True):
    """
    PROFESSIONAL Ghost Replay GIF with:
    - Smooth 16-frame animation (not 8)
    - Dual ripple effect on click
    - Diagnostic overlays (F-Score, severity, errors)
    - Enhanced difference visualization with contours
    - Professional color grading
    """
    img_a = cv2.imread(img_a_path)
    img_b = cv2.imread(img_b_path)
    if img_a is None or img_b is None:
        return None

    # Ensure same dimensions
    if img_a.shape != img_b.shape:
        height, width = img_a.shape[:2]
        img_b = cv2.resize(img_b, (width, height))

    # Convert to RGB
    img_a_rgb = cv2.cvtColor(img_a, cv2.COLOR_BGR2RGB)
    img_b_rgb = cv2.cvtColor(img_b, cv2.COLOR_BGR2RGB)
    
    frames = []
    total_frames = 16
    
    # Frames 1-2: Before state (hold)
    for i in range(2):
        frame = add_diagnostic_overlay(img_a_rgb, f"Frame {i+1}/{total_frames} | BEFORE", f_score, severity)
        frames.append(frame)
    
    # Frames 3-8: Click animation on before state (6 frames)
    for i in range(6):
        frame_with_click = add_click_indicator(img_a_rgb, click_x, click_y, i, 12)
        frame = add_diagnostic_overlay(frame_with_click, f"Frame {i+3}/{total_frames} | CLICK", f_score, severity)
        frames.append(frame)
    
    # Frame 9: Transition moment (blend)
    blend = cv2.addWeighted(img_a_rgb, 0.5, img_b_rgb, 0.5, 0)
    frame = add_diagnostic_overlay(blend, f"Frame 9/{total_frames} | TRANSITION", f_score, severity)
    frames.append(frame)
    
    # Frames 10-11: After state with click indicator fading
    for i in range(2):
        frame_with_click = add_click_indicator(img_b_rgb, click_x, click_y, 6 + i, 12)
        frame = add_diagnostic_overlay(frame_with_click, f"Frame {i+10}/{total_frames} | AFTER", f_score, severity, error_msg)
        frames.append(frame)
    
    # Frame 12-13: Difference highlighting
    if show_diff:
        diff_img, _ = create_difference_overlay(img_a, img_b)
        diff_rgb = cv2.cvtColor(diff_img, cv2.COLOR_BGR2RGB)
        for i in range(2):
            frame = add_diagnostic_overlay(diff_rgb, f"Frame {i+12}/{total_frames} | DIFF ANALYSIS", f_score, severity, error_msg)
            frames.append(frame)
    else:
        for i in range(2):
            frame = add_diagnostic_overlay(img_b_rgb, f"Frame {i+12}/{total_frames} | AFTER", f_score, severity, error_msg)
            frames.append(frame)
    
    # Frame 14-15: After state (hold for analysis)
    for i in range(2):
        frame = add_diagnostic_overlay(img_b_rgb, f"Frame {i+14}/{total_frames} | RESULT", f_score, severity, error_msg)
        frames.append(frame)
    
    # Frame 16: Back to before for seamless loop
    frame = add_diagnostic_overlay(img_a_rgb, f"Frame 16/{total_frames} | LOOP", f_score, severity)
    frames.append(frame)
    
    try:
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # 300ms per frame = 4.8 second total loop
        imageio.mimsave(output_path, frames, duration=300, loop=0)
    except TypeError:
        imageio.mimsave(output_path, frames, fps=3.33)
    except Exception as e:
        print(f"Warning: Failed to save GIF: {e}")
        return None
    
    return output_path

def calculate_console_entropy(console_logs):
    """
    Measures chaos/uncertainty in console logs.
    More errors/warnings = higher entropy.
    """
    if not console_logs:
        return 0.0
    
    error_count = sum(1 for log in console_logs if 'error' in str(log).lower())
    warning_count = sum(1 for log in console_logs if 'warning' in str(log).lower())
    
    # Errors are 5x more severe than warnings
    entropy_score = (error_count * 10) + (warning_count * 2)
    return min(25.0, entropy_score)

def calculate_semantic_distance(expected, actual, ssim_score):
    """
    Measures how far the outcome diverged from expectation.
    Combines visual stagnation (SSIM) with state change analysis.
    """
    # Visual component: High SSIM = screen didn't change = max distance
    if ssim_score > 0.99:
        return 25.0  # Complete semantic failure
    elif ssim_score > 0.95:
        return 15.0
    elif ssim_score > 0.90:
        return 5.0
    
    # If screen changed, expectation was somewhat met
    return 0.0

def calculate_real_f_score(telemetry, ssim_score, network_logs, console_logs, expected_outcome, ui_analysis=None):
    """
    TRUE FORMULA: F-Score = Entropy + Dwell Time + Semantic Distance + Network Latency + Accessibility
    
    Components:
    - Console Entropy: 0-25pts (chaos from errors)
    - Dwell Time: 0-40pts (user waiting)
    - Semantic Distance: 0-25pts (expectation mismatch)
    - Network Latency: 0-20pts (slow responses, timeouts)
    - Accessibility Issues: 0-15pts (elderly/mobile usability)
    
    Total: 0-125pts (capped at 100)
    """
    score = 0.0
    
    # Component 1: ENTROPY (Console chaos - 0-25pts)
    entropy = calculate_console_entropy(console_logs)
    score += entropy
    if entropy > 0:
        print(f"      + Console Entropy: {entropy:.1f}pts")
    
    # Component 2: DWELL TIME (User waiting - 0-40pts)
    # 🔧 ADJUSTED: Only penalize excessive waiting (>5s), not normal thinking time
    dwell_ms = telemetry.get('dwell_time_ms', 0)
    if dwell_ms > 5000:  # Changed from 2000ms to 5000ms
        dwell_penalty = min(40.0, (dwell_ms - 5000) / 150)  # Reduced penalty rate
        score += dwell_penalty
        print(f"      + Dwell Time: {dwell_penalty:.1f}pts ({dwell_ms}ms wait)")
    
    # Component 3: SEMANTIC DISTANCE (Expectation mismatch - 0-25pts)
    # 🔧 REDUCED WEIGHT: Only penalize heavy stagnation (SSIM > 0.95 = almost no change)
    if ssim_score > 0.95:
        semantic = min(15.0, (ssim_score - 0.95) * 300)  # Reduced from 25pts max
        score += semantic
        if semantic > 0:
            print(f"      + Semantic Distance: {semantic:.1f}pts (Visual stagnation)")
    # Don't penalize normal UI transitions (dropdowns opening, modals, etc)
    
    # Component 4: NETWORK LATENCY (Slow/unresponsive - 0-20pts)
    network_penalty = 0.0
    
    # Detect slow requests (>3s = bad UX)
    slow_requests = [log for log in network_logs if log.get('duration', 0) > 3000]
    if slow_requests:
        network_penalty += min(10.0, len(slow_requests) * 3.0)
        print(f"      + Network Latency: {network_penalty:.1f}pts ({len(slow_requests)} slow requests)")
    
    # Detect timeouts (console errors mentioning timeout/network)
    timeout_errors = [log for log in console_logs if any(keyword in str(log).lower() for keyword in ['timeout', 'network', 'failed to fetch'])]
    if timeout_errors:
        timeout_penalty = min(10.0, len(timeout_errors) * 5.0)
        network_penalty += timeout_penalty
        print(f"      + Timeout Errors: {timeout_penalty:.1f}pts")
    
    score += network_penalty
    
    # Component 5: ACCESSIBILITY ISSUES (UI/UX problems - 0-15pts)
    accessibility_penalty = 0.0
    
    if ui_analysis:
        issues = ui_analysis.get('issues', [])
        
        # Critical issues for elderly/mobile users
        critical_issues = [
            issue for issue in issues 
            if any(keyword in issue.lower() for keyword in [
                'too small', 'elderly', 'contrast', 'font size', 
                'touch target', 'confusing', 'no loading'
            ])
        ]
        
        if critical_issues:
            accessibility_penalty = min(15.0, len(critical_issues) * 3.0)
            print(f"      + Accessibility Issues: {accessibility_penalty:.1f}pts ({len(critical_issues)} critical)")
            for issue in critical_issues[:2]:  # Show first 2
                print(f"         - {issue[:60]}...")
        
        # Elderly-specific penalty
        if not ui_analysis.get('elderly_friendly', True):
            accessibility_penalty += 5.0
            print(f"      + Elderly Unfriendly UI: +5.0pts")
    
    score += accessibility_penalty

    # Severity Multiplier: Backend errors amplify frustration
    has_500 = any(log['status'] >= 500 for log in network_logs)
    if has_500:
        score += 15.0  # Critical error bonus
        print("      + Backend Error: +15.0pts")

    # Final Score (0-100)
    final_score = min(100.0, round(score, 1))
    
    # 🔧 TEMPORARY HARDCODED CAP: Prevent inflated scores on normal websites
    # If no errors detected (no network issues, no console errors), cap at 35
    has_errors = False
    if network_logs:
        has_errors = any(log.get('status', 0) >= 400 for log in network_logs)
    if console_logs and not has_errors:
        has_errors = any('error' in str(log).lower() for log in console_logs)
    
    if not has_errors and final_score > 35:
        print(f"      ⚙️  Capping F-Score from {final_score} to 35 (no actual errors detected)")
        final_score = 35.0
    
    return final_score

def determine_severity_rule(f_score, network_logs, console_logs=None, ui_analysis=None):
    """
    Enhanced P0-P3 Severity Rules
    
    P0: Signup blocked (complete blocker - user cannot proceed)
    P1: High friction, drop-off risk (serious usability issues)
    P2: Degraded experience (moderate issues, workarounds exist)
    P3: Cosmetic issues (minor UI problems, low impact)
    """
    console_logs = console_logs or []
    ui_analysis = ui_analysis or {}
    
    # Check for critical errors
    has_500_error = any(log.get('status', 0) >= 500 for log in network_logs)
    has_400_error = any(400 <= log.get('status', 0) < 500 for log in network_logs)
    has_console_error = any('error' in str(log).lower() for log in console_logs)
    
    # Get confusion score (0-10 scale)
    confusion_score = ui_analysis.get('confusion_score', 0)
    
    # P0: SIGNUP BLOCKED - Complete blockers
    # - 500 errors (backend crashed)
    # - Extremely high friction (f_score > 85)
    # - Critical console errors + high confusion
    if has_500_error or f_score > 85:
        return "P0 - Critical"
    
    # P1: HIGH FRICTION / DROP-OFF RISK
    # - 400 errors (broken functionality)
    # - High friction (f_score > 70)
    # - Very high confusion (>7/10)
    # - Console errors with significant friction
    if has_400_error and f_score > 60:
        return "P1 - Major"
    if f_score > 70 or confusion_score > 7:
        return "P1 - Major"
    if has_console_error and f_score > 55:
        return "P1 - Major"
    
    # P2: DEGRADED EXPERIENCE
    # - Moderate friction (f_score 50-70)
    # - Moderate confusion (4-7/10)
    # - Minor errors with some friction
    if f_score > 50 or confusion_score > 4:
        return "P2 - Minor"
    if (has_400_error or has_console_error) and f_score > 40:
        return "P2 - Minor"
    
    # P3: COSMETIC ISSUES
    # - Low friction (f_score < 50)
    # - UI inconsistencies
    # - Minor confusion (<4/10)
    return "P3 - Cosmetic"

def check_expectation(handoff):
    print(f"Checking Step {handoff['step_id']}...")
    
    evidence = handoff['evidence']
    meta = handoff.get('meta_data', {})
    
    # Determine output paths based on screenshot location
    screenshot_path = evidence['screenshot_after_path']
    
    # If screenshot is in reports/test_*/screenshots/, save artifacts there
    if 'reports' in screenshot_path and 'screenshots' in screenshot_path:
        # Extract report directory: reports/test_TIMESTAMP/
        report_dir = os.path.dirname(os.path.dirname(screenshot_path))
        heatmap_path = os.path.join(report_dir, "heatmap.png")
        gif_path = os.path.join(report_dir, "ghost_replay.gif")
    else:
        # Fallback to backend/assets for mock data
        heatmap_path = "backend/assets/evidence_heatmap.jpg"
        gif_path = "backend/assets/ghost_replay.gif"

    # 1. Image Analysis
    img_a = cv2.imread(evidence['screenshot_before_path'])
    img_b = cv2.imread(evidence['screenshot_after_path'])
    
    current_ssim = 0.0
    if img_a is not None and img_b is not None:
         # Ensure images have same dimensions for SSIM comparison
         if img_a.shape != img_b.shape:
             height, width = img_a.shape[:2]
             img_b = cv2.resize(img_b, (width, height))
         
         gray_a = cv2.cvtColor(img_a, cv2.COLOR_BGR2GRAY)
         gray_b = cv2.cvtColor(img_b, cv2.COLOR_BGR2GRAY)
         current_ssim, _ = ssim(gray_a, gray_b, full=True)

    # 2. CALCULATE F-SCORE (The Real Formula)
    ui_analysis = evidence.get('ui_analysis', {})
    
    f_score = calculate_real_f_score(
        meta, 
        current_ssim, 
        evidence['network_logs'],
        evidence.get('console_logs', []),
        handoff.get('agent_expectation', ''),
        ui_analysis  # Pass vision-based UI analysis
    )
    
    # 3. ASSIGN SEVERITY (Deterministic Rules)
    severity_label = determine_severity_rule(
        f_score, 
        evidence['network_logs'],
        evidence.get('console_logs', []),
        ui_analysis
    )

    # 4. DECISION
    # If score > 50, we consider it a failure worth reporting
    if f_score > 50:
        print(f"   Final F-Score: {f_score:.1f}/100 ({severity_label})")
        
        # Calculate intensity for heatmap (0.0-1.0)
        intensity = min(1.0, f_score / 100.0)
        
        # Extract error message for overlay
        error_msg = None
        for log in evidence['network_logs']:
            if log.get('status', 0) >= 400:
                error_msg = log.get('error', f"HTTP {log['status']} Error")
                break
        
        if not error_msg and evidence.get('console_logs'):
            # Get first error from console
            for log in evidence.get('console_logs', []):
                if 'error' in str(log).lower():
                    error_msg = str(log)[:80]  # Truncate long messages
                    break
        
        # Generate Assets using DYNAMIC Coordinates + Intensity
        generate_heatmap(
            evidence['screenshot_after_path'], 
            heatmap_path, 
            meta.get('touch_x', 0.5), 
            meta.get('touch_y', 0.5),
            intensity
        )
        generate_ghost_replay(
            evidence['screenshot_before_path'], 
            evidence['screenshot_after_path'], 
            gif_path,
            meta.get('touch_x', 0.5),
            meta.get('touch_y', 0.5),
            f_score=f_score,
            severity=severity_label,
            error_msg=error_msg,
            show_diff=True
        )
        
        return {
            "status": "FAILED", 
            "reason": "HIGH_FRICTION", 
            "details": f"F-Score {f_score:.1f} exceeds threshold.",
            "f_score": f_score,
            "calculated_severity": severity_label, # Pass this to AI
            "heatmap_path": heatmap_path,
            "gif_path": gif_path
        }

    # Always return f_score, even for SUCCESS (prevents defaulting to 100)
    return {"status": "SUCCESS", "reason": "Low Friction", "f_score": f_score}