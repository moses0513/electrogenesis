# NOTE: This is not an ideal system, but it works for further testing.
#
# This function creates PNGs that are completely blue for the photolithography layer,
# or completely red for the alignment assist layer.
# A combined magenta pixmap (or separate blue and red pixmaps) will be returned when the function is called.
#
# This image can be moved around and scaled in the preview,
# but this will no longer yield a perfect pixel-by-pixel resemblance
# of the original image. This could cause microscopic differences
# between the exposed silicon wafer and original schemiatic.
#
# Anti-aliasing may be helpful, and should be experimented with
# to see if it offers better results, specifically for curves.

import numpy as np
import config
from PIL import Image
from PyQt6.QtWidgets import QGraphicsPixmapItem
from PyQt6.QtGui import QPixmap, QImage

def add_images(img_photo_path, img_align_path):
    
    img_photo = Image.open(img_photo_path).convert("RGB")
    img_align = Image.open(img_align_path).convert("RGB")

    img_photo = img_photo.resize(size=(config.LITHO_SIZE_PX_X, config.LITHO_SIZE_PX_Y))
    if img_photo.size != img_align.size:
        img_align = img_align.resize(img_photo.size)

    # Convert to numpy arrays, use int16 to avoid immediate overflow
    arr1 = np.array(img_photo, dtype=np.int16)
    arr2 = np.array(img_align, dtype=np.int16)

    # PNGs come in with white representing UV exposed areas and black representing no UV exposure.
    # Technically, only the BLUE values matter for the photo layer.
    # Both RED and GREEN values are dropped.
    # The opposite is true for the align layer. Only the RED matters, and green and blue are dropped.
    # Because white pictures already contain all three, it's best to draw in white for compatibility with both.

    # Add arrays and clip values to stay within the valid 0-255 range
    added_arr1 = np.clip(arr1 + [-255, -255, -(255-config.BRIGHTNESS_UV)], 0, 255).astype(np.uint8) # Only keep blue
    added_arr2 = np.clip(arr2 + [-(255-config.BRIGHTNESS_RED), -(255-config.BRIGHTNESS_GREEN), -255], 0, 255).astype(np.uint8) # Only keep red
    added_arr = np.clip(added_arr1 + added_arr2, 0, 255).astype(np.uint8)

    # Convert back to PIL Image and then to QImage
    blended_img = Image.fromarray(added_arr, 'RGB')
    blended_img.save("blended_image.png")
    blended_img_data = blended_img.tobytes("raw", "RGBA")
    blended_q_img = QImage(blended_img_data, blended_img.width, blended_img.height, QImage.Format.Format_RGBA8888)
    # return blended_q_img

    # Create blended image
    pixmap = QPixmap.fromImage(blended_q_img)
    graphicsPixmapItem = QGraphicsPixmapItem(pixmap)
    return graphicsPixmapItem

    # lbl = QLabel()
    # lbl.setPixmap(pixmap)
    # return lbl
