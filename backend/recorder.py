from collections import deque
from typing import Deque, Optional, List, Tuple
import os
import logging
import cv2
import numpy as np
import imageio

# Module logger
logger = logging.getLogger(__name__)


class GhostRecorder:
    """Rolling frame buffer and GIF exporter for Ghost Replay visuals.

    Usage:
        rec = GhostRecorder(max_frames=180)
        rec.update(frame)  # BGR OpenCV frame
        rec.save_doom_scroll('path/to/out.gif')
    """

    def __init__(self, max_frames: int = 180) -> None:
        self.max_frames = int(max_frames)
        self._buf: Deque[np.ndarray] = deque(maxlen=self.max_frames)

    def update(self, frame: np.ndarray) -> None:
        """Append a BGR frame (numpy array) to the rolling buffer."""
        try:
            if frame is None:
                return
            # Keep a copy to avoid external mutation
            self._buf.append(frame.copy())
        except Exception:
            return

    def save_doom_scroll(self, filename: str, duration_ms: int = 300) -> Optional[str]:
        """Export the buffered frames as a looping GIF.

        Returns the filename on success, or None on failure.
        """
        try:
            if not self._buf:
                return None
            out_dir = os.path.dirname(filename)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)

            # Convert frames from BGR -> RGB for imageio
            frames_rgb: List[np.ndarray] = []
            for f in list(self._buf):
                rgb = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
                frames_rgb.append(rgb)

            # duration in seconds per frame
            duration = max(0.02, duration_ms / 1000.0)
            imageio.mimsave(filename, frames_rgb, duration=duration, loop=0)
            return filename
        except Exception:
            logger.exception('GhostRecorder.save_doom_scroll failed for %s', filename)
            return None


# --- Helper visual functions for ghost replay (used by expectation engine) ---
def add_click_indicator(img: np.ndarray, x: float, y: float, frame_num: int = 0, total_frames: int = 12) -> np.ndarray:
    """Draw animated click ripples on an RGB image. Coordinates x,y are ratios (0..1) or pixels.
    Returns an RGB image.
    """
    img_copy = img.copy()
    rows, cols = img_copy.shape[:2]
    center_x = int(cols * x) if x <= 1.0 else int(x)
    center_y = int(rows * y) if y <= 1.0 else int(y)
    progress = frame_num / max(total_frames - 1, 1)

    radius1 = int(10 + (progress * 50))
    thickness1 = max(2, int(6 - (progress * 4)))
    alpha1 = max(0.0, 1.0 - (progress * 1.2))

    ring2_start = 0.3
    if progress > ring2_start:
        progress2 = (progress - ring2_start) / (1.0 - ring2_start)
        radius2 = int(10 + (progress2 * 40))
        thickness2 = max(2, int(5 - (progress2 * 3)))
        alpha2 = max(0.0, 0.8 - (progress2 * 1.0))
    else:
        radius2, thickness2, alpha2 = 0, 0, 0

    overlay = img_copy.copy()
    if alpha1 > 0:
        cv2.circle(overlay, (center_x + 2, center_y + 2), radius1, (0, 0, 0), thickness1)
        cv2.addWeighted(overlay, alpha1 * 0.3, img_copy, 1 - (alpha1 * 0.3), 0, img_copy)
        overlay = img_copy.copy()

    if alpha1 > 0:
        cv2.circle(overlay, (center_x, center_y), radius1, (0, 255, 255), thickness1)
        cv2.addWeighted(overlay, alpha1, img_copy, 1 - alpha1, 0, img_copy)
        overlay = img_copy.copy()

    if alpha2 > 0:
        cv2.circle(overlay, (center_x, center_y), radius2, (255, 255, 0), thickness2)
        cv2.addWeighted(overlay, alpha2, img_copy, 1 - alpha2, 0, img_copy)
        overlay = img_copy.copy()

    cv2.circle(img_copy, (center_x, center_y), 5, (0, 0, 255), -1)
    cv2.circle(img_copy, (center_x, center_y), 5, (255, 255, 255), 2)
    return img_copy


