# Opens a window with the Basler ACE USB camera feed.
# From this tutorial: https://pythonforthelab.com/blog/getting-started-with-basler-cameras/
# https://www.iditect.com/faq/python/convert-python-opencv-image-numpy-array-to-pyqt-qpixmap-image.html
import numpy as np
from PIL import Image
import sys
from PyQt6.QtWidgets import  QWidget, QLabel, QApplication
from PyQt6.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap
from pypylon import pylon

app = QApplication(sys.argv)

# def np_arr_to_qimage(arr):

converter = pylon.ImageFormatConverter()
# For outputpixelformat:
# Grayscale: PixelType_Mono8
# RGB: PixelType_BGR8packed
converter.OutputPixelFormat = pylon.PixelType_Mono8 # Trying grayscale to avoid rainbow vomit
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
    
tl_factory = pylon.TlFactory.GetInstance()
camera = pylon.InstantCamera()
camera.Attach(tl_factory.CreateFirstDevice())
camera.Open()
camera.StartGrabbing(1)
grab = camera.RetrieveResult(2000, pylon.TimeoutHandling_ThrowException)
if grab.GrabSucceeded():
    image = converter.Convert(grab)
    arr = image.GetArray()
    arr = np.ascontiguousarray(arr)
    print("Grabbed an image")
    print(arr)
    h, w = arr.shape # For RGB: h, w, _ = arr.shape
    qimg = QImage(arr.data, w, h, arr.strides[0], QImage.Format.Format_Grayscale8) # Trying grayscale to avoid rainbow vomit (RGB is ...Format_BGR888)
    qimg = qimg.copy()
    print("converted to QImage")
    # qimg = qimg.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio)
    print("scaled")
    qimg.save("qimg_test.png")
    print("qimg saved")
    print(qimg)
    
grab.Release()
 
camera.Close()

label = QLabel()
pixmap = QPixmap.fromImage(qimg)
label.setPixmap(pixmap)
label.show()
app.exec()
