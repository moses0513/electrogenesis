# Paste the relative path of whatever picture you want to invert at the bottom of this code
# Useful for fixing black stencils (white lines will be UV light, black will be darkness)

import numpy as np
from PIL import Image

def invert_image(img_path):
    # ... inside a function ...
    img_photo = Image.open(img_path).convert("RGB")

    arr = np.array(img_photo, dtype=np.int16)
    arr = np.clip(255 - arr, 0, 255).astype(np.uint8)

    # Convert back to PIL Image and then to QImage
    blended_img = Image.fromarray(arr, 'RGB')
    blended_img.save("inverted_image.png")

### PASTE DIRECTORY IN THIS FUNCTION: ###
invert_image("png_images\\25 EGen Logo Text.png")