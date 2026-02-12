SUPPORTED_BROWSERS = ['chromium', 'firefox', 'webkit']
HEADLESS = [True, False]
# SUPPORTED_BROWSERS = ["firefox"]

SUPPORTED_RESOLUTIONS = [
    {'width': 1366, 'height': 768},
    # {"width": 1440, "height": 900},
    {'width': 1920, 'height': 1080},
    # {"width": 2560, "height": 1440},
]

DEFAULT_CONFIG = {
    'browser_type': 'chromium',
    'viewport': {'width': 1280, 'height': 720},
    'device_scale_factor': 1.0,  # Force 1.0 for consistent coordinates on Retina/HiDPI screens
    'headless': True,
    'language': 'en-US',
}