def create_difference_overlay(img_before: np.ndarray, img_after: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Create a colored difference overlay and binary mask from two BGR images."""
    gray_before = cv2.cvtColor(img_before, cv2.COLOR_BGR2GRAY)
    gray_after = cv2.cvtColor(img_after, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(gray_before, gray_after)
    diff = cv2.GaussianBlur(diff, (5, 5), 0)
    _, thresh = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    img_overlay = img_after.copy()
    diff_colored = cv2.applyColorMap(diff, cv2.COLORMAP_JET)
    mask = thresh > 0
    img_overlay[mask] = cv2.addWeighted(img_after, 0.4, diff_colored, 0.6, 0)[mask]
    cv2.drawContours(img_overlay, contours, -1, (0, 255, 0), 2)

    if len(contours) > 0:
        total_change_area = sum(cv2.contourArea(c) for c in contours)
        img_h, img_w = img_after.shape[:2]
        change_percent = (total_change_area / (img_w * img_h)) * 100
        text = f"Changed: {change_percent:.1f}%"
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, 0.7, 2)[0]
        bg_x1, bg_y1 = 10, 10
        bg_x2, bg_y2 = bg_x1 + text_size[0] + 10, bg_y1 + text_size[1] + 10
        cv2.rectangle(img_overlay, (bg_x1, bg_y1), (bg_x2, bg_y2), (0, 0, 0), -1)
        cv2.rectangle(img_overlay, (bg_x1, bg_y1), (bg_x2, bg_y2), (0, 255, 0), 2)
        cv2.putText(img_overlay, text, (15, 30), font, 0.7, (0, 255, 0), 2)

    return img_overlay, thresh


def add_diagnostic_overlay(img: np.ndarray, frame_info: str, f_score: Optional[float] = None, severity: Optional[str] = None, error_msg: Optional[str] = None) -> np.ndarray:
    """Add top/bottom banners with diagnostic text onto an RGB image.
    Returns an RGB image.
    """
    # Expect RGB input
    img_copy = img.copy()
    height, width = img_copy.shape[:2]
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Top banner
    banner_h = 40
    banner = np.zeros((banner_h, width, 3), dtype=np.uint8)
    banner[:] = (30, 30, 30)
    cv2.putText(banner, frame_info, (10, 27), font, 0.6, (255, 255, 255), 1)

    if severity:
        severity_color = {'P0': (0, 0, 255), 'P1': (0, 140, 255), 'P2': (0, 255, 255), 'P3': (128, 128, 128)}.get(severity, (255, 255, 255))
        cv2.putText(banner, f"[{severity}]", (width - 100, 27), font, 0.7, severity_color, 2)

    if f_score is not None:
        score_x = width - 250
        score_text = f"F-Score: {f_score:.1f}"
        if f_score >= 80:
            score_color = (0, 0, 255)
        elif f_score >= 60:
            score_color = (0, 140, 255)
        elif f_score >= 40:
            score_color = (0, 255, 255)
        else:
            score_color = (0, 255, 0)
        cv2.putText(banner, score_text, (score_x, 27), font, 0.6, score_color, 2)

    result = np.vstack([banner, img_copy])

    # Bottom error banner
    error_h = 50
    error_banner = np.zeros((error_h, width, 3), dtype=np.uint8)
    if error_msg:
        error_banner[:] = (0, 0, 128)
        max_chars = int(width / 8)
        msg = error_msg if len(error_msg) <= max_chars else error_msg[:max_chars - 3] + "..."
        cv2.putText(error_banner, f"Warning: {msg}", (10, 32), font, 0.5, (255, 255, 255), 1)
    else:
        error_banner[:] = (30, 30, 30)

    result = np.vstack([result, error_banner])
    return result


def generate_ghost_replay(img_a_path: str = None, img_b_path: str = None, output_path: str = None, click_x: float = 0.5, click_y: float = 0.5, f_score: Optional[float] = None, severity: Optional[str] = None, error_msg: Optional[str] = None, show_diff: bool = True, img_sequence: Optional[List[str]] = None) -> Optional[str]:
    """Create a ghost replay GIF.

    Supports two-image mode (img_a_path, img_b_path) for compatibility,
    or a multi-frame mode by passing `img_sequence` (list of image paths).

    Returns the output_path on success, None on failure.
    """
    try:
        frames = []

        # Multi-frame sequence mode
        if img_sequence and isinstance(img_sequence, list) and len(img_sequence) >= 1:
            # Load images in sequence, convert to RGB
            imgs_rgb = []
            for p in img_sequence:
                img = cv2.imread(p)
                if img is None:
                    continue
                imgs_rgb.append(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

            if not imgs_rgb:
                return None

            total_frames = max(16, len(imgs_rgb) * 2)

            # Build frames: for each image, add diagnostic overlay and a click indicator
            for idx, img_rgb in enumerate(imgs_rgb):
                frame_info = f"Step {idx+1}/{len(imgs_rgb)}"
                frames.append(add_diagnostic_overlay(img_rgb, f"{frame_info} | SNAPSHOT", f_score, severity))

                # small click pulse after snapshot
                pulse = add_click_indicator(img_rgb, click_x, click_y, idx % 12, 12)
                frames.append(add_diagnostic_overlay(pulse, f"{frame_info} | PULSE", f_score, severity))

                # Add transition blend to next frame if exists
                if idx + 1 < len(imgs_rgb):
                    next_img = imgs_rgb[idx + 1]
                    blend = cv2.addWeighted(img_rgb, 0.5, next_img, 0.5, 0)
                    frames.append(add_diagnostic_overlay(blend, f"Transition {idx+1}->{idx+2}", f_score, severity))

            # Optionally append diff analysis for final pair
            if show_diff and len(imgs_rgb) >= 2:
                try:
                    # use last two original BGR images for diff
                    last = cv2.cvtColor(imgs_rgb[-2], cv2.COLOR_RGB2BGR)
                    last2 = cv2.cvtColor(imgs_rgb[-1], cv2.COLOR_RGB2BGR)
                    diff_img, _ = create_difference_overlay(last, last2)
                    diff_rgb = cv2.cvtColor(diff_img, cv2.COLOR_BGR2RGB)
                    frames.append(add_diagnostic_overlay(diff_rgb, "DIFF ANALYSIS", f_score, severity, error_msg))
                except Exception:
                    pass

            # Hold final frame(s)
            for i in range(2):
                frames.append(add_diagnostic_overlay(imgs_rgb[-1], f"Result | {len(imgs_rgb)}", f_score, severity, error_msg))

        else:
            # Backwards-compatible two-image mode
            if not img_a_path or not img_b_path:
                return None

            img_a = cv2.imread(img_a_path)
            img_b = cv2.imread(img_b_path)
            if img_a is None or img_b is None:
                return None

            if img_a.shape != img_b.shape:
                h, w = img_a.shape[:2]
                img_b = cv2.resize(img_b, (w, h))

            img_a_rgb = cv2.cvtColor(img_a, cv2.COLOR_BGR2RGB)
            img_b_rgb = cv2.cvtColor(img_b, cv2.COLOR_BGR2RGB)

            total_frames = 16

            # Before holds
            for i in range(2):
                frames.append(add_diagnostic_overlay(img_a_rgb, f"Frame {i+1}/{total_frames} | BEFORE", f_score, severity))

            # Click animation
            for i in range(6):
                frame_with_click = add_click_indicator(img_a_rgb, click_x, click_y, i, 12)
                frames.append(add_diagnostic_overlay(frame_with_click, f"Frame {i+3}/{total_frames} | CLICK", f_score, severity))

            # Transition blend
            blend = cv2.addWeighted(img_a_rgb, 0.5, img_b_rgb, 0.5, 0)
            frames.append(add_diagnostic_overlay(blend, f"Frame 9/{total_frames} | TRANSITION", f_score, severity))

            # After with fading click
            for i in range(2):
                frame_with_click = add_click_indicator(img_b_rgb, click_x, click_y, 6 + i, 12)
                frames.append(add_diagnostic_overlay(frame_with_click, f"Frame {i+10}/{total_frames} | AFTER", f_score, severity, error_msg))

            # Diff analysis
            if show_diff:
                diff_img, _ = create_difference_overlay(img_a, img_b)
                diff_rgb = cv2.cvtColor(diff_img, cv2.COLOR_BGR2RGB)
                for i in range(2):
                    frames.append(add_diagnostic_overlay(diff_rgb, f"Frame {i+12}/{total_frames} | DIFF ANALYSIS", f_score, severity, error_msg))
            else:
                for i in range(2):
                    frames.append(add_diagnostic_overlay(img_b_rgb, f"Frame {i+12}/{total_frames} | AFTER", f_score, severity, error_msg))

            # Hold then loop
            for i in range(2):
                frames.append(add_diagnostic_overlay(img_b_rgb, f"Frame {i+14}/{total_frames} | RESULT", f_score, severity, error_msg))
            frames.append(add_diagnostic_overlay(img_a_rgb, f"Frame 16/{total_frames} | LOOP", f_score, severity))

        out_dir = os.path.dirname(output_path) if output_path else None
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        # Save GIF
        imageio.mimsave(output_path, frames, duration=0.3, loop=0)
        return output_path
    except Exception:
        logger.exception('generate_ghost_replay failed for %s -> %s', img_sequence or (img_a_path, img_b_path), output_path)
        return None


__all__ = ["GhostRecorder", "generate_ghost_replay", "add_click_indicator", "create_difference_overlay", "add_diagnostic_overlay"]
