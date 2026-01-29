# Opens a window with the Basler ACE USB camera feed.
# From this tutorial: https://pythonforthelab.com/blog/getting-started-with-basler-cameras/

import numpy as npfrom
import sys
from PyQt6.QtWidgets import  QWidget, QLabel, QApplication
from PyQt6.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap
from pypylon import pylon

def np_arr_to_qimage(arr):
    try:
        h, w = arr.shape
        bytesPerLine = 3 * w
        convertToQtFormat = QImage(arr.data, w, h, bytesPerLine, QImage.Format.Format_RGB888)
        qimg = convertToQtFormat.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio)
        return qimg
    except Exception as e:
        print(e)
    
tl_factory = pylon.TlFactory.GetInstance()
camera = pylon.InstantCamera()
camera.Attach(tl_factory.CreateFirstDevice())
camera.Open()
camera.StartGrabbing(1)
grab = camera.RetrieveResult(2000, pylon.TimeoutHandling_ThrowException)
if grab.GrabSucceeded():
    arr = grab.GetArray()
    print("Grabbed an image")
    qimg = np_arr_to_qimage(arr)
    label = QLabel()
    label.setPixmap(QPixmap.fromImage(qimg))
    print("converted to QImage")
    
camera.Close()

app = QApplication(sys.argv)
# label.show()
app.exec()
