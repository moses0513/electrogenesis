# Enter parameters here:
import os

LITHO_SIZE_PX_X = 1280 # 768  # Lithography image size in pixels (X direction)
LITHO_SIZE_PX_Y = 720 # 768  # Lithography image size in pixels (Y direction)

PHOTO_FILE = 'png_images/25 Egen Logo (White).png' # Use relative path from main script folder
ALIGNMENT_FILE = 'png_images/25 Egen Logo (White).png'

DRAW_BOUNDING_CIRCLE = True  # Draw bounding box around lithography image for alignment purposes

CAMERA_OUTPUT_GRAYSCALE = True # When true, the camera feed will be black and white instead of RGB. This can help with the "rainbow vomit" problem.
EXPOSURE_TIME = 3.0  # Default exposure time in seconds
BRIGHTNESS_UV = 128  # Default UV LED brightness (0-255)
BRIGHTNESS_RED = 128  # Default Red LED brightness (0-255)
BRIGHTNESS_GREEN = 0  # Default Green LED brightness (0-255)
