# test_imports.py
try:
    import anthropic
    print("Anthropic (Claude) is ready.")
except ImportError:
    print("Anthropic is MISSING.")

try:
    import slack_sdk
    print("Slack SDK is ready.")
except ImportError:
    print("Slack SDK is MISSING.")

try:
    import cv2
    from skimage.metrics import structural_similarity
    print("OpenCV & Scikit-Image are ready.")
except ImportError:
    print("Visual Libraries missing (Check pip install).")

print("Ready to demo")