#!/usr/bin/env python3
"""
Force-generate heatmaps and ghost-replay GIFs for all step JSONs in a report.
Usage:
  python backend/scripts/force_generate_heatmaps.py --report reports/test_2026-02-12_16-35-17_863434
"""
import os
import sys
import glob
import json
import argparse

# Ensure project root is on sys.path so 'backend' package can be imported when
# running the script directly from PowerShell/Windows.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.expectation_engine import check_expectation
# helper to resolve paths like webqa_bridge did during live runs
try:
    from backend.webqa_bridge import _resolve_screenshot_path
except Exception:
    _resolve_screenshot_path = lambda p: p


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--report", required=True, help="Report directory containing step_XX_report.json files")
    args = p.parse_args()

    report_dir = args.report
    if not os.path.isdir(report_dir):
        print(f"Report directory not found: {report_dir}")
        sys.exit(2)

    json_files = sorted(glob.glob(os.path.join(report_dir, "step_*_report.json")))
    if not json_files:
        print("No step JSON files found in report directory.")
        sys.exit(0)

    for jf in json_files:
        print("Processing", os.path.basename(jf))
        try:
            h = json.load(open(jf, 'r', encoding='utf-8'))
        except Exception as e:
            print("  Failed to read JSON:", e)
            continue

        h.setdefault('meta_data', {})['force_heatmap'] = True

        # Remap any screenshot paths that are absolute but missing to report screenshots
        ev = h.get('evidence', {})
        if ev:
            for key in ('screenshot_before_path', 'screenshot_after_path'):
                if ev.get(key):
                    ev[key] = _resolve_screenshot_path(ev.get(key))

        try:
            res = check_expectation(h)
            print("  -> status:", res.get('status'), "heatmap:", res.get('heatmap_path'), "gif:", res.get('gif_path'))
        except Exception as e:
            print("  -> check_expectation raised:", e)

    print("Done")


if __name__ == '__main__':
    main()
