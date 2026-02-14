"""
Specter Expectation Engine - COMPLETE FIXED VERSION
F-Score Calculation & Severity Classification with OCR and Heatmap Fixes

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

FIXES IN THIS VERSION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. OCR confidence properly extracted from multiple field names
2. Heatmap uses maximum instead of sum to prevent oversaturation
3. Region deduplication to reduce noise
4. Improved visual fallback detector with strict filtering
5. Adaptive alpha blending for cleaner visualization
6. All core functions integrated: record_frame, calculate_ui_uncertainty, 
   determine_severity_rule, check_expectation
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
import logging
logger = logging.getLogger(__name__)

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
    """
    Call from capture loop with OpenCV BGR frames to keep a rolling buffer.
    This is critical for generating ghost replay animations.
    """
    try:
        _RECORDER.update(frame)
    except Exception as e:
        logger.debug(f"Frame recording failed: {e}")
        return


def _visual_detect_elements_from_image(img_path: str, max_elements: int = 50):
    """
    FIXED: Improved fallback visual detector with better filtering.
    
    Returns a list of element dicts matching the format expected by
    `extract_uncertainty_from_elements` when the DOM-based detector fails.
    
    Improvements:
    - Stricter size filtering (elements must be 3%+ of width, 2%+ of height)
    - Aspect ratio filtering (reject very thin elements >15:1)
    - Better confidence scoring based on element size
    - Larger morphological kernel for better grouping
    """
    out = []
    try:
        img = cv2.imread(img_path)
        if img is None:
            return out
        
        rows, cols = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Better edge detection parameters
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 30, 100)  # Lower thresholds for better detection
        
        # Larger morphological kernel for better grouping
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Sort by area (largest first)
        contours = sorted(contours, key=lambda c: cv2.contourArea(c), reverse=True)
        
        total_area = float(rows * cols)
        cid = 0
        
        for c in contours[:max_elements]:
            x, y, w, h = cv2.boundingRect(c)
            
            # Stricter size filtering
            min_w = max(30, int(cols * 0.03))  # At least 3% of width
            min_h = max(20, int(rows * 0.02))  # At least 2% of height
            max_w = int(cols * 0.9)  # Not more than 90% of width
            max_h = int(rows * 0.9)
            
            if w < min_w or h < min_h or w > max_w or h > max_h:
                continue
            
            # Filter very thin elements (likely borders)
            aspect_ratio = max(w, h) / max(min(w, h), 1)
            if aspect_ratio > 15:  # Too thin
                continue
            
            area = float(w * h)
            area_ratio = area / total_area
            
            # Confidence based on area (reasonable sizes get higher confidence)
            if 0.01 < area_ratio < 0.3:  # 1-30% of screen
                conf = 0.7
            elif 0.001 < area_ratio <= 0.01:  # 0.1-1% of screen
                conf = 0.5
            else:
                conf = 0.3
            
            elem_type = 'button' if (w > h and 1.5 < (w / max(1, h)) < 5) else 'unknown'
            
            out.append({
                'id': f'v{cid}',
                'type': elem_type,
                'text': '',
                'bbox': [int(x), int(y), int(w), int(h)],
                'confidence': conf,
                'ocr_confidence': 0.0  # Visual detector doesn't have OCR
            })
            cid += 1
        
        logger.debug(f"Visual detector found {len(out)} valid elements from {len(contours)} contours")
        
    except Exception as e:
        logger.error(f"Visual detection failed: {e}")
        return []
    
    return out


def extract_uncertainty_from_elements(
    interactive_elements: List[Dict[str, Any]],
    agent_decision: Dict[str, Any],
    screenshot_path: str,
    attention_map: Optional[Any] = None
) -> Dict[str, Any]:
    """
    FIXED: Extract uncertainty regions from Felicia's interactive element detection.
    
    Key Improvements:
    1. OCR confidence properly extracted from multiple possible field names
    2. Better confidence combination logic
    3. Improved handling of missing values
    
    Args:
        interactive_elements: List from DeepCrawler containing:
            [{'id': 1, 'type': 'button', 'text': 'Sign Up', 'bbox': [x, y, w, h], 
              'confidence': 0.95, 'ocr_confidence': 0.87}, ...]
        agent_decision: Felicia's decision containing:
            {'action': 'click', 'target_id': 3, 'reasoning': '...', 'confidence': 0.8}
        screenshot_path: Path to screenshot for dimensions
        attention_map: Optional attention heatmap
    
    Returns:
        Uncertainty data with regions mapped from element bboxes
    """
    img = cv2.imread(screenshot_path)
    if img is None:
        logger.warning(f"Failed to load screenshot: {screenshot_path}")
        return {'global_uncertainty': 0.5, 'regions': []}
    
    rows, cols, _ = img.shape
    uncertainty_regions = []
    
    # Calculate per-element uncertainty
    per_element_uncs = []
    
    if not interactive_elements:
        logger.debug("No interactive elements provided - attempting visual fallback on %s", screenshot_path)
        try:
            visual_elems = _visual_detect_elements_from_image(screenshot_path)
            if visual_elems:
                logger.debug("Visual fallback produced %d elements, using them.", len(visual_elems))
                interactive_elements = visual_elems
            else:
                logger.debug("Visual fallback produced no elements; using global fallback uncertainty.")
                global_uncertainty = 0.8
                return {
                    'global_uncertainty': global_uncertainty,
                    'regions': [{
                        'x': 0.5, 'y': 0.5,
                        'uncertainty': global_uncertainty,
                        'reason': 'No elements detected',
                        'element_id': None,
                        'element_type': 'fallback',
                        'is_target': False,
                        'bbox': [int(cols*0.4), int(rows*0.4), int(cols*0.2), int(rows*0.2)]
                    }],
                    'num_elements_detected': 0,
                    'agent_confidence': agent_decision.get('confidence', 0.5) if agent_decision else 0.5
                }
        except Exception as e:
            logger.exception("Visual fallback failed")
            global_uncertainty = 0.8
            return {
                'global_uncertainty': global_uncertainty,
                'regions': [{
                    'x': 0.5, 'y': 0.5,
                    'uncertainty': global_uncertainty,
                    'reason': 'Detection failed',
                    'element_id': None,
                    'element_type': 'fallback',
                    'is_target': False,
                    'bbox': [int(cols*0.4), int(rows*0.4), int(cols*0.2), int(rows*0.2)]
                }],
                'num_elements_detected': 0,
                'agent_confidence': agent_decision.get('confidence', 0.5) if agent_decision else 0.5
            }
    
    # Map each interactive element to an uncertainty region
    for element in interactive_elements:
        elem_id = element.get('id')
        elem_type = element.get('type', 'unknown')
        elem_text = element.get('text', '')
        bbox = element.get('bbox', [0, 0, 0, 0])  # [x, y, width, height]
        is_interactive = element.get('isInteractive', False)
        
        # FILTER: Skip non-interactive text elements (headings, paragraphs, labels)
        # Only show uncertainty for truly interactive elements (buttons, inputs, links)
        non_interactive_types = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'label', 'div']
        if elem_type in non_interactive_types and not is_interactive:
            # If it's just static text (not clickable), skip it
            if elem_text and len(elem_text) > 0:
                logger.debug(f"Skipping non-interactive text element: {elem_type} with text '{elem_text[:30]}'")
                continue
        
        # FIX 1: Extract OCR confidence from multiple possible field names
        ocr_conf = 0.0
        for key in ['ocr_confidence', 'text_confidence', 'ocr_score', 'text_score']:
            if key in element:
                try:
                    ocr_conf = float(element[key])
                    if ocr_conf > 0:
                        logger.debug(f"Element {elem_id}: Found OCR confidence={ocr_conf:.3f} from field '{key}'")
                        break
                except (ValueError, TypeError):
                    continue
        
        # Detector confidence
        det_conf = float(element.get('confidence', 0.5))
        
        # VLM confidence (optional)
        vlm_conf = element.get('vlm_confidence')
        if vlm_conf is not None:
            try:
                vlm_conf = float(vlm_conf)
            except (ValueError, TypeError):
                vlm_conf = None
        
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
        
        # FIX 2: Improved confidence combination
        # Start with detector confidence
        combined_conf = det_conf
        
        # Add VLM confidence if available
        if vlm_conf is not None:
            combined_conf = (det_conf * 0.6) + (vlm_conf * 0.4)
        
        # FIX 3: OCR confidence as strong positive signal
        if ocr_conf >= 0.50:
            # High OCR confidence means text is clearly readable
            # Boost by up to 0.35 based on OCR score
            ocr_boost = min(0.35, ocr_conf * 0.40)
            combined_conf = min(0.99, combined_conf + ocr_boost)
            logger.debug(f"Element {elem_id}: OCR boost={ocr_boost:.3f}, combined_conf={combined_conf:.3f}")
        elif elem_text and isinstance(elem_text, str) and len(elem_text.strip()) > 0:
            # Has text but low/no OCR score - small boost
            combined_conf = min(0.95, combined_conf + 0.08)
        
        # Area-based trust: very large elements (e.g., prominent headings/logos)
        # are less likely to be false positives — give a small additional boost
        if len(bbox) == 4:
            _, _, bw, bh = bbox
            area = float(max(1, bw * bh))
            area_ratio = area / float(max(1, rows * cols))
            
            # Large elements (>5% of screen) get modest boost
            if area_ratio > 0.05:
                area_boost = min(0.12, area_ratio * 1.2)
                combined_conf = min(0.99, combined_conf + area_boost)
        
        # Base uncertainty from combined confidence
        uncertainty = 1.0 - combined_conf
        per_element_uncs.append(uncertainty)
        
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
            except Exception as e:
                logger.debug(f"Attention map processing failed: {e}")
        
        # Determine reason for uncertainty
        reasons = []
        if combined_conf < 0.6:
            reasons.append(f"Low confidence ({combined_conf:.1%})")
        if ocr_conf > 0 and ocr_conf < 0.5:
            reasons.append(f"Low OCR ({ocr_conf:.1%})")
        if elem_type == 'unknown':
            reasons.append("Unknown type")
        if not elem_text or elem_text.strip() == '':
            reasons.append("No text")
        if bbox[2] < 10 or bbox[3] < 10:  # Very small element
            reasons.append("Very small")
        if is_target and decision_confidence < 0.7:
            reasons.append(f"Agent uncertain")
        
        reason = "; ".join(reasons) if reasons else f"{elem_type}: {elem_text}"
        
        uncertainty_regions.append({
            'x': x_ratio,
            'y': y_ratio,
            'uncertainty': min(1.0, uncertainty + target_boost),
            'reason': reason,
            'element_id': elem_id,
            'element_type': elem_type,
            'is_target': is_target,
            'bbox': bbox,
            'ocr_confidence': ocr_conf,  # Store for debugging
            'combined_confidence': combined_conf
        })
    
    # Sort by uncertainty (highest first)
    uncertainty_regions.sort(key=lambda r: r['uncertainty'], reverse=True)
    
    # FIX 4: Better global uncertainty calculation
    # Weight by top uncertain elements more heavily
    if per_element_uncs:
        avg_elem_unc = sum(per_element_uncs) / len(per_element_uncs)
        # Weight by top 3 most uncertain elements
        top_3_unc = sum(sorted(per_element_uncs, reverse=True)[:3]) / min(3, len(per_element_uncs))
        global_uncertainty = (avg_elem_unc * 0.5) + (top_3_unc * 0.5)
    else:
        global_uncertainty = 0.8
    
    agent_conf = agent_decision.get('confidence', 0.5) if agent_decision else 0.5
    # Combine global uncertainty with agent confidence
    combined_global = min(1.0, (global_uncertainty + (1.0 - agent_conf)) / 2.0)
    
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
    show_bboxes: bool = True,
    blur_strength: int = 41,  # Increased from 21 for smoother, more spread-out gradients
    debug: bool = False
) -> Optional[str]:
    """
    FIXED: Generate heatmap based on AI uncertainty metrics with cleaner visualization.
    
    Key Improvements:
    1. Uses maximum instead of sum to prevent oversaturation
    2. Deduplicates overlapping regions
    3. Adaptive alpha blending
    4. Better gaussian blob sizing
    
    Args:
        img_path: Input screenshot path
        output_path: Output heatmap path
        uncertainty_data: Dictionary from extract_uncertainty_from_elements()
        color_scheme: Visualization style
        show_legend: Add legend explaining colors
        show_bboxes: Draw bounding boxes around detected elements
        blur_strength: Gaussian blur for smooth gradients
        debug: Enable debug output
    """
    img = cv2.imread(img_path)
    if img is None:
        logger.error(f"Failed to load image: {img_path}")
        return None
    
    rows, cols, _ = img.shape
    
    # Create empty heatmap overlay
    heatmap = np.zeros((rows, cols), dtype=np.float32)
    
    # Normalize global uncertainty (0..1)
    global_unc = float(uncertainty_data.get('global_uncertainty', 0.0))
    global_unc = max(0.0, min(1.0, global_unc))
    
    regions = uncertainty_data.get('regions', []) or []
    
    # Ensure at least one region so heatmap is not uniformly empty
    if not regions:
        touch_x = uncertainty_data.get('touch_x') or uncertainty_data.get('meta', {}).get('touch_x') or (uncertainty_data.get('agent_decision') or {}).get('touch_x')
        touch_y = uncertainty_data.get('touch_y') or uncertainty_data.get('meta', {}).get('touch_y') or (uncertainty_data.get('agent_decision') or {}).get('touch_y')
        try:
            tx = float(touch_x) if touch_x is not None else 0.5
            ty = float(touch_y) if touch_y is not None else 0.5
        except Exception:
            tx, ty = 0.5, 0.5
        regions = [{
            'x': max(0.0, min(1.0, tx)),
            'y': max(0.0, min(1.0, ty)),
            'uncertainty': global_unc,
            'reason': 'fallback_confusion',
            'bbox': [int(cols*0.4), int(rows*0.4), int(cols*0.2), int(rows*0.2)]
        }]
    
    agent_conf = float(uncertainty_data.get('agent_confidence', 0.5))
    
    # FIX 5: Deduplicate overlapping regions to reduce noise
    deduped_regions = []
    for region in regions:
        # Check if this region overlaps significantly with existing ones
        overlaps = False
        rx, ry = region.get('x', 0.5), region.get('y', 0.5)
        
        for existing in deduped_regions:
            ex, ey = existing.get('x', 0.5), existing.get('y', 0.5)
            dist = np.sqrt((rx - ex)**2 + (ry - ey)**2)
            
            # If within 5% of screen, consider overlap
            if dist < 0.05:
                # Keep the more uncertain one
                if region.get('uncertainty', 0) > existing.get('uncertainty', 0):
                    deduped_regions.remove(existing)
                    deduped_regions.append(region)
                overlaps = True
                break
        
        if not overlaps:
            deduped_regions.append(region)
    
    logger.debug(f"Deduplication: {len(regions)} -> {len(deduped_regions)} regions")
    regions = deduped_regions
    
    # FIX 6: Improved gaussian blob generation with maximum instead of sum
    for region in regions:
        x_ratio = float(region.get('x', 0.5))
        y_ratio = float(region.get('y', 0.5))
        elem_unc = float(region.get('uncertainty', global_unc))
        bbox = region.get('bbox')
        
        # Combine global and element uncertainties and agent confidence
        combined_unc = (0.5 * global_unc) + (0.4 * elem_unc) + (0.1 * (1.0 - agent_conf))
        combined_unc = max(0.0, min(1.0, combined_unc))
        
        # Convert to pixels
        center_x = int(cols * x_ratio)
        center_y = int(rows * y_ratio)
        
        # Use bbox size to determine spread if available
        if bbox and len(bbox) == 4:
            try:
                bx, by, bw, bh = bbox
                # Create rectangular gaussian that covers the entire bbox with good spread
                Y, X = np.ogrid[:rows, :cols]
                
                # Calculate distance in X and Y separately for elliptical gaussian
                # Use larger sigma for more spread (was /2.5, now /1.5 for wider coverage)
                sigma_x = max(bw / 1.5, 30.0)  # Wider spread to cover bbox
                sigma_y = max(bh / 1.5, 30.0)  # Taller spread to cover bbox
                
                # Use bbox center for gaussian origin
                bbox_center_x = int(bx + bw / 2)
                bbox_center_y = int(by + bh / 2)
                
                # Elliptical gaussian - spreads according to bbox dimensions
                gaussian_mask = np.exp(
                    -((X - bbox_center_x)**2 / (2 * sigma_x**2) + 
                      (Y - bbox_center_y)**2 / (2 * sigma_y**2))
                )
            except Exception as e:
                logger.debug(f"Failed to create bbox-based gaussian: {e}")
                # Fallback to circular gaussian
                Y, X = np.ogrid[:rows, :cols]
                dist_from_center = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
                sigma = 60.0  # Larger fallback
                gaussian_mask = np.exp(-(dist_from_center**2) / (2 * sigma**2))
        else:
            # No bbox - use circular gaussian centered on region point
            radius_default = int(60 + (combined_unc * 100))  # Larger base radius
            Y, X = np.ogrid[:rows, :cols]
            dist_from_center = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
            sigma = max(radius_default / 2.5, 30.0)  # Wider spread
            gaussian_mask = np.exp(-(dist_from_center**2) / (2 * sigma**2))
        
        # FIX: Use maximum instead of addition to prevent oversaturation
        contribution = gaussian_mask * combined_unc * 0.7  # Scale down contribution
        heatmap = np.maximum(heatmap, contribution)  # Take max, not sum
    
    # Apply Gaussian blur for smooth gradients
    if blur_strength and isinstance(blur_strength, int) and blur_strength > 0:
        k = blur_strength
        if k % 2 == 0:
            k += 1
        k = max(3, min(k, 51))
        try:
            heatmap = cv2.GaussianBlur(heatmap, (k, k), 0)
        except Exception as e:
            logger.warning(f"Blur failed: {e}")
    
    # FIX 9 (revised v2): Aggressive boost for visibility
    # The goal: make low uncertainty VISIBLE while keeping HIGH uncertainty RED
    # Strategy: Boost low values to use more of the colormap (blue-green range)
    # while preserving the relative differences
    heatmap_max = heatmap.max()
    heatmap_min = heatmap.min()
    
    if debug:
        print(f"[debug] Before boost: min={heatmap_min:.6f}, max={heatmap_max:.6f}")
    
    if heatmap_max < 0.15:  # All values are very low (<15%)
        # Boost to use 30-60% of colormap (green-yellow range)
        # Map [0, 0.15] -> [0, 0.6] for visibility
        heatmap = np.clip(heatmap / 0.15 * 0.6, 0.0, 0.6)
        if debug:
            print(f"[debug] Applied strong boost: new max={heatmap.max():.6f}")
    elif heatmap_max < 0.3:  # All values are low-medium (<30%)
        # Boost to use 40-70% of colormap (yellow-orange range)
        # Map [0, 0.3] -> [0, 0.7]
        heatmap = np.clip(heatmap / 0.3 * 0.7, 0.0, 0.7)
        if debug:
            print(f"[debug] Applied medium boost: new max={heatmap.max():.6f}")
    else:
        # Values are already in good range, just clip to [0, 1]
        heatmap = np.clip(heatmap, 0.0, 1.0)
        if debug:
            print(f"[debug] No boost needed: max={heatmap.max():.6f}")

    
    # Apply color scheme
    color_schemes = {
        'uncertainty': cv2.COLORMAP_JET,
        'confidence': cv2.COLORMAP_WINTER,
        'attention': cv2.COLORMAP_HOT,
        'fire': getattr(cv2, 'COLORMAP_INFERNO', cv2.COLORMAP_HOT),
        'viridis': getattr(cv2, 'COLORMAP_VIRIDIS', cv2.COLORMAP_JET)
    }
    
    colormap = color_schemes.get(color_scheme, cv2.COLORMAP_JET)
    
    # Convert to 0-255 and apply colormap
    heatmap_uint8 = np.clip((heatmap * 255.0), 0, 255).astype(np.uint8)
    
    if debug:
        try:
            print(f"[debug] regions={len(regions)}, global_unc={global_unc:.3f}, agent_conf={agent_conf:.3f}")
            print(f"[debug] heatmap min/max: {heatmap.min():.6f}/{heatmap.max():.6f}")
            print(f"[debug] heatmap_uint8 min/max: {heatmap_uint8.min()}/{heatmap_uint8.max()}")
        except Exception:
            pass
    
    heatmap_colored = cv2.applyColorMap(heatmap_uint8, colormap)
    
    # FIX 8 & 10: Balance visibility with text readability
    # Use moderate alpha that scales with uncertainty
    # For low uncertainty (0-30%): 20-35% opacity (visible but subtle)
    # For high uncertainty (30-100%): 35-60% opacity (clearly visible)
    alpha_map = np.where(
        heatmap < 0.3,
        0.20 + (heatmap * 0.5),   # Low uncertainty: 20-35% opacity
        0.35 + (heatmap * 0.35)   # High uncertainty: 35-70% opacity
    )
    alpha_map = np.stack([alpha_map] * 3, axis=2)  # Make 3-channel
    
    result = (img * (1 - alpha_map) + heatmap_colored * alpha_map).astype(np.uint8)
    
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
            ocr_conf = region.get('ocr_confidence', 0.0)
            
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
            
            # Draw element ID label with OCR confidence
            label = f"#{elem_id}"
            if is_target:
                label += " ★"  # Star for target
            if ocr_conf > 0:
                label += f" OCR:{ocr_conf:.0%}"
            
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
    
    # Add legend
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
        confusion = uncertainty_data.get('confusion_score', 0.0)
        
        metrics_y = bar_y + bar_height + 25
        cv2.putText(legend, f"Elements: {num_elements}", (10, metrics_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 200, 200), 1)
        cv2.putText(legend, f"Agent Conf: {agent_conf:.1%}", (150, metrics_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 200, 200), 1)
        
        metrics_y += 16
        cv2.putText(legend, f"Confusion: {confusion:.2f}", (10, metrics_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 200, 200), 1)
        cv2.putText(legend, f"Entropy: {entropy:.2f}", (150, metrics_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 200, 200), 1)
        
        metrics_y += 16
        cv2.putText(legend, f"Semantic: {semantic:.2f}", (10, metrics_y),
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
                'agent_confidence': float(uncertainty_data.get('agent_confidence', 0.5)),  # Added for legend display
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
                    'ocr_confidence': r.get('ocr_confidence', None),
                    'combined_confidence': r.get('combined_confidence', None),
                    'llm_reasoning': r.get('llm_reasoning', None)
                })
            
            meta_out['top_uncertain_elements'] = top_n
            
            json_path = os.path.splitext(output_path)[0] + '.json'
            with open(json_path, 'w', encoding='utf-8') as jf:
                json.dump(meta_out, jf, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save metadata JSON: {e}")
        
        logger.info(f"Heatmap saved to: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Failed to save uncertainty heatmap: {e}")
        return None


def calculate_ui_uncertainty(ui_analysis: Dict[str, Any], expected_outcome: str) -> Dict[str, Any]:
    """
    Calculate AI uncertainty from UI analysis and expectations.
    This is a legacy function that creates uncertainty data when element detection isn't available.
    
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
    Enhanced P0-P3 Severity Rules - CRITICAL for proper triage
    
    P0: Signup blocked (complete blocker - user cannot proceed)
    P1: High friction, drop-off risk (serious usability issues)
    P2: Degraded experience (moderate issues, workarounds exist)
    P3: Cosmetic issues (minor UI problems, low impact)
    
    Args:
        f_score: Friction score (0-100)
        network_logs: List of network request logs
        console_logs: List of console logs (errors, warnings)
        ui_analysis: UI analysis dict with confusion_score
    
    Returns:
        str: Severity label (e.g., "P0 - Critical")
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
    """
    MAIN ENTRY POINT - Check expectations and generate diagnostics.
    
    This is the core function that orchestrates:
    1. F-Score calculation
    2. Severity determination
    3. Heatmap generation (on failure OR when enabled)
    4. Ghost replay generation
    
    Args:
        handoff: Dictionary containing:
            - step_id: Step identifier
            - evidence: Screenshots, network logs, console logs, UI analysis
            - meta_data: Touch coordinates, dwell time, action probabilities
            - agent_expectation: What the agent expected to happen
    
    Returns:
        Dictionary with status, f_score, severity, and diagnostic paths
    """
    print(f"Checking Step {handoff['step_id']}...")
    
    evidence = handoff['evidence']
    meta = handoff.get('meta_data', {})
    
    # Extract Felicia's element detection data
    interactive_elements = evidence.get('interactive_elements', [])
    agent_decision = evidence.get('agent_decision', {})
    
    # Determine output paths. Prefer writing into the test report directory
    screenshot_path = evidence['screenshot_after_path']
    
    def _find_report_dir(path: str) -> Optional[str]:
        """Find the report directory for this test run."""
        try:
            if not path:
                return None
            abs_p = os.path.abspath(path)
            
            if os.path.exists(abs_p):
                parts = abs_p.replace('\\', '/').split('/')
                low_parts = [p.lower() for p in parts]
                if 'screenshots' in low_parts and 'reports' in low_parts:
                    idx = low_parts.index('screenshots')
                    if idx >= 1:
                        test_dir = '/'.join(parts[:idx])
                        return os.path.normpath(test_dir)
                
                cur = abs_p
                while True:
                    cur = os.path.dirname(cur)
                    if not cur or cur == os.path.dirname(cur):
                        break
                    if os.path.basename(cur).lower().startswith('test_'):
                        return cur
            
            base = os.path.basename(path)
            reports_dir = os.path.join(os.getcwd(), 'reports')
            if os.path.exists(reports_dir):
                for root, dirs, files in os.walk(reports_dir):
                    if base in files and 'screenshots' in root.replace('\\', '/'):
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
    
    def _collect_report_screenshots(report_dir: Optional[str], max_steps: Optional[int] = None):
        """Collect up to N screenshots from the same report."""
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
        # Fallback: estimate entropy from available signals
        if console_logs:
            error_count = sum(1 for log in console_logs if 'error' in str(log).lower())
            warning_count = sum(1 for log in console_logs if 'warning' in str(log).lower())
            entropy_val = min(2.5, ((error_count * 10) + (warning_count * 2)) / 10.0)
        
        # Additional entropy estimate from uncertainty signals
        if entropy_val == 0.0 and ui_analysis:
            confusion = ui_analysis.get('confusion_score', 0)
            # High confusion or dwell time suggests higher entropy (uncertainty in action selection)
            if confusion > 0 or dwell_ms > 3000:
                # Scale confusion (0-10) to entropy (0-2.5 bits)
                confusion_entropy = min(2.5, confusion / 4.0)
                # Scale dwell time to entropy: 3s+ suggests hesitation
                dwell_entropy = min(1.5, max(0, (dwell_ms - 3000) / 4000.0))
                entropy_val = min(2.5, confusion_entropy + dwell_entropy)
    
    dwell_ms = meta.get('dwell_time_ms', 0) if isinstance(meta, dict) else 0
    
    semantic_dist = _FM.calculate_semantic_distance(
        handoff.get('agent_expectation', ''),
        ui_summary
    )
    
    # 2. CALCULATE F-SCORE
    try:
        f_score = _FM.compute_f_score(entropy_val, dwell_ms, semantic_dist)
    except Exception as e:
        logger.error(f"FrictionMathematician compute_f_score failed: {e}")
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
    
    # Force heatmap flag
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
    
    # Global override via env var
    try:
        always_heatmap = os.getenv('ALWAYS_GENERATE_HEATMAP', '1').lower() in ('1', 'true', 'yes')
    except Exception:
        always_heatmap = True
    
    # 5. DECISION - Generate diagnostics on failure OR when enabled
    do_generate_heatmap = (f_score > 50) or force_heatmap or always_heatmap
    
    # HIGH FRICTION - Follow failure flow
    if f_score > 50:
        print(f"   Final F-Score: {f_score:.1f}/100 ({severity_label})")
        
        def _load_elements_for_screenshot(screenshot_path: str, fallback_elements: List[Dict[str, Any]]):
            """Try to load per-screenshot interactive_elements JSON; fall back to provided list.

            Returns a list of elements.
            """
            try:
                if not screenshot_path:
                    logger.debug("No screenshot path provided for element lookup")
                    return fallback_elements or []

                screenshots_dir = os.path.dirname(screenshot_path)
                stem = os.path.splitext(os.path.basename(screenshot_path))[0]
                candidate = os.path.join(screenshots_dir, f"{stem}_interactive_elements.json")
                elems = None
                if os.path.exists(candidate):
                    try:
                        with open(candidate, 'r', encoding='utf-8') as cf:
                            j = json.load(cf)
                        # Support both {"interactive_elements": [...] } and raw list
                        elems = j.get('interactive_elements') if isinstance(j, dict) and 'interactive_elements' in j else j
                        if isinstance(elems, list) and elems:
                            # Log counts and OCR presence
                            ocr_count = sum(1 for e in elems if float(e.get('ocr_confidence', 0) or 0) > 0)
                            logger.info(f"Using per-screenshot interactive elements from {candidate}: {len(elems)} elements, OCR present on {ocr_count}")
                            return elems
                    except Exception as e:
                        logger.debug(f"Failed to read per-screenshot elements {candidate}: {e}")

                # If per-screenshot candidate is missing or has few elements, prefer any "_observe_" per-screenshot file
                try:
                    all_files = os.listdir(screenshots_dir)
                    best_obs = None
                    best_count = 0
                    for fname in all_files:
                        lf = fname.lower()
                        if lf.endswith('_interactive_elements.json') and '_observe' in lf:
                            p = os.path.join(screenshots_dir, fname)
                            try:
                                with open(p, 'r', encoding='utf-8') as cf2:
                                    j2 = json.load(cf2)
                                cand = j2.get('interactive_elements') if isinstance(j2, dict) and 'interactive_elements' in j2 else j2
                                if isinstance(cand, list):
                                    cnt = len(cand)
                                    if cnt > best_count:
                                        best_count = cnt
                                        best_obs = (p, cand)
                            except Exception:
                                continue
                    if best_obs and best_count > 0:
                        p, cand = best_obs
                        ocr_count = sum(1 for e in cand if float(e.get('ocr_confidence', 0) or 0) > 0)
                        logger.info(f"Preferring observe interactive elements from {p}: {best_count} elements, OCR present on {ocr_count}")
                        return cand
                except Exception:
                    pass

                # No per-screenshot file, fall back to provided step-level elements
                if fallback_elements:
                    logger.info(f"Using step-level interactive elements for screenshot {os.path.basename(screenshot_path)}")
                    return fallback_elements
                else:
                    logger.info(f"No interactive elements available for {os.path.basename(screenshot_path)}; visual fallback will be used")
                    return []
            except Exception as e:
                logger.debug(f"_load_elements_for_screenshot error: {e}")
                return fallback_elements or []

        # Extract uncertainty from Felicia's element detection (prefer per-screenshot lists)
        elems_for_main = _load_elements_for_screenshot(evidence.get('screenshot_after_path'), interactive_elements)
        uncertainty_data = extract_uncertainty_from_elements(
            elems_for_main,
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
                show_bboxes=True
            )
        except Exception as e:
            logger.warning(f"Heatmap generation failed: {e}")
        
        # Generate ghost replay
        try:
            seq = _collect_report_screenshots(report_dir)
            if seq and len(seq) >= 2:
                # Generate per-step heatmaps
                try:
                    for idx, sp in enumerate(seq):
                        try:
                            step_hm_path = os.path.join(report_dir, f"uncertainty_heatmap_step_{idx+1:02d}.png")
                            elems = _load_elements_for_screenshot(sp, interactive_elements)
                            ud = extract_uncertainty_from_elements(
                                elems,
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
                            logger.debug(f"Failed generating step heatmap for {sp}", exc_info=True)
                except Exception:
                    logger.debug("Failed generating per-step heatmaps", exc_info=True)
                
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
            logger.warning(f"Ghost replay generation failed: {e}")
        
        # Try to save rolling buffer
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
    
    # LOW FRICTION - But generate diagnostics if enabled
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
            logger.warning(f"Heatmap generation failed: {e}")
        
        try:
            seq = _collect_report_screenshots(report_dir)
            if seq and len(seq) >= 2:
                try:
                    for idx, sp in enumerate(seq):
                        try:
                            step_hm_path = os.path.join(report_dir, f"uncertainty_heatmap_step_{idx+1:02d}.png")
                            elems = _load_elements_for_screenshot(sp, interactive_elements)
                            ud = extract_uncertainty_from_elements(
                                elems,
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
                            logger.debug(f"Failed generating step heatmap for {sp}", exc_info=True)
                except Exception:
                    logger.debug("Failed generating per-step heatmaps", exc_info=True)
                
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
            logger.warning(f"Ghost replay generation failed: {e}")
        
        return {
            "status": "SUCCESS",
            "reason": "Heatmap Generated",
            "f_score": f_score,
            "heatmap_path": heatmap_path,
            "gif_path": gif_path,
            "uncertainty_metrics": uncertainty_data
        }
    
    # LOW FRICTION - No diagnostics needed
    return {
        "status": "SUCCESS",
        "reason": "Low Friction",
        "f_score": f_score
    }