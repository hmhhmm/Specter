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
try:
    from skimage.metrics import structural_similarity as ssim
except Exception:
    # Fallback approximate SSIM when scikit-image is not installed.
    def ssim(a, b, multichannel=True):
        try:
            if a is None or b is None:
                return 0.0
            # convert to grayscale
            if getattr(a, 'ndim', 0) == 3:
                a_gray = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY)
            else:
                a_gray = a
            if getattr(b, 'ndim', 0) == 3:
                b_gray = cv2.cvtColor(b, cv2.COLOR_BGR2GRAY)
            else:
                b_gray = b
            # simple normalized similarity based on MSE
            a_f = a_gray.astype('float32')
            b_f = b_gray.astype('float32')
            if a_f.shape != b_f.shape:
                return 0.0
            mse = np.mean((a_f - b_f) ** 2)
            if mse == 0:
                return 1.0
            max_val = 255.0
            sim = 1.0 - (mse / (max_val ** 2))
            return max(0.0, min(1.0, sim))
        except Exception:
            return 0.0
import os
import json
from datetime import datetime
from typing import Any, Dict, Optional, List

from backend.friction import FrictionMathematician
from backend.recorder import (
    GhostRecorder,
    generate_ghost_replay,
    add_diagnostic_overlay,
    add_click_indicator,
    create_difference_overlay,
)


# Instantiate core services
_FM = FrictionMathematician()
_RECORDER = GhostRecorder()

def record_frame(frame: np.ndarray) -> None:
    """Call from capture loop with OpenCV BGR frames to keep a rolling buffer."""
    try:
        _RECORDER.update(frame)
    except Exception:
        return


