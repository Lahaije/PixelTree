from pathlib import Path

IMAGE = (640, 480)  # Dimensions of image snapped by webcam
LENS_ANGLE = (60, 60)  # Estimated opening angles of webcam (x, y)

storage = Path(__file__).parent.parent / 'snap'  # Folder to store images made by webcam and calculated image data.
NUM_PIXELS = 600

"""
Number of frames used to find the led positions.
This number corresponds with the maximum number of leds supported in the system.
The maximum number of leds = 2 ^ NUM_SNAP_FRAMES - 16 .
With NUM_SNAP_FRAMES == 8, 240 leds are supported.
NUM_SNAP_FRAMES == 12, has 4080 leds supported.
"""

NUM_SNAP_FRAMES = 12
