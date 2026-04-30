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

# Returns a QPixmap solely for alignment purposes (only RED and GREEN values). The QPixmap can be added to a QGraphicsScene.
def align_image(img_path):
    img = Image.open(img_path).convert("RGB")
    scale = min(config.LITHO_SIZE_PX_X / img.width, config.LITHO_SIZE_PX_Y / img.height)    
    img = img.resize(size=(int(img.width * scale), int(img.height * scale)), resample=Image.Resampling.NEAREST)
    arr = np.array(img, dtype=np.int16)
    
    # Images should white by default. This sets the RG values to whatever is specified by the GUI, gets rid of any BLUE, and clips values outside of the 0-255 range.
    red_green_array = np.clip(arr - [(255-config.BRIGHTNESS_RED), (255-config.BRIGHTNESS_GREEN), 255], 0, 255).astype(np.uint8) # Only keep red
    
    # Convert the array to a QPixmap (usable with QGraphicsScene)
    return pixmap_from_qimage_from_PIL_from_arr(red_green_array)

# Returns a QPixmap that can be added to a QGraphicsScene. Combines the photo and align images into a single item.
def add_images(img_photo_path, img_align_path):
    img_photo = Image.open(img_photo_path).convert("RGB")
    if img_align_path is None:
        img_align = img_photo
    else:
        img_align = Image.open(img_align_path).convert("RGB")

    scale = min(config.LITHO_SIZE_PX_X / img_photo.width, config.LITHO_SIZE_PX_Y / img_photo.height)    
    img_photo = img_photo.resize(size=(int(img_photo.width * scale), int(img_photo.height * scale)), resample=Image.Resampling.NEAREST)
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
    
    # Bug fix for "draw aligmnet image checkbox" unchecked
    if img_align_path is None:
        added_arr = added_arr1
    else:
        added_arr = np.clip(added_arr1 + added_arr2, 0, 255).astype(np.uint8)

    # Convert the array to a QPixmap (usable with QGraphicsScene)
    return pixmap_from_qimage_from_PIL_from_arr(added_arr)
    
    
def pixmap_from_qimage_from_PIL_from_arr(arr):
    # Convert back to PIL Image, then to QImage, then to QPixmap
    img = Image.fromarray(arr, 'RGB')
    img.save("blended_image.png")
    img_data = img.tobytes("raw", "RGBA")
    q_img = QImage(img_data, img.width, img.height, QImage.Format.Format_RGBA8888)
    pixmap = QPixmap.fromImage(q_img)
    graphicsPixmapItem = QGraphicsPixmapItem(pixmap)
    return graphicsPixmapItem