def extract_uncertainty_from_elements(
    interactive_elements: List[Dict[str, Any]],
    agent_decision: Dict[str, Any],
    screenshot_path: str,
    attention_map: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Extract uncertainty regions from Felicia's interactive element detection.
    
    Args:
        interactive_elements: List from DeepCrawler containing:
            [{'id': 1, 'type': 'button', 'text': 'Sign Up', 'bbox': [x, y, w, h], 'confidence': 0.95}, ...]
        agent_decision: Felicia's decision containing:
            {'action': 'click', 'target_id': 3, 'reasoning': '...', 'confidence': 0.8}
        screenshot_path: Path to screenshot for dimensions
    
    Returns:
        Uncertainty data with regions mapped from element bboxes
    """
    img = cv2.imread(screenshot_path)
    if img is None:
        return {'global_uncertainty': 0.5, 'regions': []}
    
    rows, cols, _ = img.shape
    uncertainty_regions = []
    
    # Calculate per-element uncertainty and global uncertainty
    per_element_uncs = []
    if interactive_elements:
        # Compute combined confidence using detector and optional VLM scores
        for e in interactive_elements:
            det_conf = float(e.get('confidence', 0.5))
            vlm_conf = e.get('vlm_confidence')
            if vlm_conf is not None:
                try:
                    vlm_conf = float(vlm_conf)
                except Exception:
                    vlm_conf = None

            combined_conf = det_conf if vlm_conf is None else (det_conf * 0.6 + vlm_conf * 0.4)
            per_element_uncs.append(1.0 - combined_conf)
        avg_confidence = 1.0 - (sum(per_element_uncs) / len(per_element_uncs))
        global_uncertainty = 1.0 - avg_confidence
    else:
        global_uncertainty = 0.8  # High uncertainty if no elements detected
    
    # Map each interactive element to an uncertainty region
    for element in interactive_elements:
        elem_id = element.get('id')
        elem_type = element.get('type', 'unknown')
        elem_text = element.get('text', '')
        bbox = element.get('bbox', [0, 0, 0, 0])  # [x, y, width, height]
        confidence = element.get('confidence', 0.5)
        
        # Calculate center point from bbox
        if len(bbox) == 4:
            x, y, w, h = bbox
            center_x = x + (w / 2)
            center_y = y + (h / 2)
            
            # Convert to ratio (0.0-1.0)
            x_ratio = center_x / cols
            y_ratio = center_y / rows
        else:
            x_ratio, y_ratio = 0.5, 0.5
        
        # Base uncertainty is inverse of combined confidence (detector + vlm)
        vlm_conf = element.get('vlm_confidence')
        try:
            vlm_conf = float(vlm_conf) if vlm_conf is not None else None
        except Exception:
            vlm_conf = None

        if vlm_conf is not None:
            combined_conf = (float(confidence) * 0.6) + (vlm_conf * 0.4)
        else:
            combined_conf = float(confidence)

        uncertainty = 1.0 - combined_conf
        
        # Check if this element was the agent's target
        is_target = False
        target_boost = 0.0
        if agent_decision and elem_id == agent_decision.get('target_id'):
            is_target = True
            # If agent had low confidence in decision, boost uncertainty
            decision_confidence = agent_decision.get('confidence', 0.5)
            target_boost = (1.0 - decision_confidence) * 0.3

        # If LLM reasoning mentions ambiguity for this element, boost uncertainty
        reasoning_text = ''
        if agent_decision:
            reasoning_text = agent_decision.get('reasoning_llm') or agent_decision.get('llm_reasoning', '')
        if reasoning_text and is_target:
            rt = reasoning_text.lower()
            if any(k in rt for k in ('uncertain', 'ambig', 'maybe', 'could be', 'not sure', 'confusing', 'alternat')):
                target_boost = min(1.0, target_boost + 0.25)

        # If attention_map provided, sample approximate attention at element center and adjust
        if attention_map is not None and len(bbox) == 4:
            try:
                # Ensure attention_map is a numpy array
                att = np.array(attention_map, dtype=float)
                # Resize to image dims if small
                att_h, att_w = att.shape[:2]
                cx = int(center_x)
                cy = int(center_y)
                if (att_w, att_h) != (cols, rows):
                    att_resized = cv2.resize(att, (cols, rows), interpolation=cv2.INTER_CUBIC)
                else:
                    att_resized = att
                att_val = float(att_resized[cy, cx]) if att_resized.max() > 0 else 0.0
                # Normalize if necessary
                if att_val > 1.5:  # likely 0-255
                    att_val = att_val / 255.0
                # Low attention -> increase uncertainty; high attention slightly decrease
                if att_val < 0.3:
                    target_boost = min(1.0, target_boost + 0.15)
                elif att_val > 0.7:
                    target_boost = max(0.0, target_boost - 0.07)
            except Exception:
                pass
        
        # Determine reason for uncertainty
        reasons = []
        if confidence < 0.6:
            reasons.append(f"Low detection confidence ({confidence:.1%})")
        if elem_type == 'unknown':
            reasons.append("Element type unclear")
        if not elem_text or elem_text.strip() == '':
            reasons.append("No text label")
        if bbox[2] < 10 or bbox[3] < 10:  # Very small element
            reasons.append("Very small click target")
        if is_target and decision_confidence < 0.7:
            reasons.append(f"Agent uncertain about action ({decision_confidence:.1%})")
        
        reason = "; ".join(reasons) if reasons else f"{elem_type}: {elem_text}"
        
        uncertainty_regions.append({
            'x': x_ratio,
            'y': y_ratio,
            'uncertainty': min(1.0, uncertainty + target_boost),
            'reason': reason,
            'element_id': elem_id,
            'element_type': elem_type,
            'is_target': is_target,
            'bbox': bbox  # Keep for drawing bounding boxes
        })
    
    # Sort by uncertainty (highest first)
    uncertainty_regions.sort(key=lambda r: r['uncertainty'], reverse=True)
    
    # Recompute global uncertainty as a combination of confusion, avg element uncertainty, and agent uncertainty
    try:
        avg_elem_unc = (sum(r['uncertainty'] for r in uncertainty_regions) / len(uncertainty_regions)) if uncertainty_regions else global_uncertainty
    except Exception:
        avg_elem_unc = global_uncertainty

    agent_conf = agent_decision.get('confidence', 0.5) if agent_decision else 0.5
    combined_global = min(1.0, (global_uncertainty + avg_elem_unc + (1.0 - agent_conf)) / 3.0)

    return {
        'global_uncertainty': combined_global,
        'regions': uncertainty_regions,
        'num_elements_detected': len(interactive_elements),
        'agent_confidence': agent_conf
    }
    


def generate_uncertainty_heatmap(
    img_path: str,
    output_path: str,
    uncertainty_data: Dict[str, Any],
    color_scheme: str = 'uncertainty',
    show_legend: bool = True,
    show_bboxes: bool = True,  # NEW: Draw element bounding boxes
    blur_strength: int = 15
) -> Optional[str]:
    """
    Generate heatmap based on AI uncertainty metrics from Felicia's element detection.
    
    Args:
        img_path: Input screenshot path
        output_path: Output heatmap path
        uncertainty_data: Dictionary from extract_uncertainty_from_elements()
        color_scheme: Visualization style
        show_legend: Add legend explaining colors
        show_bboxes: Draw bounding boxes around detected elements
        blur_strength: Gaussian blur for smooth gradients
    """
    img = cv2.imread(img_path)
    if img is None:
        return None
    
    rows, cols, _ = img.shape
    
    # Create empty heatmap overlay
    heatmap = np.zeros((rows, cols), dtype=np.float32)
    
    # Generate heatmap from detected element regions
    if 'regions' in uncertainty_data and uncertainty_data['regions']:
        for region in uncertainty_data['regions']:
            x_ratio = region.get('x', 0.5)
            y_ratio = region.get('y', 0.5)
            uncertainty = region.get('uncertainty', 0.5)
            bbox = region.get('bbox', None)
            
            # Convert to pixels
            center_x = int(cols * x_ratio)
            center_y = int(rows * y_ratio)
            
            # Use bbox size to determine radius if available
            if bbox and len(bbox) == 4:
                _, _, w, h = bbox
                radius = int(max(w, h) * 0.8)  # Slightly larger than element
            else:
                radius = int(50 + (uncertainty * 100))
            
            # Draw Gaussian-like blob
            Y, X = np.ogrid[:rows, :cols]
            dist_from_center = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
            
            # Gaussian falloff
            gaussian_mask = np.exp(-(dist_from_center**2) / (2 * (radius/2)**2))
            heatmap += gaussian_mask * uncertainty
    
    # Normalize heatmap to 0-1
    if heatmap.max() > 0:
        heatmap = heatmap / heatmap.max()
    
    # Apply Gaussian blur for smooth gradients - ensure kernel is odd and valid
    if blur_strength and isinstance(blur_strength, int) and blur_strength > 0:
        k = blur_strength
        if k % 2 == 0:
            k += 1
        # Clamp kernel to image size
        k = max(1, min(k, max(1, min(rows | cols, k))))
        try:
            heatmap = cv2.GaussianBlur(heatmap, (k, k), 0)
        except Exception:
            # Fallback: skip blur if OpenCV fails for some kernel sizes
            pass
    
    # Apply color scheme
    # Robust colormap selection: provide fallbacks for OpenCV variants
    color_schemes = {
        'uncertainty': getattr(cv2, 'COLORMAP_JET', 2),
        'confidence': getattr(cv2, 'COLORMAP_WINTER', getattr(cv2, 'COLORMAP_RAINBOW', 2)),
        'attention': getattr(cv2, 'COLORMAP_HOT', getattr(cv2, 'COLORMAP_JET', 2)),
        'fire': getattr(cv2, 'COLORMAP_INFERNO', getattr(cv2, 'COLORMAP_HOT', 2)),
        'viridis': getattr(cv2, 'COLORMAP_VIRIDIS', getattr(cv2, 'COLORMAP_JET', 2))
    }

    colormap = color_schemes.get(color_scheme, getattr(cv2, 'COLORMAP_JET', 2))
    
    # Convert to 0-255 and apply colormap
    heatmap_uint8 = (heatmap * 255).astype(np.uint8)
    heatmap_colored = cv2.applyColorMap(heatmap_uint8, colormap)
    
    # Blend with original image
    alpha = 0.5
    result = cv2.addWeighted(img, 1 - alpha, heatmap_colored, alpha, 0)
    
    # Draw bounding boxes around detected elements
    if show_bboxes and 'regions' in uncertainty_data:
        font = cv2.FONT_HERSHEY_SIMPLEX
        for region in uncertainty_data['regions']:
            bbox = region.get('bbox')
            if not bbox or len(bbox) != 4:
                continue
            
            x, y, w, h = bbox
            uncertainty = region.get('uncertainty', 0.5)
            is_target = region.get('is_target', False)
            elem_id = region.get('element_id', '?')
            
            # Color code: Green = target, Red = high uncertainty, Yellow = medium
            if is_target:
                box_color = (0, 255, 0)  # Green
                thickness = 3
            elif uncertainty > 0.7:
                box_color = (0, 0, 255)  # Red
                thickness = 2
            elif uncertainty > 0.4:
                box_color = (0, 165, 255)  # Orange
                thickness = 2
            else:
                box_color = (0, 255, 255)  # Yellow
                thickness = 1
            
            # Draw rectangle
            cv2.rectangle(result, (int(x), int(y)), (int(x + w), int(y + h)), 
                         box_color, thickness)
            
            # Draw element ID label
            label = f"#{elem_id}"
            if is_target:
                label += " ★"  # Star for target
            
            label_size = cv2.getTextSize(label, font, 0.4, 1)[0]
            cv2.rectangle(result, (int(x), int(y) - 18), 
                         (int(x) + label_size[0] + 4, int(y)), 
                         box_color, -1)
            cv2.putText(result, label, (int(x) + 2, int(y) - 5), 
                       font, 0.4, (255, 255, 255), 1)
            
            # Draw uncertainty percentage
            unc_label = f"{uncertainty*100:.0f}%"
            cv2.putText(result, unc_label, (int(x + w) - 35, int(y + h) + 15), 
                       font, 0.4, box_color, 1)
    
    # Add legend (robust to small images)
    if show_legend:
        legend_height = 80
        legend = np.zeros((legend_height, cols, 3), dtype=np.uint8)
        legend[:] = (20, 20, 20)

        # Positioning with clamping
        bar_x = int(max(10, cols * 0.12))
        bar_width = int(max(30, cols - bar_x - 150))
        bar_width = min(bar_width, max(10, cols - bar_x - 10))
        bar_height = max(8, int(legend_height * 0.25))
        bar_y = int((legend_height - bar_height) / 2)

        if bar_width > 1:
            for i in range(bar_width):
                val = int((i / max(1, (bar_width - 1))) * 255)
                try:
                    color = cv2.applyColorMap(np.array([[val]], dtype=np.uint8), colormap)[0, 0]
                    cv2.line(legend, (bar_x + i, bar_y), (bar_x + i, bar_y + bar_height), color.tolist(), 1)
                except Exception:
                    # Fallback: draw grayscale
                    gray = int(val)
                    cv2.line(legend, (bar_x + i, bar_y), (bar_x + i, bar_y + bar_height), (gray, gray, gray), 1)

        cv2.putText(legend, "Low Uncertainty", (max(0, bar_x - 110), bar_y + bar_height + 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        cv2.putText(legend, "High Uncertainty", (min(cols - 10, bar_x + bar_width + 10), bar_y + bar_height + 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        # Metrics
        num_elements = uncertainty_data.get('num_elements_detected', 0)
        agent_conf = uncertainty_data.get('agent_confidence', 0.0)
        entropy = uncertainty_data.get('entropy', 0.0)
        semantic = uncertainty_data.get('semantic_distance', 0.0)

        metrics_y = bar_y + bar_height + 25
        cv2.putText(legend, f"Elements: {num_elements}", (10, metrics_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 200, 200), 1)
        cv2.putText(legend, f"Agent Conf: {agent_conf:.1%}", (150, metrics_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 200, 200), 1)

        metrics_y += 16
        cv2.putText(legend, f"Entropy: {entropy:.2f}", (10, metrics_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 200, 200), 1)
        cv2.putText(legend, f"Semantic: {semantic:.2f}", (150, metrics_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 200, 200), 1)

        # Legend for bbox colors
        legend_x = max(10, cols - 220)
        cv2.rectangle(legend, (legend_x, 10), (legend_x + 12, 22), (0, 255, 0), -1)
        cv2.putText(legend, "= Target", (legend_x + 18, 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 200, 200), 1)

        cv2.rectangle(legend, (legend_x, 28), (legend_x + 12, 40), (0, 0, 255), -1)
        cv2.putText(legend, "= High Unc", (legend_x + 18, 38),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 200, 200), 1)

        result = np.vstack([result, legend])
    
    # Save output
    try:
        out_dir = os.path.dirname(output_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        cv2.imwrite(output_path, result)

        # Persist metadata JSON alongside the heatmap for downstream analysis
        try:
            meta_out = {
                'generated_at': datetime.utcnow().isoformat() + 'Z',
                'source_screenshot': img_path,
                'num_elements_detected': int(uncertainty_data.get('num_elements_detected', len(uncertainty_data.get('regions', [])))),
                'global_uncertainty': float(uncertainty_data.get('global_uncertainty', 0.0)),
                'entropy': float(uncertainty_data.get('entropy', 0.0)),
                'semantic_distance': float(uncertainty_data.get('semantic_distance', 0.0)),
                'confusion_score': float(uncertainty_data.get('confusion_score', 0.0)),
                'agent_decision': uncertainty_data.get('agent_decision') or uncertainty_data.get('agent', None),
            }

            regions = uncertainty_data.get('regions', []) or []
            # Build top-N uncertain elements list
            try:
                sorted_regions = sorted(regions, key=lambda r: float(r.get('uncertainty', 0.0)), reverse=True)
            except Exception:
                sorted_regions = regions

            top_n = []
            for r in sorted_regions[:10]:
                top_n.append({
                    'element_id': r.get('element_id') or r.get('id'),
                    'bbox': r.get('bbox'),
                    'uncertainty': float(r.get('uncertainty', 0.0)),
                    'reason': r.get('reason', None),
                    'vlm_confidence': r.get('vlm_confidence', None),
                    'llm_reasoning': r.get('llm_reasoning', None)
                })

            meta_out['top_uncertain_elements'] = top_n

            json_path = os.path.splitext(output_path)[0] + '.json'
            with open(json_path, 'w', encoding='utf-8') as jf:
                json.dump(meta_out, jf, indent=2)
        except Exception:
            # Non-fatal: metadata persistence should not block heatmap creation
            pass

        return output_path
    except Exception as e:
        print(f"Failed to save uncertainty heatmap: {e}")
        return None


def calculate_ui_uncertainty(ui_analysis: Dict[str, Any], expected_outcome: str) -> Dict[str, Any]:
    """
    Calculate AI uncertainty from UI analysis and expectations.
    
    Args:
        ui_analysis: Vision model's UI analysis containing:
            - issues: List of detected issues
            - elements: Detected UI elements
            - confusion_score: How confusing the UI is (0-10)
        expected_outcome: What the agent expected to happen
    
    Returns:
        Dictionary with uncertainty metrics:
            - global_uncertainty: Overall uncertainty (0.0-1.0)
            - regions: List of uncertain regions
            - entropy: Action entropy
            - semantic_distance: Expectation vs reality
    """
    uncertainty_regions = []

    # Priority 1: if explicit regions provided, use them (expected normalized 0..1)
    if 'regions' in ui_analysis and ui_analysis.get('regions'):
        for r in ui_analysis.get('regions'):
            try:
                x = float(r.get('x', 0.5))
                y = float(r.get('y', 0.5))
                unc = float(r.get('uncertainty', 0.6))
                reason = r.get('reason', '')
                uncertainty_regions.append({'x': x, 'y': y, 'uncertainty': unc, 'reason': reason})
            except Exception:
                continue
    else:
        # Priority 2: derive from elements with bounding boxes
        elements = ui_analysis.get('elements', [])
        viewport_w = ui_analysis.get('viewport_width', None)
        viewport_h = ui_analysis.get('viewport_height', None)
        for el in elements:
            bbox = el.get('bbox')
            if not bbox:
                continue
            # bbox may be relative (0..1) or absolute pixels
            bx = bbox.get('x')
            by = bbox.get('y')
            bw = bbox.get('width') or bbox.get('w')
            bh = bbox.get('height') or bbox.get('h')
            try:
                if viewport_w and viewport_h and bw and bh and bx is not None and by is not None:
                    # If bbox values look like pixels (large), normalize by viewport
                    cx = (float(bx) + float(bw) / 2.0) / float(viewport_w)
                    cy = (float(by) + float(bh) / 2.0) / float(viewport_h)
                else:
                    # Assume relative bbox values
                    cx = (float(bx) + float(bw) / 2.0) if (bx is not None and bw is not None) else None
                    cy = (float(by) + float(bh) / 2.0) if (by is not None and bh is not None) else None
                if cx is not None and cy is not None:
                    confidence = float(el.get('confidence', 0.6))
                    uncertainty_regions.append({'x': max(0.0, min(1.0, cx)), 'y': max(0.0, min(1.0, cy)), 'uncertainty': 1.0 - confidence, 'reason': 'element'})
            except Exception:
                continue

        # Priority 3: fallback to click coordinates if provided
        if not uncertainty_regions and ui_analysis.get('click_coords'):
            try:
                cc = ui_analysis.get('click_coords')
                # If click_coords are absolute pixels, normalize if viewport present
                if isinstance(cc, (list, tuple)) and len(cc) >= 2:
                    cx_px, cy_px = cc[0], cc[1]
                    vw = ui_analysis.get('viewport_width', None)
                    vh = ui_analysis.get('viewport_height', None)
                    if vw and vh:
                        cx = float(cx_px) / float(vw)
                        cy = float(cy_px) / float(vh)
                    else:
                        cx = float(cx_px)
                        cy = float(cy_px)
                    uncertainty_regions.append({'x': max(0.0, min(1.0, cx)), 'y': max(0.0, min(1.0, cy)), 'uncertainty': 0.6, 'reason': 'click'})
            except Exception:
                pass
    
    # Calculate global uncertainty from confusion score
    confusion = ui_analysis.get('confusion_score', 0) / 10.0  # Normalize to 0-1
    
    # Get semantic distance from FrictionMathematician
    ui_summary = ' '.join(ui_analysis.get('issues', []))
    semantic_dist = _FM.calculate_semantic_distance(expected_outcome, ui_summary)
    
    # Calculate entropy from action probabilities if available
    entropy = 0.0
    if 'action_probabilities' in ui_analysis:
        entropy = _FM.calculate_entropy(ui_analysis['action_probabilities'])
    
    # Global uncertainty combines confusion and semantic mismatch
    global_uncertainty = min(1.0, (confusion + semantic_dist) / 2.0)
    
    return {
        'global_uncertainty': global_uncertainty,
        'regions': uncertainty_regions,
        'entropy': entropy,
        'semantic_distance': semantic_dist,
        'confusion_score': confusion
    }


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
    if has_500_error or f_score > 85:
        return "P0 - Critical"
    
    # P1: HIGH FRICTION / DROP-OFF RISK
    if has_400_error and f_score > 60:
        return "P1 - Major"
    if f_score > 70 or confusion_score > 7:
        return "P1 - Major"
    if has_console_error and f_score > 55:
        return "P1 - Major"
    
    # P2: DEGRADED EXPERIENCE
    if f_score > 50 or confusion_score > 4:
        return "P2 - Minor"
    if (has_400_error or has_console_error) and f_score > 40:
        return "P2 - Minor"
    
    # P3: COSMETIC ISSUES
    return "P3 - Cosmetic"


def check_expectation(handoff):
    print(f"Checking Step {handoff['step_id']}...")
    
    evidence = handoff['evidence']
    meta = handoff.get('meta_data', {})
    
    # Extract Felicia's element detection data
    interactive_elements = evidence.get('interactive_elements', [])
    agent_decision = evidence.get('agent_decision', {})
    
    # Determine output paths. Prefer writing into the test report directory
    # (reports/test_.../). If the screenshot is missing or not inside a report,
    # fallback to backend/assets.
    screenshot_path = evidence['screenshot_after_path']

    def _find_report_dir(path: str) -> Optional[str]:
        try:
            if not path:
                return None
            abs_p = os.path.abspath(path)

            # If the file exists, try to find a parent 'screenshots' folder
            if os.path.exists(abs_p):
                parts = abs_p.replace('\\', '/').split('/')
                low_parts = [p.lower() for p in parts]
                if 'screenshots' in low_parts and 'reports' in low_parts:
                    # Find index of 'screenshots' and return its parent (the test dir)
                    idx = low_parts.index('screenshots')
                    if idx >= 1:
                        test_dir = '/'.join(parts[:idx])
                        return os.path.normpath(test_dir)

                # Walk upwards looking for a test_* ancestor
                cur = abs_p
                while True:
                    cur = os.path.dirname(cur)
                    if not cur or cur == os.path.dirname(cur):
                        break
                    if os.path.basename(cur).lower().startswith('test_'):
                        return cur

            # If the path does not exist yet, try locating by basename under reports/*/screenshots
            base = os.path.basename(path)
            reports_dir = os.path.join(os.getcwd(), 'reports')
            if os.path.exists(reports_dir):
                for root, dirs, files in os.walk(reports_dir):
                    if base in files and 'screenshots' in root.replace('\\', '/'):
                        # root is .../test_xxx/screenshots
                        return os.path.dirname(root)

            return None
        except Exception:
            return None

    report_dir = _find_report_dir(screenshot_path)
    if report_dir:
        heatmap_path = os.path.join(report_dir, "uncertainty_heatmap.png")
        gif_path = os.path.join(report_dir, "ghost_replay.gif")
    else:
        heatmap_path = os.path.join("backend", "assets", "uncertainty_heatmap.png")
        gif_path = os.path.join("backend", "assets", "ghost_replay.gif")

    # Helper: collect up to N screenshots from the same report (step 1..10)
    def _collect_report_screenshots(report_dir: Optional[str], max_steps: Optional[int] = None):
        out = []
        try:
            if not report_dir:
                return out
            screenshots_dir = os.path.join(report_dir, 'screenshots')
            if not os.path.exists(screenshots_dir):
                return out
            files = [f for f in os.listdir(screenshots_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            if not files:
                return out
            # Sort by modification time (oldest -> newest) to preserve chronological order
            files_with_mtime = []
            for f in files:
                p = os.path.join(screenshots_dir, f)
                try:
                    m = os.path.getmtime(p)
                except Exception:
                    m = 0
                files_with_mtime.append((f, m))
            files_with_mtime.sort(key=lambda x: x[1])
            sorted_files = [f for f, _ in files_with_mtime]
            if max_steps is None:
                selected = sorted_files
            else:
                selected = sorted_files[:max_steps]
            return [os.path.join(screenshots_dir, s) for s in selected]
        except Exception:
            return out

    # 1. Prepare data for FrictionMathematician
    ui_analysis = evidence.get('ui_analysis', {})
    console_logs = evidence.get('console_logs', [])
    network_logs = evidence['network_logs']
    
    ui_summary = ''
    if isinstance(ui_analysis, dict):
        issues = ui_analysis.get('issues', [])
        ui_summary = ' '.join(issues) if issues else ui_analysis.get('summary', '')

    # Extract entropy
    entropy_val = 0.0
    if isinstance(meta, dict) and meta.get('action_probabilities'):
        try:
            entropy_val = _FM.calculate_entropy(meta.get('action_probabilities'))
        except Exception:
            entropy_val = 0.0
    else:
        if console_logs:
            error_count = sum(1 for log in console_logs if 'error' in str(log).lower())
            warning_count = sum(1 for log in console_logs if 'warning' in str(log).lower())
            entropy_val = min(2.5, ((error_count * 10) + (warning_count * 2)) / 10.0)

    dwell_ms = meta.get('dwell_time_ms', 0) if isinstance(meta, dict) else 0
    
    semantic_dist = _FM.calculate_semantic_distance(
        handoff.get('agent_expectation', ''),
        ui_summary
    )

    # 2. CALCULATE F-SCORE
    try:
        f_score = _FM.compute_f_score(entropy_val, dwell_ms, semantic_dist)
    except Exception as e:
        print(f"      FrictionMathematician compute_f_score failed: {e}")
        f_score = 0

    # 3. Apply business rules
    has_500 = any(log.get('status', 0) >= 500 for log in network_logs)
    if has_500:
        f_score = min(100, int(f_score) + 15)

    has_errors = any(log.get('status', 0) >= 400 for log in network_logs)
    if console_logs and not has_errors:
        has_errors = any('error' in str(log).lower() for log in console_logs)
    if not has_errors and f_score > 35:
        f_score = 35.0

    print(f"      + F-Score: {f_score:.1f} (entropy={entropy_val:.2f}, semantic={semantic_dist:.2f}, dwell={dwell_ms}ms)")
    
    # 4. ASSIGN SEVERITY
    severity_label = determine_severity_rule(f_score, network_logs, console_logs, ui_analysis)

    # Force heatmap flag can be provided in meta_data or evidence for diagnostics
    force_heatmap = False
    try:
        force_heatmap = bool(meta.get('force_heatmap', False)) if isinstance(meta, dict) else False
    except Exception:
        force_heatmap = False
    try:
        if not force_heatmap:
            force_heatmap = bool(evidence.get('force_heatmap', False))
    except Exception:
        pass

    # Global override via env var: ALWAYS_GENERATE_HEATMAP (default '1' -> enabled)
    try:
        always_heatmap = os.getenv('ALWAYS_GENERATE_HEATMAP', '1').lower() in ('1', 'true', 'yes')
    except Exception:
        always_heatmap = True

    # 5. DECISION
    # Decide whether to generate diagnostics heatmap: on failure, when forced, or when global override enabled
    do_generate_heatmap = (f_score > 50) or force_heatmap or always_heatmap

    # If high friction, follow the failure flow
    if f_score > 50:
        print(f"   Final F-Score: {f_score:.1f}/100 ({severity_label})")

        # Extract uncertainty from Felicia's element detection
        uncertainty_data = extract_uncertainty_from_elements(
            interactive_elements,
            agent_decision,
            evidence['screenshot_after_path'],
            attention_map=evidence.get('attention_map')
        )
        uncertainty_data['entropy'] = entropy_val
        uncertainty_data['semantic_distance'] = semantic_dist

        error_msg = None
        for log in network_logs:
            if log.get('status', 0) >= 400:
                error_msg = log.get('error', f"HTTP {log['status']} Error")
                break

        if not error_msg and console_logs:
            for log in console_logs:
                if 'error' in str(log).lower():
                    error_msg = str(log)[:80]
                    break

        # Generate AI Uncertainty Heatmap with element bboxes
        try:
            generate_uncertainty_heatmap(
                evidence['screenshot_after_path'],
                heatmap_path,
                uncertainty_data,
                color_scheme='uncertainty',
                show_legend=True,
                show_bboxes=True  # Show Felicia's detected elements
            )
        except Exception as e:
            print(f"Warning: heatmap generation failed: {e}")

        # Generate ghost replay using up to 10 screenshots from the report
        try:
            seq = _collect_report_screenshots(report_dir)
            if seq and len(seq) >= 2:
                # Generate a heatmap for every screenshot in the sequence
                try:
                    for idx, sp in enumerate(seq):
                        try:
                            step_hm_path = os.path.join(report_dir, f"uncertainty_heatmap_step_{idx+1:02d}.png")
                            ud = extract_uncertainty_from_elements(
                                interactive_elements,
                                agent_decision,
                                sp,
                                attention_map=evidence.get('attention_map')
                            )
                            ud['entropy'] = entropy_val
                            ud['semantic_distance'] = semantic_dist
                            generate_uncertainty_heatmap(
                                sp,
                                step_hm_path,
                                ud,
                                color_scheme='uncertainty',
                                show_legend=True,
                                show_bboxes=True
                            )
                        except Exception:
                            # non-fatal per-step
                            pass
                except Exception:
                    pass
                try:
                    generate_ghost_replay(
                        img_sequence=seq,
                        output_path=gif_path,
                        click_x=meta.get('touch_x', 0.5),
                        click_y=meta.get('touch_y', 0.5),
                        f_score=f_score,
                        severity=severity_label,
                        error_msg=error_msg,
                        show_diff=True,
                    )
                except Exception:
                    pass
            else:
                try:
                            # fallback to two-image mode if seq not available
                            generate_ghost_replay(
                                evidence['screenshot_before_path'],
                                evidence['screenshot_after_path'],
                                gif_path,
                                meta.get('touch_x', 0.5),
                                meta.get('touch_y', 0.5),
                                f_score=f_score,
                                severity=severity_label,
                                error_msg=error_msg,
                                show_diff=True,
                            )
                except Exception:
                    pass
        except Exception as e:
            print(f"Warning: ghost replay generation failed: {e}")

        try:
            saved = _RECORDER.save_doom_scroll(os.path.join(os.path.dirname(gif_path), "ghost_replay_buffer.gif"))
            if saved:
                gif_path = saved
        except Exception:
            pass

        return {
            "status": "FAILED",
            "reason": "HIGH_FRICTION",
            "details": f"F-Score {f_score:.1f} exceeds threshold.",
            "f_score": f_score,
            "calculated_severity": severity_label,
            "heatmap_path": heatmap_path,
            "gif_path": gif_path,
            "uncertainty_metrics": uncertainty_data
        }

    # If not failing but generation requested (force or global), create diagnostics
    if do_generate_heatmap and f_score <= 50:
        print(f"   Generating diagnostics (F-Score {f_score:.1f}) because heatmap generation is enabled")
        uncertainty_data = extract_uncertainty_from_elements(
            interactive_elements,
            agent_decision,
            evidence['screenshot_after_path'],
            attention_map=evidence.get('attention_map')
        )
        uncertainty_data['entropy'] = entropy_val
        uncertainty_data['semantic_distance'] = semantic_dist

        try:
            generate_uncertainty_heatmap(
                evidence['screenshot_after_path'],
                heatmap_path,
                uncertainty_data,
                color_scheme='uncertainty',
                show_legend=True,
                show_bboxes=True
            )
        except Exception as e:
            print(f"Warning: heatmap generation failed: {e}")

        try:
            seq = _collect_report_screenshots(report_dir)
            if seq and len(seq) >= 2:
                # Generate per-step heatmaps first
                try:
                    for idx, sp in enumerate(seq):
                        try:
                            step_hm_path = os.path.join(report_dir, f"uncertainty_heatmap_step_{idx+1:02d}.png")
                            ud = extract_uncertainty_from_elements(
                                interactive_elements,
                                agent_decision,
                                sp,
                                attention_map=evidence.get('attention_map')
                            )
                            ud['entropy'] = entropy_val
                            ud['semantic_distance'] = semantic_dist
                            generate_uncertainty_heatmap(
                                sp,
                                step_hm_path,
                                ud,
                                color_scheme='uncertainty',
                                show_legend=True,
                                show_bboxes=True
                            )
                        except Exception:
                            pass
                except Exception:
                    pass

                try:
                    generate_ghost_replay(
                        img_sequence=seq,
                        output_path=gif_path,
                        click_x=meta.get('touch_x', 0.5),
                        click_y=meta.get('touch_y', 0.5),
                        f_score=f_score,
                        severity=severity_label,
                        error_msg=None,
                        show_diff=True,
                    )
                except Exception:
                    pass
            else:
                try:
                    generate_ghost_replay(
                        evidence['screenshot_before_path'],
                        evidence['screenshot_after_path'],
                        gif_path,
                        meta.get('touch_x', 0.5),
                        meta.get('touch_y', 0.5),
                        f_score=f_score,
                        severity=severity_label,
                        error_msg=None,
                        show_diff=True,
                    )
                except Exception:
                    pass
        except Exception as e:
            print(f"Warning: ghost replay generation failed: {e}")

        return {
            "status": "SUCCESS",
            "reason": "Heatmap Generated",
            "f_score": f_score,
            "heatmap_path": heatmap_path,
            "gif_path": gif_path,
            "uncertainty_metrics": uncertainty_data
        }

    return {"status": "SUCCESS", "reason": "Low Friction", "f_score": f_score}