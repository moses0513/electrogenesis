# Used to see live footage from the basler camera of the maskless photolithography machine.
# The footage needs to be retrieved using PyPylon and returned in the form of a PyQt6 widget.
# Updated 1/31/2025 by S. Jacob Finch

from PyQt6.QtWidgets import  QWidget, QLabel, QApplication
from PyQt6.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap
from pypylon import pylon
import cv2, sys
import numpy as np

converter = pylon.ImageFormatConverter()
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
    
tl_factory = pylon.TlFactory.GetInstance()
camera = pylon.InstantCamera()
camera.Attach(tl_factory.CreateFirstDevice())

class Thread(QThread):
    updatePixmap = pyqtSignal(QImage)

    def run(self):
        # Try to open the basler camera
        try:
            camera.Open()
            # The camera will continuously grab frames one by one
            camera.StartGrabbing(pylon.GrabStrategy_OneByOne)
        except Exception as e:
            print(f"Could not open camera. Exception: {e}")
            return
        # Constantly be updating the Pixmap with the new frame
        while camera.IsGrabbing():
            # Get the frame
            grab = camera.RetrieveResult(2000, pylon.TimeoutHandling_ThrowException)
            if grab.GrabSucceeded():
                # Convert to BRG888 pixel format (see top of this script)
                image = converter.Convert(grab)
                arr = image.GetArray()
                arr = np.ascontiguousarray(arr) # silly little numpy formatting
                h, w, _ = arr.shape
                # Convert to a QImage so we can use it with the PyQt6 GUI
                qimg = QImage(arr.data, w, h, arr.strides[0], QImage.Format.Format_BGR888)
                qimg = qimg.copy() # Separate from numpy array in memory, for some reason this helped
                # Scale it to a good size
                p = qimg.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio)
                # If all goes well, update the CameraFeed by emitting a signal
                self.updatePixmap.emit(p)
            
            # We are done with this frame, so release it from memory so that the memory can be reused
            grab.Release()
                

class CameraFeed(QWidget):
    def __init__(self):
        super().__init__()
        # Make a label to hold the camera feed
        self.label = QLabel(self)
        self.label.resize(640, 480)
        # Use threading to continuously update the camera
        th = Thread(self)
        # When a pyqtSignal is emitted, run the "self.setImage" function
        # This will update the camera box in the GUI every time the signal is received
        th.updatePixmap.connect(self.setImage) 
        th.start()
        self.show()
    @pyqtSlot(QImage) # Listen for QImage signals
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

# FOR DEBUGGING: Uncomment to make a window appear when running this script
# app = QApplication(sys.argv)
# camFeed = CameraFeed()
# camFeed.show()
# app.exec()