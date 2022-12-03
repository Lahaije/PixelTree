from pathlib import Path

IMAGE = (640, 480)  # Dimensions of image snapped by webcam
LENS_ANGLE = (60, 60)  # Estimated opening angles of webcam (x, y)

storage = Path(__file__).parent.parent / 'snap'  # Folder to store images made by webcam and calculated image data.
NUM_PIXELS = 50
